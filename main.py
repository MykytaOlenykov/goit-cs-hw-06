from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from pathlib import Path
import signal
import socket
import logging
from dotenv import load_dotenv
import threading

from socket_srv import socket_server

WEB_DIR = "./front"

logging.basicConfig(
    filename="server.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(os.path.join(WEB_DIR, "index.html"), "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/message.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(os.path.join(WEB_DIR, "message.html"), "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/logo.png":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open(os.path.join(WEB_DIR, "logo.png"), "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/style.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open(os.path.join(WEB_DIR, "style.css"), "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(os.path.join(WEB_DIR, "error.html"), "rb") as file:
                self.wfile.write(file.read())

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            data = self.rfile.read(content_length)

            threading.Thread(
                target=self.send_data_to_socket_server, args=(data,)
            ).start()

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Data sent to socket server")

    def send_data_to_socket_server(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", PORT2))
            sock.sendall(data)


def stop_servers(signum, frame):
    print("Stopping servers...")
    os._exit(0)  # Force exit


signal.signal(signal.SIGINT, stop_servers)

if __name__ == "__main__":
    ENV_PATH = Path(__file__).parent / ".env"
    load_dotenv(ENV_PATH)

    PORT = int(os.getenv("HTTP_SERVER_PORT"))
    PORT2 = int(os.getenv("SOCKET_SERVER_PORT"))

    web_thread = threading.Thread(target=socket_server, args=(PORT2,))
    web_thread.daemon = True
    web_thread.start()

    server_address = ("", PORT)
    httpd = HTTPServer(server_address, RequestHandler)

    try:
        print(f"Starting server on port {PORT}...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.error("Server stopping...")
        os._exit(0)  # Force exit
