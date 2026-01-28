# 물리보안 통합플랫폼 검증 소프트웨어
# physical security integrated platform validation software

import os
from api.api_server import Server
from api.client import APIClient
from api.server_thread import server_th, json_data
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor, QPixmap
from PyQt5.QtCore import Qt, QSettings, QTimer, QThread, pyqtSignal
import sys
from datetime import datetime
import json
from core.functions import build_result_json
import requests
import config.CONSTANTS as CONSTANTS
from core.json_checker_new import timeout_field_finder
from core.functions import json_check_, resource_path, json_to_data
from ui.splash_screen import LoadingPopup
from ui.detail_dialog import CombinedDetailDialog
from ui.result_page import ResultPageWidget
from ui.gui_utils import CustomDialog
from ui.platform_window import PlatformValidationWindow
from ui.platform_main_ui import PlatformMainUI
import spec.Schema_response as schema_response_module
import warnings
from core.validation_registry import get_validation_rules
from core.utils import remove_api_number_suffix, to_detail_text, redact, clean_trace_directory, format_schema, load_from_trace_file, load_external_constants
from core.logger import Logger

warnings.filterwarnings('ignore')
result_dir = os.path.join(os.getcwd(), "results")
os.makedirs(result_dir, exist_ok=True)


# 시험 결과 페이지 위젯 (result_page.py로 분리됨)


class MyApp(PlatformMainUI):
    # 시험 결과 표시 요청 시그널
    showResultRequested = pyqtSignal(object)

    def __init__(self, embedded=False, mode=None, spec_id=None):
        # CONSTANTS 사용
        super().__init__()
        
        # ✅ 프로그램 시작 시 모든 일시정지 파일 삭제
        self._cleanup_all_paused_files_on_startup()

        self.CONSTANTS = CONSTANTS
        self.current_spec_id = spec_id
        self.current_group_id = None  # ✅ 그룹 ID 저장용

        # ✅ 웹훅 관련 변수 미리 초기화 (load_specs_from_constants 호출 전)
        self.videoWebhookSchema = []
        self.videoWebhookData = []
        self.videoWebhookConstraint = []

        self.load_specs_from_constants()
        self.embedded = embedded
        self.mode = mode
        self.radio_check_flag = "video"
        self.run_status = "진행전"
        self._wrapper_window = None

        # 전체화면 관련 변수 초기화
        self._is_fullscreen = False
        self._saved_geom = None
        self._saved_state = None

        # 로딩 팝업 인스턴스 변수
        self.loading_popup = None

        # 아이콘 경로 (메인 페이지용)
        self.img_pass = resource_path("assets/image/icon/icn_success.png")
        self.img_fail = resource_path("assets/image/icon/icn_fail.png")
        self.img_none = resource_path("assets/image/icon/icn_basic.png")

        self.flag_opt = self.CONSTANTS.flag_opt
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_view)
        self.auth_flag = True
        self.Server = Server
        self.server_th = None  # ✅ 서버 스레드 변수 초기화

        parts = self.auth_info.split(",")
        auth = [parts[0], parts[1] if len(parts) > 1 else ""]
        self.accessInfo = [auth[0], auth[1]]

        # spec_id 초기화
        if spec_id:
            self.current_spec_id = spec_id
            Logger.info(f"전달받은 spec_id 사용: {spec_id}")

        # Load specs dynamically from CONSTANTS

        # ✅ 분야별 점수 (현재 spec만)
        self.current_retry = 0
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.total_opt_pass_cnt = 0  # 선택 필드 통과 수
        self.total_opt_error_cnt = 0  # 선택 필드 에러 수

        # ✅ 전체 점수 (모든 spec 합산)
        self.global_pass_cnt = 0
        self.global_error_cnt = 0
        self.global_opt_pass_cnt = 0  # 전체 선택 필드 통과 수
        self.global_opt_error_cnt = 0  # 전체 선택 필드 에러 수

        # ✅ 각 spec_id별 테이블 데이터 저장 (시나리오 전환 시 결과 유지)
        self.spec_table_data = {}  # {spec_id: {table_data, step_buffers, scores}}

        self.initUI()
        self.realtime_flag = False
        self.cnt = 0
        self.current_retry = 0

        self.time_pre = 0
        self.cnt_pre = 0
        self.final_report = ""

        # ✅ 일시정지 및 재개 관련 변수
        self.is_paused = False
        self.last_completed_api_index = -1
        self.paused_valResult_text = ""

        # step_buffers 동적 생성
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS", "raw_data_list": []} for _ in range(len(self.videoMessages))
        ]

        # ✅ 현재 spec에 맞게 누적 카운트 초기화
        api_count = len(self.videoMessages)
        self.step_pass_counts = [0] * api_count
        self.step_error_counts = [0] * api_count
        self.step_opt_pass_counts = [0] * api_count  # API별 선택 필드 통과 수
        self.step_opt_error_counts = [0] * api_count  # API별 선택 필드 에러 수
        self.step_pass_flags = [0] * api_count

        self.get_setting()
        self.first_run = True

        with open(resource_path("spec/rows.json"), "w") as out_file:
            json.dump(None, out_file, ensure_ascii=False)

        self.reference_context = {}

    def load_specs_from_constants(self):

        SPEC_CONFIG = load_external_constants(self.CONSTANTS)

        self.url = getattr(self.CONSTANTS, 'url', None)
        self.auth_type = getattr(self.CONSTANTS, 'auth_type', None)
        self.auth_info = getattr(self.CONSTANTS, 'auth_info', None)

        self.LOADED_SPEC_CONFIG = SPEC_CONFIG

        if not SPEC_CONFIG:
            raise ValueError("CONSTANTS.SPEC_CONFIG가 정의되지 않았습니다!")

        Logger.debug(f"[PLATFORM DEBUG] SPEC_CONFIG 개수: {len(SPEC_CONFIG)}")
        Logger.debug(f"[PLATFORM DEBUG] 찾을 spec_id: {self.current_spec_id}")

        config = {}
        for group in SPEC_CONFIG:
            if self.current_spec_id in group:
                config = group[self.current_spec_id]
                break

        if not config:
            raise ValueError(f"spec_id '{self.current_spec_id}'에 대한 설정을 찾을 수 없습니다!")

        self.spec_description = config.get('test_name', 'Unknown Test')
        spec_names = config.get('specs', [])

        # trans_protocol, time_out, num_retries 저장
        self.trans_protocols = config.get('trans_protocol', [])
        self.time_outs = config.get('time_out', [])
        self.num_retries_list = config.get('num_retries', [])

        if len(spec_names) < 3:
            raise ValueError(f"spec_id '{self.current_spec_id}'의 specs 설정이 올바르지 않습니다!")
        Logger.debug(f" 📋 Spec 로딩 시작: {self.spec_description} (ID: {self.current_spec_id})")

        # ===== PyInstaller 환경에서 외부 spec 디렉토리 우선 사용 =====
        import sys
        import os
        import importlib

        if getattr(sys, 'frozen', False):
            # PyInstaller 환경: 외부 spec 디렉토리를 sys.path 맨 앞에 추가
            exe_dir = os.path.dirname(sys.executable)
            external_spec_parent = exe_dir  # exe_dir/spec을 찾기 위해 exe_dir을 추가

            # 외부 spec 폴더 파일 존재 확인
            external_spec_dir = os.path.join(external_spec_parent, 'spec')
            Logger.debug(f"외부 spec 폴더: {external_spec_dir}")
            Logger.debug(f"외부 spec 폴더 존재: {os.path.exists(external_spec_dir)}")
            if os.path.exists(external_spec_dir):
                files = [f for f in os.listdir(external_spec_dir) if f.endswith('.py')]
                Logger.debug(f"외부 spec 폴더 .py 파일: {files}")

            # sys.path 전체 출력 (디버깅)
            Logger.debug(f"[PLATFORM SPEC DEBUG] sys.path 전체 개수: {len(sys.path)}")
            for i, p in enumerate(sys.path):
                Logger.debug(f"[PLATFORM SPEC DEBUG]   [{i}] {p}")

            # 이미 있더라도 제거 후 맨 앞에 추가 (우선순위 보장)
            if external_spec_parent in sys.path:
                sys.path.remove(external_spec_parent)
            sys.path.insert(0, external_spec_parent)
            Logger.debug(f"sys.path에 외부 디렉토리 추가: {external_spec_parent}")

        # sys.modules에서 기존 spec 모듈 제거 (캐시 초기화)
        # 주의: 'spec' 패키지 자체는 유지 (parent 패키지 필요)
        modules_to_remove = [
            'spec.Schema_request',
            'spec.Data_response',
            'spec.Constraints_response'
        ]
        for mod_name in modules_to_remove:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
                Logger.debug(f"[PLATFORM SPEC] 모듈 캐시 삭제: {mod_name}")
            else:
                Logger.debug(f"[PLATFORM SPEC] 모듈 캐시 없음: {mod_name}")

        # spec 패키지가 없으면 빈 모듈로 등록
        if 'spec' not in sys.modules:
            import types
            sys.modules['spec'] = types.ModuleType('spec')
            Logger.debug(f"빈 'spec' 패키지 생성")

        # PyInstaller 환경에서는 importlib.util로 명시적으로 외부 파일 로드
        if getattr(sys, 'frozen', False):
            import importlib.util

            # 외부 spec 파일 경로
            schema_file = os.path.join(exe_dir, 'spec', 'Schema_request.py')
            data_file = os.path.join(exe_dir, 'spec', 'Data_response.py')
            constraints_file = os.path.join(exe_dir, 'spec', 'Constraints_response.py')

            Logger.debug(f"명시적 로드 시도:")
            Logger.debug(f"  - Schema: {schema_file} (존재: {os.path.exists(schema_file)})")
            Logger.debug(f"  - Data: {data_file} (존재: {os.path.exists(data_file)})")
            Logger.debug(f"  - Constraints: {constraints_file} (존재: {os.path.exists(constraints_file)})")

            # importlib.util로 명시적 로드
            spec = importlib.util.spec_from_file_location('spec.Schema_request', schema_file)
            schema_request_module = importlib.util.module_from_spec(spec)
            sys.modules['spec.Schema_request'] = schema_request_module
            spec.loader.exec_module(schema_request_module)

            spec = importlib.util.spec_from_file_location('spec.Data_response', data_file)
            data_response_module = importlib.util.module_from_spec(spec)
            sys.modules['spec.Data_response'] = data_response_module
            spec.loader.exec_module(data_response_module)

            spec = importlib.util.spec_from_file_location('spec.Constraints_response', constraints_file)
            constraints_response_module = importlib.util.module_from_spec(spec)
            sys.modules['spec.Constraints_response'] = constraints_response_module
            spec.loader.exec_module(constraints_response_module)

            Logger.debug(f"importlib.util로 외부 파일 로드 완료")
        else:
            # 일반 환경에서는 기존 방식 사용
            import spec.Schema_request as schema_request_module
            import spec.Data_response as data_response_module
            import spec.Constraints_response as constraints_response_module

        # ===== spec 파일 경로 로그 추가 =====
        Logger.debug(f"[PLATFORM SPEC] Schema_request.py 로드 경로: {schema_request_module.__file__}")
        Logger.debug(f"[PLATFORM SPEC] Data_response.py 로드 경로: {data_response_module.__file__}")
        Logger.debug(f"[PLATFORM SPEC] Constraints_response.py 로드 경로: {constraints_response_module.__file__}")

        # 파일 수정 시간 확인
        for module, name in [(schema_request_module, 'Schema_request'),
                              (data_response_module, 'Data_response'),
                              (constraints_response_module, 'Constraints_response')]:
            file_path = module.__file__
            if file_path.endswith('.pyc'):
                file_path = file_path[:-1]  # .pyc -> .py
            if os.path.exists(file_path):
                mtime = os.path.getmtime(file_path)
                from datetime import datetime
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                Logger.debug(f"[PLATFORM SPEC] {name}.py 수정 시간: {mtime_str}")
        # ===== 로그 끝 =====
        Logger.debug(f" 🔧 타입: 요청 검증 + 응답 전송")

        # Request 검증용 데이터 로드
        self.videoInSchema = getattr(schema_request_module, spec_names[0], [])

        # Response 전송용 데이터 로드
        self.videoOutMessage = getattr(data_response_module, spec_names[1], [])
        self.videoMessages = getattr(data_response_module, spec_names[2], [])
        # 표시용 API 이름 (숫자 제거)
        self.videoMessagesDisplay = [remove_api_number_suffix(msg) for msg in self.videoMessages]
        self.videoOutConstraint = getattr(constraints_response_module, self.current_spec_id + "_outConstraints", [])

        # Webhook 관련
        try:
            if len(spec_names) >= 5:
                webhook_schema_name = spec_names[3]
                webhook_data_name = spec_names[4]

                self.videoWebhookSchema = getattr(schema_request_module, webhook_schema_name, [])
                self.videoWebhookData = getattr(data_response_module, webhook_data_name, [])
                self.videoWebhookConstraint = getattr(constraints_response_module,
                                                     self.current_spec_id + "_webhook_inConstraints",
                                                  [])

                Logger.debug(f" 📦 웹훅 스키마 개수: {len(self.videoWebhookSchema)}개 API")
                Logger.debug(f" 📋 웹훅 데이터 개수: {len(self.videoWebhookData)}개")
                Logger.debug(f" 📋 웹훅 constraints 개수: {len(self.videoWebhookConstraint)}개")

                webhook_indices = [i for i, msg in enumerate(self.videoMessages) if "Webhook" in msg]
                if webhook_indices:
                    Logger.debug(f" 🔔 웹훅 API 인덱스: {webhook_indices}")
                else:
                    Logger.debug(f" ⚠️ 웹훅 API가 videoMessages에 없습니다.")
            else:
                Logger.debug(f" ⚠️ 웹훅 스키마 및 데이터가 SPEC_CONFIG에 정의되어 있지 않습니다.")
                self.videoWebhookSchema = []
                self.videoWebhookData = []
                self.videoWebhookConstraint = []
        except Exception as e:
            Logger.debug(f" ⚠️ 웹훅 스키마 및 데이터 로드 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            self.videoWebhookSchema = []
            self.videoWebhookData = []
            self.videoWebhookConstraint = []

        Logger.debug(f" ✅ 로딩 완료: {len(self.videoMessages)}개 API")
        Logger.debug(f" 📋 API 목록: {self.videoMessages}")
        Logger.debug(f" 🔄 프로토콜 설정: {self.trans_protocols}")

        # ✅ spec_config 저장 (URL 생성에 필요)
        self.spec_config = config

    def _push_event(self, api_name, direction, payload):
        """direction: 'REQUEST'|'RESPONSE'|'WEBHOOK'"""
        try:
            if not hasattr(self.Server, "trace") or self.Server.trace is None:
                from collections import defaultdict, deque
                self.Server.trace = defaultdict(lambda: deque(maxlen=500))
            if api_name not in self.Server.trace:
                from collections import deque
                self.Server.trace[api_name] = deque(maxlen=500)
            evt = {
                "time": datetime.utcnow().isoformat() + "Z",
                "api": api_name,
                "dir": direction,
                "data": redact(payload),
            }
            self.Server.trace[api_name].append(evt)
        except Exception:
            pass



    def update_view(self):
        try:
            time_interval = 0

            if self.cnt >= len(self.Server.message):
                Logger.debug(f" 모든 API 처리 완료, 타이머 정지")
                self.tick_timer.stop()

                # ✅ 현재 spec 데이터 저장
                self.save_current_spec_data()

                self.sbtn.setEnabled(True)
                self.stop_btn.setDisabled(True)
                self.cancel_btn.setDisabled(True)

                # ✅ 완료 메시지 추가
                self.valResult.append("\n" + "=" * 50)
                self.valResult.append("모든 API 검증이 완료되었습니다!")
                self.valResult.append("=" * 50)

                # ✅ 자동 저장
                Logger.debug(f" 평가 완료 - 자동 저장 시작")
                try:
                    self.run_status = "완료"
                    result_json = build_result_json(self)
                    url = f"{CONSTANTS.management_url}/api/integration/test-results"
                    response = requests.post(url, json=result_json)
                    Logger.debug(f"✅ 시험 결과 전송 상태 코드:: {response.status_code}")
                    Logger.debug(f"📥  시험 결과 전송 응답:: {response.text}")

                    json_path = os.path.join(result_dir, "request_results.json")
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
                    
                    # ✅ 시험 완료 - idle 상태 heartbeat 전송
                    try:
                        api_client = APIClient()
                        api_client.send_heartbeat_idle()
                        Logger.info(f"✅ 시험 완료 - idle 상태 전송 완료")
                    except Exception as e:
                        Logger.warning(f"⚠️ 시험 완료 - idle 상태 전송 실패: {e}")

                return

            # 첫 틱에서는 대기만
            if self.time_pre == 0 or self.cnt != self.cnt_pre:
                Logger.debug(f" 첫 틱 대기: time_pre={self.time_pre}, cnt={self.cnt}, cnt_pre={self.cnt_pre}")
                self.time_pre = time.time()
                self.cnt_pre = self.cnt
                self.step_start_log_printed = False # ✅ 단계 변경 시 플래그 리셋
                return
            else:
                time_interval = time.time() - self.time_pre
                Logger.debug(f" 시간 간격: {time_interval}초")

            if self.realtime_flag is True:
                Logger.debug(f"[json_check] do_checker 호출")

            # SPEC_CONFIG에서 timeout
            current_timeout = (self.time_outs[self.cnt] / 1000) if self.cnt < len(self.time_outs) else 5.0

            # timeout이 0인 경우
            if current_timeout == 0 or time_interval < current_timeout:
                # 시스템 요청 확인
                api_name = self.Server.message[self.cnt]
                
                # ✅ 대기 시작 시 로그 먼저 출력 (최초 1회)
                if not self.step_start_log_printed:
                    current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                    display_name = self.Server.message_display[self.cnt] if self.cnt < len(self.Server.message_display) else "Unknown"
                    self.append_monitor_log(
                        step_name=f"시험 API: {display_name} (시도 {self.current_retry + 1}/{current_retries})",
                        details="시스템 요청 대기 중...",
                        is_temp=True
                    )
                    self.step_start_log_printed = True

                Logger.debug(f" API 처리 시작: {api_name}")

                current_validation = {}

                Logger.debug("++++++++++ 규칙 가져오기 ++++++++++")

                try:
                    current_validation = get_validation_rules(
                        spec_id=self.current_spec_id,
                        api_name=api_name,
                        direction="in",
                    ) or {}
                    if current_validation:
                        Logger.debug(f" 현재 API의 검증 규칙 로드 완료: {list(current_validation.keys())}")
                except Exception as e:
                    current_validation = {}
                    Logger.debug(f" 현재 API의 검증 규칙 로드 실패: {e}")

                Logger.debug("++++++++++ 규칙 로드 끝 ++++++++++")

                request_received = False
                expected_count = self.current_retry + 1
                actual_count = 0

                # Server 클래스 변수 request_counter 확인
                if hasattr(self.Server, 'request_counter') and api_name in self.Server.request_counter:
                    actual_count = self.Server.request_counter[api_name]
                    Logger.debug(f" API: {api_name}, 예상: {expected_count}, 실제: {actual_count}")
                    if actual_count >= expected_count:
                        request_received = True

                # 요청이 도착하지 않았으면 대기
                if not request_received:
                    # ✅ 대기 시간 타이머 표시 (마지막 줄 갱신)
                    remaining = max(0, int(current_timeout - time_interval))
                    self.update_last_line_timer(f"남은 대기 시간: {remaining}초")

                    if self.current_retry == 0:
                        Logger.debug(f"능동 대기(WAIT): 시스템 요청 대기 중 (API: {api_name}, 예상: {expected_count}회, 실제: {actual_count}회)")
                    return
                
                # ✅ 요청 수신 완료 - 타이머 라인 제거
                self.update_last_line_timer("", remove=True)

                request_arrival_time = time.time()
                expected_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                Logger.debug(f" ✅ 요청 도착 감지! API: {api_name}, 시도: {self.current_retry + 1}/{expected_retries}")

                display_name = self.Server.message_display[self.cnt] if self.cnt < len(self.Server.message_display) else "Unknown"
                message_name = "시험 API: " + display_name

                # SPEC_CONFIG에서 검증 설정 가져오기
                current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                current_protocol = self.trans_protocols[self.cnt] if self.cnt < len(self.trans_protocols) else "basic"

                # API별 누적 데이터 초기화
                if not hasattr(self, 'api_accumulated_data'):
                    self.api_accumulated_data = {}

                api_index = self.cnt
                if self.current_retry == 0 or api_index not in self.api_accumulated_data:
                    self.api_accumulated_data[api_index] = {
                        'data_parts': [],
                        'error_messages': [],
                        'validation_results': [],
                        'total_pass': 0,
                        'total_error': 0,
                        'total_opt_pass': 0,  # 선택 필드 통과 수
                        'total_opt_error': 0,  # 선택 필드 에러 수
                        'raw_data_list': []
                    }

                accumulated = self.api_accumulated_data[api_index]

                retry_attempt = self.current_retry

                combined_error_parts = []
                step_result = "PASS"
                add_pass = 0
                add_err = 0
                add_opt_pass = 0  # 선택 필드 통과 수
                add_opt_error = 0  # 선택 필드 에러 수

                # 실시간 진행률 표시
                if retry_attempt == 0:
                    self.append_monitor_log(
                        step_name=message_name,
                        details=f"총 {current_retries}회 검증 예정"
                    )

                api_name = self.Server.message[self.cnt]
                Logger.debug(f"시스템 요청 수신: {api_name} (시도 {retry_attempt + 1}/{current_retries})")


                # 테이블에 실시간 진행률 표시
                self.update_table_row_with_retries(self.cnt, "진행중", 0, 0, "검증 진행중...",
                                                   f"시도 {retry_attempt + 1}/{current_retries}", retry_attempt + 1)

                QApplication.processEvents()

                current_data = load_from_trace_file(api_name, "REQUEST") or {}

                if not current_data:
                    Logger.debug(f" ⚠️ trace 파일에서 요청 데이터를 불러오지 못했습니다!")
                    Logger.debug(f" API 이름: {api_name}")
                    Logger.debug(f" Direction: REQUEST")
                else:
                    Logger.debug(f" ✅ trace 파일에서 요청 데이터 로드 완료: {len(str(current_data))} bytes")

                # 1-1. response 데이터 로드
                response_data = load_from_trace_file(api_name, "RESPONSE") or {}

                if not response_data:
                    Logger.debug(f" ⚠️ trace 파일에서 응답 데이터를 불러오지 못했습니다!")
                    Logger.debug(f" API 이름: {api_name}")
                    Logger.debug(f" Direction: RESPONSE")
                else:
                    Logger.debug(f" ✅ trace 파일에서 응답 데이터 로드 완료: {len(str(response_data))} bytes")

                # 2. 맥락 검증용
                if current_validation:

                    for field_path, validation_rule in current_validation.items():
                        validation_type = validation_rule.get("validationType", "")
                        direction = "REQUEST" if "request-field" in validation_type else "RESPONSE"

                        ref_endpoint = validation_rule.get("referenceEndpoint", "")
                        if ref_endpoint:
                            ref_api_name = ref_endpoint.lstrip("/")
                            ref_data = load_from_trace_file(ref_api_name, direction)
                            if ref_data and isinstance(ref_data, dict):
                                self.reference_context[ref_endpoint] = ref_data
                                Logger.debug(f" {ref_endpoint} {direction}를 trace 파일에서 로드 (from validation rule)")

                        ref_endpoint_max = validation_rule.get("referenceEndpointMax", "")
                        if ref_endpoint_max:
                            ref_api_name_max = ref_endpoint_max.lstrip("/")
                            ref_data_max = load_from_trace_file(ref_api_name_max, direction)
                            if ref_data_max and isinstance(ref_data_max, dict):
                                self.reference_context[ref_endpoint_max] = ref_data_max
                                Logger.debug(f" {ref_endpoint_max} {direction}를 trace 파일에서 로드 (from validation rule)")

                        ref_endpoint_min = validation_rule.get("referenceEndpointMin", "")
                        if ref_endpoint_min:
                            ref_api_name_min = ref_endpoint_min.lstrip("/")
                            ref_data_min = load_from_trace_file(ref_api_name_min, direction)
                            if ref_data_min and isinstance(ref_data_min, dict):
                                self.reference_context[ref_endpoint_min] = ref_data_min
                                Logger.debug(f" {ref_endpoint_min} {direction}를 trace 파일에서 로드 (from validation rule)")

                if self.Server.message[self.cnt] in CONSTANTS.none_request_message:
                    # 매 시도마다 데이터 수집
                    from core.utils import replace_transport_desc_for_display
                    tmp_res_auth = json.dumps(current_data, indent=4, ensure_ascii=False)
                    tmp_res_auth = replace_transport_desc_for_display(tmp_res_auth)  # UI 표시용 치환

                    if retry_attempt == 0:
                        accumulated['data_parts'].append(f"{tmp_res_auth}")
                    else:
                        accumulated['data_parts'].append(f"\n{tmp_res_auth}")

                    # 실시간 모니터링 창에 요청 데이터 표시 (API 이름 중복 없이 데이터만)
                    # if retry_attempt == 0:
                    #     self.append_monitor_log(
                    #         step_name="",
                    #         request_json=tmp_res_auth
                    #     )

                    accumulated['raw_data_list'].append(current_data)

                    if (len(current_data) != 0) and current_data != "{}":
                        step_result = "FAIL"
                        add_err = 1
                        # 통일된 포맷으로 변경
                        error_msg = f"[시도 {retry_attempt + 1}/{current_retries}]\n[맥락 오류] Request Body 값 오류\n- 입력값: {json.dumps(current_data, ensure_ascii=False)}\n- 예상값: Empty"
                        combined_error_parts.append(error_msg)
                    elif (len(current_data) == 0) or current_data == "{}":
                        step_result = "PASS"
                        add_pass = 1

                else:
                    # 매 시도마다 입력 데이터 수집
                    from core.utils import replace_transport_desc_for_display
                    tmp_res_auth = json.dumps(current_data, indent=4, ensure_ascii=False)
                    tmp_res_auth = replace_transport_desc_for_display(tmp_res_auth)  # UI 표시용 치환

                    if retry_attempt == 0:
                        accumulated['data_parts'].append(f"{tmp_res_auth}")
                    else:
                        accumulated['data_parts'].append(f"\n{tmp_res_auth}")

                    # ✅ 실시간 모니터링 출력
                    if retry_attempt == 0:
                        self.append_monitor_log(
                            step_name=f"시험 API: {self.Server.message[self.cnt]} (시도 {retry_attempt + 1}/{current_retries})",
                            request_json=tmp_res_auth,
                            details=f"총 {current_retries}회 검증 예정"
                        )
                    else:
                        self.append_monitor_log(
                            step_name=f"시험 API (시도 {retry_attempt + 1}/{current_retries})",
                            request_json=tmp_res_auth
                        )

                    accumulated['raw_data_list'].append(current_data)

                    if "DoorControl" in api_name:
                        # 1. 검증 규칙 강제 수정 (혹시 doorList.doorID로 되어있다면 다시 doorID로 원복)
                        if "doorID" in current_validation:
                            current_validation["doorID"]["referenceField"] = "doorID"
                            Logger.debug(f" 규칙 강제 설정: referenceField = 'doorID'")

                        # 2. 데이터 강제 평탄화 (Flattening)
                        target_key = "/RealtimeDoorStatus"

                        ref_data = self.reference_context.get(target_key, {})
                        
                        # 데이터가 없으면 Trace 파일에서 비상 로드
                        if "doorList" not in ref_data or not ref_data.get("doorList"):
                            try:
                                webhook_data = load_from_trace_file("RealtimeDoorStatus", "WEBHOOK_OUT")
                                if webhook_data and "doorList" in webhook_data:
                                    ref_data = webhook_data
                                    Logger.debug(f" reference_context에 RealtimeDoorStatus 데이터가 없어 WEBHOOK에서 로드함")
                            except:
                                pass
                        
                        if "doorList" not in ref_data or not ref_data.get("doorList"):
                            try:
                                response_data = load_from_trace_file("RealtimeDoorStatus", "REQUEST")
                                if response_data and "doorList" in response_data:
                                    ref_data = response_data
                                    Logger.debug(f" reference_context에 RealtimeDoorStatus 데이터가 없어 REQUEST에서 로드함")
                            except:
                                pass
                        
                        extracted_ids = []
                        if "doorList" in ref_data and isinstance(ref_data["doorList"], list):
                            for item in ref_data["doorList"]:
                                if isinstance(item, dict):
                                    val = item.get("doorID") or item.get("doorId")
                                    if val: extracted_ids.append(val)

                        if extracted_ids:
                            ref_data["doorID"] = extracted_ids

                            self.reference_context[target_key] = ref_data
                            Logger.debug(f" 데이터 평탄화 성공: {extracted_ids}")

                        else:
                            Logger.debug(f" 경고: doorList는 있지만 내부에 doorID가 없습니다.")                       
                        
                                
                    try:
                        Logger.debug(f" json_check_ 호출 시작")

                        val_result, val_text, key_psss_cnt, key_error_cnt, opt_correct, opt_error = json_check_(
                            self.videoInSchema[self.cnt],
                            current_data,
                            self.flag_opt,
                            validation_rules=current_validation,
                            reference_context=self.reference_context
                        )

                        Logger.debug(f"json_check_ 성공: result={val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
                    except TypeError as e:
                        Logger.debug(f" TypeError 발생, 맥락 검증 제외 하고 다시 시도: {e}")
                        val_result, val_text, key_psss_cnt, key_error_cnt, opt_correct, opt_error = json_check_(
                            self.videoInSchema[self.cnt],
                            current_data,
                            self.flag_opt
                        )

                    except Exception as e:
                        Logger.debug(f" json_check_ 기타 에러: {e}")
                        import traceback
                        traceback.print_exc()
                        raise

                    # ✅ 의미 검증: code_value 확인
                    if isinstance(current_data, dict):
                        response_code = str(current_data.get("code", "")).strip()
                        response_message = current_data.get("message", "")
                        code_value = current_data.get("code_value", 200)
                        
                        # code_value 읽은 후 제거 (저장/UI에 포함 안 됨)
                        if "code_value" in current_data:
                            del current_data["code_value"]
                            Logger.debug(f" code_value={code_value} 읽고 제거 완료")
                        
                        Logger.debug(f" response_code={response_code}, code_value={code_value}")

                        # 케이스 1: code_value=400이고 response_code가 200인 경우
                        # → 잘못된 요청인데 200으로 응답 → 모든 필드 FAIL
                        if code_value == 400 and response_code in ["200", "성공", "Success", ""]:
                            Logger.debug(f" 잘못된 요청인데 200 응답: code_value={code_value}, response_code={response_code}")
                            Logger.debug(f" 모든 필드 FAIL 처리")
                            
                            total_schema_fields = key_psss_cnt + key_error_cnt
                            key_psss_cnt = 0
                            key_error_cnt = total_schema_fields
                            val_result = "FAIL"
                            val_text = f"잘못된 요청 (code_value=400): 모든 필드 자동 FAIL 처리됨"
                            
                            Logger.debug(f" 잘못된 요청 처리 완료: 전체 {total_schema_fields}개 필드 FAIL")
                        
                        # 케이스 2: code_value=400이고 response_code도 400/201/404인 경우
                        # → 의도적 오류 요청, 올바르게 에러 응답 → 모든 필드 PASS
                        elif code_value == 400 and response_code in ["400", "201", "404"]:
                            Logger.debug(f" 에러 응답 감지: code={response_code}, message={response_message}")
                            Logger.debug(f" 동적으로 스키마 필드 자동 PASS 처리 시작")
                            
                            total_schema_fields = key_psss_cnt + key_error_cnt
                            key_psss_cnt = total_schema_fields
                            key_error_cnt = 0
                            val_result = "PASS"
                            val_text = f"에러 응답 (code={response_code}): 모든 필드 자동 PASS 처리됨"
                            
                            Logger.debug(f" 에러 응답 처리 완료: 전체 {total_schema_fields}개 필드 PASS")

                    add_pass += key_psss_cnt
                    add_err += key_error_cnt
                    add_opt_pass += opt_correct  # 선택 필드 통과 수 누적
                    add_opt_error += opt_error  # 선택 필드 에러 수 누적

                    inbound_err_txt = to_detail_text(val_text)
                    if val_result == "FAIL":
                        step_result = "FAIL"
                        combined_error_parts.append(f"[시도 {retry_attempt + 1}/{current_retries}]\n" + inbound_err_txt)

                    # WebHook 프로토콜인 경우
                    if current_protocol == "WebHook":

                        # 웹훅 스레드가 생성될 때까지 짧게 대기 
                        wait_count = 0
                        while wait_count < 10:
                            if hasattr(self.Server, 'webhook_thread') and self.Server.webhook_thread:
                                break
                            time.sleep(0.1)
                            wait_count += 1

                        # 웹훅 스레드 완료 대기
                        if hasattr(self.Server, 'webhook_thread') and self.Server.webhook_thread:
                            self.Server.webhook_thread.join(timeout=5)

                        # 실제 웹훅 응답 사용
                        # ✅ 웹훅 응답이 null인 경우에도 검증을 수행하여 실패로 카운트
                        if hasattr(self.Server, 'webhook_response'):
                            # webhook_response가 None이거나 빈 값인 경우 빈 딕셔너리로 처리
                            webhook_response = self.Server.webhook_response if self.Server.webhook_response else {}
                            
                            if webhook_response:
                                from core.utils import replace_transport_desc_for_display
                                tmp_webhook_response = json.dumps(webhook_response, indent=4, ensure_ascii=False)
                                tmp_webhook_response = replace_transport_desc_for_display(tmp_webhook_response)  # UI 표시용 치환
                                accumulated['data_parts'].append(
                                    f"\n--- Webhook 응답 (시도 {retry_attempt + 1}회차) ---\n{tmp_webhook_response}")
                            else:
                                accumulated['data_parts'].append(f"\n--- Webhook 응답 (시도 {retry_attempt + 1}회차) ---\nnull")
                            
                            if self.cnt < len(self.step_buffers):
                                self.step_buffers[self.cnt]["is_webhook_api"] = True
                            
                            # 웹훅 응답 검증 (null인 경우에도 검증 수행)
                            webhook_resp_val_result, webhook_resp_val_text, webhook_resp_key_psss_cnt, webhook_resp_key_error_cnt, opt_correct, opt_error = json_check_(
                                self.videoWebhookSchema[self.cnt], webhook_response, self.flag_opt
                            )

                            add_pass += webhook_resp_key_psss_cnt
                            add_err += webhook_resp_key_error_cnt
                            add_opt_pass += opt_correct  # 웹훅 선택 필드 통과 수 누적
                            add_opt_error += opt_error  # 웹훅 선택 필드 에러 수 누적

                            webhook_resp_err_txt = to_detail_text(webhook_resp_val_text)
                            if webhook_resp_val_result == "FAIL":
                                step_result = "FAIL"
                                combined_error_parts.append(f"\n--- Webhook 검증 ---\n" + webhook_resp_err_txt)

                            # webhook_response가 None이 아닌 경우에만 reference_context에 저장
                            if webhook_response:
                                webhook_context_key = f"/{api_name}"
                                self.reference_context[webhook_context_key] = webhook_response
                                Logger.debug(f" webhook 응답을 reference_context에 저장: {webhook_context_key}")
                        else:
                            # webhook_response 속성이 없는 경우 (초기화되지 않은 경우)
                            accumulated['data_parts'].append(f"\n--- Webhook 응답 ---\nnull")
                            # 웹훅 스키마가 있는 경우 빈 딕셔너리로 검증 수행
                            webhook_response = {}
                            webhook_resp_val_result, webhook_resp_val_text, webhook_resp_key_psss_cnt, webhook_resp_key_error_cnt, opt_correct, opt_error = json_check_(
                                self.videoWebhookSchema[self.cnt], webhook_response, self.flag_opt
                            )

                            add_pass += webhook_resp_key_psss_cnt
                            add_err += webhook_resp_key_error_cnt
                            add_opt_pass += opt_correct  # 웹훅 선택 필드 통과 수 누적
                            add_opt_error += opt_error  # 웹훅 선택 필드 에러 수 누적

                            webhook_resp_err_txt = to_detail_text(webhook_resp_val_text)
                            if webhook_resp_val_result == "FAIL":
                                step_result = "FAIL"
                                combined_error_parts.append(f"\n--- Webhook 검증 ---\n" + webhook_resp_err_txt)


                    # LongPolling 프로토콜인 경우
                    elif current_protocol == "LongPolling":
                        if retry_attempt == 0:
                            Logger.debug(f"[LongPolling] 실시간 데이터 수신 대기 중... (API: {api_name})")
                        pass

                # 이번 회차 결과를 누적 데이터에 저장
                accumulated['validation_results'].append(step_result)
                accumulated['error_messages'].extend(combined_error_parts)
                # ✅ 필드 수는 마지막 시도로 덮어쓰기 (누적 X)
                accumulated['total_pass'] = add_pass
                accumulated['total_error'] = add_err
                accumulated['total_opt_pass'] = add_opt_pass  # 선택 필드 통과 수 저장
                accumulated['total_opt_error'] = add_opt_error  # 선택 필드 에러 수 저장

                # ✅ 매 시도마다 테이블 실시간 업데이트 (시스템과 동일)
                self.update_table_row_with_retries(
                    self.cnt, 
                    "진행중" if self.current_retry + 1 < current_retries else step_result,
                    accumulated['total_pass'],
                    accumulated['total_error'],
                    tmp_res_auth if 'tmp_res_auth' in locals() else "검증 진행중...",
                    f"시도 {self.current_retry + 1}/{current_retries}",
                    self.current_retry + 1
                )
                QApplication.processEvents()

                # 플랫폼은 응답 메시지 표시 안 함 (요청만 표시)
                # self.valResult.append(f"\n📤 응답 메시지 송신 [{retry_attempt + 1}/{current_retries}]")
                # if 'tmp_response' in locals():
                #     self.valResult.append(tmp_response)

                # current_retry 증가
                self.current_retry += 1

                # 모든 재시도 완료 여부 확인
                if self.current_retry >= current_retries:
                    # 최종 결과
                    final_result = "FAIL" if "FAIL" in accumulated['validation_results'] else "PASS"

                    # ✅ step_pass_counts 배열에 저장 (배열이 없으면 생성)
                    api_count = len(self.videoMessages)
                    if not hasattr(self, 'step_pass_counts') or len(self.step_pass_counts) != api_count:
                        self.step_pass_counts = [0] * api_count
                        self.step_error_counts = [0] * api_count
                        self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수 배열
                        self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수 배열

                    # 이번 API의 결과 저장
                    self.step_pass_counts[self.cnt] = accumulated['total_pass']
                    self.step_error_counts[self.cnt] = accumulated['total_error']
                    self.step_opt_pass_counts[self.cnt] = accumulated['total_opt_pass']  # 선택 필드 통과 수
                    self.step_opt_error_counts[self.cnt] = accumulated['total_opt_error']  # 선택 필드 에러 수

                    # 스텝 버퍼 저장
                    data_text = "\n".join(accumulated['data_parts']) if accumulated[
                        'data_parts'] else "아직 수신된 데이터가 없습니다."
                    error_text = "\n".join(accumulated['error_messages']) if accumulated[
                        'error_messages'] else "오류가 없습니다."
                    self.step_buffers[self.cnt]["data"] = data_text
                    self.step_buffers[self.cnt]["error"] = error_text
                    self.step_buffers[self.cnt]["result"] = final_result
                    self.step_buffers[self.cnt]["raw_data_list"] = accumulated['raw_data_list']
                    try:
                        api_name = self.Server.message[self.cnt]
                        events = list(self.Server.trace.get(api_name, []))
                        self.step_buffers[self.cnt]["events"] = events
                    except Exception:
                        self.step_buffers[self.cnt]["events"] = []

                    # 아이콘/툴팁 갱신
                    if accumulated['data_parts']:
                        tmp_res_auth = accumulated['data_parts'][0]
                    else:
                        tmp_res_auth = "No data"

                    # 테이블 업데이트
                    self.update_table_row_with_retries(self.cnt, final_result, accumulated['total_pass'],
                                                       accumulated['total_error'], tmp_res_auth, error_text,
                                                       current_retries)

                    # ✅ 전체 누적 점수 업데이트 (모든 spec) - API당 1회만 추가
                    self.global_error_cnt += accumulated['total_error']
                    self.global_pass_cnt += accumulated['total_pass']
                    self.global_opt_pass_cnt += accumulated['total_opt_pass']  # 선택 필드 통과 수
                    self.global_opt_error_cnt += accumulated['total_opt_error']  # 선택 필드 에러 수

                    self.update_score_display()

                    # ✅ 점수 계산은 현재 API만의 통과/에러 수로 계산
                    current_api_total = accumulated['total_pass'] + accumulated['total_error']
                    if current_api_total > 0:
                        score_value = (accumulated['total_pass'] / current_api_total * 100)
                    else:
                        score_value = 0

                    # 모니터링 창에 최종 결과 표시 (HTML 카드 형식)
                    api_name = self.Server.message[self.cnt] if self.cnt < len(self.Server.message) else "Unknown"
                    display_name = self.Server.message_display[self.cnt] if self.cnt < len(self.Server.message_display) else "Unknown"
                    
                    # 최종 결과는 데이터 없이 점수와 상태만 표시 (데이터는 이미 실시간으로 출력됨)
                    self.append_monitor_log(
                        step_name=f"시험 API 결과: {display_name} ({current_retries}회 검증 완료)",
                        request_json="",  # 데이터는 이미 출력되었으므로 빈 문자열
                        result_status=final_result,
                        score=score_value,
                        details=f"통과 필드 수: {self.total_pass_cnt}, 실패 필드 수: {self.total_error_cnt} | {'일반 메시지' if current_protocol.lower() == 'basic' else f'실시간 메시지: {current_protocol}'}"
                    )

                    self.cnt += 1
                    self.current_retry = 0

                    if CONSTANTS.enable_retry_delay:
                        Logger.debug(f"수동 지연(SLEEP): API 완료 후 2초 대기 추가")
                        self.time_pre = time.time()
                    else:
                        Logger.debug(f"수동 지연 비활성화: API 완료, 다음 시스템 요청 대기")
                        self.time_pre = time.time()
                else:
                    # 재시도인 경우
                    if CONSTANTS.enable_retry_delay:
                        Logger.debug(f"수동 지연(SLEEP): 재시도 후 2초 대기 추가")
                        self.time_pre = time.time()
                    else:
                        Logger.debug(f"수동 지연 비활성화: 재시도 완료, 다음 시스템 요청 대기")
                        self.time_pre = time.time()

                self.realtime_flag = False

            elif time_interval > current_timeout and self.cnt == self.cnt_pre:
                display_name = self.Server.message_display[self.cnt] if self.cnt < len(self.Server.message_display) else "Unknown"
                message_name = "step " + str(self.cnt + 1) + ": " + display_name

                # message missing인 경우 버퍼 업데이트
                self.step_buffers[self.cnt]["data"] = "아직 수신된 데이터가 없습니다."
                self.step_buffers[self.cnt]["error"] = "메시지 미수신"
                self.step_buffers[self.cnt]["result"] = "FAIL"

                tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(self.Server.inSchema[self.cnt])

                # ✅ 웹훅 API인 경우 웹훅 스키마 필드 수도 추가
                current_protocol = self.trans_protocols[self.cnt] if self.cnt < len(self.trans_protocols) else "basic"
                if current_protocol == "WebHook" :
                    webhook_rqd_cnt, webhook_opt_cnt = timeout_field_finder(self.videoWebhookSchema[self.cnt])
                    tmp_fields_rqd_cnt += webhook_rqd_cnt
                    tmp_fields_opt_cnt += webhook_opt_cnt
                    Logger.debug(f" 웹훅 필드 수 추가: 필수={webhook_rqd_cnt}, 선택={webhook_opt_cnt}")
                    # 웹훅 API임을 step_buffers에 표시
                    self.step_buffers[self.cnt]["is_webhook_api"] = True

                self.total_error_cnt += tmp_fields_rqd_cnt
                if tmp_fields_rqd_cnt == 0:
                    self.total_error_cnt += 1
                if self.flag_opt:
                    self.total_error_cnt += tmp_fields_opt_cnt

                self.total_pass_cnt += 0

                # ✅ 전체 점수에도 반영
                self.global_error_cnt += tmp_fields_rqd_cnt
                if tmp_fields_rqd_cnt == 0:
                    self.global_error_cnt += 1
                if self.flag_opt:
                    self.global_error_cnt += tmp_fields_opt_cnt

                # ✅ step_error_counts 배열에도 저장 (타임아웃 경우)
                api_count = len(self.videoMessages)
                if not hasattr(self, 'step_error_counts') or len(self.step_error_counts) != api_count:
                    self.step_error_counts = [0] * api_count
                    self.step_pass_counts = [0] * api_count
                    self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
                    self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수

                # 이미 계산된 값을 배열에 저장
                step_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                opt_err = tmp_fields_opt_cnt if self.flag_opt else 0  # 타임아웃 시 선택 필드 에러
                if self.flag_opt:
                    step_err += tmp_fields_opt_cnt

                self.step_error_counts[self.cnt] = step_err
                self.step_pass_counts[self.cnt] = 0
                self.step_opt_pass_counts[self.cnt] = 0  # 타임아웃 시 선택 필드 통과 0
                self.step_opt_error_counts[self.cnt] = opt_err  # 타임아웃 시 선택 필드 에러

                # 평가 점수 디스플레이 업데이트
                self.update_score_display()

                total_fields = self.total_pass_cnt + self.total_error_cnt
                if total_fields > 0:
                    score_value = (self.total_pass_cnt / total_fields * 100)
                else:
                    score_value = 0

                # 타임아웃 결과를 HTML 카드로 출력
                api_name = self.Server.message[self.cnt] if self.cnt < len(self.Server.message) else "Unknown"
                self.append_monitor_log(
                    step_name=f"시험 API: {api_name}",
                    request_json="",
                    score=score_value,
                    details=f"⏱️ 메시지 수신 타임아웃({current_timeout}초) -> 메시지 미수신 | 통과 필드 수: {self.total_pass_cnt}, 실패 필드 수: {self.total_error_cnt}"
                )

                # 테이블 업데이트 (Message Missing)
                add_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                if self.flag_opt:
                    add_err += tmp_fields_opt_cnt

                current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                self.update_table_row_with_retries(self.cnt, "FAIL", 0, add_err, "", "메시지 미수신",
                                                   current_retries)

                self.cnt += 1
                self.current_retry = 0
                self.time_pre = time.time()

                if hasattr(self.Server, 'request_counter'):
                    try:
                        del self.Server.request_counter[self.Server.message[self.cnt - 1]]
                    except Exception:
                        pass
                return

            if self.cnt == len(self.Server.message):
                self.tick_timer.stop()
                self.append_monitor_log(
                    step_name="시험 완료",
                    request_json="",
                    details="시험이 완료되었습니다."
                )
                self.cnt = 0

                total_fields = self.total_pass_cnt + self.total_error_cnt
                if total_fields > 0:
                    final_score = (self.total_pass_cnt / total_fields * 100)
                else:
                    final_score = 0

                self.final_report += "전체 점수: " + str(final_score) + "\n"
                self.final_report += "전체 결과: " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                    self.total_error_cnt) + "(누적 오류 필드 수)" + "\n"
                self.final_report += "\n"
                self.final_report += "메시지 검증 세부 결과 \n"
                self.final_report += self.valResult.toPlainText()
                self.sbtn.setEnabled(True)
                self.stop_btn.setDisabled(True)
                self.cancel_btn.setDisabled(True)

                # ✅ 현재 spec 데이터 저장
                self.save_current_spec_data()

                # ✅ 자동 저장
                Logger.debug(f" 평가 완료 - 자동 저장 시작 (경로2)")
                try:
                    self.run_status = "완료"
                    result_json = build_result_json(self)
                    url = f"{CONSTANTS.management_url}/api/integration/test-results"
                    response = requests.post(url, json=result_json)
                    Logger.debug(f"✅ 시험 결과 전송 상태 코드:: {response.status_code}")
                    Logger.debug(f"📥  시험 결과 전송 응답:: {response.text}")

                    json_path = os.path.join(result_dir, "request_results.json")
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
                    
                    # ✅ 시험 완료 - idle 상태 heartbeat 전송 (경로2)
                    try:
                        api_client = APIClient()
                        api_client.send_heartbeat_idle()
                        Logger.info(f"✅ 시험 완료 (경로2) - idle 상태 전송 완료")
                    except Exception as e:
                        Logger.warning(f"⚠️ 시험 완료 (경로2) - idle 상태 전송 실패: {e}")

        except Exception as err:
            Logger.error(f" update_view에서 예외 발생: {err}")
            import traceback
            traceback.print_exc()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error Message: 오류 확인 후 검증 절차를 다시 시작해주세요")
            msg.setInformativeText(str(err))
            msg.setWindowTitle("Error")
            msg.exec_()
            self.tick_timer.stop()
            self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">검증 절차가 중지되었습니다.</div>')
            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)
            self.cancel_btn.setDisabled(True)

    def load_test_info_from_constants(self):
        """CONSTANTS.py에서 시험정보를 로드"""
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
            self.test_selection_panel.update_test_field_table(selected_group)

    def save_current_spec_data(self):
        """현재 spec의 테이블 데이터와 상태를 저장"""
        if not hasattr(self, 'current_spec_id'):
            return

        # 테이블 데이터 저장
        table_data = []
        for row in range(self.tableWidget.rowCount()):
            row_data = {
                'api_name': self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else "",  # API 명은 컬럼 1
                'icon_state': self._get_icon_state(row),  # PASS/FAIL/NONE 상태
                'retry_count': self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else "0",
                'pass_count': self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else "0",
                'total_count': self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else "0",
                'fail_count': self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else "0",
                'score': self.tableWidget.item(row, 7).text() if self.tableWidget.item(row, 7) else "0%",
            }
            table_data.append(row_data)

        # 전체 데이터 저장 (✅ 복합키 사용: group_id_spec_id)
        composite_key = f"{self.current_group_id}_{self.current_spec_id}"

        Logger.debug(f" 💾 데이터 저장: {composite_key}")
        Logger.debug(f"   - 테이블 행 수: {len(table_data)}")
        Logger.debug(f"   - step_pass_counts: {self.step_pass_counts[:] if hasattr(self, 'step_pass_counts') else []}")

        self.spec_table_data[composite_key] = {
            'table_data': table_data,
            'step_buffers': [buf.copy() for buf in self.step_buffers],  # 깊은 복사
            'total_pass_cnt': self.total_pass_cnt,
            'total_error_cnt': self.total_error_cnt,
            'total_opt_pass_cnt': getattr(self, 'total_opt_pass_cnt', 0),  # 선택 필드 통과 수
            'total_opt_error_cnt': getattr(self, 'total_opt_error_cnt', 0),  # 선택 필드 에러 수
            'api_accumulated_data': self.api_accumulated_data.copy() if hasattr(self, 'api_accumulated_data') else {},
            # ✅ step_pass_counts와 step_error_counts 배열도 저장
            'step_pass_counts': self.step_pass_counts[:] if hasattr(self, 'step_pass_counts') else [],
            'step_error_counts': self.step_error_counts[:] if hasattr(self, 'step_error_counts') else [],
            'step_opt_pass_counts': self.step_opt_pass_counts[:] if hasattr(self, 'step_opt_pass_counts') else [],  # 선택 필드 통과 수 배열
            'step_opt_error_counts': self.step_opt_error_counts[:] if hasattr(self, 'step_opt_error_counts') else [],  # 선택 필드 에러 수 배열
        }

        Logger.debug(f" ✅ 데이터 저장 완료")

    def _get_icon_state(self, row):
        """테이블 행의 아이콘 상태 반환 (PASS/FAIL/NONE)"""
        icon_widget = self.tableWidget.cellWidget(row, 2)  # 아이콘은 컬럼 2
        if icon_widget:
            icon_label = icon_widget.findChild(QLabel)
            if icon_label:
                tooltip = icon_label.toolTip()
                if "PASS" in tooltip:
                    return "PASS"
                elif "FAIL" in tooltip:
                    return "FAIL"
        return "NONE"

    def restore_spec_data(self, spec_id):
        """저장된 spec 데이터 복원 (✅ 복합키 사용)"""
        composite_key = f"{self.current_group_id}_{spec_id}"
        Logger.debug(f" 📂 데이터 복원 시도: {composite_key}")

        if composite_key not in self.spec_table_data:
            Logger.debug(f" ❌ {composite_key} 저장된 데이터 없음 - 초기화 필요")
            return False

        saved_data = self.spec_table_data[composite_key]
        
        # ✅ 방어 로직: 저장된 데이터의 API 개수/이름이 현재와 다르면 복원 취소
        saved_api_list = [row['api_name'] for row in saved_data['table_data']]
        if len(saved_api_list) != len(self.videoMessages):
             Logger.debug(f" ⚠️ 데이터 불일치: 저장된 API 개수({len(saved_api_list)}) != 현재 API 개수({len(self.videoMessages)}) -> 복원 취소")
             del self.spec_table_data[composite_key]
             return False

        Logger.debug(f" ✅ 저장된 데이터 발견!")
        Logger.debug(f"   - 테이블 행 수: {len(saved_data['table_data'])}")
        Logger.debug(f"   - step_pass_counts: {saved_data.get('step_pass_counts', [])}")

        # 테이블 복원
        table_data = saved_data['table_data']
        for row, row_data in enumerate(table_data):
            if row >= self.tableWidget.rowCount():
                break

            # No. (숫자) - 컬럼 0
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # API 이름 - 컬럼 1 (숫자 제거된 이름으로 표시)
            display_name = remove_api_number_suffix(row_data['api_name'])
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            # 아이콘 상태 복원 - 컬럼 2
            icon_state = row_data['icon_state']
            if icon_state == "PASS":
                img = self.img_pass
                icon_size = (84, 20)
            elif icon_state == "FAIL":
                img = self.img_fail
                icon_size = (84, 20)
            else:
                img = self.img_none
                icon_size = (16, 16)

            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(img).pixmap(*icon_size))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setToolTip(f"Result: {icon_state}")
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 2, icon_widget)

            # 나머지 컬럼 복원 - 컬럼 3-7
            for col, key in [(3, 'retry_count'), (4, 'pass_count'),
                             (5, 'total_count'), (6, 'fail_count'), (7, 'score')]:
                new_item = QTableWidgetItem(row_data[key])
                new_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, new_item)

        # step_buffers 복원
        self.step_buffers = [buf.copy() for buf in saved_data['step_buffers']]

        # 점수 복원
        self.total_pass_cnt = saved_data['total_pass_cnt']
        self.total_error_cnt = saved_data['total_error_cnt']
        self.total_opt_pass_cnt = saved_data.get('total_opt_pass_cnt', 0)  # 선택 필드 통과 수
        self.total_opt_error_cnt = saved_data.get('total_opt_error_cnt', 0)  # 선택 필드 에러 수

        # ✅ step_pass_counts와 step_error_counts 배열 복원
        self.step_pass_counts = saved_data.get('step_pass_counts', [0] * len(self.videoMessages))[:]
        self.step_error_counts = saved_data.get('step_error_counts', [0] * len(self.videoMessages))[:]
        self.step_opt_pass_counts = saved_data.get('step_opt_pass_counts', [0] * len(self.videoMessages))[:]  # 선택 필드 통과
        self.step_opt_error_counts = saved_data.get('step_opt_error_counts', [0] * len(self.videoMessages))[:]  # 선택 필드 에러
        Logger.debug(f" step_pass_counts 복원: {self.step_pass_counts}")
        Logger.debug(f" step_error_counts 복원: {self.step_error_counts}")
        Logger.debug(f" step_opt_pass_counts 복원: {self.step_opt_pass_counts}")
        Logger.debug(f" step_opt_error_counts 복원: {self.step_opt_error_counts}")

        # api_accumulated_data 복원
        if 'api_accumulated_data' in saved_data:
            self.api_accumulated_data = saved_data['api_accumulated_data'].copy()

        Logger.debug(f" {spec_id} 데이터 복원 완료")
        return True

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

                # ✅ 4. 기본 변수 초기화 (테이블 제외)
                self.cnt = 0
                self.current_retry = 0
                self.message_error = []
                
                # ✅ 4-1. 서버 및 플래그 초기화
                self.realtime_flag = False
                self.tmp_msg_append_flag = False
                if self.server_th is not None and self.server_th.isRunning():
                    try:
                        self.server_th.httpd.shutdown()
                        self.server_th.wait(2000)
                        Logger.debug(f" 시나리오 전환: 기존 서버 스레드 종료 완료")
                    except Exception as e:
                        Logger.warn(f" 서버 종료 중 오류 (무시): {e}")
                    self.server_th = None

                # ✅ 5. 테이블 구조 업데이트 (행 수만 조정)
                self.update_result_table_structure(self.videoMessages)

                # ✅ 6. 저장된 데이터가 있으면 복원, 없으면 초기화
                if not self.restore_spec_data(new_spec_id):
                    # 저장된 데이터가 없으면 초기화
                    self.total_pass_cnt = 0
                    self.total_error_cnt = 0
                    self.total_opt_pass_cnt = 0  # 선택 필드 통과 수
                    self.total_opt_error_cnt = 0  # 선택 필드 에러 수

                    # ✅ step_pass_counts와 step_error_counts 배열 초기화
                    api_count = len(self.videoMessages)
                    self.step_pass_counts = [0] * api_count
                    self.step_error_counts = [0] * api_count
                    self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
                    self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수

                    self.step_buffers = [
                        {"data": "", "error": "", "result": "PASS"} for _ in range(len(self.videoMessages))
                    ]
                    # 테이블 초기화
                    Logger.debug(f" 💥 저장된 데이터 없음 - 테이블 초기화 시작 ({self.tableWidget.rowCount()}개 행)")
                    for i in range(self.tableWidget.rowCount()):
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

                        # 카운트 초기화 - ✅ 아이템이 없으면 새로 생성 (9컬럼 구조)
                        for col, value in [(3, "0"), (4, "0"), (5, "0"), (6, "0"), (7, "0%")]:
                            item = self.tableWidget.item(i, col)
                            if item:
                                item.setText(value)
                            else:
                                # ✅ 아이템이 없으면 새로 생성
                                new_item = QTableWidgetItem(value)
                                new_item.setTextAlignment(Qt.AlignCenter)
                                self.tableWidget.setItem(i, col, new_item)
                    Logger.debug(f" ✅ 테이블 초기화 완료")

                # trace 초기화 (선택사항 - 필요시)
                # if hasattr(self.Server, 'trace'):
                #     self.Server.trace.clear()

                # Server 객체 초기화
                if hasattr(self, 'Server'):
                    self.Server.cnt = 0
                    self.Server.message = self.videoMessages  # 실제 API 이름 (통신용)
                    self.Server.message_display = self.videoMessagesDisplay  # 표시용 이름
                    self.Server.outMessage = self.videoOutMessage
                    self.Server.outCon = self.videoOutConstraint
                    self.Server.inSchema = self.videoInSchema
                    self.Server.webhookSchema = self.videoWebhookSchema

                    # ✅ api_server는 "Realtime"이 포함된 API만 별도 인덱싱하므로 데이터 필터링
                    filtered_webhook_data = []
                    filtered_webhook_con = []
                    if self.videoMessages:
                        for i, msg in enumerate(self.videoMessages):
                            if "Realtime" in msg:
                                if self.videoWebhookData and i < len(self.videoWebhookData):
                                    filtered_webhook_data.append(self.videoWebhookData[i])
                                else:
                                    filtered_webhook_data.append(None)
                                if self.videoWebhookConstraint and i < len(self.videoWebhookConstraint):
                                    filtered_webhook_con.append(self.videoWebhookConstraint[i])
                                else:
                                    filtered_webhook_con.append(None)

                    self.Server.webhookData = filtered_webhook_data
                    self.Server.webhookCon = filtered_webhook_con

                # 설정 다시 로드
                self.get_setting()

                # 평가 점수 디스플레이 업데이트
                self.update_score_display()

                # URL 업데이트 (test_name 사용)
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', self.current_spec_id)
                    self.pathUrl = self.url + "/" + test_name
                else:
                    self.pathUrl = self.url + "/" + self.current_spec_id
                self.url_text_box.setText(self.pathUrl)
                self.Server.current_spec_id = self.current_spec_id
                self.Server.num_retries = self.spec_config.get('num_retries', self.current_spec_id)
                self.Server.trans_protocol = self.spec_config.get('trans_protocol', self.current_spec_id)

                # 결과 텍스트 초기화
                self.valResult.clear()
                self.append_monitor_log(
                    step_name=f"전환 완료: {self.spec_description}",
                    details=f"API 목록 ({len(self.videoMessages)}개): {', '.join(self.videoMessagesDisplay)}"
                )

                Logger.debug(f" ✅ 전환 완료: {self.spec_description}, API 수: {len(self.videoMessages)}")
        except Exception as e:
            Logger.debug(f"시험 분야 선택 처리 실패: {e}")
            import traceback
            traceback.print_exc()

    def update_result_table_structure(self, api_list):
        """테이블 구조만 업데이트 (API 이름 및 행 수만 조정, 결과는 유지)"""
        api_count = len(api_list)
        current_row_count = self.tableWidget.rowCount()

        # 행 수 조정
        if api_count != current_row_count:
            self.tableWidget.setRowCount(api_count)

        # API 이름만 업데이트
        for row, api_name in enumerate(api_list):
            # 표시용 이름 (숫자 제거)
            display_name = remove_api_number_suffix(api_name)
            
            # No. (숫자) - 컬럼 0
            if self.tableWidget.item(row, 0):
                self.tableWidget.item(row, 0).setText(f"{row + 1}")
            else:
                no_item = QTableWidgetItem(f"{row + 1}")
                no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(row, 0, no_item)

            # API 명 - 컬럼 1 (숫자 제거)
            if self.tableWidget.item(row, 1):
                self.tableWidget.item(row, 1).setText(display_name)
            else:
                api_item = QTableWidgetItem(display_name)
                api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(row, 1, api_item)

            # 결과 아이콘이 없으면 추가 - 컬럼 2
            if not self.tableWidget.cellWidget(row, 2):
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

            # 컬럼 3-7 초기화 (검증 횟수, 통과/전체/실패 필드 수, 평가 점수)
            col_values = [
                (3, "0"),  # 검증 횟수
                (4, "0"),  # 통과 필드 수
                (5, "0"),  # 전체 필드 수
                (6, "0"),  # 실패 필드 수
                (7, "0%")  # 평가 점수
            ]
            for col, value in col_values:
                if not self.tableWidget.item(row, col):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(row, col, item)

            # 상세 내용 버튼이 없으면 추가 - 컬럼 8
            if not self.tableWidget.cellWidget(row, 8):
                detail_label = QLabel()
                img_path = resource_path("assets/image/test_runner/btn_상세내용확인.png").replace("\\", "/")
                pixmap = QPixmap(img_path)
                detail_label.setPixmap(pixmap)
                detail_label.setScaledContents(False)
                detail_label.setFixedSize(pixmap.size())
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

    def update_result_table_with_apis(self, api_list):
        """시험 결과 테이블을 새로운 API 목록으로 업데이트"""
        api_count = len(api_list)
        self.tableWidget.setRowCount(api_count)

        for row, api_name in enumerate(api_list):
            # No. (숫자) - 컬럼 0
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # API 명 - 컬럼 1
            display_name = remove_api_number_suffix(api_name)
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            # 결과 아이콘 초기화 - 컬럼 2
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(84, 20))
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

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_btn)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 8, container)
            self.tableWidget.setRowHeight(row, 40)

    def select_first_scenario(self):
        """프로그램 시작 시 첫 번째 그룹의 첫 번째 시나리오 자동 선택"""
        try:
            Logger.debug(f" 초기 시나리오 자동 선택 시작")

            # 1. 첫 번째 그룹이 있는지 확인
            if self.group_table.rowCount() > 0:
                # 첫 번째 그룹 선택
                self.group_table.selectRow(0)
                Logger.debug(f" 첫 번째 그룹 선택: {self.index_to_group_name.get(0)}")

                # 그룹에 해당하는 시나리오 로드
                self.on_group_selected(0, 0)

            # 2. 시나리오 테이블에 첫 번째 항목이 있는지 확인
            if self.test_field_table.rowCount() > 0:
                # 첫 번째 시나리오 선택
                self.test_field_table.selectRow(0)
                first_spec_id = self.index_to_spec_id.get(0)
                Logger.debug(f" 첫 번째 시나리오 선택: spec_id={first_spec_id}")
                # URL 생성 (test_name 사용)
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', first_spec_id)
                    self.pathUrl = self.url + "/" + test_name
                else:
                    self.pathUrl = self.url + "/" + first_spec_id

                self.Server.current_spec_id = first_spec_id
                self.Server.num_retries = self.spec_config.get('num_retries', first_spec_id)
                self.Server.trans_protocol = self.spec_config.get('trans_protocol', self.current_spec_id)
                # 시나리오 선택 이벤트 수동 트리거 (테이블 업데이트)
                self.on_test_field_selected(0, 0)
            self.url_text_box.setText(self.pathUrl)
            Logger.debug(f" 초기 시나리오 자동 선택 완료: {self.spec_description}")

            # 3. UI 업데이트
            QApplication.processEvents()

        except Exception as e:
            Logger.error(f" 초기 시나리오 선택 실패: {e}")
            import traceback
            traceback.print_exc()
    def show_combined_result(self, row):
        """통합 상세 내용 확인"""
        try:
            buf = self.step_buffers[row]
            api_name = self.tableWidget.item(row, 1).text()  # API 명은 컬럼 1

            # 스키마 데이터 가져오기
            try:
                schema_data = self.videoInSchema[row] if row < len(self.videoInSchema) else None
            except:
                schema_data = None

            # 웹훅 검증인 경우에만 웹훅 스키마
            webhook_schema = None
            if row < len(self.trans_protocols):
                current_protocol = self.trans_protocols[row]
                if current_protocol == "WebHook":
                    try:
                        # ✅ row 인덱스 사용 (self.cnt 아님!)
                        webhook_schema = self.videoWebhookSchema[row] if row < len(self.videoWebhookSchema) else None
                        Logger.debug(f" 웹훅 스키마 로드: row={row}, schema={'있음' if webhook_schema else '없음'}")
                    except Exception as e:
                        Logger.error(f" 웹훅 스키마 로드 실패: {e}")
                        webhook_schema = None
                else:
                    Logger.debug(f" 일반 API (프로토콜: {current_protocol})")

            # 통합 팝업창
            dialog = CombinedDetailDialog(api_name, buf, schema_data, webhook_schema)
            dialog.exec_()

        except Exception as e:
            CustomDialog(f"오류:\n{str(e)}", "상세 내용 확인 오류")

    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭"""
        if col == 2:  # 아이콘 컬럼
            msg = getattr(self, f"step{row + 1}_msg", "")
            if msg:
                CustomDialog(msg, self.tableWidget.item(row, 1).text())  # API 명은 컬럼 1

    def run_single_spec_test(self):
        """단일 spec_id에 대한 시험 실행"""
        # ✅ trace 초기화는 sbtn_push()의 신규 시작 모드에서만 수행
        pass

        # ✅ 이전 시험 결과가 global 점수에 포함되어 있으면 제거 (복합키 사용)
        composite_key = f"{self.current_group_id}_{self.current_spec_id}"
        if composite_key in self.spec_table_data:
            prev_data = self.spec_table_data[composite_key]
            prev_pass = prev_data.get('total_pass_cnt', 0)
            prev_error = prev_data.get('total_error_cnt', 0)
            Logger.debug(f"[SCORE RESET] 기존 {composite_key} 점수 제거: pass={prev_pass}, error={prev_error}")

            # global 점수에서 해당 spec 점수 제거
            self.global_pass_cnt = max(0, self.global_pass_cnt - prev_pass)
            self.global_error_cnt = max(0, self.global_error_cnt - prev_error)
            # global 선택 필드 점수에서도 해당 spec 점수 제거
            prev_opt_pass = prev_data.get('total_opt_pass_cnt', 0)
            prev_opt_error = prev_data.get('total_opt_error_cnt', 0)
            self.global_opt_pass_cnt = max(0, self.global_opt_pass_cnt - prev_opt_pass)
            self.global_opt_error_cnt = max(0, self.global_opt_error_cnt - prev_opt_error)
            Logger.debug(f"[SCORE RESET] 선택 필드 점수 제거: opt_pass={prev_opt_pass}, opt_error={prev_opt_error}")

        # ✅ 현재 시험 시나리오(spec)의 점수만 초기화
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.total_opt_pass_cnt = 0  # 선택 필드 통과 수
        self.total_opt_error_cnt = 0  # 선택 필드 에러 수
        # ✅ step_pass_counts, step_error_counts 배열도 초기화
        if hasattr(self, 'step_pass_counts'):
            api_count = len(self.videoMessages)
            self.step_pass_counts = [0] * api_count
            self.step_error_counts = [0] * api_count
            self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
            self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수
        # global_pass_cnt, global_error_cnt는 유지 (다른 spec 영향 없음)

        self.cnt = 0
        self.current_retry = 0
        self.init_win()
        self.valResult.append(f"시험 시작: {self.spec_description}")

    def sbtn_push(self):
        try:
            # ✅ 자동 재시작 플래그 확인 및 제거
            is_auto_restart = getattr(self, '_auto_restart', False)
            if is_auto_restart:
                self._auto_restart = False
                Logger.debug(f" 자동 재시작 모드 - 시나리오 선택 검증 건너뜀")
            
            # ✅ 시나리오 선택 확인 (자동 재시작이 아닐 때만 검증)
            selected_rows = self.test_field_table.selectionModel().selectedRows()
            if not is_auto_restart and not selected_rows:
                QMessageBox.warning(self, "알림", "시험 시나리오를 선택하세요.")
                return
            
            self.save_current_spec_data()

            # ✅ 로딩 팝업 표시
            self.loading_popup = LoadingPopup()
            self.loading_popup.show()
            self.loading_popup.raise_()  # 최상위로 올리기
            self.loading_popup.activateWindow()  # 활성화
            self.loading_popup.repaint()  # 강제 다시 그리기
            # UI가 확실히 렌더링되도록 여러 번 processEvents 호출
            for _ in range(10):
                QApplication.processEvents()

            selected_spec_ids = [self.index_to_spec_id[r.row()] for r in selected_rows]
            for spec_id in selected_spec_ids:
                QApplication.processEvents()  # 스피너 애니메이션 유지
                self.current_spec_id = spec_id
                self.load_specs_from_constants()
                QApplication.processEvents()  # 스피너 애니메이션 유지
                self.run_single_spec_test()
                QApplication.processEvents()  # 스피너 애니메이션 유지

            # ✅ 일시정지 파일 존재 여부 확인 (spec_id별로 관리)
            paused_file_path = os.path.join(result_dir, f"request_results_paused_{self.current_spec_id}.json")
            resume_mode = os.path.exists(paused_file_path)

            if resume_mode:
                Logger.debug(f" ========== 재개 모드: 일시정지 상태 복원 ==========")
                # 재개 모드: 저장된 상태 복원
                if self.load_paused_state():
                    self.is_paused = False  # 재개 시작이므로 paused 플래그 해제
                    Logger.debug(f" 재개 모드: {self.last_completed_api_index + 1}번째 API부터 시작")
                else:
                    # 복원 실패 시 신규 시작으로 전환
                    Logger.warn(f" 상태 복원 실패, 신규 시작으로 전환")
                    resume_mode = False

            # ✅ 1. 기존 타이머 정지 (재개/신규 공통)
            if self.tick_timer.isActive():
                Logger.debug(f" 기존 타이머 중지")
                self.tick_timer.stop()

            # ✅ 2. 기존 서버 스레드 종료 (재개/신규 공통)
            if self.server_th is not None and self.server_th.isRunning():
                Logger.debug(f" 기존 서버 스레드 종료 중...")
                try:
                    self.server_th.httpd.shutdown()
                    self.server_th.wait(2000)  # 최대 2초 대기
                    Logger.debug(f" 기존 서버 스레드 종료 완료")
                except Exception as e:
                    Logger.warn(f" 서버 종료 중 오류 (무시): {e}")
                self.server_th = None

            QApplication.processEvents()  # 스피너 애니메이션 유지

            if not resume_mode:
                # ========== 신규 시작 모드: 완전 초기화 ==========
                Logger.debug(f" ========== 검증 시작: 완전 초기화 ==========")

                # ✅ 3. trace 디렉토리 초기화
                clean_trace_directory(self.CONSTANTS.trace_path)

                # ✅ 4. 모든 카운터 및 플래그 초기화 (첫 실행처럼)
                self.cnt = 0
                self.cnt_pre = 0
                self.time_pre = 0
                self.current_retry = 0
                self.realtime_flag = False
                self.tmp_msg_append_flag = False
                self.step_start_log_printed = False # ✅ 플래그 초기화

                # ✅ 5. 현재 spec의 점수만 초기화
                self.total_error_cnt = 0
                self.total_pass_cnt = 0

                # ✅ 6. 메시지 및 에러 관련 변수 초기화
                self.message_error = []
                self.final_report = ""

                # ✅ 7. API별 누적 데이터 초기화
                if hasattr(self, 'api_accumulated_data'):
                    self.api_accumulated_data.clear()
                else:
                    self.api_accumulated_data = {}

                # ✅ 8. step별 메시지 초기화
                for i in range(1, 10):
                    setattr(self, f"step{i}_msg", "")

                # ✅ 9. step_buffers 완전 재생성
                api_count = len(self.videoMessages) if self.videoMessages else 9
                self.step_buffers = [
                    {"data": "", "error": "", "result": "PASS", "raw_data_list": []}
                    for _ in range(api_count)
                ]
                Logger.debug(f" step_buffers 재생성 완료: {len(self.step_buffers)}개")

                # ✅ 10. 현재 spec에 맞게 누적 카운트 초기화
                self.step_pass_counts = [0] * api_count
                self.step_error_counts = [0] * api_count
                self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
                self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수
                Logger.debug(f" step_pass_counts, step_error_counts, step_opt_pass_counts, step_opt_error_counts 초기화 완료: {api_count}개")

                # ✅ 11. Server 객체 상태 초기화
                if hasattr(self.Server, 'trace'):
                    from collections import defaultdict, deque
                    self.Server.trace = defaultdict(lambda: deque(maxlen=1000))
                if hasattr(self.Server, 'latest_event'):
                    from collections import defaultdict
                    self.Server.latest_event = defaultdict(dict)
                if hasattr(self.Server, 'request_counter'):
                    self.Server.request_counter = {}
                if hasattr(self.Server, 'webhook_thread'):
                    self.Server.webhook_thread = None

                # ✅ 12. 평가 점수 디스플레이 초기화
                self.update_score_display()
                QApplication.processEvents()  # 스피너 애니메이션 유지
            else:
                # ========== 재개 모드: 저장된 상태 사용, 초기화 건너뛰기 ==========
                Logger.debug(f" 재개 모드: 초기화 건너뛰기, 저장된 상태 사용")
                # cnt는 last_completed_api_index + 1로 설정
                self.cnt = self.last_completed_api_index + 1
                Logger.debug(f" 재개 모드: cnt = {self.cnt}")

                # ✅ 재개 모드에서도 실행 상태 변수는 초기화 필요
                self.current_retry = 0  # 재시도 카운터 초기화 (중요!)
                self.cnt_pre = 0
                self.time_pre = 0
                self.realtime_flag = False
                self.tmp_msg_append_flag = False
                self.message_error = []
                self.final_report = ""
                Logger.debug(f" 재개 모드: 실행 상태 변수 초기화 완료")

                # ✅ 미완료 API의 trace 파일 삭제 (완료된 API는 유지)
                trace_dir = os.path.join(result_dir, "trace")
                if os.path.exists(trace_dir):
                    Logger.debug(f" 미완료 API trace 파일 삭제 시작 (완료: 0~{self.last_completed_api_index})")
                    for i in range(self.last_completed_api_index + 1, len(self.videoMessages)):
                        api_name = self.videoMessages[i]
                        # ✅ api_server.py와 동일한 방식으로 파일명 변환
                        safe_api = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(api_name))
                        # ✅ 실제 생성되는 파일명 패턴으로 삭제
                        # 주의: api_server.py에서는 step_idx + 1을 사용하므로 여기서도 i + 1 사용
                        trace_patterns = [
                            f"trace_{safe_api}.ndjson",
                            f"trace_{i + 1:02d}_{safe_api}.ndjson"
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

            QApplication.processEvents()  # 스피너 애니메이션 유지

            # ✅ 12. 버튼 상태 변경
            self.sbtn.setDisabled(True)
            self.stop_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)

            # ✅ 13. JSON 데이터 준비
            json_to_data(self.radio_check_flag)
            timeout = 5
            default_timeout = 5

            # ✅ 15. Server 설정
            Logger.debug(f" Server 설정 시작")
            self.Server.message = self.videoMessages  # 실제 API 이름 (통신용)
            self.Server.message_display = self.videoMessagesDisplay  # 표시용 이름
            self.Server.outMessage = self.videoOutMessage
            self.Server.inSchema = self.videoInSchema
            self.Server.outCon = self.videoOutConstraint

            # ✅ api_server는 "Realtime"이 포함된 API만 별도 인덱싱하므로 데이터 필터링
            filtered_webhook_data = []
            filtered_webhook_con = []
            if self.videoMessages:
                for i, msg in enumerate(self.videoMessages):
                    if "Realtime" in msg:
                        if self.videoWebhookData and i < len(self.videoWebhookData):
                            filtered_webhook_data.append(self.videoWebhookData[i])
                        else:
                            filtered_webhook_data.append(None)
                        if self.videoWebhookConstraint and i < len(self.videoWebhookConstraint):
                            filtered_webhook_con.append(self.videoWebhookConstraint[i])
                        else:
                            filtered_webhook_con.append(None)

            self.Server.webhookData = filtered_webhook_data
            self.Server.webhookCon = filtered_webhook_con
            self.Server.system = "video"
            self.Server.timeout = timeout
            Logger.debug(f" Server 설정 완료")
            QApplication.processEvents()  # 스피너 애니메이션 유지

            # ✅ 16. UI 초기화
            Logger.debug(f" UI 초기화 시작")
            if not resume_mode:
                # 신규 시작: valResult 클리어
                self.valResult.clear()
            else:
                # 재개 모드: 저장된 모니터링 메시지 복원
                self.valResult.clear()  # 일단 클리어
                if self.paused_valResult_text:
                    self.valResult.setHtml(self.paused_valResult_text)
                    self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 10px;">========== 재개 ==========</div>')
                    self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">마지막 완료 API: {self.last_completed_api_index + 1}번째</div>')
                    self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-bottom: 10px;">{self.last_completed_api_index + 2}번째 API부터 재개합니다.</div>')
                    Logger.debug(f" 모니터링 메시지 복원 완료: {len(self.paused_valResult_text)} 문자")
            Logger.debug(f" UI 초기화 완료")

            # ✅ 17. 테이블 아이콘 및 데이터 초기화 (신규 시작 시만)
            if not resume_mode:
                Logger.debug(f" 테이블 초기화 시작")
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

                    # 모든 카운트 0으로 초기화 (9컬럼 구조)
                    for col, value in ((3, "0"), (4, "0"), (5, "0"), (6, "0"), (7, "0%")):
                        item = QTableWidgetItem(value)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget.setItem(i, col, item)
                Logger.debug(f" 테이블 초기화 완료")
            else:
                Logger.debug(f" 재개 모드: 테이블 초기화 건너뛰기 (기존 데이터 유지)")

            # ✅ 18. 인증 설정
            Logger.debug(f"인증 설정 시작")
            Logger.debug(f"사용자 인증 방식: {self.CONSTANTS.auth_type}")

            if self.r2 == "B":
                self.Server.auth_type = "B"
                self.Server.bearer_credentials[0] = self.accessInfo[0]
                self.Server.bearer_credentials[1] = self.accessInfo[1]
            elif self.r2 == "D":
                self.Server.auth_type = "D"
                self.Server.auth_Info[0] = self.accessInfo[0]
                self.Server.auth_Info[1] = self.accessInfo[1]

            self.Server.transProtocolInput = "LongPolling"
            
            # ✅ 19. 시작 메시지 출력
            self.append_monitor_log(
                step_name="시험 시작",
                details=f"API 개수: {len(self.videoMessages)}개"
            )

            # ✅ 20. 서버 시작
            Logger.debug(f" 서버 시작 준비")
            url = self.url.split(":")
            address_port = int(url[-1])
            # ✅ 0.0.0.0으로 바인딩 (모든 네트워크 인터페이스에서 수신)
            address_ip = "0.0.0.0"

            Logger.debug(f" 플랫폼 서버 시작: {address_ip}:{address_port} (외부 접근: {self.url})")
            self.server_th = server_th(handler_class=self.Server, address=address_ip, port=address_port)
            self.server_th.start()

            # 서버 준비 완료까지 대기 (첫 실행 시만)
            if self.first_run:
                # 5초 대기하면서 스피너 애니메이션 유지
                for _ in range(50):  # 50 * 100ms = 5초
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.first_run = False
            else:
                # 두 번째 이후에도 서버 안정화를 위한 짧은 대기
                Logger.debug("[DEBUG] 서버 재시작 안정화 대기...")
                # 2초 대기하면서 스피너 애니메이션 유지
                for _ in range(20):  # 20 * 100ms = 2초
                    time.sleep(0.1)
                    QApplication.processEvents()
 
            # ✅ 21. 타이머 시작 (모든 초기화 완료 후)
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

        except Exception as e:
            Logger.error(f" sbtn_push에서 예외 발생: {e}")
            import traceback
            traceback.print_exc()

            # ✅ 에러 발생 시 로딩 팝업 닫기
            if self.loading_popup:
                self.loading_popup.close()
                self.loading_popup = None

            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)
            self.cancel_btn.setDisabled(True)

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
                "step_opt_pass_counts": getattr(self, 'step_opt_pass_counts', [0] * len(self.videoMessages)),  # 선택 필드 통과
                "step_opt_error_counts": getattr(self, 'step_opt_error_counts', [0] * len(self.videoMessages)),  # 선택 필드 에러
                "total_pass_cnt": self.total_pass_cnt,
                "total_error_cnt": self.total_error_cnt,
                "total_opt_pass_cnt": getattr(self, 'total_opt_pass_cnt', 0),  # 선택 필드 통과 수
                "total_opt_error_cnt": getattr(self, 'total_opt_error_cnt', 0),  # 선택 필드 에러 수
                "valResult_text": self.valResult.toHtml(),
                "current_spec_id": self.current_spec_id,
                "global_pass_cnt": self.global_pass_cnt,
                "global_error_cnt": self.global_error_cnt,
                "global_opt_pass_cnt": getattr(self, 'global_opt_pass_cnt', 0),  # 전체 선택 필드 통과 수
                "global_opt_error_cnt": getattr(self, 'global_opt_error_cnt', 0)  # 전체 선택 필드 에러 수
            }

            # JSON 파일로 저장 (spec_id 포함)
            paused_file_path = os.path.join(result_dir, f"request_results_paused_{self.current_spec_id}.json")
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
            self.valResult.append(f'<div style="font-size: 18px; color: #ef4444; font-family: \'Noto Sans KR\'; margin-top: 10px;">재개 정보 저장 실패: {str(e)}</div>')

    def load_paused_state(self):
        """일시정지된 상태를 JSON 파일에서 복원"""
        try:
            paused_file_path = os.path.join(result_dir, f"request_results_paused_{self.current_spec_id}.json")

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
            self.step_opt_pass_counts = paused_state.get("step_opt_pass_counts", [0] * len(self.videoMessages))  # 선택 필드 통과
            self.step_opt_error_counts = paused_state.get("step_opt_error_counts", [0] * len(self.videoMessages))  # 선택 필드 에러
            self.total_pass_cnt = paused_state.get("total_pass_cnt", 0)
            self.total_error_cnt = paused_state.get("total_error_cnt", 0)
            self.total_opt_pass_cnt = paused_state.get("total_opt_pass_cnt", 0)  # 선택 필드 통과 수
            self.total_opt_error_cnt = paused_state.get("total_opt_error_cnt", 0)  # 선택 필드 에러 수
            self.paused_valResult_text = paused_state.get("valResult_text", "")
            self.global_pass_cnt = paused_state.get("global_pass_cnt", 0)
            self.global_opt_pass_cnt = paused_state.get("global_opt_pass_cnt", 0)  # 전체 선택 필드 통과 수
            self.global_opt_error_cnt = paused_state.get("global_opt_error_cnt", 0)  # 전체 선택 필드 에러 수
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
            paused_file_path = os.path.join(result_dir, f"request_results_paused_{self.current_spec_id}.json")
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
            # request_results_paused_*.json 패턴으로 모든 일시정지 파일 찾기
            pattern = os.path.join(result_dir, "request_results_paused_*.json")
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
            # request_results_paused_*.json 패턴으로 모든 일시정지 파일 찾기
            pattern = os.path.join(result_dir, "request_results_paused_*.json")
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
        # ✅ 타이머 중지
        if self.tick_timer.isActive():
            self.tick_timer.stop()
            Logger.debug(f" 타이머 중지됨")

        # ✅ 서버 스레드 종료
        if self.server_th is not None and self.server_th.isRunning():
            Logger.debug(f" 서버 스레드 종료 시작...")
            try:
                self.server_th.httpd.shutdown()
                self.server_th.wait(2000)  # 최대 2초 대기
                Logger.debug(f" 서버 스레드 종료 완료")
            except Exception as e:
                Logger.warn(f" 서버 종료 중 오류 (무시): {e}")
            self.server_th = None

        self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">검증 절차가 중지되었습니다.</div>')
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)
        self.cancel_btn.setDisabled(True)
        
        # ✅ 시험 중지 - idle 상태 heartbeat 전송
        try:
            api_client = APIClient()
            api_client.send_heartbeat_idle()
            Logger.info(f"✅ 시험 중지 - idle 상태 전송 완료")
        except Exception as e:
            Logger.warning(f"⚠️ 시험 중지 - idle 상태 전송 실패: {e}")
        
        self.save_current_spec_data()

        # ✅ 일시정지 상태 저장
        self.is_paused = True
        self.save_paused_state()

        try:
            self.run_status = "진행중"
            result_json = build_result_json(self)
            url = f"{CONSTANTS.management_url}/api/integration/test-results"
            response = requests.post(url, json=result_json)
            Logger.debug(f"✅ 시험 결과 전송 상태 코드:: {response.status_code}")
            Logger.debug(f"📥  시험 결과 전송 응답:: {response.text}")
            json_path = os.path.join(result_dir, "request_results.json")
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
        
        # 2. 서버 스레드 완전 종료
        if self.server_th is not None and self.server_th.isRunning():
            Logger.debug(f" 서버 스레드 종료 시작...")
            try:
                self.server_th.httpd.shutdown()
                self.server_th.wait(3000)  # 최대 3초 대기
                Logger.debug(f" 서버 스레드 종료 완료")
            except Exception as e:
                Logger.warn(f" 서버 종료 중 오류 (무시): {e}")
            self.server_th = None
        
        # 3. 일시정지 파일 삭제
        self.cleanup_paused_file()
        Logger.debug(f" 일시정지 파일 삭제 완료")
        
        # 4. 상태 완전 초기화
        self.is_paused = False
        self.last_completed_api_index = -1
        self.paused_valResult_text = ""
        self.cnt = 0
        self.current_retry = 0
        self.post_flag = False  # 웹훅 플래그 초기화
        self.res = None  # 응답 초기화
        Logger.debug(f" 상태 초기화 완료")
        
        # 5. 버튼 상태 초기화
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)
        self.cancel_btn.setDisabled(True)
        
        # ✅ 시험 취소 - idle 상태 heartbeat 전송
        try:
            api_client = APIClient()
            api_client.send_heartbeat_idle()
            Logger.info(f"✅ 시험 취소 - idle 상태 전송 완료")
        except Exception as e:
            Logger.warning(f"⚠️ 시험 취소 - idle 상태 전송 실패: {e}")
        
        # 6. 모니터링 화면 초기화
        self.valResult.clear()
        self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">시험이 취소되었습니다. 시험 시작 버튼을 눌러 다시 시작하세요.</div>')
        Logger.debug(f" 모니터링 화면 초기화")
        
        # 7. UI 업데이트 처리
        QApplication.processEvents()
        
        Logger.debug(f" ========== 시험 취소 완료 ==========")

    def init_win(self):
        """기본 초기화 (sbtn_push에서 이미 대부분 처리되므로 최소화)"""
        # 이 함수는 레거시 호환성을 위해 유지되지만, 실제 초기화는 sbtn_push에서 수행
        pass

    def show_result_page(self):
        """시험 결과 페이지 표시"""
        if self.embedded:
            self.showResultRequested.emit(self)
        else:
            if self._wrapper_window is not None:
                self._wrapper_window._show_result_page()
            else:
                if hasattr(self, 'result_window') and self.result_window is not None:
                    self.result_window.close()
                self.result_window = ResultPageWidget(self, embedded=False)
                self.result_window.show()

    def toggle_fullscreen(self):
        """전체화면 전환"""
        try:
            if not self._is_fullscreen:
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
        self.Server.system = "video"

        # 기본 시스템 설정
        self.message = self.videoMessages
        self.outMessage = self.videoOutMessage
        self.inSchema = self.videoInSchema
        self.outCon = self.videoOutConstraint

        # 이 부분 수정해야함
        try:
            webhook_schema_name = f"{self.current_spec_id}_webhook_inSchema"
            self.webhookSchema = getattr(schema_response_module, webhook_schema_name, [])
        except Exception as e:
            Logger.debug(f"Error loading webhook schema: {e}")
            self.webhookSchema = []

        self.r2 = self.auth_type
        if self.r2 == "Digest Auth":
            self.r2 = "D"
        elif self.r2 == "Bearer Token":
            self.r2 = "B"
        else:
            self.r2 = "None"

        # ✅ URL 업데이트 (test_name 사용) - spec_config가 로드된 후 실행
        if hasattr(self, 'spec_config') and hasattr(self, 'url_text_box'):
            test_name = self.spec_config.get('test_name', self.current_spec_id)
            self.pathUrl = self.url + "/" + test_name
            self.url_text_box.setText(self.pathUrl)
            Logger.debug(f" 시험 URL 업데이트: {self.pathUrl}")

    def closeEvent(self, event):
        """창 닫기 이벤트 - 서버 스레드 정리"""
        # ✅ 타이머 중지
        if hasattr(self, 'tick_timer') and self.tick_timer.isActive():
            self.tick_timer.stop()

        # ✅ 서버 스레드 종료
        if hasattr(self, 'server_th') and self.server_th is not None and self.server_th.isRunning():
            try:
                self.server_th.httpd.shutdown()
                self.server_th.wait(2000)  # 최대 2초 대기
            except Exception as e:
                Logger.warn(f" 서버 종료 중 오류 (무시): {e}")

        event.accept()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    fontDB.addApplicationFont(resource_path('assets/fonts/NotoSansKR-Regular.ttf'))
    fontDB.addApplicationFont(resource_path('assets/fonts/NotoSansKR-Medium.ttf'))
    fontDB.addApplicationFont(resource_path('assets/fonts/NotoSansKR-Bold.ttf'))
    app.setFont(QFont('NanumGothic'))

    ex = PlatformValidationWindow(MyApp)
    ex.initialize()
    ex.show()
    sys.exit(app.exec())