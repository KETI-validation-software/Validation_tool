from http.server import BaseHTTPRequestHandler, HTTPServer
from PyQt5.QtCore import *
import json
import traceback
from core.functions import resource_path
import ssl
from urllib.parse import urlparse

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
        print(f"[WEBHOOK] do_POST called: path={self.path}")  # ✅ 디버그 로그
        try:
            content_length = int(self.headers.get('Content-Length', '0'))
            print(f"[WEBHOOK] Content-Length: {content_length}")  # ✅ 디버그 로그
            raw = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                payload = json.loads(raw.decode('utf-8'))
            except Exception:
                # JSON 파싱 실패 대비 (원문 그대로 보존)
                payload = {"_raw": raw.decode('utf-8', errors='ignore')}

            print(f"[WEBHOOK] Payload received: {json.dumps(payload, ensure_ascii=False)[:200]}")  # ✅ 디버그 로그

            # ✅ 1) 수신한 웹훅 요청 바디를 그대로 상위로 전달 (검증용)
            if self.result_signal:
                self.result_signal.emit(payload)

            # ✅ 2) 플랫폼(콜백 보낸 쪽)에게는 "간단한 성공 응답"만 돌려준다
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            resp = {"code": "200", "message": "성공"}
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            self.wfile.flush()
            
            print(f"[WEBHOOK] Response sent: {resp}")  # ✅ 디버그 로그

        except Exception as e:
            print(f"[WEBHOOK ERROR] {e}")  # ✅ 디버그 로그
            # 실패 응답 (옵션)
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                err = {"code": 500, "message": f"서버 오류: {str(e)}"}
                self.wfile.write(json.dumps(err, ensure_ascii=False).encode('utf-8'))
                self.wfile.flush()
            finally:
                import traceback
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
        # ✅ 웹훅 서버는 항상 0.0.0.0에 바인딩 (모든 인터페이스에서 수신)
        # safe_url은 로깅/디버깅용으로만 사용
        server_address = ("0.0.0.0", self.port)
        print(f"[Webhook] 서버 바인딩: 0.0.0.0:{self.port}")
        
        # SSL 인증서 설정
        certificate_private = resource_path('config/key0627/server.crt')
        certificate_key = resource_path('config/key0627/server.key')
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=certificate_private, keyfile=certificate_key)

        self.httpd = HTTPServer(server_address, lambda *args, **kwargs: WebhookServer(*args, msg=self.message,
                                                                                      result_signal=self.result_signal,
                                                                                      **kwargs))
        # SSL 설정
        self.httpd.socket = ssl_context.wrap_socket(self.httpd.socket, server_side=True)

        print(f'[Webhook] 웹훅 서버 시작됨: 0.0.0.0:{self.port}')

        try:
            self.httpd.serve_forever()
        except Exception as e:
            print(e)
        finally:
            if self.httpd:
                self.httpd.server_close()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            return True

