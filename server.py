import cv2
import torch
import socket
import argparse
import numpy as np
from requests_toolbelt.multipart import decoder
from http.server import HTTPServer, BaseHTTPRequestHandler

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("hi!"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        try:
            self._set_headers()
            content_type = self.headers['Content-Type']
            content = self.rfile.read(int(self.headers.get('Content-Length')))
            img_byte = decoder.MultipartDecoder(content, content_type=content_type).parts[0].content
            img_np = np.frombuffer(img_byte, dtype=np.uint8)
            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  
            res=model(img)
            df_byte = res.pandas().xyxy[0].to_json().encode()
            print(df_byte)
            self.wfile.write(df_byte)

        except Exception as e:
            print(e)


def run(server_class=HTTPServer, handler_class=Server, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting http server on {addr}:{port}")
    httpd.serve_forever()

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, help='port number', required=True)

    return parser.parse_args()

if __name__ == '__main__':
    opt = parse_opt()
    run(addr=socket.gethostbyname(socket.gethostname()), port=int(opt.port))