import http.server
import re
from json import dumps
from typing import Optional

from database import DBClient
from status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

NOT_FOUND_RESOURCE = "Not found"
NOT_FOUND_URL = "This URL does not exists"

client = DBClient()


def get_reply(messageid: Optional[int]):
    if messageid is not None:
        reply = (
            client.search_one("SELECT * FROM message WHERE messageid = ?", messageid),
        )
        return parse_message(reply)
    return None


def parse_message(result: tuple):
    reply = get_reply(result[5])
    return {
        "messageid": result[0],
        "sender": client.search_one(
            "SELECT name FROM user WHERE userid = ?", result[1]
        ),
        "receiver": client.search_one(
            "SELECT name FROM user WHERE userid = ?", result[2]
        ),
        "subject": result[3],
        "body": result[4],
        "reply": reply,
    }


def parse_messages(result: list):
    parsed = []
    for message in result:
        parsed.append(parse_message(message))
    return parsed


class CustomHandler(http.server.BaseHTTPRequestHandler):
    def not_found(self, error_message: str):
        response = {"error": error_message}
        self.prepare_response(response=response, status=HTTP_404_NOT_FOUND)

    def prepare_response(self, response: dict, status: int):
        response = dumps(response).encode(encoding="utf_8")
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response)

    def _find_a_message(self):
        message_id = int(re.search("^/messages/(?P<id>\d+)/?$", self.path).gropus()[0])
        return (
            client.search_one(table_name="message", value=message_id, condition="id"),
            message_id,
        )

    def do_GET(self):
        if re.search("^/messages/?$", self.path) is not None:
            as_sender = client.search_all(
                table_name="message", value=user_id, condition="sender"
            )
            as_receiver = client.search_all(
                table_name="message", value=user_id, condition="receiver"
            )
            as_sender = parse_messages(as_sender)
            as_receiver = parse_messages(as_receiver)
            messages = {"sent": as_sender, "received": as_receiver}
            self.prepare_response(messages, HTTP_200_OK)
        elif re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            message, _ = self._find_a_message()
            if message is None:
                self.not_found(NOT_FOUND_RESOURCE)
                return
            message = parse_message(message)
            self.prepare_response(message, HTTP_200_OK)
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_POST(self):
        if re.search("^/messages/?$", self.path) is not None:
            pass
        elif re.search("^/login/?$", self.path) is not None:
            pass
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_PATCH(self):
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            message, message_id = self._find_a_message()
            if message is None:
                self.not_found(NOT_FOUND_RESOURCE)
                return
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_PUT(self):
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            message, message_id = self._find_a_message()
            if message is None:
                self.not_found(NOT_FOUND_RESOURCE)
                return
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_DELETE(self):
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            message, message_id = self._find_a_message()
            if message is None:
                self.not_found(NOT_FOUND_RESOURCE)
                return
            command = "UPDATE message SET receiver = NULL WHERE id = ? AND receiver = ?"
            client.transaction_operation(command, (message_id, user_id))
            command = "UPDATE message SET sender = NULL WHERE id = ? AND sender = ?"
            client.transaction_operation(command, (message_id, user_id))
            self.send_response(HTTP_204_NO_CONTENT)
        else:
            self.not_found(NOT_FOUND_URL)
        return
