import http.server
from json import dumps
from status import HTTP_200_OK

class CustomHandler(http.server.BaseHTTPRequestHandler):
    def prepare_response(self, response: dict, status: int):
        response = dumps(response).encode(encoding='utf_8')
        self.send_response(status)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(response)

    def do_GET(self):
        response = {
            "message": "ok"
        }
        self.prepare_response(response=response, status=HTTP_200_OK)
        return
