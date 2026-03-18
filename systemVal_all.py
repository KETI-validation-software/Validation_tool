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
import math
import re
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor, QPixmap
from PyQt5.QtCore import *
from api.webhook_api import WebhookThread
from api.api_server import Server  # ✅ door_memory 접근을 위한 import 추가
from api.client import APIClient
from core.json_checker_new import timeout_field_finder
from core.functions import (
    json_check_,
    resource_path,
    json_to_data,
    build_result_json,
    update_webhook_step_buffer_fields,
)
from core.data_mapper import ConstraintDataGenerator
from core.logger import Logger
from ui.splash_screen import LoadingPopup
from ui.result_page import ResultPageWidget
from ui.widgets import install_gradient_messagebox
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
from core.utils import to_detail_text, redact, remove_api_number_suffix

class MyApp(SystemMainUI):
    previousPageRequested = pyqtSignal(object)
    # 시험 결과 표시 요청 시그널 (main.py와 연동)
    showResultRequested = pyqtSignal(object)  # parent widget을 인자로 전달

    def _load_from_trace_file(self, api_name, direction="RESPONSE"):
        """Trace 파일에서 최신 이벤트 데이터 로드"""
        try:
            # API 이름에서 슬래시 제거
            api_name_clean = api_name.lstrip("/")
            
            Logger.debug(f"trace 파일 찾기: api_name={api_name}, direction={direction}")
            
            # trace 디렉토리의 모든 파일 검색
            trace_dir = Path(CONSTANTS.trace_path)
            if not trace_dir.exists():
                Logger.debug(f"trace 디렉토리 없음: {trace_dir}")
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
                Logger.debug(f"번호 있는 trace 파일 발견: {trace_file.name}")
            
            # ✅ 우선순위 2: 번호 없는 형식 찾기 (trace_API.ndjson)
            if not trace_file:
                unnumbered_files = list(trace_dir.glob(f"trace_{safe_api}.ndjson"))
                if unnumbered_files:
                    # 번호 없는 파일 중 가장 최근 파일 사용
                    trace_file = max(unnumbered_files, key=lambda f: f.stat().st_mtime)
                    Logger.debug(f"번호 없는 trace 파일 발견: {trace_file.name}")
            
            if not trace_file:
                Logger.debug(f"trace 파일 없음 (패턴: trace_*_{safe_api}.ndjson 또는 trace_{safe_api}.ndjson)")
                return None
            
            Logger.debug(f"사용할 trace 파일: {trace_file.name}")

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
                
                Logger.debug(f"trace 파일에서 {api_name} {direction} 데이터 로드 완료")
                Logger.debug(f"latest_events에 저장된 키들: {api_key}, {api_key_clean}, {api_key_with_slash}")
                return latest_event.get("data")
            else:
                Logger.debug(f"trace 파일에서 {api_name} {direction} 데이터 없음")
                return None

        except Exception as e:
            Logger.error(f"trace 파일 로드 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _apply_request_constraints(self, request_data, cnt):
        """
        이전 응답 데이터를 기반으로 요청 데이터 업데이트
        - inCon (request constraints)을 사용하여 이전 endpoint 응답에서 값 가져오기
        """
        try:
            # constraints 가져오기
            if cnt >= len(self.inCon) or not self.inCon[cnt]:
                # constraints가 없더라도 강제 로드 로직은 타야 하므로 바로 리턴하지 않고 빈 dict 할당
                constraints = {}
            else:
                constraints = self.inCon[cnt]

            if not isinstance(constraints, dict):
                constraints = {}

            required_endpoints = set()

            for field, rule in constraints.items():
                if isinstance(rule, dict):
                    ref_endpoint = rule.get("referenceEndpoint")
                    if ref_endpoint:
                        required_endpoints.add(ref_endpoint.lstrip('/'))

            for endpoint in required_endpoints:
                if endpoint not in self.latest_events or "RESPONSE" not in self.latest_events.get(endpoint, {}):
                    Logger.debug(f"trace 파일에서 {endpoint} RESPONSE 로드 시도")
                    self._load_from_trace_file(endpoint, "RESPONSE")
                else:
                    Logger.debug(f"latest_events에 이미 {endpoint} RESPONSE 존재")
            
            api_name = self.message[cnt] if cnt < len(self.message) else ""

            # 둘 다 무조건 맵핑 되어야 함
            if "RealtimeDoorStatus" in api_name:
                if "DoorProfiles" not in self.latest_events or "RESPONSE" not in self.latest_events.get("DoorProfiles", {}):
                    Logger.debug(f"RealtimeDoorStatus용 DoorProfiles RESPONSE 로드 시도")
                    self._load_from_trace_file("DoorProfiles", "RESPONSE")
            
            self.generator.latest_events = self.latest_events

            updated_request = self.generator._applied_constraints(
                request_data={},  # 이전 요청 데이터는 필요 없음
                template_data=request_data.copy(),  # 현재 요청 데이터를 템플릿으로
                constraints=constraints,
                api_name=api_name,  # ✅ API 이름 전달
                door_memory=Server.door_memory  # ✅ 문 상태 저장소 전달
            )

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
            except Exception as e:
                # Logger.warning(f"constraint 적용 중 일부 실패: {e}")
                return updated_request
        except Exception as e:
            Logger.error(f"_apply_request_constraints 실행 중 오류: {e}")
            import traceback
            
            return request_data

    def _append_text(self, obj):
        import json
        from html import escape
        try:
            if isinstance(obj, (dict, list)):
                json_str = json.dumps(obj, ensure_ascii=False, indent=2)
                # HTML 태그를 escape 처리하여 렌더링 방지
                escaped_json = escape(json_str)
                # 개행을 <br> 태그로 변환하고 공백을 &nbsp;로 변환
                formatted = escaped_json.replace('\n', '<br>').replace(' ', '&nbsp;')
                self.valResult.append(formatted)
            else:
                # 문자열도 HTML escape 처리
                escaped_str = escape(str(obj))
                formatted = escaped_str.replace('\n', '<br>').replace(' ', '&nbsp;')
                self.valResult.append(formatted)
        except Exception as e:
            self.valResult.append(f"[append_error] {escape(str(e))}")

    def handle_authentication_response(self, res_data):
        
        if isinstance(res_data, dict):
            token = res_data.get("accessToken")
            if token:
                self.token = token

    def __init__(self, embedded=False, spec_id=None):
        super().__init__()
        # ✅ 프로그램 시작 시 모든 일시정지 파일 삭제
        self._cleanup_all_paused_files_on_startup()
        
        # ✅ 상태 관리자 초기화
        self.state_manager = SystemStateManager(self)
        
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
        
        # ✅ spec_id 초기화 (info_GUI에서 전달받거나 기본값 사용)
        if spec_id:
            self.current_spec_id = spec_id
            Logger.info(f"전달받은 spec_id 사용: {spec_id}")
        else:
            self.current_spec_id = "cmgatbdp000bqihlexmywusvq"  # 기본값: 보안용센서 시스템 (7개 API) -> 지금은 잠깐 없어짐
            Logger.info(f"기본 spec_id 사용: {self.current_spec_id}")

        self.current_group_id = None  # ✅ 그룹 ID 저장용
        
        self.load_specs_from_constants()
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

        # 아이콘 경로 (메인 페이지용)
        self.img_pass = resource_path("assets/image/icon/icn_success.png")
        self.img_fail = resource_path("assets/image/icon/icn_fail.png")
        self.img_none = resource_path("assets/image/icon/icn_basic.png")

        self.flag_opt = self.CONSTANTS.flag_opt
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_view)
        self.cnt = 0
        self.auth_flag = True

        self.time_pre = 0
        self.post_flag = False
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
        
        # System에서는 시험 URL 수정 불가
        if hasattr(self, 'url_text_box'):
            self.url_text_box.setReadOnly(True)
            self.url_text_box.setStyleSheet("""
                QLineEdit {
                    background-color: #F5F5F5;
                    border: 1px solid #CECECE;
                    border-radius: 4px;
                    padding: 0 24px;
                    font-family: "Noto Sans KR";
                    font-size: 18px;
                    font-weight: 400;
                    color: #6B6B6B;
                }
            """)

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

    def _push_event(self, step_idx, direction, payload):  # ### NEW
        """REQUEST/RESPONSE/WEBHOOK 이벤트를 순서대로 기록하고 ndjson에 append"""
        try:
            api = self.message[step_idx] if 0 <= step_idx < len(self.message) else f"step_{step_idx + 1}"
            evt = {
                "time": datetime.utcnow().isoformat() + "Z",
                "api": api,
                "dir": direction,  # "REQUEST" | "RESPONSE" | "WEBHOOK"
                "data": redact(payload)
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
            Logger.debug(f" API={api}, Direction={direction}")
            Logger.debug(f" 저장된 키들: {api}, {api_clean}, {api_with_slash}")
            Logger.debug(f" latest_events 전체 키 목록: {list(self.latest_events.keys())}")

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
                Logger.info(f"외부 CONSTANTS.py에서 SPEC_CONFIG 로드: {external_constants_path}")
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

                    Logger.debug(f" ✅ 외부 SPEC_CONFIG 로드 완료: {len(SPEC_CONFIG)}개 그룹")
                    # 디버그: 그룹 이름 출력
                    for i, g in enumerate(SPEC_CONFIG):
                        group_name = g.get('group_name', '이름없음')
                        group_keys = [k for k in g.keys() if k not in ['group_name', 'group_id']]
                        Logger.debug(f"[SYSTEM DEBUG] 그룹 {i}: {group_name}, spec_id 개수: {len(group_keys)}, spec_ids: {group_keys}")
                except Exception as e:
                    Logger.debug(f" ⚠️ 외부 CONSTANTS 로드 실패, 기본값 사용: {e}")
        # ===== 외부 CONSTANTS 로드 끝 =====

        # ===== 인스턴스 변수에 저장 (다른 메서드에서 사용) =====
        self.LOADED_SPEC_CONFIG = SPEC_CONFIG
        self.url = url_value  # ✅ 외부 CONSTANTS.py에 정의된 url도 반영
        self._original_base_url = str(url_value)  # ✅ 오염 방지용 불변 복사본
        if hasattr(self, 'url_text_box') and self.url:
            self.url_text_box.setText(self.url)
            
        self.auth_type = auth_type
        self.auth_info = auth_info
        # ===== 저장 완료 =====

        # ===== 디버그 로그 추가 =====
        Logger.debug(f"[SYSTEM DEBUG] SPEC_CONFIG 개수: {len(SPEC_CONFIG)}")
        Logger.debug(f"[SYSTEM DEBUG] 찾을 spec_id: {self.current_spec_id}")
        for i, group in enumerate(SPEC_CONFIG):
            Logger.debug(f"[SYSTEM DEBUG] Group {i} keys: {list(group.keys())}")
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

        Logger.info(f"Spec 로딩 시작: {self.spec_description} (ID: {self.current_spec_id})")

        # 시스템은 response schema / request data 사용
        Logger.debug(f"모듈: spec (센서/바이오/영상 통합)")

        # ===== PyInstaller 환경에서 외부 spec 디렉토리 우선 로드 =====
        import sys
        import os

        if getattr(sys, 'frozen', False):
            # PyInstaller 환경: 외부 spec 디렉토리 사용
            exe_dir = os.path.dirname(sys.executable)
            external_spec_parent = exe_dir

            # 외부 spec 폴더 파일 존재 확인
            external_spec_dir = os.path.join(external_spec_parent, 'spec')
            Logger.debug(f"외부 spec 폴더: {external_spec_dir}")
            Logger.debug(f"외부 spec 폴더 존재: {os.path.exists(external_spec_dir)}")
            if os.path.exists(external_spec_dir):
                files = [f for f in os.listdir(external_spec_dir) if f.endswith('.py')]
                Logger.debug(f"외부 spec 폴더 .py 파일: {files}")

            # 이미 있더라도 제거 후 맨 앞에 추가 (우선순위 보장)
            if external_spec_parent in sys.path:
                sys.path.remove(external_spec_parent)
            sys.path.insert(0, external_spec_parent)
            Logger.debug(f"sys.path에 외부 디렉토리 추가: {external_spec_parent}")

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
                Logger.debug(f"[SYSTEM SPEC] 모듈 캐시 삭제: {mod_name}")
            else:
                Logger.debug(f"[SYSTEM SPEC] 모듈 캐시 없음: {mod_name}")

        # spec 패키지가 없으면 빈 모듈로 등록
        if 'spec' not in sys.modules:
            import types
            sys.modules['spec'] = types.ModuleType('spec')
            Logger.debug(f"빈 'spec' 패키지 생성")
        # ===== 캐시 삭제 끝 =====

        # PyInstaller 환경에서는 importlib.util로 명시적으로 외부 파일 로드
        import importlib
        if getattr(sys, 'frozen', False):
            import importlib.util

            # 외부 spec 파일 경로
            data_file = os.path.join(exe_dir, 'spec', 'Data_request.py')
            schema_file = os.path.join(exe_dir, 'spec', 'Schema_response.py')
            constraints_file = os.path.join(exe_dir, 'spec', 'Constraints_request.py')

            Logger.debug(f"명시적 로드 시도:")
            Logger.debug(f"  - Data: {data_file} (존재: {os.path.exists(data_file)})")
            Logger.debug(f"  - Schema: {schema_file} (존재: {os.path.exists(schema_file)})")
            Logger.debug(f"  - Constraints: {constraints_file} (존재: {os.path.exists(constraints_file)})")

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

            Logger.debug(f"importlib.util로 외부 파일 로드 완료")
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
                Logger.debug(f"{name} 로드 경로: {file_path}")
                Logger.debug(f"{name} 수정 시간: {mtime_str}")
            else:
                Logger.debug(f"{name} 로드 경로: {file_path} (파일 없음)")
        # ===== 로그 끝 =====

        # importlib.util로 직접 로드했으므로 reload 불필요 (이미 최신 파일 로드됨)
        # PyInstaller 환경이 아닌 경우에만 reload 수행
        if not getattr(sys, 'frozen', False):
            importlib.reload(data_request_module)
            importlib.reload(schema_response_module)
            importlib.reload(constraints_request_module)

        # ✅ 시스템은 응답 검증 + 요청 전송 (outSchema/inData 사용)
        Logger.debug(f"타입: 응답 검증 + 요청 전송")
        Logger.debug(str(spec_names))
        # ✅ Response 검증용 스키마 로드 (시스템이 플랫폼으로부터 받을 응답 검증) - outSchema
        self.videoOutSchema = getattr(schema_response_module, spec_names[0], [])

        # ✅ Request 전송용 데이터 로드 (시스템이 플랫폼에게 보낼 요청) - inData
        self.videoInMessage = getattr(data_request_module, spec_names[1], [])
        self.videoMessages = getattr(data_request_module, spec_names[2], [])
        # 표시용 API 이름 (숫자 제거)
        self.videoMessagesDisplay = [self._remove_api_number_suffix(msg) for msg in self.videoMessages]
        self.videoInConstraint = getattr(constraints_request_module, self.current_spec_id + "_inConstraints", [])
        try:
            if len(spec_names) > 3:
                self.webhookInSchema = getattr(schema_response_module, spec_names[3], [])
            else:
                self.webhookInSchema = []
        except Exception as e:
            Logger.error(f"Error loading webhook schema: {e}")
            self.webhookInSchema = []

        # ✅ Webhook 관련 (현재 미사용)
        # self.videoWebhookSchema = []
        # self.videoWebhookData = []
        # self.videoWebhookInSchema = []
        # self.videoWebhookInData = []

        Logger.info(f"로딩 완료: {len(self.videoMessages)}개 API")
        Logger.info(f"API 목록: {self.videoMessages}")
        Logger.debug(f"프로토콜 설정: {self.trans_protocols}")
        self.webhook_schema_idx = 0

        # ✅ spec_config 저장 (URL 생성에 필요)
        self.spec_config = config
        
        # ✅ UI 호환성을 위해 inSchema 변수 매핑 (시스템 검증은 응답 스키마 사용)
        self.inSchema = self.videoOutSchema

    def update_table_row_with_retries(self, row, result, pass_count, error_count, data, error_text, retries):
        """테이블 행 업데이트 (안전성 강화)"""
        # ✅ 1. 범위 체크
        if row >= self.tableWidget.rowCount():
            Logger.debug(f"[TABLE UPDATE] 경고: row={row}가 테이블 범위를 벗어남 (총 {self.tableWidget.rowCount()}행)")
            return

        Logger.debug(f"[TABLE UPDATE] row={row}, result={result}, pass={pass_count}, error={error_count}, retries={retries}")

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

        Logger.debug(f"[TABLE UPDATE] 완료: row={row}")

    def load_test_info_from_constants(self):
        # ✅ 그룹명이 저장되어 있으면 사용, 없으면 spec_description 사용
        test_field = getattr(self, 'current_group_name', self.spec_description)

        return [
            ("기업명", self.CONSTANTS.company_name),
            ("제품명", self.CONSTANTS.product_name),
            ("버전", self.CONSTANTS.version),
            ("시험유형", self.CONSTANTS.test_category),
            ("시험분야", test_field),  # ✅ 그룹명 사용
            ("시험범위", self.CONSTANTS.test_range),
            ("사용자 인증 방식", self.auth_type),
            ("시험 접속 정보", self.url)
        ]

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

            Logger.debug(f" 🔄 그룹 선택: {old_group_id} → {new_group_id}")

            # ✅ 그룹이 변경되면 current_spec_id 초기화 (다음 시나리오 선택 시 무조건 다시 로드되도록)
            if old_group_id != new_group_id:
                self.current_spec_id = None
                Logger.debug(f" ✨ 그룹 변경으로 current_spec_id 초기화")

            # ✅ 그룹 ID 저장
            self.current_group_id = new_group_id
            self.update_test_field_table(selected_group)

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
            Logger.warn(f" 선택된 그룹({group_name}) 데이터를 찾을 수 없습니다.")
            return

        # ✅ 그룹 변경 감지 및 current_spec_id 초기화
        new_group_id = selected_group.get('group_id')
        old_group_id = getattr(self, 'current_group_id', None)

        Logger.debug(f" 🔄 그룹 선택: {old_group_id} → {new_group_id}")

        # ✅ 그룹이 변경되면 current_spec_id 초기화 (다음 시나리오 선택 시 무조건 다시 로드되도록)
        if old_group_id != new_group_id:
            self.current_spec_id = None
            Logger.debug(f" ✨ 그룹 변경으로 current_spec_id 초기화")

        # ✅ 그룹 ID 저장
        self.current_group_id = new_group_id

        # 시험 분야 테이블 갱신
        self.update_test_field_table(selected_group)

    def on_test_field_selected(self, row, col):
        """시험 분야 클릭 시 해당 시스템으로 동적 전환"""
        try:
            # ✅ 시험 진행 중이면 시나리오 변경 차단
            if hasattr(self, 'sbtn') and not self.sbtn.isEnabled():
                Logger.debug(f" 시험 진행 중 - 시나리오 변경 차단")
                # 비동기로 경고창 표시 (시험 진행에 영향 없도록)
                QTimer.singleShot(0, lambda: QMessageBox.warning(
                    self, "알림", "시험이 진행 중입니다.\n시험 완료 후 다른 시나리오를 진행해주세요."
                ))
                return

            self.selected_test_field_row = row

            if row in self.index_to_spec_id:
                new_spec_id = self.index_to_spec_id[row]

                if new_spec_id == self.current_spec_id:
                    Logger.debug(f" 이미 선택된 시나리오: {new_spec_id}")
                    return

                Logger.debug(f" 🔄 시험 분야 전환: {self.current_spec_id} → {new_spec_id}")
                Logger.debug(f" 현재 그룹: {self.current_group_id}")

                # ✅ 0. 일시정지 파일은 각 시나리오별로 유지 (삭제하지 않음)

                # ✅ 1. 현재 spec의 테이블 데이터 저장 (current_spec_id가 None이 아닐 때만)
                if self.current_spec_id is not None:
                    Logger.debug(f" 데이터 저장 전 - 테이블 행 수: {self.tableWidget.rowCount()}")
                    self.save_current_spec_data()
                else:
                    Logger.debug(f" ⚠️ current_spec_id가 None - 저장 스킵 (그룹 전환 직후)")

                # ✅ 2. spec_id 업데이트
                self.current_spec_id = new_spec_id

                # ✅ 3. spec 데이터 다시 로드
                self.load_specs_from_constants()

                Logger.debug(f" 로드된 API 개수: {len(self.videoMessages)}")
                Logger.debug(f" API 목록: {self.videoMessages}")

                # ✅ 4. 기본 변수 초기화
                self.cnt = 0
                self.current_retry = 0
                self.message_error = []
                
                # ✅ 4-1. 웹훅 관련 변수 초기화
                self.webhook_flag = False
                self.post_flag = False
                self.res = None
                self.webhook_schema_idx = 0

                # ✅ 5. 테이블 완전 재구성
                Logger.debug(f" 테이블 완전 재구성 시작")
                self.update_result_table_structure(self.videoMessages)

                # ✅ 6. 저장된 데이터 복원 시도
                restored = self.restore_spec_data(new_spec_id)

                if not restored:
                    Logger.debug(f" 저장된 데이터 없음 - 초기화")
                    # 시나리오별 모니터링 로그 복원 정책:
                    # 저장된 로그가 없으면 이전 시나리오 로그를 남기지 않고 비운다.
                    self.valResult.clear()
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
                    Logger.debug(f" 저장된 데이터 복원 완료")

                # ✅ 7. trace 및 latest_events 초기화
                self.trace.clear()
                self.latest_events = {}

                # ✅ 8. 설정 다시 로드
                self.get_setting()

                # ✅ 9. 평가 점수 디스플레이 업데이트
                self.update_score_display()

                # URL 업데이트 (base_url + 시나리오명) - 오염 방지: CONSTANTS에서 직접 읽기
                test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
                fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
                self.pathUrl = fresh_base_url.rstrip('/') + "/" + test_name
                self.url_text_box.setText(self.pathUrl)  # 안내 문구 변경
                Logger.debug(f" 시험 URL 업데이트: {self.pathUrl}")
                print(f"[SYSTEM DEBUG] on_test_field_selected에서 pathUrl 설정: {self.pathUrl}")

                # ✅ 10. 결과 텍스트 초기화
                # self.append_monitor_log(
                #     step_name=f"시스템 전환 완료: {self.spec_description}",
                #     details=f"API 개수: {len(self.videoMessages)}개 | API 목록: {', '.join(self.videoMessagesDisplay)}"
                # )

                Logger.debug(f" ✅ 시스템 전환 완료")

        except Exception as e:
            Logger.debug(f" 시험 분야 선택 처리 실패: {e}")
            import traceback
            traceback.print_exc()

    def update_result_table_structure(self, api_list):
        """테이블 구조를 완전히 재구성 (API 개수에 맞게)"""
        api_count = len(api_list)
        Logger.debug(f" 테이블 재구성 시작: {api_count}개 API")

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

            Logger.debug(f" Row {row}: {display_name} 설정 완료")

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

        Logger.debug(f" 테이블 재구성 완료: {self.tableWidget.rowCount()}개 행")

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
        self.webhook_flag = False
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
                    # 서버가 완전히 준비될 때까지 대기 (최대 15초)
                    ready = self.webhook_thread.server_ready.wait(timeout=15)
                    if not ready:
                        Logger.error("[Webhook] 서버 준비 타임아웃 - POST 전송 취소")
                else:
                    # WebHook이 아닌 경우 플래그 초기화
                    self.webhook_flag = False
        except Exception as e:
            Logger.debug(str(e))
            import traceback
            traceback.print_exc()

        try:
            path = re.sub(r'\d+$', '', path)
            Logger.debug(f" [post] Sending request to {path} with auth_type={self.r2}, token={self.token}")
            Logger.debug(f" [post] request message {json_data}")
            self.res = requests.post(
                path,
                headers=headers,
                data=json_data,
                auth=auth,
                verify=False,
                timeout=time_out
            )
            Logger.debug(f" [post] response message {self.res.status_code}")
            Logger.debug(
                f"{self.res.json() if self.res.headers.get('Content-Type', '').startswith('application/json') else self.res.text}"
            )
        except Exception as e:
            Logger.debug(str(e))

    # 임시 수정 
    def handle_webhook_result(self, result):
        self.webhook_res = result
        self.webhook_thread.stop()
        self._push_event(self.webhook_cnt, "WEBHOOK", result)

    # 웹훅 검증
    def get_webhook_result(self):
        # ✅ 웹훅 스키마가 없으면 검증하지 않음
        if self.cnt >= len(self.webhookSchema) or not self.webhookSchema[self.cnt]:
            Logger.debug(f" API {self.cnt}는 웹훅 스키마가 없음 - 검증 건너뜀")
            self.webhook_flag = False
            return
        
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
            Logger.debug(f"\n========== 웹훅 이벤트 검증 디버깅 ==========")
            webhook_api = self.message[self.webhook_cnt] if self.webhook_cnt < len(self.message) else 'N/A'
            Logger.debug(f"webhook_cnt={self.webhook_cnt}, API={webhook_api}")
            Logger.debug(f"webhookSchema 총 개수={len(self.webhookSchema)}")
            Logger.debug(f"webhook_res is None: {self.webhook_res is None}")

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
            Logger.debug(f" ==========================================\n")

        display_name = self.message_display[self.webhook_cnt] if self.webhook_cnt < len(self.message_display) else (
            self.message[self.webhook_cnt] if self.webhook_cnt < len(self.message) else "Unknown"
        )

        # 웹훅 수신 payload를 실시간 모니터링에 [수신]으로 표시
        self.append_monitor_log(
            step_name=f"웹훅 이벤트: {display_name}",
            request_json=tmp_webhook_res,
            direction="RECV"
        )

        # 웹훅 ACK 응답 payload를 실시간 모니터링에 [송신]으로 표시
        if self.webhook_res is not None:
            webhook_ack_payload = {"code": "200", "message": "성공"}
            self.append_monitor_log(
                step_name=f"웹훅 응답: {display_name}",
                request_json=json.dumps(webhook_ack_payload, indent=4, ensure_ascii=False),
                direction="SEND"
            )

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

                Logger.debug(f" 누적 결과: pass={accumulated_pass}, error={accumulated_error}")
            else:
                # 누적 배열이 없으면 웹훅 결과만 사용
                accumulated_pass = key_psss_cnt
                accumulated_error = key_error_cnt

            if self.webhook_cnt < len(self.num_retries_list):
                current_retries = self.num_retries_list[self.webhook_cnt]
            else:
                current_retries = 1

            result_step_title = f"결과: {display_name} - 웹훅 이벤트 데이터 ({self.current_retry + 1}/{current_retries})"
            total_fields = accumulated_pass + accumulated_error
            score_value = (accumulated_pass / total_fields * 100) if total_fields > 0 else 0
            result_details = (
                f"통과 필드 수: {accumulated_pass}, 실패 필드 수: {accumulated_error} | 실시간 메시지: WebHook"
            )
            if val_result == "FAIL":
                result_details += f" | 상세: {to_detail_text(val_text)}"

            self.append_monitor_log(
                step_name=result_step_title,
                request_json="",
                result_status=val_result,
                score=score_value,
                details=result_details,
                direction="RECV"
            )

                # 누적된 필드 수로 테이블 업데이트
            self.update_table_row_with_retries(
                self.webhook_cnt, val_result, accumulated_pass, accumulated_error,
                tmp_webhook_res, to_detail_text(val_text), current_retries
            )

        # step_buffers 업데이트 추가 (실시간 모니터링과 상세보기 일치)
        if self.webhook_cnt < len(self.step_buffers):
            webhook_data_text = tmp_webhook_res
            webhook_error_text = to_detail_text(val_text) if val_result == "FAIL" else "오류가 없습니다."
            update_webhook_step_buffer_fields(
                step_buffer=self.step_buffers[self.webhook_cnt],
                webhook_data=webhook_data,
                webhook_error_text=webhook_error_text,
                webhook_pass_cnt=key_psss_cnt,
                webhook_total_cnt=(key_psss_cnt + key_error_cnt),
            )
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
                self.valResult.append("시험이 완료되었습니다.")
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
                api_name = self.message[self.cnt] if self.cnt < len(self.message) else 'N/A'
                Logger.debug(f"웹훅 이벤트 수신 완료 (API: {api_name})")
                if self.webhook_res != None:
                    Logger.warn(f" 웹훅 메시지 수신")
                    # ✅ 타이머 라인 제거
                    self.update_last_line_timer("", remove=True)
                elif math.ceil(time_interval) >= self.time_outs[self.cnt] / 1000 - 1:
                    Logger.warn(f" 메시지 타임아웃! 웹훅 대기 종료")
                    # ✅ 타이머 라인 제거
                    self.update_last_line_timer("", remove=True)
                else :
                    # ✅ 대기 시간 타이머 표시 (마지막 줄 갱신)
                    remaining = max(0, int((self.time_outs[self.cnt] / 1000) - time_interval))
                    self.update_last_line_timer(f"남은 대기 시간: {remaining}초")
                    
                    Logger.debug(f" 웹훅 대기 중... (API {self.cnt}) 타임아웃 {round(time_interval)} /{round(self.time_outs[self.cnt] / 1000)}")
                    return
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
                api_endpoint = self.message[self.cnt] if self.cnt < len(self.message) else ""
                
                # ✅ URL 오염 방지: pathUrl을 매번 깨끗한 base로 재구성
                fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
                    base_with_scenario = fresh_base_url.rstrip('/') + "/" + test_name
                else:
                    base_with_scenario = fresh_base_url.rstrip('/')
                
                # API 엔드포인트 추가
                api_path = api_endpoint.lstrip('/')
                path = f"{base_with_scenario}/{api_path}"
                print(f"[SYSTEM DEBUG] update_view에서 API 호출 경로: {path}")
                print(f"[SYSTEM DEBUG] fresh_base_url: {fresh_base_url}, base_with_scenario: {base_with_scenario}, api_path: {api_path}")

                # ✅ 실시간 API 경로 표시 (매번 새로 생성된 path를 사용하므로 누적되지 않음)
                if hasattr(self, 'url_text_box'):
                    self.url_text_box.setText(path) 
                
                inMessage = self.inMessage[self.cnt] if self.cnt < len(self.inMessage) else {}
                # ✅ Data Mapper 적용 - 이전 응답 데이터로 요청 업데이트
                # generator는 이미 self.latest_events를 참조하고 있으므로 재할당 불필요
                Logger.debug(f"[MAPPER] latest_events 상태: {list(self.latest_events.keys())}")
                inMessage = self._apply_request_constraints(inMessage, self.cnt)

                trans_protocol = inMessage.get("transProtocol", {})
                if trans_protocol:
                    trans_protocol_type = trans_protocol.get("transProtocolType", {})
                    if "WebHook".lower() in str(trans_protocol_type).lower():

                        # 플랫폼이 웹훅을 보낼 외부 주소 설정 - 동적
                        WEBHOOK_IP = CONSTANTS.WEBHOOK_PUBLIC_IP  # 웹훅 수신 IP/도메인
                        WEBHOOK_PORT = CONSTANTS.WEBHOOK_PORT  # 웹훅 수신 포트
                        WEBHOOK_URL = f"https://{WEBHOOK_IP}:{WEBHOOK_PORT}"  # 플랫폼/시스템이 웹훅을 보낼 주소

                        trans_protocol = {
                            "transProtocolType": "WebHook",
                            "transProtocolDesc": WEBHOOK_URL
                        }
                        
                        # ngrok 하드 코딩 부분 (01/09)
                        # ---- 여기부터
                        # WEBHOOK_DISPLAY_URL = CONSTANTS.WEBHOOK_DISPLAY_URL
                        # trans_protocol = {
                        #     "transProtocolType": "WebHook",
                        #     "transProtocolDesc": WEBHOOK_DISPLAY_URL  # ngrok 주소 전송
                        # }
                        #---- 여기까지
                        inMessage["transProtocol"] = trans_protocol

                        # (01/08 - 동적: 위에 작동, 하드코딩: 아래를 작동)
                        Logger.debug(f" [post] transProtocol 설정 추가됨: {inMessage}")
                        # Logger.debug(f" [post] transProtocol 설정 (ngrok 주소): {WEBHOOK_DISPLAY_URL}")
                        
                elif self.r2 == "B" and self.message[self.cnt] == "Authentication":
                    inMessage["userID"] = self.accessInfo[0]
                    inMessage["userPW"] = self.accessInfo[1]

                json_data = json.dumps(inMessage).encode('utf-8')

                # ✅ REQUEST 기록 제거 - 서버(api_server.py)에서만 기록하도록 변경
                self._push_event(self.cnt, "REQUEST", inMessage)

                api_name = self.message[self.cnt] if self.cnt < len(self.message) else ""
                if api_name and isinstance(inMessage, dict):
                    self.reference_context[f"/{api_name}"] = inMessage

                # 순서 확인용 로그
                api_name = self.message[self.cnt] if self.cnt < len(self.message) else 'index out of range'
                Logger.debug(f"플랫폼에 요청 전송: {api_name} (시도 {self.current_retry + 1})")

                # ✅ 송신 메시지 실시간 모니터링 로그 추가 (SEND)
                display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                self.append_monitor_log(
                    step_name=display_name,
                    request_json=json.dumps(inMessage, indent=4, ensure_ascii=False),
                    direction="SEND"
                )

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
                            Logger.debug(f" 웹훅 스키마 필드 추가: rqd={webhook_rqd_cnt}, opt={webhook_opt_cnt}")

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
                    step_name=f"시험 API: {api_name}",
                    request_json="",
                    score=score_value,
                    details=f"⏱️ Timeout ({timeout_sec}초) - Message Missing! (시도 {self.current_retry + 1}/{current_retries}) | 통과 필드 수: {self.total_pass_cnt}, 실패 필드 수: {self.total_error_cnt}"
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
                    self.webhook_flag = False

                    # 다음 API를 위한 누적 카운트 초기 설정 확인
                    if hasattr(self, 'step_pass_counts') and self.cnt < len(self.step_pass_counts):
                        self.step_pass_counts[self.cnt] = 0
                        self.step_error_counts[self.cnt] = 0
                        # ✅ 배열 범위 체크 추가
                        if self.cnt < len(self.step_pass_flags):
                            self.step_pass_flags[self.cnt] = 0

                self.message_in_cnt = 0
                self.post_flag = False
                self.processing_response = False

                # 플랫폼과 동일한 대기 시간 설정
                self.time_pre = time.time()

                if self.cnt >= len(self.message):
                    self.tick_timer.stop()
                    self.valResult.append("시험이 완료되었습니다.")

                    # ✅ 현재 spec 데이터 저장
                    self.save_current_spec_data()

                    self.processing_response = False
                    self.post_flag = False

                    self.cnt = 0
                    self.current_retry = 0

                    # 최종 리포트 생성
                    total_fields = self.total_pass_cnt + self.total_error_cnt

                    # ✅ JSON 결과 자동 저장 추가
                    Logger.debug(f" 평가 완료 - 자동 저장 시작")
                    try:
                        self.run_status = "완료"
                        result_json = build_result_json(self)
                        url = f"{CONSTANTS.management_url}/api/integration/test-results"
                        response = requests.post(url, json=result_json)
                        Logger.debug(f"시험 결과 전송 상태 코드: {response.status_code}")
                        Logger.debug(f"시험 결과 전송 응답: {response.text}")
                        json_path = os.path.join(result_dir, "response_results.json")
                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump(result_json, f, ensure_ascii=False, indent=2)
                        Logger.debug(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                        self.append_monitor_log(
                            step_name="관리시스템 결과 전송 완료",
                            details=""
                        )
                        Logger.debug(f" try 블록 정상 완료")

                    except Exception as e:
                        Logger.debug(f"❌ JSON 저장 중 오류 발생: {e}")
                        import traceback
                        traceback.print_exc()
                        self.valResult.append(f"\n결과 저장 실패: {str(e)}")
                        Logger.debug(f" except 블록 실행됨")

                    finally:
                        # ✅ 평가 완료 시 일시정지 파일 정리 (에러 발생 여부와 무관하게 항상 실행)
                        Logger.debug(f" ========== finally 블록 진입 ==========")
                        self.cleanup_paused_file()
                        Logger.debug(f" ========== finally 블록 종료 ==========")
                        
                        # stop/pause 의도가 있으면 completed 전송 금지
                        if not getattr(self, "is_paused", False):
                            try:
                                api_client = APIClient()
                                api_client.send_heartbeat_completed()
                                Logger.info(f"✅ 시험 완료 - completed 상태 전송 완료")
                            except Exception as e:
                                Logger.warning(f"⚠️ 시험 완료 - completed 상태 전송 실패: {e}")
                        else:
                            Logger.info("⏭️ 일시정지 상태이므로 completed heartbeat 전송 생략")

                    self.sbtn.setEnabled(True)
                    self.stop_btn.setDisabled(True)
                    self.cancel_btn.setDisabled(True)


            # 응답이 도착한 경우 처리
            elif self.post_flag == True:
                if self.res is None:
                    # ✅ 대기 시간 타이머 표시 (마지막 줄 갱신)
                    current_timeout = self.time_outs[self.cnt] / 1000 if self.cnt < len(self.time_outs) else 5.0
                    remaining = max(0, int(current_timeout - time_interval))
                    self.update_last_line_timer(f"남은 대기 시간: {remaining}초")

                if self.res != None:
                    # ✅ 응답 수신 완료 - 타이머 라인 제거 (웹훅 대기가 아닐 때만)
                    if not self.webhook_flag:
                        self.update_last_line_timer("", remove=True)
                    
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
                            #self.post_flag = False
                            #self.processing_response = False
                            #self.current_retry += 1
                            self.res.txt = {}
                            #return

                        # ✅ RESPONSE 기록 제거 - 서버(api_server.py)에서만 기록하도록 변경
                        self._push_event(self.cnt, "RESPONSE", res_data)

                        # 현재 재시도 정보
                        current_retries = self.num_retries_list[self.cnt] if self.cnt < len(
                            self.num_retries_list) else 1
                        current_protocol = self.trans_protocols[self.cnt] if self.cnt < len(
                            self.trans_protocols) else "Unknown"

                        # 단일 응답에 대한 검증 처리
                        from core.utils import replace_transport_desc_for_display
                        tmp_res_auth = json.dumps(res_data, indent=4, ensure_ascii=False)
                        tmp_res_auth = replace_transport_desc_for_display(tmp_res_auth)  # UI 표시용 치환

                        # 실시간 모니터링 창에 응답 데이터 표시
                        # 첫 번째 응답일 때만 API 명과 검증 예정 횟수 표시
                        if self.current_retry == 0:
                            api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                            display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                            self.append_monitor_log(
                                step_name=f"시험 API: {display_name} ({self.current_retry + 1}/{current_retries})",
                                request_json=tmp_res_auth,
                                direction="RECV"
                            )
                        else:
                            # 2회차 이상: API 명과 회차만 표시
                            api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                            display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                            self.append_monitor_log(
                                step_name=f"시험 API: {display_name} ({self.current_retry + 1}/{current_retries})",
                                request_json=tmp_res_auth,
                                direction="RECV"
                            )

                    # ✅ 디버깅: 어떤 스키마로 검증하는지 확인
                    if self.current_retry == 0:  # 첫 시도에만 출력
                        Logger.debug(f"\n========== 스키마 검증 디버깅 ==========")
                        api_name = self.message[self.cnt] if self.cnt < len(self.message) else 'N/A'
                        Logger.debug(f"cnt={self.cnt}, API={api_name}")
                        Logger.debug(f"webhook_flag={self.webhook_flag}")
                        Logger.debug(f"current_protocol={current_protocol}")

                        # ✅ 웹훅 API의 구독 응답은 일반 스키마 사용
                        # webhook_flag는 실제 웹훅 이벤트 수신 시에만 True
                        # 구독 응답은 항상 outSchema[self.cnt] 사용
                        schema_index = self.cnt
                        Logger.debug(f" 사용 스키마: outSchema[{schema_index}]")

                        # 스키마 필드 확인
                        if self.cnt < len(self.outSchema):
                            schema_to_use = self.outSchema[self.cnt]
                            if isinstance(schema_to_use, dict):
                                schema_keys = list(schema_to_use.keys())[:5]
                                Logger.debug(f" 스키마 필드 (first 5): {schema_keys}")

                    # val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.outSchema[self.cnt], res_data, self.flag_opt)
                    resp_rules = {}
                    try:
                        resp_rules = self.resp_rules or {}
                    except Exception as e:
                        resp_rules = {}
                        Logger.error(f" 응답 검증 규칙 로드 실패: {e}")

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
                                    Logger.debug(f" {ref_endpoint} {direction}를 trace 파일에서 로드 시도")
                                    response_data = self._load_from_trace_file(ref_api_name, direction)
                                    if response_data and isinstance(response_data, dict):
                                        self.reference_context[ref_endpoint] = response_data
                                        Logger.debug(f" {ref_endpoint} {direction}를 trace 파일에서 로드 완료")
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
                                    Logger.debug(f" {ref_endpoint_max} {direction}를 trace 파일에서 로드 시도 (Max)")
                                    response_data_max = self._load_from_trace_file(ref_api_name_max, direction)
                                    if response_data_max and isinstance(response_data_max, dict):
                                        self.reference_context[ref_endpoint_max] = response_data_max
                                        Logger.debug(f" {ref_endpoint_max} {direction}를 trace 파일에서 로드 완료 (Max)")
                                else:
                                    event_data = self.latest_events.get(ref_api_name_max, {}).get(direction, {})
                                    if event_data and isinstance(event_data, dict):
                                        self.reference_context[ref_endpoint_max] = event_data.get("data", {})
                            
                            # referenceEndpointMin 처리
                            ref_endpoint_min = validation_rule.get("referenceEndpointMin", "")
                            if ref_endpoint_min:
                                ref_api_name_min = ref_endpoint_min.lstrip("/")
                                if ref_api_name_min not in self.latest_events or direction not in self.latest_events.get(ref_api_name_min, {}):
                                    Logger.debug(f" {ref_endpoint_min} {direction}를 trace 파일에서 로드 시도 (Min)")
                                    response_data_min = self._load_from_trace_file(ref_api_name_min, direction)
                                    if response_data_min and isinstance(response_data_min, dict):
                                        self.reference_context[ref_endpoint_min] = response_data_min
                                        Logger.debug(f" {ref_endpoint_min} {direction}를 trace 파일에서 로드 완료 (Min)")
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
                        Logger.error(f" 응답 검증 중 TypeError 발생: {te}, 일반 검증으로 재시도")
                        val_result, val_text, key_psss_cnt, key_error_cnt, opt_correct, opt_error = json_check_(
                            self.outSchema[self.cnt],
                            res_data,
                            self.flag_opt
                        )
                    if self.message[self.cnt] == "Authentication":
                        self.handle_authentication_response(res_data)

                    if self.current_retry == 0:  # 첫 시도에만 출력
                        Logger.debug(f" 검증 결과: {val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
                        Logger.debug(f" ==========================================\n")

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
                    
                    Logger.debug(f"[SCORE DEBUG] API {self.cnt} 시도 {self.current_retry + 1}: pass={key_psss_cnt}, error={key_error_cnt}")
                    Logger.debug(f"[SCORE DEBUG] step_pass_counts[{self.cnt}] = {self.step_pass_counts[self.cnt]}")
                    Logger.debug(f"[SCORE DEBUG] step_error_counts[{self.cnt}] = {self.step_error_counts[self.cnt]}")

                    if final_result == "PASS":
                        # ✅ 배열 범위 체크 추가
                        if self.cnt < len(self.step_pass_flags):
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
                        error_text = to_detail_text(val_text)
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
                        # ✅ 배열 범위 체크 추가
                        if self.cnt < len(self.step_pass_flags) and self.step_pass_flags[self.cnt] >= current_retries:
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
                            details=f"통과 필드 수: {total_pass_count}, 실패 필드 수: {total_error_count} | {'일반 메시지' if current_protocol.lower() == 'basic' else f'실시간 메시지: {current_protocol}'}"
                        )
                    else:
                        # 중간 시도 - 진행중 표시
                        self.append_monitor_log(
                            step_name=step_title,
                            request_json="",  # 데이터는 앞서 출력되었으므로 생략
                            details=f"검증 진행 중... | {'일반 메시지' if current_protocol.lower() == 'basic' else f'실시간 메시지: {current_protocol}'}"
                        )

                    # ✅ 웹훅 처리를 재시도 완료 체크 전에 실행 (step_pass_counts 업데이트를 위해)
                    if self.webhook_flag:
                        Logger.debug(f" 웹훅 처리 시작 (API {self.cnt})")
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
                        
                        Logger.debug(f" API {self.cnt} 완료: pass={final_pass_count}, error={final_error_count}")

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

                        Logger.debug(f" 분야별 점수: pass={self.total_pass_cnt}, error={self.total_error_cnt}")
                        Logger.debug(f" 전체 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}")

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
                    details="시험이 완료되었습니다."
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
                Logger.debug(f"분야별 점수: pass={self.total_pass_cnt}, error={self.total_error_cnt}, score={final_score:.1f}%")
                Logger.debug(f"전체 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}, score={global_score:.1f}%")

                # ✅ JSON 결과 자동 저장 추가
                Logger.debug(f"평가 완료 - 자동 저장 시작 (경로2)")
                try:
                    self.run_status = "완료"
                    result_json = build_result_json(self)
                    url = f"{CONSTANTS.management_url}/api/integration/test-results"
                    response = requests.post(url, json=result_json)
                    Logger.debug(f"✅ 시험 결과 전송 상태 코드:: {response.status_code}")
                    Logger.debug(f"📥  시험 결과 전송 응답:: {response.text}")
                    json_path = os.path.join(result_dir, "response_results.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result_json, f, ensure_ascii=False, indent=2)
                    Logger.debug(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                    self.append_monitor_log(
                        step_name="관리시스템 결과 전송 완료",
                        details=""
                    )
                    Logger.debug(f" try 블록 정상 완료 (경로2)")
                except Exception as e:
                    Logger.debug(f"❌ JSON 저장 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    self.valResult.append(f"\n결과 저장 실패: {str(e)}")
                    Logger.debug(f" except 블록 실행됨 (경로2)")
                finally:
                    # ✅ 평가 완료 시 일시정지 파일 정리 (에러 발생 여부와 무관하게 항상 실행)
                    Logger.debug(f" ========== finally 블록 진입 (경로2) ==========")
                    self.cleanup_paused_file()
                    Logger.debug(f" ========== finally 블록 종료 (경로2) ==========")
                    
                    # stop/pause 의도가 있으면 completed 전송 금지 (경로2)
                    if not getattr(self, "is_paused", False):
                        try:
                            api_client = APIClient()
                            api_client.send_heartbeat_completed()
                            Logger.info(f"✅ 시험 완료 (경로2) - completed 상태 전송 완료")
                        except Exception as e:
                            Logger.warning(f"⚠️ 시험 완료 (경로2) - completed 상태 전송 실패: {e}")
                    else:
                        Logger.info("⏭️ 일시정지 상태이므로 completed heartbeat 전송 생략 (경로2)")

                self.sbtn.setEnabled(True)
                self.stop_btn.setDisabled(True)
                self.cancel_btn.setDisabled(True)

        except Exception as err:
            import traceback
            Logger.error(f" Exception in update_view: {err}")
            Logger.error(f" Current state - cnt={self.cnt}, current_retry={self.current_retry}")
            Logger.error(f" Traceback:")
            traceback.print_exc()
            APIClient().send_heartbeat_error(str(err))
            QMessageBox.critical(self, "Error", "Error Message: 오류 확인 후 검증 절차를 다시 시작해주세요" + '\n' + f"Error at step {self.cnt + 1}: {str(err)}")
            self.tick_timer.stop()
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">검증 절차가 중지되었습니다. (오류 위치: Step {self.cnt + 1})</div>')
            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)
            self.cancel_btn.setDisabled(True)

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

    def _clean_trace_dir_once(self):
        """results/trace 폴더 안의 파일들을 삭제"""
        Logger.debug(f" ⚠️  _clean_trace_dir_once() 호출됨!")
        import traceback
        Logger.debug(f" 호출 스택:\n{''.join(traceback.format_stack()[-3:-1])}")
        os.makedirs(CONSTANTS.trace_path, exist_ok=True)
        for name in os.listdir(CONSTANTS.trace_path):
            path = os.path.join(CONSTANTS.trace_path, name)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    Logger.debug(f" 삭제: {name}")
                except OSError:
                    pass

    def start_btn_clicked(self):
        """평가 시작 버튼 클릭"""
        try:
            setattr(CONSTANTS, "SUPPRESS_COMPLETED_HEARTBEAT", False)
            setattr(CONSTANTS, "HEARTBEAT_STOPPED_LOCK", False)
            APIClient().send_heartbeat_in_progress(getattr(self.CONSTANTS, "request_id", ""))
        except Exception as e:
            Logger.warning(f"⚠️ 시험 시작 - in_progress 상태 전송 실패: {e}")

        # ✅ 자동 재시작 플래그 확인 및 제거
        is_auto_restart = getattr(self, '_auto_restart', False)
        if is_auto_restart:
            self._auto_restart = False
            Logger.debug(f" 자동 재시작 모드 - 시나리오 선택 검증 건너뜀")
        else:
            # ✅ 1. 시나리오 선택 확인 (수동 시작 시에만)
            if not hasattr(self, 'current_spec_id') or not self.current_spec_id:
                QMessageBox.warning(self, "알림", "시험 시나리오를 먼저 선택하세요.")
                return

        # ✅ 일시정지 파일 존재 여부 확인 (spec_id별로 관리)
        paused_file_path = os.path.join(result_dir, f"response_results_paused_{self.current_spec_id}.json")
        resume_mode = os.path.exists(paused_file_path)

        if resume_mode:
            Logger.debug(f" ========== 재개 모드: 일시정지 상태 복원 ==========")
            # 재개 모드: 저장된 상태 복원
            if self.load_paused_state():
                self.is_paused = False  # 재개 시작이므로 paused 플래그 해제
                Logger.debug(f" 재개 모드: {self.last_completed_api_index + 2}번째 API부터 시작")
            else:
                # 복원 실패 시 신규 시작으로 전환
                Logger.warn(f" 상태 복원 실패, 신규 시작으로 전환")
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

        # ✅ URL 오염 방지: 텍스트 박스가 아닌 CONSTANTS에서 직접 읽기
        fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
        if hasattr(self, 'spec_config'):
            test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
            self.pathUrl = fresh_base_url.rstrip('/') + "/" + test_name
        else:
            self.pathUrl = fresh_base_url
        print(f"[SYSTEM DEBUG] sbtn_push에서 pathUrl 설정: {self.pathUrl}")
        if not resume_mode:
            Logger.debug(f"========== 검증 시작: 완전 초기화 ==========")
        Logger.debug(f"시험 URL: {self.pathUrl}")
        Logger.debug(f"시험: {self.current_spec_id} - {self.spec_description}")
        Logger.debug(f"사용자 인증 방식: {self.CONSTANTS.auth_type}")

        QApplication.processEvents()  # 스피너 애니메이션 유지
        self.update_result_table_structure(self.videoMessages)
        QApplication.processEvents()  # 스피너 애니메이션 유지

        # ✅ 2. 기존 타이머 정지 (중복 실행 방지)
        if self.tick_timer.isActive():
            Logger.debug(f" 기존 타이머 중지")
            self.tick_timer.stop()

        if not resume_mode:
            # ========== 신규 시작 모드: 완전 초기화 ==========
            Logger.debug(f" ========== 신규 시작: 완전 초기화 ==========")

            # ✅ 3. trace 디렉토리 초기화 (그룹이 변경될 때만)
            # 같은 그룹 내 spec 전환 시에는 trace 유지 (맥락 검증용)
            if not hasattr(self, '_last_cleaned_group') or self._last_cleaned_group != self.current_group_id:
                Logger.debug(f" 그룹 변경 감지: {getattr(self, '_last_cleaned_group', None)} → {self.current_group_id}")
                Logger.debug(f" trace 디렉토리 초기화 실행")
                self._clean_trace_dir_once()
                self._last_cleaned_group = self.current_group_id
            else:
                Logger.debug(f" 같은 그룹 내 spec 전환: trace 디렉토리 유지 (맥락 검증용)")

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
                Logger.debug(f"[SCORE RESET] 기존 {composite_key} 점수 제거: pass={prev_pass}, error={prev_error}")
                Logger.debug(f"[SCORE RESET] 기존 {composite_key} 선택 점수 제거: opt_pass={prev_opt_pass}, opt_error={prev_opt_error}")

                # ✅ global 점수에서 해당 spec 점수 제거
                self.global_pass_cnt = max(0, self.global_pass_cnt - prev_pass)
                self.global_error_cnt = max(0, self.global_error_cnt - prev_error)
                # ✅ global 선택 점수에서 해당 spec 점수 제거
                self.global_opt_pass_cnt = max(0, self.global_opt_pass_cnt - prev_opt_pass)
                self.global_opt_error_cnt = max(0, self.global_opt_error_cnt - prev_opt_error)

                Logger.debug(f"[SCORE RESET] 조정 후 global 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}")
                Logger.debug(f"[SCORE RESET] 조정 후 global 선택 점수: opt_pass={self.global_opt_pass_cnt}, opt_error={self.global_opt_error_cnt}")

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
            Logger.debug(f" step_buffers 재생성 완료: {len(self.step_buffers)}개")

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
            Logger.debug(f" 테이블 초기화: {api_count}개 API")
            for i in range(self.tableWidget.rowCount()):
                QApplication.processEvents()  # 스피너 애니메이션 유지
                # ✅ 기존 위젯 제거 (겹침 방지)
                self.tableWidget.setCellWidget(i, 2, None)
                
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
                    existing_item = self.tableWidget.item(i, col)
                    if existing_item:
                        # 기존 아이템이 있으면 값만 업데이트 (setItem 호출하지 않음)
                        existing_item.setText(value)
                        existing_item.setTextAlignment(Qt.AlignCenter)
                    else:
                        # 아이템이 없으면 새로 생성하고 설정
                        new_item = QTableWidgetItem(value)
                        new_item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget.setItem(i, col, new_item)
            Logger.debug(f" 테이블 초기화 완료")

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

            # ✅ 17. URL 설정 (오염 방지: CONSTANTS에서 읽기)
            fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
            if hasattr(self, 'spec_config'):
                test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
                self.pathUrl = fresh_base_url.rstrip('/') + "/" + test_name
            else:
                self.pathUrl = fresh_base_url
            self.url_text_box.setText(self.pathUrl)  # 안내 문구 변경
            print(f"[SYSTEM DEBUG] start_test_execution에서 pathUrl 설정: {self.pathUrl}")

            # ✅ 18. 시작 메시지
            self.append_monitor_log(
                step_name=f"시험 시작: {self.spec_description}",
                details=f"API 개수: {len(self.videoMessages)}개"
            )
        else:
            # ========== 재개 모드: 저장된 상태 사용, 초기화 건너뛰기 ==========
            Logger.debug(f" 재개 모드: 초기화 건너뛰기, 저장된 상태 사용")
            # cnt는 last_completed_api_index + 1로 설정
            self.cnt = self.last_completed_api_index + 1
            Logger.debug(f" 재개 모드: cnt = {self.cnt}")

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
            Logger.debug(f" 재개 모드: 실행 상태 변수 초기화 완료")

            # ✅ 미완료 API의 trace 파일 삭제 (완료된 API는 유지)
            trace_dir = os.path.join(result_dir, "trace")
            if os.path.exists(trace_dir):
                Logger.debug(f" 미완료 API trace 파일 삭제 시작 (완료: 0~{self.last_completed_api_index})")
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
                                Logger.debug(f" 삭제: {pattern}")
                            except Exception as e:
                                Logger.warn(f" trace 파일 삭제 실패: {e}")
                Logger.debug(f" 미완료 API trace 파일 정리 완료")

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
                Logger.debug(f" 모니터링 메시지 복원 완료: {len(self.paused_valResult_text)} 문자")

            # ✅ 테이블 데이터 복원 (완료된 API들만)
            Logger.debug(f" 테이블 데이터 복원 시작: 0 ~ {self.last_completed_api_index}번째 API")
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
                        Logger.debug(f" 테이블 복원: API {i+1} - result={result}, pass={pass_count}, error={error_count}, retries={retries}")
            Logger.debug(f" 테이블 데이터 복원 완료")

        QApplication.processEvents()  # 스피너 애니메이션 유지

        # ✅ 5. 버튼 상태 변경 (신규/재개 공통)
        self.sbtn.setDisabled(True)
        self.stop_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)

        QApplication.processEvents()  # 스피너 애니메이션 유지

        # ✅ 19. 타이머 시작 (모든 초기화 완료 후)
        Logger.debug(f" 타이머 시작")
        self.tick_timer.start(1000)
        Logger.debug(f" ========== 검증 시작 준비 완료 ==========")

        # ✅ 로딩 팝업 닫기 (최소 표시 시간 확보)
        if self.loading_popup:
            # 팝업이 최소한 보이도록 잠시 대기 (스피너 유지)
            for _ in range(3):  # 3 * 100ms = 300ms
                time.sleep(0.1)
                QApplication.processEvents()
            self.loading_popup.close()
            self.loading_popup = None

        Logger.debug(f" 현재 global 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}")

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

            # JSON 파일로 저장 (spec_id 포함)
            paused_file_path = os.path.join(result_dir, f"response_results_paused_{self.current_spec_id}.json")
            with open(paused_file_path, "w", encoding="utf-8") as f:
                json.dump(paused_state, f, ensure_ascii=False, indent=2)

            Logger.debug(f"✅ 일시정지 상태 저장 완료: {paused_file_path}")
            Logger.debug(f"   마지막 완료 API 인덱스: {last_completed}")

            # 모니터링 창에 로그 추가
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 10px;">💾 재개 정보 저장 완료: {paused_file_path}</div>')
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">   (마지막 완료 API: {last_completed + 1}번째, 다음 재시작 시 {last_completed + 2}번째 API부터 이어서 실행)</div>')

        except Exception as e:
            Logger.debug(f"❌ 일시정지 상태 저장 실패: {e}")
            import traceback
            traceback.print_exc()

    def load_paused_state(self):
        """일시정지된 상태를 JSON 파일에서 복원"""
        try:
            paused_file_path = os.path.join(result_dir, f"response_results_paused_{self.current_spec_id}.json")

            if not os.path.exists(paused_file_path):
                Logger.debug("[INFO] 일시정지 파일이 존재하지 않습니다.")
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

            Logger.debug(f"✅ 일시정지 상태 복원 완료")
            Logger.debug(f"   타임스탬프: {paused_state.get('timestamp')}")
            Logger.debug(f"   마지막 완료 API 인덱스: {self.last_completed_api_index}")
            Logger.debug(f"   복원된 점수: PASS={self.total_pass_cnt}, FAIL={self.total_error_cnt}")

            return True

        except Exception as e:
            Logger.debug(f"❌ 일시정지 상태 복원 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup_paused_file(self):
        """평가 완료 후 일시정지 파일 삭제 및 상태 초기화"""
        try:
            paused_file_path = os.path.join(result_dir, f"response_results_paused_{self.current_spec_id}.json")
            Logger.debug(f" cleanup_paused_file() 호출됨")
            Logger.debug(f" 파일 경로: {paused_file_path}")
            Logger.debug(f" 파일 존재 여부: {os.path.exists(paused_file_path)}")

            if os.path.exists(paused_file_path):
                os.remove(paused_file_path)
                Logger.debug("✅ 일시정지 중간 파일 삭제 완료")
            else:
                Logger.debug("[CLEANUP] 일시정지 파일이 존재하지 않음 (일시정지하지 않았거나 이미 삭제됨)")

            # 일시정지 상태 초기화
            self.is_paused = False
            self.last_completed_api_index = -1
            self.paused_valResult_text = ""

        except Exception as e:
            Logger.debug(f"❌ 일시정지 파일 정리 실패: {e}")

    def _cleanup_all_paused_files_on_startup(self):
        """프로그램 시작 시 모든 일시정지 파일 삭제"""
        try:
            import glob
            # response_results_paused_*.json 패턴으로 모든 일시정지 파일 찾기
            pattern = os.path.join(result_dir, "response_results_paused_*.json")
            paused_files = glob.glob(pattern)
            
            if paused_files:
                Logger.debug(f" {len(paused_files)}개의 일시정지 파일 발견")
                for file_path in paused_files:
                    try:
                        os.remove(file_path)
                        Logger.debug(f" 삭제 완료: {os.path.basename(file_path)}")
                    except Exception as e:
                        Logger.warn(f" 파일 삭제 실패 {file_path}: {e}")
                Logger.debug(f"✅ 시작 시 일시정지 파일 삭제 완료")
            else:
                Logger.debug("[STARTUP_CLEANUP] 삭제할 일시정지 파일이 없음")
        except Exception as e:
            Logger.debug(f"❌ 시작 시 일시정지 파일 삭제 실패: {e}")

    def cleanup_all_paused_files(self):
        """프로그램 종료 시 모든 일시정지 파일 삭제"""
        try:
            import glob
            # response_results_paused_*.json 패턴으로 모든 일시정지 파일 찾기
            pattern = os.path.join(result_dir, "response_results_paused_*.json")
            paused_files = glob.glob(pattern)
            
            if paused_files:
                Logger.debug(f" {len(paused_files)}개의 일시정지 파일 발견")
                for file_path in paused_files:
                    try:
                        os.remove(file_path)
                        Logger.debug(f" 삭제 완료: {os.path.basename(file_path)}")
                    except Exception as e:
                        Logger.warn(f" 파일 삭제 실패 {file_path}: {e}")
                Logger.debug(f"✅ 모든 일시정지 파일 삭제 완료")
            else:
                Logger.debug("[CLEANUP_ALL] 삭제할 일시정지 파일이 없음")
        except Exception as e:
            Logger.debug(f"❌ 일시정지 파일 일괄 삭제 실패: {e}")

    def stop_btn_clicked(self):
        setattr(CONSTANTS, "SUPPRESS_COMPLETED_HEARTBEAT", True)
        self.is_paused = True
        """평가 중지 버튼 클릭"""
        # 완료 루프와 레이스가 나도 completed가 나가지 않도록 먼저 설정
        self.is_paused = True

        # ✅ 타이머 중지
        if self.tick_timer.isActive():
            self.tick_timer.stop()
            Logger.debug(f" 타이머 중지됨")

        self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">검증 절차가 중지되었습니다.</div>')
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)
        self.cancel_btn.setDisabled(True)
        
        # ✅ 시험 중지 - stopped 상태 heartbeat 전송
        try:
            api_client = APIClient()
            api_client.send_heartbeat_stopped(getattr(self.CONSTANTS, "request_id", ""))
            Logger.info(f"✅ 시험 중지 - in_progress 상태 전송 완료")
        except Exception as e:
            Logger.warning(f"⚠️ 시험 중지 - in_progress 상태 전송 실패: {e}")

        self.save_current_spec_data()

        # ✅ 일시정지 상태 저장
        self.save_paused_state()
        return

        # ✅ JSON 결과 저장 추가
        try:
            self.run_status = "진행중"
            result_json = build_result_json(self)
            url = f"{CONSTANTS.management_url}/api/integration/test-results"
            response = requests.post(url, json=result_json)
            Logger.debug(f"✅ 시험 결과 전송 상태 코드:: {response.status_code}")
            Logger.debug(f"📥  시험 결과 전송 응답:: {response.text}")
            json_path = os.path.join(result_dir, "response_results.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)
            Logger.debug(f"✅ 진행 중 결과가 '{json_path}'에 저장되었습니다.")
            self.append_monitor_log(
                step_name="진행 상황 저장 완료",
                details=f"{json_path} (일시정지 시점까지의 결과가 저장되었습니다)"
            )
        except Exception as e:
            Logger.debug(f"❌ JSON 저장 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            self.valResult.append(f"\n결과 저장 실패: {str(e)}")

    def cancel_btn_clicked(self):
        """시험 취소 버튼 클릭 - 진행 중단, 상태 초기화"""
        Logger.debug(f" 시험 취소 버튼 클릭")
        setattr(CONSTANTS, "SUPPRESS_COMPLETED_HEARTBEAT", True)
        
        # 확인 메시지 표시
        reply = QMessageBox.question(
            self, '시험 취소',
            '현재 진행 중인 시험을 취소하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            Logger.debug(f" 사용자가 취소를 취소함")
            return
        
        Logger.debug(f" ========== 시험 취소 시작 ==========")
        
        # 1. 타이머 중지 및 초기화
        if self.tick_timer.isActive():
            self.tick_timer.stop()
            Logger.debug(f" 타이머 중지됨")
        
        # 2. 일시정지 파일 삭제
        self.cleanup_paused_file()
        Logger.debug(f" 일시정지 파일 삭제 완료")
        
        # 3. 상태 완전 초기화
        self.is_paused = False
        self.last_completed_api_index = -1
        self.paused_valResult_text = ""
        self.cnt = 0
        self.current_retry = 0
        self.post_flag = False  # 웹훅 플래그 초기화
        self.res = None  # 응답 초기화
        self.webhook_flag = False
        Logger.debug(f" 상태 초기화 완료")
        
        # 4. 버튼 상태 초기화
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)
        self.cancel_btn.setDisabled(True)
        
        # ✅ 시험 취소 - stopped 상태 heartbeat 전송
        try:
            api_client = APIClient()
            api_client.send_heartbeat_stopped(getattr(self.CONSTANTS, "request_id", ""))
            Logger.info(f"✅ 시험 취소 - in_progress 상태 전송 완료")
        except Exception as e:
            Logger.warning(f"⚠️ 시험 취소 - in_progress 상태 전송 실패: {e}")
        
        # 5. 모니터링 화면 초기화
        self.valResult.clear()
        self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">시험이 취소되었습니다. 시험 시작 버튼을 눌러 다시 시작하세요.</div>')
        Logger.debug(f" 모니터링 화면 초기화")
        
        # 6. UI 업데이트 처리
        QApplication.processEvents()
        
        Logger.debug(f" ========== 시험 취소 완료 ==========")

    def init_win(self):
            """검증 시작 전 초기화"""
            self.cnt = 0
            self.current_retry = 0
            # 현재 spec의 API 개수에 맞게 버퍼 생성
            api_count = len(self.videoMessages) if self.videoMessages else 0
            Logger.debug(f" 초기화: {api_count}개 API")

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
                # ✅ 기존 위젯 제거 (겹침 방지)
                self.tableWidget.setCellWidget(i, 2, None)
                
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
            Logger.debug(f"전체화면 전환 오류: {e}")

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

            try:
                APIClient().send_heartbeat_pending(getattr(self.CONSTANTS, "request_id", ""))
            except Exception as e:
                Logger.warning(f"⚠️ 종료 시 stopped 상태 전송 실패: {e}")
            QApplication.instance().setProperty("skip_exit_confirm", True)
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

        # ✅ URL 업데이트 (base_url + 시나리오명) - 오염 방지: CONSTANTS에서 직접 읽기
        if hasattr(self, 'spec_config') and hasattr(self, 'url_text_box'):
            test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
            fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
            self.pathUrl = fresh_base_url.rstrip('/') + "/" + test_name
            self.url_text_box.setText(self.pathUrl)
            print(f"[SYSTEM DEBUG] get_setting에서 pathUrl 설정: {self.pathUrl}")

    def closeEvent(self, event):
        """창 닫기 이벤트 - 타이머 정리"""
        # ✅ 타이머 중지
        if hasattr(self, 'tick_timer') and self.tick_timer.isActive():
            APIClient().send_heartbeat_pending(getattr(self.CONSTANTS, "request_id", ""))
            self.tick_timer.stop()

        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    install_gradient_messagebox()
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    fontDB.addApplicationFont(resource_path('assets/fonts/NotoSansKR-Regular.ttf'))
    fontDB.addApplicationFont(resource_path('assets/fonts/NotoSansKR-Medium.ttf'))
    fontDB.addApplicationFont(resource_path('assets/fonts/NotoSansKR-Bold.ttf'))
    app.setFont(QFont('NanumGothic'))
    ex = MyApp(embedded=False)
    sys.exit(app.exec())
