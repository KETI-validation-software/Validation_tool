import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import ssl
import json
import cgi
from collections import defaultdict, deque  # ### NEW
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
from core.data_mapper import ConstraintDataGenerator
from requests.auth import HTTPDigestAuth
from config.CONSTANTS import none_request_message
from collections import defaultdict

import random


class Server(BaseHTTPRequestHandler):
    message = None
    inMessage = None
    outMessage = None
    outCon = None
    inSchema = None
    outSchema = None
    webhookData = None  # ✅ 웹훅 데이터 추가
    webhook_thread = None  # ✅ 웹훅 스레드 (클래스 변수)
    webhook_response = None  # ✅ 웹훅 응답 (클래스 변수)
    webhookCon = None
    system = ""
    auth_type = "D"
    auth_Info = ['admin', '1234', 'user', 'abcd1234', 'SHA-256', None]  # 저장된 상태로 main 입력하지 않으면 digest auth 인증 x
    digest_res = ""
    transProtocolInput = ""
    #bearer_credentials = ['PlatformID','PlatformPW']
    bearer_credentials = ['user0001', 'pass0001']
    url_tmp = None
    current_spec_id = None

    trace = defaultdict(lambda: deque(maxlen=1000))  # api_name -> deque(events)
    request_counter = {}  # ✅ API별 시스템 요청 카운터 (클래스 변수)
    latest_event = defaultdict(dict)  # ✅ API별 최신 이벤트 저장 (클래스 변수)

    def __init__(self, *args, **kwargs):
        self.result = ""
        self.webhook_flag = False
        self.generator = ConstraintDataGenerator(Server.latest_event)  # ✅ 클래스 변수 참조

        # super().__init__()를 마지막에 호출 (이때 handle()이 실행되어 do_POST가 호출됨)
        super().__init__(*args, **kwargs)

    def _push_event(self, api_name, direction, payload):
        try:
            evt = {
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "api": api_name,
                "dir": direction,  # "REQUEST" | "RESPONSE" | "WEBHOOK"
                "data": payload
            }

            print(f"[_push_event] 저장 시도: api={api_name}, dir={direction}")
            print(f"[_push_event] 저장 전 latest_event 키: {list(Server.latest_event.keys())}")

            Server.trace[api_name].append(evt)  # ✅ 클래스 변수 사용
            Server.latest_event[api_name][direction] = evt  # ✅ 클래스 변수 사용

            print(f"[_push_event] 저장 후 latest_event 키: {list(Server.latest_event.keys())}")
            print(f"[_push_event] 저장된 데이터: {api_name} -> {list(Server.latest_event[api_name].keys())}")

            # 파일 쓰기는 선택적으로 (환경 변수나 설정으로 제어 가능)
            # 성능이 중요하면 주석 처리하거나 비동기로 처리
            if CONSTANTS.trace_path:  # trace_path가 설정되어 있을 때만 파일 쓰기
                try:
                    os.makedirs(CONSTANTS.trace_path, exist_ok=True)
                    safe_api = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(api_name))

                    # ✅ 1. 번호 없는 파일 (기존 방식)
                    trace_path = os.path.join(CONSTANTS.trace_path, f"trace_{safe_api}.ndjson")
                    with open(trace_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(evt, ensure_ascii=False) + "\n")

                    # ✅ 2. 번호 포함 파일 (systemVal_all.py 방식과 동일)
                    # Server.message에서 api_name의 인덱스 찾기
                    if hasattr(Server, 'message') and Server.message:
                        try:
                            step_idx = Server.message.index(api_name)
                            trace_path_with_num = os.path.join(CONSTANTS.trace_path, f"trace_{step_idx + 1:02d}_{safe_api}.ndjson")
                            with open(trace_path_with_num, "a", encoding="utf-8") as f:
                                f.write(json.dumps(evt, ensure_ascii=False) + "\n")
                        except ValueError:
                            # api_name이 message 리스트에 없는 경우 (예: webhook)
                            pass
                except Exception as e:
                    print(f"[_push_event] 파일 쓰기 실패: {e}")
        except Exception as e:
            print(f"[_push_event] ❌ 에러 발생: {e}")
            import traceback
            traceback.print_exc()

    def get_latest_event(self, api_name, direction="RESPONSE"):
        """
        메시지별 가장 최근 이벤트를 반환
        """
        direction = direction.upper()
        if api_name in Server.latest_event:  # ✅ 클래스 변수 사용
            return Server.latest_event[api_name].get(direction)  # ✅ 클래스 변수 사용
        return None

    # ========== 오류 검사 함수들 (400/201/404) ==========
    
    def _check_request_errors(self, api_name, request_data):
        """
        요청 데이터 오류 검사
        
        Returns:
            dict: 오류 응답 (오류 있을 때) 또는 None (정상)
        """
        # 해당 API의 스키마 가져오기
        schema = self._get_request_schema(api_name)
        if not schema:
            print(f"[ERROR_CHECK] 스키마를 찾을 수 없음: {api_name}")
            return None  # 스키마 없으면 검사 안 함
        
        # 1. 타입 불일치 검사 → 400
        type_error = self._check_type_mismatch(request_data, schema)
        if type_error:
            print(f"[ERROR_CHECK] 타입 불일치 감지: {type_error}")
            return {"code": "400", "message": "잘못된 요청"}
        
        # 2. 시간 구간 검사 → 201 (startTime, endTime 있는 API만)
        if "startTime" in request_data or "endTime" in request_data:
            time_error = self._check_time_range(request_data)
            if time_error:
                print(f"[ERROR_CHECK] 시간 범위 오류 감지: {time_error}")
                return {"code": "201", "message": "정보 없음"}
        
        # 3. 장치 존재 검사 → 404 (camID, camList 있는 API만)
        if "camID" in request_data or "camList" in request_data:
            device_error = self._check_device_exists(request_data)
            if device_error:
                print(f"[ERROR_CHECK] 장치 없음 감지: {device_error}")
                return {"code": "404", "message": "장치 없음"}
        
        return None  # 오류 없음

    def _get_request_schema(self, api_name):
        """API의 요청 스키마 가져오기"""
        try:
            if self.inSchema and self.message:
                for i, msg in enumerate(self.message):
                    if msg == api_name and i < len(self.inSchema):
                        return self.inSchema[i]
        except Exception as e:
            print(f"[ERROR] 스키마 가져오기 실패: {e}")
        return None

    def _check_type_mismatch(self, request_data, schema):
        """
        타입 불일치 검사
        
        Returns:
            str: 오류 필드명 (오류 있을 때) 또는 None (정상)
        """
        try:
            for field, expected_type in schema.items():
                # OptionalKey 처리
                field_name = field.key if hasattr(field, 'key') else field
                
                if field_name in request_data:
                    value = request_data[field_name]
                    
                    # None 값은 검사 스킵
                    if value is None:
                        continue
                    
                    # 타입 검사
                    if expected_type == str:
                        if not isinstance(value, str):
                            print(f"[TYPE_CHECK] {field_name}: expected str, got {type(value).__name__}")
                            return field_name
                    elif expected_type == int:
                        if not isinstance(value, int) or isinstance(value, bool):
                            print(f"[TYPE_CHECK] {field_name}: expected int, got {type(value).__name__}")
                            return field_name
                    elif expected_type == list:
                        if not isinstance(value, list):
                            print(f"[TYPE_CHECK] {field_name}: expected list, got {type(value).__name__}")
                            return field_name
                    elif expected_type == dict:
                        if not isinstance(value, dict):
                            print(f"[TYPE_CHECK] {field_name}: expected dict, got {type(value).__name__}")
                            return field_name
        except Exception as e:
            print(f"[ERROR] 타입 검사 중 오류: {e}")
        
        return None

    def _check_time_range(self, request_data):
        """
        시간 구간 검사 - 현재 시간 기준으로 과거 데이터 요청인지 확인
        
        Returns:
            str: 오류 메시지 (오류 있을 때) 또는 None (정상)
        """
        current_time = int(time.time())
        
        start_time = request_data.get("startTime")
        end_time = request_data.get("endTime")
        
        try:
            if start_time is not None and end_time is not None:
                # Unix timestamp로 가정 (정수형)
                # 2년 전보다 과거 데이터면 "정보 없음"
                two_years_ago = current_time - (2 * 365 * 24 * 60 * 60)
                
                if isinstance(start_time, int) and isinstance(end_time, int):
                    if end_time < two_years_ago:
                        return "시간 구간이 너무 과거입니다"
        except Exception as e:
            print(f"[ERROR] 시간 검사 실패: {e}")
        
        return None

    def _check_device_exists(self, request_data):
        """
        장치 존재 검사 - 유효한 camID인지 확인
        
        Returns:
            str: 오류 메시지 (오류 있을 때) 또는 None (정상)
        """
        # 유효한 카메라 ID 목록
        # TODO: 실제로는 DB나 설정에서 가져와야 함
        valid_cam_ids = ["cam001", "cam002", "keti", "camera1", "camera2"]
        
        # camID 검사
        cam_id = request_data.get("camID")
        if cam_id is not None:
            if cam_id not in valid_cam_ids:
                return f"존재하지 않는 장치: {cam_id}"
        
        # camList 검사
        cam_list = request_data.get("camList")
        if cam_list is not None and isinstance(cam_list, list):
            for cam in cam_list:
                cam_id_in_list = cam.get("camID") if isinstance(cam, dict) else cam
                if cam_id_in_list and cam_id_in_list not in valid_cam_ids:
                    return f"존재하지 않는 장치: {cam_id_in_list}"
        
        return None

    # ========== 오류 검사 함수들 끝 ==========

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
        print(f"[DEBUG][DIGEST] 401 전송 완료")
        print(f"[DEBUG][DIGEST] Digest Header: {digest_header}")
        print(f"[DEBUG][DIGEST] 클라이언트가 재요청을 보내야 합니다")
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
        spec_id, api_name = self.parse_path()
        if not api_name or self.current_spec_id!=spec_id:#"cmgyv3rzl014nvsveidu5jpzp" != spec_id:
            print(f"[ERROR] 잘못된 path 형식: {self.path}")
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = json.dumps({"code": "400", "message": "잘못된 URL 형식"})
            self.wfile.write(error_msg.encode('utf-8'))
            return
        print(
            f"[DEBUG][SERVER] do_POST called, path={self.path}, auth_type={self.auth_type}, headers={dict(self.headers)}")
        ctype, pdict = cgi.parse_header(self.headers.get_content_type())

        # ✅ 1단계: 요청 본문 먼저 읽기 (self.request_data 생성)
        # ✅ 1단계: 요청 본문 먼저 읽기
        content_length = int(self.headers.get('Content-Length', 0))
        print(f"[DEBUG][SERVER] Content-Length: {content_length}")
        if content_length > 0:
            request_body = self.rfile.read(content_length)
            print(f"[DEBUG][SERVER] 요청 본문 읽음: {len(request_body)} bytes")
            try:
                self.request_data = json.loads(request_body.decode('utf-8'))
                print(f"[DEBUG][SERVER] 파싱된 요청 데이터: {self.request_data}")

                # ✅ API 이름으로 로깅 (spec_id 제외)
                print(f"[TRACE WRITE] API 이름: {api_name}")
                print(f"[TRACE WRITE] spec_id: {spec_id}")
                print(f"[TRACE WRITE] Direction: REQUEST")

                print(f"[TRACE WRITE] ✅ trace 파일에 저장 완료")
                print(f"[TRACE WRITE] latest_event 키 목록: {list(Server.latest_event.keys())}")
            except Exception as e:
                print(f"[ERROR] 요청 본문 파싱 실패: {e}")
                self.request_data = {}
        else:
            print(f"[DEBUG][SERVER] 요청 본문 없음 (Content-Length=0)")
            self.request_data = {}

        # ✅ 2단계: Authentication API 특별 처리 (Bearer Token 발급)
        if api_name == "Authentication" and self.auth_type == "B":
            print(f"[DEBUG][AUTH] Bearer 인증 시작 - userID/userPW 검증")

            # 요청 본문에서 자격 증명 추출
            user_id = self.request_data.get('userID', '')
            user_pw = self.request_data.get('userPW', '')

            print(f"[DEBUG][AUTH] 요청 userID: {user_id}")
            print(f"[DEBUG][AUTH] 요청 userPW: {user_pw}")

            # 자격 증명 검증
            if (user_id == Server.bearer_credentials[0] and
                    user_pw == Server.bearer_credentials[1]):

                print(f"[DEBUG][AUTH] ✅ 자격 증명 검증 성공!")

                # ✅ request_counter 증가 (return 전에!)
                if api_name not in Server.request_counter:
                    Server.request_counter[api_name] = 0
                Server.request_counter[api_name] += 1
                print(f"[API_SERVER] 요청 수신: {api_name} (카운트: {Server.request_counter[api_name]})")

                # 토큰 생성 및 저장
                import uuid
                import time
                new_token = f"{uuid.uuid4().hex}_{int(time.time())}"
                if not isinstance(Server.auth_Info, list):
                    Server.auth_Info = []
                if len(Server.auth_Info) == 0:
                    Server.auth_Info.append(None)
                Server.auth_Info[0] = str(new_token).strip()

                print(f"[DEBUG][AUTH] Bearer 토큰 저장 완료: {new_token}")

                # api_res() 호출하여 응답 데이터 가져오기
                message_cnt, data, out_con = self.api_res(api_name)

                if message_cnt is None:
                    self._set_headers()
                    self.wfile.write(json.dumps(data).encode('utf-8'))
                    return

                # ========== 오류 검사 전 REQUEST 이벤트 기록 ==========
                self._push_event(api_name, "REQUEST", self.request_data)
                # ===================================================

                # ========== Authentication API도 오류 검사 (400/201/404) ==========
                error_response = self._check_request_errors(api_name, self.request_data)
                if error_response:
                    print(f"[DEBUG][SERVER] Authentication 오류 감지: {error_response}")
                    self._push_event(api_name, "RESPONSE", error_response)
                    self._set_headers()
                    self.wfile.write(json.dumps(error_response).encode('utf-8'))
                    return
                # ================================================================

                # 응답에 토큰 포함
                if isinstance(data, dict):
                    data = data.copy()
                    data['accessToken'] = new_token
                    print(f"[DEBUG][AUTH] ✅ 응답에 토큰 포함")

                # 성공 응답 전송
                try:
                    self._push_event(api_name, "REQUEST", self.request_data)
                    self._push_event(api_name, "RESPONSE", data)
                    response_json = json.dumps(data).encode('utf-8')
                    self._set_headers()
                    self.wfile.write(response_json)
                    print(f"[DEBUG][AUTH] ✅ 인증 성공 응답 전송 완료")
                except Exception as e:
                    print(f"[ERROR] 응답 전송 중 오류: {e}")
                    import traceback
                    traceback.print_exc()
                return

            else:
                print(f"[DEBUG][AUTH] ❌ 자격 증명 불일치!")

                # ✅ 실패 시에도 카운터 증가
                if api_name not in Server.request_counter:
                    Server.request_counter[api_name] = 0
                Server.request_counter[api_name] += 1
                print(f"[API_SERVER] 요청 수신: {api_name} (카운트: {Server.request_counter[api_name]})")

                error_response = {
                    "code": "401",
                    "message": "인증 실패: 잘못된 사용자 ID 또는 비밀번호"
                }
                self._push_event(api_name, "RESPONSE", error_response)
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_msg = json.dumps(error_response)
                self.wfile.write(error_msg.encode('utf-8'))
                return

        # ✅ 3단계: 기존 인증 로직 (Bearer Token 검증 / Digest Auth)
        auth = self.headers.get('Authorization')
        if auth is None:
            auth = self.headers.get('authorization')
        auth_pass = False

        # api_res() 호출 (Authentication이 아닌 경우)
        message_cnt, data, out_con = self.api_res(api_name)

        # api_res()가 에러를 반환한 경우
        if message_cnt is None:
            self._set_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        # ========== 오류 검사 전 REQUEST 이벤트 기록 및 카운터 증가 ==========
        self._push_event(api_name, "REQUEST", self.request_data)
        
        # 클래스 변수 request_counter 사용하여 API별 요청 횟수 추적
        try:
            if api_name not in Server.request_counter:
                Server.request_counter[api_name] = 0
            Server.request_counter[api_name] += 1
            print(f"[API_SERVER] 요청 수신: {api_name} (카운트: {Server.request_counter[api_name]})")
        except Exception as e:
            print(f"[API_SERVER] request_counter 에러: {e}")
        # ================================================================

        # ========== 오류 검사 로직 (400/201/404) ==========
        # ✅ api_res() 호출 후에 검사 (self.message, self.inSchema가 설정된 후)
        error_response = self._check_request_errors(api_name, self.request_data)
        if error_response:
            print(f"[DEBUG][SERVER] 오류 감지: {error_response}")
            self._push_event(api_name, "RESPONSE", error_response)
            self._set_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            return
        # ================================================

        if self.auth_type == "None":
            auth_pass = True
        elif api_name == "Authentication":
            print(f"[DEBUG][AUTH] Authentication API - 인증 건너뛰기")
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
                # 3) response 추출 및 검증
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

                    # password 가져오기
                    password = ''
                    if isinstance(Server.auth_Info, list) and len(Server.auth_Info) > 1:
                        password = Server.auth_Info[1]

                    # SHA-256로 해시 계산
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

            # Bearer Auth (다른 API들)
            elif self.auth_type == "B":
                print(f"[DEBUG][SERVER] Bearer 토큰 검증 시작")

                # 1단계: Authorization 헤더 존재 확인
                if not auth:
                    print(f"[DEBUG][SERVER][AUTH] ❌ Authorization 헤더 없음!")
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('WWW-Authenticate', 'Bearer realm="API"')
                    self.end_headers()
                    error_msg = json.dumps({"code": "401", "message": "인증 헤더 누락"})
                    self.wfile.write(error_msg.encode('utf-8'))
                    return

                # 2단계: Bearer 스킴 확인
                auth_parts = auth.split(" ", 1)
                if len(auth_parts) != 2 or auth_parts[0] != 'Bearer':
                    print(f"[DEBUG][SERVER][AUTH] ❌ 잘못된 인증 스킴: {auth_parts[0] if auth_parts else 'None'}")
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('WWW-Authenticate', 'Bearer realm="API"')
                    self.end_headers()
                    error_msg = json.dumps({"code": "401", "message": "잘못된 인증 스킴"})
                    self.wfile.write(error_msg.encode('utf-8'))
                    return

                # 3단계: 토큰 추출
                token = auth_parts[1].strip().strip('"')

                # 4단계: 저장된 토큰 가져오기
                stored_token = Server.auth_Info[0]

                print(f"[DEBUG][SERVER] Bearer token in header: {token}")
                print(f"[DEBUG][SERVER] Stored token: {stored_token}")

                # 5단계: 토큰 비교
                if stored_token and token == str(stored_token).strip():
                    print(f"[DEBUG][SERVER][AUTH] ✅ Bearer 토큰 인증 성공!")
                    auth_pass = True
                else:
                    print(f"[DEBUG][SERVER][AUTH] ❌ Bearer 토큰 불일치!")
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('WWW-Authenticate', 'Bearer realm="API", error="invalid_token"')
                    self.end_headers()
                    error_msg = json.dumps({"code": "401", "message": "유효하지 않은 토큰"})
                    self.wfile.write(error_msg.encode('utf-8'))
                    return

            # 특정 path 우회
            elif self.path == "/" + self.message[0]:
                auth_pass = True

        # ✅ 요청 본문은 이미 do_POST 시작 부분에서 self.request_data에 저장됨
        # 중복 읽기 방지를 위해 이미 저장된 데이터 사용
        dict_data = self.request_data
        print(f"[DEBUG][SERVER] dict_data 사용: {dict_data}")

        # 클래스 변수 request_counter 사용하여 API별 요청 횟수 추적
        try:
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

        # do_POST 함수 출신 - 지금은 realtime이라는 단어가 들어간 api에 한해서 웹훅 하는걸로 하드코딩 되어있음
        if "Realtime".lower() in self.message[message_cnt].lower():
            print(f"[DEBUG][SERVER] Realtime API 감지: {self.message[message_cnt]}")
            trans_protocol = dict_data.get("transProtocol", {})
            print(f"[DEBUG][SERVER] transProtocol: {trans_protocol}")

            # transProtocol이 데이터에 없으면 constants에서 로드 시도
            if not trans_protocol:
                try:
                    for group in CONSTANTS.SPEC_CONFIG:
                        for spec_id, config in group.items():
                            if spec_id in ["group_name", "group_id"]:
                                continue
                        
                        trans_protocols = config.get('trans_protocol', [])
                        if message_cnt < len(trans_protocols):
                            protocol_type = trans_protocols[message_cnt]

                            if protocol_type == 'WebHook':
                                # ✅ CONSTANTS에서 웹훅 URL 가져오기 (10.252.219.95:8090)
                                webhook_url = CONSTANTS.WEBHOOK_URL
                                trans_protocol = {
                                    "transProtocolType": "WebHook",
                                    "transProtocolDesc": webhook_url
                                }
                                print(f"[DEBUG][SERVER] 기본 WebHook 프로토콜 설정: {webhook_url}")
                                break
                        if trans_protocol:
                            break
                except Exception as e:
                    print(f"[DEBUG][SERVER] constants에서 프로토콜 로드 실패: {e}")

            # transProtocol이 데이터에 들어가있으면 -> 지금 있어서 앞에 https 붙여주어야함 + 시스템이 보낼때 제대로 다시 맵핑하도록 수정해야함
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
                        
                        # 2단계: 잘못된 주소인 경우
                        url_tmp = str(url_tmp).strip()

                        # 4단계: 올바른 인덱스 사용
                        message = self.outMessage[message_cnt]

                        print("!!! update message", message)
                        self.webhook_flag = True
                        print(f"[DEBUG][SERVER] 웹훅 플래그 설정 완료, message={message}")

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
        try:
            # constraints 디버그 로그
            print(f"[DEBUG][CONSTRAINTS] out_con type: {type(out_con)}")
            print(f"[DEBUG][CONSTRAINTS] out_con value: {out_con}")
            print(f"[DEBUG][CONSTRAINTS] out_con length: {len(out_con) if isinstance(out_con, dict) else 'N/A'}")
            print(f"[DEBUG][CONSTRAINTS] 원본 message 내용: {json.dumps(message, ensure_ascii=False)[:200]}")
            print(f"[DEBUG][CONSTRAINTS] ★ latest_event 키 목록: {list(Server.latest_event.keys())}")
            print(f"[DEBUG][CONSTRAINTS] ★ generator.latest_events 동일 객체?: {id(self.generator.latest_events) == id(Server.latest_event)}")
            self._push_event(api_name, "REQUEST", self.request_data)

            # constraints가 있을 때만 _applied_constraints 호출 (성능 최적화)
            if out_con and isinstance(out_con, dict) and len(out_con) > 0:
                print(f"[DEBUG][CONSTRAINTS] _applied_constraints 호출 예정")
                
                # ✅ generator의 latest_events를 명시적으로 업데이트 (참조 동기화)
                self.generator.latest_events = Server.latest_event
                print(f"[DEBUG][CONSTRAINTS] 🔄 generator.latest_events 동기화 완료: {list(self.generator.latest_events.keys())}")
                
                num_data = [random.randint(0, 9) for _ in range(3)]

                print(f"[DEBUG][CONSTRAINTS] request_data: {self.request_data}")
                print(f"[DEBUG][CONSTRAINTS] message keys: {message.keys() if isinstance(message, dict) else 'N/A'}")

                # request_data, template_data, constraints, n 순서로 전달
                updated_message = self.generator._applied_constraints(
                    request_data=self.request_data,
                    template_data=message,  # copy() 제거 - 성능 향상
                    constraints=out_con,
                    n=len(num_data)
                )
                print(f"[DEBUG][CONSTRAINTS] 업데이트된 message 내용: {json.dumps(updated_message, ensure_ascii=False)[:200]}")

                self._push_event(api_name, "RESPONSE", updated_message)

                # 업데이트된 메시지를 응답으로 전송
                a = json.dumps(updated_message).encode('utf-8')
            else:
                print(f"[DEBUG][CONSTRAINTS] constraints 없음 - 원본 메시지 사용")
                # constraints가 없으면 원본 메시지 그대로 사용

                self._push_event(api_name, "RESPONSE", message)
                a = json.dumps(message).encode('utf-8')
        except Exception as e:
            print(f"[ERROR] _applied_constraints 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
            # 에러 발생 시 원본 메시지 사용
            self._push_event(api_name, "REQUEST", self.request_data)
            self._push_event(api_name, "RESPONSE", message)
            a = json.dumps(message).encode('utf-8')

        # 응답 전송 (연결 끊김 에러 처리)
        try:
            self._set_headers()
            self.wfile.write(a)
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
            print(f"[WARNING] 클라이언트 연결 끊김: {e}")
            # 연결이 끊겼으므로 더 이상 처리하지 않음
            return
        except Exception as e:
            print(f"[ERROR] 응답 전송 중 오류: {e}")
            import traceback
            traceback.print_exc()

        if self.webhook_flag:
            print(f"[DEBUG][SERVER] 웹훅 전송 준비 중...")
            print(
                f"[DEBUG][SERVER] self.webhookData: {self.webhookData is not None}, len: {len(self.webhookData) if self.webhookData else 0}")
            print(f"[DEBUG][SERVER] message_cnt: {message_cnt}")
            print(f"[DEBUG][SERVER] url_tmp: {url_tmp}")

            # ✅ API 이름으로 webhookData 매칭
            if self.webhookData and len(self.webhookData) > 0:
                # 현재 API 이름 가져오기
                api_name = self.message[message_cnt]
                print(f"[DEBUG][SERVER] 현재 API: {api_name}")

                # 웹훅이 있는 API들만 필터링 (Realtime이 들어간 API)
                webhook_apis = [msg for msg in self.message if "Realtime" in msg]
                print(f"[DEBUG][SERVER] 웹훅 API 목록: {webhook_apis}")

                # 현재 API가 웹훅 API 목록에 있는지 확인
                if api_name not in webhook_apis:
                    print(f"[DEBUG][SERVER] '{api_name}'는 웹훅 API가 아님, 웹훅 전송 건너뛰기")
                    return

                # 웹훅 API 목록에서 현재 API의 인덱스 찾기
                webhook_index = webhook_apis.index(api_name)
                print(f"[DEBUG][SERVER] 웹훅 인덱스: {webhook_index}")

                # webhookData에서 해당 인덱스의 데이터 가져오기
                if webhook_index >= len(self.webhookData):
                    print(
                        f"[DEBUG][SERVER] webhookData 인덱스 범위 초과: {webhook_index} >= {len(self.webhookData)}, 웹훅 전송 건너뛰기")
                    return

                webhook_payload = self.webhookData[webhook_index]
                print(f"[DEBUG][SERVER] 웹훅 데이터 사용: webhookData[{webhook_index}]")
                print(
                    f"[DEBUG][SERVER] 원본 웹훅 페이로드: {json.dumps(webhook_payload, ensure_ascii=False) if webhook_payload else 'None'}")
                print(f"[DEBUG][SERVER] 원본 웹훅 페이로드 타입: {type(webhook_payload)}")
                print(f"[DEBUG][SERVER] 원본 웹훅 페이로드 내용 상세: {webhook_payload}")

                # None이면 웹훅 전송하지 않음
                if webhook_payload is None:
                    print(f"[DEBUG][SERVER] 웹훅 데이터가 None, 웹훅 전송 건너뛰기")
                    return

                # ✅ 웹훅에도 constraints 적용
                try:
                    # webhookCon 리스트가 있는 경우
                    if self.webhookCon and isinstance(self.webhookCon, list):
                        print(f"[DEBUG][WEBHOOK_CONSTRAINTS] self.webhookCon 타입: {type(self.webhookCon)}")
                        print(f"[DEBUG][WEBHOOK_CONSTRAINTS] self.webhookCon 길이: {len(self.webhookCon)}")

                        # webhookCon에서 해당 인덱스의 constraint 가져오기
                        if len(self.webhookCon) > webhook_index:
                            webhook_con = self.webhookCon[webhook_index]

                            if webhook_con and isinstance(webhook_con, dict) and len(webhook_con) > 0:
                                print(f"[DEBUG][WEBHOOK_CONSTRAINTS] 웹훅 constraints 적용 시작")
                                print(f"[DEBUG][WEBHOOK_CONSTRAINTS] webhook_con keys: {list(webhook_con.keys())}")
                                print(f"[DEBUG][WEBHOOK_CONSTRAINTS] latest_events keys: {list(Server.latest_event.keys())}")
                                
                                # ✅ generator의 latest_events를 명시적으로 업데이트 (참조 동기화)
                                self.generator.latest_events = Server.latest_event
                                print(f"[DEBUG][WEBHOOK_CONSTRAINTS] 🔄 generator.latest_events 동기화 완료")
                                
                                # 웹훅 페이로드에 constraints 적용
                                num_data = [random.randint(0, 9) for _ in range(3)]
                                webhook_payload = self.generator._applied_constraints(
                                    request_data=self.request_data,
                                    template_data=webhook_payload,
                                    constraints=webhook_con,
                                    n=len(num_data)
                                )
                                print(f"[DEBUG][WEBHOOK_CONSTRAINTS] constraints 적용 완료")
                                print(f"[DEBUG][WEBHOOK_CONSTRAINTS] 업데이트된 webhook_payload: {json.dumps(webhook_payload, ensure_ascii=False)[:300]}")
                            else:
                                print(f"[DEBUG][WEBHOOK_CONSTRAINTS] 웹훅 constraints가 비어있음 - 원본 페이로드 사용")
                        else:
                            print(
                                f"[DEBUG][WEBHOOK_CONSTRAINTS] webhookCon 인덱스 범위 초과: {webhook_index} >= {len(self.webhookCon)}")
                    else:
                        print(f"[DEBUG][WEBHOOK_CONSTRAINTS] webhookCon이 없거나 리스트가 아님")

                except Exception as e:
                    print(f"[ERROR][WEBHOOK_CONSTRAINTS] 웹훅 constraints 적용 중 오류: {e}")
                    import traceback
                    traceback.print_exc()
                    # 에러 발생 시 원본 페이로드 사용
                    pass

            else:
                print(f"[DEBUG][SERVER] webhookData가 없거나 비어있음, 웹훅 전송 건너뛰기")
                return

            print(f"[DEBUG][SERVER] 최종 webhook_payload: {json.dumps(webhook_payload, ensure_ascii=False)[:200]}")

            # ✅ 웹훅 이벤트 전송 기록 (trace) - constraints 적용 후의 페이로드 기록
            self._push_event(api_name, "WEBHOOK_OUT", webhook_payload)

            # ✅ 웹훅 응답 초기화 (클래스 변수)
            Server.webhook_response = None

            json_data_tmp = json.dumps(webhook_payload).encode('utf-8')
            webhook_thread = threading.Thread(target=self.webhook_req, args=(url_tmp, json_data_tmp, 5))
            Server.webhook_thread = webhook_thread  # ✅ 클래스 변수에 저장
            print(f"[DEBUG][SERVER] webhook_thread 저장됨 (클래스 변수): thread={id(webhook_thread)}")
            webhook_thread.start()
            print(f"[DEBUG][SERVER] 웹훅 스레드 시작됨")

        # print("통플검증sw이 보낸 메시지", a)

    def webhook_req(self, url, json_data_tmp, max_retries=3):
        import requests
        for attempt in range(max_retries):

            try:
                result = requests.post(url, data=json_data_tmp, verify=False)
                print(f"[DEBUG][SERVER] 웹훅 응답 수신: {result.text}")
                self.result = result
                Server.webhook_response = json.loads(result.text)  # ✅ 클래스 변수에 저장
                print(f"[DEBUG][SERVER] webhook_response 저장됨 (클래스 변수): {Server.webhook_response}")
                
                # ✅ 웹훅 응답 기록 (trace)
                spec_id, api_name = self.parse_path()
                self._push_event(api_name, "WEBHOOK_IN", Server.webhook_response)
                
                # JSON 파일 저장 제거 - spec/video/videoData_response.py 사용
                # with open(resource_path("spec/" + self.system + "/" + "webhook_" + self.path[1:] + ".json"),
                #           "w", encoding="UTF-8") as out_file2:
                #     json.dump(json.loads(str(self.result.text)), out_file2, ensure_ascii=False)
                break
                #  self.res.emit(str(self.result.text))
            # except requests.ConnectionError:
            #    print("..")
            #    time.sleep(1)
            except Exception as e:
                print(e)
                # print(traceback.format_exc())
                #  self.res.emit(str("err from WebhookRequest"))

    def api_res(self, api_name = None):
        i, data, out_con = None, None, None

        if not self.message:
            print("[ERROR] Server.message is None or empty!")
            return None, {"code": "500", "message": "Server not initialized"}, None

        for i in range(0, len(self.message)):
            if api_name == self.message[i]:
                data = self.outMessage[i]
                out_con = self.outCon[i]
                print(f"[DEBUG][API_RES] API 매칭 성공: {api_name} (index={i})")
                break

        if data is None:
            print(f"[WARNING][API_RES] API를 찾을 수 없음: {api_name}")
            return None, {"code": "404", "message": f"API를 찾을 수 없습니다: {api_name}"}, None

        return i, data, out_con

    def parse_path(self):
        """
        URL path를 파싱하여 spec_id와 api_name을 추출

        지원 형식:
        1. /spec_id/api_name  (예: /cmgvieyak001b6cd04cgaawmm/Authentication)
        2. /test_name/api_name (예: /test_video_001/Authentication - test_name을 spec_id로 변환)
        3. /api_name          (예: /Authentication - 하위 호환성)

        Returns:
            tuple: (spec_id, api_name) 또는 (None, api_name)
        """
        try:
            path = self.path.strip('/')

            # path가 비어있으면
            if not path:
                return None, None

            # '/'로 분리
            parts = path.split('/')

            if len(parts) >= 2:
                # 형식 1/2: /spec_id_or_test_name/api_name
                spec_id_or_name = parts[0]
                api_name = parts[1]
                
                # ✅ test_name을 spec_id로 변환 시도
                actual_spec_id = self._resolve_spec_id(spec_id_or_name)
                
                print(f"[DEBUG][PARSE_PATH] 입력={spec_id_or_name}, 변환={actual_spec_id}, api_name={api_name}")
                return actual_spec_id, api_name
            elif len(parts) == 1:
                # 형식 3: /api_name (하위 호환성)
                api_name = parts[0]
                print(f"[DEBUG][PARSE_PATH] api_name={api_name} (spec_id 없음)")
                return None, api_name
            else:
                return None, None

        except Exception as e:
            print(f"[ERROR][PARSE_PATH] path 파싱 실패: {e}")
            return None, None

    def _resolve_spec_id(self, spec_id_or_name):
        """
        test_name 또는 spec_id를 실제 spec_id로 변환
        
        Args:
            spec_id_or_name: URL에서 추출한 spec_id 또는 test_name
            
        Returns:
            str: 실제 spec_id (변환 실패 시 원본 반환)
        """
        try:
            # ✅ 1. 이미 spec_id 형식이면 그대로 반환 (cm으로 시작하는 cuid)
            if spec_id_or_name.startswith('cm') and len(spec_id_or_name) == 25:
                return spec_id_or_name
            
            # ✅ 2. CONSTANTS에서 SPEC_CONFIG 로드
            import config.CONSTANTS as CONSTANTS
            import sys
            import os
            
            SPEC_CONFIG = getattr(CONSTANTS, 'SPEC_CONFIG', [])
            
            # PyInstaller 환경에서 외부 CONSTANTS.py 로드
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                external_constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
                
                if os.path.exists(external_constants_path):
                    with open(external_constants_path, 'r', encoding='utf-8') as f:
                        constants_code = f.read()
                    
                    namespace = {'__file__': external_constants_path}
                    exec(constants_code, namespace)
                    SPEC_CONFIG = namespace.get('SPEC_CONFIG', SPEC_CONFIG)
            
            # ✅ 3. test_name으로 spec_id 찾기
            for group in SPEC_CONFIG:
                for key, value in group.items():
                    if key in ['group_name', 'group_id']:
                        continue
                    if isinstance(value, dict):
                        test_name = value.get('test_name', '')
                        if test_name == spec_id_or_name:
                            print(f"[RESOLVE] test_name '{spec_id_or_name}' → spec_id '{key}'")
                            return key
            
            # ✅ 4. 변환 실패 시 원본 반환
            print(f"[RESOLVE] '{spec_id_or_name}' 변환 실패, 원본 사용")
            return spec_id_or_name
            
        except Exception as e:
            print(f"[ERROR][RESOLVE] spec_id 변환 실패: {e}")
            return spec_id_or_name


# 확인용 - 안쓰이는 코드임
def run(server_class=HTTPServer, handler_class=Server, address='127.0.0.1', port=8008, system="video"):
    server_address = (address, port)
    certificate_private = resource_path('config/key0627/server.crt')
    certificate_key = resource_path('config/key0627/server.key')
    httpd = server_class(server_address, handler_class)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=certificate_private,
                                   keyfile=certificate_key, server_side=True)
    print('Starting https on port %d...' % port)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()