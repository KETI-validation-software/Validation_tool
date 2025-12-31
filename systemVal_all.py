# 시스템 검증 소프트웨어
# physical security integrated system validation software
import os
import time
import threading
import json
import requests
import sys
import urllib3
import warnings
from datetime import datetime
from collections import defaultdict
import importlib
# SSL 경고 비활성화 (자체 서명 인증서 사용 시)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

import re
from urllib.parse import urlparse
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor, QPixmap
from PyQt5.QtCore import *
from PyQt5 import QtCore
from api.webhook_api import WebhookThread
from api.api_server import Server  # ✅ door_memory 접근을 위한 import 추가
from core.json_checker_new import timeout_field_finder
from core.functions import json_check_, resource_path, json_to_data, build_result_json
from core.data_mapper import ConstraintDataGenerator
from ui.splash_screen import LoadingPopup
from ui.detail_dialog import CombinedDetailDialog
from ui.gui_utils import CustomDialog
from ui.api_selection_dialog import APISelectionDialog
from ui.result_page import ResultPageWidget
from ui.system_main_ui import SystemMainUI
from core.system_state_manager import SystemStateManager
from requests.auth import HTTPDigestAuth
import config.CONSTANTS as CONSTANTS
from core.validation_registry import get_validation_rules
from pathlib import Path
import spec.Data_request as data_request_module
import spec.Schema_response as schema_response_module
import spec.Constraints_request as constraints_request_module

importlib.reload(data_request_module)
importlib.reload(schema_response_module)
importlib.reload(constraints_request_module)

result_dir = os.path.join(os.getcwd(), "results")
os.makedirs(result_dir, exist_ok=True)
class MyApp(SystemMainUI):
    # 시험 결과 표시 요청 시그널 (main.py와 연동)
    showResultRequested = pyqtSignal(object)  # parent widget을 인자로 전달

    def _load_from_trace_file(self, api_name, direction="RESPONSE"):
        """Trace 파일에서 최신 이벤트 데이터 로드"""
        try:
            # API 이름에서 슬래시 제거
            api_name_clean = api_name.lstrip("/")
            
            print(f"[DEBUG] trace 파일 찾기: api_name={api_name}, direction={direction}")
            
            # trace 디렉토리의 모든 파일 검색
            trace_dir = Path(CONSTANTS.trace_path)
            if not trace_dir.exists():
                print(f"[DEBUG] trace 디렉토리 없음: {trace_dir}")
                return None
            
            # API 이름과 매칭되는 파일 찾기
            # 우선순위: 1) 번호 있는 파일 → 2) 번호 없는 파일
            safe_api = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(api_name_clean))
            
            trace_file = None
            
            # ✅ 우선순위 1: 번호 prefix 포함된 형식 찾기 (trace_XX_API.ndjson)
            numbered_files = list(trace_dir.glob(f"trace_*_{safe_api}.ndjson"))
            if numbered_files:
                # 번호가 있는 파일 중 가장 최근 파일 사용
                trace_file = max(numbered_files, key=lambda f: f.stat().st_mtime)
                print(f"[DEBUG] 번호 있는 trace 파일 발견: {trace_file.name}")
            
            # ✅ 우선순위 2: 번호 없는 형식 찾기 (trace_API.ndjson)
            if not trace_file:
                unnumbered_files = list(trace_dir.glob(f"trace_{safe_api}.ndjson"))
                if unnumbered_files:
                    # 번호 없는 파일 중 가장 최근 파일 사용
                    trace_file = max(unnumbered_files, key=lambda f: f.stat().st_mtime)
                    print(f"[DEBUG] 번호 없는 trace 파일 발견: {trace_file.name}")
            
            if not trace_file:
                print(f"[DEBUG] trace 파일 없음 (패턴: trace_*_{safe_api}.ndjson 또는 trace_{safe_api}.ndjson)")
                return None
            
            print(f"[DEBUG] 사용할 trace 파일: {trace_file.name}")

            # 파일에서 가장 최근의 해당 direction 이벤트 찾기
            latest_event = None
            with open(trace_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        # direction만 확인 (api는 이미 파일명으로 필터링됨)
                        if event.get("dir") == direction:
                            latest_event = event
                    except json.JSONDecodeError:
                        continue

            if latest_event:
                # latest_events 업데이트 - 여러 키 형식으로 저장
                api_key = latest_event.get("api", api_name)
                
                # ✅ 1. 원본 API 이름으로 저장
                if api_key not in self.latest_events:
                    self.latest_events[api_key] = {}
                self.latest_events[api_key][direction] = latest_event
                
                # ✅ 2. 슬래시 제거한 형식으로도 저장 (예: "CameraProfiles")
                api_key_clean = api_key.lstrip('/')
                if api_key_clean not in self.latest_events:
                    self.latest_events[api_key_clean] = {}
                self.latest_events[api_key_clean][direction] = latest_event
                
                # ✅ 3. 슬래시 포함한 형식으로도 저장 (예: "/CameraProfiles")
                api_key_with_slash = f"/{api_key_clean}" if not api_key_clean.startswith('/') else api_key_clean
                if api_key_with_slash not in self.latest_events:
                    self.latest_events[api_key_with_slash] = {}
                self.latest_events[api_key_with_slash][direction] = latest_event
                
                print(f"[DEBUG] trace 파일에서 {api_name} {direction} 데이터 로드 완료")
                print(f"[DEBUG] latest_events에 저장된 키들: {api_key}, {api_key_clean}, {api_key_with_slash}")
                return latest_event.get("data")
            else:
                print(f"[DEBUG] trace 파일에서 {api_name} {direction} 데이터 없음")
                return None

        except Exception as e:
            print(f"[ERROR] trace 파일 로드 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    # 
    def _apply_request_constraints(self, request_data, cnt):
        """
        이전 응답 데이터를 기반으로 요청 데이터 업데이트
        - inCon (request constraints)을 사용하여 이전 endpoint 응답에서 값 가져오기
        """
        try:
            # constraints 가져오기
            # if cnt >= len(self.inCon) or not self.inCon[cnt]:
            #     print(f"[DATA_MAPPER] constraints 없음 (cnt={cnt})")
            #     return request_data

            # constraints = self.inCon[cnt]

            # if not constraints or not isinstance(constraints, dict):
            #     print(f"[DATA_MAPPER] constraints가 비어있거나 dict가 아님")
            #     return request_data
            # constraints 가져오기
            if cnt >= len(self.inCon) or not self.inCon[cnt]:
                # constraints가 없더라도 강제 로드 로직은 타야 하므로 바로 리턴하지 않고 빈 dict 할당
                constraints = {}
            else:
                constraints = self.inCon[cnt]

            if not isinstance(constraints, dict):
                constraints = {}

            # print(f"[DATA_MAPPER] 요청 데이터 업데이트 시작 (API: {self.message[cnt]})")
            # print(f"[DATA_MAPPER] constraints: {list(constraints.keys())}")

            required_endpoints = set()

            for field, rule in constraints.items():
                if isinstance(rule, dict):
                    ref_endpoint = rule.get("referenceEndpoint")
                    if ref_endpoint:
                        required_endpoints.add(ref_endpoint.lstrip('/'))

            for endpoint in required_endpoints:
                if endpoint not in self.latest_events or "RESPONSE" not in self.latest_events.get(endpoint, {}):
                    print(f"[DATA_MAPPER] trace 파일에서 {endpoint} RESPONSE 로드 시도")
                    self._load_from_trace_file(endpoint, "RESPONSE")
                else:
                    print(f"[DATA_MAPPER] latest_events에 이미 {endpoint} RESPONSE 존재")
            
            api_name = self.message[cnt] if cnt < len(self.message) else ""

            # 둘 다 무조건 맵핑 되어야 함
            if "RealtimeDoorStatus" in api_name:
                if "DoorProfiles" not in self.latest_events or "RESPONSE" not in self.latest_events.get("DoorProfiles", {}):
                    print(f"[DATA_MAPPER] RealtimeDoorStatus용 DoorProfiles RESPONSE 로드 시도")
                    self._load_from_trace_file("DoorProfiles", "RESPONSE")
            
            self.generator.latest_events = self.latest_events

            updated_request = self.generator._applied_constraints(
                request_data={},  # 이전 요청 데이터는 필요 없음
                template_data=request_data.copy(),  # 현재 요청 데이터를 템플릿으로
                constraints=constraints,
                api_name=api_name,  # ✅ API 이름 전달
                door_memory=Server.door_memory  # ✅ 문 상태 저장소 전달
            )

            # print(f"[DATA_MAPPER] 요청 데이터 업데이트 완료")
            # print(f"[DATA_MAPPER] 업데이트된 필드: {list(updated_request.keys())}")
            self.resp_rules = get_validation_rules(
                spec_id=self.current_spec_id,
                api_name=self.message[self.cnt] if self.cnt < len(self.message) else "",
                direction="out"  # 응답 검증

            )
            try:
                code_value = self.resp_rules.get("code")
                allowed_value = code_value.get("allowedValues", [])[0]
                updated_request = self.generator._applied_codevalue(
                    request_data=updated_request,
                    allowed_value=allowed_value
                )
                return updated_request
            except :
                return updated_request
        except Exception as e:
            print(f"[ERROR] _apply_request_constraints 실행 중 오류: {e}")
            import traceback
            
            return request_data

    def _load_from_trace_file_OLD(self, api_name, direction="RESPONSE"):
        try:
            trace_file = Path("results/trace") / f"trace_{api_name.replace('/', '_')}.ndjson"

            if not trace_file.exists():
                return None  # 파일이 없으면 None 반환

            latest_data = None

            with open(trace_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)

                        if entry.get("dir") == direction and entry.get("api") == api_name:
                            latest_data = entry.get("data", {})

                    except json.JSONDecodeError:
                        continue

            if latest_data:
                print(f"[DEBUG] trace 파일에서 {api_name} {direction} 데이터 로드 완료")
                return latest_data
            else:
                print(f"[DEBUG] trace 파일에서 {api_name} {direction} 데이터 없음")
                return None

        except Exception as e:
            print(f"[ERROR] trace 파일 로드 중 오류: {e}")
            return None

    def _append_text(self, obj):
        import json
        try:
            if isinstance(obj, (dict, list)):
                self.valResult.append(json.dumps(obj, ensure_ascii=False, indent=2))
            else:
                self.valResult.append(str(obj))
        except Exception as e:
            self.valResult.append(f"[append_error] {e}")

    def handle_authentication_response(self, res_data):
        """Handles the response for the Authentication step, updates token if present."""
        # Fix: Use 'accessToken' key, not 'token'
        if isinstance(res_data, dict):
            token = res_data.get("accessToken")
            if token:
                self.token = token
                # print(f"[DEBUG] [handle_authentication_response] Token updated: {self.token}")

    def __init__(self, embedded=False, spec_id=None):
        # ===== 수정: instantiation time에 CONSTANTS를 fresh import =====
        # PyInstaller 환경에서는 절대 경로로 직접 로드
        import sys
        import os
        self.run_status = "진행전"

        # ✅ 분야별 점수 (현재 spec만)
        self.current_retry = 0
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.total_opt_pass_cnt = 0  # 선택 필드 통과 수
        self.total_opt_error_cnt = 0  # 선택 필드 에러 수

        # ✅ 전체 점수 (모든 spec 합산) - 추가
        self.global_pass_cnt = 0
        self.global_error_cnt = 0
        self.global_opt_pass_cnt = 0  # 전체 선택 필드 통과 수
        self.global_opt_error_cnt = 0  # 전체 선택 필드 에러 수

        # ✅ 각 spec_id별 테이블 데이터 저장 (시나리오 전환 시 결과 유지) - 추가
        self.spec_table_data = {}  # {spec_id: {table_data, step_buffers, scores}}

        # CONSTANTS 사용
        self.CONSTANTS = CONSTANTS
        self.current_spec_id = spec_id
        self.current_group_id = None  # ✅ 그룹 ID 저장용
        
        # ✅ 상태 관리자 초기화
        self.state_manager = SystemStateManager(self)

        self.load_specs_from_constants()
        self.CONSTANTS = CONSTANTS
        super().__init__()
        self.embedded = embedded

        # 전체화면 관련 변수 초기화
        self._is_fullscreen = False
        self._saved_geom = None
        self._saved_state = None

        self.webhook_res = None
        self.res = None
        self.radio_check_flag = "video"  # 영상보안 시스템으로 고정

        # 로딩 팝업 인스턴스 변수
        self.loading_popup = None

        # ✅ spec_id 초기화 (info_GUI에서 전달받거나 기본값 사용)
        if spec_id:
            self.current_spec_id = spec_id
            print(f"[SYSTEM] 📌 전달받은 spec_id 사용: {spec_id}")
        else:
            self.current_spec_id = "cmgatbdp000bqihlexmywusvq"  # 기본값: 보안용센서 시스템 (7개 API) -> 지금은 잠깐 없어짐
            print(f"[SYSTEM] 📌 기본 spec_id 사용: {self.current_spec_id}")
        
        # 아이콘 경로 (메인 페이지용)
        self.img_pass = resource_path("assets/image/icon/icn_success.png")
        self.img_fail = resource_path("assets/image/icon/icn_fail.png")
        self.img_none = resource_path("assets/image/icon/icn_basic.png")

        self.flag_opt = self.CONSTANTS.flag_opt
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_view)
        self.cnt = 0
        self.current_retry = 0  # 현재 API의 반복 횟수 카운터
        self.auth_flag = True

        self.time_pre = 0
        self.post_flag = False
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.message_in_cnt = 0
        self.message_error = []
        self.message_name = ""

        # ✅ 일시정지 및 재개 관련 변수
        self.is_paused = False
        self.last_completed_api_index = -1
        self.paused_valResult_text = ""

        parts = self.auth_info.split(",")
        auth = [parts[0], parts[1] if len(parts) > 1 else ""]
        self.accessInfo = [auth[0], auth[1]]

        # step_buffers 동적 생성 (API 개수에 따라)
        api_count = len(self.videoMessages)
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS", "raw_data_list": []} for _ in range(api_count)
        ]

        # ✅ 누적 카운트 초기화
        self.step_pass_counts = [0] * api_count
        self.step_error_counts = [0] * api_count
        self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
        self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수
        self.step_pass_flags = [0] * api_count

        self.trace = defaultdict(list)

        # ✅ Data Mapper 초기화 - trace 기반 latest_events 사용
        self.latest_events = {}  # API별 최신 이벤트 저장
        self.generator = ConstraintDataGenerator(self.latest_events)

        self.initUI()

        self.webhookInSchema = []
        self.get_setting()  # 실행되는 시점
        self.webhook_flag = False
        self.webhook_msg = "."
        self.webhook_cnt = 99
        self.reference_context = {}  # 맥락검증 참조 컨텍스트
        self.webhook_schema_idx = 0  # ✅ 웹훅 스키마 인덱스 추가

    def save_current_spec_data(self):
        """현재 spec의 테이블 데이터와 상태를 저장 (state_manager 위임)"""
        if hasattr(self, 'state_manager'):
            self.state_manager.save_current_spec_data()

    def _get_icon_state(self, row):
        """테이블 행의 아이콘 상태 반환 (state_manager 위임)"""
        if hasattr(self, 'state_manager'):
            return self.state_manager._get_icon_state(row)
        return "NONE"

    def restore_spec_data(self, spec_id):
        """저장된 spec 데이터 복원 (state_manager 위임)"""
        if hasattr(self, 'state_manager'):
            return self.state_manager.restore_spec_data(spec_id)
        return False
        print(f"[RESTORE] step_opt_pass_counts 복원: {self.step_opt_pass_counts}")
        print(f"[RESTORE] step_opt_error_counts 복원: {self.step_opt_error_counts}")

        print(f"[RESTORE] {spec_id} 데이터 복원 완료")
        return True

    def _redact(self, payload):  # ### NEW
        """응답/요청에서 토큰, 패스워드 등 민감값 마스킹(선택)"""
        try:
            if isinstance(payload, dict):
                red = dict(payload)
                for k in ["accessToken", "token", "Authorization", "password", "secret", "apiKey"]:
                    if k in red and isinstance(red[k], (str, bytes)):
                        red[k] = "***"
                return red
            return payload
        except Exception:
            return payload

    def _push_event(self, step_idx, direction, payload):  # ### NEW
        """REQUEST/RESPONSE/WEBHOOK 이벤트를 순서대로 기록하고 ndjson에 append"""
        try:
            api = self.message[step_idx] if 0 <= step_idx < len(self.message) else f"step_{step_idx + 1}"
            evt = {
                "time": datetime.utcnow().isoformat() + "Z",
                "api": api,
                "dir": direction,  # "REQUEST" | "RESPONSE" | "WEBHOOK"
                "data": self._redact(payload)
            }
            self.trace[step_idx].append(evt)

            # ✅ latest_events 업데이트 (data mapper용) - 여러 키 형식으로 저장
            # 1. 원본 API 이름으로 저장
            if api not in self.latest_events:
                self.latest_events[api] = {}
            self.latest_events[api][direction] = evt
            
            # 2. 슬래시 제거한 형식으로도 저장 (예: "CameraProfiles")
            api_clean = api.lstrip('/')
            if api_clean != api:
                if api_clean not in self.latest_events:
                    self.latest_events[api_clean] = {}
                self.latest_events[api_clean][direction] = evt
            
            # 3. 슬래시 포함한 형식으로도 저장 (예: "/CameraProfiles")
            api_with_slash = f"/{api_clean}" if not api_clean.startswith('/') else api_clean
            if api_with_slash != api:
                if api_with_slash not in self.latest_events:
                    self.latest_events[api_with_slash] = {}
                self.latest_events[api_with_slash][direction] = evt
            
            # ✅ 디버그 로그 추가
            print(f"[PUSH_EVENT] API={api}, Direction={direction}")
            print(f"[PUSH_EVENT] 저장된 키들: {api}, {api_clean}, {api_with_slash}")
            print(f"[PUSH_EVENT] latest_events 전체 키 목록: {list(self.latest_events.keys())}")

            # (옵션) 즉시 파일로도 남김 - append-only ndjson
            os.makedirs(CONSTANTS.trace_path, exist_ok=True)
            safe_api = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(api))
            trace_path = os.path.join(CONSTANTS.trace_path, f"trace_{step_idx + 1:02d}_{safe_api}.ndjson")
            with open(trace_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(evt, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def load_specs_from_constants(self):
        """
        ✅ SPEC_CONFIG 기반으로 spec 데이터 동적 로드
        - current_spec_id에 따라 올바른 모듈(spec.video 또는 spec/)에서 데이터 로드
        - trans_protocol, time_out, num_retries도 SPEC_CONFIG에서 가져옴
        """
        # ===== PyInstaller 환경에서 외부 CONSTANTS.py에서 SPEC_CONFIG 로드 =====
        import sys
        import os

        SPEC_CONFIG = getattr(self.CONSTANTS, 'SPEC_CONFIG', [])
        url_value = getattr(self.CONSTANTS, 'url', None)
        auth_type = getattr(self.CONSTANTS, 'auth_type', None)
        auth_info = getattr(self.CONSTANTS, 'auth_info', None)
        if getattr(sys, 'frozen', False):
            # PyInstaller 환경: 외부 CONSTANTS.py에서 SPEC_CONFIG 읽기
            exe_dir = os.path.dirname(sys.executable)
            external_constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")

            if os.path.exists(external_constants_path):
                print(f"[SYSTEM] 외부 CONSTANTS.py에서 SPEC_CONFIG 로드: {external_constants_path}")
                try:
                    # 외부 파일 읽어서 SPEC_CONFIG만 추출
                    with open(external_constants_path, 'r', encoding='utf-8') as f:
                        constants_code = f.read()

                    # SPEC_CONFIG만 추출하기 위해 exec 실행
                    namespace = {'__file__': external_constants_path}
                    exec(constants_code, namespace)
                    SPEC_CONFIG = namespace.get('SPEC_CONFIG', self.CONSTANTS.SPEC_CONFIG)
                    url_value = namespace.get('url', url_value)
                    auth_type = namespace.get('auth_type', auth_type)
                    auth_info = namespace.get('auth_info', auth_info)
                    self.CONSTANTS.company_name = namespace.get('company_name', self.CONSTANTS.company_name)
                    self.CONSTANTS.product_name = namespace.get('product_name', self.CONSTANTS.product_name)
                    self.CONSTANTS.version = namespace.get('version', self.CONSTANTS.version)
                    self.CONSTANTS.test_category = namespace.get('test_category', self.CONSTANTS.test_category)
                    self.CONSTANTS.test_target = namespace.get('test_target', self.CONSTANTS.test_target)
                    self.CONSTANTS.test_range = namespace.get('test_range', self.CONSTANTS.test_range)

                    print(f"[SYSTEM] ✅ 외부 SPEC_CONFIG 로드 완료: {len(SPEC_CONFIG)}개 그룹")
                    # 디버그: 그룹 이름 출력
                    for i, g in enumerate(SPEC_CONFIG):
                        group_name = g.get('group_name', '이름없음')
                        group_keys = [k for k in g.keys() if k not in ['group_name', 'group_id']]
                        print(f"[SYSTEM DEBUG] 그룹 {i}: {group_name}, spec_id 개수: {len(group_keys)}, spec_ids: {group_keys}")
                except Exception as e:
                    print(f"[SYSTEM] ⚠️ 외부 CONSTANTS 로드 실패, 기본값 사용: {e}")
        # ===== 외부 CONSTANTS 로드 끝 =====

        # ===== 인스턴스 변수에 저장 (다른 메서드에서 사용) =====
        self.LOADED_SPEC_CONFIG = SPEC_CONFIG
        self.url = url_value  # ✅ 외부 CONSTANTS.py에 정의된 url도 반영
        self.auth_type = auth_type
        self.auth_info = auth_info
        # ===== 저장 완료 =====

        # ===== 디버그 로그 추가 =====
        print(f"[SYSTEM DEBUG] SPEC_CONFIG 개수: {len(SPEC_CONFIG)}")
        print(f"[SYSTEM DEBUG] 찾을 spec_id: {self.current_spec_id}")
        for i, group in enumerate(SPEC_CONFIG):
            print(f"[SYSTEM DEBUG] Group {i} keys: {list(group.keys())}")
        # ===== 디버그 로그 끝 =====

        config = {}
        # ===== 수정: 로드한 SPEC_CONFIG 사용 =====
        for group in SPEC_CONFIG:
            if self.current_spec_id in group:
                config = group[self.current_spec_id]
                break
        # ===== 수정 끝 =====

        if not config:
            raise ValueError(f"spec_id '{self.current_spec_id}'에 대한 설정을 찾을 수 없습니다!")
            return

        # ✅ 설정 정보 추출
        self.spec_description = config.get('test_name', 'Unknown Test')
        spec_names = config.get('specs', [])

        # ✅ trans_protocol, time_out, num_retries 저장
        self.trans_protocols = config.get('trans_protocol', [])
        self.time_outs = config.get('time_out', [])
        self.num_retries_list = config.get('num_retries', [])

        if len(spec_names) < 3:
            raise ValueError(f"spec_id '{self.current_spec_id}'의 specs 설정이 올바르지 않습니다! (최소 3개 필요)")

        print(f"[SYSTEM] 📋 Spec 로딩 시작: {self.spec_description} (ID: {self.current_spec_id})")

        # 시스템은 response schema / request data 사용
        print(f"[SYSTEM] 📁 모듈: spec (센서/바이오/영상 통합)")

        # ===== PyInstaller 환경에서 외부 spec 디렉토리 우선 로드 =====
        import sys
        import os

        if getattr(sys, 'frozen', False):
            # PyInstaller 환경: 외부 spec 디렉토리 사용
            exe_dir = os.path.dirname(sys.executable)
            external_spec_parent = exe_dir

            # 외부 spec 폴더 파일 존재 확인
            external_spec_dir = os.path.join(external_spec_parent, 'spec')
            print(f"[SYSTEM SPEC DEBUG] 외부 spec 폴더: {external_spec_dir}")
            print(f"[SYSTEM SPEC DEBUG] 외부 spec 폴더 존재: {os.path.exists(external_spec_dir)}")
            if os.path.exists(external_spec_dir):
                files = [f for f in os.listdir(external_spec_dir) if f.endswith('.py')]
                print(f"[SYSTEM SPEC DEBUG] 외부 spec 폴더 .py 파일: {files}")

            # 이미 있더라도 제거 후 맨 앞에 추가 (우선순위 보장)
            if external_spec_parent in sys.path:
                sys.path.remove(external_spec_parent)
            sys.path.insert(0, external_spec_parent)
            print(f"[SYSTEM SPEC] sys.path에 외부 디렉토리 추가: {external_spec_parent}")

        # ===== 모듈 캐시 강제 삭제 =====
        # 주의: 'spec' 패키지 자체는 유지 (parent 패키지 필요)
        module_names = [
            'spec.Data_request',
            'spec.Schema_response',
            'spec.Constraints_request'
        ]

        for mod_name in module_names:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
                print(f"[SYSTEM SPEC] 모듈 캐시 삭제: {mod_name}")
            else:
                print(f"[SYSTEM SPEC] 모듈 캐시 없음: {mod_name}")

        # spec 패키지가 없으면 빈 모듈로 등록
        if 'spec' not in sys.modules:
            import types
            sys.modules['spec'] = types.ModuleType('spec')
            print(f"[SYSTEM SPEC] 빈 'spec' 패키지 생성")
        # ===== 캐시 삭제 끝 =====

        # PyInstaller 환경에서는 importlib.util로 명시적으로 외부 파일 로드
        import importlib
        if getattr(sys, 'frozen', False):
            import importlib.util

            # 외부 spec 파일 경로
            data_file = os.path.join(exe_dir, 'spec', 'Data_request.py')
            schema_file = os.path.join(exe_dir, 'spec', 'Schema_response.py')
            constraints_file = os.path.join(exe_dir, 'spec', 'Constraints_request.py')

            print(f"[SYSTEM SPEC] 명시적 로드 시도:")
            print(f"  - Data: {data_file} (존재: {os.path.exists(data_file)})")
            print(f"  - Schema: {schema_file} (존재: {os.path.exists(schema_file)})")
            print(f"  - Constraints: {constraints_file} (존재: {os.path.exists(constraints_file)})")

            # importlib.util로 명시적 로드
            spec = importlib.util.spec_from_file_location('spec.Data_request', data_file)
            data_request_module = importlib.util.module_from_spec(spec)
            sys.modules['spec.Data_request'] = data_request_module
            spec.loader.exec_module(data_request_module)

            spec = importlib.util.spec_from_file_location('spec.Schema_response', schema_file)
            schema_response_module = importlib.util.module_from_spec(spec)
            sys.modules['spec.Schema_response'] = schema_response_module
            spec.loader.exec_module(schema_response_module)

            spec = importlib.util.spec_from_file_location('spec.Constraints_request', constraints_file)
            constraints_request_module = importlib.util.module_from_spec(spec)
            sys.modules['spec.Constraints_request'] = constraints_request_module
            spec.loader.exec_module(constraints_request_module)

            print(f"[SYSTEM SPEC] ✅ importlib.util로 외부 파일 로드 완료")
        else:
            # 일반 환경에서는 기존 방식 사용
            import spec.Data_request as data_request_module
            import spec.Schema_response as schema_response_module
            import spec.Constraints_request as constraints_request_module

        # ===== spec 파일 경로 및 수정 시간 로그 =====
        import datetime

        for module, name in [
            (data_request_module, "Data_request.py"),
            (schema_response_module, "Schema_response.py"),
            (constraints_request_module, "Constraints_request.py")
        ]:
            file_path = module.__file__
            if os.path.exists(file_path):
                mtime = os.path.getmtime(file_path)
                mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"[SYSTEM SPEC] {name} 로드 경로: {file_path}")
                print(f"[SYSTEM SPEC] {name} 수정 시간: {mtime_str}")
            else:
                print(f"[SYSTEM SPEC] {name} 로드 경로: {file_path} (파일 없음)")
        # ===== 로그 끝 =====

        # importlib.util로 직접 로드했으므로 reload 불필요 (이미 최신 파일 로드됨)
        # PyInstaller 환경이 아닌 경우에만 reload 수행
        if not getattr(sys, 'frozen', False):
            importlib.reload(data_request_module)
            importlib.reload(schema_response_module)
            importlib.reload(constraints_request_module)

        # ✅ 시스템은 응답 검증 + 요청 전송 (outSchema/inData 사용)
        print(f"[SYSTEM] 🔧 타입: 응답 검증 + 요청 전송")
        print(spec_names)
        # ✅ Response 검증용 스키마 로드 (시스템이 플랫폼으로부터 받을 응답 검증) - outSchema
        self.videoOutSchema = getattr(schema_response_module, spec_names[0], [])

        # ✅ Request 전송용 데이터 로드 (시스템이 플랫폼에게 보낼 요청) - inData
        self.videoInMessage = getattr(data_request_module, spec_names[1], [])
        self.videoMessages = getattr(data_request_module, spec_names[2], [])
        # 표시용 API 이름 (숫자 제거)
        self.videoMessagesDisplay = [self._remove_api_number_suffix(msg) for msg in self.videoMessages]
        self.videoInConstraint = getattr(constraints_request_module, self.current_spec_id + "_inConstraints", [])
        try:
            self.webhookInSchema = getattr(schema_response_module, spec_names[3], [])
        except Exception as e:
            print(f"Error loading webhook schema: {e}")
            self.webhookInSchema = []

        # ✅ Webhook 관련 (현재 미사용)
        # self.videoWebhookSchema = []
        # self.videoWebhookData = []
        # self.videoWebhookInSchema = []
        # self.videoWebhookInData = []

        print(f"[SYSTEM] ✅ 로딩 완료: {len(self.videoMessages)}개 API")
        print(f"[SYSTEM] 📋 API 목록: {self.videoMessages}")
        print(f"[SYSTEM] 🔄 프로토콜 설정: {self.trans_protocols}")
        self.webhook_schema_idx = 0

        # ✅ spec_config 저장 (URL 생성에 필요)
        self.spec_config = config
        
        # ✅ UI 호환성을 위해 inSchema 변수 매핑 (시스템 검증은 응답 스키마 사용)
        self.inSchema = self.videoOutSchema

    def _to_detail_text(self, val_text):
        """검증 결과 텍스트를 항상 사람이 읽을 문자열로 표준화"""
        if val_text is None:
            return "오류가 없습니다."
        if isinstance(val_text, list):
            return "\n".join(str(x) for x in val_text) if val_text else "오류가 없습니다."
        if isinstance(val_text, dict):
            try:
                return json.dumps(val_text, indent=2, ensure_ascii=False)
            except Exception:
                return str(val_text)
        return str(val_text)

    def update_table_row_with_retries(self, row, result, pass_count, error_count, data, error_text, retries):
        """테이블 행 업데이트 (안전성 강화)"""
        # ✅ 1. 범위 체크
        if row >= self.tableWidget.rowCount():
            print(f"[TABLE UPDATE] 경고: row={row}가 테이블 범위를 벗어남 (총 {self.tableWidget.rowCount()}행)")
            return

        print(f"[TABLE UPDATE] row={row}, result={result}, pass={pass_count}, error={error_count}, retries={retries}")

        # ✅ 2. 아이콘 업데이트
        msg, img = self.icon_update_step(data, result, error_text)

        icon_widget = QWidget()
        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(img).pixmap(84, 20))
        icon_label.setToolTip(msg)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_widget.setLayout(icon_layout)

        self.tableWidget.setCellWidget(row, 2, icon_widget)

        # ✅ 3. 각 컬럼 업데이트 (아이템이 없으면 생성)
        updates = [
            (3, str(retries)),  # 검증 횟수
            (4, str(pass_count)),  # 통과 필드 수
            (5, str(pass_count + error_count)),  # 전체 필드 수
            (6, str(error_count)),  # 실패 필드 수
        ]

        for col, value in updates:
            item = self.tableWidget.item(row, col)
            if item is None:
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)
            else:
                item.setText(value)

        # ✅ 4. 평가 점수 업데이트
        total_fields = pass_count + error_count
        if total_fields > 0:
            score = (pass_count / total_fields) * 100
            score_text = f"{score:.1f}%"
        else:
            score_text = "0%"

        score_item = self.tableWidget.item(row, 7)
        if score_item is None:
            score_item = QTableWidgetItem(score_text)
            score_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row, 7, score_item)
        else:
            score_item.setText(score_text)

        # ✅ 5. 메시지 저장
        setattr(self, f"step{row + 1}_msg", msg)

        # ✅ 6. UI 즉시 업데이트
        QApplication.processEvents()

        print(f"[TABLE UPDATE] 완료: row={row}")

    def load_test_info_from_constants(self):
        return [
            ("기업명", self.CONSTANTS.company_name),
            ("제품명", self.CONSTANTS.product_name),
            ("버전", self.CONSTANTS.version),
            ("시험유형", self.CONSTANTS.test_category),
            ("시험대상", self.CONSTANTS.test_target),
            ("시험범위", self.CONSTANTS.test_range),
            ("사용자 인증 방식", self.auth_type),
            ("시험 접속 정보", self.url)
        ]

    def create_spec_selection_panel(self, parent_layout):
        """시험 선택 패널 - 424px 너비"""
        # 타이틀: 424*24, 폰트 20px Medium
        self.spec_panel_title = QLabel("시험 선택")
        self.spec_panel_title.setFixedSize(424, 24)
        self.spec_panel_title.setStyleSheet("""
            font-size: 20px;
            font-style: normal;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
            letter-spacing: -0.3px;
        """)
        parent_layout.addWidget(self.spec_panel_title)

        # ✅ 반응형: 원본 크기 저장
        self.original_spec_panel_title_size = (424, 24)

        # 타이틀 아래 8px gap
        parent_layout.addSpacing(8)

        # 그룹 테이블 추가 (시험 분야 테이블)
        self.group_table_widget = self.create_group_selection_table()
        parent_layout.addWidget(self.group_table_widget)

        # 20px gap
        parent_layout.addSpacing(20)

        # 시험 시나리오 테이블
        self.field_group = self.create_test_field_group()
        parent_layout.addWidget(self.field_group)

    def create_group_selection_table(self):
        """시험 분야명 테이블 - 424*204, 헤더 31px, 데이터셀 39px"""
        group_box = QWidget()
        group_box.setFixedSize(424, 204)
        group_box.setStyleSheet("background: transparent;")

        # ✅ 반응형: 원본 크기 저장
        self.original_group_table_widget_size = (424, 204)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.group_table = QTableWidget(0, 1)
        self.group_table.setHorizontalHeaderLabels(["시험 분야"])
        self.group_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.group_table.horizontalHeader().setFixedHeight(31)  # 헤더 높이 31px
        self.group_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.group_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.group_table.verticalHeader().setVisible(False)
        self.group_table.setFixedHeight(204)
        self.group_table.verticalHeader().setDefaultSectionSize(39)  # 데이터셀 높이 39px

        # ✅ 플랫폼과 동일한 스타일 적용
        self.group_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                outline: none;
                font-family: "Noto Sans KR";
                font-size: 19px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-weight: 400;
                padding: 8px;
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #F2F8FF;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CECECE;
                color: #1B1B1C;
                text-align: center;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 600;
                letter-spacing: -0.156px;
            }
        """)

        # SPEC_CONFIG 기반 그룹 로드
        # ===== 외부 로드된 SPEC_CONFIG 사용 (fallback: CONSTANTS 모듈) =====
        import sys
        import os

        SPEC_CONFIG = self.CONSTANTS.SPEC_CONFIG  # 기본값

        if getattr(sys, 'frozen', False):
            # PyInstaller 환경: 외부 CONSTANTS.py에서 SPEC_CONFIG 읽기
            exe_dir = os.path.dirname(sys.executable)
            external_constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")

            if os.path.exists(external_constants_path):
                print(f"[GROUP TABLE] 외부 CONSTANTS.py에서 SPEC_CONFIG 로드: {external_constants_path}")
                try:
                    with open(external_constants_path, 'r', encoding='utf-8') as f:
                        constants_code = f.read()

                    namespace = {'__file__': external_constants_path}
                    exec(constants_code, namespace)
                    SPEC_CONFIG = namespace.get('SPEC_CONFIG', self.CONSTANTS.SPEC_CONFIG)
                    print(f"[GROUP TABLE] ✅ 외부 SPEC_CONFIG 로드 완료: {len(SPEC_CONFIG)}개 그룹")
                    # 디버그: 그룹 이름 출력
                    for i, g in enumerate(SPEC_CONFIG):
                        group_name = g.get('group_name', '이름없음')
                        group_keys = [k for k in g.keys() if k not in ['group_name', 'group_id']]
                        print(f"[GROUP TABLE DEBUG] 그룹 {i}: {group_name}, spec_id 개수: {len(group_keys)}, spec_ids: {group_keys}")
                except Exception as e:
                    print(f"[GROUP TABLE] ⚠️ 외부 CONSTANTS 로드 실패, 기본값 사용: {e}")
        # ===== 외부 CONSTANTS 로드 끝 =====
        self.webhook_schema_idx = 0
        self.webhookInSchema = []
        group_items = [
            (g.get("group_name", "미지정 그룹"), g.get("group_id", ""))
            for g in SPEC_CONFIG
        ]
        self.group_table.setRowCount(len(group_items))

        self.group_name_to_index = {}
        self.index_to_group_name = {}

        for idx, (name, gid) in enumerate(group_items):
            display_name = name
            item = QTableWidgetItem(display_name)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.group_table.setItem(idx, 0, item)
            self.group_name_to_index[name] = idx
            self.index_to_group_name[idx] = name

        self.group_table.cellClicked.connect(self.on_group_selected)

        layout.addWidget(self.group_table)
        group_box.setLayout(layout)
        return group_box

    def on_group_selected(self, row, col):
        group_name = self.index_to_group_name.get(row)
        if not group_name:
            return

        # ===== 외부 로드된 SPEC_CONFIG 사용 (fallback: CONSTANTS 모듈) =====
        SPEC_CONFIG = getattr(self, 'LOADED_SPEC_CONFIG', self.CONSTANTS.SPEC_CONFIG)
        selected_group = next(
            (g for g in SPEC_CONFIG if g.get("group_name") == group_name), None
        )
        # ===== 수정 끝 =====

        if selected_group:
            new_group_id = selected_group.get('group_id')
            old_group_id = getattr(self, 'current_group_id', None)

            print(f"[DEBUG] 🔄 그룹 선택: {old_group_id} → {new_group_id}")

            # ✅ 그룹이 변경되면 current_spec_id 초기화 (다음 시나리오 선택 시 무조건 다시 로드되도록)
            if old_group_id != new_group_id:
                self.current_spec_id = None
                print(f"[DEBUG] ✨ 그룹 변경으로 current_spec_id 초기화")

            # ✅ 그룹 ID 저장
            self.current_group_id = new_group_id
            self.update_test_field_table(selected_group)

    def update_test_field_table(self, group_data):
        """선택된 그룹의 spec_id 목록으로 테이블 갱신"""
        self.test_field_table.clearContents()

        spec_items = [
            (k, v) for k, v in group_data.items()
            if k not in ['group_name', 'group_id'] and isinstance(v, dict)
        ]
        self.test_field_table.setRowCount(len(spec_items))

        self.spec_id_to_index.clear()
        self.index_to_spec_id.clear()

        for idx, (spec_id, config) in enumerate(spec_items):
            desc = config.get('test_name', f'시험분야 {idx + 1}')
            desc_with_role = f"{desc} (응답 검증)"
            item = QTableWidgetItem(desc_with_role)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.test_field_table.setItem(idx, 0, item)
            self.spec_id_to_index[spec_id] = idx
            self.index_to_spec_id[idx] = spec_id
    def on_group_selected(self, row, col):
        """
        ✅ 시험 그룹 선택 시 해당 그룹의 시험 분야 목록을 자동 갱신
        """
        # 선택된 그룹명 가져오기
        if not hasattr(self, "index_to_group_name"):
            return

        group_name = self.index_to_group_name.get(row)
        if not group_name:
            return

        # ===== 외부 로드된 SPEC_CONFIG 사용 (fallback: CONSTANTS 모듈) =====
        SPEC_CONFIG = getattr(self, 'LOADED_SPEC_CONFIG', self.CONSTANTS.SPEC_CONFIG)
        # SPEC_CONFIG에서 선택된 그룹 데이터 찾기
        selected_group = None
        for group_data in SPEC_CONFIG:
            if group_data.get("group_name") == group_name:
                selected_group = group_data
                break
        # ===== 수정 끝 =====

        if selected_group is None:
            print(f"[WARN] 선택된 그룹({group_name}) 데이터를 찾을 수 없습니다.")
            return

        # ✅ 그룹 변경 감지 및 current_spec_id 초기화
        new_group_id = selected_group.get('group_id')
        old_group_id = getattr(self, 'current_group_id', None)

        print(f"[DEBUG] 🔄 그룹 선택: {old_group_id} → {new_group_id}")

        # ✅ 그룹이 변경되면 current_spec_id 초기화 (다음 시나리오 선택 시 무조건 다시 로드되도록)
        if old_group_id != new_group_id:
            self.current_spec_id = None
            print(f"[DEBUG] ✨ 그룹 변경으로 current_spec_id 초기화")

        # ✅ 그룹 ID 저장
        self.current_group_id = new_group_id

        # 시험 분야 테이블 갱신
        self.update_test_field_table(selected_group)

    def create_test_field_group(self):
        """시험 시나리오 테이블 - 424*526, 헤더 31px, 데이터셀 39px"""
        group_box = QWidget()
        group_box.setFixedSize(424, 526)
        group_box.setStyleSheet("background: transparent;")

        # ✅ 반응형: 원본 크기 저장
        self.original_field_group_size = (424, 526)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.test_field_table = QTableWidget(0, 1)
        self.test_field_table.setHorizontalHeaderLabels(["시험 시나리오"])
        self.test_field_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_field_table.horizontalHeader().setFixedHeight(31)  # 헤더 높이 31px
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)
        self.test_field_table.verticalHeader().setVisible(False)
        self.test_field_table.setFixedHeight(526)
        self.test_field_table.verticalHeader().setDefaultSectionSize(39)  # 데이터셀 높이 39px

        # ✅ 플랫폼과 완전히 동일한 스타일
        self.test_field_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: "Noto Sans KR";
                font-size: 19px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                border-right: 0px solid transparent;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-style: normal;
                font-weight: 400;
                letter-spacing: 0.098px;
                text-align: center; 
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
            }
            QTableWidget::item:hover {
                background-color: #E3F2FF;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border-right: 0px solid transparent;
                border-left: 0px solid transparent;
                border-top: 0px solid transparent;
                border-bottom: 1px solid #CECECE;
                color: #1B1B1C;
                text-align: center;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                letter-spacing: -0.156px;
            }
        """)

        # SPEC_CONFIG에서 spec_id와 config 추출
        spec_items = []
        for group_data in self.CONSTANTS.SPEC_CONFIG:
            for key, value in group_data.items():
                if key not in ['group_name', 'group_id'] and isinstance(value, dict):
                    spec_items.append((key, value))

        if spec_items:
            self.test_field_table.setRowCount(len(spec_items))

            self.spec_id_to_index = {}
            self.index_to_spec_id = {}

            for idx, (spec_id, config) in enumerate(spec_items):
                description = config.get('test_name', f'시험 분야 {idx + 1}')
                description_with_role = f"{description} (응답 검증)"
                item = QTableWidgetItem(description_with_role)
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.test_field_table.setItem(idx, 0, item)

                self.spec_id_to_index[spec_id] = idx
                self.index_to_spec_id[idx] = spec_id

            # 현재 로드된 spec_id 선택
            if self.current_spec_id in self.spec_id_to_index:
                current_index = self.spec_id_to_index[self.current_spec_id]
                self.test_field_table.selectRow(current_index)
                self.selected_test_field_row = current_index

        layout.addWidget(self.test_field_table)
        group_box.setLayout(layout)
        return group_box

    def update_test_field_table(self, group_data):
        """
        ✅ 선택된 시험 그룹의 시험 분야 테이블을 갱신
        """
        # 기존 테이블 초기화
        self.test_field_table.clearContents()

        # 시험 분야만 추출
        spec_items = [
            (key, value)
            for key, value in group_data.items()
            if key not in ["group_name", "group_id"] and isinstance(value, dict)
        ]

        # 행 개수 재설정
        self.test_field_table.setRowCount(len(spec_items))

        # 인덱스 매핑 초기화
        self.spec_id_to_index = {}
        self.index_to_spec_id = {}

        # 테이블 갱신
        for idx, (spec_id, config) in enumerate(spec_items):
            description = config.get("test_name", f"시험 분야 {idx + 1}")
            description_with_role = f"{description} (응답 검증)"
            item = QTableWidgetItem(description_with_role)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.test_field_table.setItem(idx, 0, item)

            # 매핑 저장
            self.spec_id_to_index[spec_id] = idx
            self.index_to_spec_id[idx] = spec_id

        print(f"[INFO] '{group_data.get('group_name')}' 그룹의 시험 분야 {len(spec_items)}개 로드 완료.")

    def on_test_field_selected(self, row, col):
        """시험 분야 클릭 시 해당 시스템으로 동적 전환"""
        try:
            self.selected_test_field_row = row

            if row in self.index_to_spec_id:
                new_spec_id = self.index_to_spec_id[row]

                if new_spec_id == self.current_spec_id:
                    print(f"[SELECT] 이미 선택된 시나리오: {new_spec_id}")
                    return

                print(f"[SYSTEM] 🔄 시험 분야 전환: {self.current_spec_id} → {new_spec_id}")
                print(f"[DEBUG] 현재 그룹: {self.current_group_id}")

                # ✅ 1. 현재 spec의 테이블 데이터 저장 (current_spec_id가 None이 아닐 때만)
                if self.current_spec_id is not None:
                    print(f"[DEBUG] 데이터 저장 전 - 테이블 행 수: {self.tableWidget.rowCount()}")
                    self.save_current_spec_data()
                else:
                    print(f"[DEBUG] ⚠️ current_spec_id가 None - 저장 스킵 (그룹 전환 직후)")

                # ✅ 2. spec_id 업데이트
                self.current_spec_id = new_spec_id

                # ✅ 3. spec 데이터 다시 로드
                self.load_specs_from_constants()

                print(f"[SELECT] 로드된 API 개수: {len(self.videoMessages)}")
                print(f"[SELECT] API 목록: {self.videoMessages}")

                # ✅ 4. 기본 변수 초기화
                self.cnt = 0
                self.current_retry = 0
                self.message_error = []

                # ✅ 5. 테이블 완전 재구성
                print(f"[SELECT] 테이블 완전 재구성 시작")
                self.update_result_table_structure(self.videoMessages)

                # ✅ 6. 저장된 데이터 복원 시도
                restored = self.restore_spec_data(new_spec_id)

                if not restored:
                    print(f"[SELECT] 저장된 데이터 없음 - 초기화")
                    # 점수 초기화
                    self.total_pass_cnt = 0
                    self.total_error_cnt = 0

                    # ✅ step_pass_counts와 step_error_counts 배열 초기화
                    api_count = len(self.videoMessages)
                    self.step_pass_counts = [0] * api_count
                    self.step_error_counts = [0] * api_count
                    self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
                    self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수

                    # step_buffers 초기화
                    self.step_buffers = [
                        {"data": "", "error": "", "result": "PASS", "raw_data_list": []} for _ in range(len(self.videoMessages))
                    ]
                else:
                    print(f"[SELECT] 저장된 데이터 복원 완료")

                # ✅ 7. trace 및 latest_events 초기화
                self.trace.clear()
                self.latest_events = {}

                # ✅ 8. 설정 다시 로드
                self.get_setting()

                # ✅ 9. 평가 점수 디스플레이 업데이트
                self.update_score_display()

                # URL 업데이트 (test_name 사용)
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', self.current_spec_id)
                    self.pathUrl = self.url + "/" + test_name
                else:
                    self.pathUrl = self.url + "/" + self.current_spec_id
                self.url_text_box.setText(self.pathUrl)  # 안내 문구 변경

                # ✅ 10. 결과 텍스트 초기화
                self.valResult.clear()
                self.append_monitor_log(
                    step_name=f"시스템 전환 완료: {self.spec_description}",
                    details=f"API 개수: {len(self.videoMessages)}개 | API 목록: {', '.join(self.videoMessagesDisplay)}"
                )

                print(f"[SELECT] ✅ 시스템 전환 완료")

        except Exception as e:
            print(f"[SELECT] 시험 분야 선택 처리 실패: {e}")
            import traceback
            traceback.print_exc()

    def update_result_table_structure(self, api_list):
        """테이블 구조를 완전히 재구성 (API 개수에 맞게)"""
        api_count = len(api_list)
        print(f"[TABLE] 테이블 재구성 시작: {api_count}개 API")

        # ✅ 1. 테이블 행 개수 설정
        self.tableWidget.setRowCount(api_count)

        # ✅ 2. 각 행을 완전히 초기화
        for row in range(api_count):
            api_name = api_list[row]
            # 표시용 이름 (숫자 제거)
            display_name = self._remove_api_number_suffix(api_name)

            # 컬럼 0: No. (숫자)
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # 컬럼 1: API 명 (숫자 제거)
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            print(f"[TABLE] Row {row}: {display_name} 설정 완료")

            # 컬럼 2: 결과 아이콘
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 2, icon_widget)

            # 컬럼 3-7: 검증 횟수, 통과/전체/실패 필드 수, 평가 점수
            col_values = [
                (3, "0"),  # 검증 횟수
                (4, "0"),  # 통과 필드 수
                (5, "0"),  # 전체 필드 수
                (6, "0"),  # 실패 필드 수
                (7, "0%")  # 평가 점수
            ]

            for col, value in col_values:
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # 컬럼 8: 상세 내용 버튼
            detail_label = QLabel()
            try:
                img_path = resource_path("assets/image/test_runner/btn_상세내용확인.png").replace("\\", "/")
                pixmap = QPixmap(img_path)
                detail_label.setPixmap(pixmap)
                detail_label.setScaledContents(False)
                detail_label.setFixedSize(pixmap.size())
            except:
                detail_label.setText("확인")
                detail_label.setStyleSheet("color: #4A90E2; font-weight: bold;")

            detail_label.setCursor(Qt.PointingHandCursor)
            detail_label.setAlignment(Qt.AlignCenter)
            detail_label.mousePressEvent = lambda event, r=row: self.show_combined_result(r)

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 8, container)

            # 행 높이 설정
            self.tableWidget.setRowHeight(row, 40)

        print(f"[TABLE] 테이블 재구성 완료: {self.tableWidget.rowCount()}개 행")

    def update_result_table_with_apis(self, api_list):
        """시험 결과 테이블을 새로운 API 목록으로 업데이트"""
        api_count = len(api_list)
        self.tableWidget.setRowCount(api_count)

        # 각 행의 API 명 업데이트
        for row in range(api_count):
            # No. (숫자) - 컬럼 0
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # API 명 - 컬럼 1 (숫자 제거)
            display_name = self.parent._remove_api_number_suffix(api_list[row])
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            # 결과 아이콘 - 컬럼 2
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 2, icon_widget)

            # 검증 횟수, 통과 필드 수, 전체 필드 수, 실패 필드 수, 평가 점수 - 컬럼 3-7
            for col in range(3, 8):
                item = QTableWidgetItem("0" if col != 7 else "0%")
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # 상세 내용 버튼 - 컬럼 8
            detail_btn = QPushButton("상세 내용 확인")
            detail_btn.setMaximumHeight(30)
            detail_btn.setMaximumWidth(130)
            detail_btn.clicked.connect(lambda checked, r=row: self.show_combined_result(r))

            # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_btn)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 8, container)

            # 행 높이 설정
            self.tableWidget.setRowHeight(row, 40)

    def post(self, path, json_data, time_out):
        self.res = None
        headers = CONSTANTS.headers.copy()
        auth = None
        if self.r2 == "B":  # Bearer
            if self.token:
                headers['Authorization'] = f"Bearer {self.token}"
        elif self.r2 == "D":  # Digest
            auth = HTTPDigestAuth(self.accessInfo[0], self.accessInfo[1])
        # self.r2 == "None"이면 그대로 None

        try:
            json_data_dict = json.loads(json_data.decode('utf-8'))
            trans_protocol = json_data_dict.get("transProtocol", {})    # 이 부분 수정해야함
            if trans_protocol:
                # 웹훅 서버 시작 (transProtocolType이 WebHook인 경우만)
                if "WebHook" == self.spec_config.get('trans_protocol', self.current_spec_id)[self.cnt]:
                    self.webhook_flag = True
                    time.sleep(0.001)
                    url = CONSTANTS.WEBHOOK_HOST  # ✅ 기본값 수정
                    port = CONSTANTS.WEBHOOK_PORT  # ✅ 포트도 2001로

                    msg = {}
                    self.step_buffers[self.cnt]["is_webhook_api"] = True

                    self.webhook_cnt = self.cnt
                    self.webhook_thread = WebhookThread(url, port, msg)
                    self.webhook_thread.result_signal.connect(self.handle_webhook_result)
                    self.webhook_thread.start()
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()

        try:
            path = re.sub(r'\d+$', '', path)
            print(f"[DEBUG] [post] Sending request to {path} with auth_type={self.r2}, token={self.token}")
            self.res = requests.post(
                path,
                headers=headers,
                data=json_data,
                auth=auth,
                verify=False,
                timeout=time_out
            )
        except Exception as e:
            print(e)

    # 임시 수정 
    def handle_webhook_result(self, result):
        self.webhook_res = result
        self.webhook_thread.stop()
        self._push_event(self.webhook_cnt, "WEBHOOK", result)

    # 웹훅 검증
    def get_webhook_result(self):
        # ✅ 웹훅 응답이 null인 경우에도 검증을 수행하여 실패로 카운트
        # None이거나 빈 값인 경우 빈 딕셔너리로 처리
        webhook_data = self.webhook_res if self.webhook_res else {}
        tmp_webhook_res = json.dumps(webhook_data, indent=4, ensure_ascii=False) if webhook_data else "null"
        
        if self.webhook_cnt < len(self.message):
            message_name = "step " + str(self.webhook_cnt + 1) + ": " + self.message[self.webhook_cnt]
        else:
            message_name = f"step {self.webhook_cnt + 1}: (index out of range)"

        # ✅ 디버깅: 웹훅 이벤트 스키마 검증 (첫 호출에만 출력)
        if not hasattr(self, '_webhook_debug_printed'):
            self._webhook_debug_printed = True
            print(f"\n[DEBUG] ========== 웹훅 이벤트 검증 디버깅 ==========")
            print(
                f"[DEBUG] webhook_cnt={self.webhook_cnt}, API={self.message[self.webhook_cnt] if self.webhook_cnt < len(self.message) else 'N/A'}")
            print(f"[DEBUG] webhookSchema 총 개수={len(self.webhookSchema)}")
            print(f"[DEBUG] webhook_res is None: {self.webhook_res is None}")

        schema_to_check = self.webhookSchema[self.cnt]

        # ⭐ 추가: webhook_res가 None이면 timeout 처리
        if self.webhook_res is None:
            # timeout_field_finder로 스키마의 필드 개수 계산
            from core.json_checker_new import timeout_field_finder
            tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(schema_to_check)
            key_error_cnt = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
            if self.flag_opt:
                key_error_cnt += tmp_fields_opt_cnt

            val_result = "FAIL"
            val_text = "Webhook Message Missing!"
            key_psss_cnt = 0
            opt_correct = 0
            opt_error = tmp_fields_opt_cnt if self.flag_opt else 0
        else:
            # ✅ 정상적으로 webhook 데이터가 있는 경우 검증
            val_result, val_text, key_psss_cnt, key_error_cnt, opt_correct, opt_error = json_check_(
                schema=schema_to_check,
                data=webhook_data,
                flag=self.flag_opt,
                reference_context=self.reference_context
            )

        if not hasattr(self, '_webhook_debug_printed') or not self._webhook_debug_printed:
            print(f"[DEBUG] ==========================================\n")

        self.valResult.append(
            f'<div style="font-size: 20px; font-weight: bold; color: #333; font-family: \'Noto Sans KR\'; margin-top: 10px;">{message_name}</div>')
        self.valResult.append(
            '<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 5px;">=== 웹훅 이벤트 데이터 ===</div>')
        self.valResult.append(
            f'<pre style="font-size: 18px; color: #1f2937; font-family: \'Consolas\', monospace; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; padding: 10px; margin: 5px 0;">{tmp_webhook_res}</pre>')

        if val_result == "PASS":
            self.valResult.append(
                f'<div style="font-size: 18px; color: #10b981; font-family: \'Noto Sans KR\'; margin-top: 5px;">웹훅 검증 결과: {val_result}</div>')
            self.valResult.append(
                '<div style="font-size: 18px; color: #10b981; font-family: \'Noto Sans KR\';">웹훅 데이터 검증 성공</div>')
        else:
            self.valResult.append(
                f'<div style="font-size: 18px; color: #ef4444; font-family: \'Noto Sans KR\'; margin-top: 5px;">웹훅 검증 결과: {val_result}</div>')
            self.valResult.append(
                '<div style="font-size: 18px; color: #ef4444; font-family: \'Noto Sans KR\';">웹훅 데이터 검증 실패</div>')

        # ✅ step_pass_counts 배열에 웹훅 결과 추가 (배열이 없으면 생성하지 않음)
        # 점수 업데이트는 모든 재시도 완료 후에 일괄 처리됨 (플랫폼과 동일)

        # ✅ 점수는 표시하지 않음 (재시도 완료 후에만 표시)
        # 평가 점수 디스플레이 업데이트는 재시도 완료 시에만 호출

        if val_result == "PASS":
            msg = "\n" + tmp_webhook_res + "\n\n" + "Result: " + val_text + "\n"
            img = self.img_pass
        else:
            msg = "\n" + tmp_webhook_res + "\n\n" + "Result: " + val_result + "\nResult details:\n" + val_text + "\n"
            img = self.img_fail

        # ✅ 웹훅 검증 결과를 기존 누적 필드 수에 추가
        if self.webhook_cnt < self.tableWidget.rowCount():
            # 기존 누적 필드 수 가져오기
            if hasattr(self, 'step_pass_counts') and hasattr(self, 'step_error_counts'):
                # ✅ 웹훅 결과를 기존 step_pass_counts에 추가 (inbound + webhook)
                self.step_pass_counts[self.webhook_cnt] += key_psss_cnt
                self.step_error_counts[self.webhook_cnt] += key_error_cnt

                # ⭐ 선택 필드 합산
                if hasattr(self, 'step_opt_pass_counts') and hasattr(self, 'step_opt_error_counts'):
                    self.step_opt_pass_counts[self.webhook_cnt] += opt_correct
                    self.step_opt_error_counts[self.webhook_cnt] += opt_error

                # 누적된 총 필드 수로 테이블 업데이트
                accumulated_pass = self.step_pass_counts[self.webhook_cnt]
                accumulated_error = self.step_error_counts[self.webhook_cnt]

                print(f"[WEBHOOK] 누적 결과: pass={accumulated_pass}, error={accumulated_error}")
            else:
                # 누적 배열이 없으면 웹훅 결과만 사용
                accumulated_pass = key_psss_cnt
                accumulated_error = key_error_cnt

            if self.webhook_cnt < len(self.num_retries_list):
                current_retries = self.num_retries_list[self.webhook_cnt]
            else:
                current_retries = 1

                # 누적된 필드 수로 테이블 업데이트
            self.update_table_row_with_retries(
                self.webhook_cnt, val_result, accumulated_pass, accumulated_error,
                tmp_webhook_res, self._to_detail_text(val_text), current_retries
            )

        # step_buffers 업데이트 추가 (실시간 모니터링과 상세보기 일치)
        if self.webhook_cnt < len(self.step_buffers):
            webhook_data_text = tmp_webhook_res
            webhook_error_text = self._to_detail_text(val_text) if val_result == "FAIL" else "오류가 없습니다."
            # ✅ 웹훅 이벤트 데이터를 명확히 표시
            self.step_buffers[self.webhook_cnt]["data"] += f"\n\n--- Webhook 이벤트 데이터 ---\n{webhook_data_text}"
            self.step_buffers[self.webhook_cnt][
                "error"] += f"\n\n--- Webhook 검증 ---\n{webhook_error_text}"  # 얘가 문제임 화딱지가 난다
            self.step_buffers[self.webhook_cnt]["result"] = val_result

            # 메시지 저장
        if self.webhook_cnt == 6:
            self.step7_msg += msg
        elif self.webhook_cnt == 4:
            self.step5_msg += msg
        elif self.webhook_cnt == 3:
            self.step4_msg += msg

        self.webhook_res = None  # init
        self.webhook_flag = False

    def update_view(self):

        try:
            time_interval = 0

            # cnt가 리스트 길이 이상이면 종료 처리 (무한 반복 방지)
            if self.cnt >= len(self.message) or self.cnt >= len(self.time_outs):
                self.tick_timer.stop()
                self.valResult.append("검증 절차가 완료되었습니다.")
                self.cnt = 0
                return
            # 플랫폼과 동일하게 time_pre/cnt_pre 조건 적용
            if self.time_pre == 0 or self.cnt != self.cnt_pre:
                self.time_pre = time.time()
                self.cnt_pre = self.cnt
                return  # 첫 틱에서는 대기만 하고 리턴
            else:
                time_interval = time.time() - self.time_pre

            # 웹훅 이벤트 수신 확인 - webhook_thread.wait()이 이미 동기화 처리하므로 별도 sleep 불필요
            if self.webhook_flag is True:
                print(
                    f"[TIMING_DEBUG] 웹훅 이벤트 수신 완료 (API: {self.message[self.cnt] if self.cnt < len(self.message) else 'N/A'})")
                print(f"[TIMING_DEBUG] ✅ 웹훅 스레드의 wait()이 동기화 처리 완료 (수동 sleep 제거됨)")

            if (self.post_flag is False and
                    self.processing_response is False and
                    self.cnt < len(self.message) and
                    self.cnt < len(self.num_retries_list) and
                    self.current_retry < self.num_retries_list[self.cnt]):

                self.message_in_cnt += 1
                self.time_pre = time.time()

                retry_info = f" (시도 {self.current_retry + 1}/{self.num_retries_list[self.cnt]})"
                if self.cnt < len(self.message):
                    display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else self.message[self.cnt]
                    self.message_name = "step " + str(self.cnt + 1) + ": " + display_name + retry_info
                else:
                    self.message_name = f"step {self.cnt + 1}: (index out of range)" + retry_info

                # 첫 번째 시도일 때만 메시지 표시 - 제거 (응답 처리 시 표시)
                # if self.current_retry == 0:
                #     self.append_monitor_log(
                #         step_name=self.message_name
                #     )

                # 시스템은 요청 송신 메시지 표시 안 함 (응답만 표시)
                # self.append_monitor_log(
                #     step_name=f"요청 메시지 송신 [{self.current_retry + 1}/{self.num_retries_list[self.cnt]}]",
                #     result_status="진행중"
                # )

                if self.cnt == 0 and self.current_retry == 0:
                    self.tmp_msg_append_flag = True

                # 시스템이 플랫폼에 요청 전송
                current_timeout = self.time_outs[self.cnt] / 1000 if self.cnt < len(self.time_outs) else 5.0
                path = self.pathUrl + "/" + (self.message[self.cnt] if self.cnt < len(self.message) else "")
                inMessage = self.inMessage[self.cnt] if self.cnt < len(self.inMessage) else {}
                # ✅ Data Mapper 적용 - 이전 응답 데이터로 요청 업데이트
                # generator는 이미 self.latest_events를 참조하고 있으므로 재할당 불필요
                print(f"[DEBUG][MAPPER] latest_events 상태: {list(self.latest_events.keys())}")
                inMessage = self._apply_request_constraints(inMessage, self.cnt)

                trans_protocol = inMessage.get("transProtocol", {})  # 이 부분 수정해야함
                if trans_protocol:
                    trans_protocol_type = trans_protocol.get("transProtocolType", {})
                    if "WebHook".lower() in str(trans_protocol_type).lower():
                        WEBHOOK_IP = CONSTANTS.WEBHOOK_PUBLIC_IP
                        WEBHOOK_PORT = CONSTANTS.WEBHOOK_PORT  # 웹훅 수신 포트
                        WEBHOOK_URL = f"https://{WEBHOOK_IP}:{WEBHOOK_PORT}"  # 플랫폼/시스템이 웹훅을 보낼 주소

                        trans_protocol = {
                            "transProtocolType": "WebHook",
                            "transProtocolDesc": WEBHOOK_URL
                        }
                        inMessage["transProtocol"] = trans_protocol
                        # 재직렬화
                        print(f"[DEBUG] [post] transProtocol 설정 추가됨: {inMessage}")
                elif self.r2 == "B" and self.message[self.cnt] == "Authentication":
                    inMessage["userID"] = self.accessInfo[0]
                    inMessage["userPW"] = self.accessInfo[1]

                # 시스템은 요청 데이터 표시 안 함 (응답만 표시)
                tmp_request = json.dumps(inMessage, indent=4, ensure_ascii=False)
                # self.append_monitor_log(
                #     step_name=f"[요청 {self.current_retry + 1}회차]",
                #     request_json=tmp_request,
                #     result_status="진행중"
                # )

                json_data = json.dumps(inMessage).encode('utf-8')

                # ✅ REQUEST 기록 제거 - 서버(api_server.py)에서만 기록하도록 변경
                self._push_event(self.cnt, "REQUEST", inMessage)

                api_name = self.message[self.cnt] if self.cnt < len(self.message) else ""
                if api_name and isinstance(inMessage, dict):
                    self.reference_context[f"/{api_name}"] = inMessage

                # 순서 확인용 로그
                print(
                    f"[SYSTEM] 플랫폼에 요청 전송: {(self.message[self.cnt] if self.cnt < len(self.message) else 'index out of range')} (시도 {self.current_retry + 1})")

                t = threading.Thread(target=self.post, args=(path, json_data, current_timeout), daemon=True)
                t.start()
                self.post_flag = True

            # timeout 조건은 응답 대기/재시도 판단에만 사용
            elif self.cnt < len(self.time_outs) and time_interval >= self.time_outs[
                self.cnt] / 1000 and self.post_flag is True:

                if self.cnt < len(self.message):
                    self.message_error.append([self.message[self.cnt]])
                else:
                    self.message_error.append([f"index out of range: {self.cnt}"])
                self.message_in_cnt = 0
                current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1

                # 현재 시도에 대한 타임아웃 처리
                if self.cnt < len(self.outSchema):
                    tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(self.outSchema[self.cnt])
                else:
                    tmp_fields_rqd_cnt, tmp_fields_opt_cnt = 0, 0

                # ✅ 웹훅 API인 경우 웹훅 스키마 필드 수도 추가
                if self.cnt < len(self.trans_protocols):
                    current_protocol = self.trans_protocols[self.cnt]
                    if current_protocol == "WebHook" and self.cnt < len(self.webhookSchema):
                        webhook_schema = self.webhookSchema[self.cnt]
                        if webhook_schema:
                            webhook_rqd_cnt, webhook_opt_cnt = timeout_field_finder(webhook_schema)
                            tmp_fields_rqd_cnt += webhook_rqd_cnt
                            tmp_fields_opt_cnt += webhook_opt_cnt
                            print(f"[TIMEOUT] 웹훅 스키마 필드 추가: rqd={webhook_rqd_cnt}, opt={webhook_opt_cnt}")

                add_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                if self.flag_opt:
                    add_err += tmp_fields_opt_cnt

                total_fields = self.total_pass_cnt + self.total_error_cnt
                if total_fields > 0:
                    score_value = (self.total_pass_cnt / total_fields) * 100
                else:
                    score_value = 0
                
                # 타임아웃 로그를 HTML 카드로 출력
                api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                timeout_sec = self.time_outs[self.cnt] / 1000 if self.cnt < len(self.time_outs) else 0
                self.append_monitor_log(
                    step_name=f"Step {self.cnt + 1}: {api_name}",
                    request_json="",
                    score=score_value,
                    details=f"⏱️ Timeout ({timeout_sec}초) - Message Missing! (시도 {self.current_retry + 1}/{current_retries}) | 통과: {self.total_pass_cnt}, 오류: {self.total_error_cnt}"
                )

                # 재시도 카운터 증가
                self.current_retry += 1
                self.update_table_row_with_retries(
                    self.cnt,
                    "진행중",  # ← 검정색 아이콘
                    0, 0,  # ← 아직 결과 없음
                    "검증 진행중...",
                    f"시도 {self.current_retry }/{current_retries}",
                    self.current_retry   # ← 검증 횟수: 1, 2, 3...
                )
                QApplication.processEvents()  # UI 즉시 반영

                # 재시도 완료 여부 확인
                if (self.cnt < len(self.num_retries_list) and
                        self.current_retry >= self.num_retries_list[self.cnt]):
                    # 모든 재시도 완료 - 버퍼에 최종 결과 저장
                    self.step_buffers[self.cnt]["data"] = "타임아웃으로 인해 수신된 데이터가 없습니다."
                    current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                    self.step_buffers[self.cnt]["error"] = f"Message Missing! - 모든 시도({current_retries}회)에서 타임아웃 발생"
                    self.step_buffers[self.cnt]["result"] = "FAIL"
                    self.step_buffers[self.cnt]["events"] = list(self.trace.get(self.cnt, []))

                    # ✅ step_pass_counts 배열에 저장 (배열이 있는 경우에만)
                    if hasattr(self, 'step_pass_counts') and self.cnt < len(self.step_pass_counts):
                        self.step_pass_counts[self.cnt] = 0
                        self.step_error_counts[self.cnt] = add_err
                    
                    # ✅ 전체 점수 업데이트 (모든 spec 합산)
                    self.global_error_cnt += add_err
                    self.global_pass_cnt += 0

                    # 평가 점수 디스플레이 업데이트
                    self.update_score_display()
                    # 테이블 업데이트 (Message Missing)
                    self.update_table_row_with_retries(self.cnt, "FAIL", 0, add_err, "", "Message Missing!",
                                                       current_retries)

                    # 다음 API로 이동
                    self.cnt += 1
                    self.current_retry = 0  # 재시도 카운터 리셋

                    # 다음 API를 위한 누적 카운트 초기 설정 확인
                    if hasattr(self, 'step_pass_counts') and self.cnt < len(self.step_pass_counts):
                        self.step_pass_counts[self.cnt] = 0
                        self.step_error_counts[self.cnt] = 0
                        self.step_pass_flags[self.cnt] = 0

                self.message_in_cnt = 0
                self.post_flag = False
                self.processing_response = False

                # 플랫폼과 동일한 대기 시간 설정
                self.time_pre = time.time()

                if self.cnt >= len(self.message):
                    self.tick_timer.stop()
                    self.valResult.append("검증 절차가 완료되었습니다.")

                    # ✅ 현재 spec 데이터 저장
                    self.save_current_spec_data()

                    self.processing_response = False
                    self.post_flag = False

                    self.cnt = 0
                    self.current_retry = 0

                    # 최종 리포트 생성
                    total_fields = self.total_pass_cnt + self.total_error_cnt

                    # ✅ JSON 결과 자동 저장 추가
                    print(f"[DEBUG] 평가 완료 - 자동 저장 시작")
                    try:
                        self.run_status = "완료"
                        result_json = build_result_json(self)
                        url = f"{CONSTANTS.management_url}/api/integration/test-results"
                        response = requests.post(url, json=result_json)
                        print("✅ 시험 결과 전송 상태 코드:", response.status_code)
                        print("📥  시험 결과 전송 응답:", response.text)
                        json_path = os.path.join(result_dir, "response_results.json")
                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump(result_json, f, ensure_ascii=False, indent=2)
                        print(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                        self.append_monitor_log(
                            step_name="결과 파일 저장 완료",
                            details=json_path
                        )
                        print(f"[DEBUG] try 블록 정상 완료")

                    except Exception as e:
                        print(f"❌ JSON 저장 중 오류 발생: {e}")
                        import traceback
                        traceback.print_exc()
                        self.valResult.append(f"\n결과 저장 실패: {str(e)}")
                        print(f"[DEBUG] except 블록 실행됨")

                    finally:
                        # ✅ 평가 완료 시 일시정지 파일 정리 (에러 발생 여부와 무관하게 항상 실행)
                        print(f"[DEBUG] ========== finally 블록 진입 ==========")
                        self.cleanup_paused_file()
                        print(f"[DEBUG] ========== finally 블록 종료 ==========")

                    self.sbtn.setEnabled(True)
                    self.stop_btn.setDisabled(True)


            # 응답이 도착한 경우 처리
            elif self.post_flag == True:
                if self.res != None:
                    # 응답 처리 시작
                    if self.res != None:
                        # 응답 처리 시작
                        self.processing_response = True

                        # 시스템은 step 메시지와 응답 수신 메시지 표시 안 함 (받은 데이터만 표시)
                        # if self.cnt == 0 or self.tmp_msg_append_flag:
                        #     self.append_monitor_log(
                        #         step_name=self.message_name,
                        #         result_status="진행중"
                        #     )

                        # self.append_monitor_log(
                        #     step_name=f"응답 메시지 수신 [{self.current_retry + 1}/{self.num_retries_list[self.cnt]}]",
                        #     result_status="진행중"
                        # )

                        res_data = self.res.text

                        try:
                            res_data = json.loads(res_data)

                            if isinstance(res_data, dict) and "code_value" in res_data:
                                del res_data["code_value"]

                        except Exception as e:
                            self._append_text(f"응답 JSON 파싱 오류: {e}")
                            self._append_text({"raw_response": self.res.text})
                            self.post_flag = False
                            self.processing_response = False
                            self.current_retry += 1
                            return

                        # ✅ RESPONSE 기록 제거 - 서버(api_server.py)에서만 기록하도록 변경
                        self._push_event(self.cnt, "RESPONSE", res_data)

                        # 현재 재시도 정보
                        current_retries = self.num_retries_list[self.cnt] if self.cnt < len(
                            self.num_retries_list) else 1
                        current_protocol = self.trans_protocols[self.cnt] if self.cnt < len(
                            self.trans_protocols) else "Unknown"

                        # 단일 응답에 대한 검증 처리
                        tmp_res_auth = json.dumps(res_data, indent=4, ensure_ascii=False)

                        # 실시간 모니터링 창에 응답 데이터 표시
                        # 첫 번째 응답일 때만 API 명과 검증 예정 횟수 표시
                        if self.current_retry == 0:
                            api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                            display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                            self.append_monitor_log(
                                step_name=f"Step {self.cnt + 1}: {display_name} ({self.current_retry + 1}/{current_retries})",
                                details=f"총 {current_retries}회 검증 예정",
                                request_json=tmp_res_auth
                            )
                        else:
                            # 2회차 이상: API 명과 회차만 표시
                            api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                            display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                            self.append_monitor_log(
                                step_name=f"Step {self.cnt + 1}: {display_name} ({self.current_retry + 1}/{current_retries})",
                                request_json=tmp_res_auth
                            )

                    # ✅ 디버깅: 어떤 스키마로 검증하는지 확인
                    if self.current_retry == 0:  # 첫 시도에만 출력
                        print(f"\n[DEBUG] ========== 스키마 검증 디버깅 ==========")
                        print(
                            f"[DEBUG] cnt={self.cnt}, API={self.message[self.cnt] if self.cnt < len(self.message) else 'N/A'}")
                        print(f"[DEBUG] webhook_flag={self.webhook_flag}")
                        print(f"[DEBUG] current_protocol={current_protocol}")
                        # print(f"[DEBUG] outSchema 총 개수={len(self.outSchema)}")

                        # ✅ 웹훅 API의 구독 응답은 일반 스키마 사용
                        # webhook_flag는 실제 웹훅 이벤트 수신 시에만 True
                        # 구독 응답은 항상 outSchema[self.cnt] 사용
                        schema_index = self.cnt
                        print(f"[DEBUG] 사용 스키마: outSchema[{schema_index}]")

                        # 스키마 필드 확인
                        if self.cnt < len(self.outSchema):
                            schema_to_use = self.outSchema[self.cnt]
                            if isinstance(schema_to_use, dict):
                                schema_keys = list(schema_to_use.keys())[:5]
                                print(f"[DEBUG] 스키마 필드 (first 5): {schema_keys}")

                    # val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.outSchema[self.cnt], res_data, self.flag_opt)
                    resp_rules = {}
                    try:
                        resp_rules = self.resp_rules or {}
                    except Exception as e:
                        resp_rules = {}
                        print(f"[ERROR] 응답 검증 규칙 로드 실패: {e}")

                    # 🆕 응답 검증용 - resp_rules의 각 필드별 referenceEndpoint/Max/Min에서 trace 파일 로드
                    if resp_rules:
                        for field_path, validation_rule in resp_rules.items():
                            validation_type = validation_rule.get("validationType", "")
                            direction = "REQUEST" if "request-field" in validation_type else "RESPONSE"

                            # referenceEndpoint 처리
                            ref_endpoint = validation_rule.get("referenceEndpoint", "")
                            if ref_endpoint:
                                ref_api_name = ref_endpoint.lstrip("/")
                                # latest_events에 없으면 trace 파일에서 로드
                                if ref_api_name not in self.latest_events or direction not in self.latest_events.get(ref_api_name, {}):
                                    print(f"[TRACE] {ref_endpoint} {direction}를 trace 파일에서 로드 시도")
                                    response_data = self._load_from_trace_file(ref_api_name, direction)
                                    if response_data and isinstance(response_data, dict):
                                        self.reference_context[ref_endpoint] = response_data
                                        print(f"[TRACE] {ref_endpoint} {direction}를 trace 파일에서 로드 완료")
                                else:
                                    # latest_events에 있으면 거기서 가져오기
                                    event_data = self.latest_events.get(ref_api_name, {}).get(direction, {})
                                    if event_data and isinstance(event_data, dict):
                                        self.reference_context[ref_endpoint] = event_data.get("data", {})
                            
                            # referenceEndpointMax 처리
                            ref_endpoint_max = validation_rule.get("referenceEndpointMax", "")
                            if ref_endpoint_max:
                                ref_api_name_max = ref_endpoint_max.lstrip("/")
                                if ref_api_name_max not in self.latest_events or direction not in self.latest_events.get(ref_api_name_max, {}):
                                    print(f"[TRACE] {ref_endpoint_max} {direction}를 trace 파일에서 로드 시도 (Max)")
                                    response_data_max = self._load_from_trace_file(ref_api_name_max, direction)
                                    if response_data_max and isinstance(response_data_max, dict):
                                        self.reference_context[ref_endpoint_max] = response_data_max
                                        print(f"[TRACE] {ref_endpoint_max} {direction}를 trace 파일에서 로드 완료 (Max)")
                                else:
                                    event_data = self.latest_events.get(ref_api_name_max, {}).get(direction, {})
                                    if event_data and isinstance(event_data, dict):
                                        self.reference_context[ref_endpoint_max] = event_data.get("data", {})
                            
                            # referenceEndpointMin 처리
                            ref_endpoint_min = validation_rule.get("referenceEndpointMin", "")
                            if ref_endpoint_min:
                                ref_api_name_min = ref_endpoint_min.lstrip("/")
                                if ref_api_name_min not in self.latest_events or direction not in self.latest_events.get(ref_api_name_min, {}):
                                    print(f"[TRACE] {ref_endpoint_min} {direction}를 trace 파일에서 로드 시도 (Min)")
                                    response_data_min = self._load_from_trace_file(ref_api_name_min, direction)
                                    if response_data_min and isinstance(response_data_min, dict):
                                        self.reference_context[ref_endpoint_min] = response_data_min
                                        print(f"[TRACE] {ref_endpoint_min} {direction}를 trace 파일에서 로드 완료 (Min)")
                                else:
                                    event_data = self.latest_events.get(ref_api_name_min, {}).get(direction, {})
                                    if event_data and isinstance(event_data, dict):
                                        self.reference_context[ref_endpoint_min] = event_data.get("data", {})

                    try:
                        val_result, val_text, key_psss_cnt, key_error_cnt, opt_correct, opt_error = json_check_(
                            self.outSchema[self.cnt],
                            res_data,
                            self.flag_opt,
                            validation_rules=resp_rules,
                            reference_context=self.reference_context
                        )
                    except TypeError as te:
                        print(f"[ERROR] 응답 검증 중 TypeError 발생: {te}, 일반 검증으로 재시도")
                        val_result, val_text, key_psss_cnt, key_error_cnt, opt_correct, opt_error = json_check_(
                            self.outSchema[self.cnt],
                            res_data,
                            self.flag_opt
                        )
                    if self.message[self.cnt] == "Authentication":
                        self.handle_authentication_response(res_data)

                    if self.current_retry == 0:  # 첫 시도에만 출력
                        print(f"[DEBUG] 검증 결과: {val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
                        print(f"[DEBUG] ==========================================\n")

                    # 이번 시도의 결과
                    final_result = val_result

                    # ✅ 마지막 시도 결과로 덮어쓰기 (누적 X)
                    if not hasattr(self, 'step_pass_counts'):
                        api_count = len(self.videoMessages)
                        self.step_pass_counts = [0] * api_count
                        self.step_error_counts = [0] * api_count
                        self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
                        self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수
                        self.step_pass_flags = [0] * api_count

                    # ✅ 이번 시도 결과로 덮어쓰기 (누적하지 않음!)
                    self.step_pass_counts[self.cnt] = key_psss_cnt
                    self.step_error_counts[self.cnt] = key_error_cnt
                    self.step_opt_pass_counts[self.cnt] = opt_correct  # 선택 필드 통과 수
                    self.step_opt_error_counts[self.cnt] = opt_error  # 선택 필드 에러 수
                    
                    print(f"[SCORE DEBUG] API {self.cnt} 시도 {self.current_retry + 1}: pass={key_psss_cnt}, error={key_error_cnt}")
                    print(f"[SCORE DEBUG] step_pass_counts[{self.cnt}] = {self.step_pass_counts[self.cnt]}")
                    print(f"[SCORE DEBUG] step_error_counts[{self.cnt}] = {self.step_error_counts[self.cnt]}")

                    if final_result == "PASS":
                        self.step_pass_flags[self.cnt] += 1

                    total_pass_count = self.step_pass_counts[self.cnt]
                    total_error_count = self.step_error_counts[self.cnt]

                    # (1) 스텝 버퍼 저장 - 재시도별로 누적
                    # ✅ 시스템은 플랫폼이 보내는 데이터를 표시해야 함
                    if isinstance(res_data, (dict, list)):
                        platform_data = res_data
                    else:
                        # 혹시 dict/list가 아니면 raw 텍스트를 감싸서 기록
                        platform_data = {"raw_response": self.res.text}

                    data_text = json.dumps(platform_data, indent=4, ensure_ascii=False)

                    # ✅ PASS인 경우 오류 텍스트 무시 (val_text에 불필요한 정보가 있을 수 있음)
                    if val_result == "FAIL":
                        error_text = self._to_detail_text(val_text)
                    else:
                        # PASS일 때는 val_text를 그대로 사용 (400 에러 응답 메시지 포함)
                        error_text = val_text if isinstance(val_text, str) else "오류가 없습니다."

                    # ✅ raw_data_list에 현재 응답 데이터 추가 (재개 시 retry count 복원용)
                    self.step_buffers[self.cnt]["raw_data_list"].append(platform_data)

                    # 기존 버퍼에 누적 (재시도 정보와 함께)
                    if self.current_retry == 0:
                        # 첫 번째 시도인 경우 초기화
                        self.step_buffers[self.cnt][
                            "data"] = f"[시도 {self.current_retry + 1}/{current_retries}]\n{data_text}"
                        self.step_buffers[self.cnt][
                            "error"] = f"[시도 {self.current_retry + 1}/{current_retries}]\n{error_text}"
                        self.step_buffers[self.cnt]["result"] = val_result  # 첫 시도 결과로 초기화
                    else:
                        # 재시도인 경우 누적
                        self.step_buffers[self.cnt][
                            "data"] += f"\n\n[시도 {self.current_retry + 1}/{current_retries}]\n{data_text}"
                        self.step_buffers[self.cnt][
                            "error"] += f"\n\n[시도 {self.current_retry + 1}/{current_retries}]\n{error_text}"
                        self.step_buffers[self.cnt]["result"] = val_result  # 마지막 시도 결과로 항상 갱신
                    # 최종 결과 판정 (플랫폼과 동일한 로직)
                    if self.current_retry + 1 >= current_retries:
                        # 모든 재시도 완료 - 모든 시도가 PASS일 때만 PASS
                        if self.step_pass_flags[self.cnt] >= current_retries:
                            self.step_buffers[self.cnt]["result"] = "PASS"
                        else:
                            self.step_buffers[self.cnt]["result"] = "FAIL"
                        # 마지막 시도 결과의 오류 텍스트로 덮어쓰기 (실패 시)
                        if self.step_buffers[self.cnt]["result"] == "FAIL":
                            self.step_buffers[self.cnt][
                                "error"] = f"[시도 {self.current_retry + 1}/{current_retries}]\n{error_text}"

                    # 진행 중 표시 (플랫폼과 동일하게)
                    display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else self.message[self.cnt]
                    message_name = "step " + str(self.cnt + 1) + ": " + display_name
                    # 각 시도별로 pass/error count는 누적이 아니라 이번 시도만 반영해야 함
                    # key_psss_cnt, key_error_cnt는 이번 시도에 대한 값임
                    if self.current_retry + 1 < current_retries:
                        # 아직 재시도가 남아있으면 진행중으로 표시 (누적 카운트 표시)
                        self.update_table_row_with_retries(
                            self.cnt, "진행중", total_pass_count, total_error_count,
                            f"검증 진행중... ({self.current_retry + 1}/{current_retries})",
                            f"시도 {self.current_retry + 1}/{current_retries}", self.current_retry + 1)
                    else:
                        # ✅ 마지막 시도이면 최종 결과 표시 (누적된 필드 수 사용!)
                        final_buffer_result = self.step_buffers[self.cnt]["result"]
                        self.update_table_row_with_retries(
                            self.cnt, final_buffer_result, total_pass_count, total_error_count,
                            tmp_res_auth, error_text, current_retries)

                    # UI 즉시 업데이트 (화면에 반영)
                    QApplication.processEvents()

                    # ✅ 검증 진행 중 로그를 HTML 카드로 출력
                    api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                    
                    # 데이터 포맷팅 (JSON 형식으로)
                    try:
                        if data_text and data_text.strip():
                            json_obj = json.loads(data_text)
                            formatted_data = json.dumps(json_obj, indent=2, ensure_ascii=False)
                        else:
                            formatted_data = data_text
                    except:
                        formatted_data = data_text
                    
                    # 웹훅 여부에 따라 다른 표시
                    api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                    display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                    if current_protocol == "WebHook":
                        step_title = f"결과: {display_name} - 웹훅 구독 ({self.current_retry + 1}/{current_retries})"
                    else:
                        step_title = f"결과: {display_name} ({self.current_retry + 1}/{current_retries})"
                    
                    # 마지막 시도에만 점수 표시, 진행중에는 표시 안함
                    if self.current_retry + 1 >= current_retries:
                        # 마지막 시도 - 최종 결과 표시
                        total_fields = total_pass_count + total_error_count
                        score_value = (total_pass_count / total_fields * 100) if total_fields > 0 else 0
                        self.append_monitor_log(
                            step_name=step_title,
                            request_json="",  # 데이터는 앞서 출력되었으므로 생략
                            result_status=final_result,
                            score=score_value,
                            details=f"통과: {total_pass_count}, 오류: {total_error_count} | 프로토콜: {current_protocol}"
                        )
                    else:
                        # 중간 시도 - 진행중 표시
                        self.append_monitor_log(
                            step_name=step_title,
                            request_json="",  # 데이터는 앞서 출력되었으므로 생략
                            details=f"검증 진행 중... | 프로토콜: {current_protocol}"
                        )

                    # ✅ 웹훅 처리를 재시도 완료 체크 전에 실행 (step_pass_counts 업데이트를 위해)
                    if self.webhook_flag:
                        print(f"[WEBHOOK] 웹훅 처리 시작 (API {self.cnt})")
                        self.get_webhook_result()

                    # 재시도 카운터 증가
                    self.current_retry += 1

                    # ✅ 현재 API의 모든 재시도가 완료되었는지 확인
                    if (self.cnt < len(self.num_retries_list) and
                            self.current_retry >= self.num_retries_list[self.cnt]):
                        # ✅ 모든 재시도 완료
                        # ✅ 웹훅 API의 경우 step_pass_counts가 이미 업데이트되었을 수 있으므로 배열에서 직접 가져옴
                        final_pass_count = self.step_pass_counts[self.cnt]
                        final_error_count = self.step_error_counts[self.cnt]
                        
                        print(f"[SCORE] API {self.cnt} 완료: pass={final_pass_count}, error={final_error_count}")

                        # ✅ 분야별 점수 업데이트 (현재 spec만)
                        self.total_pass_cnt += final_pass_count
                        self.total_error_cnt += final_error_count

                        # ✅ 전체 점수 업데이트 (모든 spec 합산) - API당 1회만 추가
                        self.global_error_cnt += final_error_count
                        self.global_pass_cnt += final_pass_count
                        # ✅ 선택 필드 통과 수도 전체 점수에 누적
                        final_opt_pass_count = self.step_opt_pass_counts[self.cnt]
                        self.global_opt_pass_cnt += final_opt_pass_count
                        # ✅ 선택 필드 에러 수도 전체 점수에 누적
                        final_opt_error_count = self.step_opt_error_counts[self.cnt]
                        self.global_opt_error_cnt += final_opt_error_count

                        print(f"[SCORE] 분야별 점수: pass={self.total_pass_cnt}, error={self.total_error_cnt}")
                        print(f"[SCORE] 전체 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}")

                        # ✅ 전체 점수 포함하여 디스플레이 업데이트 (재시도 완료 후에만)
                        self.update_score_display()
                        
                        # ✅ 최종 점수는 이미 HTML 카드에 포함되어 있으므로 별도 표시 안함

                        self.step_buffers[self.cnt]["events"] = list(self.trace.get(self.cnt, []))

                        # 다음 API로 이동
                        self.cnt += 1
                        self.current_retry = 0

                    self.message_in_cnt = 0
                    self.post_flag = False
                    self.processing_response = False

                    # 재시도 여부에 따라 대기 시간 조정
                    if (self.cnt < len(self.num_retries_list) and
                            self.current_retry < self.num_retries_list[self.cnt] - 1):
                        self.time_pre = time.time()
                    else:
                        self.time_pre = time.time()
                    self.message_in_cnt = 0

                    # ✅ 웹훅 처리는 이미 위에서 완료됨 (중복 제거)

            if self.cnt >= len(self.message):
                self.tick_timer.stop()
                self.append_monitor_log(
                    step_name="시험 완료",
                    details="검증 절차가 완료되었습니다."
                )

                # ✅ 현재 spec 데이터 저장
                self.save_current_spec_data()

                self.processing_response = False
                self.post_flag = False

                self.cnt = 0
                self.current_retry = 0

                # 최종 리포트 생성
                total_fields = self.total_pass_cnt + self.total_error_cnt
                if total_fields > 0:
                    final_score = (self.total_pass_cnt / total_fields) * 100
                else:
                    final_score = 0

                # ✅ 전체 점수 최종 확인 로그
                global_total = self.global_pass_cnt + self.global_error_cnt
                global_score = (self.global_pass_cnt / global_total * 100) if global_total > 0 else 0
                print(
                    f"[FINAL] 분야별 점수: pass={self.total_pass_cnt}, error={self.total_error_cnt}, score={final_score:.1f}%")
                print(
                    f"[FINAL] 전체 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}, score={global_score:.1f}%")

                # ✅ JSON 결과 자동 저장 추가
                print(f"[DEBUG] 평가 완료 - 자동 저장 시작 (경로2)")
                try:
                    self.run_status = "완료"
                    result_json = build_result_json(self)
                    url = f"{CONSTANTS.management_url}/api/integration/test-results"
                    response = requests.post(url, json=result_json)
                    print("✅ 시험 결과 전송 상태 코드:", response.status_code)
                    print("📥  시험 결과 전송 응답:", response.text)
                    json_path = os.path.join(result_dir, "response_results.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result_json, f, ensure_ascii=False, indent=2)
                    print(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                    self.append_monitor_log(
                        step_name="결과 파일 저장 완료",
                        details=json_path
                    )
                    print(f"[DEBUG] try 블록 정상 완료 (경로2)")
                except Exception as e:
                    print(f"❌ JSON 저장 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    self.valResult.append(f"\n결과 저장 실패: {str(e)}")
                    print(f"[DEBUG] except 블록 실행됨 (경로2)")
                finally:
                    # ✅ 평가 완료 시 일시정지 파일 정리 (에러 발생 여부와 무관하게 항상 실행)
                    print(f"[DEBUG] ========== finally 블록 진입 (경로2) ==========")
                    self.cleanup_paused_file()
                    print(f"[DEBUG] ========== finally 블록 종료 (경로2) ==========")

                self.sbtn.setEnabled(True)
                self.stop_btn.setDisabled(True)

        except Exception as err:
            import traceback
            print(f"[ERROR] Exception in update_view: {err}")
            print(f"[ERROR] Current state - cnt={self.cnt}, current_retry={self.current_retry}")
            print(f"[ERROR] Traceback:")
            traceback.print_exc()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error Message: 오류 확인 후 검증 절차를 다시 시작해주세요")
            msg.setInformativeText(f"Error at step {self.cnt + 1}: {str(err)}")
            msg.setWindowTitle("Error")
            msg.exec_()
            self.tick_timer.stop()
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">검증 절차가 중지되었습니다. (오류 위치: Step {self.cnt + 1})</div>')
            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)

    def icon_update_step(self, auth_, result_, text_):
        # 플랫폼과 동일하게 '진행중'이면 검정색, PASS면 초록, FAIL이면 빨강
        if result_ == "PASS":
            msg = auth_ + "\n\n" + "Result: PASS" + "\n" + text_
            img = self.img_pass
        elif result_ == "진행중":
            msg = auth_ + "\n\n" + "Status: " + text_
            img = self.img_none
        else:
            msg = auth_ + "\n\n" + "Result: FAIL" + "\nResult details:\n" + text_
            img = self.img_fail
        return msg, img

    def icon_update(self, tmp_res_auth, val_result, val_text):
        msg, img = self.icon_update_step(tmp_res_auth, val_result, val_text)

        if self.cnt < self.tableWidget.rowCount():
            # 아이콘 위젯 생성
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)

            icon_label = QLabel()
            icon_label.setPixmap(QIcon(img).pixmap(84, 20))
            icon_label.setAlignment(Qt.AlignCenter)

            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)

            self.tableWidget.setCellWidget(self.cnt, 1, icon_widget)

            if self.cnt == 0:
                self.step1_msg += msg
            elif self.cnt == 1:
                self.step2_msg += msg
            elif self.cnt == 2:
                self.step3_msg += msg
            elif self.cnt == 3:
                self.step4_msg += msg
            elif self.cnt == 4:
                self.step5_msg += msg
            elif self.cnt == 5:
                self.step6_msg += msg
            elif self.cnt == 6:
                self.step7_msg += msg
            elif self.cnt == 7:
                self.step8_msg += msg
            elif self.cnt == 8:
                self.step9_msg += msg

    def initUI(self):
        # ✅ 반응형: 최소 크기 설정
        self.setMinimumSize(1680, 1006)

        if not self.embedded:
            self.setWindowTitle('시스템 연동 검증')

        # ✅ 메인 레이아웃
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ✅ 상단 헤더 영역 (반응형 - 배경 늘어남, 로고/타이틀 가운데 고정)
        header_widget = QWidget()
        header_widget.setFixedHeight(64)
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 배경 이미지 설정 (늘어남 - border-image 사용)
        header_bg_path = resource_path("assets/image/common/header.png").replace(chr(92), "/")
        header_widget.setStyleSheet(f"""
            QWidget {{
                border-image: url({header_bg_path}) 0 0 0 0 stretch stretch;
            }}
            QLabel {{
                border-image: none;
                background: transparent;
            }}
        """)

        # 헤더 레이아웃 (좌측 정렬, padding: 좌우 48px, 상하 10px)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(48, 10, 48, 10)
        header_layout.setSpacing(0)

        # 로고 이미지 (90x32)
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("assets/image/common/logo_KISA.png"))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setFixedSize(90, 32)
        header_layout.addWidget(logo_label)

        # 로고와 타이틀 사이 간격 20px
        header_layout.addSpacing(20)

        # 타이틀 이미지 (408x36)
        header_title_label = QLabel()
        header_title_pixmap = QPixmap(resource_path("assets/image/test_runner/runner_title.png"))
        header_title_label.setPixmap(header_title_pixmap.scaled(407, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_title_label.setFixedSize(407, 36)
        header_layout.addWidget(header_title_label)

        # 오른쪽 stretch (나머지 공간 채우기)
        header_layout.addStretch()

        mainLayout.addWidget(header_widget)

        # ✅ 본문 영역 컨테이너 (반응형 - main.png 배경)
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 배경 이미지를 QLabel로 설정 (절대 위치)
        main_bg_path = resource_path("assets/image/common/main.png").replace(chr(92), "/")
        self.content_bg_label = QLabel(self.content_widget)
        self.content_bg_label.setPixmap(QPixmap(main_bg_path))
        self.content_bg_label.setScaledContents(True)
        self.content_bg_label.lower()  # 맨 뒤로 보내기

        # ✅ 2컬럼 레이아웃 적용
        self.bg_root = QWidget(self.content_widget)
        self.bg_root.setObjectName("bg_root")
        self.bg_root.setFixedSize(1584, 898)  # left_col(472) + right_col(1112) = 1584
        self.bg_root.setAttribute(Qt.WA_StyledBackground, True)
        self.bg_root.setStyleSheet("QWidget#bg_root { background: transparent; }")

        # ✅ 반응형: 원본 크기 저장
        self.original_window_size = (1680, 1006)
        self.original_bg_root_size = (1584, 898)

        bg_root_layout = QVBoxLayout()
        bg_root_layout.setContentsMargins(0, 0, 0, 0)
        bg_root_layout.setSpacing(0)

        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(0)

        # ✅ 왼쪽 컬럼 (시험 분야 선택) - 472*898, padding: 좌우 24px, 상 36px, 하 80px
        self.left_col = QWidget()
        self.left_col.setFixedSize(472, 898)
        self.left_col.setStyleSheet("background: transparent;")
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(24, 36, 24, 80)
        self.left_layout.setSpacing(0)

        # ✅ 반응형: 왼쪽 패널 원본 크기 저장
        self.original_left_col_size = (472, 898)

        self.create_spec_selection_panel(self.left_layout)
        self.left_col.setLayout(self.left_layout)

        # ✅ 오른쪽 컬럼 (나머지 UI)
        self.right_col = QWidget()
        self.right_col.setFixedSize(1112, 898)
        self.right_col.setStyleSheet("background: transparent;")
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(24, 30, 24, 0)
        self.right_layout.setSpacing(0)
        self.right_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 왼쪽 상단 정렬

        # ✅ 반응형: 오른쪽 패널 원본 크기 저장
        self.original_right_col_size = (1112, 898)

        # ✅ 시험 URL 라벨 + 텍스트 박스 (가로 배치)
        self.url_row = QWidget()
        self.url_row.setFixedSize(1064, 36)
        self.url_row.setStyleSheet("background: transparent;")
        self.original_url_row_size = (1064, 36)
        url_row_layout = QHBoxLayout()
        url_row_layout.setContentsMargins(0, 0, 0, 0)
        url_row_layout.setSpacing(8)  # 라벨과 텍스트 박스 사이 8px gap
        url_row_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 왼쪽 정렬

        # 시험 URL 라벨 (96 × 24, 20px Medium)
        result_label = QLabel('시험 URL')
        result_label.setFixedSize(96, 24)
        result_label.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """)
        result_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        url_row_layout.addWidget(result_label)

        # ✅ URL 텍스트 박스 (960 × 36, 내부 좌우 24px padding, 18px Medium)
        self.url_text_box = QLineEdit()
        self.url_text_box.setFixedSize(960, 36)
        self.original_url_text_box_size = (960, 36)
        self.url_text_box.setReadOnly(False)
        self.url_text_box.setPlaceholderText("접속 주소를 입력하세요.")

        # URL 생성 (초기에는 spec_id 사용, get_setting() 후 test_name으로 업데이트됨)
        self.pathUrl = self.url + "/" + self.current_spec_id
        self.url_text_box.setText(self.pathUrl)

        self.url_text_box.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #868686;
                border-radius: 4px;
                padding: 0 24px;
                font-family: "Noto Sans KR";
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                selection-background-color: #4A90E2;
                selection-color: white;
            }
            QLineEdit::placeholder {
                color: #6B6B6B;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background-color: #FFFFFF;
            }
        """)
        url_row_layout.addWidget(self.url_text_box)

        self.url_row.setLayout(url_row_layout)
        self.right_layout.addWidget(self.url_row)

        # 20px gap
        self.right_layout.addSpacing(20)

        # ========== 시험 API 영역 (1064 × 251) ==========
        self.api_section = QWidget()
        self.api_section.setFixedSize(1064, 251)
        self.api_section.setStyleSheet("background: transparent;")
        self.original_api_section_size = (1064, 251)

        api_section_layout = QVBoxLayout(self.api_section)
        api_section_layout.setContentsMargins(0, 0, 0, 0)
        api_section_layout.setSpacing(8)

        # 시험 API 라벨 (1064 × 24, 20px Medium)
        self.api_label = QLabel('시험 API')
        self.api_label.setFixedSize(1064, 24)
        self.original_api_label_size = (1064, 24)
        self.api_label.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """)
        api_section_layout.addWidget(self.api_label)

        # 시험 API 테이블 (1064 × 219)
        self.init_centerLayout()
        self.api_content_widget = QWidget()
        self.api_content_widget.setFixedSize(1064, 219)
        self.original_api_content_widget_size = (1064, 219)
        self.api_content_widget.setStyleSheet("background: transparent;")
        self.api_content_widget.setLayout(self.centerLayout)
        api_section_layout.addWidget(self.api_content_widget)

        self.right_layout.addWidget(self.api_section)

        # 20px gap
        self.right_layout.addSpacing(20)

        # ========== 수신 메시지 실시간 모니터링 영역 (1064 × 157) ==========
        self.monitor_section = QWidget()
        self.monitor_section.setFixedSize(1064, 157)
        self.monitor_section.setStyleSheet("background: transparent;")
        self.original_monitor_section_size = (1064, 157)

        monitor_section_layout = QVBoxLayout(self.monitor_section)
        monitor_section_layout.setContentsMargins(0, 0, 0, 0)
        monitor_section_layout.setSpacing(0)

        # 수신 메시지 실시간 모니터링 라벨 (1064 × 24, 20px Medium)
        self.monitor_label = QLabel("수신 메시지 실시간 모니터링")
        self.monitor_label.setFixedSize(1064, 24)
        self.original_monitor_label_size = (1064, 24)
        self.monitor_label.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """)
        monitor_section_layout.addWidget(self.monitor_label)

        # 8px gap
        monitor_section_layout.addSpacing(8)

        # ✅ QTextBrowser를 담을 컨테이너 생성 (1064 × 125)
        self.text_browser_container = QWidget()
        self.text_browser_container.setFixedSize(1064, 125)
        self.original_text_browser_container_size = (1064, 125)

        self.valResult = QTextBrowser(self.text_browser_container)
        self.valResult.setFixedSize(1064, 125)
        self.original_valResult_size = (1064, 125)
        self.valResult.setStyleSheet("""
            QTextBrowser {
                background: #FFF;
                border-radius: 4px;
                border: 1px solid #CECECE;
                font-family: "Noto Sans KR";
                font-size: 32px;
                font-weight: 400;
                color: #1B1B1C;
            }
            QScrollBar:vertical {
                border: none;
                background: #DFDFDF;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #A3A9AD;
                min-height: 20px;
                border-radius: 4px;
                margin: 0px 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8A9094;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        # 텍스트 영역 여백 설정 (좌24, 우12) - 스크롤바는 맨 끝에 위치
        self.valResult.setViewportMargins(24, 0, 12, 0)

        # ✅ 커스텀 placeholder 라벨
        self.placeholder_label = QLabel("모니터링 내용이 표출됩니다", self.text_browser_container)
        self.placeholder_label.setGeometry(24, 16, 1000, 30)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #CECECE;
                font-family: "Noto Sans KR";
                font-size: 20px;
                font-weight: 400;
                background: transparent;
            }
        """)
        self.placeholder_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # ✅ 텍스트 변경 시 placeholder 숨기기
        self.valResult.textChanged.connect(self._toggle_placeholder)

        monitor_section_layout.addWidget(self.text_browser_container)
        self.right_layout.addWidget(self.monitor_section)

        # 초기 상태 설정
        self._toggle_placeholder()

        # 20px gap
        self.right_layout.addSpacing(20)

        self.valmsg = QLabel('시험 점수 요약', self)
        self.valmsg.setFixedSize(1064, 24)
        self.original_valmsg_size = (1064, 24)
        self.valmsg.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """)
        self.right_layout.addWidget(self.valmsg)

        # 6px gap
        self.right_layout.addSpacing(6)

        # 평가 점수 표시
        self.spec_score_group = self.create_spec_score_display_widget()
        self.right_layout.addWidget(self.spec_score_group)

        self.total_score_group = self.create_total_score_display_widget()
        self.right_layout.addWidget(self.total_score_group)

        # 30px gap
        self.right_layout.addSpacing(30)

        # ✅ 버튼 그룹 (레이아웃 없이 직접 위치 설정)
        self.buttonGroup = QWidget()
        self.buttonGroup.setFixedSize(1064, 48)
        self.original_buttonGroup_size = (1064, 48)
        self.button_spacing = 16  # 버튼 간격 고정

        # 평가 시작 버튼
        self.sbtn = QPushButton("시험 시작", self.buttonGroup)  # 텍스트 추가
        self.original_button_size = (254, 48)  # 버튼 원본 크기 저장
        start_enabled = resource_path("assets/image/test_runner/btn_평가시작_enabled.png").replace("\\", "/")
        start_hover = resource_path("assets/image/test_runner/btn_평가시작_hover.png").replace("\\", "/")
        start_disabled = resource_path("assets/image/test_runner/btn_평가시작_disabled.png").replace("\\", "/")
        self.sbtn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{start_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                border-image: url('{start_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:pressed {{
                border-image: url('{start_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:disabled {{
                border-image: url('{start_disabled}') 0 0 0 0 stretch stretch;
                color: #CECECE;
            }}
        """)
        self.sbtn.clicked.connect(self.start_btn_clicked)

        # 정지 버튼
        self.stop_btn = QPushButton("일시 정지", self.buttonGroup)  # 텍스트 추가
        stop_enabled = resource_path("assets/image/test_runner/btn_일시정지_enabled.png").replace("\\", "/")
        stop_hover = resource_path("assets/image/test_runner/btn_일시정지_hover.png").replace("\\", "/")
        stop_disabled = resource_path("assets/image/test_runner/btn_일시정지_disabled.png").replace("\\", "/")
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{stop_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }}
            QPushButton:hover {{
                border-image: url('{stop_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:pressed {{
                border-image: url('{stop_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:disabled {{
                border-image: url('{stop_disabled}') 0 0 0 0 stretch stretch;
                color: #CECECE;
            }}
        """)
        self.stop_btn.clicked.connect(self.stop_btn_clicked)
        self.stop_btn.setDisabled(True)

        # 종료 버튼
        self.rbtn = QPushButton("종료", self.buttonGroup)  # 텍스트 추가
        exit_enabled = resource_path("assets/image/test_runner/btn_종료_enabled.png").replace("\\", "/")
        exit_hover = resource_path("assets/image/test_runner/btn_종료_hover.png").replace("\\", "/")
        exit_disabled = resource_path("assets/image/test_runner/btn_종료_disabled.png").replace("\\", "/")
        self.rbtn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{exit_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }}
            QPushButton:hover {{
                border-image: url('{exit_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:pressed {{
                border-image: url('{exit_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:disabled {{
                border-image: url('{exit_disabled}') 0 0 0 0 stretch stretch;
                color: #CECECE;
            }}
        """)
        self.rbtn.clicked.connect(self.exit_btn_clicked)

        # 시험 결과 버튼
        self.result_btn = QPushButton("시험 결과", self.buttonGroup)  # 텍스트 추가
        result_enabled = resource_path("assets/image/test_runner/btn_시험결과_enabled.png").replace("\\", "/")
        result_hover = resource_path("assets/image/test_runner/btn_시험결과_hover.png").replace("\\", "/")
        result_disabled = resource_path("assets/image/test_runner/btn_시험결과_disabled.png").replace("\\", "/")
        self.result_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{result_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }}
            QPushButton:hover {{
                border-image: url('{result_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:pressed {{
                border-image: url('{result_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:disabled {{
                border-image: url('{result_disabled}') 0 0 0 0 stretch stretch;
                color: #CECECE;
            }}
        """)
        self.result_btn.clicked.connect(self.show_result_page)

        # 초기 버튼 위치 설정 (레이아웃 없이 직접 배치)
        self._update_button_positions()
        self.right_layout.addWidget(self.buttonGroup)
        self.right_layout.addStretch()
        self.right_col.setLayout(self.right_layout)

        columns_layout.addWidget(self.left_col)
        columns_layout.addWidget(self.right_col)

        bg_root_layout.addLayout(columns_layout)
        self.bg_root.setLayout(bg_root_layout)

        # content_widget 레이아웃 설정 (좌우 48px, 하단 44px padding, 가운데 정렬)
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(48, 0, 48, 44)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.bg_root, 0, Qt.AlignHCenter | Qt.AlignVCenter)

        mainLayout.addWidget(self.content_widget, 1)  # 반응형: stretch=1로 남은 공간 채움

        self.setLayout(mainLayout)

        if not self.embedded:
            self.setWindowTitle('물리보안 시스템 연동 검증 소프트웨어')

        QTimer.singleShot(100, self.select_first_scenario)

        if not self.embedded:
            self.show()

    def _update_button_positions(self, group_width=None, group_height=None):
        """버튼 위치 직접 설정 (간격 16px 고정)"""
        if not hasattr(self, 'buttonGroup'):
            return

        # 크기가 전달되지 않으면 현재 크기 사용
        if group_width is None:
            group_width = self.buttonGroup.width()
        if group_height is None:
            group_height = self.buttonGroup.height()

        spacing = self.button_spacing  # 16px

        # 버튼 너비 = (전체 너비 - 간격 3개) / 4
        btn_width = (group_width - spacing * 3) // 4
        btn_height = group_height

        # 각 버튼 크기 및 위치 설정
        x = 0
        self.sbtn.setFixedSize(btn_width, btn_height)
        self.sbtn.move(x, 0)
        x += btn_width + spacing
        self.stop_btn.setFixedSize(btn_width, btn_height)
        self.stop_btn.move(x, 0)
        x += btn_width + spacing
        self.result_btn.setFixedSize(btn_width, btn_height)
        self.result_btn.move(x, 0)
        x += btn_width + spacing
        self.rbtn.setFixedSize(btn_width, btn_height)
        self.rbtn.move(x, 0)

    def resizeEvent(self, event):
        """창 크기 변경 시 배경 이미지 및 왼쪽 패널 크기 재조정"""
        super().resizeEvent(event)

        # 파일 로그로 resizeEvent 호출 확인 (PyInstaller 호환)
        try:
            import os
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(base_dir, "resize_debug.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[SYSTEM] width={self.width()}, height={self.height()}\n")
        except:
            pass

        # content_widget의 배경 이미지 크기 조정
        if hasattr(self, 'content_widget') and self.content_widget:
            if hasattr(self, 'content_bg_label'):
                content_width = self.content_widget.width()
                content_height = self.content_widget.height()
                self.content_bg_label.setGeometry(0, 0, content_width, content_height)

        # ✅ 반응형: 왼쪽 패널 크기 조정
        if hasattr(self, 'original_window_size') and hasattr(self, 'left_col'):
            current_width = self.width()
            current_height = self.height()

            # 비율 계산 (최소 1.0 - 원본 크기 이하로 줄어들지 않음)
            width_ratio = max(1.0, current_width / self.original_window_size[0])
            height_ratio = max(1.0, current_height / self.original_window_size[1])

            # ✅ 왼쪽/오른쪽 패널 정렬을 위한 확장량 계산
            # 컬럼의 추가 높이를 계산하고, 그 추가분만 확장 요소들에 분배
            original_column_height = 898  # 원본 컬럼 높이
            extra_column_height = original_column_height * (height_ratio - 1)

            # 왼쪽 패널 확장 요소: group_table(204) + field_group(526) = 730px
            left_expandable_total = 204 + 526  # 730

            # 오른쪽 패널 확장 요소: api_section(251) + monitor_section(157) = 408px
            right_expandable_total = 251 + 157  # 408

            # bg_root 크기 조정
            if hasattr(self, 'bg_root') and hasattr(self, 'original_bg_root_size'):
                new_bg_width = int(self.original_bg_root_size[0] * width_ratio)
                new_bg_height = int(self.original_bg_root_size[1] * height_ratio)
                self.bg_root.setFixedSize(new_bg_width, new_bg_height)

            # 왼쪽 컬럼 크기 조정
            if hasattr(self, 'original_left_col_size'):
                new_left_width = int(self.original_left_col_size[0] * width_ratio)
                new_left_height = int(self.original_left_col_size[1] * height_ratio)
                self.left_col.setFixedSize(new_left_width, new_left_height)

            # 시험 선택 타이틀 크기 조정
            if hasattr(self, 'spec_panel_title') and hasattr(self, 'original_spec_panel_title_size'):
                new_title_width = int(self.original_spec_panel_title_size[0] * width_ratio)
                self.spec_panel_title.setFixedSize(new_title_width, self.original_spec_panel_title_size[1])

            # 그룹 테이블 위젯 크기 조정 (extra_column_height 비례 분배)
            if hasattr(self, 'group_table_widget') and hasattr(self, 'original_group_table_widget_size'):
                new_group_width = int(self.original_group_table_widget_size[0] * width_ratio)
                group_extra = extra_column_height * (204 / left_expandable_total)
                new_group_height = int(204 + group_extra)
                self.group_table_widget.setFixedSize(new_group_width, new_group_height)
                # 내부 테이블 크기도 조정
                if hasattr(self, 'group_table'):
                    self.group_table.setFixedHeight(new_group_height)

            # 시험 시나리오 테이블 크기 조정 (extra_column_height 비례 분배)
            if hasattr(self, 'field_group') and hasattr(self, 'original_field_group_size'):
                new_field_width = int(self.original_field_group_size[0] * width_ratio)
                field_extra = extra_column_height * (526 / left_expandable_total)
                new_field_height = int(526 + field_extra)
                self.field_group.setFixedSize(new_field_width, new_field_height)
                # 내부 테이블 크기도 조정
                if hasattr(self, 'test_field_table'):
                    self.test_field_table.setFixedHeight(new_field_height)

            # ✅ 오른쪽 컬럼 크기 조정
            if hasattr(self, 'right_col') and hasattr(self, 'original_right_col_size'):
                new_right_width = int(self.original_right_col_size[0] * width_ratio)
                new_right_height = int(self.original_right_col_size[1] * height_ratio)
                self.right_col.setFixedSize(new_right_width, new_right_height)

            # URL 행 크기 조정
            if hasattr(self, 'url_row') and hasattr(self, 'original_url_row_size'):
                new_url_width = int(self.original_url_row_size[0] * width_ratio)
                self.url_row.setFixedSize(new_url_width, self.original_url_row_size[1])

            # API 섹션 크기 조정 (extra_column_height 비례 분배)
            if hasattr(self, 'api_section') and hasattr(self, 'original_api_section_size'):
                new_api_width = int(self.original_api_section_size[0] * width_ratio)
                api_extra = extra_column_height * (251 / right_expandable_total)
                new_api_height = int(251 + api_extra)
                self.api_section.setFixedSize(new_api_width, new_api_height)

            # 모니터링 섹션 크기 조정 (extra_column_height 비례 분배)
            if hasattr(self, 'monitor_section') and hasattr(self, 'original_monitor_section_size'):
                new_monitor_width = int(self.original_monitor_section_size[0] * width_ratio)
                monitor_extra = extra_column_height * (157 / right_expandable_total)
                new_monitor_height = int(157 + monitor_extra)
                self.monitor_section.setFixedSize(new_monitor_width, new_monitor_height)

            # ✅ 버튼 그룹 및 버튼 크기 조정 (간격 16px 고정, 세로 크기 고정)
            if hasattr(self, 'original_buttonGroup_size'):
                new_group_width = int(self.original_buttonGroup_size[0] * width_ratio)
                btn_height = self.original_buttonGroup_size[1]  # 세로 크기 고정
                self.buttonGroup.setFixedSize(new_group_width, btn_height)
                self._update_button_positions(new_group_width, btn_height)

            # ✅ 내부 위젯 크기 조정
            # URL 텍스트 박스
            if hasattr(self, 'url_text_box') and hasattr(self, 'original_url_text_box_size'):
                new_url_tb_width = int(self.original_url_text_box_size[0] * width_ratio)
                self.url_text_box.setFixedSize(new_url_tb_width, self.original_url_text_box_size[1])

            # API 라벨
            if hasattr(self, 'api_label') and hasattr(self, 'original_api_label_size'):
                new_api_label_width = int(self.original_api_label_size[0] * width_ratio)
                self.api_label.setFixedSize(new_api_label_width, self.original_api_label_size[1])

            # API 콘텐츠 위젯 (api_section 내부 - 라벨 24px 제외)
            if hasattr(self, 'api_content_widget') and hasattr(self, 'original_api_content_widget_size'):
                new_api_cw_width = int(self.original_api_content_widget_size[0] * width_ratio)
                new_api_cw_height = int(219 + api_extra)  # api_section에서 라벨 제외한 부분
                self.api_content_widget.setFixedSize(new_api_cw_width, new_api_cw_height)

            # 모니터링 라벨
            if hasattr(self, 'monitor_label') and hasattr(self, 'original_monitor_label_size'):
                new_mon_label_width = int(self.original_monitor_label_size[0] * width_ratio)
                self.monitor_label.setFixedSize(new_mon_label_width, self.original_monitor_label_size[1])

            # 텍스트 브라우저 컨테이너 (monitor_section 내부 - 라벨 24px 제외)
            if hasattr(self, 'text_browser_container') and hasattr(self, 'original_text_browser_container_size'):
                new_tbc_width = int(self.original_text_browser_container_size[0] * width_ratio)
                new_tbc_height = int(125 + monitor_extra)  # monitor_section에서 라벨 제외한 부분
                self.text_browser_container.setFixedSize(new_tbc_width, new_tbc_height)

            # valResult (QTextBrowser) (monitor_section 내부)
            if hasattr(self, 'valResult') and hasattr(self, 'original_valResult_size'):
                new_vr_width = int(self.original_valResult_size[0] * width_ratio)
                new_vr_height = int(125 + monitor_extra)
                self.valResult.setFixedSize(new_vr_width, new_vr_height)

            # ✅ 시험 점수 요약 섹션
            if hasattr(self, 'valmsg') and hasattr(self, 'original_valmsg_size'):
                new_valmsg_width = int(self.original_valmsg_size[0] * width_ratio)
                self.valmsg.setFixedSize(new_valmsg_width, self.original_valmsg_size[1])

            if hasattr(self, 'spec_score_group') and hasattr(self, 'original_spec_group_size'):
                new_spec_width = int(self.original_spec_group_size[0] * width_ratio)
                self.spec_score_group.setFixedSize(new_spec_width, self.original_spec_group_size[1])

            if hasattr(self, 'total_score_group') and hasattr(self, 'original_total_group_size'):
                new_total_width = int(self.original_total_group_size[0] * width_ratio)
                self.total_score_group.setFixedSize(new_total_width, self.original_total_group_size[1])

            # ✅ 시험 점수 요약 내부 데이터 영역 비례 조정
            if hasattr(self, 'spec_data_widget') and hasattr(self, 'original_spec_data_widget_size'):
                new_spec_data_width = int(self.original_spec_data_widget_size[0] * width_ratio)
                self.spec_data_widget.setFixedSize(new_spec_data_width, self.original_spec_data_widget_size[1])

            if hasattr(self, 'total_data_widget') and hasattr(self, 'original_total_data_widget_size'):
                new_total_data_width = int(self.original_total_data_widget_size[0] * width_ratio)
                self.total_data_widget.setFixedSize(new_total_data_width, self.original_total_data_widget_size[1])

            # ✅ 시험 점수 요약 내부 라벨 너비 비례 조정
            if hasattr(self, 'original_score_label_width'):
                new_label_width = int(self.original_score_label_width * width_ratio)
                # 분야별 점수 라벨
                if hasattr(self, 'spec_pass_label'):
                    self.spec_pass_label.setFixedSize(new_label_width, 60)
                if hasattr(self, 'spec_total_label'):
                    self.spec_total_label.setFixedSize(new_label_width, 60)
                if hasattr(self, 'spec_score_label'):
                    self.spec_score_label.setFixedSize(new_label_width, 60)
                # 전체 점수 라벨
                if hasattr(self, 'total_pass_label'):
                    self.total_pass_label.setFixedSize(new_label_width, 60)
                if hasattr(self, 'total_total_label'):
                    self.total_total_label.setFixedSize(new_label_width, 60)
                if hasattr(self, 'total_score_label'):
                    self.total_score_label.setFixedSize(new_label_width, 60)

            # ✅ 시험 API 테이블 헤더
            if hasattr(self, 'api_header_widget') and hasattr(self, 'original_api_header_widget_size'):
                new_header_width = int(self.original_api_header_widget_size[0] * width_ratio)
                self.api_header_widget.setFixedSize(new_header_width, self.original_api_header_widget_size[1])

            # ✅ 시험 API 테이블 본문 (scroll_area) - 세로도 확장 (api_extra 사용)
            if hasattr(self, 'api_scroll_area') and hasattr(self, 'original_api_scroll_area_size'):
                new_scroll_width = int(self.original_api_scroll_area_size[0] * width_ratio)
                new_scroll_height = int(189 + api_extra)  # api_content_widget 내부 (헤더 30px 제외)
                self.api_scroll_area.setFixedSize(new_scroll_width, new_scroll_height)

            # ✅ 시험 API 테이블 컬럼 너비 비례 조정 (마지막 컬럼이 남은 공간 채움)
            if hasattr(self, 'tableWidget') and hasattr(self, 'original_column_widths'):
                # 스크롤바 표시 여부 확인 (테이블 전체 높이 > 스크롤 영역 높이)
                row_count = self.tableWidget.rowCount()
                total_row_height = row_count * 40  # 각 행 40px
                scrollbar_visible = total_row_height > new_scroll_height
                scrollbar_width = 16 if scrollbar_visible else 2  # 여유분 2px

                available_width = new_scroll_width - scrollbar_width

                # 마지막 컬럼을 제외한 나머지 컬럼 너비 설정
                used_width = 0
                for i, orig_width in enumerate(self.original_column_widths[:-1]):
                    new_col_width = int(orig_width * width_ratio)
                    self.tableWidget.setColumnWidth(i, new_col_width)
                    used_width += new_col_width

                # 마지막 컬럼은 남은 공간을 채움
                last_col_width = available_width - used_width
                self.tableWidget.setColumnWidth(len(self.original_column_widths) - 1, last_col_width)

            # ✅ 시험 API 테이블 헤더 라벨 너비 비례 조정
            if hasattr(self, 'header_labels') and hasattr(self, 'original_header_widths'):
                for i, label in enumerate(self.header_labels):
                    new_label_width = int(self.original_header_widths[i] * width_ratio)
                    label.setFixedSize(new_label_width, 30)

    def select_first_scenario(self):
        """프로그램 시작 시 첫 번째 그룹의 첫 번째 시나리오 자동 선택"""
        try:
            print(f"[DEBUG] 초기 시나리오 자동 선택 시작")

            # 1. 첫 번째 그룹이 있는지 확인
            if self.group_table.rowCount() > 0:
                self.group_table.selectRow(0)
                print(f"[DEBUG] 첫 번째 그룹 선택: {self.index_to_group_name.get(0)}")
                self.on_group_selected(0, 0)

            # 2. 시나리오 테이블에 첫 번째 항목이 있는지 확인
            if self.test_field_table.rowCount() > 0:
                self.test_field_table.selectRow(0)
                first_spec_id = self.index_to_spec_id.get(0)
                print(f"[DEBUG] 첫 번째 시나리오 선택: spec_id={first_spec_id}")
                self.on_test_field_selected(0, 0)
                # URL 생성 (test_name 사용)
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', self.current_spec_id)
                    self.pathUrl = self.url + "/" + test_name
                else:
                    self.pathUrl = self.url + "/" + self.current_spec_id
                self.url_text_box.setText(self.pathUrl)  # 안내 문구 변경
            print(f"[DEBUG] 초기 시나리오 자동 선택 완료: {self.spec_description}")
            QApplication.processEvents()

        except Exception as e:
            print(f"[ERROR] 초기 시나리오 선택 실패: {e}")
            import traceback
            traceback.print_exc()
    def init_centerLayout(self):
        # 표 형태로 변경 - 동적 API 개수
        api_count = len(self.videoMessages)

        # 별도 헤더 위젯 (1064px 전체 너비)
        self.api_header_widget = QWidget()
        self.api_header_widget.setFixedSize(1064, 30)
        self.original_api_header_widget_size = (1064, 30)
        self.api_header_widget.setStyleSheet("""
            QWidget {
                background-color: #EDF0F3;
                border: 1px solid #CECECE;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        """)
        header_layout = QHBoxLayout(self.api_header_widget)
        header_layout.setContentsMargins(0, 0, 14, 0)  # 오른쪽 14px (스크롤바 영역)
        header_layout.setSpacing(0)

        # 헤더 컬럼 정의 (너비, 텍스트) - 9컬럼 구조
        header_columns = [
            (40, ""),            # No.
            (261, "API 명"),
            (100, "결과"),
            (94, "검증 횟수"),
            (116, "통과 필드 수"),
            (116, "전체 필드 수"),
            (94, "실패 횟수"),
            (94, "평가 점수"),
            (133, "상세 내용")
        ]

        # 헤더 라벨 저장 (반응형 조정용)
        self.header_labels = []
        self.original_header_widths = [col[0] for col in header_columns]

        for i, (width, text) in enumerate(header_columns):
            label = QLabel(text)
            label.setFixedSize(width, 30)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                    color: #1B1B1C;
                    font-family: 'Noto Sans KR';
                    font-size: 18px;
                    font-weight: 600;
                }
            """)
            self.header_labels.append(label)
            header_layout.addWidget(label)

        # 테이블 본문 (헤더 숨김)
        self.tableWidget = QTableWidget(api_count, 9)  # 9개 컬럼
        # self.tableWidget.setFixedWidth(1050)  # setWidgetResizable(True) 사용으로 주석 처리
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.tableWidget.setStyleSheet("""
            QTableWidget {
                background: #FFF;
                border: none;
                font-size: 18px;
                color: #222;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                border-right: 0px solid transparent;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-style: normal;
                font-weight: 400;
                text-align: center;
            }
        """)

        self.tableWidget.setShowGrid(False)

        # 컬럼 너비 설정 - 9컬럼 구조 (원본 너비 저장)
        self.original_column_widths = [40, 261, 100, 94, 116, 116, 94, 94, 133]
        for i, width in enumerate(self.original_column_widths):
            self.tableWidget.setColumnWidth(i, width)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)  # 비례 조정을 위해 비활성화

        # 행 높이 설정 (40px)
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 40)

        # 단계명 리스트 (동적으로 로드된 API 이름 사용)
        self.step_names = self.videoMessages
        for i, name in enumerate(self.step_names):
            # No. (숫자)
            no_item = QTableWidgetItem(f"{i + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(i, 0, no_item)

            # API 명
            api_item = QTableWidgetItem(name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(i, 1, api_item)

            # 결과 아이콘
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)

            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)

            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)

            self.tableWidget.setCellWidget(i, 2, icon_widget)

            # 검증 횟수
            self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
            self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
            # 통과 필드 수
            self.tableWidget.setItem(i, 4, QTableWidgetItem("0"))
            self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)
            # 전체 필드 수
            self.tableWidget.setItem(i, 5, QTableWidgetItem("0"))
            self.tableWidget.item(i, 5).setTextAlignment(Qt.AlignCenter)
            # 실패 횟수
            self.tableWidget.setItem(i, 6, QTableWidgetItem("0"))
            self.tableWidget.item(i, 6).setTextAlignment(Qt.AlignCenter)
            # 평가 점수
            self.tableWidget.setItem(i, 7, QTableWidgetItem("0%"))
            self.tableWidget.item(i, 7).setTextAlignment(Qt.AlignCenter)

            # 상세 내용 버튼
            detail_label = QLabel()
            img_path = resource_path("assets/image/test_runner/btn_상세내용확인.png").replace("\\", "/")
            pixmap = QPixmap(img_path)
            detail_label.setPixmap(pixmap)
            detail_label.setScaledContents(False)
            detail_label.setFixedSize(pixmap.size())
            detail_label.setCursor(Qt.PointingHandCursor)
            detail_label.setAlignment(Qt.AlignCenter)

            detail_label.mousePressEvent = lambda event, row=i: self.show_combined_result(row)

            # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(i, 8, container)

        # 결과 컬럼만 클릭 가능하도록 설정 (기존 기능 유지)
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)

        # ✅ QScrollArea로 본문만 감싸기 (헤더 아래부터 스크롤)
        self.api_scroll_area = QScrollArea()
        self.api_scroll_area.setWidget(self.tableWidget)
        self.api_scroll_area.setWidgetResizable(True)
        self.api_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.api_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 필요할 때만 스크롤바 표시
        self.api_scroll_area.setFixedSize(1064, 189)  # 헤더 제외 (219 - 30)
        self.original_api_scroll_area_size = (1064, 189)
        self.api_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #CECECE;
                border-top: none;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #FFFFFF;
            }
            QScrollBar:vertical {
                border: none;
                background: #DFDFDF;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #A3A9AD;
                min-height: 20px;
                border-radius: 4px;
                margin: 0px 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8A9094;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

        # centerLayout을 초기화하고 헤더 + 스크롤 영역 추가
        self.centerLayout = QVBoxLayout()
        self.centerLayout.setContentsMargins(0, 0, 0, 0)
        self.centerLayout.setSpacing(0)
        self.centerLayout.addWidget(self.api_header_widget)
        self.centerLayout.addWidget(self.api_scroll_area)
        self.centerLayout.addStretch()  # 세로 확장 시 여분 공간을 하단으로

    def show_combined_result(self, row):
        """통합 상세 내용 확인 - 데이터, 규격, 오류를 모두 보여주는 3열 팝업"""
        try:
            buf = self.step_buffers[row]
            api_name = self.tableWidget.item(row, 1).text()  # API 명은 컬럼 1

            # 스키마 데이터 가져오기 -> 09/24 시스템쪽은 OutSchema
            try:
                schema_data = self.videoOutSchema[row] if row < len(self.videoOutSchema) else None
            except:
                schema_data = None

            # ✅ 웹훅 스키마 데이터 가져오기 (수정됨)
            webhook_schema = None
            if row < len(self.trans_protocols):
                current_protocol = self.trans_protocols[row]
                if current_protocol == "WebHook":
                    # ✅ row를 직접 사용 (webhookInSchema는 전체 API 리스트와 1:1 매칭)
                    if row < len(self.webhookInSchema):
                        webhook_schema = self.webhookInSchema[row]
                        print(f"[DEBUG] 웹훅 스키마 로드: row={row}, schema={'있음' if webhook_schema else '없음'}")
                    else:
                        print(f"[WARN] 웹훅 스키마 인덱스 초과: row={row}, 전체={len(self.webhookInSchema)}")

            # 통합 팝업창 띄우기
            dialog = CombinedDetailDialog(api_name, buf, schema_data, webhook_schema)
            dialog.exec_()

        except Exception as e:
            CustomDialog(f"오류:\n{str(e)}", "상세 내용 확인 오류")

    def group_score(self):
        """평가 점수 박스"""
        sgroup = QGroupBox('평가 점수')
        sgroup.setMaximumWidth(1050)
        sgroup.setMinimumWidth(950)

        # 점수 표시용 레이블들
        self.pass_count_label = QLabel("통과 필드 수: 0")
        self.total_count_label = QLabel("전체 필드 수: 0")
        self.score_label = QLabel("종합 평가 점수: 0%")

        # 폰트 크기 조정
        font = self.pass_count_label.font()
        font.setPointSize(20)
        self.pass_count_label.setFont(font)
        self.total_count_label.setFont(font)
        self.score_label.setFont(font)

        # 가로 배치
        layout = QHBoxLayout()
        layout.setSpacing(90)
        layout.addWidget(self.pass_count_label)
        layout.addWidget(self.total_count_label)
        layout.addWidget(self.score_label)
        layout.addStretch()

        sgroup.setLayout(layout)
        return sgroup

    def update_score_display(self):
        """평가 점수 디스플레이를 업데이트"""
        if not (hasattr(self, "spec_pass_label") and hasattr(self, "spec_total_label") and hasattr(self,
                                                                                                   "spec_score_label")):
            return

        # ✅ 분야별 점수 제목 업데이트 (시나리오 명 변경 반영)
        if hasattr(self, "spec_name_label"):
            self.spec_name_label.setText(f"{self.spec_description} ({len(self.videoMessages)}개 API)")

        # ✅ 1️⃣ 분야별 점수 (현재 spec만) - step_pass_counts 배열의 합으로 계산
        if hasattr(self, 'step_pass_counts') and hasattr(self, 'step_error_counts'):
            self.total_pass_cnt = sum(self.step_pass_counts)
            self.total_error_cnt = sum(self.step_error_counts)
            print(f"[SCORE UPDATE] step_pass_counts: {self.step_pass_counts}, sum: {self.total_pass_cnt}")
            print(f"[SCORE UPDATE] step_error_counts: {self.step_error_counts}, sum: {self.total_error_cnt}")

        # ✅ 선택 필드 통과 수 계산
        if hasattr(self, 'step_opt_pass_counts'):
            self.total_opt_pass_cnt = sum(self.step_opt_pass_counts)
            print(f"[SCORE UPDATE] step_opt_pass_counts: {self.step_opt_pass_counts}, sum: {self.total_opt_pass_cnt}")
        else:
            self.total_opt_pass_cnt = 0

        # ✅ 선택 필드 에러 수 계산
        if hasattr(self, 'step_opt_error_counts'):
            self.total_opt_error_cnt = sum(self.step_opt_error_counts)
            print(f"[SCORE UPDATE] step_opt_error_counts: {self.step_opt_error_counts}, sum: {self.total_opt_error_cnt}")
        else:
            self.total_opt_error_cnt = 0

        # 필수 필드 통과 수 = 전체 통과 - 선택 통과
        spec_required_pass = self.total_pass_cnt - self.total_opt_pass_cnt

        spec_total_fields = self.total_pass_cnt + self.total_error_cnt
        # 선택 필드 전체 수 = 선택 통과 + 선택 에러
        spec_opt_total = self.total_opt_pass_cnt + self.total_opt_error_cnt
        # 필수 필드 전체 수 = 전체 필드 - 선택 필드
        spec_required_total = spec_total_fields - spec_opt_total

        if spec_total_fields > 0:
            spec_score = (self.total_pass_cnt / spec_total_fields) * 100
        else:
            spec_score = 0

        # 필수 통과율 계산
        if spec_required_total > 0:
            spec_required_score = (spec_required_pass / spec_required_total) * 100
        else:
            spec_required_score = 0

        # 선택 통과율 계산
        if spec_opt_total > 0:
            spec_opt_score = (self.total_opt_pass_cnt / spec_opt_total) * 100
        else:
            spec_opt_score = 0

        # 필수/선택/종합 점수 표시 (% (통과/전체) 형식)
        self.spec_pass_label.setText(
            f"통과 필수 필드 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{spec_required_score:.1f}% ({spec_required_pass}/{spec_required_total})</span>"
        )
        self.spec_total_label.setText(
            f"통과 선택 필드 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{spec_opt_score:.1f}% ({self.total_opt_pass_cnt}/{spec_opt_total})</span>"
        )
        self.spec_score_label.setText(
            f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{spec_score:.1f}% ({self.total_pass_cnt}/{spec_total_fields})</span>"
        )

        # ✅ 2️⃣ 전체 점수 (모든 spec 합산)
        if hasattr(self, "total_pass_label") and hasattr(self, "total_total_label") and hasattr(self,
                                                                                                "total_score_label"):
            # ✅ 전체 점수는 별도로 누적됨 (여러 spec을 실행할 경우 합산)
            # 현재는 spec이 1개뿐이므로 분야별 점수와 동일하지만,
            # 나중에 여러 spec을 실행하면 달라짐

            global_total_fields = self.global_pass_cnt + self.global_error_cnt
            if global_total_fields > 0:
                global_score = (self.global_pass_cnt / global_total_fields) * 100
            else:
                global_score = 0

            # 전체 필수 필드 통과 수 = 전체 통과 - 전체 선택 통과
            global_required_pass = self.global_pass_cnt - self.global_opt_pass_cnt
            # 전체 선택 필드 수 = 전체 선택 통과 + 전체 선택 에러
            global_opt_total = self.global_opt_pass_cnt + self.global_opt_error_cnt
            # 전체 필수 필드 수 = 전체 필드 - 전체 선택 필드
            global_required_total = global_total_fields - global_opt_total

            # 필수 통과율 계산
            if global_required_total > 0:
                global_required_score = (global_required_pass / global_required_total) * 100
            else:
                global_required_score = 0

            # 선택 통과율 계산
            if global_opt_total > 0:
                global_opt_score = (self.global_opt_pass_cnt / global_opt_total) * 100
            else:
                global_opt_score = 0

            # 필수/선택/종합 점수 표시 (% (통과/전체) 형식)
            self.total_pass_label.setText(
                f"통과 필수 필드 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
                f"{global_required_score:.1f}% ({global_required_pass}/{global_required_total})</span>"
            )
            self.total_total_label.setText(
                f"통과 선택 필드 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
                f"{global_opt_score:.1f}% ({self.global_opt_pass_cnt}/{global_opt_total})</span>"
            )
            self.total_score_label.setText(
                f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
                f"{global_score:.1f}% ({self.global_pass_cnt}/{global_total_fields})</span>"
            )

            # ✅ 디버그 로그 추가
            print(
                f"[SCORE UPDATE] 분야별 - pass: {self.total_pass_cnt}, error: {self.total_error_cnt}, score: {spec_score:.1f}%")
            print(
                f"[SCORE UPDATE] 전체 - pass: {self.global_pass_cnt}, error: {self.global_error_cnt}, score: {global_score:.1f}%")

    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭 시 호출되는 함수"""
        if col == 2:  # 결과 컬럼 클릭 시에만 동작 (컬럼 2)
            msg = getattr(self, f"step{row + 1}_msg", "")
            if msg:
                api_name = self.step_names[row] if row < len(self.step_names) else f"Step {row + 1}"
                CustomDialog(msg, api_name)
    
    def _toggle_placeholder(self):
        """QTextBrowser에 텍스트가 있으면 placeholder 숨기기, 없으면 표시"""
        if self.valResult.toPlainText().strip():
            self.placeholder_label.hide()
        else:
            self.placeholder_label.show()

    def _remove_api_number_suffix(self, api_name):
        """API 이름 뒤의 숫자 제거 (화면 표시용)
        예: Authentication2 -> Authentication, RealTimeDoorStatus3 -> RealTimeDoorStatus
        """
        import re
        # 마지막에 숫자만 있으면 제거
        return re.sub(r'\d+$', '', api_name)

    def append_monitor_log(self, step_name, request_json="", result_status="진행중", score=None, details=""):
        """
        Qt 호환성이 보장된 HTML 테이블 구조 로그 출력 함수
        """
        from datetime import datetime
        import html

        # 타임스탬프
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 점수에 따른 색상 결정
        if score is not None:
            if score >= 100:
                node_color = "#10b981"  # 녹색
                text_color = "#10b981"  # 녹색 텍스트
            else:
                node_color = "#ef4444"  # 빨강
                text_color = "#ef4444"  # 빨강 텍스트
        else:
            node_color = "#6b7280"  # 회색
            text_color = "#333"  # 기본 검정

        # 1. 헤더 (Step 이름 + 시간) - Table로 블록 분리
        html_content = f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 15px;">
            <tr>
                <td valign="middle">
                    <span style="font-size: 20px; font-weight: bold; color: {text_color}; font-family: 'Noto Sans KR';">{step_name}</span>
                    <span style="font-size: 16px; color: #9ca3af; font-family: 'Consolas', monospace; margin-left: 8px;">{timestamp}</span>
                </td>
            </tr>
        </table>
        """

        # 2. 내용 영역
        html_content += f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td>
        """

        # 2-1. 상세 내용 (Details)
        if details:
            html_content += f"""
                <div style="margin-bottom: 8px; font-size: 18px; color: #6b7280; font-family: 'Noto Sans KR';">
                    {details}
                </div>
            """

        # 2-2. JSON 데이터 (회색 박스)
        if request_json and request_json.strip():
            escaped_json = html.escape(request_json)
            is_json_structure = request_json.strip().startswith('{') or request_json.strip().startswith('[')

            if is_json_structure:
                html_content += f"""
                <div style="margin-top: 5px; margin-bottom: 10px;">
                    <div style="font-size: 15px; color: #9ca3af; font-weight: bold; margin-bottom: 4px;">📦 데이터</div>
                    <div style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; padding: 10px;">
                        <pre style="margin: 0; font-family: 'Consolas', monospace; font-size: 18px; color: #1f2937;">{escaped_json}</pre>
                    </div>
                </div>
                """
            else:
                # JSON이 아닌 일반 텍스트일 경우
                html_content += f"""
                <div style="margin-top: 5px; margin-bottom: 10px;">
                    <pre style="font-size: 18px; color: #6b7280; font-family: 'Consolas', monospace;">{escaped_json}</pre>
                </div>
                """

        # 2-3. 점수 (Score)
        if score is not None:
            html_content += f"""
                <div style="margin-top: 5px; font-size: 18px; color: #6b7280; font-weight: bold; font-family: 'Consolas', monospace;">
                    점수: {score:.1f}%
                </div>
            """

        # Table 닫기
        html_content += """
                </td>
            </tr>
        </table>
        <div style="margin-bottom: 10px;"></div>
        """

        self.valResult.append(html_content)

        # 자동 스크롤
        self.valResult.verticalScrollBar().setValue(
            self.valResult.verticalScrollBar().maximum()
        )

    def create_spec_score_display_widget(self):
        """메인 화면에 표시할 시험 분야별 평가 점수 위젯"""

        spec_group = QGroupBox()
        spec_group.setFixedSize(1064, 128)
        self.original_spec_group_size = (1064, 128)
        spec_group.setStyleSheet("""
            QGroupBox {
                background-color: #FFF;
                border: 1px solid #CECECE;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                padding: 0px;
                margin: 0px;
            }
        """)

        # 분야별 점수 아이콘 (52 × 42)
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_분야별점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(52, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(52, 42)
        icon_label.setAlignment(Qt.AlignCenter)

        # 분야별 점수 레이블 (500 Medium 20px)
        score_type_label = QLabel("분야별 점수")
        score_type_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
        """)

        # 세로선 (27px)
        header_vline = QFrame()
        header_vline.setFrameShape(QFrame.VLine)
        header_vline.setFixedSize(1, 27)
        header_vline.setStyleSheet("background-color: #000000;")

        # spec 정보 레이블 (500 Medium 20px)
        self.spec_name_label = QLabel(f"{self.spec_description} ({len(self.videoMessages)}개 API)")
        self.spec_name_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
        """)

        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet("""
            QFrame {
                color: #CECECE;
                background-color: #CECECE;
            }
        """)
        separator.setFixedHeight(1)

        # 점수 레이블들 (500 Medium 20px #000000, 325 × 60)
        # 원본 크기 저장 (반응형 조정용)
        self.original_score_label_width = 325

        self.spec_pass_label = QLabel("통과 필드 수")
        self.spec_pass_label.setFixedHeight(60)
        self.spec_pass_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.spec_pass_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;

        """)
        self.spec_total_label = QLabel("전체 필드 수")
        self.spec_total_label.setFixedHeight(60)
        self.spec_total_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.spec_total_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
            
        """)
        self.spec_score_label = QLabel("종합 평가 점수")
        self.spec_score_label.setFixedHeight(60)
        self.spec_score_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.spec_score_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
            
        """)

        spec_layout = QVBoxLayout()
        spec_layout.setContentsMargins(0, 0, 0, 0)
        spec_layout.setSpacing(0)

        # 아이콘 + 분야명 (헤더 영역 1064 × 52)
        header_widget = QWidget()
        header_widget.setFixedSize(1064, 52)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 5, 0, 5)
        header_layout.setSpacing(12)
        header_layout.addWidget(icon_label, alignment=Qt.AlignVCenter)
        header_layout.addWidget(score_type_label, alignment=Qt.AlignVCenter)
        header_layout.addWidget(header_vline, alignment=Qt.AlignVCenter)
        header_layout.addWidget(self.spec_name_label, alignment=Qt.AlignVCenter)
        header_layout.addStretch()
        spec_layout.addWidget(header_widget)
        spec_layout.addWidget(separator)

        # 데이터 영역 (1064 × 76)
        self.spec_data_widget = QWidget()
        self.spec_data_widget.setFixedSize(1064, 76)
        self.original_spec_data_widget_size = (1064, 76)
        spec_score_layout = QHBoxLayout(self.spec_data_widget)
        spec_score_layout.setContentsMargins(56, 8, 32, 8)
        spec_score_layout.setSpacing(0)

        # 통과 필드 수 + 구분선 + spacer
        spec_score_layout.addWidget(self.spec_pass_label)
        spec_vline1 = QFrame()
        spec_vline1.setFixedSize(2, 60)
        spec_vline1.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline1)
        spec_spacer1 = QWidget()
        spec_spacer1.setFixedSize(24, 60)
        spec_score_layout.addWidget(spec_spacer1)

        # 전체 필드 수 + 구분선 + spacer
        spec_score_layout.addWidget(self.spec_total_label)
        spec_vline2 = QFrame()
        spec_vline2.setFixedSize(2, 60)
        spec_vline2.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline2)
        spec_spacer2 = QWidget()
        spec_spacer2.setFixedSize(24, 60)
        spec_score_layout.addWidget(spec_spacer2)

        # 종합 평가 점수
        spec_score_layout.addWidget(self.spec_score_label)
        spec_score_layout.addStretch()

        spec_layout.addWidget(self.spec_data_widget)
        spec_group.setLayout(spec_layout)

        return spec_group

    def create_total_score_display_widget(self):
        """메인 화면에 표시할 전체 평가 점수 위젯"""
        total_group = QGroupBox()
        total_group.setFixedSize(1064, 128)
        self.original_total_group_size = (1064, 128)
        total_group.setStyleSheet("""
            QGroupBox {
                background-color: #F0F6FB;
                border: 1px solid #CECECE;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
                padding: 0px;
                margin: 0px;
            }
        """)

        # 전체 점수 아이콘 (52 × 42)
        icon_label = QLabel()
        icon_label.setFixedSize(52, 42)
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_전체점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(52, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 전체 점수 레이블 (500 Medium 20px)
        total_name_label = QLabel("전체 점수")
        total_name_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """)

        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet("""
            QFrame {
                color: #CECECE;
                background-color: #CECECE;
            }
        """)
        separator.setFixedHeight(1)

        # 점수 레이블들 (500 Medium 20px #000000, 325 × 60)
        self.total_pass_label = QLabel("통과 필드 수")
        self.total_pass_label.setFixedHeight(60)
        self.total_pass_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.total_pass_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
            
        """)
        self.total_total_label = QLabel("전체 필드 수")
        self.total_total_label.setFixedHeight(60)
        self.total_total_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.total_total_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
            
        """)
        self.total_score_label = QLabel("종합 평가 점수")
        self.total_score_label.setFixedHeight(60)
        self.total_score_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.total_score_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
            
        """)

        total_layout = QVBoxLayout()
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.setSpacing(0)

        # 아이콘 + 전체 점수 텍스트 (헤더 영역 1064 × 52)
        header_widget = QWidget()
        header_widget.setFixedSize(1064, 52)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 5, 0, 5)
        header_layout.setSpacing(6)
        header_layout.addWidget(icon_label, alignment=Qt.AlignVCenter)
        header_layout.addWidget(total_name_label, alignment=Qt.AlignVCenter)
        header_layout.addStretch()
        total_layout.addWidget(header_widget)
        total_layout.addWidget(separator)

        # 데이터 영역 (1064 × 76)
        self.total_data_widget = QWidget()
        self.total_data_widget.setFixedSize(1064, 76)
        self.original_total_data_widget_size = (1064, 76)
        score_layout = QHBoxLayout(self.total_data_widget)
        score_layout.setContentsMargins(56, 8, 32, 8)
        score_layout.setSpacing(0)

        # 통과 필드 수 + 구분선 + spacer
        score_layout.addWidget(self.total_pass_label)
        total_vline1 = QFrame()
        total_vline1.setFixedSize(2, 60)
        total_vline1.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline1)
        total_spacer1 = QWidget()
        total_spacer1.setFixedSize(24, 60)
        score_layout.addWidget(total_spacer1)

        # 전체 필드 수 + 구분선 + spacer
        score_layout.addWidget(self.total_total_label)
        total_vline2 = QFrame()
        total_vline2.setFixedSize(2, 60)
        total_vline2.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline2)
        total_spacer2 = QWidget()
        total_spacer2.setFixedSize(24, 60)
        score_layout.addWidget(total_spacer2)

        # 종합 평가 점수
        score_layout.addWidget(self.total_score_label)
        score_layout.addStretch()

        total_layout.addWidget(self.total_data_widget)
        total_group.setLayout(total_layout)

        return total_group

    def _clean_trace_dir_once(self):
        """results/trace 폴더 안의 파일들을 삭제"""
        print(f"[TRACE_CLEAN] ⚠️  _clean_trace_dir_once() 호출됨!")
        import traceback
        print(f"[TRACE_CLEAN] 호출 스택:\n{''.join(traceback.format_stack()[-3:-1])}")
        os.makedirs(CONSTANTS.trace_path, exist_ok=True)
        for name in os.listdir(CONSTANTS.trace_path):
            path = os.path.join(CONSTANTS.trace_path, name)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    print(f"[TRACE_CLEAN] 삭제: {name}")
                except OSError:
                    pass

    def start_btn_clicked(self):
        """평가 시작 버튼 클릭"""
        # ✅ 1. 시나리오 선택 확인
        if not hasattr(self, 'current_spec_id') or not self.current_spec_id:
            QMessageBox.warning(self, "알림", "시험 시나리오를 먼저 선택하세요.")
            return

        # ✅ 일시정지 파일 존재 여부 확인
        paused_file_path = os.path.join(result_dir, "response_results_paused.json")
        resume_mode = os.path.exists(paused_file_path)

        if resume_mode:
            print(f"[DEBUG] ========== 재개 모드: 일시정지 상태 복원 ==========")
            # 재개 모드: 저장된 상태 복원
            if self.load_paused_state():
                self.is_paused = False  # 재개 시작이므로 paused 플래그 해제
                print(f"[DEBUG] 재개 모드: {self.last_completed_api_index + 2}번째 API부터 시작")
            else:
                # 복원 실패 시 신규 시작으로 전환
                print(f"[WARN] 상태 복원 실패, 신규 시작으로 전환")
                resume_mode = False
        self.webhook_schema_idx = 0

        # ✅ 로딩 팝업 표시
        self.loading_popup = LoadingPopup()
        self.loading_popup.show()
        self.loading_popup.raise_()  # 최상위로 올리기
        self.loading_popup.activateWindow()  # 활성화
        self.loading_popup.repaint()  # 강제 다시 그리기
        # UI가 확실히 렌더링되도록 여러 번 processEvents 호출
        for _ in range(10):
            QApplication.processEvents()

        self.pathUrl = self.url_text_box.text()
        if not resume_mode:
            print(f"[START] ========== 검증 시작: 완전 초기화 ==========")
        print(f"[START] 시험 URL : ", self.pathUrl)
        print(f"[START] 시험: {self.current_spec_id} - {self.spec_description}")
        print(f"[START] 사용자 인증 방식 : ", self.CONSTANTS.auth_type)

        QApplication.processEvents()  # 스피너 애니메이션 유지
        self.update_result_table_structure(self.videoMessages)
        QApplication.processEvents()  # 스피너 애니메이션 유지

        # ✅ 2. 기존 타이머 정지 (중복 실행 방지)
        if self.tick_timer.isActive():
            print(f"[START] 기존 타이머 중지")
            self.tick_timer.stop()

        if not resume_mode:
            # ========== 신규 시작 모드: 완전 초기화 ==========
            print(f"[START] ========== 신규 시작: 완전 초기화 ==========")

            # ✅ 3. trace 디렉토리 초기화 (그룹이 변경될 때만)
            # 같은 그룹 내 spec 전환 시에는 trace 유지 (맥락 검증용)
            if not hasattr(self, '_last_cleaned_group') or self._last_cleaned_group != self.current_group_id:
                print(f"[TRACE_CLEAN] 그룹 변경 감지: {getattr(self, '_last_cleaned_group', None)} → {self.current_group_id}")
                print(f"[TRACE_CLEAN] trace 디렉토리 초기화 실행")
                self._clean_trace_dir_once()
                self._last_cleaned_group = self.current_group_id
            else:
                print(f"[TRACE_KEEP] 같은 그룹 내 spec 전환: trace 디렉토리 유지 (맥락 검증용)")

            # ✅ 4. JSON 데이터 준비
            json_to_data("video")

            # ✅ 6. 이전 시험 결과가 global 점수에 포함되어 있으면 제거 (복합키 사용)
            composite_key = f"{self.current_group_id}_{self.current_spec_id}"
            if composite_key in self.spec_table_data:
                prev_data = self.spec_table_data[composite_key]
                prev_pass = prev_data.get('total_pass_cnt', 0)
                prev_error = prev_data.get('total_error_cnt', 0)
                # ✅ 선택 필드 통과/에러 수 계산
                prev_opt_pass = sum(prev_data.get('step_opt_pass_counts', []))
                prev_opt_error = sum(prev_data.get('step_opt_error_counts', []))
                print(f"[SCORE RESET] 기존 {composite_key} 점수 제거: pass={prev_pass}, error={prev_error}")
                print(f"[SCORE RESET] 기존 {composite_key} 선택 점수 제거: opt_pass={prev_opt_pass}, opt_error={prev_opt_error}")

                # ✅ global 점수에서 해당 spec 점수 제거
                self.global_pass_cnt = max(0, self.global_pass_cnt - prev_pass)
                self.global_error_cnt = max(0, self.global_error_cnt - prev_error)
                # ✅ global 선택 점수에서 해당 spec 점수 제거
                self.global_opt_pass_cnt = max(0, self.global_opt_pass_cnt - prev_opt_pass)
                self.global_opt_error_cnt = max(0, self.global_opt_error_cnt - prev_opt_error)

                print(f"[SCORE RESET] 조정 후 global 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}")
                print(f"[SCORE RESET] 조정 후 global 선택 점수: opt_pass={self.global_opt_pass_cnt}, opt_error={self.global_opt_error_cnt}")

            # ✅ 7. 모든 카운터 및 플래그 초기화 (첫 실행처럼)
            self.cnt = 0
            self.cnt_pre = 0
            self.time_pre = 0
            self.current_retry = 0
            self.post_flag = False
            self.processing_response = False
            self.message_in_cnt = 0
            self.realtime_flag = False
            self.tmp_msg_append_flag = False

            # ✅ 8. 현재 spec의 점수만 초기화 (global은 유지)
            self.total_error_cnt = 0
            self.total_pass_cnt = 0

            # ✅ 9. 메시지 및 에러 관련 변수 초기화
            self.message_error = []
            self.res = None
            self.webhook_res = None

            # ✅ 10. 현재 spec에 맞게 누적 카운트 초기화
            api_count = len(self.videoMessages)
            self.step_pass_counts = [0] * api_count
            self.step_error_counts = [0] * api_count
            self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
            self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수
            self.step_pass_flags = [0] * api_count

            # ✅ 11. step_buffers 완전 재생성
            self.step_buffers = [
                {"data": "", "error": "", "result": "PASS", "raw_data_list": []} for _ in range(api_count)
            ]
            print(f"[START] step_buffers 재생성 완료: {len(self.step_buffers)}개")

            # ✅ 12. trace 초기화
            if hasattr(self, 'trace'):
                self.trace.clear()
            else:
                self.trace = {}

            if hasattr(self, 'latest_events'):
                self.latest_events.clear()
            else:
                self.latest_events = {}

            # ✅ 13. 테이블 완전 초기화
            print(f"[START] 테이블 초기화: {api_count}개 API")
            for i in range(self.tableWidget.rowCount()):
                QApplication.processEvents()  # 스피너 애니메이션 유지
                # 아이콘 초기화
                icon_widget = QWidget()
                icon_layout = QHBoxLayout()
                icon_layout.setContentsMargins(0, 0, 0, 0)
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
                icon_label.setAlignment(Qt.AlignCenter)
                icon_layout.addWidget(icon_label)
                icon_layout.setAlignment(Qt.AlignCenter)
                icon_widget.setLayout(icon_layout)
                self.tableWidget.setCellWidget(i, 2, icon_widget)

                # 카운트 초기화 (9컬럼 구조)
                for col, value in [(3, "0"), (4, "0"), (5, "0"), (6, "0"), (7, "0%")]:
                    item = QTableWidgetItem(value) if not self.tableWidget.item(i, col) else self.tableWidget.item(i, col)
                    item.setText(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(i, col, item)
            print(f"[START] 테이블 초기화 완료")

            # ✅ 14. 인증 정보 설정
            parts = self.auth_info.split(",")
            auth = [parts[0], parts[1] if len(parts) > 1 else ""]
            self.accessInfo = [auth[0], auth[1]]
            self.token = None

            # ✅ 15. 평가 점수 디스플레이 초기화 (전체 점수 포함)
            self.update_score_display()
            QApplication.processEvents()  # 스피너 애니메이션 유지

            # ✅ 16. 결과 텍스트 초기화
            self.valResult.clear()

            # ✅ 17. URL 설정
            #self.pathUrl = self.url + "/" + self.current_spec_id
            self.pathUrl = self.url_text_box.text()
            self.url_text_box.setText(self.pathUrl)  # 안내 문구 변경

            # ✅ 18. 시작 메시지
            self.append_monitor_log(
                step_name=f"시스템 검증 시작: {self.spec_description}",
                details=f"API 개수: {len(self.videoMessages)}개"
            )
        else:
            # ========== 재개 모드: 저장된 상태 사용, 초기화 건너뛰기 ==========
            print(f"[DEBUG] 재개 모드: 초기화 건너뛰기, 저장된 상태 사용")
            # cnt는 last_completed_api_index + 1로 설정
            self.cnt = self.last_completed_api_index + 1
            print(f"[DEBUG] 재개 모드: cnt = {self.cnt}")

            # ✅ 재개 모드에서도 실행 상태 변수는 초기화 필요
            self.current_retry = 0  # 재시도 카운터 초기화 (중요!)
            self.post_flag = False
            self.processing_response = False
            self.message_in_cnt = 0
            self.realtime_flag = False
            self.tmp_msg_append_flag = False
            self.cnt_pre = 0
            self.time_pre = 0
            self.res = None
            self.webhook_res = None
            self.message_error = []
            print(f"[DEBUG] 재개 모드: 실행 상태 변수 초기화 완료")

            # ✅ 미완료 API의 trace 파일 삭제 (완료된 API는 유지)
            trace_dir = os.path.join(result_dir, "trace")
            if os.path.exists(trace_dir):
                print(f"[DEBUG] 미완료 API trace 파일 삭제 시작 (완료: 0~{self.last_completed_api_index})")
                for i in range(self.last_completed_api_index + 1, len(self.videoMessages)):
                    api_name = self.videoMessages[i]
                    # ✅ 두 가지 형식 모두 삭제 (trace_API.ndjson, trace_NN_API.ndjson)
                    trace_patterns = [
                        f"trace_{api_name}.ndjson",
                        f"trace_{i:02d}_{api_name}.ndjson"
                    ]
                    for pattern in trace_patterns:
                        trace_file = os.path.join(trace_dir, pattern)
                        if os.path.exists(trace_file):
                            try:
                                os.remove(trace_file)
                                print(f"[DEBUG] 삭제: {pattern}")
                            except Exception as e:
                                print(f"[WARN] trace 파일 삭제 실패: {e}")
                print(f"[DEBUG] 미완료 API trace 파일 정리 완료")

            # 점수 디스플레이 업데이트 (복원된 점수로)
            self.update_score_display()
            QApplication.processEvents()  # 스피너 애니메이션 유지

            # 모니터링 메시지 복원
            self.valResult.clear()
            if self.paused_valResult_text:
                self.valResult.setHtml(self.paused_valResult_text)
                self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 10px;">========== 재개 ==========</div>')
                self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">마지막 완료 API: {self.last_completed_api_index + 1}번째</div>')
                self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-bottom: 10px;">{self.last_completed_api_index + 2}번째 API부터 재개합니다.</div>')
                print(f"[DEBUG] 모니터링 메시지 복원 완료: {len(self.paused_valResult_text)} 문자")

            # ✅ 테이블 데이터 복원 (완료된 API들만)
            print(f"[DEBUG] 테이블 데이터 복원 시작: 0 ~ {self.last_completed_api_index}번째 API")
            for i in range(self.last_completed_api_index + 1):
                if i < len(self.step_buffers):
                    buffer = self.step_buffers[i]
                    # 실제 데이터가 있는 경우만 테이블 업데이트
                    has_data = (
                        buffer.get('raw_data_list') or
                        buffer.get('data') or
                        buffer.get('error')
                    )
                    if has_data:
                        result = buffer.get('result', 'PASS')
                        data = buffer.get('data', '')
                        error = buffer.get('error', '')
                        pass_count = self.step_pass_counts[i] if i < len(self.step_pass_counts) else 0
                        error_count = self.step_error_counts[i] if i < len(self.step_error_counts) else 0

                        # 부하테스트의 경우 검증 횟수는 raw_data_list 길이
                        retries = len(buffer.get('raw_data_list', [])) if buffer.get('raw_data_list') else 1

                        # 테이블 행 업데이트
                        self.update_table_row_with_retries(
                            i, result, pass_count, error_count, data, error, retries
                        )
                        print(f"[DEBUG] 테이블 복원: API {i+1} - result={result}, pass={pass_count}, error={error_count}, retries={retries}")
            print(f"[DEBUG] 테이블 데이터 복원 완료")

        QApplication.processEvents()  # 스피너 애니메이션 유지

        # ✅ 5. 버튼 상태 변경 (신규/재개 공통)
        self.sbtn.setDisabled(True)
        self.stop_btn.setEnabled(True)

        QApplication.processEvents()  # 스피너 애니메이션 유지

        # ✅ 19. 타이머 시작 (모든 초기화 완료 후)
        print(f"[START] 타이머 시작")
        self.tick_timer.start(1000)
        print(f"[START] ========== 검증 시작 준비 완료 ==========")

        # ✅ 로딩 팝업 닫기 (최소 표시 시간 확보)
        if self.loading_popup:
            # 팝업이 최소한 보이도록 잠시 대기 (스피너 유지)
            for _ in range(3):  # 3 * 100ms = 300ms
                time.sleep(0.1)
                QApplication.processEvents()
            self.loading_popup.close()
            self.loading_popup = None

        print(f"[START] 현재 global 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}")

    def save_paused_state(self):
        """일시정지 시 현재 상태를 JSON 파일로 저장"""
        try:
            from datetime import datetime

            # 마지막 완료된 API 인덱스 계산
            # 모든 retry가 완료된 API만 완료로 간주
            last_completed = -1
            for i, buffer in enumerate(self.step_buffers):
                # ✅ 부하테스트의 경우 모든 retry가 완료되어야 "완료"로 판단
                raw_data_list = buffer.get('raw_data_list', [])
                expected_retries = self.num_retries_list[i] if i < len(self.num_retries_list) else 1

                # 실제 완료된 retry 수가 예상 retry 수와 같거나 크면 완료
                if len(raw_data_list) >= expected_retries:
                    last_completed = i
                # timeout 등으로 데이터 없이 FAIL 처리된 경우도 완료로 간주
                elif buffer.get('result') == 'FAIL' and (buffer.get('data') or buffer.get('error')):
                    has_timeout_error = 'Message Missing' in str(buffer.get('error', ''))
                    if has_timeout_error:
                        last_completed = i

            self.last_completed_api_index = last_completed

            # 저장할 상태 데이터 구성
            paused_state = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_completed_api_index": self.last_completed_api_index,
                "step_buffers": self.step_buffers,
                "step_pass_counts": getattr(self, 'step_pass_counts', [0] * len(self.videoMessages)),
                "step_error_counts": getattr(self, 'step_error_counts', [0] * len(self.videoMessages)),
                "step_opt_pass_counts": getattr(self, 'step_opt_pass_counts', [0] * len(self.videoMessages)),
                "step_opt_error_counts": getattr(self, 'step_opt_error_counts', [0] * len(self.videoMessages)),
                "total_pass_cnt": self.total_pass_cnt,
                "total_error_cnt": self.total_error_cnt,
                "valResult_text": self.valResult.toHtml(),
                "current_spec_id": self.current_spec_id,
                "global_pass_cnt": self.global_pass_cnt,
                "global_error_cnt": self.global_error_cnt
            }

            # JSON 파일로 저장
            paused_file_path = os.path.join(result_dir, "response_results_paused.json")
            with open(paused_file_path, "w", encoding="utf-8") as f:
                json.dump(paused_state, f, ensure_ascii=False, indent=2)

            print(f"✅ 일시정지 상태 저장 완료: {paused_file_path}")
            print(f"   마지막 완료 API 인덱스: {last_completed}")

            # 모니터링 창에 로그 추가
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 10px;">💾 재개 정보 저장 완료: {paused_file_path}</div>')
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">   (마지막 완료 API: {last_completed + 1}번째, 다음 재시작 시 {last_completed + 2}번째 API부터 이어서 실행)</div>')

        except Exception as e:
            print(f"❌ 일시정지 상태 저장 실패: {e}")
            import traceback
            traceback.print_exc()

    def load_paused_state(self):
        """일시정지된 상태를 JSON 파일에서 복원"""
        try:
            paused_file_path = os.path.join(result_dir, "response_results_paused.json")

            if not os.path.exists(paused_file_path):
                print("[INFO] 일시정지 파일이 존재하지 않습니다.")
                return False

            with open(paused_file_path, "r", encoding="utf-8") as f:
                paused_state = json.load(f)

            # 상태 복원
            self.last_completed_api_index = paused_state.get("last_completed_api_index", -1)
            self.step_buffers = paused_state.get("step_buffers", [])
            self.step_pass_counts = paused_state.get("step_pass_counts", [0] * len(self.videoMessages))
            self.step_error_counts = paused_state.get("step_error_counts", [0] * len(self.videoMessages))
            self.step_opt_pass_counts = paused_state.get("step_opt_pass_counts", [0] * len(self.videoMessages))
            self.step_opt_error_counts = paused_state.get("step_opt_error_counts", [0] * len(self.videoMessages))
            self.total_pass_cnt = paused_state.get("total_pass_cnt", 0)
            self.total_error_cnt = paused_state.get("total_error_cnt", 0)
            self.paused_valResult_text = paused_state.get("valResult_text", "")
            self.global_pass_cnt = paused_state.get("global_pass_cnt", 0)
            self.global_error_cnt = paused_state.get("global_error_cnt", 0)

            print(f"✅ 일시정지 상태 복원 완료")
            print(f"   타임스탬프: {paused_state.get('timestamp')}")
            print(f"   마지막 완료 API 인덱스: {self.last_completed_api_index}")
            print(f"   복원된 점수: PASS={self.total_pass_cnt}, FAIL={self.total_error_cnt}")

            return True

        except Exception as e:
            print(f"❌ 일시정지 상태 복원 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup_paused_file(self):
        """평가 완료 후 일시정지 파일 삭제 및 상태 초기화"""
        try:
            paused_file_path = os.path.join(result_dir, "response_results_paused.json")
            print(f"[CLEANUP] cleanup_paused_file() 호출됨")
            print(f"[CLEANUP] 파일 경로: {paused_file_path}")
            print(f"[CLEANUP] 파일 존재 여부: {os.path.exists(paused_file_path)}")

            if os.path.exists(paused_file_path):
                os.remove(paused_file_path)
                print("✅ 일시정지 중간 파일 삭제 완료")
            else:
                print("[CLEANUP] 일시정지 파일이 존재하지 않음 (일시정지하지 않았거나 이미 삭제됨)")

            # 일시정지 상태 초기화
            self.is_paused = False
            self.last_completed_api_index = -1
            self.paused_valResult_text = ""

        except Exception as e:
            print(f"❌ 일시정지 파일 정리 실패: {e}")

    def stop_btn_clicked(self):
        """평가 중지 버튼 클릭"""
        # ✅ 타이머 중지
        if self.tick_timer.isActive():
            self.tick_timer.stop()
            print(f"[STOP] 타이머 중지됨")

        self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">검증 절차가 중지되었습니다.</div>')
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)

        self.save_current_spec_data()

        # ✅ 일시정지 상태 저장
        self.is_paused = True
        self.save_paused_state()

        # ✅ JSON 결과 저장 추가
        try:
            self.run_status = "진행중"
            result_json = build_result_json(self)
            url = f"{CONSTANTS.management_url}/api/integration/test-results"
            response = requests.post(url, json=result_json)
            print("✅ 시험 결과 전송 상태 코드:", response.status_code)
            print("📥  시험 결과 전송 응답:", response.text)
            json_path = os.path.join(result_dir, "response_results.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)
            print(f"✅ 진행 중 결과가 '{json_path}'에 저장되었습니다.")
            self.append_monitor_log(
                step_name="진행 상황 저장 완료",
                details=f"{json_path} (일시정지 시점까지의 결과가 저장되었습니다)"
            )
        except Exception as e:
            print(f"❌ JSON 저장 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            self.valResult.append(f"\n결과 저장 실패: {str(e)}")

    def init_win(self):
        def init_win(self):
            """검증 시작 전 초기화"""
            self.cnt = 0
            self.current_retry = 0
            # 현재 spec의 API 개수에 맞게 버퍼 생성
            api_count = len(self.videoMessages) if self.videoMessages else 0
            print(f"[INIT] 초기화: {api_count}개 API")

            # 버퍼 초기화
            self.step_buffers = [
                {"data": "", "result": "", "error": "", "raw_data_list": []} for _ in range(api_count)
            ]

            # 누적 카운트 초기화
            self.step_pass_counts = [0] * api_count
            self.step_error_counts = [0] * api_count
            self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
            self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수
            self.step_pass_flags = [0] * api_count
            self.webhook_schema_idx = 0

            self.valResult.clear()

            # 메시지 초기화
            for i in range(1, 10):
                setattr(self, f"step{i}_msg", "")

            # 테이블 아이콘 및 카운트 초기화
            for i in range(self.tableWidget.rowCount()):
                icon_widget = QWidget()
                icon_layout = QHBoxLayout()
                icon_layout.setContentsMargins(0, 0, 0, 0)
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
                icon_label.setAlignment(Qt.AlignCenter)
                icon_layout.addWidget(icon_label)
                icon_layout.setAlignment(Qt.AlignCenter)
                icon_widget.setLayout(icon_layout)
                self.tableWidget.setCellWidget(i, 2, icon_widget)

                # 카운트 초기화 (9컬럼 구조)
                for col, value in ((3, "0"), (4, "0"), (5, "0"), (6, "0"), (7, "0%")):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(i, col, item)

    def show_result_page(self):
        """시험 결과 페이지 표시"""
        if self.embedded:
            # Embedded 모드: 시그널을 emit하여 main.py에서 스택 전환 처리
            self.showResultRequested.emit(self)
        else:
            # Standalone 모드: 새 창으로 위젯 표시
            if hasattr(self, 'result_window') and self.result_window is not None:
                self.result_window.close()
            self.result_window = ResultPageWidget(self)
            self.result_window.show()

    def toggle_fullscreen(self):
        """전체화면 전환 (main.py 스타일)"""
        try:
            if not self._is_fullscreen:
                # 전체화면으로 전환
                self._saved_geom = self.saveGeometry()
                self._saved_state = self.windowState()

                flags = (Qt.Window | Qt.WindowTitleHint |
                         Qt.WindowMinimizeButtonHint |
                         Qt.WindowMaximizeButtonHint |
                         Qt.WindowCloseButtonHint)
                self.setWindowFlags(flags)
                self.show()
                self.showMaximized()
                self._is_fullscreen = True
                if hasattr(self, 'fullscreen_btn'):
                    self.fullscreen_btn.setText("전체화면 해제")
            else:
                # 원래 크기로 복원
                self.setWindowFlags(Qt.Window)
                self.show()
                if self._saved_geom:
                    self.restoreGeometry(self._saved_geom)
                self.showNormal()
                self._is_fullscreen = False
                if hasattr(self, 'fullscreen_btn'):
                    self.fullscreen_btn.setText("전체화면")
        except Exception as e:
            print(f"전체화면 전환 오류: {e}")

    def build_result_payload(self):
        """최종 결과를 dict로 반환"""
        total_fields = self.total_pass_cnt + self.total_error_cnt
        score = (self.total_pass_cnt / total_fields) * 100 if total_fields > 0 else 0
        return {
            "score": score,
            "pass_count": self.total_pass_cnt,
            "error_count": self.total_error_cnt,
            "details": self.final_report if hasattr(self, "final_report") else ""
        }

    def exit_btn_clicked(self):
        reply = QMessageBox.question(self, '프로그램 종료',
                                     '정말로 프로그램을 종료하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            result_payload = self.build_result_payload()

            # ✅ 종료 시 일시정지 파일 삭제
            self.cleanup_paused_file()

            QApplication.quit()

    def get_setting(self):
        self.setting_variables = QSettings('My App', 'Variable')
        self.system = "video"  # 고정

        # 기본 시스템 설정
        self.radio_check_flag = "video"
        self.message = self.videoMessages  # 실제 API 이름 (통신용)
        self.message_display = self.videoMessagesDisplay  # 표시용 이름
        self.inMessage = self.videoInMessage
        self.outSchema = self.videoOutSchema
        self.inCon = self.videoInConstraint
        self.webhookSchema = self.webhookInSchema

        # 기본 인증 설정 (CONSTANTS.py에서 가져옴)
        self.r2 = self.auth_type
        if self.r2 == "Digest Auth":
            self.r2 = "D"
        elif self.r2 == "Bearer Token":
            self.r2 = "B"

        # ✅ URL 업데이트 (test_name 사용) - spec_config가 로드된 후 실행
        if hasattr(self, 'spec_config') and hasattr(self, 'url_text_box'):
            test_name = self.spec_config.get('test_name', self.current_spec_id)
            self.pathUrl = self.url + "/" + test_name
            self.url_text_box.setText(self.pathUrl)

    def closeEvent(self, event):
        """창 닫기 이벤트 - 타이머 정리"""
        # ✅ 타이머 중지
        if hasattr(self, 'tick_timer') and self.tick_timer.isActive():
            self.tick_timer.stop()

        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))
    ex = MyApp(embedded=False)
    sys.exit(app.exec())