import http.server

from database import DBClient
from handler import CustomHandler

PORT = 8000
HOST = "0.0.0.0"
Handler = CustomHandler

with http.server.ThreadingHTTPServer((HOST, PORT), Handler) as httpd:
    print(f"Running Server on port {PORT}")
    print("Creating Database")
    client = DBClient()
    client.create_table()
    print("Serving...")
    httpd.serve_forever()
