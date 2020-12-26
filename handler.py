import http.server
import re
from json import dumps

from status import HTTP_200_OK, HTTP_404_NOT_FOUND

NOT_FOUND_RESOURCE = "Not found"
NOT_FOUND_URL = "This URL does not exists"


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

    def do_GET(self):
        response = {}
        if re.search("^/messages/?$", self.path) is not None:
            pass
        elif re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            pass
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_POST(self):
        response = {}
        if re.search("^/messages/?$", self.path) is not None:
            pass
        elif re.search("^/login/?$", self.path) is not None:
            pass
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_PATCH(self):
        response = {}
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            pass
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_PUT(self):
        response = {}
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            pass
        else:
            self.not_found(NOT_FOUND_URL)
        return

    def do_DELETE(self):
        response = {}
        if re.search("^/messages/(?P<id>\d+)/?$", self.path) is not None:
            pass
        else:
            self.not_found(NOT_FOUND_URL)
        return
