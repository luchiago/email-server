import http.server
import re
from json import dumps

from database import find_user, transaction_operation
from formatters import format_user
from status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

NOT_FOUND_RESOURCE = "não encontrado"
NOT_FOUND_URL = "Esta URL não existe"


class CustomHandler(http.server.BaseHTTPRequestHandler):
    def not_found(self, error_message: str):
        response = {"error": error_message}
        self.prepare_response(response=response, status=HTTP_404_NOT_FOUND)

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
        return headers.get("user_id")

    def do_POST(self):
        if re.search("^/messages/?$", self.path) is not None:
            message_data = self.get_body_request()
            sender = find_user(id=self.get_user_from_headers())[0]
            receiver = find_user(name=message_data.get("receiver"))[0]
            if sender is None or receiver is None:
                self.not_found(f"Usuário {NOT_FOUND_RESOURCE}")
                return
            command = "INSERT INTO message (sender, receiver, subject, body) VALUES (?, ?, ?, ?)"
            values = (
                sender,
                receiver,
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
