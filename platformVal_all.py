# 물리보안 통합플랫폼 검증 소프트웨어
# physical security integrated platform validation software

import os
from api.api_server import Server
import time
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor
from PyQt5.QtCore import Qt, QSettings, QTimer, QThread, pyqtSignal
import sys
import ssl
from datetime import datetime

from core.functions import json_check_, save_result, resource_path, field_finder, json_to_data, set_auth, timeout_field_finder

import config.CONSTANTS as CONSTANTS

from core.functions import json_check_, save_result, resource_path, field_finder, json_to_data, set_auth, timeout_field_finder 
from core.json_checker_new import check_message_data, check_message_schema, check_message_error 

from http.server import HTTPServer
import json
import traceback
import warnings
import importlib
warnings.filterwarnings('ignore')


# 플랫폼 검증을 위한 래퍼 윈도우 (standalone 모드에서 스택 전환 지원)
class PlatformValidationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("통합플랫폼 연동 검증")
        self.resize(1200, 720)
        
        # 스택 위젯 생성
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # 플랫폼 검증 위젯은 나중에 생성 (순환 참조 방지)
        self.validation_widget = None
        self._result_widget = None
    
    def initialize(self):
        """검증 위젯 초기화 (MyApp 클래스 정의 후 호출)"""
        if self.validation_widget is None:
            self.validation_widget = MyApp(embedded=False)
            self.validation_widget._wrapper_window = self  # 래퍼 참조 전달
            self.stack.addWidget(self.validation_widget)
            self.stack.setCurrentWidget(self.validation_widget)
    
    def _show_result_page(self):
        """시험 결과 페이지로 전환 (스택 내부)"""
        # 기존 결과 위젯 제거
        if self._result_widget is not None:
            self.stack.removeWidget(self._result_widget)
            self._result_widget.deleteLater()
        
        # 새로운 결과 위젯 생성
        self._result_widget = ResultPageWidget(self.validation_widget, embedded=True)
        self._result_widget.backRequested.connect(self._on_back_to_validation)
        
        # 스택에 추가하고 전환
        self.stack.addWidget(self._result_widget)
        self.stack.setCurrentWidget(self._result_widget)
    
    def _on_back_to_validation(self):
        """뒤로가기: 시험 결과에서 검증 화면으로 복귀"""
        self.stack.setCurrentWidget(self.validation_widget)


# 통합된 상세 내용 확인 팝업창 클래스
class CombinedDetailDialog(QDialog):
    def __init__(self, api_name, step_buffer, schema_data, webhook_schema=None):
        super().__init__()
        
        self.setWindowTitle(f"{api_name} - 통합 상세 정보")
        self.setGeometry(400, 300, 1200, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # 전체 레이아웃
        main_layout = QVBoxLayout()
        
        # webhook_schema 저장
        self.webhook_schema = webhook_schema
        
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
        
        # 기본 스키마 + 웹훅 스키마 결합
        schema_text = self._format_schema(schema_data)
        if self.webhook_schema:
            schema_text += "\n\n=== 웹훅 응답 스키마 (시스템→플랫폼) ===\n"
            schema_text += self._format_schema(self.webhook_schema)
        
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


# API 선택 다이얼로그
class APISelectionDialog(QDialog):
    def __init__(self, api_list, selected_indices, parent=None):
        super().__init__(parent)
        self.api_list = api_list
        self.selected_indices = selected_indices.copy()
        
        self.setWindowTitle("API 선택")
        self.setGeometry(400, 300, 500, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 상단 안내
        info_label = QLabel("시험할 API를 선택하세요 (복수 선택 가능)")
        info_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 10px;")
        layout.addWidget(info_label)
        
        # 전체 선택/해제 버튼
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("전체 선택")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("전체 해제")
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # API 리스트 (체크박스)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        self.checkboxes = []
        for idx, api_name in enumerate(self.api_list):
            checkbox = QCheckBox(f"{idx + 1}. {api_name}")
            checkbox.setChecked(idx in self.selected_indices)
            self.checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # 하단 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def select_all(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)
    
    def deselect_all(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
    
    def get_selected_indices(self):
        """선택된 API 인덱스 리스트 반환"""
        return [idx for idx, checkbox in enumerate(self.checkboxes) if checkbox.isChecked()]


# 시험 결과 페이지 위젯
class ResultPageWidget(QWidget):
    # 뒤로가기 시그널 추가
    backRequested = pyqtSignal()
    
    def __init__(self, parent, embedded=False):
        super().__init__()
        self.parent = parent
        self.embedded = embedded  # embedded 모드 여부 저장
        self.setWindowTitle('통합플랫폼 연동 시험 결과')
        self.resize(1100, 600)
        
        self.initUI()
    
    def initUI(self):
        mainLayout = QVBoxLayout()
        
        # 상단 대제목 (수정된 부분)S
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
        
        # 결과 테이블 (parent의 테이블 데이터 복사) - 동적 API 개수
        api_count = self.parent.tableWidget.rowCount()
        self.tableWidget = QTableWidget(api_count, 8)
        self.tableWidget.setHorizontalHeaderLabels([
            "API 명", "결과", "검증 횟수", "통과 필드 수", 
            "전체 필드 수", "실패 필드 수", "평가 점수", "상세 내용"
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
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 40)
        
        # parent 테이블 데이터 복사
        self._copy_table_data()
        
        # 상세 내용 버튼 클릭 이벤트
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)
        
        mainLayout.addWidget(self.tableWidget)
        
        mainLayout.addSpacing(15)
        
        # 시험 분야별 점수 표시
        spec_score_group = self._create_spec_score_display()
        mainLayout.addWidget(spec_score_group)
        
        mainLayout.addSpacing(10)
        
        # 전체 점수 표시
        total_score_group = self._create_total_score_display()
        mainLayout.addWidget(total_score_group)
        
        mainLayout.addSpacing(20)
        
        # 뒤로가기/닫기 버튼
        if self.embedded:
            # Embedded 모드: 뒤로가기 버튼
            back_btn = QPushButton('← 뒤로가기')
            back_btn.setFixedSize(140, 50)
            back_btn.setStyleSheet("""
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
            back_btn.clicked.connect(self._on_back_clicked)
            
            close_layout = QHBoxLayout()
            close_layout.setAlignment(Qt.AlignCenter)
            close_layout.addWidget(back_btn)
            mainLayout.addLayout(close_layout)
        else:
            # Standalone 모드: 닫기 버튼
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
            close_btn.clicked.connect(self.close)
            
            close_layout = QHBoxLayout()
            close_layout.setAlignment(Qt.AlignCenter)
            close_layout.addWidget(close_btn)
            mainLayout.addLayout(close_layout)
        
        mainLayout.addStretch()
        self.setLayout(mainLayout)
    
    def _on_back_clicked(self):
        """뒤로가기 버튼 클릭 시 시그널 발생"""
        self.backRequested.emit()
    
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
            
            # 나머지 컬럼들 (검증 횟수, 통과 필드 수, 전체 필드 수, 실패 필드 수, 평가 점수)
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
    
    def _create_spec_score_display(self):
        """시험 분야별 점수 표시 그룹"""
        spec_group = QGroupBox('시험 분야별 점수')
        spec_group.setMaximumWidth(1050)
        spec_group.setMinimumWidth(950)
        
        # spec 정보 가져오기
        spec_description = self.parent.spec_description
        api_count = len(self.parent.videoMessages)
        
        total_pass = self.parent.total_pass_cnt
        total_error = self.parent.total_error_cnt
        total_fields = total_pass + total_error
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0
        
        # 분야명 레이블 (강조)
        spec_name_label = QLabel(f"📋 {spec_description} ({api_count}개 API)")
        spec_name_font = spec_name_label.font()
        spec_name_font.setPointSize(16)
        spec_name_font.setBold(True)
        spec_name_label.setFont(spec_name_font)
        
        # 점수 레이블들
        pass_label = QLabel(f"통과 필드 수: {total_pass}")
        total_label = QLabel(f"전체 필드 수: {total_fields}")
        score_label = QLabel(f"종합 평가 점수: {score:.1f}%")
        
        # 폰트 크기 조정
        font = pass_label.font()
        font.setPointSize(14)
        pass_label.setFont(font)
        total_label.setFont(font)
        score_label.setFont(font)
        
        # 레이아웃 구성
        main_layout = QVBoxLayout()
        main_layout.addWidget(spec_name_label)
        main_layout.addSpacing(10)
        
        score_layout = QHBoxLayout()
        score_layout.setSpacing(70)
        score_layout.addWidget(pass_label)
        score_layout.addWidget(total_label)
        score_layout.addWidget(score_label)
        score_layout.addStretch()
        
        main_layout.addLayout(score_layout)
        spec_group.setLayout(main_layout)
        return spec_group
    
    def _create_total_score_display(self):
        """전체 점수 표시 그룹 (향후 여러 spec 평균 계산용)"""
        total_group = QGroupBox('전체 점수')
        total_group.setMaximumWidth(1050)
        total_group.setMinimumWidth(950)
        
        # 현재는 1개 spec만 실행하므로 동일한 값
        total_pass = self.parent.total_pass_cnt
        total_error = self.parent.total_error_cnt
        total_fields = total_pass + total_error
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0
        
        pass_label = QLabel(f"통과 필드 수: {total_pass}")
        total_label = QLabel(f"전체 필드 수: {total_fields}")
        score_label = QLabel(f"종합 평가 점수: {score:.1f}%")
        
        # 폰트 크기 조정
        font = pass_label.font()
        font.setPointSize(16)
        font.setBold(True)
        pass_label.setFont(font)
        total_label.setFont(font)
        score_label.setFont(font)
        
        layout = QHBoxLayout()
        layout.setSpacing(70)
        layout.addWidget(pass_label)
        layout.addWidget(total_label)
        layout.addWidget(score_label)
        layout.addStretch()
        
        total_group.setLayout(layout)
        return total_group
    
    def _create_score_display(self):
        """평가 점수 표시 그룹 (구 버전 - 호환성 유지)"""
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
    def _get_latest_request_data(self, api_name, direction="REQUEST"):
        """
        Server.trace에서 해당 api_name, direction의 최신 데이터를 반환한다.
        direction은 'REQUEST' 또는 'RESPONSE'가 될 수 있다.
        """
        try:
            print(f"[DEBUG] _get_latest_request_data 호출: api_name={api_name}, direction={direction}")
            
            if not hasattr(self.Server, "trace") or self.Server.trace is None:
                print(f"[DEBUG] Server.trace가 없음")
                return {}
            
            events = list((getattr(self.Server, "trace", {}) or {}).get(api_name, []))
            print(f"[DEBUG] {api_name}의 이벤트 개수: {len(events)}")
            
            for ev in reversed(events):
                if ev.get("dir") == direction:
                    data = ev.get("data", {})
                    print(f"[DEBUG] {direction} 데이터 발견: {type(data)}")
                    return data
            
            print(f"[DEBUG] {direction} 데이터 없음")
            return {}
        except Exception as e:
            print(f"[DEBUG] _get_latest_request_data 에러: {e}")
            import traceback
            traceback.print_exc()
            return {}
    # 시험 결과 표시 요청 시그널 (main.py와 연동)
    showResultRequested = pyqtSignal(object)  # parent widget을 인자로 전달

    def __init__(self, embedded=False, mode=None, spec_id=None):
        importlib.reload(CONSTANTS)  # CONSTANTS 모듈을 다시 로드하여 최신 설정 반영
        super().__init__()
        self.embedded = embedded
        self.mode = mode  # 모드 저장
        self.radio_check_flag = "video"  # 영상보안 시스템으로 고정
        
        # Standalone 모드일 때 래퍼 윈도우 참조 저장
        self._wrapper_window = None
        
        # 전체화면 관련 변수 초기화
        self._is_fullscreen = False
        self._saved_geom = None
        self._saved_state = None
        
        # 아이콘 경로 먼저 초기화 (initUI에서 사용됨)
        self.img_pass = resource_path("assets/image/green.png")
        self.img_fail = resource_path("assets/image/red.png")
        self.img_none = resource_path("assets/image/black.png")

        self.flag_opt = CONSTANTS.flag_opt  # 필수필드만 확인 False, optional 필드까지 확인 True
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_view)
        self.auth_flag = True 
        self.Server = Server

        auth_temp, auth_temp2 = set_auth("config/config.txt")
        self.digestInfo = [auth_temp2[0], auth_temp2[1]]
        self.token = auth_temp

        # ✅ spec_id 초기화 (info_GUI에서 전달받거나 기본값 사용)
        if spec_id:
            self.current_spec_id = spec_id
            print(f"[PLATFORM] 📌 전달받은 spec_id 사용: {spec_id}")
        else:
            self.current_spec_id = "cmgatbdp000bqihlexmywusvq"  # 기본값: 보안용 센서 시스템 (7개 API)
            print(f"[PLATFORM] 📌 기본 spec_id 사용: {self.current_spec_id}")
        
        # Load specs dynamically from CONSTANTS
        self.load_specs_from_constants()

        self.initUI()
        self.realtime_flag = False
        self.cnt = 0
        self.current_retry = 0  # 현재 API의 반복 횟수 카운터
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.time_pre = 0
        self.cnt_pre = 0
        self.final_report = ""
        
        # step_buffers 동적 생성 (API 개수에 따라)
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS"} for _ in range(len(self.videoMessages))
        ]

        self.get_setting()
        # 첫 실행 여부 플래그
        self.first_run = True

        with open(resource_path("spec/rows.json"), "w") as out_file:
            json.dump(None, out_file, ensure_ascii=False)

    def load_specs_from_constants(self):
        """
        ✅ SPEC_CONFIG 기반으로 spec 데이터 동적 로드
        - current_spec_id에 따라 올바른 모듈(spec.video 또는 spec/)에서 데이터 로드
        - trans_protocol, time_out, num_retries도 SPEC_CONFIG에서 가져옴
        """
        # ✅ SPEC_CONFIG에서 현재 spec 설정 가져오기
        if not hasattr(CONSTANTS, 'SPEC_CONFIG'):
            raise ValueError("CONSTANTS.SPEC_CONFIG가 정의되지 않았습니다!")
        
        config = CONSTANTS.SPEC_CONFIG.get(self.current_spec_id, {})
        if not config:
            raise ValueError(f"spec_id '{self.current_spec_id}'에 대한 설정을 찾을 수 없습니다!")
        
        # ✅ 설정 정보 추출
        self.spec_description = config.get('test_name', 'Unknown Test')
        spec_names = config.get('specs', [])
        
        # ✅ trans_protocol, time_out, num_retries 저장
        self.trans_protocols = config.get('trans_protocol', [])
        self.time_outs = config.get('time_out', [])
        self.num_retries_list = config.get('num_retries', [])
        
        if len(spec_names) < 3:
            raise ValueError(f"spec_id '{self.current_spec_id}'의 specs 설정이 올바르지 않습니다! (최소 3개 필요)")
        
        print(f"[PLATFORM] 📋 Spec 로딩 시작: {self.spec_description} (ID: {self.current_spec_id})")
        
        # ✅ 모든 시스템은 spec/ 폴더 사용
        print(f"[PLATFORM] 📁 모듈: spec (센서/바이오/영상 통합)")
        import spec.Schema_request as schema_request_module
        import spec.Data_response as data_response_module
        import spec.Constraints_response as constraints_response_module
        # ✅ 플랫폼은 요청 검증 + 응답 전송 (inSchema/outData 사용)
        print(f"[PLATFORM] 🔧 타입: 요청 검증 + 응답 전송")
        
        # ✅ Request 검증용 데이터 로드 (플랫폼이 시스템으로부터 받을 요청 검증) - inSchema
        self.videoInSchema = getattr(schema_request_module, spec_names[0], [])
        
        # ✅ Response 전송용 데이터 로드 (플랫폼이 시스템에게 보낼 응답) - outData
        self.videoOutMessage = getattr(data_response_module, spec_names[1], [])
        self.videoOutConstraint = getattr(constraints_response_module, self.current_spec_id+"_OutConstraints", [])
        self.videoMessages = getattr(data_response_module, spec_names[2], [])

        # ✅ Webhook 관련 (영상보안 시스템만 사용)
        self.videoWebhookSchema = []
        self.videoWebhookData = []
        self.videoWebhookInSchema = []
        self.videoWebhookInData = []
        
        # if self.current_spec_id == "cmga0l5mh005dihlet5fcoj0o":
        #     # 영상보안만 Webhook 지원
        #     webhookSchema_name = "spec_001_webhookSchema"  # 고정값
        #     webhookData_name = "spec_001_webhookData"
        #     self.videoWebhookSchema = getattr(video_schema_request, webhookSchema_name, [])
        #     self.videoWebhookData = getattr(video_data_request, webhookData_name, [])
            
        #     webhookInSchema_name = "spec_002_webhookSchema"
        #     webhookInData_name = "spec_002_webhookData"
        #     self.videoWebhookInSchema = getattr(video_schema_response, webhookInSchema_name, [])
        #     self.videoWebhookInData = getattr(video_data_response, webhookInData_name, [])
        
        print(f"[PLATFORM] ✅ 로딩 완료: {len(self.videoMessages)}개 API")
        print(f"[PLATFORM] 📋 API 목록: {self.videoMessages}")
        print(f"[PLATFORM] 🔄 프로토콜 설정: {self.trans_protocols}")


    def _redact(self, payload):
        try:
            if isinstance(payload, dict):
                p = dict(payload)
                for k in ["accessToken", "token", "Authorization", "password", "secret", "apiKey"]:
                    if k in p and isinstance(p[k], (str, bytes)):
                        p[k] = "***"
                return p
            return payload
        except Exception:
            return payload

    def _push_event(self, api_name, direction, payload):
        """direction: 'REQUEST'|'RESPONSE'|'WEBHOOK'"""
        try:
            if not hasattr(self.Server, "trace") or self.Server.trace is None:
                self.Server.trace = {}
            if api_name not in self.Server.trace:
                from collections import deque
                self.Server.trace[api_name] = deque(maxlen=500)
            evt = {
                "time": datetime.utcnow().isoformat()+"Z",
                "api": api_name,
                "dir": direction,
                "data": self._redact(payload),
            }
            self.Server.trace[api_name].append(evt)
        except Exception:
            pass

    def get_latest_from_trace(self, api_name, direction):
        """trace에서 해당 방향의 최신 이벤트 반환"""
        try:
            events = list((getattr(self.Server, "trace", {}) or {}).get(api_name, []))
            for ev in reversed(events):
                if ev.get("dir") == direction:
                    return ev.get("data")
        except Exception:
            pass
        return None

    def get_latest_request(self, step_idx):
        api = self.Server.message[step_idx]
        return self.get_latest_from_trace(api, "REQUEST")

    def get_latest_response(self, step_idx):
        api = self.Server.message[step_idx]
        return self.get_latest_from_trace(api, "RESPONSE")


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
        # print(f"[DEBUG][PLATFORM] _update_server_bearer_token: stored_token={self.Server.auth_Info[0]}")

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
        
        # 실패 필드 수 업데이트
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
            # print(f"[DEBUG] update_view 시작: cnt={self.cnt}, cnt_pre={self.cnt_pre}")
            time_interval = 0
            
            # cnt가 리스트 길이 이상이면 종료 처리
            if self.cnt >= len(self.Server.message):
                print(f"[DEBUG] 모든 API 처리 완료, 타이머 정지")
                self.tick_timer.stop()
                return
            
            # ✅ 시스템과 동일: 첫 틱에서는 대기만 하고 리턴
            if self.time_pre == 0 or self.cnt != self.cnt_pre:
                print(f"[DEBUG] 첫 틱 대기: time_pre={self.time_pre}, cnt={self.cnt}, cnt_pre={self.cnt_pre}")
                self.time_pre = time.time()
                self.cnt_pre = self.cnt
                return  # 첫 틱에서는 대기만 하고 리턴
            else:
                time_interval = time.time() - self.time_pre
                print(f"[DEBUG] 시간 간격: {time_interval}초")

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
                # print(f"[DEBUG][PLATFORM] update_view: token={token}, stored_token={stored_token}")

            # 웹훅 모드 - 웹훅 스레드의 join()이 동기화를 담당하므로 별도 sleep 불필요
            if self.realtime_flag is True:
                print(f"[TIMING_DEBUG] 웹훅 모드 활성화 (API: {self.Server.message[self.cnt] if self.cnt < len(self.Server.message) else 'N/A'})")
                print(f"[TIMING_DEBUG] ✅ 웹훅 스레드의 join()이 동기화 처리 (수동 sleep 제거됨)")

            # SPEC_CONFIG에서 timeout
            current_timeout = (self.time_outs[self.cnt] / 1000) if self.cnt < len(self.time_outs) else 5.0
            
            # timeout이 0인 경우
            if current_timeout == 0 or time_interval < current_timeout:
                # ✅ 시스템 요청 확인 (요청-응답 구조)
                # Server 클래스의 request_counter(클래스 변수)를 확인하여 시스템이 요청을 보냈는지 체크
                api_name = self.Server.message[self.cnt]
                print(f"[DEBUG] API 처리 시작: {api_name}")
                print(f"[DEBUG] cnt={self.cnt}, current_retry={self.current_retry}")
                
                request_received = False
                expected_count = self.current_retry + 1  # 현재 회차에 맞는 요청 수
                actual_count = 0  # 초기값
                
                # Server 클래스 변수 request_counter 확인
                if hasattr(self.Server, 'request_counter') and api_name in self.Server.request_counter:
                    actual_count = self.Server.request_counter[api_name]
                    print(f"[DEBUG] API: {api_name}, 예상: {expected_count}, 실제: {actual_count}")
                    if actual_count >= expected_count:
                        request_received = True
                
                # ✅ 요청이 도착하지 않았으면 대기
                if not request_received:
                    # ✅ [TIMING_DEBUG] 능동적 대기 (올바른 방법)
                    if self.current_retry == 0:  # 첫 시도에만 출력
                        print(f"[TIMING_DEBUG] ✅ 능동 대기(WAIT): 시스템 요청 대기 중 (API: {api_name}, 예상: {expected_count}회, 실제: {actual_count}회)")
                        print(f"[TIMING_DEBUG] ✅ 이것은 올바른 대기입니다! 시스템 요청이 올 때까지 기다립니다.")
                    return  # 다음 틱까지 대기
                
                # ✅ [TIMING_DEBUG] 시스템 요청 도착 확인
                request_arrival_time = time.time()
                expected_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                print(f"[TIMING_DEBUG] ✅ 요청 도착 감지! API: {api_name}, 시도: {self.current_retry + 1}/{expected_retries}")
                print(f"[TIMING_DEBUG] ✅ 시스템 요청 카운트: {actual_count}회, 즉시 검증 시작합니다.")
                
                # (10/20) 수정
                # if self.cnt < len(self.videoInMessage):
                #     data = self.videoInMessage[self.cnt]
                # else:
                #     data = {}  # 데이터가 없으면 빈 딕셔너리


                message_name = "step " + str(self.cnt + 1) + ": " + self.Server.message[self.cnt]
                
                # ✅ SPEC_CONFIG에서 검증 설정 가져오기
                current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                current_protocol = self.trans_protocols[self.cnt] if self.cnt < len(self.trans_protocols) else "basic"

                # ✅ API별 누적 데이터 초기화 (시스템과 동일)
                if not hasattr(self, 'api_accumulated_data'):
                    self.api_accumulated_data = {}
                
                api_index = self.cnt
                # ✅ 첫 회차면 초기화 (이전 데이터 제거)
                if self.current_retry == 0 or api_index not in self.api_accumulated_data:
                    self.api_accumulated_data[api_index] = {
                        'data_parts': [],
                        'error_messages': [],
                        'validation_results': [],
                        'total_pass': 0,
                        'total_error': 0
                    }
                
                accumulated = self.api_accumulated_data[api_index]
                
                # ✅ 시스템과 동일: for 루프 제거, current_retry 사용
                retry_attempt = self.current_retry
                
                combined_error_parts = []
                step_result = "PASS"
                add_pass = 0
                add_err = 0

                # 실시간 진행률 표시
                if retry_attempt == 0:
                    self.valResult.append(message_name)
                    # self.valResult.append(f"🔄 부하테스트 시작: 총 {current_retries}회 검증 예정")  # 가독성 개선: 주석 처리

                # 순서 확인용 로그 - 가독성 개선: 주석 처리
                # print(f"[PLATFORM] 시스템 요청 수신: {self.Server.message[self.cnt]} (시도 {retry_attempt + 1}/{current_retries})")

                # self.valResult.append(f"📨 시스템 요청 수신, 검증 중... [{retry_attempt + 1}/{current_retries}]")  # 가독성 개선: 주석 처리

                # 테이블에 실시간 진행률 표시
                self.update_table_row_with_retries(self.cnt, "진행중", 0, 0, "검증 진행중...", f"시도 {retry_attempt + 1}/{current_retries}", retry_attempt + 1)

                QApplication.processEvents()

                # 현재 데이터 사용 (이미 읽음)
                current_data = self._get_latest_request_data(api_name, "REQUEST") or {}

                if self.Server.message[self.cnt] in CONSTANTS.none_request_message:
                    # 매 시도마다 데이터 수집
                    tmp_res_auth = json.dumps(current_data, indent=4, ensure_ascii=False)
                    if retry_attempt == 0:
                        accumulated['data_parts'].append(f"[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")
                    else:
                        accumulated['data_parts'].append(f"\n[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")

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
                        accumulated['data_parts'].append(f"[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")
                    else:
                        accumulated['data_parts'].append(f"\n[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")
                    
                    # ✅ 디버깅: 어떤 스키마로 검증하는지 확인
                    if retry_attempt == 0:  # 첫 시도에만 출력
                        print(f"\n[DEBUG] ========== 스키마 검증 디버깅 ==========")
                        print(f"[DEBUG] cnt={self.cnt}, API={self.Server.message[self.cnt] if self.cnt < len(self.Server.message) else 'N/A'}")
                        print(f"[DEBUG] current_protocol={current_protocol}")
                        print(f"[DEBUG] videoInSchema 총 개수={len(self.videoInSchema)}")
                        print(f"[DEBUG] 사용 스키마: videoInSchema[{self.cnt}]")
                        
                        # 스키마 필드 확인
                        if self.cnt < len(self.videoInSchema):
                            schema_to_use = self.videoInSchema[self.cnt]
                            if isinstance(schema_to_use, dict):
                                schema_keys = list(schema_to_use.keys())[:5]
                                print(f"[DEBUG] 스키마 필드 (first 5): {schema_keys}")
                    
                    try:
                        print(f"[DEBUG] json_check_ 호출 시작")
                        print(f"[DEBUG] videoInSchema[{self.cnt}] type: {type(self.videoInSchema[self.cnt])}")
                        print(f"[DEBUG] current_data type: {type(current_data)}")
                        print(f"[DEBUG] current_data 내용: {repr(current_data)}")
                        
                        val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.videoInSchema[self.cnt],
                                                                            current_data, self.flag_opt)
                        
                        print(f"[DEBUG] json_check_ 성공: result={val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
                    except TypeError as e:
                        if "unhashable type" in str(e):
                            import traceback
                            print("[DEBUG][unhashable] error in platformVal_all.py update_view")
                            print("videoInSchema:", self.videoInSchema[self.cnt])
                            print("current_data:", current_data)
                            print("videoInSchema type:", type(self.videoInSchema[self.cnt]))
                            print("current_data type:", type(current_data))
                            traceback.print_exc()
                        raise
                    except Exception as e:
                        print(f"[DEBUG] json_check_ 기타 에러: {e}")
                        import traceback
                        traceback.print_exc()
                        raise
                    
                    if retry_attempt == 0:  # 첫 시도에만 출력
                        print(f"[DEBUG] 검증 결과: {val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
                        print(f"[DEBUG] ==========================================\n")
                    
                    add_pass += key_psss_cnt
                    add_err += key_error_cnt
                
                    inbound_err_txt = self._to_detail_text(val_text)
                    if val_result == "FAIL":
                        step_result = "FAIL"
                        combined_error_parts.append(f"[검증 {retry_attempt + 1}회차] [Inbound] " + inbound_err_txt)
                    
                    # ✅ WebHook 프로토콜인 경우 웹훅 응답 표시 (transProtocol 기반으로만 판단)
                    if current_protocol == "WebHook":
                        
                        # ✅ 웹훅 스레드가 생성될 때까지 짧게 대기
                        wait_count = 0
                        while wait_count < 10:  # 최대 1초 (0.1초 x 10)
                            if hasattr(self.Server, 'webhook_thread') and self.Server.webhook_thread:
                                # print(f"[DEBUG][PLATFORM] 웹훅 스레드 발견! (대기 횟수: {wait_count})")
                                break
                            time.sleep(0.1)
                            wait_count += 1
                        
                        # ✅ 웹훅 스레드 완료 대기
                        if hasattr(self.Server, 'webhook_thread') and self.Server.webhook_thread:
                            self.Server.webhook_thread.join(timeout=5)  # wait/join 처리 -> 이벤트가 올때까지만 대기
                        
                        # ✅ 실제 웹훅 응답 사용 (Server.webhook_response)
                        if hasattr(self.Server, 'webhook_response') and self.Server.webhook_response:
                            webhook_response = self.Server.webhook_response  # 실제 웹훅 응답
                            # print(f"[DEBUG][PLATFORM] 웹훅 응답 사용: {webhook_response}")
                            tmp_webhook_response = json.dumps(webhook_response, indent=4, ensure_ascii=False)
                            accumulated['data_parts'].append(f"\n--- Webhook 응답 (시도 {retry_attempt + 1}회차) ---\n{tmp_webhook_response}")
                            
                            # ✅ 디버깅: 웹훅 응답 검증 스키마 확인
                            if retry_attempt == 0:  # 첫 시도에만 출력
                                print(f"\n[DEBUG] ========== 웹훅 응답 검증 디버깅 ==========")
                                print(f"[DEBUG] cnt={self.cnt}, API={self.Server.message[self.cnt] if self.cnt < len(self.Server.message) else 'N/A'}")
                                print(f"[DEBUG] videoWebhookSchema 총 개수={len(self.videoWebhookSchema)}")
                            
                            # ✅ 웹훅 응답 검증 (플랫폼은 시스템의 웹훅 응답을 받음 - spec_001의 웹훅 응답 스키마)
                            if len(self.videoWebhookSchema) > 0:
                                if retry_attempt == 0:
                                    print(f"[DEBUG] 사용 스키마: videoWebhookSchema[0]")
                                    schema_to_use = self.videoWebhookSchema[0]
                                    if isinstance(schema_to_use, dict):
                                        schema_keys = list(schema_to_use.keys())[:5]
                                        print(f"[DEBUG] 웹훅 응답 스키마 필드 (first 5): {schema_keys}")
                                
                                webhook_resp_val_result, webhook_resp_val_text, webhook_resp_key_psss_cnt, webhook_resp_key_error_cnt = json_check_(
                                    self.videoWebhookSchema[0], webhook_response, self.flag_opt
                                )
                                
                                if retry_attempt == 0:
                                    print(f"[DEBUG] 웹훅 응답 검증 결과: {webhook_resp_val_result}, pass={webhook_resp_key_psss_cnt}, error={webhook_resp_key_error_cnt}")
                                    print(f"[DEBUG] ==========================================\n")
                                
                                add_pass += webhook_resp_key_psss_cnt
                                add_err += webhook_resp_key_error_cnt
                                
                                webhook_resp_err_txt = self._to_detail_text(webhook_resp_val_text)
                                if webhook_resp_val_result == "FAIL":
                                    step_result = "FAIL"
                                    combined_error_parts.append(f"[검증 {retry_attempt + 1}회차] [Webhook 응답] " + webhook_resp_err_txt)
                            else:
                                if retry_attempt == 0:
                                    print(f"[DEBUG] videoWebhookSchema가 없습니다!")
                                    print(f"[DEBUG] ==========================================\n")
                        else:
                            # print(f"[DEBUG][PLATFORM] 웹훅 응답 없음")
                            accumulated['data_parts'].append(f"\n--- Webhook 응답 ---\nnull")
                    
                    # ✅ LongPolling 프로토콜인 경우 (순수 LongPolling만 처리)
                    elif current_protocol == "LongPolling":

                        if retry_attempt == 0:
                            print(f"[LongPolling] 실시간 데이터 수신 대기 중... (API: {api_name})")

                        pass
                
                # ✅ 이번 회차 결과를 누적 데이터에 저장
                accumulated['validation_results'].append(step_result)
                accumulated['error_messages'].extend(combined_error_parts)
                accumulated['total_pass'] += add_pass
                accumulated['total_error'] += add_err

                # ✅ current_retry 증가
                self.current_retry += 1
                
                # ✅ 모든 재시도 완료 여부 확인
                if self.current_retry >= current_retries:
                    # 최종 결과
                    final_result = "FAIL" if "FAIL" in accumulated['validation_results'] else "PASS"

                    # 스텝 버퍼 저장
                    data_text = "\n".join(accumulated['data_parts']) if accumulated['data_parts'] else "아직 수신된 데이터가 없습니다."
                    error_text = "\n".join(accumulated['error_messages']) if accumulated['error_messages'] else "오류가 없습니다."
                    self.step_buffers[self.cnt]["data"] = data_text
                    self.step_buffers[self.cnt]["error"] = error_text
                    self.step_buffers[self.cnt]["result"] = final_result

                    try:
                        api_name = self.Server.message[self.cnt]  # 현재 스텝의 API 이름
                        events = list(self.Server.trace.get(api_name, []))  # deque -> list
                        self.step_buffers[self.cnt]["events"] = events
                    except Exception:
                        self.step_buffers[self.cnt]["events"] = []

                    # 아이콘/툴팁 갱신
                    if accumulated['data_parts']:
                        tmp_res_auth = accumulated['data_parts'][0]
                    else:
                        tmp_res_auth = "No data"
                    
                    # 테이블 업데이트 
                    self.update_table_row_with_retries(self.cnt, final_result, accumulated['total_pass'], accumulated['total_error'], tmp_res_auth, error_text, current_retries)

                    # 모니터링 창에 최종 결과 표시
                    self.valResult.append(f"\n✅ 부하테스트 완료: {current_retries}회 검증 완료")
                    self.valResult.append(f"프로토콜: {current_protocol}")
                    self.valResult.append("\n" + data_text)
                    self.valResult.append(final_result)

                    # 누적 점수 업데이트
                    self.total_error_cnt += accumulated['total_error']
                    self.total_pass_cnt += accumulated['total_pass']

                    self.update_score_display()
                    
                    total_fields = self.total_pass_cnt + self.total_error_cnt
                    if total_fields > 0:
                        score_text = str((self.total_pass_cnt / total_fields * 100))
                    else:
                        score_text = "0"
                    
                    self.valResult.append("Score : " + score_text)
                    self.valResult.append(
                        "Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(self.total_error_cnt) + "(누적 오류 필드 수)\n")
                    
                    self.cnt += 1
                    self.current_retry = 0  # 재시도 카운터 리셋
                    
                    # ✅ [TIMING_CONTROL] 반복 검증 시 대기시간 (CONSTANTS.enable_retry_delay로 제어)
                    if CONSTANTS.enable_retry_delay:
                        print(f"[TIMING_DEBUG] ⚠️ 수동 지연(SLEEP): API 완료 후 2초 대기 추가 (API: {self.Server.message[self.cnt-1] if self.cnt > 0 else 'N/A'})")
                        print(f"[TIMING_DEBUG] ⚠️ WARNING: enable_retry_delay=True로 인한 인위적 대기입니다!")
                        print(f"[TIMING_DEBUG] 💡 제안: CONSTANTS.enable_retry_delay=False로 설정하여 이 sleep을 제거하세요.")
                        self.time_pre = time.time() + 2.0
                    else:
                        print(f"[TIMING_DEBUG] ✅ 수동 지연 비활성화: API 완료, 다음 시스템 요청 대기 (API: {self.Server.message[self.cnt-1] if self.cnt > 0 else 'N/A'})")
                        print(f"[TIMING_DEBUG] ✅ enable_retry_delay=False: 시스템 요청 도착 시 즉시 검증 시작합니다.")
                        self.time_pre = time.time()  # 즉시 다음 검증 가능
                else:
                    # 재시도인 경우
                    if CONSTANTS.enable_retry_delay:
                        print(f"[TIMING_DEBUG] ⚠️ 수동 지연(SLEEP): 재시도 후 2초 대기 추가 (API: {self.Server.message[self.cnt] if self.cnt < len(self.Server.message) else 'N/A'}, 시도: {self.current_retry}/{current_retries})")
                        print(f"[TIMING_DEBUG] ⚠️ WARNING: enable_retry_delay=True로 인한 인위적 대기입니다!")
                        self.time_pre = time.time() + 2.0
                    else:
                        print(f"[TIMING_DEBUG] ✅ 수동 지연 비활성화: 재시도 완료, 다음 시스템 요청 대기 (API: {self.Server.message[self.cnt] if self.cnt < len(self.Server.message) else 'N/A'})")
                        print(f"[TIMING_DEBUG] ✅ enable_retry_delay=False: 시스템 요청 도착 시 즉시 검증 시작합니다.")
                        self.time_pre = time.time()  # 즉시 다음 재시도 가능
                        
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
                
                total_fields = self.total_pass_cnt + self.total_error_cnt
                if total_fields > 0:
                    score_text = str((self.total_pass_cnt / total_fields * 100))
                else:
                    score_text = "0"
                
                self.valResult.append("Score : " + score_text)
                self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                    self.total_error_cnt) + "(누적 오류 필드 수)\n")
                
                # 테이블 업데이트 (Message Missing)
                add_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                if self.flag_opt:
                    add_err += tmp_fields_opt_cnt
                
                # ✅ SPEC_CONFIG에서 retries 가져오기
                current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                self.update_table_row_with_retries(self.cnt, "FAIL", 0, add_err, "", "Message Missing!", current_retries)
                
                self.cnt += 1

            if self.cnt == len(self.Server.message):
                self.tick_timer.stop()
                self.valResult.append("검증 절차가 완료되었습니다.")
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

        except Exception as err:
            print(f"[ERROR] update_view에서 예외 발생: {err}")
            print(f"[ERROR] 현재 상태 - cnt={self.cnt}, current_retry={self.current_retry}")
            print(f"[ERROR] Server.message 길이: {len(self.Server.message) if hasattr(self.Server, 'message') else 'None'}")
            import traceback
            print(f"[ERROR] Traceback:")
            traceback.print_exc()
            
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
        # 메인 화면의 평가 점수 레이블 업데이트
        if not (hasattr(self, "spec_pass_label") and hasattr(self, "spec_total_label") and hasattr(self, "spec_score_label")):
            return
        
        total_fields = self.total_pass_cnt + self.total_error_cnt
        if total_fields > 0:
            score = (self.total_pass_cnt / total_fields) * 100
        else:
            score = 0
        
        # 시험 분야별 점수 업데이트
        self.spec_pass_label.setText(f"통과 필드 수: {self.total_pass_cnt}")
        self.spec_total_label.setText(f"전체 필드 수: {total_fields}")
        self.spec_score_label.setText(f"종합 평가 점수: {score:.1f}%")
        
        # 전체 점수 업데이트 (현재는 1개 spec만 실행하므로 동일한 값)
        if hasattr(self, "total_pass_label") and hasattr(self, "total_total_label") and hasattr(self, "total_score_label"):
            self.total_pass_label.setText(f"통과 필드 수: {self.total_pass_cnt}")
            self.total_total_label.setText(f"전체 필드 수: {total_fields}")
            self.total_score_label.setText(f"종합 평가 점수: {score:.1f}%")

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

    def create_spec_selection_panel(self, parent_layout):
        """시험 분야 선택 패널 생성"""
        # 시험 분야 패널
        panel_widget = QWidget()
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(10, 10, 10, 10)
        
        # 시험 분야 확인 문구
        title = QLabel("시험 분야를 선택하세요.")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        panel_layout.addWidget(title)
        
        # 시험 분야명 테이블
        field_group = self.create_test_field_group()
        panel_layout.addWidget(field_group)
        
        panel_widget.setLayout(panel_layout)
        parent_layout.addWidget(panel_widget)
        
        # 선택된 시험 분야 행
        self.selected_test_field_row = None
    
    def create_test_field_group(self):
        """
        ✅ Platform은 Request 검증만 - Request 스키마 ID만 표시 (3개)
        """
        group = QGroupBox("시험 분야")
        layout = QVBoxLayout()
        
        self.test_field_table = QTableWidget(0, 1)
        self.test_field_table.setHorizontalHeaderLabels(["시험 분야명"])
        self.test_field_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)
        self.test_field_table.verticalHeader().setVisible(False)
        self.test_field_table.setMaximumHeight(200)
        
        # platform spec_id -> spec_config 기반
        request_spec_ids = list(CONSTANTS.SPEC_CONFIG.keys())
        
        if hasattr(CONSTANTS, 'SPEC_CONFIG') and CONSTANTS.SPEC_CONFIG:
            spec_items = [(sid, CONSTANTS.SPEC_CONFIG[sid]) for sid in request_spec_ids if sid in CONSTANTS.SPEC_CONFIG]
            self.test_field_table.setRowCount(len(spec_items))
            
            # spec_id와 인덱스 매핑 저장
            self.spec_id_to_index = {}
            self.index_to_spec_id = {}
            
            for idx, (spec_id, config) in enumerate(spec_items):
                description = config.get('test_name', f'시험 분야 {idx + 1}')
                # ✅ 플랫폼은 요청 검증 역할 명시
                description_with_role = f"{description} (요청 검증)"
                item = QTableWidgetItem(description_with_role)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.test_field_table.setItem(idx, 0, item)
                
                # 매핑 저장
                self.spec_id_to_index[spec_id] = idx
                self.index_to_spec_id[idx] = spec_id
            
            # 현재 로드된 spec_id 선택
            if self.current_spec_id in self.spec_id_to_index:
                current_index = self.spec_id_to_index[self.current_spec_id]
                self.test_field_table.selectRow(current_index)
                self.selected_test_field_row = current_index
        
        layout.addWidget(self.test_field_table)
        group.setLayout(layout)
        return group
    
    def on_test_field_selected(self, row, col):
        """
        ✅ SPEC_CONFIG 기반 - 시험 분야 클릭 시 해당 시스템으로 동적 전환
        """
        try:
            self.selected_test_field_row = row
            
            # ✅ 클릭한 행에 해당하는 spec_id 가져오기
            if row in self.index_to_spec_id:
                new_spec_id = self.index_to_spec_id[row]
                
                # 이미 선택된 시스템이면 무시
                if new_spec_id == self.current_spec_id:
                    return
                
                print(f"[PLATFORM] 🔄 시험 분야 전환: {self.current_spec_id} → {new_spec_id}")
                
                # spec_id 업데이트
                self.current_spec_id = new_spec_id
                
                # spec 데이터 다시 로드
                self.load_specs_from_constants()
                
                # 테이블 초기화
                self.cnt = 0
                self.current_retry = 0
                self.total_pass_cnt = 0
                self.total_error_cnt = 0
                self.message_error = []
                
                # step_buffers 재생성
                self.step_buffers = [
                    {"data": "", "error": "", "result": "PASS"} for _ in range(len(self.videoMessages))
                ]
                
                # trace 초기화 (Server 객체에 있음)
                if hasattr(self.Server, 'trace'):
                    self.Server.trace.clear()
                
                # 시험 결과 테이블 업데이트
                self.update_result_table_with_apis(self.videoMessages)
                
                # Server 객체 초기화
                if hasattr(self, 'Server'):
                    self.Server.cnt = 0
                    self.Server.message = self.videoMessages
                    self.Server.outMessage = self.videoOutMessage
                    self.Server.outCon = self.videoOutConstraint
                    self.Server.inSchema = self.videoInSchema
                    self.Server.webhookSchema = self.videoWebhookSchema
                    self.Server.webhookData = self.videoWebhookData
                
                # 설정 다시 로드
                self.get_setting()
                
                # 평가 점수 디스플레이 초기화
                self.update_score_display()
                
                # 결과 텍스트 초기화
                self.valResult.clear()
                self.valResult.append(f"✅ 시스템 전환 완료: {self.spec_description}")
                self.valResult.append(f"📋 API 목록 ({len(self.videoMessages)}개): {self.videoMessages}\n")
                
                print(f"[PLATFORM] ✅ 시스템 전환 완료: {self.spec_description}, API 수: {len(self.videoMessages)}")
        except Exception as e:
            print(f"시험 분야 선택 처리 실패: {e}")
            import traceback
            traceback.print_exc()
    
    def update_result_table_with_apis(self, api_list):
        """시험 결과 테이블을 새로운 API 목록으로 업데이트"""
        api_count = len(api_list)
        self.tableWidget.setRowCount(api_count)
        
        # 각 행의 API 명 업데이트
        for row in range(api_count):
            # API 명
            api_item = QTableWidgetItem(api_list[row])
            api_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, api_item)
            
            # 나머지 컬럼 초기화
            # 결과 아이콘 (검정색)
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 1, icon_widget)
            
            # 검증 횟수, 통과 필드 수, 전체 필드 수, 실패 필드 수, 평가 점수
            for col in range(2, 7):
                item = QTableWidgetItem("0" if col != 6 else "0%")
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)
            
            # 상세 내용 버튼 (중앙 정렬을 위한 위젯 컨테이너)
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
            
            self.tableWidget.setCellWidget(row, 7, container)
            
            # 행 높이 설정
            self.tableWidget.setRowHeight(row, 40)


    def initUI(self):
        # 창 크기 설정 (main.py와 동일)
        if not self.embedded:
            self.resize(1200, 720)
            self.setWindowTitle('통합플랫폼 연동 검증')
        
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

        # 시험 분야 선택 영역 추가
        self.create_spec_selection_panel(mainLayout)

        # 시험 결과
        self.valmsg = QLabel('시험 결과', self)
        mainLayout.addWidget(self.valmsg)

        self.init_centerLayout()
        contentWidget = QWidget()
        contentWidget.setLayout(self.centerLayout)
        # 고정 크기 제거 - 반응형으로 변경
        mainLayout.addWidget(contentWidget, 1)  # stretch factor 1 추가

        mainLayout.addSpacing(15)

        # 수신 메시지 실시간 모니터링
        monitor_label = QLabel("수신 메시지 실시간 모니터링")
        mainLayout.addWidget(monitor_label)
        self.valResult = QTextBrowser(self)
        # 고정 크기 제거 - 반응형으로 변경
        self.valResult.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mainLayout.addWidget(self.valResult, 1)  # stretch factor 1 추가

        mainLayout.addSpacing(15)

        # 평가 점수 표시 (메인 화면에 추가)
        spec_score_group = self.create_spec_score_display_widget()
        mainLayout.addWidget(spec_score_group)
        
        # 전체 점수 표시
        total_score_group = self.create_total_score_display_widget()
        mainLayout.addWidget(total_score_group)

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
        
        # 창 제목 설정 (embedded가 아닐 때만)
        if not self.embedded:
            self.setWindowTitle('물리보안 통합플랫폼 연동 검증 소프트웨어')

        # tableWidget이 생성된 후에 초기 시험 분야 선택 처리
        if hasattr(self, '_initial_spec_index'):
            self.on_test_field_selected(self._initial_spec_index, 0)

        if not self.embedded:
            self.show()

    def init_centerLayout(self):
        # 동적 API 개수에 따라 테이블 생성
        api_count = len(self.videoMessages)
        self.tableWidget = QTableWidget(api_count, 8)
        self.tableWidget.setHorizontalHeaderLabels(["API 명", "결과", "검증 횟수", "통과 필드 수", "전체 필드 수", "실패 필드 수", "평가 점수", "상세 내용"])
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
            # 실패 필드 수
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
                schema_data = self.videoInSchema[row] if row < len(self.videoInSchema) else None
            except:
                schema_data = None
            
            # ✅ 웹훅 검증인 경우에만 웹훅 스키마 (SPEC_CONFIG 기반)
            webhook_schema = None
            if row < len(self.trans_protocols):
                current_protocol = self.trans_protocols[row]
                if current_protocol == "WebHook":
                    try:
                        webhook_schema = self.videoWebhookSchema[0] if len(self.videoWebhookSchema) > 0 else None
                    except:
                        webhook_schema = None
            
            # 통합 팝업창 띄우기
            dialog = CombinedDetailDialog(api_name, buf, schema_data, webhook_schema)
            dialog.exec_()
            
        except Exception as e:
            CustomDialog(f"오류:\n{str(e)}", "상세 내용 확인 오류")


    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭 시 호출되는 함수 (결과 아이콘 클릭용으로 유지)"""
        if col == 1:
            msg = getattr(self, f"step{row+1}_msg", "")
            if msg:
                CustomDialog(msg, self.tableWidget.item(row, 0).text())

    def create_spec_score_display_widget(self):
        """메인 화면에 표시할 시험 분야별 평가 점수 위젯 생성"""
        # 시험 분야별 점수 그룹
        spec_group = QGroupBox('시험 분야별 점수')
        spec_group.setMaximumWidth(1050)
        spec_group.setMinimumWidth(950)
        spec_group.setMaximumHeight(120)
        
        # 분야명 레이블
        self.spec_name_label = QLabel(f"📋 {self.spec_description} ({len(self.videoMessages)}개 API)")
        spec_name_font = self.spec_name_label.font()
        spec_name_font.setPointSize(14)
        spec_name_font.setBold(True)
        self.spec_name_label.setFont(spec_name_font)
        
        # 점수 레이블들
        self.spec_pass_label = QLabel("통과 필드 수: 0")
        self.spec_total_label = QLabel("전체 필드 수: 0")
        self.spec_score_label = QLabel("종합 평가 점수: 0.0%")
        
        font = self.spec_pass_label.font()
        font.setPointSize(12)
        self.spec_pass_label.setFont(font)
        self.spec_total_label.setFont(font)
        self.spec_score_label.setFont(font)
        
        spec_layout = QVBoxLayout()
        spec_layout.addWidget(self.spec_name_label)
        spec_layout.addSpacing(5)
        
        spec_score_layout = QHBoxLayout()
        spec_score_layout.setSpacing(50)
        spec_score_layout.addWidget(self.spec_pass_label)
        spec_score_layout.addWidget(self.spec_total_label)
        spec_score_layout.addWidget(self.spec_score_label)
        spec_score_layout.addStretch()
        
        spec_layout.addLayout(spec_score_layout)
        spec_group.setLayout(spec_layout)
        
        return spec_group

    def create_total_score_display_widget(self):
        """메인 화면에 표시할 전체 평가 점수 위젯 생성"""
        # 전체 점수 그룹
        total_group = QGroupBox('전체 점수')
        total_group.setMaximumWidth(1050)
        total_group.setMinimumWidth(950)
        total_group.setMaximumHeight(90)
        
        # 점수 레이블들 (전체 점수는 볼드체로 강조)
        self.total_pass_label = QLabel("통과 필드 수: 0")
        self.total_total_label = QLabel("전체 필드 수: 0")
        self.total_score_label = QLabel("종합 평가 점수: 0.0%")
        
        font = self.total_pass_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.total_pass_label.setFont(font)
        self.total_total_label.setFont(font)
        self.total_score_label.setFont(font)
        
        total_layout = QHBoxLayout()
        total_layout.setSpacing(60)
        total_layout.addWidget(self.total_pass_label)
        total_layout.addWidget(self.total_total_label)
        total_layout.addWidget(self.total_score_label)
        total_layout.addStretch()
        
        total_group.setLayout(total_layout)
        
        return total_group

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
        """창 크기 변경 시 반응형 UI 조정"""
        try:
            super().resizeEvent(event)
            
            # 테이블 위젯 크기 조정
            if hasattr(self, 'tableWidget'):
                # 현재 창 너비의 95%를 테이블 너비로 설정
                new_width = int(self.width() * 0.95)
                new_width = max(950, new_width)  # 최소 950px
                
                # 컬럼 너비를 창 크기에 맞춰 조정
                total_width = new_width - 50  # 여백 고려
                col_widths = [0.22, 0.09, 0.10, 0.11, 0.11, 0.10, 0.11, 0.16]  # 비율
                for col, ratio in enumerate(col_widths):
                    self.tableWidget.setColumnWidth(col, int(total_width * ratio))
                
        except Exception as e:
            print(f"resizeEvent 오류: {e}")

    def _clean_trace_dir_once(self):
        """results/trace 폴더 안의 파일들을 삭제"""
        os.makedirs(CONSTANTS.trace_path, exist_ok=True)
        for name in os.listdir(CONSTANTS.trace_path):
            path = os.path.join(CONSTANTS.trace_path, name)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def sbtn_push(self):
        try:
            print(f"[DEBUG] sbtn_push 시작")
            print(f"[DEBUG] videoMessages 개수: {len(self.videoMessages)}")
            print(f"[DEBUG] videoInSchema 개수: {len(self.videoInSchema)}")
            print(f"[DEBUG] videoOutMessage 개수: {len(self.videoOutMessage)}")
            
            self._clean_trace_dir_once()
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
                self.videoOutMessage[0]['accessToken'] = token_value
            
            # Server 설정 (디버그 메시지 추가)
            print(f"[DEBUG] Server 설정 시작")
            self.Server.message = self.videoMessages
            self.Server.outMessage = self.videoOutMessage
            self.Server.inSchema = self.videoInSchema
            self.Server.webhookData = self.videoWebhookData  # ✅ 웹훅 이벤트 데이터 (플랫폼 → 시스템)
            self.Server.system = "video"
            self.Server.timeout = timeout
            print(f"[DEBUG] Server 설정 완료")
            #print(f"[DEBUG] sbtn_push: Server configured - message={self.Server.message[:3] if self.Server.message else 'None'}...")
            #print(f"[DEBUG] sbtn_push: webhookData length={len(self.Server.webhookData) if self.Server.webhookData else 0}")  # ✅ 디버그 로그
            
            print(f"[DEBUG] init_win 호출")
            self.init_win()
            self.valResult.clear()  # 초기화
            self.final_report = ""  # 초기화
            print(f"[DEBUG] UI 초기화 완료")
            
            # 테이블 아이콘 초기화
            print(f"[DEBUG] 테이블 아이콘 초기화 시작")
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
            print(f"[DEBUG] 인증 설정 시작")
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
            
            # (10/20) 수정
            # 서버는 address_ip, port로 listen, 클라이언트는 constants.url로 접속
            print(f"[DEBUG] 서버 시작 준비")
            url = CONSTANTS.url.split(":")
            address_port = int(url[-1])  # 포트만 사용
            address_ip = "127.0.0.1"  # 내부 IP 주소, 외부에서도 접근 가능하게 설정

            print(f"[DEBUG] 플랫폼 서버 시작: {address_ip}:{address_port}")
            self.server_th = server_th(handler_class=self.Server, address=address_ip, port=address_port)
            self.server_th.start()
            
            # 서버 준비 완료까지 대기 (첫 실행 시)
            if self.first_run:
                self.valResult.append("🔄 플랫폼 서버 초기화 중...")
                time.sleep(5)
                self.valResult.append("✅ 플랫폼 서버 준비 완료")
            
            print(f"[DEBUG] 타이머 시작")
            self.tick_timer.start(1000)  # 시스템쪽과 동일한 1초 간격
            print(f"[DEBUG] sbtn_push 완료")
            
        except Exception as e:
            print(f"[ERROR] sbtn_push에서 예외 발생: {e}")
            import traceback
            print(f"[ERROR] Traceback:")
            traceback.print_exc()
            
            # 에러 발생 시 버튼 상태 복원
            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)

    def stop_btn_clicked(self):
        self.tick_timer.stop()
        self.valResult.append("검증 절차가 중지되었습니다.")
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)

    def init_win(self):
        self.cnt = 0
        # 버퍼 초기화 - API 개수에 맞춰 동적으로 생성
        api_count = len(self.videoMessages) if self.videoMessages else 9
        self.step_buffers = [{"data": "", "result": "", "error": ""} for _ in range(api_count)]
       #print(f"[DEBUG] init_win: step_buffers 초기화 완료 (크기={api_count})")
        # JSON 파일 초기화 제거 - 더 이상 개별 JSON 파일을 사용하지 않음
        # (videoData_request.py와 videoData_response.py에서 데이터를 가져옴)
        
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
            self.tableWidget.setItem(i, 4, QTableWidgetItem("0"))
            self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)

    def show_result_page(self):
        """시험 결과 페이지 표시"""
        if self.embedded:
            # Embedded 모드: 시그널을 emit하여 main.py에서 스택 전환 처리
            self.showResultRequested.emit(self)
        else:
            # Standalone 모드: 래퍼 윈도우가 있으면 그 안에서 스택 전환
            if self._wrapper_window is not None:
                self._wrapper_window._show_result_page()
            else:
                # 래퍼가 없으면 새 창으로 표시 (하위 호환성)
                if hasattr(self, 'result_window') and self.result_window is not None:
                    self.result_window.close()
                self.result_window = ResultPageWidget(self, embedded=False)
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
            step_lines.append(f"{name} | 결과: {final_res} | 검증 횟수: {retries} | 통과 필드 수: {pass_cnt} | 전체 필드 수: {total_cnt} | 실패 필드 수: {fail_cnt} | 평가 점수: {score}") 

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

    # busy loop 대체용 -> cpu 사용량 최적화
    def run(self):
        import time
        while True:
            with open(resource_path("spec/rows.json"), "r", encoding="UTF-8") as out_file:
                data = json.load(out_file)
            if data is not None:
                with open(resource_path("spec/rows.json"), "w", encoding="UTF-8") as out_file:
                    json.dump(None, out_file, ensure_ascii=False)
                self.json_update_data.emit(data)
            time.sleep(0.1)  # 0.1초 대기


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))
    # 래퍼 윈도우 사용 (스택 전환 지원)
    ex = PlatformValidationWindow()
    ex.initialize()  # MyApp 정의 후 초기화
    ex.show()
    sys.exit(app.exec())