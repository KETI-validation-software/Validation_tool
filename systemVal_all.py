# ?쒖뒪??寃利??뚰봽?몄썾??
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
# SSL 寃쎄퀬 鍮꾪솢?깊솕 (?먯껜 ?쒕챸 ?몄쬆???ъ슜 ??
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')
import math
import re
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor, QPixmap
from PyQt5.QtCore import *
from api.webhook_api import WebhookThread
from api.api_server import Server  # ??door_memory ?묎렐???꾪븳 import 異붽?
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
    # ?쒗뿕 寃곌낵 ?쒖떆 ?붿껌 ?쒓렇??(main.py? ?곕룞)
    showResultRequested = pyqtSignal(object)  # parent widget???몄옄濡??꾨떖

    def _load_from_trace_file(self, api_name, direction="RESPONSE"):
        """Trace ?뚯씪?먯꽌 理쒖떊 ?대깽???곗씠??濡쒕뱶"""
        try:
            # API ?대쫫?먯꽌 ?щ옒???쒓굅
            api_name_clean = api_name.lstrip("/")
            
            Logger.debug(f"trace ?뚯씪 李얘린: api_name={api_name}, direction={direction}")
            
            # trace ?붾젆?좊━??紐⑤뱺 ?뚯씪 寃??
            trace_dir = Path(CONSTANTS.trace_path)
            if not trace_dir.exists():
                Logger.debug(f"trace ?붾젆?좊━ ?놁쓬: {trace_dir}")
                return None
            
            # API ?대쫫怨?留ㅼ묶?섎뒗 ?뚯씪 李얘린
            # ?곗꽑?쒖쐞: 1) 踰덊샇 ?덈뒗 ?뚯씪 ??2) 踰덊샇 ?녿뒗 ?뚯씪
            safe_api = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(api_name_clean))
            
            trace_file = None
            
            # ???곗꽑?쒖쐞 1: 踰덊샇 prefix ?ы븿???뺤떇 李얘린 (trace_XX_API.ndjson)
            numbered_files = list(trace_dir.glob(f"trace_*_{safe_api}.ndjson"))
            if numbered_files:
                # 踰덊샇媛 ?덈뒗 ?뚯씪 以?媛??理쒓렐 ?뚯씪 ?ъ슜
                trace_file = max(numbered_files, key=lambda f: f.stat().st_mtime)
                Logger.debug(f"踰덊샇 ?덈뒗 trace ?뚯씪 諛쒓껄: {trace_file.name}")
            
            # ???곗꽑?쒖쐞 2: 踰덊샇 ?녿뒗 ?뺤떇 李얘린 (trace_API.ndjson)
            if not trace_file:
                unnumbered_files = list(trace_dir.glob(f"trace_{safe_api}.ndjson"))
                if unnumbered_files:
                    # 踰덊샇 ?녿뒗 ?뚯씪 以?媛??理쒓렐 ?뚯씪 ?ъ슜
                    trace_file = max(unnumbered_files, key=lambda f: f.stat().st_mtime)
                    Logger.debug(f"踰덊샇 ?녿뒗 trace ?뚯씪 諛쒓껄: {trace_file.name}")
            
            if not trace_file:
                Logger.debug(f"trace ?뚯씪 ?놁쓬 (?⑦꽩: trace_*_{safe_api}.ndjson ?먮뒗 trace_{safe_api}.ndjson)")
                return None
            
            Logger.debug(f"?ъ슜??trace ?뚯씪: {trace_file.name}")

            # ?뚯씪?먯꽌 媛??理쒓렐???대떦 direction ?대깽??李얘린
            latest_event = None
            with open(trace_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        # direction留??뺤씤 (api???대? ?뚯씪紐낆쑝濡??꾪꽣留곷맖)
                        if event.get("dir") == direction:
                            latest_event = event
                    except json.JSONDecodeError:
                        continue

            if latest_event:
                # latest_events ?낅뜲?댄듃 - ?щ윭 ???뺤떇?쇰줈 ???
                api_key = latest_event.get("api", api_name)
                
                # ??1. ?먮낯 API ?대쫫?쇰줈 ???
                if api_key not in self.latest_events:
                    self.latest_events[api_key] = {}
                self.latest_events[api_key][direction] = latest_event
                
                # ??2. ?щ옒???쒓굅???뺤떇?쇰줈?????(?? "CameraProfiles")
                api_key_clean = api_key.lstrip('/')
                if api_key_clean not in self.latest_events:
                    self.latest_events[api_key_clean] = {}
                self.latest_events[api_key_clean][direction] = latest_event
                
                # ??3. ?щ옒???ы븿???뺤떇?쇰줈?????(?? "/CameraProfiles")
                api_key_with_slash = f"/{api_key_clean}" if not api_key_clean.startswith('/') else api_key_clean
                if api_key_with_slash not in self.latest_events:
                    self.latest_events[api_key_with_slash] = {}
                self.latest_events[api_key_with_slash][direction] = latest_event
                
                Logger.debug(f"trace ?뚯씪?먯꽌 {api_name} {direction} ?곗씠??濡쒕뱶 ?꾨즺")
                Logger.debug(f"latest_events????λ맂 ?ㅻ뱾: {api_key}, {api_key_clean}, {api_key_with_slash}")
                return latest_event.get("data")
            else:
                Logger.debug(f"trace ?뚯씪?먯꽌 {api_name} {direction} ?곗씠???놁쓬")
                return None

        except Exception as e:
            Logger.error(f"trace ?뚯씪 濡쒕뱶 以??ㅻ쪟: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _apply_request_constraints(self, request_data, cnt):
        """
        ?댁쟾 ?묐떟 ?곗씠?곕? 湲곕컲?쇰줈 ?붿껌 ?곗씠???낅뜲?댄듃
        - inCon (request constraints)???ъ슜?섏뿬 ?댁쟾 endpoint ?묐떟?먯꽌 媛?媛?몄삤湲?
        """
        try:
            # constraints 媛?몄삤湲?
            if cnt >= len(self.inCon) or not self.inCon[cnt]:
                # constraints媛 ?녿뜑?쇰룄 媛뺤젣 濡쒕뱶 濡쒖쭅? ????섎?濡?諛붾줈 由ы꽩?섏? ?딄퀬 鍮?dict ?좊떦
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
                    Logger.debug(f"trace ?뚯씪?먯꽌 {endpoint} RESPONSE 濡쒕뱶 ?쒕룄")
                    self._load_from_trace_file(endpoint, "RESPONSE")
                else:
                    Logger.debug(f"latest_events???대? {endpoint} RESPONSE 議댁옱")
            
            api_name = self.message[cnt] if cnt < len(self.message) else ""

            # ????臾댁“嫄?留듯븨 ?섏뼱????
            if "RealtimeDoorStatus" in api_name:
                if "DoorProfiles" not in self.latest_events or "RESPONSE" not in self.latest_events.get("DoorProfiles", {}):
                    Logger.debug(f"RealtimeDoorStatus??DoorProfiles RESPONSE 濡쒕뱶 ?쒕룄")
                    self._load_from_trace_file("DoorProfiles", "RESPONSE")
            
            self.generator.latest_events = self.latest_events

            updated_request = self.generator._applied_constraints(
                request_data={},  # ?댁쟾 ?붿껌 ?곗씠?곕뒗 ?꾩슂 ?놁쓬
                template_data=request_data.copy(),  # ?꾩옱 ?붿껌 ?곗씠?곕? ?쒗뵆由우쑝濡?
                constraints=constraints,
                api_name=api_name,  # ??API ?대쫫 ?꾨떖
                door_memory=Server.door_memory  # ??臾??곹깭 ??μ냼 ?꾨떖
            )

            self.resp_rules = get_validation_rules(
                spec_id=self.current_spec_id,
                api_name=self.message[self.cnt] if self.cnt < len(self.message) else "",
                direction="out"  # ?묐떟 寃利?

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
                # Logger.warning(f"constraint ?곸슜 以??쇰? ?ㅽ뙣: {e}")
                return updated_request
        except Exception as e:
            Logger.error(f"_apply_request_constraints ?ㅽ뻾 以??ㅻ쪟: {e}")
            import traceback
            
            return request_data

    def _append_text(self, obj):
        import json
        from html import escape
        try:
            if isinstance(obj, (dict, list)):
                json_str = json.dumps(obj, ensure_ascii=False, indent=2)
                # HTML ?쒓렇瑜?escape 泥섎━?섏뿬 ?뚮뜑留?諛⑹?
                escaped_json = escape(json_str)
                # 媛쒗뻾??<br> ?쒓렇濡?蹂?섑븯怨?怨듬갚??&nbsp;濡?蹂??
                formatted = escaped_json.replace('\n', '<br>').replace(' ', '&nbsp;')
                self.valResult.append(formatted)
            else:
                # 臾몄옄?대룄 HTML escape 泥섎━
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
        # ???꾨줈洹몃옩 ?쒖옉 ??紐⑤뱺 ?쇱떆?뺤? ?뚯씪 ??젣
        self._cleanup_all_paused_files_on_startup()
        
        # ???곹깭 愿由ъ옄 珥덇린??
        self.state_manager = SystemStateManager(self)
        
        self.run_status = "吏꾪뻾??

        # ??遺꾩빞蹂??먯닔 (?꾩옱 spec留?
        self.current_retry = 0
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.total_opt_pass_cnt = 0  # ?좏깮 ?꾨뱶 ?듦낵 ??
        self.total_opt_error_cnt = 0  # ?좏깮 ?꾨뱶 ?먮윭 ??

        # ???꾩껜 ?먯닔 (紐⑤뱺 spec ?⑹궛) - 異붽?
        self.global_pass_cnt = 0
        self.global_error_cnt = 0
        self.global_opt_pass_cnt = 0  # ?꾩껜 ?좏깮 ?꾨뱶 ?듦낵 ??
        self.global_opt_error_cnt = 0  # ?꾩껜 ?좏깮 ?꾨뱶 ?먮윭 ??

        # ??媛?spec_id蹂??뚯씠釉??곗씠?????(?쒕굹由ъ삤 ?꾪솚 ??寃곌낵 ?좎?) - 異붽?
        self.spec_table_data = {}  # {spec_id: {table_data, step_buffers, scores}}

        # CONSTANTS ?ъ슜
        self.CONSTANTS = CONSTANTS
        
        # ??spec_id 珥덇린??(info_GUI?먯꽌 ?꾨떖諛쏄굅??湲곕낯媛??ъ슜)
        if spec_id:
            self.current_spec_id = spec_id
            Logger.info(f"?꾨떖諛쏆? spec_id ?ъ슜: {spec_id}")
        else:
            self.current_spec_id = "cmgatbdp000bqihlexmywusvq"  # 湲곕낯媛? 蹂댁븞?⑹꽱???쒖뒪??(7媛?API) -> 吏湲덉? ?좉퉸 ?놁뼱吏?
            Logger.info(f"湲곕낯 spec_id ?ъ슜: {self.current_spec_id}")

        self.current_group_id = None  # ??洹몃９ ID ??μ슜
        
        self.load_specs_from_constants()
        self.embedded = embedded

        # ?꾩껜?붾㈃ 愿??蹂??珥덇린??
        self._is_fullscreen = False
        self._saved_geom = None
        self._saved_state = None

        self.webhook_res = None
        self.res = None
        self.radio_check_flag = "video"  # ?곸긽蹂댁븞 ?쒖뒪?쒖쑝濡?怨좎젙

        # 濡쒕뵫 ?앹뾽 ?몄뒪?댁뒪 蹂??
        self.loading_popup = None

        # ?꾩씠肄?寃쎈줈 (硫붿씤 ?섏씠吏??
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

        # ???쇱떆?뺤? 諛??ш컻 愿??蹂??
        self.is_paused = False
        self.last_completed_api_index = -1
        self.paused_valResult_text = ""

        parts = self.auth_info.split(",")
        auth = [parts[0], parts[1] if len(parts) > 1 else ""]
        self.accessInfo = [auth[0], auth[1]]

        # step_buffers ?숈쟻 ?앹꽦 (API 媛쒖닔???곕씪)
        api_count = len(self.videoMessages)
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS", "raw_data_list": []} for _ in range(api_count)
        ]

        # ???꾩쟻 移댁슫??珥덇린??
        self.step_pass_counts = [0] * api_count
        self.step_error_counts = [0] * api_count
        self.step_opt_pass_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?듦낵 ??
        self.step_opt_error_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?먮윭 ??
        self.step_pass_flags = [0] * api_count

        self.trace = defaultdict(list)

        # ??Data Mapper 珥덇린??- trace 湲곕컲 latest_events ?ъ슜
        self.latest_events = {}  # API蹂?理쒖떊 ?대깽?????
        self.generator = ConstraintDataGenerator(self.latest_events)

        self.initUI()
        
        # System?먯꽌???쒗뿕 URL ?섏젙 遺덇?
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
        self.get_setting()  # ?ㅽ뻾?섎뒗 ?쒖젏
        self.webhook_flag = False
        self.webhook_msg = "."
        self.webhook_cnt = 99
        self.reference_context = {}  # 留λ씫寃利?李몄“ 而⑦뀓?ㅽ듃
        self.webhook_schema_idx = 0  # ???뱁썒 ?ㅽ궎留??몃뜳??異붽?

    def save_current_spec_data(self):
        """?꾩옱 spec???뚯씠釉??곗씠?곗? ?곹깭瑜????(state_manager ?꾩엫)"""
        if hasattr(self, 'state_manager'):
            self.state_manager.save_current_spec_data()

    def _get_icon_state(self, row):
        """?뚯씠釉??됱쓽 ?꾩씠肄??곹깭 諛섑솚 (state_manager ?꾩엫)"""
        if hasattr(self, 'state_manager'):
            return self.state_manager._get_icon_state(row)
        return "NONE"

    def restore_spec_data(self, spec_id):
        """??λ맂 spec ?곗씠??蹂듭썝 (state_manager ?꾩엫)"""
        if hasattr(self, 'state_manager'):
            return self.state_manager.restore_spec_data(spec_id)
        return False

    def _push_event(self, step_idx, direction, payload):  # ### NEW
        """REQUEST/RESPONSE/WEBHOOK ?대깽?몃? ?쒖꽌?濡?湲곕줉?섍퀬 ndjson??append"""
        try:
            api = self.message[step_idx] if 0 <= step_idx < len(self.message) else f"step_{step_idx + 1}"
            evt = {
                "time": datetime.utcnow().isoformat() + "Z",
                "api": api,
                "dir": direction,  # "REQUEST" | "RESPONSE" | "WEBHOOK"
                "data": redact(payload)
            }
            self.trace[step_idx].append(evt)

            # ??latest_events ?낅뜲?댄듃 (data mapper?? - ?щ윭 ???뺤떇?쇰줈 ???
            # 1. ?먮낯 API ?대쫫?쇰줈 ???
            if api not in self.latest_events:
                self.latest_events[api] = {}
            self.latest_events[api][direction] = evt
            
            # 2. ?щ옒???쒓굅???뺤떇?쇰줈?????(?? "CameraProfiles")
            api_clean = api.lstrip('/')
            if api_clean != api:
                if api_clean not in self.latest_events:
                    self.latest_events[api_clean] = {}
                self.latest_events[api_clean][direction] = evt
            
            # 3. ?щ옒???ы븿???뺤떇?쇰줈?????(?? "/CameraProfiles")
            api_with_slash = f"/{api_clean}" if not api_clean.startswith('/') else api_clean
            if api_with_slash != api:
                if api_with_slash not in self.latest_events:
                    self.latest_events[api_with_slash] = {}
                self.latest_events[api_with_slash][direction] = evt
            
            # ???붾쾭洹?濡쒓렇 異붽?
            Logger.debug(f" API={api}, Direction={direction}")
            Logger.debug(f" ??λ맂 ?ㅻ뱾: {api}, {api_clean}, {api_with_slash}")
            Logger.debug(f" latest_events ?꾩껜 ??紐⑸줉: {list(self.latest_events.keys())}")

            # (?듭뀡) 利됱떆 ?뚯씪濡쒕룄 ?④? - append-only ndjson
            os.makedirs(CONSTANTS.trace_path, exist_ok=True)
            safe_api = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(api))
            trace_path = os.path.join(CONSTANTS.trace_path, f"trace_{step_idx + 1:02d}_{safe_api}.ndjson")
            with open(trace_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(evt, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def load_specs_from_constants(self):
        """
        ??SPEC_CONFIG 湲곕컲?쇰줈 spec ?곗씠???숈쟻 濡쒕뱶
        - current_spec_id???곕씪 ?щ컮瑜?紐⑤뱢(spec.video ?먮뒗 spec/)?먯꽌 ?곗씠??濡쒕뱶
        - trans_protocol, time_out, num_retries??SPEC_CONFIG?먯꽌 媛?몄샂
        """
        # ===== PyInstaller ?섍꼍?먯꽌 ?몃? CONSTANTS.py?먯꽌 SPEC_CONFIG 濡쒕뱶 =====
        import sys
        import os

        SPEC_CONFIG = getattr(self.CONSTANTS, 'SPEC_CONFIG', [])
        url_value = getattr(self.CONSTANTS, 'url', None)
        auth_type = getattr(self.CONSTANTS, 'auth_type', None)
        auth_info = getattr(self.CONSTANTS, 'auth_info', None)
        if getattr(sys, 'frozen', False):
            # PyInstaller ?섍꼍: ?몃? CONSTANTS.py?먯꽌 SPEC_CONFIG ?쎄린
            exe_dir = os.path.dirname(sys.executable)
            external_constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")

            if os.path.exists(external_constants_path):
                Logger.info(f"?몃? CONSTANTS.py?먯꽌 SPEC_CONFIG 濡쒕뱶: {external_constants_path}")
                try:
                    # ?몃? ?뚯씪 ?쎌뼱??SPEC_CONFIG留?異붿텧
                    with open(external_constants_path, 'r', encoding='utf-8') as f:
                        constants_code = f.read()

                    # SPEC_CONFIG留?異붿텧?섍린 ?꾪빐 exec ?ㅽ뻾
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

                    Logger.debug(f" ???몃? SPEC_CONFIG 濡쒕뱶 ?꾨즺: {len(SPEC_CONFIG)}媛?洹몃９")
                    # ?붾쾭洹? 洹몃９ ?대쫫 異쒕젰
                    for i, g in enumerate(SPEC_CONFIG):
                        group_name = g.get('group_name', '?대쫫?놁쓬')
                        group_keys = [k for k in g.keys() if k not in ['group_name', 'group_id']]
                        Logger.debug(f"[SYSTEM DEBUG] 洹몃９ {i}: {group_name}, spec_id 媛쒖닔: {len(group_keys)}, spec_ids: {group_keys}")
                except Exception as e:
                    Logger.debug(f" ?좑툘 ?몃? CONSTANTS 濡쒕뱶 ?ㅽ뙣, 湲곕낯媛??ъ슜: {e}")
        # ===== ?몃? CONSTANTS 濡쒕뱶 ??=====

        # ===== ?몄뒪?댁뒪 蹂?섏뿉 ???(?ㅻⅨ 硫붿꽌?쒖뿉???ъ슜) =====
        self.LOADED_SPEC_CONFIG = SPEC_CONFIG
        self.url = url_value  # ???몃? CONSTANTS.py???뺤쓽??url??諛섏쁺
        self._original_base_url = str(url_value)  # ???ㅼ뿼 諛⑹???遺덈? 蹂듭궗蹂?
        if hasattr(self, 'url_text_box') and self.url:
            self.url_text_box.setText(self.url)
            
        self.auth_type = auth_type
        self.auth_info = auth_info
        # ===== ????꾨즺 =====

        # ===== ?붾쾭洹?濡쒓렇 異붽? =====
        Logger.debug(f"[SYSTEM DEBUG] SPEC_CONFIG 媛쒖닔: {len(SPEC_CONFIG)}")
        Logger.debug(f"[SYSTEM DEBUG] 李얠쓣 spec_id: {self.current_spec_id}")
        for i, group in enumerate(SPEC_CONFIG):
            Logger.debug(f"[SYSTEM DEBUG] Group {i} keys: {list(group.keys())}")
        # ===== ?붾쾭洹?濡쒓렇 ??=====

        config = {}
        # ===== ?섏젙: 濡쒕뱶??SPEC_CONFIG ?ъ슜 =====
        for group in SPEC_CONFIG:
            if self.current_spec_id in group:
                config = group[self.current_spec_id]
                break
        # ===== ?섏젙 ??=====

        if not config:
            raise ValueError(f"spec_id '{self.current_spec_id}'??????ㅼ젙??李얠쓣 ???놁뒿?덈떎!")
            return

        # ???ㅼ젙 ?뺣낫 異붿텧
        self.spec_description = config.get('test_name', 'Unknown Test')
        spec_names = config.get('specs', [])

        # ??trans_protocol, time_out, num_retries ???
        self.trans_protocols = config.get('trans_protocol', [])
        self.time_outs = config.get('time_out', [])
        self.num_retries_list = config.get('num_retries', [])

        if len(spec_names) < 3:
            raise ValueError(f"spec_id '{self.current_spec_id}'??specs ?ㅼ젙???щ컮瑜댁? ?딆뒿?덈떎! (理쒖냼 3媛??꾩슂)")

        Logger.info(f"Spec 濡쒕뵫 ?쒖옉: {self.spec_description} (ID: {self.current_spec_id})")

        # ?쒖뒪?쒖? response schema / request data ?ъ슜
        Logger.debug(f"紐⑤뱢: spec (?쇱꽌/諛붿씠???곸긽 ?듯빀)")

        # ===== PyInstaller ?섍꼍?먯꽌 ?몃? spec ?붾젆?좊━ ?곗꽑 濡쒕뱶 =====
        import sys
        import os

        if getattr(sys, 'frozen', False):
            # PyInstaller ?섍꼍: ?몃? spec ?붾젆?좊━ ?ъ슜
            exe_dir = os.path.dirname(sys.executable)
            external_spec_parent = exe_dir

            # ?몃? spec ?대뜑 ?뚯씪 議댁옱 ?뺤씤
            external_spec_dir = os.path.join(external_spec_parent, 'spec')
            Logger.debug(f"?몃? spec ?대뜑: {external_spec_dir}")
            Logger.debug(f"?몃? spec ?대뜑 議댁옱: {os.path.exists(external_spec_dir)}")
            if os.path.exists(external_spec_dir):
                files = [f for f in os.listdir(external_spec_dir) if f.endswith('.py')]
                Logger.debug(f"?몃? spec ?대뜑 .py ?뚯씪: {files}")

            # ?대? ?덈뜑?쇰룄 ?쒓굅 ??留??욎뿉 異붽? (?곗꽑?쒖쐞 蹂댁옣)
            if external_spec_parent in sys.path:
                sys.path.remove(external_spec_parent)
            sys.path.insert(0, external_spec_parent)
            Logger.debug(f"sys.path???몃? ?붾젆?좊━ 異붽?: {external_spec_parent}")

        # ===== 紐⑤뱢 罹먯떆 媛뺤젣 ??젣 =====
        # 二쇱쓽: 'spec' ?⑦궎吏 ?먯껜???좎? (parent ?⑦궎吏 ?꾩슂)
        module_names = [
            'spec.Data_request',
            'spec.Schema_response',
            'spec.Constraints_request'
        ]

        for mod_name in module_names:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
                Logger.debug(f"[SYSTEM SPEC] 紐⑤뱢 罹먯떆 ??젣: {mod_name}")
            else:
                Logger.debug(f"[SYSTEM SPEC] 紐⑤뱢 罹먯떆 ?놁쓬: {mod_name}")

        # spec ?⑦궎吏媛 ?놁쑝硫?鍮?紐⑤뱢濡??깅줉
        if 'spec' not in sys.modules:
            import types
            sys.modules['spec'] = types.ModuleType('spec')
            Logger.debug(f"鍮?'spec' ?⑦궎吏 ?앹꽦")
        # ===== 罹먯떆 ??젣 ??=====

        # PyInstaller ?섍꼍?먯꽌??importlib.util濡?紐낆떆?곸쑝濡??몃? ?뚯씪 濡쒕뱶
        import importlib
        if getattr(sys, 'frozen', False):
            import importlib.util

            # ?몃? spec ?뚯씪 寃쎈줈
            data_file = os.path.join(exe_dir, 'spec', 'Data_request.py')
            schema_file = os.path.join(exe_dir, 'spec', 'Schema_response.py')
            constraints_file = os.path.join(exe_dir, 'spec', 'Constraints_request.py')

            Logger.debug(f"紐낆떆??濡쒕뱶 ?쒕룄:")
            Logger.debug(f"  - Data: {data_file} (議댁옱: {os.path.exists(data_file)})")
            Logger.debug(f"  - Schema: {schema_file} (議댁옱: {os.path.exists(schema_file)})")
            Logger.debug(f"  - Constraints: {constraints_file} (議댁옱: {os.path.exists(constraints_file)})")

            # importlib.util濡?紐낆떆??濡쒕뱶
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

            Logger.debug(f"importlib.util濡??몃? ?뚯씪 濡쒕뱶 ?꾨즺")
        else:
            # ?쇰컲 ?섍꼍?먯꽌??湲곗〈 諛⑹떇 ?ъ슜
            import spec.Data_request as data_request_module
            import spec.Schema_response as schema_response_module
            import spec.Constraints_request as constraints_request_module

        # ===== spec ?뚯씪 寃쎈줈 諛??섏젙 ?쒓컙 濡쒓렇 =====
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
                Logger.debug(f"{name} 濡쒕뱶 寃쎈줈: {file_path}")
                Logger.debug(f"{name} ?섏젙 ?쒓컙: {mtime_str}")
            else:
                Logger.debug(f"{name} 濡쒕뱶 寃쎈줈: {file_path} (?뚯씪 ?놁쓬)")
        # ===== 濡쒓렇 ??=====

        # importlib.util濡?吏곸젒 濡쒕뱶?덉쑝誘濡?reload 遺덊븘??(?대? 理쒖떊 ?뚯씪 濡쒕뱶??
        # PyInstaller ?섍꼍???꾨땶 寃쎌슦?먮쭔 reload ?섑뻾
        if not getattr(sys, 'frozen', False):
            importlib.reload(data_request_module)
            importlib.reload(schema_response_module)
            importlib.reload(constraints_request_module)

        # ???쒖뒪?쒖? ?묐떟 寃利?+ ?붿껌 ?꾩넚 (outSchema/inData ?ъ슜)
        Logger.debug(f"??? ?묐떟 寃利?+ ?붿껌 ?꾩넚")
        Logger.debug(str(spec_names))
        # ??Response 寃利앹슜 ?ㅽ궎留?濡쒕뱶 (?쒖뒪?쒖씠 ?뚮옯?쇱쑝濡쒕???諛쏆쓣 ?묐떟 寃利? - outSchema
        self.videoOutSchema = getattr(schema_response_module, spec_names[0], [])

        # ??Request ?꾩넚???곗씠??濡쒕뱶 (?쒖뒪?쒖씠 ?뚮옯?쇱뿉寃?蹂대궪 ?붿껌) - inData
        self.videoInMessage = getattr(data_request_module, spec_names[1], [])
        self.videoMessages = getattr(data_request_module, spec_names[2], [])
        # ?쒖떆??API ?대쫫 (?レ옄 ?쒓굅)
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

        # ??Webhook 愿??(?꾩옱 誘몄궗??
        # self.videoWebhookSchema = []
        # self.videoWebhookData = []
        # self.videoWebhookInSchema = []
        # self.videoWebhookInData = []

        Logger.info(f"濡쒕뵫 ?꾨즺: {len(self.videoMessages)}媛?API")
        Logger.info(f"API 紐⑸줉: {self.videoMessages}")
        Logger.debug(f"?꾨줈?좎퐳 ?ㅼ젙: {self.trans_protocols}")
        self.webhook_schema_idx = 0

        # ??spec_config ???(URL ?앹꽦???꾩슂)
        self.spec_config = config
        
        # ??UI ?명솚?깆쓣 ?꾪빐 inSchema 蹂??留ㅽ븨 (?쒖뒪??寃利앹? ?묐떟 ?ㅽ궎留??ъ슜)
        self.inSchema = self.videoOutSchema

    def update_table_row_with_retries(self, row, result, pass_count, error_count, data, error_text, retries):
        """?뚯씠釉????낅뜲?댄듃 (?덉쟾??媛뺥솕)"""
        # ??1. 踰붿쐞 泥댄겕
        if row >= self.tableWidget.rowCount():
            Logger.debug(f"[TABLE UPDATE] 寃쎄퀬: row={row}媛 ?뚯씠釉?踰붿쐞瑜?踰쀬뼱??(珥?{self.tableWidget.rowCount()}??")
            return

        Logger.debug(f"[TABLE UPDATE] row={row}, result={result}, pass={pass_count}, error={error_count}, retries={retries}")

        # ??2. ?꾩씠肄??낅뜲?댄듃
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

        # ??3. 媛?而щ읆 ?낅뜲?댄듃 (?꾩씠?쒖씠 ?놁쑝硫??앹꽦)
        updates = [
            (3, str(retries)),  # 寃利??잛닔
            (4, str(pass_count)),  # ?듦낵 ?꾨뱶 ??
            (5, str(pass_count + error_count)),  # ?꾩껜 ?꾨뱶 ??
            (6, str(error_count)),  # ?ㅽ뙣 ?꾨뱶 ??
        ]

        for col, value in updates:
            item = self.tableWidget.item(row, col)
            if item is None:
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)
            else:
                item.setText(value)

        # ??4. ?됯? ?먯닔 ?낅뜲?댄듃
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

        # ??5. 硫붿떆吏 ???
        setattr(self, f"step{row + 1}_msg", msg)

        # ??6. UI 利됱떆 ?낅뜲?댄듃
        QApplication.processEvents()

        Logger.debug(f"[TABLE UPDATE] ?꾨즺: row={row}")

    def load_test_info_from_constants(self):
        # ??洹몃９紐낆씠 ??λ릺???덉쑝硫??ъ슜, ?놁쑝硫?spec_description ?ъ슜
        test_field = getattr(self, 'current_group_name', self.spec_description)

        return [
            ("湲곗뾽紐?, self.CONSTANTS.company_name),
            ("?쒗뭹紐?, self.CONSTANTS.product_name),
            ("踰꾩쟾", self.CONSTANTS.version),
            ("?쒗뿕?좏삎", self.CONSTANTS.test_category),
            ("?쒗뿕遺꾩빞", test_field),  # ??洹몃９紐??ъ슜
            ("?쒗뿕踰붿쐞", self.CONSTANTS.test_range),
            ("?ъ슜???몄쬆 諛⑹떇", self.auth_type),
            ("?쒗뿕 ?묒냽 ?뺣낫", self.url)
        ]

    def on_group_selected(self, row, col):
        group_name = self.index_to_group_name.get(row)
        if not group_name:
            return

        # ===== ?몃? 濡쒕뱶??SPEC_CONFIG ?ъ슜 (fallback: CONSTANTS 紐⑤뱢) =====
        SPEC_CONFIG = getattr(self, 'LOADED_SPEC_CONFIG', self.CONSTANTS.SPEC_CONFIG)
        selected_group = next(
            (g for g in SPEC_CONFIG if g.get("group_name") == group_name), None
        )
        # ===== ?섏젙 ??=====

        if selected_group:
            new_group_id = selected_group.get('group_id')
            old_group_id = getattr(self, 'current_group_id', None)

            Logger.debug(f" ?봽 洹몃９ ?좏깮: {old_group_id} ??{new_group_id}")

            # ??洹몃９??蹂寃쎈릺硫?current_spec_id 珥덇린??(?ㅼ쓬 ?쒕굹由ъ삤 ?좏깮 ??臾댁“嫄??ㅼ떆 濡쒕뱶?섎룄濡?
            if old_group_id != new_group_id:
                self.current_spec_id = None
                Logger.debug(f" ??洹몃９ 蹂寃쎌쑝濡?current_spec_id 珥덇린??)

            # ??洹몃９ ID ???
            self.current_group_id = new_group_id
            self.update_test_field_table(selected_group)

    def on_group_selected(self, row, col):
        """
        ???쒗뿕 洹몃９ ?좏깮 ???대떦 洹몃９???쒗뿕 遺꾩빞 紐⑸줉???먮룞 媛깆떊
        """
        # ?좏깮??洹몃９紐?媛?몄삤湲?
        if not hasattr(self, "index_to_group_name"):
            return

        group_name = self.index_to_group_name.get(row)
        if not group_name:
            return

        # ===== ?몃? 濡쒕뱶??SPEC_CONFIG ?ъ슜 (fallback: CONSTANTS 紐⑤뱢) =====
        SPEC_CONFIG = getattr(self, 'LOADED_SPEC_CONFIG', self.CONSTANTS.SPEC_CONFIG)
        # SPEC_CONFIG?먯꽌 ?좏깮??洹몃９ ?곗씠??李얘린
        selected_group = None
        for group_data in SPEC_CONFIG:
            if group_data.get("group_name") == group_name:
                selected_group = group_data
                break
        # ===== ?섏젙 ??=====

        if selected_group is None:
            Logger.warn(f" ?좏깮??洹몃９({group_name}) ?곗씠?곕? 李얠쓣 ???놁뒿?덈떎.")
            return

        # ??洹몃９ 蹂寃?媛먯? 諛?current_spec_id 珥덇린??
        new_group_id = selected_group.get('group_id')
        old_group_id = getattr(self, 'current_group_id', None)

        Logger.debug(f" ?봽 洹몃９ ?좏깮: {old_group_id} ??{new_group_id}")

        # ??洹몃９??蹂寃쎈릺硫?current_spec_id 珥덇린??(?ㅼ쓬 ?쒕굹由ъ삤 ?좏깮 ??臾댁“嫄??ㅼ떆 濡쒕뱶?섎룄濡?
        if old_group_id != new_group_id:
            self.current_spec_id = None
            Logger.debug(f" ??洹몃９ 蹂寃쎌쑝濡?current_spec_id 珥덇린??)

        # ??洹몃９ ID ???
        self.current_group_id = new_group_id

        # ?쒗뿕 遺꾩빞 ?뚯씠釉?媛깆떊
        self.update_test_field_table(selected_group)

    def on_test_field_selected(self, row, col):
        """?쒗뿕 遺꾩빞 ?대┃ ???대떦 ?쒖뒪?쒖쑝濡??숈쟻 ?꾪솚"""
        try:
            # ???쒗뿕 吏꾪뻾 以묒씠硫??쒕굹由ъ삤 蹂寃?李⑤떒
            if hasattr(self, 'sbtn') and not self.sbtn.isEnabled():
                Logger.debug(f" ?쒗뿕 吏꾪뻾 以?- ?쒕굹由ъ삤 蹂寃?李⑤떒")
                # 鍮꾨룞湲곕줈 寃쎄퀬李??쒖떆 (?쒗뿕 吏꾪뻾???곹뼢 ?녿룄濡?
                QTimer.singleShot(0, lambda: QMessageBox.warning(
                    self, "?뚮┝", "?쒗뿕??吏꾪뻾 以묒엯?덈떎.\n?쒗뿕 ?꾨즺 ???ㅻⅨ ?쒕굹由ъ삤瑜?吏꾪뻾?댁＜?몄슂."
                ))
                return

            self.selected_test_field_row = row

            if row in self.index_to_spec_id:
                new_spec_id = self.index_to_spec_id[row]

                if new_spec_id == self.current_spec_id:
                    Logger.debug(f" ?대? ?좏깮???쒕굹由ъ삤: {new_spec_id}")
                    return

                Logger.debug(f" ?봽 ?쒗뿕 遺꾩빞 ?꾪솚: {self.current_spec_id} ??{new_spec_id}")
                Logger.debug(f" ?꾩옱 洹몃９: {self.current_group_id}")

                # ??0. ?쇱떆?뺤? ?뚯씪? 媛??쒕굹由ъ삤蹂꾨줈 ?좎? (??젣?섏? ?딆쓬)

                # ??1. ?꾩옱 spec???뚯씠釉??곗씠?????(current_spec_id媛 None???꾨땺 ?뚮쭔)
                if self.current_spec_id is not None:
                    Logger.debug(f" ?곗씠???????- ?뚯씠釉????? {self.tableWidget.rowCount()}")
                    self.save_current_spec_data()
                else:
                    Logger.debug(f" ?좑툘 current_spec_id媛 None - ????ㅽ궢 (洹몃９ ?꾪솚 吏곹썑)")

                # ??2. spec_id ?낅뜲?댄듃
                self.current_spec_id = new_spec_id

                # ??3. spec ?곗씠???ㅼ떆 濡쒕뱶
                self.load_specs_from_constants()

                Logger.debug(f" 濡쒕뱶??API 媛쒖닔: {len(self.videoMessages)}")
                Logger.debug(f" API 紐⑸줉: {self.videoMessages}")

                # ??4. 湲곕낯 蹂??珥덇린??
                self.cnt = 0
                self.current_retry = 0
                self.message_error = []
                
                # ??4-1. ?뱁썒 愿??蹂??珥덇린??
                self.webhook_flag = False
                self.post_flag = False
                self.res = None
                self.webhook_schema_idx = 0

                # ??5. ?뚯씠釉??꾩쟾 ?ш뎄??
                Logger.debug(f" ?뚯씠釉??꾩쟾 ?ш뎄???쒖옉")
                self.update_result_table_structure(self.videoMessages)

                # ??6. ??λ맂 ?곗씠??蹂듭썝 ?쒕룄
                restored = self.restore_spec_data(new_spec_id)

                if not restored:
                    Logger.debug(f" ??λ맂 ?곗씠???놁쓬 - 珥덇린??)
                    # ?쒕굹由ъ삤蹂?紐⑤땲?곕쭅 濡쒓렇 蹂듭썝 ?뺤콉:
                    # ??λ맂 濡쒓렇媛 ?놁쑝硫??댁쟾 ?쒕굹由ъ삤 濡쒓렇瑜??④린吏 ?딄퀬 鍮꾩슫??
                    self.valResult.clear()
                    # ?먯닔 珥덇린??                    self.total_pass_cnt = 0
                    self.total_error_cnt = 0

                    # ??step_pass_counts? step_error_counts 諛곗뿴 珥덇린??
                    api_count = len(self.videoMessages)
                    self.step_pass_counts = [0] * api_count
                    self.step_error_counts = [0] * api_count
                    self.step_opt_pass_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?듦낵 ??
                    self.step_opt_error_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?먮윭 ??

                    # step_buffers 珥덇린??
                    self.step_buffers = [
                        {"data": "", "error": "", "result": "PASS", "raw_data_list": []} for _ in range(len(self.videoMessages))
                    ]
                else:
                    Logger.debug(f" ??λ맂 ?곗씠??蹂듭썝 ?꾨즺")

                # ??7. trace 諛?latest_events 珥덇린??
                self.trace.clear()
                self.latest_events = {}

                # ??8. ?ㅼ젙 ?ㅼ떆 濡쒕뱶
                self.get_setting()

                # ??9. ?됯? ?먯닔 ?붿뒪?뚮젅???낅뜲?댄듃
                self.update_score_display()

                # URL ?낅뜲?댄듃 (base_url + ?쒕굹由ъ삤紐? - ?ㅼ뿼 諛⑹?: CONSTANTS?먯꽌 吏곸젒 ?쎄린
                test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
                fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
                self.pathUrl = fresh_base_url.rstrip('/') + "/" + test_name
                self.url_text_box.setText(self.pathUrl)  # ?덈궡 臾멸뎄 蹂寃?
                Logger.debug(f" ?쒗뿕 URL ?낅뜲?댄듃: {self.pathUrl}")
                print(f"[SYSTEM DEBUG] on_test_field_selected?먯꽌 pathUrl ?ㅼ젙: {self.pathUrl}")

                # ??10. 寃곌낵 ?띿뒪??珥덇린??
                # self.append_monitor_log(
                #     step_name=f"?쒖뒪???꾪솚 ?꾨즺: {self.spec_description}",
                #     details=f"API 媛쒖닔: {len(self.videoMessages)}媛?| API 紐⑸줉: {', '.join(self.videoMessagesDisplay)}"
                # )

                Logger.debug(f" ???쒖뒪???꾪솚 ?꾨즺")

        except Exception as e:
            Logger.debug(f" ?쒗뿕 遺꾩빞 ?좏깮 泥섎━ ?ㅽ뙣: {e}")
            import traceback
            traceback.print_exc()

    def update_result_table_structure(self, api_list):
        """?뚯씠釉?援ъ“瑜??꾩쟾???ш뎄??(API 媛쒖닔??留욊쾶)"""
        api_count = len(api_list)
        Logger.debug(f" ?뚯씠釉??ш뎄???쒖옉: {api_count}媛?API")

        # ??1. ?뚯씠釉???媛쒖닔 ?ㅼ젙
        self.tableWidget.setRowCount(api_count)

        # ??2. 媛??됱쓣 ?꾩쟾??珥덇린??
        for row in range(api_count):
            api_name = api_list[row]
            # ?쒖떆???대쫫 (?レ옄 ?쒓굅)
            display_name = self._remove_api_number_suffix(api_name)

            # 而щ읆 0: No. (?レ옄)
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # 而щ읆 1: API 紐?(?レ옄 ?쒓굅)
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            Logger.debug(f" Row {row}: {display_name} ?ㅼ젙 ?꾨즺")

            # 而щ읆 2: 寃곌낵 ?꾩씠肄?
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

            # 而щ읆 3-7: 寃利??잛닔, ?듦낵/?꾩껜/?ㅽ뙣 ?꾨뱶 ?? ?됯? ?먯닔
            col_values = [
                (3, "0"),  # 寃利??잛닔
                (4, "0"),  # ?듦낵 ?꾨뱶 ??
                (5, "0"),  # ?꾩껜 ?꾨뱶 ??
                (6, "0"),  # ?ㅽ뙣 ?꾨뱶 ??
                (7, "0%")  # ?됯? ?먯닔
            ]

            for col, value in col_values:
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # 而щ읆 8: ?곸꽭 ?댁슜 踰꾪듉
            detail_label = QLabel()
            try:
                img_path = resource_path("assets/image/test_runner/btn_?곸꽭?댁슜?뺤씤.png").replace("\\", "/")
                pixmap = QPixmap(img_path)
                detail_label.setPixmap(pixmap)
                detail_label.setScaledContents(False)
                detail_label.setFixedSize(pixmap.size())
            except:
                detail_label.setText("?뺤씤")
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

            # ???믪씠 ?ㅼ젙
            self.tableWidget.setRowHeight(row, 40)

        Logger.debug(f" ?뚯씠釉??ш뎄???꾨즺: {self.tableWidget.rowCount()}媛???)

    def update_result_table_with_apis(self, api_list):
        """?쒗뿕 寃곌낵 ?뚯씠釉붿쓣 ?덈줈??API 紐⑸줉?쇰줈 ?낅뜲?댄듃"""
        api_count = len(api_list)
        self.tableWidget.setRowCount(api_count)

        # 媛??됱쓽 API 紐??낅뜲?댄듃
        for row in range(api_count):
            # No. (?レ옄) - 而щ읆 0
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # API 紐?- 而щ읆 1 (?レ옄 ?쒓굅)
            display_name = self.parent._remove_api_number_suffix(api_list[row])
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            # 寃곌낵 ?꾩씠肄?- 而щ읆 2
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

            # 寃利??잛닔, ?듦낵 ?꾨뱶 ?? ?꾩껜 ?꾨뱶 ?? ?ㅽ뙣 ?꾨뱶 ?? ?됯? ?먯닔 - 而щ읆 3-7
            for col in range(3, 8):
                item = QTableWidgetItem("0" if col != 7 else "0%")
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # ?곸꽭 ?댁슜 踰꾪듉 - 而щ읆 8
            detail_btn = QPushButton("?곸꽭 ?댁슜 ?뺤씤")
            detail_btn.setMaximumHeight(30)
            detail_btn.setMaximumWidth(130)
            detail_btn.clicked.connect(lambda checked, r=row: self.show_combined_result(r))

            # 踰꾪듉??以묒븰??諛곗튂?섍린 ?꾪븳 ?꾩젽怨??덉씠?꾩썐
            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_btn)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 8, container)

            # ???믪씠 ?ㅼ젙
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
        # self.r2 == "None"?대㈃ 洹몃?濡?None

        try:
            json_data_dict = json.loads(json_data.decode('utf-8'))
            trans_protocol = json_data_dict.get("transProtocol", {})    # ??遺遺??섏젙?댁빞??
            if trans_protocol:
                # ?뱁썒 ?쒕쾭 ?쒖옉 (transProtocolType??WebHook??寃쎌슦留?
                if "WebHook" == self.spec_config.get('trans_protocol', self.current_spec_id)[self.cnt]:
                    self.webhook_flag = True
                    time.sleep(0.001)
                    url = CONSTANTS.WEBHOOK_HOST  # ??湲곕낯媛??섏젙
                    port = CONSTANTS.WEBHOOK_PORT  # ???ы듃??2001濡?

                    msg = {}
                    self.step_buffers[self.cnt]["is_webhook_api"] = True

                    self.webhook_cnt = self.cnt
                    self.webhook_thread = WebhookThread(url, port, msg)
                    self.webhook_thread.result_signal.connect(self.handle_webhook_result)
                    self.webhook_thread.start()
                    # ?쒕쾭媛 ?꾩쟾??以鍮꾨맆 ?뚭퉴吏 ?湲?(理쒕? 15珥?
                    ready = self.webhook_thread.server_ready.wait(timeout=15)
                    if not ready:
                        Logger.error("[Webhook] ?쒕쾭 以鍮???꾩븘??- POST ?꾩넚 痍⑥냼")
                else:
                    # WebHook???꾨땶 寃쎌슦 ?뚮옒洹?珥덇린??
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

    # ?꾩떆 ?섏젙 
    def handle_webhook_result(self, result):
        self.webhook_res = result
        self.webhook_thread.stop()
        self._push_event(self.webhook_cnt, "WEBHOOK", result)

    # ?뱁썒 寃利?
    def get_webhook_result(self):
        # ???뱁썒 ?ㅽ궎留덇? ?놁쑝硫?寃利앺븯吏 ?딆쓬
        if self.cnt >= len(self.webhookSchema) or not self.webhookSchema[self.cnt]:
            Logger.debug(f" API {self.cnt}???뱁썒 ?ㅽ궎留덇? ?놁쓬 - 寃利?嫄대꼫?")
            self.webhook_flag = False
            return
        
        # ???뱁썒 ?묐떟??null??寃쎌슦?먮룄 寃利앹쓣 ?섑뻾?섏뿬 ?ㅽ뙣濡?移댁슫??
        # None?닿굅??鍮?媛믪씤 寃쎌슦 鍮??뺤뀛?덈━濡?泥섎━
        webhook_data = self.webhook_res if self.webhook_res else {}
        tmp_webhook_res = json.dumps(webhook_data, indent=4, ensure_ascii=False) if webhook_data else "null"
        
        if self.webhook_cnt < len(self.message):
            message_name = "step " + str(self.webhook_cnt + 1) + ": " + self.message[self.webhook_cnt]
        else:
            message_name = f"step {self.webhook_cnt + 1}: (index out of range)"

        # ???붾쾭源? ?뱁썒 ?대깽???ㅽ궎留?寃利?(泥??몄텧?먮쭔 異쒕젰)
        if not hasattr(self, '_webhook_debug_printed'):
            self._webhook_debug_printed = True
            Logger.debug(f"\n========== ?뱁썒 ?대깽??寃利??붾쾭源?==========")
            webhook_api = self.message[self.webhook_cnt] if self.webhook_cnt < len(self.message) else 'N/A'
            Logger.debug(f"webhook_cnt={self.webhook_cnt}, API={webhook_api}")
            Logger.debug(f"webhookSchema 珥?媛쒖닔={len(self.webhookSchema)}")
            Logger.debug(f"webhook_res is None: {self.webhook_res is None}")

        schema_to_check = self.webhookSchema[self.cnt]

        # 狩?異붽?: webhook_res媛 None?대㈃ timeout 泥섎━
        if self.webhook_res is None:
            # timeout_field_finder濡??ㅽ궎留덉쓽 ?꾨뱶 媛쒖닔 怨꾩궛
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
            # ???뺤긽?곸쑝濡?webhook ?곗씠?곌? ?덈뒗 寃쎌슦 寃利?
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

        # ?뱁썒 ?섏떊 payload瑜??ㅼ떆媛?紐⑤땲?곕쭅??[?섏떊]?쇰줈 ?쒖떆
        self.append_monitor_log(
            step_name=f"?뱁썒 ?대깽?? {display_name}",
            request_json=tmp_webhook_res,
            direction="RECV"
        )

        # ?뱁썒 ACK ?묐떟 payload瑜??ㅼ떆媛?紐⑤땲?곕쭅??[?≪떊]?쇰줈 ?쒖떆
        if self.webhook_res is not None:
            webhook_ack_payload = {"code": "200", "message": "?깃났"}
            self.append_monitor_log(
                step_name=f"?뱁썒 ?묐떟: {display_name}",
                request_json=json.dumps(webhook_ack_payload, indent=4, ensure_ascii=False),
                direction="SEND"
            )

        # ??step_pass_counts 諛곗뿴???뱁썒 寃곌낵 異붽? (諛곗뿴???놁쑝硫??앹꽦?섏? ?딆쓬)
        # ?먯닔 ?낅뜲?댄듃??紐⑤뱺 ?ъ떆???꾨즺 ?꾩뿉 ?쇨큵 泥섎━??(?뚮옯?쇨낵 ?숈씪)

        # ???먯닔???쒖떆?섏? ?딆쓬 (?ъ떆???꾨즺 ?꾩뿉留??쒖떆)
        # ?됯? ?먯닔 ?붿뒪?뚮젅???낅뜲?댄듃???ъ떆???꾨즺 ?쒖뿉留??몄텧

        if val_result == "PASS":
            msg = "\n" + tmp_webhook_res + "\n\n" + "Result: " + val_text + "\n"
            img = self.img_pass
        else:
            msg = "\n" + tmp_webhook_res + "\n\n" + "Result: " + val_result + "\nResult details:\n" + val_text + "\n"
            img = self.img_fail

        # ???뱁썒 寃利?寃곌낵瑜?湲곗〈 ?꾩쟻 ?꾨뱶 ?섏뿉 異붽?
        if self.webhook_cnt < self.tableWidget.rowCount():
            # 湲곗〈 ?꾩쟻 ?꾨뱶 ??媛?몄삤湲?
            if hasattr(self, 'step_pass_counts') and hasattr(self, 'step_error_counts'):
                # ???뱁썒 寃곌낵瑜?湲곗〈 step_pass_counts??異붽? (inbound + webhook)
                self.step_pass_counts[self.webhook_cnt] += key_psss_cnt
                self.step_error_counts[self.webhook_cnt] += key_error_cnt

                # 狩??좏깮 ?꾨뱶 ?⑹궛
                if hasattr(self, 'step_opt_pass_counts') and hasattr(self, 'step_opt_error_counts'):
                    self.step_opt_pass_counts[self.webhook_cnt] += opt_correct
                    self.step_opt_error_counts[self.webhook_cnt] += opt_error

                # ?꾩쟻??珥??꾨뱶 ?섎줈 ?뚯씠釉??낅뜲?댄듃
                accumulated_pass = self.step_pass_counts[self.webhook_cnt]
                accumulated_error = self.step_error_counts[self.webhook_cnt]

                Logger.debug(f" ?꾩쟻 寃곌낵: pass={accumulated_pass}, error={accumulated_error}")
            else:
                # ?꾩쟻 諛곗뿴???놁쑝硫??뱁썒 寃곌낵留??ъ슜
                accumulated_pass = key_psss_cnt
                accumulated_error = key_error_cnt

            if self.webhook_cnt < len(self.num_retries_list):
                current_retries = self.num_retries_list[self.webhook_cnt]
            else:
                current_retries = 1

            result_step_title = f"寃곌낵: {display_name} - ?뱁썒 ?대깽???곗씠??({self.current_retry + 1}/{current_retries})"
            total_fields = accumulated_pass + accumulated_error
            score_value = (accumulated_pass / total_fields * 100) if total_fields > 0 else 0
            result_details = (
                f"?듦낵 ?꾨뱶 ?? {accumulated_pass}, ?ㅽ뙣 ?꾨뱶 ?? {accumulated_error} | ?ㅼ떆媛?硫붿떆吏: WebHook"
            )
            if val_result == "FAIL":
                result_details += f" | ?곸꽭: {to_detail_text(val_text)}"

            self.append_monitor_log(
                step_name=result_step_title,
                request_json="",
                result_status=val_result,
                score=score_value,
                details=result_details,
                direction="RECV"
            )

                # ?꾩쟻???꾨뱶 ?섎줈 ?뚯씠釉??낅뜲?댄듃
            self.update_table_row_with_retries(
                self.webhook_cnt, val_result, accumulated_pass, accumulated_error,
                tmp_webhook_res, to_detail_text(val_text), current_retries
            )

        # step_buffers ?낅뜲?댄듃 異붽? (?ㅼ떆媛?紐⑤땲?곕쭅怨??곸꽭蹂닿린 ?쇱튂)
        if self.webhook_cnt < len(self.step_buffers):
            webhook_data_text = tmp_webhook_res
            update_webhook_step_buffer_fields(
                step_buffer=self.step_buffers[self.webhook_cnt],
                webhook_data=webhook_data,
                webhook_error_text=to_detail_text(val_text) if val_result == "FAIL" else "오류가 없습니다.",
                webhook_pass_cnt=key_psss_cnt,
                webhook_total_cnt=(key_psss_cnt + key_error_cnt),
            )
            webhook_error_text = to_detail_text(val_text) if val_result == "FAIL" else "?ㅻ쪟媛 ?놁뒿?덈떎."
            # ???뱁썒 ?대깽???곗씠?곕? 紐낇솗???쒖떆
            self.step_buffers[self.webhook_cnt]["data"] += f"\n\n--- Webhook ?대깽???곗씠??---\n{webhook_data_text}"
            self.step_buffers[self.webhook_cnt][
                "error"] += f"\n\n--- Webhook 寃利?---\n{webhook_error_text}"  # ?섍? 臾몄젣???붾뵳吏媛 ?쒕떎
            self.step_buffers[self.webhook_cnt]["result"] = val_result

            # 硫붿떆吏 ???
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

            # cnt媛 由ъ뒪??湲몄씠 ?댁긽?대㈃ 醫낅즺 泥섎━ (臾댄븳 諛섎났 諛⑹?)
            if self.cnt >= len(self.message) or self.cnt >= len(self.time_outs):
                self.tick_timer.stop()
                self.valResult.append("?쒗뿕???꾨즺?섏뿀?듬땲??")
                self.cnt = 0
                return
            # ?뚮옯?쇨낵 ?숈씪?섍쾶 time_pre/cnt_pre 議곌굔 ?곸슜
            if self.time_pre == 0 or self.cnt != self.cnt_pre:
                self.time_pre = time.time()
                self.cnt_pre = self.cnt
                return  # 泥??깆뿉?쒕뒗 ?湲곕쭔 ?섍퀬 由ы꽩
            else:
                time_interval = time.time() - self.time_pre

            # ?뱁썒 ?대깽???섏떊 ?뺤씤 - webhook_thread.wait()???대? ?숆린??泥섎━?섎?濡?蹂꾨룄 sleep 遺덊븘??
            if self.webhook_flag is True:
                api_name = self.message[self.cnt] if self.cnt < len(self.message) else 'N/A'
                Logger.debug(f"?뱁썒 ?대깽???섏떊 ?꾨즺 (API: {api_name})")
                if self.webhook_res != None:
                    Logger.warn(f" ?뱁썒 硫붿떆吏 ?섏떊")
                    # ????대㉧ ?쇱씤 ?쒓굅
                    self.update_last_line_timer("", remove=True)
                elif math.ceil(time_interval) >= self.time_outs[self.cnt] / 1000 - 1:
                    Logger.warn(f" 硫붿떆吏 ??꾩븘?? ?뱁썒 ?湲?醫낅즺")
                    # ????대㉧ ?쇱씤 ?쒓굅
                    self.update_last_line_timer("", remove=True)
                else :
                    # ???湲??쒓컙 ??대㉧ ?쒖떆 (留덉?留?以?媛깆떊)
                    remaining = max(0, int((self.time_outs[self.cnt] / 1000) - time_interval))
                    self.update_last_line_timer(f"?⑥? ?湲??쒓컙: {remaining}珥?)
                    
                    Logger.debug(f" ?뱁썒 ?湲?以?.. (API {self.cnt}) ??꾩븘??{round(time_interval)} /{round(self.time_outs[self.cnt] / 1000)}")
                    return
            if (self.post_flag is False and
                    self.processing_response is False and
                    self.cnt < len(self.message) and
                    self.cnt < len(self.num_retries_list) and
                    self.current_retry < self.num_retries_list[self.cnt]):

                self.message_in_cnt += 1
                self.time_pre = time.time()

                retry_info = f" (?쒕룄 {self.current_retry + 1}/{self.num_retries_list[self.cnt]})"
                if self.cnt < len(self.message):
                    display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else self.message[self.cnt]
                    self.message_name = "step " + str(self.cnt + 1) + ": " + display_name + retry_info
                else:
                    self.message_name = f"step {self.cnt + 1}: (index out of range)" + retry_info

                # 泥?踰덉㎏ ?쒕룄???뚮쭔 硫붿떆吏 ?쒖떆 - ?쒓굅 (?묐떟 泥섎━ ???쒖떆)
                # if self.current_retry == 0:
                #     self.append_monitor_log(
                #         step_name=self.message_name
                #     )

                # ?쒖뒪?쒖? ?붿껌 ?≪떊 硫붿떆吏 ?쒖떆 ????(?묐떟留??쒖떆)
                # self.append_monitor_log(
                #     step_name=f"?붿껌 硫붿떆吏 ?≪떊 [{self.current_retry + 1}/{self.num_retries_list[self.cnt]}]",
                #     result_status="吏꾪뻾以?
                # )

                if self.cnt == 0 and self.current_retry == 0:
                    self.tmp_msg_append_flag = True

                # ?쒖뒪?쒖씠 ?뚮옯?쇱뿉 ?붿껌 ?꾩넚
                current_timeout = self.time_outs[self.cnt] / 1000 if self.cnt < len(self.time_outs) else 5.0
                api_endpoint = self.message[self.cnt] if self.cnt < len(self.message) else ""
                
                # ??URL ?ㅼ뿼 諛⑹?: pathUrl??留ㅻ쾲 源⑤걮??base濡??ш뎄??
                fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
                    base_with_scenario = fresh_base_url.rstrip('/') + "/" + test_name
                else:
                    base_with_scenario = fresh_base_url.rstrip('/')
                
                # API ?붾뱶?ъ씤??異붽?
                api_path = api_endpoint.lstrip('/')
                path = f"{base_with_scenario}/{api_path}"
                print(f"[SYSTEM DEBUG] update_view?먯꽌 API ?몄텧 寃쎈줈: {path}")
                print(f"[SYSTEM DEBUG] fresh_base_url: {fresh_base_url}, base_with_scenario: {base_with_scenario}, api_path: {api_path}")

                # ???ㅼ떆媛?API 寃쎈줈 ?쒖떆 (留ㅻ쾲 ?덈줈 ?앹꽦??path瑜??ъ슜?섎?濡??꾩쟻?섏? ?딆쓬)
                if hasattr(self, 'url_text_box'):
                    self.url_text_box.setText(path) 
                
                inMessage = self.inMessage[self.cnt] if self.cnt < len(self.inMessage) else {}
                # ??Data Mapper ?곸슜 - ?댁쟾 ?묐떟 ?곗씠?곕줈 ?붿껌 ?낅뜲?댄듃
                # generator???대? self.latest_events瑜?李몄“?섍퀬 ?덉쑝誘濡??ы븷??遺덊븘??
                Logger.debug(f"[MAPPER] latest_events ?곹깭: {list(self.latest_events.keys())}")
                inMessage = self._apply_request_constraints(inMessage, self.cnt)

                trans_protocol = inMessage.get("transProtocol", {})
                if trans_protocol:
                    trans_protocol_type = trans_protocol.get("transProtocolType", {})
                    if "WebHook".lower() in str(trans_protocol_type).lower():

                        # ?뚮옯?쇱씠 ?뱁썒??蹂대궪 ?몃? 二쇱냼 ?ㅼ젙 - ?숈쟻
                        WEBHOOK_IP = CONSTANTS.WEBHOOK_PUBLIC_IP  # ?뱁썒 ?섏떊 IP/?꾨찓??
                        WEBHOOK_PORT = CONSTANTS.WEBHOOK_PORT  # ?뱁썒 ?섏떊 ?ы듃
                        WEBHOOK_URL = f"https://{WEBHOOK_IP}:{WEBHOOK_PORT}"  # ?뚮옯???쒖뒪?쒖씠 ?뱁썒??蹂대궪 二쇱냼

                        trans_protocol = {
                            "transProtocolType": "WebHook",
                            "transProtocolDesc": WEBHOOK_URL
                        }
                        
                        # ngrok ?섎뱶 肄붾뵫 遺遺?(01/09)
                        # ---- ?ш린遺??
                        # WEBHOOK_DISPLAY_URL = CONSTANTS.WEBHOOK_DISPLAY_URL
                        # trans_protocol = {
                        #     "transProtocolType": "WebHook",
                        #     "transProtocolDesc": WEBHOOK_DISPLAY_URL  # ngrok 二쇱냼 ?꾩넚
                        # }
                        #---- ?ш린源뚯?
                        inMessage["transProtocol"] = trans_protocol

                        # (01/08 - ?숈쟻: ?꾩뿉 ?묐룞, ?섎뱶肄붾뵫: ?꾨옒瑜??묐룞)
                        Logger.debug(f" [post] transProtocol ?ㅼ젙 異붽??? {inMessage}")
                        # Logger.debug(f" [post] transProtocol ?ㅼ젙 (ngrok 二쇱냼): {WEBHOOK_DISPLAY_URL}")
                        
                elif self.r2 == "B" and self.message[self.cnt] == "Authentication":
                    inMessage["userID"] = self.accessInfo[0]
                    inMessage["userPW"] = self.accessInfo[1]

                json_data = json.dumps(inMessage).encode('utf-8')

                # ??REQUEST 湲곕줉 ?쒓굅 - ?쒕쾭(api_server.py)?먯꽌留?湲곕줉?섎룄濡?蹂寃?
                self._push_event(self.cnt, "REQUEST", inMessage)

                api_name = self.message[self.cnt] if self.cnt < len(self.message) else ""
                if api_name and isinstance(inMessage, dict):
                    self.reference_context[f"/{api_name}"] = inMessage

                # ?쒖꽌 ?뺤씤??濡쒓렇
                api_name = self.message[self.cnt] if self.cnt < len(self.message) else 'index out of range'
                Logger.debug(f"?뚮옯?쇱뿉 ?붿껌 ?꾩넚: {api_name} (?쒕룄 {self.current_retry + 1})")

                # ???≪떊 硫붿떆吏 ?ㅼ떆媛?紐⑤땲?곕쭅 濡쒓렇 異붽? (SEND)
                display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                self.append_monitor_log(
                    step_name=display_name,
                    request_json=json.dumps(inMessage, indent=4, ensure_ascii=False),
                    direction="SEND"
                )

                t = threading.Thread(target=self.post, args=(path, json_data, current_timeout), daemon=True)
                t.start()
                self.post_flag = True

            # timeout 議곌굔? ?묐떟 ?湲??ъ떆???먮떒?먮쭔 ?ъ슜
            elif self.cnt < len(self.time_outs) and time_interval >= self.time_outs[
                self.cnt] / 1000 and self.post_flag is True:

                if self.cnt < len(self.message):
                    self.message_error.append([self.message[self.cnt]])
                else:
                    self.message_error.append([f"index out of range: {self.cnt}"])
                self.message_in_cnt = 0
                current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1

                # ?꾩옱 ?쒕룄???????꾩븘??泥섎━
                if self.cnt < len(self.outSchema):
                    tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(self.outSchema[self.cnt])
                else:
                    tmp_fields_rqd_cnt, tmp_fields_opt_cnt = 0, 0

                # ???뱁썒 API??寃쎌슦 ?뱁썒 ?ㅽ궎留??꾨뱶 ?섎룄 異붽?
                if self.cnt < len(self.trans_protocols):
                    current_protocol = self.trans_protocols[self.cnt]
                    if current_protocol == "WebHook" and self.cnt < len(self.webhookSchema):
                        webhook_schema = self.webhookSchema[self.cnt]
                        if webhook_schema:
                            webhook_rqd_cnt, webhook_opt_cnt = timeout_field_finder(webhook_schema)
                            tmp_fields_rqd_cnt += webhook_rqd_cnt
                            tmp_fields_opt_cnt += webhook_opt_cnt
                            Logger.debug(f" ?뱁썒 ?ㅽ궎留??꾨뱶 異붽?: rqd={webhook_rqd_cnt}, opt={webhook_opt_cnt}")

                add_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                if self.flag_opt:
                    add_err += tmp_fields_opt_cnt

                total_fields = self.total_pass_cnt + self.total_error_cnt
                if total_fields > 0:
                    score_value = (self.total_pass_cnt / total_fields) * 100
                else:
                    score_value = 0
                
                # ??꾩븘??濡쒓렇瑜?HTML 移대뱶濡?異쒕젰
                api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                timeout_sec = self.time_outs[self.cnt] / 1000 if self.cnt < len(self.time_outs) else 0
                self.append_monitor_log(
                    step_name=f"?쒗뿕 API: {api_name}",
                    request_json="",
                    score=score_value,
                    details=f"?깍툘 Timeout ({timeout_sec}珥? - Message Missing! (?쒕룄 {self.current_retry + 1}/{current_retries}) | ?듦낵 ?꾨뱶 ?? {self.total_pass_cnt}, ?ㅽ뙣 ?꾨뱶 ?? {self.total_error_cnt}"
                )

                # ?ъ떆??移댁슫??利앷?
                self.current_retry += 1
                self.update_table_row_with_retries(
                    self.cnt,
                    "吏꾪뻾以?,  # ??寃?뺤깋 ?꾩씠肄?
                    0, 0,  # ???꾩쭅 寃곌낵 ?놁쓬
                    "寃利?吏꾪뻾以?..",
                    f"?쒕룄 {self.current_retry }/{current_retries}",
                    self.current_retry   # ??寃利??잛닔: 1, 2, 3...
                )
                QApplication.processEvents()  # UI 利됱떆 諛섏쁺

                # ?ъ떆???꾨즺 ?щ? ?뺤씤
                if (self.cnt < len(self.num_retries_list) and
                        self.current_retry >= self.num_retries_list[self.cnt]):
                    # 紐⑤뱺 ?ъ떆???꾨즺 - 踰꾪띁??理쒖쥌 寃곌낵 ???
                    self.step_buffers[self.cnt]["data"] = "??꾩븘?껋쑝濡??명빐 ?섏떊???곗씠?곌? ?놁뒿?덈떎."
                    current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                    self.step_buffers[self.cnt]["error"] = f"Message Missing! - 紐⑤뱺 ?쒕룄({current_retries}???먯꽌 ??꾩븘??諛쒖깮"
                    self.step_buffers[self.cnt]["result"] = "FAIL"
                    self.step_buffers[self.cnt]["events"] = list(self.trace.get(self.cnt, []))

                    # ??step_pass_counts 諛곗뿴?????(諛곗뿴???덈뒗 寃쎌슦?먮쭔)
                    if hasattr(self, 'step_pass_counts') and self.cnt < len(self.step_pass_counts):
                        self.step_pass_counts[self.cnt] = 0
                        self.step_error_counts[self.cnt] = add_err
                    
                    # ???꾩껜 ?먯닔 ?낅뜲?댄듃 (紐⑤뱺 spec ?⑹궛)
                    self.global_error_cnt += add_err
                    self.global_pass_cnt += 0

                    # ?됯? ?먯닔 ?붿뒪?뚮젅???낅뜲?댄듃
                    self.update_score_display()
                    # ?뚯씠釉??낅뜲?댄듃 (Message Missing)
                    self.update_table_row_with_retries(self.cnt, "FAIL", 0, add_err, "", "Message Missing!",
                                                       current_retries)

                    # ?ㅼ쓬 API濡??대룞
                    self.cnt += 1
                    self.current_retry = 0  # ?ъ떆??移댁슫??由ъ뀑
                    self.webhook_flag = False

                    # ?ㅼ쓬 API瑜??꾪븳 ?꾩쟻 移댁슫??珥덇린 ?ㅼ젙 ?뺤씤
                    if hasattr(self, 'step_pass_counts') and self.cnt < len(self.step_pass_counts):
                        self.step_pass_counts[self.cnt] = 0
                        self.step_error_counts[self.cnt] = 0
                        # ??諛곗뿴 踰붿쐞 泥댄겕 異붽?
                        if self.cnt < len(self.step_pass_flags):
                            self.step_pass_flags[self.cnt] = 0

                self.message_in_cnt = 0
                self.post_flag = False
                self.processing_response = False

                # ?뚮옯?쇨낵 ?숈씪???湲??쒓컙 ?ㅼ젙
                self.time_pre = time.time()

                if self.cnt >= len(self.message):
                    self.tick_timer.stop()
                    self.valResult.append("?쒗뿕???꾨즺?섏뿀?듬땲??")

                    # ???꾩옱 spec ?곗씠?????
                    self.save_current_spec_data()

                    self.processing_response = False
                    self.post_flag = False

                    self.cnt = 0
                    self.current_retry = 0

                    # 理쒖쥌 由ы룷???앹꽦
                    total_fields = self.total_pass_cnt + self.total_error_cnt

                    # ??JSON 寃곌낵 ?먮룞 ???異붽?
                    Logger.debug(f" ?됯? ?꾨즺 - ?먮룞 ????쒖옉")
                    try:
                        self.run_status = "?꾨즺"
                        result_json = build_result_json(self)
                        url = f"{CONSTANTS.management_url}/api/integration/test-results"
                        response = requests.post(url, json=result_json)
                        Logger.debug(f"?쒗뿕 寃곌낵 ?꾩넚 ?곹깭 肄붾뱶: {response.status_code}")
                        Logger.debug(f"?쒗뿕 寃곌낵 ?꾩넚 ?묐떟: {response.text}")
                        json_path = os.path.join(result_dir, "response_results.json")
                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump(result_json, f, ensure_ascii=False, indent=2)
                        Logger.debug(f"???쒗뿕 寃곌낵媛 '{json_path}'???먮룞 ??λ릺?덉뒿?덈떎.")
                        self.append_monitor_log(
                            step_name="愿由ъ떆?ㅽ뀥 寃곌낵 ?꾩넚 ?꾨즺",
                            details=""
                        )
                        Logger.debug(f" try 釉붾줉 ?뺤긽 ?꾨즺")

                    except Exception as e:
                        Logger.debug(f"??JSON ???以??ㅻ쪟 諛쒖깮: {e}")
                        import traceback
                        traceback.print_exc()
                        self.valResult.append(f"\n寃곌낵 ????ㅽ뙣: {str(e)}")
                        Logger.debug(f" except 釉붾줉 ?ㅽ뻾??)

                    finally:
                        # ???됯? ?꾨즺 ???쇱떆?뺤? ?뚯씪 ?뺣━ (?먮윭 諛쒖깮 ?щ?? 臾닿??섍쾶 ??긽 ?ㅽ뻾)
                        Logger.debug(f" ========== finally 釉붾줉 吏꾩엯 ==========")
                        self.cleanup_paused_file()
                        Logger.debug(f" ========== finally 釉붾줉 醫낅즺 ==========")
                        
                        # stop/pause ?섎룄媛 ?덉쑝硫?completed ?꾩넚 湲덉?
                        if not getattr(self, "is_paused", False):
                            try:
                                api_client = APIClient()
                                api_client.send_heartbeat_completed()
                                Logger.info(f"???쒗뿕 ?꾨즺 - completed ?곹깭 ?꾩넚 ?꾨즺")
                            except Exception as e:
                                Logger.warning(f"?좑툘 ?쒗뿕 ?꾨즺 - completed ?곹깭 ?꾩넚 ?ㅽ뙣: {e}")
                        else:
                            Logger.info("??툘 ?쇱떆?뺤? ?곹깭?대?濡?completed heartbeat ?꾩넚 ?앸왂")

                    self.sbtn.setEnabled(True)
                    self.stop_btn.setDisabled(True)
                    self.cancel_btn.setDisabled(True)


            # ?묐떟???꾩갑??寃쎌슦 泥섎━
            elif self.post_flag == True:
                if self.res is None:
                    # ???湲??쒓컙 ??대㉧ ?쒖떆 (留덉?留?以?媛깆떊)
                    current_timeout = self.time_outs[self.cnt] / 1000 if self.cnt < len(self.time_outs) else 5.0
                    remaining = max(0, int(current_timeout - time_interval))
                    self.update_last_line_timer(f"?⑥? ?湲??쒓컙: {remaining}珥?)

                if self.res != None:
                    # ???묐떟 ?섏떊 ?꾨즺 - ??대㉧ ?쇱씤 ?쒓굅 (?뱁썒 ?湲곌? ?꾨땺 ?뚮쭔)
                    if not self.webhook_flag:
                        self.update_last_line_timer("", remove=True)
                    
                    # ?묐떟 泥섎━ ?쒖옉
                    if self.res != None:
                        # ?묐떟 泥섎━ ?쒖옉
                        self.processing_response = True

                        # ?쒖뒪?쒖? step 硫붿떆吏? ?묐떟 ?섏떊 硫붿떆吏 ?쒖떆 ????(諛쏆? ?곗씠?곕쭔 ?쒖떆)
                        # if self.cnt == 0 or self.tmp_msg_append_flag:
                        #     self.append_monitor_log(
                        #         step_name=self.message_name,
                        #         result_status="吏꾪뻾以?
                        #     )

                        # self.append_monitor_log(
                        #     step_name=f"?묐떟 硫붿떆吏 ?섏떊 [{self.current_retry + 1}/{self.num_retries_list[self.cnt]}]",
                        #     result_status="吏꾪뻾以?
                        # )

                        res_data = self.res.text

                        try:
                            res_data = json.loads(res_data)

                            if isinstance(res_data, dict) and "code_value" in res_data:
                                del res_data["code_value"]

                        except Exception as e:
                            self._append_text(f"?묐떟 JSON ?뚯떛 ?ㅻ쪟: {e}")
                            self._append_text({"raw_response": self.res.text})
                            #self.post_flag = False
                            #self.processing_response = False
                            #self.current_retry += 1
                            self.res.txt = {}
                            #return

                        # ??RESPONSE 湲곕줉 ?쒓굅 - ?쒕쾭(api_server.py)?먯꽌留?湲곕줉?섎룄濡?蹂寃?
                        self._push_event(self.cnt, "RESPONSE", res_data)

                        # ?꾩옱 ?ъ떆???뺣낫
                        current_retries = self.num_retries_list[self.cnt] if self.cnt < len(
                            self.num_retries_list) else 1
                        current_protocol = self.trans_protocols[self.cnt] if self.cnt < len(
                            self.trans_protocols) else "Unknown"

                        # ?⑥씪 ?묐떟?????寃利?泥섎━
                        from core.utils import replace_transport_desc_for_display
                        tmp_res_auth = json.dumps(res_data, indent=4, ensure_ascii=False)
                        tmp_res_auth = replace_transport_desc_for_display(tmp_res_auth)  # UI ?쒖떆??移섑솚

                        # ?ㅼ떆媛?紐⑤땲?곕쭅 李쎌뿉 ?묐떟 ?곗씠???쒖떆
                        # 泥?踰덉㎏ ?묐떟???뚮쭔 API 紐낃낵 寃利??덉젙 ?잛닔 ?쒖떆
                        if self.current_retry == 0:
                            api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                            display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                            self.append_monitor_log(
                                step_name=f"?쒗뿕 API: {display_name} ({self.current_retry + 1}/{current_retries})",
                                details=f"珥?{current_retries}??寃利??덉젙",
                                request_json=tmp_res_auth,
                                direction="RECV"
                            )
                        else:
                            # 2?뚯감 ?댁긽: API 紐낃낵 ?뚯감留??쒖떆
                            api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                            display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                            self.append_monitor_log(
                                step_name=f"?쒗뿕 API: {display_name} ({self.current_retry + 1}/{current_retries})",
                                request_json=tmp_res_auth,
                                direction="RECV"
                            )

                    # ???붾쾭源? ?대뼡 ?ㅽ궎留덈줈 寃利앺븯?붿? ?뺤씤
                    if self.current_retry == 0:  # 泥??쒕룄?먮쭔 異쒕젰
                        Logger.debug(f"\n========== ?ㅽ궎留?寃利??붾쾭源?==========")
                        api_name = self.message[self.cnt] if self.cnt < len(self.message) else 'N/A'
                        Logger.debug(f"cnt={self.cnt}, API={api_name}")
                        Logger.debug(f"webhook_flag={self.webhook_flag}")
                        Logger.debug(f"current_protocol={current_protocol}")

                        # ???뱁썒 API??援щ룆 ?묐떟? ?쇰컲 ?ㅽ궎留??ъ슜
                        # webhook_flag???ㅼ젣 ?뱁썒 ?대깽???섏떊 ?쒖뿉留?True
                        # 援щ룆 ?묐떟? ??긽 outSchema[self.cnt] ?ъ슜
                        schema_index = self.cnt
                        Logger.debug(f" ?ъ슜 ?ㅽ궎留? outSchema[{schema_index}]")

                        # ?ㅽ궎留??꾨뱶 ?뺤씤
                        if self.cnt < len(self.outSchema):
                            schema_to_use = self.outSchema[self.cnt]
                            if isinstance(schema_to_use, dict):
                                schema_keys = list(schema_to_use.keys())[:5]
                                Logger.debug(f" ?ㅽ궎留??꾨뱶 (first 5): {schema_keys}")

                    # val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.outSchema[self.cnt], res_data, self.flag_opt)
                    resp_rules = {}
                    try:
                        resp_rules = self.resp_rules or {}
                    except Exception as e:
                        resp_rules = {}
                        Logger.error(f" ?묐떟 寃利?洹쒖튃 濡쒕뱶 ?ㅽ뙣: {e}")

                    # ?넅 ?묐떟 寃利앹슜 - resp_rules??媛??꾨뱶蹂?referenceEndpoint/Max/Min?먯꽌 trace ?뚯씪 濡쒕뱶
                    if resp_rules:
                        for field_path, validation_rule in resp_rules.items():
                            validation_type = validation_rule.get("validationType", "")
                            direction = "REQUEST" if "request-field" in validation_type else "RESPONSE"

                            # referenceEndpoint 泥섎━
                            ref_endpoint = validation_rule.get("referenceEndpoint", "")
                            if ref_endpoint:
                                ref_api_name = ref_endpoint.lstrip("/")
                                # latest_events???놁쑝硫?trace ?뚯씪?먯꽌 濡쒕뱶
                                if ref_api_name not in self.latest_events or direction not in self.latest_events.get(ref_api_name, {}):
                                    Logger.debug(f" {ref_endpoint} {direction}瑜?trace ?뚯씪?먯꽌 濡쒕뱶 ?쒕룄")
                                    response_data = self._load_from_trace_file(ref_api_name, direction)
                                    if response_data and isinstance(response_data, dict):
                                        self.reference_context[ref_endpoint] = response_data
                                        Logger.debug(f" {ref_endpoint} {direction}瑜?trace ?뚯씪?먯꽌 濡쒕뱶 ?꾨즺")
                                else:
                                    # latest_events???덉쑝硫?嫄곌린??媛?몄삤湲?
                                    event_data = self.latest_events.get(ref_api_name, {}).get(direction, {})
                                    if event_data and isinstance(event_data, dict):
                                        self.reference_context[ref_endpoint] = event_data.get("data", {})
                            
                            # referenceEndpointMax 泥섎━
                            ref_endpoint_max = validation_rule.get("referenceEndpointMax", "")
                            if ref_endpoint_max:
                                ref_api_name_max = ref_endpoint_max.lstrip("/")
                                if ref_api_name_max not in self.latest_events or direction not in self.latest_events.get(ref_api_name_max, {}):
                                    Logger.debug(f" {ref_endpoint_max} {direction}瑜?trace ?뚯씪?먯꽌 濡쒕뱶 ?쒕룄 (Max)")
                                    response_data_max = self._load_from_trace_file(ref_api_name_max, direction)
                                    if response_data_max and isinstance(response_data_max, dict):
                                        self.reference_context[ref_endpoint_max] = response_data_max
                                        Logger.debug(f" {ref_endpoint_max} {direction}瑜?trace ?뚯씪?먯꽌 濡쒕뱶 ?꾨즺 (Max)")
                                else:
                                    event_data = self.latest_events.get(ref_api_name_max, {}).get(direction, {})
                                    if event_data and isinstance(event_data, dict):
                                        self.reference_context[ref_endpoint_max] = event_data.get("data", {})
                            
                            # referenceEndpointMin 泥섎━
                            ref_endpoint_min = validation_rule.get("referenceEndpointMin", "")
                            if ref_endpoint_min:
                                ref_api_name_min = ref_endpoint_min.lstrip("/")
                                if ref_api_name_min not in self.latest_events or direction not in self.latest_events.get(ref_api_name_min, {}):
                                    Logger.debug(f" {ref_endpoint_min} {direction}瑜?trace ?뚯씪?먯꽌 濡쒕뱶 ?쒕룄 (Min)")
                                    response_data_min = self._load_from_trace_file(ref_api_name_min, direction)
                                    if response_data_min and isinstance(response_data_min, dict):
                                        self.reference_context[ref_endpoint_min] = response_data_min
                                        Logger.debug(f" {ref_endpoint_min} {direction}瑜?trace ?뚯씪?먯꽌 濡쒕뱶 ?꾨즺 (Min)")
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
                        Logger.error(f" ?묐떟 寃利?以?TypeError 諛쒖깮: {te}, ?쇰컲 寃利앹쑝濡??ъ떆??)
                        val_result, val_text, key_psss_cnt, key_error_cnt, opt_correct, opt_error = json_check_(
                            self.outSchema[self.cnt],
                            res_data,
                            self.flag_opt
                        )
                    if self.message[self.cnt] == "Authentication":
                        self.handle_authentication_response(res_data)

                    if self.current_retry == 0:  # 泥??쒕룄?먮쭔 異쒕젰
                        Logger.debug(f" 寃利?寃곌낵: {val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
                        Logger.debug(f" ==========================================\n")

                    # ?대쾲 ?쒕룄??寃곌낵
                    final_result = val_result

                    # ??留덉?留??쒕룄 寃곌낵濡???뼱?곌린 (?꾩쟻 X)
                    if not hasattr(self, 'step_pass_counts'):
                        api_count = len(self.videoMessages)
                        self.step_pass_counts = [0] * api_count
                        self.step_error_counts = [0] * api_count
                        self.step_opt_pass_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?듦낵 ??
                        self.step_opt_error_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?먮윭 ??
                        self.step_pass_flags = [0] * api_count

                    # ???대쾲 ?쒕룄 寃곌낵濡???뼱?곌린 (?꾩쟻?섏? ?딆쓬!)
                    self.step_pass_counts[self.cnt] = key_psss_cnt
                    self.step_error_counts[self.cnt] = key_error_cnt
                    self.step_opt_pass_counts[self.cnt] = opt_correct  # ?좏깮 ?꾨뱶 ?듦낵 ??
                    self.step_opt_error_counts[self.cnt] = opt_error  # ?좏깮 ?꾨뱶 ?먮윭 ??
                    
                    Logger.debug(f"[SCORE DEBUG] API {self.cnt} ?쒕룄 {self.current_retry + 1}: pass={key_psss_cnt}, error={key_error_cnt}")
                    Logger.debug(f"[SCORE DEBUG] step_pass_counts[{self.cnt}] = {self.step_pass_counts[self.cnt]}")
                    Logger.debug(f"[SCORE DEBUG] step_error_counts[{self.cnt}] = {self.step_error_counts[self.cnt]}")

                    if final_result == "PASS":
                        # ??諛곗뿴 踰붿쐞 泥댄겕 異붽?
                        if self.cnt < len(self.step_pass_flags):
                            self.step_pass_flags[self.cnt] += 1

                    total_pass_count = self.step_pass_counts[self.cnt]
                    total_error_count = self.step_error_counts[self.cnt]

                    # (1) ?ㅽ뀦 踰꾪띁 ???- ?ъ떆?꾨퀎濡??꾩쟻
                    # ???쒖뒪?쒖? ?뚮옯?쇱씠 蹂대궡???곗씠?곕? ?쒖떆?댁빞 ??
                    if isinstance(res_data, (dict, list)):
                        platform_data = res_data
                    else:
                        # ?뱀떆 dict/list媛 ?꾨땲硫?raw ?띿뒪?몃? 媛먯떥??湲곕줉
                        platform_data = {"raw_response": self.res.text}

                    data_text = json.dumps(platform_data, indent=4, ensure_ascii=False)

                    # ??PASS??寃쎌슦 ?ㅻ쪟 ?띿뒪??臾댁떆 (val_text??遺덊븘?뷀븳 ?뺣낫媛 ?덉쓣 ???덉쓬)
                    if val_result == "FAIL":
                        error_text = to_detail_text(val_text)
                    else:
                        # PASS???뚮뒗 val_text瑜?洹몃?濡??ъ슜 (400 ?먮윭 ?묐떟 硫붿떆吏 ?ы븿)
                        error_text = val_text if isinstance(val_text, str) else "?ㅻ쪟媛 ?놁뒿?덈떎."

                    # ??raw_data_list???꾩옱 ?묐떟 ?곗씠??異붽? (?ш컻 ??retry count 蹂듭썝??
                    self.step_buffers[self.cnt]["raw_data_list"].append(platform_data)

                    # 湲곗〈 踰꾪띁???꾩쟻 (?ъ떆???뺣낫? ?④퍡)
                    if self.current_retry == 0:
                        # 泥?踰덉㎏ ?쒕룄??寃쎌슦 珥덇린??
                        self.step_buffers[self.cnt][
                            "data"] = f"[?쒕룄 {self.current_retry + 1}/{current_retries}]\n{data_text}"
                        self.step_buffers[self.cnt][
                            "error"] = f"[?쒕룄 {self.current_retry + 1}/{current_retries}]\n{error_text}"
                        self.step_buffers[self.cnt]["result"] = val_result  # 泥??쒕룄 寃곌낵濡?珥덇린??
                    else:
                        # ?ъ떆?꾩씤 寃쎌슦 ?꾩쟻
                        self.step_buffers[self.cnt][
                            "data"] += f"\n\n[?쒕룄 {self.current_retry + 1}/{current_retries}]\n{data_text}"
                        self.step_buffers[self.cnt][
                            "error"] += f"\n\n[?쒕룄 {self.current_retry + 1}/{current_retries}]\n{error_text}"
                        self.step_buffers[self.cnt]["result"] = val_result  # 留덉?留??쒕룄 寃곌낵濡???긽 媛깆떊
                    # 理쒖쥌 寃곌낵 ?먯젙 (?뚮옯?쇨낵 ?숈씪??濡쒖쭅)
                    if self.current_retry + 1 >= current_retries:
                        # 紐⑤뱺 ?ъ떆???꾨즺 - 紐⑤뱺 ?쒕룄媛 PASS???뚮쭔 PASS
                        # ??諛곗뿴 踰붿쐞 泥댄겕 異붽?
                        if self.cnt < len(self.step_pass_flags) and self.step_pass_flags[self.cnt] >= current_retries:
                            self.step_buffers[self.cnt]["result"] = "PASS"
                        else:
                            self.step_buffers[self.cnt]["result"] = "FAIL"
                        # 留덉?留??쒕룄 寃곌낵???ㅻ쪟 ?띿뒪?몃줈 ??뼱?곌린 (?ㅽ뙣 ??
                        if self.step_buffers[self.cnt]["result"] == "FAIL":
                            self.step_buffers[self.cnt][
                                "error"] = f"[?쒕룄 {self.current_retry + 1}/{current_retries}]\n{error_text}"

                    # 吏꾪뻾 以??쒖떆 (?뚮옯?쇨낵 ?숈씪?섍쾶)
                    display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else self.message[self.cnt]
                    message_name = "step " + str(self.cnt + 1) + ": " + display_name
                    # 媛??쒕룄蹂꾨줈 pass/error count???꾩쟻???꾨땲???대쾲 ?쒕룄留?諛섏쁺?댁빞 ??
                    # key_psss_cnt, key_error_cnt???대쾲 ?쒕룄?????媛믪엫
                    if self.current_retry + 1 < current_retries:
                        # ?꾩쭅 ?ъ떆?꾧? ?⑥븘?덉쑝硫?吏꾪뻾以묒쑝濡??쒖떆 (?꾩쟻 移댁슫???쒖떆)
                        self.update_table_row_with_retries(
                            self.cnt, "吏꾪뻾以?, total_pass_count, total_error_count,
                            f"寃利?吏꾪뻾以?.. ({self.current_retry + 1}/{current_retries})",
                            f"?쒕룄 {self.current_retry + 1}/{current_retries}", self.current_retry + 1)
                    else:
                        # ??留덉?留??쒕룄?대㈃ 理쒖쥌 寃곌낵 ?쒖떆 (?꾩쟻???꾨뱶 ???ъ슜!)
                        final_buffer_result = self.step_buffers[self.cnt]["result"]
                        self.update_table_row_with_retries(
                            self.cnt, final_buffer_result, total_pass_count, total_error_count,
                            tmp_res_auth, error_text, current_retries)

                    # UI 利됱떆 ?낅뜲?댄듃 (?붾㈃??諛섏쁺)
                    QApplication.processEvents()

                    # ??寃利?吏꾪뻾 以?濡쒓렇瑜?HTML 移대뱶濡?異쒕젰
                    api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                    
                    # ?곗씠???щ㎎??(JSON ?뺤떇?쇰줈)
                    try:
                        if data_text and data_text.strip():
                            json_obj = json.loads(data_text)
                            formatted_data = json.dumps(json_obj, indent=2, ensure_ascii=False)
                        else:
                            formatted_data = data_text
                    except:
                        formatted_data = data_text
                    
                    # ?뱁썒 ?щ????곕씪 ?ㅻⅨ ?쒖떆
                    api_name = self.message[self.cnt] if self.cnt < len(self.message) else "Unknown"
                    display_name = self.message_display[self.cnt] if self.cnt < len(self.message_display) else api_name
                    if current_protocol == "WebHook":
                        step_title = f"寃곌낵: {display_name} - ?뱁썒 援щ룆 ({self.current_retry + 1}/{current_retries})"
                    else:
                        step_title = f"寃곌낵: {display_name} ({self.current_retry + 1}/{current_retries})"
                    
                    # 留덉?留??쒕룄?먮쭔 ?먯닔 ?쒖떆, 吏꾪뻾以묒뿉???쒖떆 ?덊븿
                    if self.current_retry + 1 >= current_retries:
                        # 留덉?留??쒕룄 - 理쒖쥌 寃곌낵 ?쒖떆
                        total_fields = total_pass_count + total_error_count
                        score_value = (total_pass_count / total_fields * 100) if total_fields > 0 else 0
                        self.append_monitor_log(
                            step_name=step_title,
                            request_json="",  # ?곗씠?곕뒗 ?욎꽌 異쒕젰?섏뿀?쇰?濡??앸왂
                            result_status=final_result,
                            score=score_value,
                            details=f"?듦낵 ?꾨뱶 ?? {total_pass_count}, ?ㅽ뙣 ?꾨뱶 ?? {total_error_count} | {'?쇰컲 硫붿떆吏' if current_protocol.lower() == 'basic' else f'?ㅼ떆媛?硫붿떆吏: {current_protocol}'}"
                        )
                    else:
                        # 以묎컙 ?쒕룄 - 吏꾪뻾以??쒖떆
                        self.append_monitor_log(
                            step_name=step_title,
                            request_json="",  # ?곗씠?곕뒗 ?욎꽌 異쒕젰?섏뿀?쇰?濡??앸왂
                            details=f"寃利?吏꾪뻾 以?.. | {'?쇰컲 硫붿떆吏' if current_protocol.lower() == 'basic' else f'?ㅼ떆媛?硫붿떆吏: {current_protocol}'}"
                        )

                    # ???뱁썒 泥섎━瑜??ъ떆???꾨즺 泥댄겕 ?꾩뿉 ?ㅽ뻾 (step_pass_counts ?낅뜲?댄듃瑜??꾪빐)
                    if self.webhook_flag:
                        Logger.debug(f" ?뱁썒 泥섎━ ?쒖옉 (API {self.cnt})")
                        self.get_webhook_result()

                    # ?ъ떆??移댁슫??利앷?
                    self.current_retry += 1

                    # ???꾩옱 API??紐⑤뱺 ?ъ떆?꾧? ?꾨즺?섏뿀?붿? ?뺤씤
                    if (self.cnt < len(self.num_retries_list) and
                            self.current_retry >= self.num_retries_list[self.cnt]):
                        # ??紐⑤뱺 ?ъ떆???꾨즺
                        # ???뱁썒 API??寃쎌슦 step_pass_counts媛 ?대? ?낅뜲?댄듃?섏뿀?????덉쑝誘濡?諛곗뿴?먯꽌 吏곸젒 媛?몄샂
                        final_pass_count = self.step_pass_counts[self.cnt]
                        final_error_count = self.step_error_counts[self.cnt]
                        
                        Logger.debug(f" API {self.cnt} ?꾨즺: pass={final_pass_count}, error={final_error_count}")

                        # ??遺꾩빞蹂??먯닔 ?낅뜲?댄듃 (?꾩옱 spec留?
                        self.total_pass_cnt += final_pass_count
                        self.total_error_cnt += final_error_count

                        # ???꾩껜 ?먯닔 ?낅뜲?댄듃 (紐⑤뱺 spec ?⑹궛) - API??1?뚮쭔 異붽?
                        self.global_error_cnt += final_error_count
                        self.global_pass_cnt += final_pass_count
                        # ???좏깮 ?꾨뱶 ?듦낵 ?섎룄 ?꾩껜 ?먯닔???꾩쟻
                        final_opt_pass_count = self.step_opt_pass_counts[self.cnt]
                        self.global_opt_pass_cnt += final_opt_pass_count
                        # ???좏깮 ?꾨뱶 ?먮윭 ?섎룄 ?꾩껜 ?먯닔???꾩쟻
                        final_opt_error_count = self.step_opt_error_counts[self.cnt]
                        self.global_opt_error_cnt += final_opt_error_count

                        Logger.debug(f" 遺꾩빞蹂??먯닔: pass={self.total_pass_cnt}, error={self.total_error_cnt}")
                        Logger.debug(f" ?꾩껜 ?먯닔: pass={self.global_pass_cnt}, error={self.global_error_cnt}")

                        # ???꾩껜 ?먯닔 ?ы븿?섏뿬 ?붿뒪?뚮젅???낅뜲?댄듃 (?ъ떆???꾨즺 ?꾩뿉留?
                        self.update_score_display()
                        
                        # ??理쒖쥌 ?먯닔???대? HTML 移대뱶???ы븿?섏뼱 ?덉쑝誘濡?蹂꾨룄 ?쒖떆 ?덊븿

                        self.step_buffers[self.cnt]["events"] = list(self.trace.get(self.cnt, []))

                        # ?ㅼ쓬 API濡??대룞
                        self.cnt += 1
                        self.current_retry = 0

                    self.message_in_cnt = 0
                    self.post_flag = False
                    self.processing_response = False

                    # ?ъ떆???щ????곕씪 ?湲??쒓컙 議곗젙
                    if (self.cnt < len(self.num_retries_list) and
                            self.current_retry < self.num_retries_list[self.cnt] - 1):
                        self.time_pre = time.time()
                    else:
                        self.time_pre = time.time()
                    self.message_in_cnt = 0

                    # ???뱁썒 泥섎━???대? ?꾩뿉???꾨즺??(以묐났 ?쒓굅)

            if self.cnt >= len(self.message):
                self.tick_timer.stop()
                self.append_monitor_log(
                    step_name="?쒗뿕 ?꾨즺",
                    details="?쒗뿕???꾨즺?섏뿀?듬땲??"
                )

                # ???꾩옱 spec ?곗씠?????
                self.save_current_spec_data()

                self.processing_response = False
                self.post_flag = False

                self.cnt = 0
                self.current_retry = 0

                # 理쒖쥌 由ы룷???앹꽦
                total_fields = self.total_pass_cnt + self.total_error_cnt
                if total_fields > 0:
                    final_score = (self.total_pass_cnt / total_fields) * 100
                else:
                    final_score = 0

                # ???꾩껜 ?먯닔 理쒖쥌 ?뺤씤 濡쒓렇
                global_total = self.global_pass_cnt + self.global_error_cnt
                global_score = (self.global_pass_cnt / global_total * 100) if global_total > 0 else 0
                Logger.debug(f"遺꾩빞蹂??먯닔: pass={self.total_pass_cnt}, error={self.total_error_cnt}, score={final_score:.1f}%")
                Logger.debug(f"?꾩껜 ?먯닔: pass={self.global_pass_cnt}, error={self.global_error_cnt}, score={global_score:.1f}%")

                # ??JSON 寃곌낵 ?먮룞 ???異붽?
                Logger.debug(f"?됯? ?꾨즺 - ?먮룞 ????쒖옉 (寃쎈줈2)")
                try:
                    self.run_status = "?꾨즺"
                    result_json = build_result_json(self)
                    url = f"{CONSTANTS.management_url}/api/integration/test-results"
                    response = requests.post(url, json=result_json)
                    Logger.debug(f"???쒗뿕 寃곌낵 ?꾩넚 ?곹깭 肄붾뱶:: {response.status_code}")
                    Logger.debug(f"?뱿  ?쒗뿕 寃곌낵 ?꾩넚 ?묐떟:: {response.text}")
                    json_path = os.path.join(result_dir, "response_results.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result_json, f, ensure_ascii=False, indent=2)
                    Logger.debug(f"???쒗뿕 寃곌낵媛 '{json_path}'???먮룞 ??λ릺?덉뒿?덈떎.")
                    self.append_monitor_log(
                        step_name="愿由ъ떆?ㅽ뀥 寃곌낵 ?꾩넚 ?꾨즺",
                        details=""
                    )
                    Logger.debug(f" try 釉붾줉 ?뺤긽 ?꾨즺 (寃쎈줈2)")
                except Exception as e:
                    Logger.debug(f"??JSON ???以??ㅻ쪟 諛쒖깮: {e}")
                    import traceback
                    traceback.print_exc()
                    self.valResult.append(f"\n寃곌낵 ????ㅽ뙣: {str(e)}")
                    Logger.debug(f" except 釉붾줉 ?ㅽ뻾??(寃쎈줈2)")
                finally:
                    # ???됯? ?꾨즺 ???쇱떆?뺤? ?뚯씪 ?뺣━ (?먮윭 諛쒖깮 ?щ?? 臾닿??섍쾶 ??긽 ?ㅽ뻾)
                    Logger.debug(f" ========== finally 釉붾줉 吏꾩엯 (寃쎈줈2) ==========")
                    self.cleanup_paused_file()
                    Logger.debug(f" ========== finally 釉붾줉 醫낅즺 (寃쎈줈2) ==========")
                    
                    # stop/pause ?섎룄媛 ?덉쑝硫?completed ?꾩넚 湲덉? (寃쎈줈2)
                    if not getattr(self, "is_paused", False):
                        try:
                            api_client = APIClient()
                            api_client.send_heartbeat_completed()
                            Logger.info(f"???쒗뿕 ?꾨즺 (寃쎈줈2) - completed ?곹깭 ?꾩넚 ?꾨즺")
                        except Exception as e:
                            Logger.warning(f"?좑툘 ?쒗뿕 ?꾨즺 (寃쎈줈2) - completed ?곹깭 ?꾩넚 ?ㅽ뙣: {e}")
                    else:
                        Logger.info("??툘 ?쇱떆?뺤? ?곹깭?대?濡?completed heartbeat ?꾩넚 ?앸왂 (寃쎈줈2)")

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
            QMessageBox.critical(self, "Error", "Error Message: ?ㅻ쪟 ?뺤씤 ??寃利??덉감瑜??ㅼ떆 ?쒖옉?댁＜?몄슂" + '\n' + f"Error at step {self.cnt + 1}: {str(err)}")
            self.tick_timer.stop()
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">寃利??덉감媛 以묒??섏뿀?듬땲?? (?ㅻ쪟 ?꾩튂: Step {self.cnt + 1})</div>')
            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)
            self.cancel_btn.setDisabled(True)

    def icon_update_step(self, auth_, result_, text_):
        # ?뚮옯?쇨낵 ?숈씪?섍쾶 '吏꾪뻾以??대㈃ 寃?뺤깋, PASS硫?珥덈줉, FAIL?대㈃ 鍮④컯
        if result_ == "PASS":
            msg = auth_ + "\n\n" + "Result: PASS" + "\n" + text_
            img = self.img_pass
        elif result_ == "吏꾪뻾以?:
            msg = auth_ + "\n\n" + "Status: " + text_
            img = self.img_none
        else:
            msg = auth_ + "\n\n" + "Result: FAIL" + "\nResult details:\n" + text_
            img = self.img_fail
        return msg, img

    def icon_update(self, tmp_res_auth, val_result, val_text):
        msg, img = self.icon_update_step(tmp_res_auth, val_result, val_text)

        if self.cnt < self.tableWidget.rowCount():
            # ?꾩씠肄??꾩젽 ?앹꽦
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
        """results/trace ?대뜑 ?덉쓽 ?뚯씪?ㅼ쓣 ??젣"""
        Logger.debug(f" ?좑툘  _clean_trace_dir_once() ?몄텧??")
        import traceback
        Logger.debug(f" ?몄텧 ?ㅽ깮:\n{''.join(traceback.format_stack()[-3:-1])}")
        os.makedirs(CONSTANTS.trace_path, exist_ok=True)
        for name in os.listdir(CONSTANTS.trace_path):
            path = os.path.join(CONSTANTS.trace_path, name)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    Logger.debug(f" ??젣: {name}")
                except OSError:
                    pass

    def start_btn_clicked(self):
        """?됯? ?쒖옉 踰꾪듉 ?대┃"""
        try:
            setattr(CONSTANTS, "SUPPRESS_COMPLETED_HEARTBEAT", False)
            setattr(CONSTANTS, "HEARTBEAT_STOPPED_LOCK", False)
            APIClient().send_heartbeat_in_progress(getattr(self.CONSTANTS, "request_id", ""))
        except Exception as e:
            Logger.warning(f"?좑툘 ?쒗뿕 ?쒖옉 - in_progress ?곹깭 ?꾩넚 ?ㅽ뙣: {e}")

        # ???먮룞 ?ъ떆???뚮옒洹??뺤씤 諛??쒓굅
        is_auto_restart = getattr(self, '_auto_restart', False)
        if is_auto_restart:
            self._auto_restart = False
            Logger.debug(f" ?먮룞 ?ъ떆??紐⑤뱶 - ?쒕굹由ъ삤 ?좏깮 寃利?嫄대꼫?")
        else:
            # ??1. ?쒕굹由ъ삤 ?좏깮 ?뺤씤 (?섎룞 ?쒖옉 ?쒖뿉留?
            if not hasattr(self, 'current_spec_id') or not self.current_spec_id:
                QMessageBox.warning(self, "?뚮┝", "?쒗뿕 ?쒕굹由ъ삤瑜?癒쇱? ?좏깮?섏꽭??")
                return

        # ???쇱떆?뺤? ?뚯씪 議댁옱 ?щ? ?뺤씤 (spec_id蹂꾨줈 愿由?
        paused_file_path = os.path.join(result_dir, f"response_results_paused_{self.current_spec_id}.json")
        resume_mode = os.path.exists(paused_file_path)

        if resume_mode:
            Logger.debug(f" ========== ?ш컻 紐⑤뱶: ?쇱떆?뺤? ?곹깭 蹂듭썝 ==========")
            # ?ш컻 紐⑤뱶: ??λ맂 ?곹깭 蹂듭썝
            if self.load_paused_state():
                self.is_paused = False  # ?ш컻 ?쒖옉?대?濡?paused ?뚮옒洹??댁젣
                Logger.debug(f" ?ш컻 紐⑤뱶: {self.last_completed_api_index + 2}踰덉㎏ API遺???쒖옉")
            else:
                # 蹂듭썝 ?ㅽ뙣 ???좉퇋 ?쒖옉?쇰줈 ?꾪솚
                Logger.warn(f" ?곹깭 蹂듭썝 ?ㅽ뙣, ?좉퇋 ?쒖옉?쇰줈 ?꾪솚")
                resume_mode = False
        self.webhook_schema_idx = 0

        # ??濡쒕뵫 ?앹뾽 ?쒖떆
        self.loading_popup = LoadingPopup()
        self.loading_popup.show()
        self.loading_popup.raise_()  # 理쒖긽?꾨줈 ?щ━湲?
        self.loading_popup.activateWindow()  # ?쒖꽦??
        self.loading_popup.repaint()  # 媛뺤젣 ?ㅼ떆 洹몃━湲?
        # UI媛 ?뺤떎???뚮뜑留곷릺?꾨줉 ?щ윭 踰?processEvents ?몄텧
        for _ in range(10):
            QApplication.processEvents()

        # ??URL ?ㅼ뿼 諛⑹?: ?띿뒪??諛뺤뒪媛 ?꾨땶 CONSTANTS?먯꽌 吏곸젒 ?쎄린
        fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
        if hasattr(self, 'spec_config'):
            test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
            self.pathUrl = fresh_base_url.rstrip('/') + "/" + test_name
        else:
            self.pathUrl = fresh_base_url
        print(f"[SYSTEM DEBUG] sbtn_push?먯꽌 pathUrl ?ㅼ젙: {self.pathUrl}")
        if not resume_mode:
            Logger.debug(f"========== 寃利??쒖옉: ?꾩쟾 珥덇린??==========")
        Logger.debug(f"?쒗뿕 URL: {self.pathUrl}")
        Logger.debug(f"?쒗뿕: {self.current_spec_id} - {self.spec_description}")
        Logger.debug(f"?ъ슜???몄쬆 諛⑹떇: {self.CONSTANTS.auth_type}")

        QApplication.processEvents()  # ?ㅽ뵾???좊땲硫붿씠???좎?
        self.update_result_table_structure(self.videoMessages)
        QApplication.processEvents()  # ?ㅽ뵾???좊땲硫붿씠???좎?

        # ??2. 湲곗〈 ??대㉧ ?뺤? (以묐났 ?ㅽ뻾 諛⑹?)
        if self.tick_timer.isActive():
            Logger.debug(f" 湲곗〈 ??대㉧ 以묒?")
            self.tick_timer.stop()

        if not resume_mode:
            # ========== ?좉퇋 ?쒖옉 紐⑤뱶: ?꾩쟾 珥덇린??==========
            Logger.debug(f" ========== ?좉퇋 ?쒖옉: ?꾩쟾 珥덇린??==========")

            # ??3. trace ?붾젆?좊━ 珥덇린??(洹몃９??蹂寃쎈맆 ?뚮쭔)
            # 媛숈? 洹몃９ ??spec ?꾪솚 ?쒖뿉??trace ?좎? (留λ씫 寃利앹슜)
            if not hasattr(self, '_last_cleaned_group') or self._last_cleaned_group != self.current_group_id:
                Logger.debug(f" 洹몃９ 蹂寃?媛먯?: {getattr(self, '_last_cleaned_group', None)} ??{self.current_group_id}")
                Logger.debug(f" trace ?붾젆?좊━ 珥덇린???ㅽ뻾")
                self._clean_trace_dir_once()
                self._last_cleaned_group = self.current_group_id
            else:
                Logger.debug(f" 媛숈? 洹몃９ ??spec ?꾪솚: trace ?붾젆?좊━ ?좎? (留λ씫 寃利앹슜)")

            # ??4. JSON ?곗씠??以鍮?
            json_to_data("video")

            # ??6. ?댁쟾 ?쒗뿕 寃곌낵媛 global ?먯닔???ы븿?섏뼱 ?덉쑝硫??쒓굅 (蹂듯빀???ъ슜)
            composite_key = f"{self.current_group_id}_{self.current_spec_id}"
            if composite_key in self.spec_table_data:
                prev_data = self.spec_table_data[composite_key]
                prev_pass = prev_data.get('total_pass_cnt', 0)
                prev_error = prev_data.get('total_error_cnt', 0)
                # ???좏깮 ?꾨뱶 ?듦낵/?먮윭 ??怨꾩궛
                prev_opt_pass = sum(prev_data.get('step_opt_pass_counts', []))
                prev_opt_error = sum(prev_data.get('step_opt_error_counts', []))
                Logger.debug(f"[SCORE RESET] 湲곗〈 {composite_key} ?먯닔 ?쒓굅: pass={prev_pass}, error={prev_error}")
                Logger.debug(f"[SCORE RESET] 湲곗〈 {composite_key} ?좏깮 ?먯닔 ?쒓굅: opt_pass={prev_opt_pass}, opt_error={prev_opt_error}")

                # ??global ?먯닔?먯꽌 ?대떦 spec ?먯닔 ?쒓굅
                self.global_pass_cnt = max(0, self.global_pass_cnt - prev_pass)
                self.global_error_cnt = max(0, self.global_error_cnt - prev_error)
                # ??global ?좏깮 ?먯닔?먯꽌 ?대떦 spec ?먯닔 ?쒓굅
                self.global_opt_pass_cnt = max(0, self.global_opt_pass_cnt - prev_opt_pass)
                self.global_opt_error_cnt = max(0, self.global_opt_error_cnt - prev_opt_error)

                Logger.debug(f"[SCORE RESET] 議곗젙 ??global ?먯닔: pass={self.global_pass_cnt}, error={self.global_error_cnt}")
                Logger.debug(f"[SCORE RESET] 議곗젙 ??global ?좏깮 ?먯닔: opt_pass={self.global_opt_pass_cnt}, opt_error={self.global_opt_error_cnt}")

            # ??7. 紐⑤뱺 移댁슫??諛??뚮옒洹?珥덇린??(泥??ㅽ뻾泥섎읆)
            self.cnt = 0
            self.cnt_pre = 0
            self.time_pre = 0
            self.current_retry = 0
            self.post_flag = False
            self.processing_response = False
            self.message_in_cnt = 0
            self.realtime_flag = False
            self.tmp_msg_append_flag = False

            # ??8. ?꾩옱 spec???먯닔留?珥덇린??(global? ?좎?)
            self.total_error_cnt = 0
            self.total_pass_cnt = 0

            # ??9. 硫붿떆吏 諛??먮윭 愿??蹂??珥덇린??
            self.message_error = []
            self.res = None
            self.webhook_res = None

            # ??10. ?꾩옱 spec??留욊쾶 ?꾩쟻 移댁슫??珥덇린??
            api_count = len(self.videoMessages)
            self.step_pass_counts = [0] * api_count
            self.step_error_counts = [0] * api_count
            self.step_opt_pass_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?듦낵 ??
            self.step_opt_error_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?먮윭 ??
            self.step_pass_flags = [0] * api_count

            # ??11. step_buffers ?꾩쟾 ?ъ깮??
            self.step_buffers = [
                {"data": "", "error": "", "result": "PASS", "raw_data_list": []} for _ in range(api_count)
            ]
            Logger.debug(f" step_buffers ?ъ깮???꾨즺: {len(self.step_buffers)}媛?)

            # ??12. trace 珥덇린??
            if hasattr(self, 'trace'):
                self.trace.clear()
            else:
                self.trace = {}

            if hasattr(self, 'latest_events'):
                self.latest_events.clear()
            else:
                self.latest_events = {}

            # ??13. ?뚯씠釉??꾩쟾 珥덇린??
            Logger.debug(f" ?뚯씠釉?珥덇린?? {api_count}媛?API")
            for i in range(self.tableWidget.rowCount()):
                QApplication.processEvents()  # ?ㅽ뵾???좊땲硫붿씠???좎?
                # ??湲곗〈 ?꾩젽 ?쒓굅 (寃뱀묠 諛⑹?)
                self.tableWidget.setCellWidget(i, 2, None)
                
                # ?꾩씠肄?珥덇린??
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

                # 移댁슫??珥덇린??(9而щ읆 援ъ“)
                for col, value in [(3, "0"), (4, "0"), (5, "0"), (6, "0"), (7, "0%")]:
                    existing_item = self.tableWidget.item(i, col)
                    if existing_item:
                        # 湲곗〈 ?꾩씠?쒖씠 ?덉쑝硫?媛믩쭔 ?낅뜲?댄듃 (setItem ?몄텧?섏? ?딆쓬)
                        existing_item.setText(value)
                        existing_item.setTextAlignment(Qt.AlignCenter)
                    else:
                        # ?꾩씠?쒖씠 ?놁쑝硫??덈줈 ?앹꽦?섍퀬 ?ㅼ젙
                        new_item = QTableWidgetItem(value)
                        new_item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget.setItem(i, col, new_item)
            Logger.debug(f" ?뚯씠釉?珥덇린???꾨즺")

            # ??14. ?몄쬆 ?뺣낫 ?ㅼ젙
            parts = self.auth_info.split(",")
            auth = [parts[0], parts[1] if len(parts) > 1 else ""]
            self.accessInfo = [auth[0], auth[1]]
            self.token = None

            # ??15. ?됯? ?먯닔 ?붿뒪?뚮젅??珥덇린??(?꾩껜 ?먯닔 ?ы븿)
            self.update_score_display()
            QApplication.processEvents()  # ?ㅽ뵾???좊땲硫붿씠???좎?

            # ??16. 寃곌낵 ?띿뒪??珥덇린??
            self.valResult.clear()

            # ??17. URL ?ㅼ젙 (?ㅼ뿼 諛⑹?: CONSTANTS?먯꽌 ?쎄린)
            fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
            if hasattr(self, 'spec_config'):
                test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
                self.pathUrl = fresh_base_url.rstrip('/') + "/" + test_name
            else:
                self.pathUrl = fresh_base_url
            self.url_text_box.setText(self.pathUrl)  # ?덈궡 臾멸뎄 蹂寃?
            print(f"[SYSTEM DEBUG] start_test_execution?먯꽌 pathUrl ?ㅼ젙: {self.pathUrl}")

            # ??18. ?쒖옉 硫붿떆吏
            self.append_monitor_log(
                step_name=f"?쒗뿕 ?쒖옉: {self.spec_description}",
                details=f"API 媛쒖닔: {len(self.videoMessages)}媛?
            )
        else:
            # ========== ?ш컻 紐⑤뱶: ??λ맂 ?곹깭 ?ъ슜, 珥덇린??嫄대꼫?곌린 ==========
            Logger.debug(f" ?ш컻 紐⑤뱶: 珥덇린??嫄대꼫?곌린, ??λ맂 ?곹깭 ?ъ슜")
            # cnt??last_completed_api_index + 1濡??ㅼ젙
            self.cnt = self.last_completed_api_index + 1
            Logger.debug(f" ?ш컻 紐⑤뱶: cnt = {self.cnt}")

            # ???ш컻 紐⑤뱶?먯꽌???ㅽ뻾 ?곹깭 蹂?섎뒗 珥덇린???꾩슂
            self.current_retry = 0  # ?ъ떆??移댁슫??珥덇린??(以묒슂!)
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
            Logger.debug(f" ?ш컻 紐⑤뱶: ?ㅽ뻾 ?곹깭 蹂??珥덇린???꾨즺")

            # ??誘몄셿猷?API??trace ?뚯씪 ??젣 (?꾨즺??API???좎?)
            trace_dir = os.path.join(result_dir, "trace")
            if os.path.exists(trace_dir):
                Logger.debug(f" 誘몄셿猷?API trace ?뚯씪 ??젣 ?쒖옉 (?꾨즺: 0~{self.last_completed_api_index})")
                for i in range(self.last_completed_api_index + 1, len(self.videoMessages)):
                    api_name = self.videoMessages[i]
                    # ????媛吏 ?뺤떇 紐⑤몢 ??젣 (trace_API.ndjson, trace_NN_API.ndjson)
                    trace_patterns = [
                        f"trace_{api_name}.ndjson",
                        f"trace_{i:02d}_{api_name}.ndjson"
                    ]
                    for pattern in trace_patterns:
                        trace_file = os.path.join(trace_dir, pattern)
                        if os.path.exists(trace_file):
                            try:
                                os.remove(trace_file)
                                Logger.debug(f" ??젣: {pattern}")
                            except Exception as e:
                                Logger.warn(f" trace ?뚯씪 ??젣 ?ㅽ뙣: {e}")
                Logger.debug(f" 誘몄셿猷?API trace ?뚯씪 ?뺣━ ?꾨즺")

            # ?먯닔 ?붿뒪?뚮젅???낅뜲?댄듃 (蹂듭썝???먯닔濡?
            self.update_score_display()
            QApplication.processEvents()  # ?ㅽ뵾???좊땲硫붿씠???좎?

            # 紐⑤땲?곕쭅 硫붿떆吏 蹂듭썝
            self.valResult.clear()
            if self.paused_valResult_text:
                self.valResult.setHtml(self.paused_valResult_text)
                self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 10px;">========== ?ш컻 ==========</div>')
                self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">留덉?留??꾨즺 API: {self.last_completed_api_index + 1}踰덉㎏</div>')
                self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-bottom: 10px;">{self.last_completed_api_index + 2}踰덉㎏ API遺???ш컻?⑸땲??</div>')
                Logger.debug(f" 紐⑤땲?곕쭅 硫붿떆吏 蹂듭썝 ?꾨즺: {len(self.paused_valResult_text)} 臾몄옄")

            # ???뚯씠釉??곗씠??蹂듭썝 (?꾨즺??API?ㅻ쭔)
            Logger.debug(f" ?뚯씠釉??곗씠??蹂듭썝 ?쒖옉: 0 ~ {self.last_completed_api_index}踰덉㎏ API")
            for i in range(self.last_completed_api_index + 1):
                if i < len(self.step_buffers):
                    buffer = self.step_buffers[i]
                    # ?ㅼ젣 ?곗씠?곌? ?덈뒗 寃쎌슦留??뚯씠釉??낅뜲?댄듃
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

                        # 遺?섑뀒?ㅽ듃??寃쎌슦 寃利??잛닔??raw_data_list 湲몄씠
                        retries = len(buffer.get('raw_data_list', [])) if buffer.get('raw_data_list') else 1

                        # ?뚯씠釉????낅뜲?댄듃
                        self.update_table_row_with_retries(
                            i, result, pass_count, error_count, data, error, retries
                        )
                        Logger.debug(f" ?뚯씠釉?蹂듭썝: API {i+1} - result={result}, pass={pass_count}, error={error_count}, retries={retries}")
            Logger.debug(f" ?뚯씠釉??곗씠??蹂듭썝 ?꾨즺")

        QApplication.processEvents()  # ?ㅽ뵾???좊땲硫붿씠???좎?

        # ??5. 踰꾪듉 ?곹깭 蹂寃?(?좉퇋/?ш컻 怨듯넻)
        self.sbtn.setDisabled(True)
        self.stop_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)

        QApplication.processEvents()  # ?ㅽ뵾???좊땲硫붿씠???좎?

        # ??19. ??대㉧ ?쒖옉 (紐⑤뱺 珥덇린???꾨즺 ??
        Logger.debug(f" ??대㉧ ?쒖옉")
        self.tick_timer.start(1000)
        Logger.debug(f" ========== 寃利??쒖옉 以鍮??꾨즺 ==========")

        # ??濡쒕뵫 ?앹뾽 ?リ린 (理쒖냼 ?쒖떆 ?쒓컙 ?뺣낫)
        if self.loading_popup:
            # ?앹뾽??理쒖냼??蹂댁씠?꾨줉 ?좎떆 ?湲?(?ㅽ뵾???좎?)
            for _ in range(3):  # 3 * 100ms = 300ms
                time.sleep(0.1)
                QApplication.processEvents()
            self.loading_popup.close()
            self.loading_popup = None

        Logger.debug(f" ?꾩옱 global ?먯닔: pass={self.global_pass_cnt}, error={self.global_error_cnt}")

    def save_paused_state(self):
        """?쇱떆?뺤? ???꾩옱 ?곹깭瑜?JSON ?뚯씪濡????""
        try:
            from datetime import datetime

            # 留덉?留??꾨즺??API ?몃뜳??怨꾩궛
            # 紐⑤뱺 retry媛 ?꾨즺??API留??꾨즺濡?媛꾩＜
            last_completed = -1
            for i, buffer in enumerate(self.step_buffers):
                # ??遺?섑뀒?ㅽ듃??寃쎌슦 紐⑤뱺 retry媛 ?꾨즺?섏뼱??"?꾨즺"濡??먮떒
                raw_data_list = buffer.get('raw_data_list', [])
                expected_retries = self.num_retries_list[i] if i < len(self.num_retries_list) else 1

                # ?ㅼ젣 ?꾨즺??retry ?섍? ?덉긽 retry ?섏? 媛숆굅???щ㈃ ?꾨즺
                if len(raw_data_list) >= expected_retries:
                    last_completed = i
                # timeout ?깆쑝濡??곗씠???놁씠 FAIL 泥섎━??寃쎌슦???꾨즺濡?媛꾩＜
                elif buffer.get('result') == 'FAIL' and (buffer.get('data') or buffer.get('error')):
                    has_timeout_error = 'Message Missing' in str(buffer.get('error', ''))
                    if has_timeout_error:
                        last_completed = i

            self.last_completed_api_index = last_completed

            # ??ν븷 ?곹깭 ?곗씠??援ъ꽦
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

            # JSON ?뚯씪濡????(spec_id ?ы븿)
            paused_file_path = os.path.join(result_dir, f"response_results_paused_{self.current_spec_id}.json")
            with open(paused_file_path, "w", encoding="utf-8") as f:
                json.dump(paused_state, f, ensure_ascii=False, indent=2)

            Logger.debug(f"???쇱떆?뺤? ?곹깭 ????꾨즺: {paused_file_path}")
            Logger.debug(f"   留덉?留??꾨즺 API ?몃뜳?? {last_completed}")

            # 紐⑤땲?곕쭅 李쎌뿉 濡쒓렇 異붽?
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 10px;">?뮶 ?ш컻 ?뺣낫 ????꾨즺: {paused_file_path}</div>')
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">   (留덉?留??꾨즺 API: {last_completed + 1}踰덉㎏, ?ㅼ쓬 ?ъ떆????{last_completed + 2}踰덉㎏ API遺???댁뼱???ㅽ뻾)</div>')

        except Exception as e:
            Logger.debug(f"???쇱떆?뺤? ?곹깭 ????ㅽ뙣: {e}")
            import traceback
            traceback.print_exc()

    def load_paused_state(self):
        """?쇱떆?뺤????곹깭瑜?JSON ?뚯씪?먯꽌 蹂듭썝"""
        try:
            paused_file_path = os.path.join(result_dir, f"response_results_paused_{self.current_spec_id}.json")

            if not os.path.exists(paused_file_path):
                Logger.debug("[INFO] ?쇱떆?뺤? ?뚯씪??議댁옱?섏? ?딆뒿?덈떎.")
                return False

            with open(paused_file_path, "r", encoding="utf-8") as f:
                paused_state = json.load(f)

            # ?곹깭 蹂듭썝
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

            Logger.debug(f"???쇱떆?뺤? ?곹깭 蹂듭썝 ?꾨즺")
            Logger.debug(f"   ??꾩뒪?ы봽: {paused_state.get('timestamp')}")
            Logger.debug(f"   留덉?留??꾨즺 API ?몃뜳?? {self.last_completed_api_index}")
            Logger.debug(f"   蹂듭썝???먯닔: PASS={self.total_pass_cnt}, FAIL={self.total_error_cnt}")

            return True

        except Exception as e:
            Logger.debug(f"???쇱떆?뺤? ?곹깭 蹂듭썝 ?ㅽ뙣: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup_paused_file(self):
        """?됯? ?꾨즺 ???쇱떆?뺤? ?뚯씪 ??젣 諛??곹깭 珥덇린??""
        try:
            paused_file_path = os.path.join(result_dir, f"response_results_paused_{self.current_spec_id}.json")
            Logger.debug(f" cleanup_paused_file() ?몄텧??)
            Logger.debug(f" ?뚯씪 寃쎈줈: {paused_file_path}")
            Logger.debug(f" ?뚯씪 議댁옱 ?щ?: {os.path.exists(paused_file_path)}")

            if os.path.exists(paused_file_path):
                os.remove(paused_file_path)
                Logger.debug("???쇱떆?뺤? 以묎컙 ?뚯씪 ??젣 ?꾨즺")
            else:
                Logger.debug("[CLEANUP] ?쇱떆?뺤? ?뚯씪??議댁옱?섏? ?딆쓬 (?쇱떆?뺤??섏? ?딆븯嫄곕굹 ?대? ??젣??")

            # ?쇱떆?뺤? ?곹깭 珥덇린??
            self.is_paused = False
            self.last_completed_api_index = -1
            self.paused_valResult_text = ""

        except Exception as e:
            Logger.debug(f"???쇱떆?뺤? ?뚯씪 ?뺣━ ?ㅽ뙣: {e}")

    def _cleanup_all_paused_files_on_startup(self):
        """?꾨줈洹몃옩 ?쒖옉 ??紐⑤뱺 ?쇱떆?뺤? ?뚯씪 ??젣"""
        try:
            import glob
            # response_results_paused_*.json ?⑦꽩?쇰줈 紐⑤뱺 ?쇱떆?뺤? ?뚯씪 李얘린
            pattern = os.path.join(result_dir, "response_results_paused_*.json")
            paused_files = glob.glob(pattern)
            
            if paused_files:
                Logger.debug(f" {len(paused_files)}媛쒖쓽 ?쇱떆?뺤? ?뚯씪 諛쒓껄")
                for file_path in paused_files:
                    try:
                        os.remove(file_path)
                        Logger.debug(f" ??젣 ?꾨즺: {os.path.basename(file_path)}")
                    except Exception as e:
                        Logger.warn(f" ?뚯씪 ??젣 ?ㅽ뙣 {file_path}: {e}")
                Logger.debug(f"???쒖옉 ???쇱떆?뺤? ?뚯씪 ??젣 ?꾨즺")
            else:
                Logger.debug("[STARTUP_CLEANUP] ??젣???쇱떆?뺤? ?뚯씪???놁쓬")
        except Exception as e:
            Logger.debug(f"???쒖옉 ???쇱떆?뺤? ?뚯씪 ??젣 ?ㅽ뙣: {e}")

    def cleanup_all_paused_files(self):
        """?꾨줈洹몃옩 醫낅즺 ??紐⑤뱺 ?쇱떆?뺤? ?뚯씪 ??젣"""
        try:
            import glob
            # response_results_paused_*.json ?⑦꽩?쇰줈 紐⑤뱺 ?쇱떆?뺤? ?뚯씪 李얘린
            pattern = os.path.join(result_dir, "response_results_paused_*.json")
            paused_files = glob.glob(pattern)
            
            if paused_files:
                Logger.debug(f" {len(paused_files)}媛쒖쓽 ?쇱떆?뺤? ?뚯씪 諛쒓껄")
                for file_path in paused_files:
                    try:
                        os.remove(file_path)
                        Logger.debug(f" ??젣 ?꾨즺: {os.path.basename(file_path)}")
                    except Exception as e:
                        Logger.warn(f" ?뚯씪 ??젣 ?ㅽ뙣 {file_path}: {e}")
                Logger.debug(f"??紐⑤뱺 ?쇱떆?뺤? ?뚯씪 ??젣 ?꾨즺")
            else:
                Logger.debug("[CLEANUP_ALL] ??젣???쇱떆?뺤? ?뚯씪???놁쓬")
        except Exception as e:
            Logger.debug(f"???쇱떆?뺤? ?뚯씪 ?쇨큵 ??젣 ?ㅽ뙣: {e}")

    def stop_btn_clicked(self):
        setattr(CONSTANTS, "SUPPRESS_COMPLETED_HEARTBEAT", True)
        self.is_paused = True
        """?됯? 以묒? 踰꾪듉 ?대┃"""
        # ?꾨즺 猷⑦봽? ?덉씠?ㅺ? ?섎룄 completed媛 ?섍?吏 ?딅룄濡?癒쇱? ?ㅼ젙
        self.is_paused = True

        # ????대㉧ 以묒?
        if self.tick_timer.isActive():
            self.tick_timer.stop()
            Logger.debug(f" ??대㉧ 以묒???)

        self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">寃利??덉감媛 以묒??섏뿀?듬땲??</div>')
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)
        self.cancel_btn.setDisabled(True)
        
        # ???쒗뿕 以묒? - stopped ?곹깭 heartbeat ?꾩넚
        try:
            api_client = APIClient()
            api_client.send_heartbeat_stopped(getattr(self.CONSTANTS, "request_id", ""))
            Logger.info(f"???쒗뿕 以묒? - in_progress ?곹깭 ?꾩넚 ?꾨즺")
        except Exception as e:
            Logger.warning(f"?좑툘 ?쒗뿕 以묒? - in_progress ?곹깭 ?꾩넚 ?ㅽ뙣: {e}")

        self.save_current_spec_data()

        # ???쇱떆?뺤? ?곹깭 ???
        self.save_paused_state()
        return

        # ??JSON 寃곌낵 ???異붽?
        try:
            self.run_status = "吏꾪뻾以?
            result_json = build_result_json(self)
            url = f"{CONSTANTS.management_url}/api/integration/test-results"
            response = requests.post(url, json=result_json)
            Logger.debug(f"???쒗뿕 寃곌낵 ?꾩넚 ?곹깭 肄붾뱶:: {response.status_code}")
            Logger.debug(f"?뱿  ?쒗뿕 寃곌낵 ?꾩넚 ?묐떟:: {response.text}")
            json_path = os.path.join(result_dir, "response_results.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)
            Logger.debug(f"??吏꾪뻾 以?寃곌낵媛 '{json_path}'????λ릺?덉뒿?덈떎.")
            self.append_monitor_log(
                step_name="吏꾪뻾 ?곹솴 ????꾨즺",
                details=f"{json_path} (?쇱떆?뺤? ?쒖젏源뚯???寃곌낵媛 ??λ릺?덉뒿?덈떎)"
            )
        except Exception as e:
            Logger.debug(f"??JSON ???以??ㅻ쪟 諛쒖깮: {e}")
            import traceback
            traceback.print_exc()
            self.valResult.append(f"\n寃곌낵 ????ㅽ뙣: {str(e)}")

    def cancel_btn_clicked(self):
        """?쒗뿕 痍⑥냼 踰꾪듉 ?대┃ - 吏꾪뻾 以묐떒, ?곹깭 珥덇린??""
        Logger.debug(f" ?쒗뿕 痍⑥냼 踰꾪듉 ?대┃")
        setattr(CONSTANTS, "SUPPRESS_COMPLETED_HEARTBEAT", True)
        
        # ?뺤씤 硫붿떆吏 ?쒖떆
        reply = QMessageBox.question(
            self, '?쒗뿕 痍⑥냼',
            '?꾩옱 吏꾪뻾 以묒씤 ?쒗뿕??痍⑥냼?섏떆寃좎뒿?덇퉴?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            Logger.debug(f" ?ъ슜?먭? 痍⑥냼瑜?痍⑥냼??)
            return
        
        Logger.debug(f" ========== ?쒗뿕 痍⑥냼 ?쒖옉 ==========")
        
        # 1. ??대㉧ 以묒? 諛?珥덇린??
        if self.tick_timer.isActive():
            self.tick_timer.stop()
            Logger.debug(f" ??대㉧ 以묒???)
        
        # 2. ?쇱떆?뺤? ?뚯씪 ??젣
        self.cleanup_paused_file()
        Logger.debug(f" ?쇱떆?뺤? ?뚯씪 ??젣 ?꾨즺")
        
        # 3. ?곹깭 ?꾩쟾 珥덇린??
        self.is_paused = False
        self.last_completed_api_index = -1
        self.paused_valResult_text = ""
        self.cnt = 0
        self.current_retry = 0
        self.post_flag = False  # ?뱁썒 ?뚮옒洹?珥덇린??
        self.res = None  # ?묐떟 珥덇린??
        self.webhook_flag = False
        Logger.debug(f" ?곹깭 珥덇린???꾨즺")
        
        # 4. 踰꾪듉 ?곹깭 珥덇린??
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)
        self.cancel_btn.setDisabled(True)
        
        # ???쒗뿕 痍⑥냼 - stopped ?곹깭 heartbeat ?꾩넚
        try:
            api_client = APIClient()
            api_client.send_heartbeat_stopped(getattr(self.CONSTANTS, "request_id", ""))
            Logger.info(f"???쒗뿕 痍⑥냼 - in_progress ?곹깭 ?꾩넚 ?꾨즺")
        except Exception as e:
            Logger.warning(f"?좑툘 ?쒗뿕 痍⑥냼 - in_progress ?곹깭 ?꾩넚 ?ㅽ뙣: {e}")
        
        # 5. 紐⑤땲?곕쭅 ?붾㈃ 珥덇린??
        self.valResult.clear()
        self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">?쒗뿕??痍⑥냼?섏뿀?듬땲?? ?쒗뿕 ?쒖옉 踰꾪듉???뚮윭 ?ㅼ떆 ?쒖옉?섏꽭??</div>')
        Logger.debug(f" 紐⑤땲?곕쭅 ?붾㈃ 珥덇린??)
        
        # 6. UI ?낅뜲?댄듃 泥섎━
        QApplication.processEvents()
        
        Logger.debug(f" ========== ?쒗뿕 痍⑥냼 ?꾨즺 ==========")

    def init_win(self):
            """寃利??쒖옉 ??珥덇린??""
            self.cnt = 0
            self.current_retry = 0
            # ?꾩옱 spec??API 媛쒖닔??留욊쾶 踰꾪띁 ?앹꽦
            api_count = len(self.videoMessages) if self.videoMessages else 0
            Logger.debug(f" 珥덇린?? {api_count}媛?API")

            # 踰꾪띁 珥덇린??
            self.step_buffers = [
                {"data": "", "result": "", "error": "", "raw_data_list": []} for _ in range(api_count)
            ]

            # ?꾩쟻 移댁슫??珥덇린??
            self.step_pass_counts = [0] * api_count
            self.step_error_counts = [0] * api_count
            self.step_opt_pass_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?듦낵 ??
            self.step_opt_error_counts = [0] * api_count  # ?좏깮 ?꾨뱶 ?먮윭 ??
            self.step_pass_flags = [0] * api_count
            self.webhook_schema_idx = 0

            self.valResult.clear()

            # 硫붿떆吏 珥덇린??
            for i in range(1, 10):
                setattr(self, f"step{i}_msg", "")

            # ?뚯씠釉??꾩씠肄?諛?移댁슫??珥덇린??
            for i in range(self.tableWidget.rowCount()):
                # ??湲곗〈 ?꾩젽 ?쒓굅 (寃뱀묠 諛⑹?)
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

                # 移댁슫??珥덇린??(9而щ읆 援ъ“)
                for col, value in ((3, "0"), (4, "0"), (5, "0"), (6, "0"), (7, "0%")):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(i, col, item)

    def show_result_page(self):
        """?쒗뿕 寃곌낵 ?섏씠吏 ?쒖떆"""
        if self.embedded:
            # Embedded 紐⑤뱶: ?쒓렇?먯쓣 emit?섏뿬 main.py?먯꽌 ?ㅽ깮 ?꾪솚 泥섎━
            self.showResultRequested.emit(self)
        else:
            # Standalone 紐⑤뱶: ??李쎌쑝濡??꾩젽 ?쒖떆
            if hasattr(self, 'result_window') and self.result_window is not None:
                self.result_window.close()
            self.result_window = ResultPageWidget(self)
            self.result_window.show()

    def toggle_fullscreen(self):
        """?꾩껜?붾㈃ ?꾪솚 (main.py ?ㅽ???"""
        try:
            if not self._is_fullscreen:
                # ?꾩껜?붾㈃?쇰줈 ?꾪솚
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
                    self.fullscreen_btn.setText("?꾩껜?붾㈃ ?댁젣")
            else:
                # ?먮옒 ?ш린濡?蹂듭썝
                self.setWindowFlags(Qt.Window)
                self.show()
                if self._saved_geom:
                    self.restoreGeometry(self._saved_geom)
                self.showNormal()
                self._is_fullscreen = False
                if hasattr(self, 'fullscreen_btn'):
                    self.fullscreen_btn.setText("?꾩껜?붾㈃")
        except Exception as e:
            Logger.debug(f"?꾩껜?붾㈃ ?꾪솚 ?ㅻ쪟: {e}")

    def build_result_payload(self):
        """理쒖쥌 寃곌낵瑜?dict濡?諛섑솚"""
        total_fields = self.total_pass_cnt + self.total_error_cnt
        score = (self.total_pass_cnt / total_fields) * 100 if total_fields > 0 else 0
        return {
            "score": score,
            "pass_count": self.total_pass_cnt,
            "error_count": self.total_error_cnt,
            "details": self.final_report if hasattr(self, "final_report") else ""
        }

    def exit_btn_clicked(self):
        reply = QMessageBox.question(self, '?꾨줈洹몃옩 醫낅즺',
                                     '?뺣쭚濡??꾨줈洹몃옩??醫낅즺?섏떆寃좎뒿?덇퉴?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:

            try:
                APIClient().send_heartbeat_pending(getattr(self.CONSTANTS, "request_id", ""))
            except Exception as e:
                Logger.warning(f"?좑툘 醫낅즺 ??stopped ?곹깭 ?꾩넚 ?ㅽ뙣: {e}")
            QApplication.instance().setProperty("skip_exit_confirm", True)
            result_payload = self.build_result_payload()

            # ??醫낅즺 ???쇱떆?뺤? ?뚯씪 ??젣
            self.cleanup_paused_file()

            QApplication.quit()

    def get_setting(self):
        self.setting_variables = QSettings('My App', 'Variable')
        self.system = "video"  # 怨좎젙

        # 湲곕낯 ?쒖뒪???ㅼ젙
        self.radio_check_flag = "video"
        self.message = self.videoMessages  # ?ㅼ젣 API ?대쫫 (?듭떊??
        self.message_display = self.videoMessagesDisplay  # ?쒖떆???대쫫
        self.inMessage = self.videoInMessage
        self.outSchema = self.videoOutSchema
        self.inCon = self.videoInConstraint
        self.webhookSchema = self.webhookInSchema

        # 湲곕낯 ?몄쬆 ?ㅼ젙 (CONSTANTS.py?먯꽌 媛?몄샂)
        self.r2 = self.auth_type
        if self.r2 == "Digest Auth":
            self.r2 = "D"
        elif self.r2 == "Bearer Token":
            self.r2 = "B"

        # ??URL ?낅뜲?댄듃 (base_url + ?쒕굹由ъ삤紐? - ?ㅼ뿼 諛⑹?: CONSTANTS?먯꽌 吏곸젒 ?쎄린
        if hasattr(self, 'spec_config') and hasattr(self, 'url_text_box'):
            test_name = self.spec_config.get('test_name', self.current_spec_id).replace("/", "")
            fresh_base_url = str(getattr(self.CONSTANTS, 'url', self._original_base_url))
            self.pathUrl = fresh_base_url.rstrip('/') + "/" + test_name
            self.url_text_box.setText(self.pathUrl)
            print(f"[SYSTEM DEBUG] get_setting?먯꽌 pathUrl ?ㅼ젙: {self.pathUrl}")

    def closeEvent(self, event):
        """李??リ린 ?대깽??- ??대㉧ ?뺣━"""
        # ????대㉧ 以묒?
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

