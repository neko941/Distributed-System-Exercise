import torch
import socket
import sys
import cv2 
import numpy as np
# import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from requests_toolbelt.multipart import decoder

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("hi!"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  
        # results = model(self.rfile.read(a)).save(save_dir='')
        try:
            # print('asd')
            self._set_headers()
            content_type = self.headers['Content-Type']
            content = self.rfile.read(int(self.headers.get('Content-Length')))
            img_byte = decoder.MultipartDecoder(content, content_type=content_type).parts[0].content
            # print(img_byte)
            img_np = np.frombuffer(img_byte, dtype=np.uint8)
            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  
            res=model(img)
            # res.save(save_dir='pics.jpg')
            df_byte = res.pandas().xyxy[0].to_json().encode()
            print(df_byte)
            self.wfile.write(df_byte)

        except Exception as e:
            print(e)


def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting http server on {addr}:{port}")
    httpd.serve_forever()

# run(addr='192.168.31.45', port=9941)
run(addr=socket.gethostbyname(socket.gethostname()), port=int(sys.argv[1]))