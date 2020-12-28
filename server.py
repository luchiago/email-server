import http.server
import os

from handler import CustomHandler

PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"
Handler = CustomHandler

with http.server.ThreadingHTTPServer((HOST, PORT), Handler) as httpd:
    print(f"Running Server on port {PORT}")
    print("Serving...")
    httpd.serve_forever()
