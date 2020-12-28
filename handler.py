import http.server
import re
from json import dumps
from typing import Optional

from database import find_message, find_user, transaction_operation
from formatters import format_message, format_messages, format_user
from status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

NOT_FOUND_RESOURCE = "não encontrado"
NOT_FOUND_URL = "Esta URL não existe"


class CustomHandler(http.server.BaseHTTPRequestHandler):
    def not_found(self, error_message: str):
        response = {"error": error_message}
        self.prepare_response(response=response, status=HTTP_404_NOT_FOUND)

    def find_a_message(self):
        message_id = int(re.search("^/messages/(?P<id>\d+)/?$", self.path).groups()[0])
        message = find_message(id=message_id)
        if message is None:
            self.not_found(f"Email {NOT_FOUND_RESOURCE}")
            raise Exception
        return message, message_id

    def prepare_response(self, response: dict, status: int = HTTP_200_OK):
        response = dumps(response).encode(encoding="utf_8")
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response)

    def get_body_request(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        return eval(post_data.decode("utf-8"))

    def get_user_from_headers(self):
        headers = dict(self.headers)
        user = headers.get("user_name")
        if user is None:
            user = headers.get("User_name")
        return user

    def verify_headers(self, user_name: Optional[str]):
        if user_name is None:
            self.prepare_response(
                response={"error": "Não autorizado"}, status=HTTP_401_UNAUTHORIZED
            )
            raise Exception

    def verify_users(
        self, receiver_user: Optional[str] = None, verify_receiver: bool = False
    ):
        user_name = self.get_user_from_headers()
        self.verify_headers(user_name)
        sender = find_user(name=user_name)
        receiver = find_user(name=receiver_user) if verify_receiver else None
        if sender is None or (receiver is None and verify_receiver):
            self.not_found(f"Usuário {NOT_FOUND_RESOURCE}")
            raise Exception
        return sender, receiver

    def send_message(
        self,
        sender: tuple,
        receiver: tuple,
        subject: str,
        body: str,
        success_message: str,
    ):
        if sender[0] == receiver[0]:
            self.prepare_response(
                {"error": "Não pode ser o mesmo user"}, status=HTTP_400_BAD_REQUEST
            )
            raise Exception
        command = (
            "INSERT INTO message (sender, receiver, subject, body) VALUES (?, ?, ?, ?)"
        )
        values = (
            sender[0],
            receiver[0],
            subject,
            body,
        )
        created_id = transaction_operation(command=command, values=values)
        self.prepare_response(
            response={"message": success_message}, status=HTTP_201_CREATED
        )
        return created_id

    def do_GET(self):
        if re.search("^/messages/?$", self.path) is not None:
            try:
                user, _ = self.verify_users()
                user_id = user[0]
                as_sender = format_messages(find_message(sender=user_id))
                as_receiver = format_messages(find_message(receiver=user_id))
                messages = {"sent": as_sender, "received": as_receiver}
                self.prepare_response(messages, HTTP_200_OK)
            except Exception:
                return
        elif re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            try:
                message, _ = self.find_a_message()
                message = format_message(message)
                self.prepare_response(message, HTTP_200_OK)
            except Exception:
                return
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_POST(self):
        if re.search("^/messages/?$", self.path) is not None:
            try:
                message_data = self.get_body_request()
                sender, receiver = self.verify_users(
                    receiver_user=message_data.get("receiver"), verify_receiver=True
                )
                self.send_message(
                    sender,
                    receiver,
                    message_data.get("subject"),
                    message_data.get("body"),
                    "Email enviado",
                )
            except Exception:
                return
        elif re.search("^/login/?$", self.path) is not None:
            name = self.get_body_request().get("name")
            user = find_user(name)
            if user is None:
                self.not_found(f"Usuário {NOT_FOUND_RESOURCE}")
                return
            json = format_user(user)
            self.prepare_response(json)
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_PATCH(self):
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            try:
                message, _ = self.find_a_message()
                message_data = self.get_body_request()
                sender, receiver = self.verify_users(
                    receiver_user=message_data.get("receiver"), verify_receiver=True
                )
                subject = f"ENC:{message[3]}"
                body = message[4]
                self.send_message(sender, receiver, subject, body, "Email encaminhado")
            except Exception:
                return
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_PUT(self):
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            try:
                message, message_id = self.find_a_message()
                message_data = self.get_body_request()
                sender, receiver = self.verify_users(
                    receiver_user=message_data.get("receiver"), verify_receiver=True
                )
                subject = f"RE:{message[3]}"
                body = message_data.get("body")
                created_id = self.send_message(
                    sender, receiver, subject, body, "Email respondido"
                )
                command = "UPDATE message SET reply = ? WHERE id = ?"
                values = (
                    created_id,
                    message_id,
                )
                transaction_operation(command=command, values=values)
            except Exception:
                return
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_DELETE(self):
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            _, message_id = self.find_a_message()
            sender, _ = self.verify_users()
            user_id = sender[0]
            command = "UPDATE message SET receiver = NULL WHERE id = ? AND receiver = ?"
            transaction_operation(command, (message_id, user_id))
            command = "UPDATE message SET sender = NULL WHERE id = ? AND sender = ?"
            transaction_operation(command, (message_id, user_id))
            self.prepare_response(
                response={"message": "Email deletado"}, status=HTTP_204_NO_CONTENT
            )
        else:
            self.not_found(NOT_FOUND_URL)
        return
