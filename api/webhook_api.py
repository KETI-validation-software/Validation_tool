from http.server import BaseHTTPRequestHandler, HTTPServer
from PyQt5.QtCore import *
import json
import traceback
from core.functions import resource_path
import ssl

class WebhookServer(BaseHTTPRequestHandler):
    result_signal = pyqtSignal(dict)

    def __init__(self, *args, msg = None, **kwargs):
        self.result = ""
        self.message = msg or {}
        self.result_signal = kwargs.pop('result_signal', None)
        super().__init__(*args, **kwargs)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        #self.send_header('User-Agent', 'test')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, World!')
        #print(f"Received GET request from {self.client_address[0]}")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        self.result = self.rfile.read(content_length)
        self.result = json.loads(self.result.decode('utf-8'))
        # 웹훅 요청 처리
        #print("path", self.path)
        if "Realtime".lower() in str(self.path).lower():
            #print('Received webhook request:', self.result)
            try:
                message = self.message
                a = json.dumps(message).encode('utf-8')
                self._set_headers()
                self.wfile.write(a)
                if self.result_signal:
                    self.result_signal.emit(self.result)
                    #print(str(self.result))
                self.wfile.flush()
            except Exception as e:
                print(e)
                print(traceback.format_exc())



class WebhookThread(QThread):
    result_signal = pyqtSignal(dict)

    def __init__(self, url, port, message):
        super().__init__()
        self.url = url
        self.port = port
        self.message = message
        self.httpd = None

    def run(self):

        #server_address = (self.url, self.port)
        #self.httpd = HTTPServer(server_address, lambda *args, **kwargs: WebhookServer(*args, msg=self.message,
        #                                                                result_signal=self.result_signal, **kwargs))
        ##print(f'Starting webhook server at {self.url}:{self.port}')
        #print('Starting https on port %d...' % self.port)

        server_address = (self.url, self.port)
        certificate_private = resource_path('config/key0627/server.crt')
        certificate_key = resource_path('config/key0627/server.key')
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=certificate_private, keyfile=certificate_key)

        self.httpd = HTTPServer(server_address, lambda *args, **kwargs: WebhookServer(*args, msg=self.message,
                                                                                      result_signal=self.result_signal,
                                                                                      **kwargs))
        # self.httpd.socket = ssl_context.wrap_socket(self.httpd.socket, server_side=True)
        self.httpd.socket = ssl.wrap_socket(self.httpd.socket, certfile=certificate_private, keyfile=certificate_key,
                                            server_side=True)

        print('Starting on '+"('"+ str(self.url) + "', "+ str(self.port) +")" )
        #self.httpd.serve_forever()



        try:
            self.httpd.serve_forever()
        except Exception as e:
            print(e)
        finally:
            if self.httpd:
                #print("webhook server shutdown " + f'{self.url}:{self.port}')
                self.httpd.server_close()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            return True

