import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import ssl
import json
import cgi
from collections import defaultdict, deque            # ### NEW
import datetime
import time
import traceback
import os
import config.CONSTANTS as CONSTANTS

# from spec.video.videoRequest import videoMessages, videoOutMessage, videoInMessage
# from spec.video.videoSchema import videoInSchema, videoOutSchema
# from spec.bio.bioRequest import bioMessages, bioOutMessage, bioInMessage
# from spec.bio.bioSchema import  bioInSchema, bioOutSchema
# from spec.security.securityRequest import securityMessages, securityOutMessage, securityInMessage
# from spec.security.securitySchema import securityInSchema, securityOutSchema

from core.functions import resource_path
from requests.auth import HTTPDigestAuth
from config.CONSTANTS import none_request_message


class Server(BaseHTTPRequestHandler):

    message = None
    inMessage = None
    outMessage = None
    inSchema = None
    outSchema = None
    webhookData = None  # ✅ 웹훅 데이터 추가
    webhook_thread = None  # ✅ 웹훅 스레드 (클래스 변수)
    webhook_response = None  # ✅ 웹훅 응답 (클래스 변수)
    system = ""
    auth_type = "D"
    auth_Info = ['admin', '1234', 'user', 'abcd1234', 'SHA-256', None]  # 저장된 상태로 main 입력하지 않으면 digest auth 인증 x
    digest_res = ""
    transProtocolInput = ""

    url_tmp = None

    trace = defaultdict(lambda: deque(maxlen=1000))  # api_name -> deque(events)
    request_counter = {}  # ✅ API별 시스템 요청 카운터 (클래스 변수)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = ""
        self.webhook_flag = False

    def _push_event(self, api_name, direction, payload):
        try:
            evt = {
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "api": api_name,
                "dir": direction,  # "REQUEST" | "RESPONSE" | "WEBHOOK"
                "data": payload
            }
            self.trace[api_name].append(evt)
            os.makedirs(CONSTANTS.trace_path, exist_ok=True)
            safe_api = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(api_name))
            trace_path = os.path.join(CONSTANTS.trace_path, f"trace_{safe_api}.ndjson")
            with open(trace_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(evt, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _set_headers(self):
        self.send_response(200, None)
        self.send_header('Content-type', 'application/json')
        self.send_header('User-Agent', 'test')
        self.end_headers()

    def _set_digest_headers(self):
        auth = HTTPDigestAuth(self.auth_Info[0], self.auth_Info[1])
        auth.init_per_thread_state()
        auth._thread_local.chal = {'realm': self.auth_Info[2], 'nonce': self.auth_Info[3],
                                   'algorithm': self.auth_Info[4]}
        auth._thread_local.chal['qop'] = None  # 'auth'
        auth._thread_local.chal['opaque'] = 'abcd1234'
        auth_opaque = auth._thread_local.chal.get("opaque")
        self.send_response(401, None)
        self.send_header('Content-type', 'application/json')
        self.send_header('User-Agent', 'test')
        digest_temp = auth.build_digest_header('POST', self.path)
        temp = []
        digest_temp = digest_temp.split(" ")
        for i in digest_temp:
            temp.append(i.split("="))
        for i in temp:
            if i[0] == "response":
                self.auth_Info[-1] = i[1].replace('"', '').replace(',', '')
        if auth_opaque is not None:
            digest_header = 'Digest' + ' ' + 'realm="' + self.auth_Info[2] + '",' + ' ' + 'nonce="' + \
                            self.auth_Info[3] + '",' + ' ' + 'opaque="' + auth_opaque + '",' + 'algorithm="' + \
                            self.auth_Info[4] + '"'

        else:
            digest_header = 'Digest' + ' ' + 'realm="' + self.auth_Info[2] + '",' + ' ' + 'nonce="' + \
                            self.auth_Info[3] + '",' + ' ' + 'algorithm="' + self.auth_Info[4] + '"'

        self.send_header('WWW-Authenticate', digest_header)
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        res_data = json.dumps({'hello': 'world', 'received': 'ok'})
        self._set_headers()
        self.wfile.write(res_data)

    # POST echoes the message adding a JSON field
    def do_POST(self):
        print(f"[DEBUG][SERVER] do_POST called, path={self.path}, auth_type={self.auth_type}, headers={dict(self.headers)}")
        ctype, pdict = cgi.parse_header(self.headers.get_content_type())
        auth = self.headers.get('Authorization')
        if auth is None:
            auth = self.headers.get('authorization')
        auth_pass = False
        message_cnt, data = self.api_res()
        
        # api_res()가 에러를 반환한 경우 (Server.message가 None)
        if message_cnt is None:
            self._set_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        if self.auth_type == "None":
            auth_pass = True
        else:
            # Digest Auth
            if self.auth_type == "D":
                import hashlib
                # 1) Authorization 없으면 → 401 챌린지
                if not auth:
                    self._set_digest_headers()
                    return
                # 2) 스킴 확인
                parts = auth.split(" ", 1)
                if parts[0] != "Digest":
                    self._set_digest_headers()
                    return
                # 3) response 추출 실패/불일치 → 401 챌린지
                try:
                    digest_header = parts[1]
                    digest_items = {}
                    for item in digest_header.split(','):
                        if '=' in item:
                            k, v = item.strip().split('=', 1)
                            digest_items[k.strip()] = v.strip().strip('"')
                    # 필수 파라미터 추출
                    username = digest_items.get('username')
                    realm = digest_items.get('realm')
                    nonce = digest_items.get('nonce')
                    uri = digest_items.get('uri')
                    qop = digest_items.get('qop')
                    nc = digest_items.get('nc')
                    cnonce = digest_items.get('cnonce')
                    response = digest_items.get('response')
                    method = self.command  # 'POST'
                    password = self.auth_Info[1] if hasattr(self, 'auth_Info') and self.auth_Info else ''
                    # SHA-256로 해시 계산 (RFC 7616, qop 없이)
                    def sha256_hex(s):
                        return hashlib.sha256(s.encode('utf-8')).hexdigest()
                    a1 = f"{username}:{realm}:{password}"
                    ha1 = sha256_hex(a1)
                    a2 = f"{method}:{uri}"
                    ha2 = sha256_hex(a2)
                    if qop and cnonce and nc:
                        expected_response = sha256_hex(f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}")
                    else:
                        expected_response = sha256_hex(f"{ha1}:{nonce}:{ha2}")
                    # 디버그 로그
                    print(f"[DEBUG][SERVER][Digest] client_response={response}, expected_response={expected_response}")
                    if not response or not expected_response or response != expected_response:
                        self._set_digest_headers()
                        return
                    auth_pass = True
                except Exception as e:
                    print(f"[DEBUG][SERVER][Digest] Exception: {e}")
                    self._set_digest_headers()
                    return
            # Bearer Auth
            elif self.auth_type == "B":
                print(f"[DEBUG][SERVER] Checking Bearer, auth={auth}")
                if auth:
                    auth_parts = auth.split(" ")
                    if len(auth_parts) > 1 and auth_parts[0] == 'Bearer':
                        token = auth_parts[1].replace('"', "").strip()
                        stored_token = None
                        if isinstance(self.auth_Info, list):
                            if self.auth_Info:
                                stored_token = self.auth_Info[0]
                        else:
                            stored_token = self.auth_Info

                        # 디버그 로그 추가: Bearer 토큰 비교 직전
                        print(f"[DEBUG][SERVER] Bearer token in header: {token}, stored_token: {stored_token}")

                        if stored_token is not None and token == str(stored_token).strip():
                            auth_pass = True
            # 기타: 특정 path 우회
            elif self.path == "/" + self.message[0]:
                auth_pass = True
        post_data = '{}'
        try:
            content_len = int(self.headers.get('Content-Length'))
            if content_len != 0:
                post_data = self.rfile.read(content_len)  # <--- Gets the data itself
        except:
            post_data = '{}'
        dict_data = json.loads(post_data)  # type(dict_data)는 <class 'dict'>

        try:
            self._push_event(self.path[1:], "REQUEST", dict_data)
        except Exception:
            pass

        # ✅ 플랫폼에 시스템 요청 도착 신호 보내기 (JSON 파일 대신)
        # 클래스 변수 request_counter 사용하여 API별 요청 횟수 추적
        try:
            api_name = self.path[1:]  # 예: "Authentication", "storedVideoInfos"
            if api_name not in Server.request_counter:
                Server.request_counter[api_name] = 0
            Server.request_counter[api_name] += 1
            print(f"[API_SERVER] 요청 수신: {api_name} (카운트: {Server.request_counter[api_name]})")
        except Exception as e:
            print(f"[API_SERVER] request_counter 에러: {e}")
            pass
        except Exception:
            pass

        #  refuse to receive non-json content
        if ctype == 'text/plain':
            for i in none_request_message:
                if self.path == "/" + i:
                    pass
                # else
        elif ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        self.webhook_flag = False
        message = ""
        url_tmp = ""  # ✅ 스코프 확장을 위해 먼저 선언
        webhook_url = ""  # ✅ 웹훅 URL 저장용
        
        if "Realtime".lower() in self.message[message_cnt].lower():
            print(f"[DEBUG][SERVER] Realtime API 감지: {self.message[message_cnt]}")
            trans_protocol = dict_data.get("transProtocol", {})
            print(f"[DEBUG][SERVER] transProtocol: {trans_protocol}")
            
            if trans_protocol:
                trans_protocol_type = trans_protocol.get("transProtocolType", {})
                print(f"[DEBUG][SERVER] transProtocolType: {trans_protocol_type}")
                
                # 동적으로 프로토콜 업데이트 해야함 (기존에는 롱풀링으로 하드코딩 - 10/14)
                self.transProtocolInput = str(trans_protocol_type)
                print(f"[DEBUG][SERVER] transProtocolInput 업데이트: {self.transProtocolInput}")
                
                if "WebHook".lower() in str(trans_protocol_type).lower():
                    print(f"[DEBUG][SERVER] WebHook 모드 감지, auth_pass={auth_pass}")
                    try:
                        url_tmp = trans_protocol.get("transProtocolDesc", {})
                        print(f"[DEBUG][SERVER] Webhook URL: {url_tmp}")
                        
                        # ✅ 인증 확인 추가
                        if not auth_pass:
                            print(f"[SERVER ERROR] 인증 실패!")
                            message = {
                                "code": "401",
                                "message": "인증 오류"
                            }
                            self._set_headers()
                            self.wfile.write(json.dumps(message).encode('utf-8'))
                            return
                        
                        # url 유효성 검사 -> 없거나 잘못되면 400
                        if not url_tmp or str(url_tmp).strip() in ["None", "", "desc"]:
                            print(f"[SERVER ERROR] Webhook URL이 유효하지 않음: {url_tmp}")
                            message = {
                                "code": "400",
                                "message": "잘못된 Webhook URL"
                            }
                            self._set_headers()
                            self.wfile.write(json.dumps(message).encode('utf-8'))
                            return
                        
                        # ✅ 올바른 인덱스 사용: message_cnt (현재 API)
                        message = self.outMessage[message_cnt]
                        self.webhook_flag = True
                        print(f"[DEBUG][SERVER] 웹훅 플래그 설정 완료, message={message}")
                        
                        # https 아니면 400
                        if "https".lower() not in url_tmp.lower():
                            print(f"[SERVER ERROR] Webhook URL이 HTTPS가 아님: {url_tmp}")
                            message = {
                                "code": "400",
                                "message": "잘못된 요청: HTTPS 필요"
                            }
                        # 웹훅인데 롱풀링으로 하려고 할 때 문제..?? 
                        if "longpolling" in str(self.transProtocolInput).lower():
                            print(f"[SERVER ERROR] transProtocolInput이 longpolling: {self.transProtocolInput}")
                            message = {
                                "code": "400",
                                "message": "잘못된 요청: 프로토콜 불일치"
                            }
                    except Exception as e:
                        print(f"[SERVER ERROR] WebHook 처리 중 예외 발생: {e}")
                        import traceback
                        traceback.print_exc()
                        message = {
                            "code": "400",
                            "message": f"잘못된 요청: {str(e)}"
                        }
                else:
                    # LongPolloing 인 경우
                    if auth_pass:
                        message = data
                        # LongPolloing 이면서 웹훅으로 하려고 할 때 문제
                        if "webhook".lower() in str(self.transProtocolInput).lower():
                            message = {
                                "code": "400",
                                "message": "잘못된 요청"
                            }
                    else:
                        # LongPolloing 이면서 인증 실패
                        message = {
                            "code": "401",
                            "message": "인증 오류"
                        }
            else:
                # webhook, LongPolloing 둘다 아닌 경우
                message = {
                    "code": "400",
                    "message": "잘못된 요청"
                }
        else:  # Realtime 메시지아니면서 Webhook 요청 없는 메시지
            if auth_pass:
                message = data
            else:
                message = {
                    "code": "401",
                    "message": "인증 오류"
                }
        # send the message back
        a = json.dumps(message).encode('utf-8')
        try:
            self._push_event(self.path[1:], "RESPONSE", message)
        except Exception:
            pass
        self._set_headers()
        self.wfile.write(a)

        if self.webhook_flag:
            print(f"[DEBUG][SERVER] 웹훅 전송 준비 중...")
            print(f"[DEBUG][SERVER] self.webhookData: {self.webhookData is not None}, len: {len(self.webhookData) if self.webhookData else 0}")
            print(f"[DEBUG][SERVER] message_cnt: {message_cnt}")
            print(f"[DEBUG][SERVER] url_tmp: {url_tmp}")
            
            # ✅ 웹훅 데이터 사용 (videoData_request.py의 webhookData)
            if self.webhookData and len(self.webhookData) > message_cnt:
                webhook_payload = self.webhookData[message_cnt]
                print(f"[DEBUG][SERVER] 웹훅 데이터 사용: webhookData[{message_cnt}]")
                
                # None이면 웹훅 전송하지 않음
                if webhook_payload is None:
                    print(f"[DEBUG][SERVER] 웹훅 데이터가 None, 웹훅 전송 건너뛰기")
                    return
            else:
                print(f"[DEBUG][SERVER] 웹훅 데이터 인덱스 범위 초과 또는 없음, 웹훅 전송 건너뛰기")
                return
            
            print(f"[DEBUG][SERVER] webhook_payload: {json.dumps(webhook_payload, ensure_ascii=False)[:200]}")
            
            # ✅ 웹훅 응답 초기화 (클래스 변수)
            Server.webhook_response = None
            
            json_data_tmp = json.dumps(webhook_payload).encode('utf-8')
            webhook_thread = threading.Thread(target=self.webhook_req, args=(url_tmp, json_data_tmp, 5))
            Server.webhook_thread = webhook_thread  # ✅ 클래스 변수에 저장
            print(f"[DEBUG][SERVER] webhook_thread 저장됨 (클래스 변수): thread={id(webhook_thread)}")
            webhook_thread.start()
            print(f"[DEBUG][SERVER] 웹훅 스레드 시작됨")

        #print("통플검증sw이 보낸 메시지", a)

    def webhook_req(self, url, json_data_tmp, max_retries=3):
        import requests
        for attempt in range(max_retries):

            try:
                result = requests.post(url, data=json_data_tmp, verify=False)
                print(f"[DEBUG][SERVER] 웹훅 응답 수신: {result.text}")
                self.result = result
                Server.webhook_response = json.loads(result.text)  # ✅ 클래스 변수에 저장
                print(f"[DEBUG][SERVER] webhook_response 저장됨 (클래스 변수): {Server.webhook_response}")
                # JSON 파일 저장 제거 - spec/video/videoData_response.py 사용
                # with open(resource_path("spec/" + self.system + "/" + "webhook_" + self.path[1:] + ".json"),
                #           "w", encoding="UTF-8") as out_file2:
                #     json.dump(json.loads(str(self.result.text)), out_file2, ensure_ascii=False)
                break
                #  self.res.emit(str(self.result.text))
            #except requests.ConnectionError:
            #    print("..")
            #    time.sleep(1)
            except Exception as e:
                print(e)
                #print(traceback.format_exc())
                #  self.res.emit(str("err from WebhookRequest"))

    def api_res(self):
        i, data = None, None
        # message가 None이거나 빈 리스트인 경우 방어 코드
        if not self.message:
            print("[ERROR] Server.message is None or empty!")
            return None, {"code": "500", "message": "Server not initialized"}
        
        for i in range(0, len(self.message)):
            data = ""
            if self.path == "/" + self.message[i]:
                data = self.outMessage[i]
                if i == 0 and self.auth_type == "B":
                    try:
                        token = data['accessToken']
                    except Exception:
                        pass
                    else:
                        if isinstance(self.auth_Info, list):
                            if not self.auth_Info:
                                self.auth_Info.append(None)
                            self.auth_Info[0] = str(token).strip()
                        else:
                            self.auth_Info = [str(token).strip()]
                break
        return i, data


# 확인용
def run(server_class=HTTPServer, handler_class=Server, address='127.0.0.1', port=8008, system="video"):
    server_address = (address, port)


    # if system == "video":
    #     Server.message = videoMessages
    #     Server.inMessage = videoInMessage
    #     Server.outMessage = videoOutMessage
    #     Server.inSchema = videoInSchema
    #     Server.outSchema = videoOutSchema

    # elif system == "bio":
    #     Server.message = bioMessages
    #     Server.inMessage = bioInMessage
    #     Server.outMessage = bioOutMessage
    #     Server.inSchema = bioInSchema
    #     Server.outSchema = bioOutSchema

    # elif system == "security":
    #     Server.message = securityMessages
    #     Server.inMessage = securityInMessage
    #     Server.outMessage = securityOutMessage
    #     Server.inSchema = securityInSchema
    #     Server.outSchema = securityOutSchema

    certificate_private = resource_path('config/key0627/server.crt')
    certificate_key = resource_path('config/key0627/server.key')
    httpd = server_class(server_address, handler_class)
    httpd.socket = ssl.wrap_socket(httpd.socket,  certfile=certificate_private,
                                   keyfile=certificate_key, server_side=True)
    print('Starting https on port %d...' % port)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()