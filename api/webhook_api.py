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

    def do_POST(self):  # ✅ 들여쓰기 수정 (클래스 메서드로 변경)
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
            resp = {"code": 200, "message": "성공"}
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
        # self.url이 잘못된 값(desc, None, 빈 문자열 등)이면 127.0.0.1로 대체
        safe_url = "127.0.0.1"  # 기본값
        
        # URL 파싱 및 검증
        try:
            if self.url and str(self.url).strip():
                url_str = str(self.url).strip()
                # 잘못된 값들 체크
                if url_str.lower() not in ["none", "", "desc", "null"]:
                    # URL이 http:// 또는 https://로 시작하는 경우 파싱
                    if url_str.lower().startswith(('http://', 'https://')):
                        parsed = urlparse(url_str)
                        if parsed.hostname:
                            safe_url = parsed.hostname
                    # 그냥 IP 주소나 도메인인 경우
                    elif '.' in url_str and not ' ' in url_str:
                        safe_url = url_str
            print(f"[Webhook] 사용할 호스트: {safe_url}")
        except Exception as e:
            print(f"[Webhook] URL 파싱 오류, 기본값 사용: {e}")
            safe_url = "127.0.0.1"

        server_address = (safe_url, self.port)
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

        print('Starting on ' + "('" + str(safe_url) + "', " + str(self.port) + ")")

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

