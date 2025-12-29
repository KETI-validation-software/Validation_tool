import ssl
import json
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtCore
from http.server import HTTPServer
from core.functions import resource_path

class server_th(QThread):
    def __init__(self, handler_class=None, address='127.0.0.1', port=8008):
        super().__init__()
        self.handler_class = handler_class
        self.address_ip = address
        self.address_port = port
        self.server_address = (self.address_ip, self.address_port)
        self.httpd = HTTPServer(self.server_address, self.handler_class)

        certificate_private = resource_path('config/key0627/server.crt')
        certificate_key = resource_path('config/key0627/server.key')
        try:
            self.httpd.socket = ssl.wrap_socket(self.httpd.socket, certfile=certificate_private,
                                                keyfile=certificate_key, server_side=True)
        except Exception as e:
            print(f"[SERVER_THREAD] SSL 인증서 로드 오류: {e}")

        print('Starting on ', self.server_address)

    def run(self):
        self.httpd.serve_forever()


class json_data(QThread):
    json_update_data = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            try:
                with open(resource_path("spec/rows.json"), "r", encoding="UTF-8") as out_file:
                    data = json.load(out_file)
                if data is not None:
                    with open(resource_path("spec/rows.json"), "w", encoding="UTF-8") as out_file:
                        json.dump(None, out_file, ensure_ascii=False)
                    self.json_update_data.emit(data)
            except Exception:
                pass
            time.sleep(0.1)
