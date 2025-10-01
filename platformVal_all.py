# 물리보안 통합플랫폼 검증 소프트웨어
# physical security integrated platform validation software

import os
from api.api_server import Server
import time
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor
from PyQt5.QtCore import Qt, QSettings, QTimer, QThread
import sys
import ssl

from core.functions import json_check_, save_result, resource_path, field_finder, json_to_data, set_auth, timeout_field_finder

import spec
# from spec.video.videoData_response import videoInMessage, videoMessages
# from spec.video.videoData_request import videoOutMessage
# from spec.video.videoSchema_request import videoInSchema
# from spec.video.videoSchema_response import videoOutSchema
#from spec.video.videoData_response import spec_002_inData, spec_002_messages, spec_0022_inData, spec_0022_messages
from spec.video.videoData_response import spec_002_inData, spec_002_messages
#from spec.video.videoData_request import spec_001_outData, spec_001_messages, spec_0011_outData, spec_0011_messages
#from spec.video.videoSchema_request import spec_001_inSchema, spec_0011_inSchema
from spec.video.videoData_request import spec_001_outData, spec_001_messages
from spec.video.videoSchema_request import spec_001_inSchema
#from spec.video.videoSchema_response import spec_002_outSchema, spec_0022_outSchema
from spec.video.videoSchema_response import spec_002_outSchema
# from spec.video.videoSchema import videoWebhookSchema

import config.CONSTANTS as CONSTANTS

from core.functions import json_check_, save_result, resource_path, field_finder, json_to_data, set_auth, timeout_field_finder 
from core.json_checker_new import check_message_data, check_message_schema, check_message_error 

from http.server import HTTPServer
import json
import traceback
import warnings
import importlib
warnings.filterwarnings('ignore')


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
        
        # 3열 테이블
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
        error_text = step_buffer["error"] if step_buffer["error"] else ("오류가 없습니다." if result=="PASS" else "")
        error_msg = f"검증 결과: {result}\n\n"
        if result == "FAIL":
            error_msg += "오류 세부사항:\n" + error_text
        else:
            error_msg += "오류가 없습니다."
        self.error_browser.setPlainText(error_msg)
        error_layout.addWidget(self.error_browser)
        error_group.setLayout(error_layout)
        
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


# 팝업창 설정하는 함수
class CustomDialog(QDialog):
    def __init__(self, dmsg, dstep):
        super().__init__()

        self.setWindowTitle(dstep)
        self.setGeometry(800, 600, 400, 600)
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
        self.setWindowTitle('통합플랫폼 연동 시험 결과')
        self.setGeometry(100, 100, 1100, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        
        self.initUI()
    
    def initUI(self):
        mainLayout = QVBoxLayout()
        
        # 상단 큰 제목
        title_label = QLabel('통합플랫폼 연동 시험 결과', self)
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
        
        # 결과 테이블 (parent의 테이블 데이터 복사)
        self.tableWidget = QTableWidget(9, 8)
        self.tableWidget.setHorizontalHeaderLabels([
            "API 명", "결과", "검증 횟수", "통과 필드 수", 
            "전체 필드 수", "실패 횟수", "평가 점수", "상세 내용"
        ])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))
        
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
        self.tableWidget.setColumnWidth(7, 150)
        
        # 행 높이 설정
        for i in range(9):
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
                background-color: #87CEEB;
                border: 2px solid #4682B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #191970;
            }
            QPushButton:hover {
                background-color: #B0E0E6;
                border: 2px solid #1E90FF;
            }
            QPushButton:pressed {
                background-color: #4682B4;
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
        for row in range(9):
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
                    background-color: #87CEEB;
                    border: 1px solid #4682B4;
                    border-radius: 3px;
                    padding: 5px;
                    font-weight: bold;
                    color: #191970;
                }
                QPushButton:hover {
                    background-color: #B0E0E6;
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

    def __init__(self, embedded=False):
        importlib.reload(CONSTANTS)  # CONSTANTS 모듈을 다시 로드하여 최신 설정 반영
        super().__init__()
        self.embedded = embedded
        self.radio_check_flag = "video"  # 영상보안 시스템으로 고정
        # 아이콘 경로 먼저 초기화 (initUI에서 사용됨)
        self.img_pass = resource_path("assets/image/green.png")
        self.img_fail = resource_path("assets/image/red.png")
        self.img_none = resource_path("assets/image/black.png")

        self.flag_opt = True  # 필수필드만 확인 False, optional 필드까지 확인 True
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_view)
        self.auth_flag = True 
        self.Server = Server

        auth_temp, auth_temp2 = set_auth("config/config.txt")
        self.digestInfo = [auth_temp2[0], auth_temp2[1]]
        self.token = auth_temp

        self.initUI()
        self.realtime_flag = False
        self.cnt = 0
        self.current_retry = 0  # 현재 API의 반복 횟수 카운터
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.time_pre = 0
        self.cnt_pre = 0
        self.final_report = ""
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS"} for _ in range(9)
        ]

        self.get_setting()
        # 첫 실행 여부 플래그
        self.first_run = True

        with open(resource_path("spec/rows.json"), "w") as out_file:
            json.dump(None, out_file, ensure_ascii=False)


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

    def _update_server_bearer_token(self, token):
        """서버 스레드가 참조하는 Bearer 토큰을 일관된 형태로 저장"""
        server_auth = getattr(self.Server, "auth_Info", [])
        if not isinstance(server_auth, list):
            server_auth = [server_auth]
        if len(server_auth) == 0:
            server_auth.append(None)

        server_auth[0] = None if token is None else str(token).strip()
        self.Server.auth_Info = server_auth
        # 디버그 로그 추가: 토큰 저장 시
        print(f"[DEBUG][PLATFORM] _update_server_bearer_token: stored_token={self.Server.auth_Info[0]}")

    def update_table_row_with_retries(self, row, result, pass_count, error_count, data, error_text, retries):
        if row>= self.tableWidget.rowCount():
            return
        
            # 아이콘 업데이트
        msg, img = self.icon_update_step(data, result, error_text)
        
        # 아이콘을 완전히 중앙에 정렬하기 위해 위젯 사용
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
        
        # 실제 검증 횟수 업데이트
        self.tableWidget.setItem(row, 2, QTableWidgetItem(str(retries)))
        self.tableWidget.item(row, 2).setTextAlignment(Qt.AlignCenter)
        
        # 통과 필드 수 업데이트
        self.tableWidget.setItem(row, 3, QTableWidgetItem(str(pass_count)))
        self.tableWidget.item(row, 3).setTextAlignment(Qt.AlignCenter)
        
        # 전체 필드 수 업데이트
        total_fields = pass_count + error_count
        self.tableWidget.setItem(row, 4, QTableWidgetItem(str(total_fields)))
        self.tableWidget.item(row, 4).setTextAlignment(Qt.AlignCenter)
        
        # 실패 횟수 업데이트
        self.tableWidget.setItem(row, 5, QTableWidgetItem(str(error_count)))
        self.tableWidget.item(row, 5).setTextAlignment(Qt.AlignCenter)
        
        # 평가 점수 업데이트
        if total_fields > 0:
            score = (pass_count / total_fields) * 100
            self.tableWidget.setItem(row, 6, QTableWidgetItem(f"{score:.1f}%"))
        else:
            self.tableWidget.setItem(row, 6, QTableWidgetItem("0%"))
        self.tableWidget.item(row, 6).setTextAlignment(Qt.AlignCenter)
        
        # 메시지 저장 (팝업용)
        setattr(self, f"step{row+1}_msg", msg)

    # 실시간 모니터링용 + 메인 검증 로직 (부하테스트 타이밍) - 09/25
    def update_view(self):
        try:
            time_interval = 0
            if self.time_pre == 0 or self.cnt != self.cnt_pre:
                self.time_pre = time.time()
                self.cnt_pre = self.cnt
            else:
                time_interval = time.time() - self.time_pre

            if self.cnt == 1 and self.r2 == "B":
                data = self.Server.outMessage[0]
                try:
                    self.auth_Info = str(data['accessToken']).strip()
                    self._update_server_bearer_token(self.auth_Info)
                except (KeyError, TypeError):
                    pass

            # 주요 요청 처리 시 Bearer 토큰 상태 디버그 로그
            if self.r2 == "B":
                token = None
                if hasattr(self, 'auth_Info'):
                    token = self.auth_Info
                stored_token = None
                if hasattr(self.Server, 'auth_Info'):
                    stored_token = self.Server.auth_Info[0] if isinstance(self.Server.auth_Info, list) and self.Server.auth_Info else self.Server.auth_Info
                print(f"[DEBUG][PLATFORM] update_view: token={token}, stored_token={stored_token}")

            if self.realtime_flag is True:
                time.sleep(1)
                time_interval += 1

            current_timeout = CONSTANTS.time_out[self.cnt] / 1000

            if time_interval < current_timeout:
                try:
                    with open(resource_path("spec/" + self.Server.system + "/" + self.Server.message[self.cnt] +
                                            ".json"), "r", encoding="UTF-8") as out_file:
                        data = json.load(out_file)

                except json.JSONDecodeError as verr:
                    #print(traceback.format_exc())
                    box = QMessageBox()
                    box.setIcon(QMessageBox.Critical)
                    # box.setText("Error Message: " + path_ + " 을 확인하세요")
                    box.setInformativeText(str(verr))
                    box.setWindowTitle("Error")
                    box.exec_()
                    return ""
                
                except Exception as err:
                    box = QMessageBox()
                    box.setIcon(QMessageBox.Critical)
                    box.setInformativeText(str(err))
                    box.setWindowTitle("Error")
                    box.exec_()
                    return ""

                if data != None:
                    message_name = "step " + str(self.cnt + 1) + ": " + self.Server.message[self.cnt]
                    
                    # 개별 검증 횟수 처리
                    current_retries = CONSTANTS.num_retries[self.cnt] if self.cnt < len(CONSTANTS.num_retries) else 1
                    current_protocol = CONSTANTS.trans_protocol[self.cnt] if self.cnt < len(CONSTANTS.trans_protocol) else "Unknown"

                    total_pass_count = 0
                    total_error_count = 0
                    all_validation_results = []
                    all_error_messages = []
                    combined_data_parts = []


                    for retry_attempt in range(current_retries):
                        combined_error_parts = []
                        step_result = "PASS"
                        add_pass = 0
                        add_err = 0

                        # 실시간 진행률 표시 (시스템쪽처럼)
                        if retry_attempt == 0:
                            self.valResult.append(message_name)
                            self.valResult.append(f"🔄 부하테스트 시작: 총 {current_retries}회 검증 예정")

                        # 순서 확인용 로그
                        print(f"[PLATFORM] 시스템 요청 대기 중: {self.Server.message[self.cnt]} (시도 {retry_attempt + 1})")

                        self.valResult.append(f"⏳ 시스템 요청 대기 중... [{retry_attempt + 1}/{current_retries}]")

                        # 테이블에 실시간 진행률 표시
                        self.update_table_row_with_retries(self.cnt, "진행중", 0, 0, "검증 진행중...", f"시도 {retry_attempt + 1}/{current_retries}", retry_attempt + 1)

                        QApplication.processEvents()
                        # 마지막 반복이 아닐 때만 대기
                        if retry_attempt < current_retries - 1:
                            time.sleep(2.0)  # 시험 진행 속도 간격임 -> 숫자 클수록 느리게 검증 횟수 카운트

                        # 매 시도마다 새로운 데이터 읽기 (실제 부하테스트)
                        try:
                            with open(resource_path("spec/" + self.Server.system + "/" + self.Server.message[self.cnt] +
                                                    ".json"), "r", encoding="UTF-8") as out_file:
                                current_data = json.load(out_file)
                        except:
                            current_data = data  # 파일 읽기 실패 시 기존 데이터 사용

                        if self.Server.message[self.cnt] in CONSTANTS.none_request_message:
                            # 매 시도마다 데이터 수집
                            tmp_res_auth = json.dumps(current_data, indent=4, ensure_ascii=False)
                            if retry_attempt == 0:
                                combined_data_parts.append(f"[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")
                            else:
                                combined_data_parts.append(f"\n[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")

                            if (len(current_data) != 0) and current_data != "{}":
                                step_result = "FAIL"
                                add_err = 1
                                combined_error_parts.append(f"[검증 {retry_attempt + 1}회차] [None Request] 데이터가 있으면 안 됩니다.")
                            elif (len(current_data) == 0) or current_data == "{}":
                                step_result = "PASS"
                                add_pass = 1

                        else:
                            # 매 시도마다 입력 데이터 수집
                            tmp_res_auth = json.dumps(current_data, indent=4, ensure_ascii=False)
                            if retry_attempt == 0:
                                combined_data_parts.append(f"[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")
                            else:
                                combined_data_parts.append(f"\n[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")
                        
                            # 매 시도마다 실제 검증 수행
                            val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.Server.inSchema[self.cnt],
                                                                                    current_data, self.flag_opt)
                            add_pass += key_psss_cnt
                            add_err += key_error_cnt
                        
                            inbound_err_txt = self._to_detail_text(val_text)
                            if val_result == "FAIL":
                                step_result = "FAIL"
                                combined_error_parts.append(f"[검증 {retry_attempt + 1}회차] [Inbound] " + inbound_err_txt)
                            
                            # 개별 프로토콜 설정에 따른 처리
                            if current_protocol == "LongPolling" and "Realtime" in str(self.Server.message[self.cnt]):
                                if "Webhook".lower() in str(current_data).lower():
                                    try:
                                        # 방어적으로 Webhook URL이 잘못된 경우 기본값을 넣어줌
                                        webhook_json_path = resource_path(
                                            "spec/" + self.Server.system + "/" + "webhook_" + self.Server.message[self.cnt] + ".json")
                                        with open(webhook_json_path, "r", encoding="UTF-8") as out_file2:
                                            self.realtime_flag = True
                                            webhook_data = json.load(out_file2)
                                            webhook_url = None
                                            # transProtocolDesc가 있으면 검사
                                            if isinstance(webhook_data, dict):
                                                for k in webhook_data:
                                                    if k.lower() in ["transprotocoldesc", "url", "webhookurl"]:
                                                        webhook_url = webhook_data[k]
                                                        break
                                            # 잘못된 값이면 기본값으로 대체
                                            if webhook_url in [None, '', 'desc', 'none', 'None'] or (isinstance(webhook_url, str) and not webhook_url.lower().startswith(('http://', 'https://'))):
                                                webhook_url = CONSTANTS.url
                                                for k in webhook_data:
                                                    if k.lower() in ["transprotocoldesc", "url", "webhookurl"]:
                                                        webhook_data[k] = webhook_url
                                            # 만약 그래도 url이 없으면 아예 Webhook 검증을 skip
                                            if webhook_url in [None, '', 'desc', 'none', 'None']:
                                                pass  # Webhook 검증 스킵
                                            else:
                                            # Webhook 데이터 수집 (매 시도마다)
                                                tmp_webhook_data = json.dumps(webhook_data, indent=4, ensure_ascii=False)
                                                combined_data_parts.append(f"\n--- Webhook (시도 {retry_attempt + 1}회차) ---\n{tmp_webhook_data}")
                                                
                                                # 매번 Webhook 검증 수행
                                                webhook_val_result, webhook_val_text, webhook_key_psss_cnt, webhook_key_error_cnt = json_check_(
                                                    self.Server.outSchema[-1], webhook_data, self.flag_opt
                                                )
                                            
                                                add_pass += webhook_key_psss_cnt
                                                add_err += webhook_key_error_cnt
                                            
                                                webhook_err_txt = self._to_detail_text(webhook_val_text)
                                                if webhook_val_result == "FAIL":
                                                    step_result = "FAIL"
                                                    combined_error_parts.append(f"[검증 {retry_attempt + 1}회차] [Webhook] " + webhook_err_txt)
                                
                                    except json.JSONDecodeError as verr:
                                        box = QMessageBox()
                                        box.setIcon(QMessageBox.Critical)
                                        box.setInformativeText(str(verr))
                                        box.setWindowTitle("Error")
                                        box.exec_()
                                        return ""
                        
                        # 각 검증 회차별 결과 저장
                        all_validation_results.append(step_result)
                        all_error_messages.extend(combined_error_parts)
                        total_pass_count += add_pass
                        total_error_count += add_err

                    # 최종 결과
                    final_result = "FAIL" if "FAIL" in all_validation_results else "PASS"

                    # 스텝 버퍼 저장
                    data_text = "\n".join(combined_data_parts) if combined_data_parts else "아직 수신된 데이터가 없습니다."
                    error_text = "\n".join(all_error_messages) if all_error_messages else "오류가 없습니다."
                    self.step_buffers[self.cnt]["data"] = data_text
                    self.step_buffers[self.cnt]["error"] = error_text
                    self.step_buffers[self.cnt]["result"] = final_result

                    # 아이콘/툴팁 갱신
                    if combined_data_parts:
                        tmp_res_auth = combined_data_parts[0]
                    else:
                        tmp_res_auth = "No data"
                    
                    # 테이블 업데이트 
                    self.update_table_row_with_retries(self.cnt, final_result, total_pass_count, total_error_count, tmp_res_auth, error_text, current_retries)

                    # 모니터링 창에 최종 결과 표시
                    self.valResult.append(f"\n✅ 부하테스트 완료: {current_retries}회 검증 완료")
                    self.valResult.append(f"프로토콜: {current_protocol}")
                    self.valResult.append("\n" + data_text)
                    self.valResult.append(final_result)

                    # 누적 점수 업데이트
                    self.total_error_cnt += total_error_count
                    self.total_pass_cnt += total_pass_count

                    self.update_score_display()
                    self.valResult.append(
                        "Score : " + str((self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                    self.valResult.append(
                        "Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(self.total_error_cnt) + "(누적 오류 필드 수)\n")
                    
                    self.cnt += 1
                self.realtime_flag = False

            elif time_interval > current_timeout and self.cnt == self.cnt_pre:
                message_name = "step " + str(self.cnt + 1) + ": " + self.Server.message[self.cnt]
                
                # message missing인 경우 버퍼 업데이트
                self.step_buffers[self.cnt]["data"] = "아직 수신된 데이터가 없습니다."
                self.step_buffers[self.cnt]["error"] = "Message Missing!"
                self.step_buffers[self.cnt]["result"] = "FAIL"

                self.valResult.append(message_name)
                self.valResult.append(f"Timeout: {current_timeout}초")
                self.valResult.append("Message Missing!")
                tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(self.Server.inSchema[self.cnt])

                self.total_error_cnt += tmp_fields_rqd_cnt
                if tmp_fields_rqd_cnt == 0:
                    self.total_error_cnt += 1
                if self.flag_opt:
                    self.total_error_cnt += tmp_fields_opt_cnt

                self.total_pass_cnt += 0
                
                # 평가 점수 디스플레이 업데이트
                self.update_score_display()
                
                self.valResult.append(
                    "Score : " + str((self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                    self.total_error_cnt) + "(누적 오류 필드 수)\n")
                
                # 테이블 업데이트 (Message Missing)
                add_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                if self.flag_opt:
                    add_err += tmp_fields_opt_cnt
                
                current_retries = CONSTANTS.num_retries[self.cnt] if self.cnt < len(CONSTANTS.num_retries) else 1
                self.update_table_row_with_retries(self.cnt, "FAIL", 0, add_err, "", "Message Missing!", current_retries)
                
                self.cnt += 1

            if self.cnt == len(self.Server.message):
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

        except Exception as err:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error Message: 오류 확인 후 검증 절차를 다시 시작해주세요")
            msg.setInformativeText(str(err))
            msg.setWindowTitle("Error")
            msg.exec_()
            self.tick_timer.stop()
            self.valResult.append("검증 절차가 중지되었습니다.")
            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)

    def update_score_display(self):
        """평가 점수 디스플레이를 업데이트"""
        # 평가 점수 UI가 주석처리된 경우 오류 방지
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

    def icon_update_step(self, auth_, result_, text_):
        if result_ == "PASS":
            msg = auth_ + "\n\n" + "Result: " + text_ +"\n"
            img = self.img_pass
        elif result_ == "진행중":
            msg = auth_ + "\n\n" + "Status: " + text_ +"\n"
            img = self.img_none  # 진행중일 때는 검은색 아이콘
        else:
            msg = auth_ + "\n\n" + "Result: " + result_ + "\nResult details:\n" + text_ +"\n"
            img = self.img_fail
        return msg, img

    def icon_update(self, tmp_res_auth, val_result, val_text):
        msg, img = self.icon_update_step(tmp_res_auth, val_result, val_text)
        
        # 아이콘을 완전히 중앙에 정렬하기 위해 위젯 사용
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
        
        if self.cnt < self.tableWidget.rowCount():
            self.tableWidget.setCellWidget(self.cnt, 1, icon_widget)
            # 메시지 저장 (팝업용)
            setattr(self, f"step{self.cnt+1}_msg", msg)
    
    def load_test_info_from_constants(self):
        """CONSTANTS.py에서 시험정보를 로드 (읽기 전용)"""
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


    def initUI(self):
        # 1열(세로) 레이아웃으로 통합
        mainLayout = QVBoxLayout()

        # 상단 큰 제목
        self.title_label = QLabel('통합플랫폼 연동 검증', self)
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
                background-color: #87CEEB;
                border: 2px solid #4682B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #191970;
            }
            QPushButton:hover {
                background-color: #B0E0E6;
                border: 2px solid #1E90FF;
            }
            QPushButton:pressed {
                background-color: #4682B4;
            }
            QPushButton:disabled {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                color: #999999;
            }
        """)
        self.sbtn.clicked.connect(self.sbtn_push)

        self.stop_btn = QPushButton(self)
        self.stop_btn.setText('일시 정지')
        self.stop_btn.setFixedSize(140, 50)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #87CEEB;
                border: 2px solid #4682B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #191970;
            }
            QPushButton:hover {
                background-color: #B0E0E6;
                border: 2px solid #1E90FF;
            }
            QPushButton:pressed {
                background-color: #4682B4;
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
                background-color: #87CEEB;
                border: 2px solid #4682B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #191970;
            }
            QPushButton:hover {
                background-color: #B0E0E6;
                border: 2px solid #1E90FF;
            }
            QPushButton:pressed {
                background-color: #4682B4;
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
                background-color: #87CEEB;
                border: 2px solid #4682B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #191970;
            }
            QPushButton:hover {
                background-color: #B0E0E6;
                border: 2px solid #1E90FF;
            }
            QPushButton:pressed {
                background-color: #4682B4;
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
        self.setWindowTitle('물리보안 통합플랫폼 연동 검증 소프트웨어')
        # 창 크기
        self.setGeometry(100, 100, 1100, 700)

        if not self.embedded:
            self.show()

    def init_centerLayout(self):
        self.tableWidget = QTableWidget(9, 8)
        self.tableWidget.setHorizontalHeaderLabels(["API 명", "결과", "검증 횟수", "통과 필드 수", "전체 필드 수", "실패 횟수", "평가 점수", "상세 내용"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))
        
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
        self.tableWidget.setColumnWidth(7, 150) 


        # 행 높이 설정
        for i in range(9):
            self.tableWidget.setRowHeight(i, 40)

        # 단계명 리스트 (기본값)
        self.step_names = [
            "Authentication", "Capabilities", "CameraProfiles", "StoredVideoInfos",
            "StreamURLs", "ReplayURL", "RealtimeVideoEventInfos",
            "StoredVideoEventInfos", "StoredObjectAnalyticsInfos"
        ]
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
            
            # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_btn)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)
            
            self.tableWidget.setCellWidget(i, 7, container)

        # 결과 컬럼만 클릭 가능하도록 설정
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)
        
        # centerLayout을 초기화하고 테이블 추가
        self.centerLayout = QVBoxLayout()
        self.centerLayout.addWidget(self.tableWidget)


    def show_combined_result(self, row):
        """통합 상세 내용 확인 - 데이터, 규격, 오류를 모두 보여주는 3열 팝업"""
        try:
            buf = self.step_buffers[row]
            api_name = self.tableWidget.item(row, 0).text()
            
            # 스키마 데이터 가져오기 -> 09/24 플랫폼쪽은 InSchema
            try:
                schema_data = videoInSchema[row] if row < len(videoInSchema) else None
            except:
                schema_data = None
            
            # 통합 팝업창 띄우기
            dialog = CombinedDetailDialog(api_name, buf, schema_data)
            dialog.exec_()
            
        except Exception as e:
            CustomDialog(f"오류:\n{str(e)}", "상세 내용 확인 오류")


    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭 시 호출되는 함수 (결과 아이콘 클릭용으로 유지)"""
        if col == 1:
            msg = getattr(self, f"step{row+1}_msg", "")
            if msg:
                CustomDialog(msg, self.tableWidget.item(row, 0).text())

    # def group_score(self):
    #     """평가 점수 박스"""
    #     sgroup = QGroupBox('평가 점수')
    #     sgroup.setMaximumWidth(1050)
    #     sgroup.setMinimumWidth(950)
        
    #     # 점수 표시용 레이블들
    #     self.pass_count_label = QLabel("통과 필드 수: 0")
    #     self.total_count_label = QLabel("전체 필드 수: 0")  
    #     self.score_label = QLabel("종합 평가 점수: 0%")
        
    #     # 폰트 크기 조정
    #     font = self.pass_count_label.font()
    #     font.setPointSize(20)
    #     self.pass_count_label.setFont(font)
    #     self.total_count_label.setFont(font)
    #     self.score_label.setFont(font)
        
    #     # 가로 배치
    #     layout = QHBoxLayout()
    #     layout.setSpacing(90)
    #     layout.addWidget(self.pass_count_label)
    #     layout.addWidget(self.total_count_label)
    #     layout.addWidget(self.score_label)
    #     layout.addStretch()
        
    #     sgroup.setLayout(layout)
    #     return sgroup

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 창 크기 변경 시 테이블 크기 조정
        if hasattr(self, 'tableWidget'):
            window_width = self.width()
            window_height = self.height()
            
            # 테이블 크기를 창 크기에 맞게 조정
            table_width = min(max(500, window_width // 3), 700)
            table_height = min(max(300, window_height // 2), 500)
            
            self.tableWidget.resize(table_width, table_height)


    def sbtn_push(self):
        self.first_run = False
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.cnt = 0
        self.cnt_pre = 0
        self.time_pre = 0
        self.realtime_flag = False
        self.tmp_msg_append_flag = False
        # 평가 점수 디스플레이 초기화
        self.update_score_display()
        self.sbtn.setDisabled(True)
        self.stop_btn.setEnabled(True)
        # self.Server = api_server.Server# -> MyApp init()으로
        json_to_data(self.radio_check_flag)
        timeout = 5 
        default_timeout = 5
        if self.r2 == "B":
            token_value = None if self.token is None else str(self.token).strip()
            videoOutMessage[0]['accessToken'] = token_value
        self.Server.message = videoMessages
        self.Server.inMessage = videoInMessage
        self.Server.outMessage = videoOutMessage
        self.Server.inSchema = videoInSchema
        self.Server.outSchema = videoOutSchema
        self.Server.system = "video"
        self.Server.timeout = timeout
        self.init_win()
        self.valResult.clear()  # 초기화
        self.final_report = ""  # 초기화
        # 테이블 아이콘 초기화
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
            self.tableWidget.setCellWidget(i, 1, icon_widget)
        # CONSTANTS.py에서 URL 가져오기
        self.pathUrl = CONSTANTS.url
        if self.r2 == "B":
            self.Server.auth_type = "B"
            self._update_server_bearer_token(self.token)
        elif self.r2 == "D":
            self.Server.auth_type = "D"
            self.Server.auth_Info[0] = self.digestInfo[0]
            self.Server.auth_Info[1] = self.digestInfo[1]
        elif self.r2 == "None":
            self.Server.auth_type = "None"
            self.Server.auth_Info[0] = None
        # 기본값으로 LongPolling 사용
        self.Server.transProtocolInput = "LongPolling"
        self.valResult.append("Start Validation...\n")
        # CONSTANTS.py의 URL 사용
        url = CONSTANTS.url.split(":")
        address_ip = url[-2].split("/")[-1]
        address_port = int(url[-1])
        self.server_th = server_th(handler_class=self.Server, address=address_ip, port=address_port)
        self.server_th.start()
        # 서버 준비 완료까지 대기 (첫 실행 시)
        if self.first_run:
            self.valResult.append("🔄 플랫폼 서버 초기화 중...")
            time.sleep(5)
            self.valResult.append("✅ 플랫폼 서버 준비 완료")
        self.tick_timer.start(1000)  # 시스템쪽과 동일한 1초 간격

    def stop_btn_clicked(self):
        self.tick_timer.stop()
        self.valResult.append("검증 절차가 중지되었습니다.")
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)

    def init_win(self):
        self.cnt = 0
        # 버퍼 초기화
        self.step_buffers = [{"data": "", "result": "", "error": ""} for _ in range(9)]
        # 첫 실행이 아닌 경우에만 JSON 파일 초기화
        if not self.first_run:
            for i in range(0, len(self.Server.message)):
                with open(resource_path("spec/"+self.Server.system + "/" + self.Server.message[i] + ".json"), "w",
                          encoding="UTF-8") as out_file:
                    json.dump(None, out_file, ensure_ascii=False)
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
        if hasattr(self, 'timer'):
            self.timer.stop()
        
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
            results_path = os.path.join(result_dir, "request_results.txt")  # 파일 저장명

            with open(results_path, "w", encoding="utf-8") as f:
                f.write(final_text)
            
            print(f"시험 결과가 '{results_path}'에 저장되었습니다.")

        # 확인 대화상자
        reply = QMessageBox.question(self, '프로그램 종료', 
                                   '정말로 프로그램을 종료하시겠습니까?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            result_payload = self.build_result_payload()

            QApplication.quit()
    def get_setting(self):
        self.setting_variables = QSettings('My App', 'Variable')
        self.Server.system = "video"  # 영상보안 시스템으로 고정
        
        self.r2 = CONSTANTS.auth_type
        if self.r2 == "Digest Auth":
            self.r2 = "D"
        elif self.r2 == "Bearer Token":
            self.r2 = "B"
        else:
            self.r2 = "None"

    def closeEvent(self, event):
        event.accept()
    
    def build_result_payload(self):
        """최종 결과(점수, 통과/실패 카운트, 세부 결과 등)를 dict로 반환 (system과 동일)"""
        total_fields = self.total_pass_cnt + self.total_error_cnt
        score = (self.total_pass_cnt / total_fields) * 100 if total_fields > 0 else 0
        return {
            "score": score,
            "pass_count": self.total_pass_cnt,
            "error_count": self.total_error_cnt,
            "details": self.final_report if hasattr(self, "final_report") else ""
        }


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
            #print(traceback.format_exc())
            print(e)


        print('Starting on ', self.server_address)

    def run(self):
        self.httpd.serve_forever()

class json_data(QThread):
    json_update_data = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            with open(resource_path("spec/rows.json"), "r", encoding="UTF-8") as out_file:
                data = json.load(out_file)
            if data is not None:
                with open(resource_path("spec/rows.json"), "w", encoding="UTF-8") as out_file:
                    json.dump(None, out_file, ensure_ascii=False)
                self.json_update_data.emit(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))
    ex = MyApp(embedded=False)
    sys.exit(app.exec())