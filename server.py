import socketserver
from handler import CustomHandler

PORT = 8000
HOST = '0.0.0.0'
Handler = CustomHandler

with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
    httpd.serve_forever()
