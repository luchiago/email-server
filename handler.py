import http.server
import re
from json import dumps

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
        return (
            find_message(id=message_id),
            message_id,
        )

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
        return headers.get("user_name")

    def do_GET(self):
        if re.search("^/messages/?$", self.path) is not None:
            user_name = self.get_user_from_headers()
            if user_name is None:
                self.prepare_response(
                    response={"error": "Não autorizado"}, status=HTTP_401_UNAUTHORIZED
                )
                return
            user_id = find_user(name=self.get_user_from_headers())
            if user_id is None:
                self.not_found(f"Usuário {NOT_FOUND_RESOURCE}")
                return
            user_id = user_id[0]
            as_sender = find_message(sender=user_id)
            as_receiver = find_message(receiver=user_id)
            as_sender = format_messages(as_sender)
            as_receiver = format_messages(as_receiver)
            messages = {"sent": as_sender, "received": as_receiver}
            self.prepare_response(messages, HTTP_200_OK)
        elif re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            message, _ = self.find_a_message()
            if message is None:
                self.not_found(NOT_FOUND_RESOURCE)
                return
            message = format_message(message)
            self.prepare_response(message, HTTP_200_OK)
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_POST(self):
        if re.search("^/messages/?$", self.path) is not None:
            message_data = self.get_body_request()
            sender = find_user(name=self.get_user_from_headers())
            receiver = find_user(name=message_data.get("receiver"))
            if sender is None or receiver is None:
                self.not_found(f"Usuário {NOT_FOUND_RESOURCE}")
                return
            if sender[0] == receiver[0]:
                self.prepare_response(
                    {"error": "Não pode ser o mesmo user"}, status=HTTP_400_BAD_REQUEST
                )
                return
            command = "INSERT INTO message (sender, receiver, subject, body) VALUES (?, ?, ?, ?)"
            values = (
                sender[0],
                receiver[0],
                message_data.get("subject"),
                message_data.get("body"),
            )
            transaction_operation(command=command, values=values)
            self.prepare_response(
                response={"message": "Email enviado"}, status=HTTP_201_CREATED
            )
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
            message_data = self.get_body_request()
            message, message_id = self.find_a_message()
            if message is None:
                self.not_found(NOT_FOUND_RESOURCE)
                return
            sender = find_user(name=self.get_user_from_headers())
            receiver = find_user(name=message_data.get("receiver"))
            if sender is None or receiver is None:
                self.not_found(f"Usuário {NOT_FOUND_RESOURCE}")
                return
            if sender[0] == receiver[0]:
                self.prepare_response(
                    {"error": "Não pode ser o mesmo user"}, status=HTTP_400_BAD_REQUEST
                )
                return
            command = "INSERT INTO message (sender, receiver, subject, body) VALUES (?, ?, ?, ?)"
            subject = f"ENC:{message[3]}"
            body = message[4]
            values = (
                sender[0],
                receiver[0],
                subject,
                body,
            )
            transaction_operation(command=command, values=values)
            self.prepare_response(
                response={"message": "Email emcaminhado"}, status=HTTP_201_CREATED
            )
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_DELETE(self):
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            message, message_id = self.find_a_message()
            if message is None:
                self.not_found(f"Email {NOT_FOUND_RESOURCE}")
                return
            user_id = find_user(name=self.get_user_from_headers())
            if user_id is None:
                self.not_found(f"Usuário {NOT_FOUND_RESOURCE}")
                return
            command = "UPDATE message SET receiver = NULL WHERE id = ? AND receiver = ?"
            transaction_operation(command, (message_id, user_id[0]))
            command = "UPDATE message SET sender = NULL WHERE id = ? AND sender = ?"
            transaction_operation(command, (message_id, user_id[0]))
            self.prepare_response(
                response={"message": "Email deletado"}, status=HTTP_204_NO_CONTENT
            )
        else:
            self.not_found(NOT_FOUND_URL)
        return
