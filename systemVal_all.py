# 시스템 검증 소프트웨어
# physical security integrated system validation software
import os
import time
import threading
import json
import requests
import sys
import spec
import urllib3
import warnings
from datetime import datetime

# SSL 경고 비활성화 (자체 서명 인증서 사용 시)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

# Dynamic spec imports - will be loaded based on CONSTANTS.specs
# Import modules for dynamic attribute access
import spec.video.videoData_response as video_data_response
import spec.video.videoData_request as video_data_request
import spec.video.videoSchema_request as video_schema_request
import spec.video.videoSchema_response as video_schema_response
from urllib.parse import urlparse
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor
from PyQt5.QtCore import *
from api.webhook_api import WebhookThread
from core.functions import BearerAuth, json_check_, field_finder, save_result, resource_path, set_auth, json_to_data, timeout_field_finder
from core.json_checker_new import check_message_error
from requests.auth import HTTPDigestAuth
import config.CONSTANTS as CONSTANTS
import traceback
import importlib


# 통합된 상세 내용 확인 팝업창 클래스
class CombinedDetailDialog(QDialog):
    def __init__(self, api_name, step_buffer, schema_data):
        super().__init__()
        
        self.setWindowTitle(f"{api_name} - 통합 상세 정보")
        self.setGeometry(400, 300, 1200, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # 전체 레이아웃
        main_layout = QVBoxLayout()
        
        # 상단 제목
        title_label = QLabel(f"{api_name} API 상세 정보")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 3열 테이블 형태로 배치
        content_layout = QHBoxLayout()
        
        # 1열: 메시지 데이터
        data_group = QGroupBox("메시지 데이터")
        data_layout = QVBoxLayout()
        self.data_browser = QTextBrowser()
        self.data_browser.setAcceptRichText(True)
        data_text = step_buffer["data"] if step_buffer["data"] else "아직 수신된 데이터가 없습니다."
        self.data_browser.setPlainText(data_text)
        data_layout.addWidget(self.data_browser)
        data_group.setLayout(data_layout)
        
        # 2열: 메시지 규격
        schema_group = QGroupBox("메시지 규격")
        schema_layout = QVBoxLayout()
        self.schema_browser = QTextBrowser()
        self.schema_browser.setAcceptRichText(True)
        schema_text = self._format_schema(schema_data)
        self.schema_browser.setPlainText(schema_text)
        schema_layout.addWidget(self.schema_browser)
        schema_group.setLayout(schema_layout)
        
        # 3열: 검증 오류
        error_group = QGroupBox("검증 오류")
        error_layout = QVBoxLayout()
        self.error_browser = QTextBrowser()
        self.error_browser.setAcceptRichText(True)
        result = step_buffer["result"]
        # 항상 step_buffer["error"]를 그대로 보여주고, 없으면 안내 메시지
        error_text = step_buffer["error"] if step_buffer["error"] else ("오류가 없습니다." if result=="PASS" else "오류 내용 없음")
        error_msg = f"검증 결과: {result}\n\n{error_text}"
        self.error_browser.setPlainText(error_msg)
        error_layout.addWidget(self.error_browser)
        error_group.setLayout(error_layout)
        
        # 3개 그룹을 가로로 배치
        content_layout.addWidget(data_group)
        content_layout.addWidget(schema_group)
        content_layout.addWidget(error_group)
        
        # 확인 버튼
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        
        # 레이아웃 구성
        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.buttonBox)
        
        self.setLayout(main_layout)
        
    def _format_schema(self, schema):
        """스키마 구조를 문자열로 변환"""
        if not schema:
            return "스키마 정보가 없습니다."
            
        def schema_to_string(schema_obj, indent=0):
            result = ""
            spaces = "  " * indent
            
            if isinstance(schema_obj, dict):
                for key, value in schema_obj.items():
                    if hasattr(key, 'expected_data'):  # OptionalKey인 경우
                        key_name = f"{key.expected_data} (선택사항)"
                    else:
                        key_name = str(key)
                        
                    if isinstance(value, dict):
                        result += f"{spaces}{key_name}: {{\n"
                        result += schema_to_string(value, indent + 1)
                        result += f"{spaces}}}\n"
                    elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        result += f"{spaces}{key_name}: [\n"
                        result += schema_to_string(value[0], indent + 1)
                        result += f"{spaces}]\n"
                    else:
                        result += f"{spaces}{key_name}: {value.__name__ if hasattr(value, '__name__') else str(value)}\n"
            return result
        
        return schema_to_string(schema)


class CustomDialog(QDialog):  # popup window for validation result
    def __init__(self, dmsg, dstep):
        super().__init__()
        self.setWindowTitle(dstep)
        self.setGeometry(1600, 500, 400, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.tb = QTextBrowser()
        self.tb.setAcceptRichText(True)
        self.tb.append(dmsg)
        self.layout.addWidget(self.tb)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.exec_()


# 시험 결과 페이지 다이얼로그
class ResultPageDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle('시스템 연동 시험 결과')
        self.setGeometry(100, 100, 1100, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        
        self.initUI()
    
    def initUI(self):
        mainLayout = QVBoxLayout()
        
        # 상단 큰 제목
        title_label = QLabel('시스템 연동 시험 결과', self)
        title_font = title_label.font()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(title_label)
        
        # 시험 정보 섹션
        info_group = QGroupBox('시험 정보')
        info_layout = QVBoxLayout()
        
        test_info = self.parent.load_test_info_from_constants()
        info_text = ""
        for label, value in test_info:
            info_text += f"{label}: {value}\n"
        
        info_browser = QTextBrowser()
        info_browser.setPlainText(info_text)
        info_browser.setMaximumHeight(150)
        info_layout.addWidget(info_browser)
        info_group.setLayout(info_layout)
        mainLayout.addWidget(info_group)
        
        mainLayout.addSpacing(10)
        
        # 시험 결과 레이블
        result_label = QLabel('시험 결과')
        mainLayout.addWidget(result_label)
        
        # 결과 테이블 (parent의 테이블 데이터 복사) - 동적 API 개수
        api_count = self.parent.tableWidget.rowCount()
        self.tableWidget = QTableWidget(api_count, 8)
        self.tableWidget.setHorizontalHeaderLabels([
            "API 명", "결과", "검증 횟수", "통과 필드 수", 
            "전체 필드 수", "실패 횟수", "평가 점수", "상세 내용"
        ])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QSize(16, 16))
        
        # 테이블 크기 설정
        self.tableWidget.setMinimumSize(950, 300)
        self.tableWidget.resize(1050, 400)
        
        # 컬럼 너비 설정
        self.tableWidget.setColumnWidth(0, 240)
        self.tableWidget.setColumnWidth(1, 90)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setColumnWidth(3, 110)
        self.tableWidget.setColumnWidth(4, 110)
        self.tableWidget.setColumnWidth(5, 100)
        self.tableWidget.setColumnWidth(6, 110)
        self.tableWidget.setColumnWidth(7, 130)
        
        # 행 높이 설정
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 40)
        
        # parent 테이블 데이터 복사
        self._copy_table_data()
        
        # 상세 내용 버튼 클릭 이벤트
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)
        
        mainLayout.addWidget(self.tableWidget)
        
        mainLayout.addSpacing(15)
        
        # 평가 점수 표시
        score_group = self._create_score_display()
        mainLayout.addWidget(score_group)
        
        mainLayout.addSpacing(20)
        
        # 닫기 버튼
        close_btn = QPushButton('닫기')
        close_btn.setFixedSize(140, 50)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFB6C1;
                border: 2px solid #FF69B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #8B0000;
            }
            QPushButton:hover {
                background-color: #FFC0CB;
                border: 2px solid #FF1493;
            }
            QPushButton:pressed {
                background-color: #FF69B4;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        close_layout = QHBoxLayout()
        close_layout.setAlignment(Qt.AlignCenter)
        close_layout.addWidget(close_btn)
        mainLayout.addLayout(close_layout)
        
        mainLayout.addStretch()
        self.setLayout(mainLayout)
    
    def _copy_table_data(self):
        """parent의 테이블 데이터를 복사"""
        api_count = self.parent.tableWidget.rowCount()
        for row in range(api_count):
            # API 명
            api_item = self.parent.tableWidget.item(row, 0)
            if api_item:
                self.tableWidget.setItem(row, 0, QTableWidgetItem(api_item.text()))
            
            # 결과 아이콘 (위젯 복사)
            icon_widget = self.parent.tableWidget.cellWidget(row, 1)
            if icon_widget:
                new_icon_widget = QWidget()
                new_icon_layout = QHBoxLayout()
                new_icon_layout.setContentsMargins(0, 0, 0, 0)
                
                # 원본 아이콘 찾기
                old_label = icon_widget.findChild(QLabel)
                if old_label:
                    new_icon_label = QLabel()
                    new_icon_label.setPixmap(old_label.pixmap())
                    new_icon_label.setToolTip(old_label.toolTip())
                    new_icon_label.setAlignment(Qt.AlignCenter)
                    
                    new_icon_layout.addWidget(new_icon_label)
                    new_icon_layout.setAlignment(Qt.AlignCenter)
                    new_icon_widget.setLayout(new_icon_layout)
                    
                    self.tableWidget.setCellWidget(row, 1, new_icon_widget)
            
            # 나머지 컬럼들 (검증 횟수, 통과 필드 수, 전체 필드 수, 실패 횟수, 평가 점수)
            for col in range(2, 7):
                item = self.parent.tableWidget.item(row, col)
                if item:
                    new_item = QTableWidgetItem(item.text())
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(row, col, new_item)
            
            # 상세 내용 버튼
            detail_btn = QPushButton('확인')
            detail_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFB6C1;
                    border: 1px solid #FF69B4;
                    border-radius: 3px;
                    padding: 5px;
                    font-weight: bold;
                    color: #8B0000;
                }
                QPushButton:hover {
                    background-color: #FFC0CB;
                }
            """)
            self.tableWidget.setCellWidget(row, 7, detail_btn)
    
    def _create_score_display(self):
        """평가 점수 표시 그룹"""
        score_group = QGroupBox('평가 점수')
        score_group.setMaximumWidth(1050)
        score_group.setMinimumWidth(950)
        
        total_pass = self.parent.total_pass_cnt
        total_error = self.parent.total_error_cnt
        total_fields = total_pass + total_error
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0
        
        pass_label = QLabel(f"통과 필드 수: {total_pass}")
        total_label = QLabel(f"전체 필드 수: {total_fields}")
        score_label = QLabel(f"종합 평가 점수: {score:.1f}%")
        
        # 폰트 크기 조정
        font = pass_label.font()
        font.setPointSize(20)
        pass_label.setFont(font)
        total_label.setFont(font)
        score_label.setFont(font)
        
        layout = QHBoxLayout()
        layout.setSpacing(90)
        layout.addWidget(pass_label)
        layout.addWidget(total_label)
        layout.addWidget(score_label)
        layout.addStretch()
        
        score_group.setLayout(layout)
        return score_group
    
    def table_cell_clicked(self, row, col):
        """상세 내용 버튼 클릭 시"""
        if col == 7:  # 상세 내용 컬럼
            self.parent.show_combined_result(row)


class MyApp(QWidget):

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
                print(f"[DEBUG] [handle_authentication_response] Token updated: {self.token}")
    def __init__(self, embedded=False):
        importlib.reload(CONSTANTS)  # CONSTANTS 모듈을 다시 로드하여 최신 설정 반영
        super().__init__()
        self.embedded = embedded
        self.webhook_res = None
        self.res = None
        self.radio_check_flag = "video"  # 영상보안 시스템으로 고정
        self.img_pass = resource_path("assets/image/green.png")
        self.img_fail = resource_path("assets/image/red.png")
        self.img_none = resource_path("assets/image/black.png")

        self.flag_opt = True
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_view)
        self.pathUrl = None
        self.auth_type = None
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
        
        auth_temp, auth_temp2 = set_auth("config/config.txt")
        self.digestInfo = [auth_temp2[0], auth_temp2[1]]
        self.token = auth_temp

        # Load specs dynamically from CONSTANTS
        self.load_specs_from_constants()

        # step_buffers 동적 생성 (API 개수에 따라)
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS"} for _ in range(len(self.videoMessages))
        ]

        self.initUI()

        self.get_setting()
        self.webhook_flag = False
        self.webhook_msg = "."
        self.webhook_cnt = 99

    def load_specs_from_constants(self):
        """CONSTANTS.specs 설정에 따라 동적으로 spec 데이터 로드"""
        # specs는 [[inSchema_name, outData_name, messages_name, webhookSchema_name, webhookData_name, description], ...]
        if not hasattr(CONSTANTS, 'specs') or not CONSTANTS.specs:
            raise ValueError("CONSTANTS.specs가 정의되지 않았습니다!")
        
        # 첫 번째 spec 사용 (향후 여러 spec 지원 가능)
        spec = CONSTANTS.specs[0]
        inSchema_name = spec[0]  # e.g., "spec_001_inSchema"
        outData_name = spec[1]   # e.g., "spec_001_outData"
        messages_name = spec[2]  # e.g., "spec_001_messages"
        webhookSchema_name = spec[3]  # e.g., "spec_001_webhookSchema"
        webhookData_name = spec[4]  # e.g., "spec_001_webhookData"
        self.spec_description = spec[5]  # e.g., "영상보안 시스템 요청 메시지 검증 API 명세서"
        
        # Dynamic import based on spec names
        # Request schemas (inSchema) from videoSchema_request
        self.videoInSchema = getattr(video_schema_request, inSchema_name, [])
        # Request data (outData) from videoData_request
        self.videoOutMessage = getattr(video_data_request, outData_name, [])
        # Message names from videoData_request
        self.videoMessages = getattr(video_data_request, messages_name, [])
        # Webhook schemas from videoSchema_request
        self.videoWebhookSchema = getattr(video_schema_request, webhookSchema_name, [])
        # Webhook data from videoData_request
        self.videoWebhookData = getattr(video_data_request, webhookData_name, [])
        
        # Response schemas (outSchema) from videoSchema_response - need to infer name
        # Convention: spec_001 -> spec_002 for response
        outSchema_name = inSchema_name.replace("_inSchema", "_outSchema").replace("spec_001", "spec_002")
        self.videoOutSchema = getattr(video_schema_response, outSchema_name, [])
        
        # Response data (inData) from videoData_response
        inData_name = outData_name.replace("_outData", "_inData").replace("spec_001", "spec_002")
        self.videoInMessage = getattr(video_data_response, inData_name, [])
        
        # Response webhook schemas from videoSchema_response
        webhookInSchema_name = webhookSchema_name.replace("spec_001", "spec_002")
        self.videoWebhookInSchema = getattr(video_schema_response, webhookInSchema_name, [])
        
        # Response webhook data from videoData_response
        webhookInData_name = webhookData_name.replace("spec_001", "spec_002")
        self.videoWebhookInData = getattr(video_data_response, webhookInData_name, [])
        
        print(f"[DEBUG] Loaded spec: {self.spec_description}")
        print(f"[DEBUG] API count: {len(self.videoMessages)}")
        print(f"[DEBUG] API names: {self.videoMessages}")

    def _to_detail_text(self, val_text):
        """검증 결과 텍스트를 항상 사람이 읽을 문자열로 표준화"""
        if val_text is None:
            return "오류가 없습니다."
        if isinstance(val_text, list):
            return "\n".join(str(x) for x in val_text) if val_text else "오류가 없습니다."
        if isinstance(val_text, dict):
            try:
                import json
                return json.dumps(val_text, indent=2, ensure_ascii=False)
            except Exception:
                return str(val_text)
        return str(val_text)

    def update_table_row_with_retries(self, row, result, pass_count, error_count, data, error_text, retries):
        """테이블 행 업데이트 (실제 검증 횟수 포함, 플랫폼과 동일하게 아이콘 처리)"""
        if row >= self.tableWidget.rowCount():
            return
        # result가 '진행중'이면 검정색, PASS/FAIL이면 초록/빨강
        msg, img = self.icon_update_step(data, result, error_text)
        icon_widget = QWidget()
        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(img).pixmap(16, 16))
        icon_label.setToolTip(msg)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_widget.setLayout(icon_layout)
        self.tableWidget.setCellWidget(row, 1, icon_widget)
        self.tableWidget.setItem(row, 2, QTableWidgetItem(str(retries)))
        self.tableWidget.item(row, 2).setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(row, 3, QTableWidgetItem(str(pass_count)))
        self.tableWidget.item(row, 3).setTextAlignment(Qt.AlignCenter)
        total_fields = pass_count + error_count
        self.tableWidget.setItem(row, 4, QTableWidgetItem(str(total_fields)))
        self.tableWidget.item(row, 4).setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(row, 5, QTableWidgetItem(str(error_count)))
        self.tableWidget.item(row, 5).setTextAlignment(Qt.AlignCenter)
        if total_fields > 0:
            score = (pass_count / total_fields) * 100
            self.tableWidget.setItem(row, 6, QTableWidgetItem(f"{score:.1f}%"))
        else:
            self.tableWidget.setItem(row, 6, QTableWidgetItem("0%"))
        self.tableWidget.item(row, 6).setTextAlignment(Qt.AlignCenter)
        setattr(self, f"step{row+1}_msg", msg)

    def load_test_info_from_constants(self):
        return [
            ("기업명", CONSTANTS.company_name),
            ("제품명", CONSTANTS.product_name),
            ("버전", CONSTANTS.version),
            ("시험유형", CONSTANTS.test_category),
            ("시험대상", CONSTANTS.test_target),
            ("시험범위", CONSTANTS.test_range),
            ("사용자 인증 방식", CONSTANTS.auth_type),
            ("관리자 코드", CONSTANTS.admin_code),
            ("시험 접속 정보", CONSTANTS.url)
        ]

    def post(self, path, json_data, time_out):
        self.res = None
        # 인증 방식(r2)에 따라 auth 인자 결정 (토큰 유무로 분기 X)
        auth = None
        if self.r2 == "B":
            auth = BearerAuth(self.token) if self.token else None
        elif self.r2 == "D":
            auth = HTTPDigestAuth(self.digestInfo[0], self.digestInfo[1])
        # self.r2 == "None"이면 그대로 None

        try:
            print(f"[DEBUG] [post] Sending request to {path} with auth_type={self.r2}, token={self.token}")
            self.res = requests.post(
                path,
                headers=CONSTANTS.headers,
                data=json_data,
                auth=auth,
                verify=False,
                timeout=time_out
            )
        except Exception as e:
            print(e)

        # Webhook/Realtime 처리 (더 방어적으로)
        if "Realtime" in path:
            time.sleep(0.1)
            try:
                json_data_dict = json.loads(json_data.decode('utf-8'))
                trans_protocol = json_data_dict.get("transProtocol", {})
                if trans_protocol:
                    trans_protocol_type = trans_protocol.get("transProtocolType", {})
                    if "WebHook".lower() in str(trans_protocol_type).lower():
                        path_tmp = trans_protocol.get("transProtocolDesc", {})
                        # http/https 접두어 보정
                        if not path_tmp or str(path_tmp).strip() in ["None", "", "desc"]:
                            path_tmp = "https://127.0.0.1"
                        if not str(path_tmp).startswith("http"):
                            path_tmp = "https://" + str(path_tmp)
                        parsed = urlparse(str(path_tmp))
                        url = parsed.hostname if parsed.hostname is not None else "127.0.0.1"
                        port = parsed.port if parsed.port is not None else 80
                        msg = self.outMessage[-1]
                        self.webhook_flag = True
                        self.webhook_cnt = self.cnt
                        self.webhook_thread = WebhookThread(url, port, msg)
                        self.webhook_thread.result_signal.connect(self.handle_webhook_result)
                        self.webhook_thread.start()
            except Exception as e:
                print(e)
                import traceback
                traceback.print_exc()


    def handle_webhook_result(self, result):
        self.webhook_flag = True
        self.webhook_res = result
        a = self.webhook_thread.stop()
        self.webhook_thread.wait()
        # tmp_res_auth =

    def get_webhook_result(self):
        tmp_webhook_res = json.dumps(self.webhook_res, indent=4, ensure_ascii=False)
        if self.webhook_cnt < len(self.message):
            message_name = "step " + str(self.webhook_cnt + 1) + ": " + self.message[self.webhook_cnt]
        else:
            message_name = f"step {self.webhook_cnt + 1}: (index out of range)"

        # Adapted for new single-element list structure of webhookSchema
        if isinstance(self.webhookSchema, list) and len(self.webhookSchema) > 0:
            schema_to_check = self.webhookSchema[0]
            val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(schema_to_check, self.webhook_res, self.flag_opt)
        else:
            val_result, val_text, key_psss_cnt, key_error_cnt = "FAIL", "webhookSchema index error", 0, 0

        self.valResult.append(message_name)
        self.valResult.append("\n" + tmp_webhook_res)
        self.valResult.append(val_result)
        self.total_error_cnt += key_error_cnt
        self.total_pass_cnt += key_psss_cnt
        
        # 평가 점수 디스플레이 업데이트
        self.update_score_display()
        
        self.valResult.append(
            "Score : " + str((self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
        self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
            self.total_error_cnt) + "(누적 오류 필드 수)\n")

        if val_result == "PASS":
            msg = "\n" + tmp_webhook_res + "\n\n" + "Result: " + val_text + "\n"
            img = self.img_pass
        else:
            msg = "\n" + tmp_webhook_res + "\n\n" + "Result: " + val_result + "\nResult details:\n" + val_text + "\n"
            img = self.img_fail

        # 새로운 테이블 업데이트 함수 사용 (개별 검증 횟수 적용)
        if self.webhook_cnt < self.tableWidget.rowCount():
            total_fields = key_psss_cnt + key_error_cnt
            if self.webhook_cnt < len(CONSTANTS.num_retries):
                current_retries = CONSTANTS.num_retries[self.webhook_cnt]
            else:
                current_retries = 1
            self.update_table_row_with_retries(self.webhook_cnt, val_result, key_psss_cnt, key_error_cnt, 
                                tmp_webhook_res, self._to_detail_text(val_text), current_retries)

        # step_buffers 업데이트 추가 (실시간 모니터링과 상세보기 일치)
        if self.webhook_cnt < len(self.step_buffers):
            webhook_data_text = tmp_webhook_res
            webhook_error_text = self._to_detail_text(val_text) if val_result == "FAIL" else "오류가 없습니다."
            self.step_buffers[self.webhook_cnt]["data"] += f"\n\n--- Webhook 결과 ---\n{webhook_data_text}"
            self.step_buffers[self.webhook_cnt]["error"] += f"\n\n--- Webhook 검증 ---\n{webhook_error_text}"
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
            if self.cnt >= len(self.message) or self.cnt >= len(CONSTANTS.time_out):
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

            # 디버깅 정보 추가
            if self.cnt >= 4:  # StreamURLs 이후부터 로깅
                print(f"[DEBUG] cnt={self.cnt}, post_flag={self.post_flag}, processing_response={self.processing_response}")
                print(f"[DEBUG] current_retry={self.current_retry}, webhook_flag={self.webhook_flag}")
                print(f"[DEBUG] time_interval={time_interval}, timeout={CONSTANTS.time_out[self.cnt]/1000 if self.cnt < len(CONSTANTS.time_out) else 'N/A'}")
                print(f"[DEBUG] self.res is None: {self.res is None}")

            if self.webhook_flag is True:
                time.sleep(1)
                time_interval += 1

            if (self.post_flag is False and 
                self.processing_response is False and 
                self.cnt < len(self.message) and 
                self.cnt < len(CONSTANTS.num_retries) and
                self.current_retry < CONSTANTS.num_retries[self.cnt]):
                
                self.message_in_cnt += 1
                self.time_pre = time.time()

                retry_info = f" (시도 {self.current_retry + 1}/{CONSTANTS.num_retries[self.cnt]})"
                if self.cnt < len(self.message):
                    self.message_name = "step " + str(self.cnt + 1) + ": " + self.message[self.cnt] + retry_info
                else:
                    self.message_name = f"step {self.cnt + 1}: (index out of range)" + retry_info

                # if self.tmp_msg_append_flag:
                #     self.valResult.append(self.message_name)
                if self.cnt == 0 and self.current_retry == 0:
                    self.tmp_msg_append_flag = True

                # 시스템이 플랫폼에 요청 전송
                current_timeout = CONSTANTS.time_out[self.cnt] / 1000 if self.cnt < len(CONSTANTS.time_out) else 5.0
                path = self.pathUrl + "/" + (self.message[self.cnt] if self.cnt < len(self.message) else "")
                inMessage = self.inMessage[self.cnt] if self.cnt < len(self.inMessage) else {}
                json_data = json.dumps(inMessage).encode('utf-8')

                # 순서 확인용 로그
                print(f"[SYSTEM] 플랫폼에 요청 전송: {(self.message[self.cnt] if self.cnt < len(self.message) else 'index out of range')} (시도 {self.current_retry + 1})")

                t = threading.Thread(target=self.post, args=(path, json_data, current_timeout), daemon=True)
                t.start()
                self.post_flag = True

            # timeout 조건은 응답 대기/재시도 판단에만 사용
            elif self.cnt < len(CONSTANTS.time_out) and time_interval >= CONSTANTS.time_out[self.cnt] / 1000 and self.post_flag is True:
                # 디버깅 로그 추가
                if self.cnt >= 4:
                    print(f"[DEBUG] TIMEOUT TRIGGERED for cnt={self.cnt}, time_interval={time_interval}, timeout_limit={(CONSTANTS.time_out[self.cnt]/1000) if self.cnt < len(CONSTANTS.time_out) else 'N/A'}")

                if self.cnt < len(self.message):
                    self.message_error.append([self.message[self.cnt]])
                else:
                    self.message_error.append([f"index out of range: {self.cnt}"])
                self.message_in_cnt = 0
                current_retries = CONSTANTS.num_retries[self.cnt] if self.cnt < len(CONSTANTS.num_retries) else 1
                self.valResult.append(f"Message Missing! (시도 {self.current_retry + 1}/{current_retries})")

                # 현재 시도에 대한 타임아웃 처리
                if self.cnt < len(self.outSchema):
                    tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(self.outSchema[self.cnt])
                else:
                    tmp_fields_rqd_cnt, tmp_fields_opt_cnt = 0, 0
                add_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                if self.flag_opt:
                    add_err += tmp_fields_opt_cnt

                self.total_error_cnt += add_err
                self.total_pass_cnt += 0

                # 평가 점수 디스플레이 업데이트
                self.update_score_display()
                
                self.valResult.append("Score : " + str(
                    (self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 검증 통과 필드 수), " + str(
                    self.total_error_cnt) + "(누적 검증 오류 필드 수)\n")
                
                # 재시도 카운터 증가
                self.current_retry += 1
                
                # 재시도 완료 여부 확인
                if (self.cnt < len(CONSTANTS.num_retries) and 
                    self.current_retry >= CONSTANTS.num_retries[self.cnt]):
                    # 모든 재시도 완료 - 버퍼에 최종 결과 저장
                    self.step_buffers[self.cnt]["data"] = "타임아웃으로 인해 수신된 데이터가 없습니다."
                    current_retries = CONSTANTS.num_retries[self.cnt] if self.cnt < len(CONSTANTS.num_retries) else 1
                    self.step_buffers[self.cnt]["error"] = f"Message Missing! - 모든 시도({current_retries}회)에서 타임아웃 발생"
                    self.step_buffers[self.cnt]["result"] = "FAIL"
                    
                    # 테이블 업데이트 (Message Missing)
                    self.update_table_row_with_retries(self.cnt, "FAIL", 0, add_err, "", "Message Missing!", current_retries)
                    
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
                self.time_pre = time.time() + 2.0  # 플랫폼과 동일한 2초 대기

                if self.cnt >= len(self.message):
                    self.tick_timer.stop()
                    self.valResult.append("검증 절차가 완료되었습니다.")
                    self.cnt = 0
                    self.final_report += "전체 점수: " + str(
                        (self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)) + "\n"
                    self.final_report += "전체 결과: " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                        self.total_error_cnt) + "(누적 오류 필드 수)" + "\n"
                    self.final_report += "\n"
                    self.final_report += "메시지 검증 세부 결과 \n"
                    self.final_report += self.valResult.toPlainText()

                    self.sbtn.setEnabled(True)
                    self.stop_btn.setDisabled(True)
                return

            # 응답이 도착한 경우 처리
            elif self.post_flag == True:
                    #  if self.cnt == 0 and
                    #    self.tmp_msg_append_flag = True
                    if self.res != None:
                        # 응답 처리 시작
                        self.processing_response = True
                        
                        if self.cnt == 0 or self.tmp_msg_append_flag:  # and -> or 수정함- 240710
                            self.valResult.append(self.message_name)

                        res_data = self.res.text
                        #res_data = json.loads(res_data)

                        try:
                            res_data = json.loads(res_data)
                        except Exception as e:
                            self._append_text(f"응답 JSON 파싱 오류: {e}")
                            self._append_text({"raw_response": self.res.text})
                            # 이후 로직 건너뜀
                            self.post_flag = False
                            self.processing_response = False
                            self.current_retry += 1
                            return

                        # 현재 재시도 정보
                        current_retries = CONSTANTS.num_retries[self.cnt] if self.cnt < len(CONSTANTS.num_retries) else 1
                        current_protocol = CONSTANTS.trans_protocol[self.cnt] if self.cnt < len(CONSTANTS.trans_protocol) else "Unknown"

                        # 단일 응답에 대한 검증 처리
                        tmp_res_auth = json.dumps(res_data, indent=4, ensure_ascii=False)
                        
                        if self.webhook_flag:  # webhook 인 경우
                            val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.outSchema[-1],
                                                                                            res_data, self.flag_opt)
                            if self.message[self.cnt] == "Authentication":
                                self.handle_authentication_response(res_data)
                        else:  # webhook 아닌경우
                            val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.outSchema[self.cnt],
                                                                                                res_data, self.flag_opt)
                            if self.message[self.cnt] == "Authentication":
                                self.handle_authentication_response(res_data)

                        # 이번 시도의 결과
                        final_result = val_result
                        
                        # 플랫폼과 동일한 누적 카운트 로직
                        if not hasattr(self, 'step_pass_counts'):
                            self.step_pass_counts = [0] * 9
                            self.step_error_counts = [0] * 9
                            self.step_pass_flags = [0] * 9  # PASS 횟수 카운트
                        
                        # 이번 시도 결과를 누적
                        self.step_pass_counts[self.cnt] += key_psss_cnt
                        self.step_error_counts[self.cnt] += key_error_cnt
                        
                        if final_result == "PASS":
                            self.step_pass_flags[self.cnt] += 1
                        
                        total_pass_count = self.step_pass_counts[self.cnt]
                        total_error_count = self.step_error_counts[self.cnt]

                        # (1) 스텝 버퍼 저장 - 재시도별로 누적
                        data_text = tmp_res_auth
                        error_text = self._to_detail_text(val_text) if val_result == "FAIL" else "오류가 없습니다."
                        
                        # 기존 버퍼에 누적 (재시도 정보와 함께)
                        if self.current_retry == 0:
                            # 첫 번째 시도인 경우 초기화
                            self.step_buffers[self.cnt]["data"] = f"[시도 {self.current_retry + 1}/{current_retries}]\n{data_text}"
                            self.step_buffers[self.cnt]["error"] = f"[시도 {self.current_retry + 1}/{current_retries}]\n{error_text}"
                            self.step_buffers[self.cnt]["result"] = val_result  # 첫 시도 결과로 초기화
                        else:
                            # 재시도인 경우 누적
                            self.step_buffers[self.cnt]["data"] += f"\n\n[시도 {self.current_retry + 1}/{current_retries}]\n{data_text}"
                            self.step_buffers[self.cnt]["error"] += f"\n\n[시도 {self.current_retry + 1}/{current_retries}]\n{error_text}"
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
                                self.step_buffers[self.cnt]["error"] = f"[시도 {self.current_retry + 1}/{current_retries}]\n{error_text}"
                        
                        # 진행 중 표시 (플랫폼과 동일하게)
                        message_name = "step " + str(self.cnt + 1) + ": " + self.message[self.cnt]
                        # 각 시도별로 pass/error count는 누적이 아니라 이번 시도만 반영해야 함
                        # key_psss_cnt, key_error_cnt는 이번 시도에 대한 값임
                        if self.current_retry + 1 < current_retries:
                            # 아직 재시도가 남아있으면 진행중으로 표시
                            self.update_table_row_with_retries(
                                self.cnt, "진행중", key_psss_cnt, key_error_cnt,
                                f"검증 진행중... ({self.current_retry + 1}/{current_retries})",
                                f"시도 {self.current_retry + 1}/{current_retries}", self.current_retry + 1)
                        else:
                            # 마지막 시도이면 최종 결과 표시
                            final_buffer_result = self.step_buffers[self.cnt]["result"]
                            # 마지막 시도에서는 누적이 아니라 마지막 시도 결과만 반영
                            self.update_table_row_with_retries(
                                self.cnt, final_buffer_result, key_psss_cnt, key_error_cnt,
                                tmp_res_auth, error_text, current_retries)

                        self.valResult.append(f"\n검증 진행: {self.current_retry + 1}/{current_retries}회")
                        self.valResult.append(f"프로토콜: {current_protocol}")
                        self.valResult.append("\n" + data_text)
                        self.valResult.append(final_result)

                        self.total_error_cnt += total_error_count
                        self.total_pass_cnt += total_pass_count
                        
                        # 평가 점수 디스플레이 업데이트
                        self.update_score_display()
                        
                        self.valResult.append("Score : " + str(
                            (self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                        self.valResult.append(
                            "Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                                self.total_error_cnt) + "(누적 오류 필드 수)\n")
                    
                        # 재시도 카운터 증가
                        self.current_retry += 1
                        
                        # 현재 API의 모든 재시도가 완료되었는지 확인
                        if (self.cnt < len(CONSTANTS.num_retries) and 
                            self.current_retry >= CONSTANTS.num_retries[self.cnt]):
                            # 다음 API로 이동
                            self.cnt += 1
                            self.current_retry = 0  # 재시도 카운터 리셋
                        
                        self.message_in_cnt = 0
                        self.post_flag = False 
                        self.processing_response = False 
                        
                        # 재시도 여부에 따라 대기 시간 조정 (플랫폼과 동기화)
                        if (self.cnt < len(CONSTANTS.num_retries) and 
                            self.current_retry < CONSTANTS.num_retries[self.cnt] - 1):
                            self.time_pre = time.time() + 2.0  # 재시도 예정 시 2초 대기 (플랫폼과 동일)
                        else:
                            self.time_pre = time.time() + 2.0  # 마지막 시도 후 2초 대기
                        self.message_in_cnt = 0

                        if self.webhook_flag and self.webhook_res is not None:
                            self.get_webhook_result()

            if self.cnt >= len(self.message):
                self.tick_timer.stop()
                self.valResult.append("검증 절차가 완료되었습니다.")
                
                self.processing_response = False
                self.post_flag = False

                self.cnt = 0
                self.current_retry = 0  # 재시도 카운터도 리셋
                self.final_report += "전체 점수: "+  str((self.total_pass_cnt/(self.total_pass_cnt+self.total_error_cnt)*100))+"\n"
                self.final_report += "전체 결과: "+ str(self.total_pass_cnt)+"(누적 통과 필드 수), "+str(self.total_error_cnt)+"(누적 오류 필드 수)"+"\n"
                self.final_report += "\n"
                self.final_report += "메시지 검증 세부 결과 \n"
                self.final_report += self.valResult.toPlainText()
                self.sbtn.setEnabled(True)
                self.stop_btn.setDisabled(True)

        except Exception as err:
            print(f"[ERROR] Exception in update_view: {err}")
            print(f"[ERROR] Current state - cnt={self.cnt}, current_retry={self.current_retry}")
            print(f"[ERROR] Traceback:")
            traceback.print_exc()
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error Message: 오류 확인 후 검증 절차를 다시 시작해주세요")
            msg.setInformativeText(f"Error at step {self.cnt+1}: {str(err)}")
            msg.setWindowTitle("Error")
            msg.exec_()
            self.tick_timer.stop()
            self.valResult.append(f"검증 절차가 중지되었습니다. (오류 위치: Step {self.cnt+1})")
            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)

    def icon_update_step(self, auth_, result_, text_):
        # 플랫폼과 동일하게 '진행중'이면 검정색, PASS면 초록, FAIL이면 빨강
        if result_ == "PASS":
            msg = auth_ + "\n\n" + "Result: " + text_
            img = self.img_pass
        elif result_ == "진행중":
            msg = auth_ + "\n\n" + "Status: " + text_
            img = self.img_none
        else:
            msg = auth_ + "\n\n" + "Result: " + result_ + "\nResult details:\n" + text_
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
            icon_label.setPixmap(QIcon(img).pixmap(16, 16))
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
        # 1열(세로) 레이아웃으로 통합
        mainLayout = QVBoxLayout()

        # 상단 큰 제목
        self.title_label = QLabel('시스템 연동 검증', self)
        title_font = self.title_label.font()
        title_font.setPointSize(22)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.title_label)

        # 시험 결과
        self.valmsg = QLabel('시험 결과', self)
        mainLayout.addWidget(self.valmsg)

        self.init_centerLayout()
        contentWidget = QWidget()
        contentWidget.setLayout(self.centerLayout)
        contentWidget.setMaximumSize(1050, 400)
        contentWidget.setMinimumSize(950, 300)
        mainLayout.addWidget(contentWidget)

        mainLayout.addSpacing(15)

        # 수신 메시지 실시간 모니터링
        monitor_label = QLabel("수신 메시지 실시간 모니터링")
        mainLayout.addWidget(monitor_label)
        self.valResult = QTextBrowser(self)
        self.valResult.setMaximumHeight(200)
        self.valResult.setMaximumWidth(1050)
        self.valResult.setMinimumWidth(950)
        mainLayout.addWidget(self.valResult)

        # 버튼 그룹 (평가 시작, 일시 정지, 종료) - 아래쪽, 가운데 정렬
        buttonGroup = QWidget()
        buttonLayout = QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignCenter)

        self.sbtn = QPushButton(self)
        self.sbtn.setText('평가 시작')
        self.sbtn.setFixedSize(140, 50)
        self.sbtn.setStyleSheet("""
            QPushButton {
                background-color: #FFB6C1;  /* 파스텔 핑크 */
                border: 2px solid #FF69B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #8B0000;  /* 진한 빨간색 텍스트 */
            }
            QPushButton:hover {
                background-color: #FFC0CB;  /* 호버시 더 밝은 핑크 */
                border: 2px solid #FF1493;
            }
            QPushButton:pressed {
                background-color: #FF69B4;  /* 클릭시 더 진한 핑크 */
            }
            QPushButton:disabled {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                color: #999999;
            }
        """)
        self.sbtn.clicked.connect(self.start_btn_clicked)

        self.stop_btn = QPushButton(self)
        self.stop_btn.setText('일시 정지')
        self.stop_btn.setFixedSize(140, 50)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFB6C1;  /* 파스텔 핑크 */
                border: 2px solid #FF69B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #8B0000;  /* 진한 빨간색 텍스트 */
            }
            QPushButton:hover {
                background-color: #FFC0CB;  /* 호버시 더 밝은 핑크 */
                border: 2px solid #FF1493;
            }
            QPushButton:pressed {
                background-color: #FF69B4;  /* 클릭시 더 진한 핑크 */
            }
            QPushButton:disabled {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                color: #999999;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_btn_clicked)
        self.stop_btn.setDisabled(True)

        self.rbtn = QPushButton(self)
        self.rbtn.setText('종료')
        self.rbtn.setFixedSize(140, 50)
        self.rbtn.setStyleSheet("""
            QPushButton {
                background-color: #FFB6C1;
                border: 2px solid #FF69B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #8B0000;
            }
            QPushButton:hover {
                background-color: #FFC0CB;
                border: 2px solid #FF1493;
            }
            QPushButton:pressed {
                background-color: #FF69B4;
            }
            QPushButton:disabled {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                color: #999999;
            }
        """)
        self.rbtn.clicked.connect(self.exit_btn_clicked)

        self.result_btn = QPushButton(self)
        self.result_btn.setText('시험 결과')
        self.result_btn.setFixedSize(140, 50)
        self.result_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFB6C1;
                border: 2px solid #FF69B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #8B0000;
            }
            QPushButton:hover {
                background-color: #FFC0CB;
                border: 2px solid #FF1493;
            }
            QPushButton:pressed {
                background-color: #FF69B4;
            }
            QPushButton:disabled {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                color: #999999;
            }
        """)
        self.result_btn.clicked.connect(self.show_result_page)

        buttonLayout.addWidget(self.sbtn)
        buttonLayout.addSpacing(20)
        buttonLayout.addWidget(self.stop_btn)
        buttonLayout.addSpacing(20)
        buttonLayout.addWidget(self.rbtn)
        buttonLayout.addSpacing(20)
        buttonLayout.addWidget(self.result_btn)
        buttonGroup.setLayout(buttonLayout)

        mainLayout.addSpacing(20)
        mainLayout.addWidget(buttonGroup)
        mainLayout.addStretch()

        self.setLayout(mainLayout)
        self.setWindowTitle('물리보안 시스템 연동 검증 소프트웨어')
        self.setGeometry(100, 100, 1100, 700)

        if not self.embedded:
            self.show()

    def init_centerLayout(self):
        # 표 형태로 변경 - 동적 API 개수
        api_count = len(self.videoMessages)
        self.tableWidget = QTableWidget(api_count, 8)
        self.tableWidget.setHorizontalHeaderLabels(["API 명", "결과", "검증 횟수", "통과 필드 수", "전체 필드 수", "실패 횟수", "평가 점수", "상세 내용"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QSize(16, 16))
        
        # 테이블 크기 설정
        self.tableWidget.setMinimumSize(950, 300) 
        self.tableWidget.resize(1050, 400)  
        
        # 컬럼 너비 설정
        self.tableWidget.setColumnWidth(0, 240)  
        self.tableWidget.setColumnWidth(1, 90)   
        self.tableWidget.setColumnWidth(2, 100)   
        self.tableWidget.setColumnWidth(3, 110) 
        self.tableWidget.setColumnWidth(4, 110)  
        self.tableWidget.setColumnWidth(5, 100)  
        self.tableWidget.setColumnWidth(6, 110)  
        self.tableWidget.setColumnWidth(7, 130)  

        # 행 높이 설정
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 40)

        # 단계명 리스트 (동적으로 로드된 API 이름 사용)
        self.step_names = self.videoMessages
        for i, name in enumerate(self.step_names):
            # API 명
            self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{i+1}. {name}"))
            # 결과 아이콘 (위젯으로 중앙 정렬)
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
            
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            
            self.tableWidget.setCellWidget(i, 1, icon_widget)
            # 검증 횟수
            self.tableWidget.setItem(i, 2, QTableWidgetItem("0"))
            self.tableWidget.item(i, 2).setTextAlignment(Qt.AlignCenter)
            # 통과 필드 수
            self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
            self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
            # 전체 필드 수
            self.tableWidget.setItem(i, 4, QTableWidgetItem("0"))
            self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)
            # 실패 횟수
            self.tableWidget.setItem(i, 5, QTableWidgetItem("0"))
            self.tableWidget.item(i, 5).setTextAlignment(Qt.AlignCenter)
            # 평가 점수
            self.tableWidget.setItem(i, 6, QTableWidgetItem("0%"))
            self.tableWidget.item(i, 6).setTextAlignment(Qt.AlignCenter)
            # 상세 결과 버튼 (중앙 정렬을 위한 위젯 컨테이너)
            detail_btn = QPushButton("상세 내용 확인")
            detail_btn.setMaximumHeight(30)
            detail_btn.setMaximumWidth(130) 
            detail_btn.clicked.connect(lambda checked, row=i: self.show_combined_result(row))
            
            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_btn)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)
            
            self.tableWidget.setCellWidget(i, 7, container)

        # 결과 컬럼만 클릭 가능하도록 설정 (기존 기능 유지)
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)
        
        # centerLayout을 초기화하고 테이블 추가
        self.centerLayout = QVBoxLayout()
        self.centerLayout.addWidget(self.tableWidget)

        # step 메시지 초기화
        self.step1_msg = ""
        self.step2_msg = ""
        self.step3_msg = ""
        self.step4_msg = ""
        self.step5_msg = ""
        self.step6_msg = ""
        self.step7_msg = ""
        self.step8_msg = ""
        self.step9_msg = ""

    def show_combined_result(self, row):
        """통합 상세 내용 확인 - 데이터, 규격, 오류를 모두 보여주는 3열 팝업"""
        try:
            buf = self.step_buffers[row]
            api_name = self.tableWidget.item(row, 0).text()
            
            # 스키마 데이터 가져오기 -> 09/24 시스템쪽은 OutSchema
            try:
                schema_data = self.videoOutSchema[row] if row < len(self.videoOutSchema) else None
            except:
                schema_data = None
            
            # 통합 팝업창 띄우기
            dialog = CombinedDetailDialog(api_name, buf, schema_data)
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
        """평가 점수 디스플레이 업데이트"""
        if not (hasattr(self, "pass_count_label") and hasattr(self, "total_count_label") and hasattr(self, "score_label")):
            return
        total_fields = self.total_pass_cnt + self.total_error_cnt
        if total_fields > 0:
            score = (self.total_pass_cnt / total_fields) * 100
        else:
            score = 0
            
        self.pass_count_label.setText(f"통과 필드 수: {self.total_pass_cnt}")
        self.total_count_label.setText(f"전체 필드 수: {total_fields}")
        self.score_label.setText(f"종합 평가 점수: {score:.1f}%")

    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭 시 호출되는 함수"""
        if col == 1:  # 결과 컬럼 클릭 시에만 동작
            msg = getattr(self, f"step{row+1}_msg", "")
            if msg:
                api_name = self.step_names[row] if row < len(self.step_names) else f"Step {row+1}"
                CustomDialog(msg, api_name)


    def start_btn_clicked(self):

        json_to_data("video")
        self.sbtn.setDisabled(True)
        self.stop_btn.setEnabled(True)

        self.init_win()
        self.valResult.clear()
        
        # 상태 변수들 초기화
        self.final_report = ""
        self.post_flag = False
        self.processing_response = False  # 응답 처리 중 플래그 추가
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.message_in_cnt = 0
        self.message_error = []
        self.cnt = 0
        self.current_retry = 0  # 반복 카운터 초기화
        self.cnt_pre = 0
        self.time_pre = time.time()  # 0 대신 현재 시간으로 설정
        self.res = None
        self.webhook_res = None
        self.realtime_flag = False
        self.tmp_msg_append_flag = False
        
        # 플랫폼과 동일한 누적 카운트 초기화 - 동적 API 개수
        api_count = len(self.videoMessages)
        self.step_pass_counts = [0] * api_count
        self.step_error_counts = [0] * api_count
        self.step_pass_flags = [0] * api_count
        
        # 점수 디스플레이 초기화
        self.update_score_display()

        # CONSTANTS.py에서 URL 가져오기
        self.pathUrl = CONSTANTS.url
        self.valResult.append("Start Validation...\n")
        self.valResult.append("시스템이 플랫폼에 요청을 전송하여 응답을 검증합니다")
        self.webhook_cnt = 99
        # 타이머를 1초 간격으로 시작 (CONSTANTS timeout과 조화)
        self.tick_timer.start(1000)

    def stop_btn_clicked(self):
        self.tick_timer.stop()
        self.valResult.append("검증 절차가 중지되었습니다.")
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)

    def init_win(self):
        self.cnt = 0
        self.current_retry = 0  # 재시도 카운터 초기화
        
        # 버퍼 초기화 - 동적 API 개수
        api_count = len(self.videoMessages)
        self.step_buffers = [{"data": "", "result": "", "error": ""} for _ in range(api_count)]
        
        # 누적 카운트 초기화 - 동적 API 개수
        self.step_pass_counts = [0] * api_count
        self.step_error_counts = [0] * api_count
        self.step_pass_flags = [0] * api_count
        
        self.valResult.clear()
        self.step1_msg = ""
        self.step2_msg = ""
        self.step3_msg = ""
        self.step4_msg = ""
        self.step5_msg = ""
        self.step6_msg = ""
        self.step7_msg = ""
        self.step8_msg = ""
        self.step9_msg = ""
        
        # 테이블 아이콘들 초기화
        for i in range(self.tableWidget.rowCount()):
            if i < len(self.step_names) and self.step_names[i]:
                icon_widget = QWidget()
                icon_layout = QHBoxLayout()
                icon_layout.setContentsMargins(0, 0, 0, 0)
                
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
                icon_label.setAlignment(Qt.AlignCenter)
                
                icon_layout.addWidget(icon_label)
                icon_layout.setAlignment(Qt.AlignCenter)
                icon_widget.setLayout(icon_layout)
                
                self.tableWidget.setCellWidget(i, 1, icon_widget)
                
                # 카운트들도 초기화
                self.tableWidget.setItem(i, 2, QTableWidgetItem("0"))
                self.tableWidget.item(i, 2).setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
                self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(i, 4, QTableWidgetItem("0%"))
                self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)

    def show_result_page(self):
        """시험 결과 페이지 표시"""
        dialog = ResultPageDialog(self)
        dialog.exec_()

    def exit_btn_clicked(self):
        """프로그램 종료"""
        # 타이머 정지
        if hasattr(self, 'tick_timer'):
            self.tick_timer.stop()
        
        # print문 추가 -> 나중에 기능 수정해야함 (09/30)
        total_pass = getattr(self, 'total_pass_cnt', 0)
        total_error = getattr(self, 'total_error_cnt', 0)
        grand_total = total_pass + total_error
        overall_score = (total_pass / grand_total * 100) if grand_total > 0 else 0

        # 스텝별 결과 수집
        rows = self.tableWidget.rowCount()
        step_lines = []
        for i in range(rows):
            name = self.tableWidget.item(i, 0).text() if self.tableWidget.item(i, 0) else "N/A"
            get_txt = lambda col: self.tableWidget.item(i, col).text() if self.tableWidget.item(i, col) else "N/A"
            retries = get_txt(2)
            pass_cnt = get_txt(3)
            total_cnt = get_txt(4)
            fail_cnt = get_txt(5)
            score = get_txt(6)
            # step_buffer에 최종 판정 가져오기
            final_res = self.step_buffers[i]["result"] if i < len(self.step_buffers) else "N/A"
            step_lines.append(f"{name} | 결과: {final_res} | 검증 횟수: {retries} | 통과 필드 수: {pass_cnt} | 전체 필드 수: {total_cnt} | 실패 횟수: {fail_cnt} | 평가 점수: {score}") 

            # 로그 원문
            raw_log = self.valResult.toPlainText() if hasattr(self, 'valResult') else ""

            # 최종 페이로드 구성
            header = "=== 시험 결과 ==="
            overall = f"통과 필드 수: {total_pass}\n전체 필드 수: {grand_total}\n종합 평가 점수: {overall_score:.1f}%"
            steps_text = "=== 스텝별 결과 ===\n" + "\n".join(step_lines) if step_lines else "스텝별 결과 없음"
            logs_text = "=== 전체 로그 ===\n" + raw_log if raw_log else "로그 없음"
            final_text = f"{header}\n{overall}\n\n{steps_text}\n\n{logs_text}\n"

            # print(final_text)  # 나중에 대체

            import os
            result_dir = os.path.join(os.getcwd(), "results")
            os.makedirs(result_dir, exist_ok=True)
            results_path = os.path.join(result_dir, "response_results.txt") # 파일 저장명 수정

            with open(results_path, "w", encoding="utf-8") as f:
                f.write(final_text)
            
            print(f"시험 결과가 '{results_path}'에 저장되었습니다.")

        # 확인 대화상자
        reply = QMessageBox.question(self, '프로그램 종료', 
                                   '정말로 프로그램을 종료하시겠습니까?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            QApplication.quit()

    def get_setting(self):
        self.setting_variables = QSettings('My App', 'Variable')
        self.system = "video"  # 영상보안 시스템으로 고정
        
        # 기본 시스템 설정 (영상보안 시스템으로 고정)
        self.radio_check_flag = "video"
        self.message = self.videoMessages
        self.inMessage = self.videoInMessage
        self.outMessage = self.videoOutMessage
        self.inSchema = self.videoInSchema
        self.outSchema = self.videoOutSchema
        # Adapted for new single-element list structure
        self.webhookSchema = self.videoWebhookInSchema if isinstance(self.videoWebhookInSchema, list) and len(self.videoWebhookInSchema) > 0 else [{}]
        self.final_report = f"{self.spec_description} 검증 결과\n"
        
        # 기본 인증 설정 (CONSTANTS.py에서 가져옴)
        self.r2 = CONSTANTS.auth_type
        if self.r2 == "Digest Auth":
            self.r2 = "D"
        elif self.r2 == "Bearer Token":
            self.r2 = "B"
        else:
            self.r2 = "None"

    def closeEvent(self, event):
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))
    ex = MyApp(embedded=False)
    sys.exit(app.exec())