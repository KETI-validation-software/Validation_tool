# 물리보안 통합플랫폼 검증 소프트웨어
# physical security integrated platform validation software

import os
from api.api_server import Server
import time
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor, QPixmap
from PyQt5.QtCore import Qt, QSettings, QTimer, QThread, pyqtSignal
import sys
import ssl
from datetime import datetime
import json
from pathlib import Path
from core.functions import build_result_json
import requests

import config.CONSTANTS as CONSTANTS
from core.functions import json_check_, save_result, resource_path, json_to_data, timeout_field_finder
from core.json_checker_new import check_message_data, check_message_schema, check_message_error
from splash_screen import LoadingPopup
import spec.Data_response as data_response_module
import spec.Schema_response as schema_response_module
import spec.Schema_request as schema_request_module
from http.server import HTTPServer
import json
import traceback
import warnings
import importlib
from core.validation_registry import get_validation_rules

warnings.filterwarnings('ignore')
import os

result_dir = os.path.join(os.getcwd(), "results")
os.makedirs(result_dir, exist_ok=True)


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
        error_text = step_buffer["error"] if step_buffer["error"] else ("오류가 없습니다." if result == "PASS" else "")
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
            return "빈 스키마"

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

        # 배경 이미지 설정
        self.setObjectName("platform_main")
        self.setAttribute(Qt.WA_StyledBackground, True)

        bg_path = resource_path("assets/image/common/bg.png").replace("\\", "/")
        print(f"배경 이미지 경로: {bg_path}")

        self.setStyleSheet(f"""
            #platform_main {{
                background-image: url('{bg_path}');
                background-repeat: no-repeat;
                background-position: center;
            }}
            QScrollArea, QScrollArea QWidget, QScrollArea::viewport,
            QGroupBox, QWidget#scroll_widget, QLabel {{
                background: transparent;
            }}
        """)

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
    backRequested = pyqtSignal()

    def __init__(self, parent, embedded=False):
        super().__init__()
        self.parent = parent
        self.embedded = embedded
        self.setWindowTitle('통합플랫폼 연동 시험 결과')
        self.resize(1680, 1080)

        # CONSTANTS 초기화
        self.CONSTANTS = parent.CONSTANTS

        # 현재 선택된 spec_id 저장
        self.current_spec_id = parent.current_spec_id

        # ✅ 시험 결과 페이지 전용 아이콘 설정
        self.img_pass = resource_path("assets/image/test_runner/tag_성공.png")
        self.img_fail = resource_path("assets/image/test_runner/tag_실패.png")
        self.img_none = resource_path("assets/image/icon/icn_basic.png")

        self.initUI()

    def initUI(self):
        # ✅ 메인 레이아웃
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ✅ 배경 이미지 설정
        self.setObjectName("result_main")
        self.setAttribute(Qt.WA_StyledBackground, True)
        bg_path = resource_path("assets/image/common/bg.png").replace("\\", "/")
        self.setStyleSheet(f"""
            QWidget#result_main {{
                background-image: url('{bg_path}');
                background-repeat: no-repeat;
                background-position: center;
            }}
            QScrollArea, QScrollArea QWidget, QScrollArea::viewport,
            QGroupBox, QWidget#scroll_widget, QLabel {{
                background: transparent;
            }}
        """)

        # ✅ 헤더 영역 추가
        header_container = QWidget()
        header_container.setFixedSize(1680, 56)
        header_container_layout = QHBoxLayout()
        header_container_layout.setContentsMargins(0, 8, 0, 0)
        header_container_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedSize(1680, 56)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header_layout.setSpacing(10)

        # 헤더 로고
        logo_label = QLabel(header_widget)
        logo_pixmap = QPixmap(resource_path("assets/image/common/header_logo.png"))
        logo_label.setPixmap(logo_pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(36, 36)
        header_layout.addWidget(logo_label)

        # 헤더 타이틀
        title_label = QLabel('통합플랫폼 연동 시험 결과', header_widget)
        title_label.setAlignment(Qt.AlignVCenter)
        title_style = """
            color: #FFF;
            font-family: "Noto Sans KR";
            font-size: 18px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
        """
        title_label.setStyleSheet(title_style)
        header_layout.addWidget(title_label)

        header_container_layout.addWidget(header_widget)
        header_container.setLayout(header_container_layout)
        mainLayout.addWidget(header_container)

        # ✅ 2컬럼 레이아웃
        bg_root = QWidget()
        bg_root.setObjectName("bg_root")
        bg_root.setAttribute(Qt.WA_StyledBackground, True)
        bg_root_layout = QVBoxLayout()
        bg_root_layout.setContentsMargins(0, 0, 0, 0)
        bg_root_layout.setSpacing(0)

        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(0)

        # ✅ 왼쪽 컬럼 (시험 분야 + 시나리오 )
        left_col = QWidget()
        left_col.setFixedSize(479, 906)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # 시험 분야 선택 (폰트 효과 추가)
        title = QLabel("시험 선택")
        title.setStyleSheet("""
            font-size: 16px; 
            font-style: normal; 
            font-family: "Noto Sans KR"; 
            font-weight: 600; 
            color: #222; 
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        """)
        left_layout.addWidget(title)

        # 그룹 테이블
        self.group_table_widget = self.create_group_selection_table()
        left_layout.addWidget(self.group_table_widget)

        # 시험 시나리오 테이블 (크기 줄임: 280px)
        self.field_group = self.create_test_field_group()
        left_layout.addWidget(self.field_group)

        left_layout.addStretch()
        left_col.setLayout(left_layout)

        # ✅ 오른쪽 컬럼 (결과 테이블 및 점수)
        right_col = QWidget()
        right_col.setFixedSize(1064, 906)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 시험 정보 (크기 키움: 360px)
        info_title = QLabel("시험 정보")
        info_title.setStyleSheet("""
            font-size: 16px; 
            font-style: normal; 
            font-family: "Noto Sans KR"; 
            font-weight: 600; 
            color: #222; 
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(info_title)

        info_widget = self._create_simple_info_display()
        right_layout.addWidget(info_widget)
        
        # 시험 결과 라벨
        result_label = QLabel('시험 API')
        result_label.setStyleSheet("""
            font-size: 16px; 
            font-style: normal; 
            font-family: "Noto Sans KR"; 
            font-weight: 600; 
            color: #222; 
            margin-top: 20px;
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(result_label)

        # 결과 테이블 (크기 키움: 350px)
        self.create_result_table(right_layout)

        result_label = QLabel('시험 점수 요약')
        result_label.setStyleSheet("""
            font-size: 16px; 
            font-style: normal; 
            font-family: "Noto Sans KR"; 
            font-weight: 600; 
            color: #222; 
            margin-top: 20px;
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(result_label)

        # 시험 분야별 점수 표시
        self.spec_score_group = self._create_spec_score_display()
        right_layout.addWidget(self.spec_score_group)

        # 전체 점수 표시
        total_score_group = self._create_total_score_display()
        right_layout.addWidget(total_score_group)

        # 뒤로가기 버튼과의 간격
        right_layout.addSpacing(80)  

        # ✅ 버튼 그룹 (가운데 정렬)
        buttonGroup = QWidget()
        buttonGroup.setFixedWidth(1064)
        buttonLayout = QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignCenter)  # 가운데 정렬
        buttonLayout.setContentsMargins(0, 0, 0, 0)

        if self.embedded:
            # Embedded 모드: 뒤로가기 버튼
            back_btn = QPushButton('뒤로가기', self)
            back_btn.setFixedSize(255, 50)
            back_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    border: none;
                    border-radius: 4px;
                    color: white;
                    font-family: "Noto Sans KR";
                    font-size: 15px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #357ABD;
                }
                QPushButton:pressed {
                    background-color: #2868A8;
                }
            """)
            back_btn.clicked.connect(self._on_back_clicked)
            buttonLayout.addWidget(back_btn)
        else:
            # Standalone 모드: 닫기 버튼
            close_btn = QPushButton('닫기', self)
            close_btn.setFixedSize(255, 50)
            try:
                exit_enabled = resource_path("assets/image/test_runner/btn_종료_enabled.png").replace("\\", "/")
                exit_hover = resource_path("assets/image/test_runner/btn_종료_hover.png").replace("\\", "/")
                close_btn.setStyleSheet(f"""
                    QPushButton {{
                        border: none;
                        background-image: url('{exit_enabled}');
                        background-repeat: no-repeat;
                        background-position: center;
                        background-color: transparent;
                    }}
                    QPushButton:hover {{
                        background-image: url('{exit_hover}');
                    }}
                    QPushButton:pressed {{
                        background-image: url('{exit_hover}');
                        opacity: 0.8;
                    }}
                """)
            except:
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E74C3C;
                        border: none;
                        border-radius: 4px;
                        color: white;
                        font-family: "Noto Sans KR";
                        font-size: 15px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                """)
            close_btn.clicked.connect(self.close)
            buttonLayout.addWidget(close_btn)

        buttonGroup.setLayout(buttonLayout)
        right_layout.addWidget(buttonGroup)

        right_layout.addStretch()
        right_col.setLayout(right_layout)

        columns_layout.addWidget(left_col)
        columns_layout.addWidget(right_col)

        bg_root_layout.addLayout(columns_layout)
        bg_root.setLayout(bg_root_layout)
        mainLayout.addWidget(bg_root)

        self.setLayout(mainLayout)

    def create_group_selection_table(self):
        """시험 분야명 테이블"""
        group_box = QWidget()
        group_box.setFixedSize(459, 220)
        group_box.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.group_table = QTableWidget(0, 1)
        self.group_table.setHorizontalHeaderLabels(["시험 분야"])
        self.group_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.group_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.group_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.group_table.verticalHeader().setVisible(False)
        self.group_table.setFixedHeight(219)

        self.group_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                outline: none;
                font-family: "Noto Sans KR";
                font-size: 14px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E0E0E0;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 14px;
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
                font-size: 13px;
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

        group_items = [
            (g.get("group_name", "미지정 그룹"), g.get("group_id", ""))
            for g in SPEC_CONFIG
        ]
        self.group_table.setRowCount(len(group_items))

        self.group_name_to_index = {}
        self.index_to_group_name = {}

        for idx, (name, gid) in enumerate(group_items):
            item = QTableWidgetItem(name)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.group_table.setItem(idx, 0, item)
            self.group_name_to_index[name] = idx
            self.index_to_group_name[idx] = name

        self.group_table.cellClicked.connect(self.on_group_selected)

        layout.addWidget(self.group_table)
        group_box.setLayout(layout)
        return group_box

    def create_test_field_group(self):
        """시험 시나리오 테이블"""
        group_box = QWidget()
        group_box.setFixedSize(459, 650)  # ✅ 더 줄임
        group_box.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.test_field_table = QTableWidget(0, 1)
        self.test_field_table.setHorizontalHeaderLabels(["시험 시나리오"])
        self.test_field_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)
        self.test_field_table.verticalHeader().setVisible(False)
        self.test_field_table.setFixedHeight(645)  # ✅ 5px 여유 확보

        self.test_field_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: "Noto Sans KR";
                font-size: 14px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E0E0E0;
                border-right: 0px solid transparent;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 14px;
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
                font-size: 13px;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                letter-spacing: -0.156px;
            }
        """)

        # 초기 로드: 현재 그룹의 시나리오 표시
        self.load_initial_scenarios()

        layout.addWidget(self.test_field_table)
        group_box.setLayout(layout)
        return group_box

    def load_initial_scenarios(self):
        """초기 시나리오 로드 및 현재 선택된 항목 하이라이트"""
        # ✅ 외부 CONSTANTS.py에서 SPEC_CONFIG 다시 로드
        import sys, os
        SPEC_CONFIG = self.CONSTANTS.SPEC_CONFIG  # 기본값

        if getattr(sys, 'frozen', False):
            # PyInstaller 환경: 외부 CONSTANTS.py 로드
            exe_dir = os.path.dirname(sys.executable)
            external_constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")

            if os.path.exists(external_constants_path):
                try:
                    with open(external_constants_path, 'r', encoding='utf-8') as f:
                        constants_code = f.read()
                    namespace = {'__file__': external_constants_path}
                    exec(constants_code, namespace)
                    SPEC_CONFIG = namespace.get('SPEC_CONFIG', self.CONSTANTS.SPEC_CONFIG)
                    print(f"[RESULT INIT] ✅ 외부 CONSTANTS 로드 완료: {len(SPEC_CONFIG)}개 그룹")
                except Exception as e:
                    print(f"[RESULT INIT] ⚠️ 외부 CONSTANTS 로드 실패, 기본값 사용: {e}")

        # 현재 spec_id가 속한 그룹 찾기
        current_group = None
        for group_data in SPEC_CONFIG:
            if self.current_spec_id in group_data:
                current_group = group_data
                break

        if current_group:
            # 해당 그룹의 시나리오 로드
            self.update_test_field_table(current_group)

            # 현재 spec_id를 선택 상태로 표시
            if hasattr(self, 'spec_id_to_index') and self.current_spec_id in self.spec_id_to_index:
                current_row = self.spec_id_to_index[self.current_spec_id]
                self.test_field_table.selectRow(current_row)

            # 그룹 테이블도 선택
            group_name = current_group.get("group_name")
            if group_name in self.group_name_to_index:
                group_row = self.group_name_to_index[group_name]
                self.group_table.selectRow(group_row)

    def on_group_selected(self, row, col):
        """시험 그룹 선택 시"""
        group_name = self.index_to_group_name.get(row)
        if not group_name:
            return

        # ===== 외부 로드된 SPEC_CONFIG 사용 (fallback: CONSTANTS 모듈) =====
        SPEC_CONFIG = getattr(self.parent, 'LOADED_SPEC_CONFIG', self.parent.CONSTANTS.SPEC_CONFIG)
        selected_group = next(
            (g for g in SPEC_CONFIG if g.get("group_name") == group_name), None
        )
        # ===== 수정 끝 =====

        if selected_group:
            new_group_id = selected_group.get('group_id')
            old_group_id = getattr(self.parent, 'current_group_id', None)

            print(f"[RESULT DEBUG] 🔄 그룹 선택: {old_group_id} → {new_group_id}")

            # ✅ 그룹이 변경되면 current_spec_id 초기화
            if old_group_id != new_group_id:
                self.current_spec_id = None
                print(f"[RESULT DEBUG] ✨ 그룹 변경으로 current_spec_id 초기화")

            # ✅ 그룹 ID 저장
            self.parent.current_group_id = new_group_id
            self.update_test_field_table(selected_group)

    def update_test_field_table(self, group_data):
        """선택된 그룹의 시나리오 목록 갱신"""
        self.test_field_table.clearContents()

        spec_items = [
            (k, v) for k, v in group_data.items()
            if k not in ['group_name', 'group_id'] and isinstance(v, dict)
        ]
        self.test_field_table.setRowCount(len(spec_items))

        self.spec_id_to_index = {}
        self.index_to_spec_id = {}

        for idx, (spec_id, config) in enumerate(spec_items):
            desc = config.get('test_name', f'시험분야 {idx + 1}')
            desc_with_role = f"{desc} (응답 검증)"
            item = QTableWidgetItem(desc_with_role)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.test_field_table.setItem(idx, 0, item)
            self.spec_id_to_index[spec_id] = idx
            self.index_to_spec_id[idx] = spec_id

    def on_test_field_selected(self, row, col):
        """시나리오 선택 시 해당 결과 표시 (결과 없어도 API 정보 표시)"""

        if row not in self.index_to_spec_id:
            return

        selected_spec_id = self.index_to_spec_id[row]

        # 선택된 시나리오가 현재와 같으면 무시
        if selected_spec_id == self.current_spec_id:
            return

        print(f"[RESULT] 시나리오 전환: {self.current_spec_id} → {selected_spec_id}")
        print(f"[RESULT DEBUG] 현재 그룹: {self.parent.current_group_id}")

        # ✅ parent의 spec 전환 (API 목록 로드)
        old_spec_id = self.parent.current_spec_id
        old_step_buffers = self.parent.step_buffers.copy() if hasattr(self.parent, 'step_buffers') else []

        try:
            # ✅ 1. spec_id 업데이트
            self.parent.current_spec_id = selected_spec_id
            self.current_spec_id = selected_spec_id

            # ✅ 2. spec 데이터 다시 로드 (스키마, API 목록 등)
            self.parent.load_specs_from_constants()

            # ✅ 3. 설정 다시 로드 (웹훅 스키마 포함)
            self.parent.get_setting()

            print(f"[RESULT] API 개수: {len(self.parent.videoMessages)}")
            print(f"[RESULT] inSchema 개수: {len(self.parent.inSchema)}")
            print(f"[RESULT] webhookSchema 개수: {len(self.parent.webhookSchema)}")

            # ✅ 4. 저장된 결과 데이터가 있으면 로드 (복합키 사용)
            composite_key = f"{self.parent.current_group_id}_{selected_spec_id}"
            print(f"[RESULT DEBUG] 📂 데이터 복원 시도: {composite_key}")
            if composite_key in self.parent.spec_table_data:
                saved_data = self.parent.spec_table_data[composite_key]

                # step_buffers 복원
                saved_buffers = saved_data.get('step_buffers', [])
                if saved_buffers:
                    self.parent.step_buffers = [buf.copy() for buf in saved_buffers]
                    print(f"[RESULT] step_buffers 복원 완료: {len(self.parent.step_buffers)}개")
                else:
                    # 저장된 버퍼가 없으면 빈 버퍼 생성
                    api_count = len(self.parent.videoMessages)
                    self.parent.step_buffers = [
                        {"data": "저장된 데이터가 없습니다.", "error": "", "result": "PASS"}
                        for _ in range(api_count)
                    ]

                # 점수 정보 복원
                self.parent.total_pass_cnt = saved_data.get('total_pass_cnt', 0)
                self.parent.total_error_cnt = saved_data.get('total_error_cnt', 0)

                # ✅ step_pass_counts와 step_error_counts 배열 복원
                self.parent.step_pass_counts = saved_data.get('step_pass_counts', [0] * len(self.parent.videoMessages))[:]
                self.parent.step_error_counts = saved_data.get('step_error_counts', [0] * len(self.parent.videoMessages))[:]
                print(f"[RESULT] step_pass_counts 복원: {self.parent.step_pass_counts}")
                print(f"[RESULT] step_error_counts 복원: {self.parent.step_error_counts}")

                # 테이블 및 점수 표시 업데이트
                self.reload_result_table(saved_data)
                self.update_score_displays(saved_data)

                print(f"[RESULT] {selected_spec_id} 저장된 결과 로드 완료")
            else:
                # 결과가 없으면 빈 테이블 표시
                print(f"[RESULT] {selected_spec_id} 결과 없음 - 빈 테이블 표시")
                self.show_empty_result_table()

        except Exception as e:
            print(f"[ERROR] 시나리오 전환 실패: {e}")
            import traceback
            traceback.print_exc()

            # ✅ 복구 처리
            self.parent.current_spec_id = old_spec_id
            self.current_spec_id = old_spec_id
            if old_step_buffers:
                self.parent.step_buffers = old_step_buffers

            try:
                self.parent.load_specs_from_constants()
                self.parent.get_setting()
            except:
                pass

            QMessageBox.warning(self, "오류", f"시나리오 전환 중 오류가 발생했습니다.\n{str(e)}")

    def show_empty_result_table(self):
        """결과가 없을 때 빈 테이블 표시 (API 목록만)"""
        api_list = self.parent.videoMessages
        api_count = len(api_list)

        print(f"[RESULT] 빈 테이블 생성: {api_count}개 API")

        # ✅ step_buffers 초기화 (상세 내용 확인을 위해 필수!)
        self.parent.step_buffers = []
        for i in range(api_count):
            api_name = api_list[i] if i < len(api_list) else f"API {i + 1}"
            self.parent.step_buffers.append({
                "data": f"아직 시험이 진행되지 않았습니다.\n\nAPI: {api_name}",
                "error": "시험 데이터가 없습니다.",
                "result": "PASS"
            })

        print(f"[RESULT] step_buffers 생성 완료: {len(self.parent.step_buffers)}개")

        # ✅ 점수 정보 초기화
        self.parent.total_pass_cnt = 0
        self.parent.total_error_cnt = 0

        # 테이블 행 수 재설정
        self.tableWidget.setRowCount(api_count)

        for row in range(api_count):
            # API 명
            api_name = f"{row + 1}. {api_list[row]}"
            api_item = QTableWidgetItem(api_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)  # 가운데 정렬
            self.tableWidget.setItem(row, 0, api_item)

            # ✅ 기본 아이콘 (결과 페이지 전용 아이콘 사용)
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))  # icn_basic.png는 16x16
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 1, icon_widget)

            # 모든 값 0으로 초기화
            for col, value in [(2, "0"), (3, "0"), (4, "0"), (5, "0"), (6, "0%")]:
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # 상세 내용 버튼
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
            detail_label.mousePressEvent = lambda event, r=row: self._show_detail(r)

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 7, container)

        # 점수 표시도 0으로 업데이트
        empty_data = {
            'total_pass_cnt': 0,
            'total_error_cnt': 0
        }
        self.update_score_displays(empty_data)

    def reload_result_table(self, saved_data):
        """저장된 데이터로 결과 테이블 재구성"""
        table_data = saved_data.get('table_data', [])

        # 테이블 행 수 재설정
        self.tableWidget.setRowCount(len(table_data))

        for row, row_data in enumerate(table_data):
            # API 명
            api_item = QTableWidgetItem(row_data['api_name'])
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)  # 가운데 정렬
            self.tableWidget.setItem(row, 0, api_item)

            # ✅ 아이콘 상태 복원 (결과 페이지 전용 아이콘 사용)
            icon_state = row_data['icon_state']
            if icon_state == "PASS":
                img = self.img_pass
                icon_size = (84, 20)  # tag_성공.png
            elif icon_state == "FAIL":
                img = self.img_fail
                icon_size = (84, 20)  # tag_실패.png
            else:
                img = self.img_none
                icon_size = (16, 16)  # icn_basic.png

            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(img).pixmap(*icon_size))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setToolTip(f"Result: {icon_state}")  # tooltip 설정으로 재저장 시 상태 유지
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 1, icon_widget)

            # 나머지 컬럼 복원
            for col, key in [(2, 'retry_count'), (3, 'pass_count'),
                             (4, 'total_count'), (5, 'fail_count'), (6, 'score')]:
                item = QTableWidgetItem(row_data[key])
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # 상세 내용 버튼
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
            detail_label.mousePressEvent = lambda event, r=row: self._show_detail(r)

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 7, container)

    def _show_detail(self, row):
        """상세 내용 확인 - parent의 show_combined_result 호출"""
        try:
            self.parent.show_combined_result(row)
        except Exception as e:
            print(f"[ERROR] 상세 내용 확인 오류: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "오류", f"상세 내용을 표시할 수 없습니다.\n{str(e)}")

    def update_score_displays(self, saved_data):
        """점수 표시 업데이트"""
        total_pass = saved_data.get('total_pass_cnt', 0)
        total_error = saved_data.get('total_error_cnt', 0)
        total_fields = total_pass + total_error
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0

        # spec_score_group 재생성
        if hasattr(self, 'spec_score_group'):
            # 기존 위젯의 위치 기억
            parent_widget = self.spec_score_group.parent()
            if parent_widget:
                layout = parent_widget.layout()
                if layout:
                    idx = layout.indexOf(self.spec_score_group)
                    if idx >= 0:
                        layout.removeWidget(self.spec_score_group)
                        self.spec_score_group.deleteLater()
                        
                        # 새로운 점수 위젯 생성
                        self.spec_score_group = self._create_spec_score_display_with_data(
                            total_pass, total_error, score
                        )
                        # 같은 위치에 다시 삽입
                        layout.insertWidget(idx, self.spec_score_group)

        # ✅ 전체 점수 표시도 업데이트
        if hasattr(self, 'total_score_group'):
            # 기존 위젯의 위치 기억
            parent_widget = self.total_score_group.parent()
            if parent_widget:
                layout = parent_widget.layout()
                if layout:
                    idx = layout.indexOf(self.total_score_group)
                    if idx >= 0:
                        layout.removeWidget(self.total_score_group)
                        self.total_score_group.deleteLater()
                        
                        # 새로운 전체 점수 위젯 생성
                        self.total_score_group = self._create_total_score_display()
                        # 같은 위치에 다시 삽입
                        layout.insertWidget(idx, self.total_score_group)

    def _create_simple_info_display(self):
        """심플한 시험 정보 표시 (단일 텍스트, 테두리 유지)"""
        info_widget = QWidget()
        info_widget.setFixedSize(1064, 150)
        info_widget.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;   /* ✅ 테두리 유지 */
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # ✅ 시험 정보 불러오기
        test_info = self.parent.load_test_info_from_constants()

        # ✅ 시험 정보를 한 개의 문자열로 합치기
        info_text = "\n".join([f"{label}: {value}" for label, value in test_info])

        # ✅ 한 개의 라벨로 출력
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)  # 줄바꿈 자동 처리
        info_label.setFont(QFont("Noto Sans KR", 10))
        info_label.setStyleSheet("""
            color: #222;
            font-weight: 400;
            line-height: 1.8;
            border: none;
        """)

        layout.addWidget(info_label)
        layout.addStretch()
        info_widget.setLayout(layout)

        # ✅ 스크롤 영역 추가
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedSize(1064, 150)  # 기존과 동일한 전체 크기
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ✅ 스크롤바 스타일
        scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
            QScrollBar:vertical {
                border: none;
                background: #F1F1F1;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #C1C1C1;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        return scroll_area

    def create_result_table(self, parent_layout):
        """결과 테이블 생성 (크기 키움: 350px)"""
        api_count = self.parent.tableWidget.rowCount()
        self.tableWidget = QTableWidget(api_count, 8)
        self.tableWidget.setFixedHeight(274)
        self.tableWidget.setFixedWidth(1064)
        self.tableWidget.setHorizontalHeaderLabels([
            "API 명", "결과", "검증 횟수", "통과 필드 수",
            "전체 필드 수", "실패 필드 수", "평가 점수", "상세 내용"
        ])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # 테이블 스타일
        main_path = resource_path("assets/image/test_runner/main_table.png").replace("\\", "/")
        self.tableWidget.setStyleSheet(f"""
            QTableWidget {{
                background: #FFF;
                background-image: url('{main_path}');
                background-repeat: no-repeat;
                background-position: center;
                border-radius: 8px;
                border: 1px solid #CECECE;
                font-size: 15px;
                color: #222;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #E0E0E0;
                border-right: 0px solid transparent;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 14px;
                font-style: normal;
                font-weight: 400;
                letter-spacing: 0.098px;
            }}
            QHeaderView::section {{
                background-color: #EDF0F3;
                border-right: 0px solid transparent;
                border-left: 0px solid transparent;
                border-top: 0px solid transparent;
                border-bottom: 1px solid #CECECE;
                color: #1B1B1C;
                text-align: center;
                font-family: 'Noto Sans KR';
                font-size: 13px;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                letter-spacing: -0.156px;
            }}
        """)

        self.tableWidget.setShowGrid(False)

        # 컬럼 너비 설정
        self.tableWidget.setColumnWidth(0, 520)  # API 명 (546 → 520, -26px)
        self.tableWidget.setColumnWidth(1, 90)   # 결과 아이콘 (56 → 90, +34px)
        self.tableWidget.setColumnWidth(2, 62)
        self.tableWidget.setColumnWidth(3, 78)
        self.tableWidget.setColumnWidth(4, 78)
        self.tableWidget.setColumnWidth(5, 78)
        self.tableWidget.setColumnWidth(6, 62)
        self.tableWidget.setColumnWidth(7, 88)

        # 행 높이 설정
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 28)  # 28 → 32

        # parent 테이블 데이터 복사
        self._copy_table_data()

        # 상세 내용 버튼 클릭 이벤트
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)

        # ✅ QScrollArea로 감싸기
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.tableWidget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFixedWidth(1064)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
            QScrollBar:vertical {
                border: none;
                background: #F1F1F1;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #C1C1C1;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        parent_layout.addWidget(scroll_area)

    def _on_back_clicked(self):
        """뒤로가기 버튼 클릭 시 시그널 발생"""
        self.backRequested.emit()

    def _copy_table_data(self):
        """parent의 테이블 데이터를 복사 (결과 페이지 전용 아이콘 사용)"""
        api_count = self.parent.tableWidget.rowCount()
        for row in range(api_count):
            # API 명
            api_item = self.parent.tableWidget.item(row, 0)
            if api_item:
                new_item = QTableWidgetItem(api_item.text())
                new_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)  # 가운데 정렬
                self.tableWidget.setItem(row, 0, new_item)

            # ✅ 결과 아이콘 (결과 페이지 전용 아이콘으로 교체)
            icon_widget = self.parent.tableWidget.cellWidget(row, 1)
            if icon_widget:
                old_label = icon_widget.findChild(QLabel)
                if old_label:
                    # ✅ tooltip에서 결과 상태 추출
                    tooltip = old_label.toolTip()
                    
                    # ✅ 결과에 따라 결과 페이지 전용 아이콘 선택
                    if "Result: PASS" in tooltip:
                        img = self.img_pass  # tag_성공.png
                        icon_size = (84, 20)
                    elif "Result: FAIL" in tooltip:
                        img = self.img_fail  # tag_실패.png
                        icon_size = (84, 20)
                    else:
                        img = self.img_none  # icn_basic.png
                        icon_size = (16, 16)

                    new_icon_widget = QWidget()
                    new_icon_layout = QHBoxLayout()
                    new_icon_layout.setContentsMargins(0, 0, 0, 0)

                    new_icon_label = QLabel()
                    new_icon_label.setPixmap(QIcon(img).pixmap(*icon_size))
                    new_icon_label.setToolTip(tooltip)
                    new_icon_label.setAlignment(Qt.AlignCenter)

                    new_icon_layout.addWidget(new_icon_label)
                    new_icon_layout.setAlignment(Qt.AlignCenter)
                    new_icon_widget.setLayout(new_icon_layout)

                    self.tableWidget.setCellWidget(row, 1, new_icon_widget)

            # 나머지 컬럼들
            for col in range(2, 7):
                item = self.parent.tableWidget.item(row, col)
                if item:
                    new_item = QTableWidgetItem(item.text())
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(row, col, new_item)

            # 상세 내용 버튼
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
            detail_label.mousePressEvent = lambda event, r=row: self._show_detail(r)

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 7, container)

    def _create_spec_score_display(self):
        """시험 분야별 점수 표시"""
        spec_description = self.parent.spec_description
        api_count = len(self.parent.videoMessages)
        total_pass = self.parent.total_pass_cnt
        total_error = self.parent.total_error_cnt
        total_fields = total_pass + total_error
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0

        return self._create_spec_score_display_with_data(total_pass, total_error, score)

    def _create_spec_score_display_with_data(self, total_pass, total_error, score):
        """데이터를 받아서 점수 표시 위젯 생성"""
        spec_group = QGroupBox()
        spec_group.setFixedWidth(1064)
        spec_group.setFixedHeight(106)
        spec_group.setStyleSheet("""
            QGroupBox {
                background-color: #FFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)

        # 분야별 점수 아이콘
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_분야별점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)

        # spec 정보 가져오기
        spec_description = self.parent.spec_description
        api_count = len(self.parent.videoMessages)
        total_fields = total_pass + total_error

        # 분야명 레이블
        spec_name_label = QLabel(f"분야별 점수      |      {spec_description} ({api_count}개 API)")
        spec_name_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)

        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet("QFrame { color: #CECECE; background-color: #CECECE; }")
        separator.setFixedHeight(1)

        # 점수 레이블들
        pass_label = QLabel(
            f"통과 필드 수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
            f"{total_pass}</span>"
        )
        total_label = QLabel(
            f"전체 필드 수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
            f"{total_fields}</span>"
        )
        score_label = QLabel(
            f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
            f"{score:.1f}%</span>"
        )

        for lbl in [pass_label, total_label, score_label]:
            lbl.setStyleSheet("""
                color: #000;
                font-family: "Noto Sans KR";
                font-size: 15px;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                letter-spacing: -0.18px;
            """)

        # 레이아웃 구성
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 15, 32, 15)

        icon_vlayout = QVBoxLayout()
        icon_vlayout.setContentsMargins(0, 0, 0, 0)
        icon_vlayout.setSpacing(0)
        icon_vlayout.addSpacing(0)
        icon_vlayout.addWidget(icon_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
        icon_vlayout.addStretch()

        header_layout = QHBoxLayout()
        header_layout.addLayout(icon_vlayout)
        header_layout.addWidget(spec_name_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(5)
        main_layout.addWidget(separator)
        main_layout.addSpacing(5)

        score_layout = QHBoxLayout()
        score_layout.setSpacing(260)
        score_layout.addWidget(pass_label)
        score_layout.addWidget(total_label)
        score_layout.addWidget(score_label)
        score_layout.addStretch()

        main_layout.addLayout(score_layout)
        spec_group.setLayout(main_layout)
        return spec_group

    def _create_total_score_display(self):
        """전체 점수 표시"""
        total_group = QGroupBox()
        total_group.setFixedWidth(1064)
        total_group.setFixedHeight(106)
        total_group.setStyleSheet("""
            QGroupBox {
                background-color: #F0F6FB;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)

        # 전체 점수 아이콘
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_전체점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(40, 40)

        # ✅ 현재 시나리오의 점수 사용 (시나리오별 점수)
        total_pass = self.parent.total_pass_cnt
        total_error = self.parent.total_error_cnt
        total_fields = total_pass + total_error
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0

        # 전체 점수 레이블
        total_name_label = QLabel("전체 점수 (모든 시험 분야 합산)")
        total_name_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)

        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet("QFrame { color: #CECECE; background-color: #CECECE; }")
        separator.setFixedHeight(1)

        pass_label = QLabel(
            f"통과 필드 수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
            f"{total_pass}</span>"
        )
        total_label = QLabel(
            f"전체 필드 수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
            f"{total_fields}</span>"
        )
        score_label = QLabel(
            f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
            f"{score:.1f}%</span>"
        )

        for lbl in [pass_label, total_label, score_label]:
            lbl.setStyleSheet("""
                color: #000;
                font-family: "Noto Sans KR";
                font-size: 15px;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                letter-spacing: -0.18px;
            """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 15, 32, 15)

        icon_vlayout = QVBoxLayout()
        icon_vlayout.setContentsMargins(0, 0, 0, 0)
        icon_vlayout.setSpacing(0)
        icon_vlayout.addSpacing(0)
        icon_vlayout.addWidget(icon_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
        icon_vlayout.addStretch()

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        header_layout.addLayout(icon_vlayout)
        header_layout.addWidget(total_name_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        main_layout.addSpacing(5)
        main_layout.addWidget(separator)
        main_layout.addSpacing(5)

        layout = QHBoxLayout()
        layout.setSpacing(260)
        layout.addWidget(pass_label)
        layout.addWidget(total_label)
        layout.addWidget(score_label)
        layout.addStretch()

        main_layout.addLayout(layout)
        total_group.setLayout(main_layout)
        return total_group

    def table_cell_clicked(self, row, col):
        """상세 내용 버튼 클릭 시"""
        if col == 7:
            self._show_detail(row)


class MyApp(QWidget):
    # 시험 결과 표시 요청 시그널
    showResultRequested = pyqtSignal(object)

    def _load_from_trace_file(self, api_name, direction="RESPONSE"):
        """trace 파일에서 특정 API의 RESPONSE 데이터를 읽어옴"""
        try:
            # API 이름에서 슬래시 제거
            api_name_clean = api_name.lstrip("/")
            
            # 번호 prefix 제거 (예: "01_Authentication" -> "Authentication")
            # 패턴: 숫자로 시작하고 '_'가 있는 경우
            import re
            api_name_no_prefix = re.sub(r'^\d+_', '', api_name_clean)
            
            # print(f"[DEBUG] trace 파일 찾기: 원본={api_name}, 정제={api_name_clean}, prefix제거={api_name_no_prefix}")
            
            # ✅ 실제 trace 폴더에서 매칭되는 파일 찾기
            trace_folder = Path("results/trace")
            trace_file = None
            
            if trace_folder.exists():
                # 가능한 파일명 패턴들
                possible_patterns = [
                    f"trace_{api_name_clean}.ndjson",  # trace_CameraProfiles.ndjson
                    f"trace_{api_name_no_prefix}.ndjson",  # 동일하면 중복이지만 안전장치
                ]
                
                # 실제 파일 목록에서 검색
                for ndjson_file in trace_folder.glob("trace_*.ndjson"):
                    file_name = ndjson_file.name
                    # trace_03_CameraProfiles.ndjson → 03_CameraProfiles
                    api_part = file_name.replace("trace_", "").replace(".ndjson", "")
                    
                    # prefix 제거하고 비교 (03_CameraProfiles → CameraProfiles)
                    api_part_no_prefix = re.sub(r'^\d+_', '', api_part)
                    
                    # 매칭 확인
                    if api_part == api_name_clean or api_part_no_prefix == api_name_no_prefix:
                        trace_file = ndjson_file
                        print(f"[DEBUG] ✅ 매칭 성공: {file_name} (검색어: {api_name_clean})")
                        break
            
            if trace_file is None or not trace_file.exists():
                print(f"[DEBUG] trace 파일 없음 (검색어: {api_name_clean})")
                return None

            latest_data = None

            with open(trace_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        
                        # direction만 확인 (api는 이미 파일명으로 필터링됨)
                        if entry.get('dir') == direction:
                            latest_data = entry.get('data', {})
                            # 계속 읽어서 가장 마지막 데이터를 가져옴

                    except json.JSONDecodeError:
                        continue

            if latest_data:
                print(f"[DEBUG] trace 파일에서 {api_name} {direction} 로드 완료: {len(str(latest_data))} bytes")
                return latest_data
            else:
                print(f"[DEBUG] trace 파일에 {api_name} {direction} 없음")
                return None

        except Exception as e:
            print(f"[ERROR] trace 파일 로드 실패: {e}")
            import traceback
            traceback.print_exc()
            return None

    def __init__(self, embedded=False, mode=None, spec_id=None):
        # CONSTANTS 사용
        super().__init__()

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
            print(f"[PLATFORM] 📌 전달받은 spec_id 사용: {spec_id}")

        # Load specs dynamically from CONSTANTS

        self.initUI()
        self.realtime_flag = False
        self.cnt = 0
        self.current_retry = 0

        # ✅ 분야별 점수 (현재 spec만)
        self.current_retry = 0
        self.total_error_cnt = 0
        self.total_pass_cnt = 0

        # ✅ 전체 점수 (모든 spec 합산)
        self.global_pass_cnt = 0
        self.global_error_cnt = 0

        # ✅ 각 spec_id별 테이블 데이터 저장 (시나리오 전환 시 결과 유지)
        self.spec_table_data = {}  # {spec_id: {table_data, step_buffers, scores}}

        self.time_pre = 0
        self.cnt_pre = 0
        self.final_report = ""

        # step_buffers 동적 생성
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS", "raw_data_list": []} for _ in range(len(self.videoMessages))
        ]

        self.get_setting()
        self.first_run = True

        with open(resource_path("spec/rows.json"), "w") as out_file:
            json.dump(None, out_file, ensure_ascii=False)

        self.reference_context = {}

    def load_specs_from_constants(self):
        """SPEC_CONFIG 기반으로 spec 데이터 동적 로드"""
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
                print(f"[PLATFORM] 외부 CONSTANTS.py에서 SPEC_CONFIG 로드: {external_constants_path}")
                try:
                    # 외부 파일 읽어서 SPEC_CONFIG만 추출
                    with open(external_constants_path, 'r', encoding='utf-8') as f:
                        constants_code = f.read()

                    # SPEC_CONFIG만 추출하기 위해 exec 실행
                    namespace = {'__file__': external_constants_path}
                    exec(constants_code, namespace)
                    SPEC_CONFIG = namespace.get('SPEC_CONFIG', SPEC_CONFIG)
                    url_value = namespace.get('url', url_value)
                    auth_type = namespace.get('auth_type', auth_type)
                    auth_info = namespace.get('auth_info', auth_info)
                    self.CONSTANTS.company_name = namespace.get('company_name', self.CONSTANTS.company_name)
                    self.CONSTANTS.product_name = namespace.get('product_name', self.CONSTANTS.product_name)
                    self.CONSTANTS.version = namespace.get('version', self.CONSTANTS.version)
                    self.CONSTANTS.test_category = namespace.get('test_category', self.CONSTANTS.test_category)
                    self.CONSTANTS.test_target = namespace.get('test_target', self.CONSTANTS.test_target)
                    self.CONSTANTS.test_range = namespace.get('test_range', self.CONSTANTS.test_range)
                    print(f"[PLATFORM] ✅ 외부 SPEC_CONFIG 로드 완료: {len(SPEC_CONFIG)}개 그룹")
                    # 디버그: 그룹 이름 출력
                    for i, g in enumerate(SPEC_CONFIG):
                        group_name = g.get('group_name', '이름없음')
                        group_keys = [k for k in g.keys() if k not in ['group_name', 'group_id']]
                        print(f"[PLATFORM DEBUG] 그룹 {i}: {group_name}, spec_id 개수: {len(group_keys)}, spec_ids: {group_keys}")
                except Exception as e:
                    print(f"[PLATFORM] ⚠️ 외부 CONSTANTS 로드 실패, 기본값 사용: {e}")
        # ===== 외부 CONSTANTS 로드 끝 =====

        # ===== 인스턴스 변수에 저장 (다른 메서드에서 사용) =====
        self.LOADED_SPEC_CONFIG = SPEC_CONFIG
        self.url = url_value  # ✅ 외부 CONSTANTS.py에 정의된 url도 반영
        self.auth_type = auth_type
        self.auth_info = auth_info
        # ===== 저장 완료 =====

        if not SPEC_CONFIG:
            raise ValueError("CONSTANTS.SPEC_CONFIG가 정의되지 않았습니다!")

        print(f"[PLATFORM DEBUG] SPEC_CONFIG 개수: {len(SPEC_CONFIG)}")
        print(f"[PLATFORM DEBUG] 찾을 spec_id: {self.current_spec_id}")

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

        print(f"[PLATFORM] 📋 Spec 로딩 시작: {self.spec_description} (ID: {self.current_spec_id})")

        print(f"[PLATFORM] 📁 모듈: spec (센서/바이오/영상 통합)")

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
            print(f"[PLATFORM SPEC DEBUG] 외부 spec 폴더: {external_spec_dir}")
            print(f"[PLATFORM SPEC DEBUG] 외부 spec 폴더 존재: {os.path.exists(external_spec_dir)}")
            if os.path.exists(external_spec_dir):
                files = [f for f in os.listdir(external_spec_dir) if f.endswith('.py')]
                print(f"[PLATFORM SPEC DEBUG] 외부 spec 폴더 .py 파일: {files}")

            # sys.path 전체 출력 (디버깅)
            print(f"[PLATFORM SPEC DEBUG] sys.path 전체 개수: {len(sys.path)}")
            for i, p in enumerate(sys.path):
                print(f"[PLATFORM SPEC DEBUG]   [{i}] {p}")

            # 이미 있더라도 제거 후 맨 앞에 추가 (우선순위 보장)
            if external_spec_parent in sys.path:
                sys.path.remove(external_spec_parent)
            sys.path.insert(0, external_spec_parent)
            print(f"[PLATFORM SPEC] sys.path에 외부 디렉토리 추가: {external_spec_parent}")

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
                print(f"[PLATFORM SPEC] 모듈 캐시 삭제: {mod_name}")
            else:
                print(f"[PLATFORM SPEC] 모듈 캐시 없음: {mod_name}")

        # spec 패키지가 없으면 빈 모듈로 등록
        if 'spec' not in sys.modules:
            import types
            sys.modules['spec'] = types.ModuleType('spec')
            print(f"[PLATFORM SPEC] 빈 'spec' 패키지 생성")

        # PyInstaller 환경에서는 importlib.util로 명시적으로 외부 파일 로드
        if getattr(sys, 'frozen', False):
            import importlib.util

            # 외부 spec 파일 경로
            schema_file = os.path.join(exe_dir, 'spec', 'Schema_request.py')
            data_file = os.path.join(exe_dir, 'spec', 'Data_response.py')
            constraints_file = os.path.join(exe_dir, 'spec', 'Constraints_response.py')

            print(f"[PLATFORM SPEC] 명시적 로드 시도:")
            print(f"  - Schema: {schema_file} (존재: {os.path.exists(schema_file)})")
            print(f"  - Data: {data_file} (존재: {os.path.exists(data_file)})")
            print(f"  - Constraints: {constraints_file} (존재: {os.path.exists(constraints_file)})")

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

            print(f"[PLATFORM SPEC] ✅ importlib.util로 외부 파일 로드 완료")
        else:
            # 일반 환경에서는 기존 방식 사용
            import spec.Schema_request as schema_request_module
            import spec.Data_response as data_response_module
            import spec.Constraints_response as constraints_response_module

        # ===== spec 파일 경로 로그 추가 =====
        print(f"[PLATFORM SPEC] Schema_request.py 로드 경로: {schema_request_module.__file__}")
        print(f"[PLATFORM SPEC] Data_response.py 로드 경로: {data_response_module.__file__}")
        print(f"[PLATFORM SPEC] Constraints_response.py 로드 경로: {constraints_response_module.__file__}")

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
                print(f"[PLATFORM SPEC] {name}.py 수정 시간: {mtime_str}")
        # ===== 로그 끝 =====
        print(f"[PLATFORM] 🔧 타입: 요청 검증 + 응답 전송")

        # Request 검증용 데이터 로드
        self.videoInSchema = getattr(schema_request_module, spec_names[0], [])

        # Response 전송용 데이터 로드
        self.videoOutMessage = getattr(data_response_module, spec_names[1], [])
        self.videoMessages = getattr(data_response_module, spec_names[2], [])
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

                print(f"[PLATFORM] 📦 웹훅 스키마 개수: {len(self.videoWebhookSchema)}개 API")
                print(f"[PLATFORM] 📋 웹훅 데이터 개수: {len(self.videoWebhookData)}개")
                print(f"[PLATFORM] 📋 웹훅 constraints 개수: {len(self.videoWebhookConstraint)}개")

                webhook_indices = [i for i, msg in enumerate(self.videoMessages) if "Webhook" in msg]
                if webhook_indices:
                    print(f"[PLATFORM] 🔔 웹훅 API 인덱스: {webhook_indices}")
                else:
                    print(f"[PLATFORM] ⚠️ 웹훅 API가 videoMessages에 없습니다.")
            else:
                print(f"[PLATFORM] ⚠️ 웹훅 스키마 및 데이터가 SPEC_CONFIG에 정의되어 있지 않습니다.")
                self.videoWebhookSchema = []
                self.videoWebhookData = []
                self.videoWebhookConstraint = []
        except Exception as e:
            print(f"[PLATFORM] ⚠️ 웹훅 스키마 및 데이터 로드 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            self.videoWebhookSchema = []
            self.videoWebhookData = []
            self.videoWebhookConstraint = []

        print(f"[PLATFORM] ✅ 로딩 완료: {len(self.videoMessages)}개 API")
        print(f"[PLATFORM] 📋 API 목록: {self.videoMessages}")
        print(f"[PLATFORM] 🔄 프로토콜 설정: {self.trans_protocols}")

        # ✅ spec_config 저장 (URL 생성에 필요)
        self.spec_config = config

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
                from collections import defaultdict, deque
                self.Server.trace = defaultdict(lambda: deque(maxlen=500))
            if api_name not in self.Server.trace:
                from collections import deque
                self.Server.trace[api_name] = deque(maxlen=500)
            evt = {
                "time": datetime.utcnow().isoformat() + "Z",
                "api": api_name,
                "dir": direction,
                "data": self._redact(payload),
            }
            self.Server.trace[api_name].append(evt)
        except Exception:
            pass

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
        if row >= self.tableWidget.rowCount():
            return

        # 아이콘 업데이트
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

        # 메시지 저장
        setattr(self, f"step{row + 1}_msg", msg)

    def update_view(self):
        try:
            time_interval = 0

            if self.cnt >= len(self.Server.message):
                print(f"[DEBUG] 모든 API 처리 완료, 타이머 정지")
                self.tick_timer.stop()

                # ✅ 현재 spec 데이터 저장
                self.save_current_spec_data()

                self.sbtn.setEnabled(True)
                self.stop_btn.setDisabled(True)

                # ✅ 완료 메시지 추가
                self.valResult.append("\n" + "=" * 50)
                self.valResult.append("🎉 모든 API 검증이 완료되었습니다!")
                self.valResult.append("=" * 50)

                # ✅ 자동 저장
                try:
                    self.run_status = "완료"
                    result_json = build_result_json(self)
                    url = f"{CONSTANTS.management_url}/api/integration/test-results"
                    response = requests.post(url, json=result_json)
                    print("✅ 시험 결과 전송 상태 코드:", response.status_code)
                    print("📥  시험 결과 전송 응답:", response.text)

                    json_path = os.path.join(result_dir, "request_results.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result_json, f, ensure_ascii=False, indent=2)
                    print(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                    self.valResult.append(f"\n📄 결과 파일 저장 완료: {json_path}")
                except Exception as e:
                    print(f"❌ JSON 저장 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    self.valResult.append(f"\n⚠️ 결과 저장 실패: {str(e)}")

                return

            # 첫 틱에서는 대기만
            if self.time_pre == 0 or self.cnt != self.cnt_pre:
                print(f"[DEBUG] 첫 틱 대기: time_pre={self.time_pre}, cnt={self.cnt}, cnt_pre={self.cnt_pre}")
                self.time_pre = time.time()
                self.cnt_pre = self.cnt
                return
            else:
                time_interval = time.time() - self.time_pre
                print(f"[DEBUG] 시간 간격: {time_interval}초")

            if self.realtime_flag is True:
                print(f"[json_check] do_checker 호출")

            # SPEC_CONFIG에서 timeout
            current_timeout = (self.time_outs[self.cnt] / 1000) if self.cnt < len(self.time_outs) else 5.0

            # timeout이 0인 경우
            if current_timeout == 0 or time_interval < current_timeout:
                # 시스템 요청 확인
                api_name = self.Server.message[self.cnt]
                print(f"[DEBUG] API 처리 시작: {api_name}")
               #  print(f"[DEBUG] cnt={self.cnt}, current_retry={self.current_retry}")

                current_validation = {}

                print("++++++++++ 규칙 가져오기 ++++++++++")

                try:
                    current_validation = get_validation_rules(
                        spec_id=self.current_spec_id,
                        api_name=api_name,
                        direction="in",
                    ) or {}
                    if current_validation:
                        print(f"[DEBUG] 현재 API의 검증 규칙 로드 완료: {list(current_validation.keys())}")
                except Exception as e:
                    current_validation = {}
                    print(f"[DEBUG] 현재 API의 검증 규칙 로드 실패: {e}")

                print("++++++++++ 규칙 로드 끝 ++++++++++")

                request_received = False
                expected_count = self.current_retry + 1
                actual_count = 0

                # Server 클래스 변수 request_counter 확인
                if hasattr(self.Server, 'request_counter') and api_name in self.Server.request_counter:
                    actual_count = self.Server.request_counter[api_name]
                    print(f"[DEBUG] API: {api_name}, 예상: {expected_count}, 실제: {actual_count}")
                    if actual_count >= expected_count:
                        request_received = True

                # 요청이 도착하지 않았으면 대기
                if not request_received:
                    if self.current_retry == 0:
                        print(
                            f"[TIMING_DEBUG] ✅ 능동 대기(WAIT): 시스템 요청 대기 중 (API: {api_name}, 예상: {expected_count}회, 실제: {actual_count}회)")
                    return

                request_arrival_time = time.time()
                expected_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                print(f"[TIMING_DEBUG] ✅ 요청 도착 감지! API: {api_name}, 시도: {self.current_retry + 1}/{expected_retries}")

                message_name = "step " + str(self.cnt + 1) + ": " + self.Server.message[self.cnt]

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
                        'raw_data_list': []
                    }

                accumulated = self.api_accumulated_data[api_index]

                retry_attempt = self.current_retry

                combined_error_parts = []
                step_result = "PASS"
                add_pass = 0
                add_err = 0

                # 실시간 진행률 표시
                if retry_attempt == 0:
                    self.valResult.append(message_name)
                    self.valResult.append(f"🔄 부하테스트 시작: 총 {current_retries}회 검증 예정")

                print(
                    f"[PLATFORM] 시스템 요청 수신: {self.Server.message[self.cnt]} (시도 {retry_attempt + 1}/{current_retries})")

                self.valResult.append(f"📨 시스템 요청 수신, 검증 중... [{retry_attempt + 1}/{current_retries}]")

                # 테이블에 실시간 진행률 표시
                self.update_table_row_with_retries(self.cnt, "진행중", 0, 0, "검증 진행중...",
                                                   f"시도 {retry_attempt + 1}/{current_retries}", retry_attempt + 1)

                QApplication.processEvents()

                # 1. request 검증용 데이터 로드
                # print(f"[DATA LOAD] API: {api_name}, 시도: {retry_attempt + 1}/{current_retries}")
                # print(f"[DATA LOAD] trace 폴더 확인: {list(Path('results/trace').glob('*.ndjson')) if Path('results/trace').exists() else '폴더 없음'}")
                
                current_data = self._load_from_trace_file(api_name, "REQUEST") or {}
                
                if not current_data:
                    print(f"[WARNING] ⚠️ trace 파일에서 데이터를 불러오지 못했습니다!")
                    print(f"[WARNING] API 이름: {api_name}")
                    print(f"[WARNING] Direction: REQUEST")
                else:
                    print(f"[SUCCESS] ✅ trace 파일에서 데이터 로드 완료: {len(str(current_data))} bytes")

                # 2. 맥락 검증용
                if current_validation:
                    # print("=" * 50)
                    # print("★★★ reference_context 채우기 시작!")
                    # print("=" * 50)

                    for field_path, validation_rule in current_validation.items():
                        validation_type = validation_rule.get("validationType", "")
                        direction = "REQUEST" if "request-field" in validation_type else "RESPONSE"

                        # print(f"★★★ field={field_path}")
                        # print(f"★★★ validationType={validation_type}")
                        # print(f"★★★ direction={direction}")

                        ref_endpoint = validation_rule.get("referenceEndpoint", "")
                        if ref_endpoint:
                            ref_api_name = ref_endpoint.lstrip("/")
                            ref_data = self._load_from_trace_file(ref_api_name, direction)
                            if ref_data and isinstance(ref_data, dict):
                                self.reference_context[ref_endpoint] = ref_data
                                print(f"[TRACE] {ref_endpoint} {direction}를 trace 파일에서 로드 (from validation rule)")

                        ref_endpoint_max = validation_rule.get("referenceEndpointMax", "")
                        if ref_endpoint_max:
                            ref_api_name_max = ref_endpoint_max.lstrip("/")
                            ref_data_max = self._load_from_trace_file(ref_api_name_max, direction)
                            if ref_data_max and isinstance(ref_data_max, dict):
                                self.reference_context[ref_endpoint_max] = ref_data_max
                                # print(f"★★★ 저장완료: {ref_endpoint_max} → {direction} 데이터")
                                print(f"[TRACE] {ref_endpoint_max} {direction}를 trace 파일에서 로드 (from validation rule)")

                        ref_endpoint_min = validation_rule.get("referenceEndpointMin", "")
                        if ref_endpoint_min:
                            ref_api_name_min = ref_endpoint_min.lstrip("/")
                            ref_data_min = self._load_from_trace_file(ref_api_name_min, direction)
                            if ref_data_min and isinstance(ref_data_min, dict):
                                self.reference_context[ref_endpoint_min] = ref_data_min
                                print(f"[TRACE] {ref_endpoint_min} {direction}를 trace 파일에서 로드 (from validation rule)")

                if self.Server.message[self.cnt] in CONSTANTS.none_request_message:
                    # 매 시도마다 데이터 수집
                    tmp_res_auth = json.dumps(current_data, indent=4, ensure_ascii=False)
                    if retry_attempt == 0:
                        accumulated['data_parts'].append(f"[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")
                    else:
                        accumulated['data_parts'].append(f"\n[시도 {retry_attempt + 1}회차]\n{tmp_res_auth}")

                    accumulated['raw_data_list'].append(current_data)

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

                    accumulated['raw_data_list'].append(current_data)

                    try:
                        print(f"[DEBUG] json_check_ 호출 시작")

                        val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(
                            self.videoInSchema[self.cnt],
                            current_data,
                            self.flag_opt,
                            validation_rules=current_validation,
                            reference_context=self.reference_context
                        )

                        print(
                            f"[DEBUG] json_check_ 성공: result={val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
                    except TypeError as e:
                        print(f"[DEBUG] TypeError 발생, 맥락 검증 제외 하고 다시 시도: {e}")
                        val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(
                            self.videoInSchema[self.cnt],
                            current_data,
                            self.flag_opt
                        )

                    except Exception as e:
                        print(f"[DEBUG] json_check_ 기타 에러: {e}")
                        import traceback
                        traceback.print_exc()
                        raise

                    add_pass += key_psss_cnt
                    add_err += key_error_cnt

                    inbound_err_txt = self._to_detail_text(val_text)
                    if val_result == "FAIL":
                        step_result = "FAIL"
                        combined_error_parts.append(f"[검증 {retry_attempt + 1}회차] [Inbound]\n" + inbound_err_txt)

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
                        if hasattr(self.Server, 'webhook_response') and self.Server.webhook_response:
                            webhook_response = self.Server.webhook_response
                            tmp_webhook_response = json.dumps(webhook_response, indent=4, ensure_ascii=False)
                            accumulated['data_parts'].append(
                                f"\n--- Webhook 응답 (시도 {retry_attempt + 1}회차) ---\n{tmp_webhook_response}")
                            if self.cnt < len(self.step_buffers):
                                self.step_buffers[self.cnt]["is_webhook_api"] = True
                            # 웹훅 응답 검증
                            if len(self.videoWebhookSchema) > 0:
                                webhook_resp_val_result, webhook_resp_val_text, webhook_resp_key_psss_cnt, webhook_resp_key_error_cnt = json_check_(
                                    self.videoWebhookSchema[0], webhook_response, self.flag_opt
                                )

                                add_pass += webhook_resp_key_psss_cnt
                                add_err += webhook_resp_key_error_cnt

                                webhook_resp_err_txt = self._to_detail_text(webhook_resp_val_text)
                                if webhook_resp_val_result == "FAIL":
                                    step_result = "FAIL"
                                    combined_error_parts.append(f"--- Webhook 검증 ---\n" + webhook_resp_err_txt)
                        else:
                            accumulated['data_parts'].append(f"\n--- Webhook 응답 ---\nnull")

                    # LongPolling 프로토콜인 경우
                    elif current_protocol == "LongPolling":
                        if retry_attempt == 0:
                            print(f"[LongPolling] 실시간 데이터 수신 대기 중... (API: {api_name})")
                        pass

                # 이번 회차 결과를 누적 데이터에 저장
                accumulated['validation_results'].append(step_result)
                accumulated['error_messages'].extend(combined_error_parts)
                # ✅ 필드 수는 마지막 시도로 덮어쓰기 (누적 X)
                accumulated['total_pass'] = add_pass
                accumulated['total_error'] = add_err

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
                    
                    # 이번 API의 결과 저장
                    self.step_pass_counts[self.cnt] = accumulated['total_pass']
                    self.step_error_counts[self.cnt] = accumulated['total_error']

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

                    # 모니터링 창에 최종 결과 표시
                    self.valResult.append(f"\n✅ 부하테스트 완료: {current_retries}회 검증 완료")
                    self.valResult.append(f"프로토콜: {current_protocol}")
                    self.valResult.append("\n" + data_text)
                    self.valResult.append(final_result)

                    # ✅ 전체 누적 점수 업데이트 (모든 spec) - API당 1회만 추가
                    self.global_error_cnt += accumulated['total_error']
                    self.global_pass_cnt += accumulated['total_pass']

                    self.update_score_display()

                    # ✅ 점수 계산은 step_pass_counts 배열의 합으로 (누적 아님!)
                    total_fields = self.total_pass_cnt + self.total_error_cnt
                    if total_fields > 0:
                        score_text = str((self.total_pass_cnt / total_fields * 100))
                    else:
                        score_text = "0"

                    self.valResult.append("Score : " + score_text)
                    self.valResult.append(
                        "Score details : " + str(self.total_pass_cnt) + "(통과 필드 수), " + str(
                            self.total_error_cnt) + "(오류 필드 수)\n")

                    self.cnt += 1
                    self.current_retry = 0

                    if CONSTANTS.enable_retry_delay:
                        print(
                            f"[TIMING_DEBUG] ⚠️ 수동 지연(SLEEP): API 완료 후 2초 대기 추가")
                        self.time_pre = time.time()
                    else:
                        print(
                            f"[TIMING_DEBUG] ✅ 수동 지연 비활성화: API 완료, 다음 시스템 요청 대기")
                        self.time_pre = time.time()
                else:
                    # 재시도인 경우
                    if CONSTANTS.enable_retry_delay:
                        print(
                            f"[TIMING_DEBUG] ⚠️ 수동 지연(SLEEP): 재시도 후 2초 대기 추가")
                        self.time_pre = time.time()
                    else:
                        print(
                            f"[TIMING_DEBUG] ✅ 수동 지연 비활성화: 재시도 완료, 다음 시스템 요청 대기")
                        self.time_pre = time.time()

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

                # ✅ 전체 점수에도 반영
                self.global_error_cnt += tmp_fields_rqd_cnt
                if tmp_fields_rqd_cnt == 0:
                    self.global_error_cnt += 1
                if self.flag_opt:
                    self.global_error_cnt += tmp_fields_opt_cnt

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

                current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                self.update_table_row_with_retries(self.cnt, "FAIL", 0, add_err, "", "Message Missing!",
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

                # ✅ 현재 spec 데이터 저장
                self.save_current_spec_data()

                # ✅ 자동 저장
                try:
                    self.run_status = "완료"
                    result_json = build_result_json(self)
                    url = f"{CONSTANTS.management_url}/api/integration/test-results"
                    response = requests.post(url, json=result_json)
                    print("✅ 시험 결과 전송 상태 코드:", response.status_code)
                    print("📥  시험 결과 전송 응답:", response.text)

                    json_path = os.path.join(result_dir, "request_results.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result_json, f, ensure_ascii=False, indent=2)
                    print(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                    self.valResult.append(f"\n📄 결과 파일 저장 완료: {json_path}")
                except Exception as e:
                    print(f"❌ JSON 저장 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    self.valResult.append(f"\n⚠️ 결과 저장 실패: {str(e)}")

        except Exception as err:
            print(f"[ERROR] update_view에서 예외 발생: {err}")
            import traceback
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
        if not (hasattr(self, "spec_pass_label") and hasattr(self, "spec_total_label") and hasattr(self,
                                                                                                   "spec_score_label")):
            return

        # ✅ 분야별 점수 제목 업데이트 (시나리오 명 변경 반영)
        if hasattr(self, "spec_name_label"):
            self.spec_name_label.setText(f"분야별 점수      |      {self.spec_description} ({len(self.videoMessages)}개 API)")

        # ✅ 1️⃣ 분야별 점수 (현재 spec만) - step_pass_counts 배열의 합으로 계산
        if hasattr(self, 'step_pass_counts') and hasattr(self, 'step_error_counts'):
            self.total_pass_cnt = sum(self.step_pass_counts)
            self.total_error_cnt = sum(self.step_error_counts)
            print(f"[SCORE UPDATE] step_pass_counts: {self.step_pass_counts}, sum: {self.total_pass_cnt}")
            print(f"[SCORE UPDATE] step_error_counts: {self.step_error_counts}, sum: {self.total_error_cnt}")

        spec_total_fields = self.total_pass_cnt + self.total_error_cnt
        if spec_total_fields > 0:
            spec_score = (self.total_pass_cnt / spec_total_fields) * 100
        else:
            spec_score = 0

        self.spec_pass_label.setText(
            f"통과 필드 수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
            f"{self.total_pass_cnt}</span>"
        )
        self.spec_total_label.setText(
            f"전체 필드 수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
            f"{spec_total_fields}</span>"
        )
        self.spec_score_label.setText(
            f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
            f"{spec_score:.1f}%</span>"
        )

        # ✅ 2️⃣ 전체 점수 (모든 spec 합산)
        if hasattr(self, "total_pass_label") and hasattr(self, "total_total_label") and hasattr(self,
                                                                                                "total_score_label"):
            global_total_fields = self.global_pass_cnt + self.global_error_cnt
            if global_total_fields > 0:
                global_score = (self.global_pass_cnt / global_total_fields) * 100
            else:
                global_score = 0

            self.total_pass_label.setText(
                f"통과 필드 수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
                f"{self.global_pass_cnt}</span>"
            )
            self.total_total_label.setText(
                f"전체 필드 수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
                f"{global_total_fields}</span>"
            )
            self.total_score_label.setText(
                f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 20px; font-style: Medium; color: #000000; margin-left: 20px;'>"
                f"{global_score:.1f}%</span>"
            )

    def icon_update_step(self, auth_, result_, text_):
        if result_ == "PASS":
            msg = auth_ + "\n\n" + "Result: PASS" + "\n" + text_ + "\n"
            img = self.img_pass
        elif result_ == "진행중":
            msg = auth_ + "\n\n" + "Status: " + text_ + "\n"
            img = self.img_none
        else:
            msg = auth_ + "\n\n" + "Result: FAIL" + "\nResult details:\n" + text_ + "\n"
            img = self.img_fail
        return msg, img

    def icon_update(self, tmp_res_auth, val_result, val_text):
        msg, img = self.icon_update_step(tmp_res_auth, val_result, val_text)

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

        if self.cnt < self.tableWidget.rowCount():
            self.tableWidget.setCellWidget(self.cnt, 1, icon_widget)
            setattr(self, f"step{self.cnt + 1}_msg", msg)

    def _toggle_placeholder(self):
        """텍스트 유무에 따라 placeholder 표시/숨김"""
        if hasattr(self, 'placeholder_label'):
            if self.valResult.toPlainText().strip():
                self.placeholder_label.hide()
            else:
                self.placeholder_label.show()

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

    def create_spec_selection_panel(self, parent_layout):
        title = QLabel("시험 분야")
        title.setStyleSheet("""
            font-size: 16px; 
            font-style: normal; 
            font-family: "Noto Sans KR"; 
            font-weight: 600; 
            color: #222; 
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        """)
        parent_layout.addWidget(title)

        # 그룹 테이블 추가
        self.group_table_widget = self.create_group_selection_table()
        parent_layout.addWidget(self.group_table_widget)

        # 시험 분야 테이블
        self.field_group = self.create_test_field_group()
        parent_layout.addWidget(self.field_group)

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
            desc_with_role = f"{desc} (요청 검증)"
            item = QTableWidgetItem(desc_with_role)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.test_field_table.setItem(idx, 0, item)
            self.spec_id_to_index[spec_id] = idx
            self.index_to_spec_id[idx] = spec_id

    def create_group_selection_table(self):
        """시험 그룹명 테이블"""
        group_box = QWidget()
        group_box.setFixedSize(459, 220)
        group_box.setStyleSheet("background: transparent;")  # ✅ 투명 배경 추가

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.group_table = QTableWidget(0, 1)
        self.group_table.setHorizontalHeaderLabels(["시험 분야"])
        self.group_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.group_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.group_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.group_table.verticalHeader().setVisible(False)
        self.group_table.setFixedHeight(219)

        self.group_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                outline: none;
                font-family: "Noto Sans KR";
                font-size: 14px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E0E0E0;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 14px;
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
                font-size: 13px;
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

    def create_test_field_group(self):
        """시험 시나리오 테이블"""
        group_box = QWidget()
        group_box.setFixedSize(459, 650)  # ✅ 더 줄임
        group_box.setStyleSheet("background: transparent;")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.test_field_table = QTableWidget(0, 1)
        self.test_field_table.setHorizontalHeaderLabels(["시험 시나리오"])
        self.test_field_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)
        self.test_field_table.verticalHeader().setVisible(False)
        self.test_field_table.setFixedHeight(645)  # ✅ 5px 여유 확보

        self.test_field_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: "Noto Sans KR";
                font-size: 14px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E0E0E0;
                border-right: 0px solid transparent;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 14px;
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
                font-size: 13px;
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
                description_with_role = f"{description} (요청 검증)"
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

    def save_current_spec_data(self):
        """현재 spec의 테이블 데이터와 상태를 저장"""
        if not hasattr(self, 'current_spec_id'):
            return

        # 테이블 데이터 저장
        table_data = []
        for row in range(self.tableWidget.rowCount()):
            row_data = {
                'api_name': self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else "",
                'icon_state': self._get_icon_state(row),  # PASS/FAIL/NONE 상태
                'retry_count': self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else "0",
                'pass_count': self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else "0",
                'total_count': self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else "0",
                'fail_count': self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else "0",
                'score': self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else "0%",
            }
            table_data.append(row_data)

        # 전체 데이터 저장 (✅ 복합키 사용: group_id_spec_id)
        composite_key = f"{self.current_group_id}_{self.current_spec_id}"

        print(f"[DEBUG] 💾 데이터 저장: {composite_key}")
        print(f"[DEBUG]   - 테이블 행 수: {len(table_data)}")
        print(f"[DEBUG]   - step_pass_counts: {self.step_pass_counts[:] if hasattr(self, 'step_pass_counts') else []}")

        self.spec_table_data[composite_key] = {
            'table_data': table_data,
            'step_buffers': [buf.copy() for buf in self.step_buffers],  # 깊은 복사
            'total_pass_cnt': self.total_pass_cnt,
            'total_error_cnt': self.total_error_cnt,
            'api_accumulated_data': self.api_accumulated_data.copy() if hasattr(self, 'api_accumulated_data') else {},
            # ✅ step_pass_counts와 step_error_counts 배열도 저장
            'step_pass_counts': self.step_pass_counts[:] if hasattr(self, 'step_pass_counts') else [],
            'step_error_counts': self.step_error_counts[:] if hasattr(self, 'step_error_counts') else [],
        }

        print(f"[DEBUG] ✅ 데이터 저장 완료")

    def _get_icon_state(self, row):
        """테이블 행의 아이콘 상태 반환 (PASS/FAIL/NONE)"""
        icon_widget = self.tableWidget.cellWidget(row, 1)
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
        print(f"[DEBUG] 📂 데이터 복원 시도: {composite_key}")

        if composite_key not in self.spec_table_data:
            print(f"[DEBUG] ❌ {composite_key} 저장된 데이터 없음 - 초기화 필요")
            return False

        saved_data = self.spec_table_data[composite_key]
        print(f"[DEBUG] ✅ 저장된 데이터 발견!")
        print(f"[DEBUG]   - 테이블 행 수: {len(saved_data['table_data'])}")
        print(f"[DEBUG]   - step_pass_counts: {saved_data.get('step_pass_counts', [])}")

        # 테이블 복원
        table_data = saved_data['table_data']
        for row, row_data in enumerate(table_data):
            if row >= self.tableWidget.rowCount():
                break

            # API 이름 - 항상 새 아이템 생성
            api_item = QTableWidgetItem(row_data['api_name'])
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, api_item)

            # 아이콘 상태 복원
            icon_state = row_data['icon_state']
            if icon_state == "PASS":
                img = self.img_pass
            elif icon_state == "FAIL":
                img = self.img_fail
            else:
                img = self.img_none

            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(img).pixmap(84, 20))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setToolTip(f"Result: {icon_state}")  # tooltip 설정으로 재저장 시 상태 유지
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 1, icon_widget)

            # 나머지 컬럼 복원 - 항상 새 아이템 생성
            for col, key in [(2, 'retry_count'), (3, 'pass_count'),
                             (4, 'total_count'), (5, 'fail_count'), (6, 'score')]:
                new_item = QTableWidgetItem(row_data[key])
                new_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, new_item)

        # step_buffers 복원
        self.step_buffers = [buf.copy() for buf in saved_data['step_buffers']]

        # 점수 복원
        self.total_pass_cnt = saved_data['total_pass_cnt']
        self.total_error_cnt = saved_data['total_error_cnt']

        # ✅ step_pass_counts와 step_error_counts 배열 복원
        self.step_pass_counts = saved_data.get('step_pass_counts', [0] * len(self.videoMessages))[:]
        self.step_error_counts = saved_data.get('step_error_counts', [0] * len(self.videoMessages))[:]
        print(f"[RESTORE] step_pass_counts 복원: {self.step_pass_counts}")
        print(f"[RESTORE] step_error_counts 복원: {self.step_error_counts}")

        # api_accumulated_data 복원
        if 'api_accumulated_data' in saved_data:
            self.api_accumulated_data = saved_data['api_accumulated_data'].copy()

        print(f"[DEBUG] {spec_id} 데이터 복원 완료")
        return True

    def on_test_field_selected(self, row, col):
        """시험 분야 클릭 시 해당 시스템으로 동적 전환"""
        try:
            self.selected_test_field_row = row

            if row in self.index_to_spec_id:
                new_spec_id = self.index_to_spec_id[row]

                if new_spec_id == self.current_spec_id:
                    return

                print(f"[PLATFORM] 🔄 시험 분야 전환: {self.current_spec_id} → {new_spec_id}")
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

                # ✅ 4. 기본 변수 초기화 (테이블 제외)
                self.cnt = 0
                self.current_retry = 0
                self.message_error = []

                # ✅ 5. 테이블 구조 업데이트 (행 수만 조정)
                self.update_result_table_structure(self.videoMessages)

                # ✅ 6. 저장된 데이터가 있으면 복원, 없으면 초기화
                if not self.restore_spec_data(new_spec_id):
                    # 저장된 데이터가 없으면 초기화
                    self.total_pass_cnt = 0
                    self.total_error_cnt = 0

                    # ✅ step_pass_counts와 step_error_counts 배열 초기화
                    api_count = len(self.videoMessages)
                    self.step_pass_counts = [0] * api_count
                    self.step_error_counts = [0] * api_count

                    self.step_buffers = [
                        {"data": "", "error": "", "result": "PASS"} for _ in range(len(self.videoMessages))
                    ]
                    # 테이블 초기화
                    print(f"[DEBUG] 💥 저장된 데이터 없음 - 테이블 초기화 시작 ({self.tableWidget.rowCount()}개 행)")
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
                        self.tableWidget.setCellWidget(i, 1, icon_widget)

                        # 카운트 초기화 - ✅ 아이템이 없으면 새로 생성
                        for col, value in [(2, "0"), (3, "0"), (4, "0"), (5, "0"), (6, "0%")]:
                            item = self.tableWidget.item(i, col)
                            if item:
                                item.setText(value)
                            else:
                                # ✅ 아이템이 없으면 새로 생성
                                new_item = QTableWidgetItem(value)
                                new_item.setTextAlignment(Qt.AlignCenter)
                                self.tableWidget.setItem(i, col, new_item)
                    print(f"[DEBUG] ✅ 테이블 초기화 완료")

                # trace 초기화 (선택사항 - 필요시)
                # if hasattr(self.Server, 'trace'):
                #     self.Server.trace.clear()

                # Server 객체 초기화
                if hasattr(self, 'Server'):
                    self.Server.cnt = 0
                    self.Server.message = self.videoMessages
                    self.Server.outMessage = self.videoOutMessage
                    self.Server.outCon = self.videoOutConstraint
                    self.Server.inSchema = self.videoInSchema
                    self.Server.webhookSchema = self.videoWebhookSchema
                    self.Server.webhookData = self.videoWebhookData
                    self.Server.webhookCon = self.videoWebhookConstraint

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
                # 결과 텍스트 초기화
                self.valResult.clear()
                self.valResult.append(f"✅ 시스템 전환 완료: {self.spec_description}")
                self.valResult.append(f"📋 API 목록 ({len(self.videoMessages)}개): {self.videoMessages}\n")

                print(f"[PLATFORM] ✅ 시스템 전환 완료: {self.spec_description}, API 수: {len(self.videoMessages)}")
        except Exception as e:
            print(f"시험 분야 선택 처리 실패: {e}")
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
            display_name = f"{row + 1}. {api_name}"
            if self.tableWidget.item(row, 0):
                self.tableWidget.item(row, 0).setText(display_name)
            else:
                api_item = QTableWidgetItem(display_name)
                api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(row, 0, api_item)

            # 상세 내용 버튼이 없으면 추가
            if not self.tableWidget.cellWidget(row, 7):
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

                self.tableWidget.setCellWidget(row, 7, container)

            # 행 높이 설정
            self.tableWidget.setRowHeight(row, 28)
    def update_result_table_with_apis(self, api_list):
        """시험 결과 테이블을 새로운 API 목록으로 업데이트"""
        api_count = len(api_list)
        self.tableWidget.setRowCount(api_count)

        for row, api_name in enumerate(api_list):
            display_name = f"{row + 1}. {api_name}"
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, api_item)

            # 결과 아이콘 초기화
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(84, 20))
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

            # 상세 내용 버튼
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

            self.tableWidget.setCellWidget(row, 7, container)
            self.tableWidget.setRowHeight(row, 40)

    def initUI(self):
        # 페이지 크기 설정
        self.setObjectName("platform_main")
        self.setAttribute(Qt.WA_StyledBackground, True)

        # 배경 이미지 설정
        bg_path = resource_path("assets/image/common/bg.png").replace("\\", "/")
        self.setStyleSheet(f"""
            QWidget#platform_main {{
                background-image: url('{bg_path}');
                background-repeat: no-repeat;
                background-position: center;
            }}
            QScrollArea, QScrollArea QWidget, QScrollArea::viewport,
            QGroupBox, QWidget#scroll_widget, QLabel {{
                background: transparent;
            }}
        """)

        if not self.embedded:
            self.setWindowTitle('통합플랫폼 연동 검증')

        # 메인 레이아웃
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # 헤더 영역
        header_container = QWidget()
        header_container.setFixedSize(1680, 56)
        header_container_layout = QHBoxLayout()
        header_container_layout.setContentsMargins(0, 8, 0, 0)
        header_container_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedSize(1680, 56)

        # 헤더 레이아웃
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header_layout.setSpacing(10)

        # 헤더 로고
        logo_label = QLabel(header_widget)
        logo_pixmap = QPixmap(resource_path("assets/image/common/header_logo.png"))
        logo_label.setPixmap(logo_pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(36, 36)
        header_layout.addWidget(logo_label)

        # 헤더 타이틀
        self.title_label = QLabel('통합 플랫폼 연동 검증 시작하기', header_widget)
        self.title_label.setAlignment(Qt.AlignVCenter)
        title_style = """
            color: #FFF;
            font-family: "Noto Sans KR";
            font-size: 18px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
            letter-spacing: -0.3px;
        """
        self.title_label.setStyleSheet(title_style)
        header_layout.addWidget(self.title_label)

        header_container_layout.addWidget(header_widget)
        header_container.setLayout(header_container_layout)

        mainLayout.addWidget(header_container)

        # 배경을 칠할 전용 컨테이너
        bg_root = QWidget()
        bg_root.setObjectName("bg_root")
        bg_root.setAttribute(Qt.WA_StyledBackground, True)
        bg_root_layout = QVBoxLayout()
        bg_root_layout.setContentsMargins(0, 0, 0, 0)
        bg_root_layout.setSpacing(0)

        # 2컬럼 레이아웃
        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(0)

        # 왼쪽 컬럼
        left_col = QWidget()
        left_col.setFixedSize(479, 906)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        # 시험 분야 선택 영역
        self.create_spec_selection_panel(left_layout)
        left_layout.addStretch()

        # 오른쪽 컬럼
        right_col = QWidget()
        right_col.setFixedSize(1064, 906)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 시험 API 라벨
        # ✅ 시험 URL 라벨 + 텍스트 박스 (가로 배치)
        url_row = QWidget()
        url_row.setFixedWidth(1064)
        url_row_layout = QHBoxLayout()
        url_row_layout.setContentsMargins(0, 20, 0, 6)
        url_row_layout.setSpacing(12)  # 라벨과 텍스트 박스 사이 간격

        # 시험 URL 라벨
        result_label = QLabel('시험 URL')
        result_label.setFixedWidth(100)  # 라벨 너비 고정
        result_label.setStyleSheet("""
            font-size: 16px; 
            font-style: normal; 
            font-family: "Noto Sans KR"; 
            font-weight: 600; 
            color: #222; 
            letter-spacing: -0.3px;
        """)
        url_row_layout.addWidget(result_label)

        # ✅ URL 텍스트 박스 (복사 가능)
        self.url_text_box = QLineEdit()
        self.url_text_box.setFixedHeight(40)
        self.url_text_box.setReadOnly(True)  # 읽기 전용
        self.url_text_box.setPlaceholderText("시험 URL이 여기에 표시됩니다")
        self.url_text_box.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;  /* ← 하얀색으로 변경 */
                border: 1px solid #CECECE;
                border-radius: 4px;
                padding: 0 12px;
                font-family: "Noto Sans KR";
                font-size: 14px;
                color: #222;
                selection-background-color: #4A90E2;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background-color: #FFFFFF;  /* 포커스 시에도 하얀색 유지 */
            }
        """)
        url_row_layout.addWidget(self.url_text_box, 1)  # stretch 적용

        url_row.setLayout(url_row_layout)
        right_layout.addWidget(url_row)

        api_label = QLabel('시험 API')
        api_label.setStyleSheet("""
            font-size: 16px; 
            font-style: normal; 
            font-family: "Noto Sans KR"; 
            font-weight: 600; 
            color: #222; 
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(api_label)

        self.init_centerLayout()
        contentWidget = QWidget()
        contentWidget.setLayout(self.centerLayout)
        right_layout.addWidget(contentWidget)

        # 수신 메시지 실시간 모니터링
        monitor_label = QLabel("수신 메시지 실시간 모니터링")
        monitor_label.setStyleSheet("""
            font-size: 16px; 
            font-style: normal; 
            font-family: "Noto Sans KR"; 
            font-weight: 600; 
            color: #222; 
            margin-top: 20px; 
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(monitor_label)

        # ✅ QTextBrowser를 담을 컨테이너 생성 (placeholder 오버레이를 위해)
        text_browser_container = QWidget()
        text_browser_container.setFixedSize(1064, 174)
        text_browser_layout = QVBoxLayout()
        text_browser_layout.setContentsMargins(0, 0, 0, 0)
        text_browser_layout.setSpacing(0)
        
        self.valResult = QTextBrowser(text_browser_container)
        self.valResult.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.valResult.setFixedHeight(174)
        self.valResult.setFixedWidth(1064)
        
        self.valResult.setStyleSheet("""
            QTextBrowser {
                background: #FFF;
                border-radius: 8px;
                border: 1px solid #CECECE;
                font-family: "Noto Sans KR";
                font-size: 15px;
                color: #222;
            }
        """)
        
        # ✅ 커스텀 placeholder 라벨 (위치 조정 가능)
        self.placeholder_label = QLabel("모니터링 내용이 표출됩니다", text_browser_container)
        self.placeholder_label.setGeometry(24, 10, 1000, 30)  # 왼쪽 24px, 위 16px
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #CECECE;
                font-family: "Noto Sans KR";
                font-size: 14px;
                font-weight: 400;
                background: transparent;
            }
        """)
        self.placeholder_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # 클릭 통과
        
        # ✅ 텍스트 변경 시 placeholder 숨기기
        self.valResult.textChanged.connect(self._toggle_placeholder)
        
        text_browser_layout.addWidget(self.valResult)
        text_browser_container.setLayout(text_browser_layout)
        right_layout.addWidget(text_browser_container, 1)
        
        # 초기 상태 설정
        self._toggle_placeholder()

        # 시험 결과
        self.valmsg = QLabel('시험 점수 요약', self)
        self.valmsg.setStyleSheet("""
            font-size: 16px; 
            font-style: normal; 
            font-family: "Noto Sans KR"; 
            font-weight: 600; 
            color: #222; 
            margin-top: 20px; 
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(self.valmsg)

        # 평가 점수 표시
        spec_score_group = self.create_spec_score_display_widget()
        right_layout.addWidget(spec_score_group)
        # 전체 점수 표시
        total_score_group = self.create_total_score_display_widget()
        right_layout.addWidget(total_score_group)

        # 버튼 그룹
        buttonGroup = QWidget()
        buttonGroup.setFixedWidth(1064)
        buttonLayout = QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignLeft)
        buttonLayout.setContentsMargins(0, 0, 0, 0)

        # 평가 시작 버튼
        self.sbtn = QPushButton(self)
        self.sbtn.setFixedSize(255, 50)
        start_enabled = resource_path("assets/image/test_runner/btn_평가시작_enabled.png").replace("\\", "/")
        start_hover = resource_path("assets/image/test_runner/btn_평가시작_hover.png").replace("\\", "/")
        start_disabled = resource_path("assets/image/test_runner/btn_평가시작_disabled.png").replace("\\", "/")
        self.sbtn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url('{start_enabled}');
                background-repeat: no-repeat;
                background-position: center;
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-image: url('{start_hover}');
            }}
            QPushButton:pressed {{
                background-image: url('{start_hover}');
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-image: url('{start_disabled}');
            }}
        """)
        self.sbtn.clicked.connect(self.sbtn_push)

        # 정지 버튼
        self.stop_btn = QPushButton(self)
        self.stop_btn.setFixedSize(255, 50)
        stop_enabled = resource_path("assets/image/test_runner/btn_일시정지_enabled.png").replace("\\", "/")
        stop_hover = resource_path("assets/image/test_runner/btn_일시정지_hover.png").replace("\\", "/")
        stop_disabled = resource_path("assets/image/test_runner/btn_일시정지_disabled.png").replace("\\", "/")
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url('{stop_enabled}');
                background-repeat: no-repeat;
                background-position: center;
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-image: url('{stop_hover}');
            }}
            QPushButton:pressed {{
                background-image: url('{stop_hover}');
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-image: url('{stop_disabled}');
            }}
        """)
        self.stop_btn.clicked.connect(self.stop_btn_clicked)
        self.stop_btn.setDisabled(True)

        # 종료 버튼
        self.rbtn = QPushButton(self)
        self.rbtn.setFixedSize(255, 50)
        exit_enabled = resource_path("assets/image/test_runner/btn_종료_enabled.png").replace("\\", "/")
        exit_hover = resource_path("assets/image/test_runner/btn_종료_hover.png").replace("\\", "/")
        exit_disabled = resource_path("assets/image/test_runner/btn_종료_disabled.png").replace("\\", "/")
        self.rbtn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url('{exit_enabled}');
                background-repeat: no-repeat;
                background-position: center;
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-image: url('{exit_hover}');
            }}
            QPushButton:pressed {{
                background-image: url('{exit_hover}');
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-image: url('{exit_disabled}');
            }}
        """)
        self.rbtn.clicked.connect(self.exit_btn_clicked)

        # 시험 결과 버튼
        self.result_btn = QPushButton(self)
        self.result_btn.setFixedSize(255, 50)
        result_enabled = resource_path("assets/image/test_runner/btn_시험결과_enabled.png").replace("\\", "/")
        result_hover = resource_path("assets/image/test_runner/btn_시험결과_hover.png").replace("\\", "/")
        result_disabled = resource_path("assets/image/test_runner/btn_시험결과_disabled.png").replace("\\", "/")
        self.result_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url('{result_enabled}');
                background-repeat: no-repeat;
                background-position: center;
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-image: url('{result_hover}');
            }}
            QPushButton:pressed {{
                background-image: url('{result_hover}');
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-image: url('{result_disabled}');
            }}
        """)
        self.result_btn.clicked.connect(self.show_result_page)

        buttonLayout.addWidget(self.sbtn)
        buttonLayout.addSpacing(18)
        buttonLayout.addWidget(self.stop_btn)
        buttonLayout.addSpacing(18)
        buttonLayout.addWidget(self.rbtn)
        buttonLayout.addSpacing(18)
        buttonLayout.addWidget(self.result_btn)
        buttonLayout.addStretch()
        buttonGroup.setLayout(buttonLayout)
        right_layout.addSpacing(32)
        right_layout.addWidget(buttonGroup)
        right_layout.addStretch()

        left_col.setLayout(left_layout)
        right_col.setLayout(right_layout)

        # 컬럼 레이아웃에 추가
        columns_layout.addWidget(left_col)
        columns_layout.addWidget(right_col)

        bg_root_layout.addLayout(columns_layout)
        bg_root.setLayout(bg_root_layout)
        mainLayout.addWidget(bg_root)

        self.setLayout(mainLayout)

        if not self.embedded:
            self.setWindowTitle('물리보안 통합플랫폼 연동 검증 소프트웨어')

        QTimer.singleShot(100, self.select_first_scenario)

        if not self.embedded:
            self.show()

    def select_first_scenario(self):
        """프로그램 시작 시 첫 번째 그룹의 첫 번째 시나리오 자동 선택"""
        try:
            print(f"[DEBUG] 초기 시나리오 자동 선택 시작")

            # 1. 첫 번째 그룹이 있는지 확인
            if self.group_table.rowCount() > 0:
                # 첫 번째 그룹 선택
                self.group_table.selectRow(0)
                print(f"[DEBUG] 첫 번째 그룹 선택: {self.index_to_group_name.get(0)}")

                # 그룹에 해당하는 시나리오 로드
                self.on_group_selected(0, 0)

            # 2. 시나리오 테이블에 첫 번째 항목이 있는지 확인
            if self.test_field_table.rowCount() > 0:
                # 첫 번째 시나리오 선택
                self.test_field_table.selectRow(0)
                first_spec_id = self.index_to_spec_id.get(0)
                print(f"[DEBUG] 첫 번째 시나리오 선택: spec_id={first_spec_id}")
                # URL 생성 (test_name 사용)
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', first_spec_id)
                    self.pathUrl = self.url + "/" + test_name
                else:
                    self.pathUrl = self.url + "/" + first_spec_id
                self.Server.current_spec_id = first_spec_id
                # 시나리오 선택 이벤트 수동 트리거 (테이블 업데이트)
                self.on_test_field_selected(0, 0)
            self.url_text_box.setText(self.pathUrl)
            print(f"[DEBUG] 초기 시나리오 자동 선택 완료: {self.spec_description}")

            # 3. UI 업데이트
            QApplication.processEvents()

        except Exception as e:
            print(f"[ERROR] 초기 시나리오 선택 실패: {e}")
            import traceback
            traceback.print_exc()
    def init_centerLayout(self):
        # 동적 API 개수에 따라 테이블 생성
        api_count = len(self.videoMessages)
        self.tableWidget = QTableWidget(api_count, 8)
        self.tableWidget.setHorizontalHeaderLabels(
            ["API 명", "결과", "검증 횟수", "통과 필드 수", "전체 필드 수", "실패 필드 수", "평가 점수", "상세 내용"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # 테이블 크기 설정
        self.tableWidget.setFixedHeight(270)
        self.tableWidget.setFixedWidth(1064)

        main_path = resource_path("assets/image/test_runner/main_table.png").replace("\\", "/")
        self.tableWidget.setStyleSheet(f"""
            QTableWidget {{
                background: #FFF;
                background-image: url('{main_path}');
                background-repeat: no-repeat;
                background-position: center;
                border-radius: 8px;
                border: 1px solid #CECECE;
                font-size: 15px;
                color: #222;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid #E0E0E0;
                border-right: 0px solid transparent;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 14px;
                font-style: normal;
                font-weight: 400;
                letter-spacing: 0.098px;
                text-align: center; 
            }}
            QHeaderView::section {{
                background-color: #EDF0F3;
                border-right: 0px solid transparent;
                border-left: 0px solid transparent;
                border-top: 0px solid transparent;
                border-bottom: 1px solid #CECECE;
                color: #1B1B1C;
                text-align: center;
                font-family: 'Noto Sans KR';
                font-size: 13px;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                letter-spacing: -0.156px;
            }}
        """)

        self.tableWidget.setShowGrid(False)

        # 컬럼 너비 설정
        self.tableWidget.setColumnWidth(0, 546)
        self.tableWidget.setColumnWidth(1, 56)
        self.tableWidget.setColumnWidth(2, 62)
        self.tableWidget.setColumnWidth(3, 78)
        self.tableWidget.setColumnWidth(4, 78)
        self.tableWidget.setColumnWidth(5, 78)
        self.tableWidget.setColumnWidth(6, 62)
        self.tableWidget.setColumnWidth(7, 88)

        # 행 높이 설정
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 28)

        # 단계명 리스트
        self.step_names = self.videoMessages
        for i, name in enumerate(self.step_names):
            # API 명
            api_item = QTableWidgetItem(f"{i + 1}. {name}")
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)  # 가운데 정렬
            self.tableWidget.setItem(i, 0, api_item)

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

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(i, 7, container)

        # 결과 컬럼만 클릭 가능
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)
        
        # ✅ QScrollArea로 감싸기
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.tableWidget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFixedWidth(1064)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # centerLayout 초기화
        self.centerLayout = QVBoxLayout()
        self.centerLayout.setContentsMargins(0, 0, 0, 0)
        self.centerLayout.addWidget(scroll_area)

    def show_combined_result(self, row):
        """통합 상세 내용 확인"""
        try:
            buf = self.step_buffers[row]
            api_name = self.tableWidget.item(row, 0).text()

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
                        webhook_schema = self.videoWebhookSchema[0] if len(self.videoWebhookSchema) > 0 else None
                    except:
                        webhook_schema = None

            # 통합 팝업창
            dialog = CombinedDetailDialog(api_name, buf, schema_data, webhook_schema)
            dialog.exec_()

        except Exception as e:
            CustomDialog(f"오류:\n{str(e)}", "상세 내용 확인 오류")

    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭"""
        if col == 1:
            msg = getattr(self, f"step{row + 1}_msg", "")
            if msg:
                CustomDialog(msg, self.tableWidget.item(row, 0).text())

    def create_spec_score_display_widget(self):
        """메인 화면에 표시할 시험 분야별 평가 점수 위젯"""

        spec_group = QGroupBox()
        spec_group.setFixedWidth(1064)
        spec_group.setFixedHeight(106)
        spec_group.setStyleSheet("""
            QGroupBox {
                background-color: #FFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)

        # 분야별 점수 아이콘
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_분야별점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)

        # 분야명 레이블
        self.spec_name_label = QLabel(f"분야별 점수      |      {self.spec_description} ({len(self.videoMessages)}개 API)")
        self.spec_name_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)
        spec_name_font = self.spec_name_label.font()
        spec_name_font.setBold(True)
        self.spec_name_label.setFont(spec_name_font)

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

        # 점수 레이블들
        self.spec_pass_label = QLabel("통과 필드 수")
        self.spec_pass_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)
        self.spec_total_label = QLabel("전체 필드 수")
        self.spec_total_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)
        self.spec_score_label = QLabel("종합 평가 점수")
        self.spec_score_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)

        font = self.spec_pass_label.font()
        self.spec_pass_label.setFont(font)
        self.spec_total_label.setFont(font)
        self.spec_score_label.setFont(font)

        spec_layout = QVBoxLayout()
        spec_layout.setContentsMargins(32, 15, 32, 15)

        icon_vlayout = QVBoxLayout()
        icon_vlayout.setContentsMargins(0, 0, 0, 0)
        icon_vlayout.setSpacing(0)
        icon_vlayout.addSpacing(0)
        icon_vlayout.addWidget(icon_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
        icon_vlayout.addStretch()

        # 아이콘 + 분야명
        header_layout = QHBoxLayout()
        header_layout.addLayout(icon_vlayout)
        header_layout.addWidget(self.spec_name_label)
        header_layout.addStretch()

        spec_layout.addLayout(header_layout)
        spec_layout.addSpacing(5)
        spec_layout.addWidget(separator)
        spec_layout.addSpacing(5)

        spec_score_layout = QHBoxLayout()
        spec_score_layout.setSpacing(260)
        spec_score_layout.addWidget(self.spec_pass_label)
        spec_score_layout.addWidget(self.spec_total_label)
        spec_score_layout.addWidget(self.spec_score_label)
        spec_score_layout.addStretch()

        spec_layout.addLayout(spec_score_layout)
        spec_group.setLayout(spec_layout)

        return spec_group

    def create_total_score_display_widget(self):
        """메인 화면에 표시할 전체 평가 점수 위젯"""
        total_group = QGroupBox()
        total_group.setFixedWidth(1064)
        total_group.setFixedHeight(106)
        total_group.setStyleSheet("""
            QGroupBox {
                background-color: #F0F6FB;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)

        # 전체 점수 아이콘
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_전체점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(40, 40)

        # 전체 점수 레이블
        total_name_label = QLabel("전체 점수 (모든 시험 분야 합산)")
        total_name_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)
        total_name_font = total_name_label.font()
        total_name_font.setBold(True)
        total_name_label.setFont(total_name_font)

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

        self.total_pass_label = QLabel("통과 필드 수")
        self.total_pass_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)
        self.total_total_label = QLabel("전체 필드 수")
        self.total_total_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)
        self.total_score_label = QLabel("종합 평가 점수")
        self.total_score_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 15px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: -0.18px;
        """)

        font = self.total_pass_label.font()
        font.setBold(True)
        self.total_pass_label.setFont(font)
        self.total_total_label.setFont(font)
        self.total_score_label.setFont(font)

        total_layout = QVBoxLayout()
        total_layout.setContentsMargins(32, 15, 32, 15)

        icon_vlayout = QVBoxLayout()
        icon_vlayout.setContentsMargins(0, 0, 0, 0)
        icon_vlayout.setSpacing(0)
        icon_vlayout.addSpacing(0)
        icon_vlayout.addWidget(icon_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
        icon_vlayout.addStretch()

        # 아이콘 + 전체 점수 텍스트
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        header_layout.addLayout(icon_vlayout)
        header_layout.addWidget(total_name_label)
        header_layout.addStretch()
        total_layout.addLayout(header_layout)

        total_layout.addSpacing(5)
        total_layout.addWidget(separator)
        total_layout.addSpacing(5)

        score_layout = QHBoxLayout()
        score_layout.setSpacing(260)
        score_layout.addWidget(self.total_pass_label)
        score_layout.addWidget(self.total_total_label)
        score_layout.addWidget(self.total_score_label)
        score_layout.addStretch()

        total_layout.addLayout(score_layout)
        total_group.setLayout(total_layout)

        return total_group

    def resizeEvent(self, event):
        """창 크기 변경 시 반응형 UI 조정"""
        try:
            super().resizeEvent(event)
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

    def run_single_spec_test(self):
        """단일 spec_id에 대한 시험 실행"""
        self._clean_trace_dir_once()

        # ✅ 이전 시험 결과가 global 점수에 포함되어 있으면 제거 (복합키 사용)
        composite_key = f"{self.current_group_id}_{self.current_spec_id}"
        if composite_key in self.spec_table_data:
            prev_data = self.spec_table_data[composite_key]
            prev_pass = prev_data.get('total_pass_cnt', 0)
            prev_error = prev_data.get('total_error_cnt', 0)
            print(f"[SCORE RESET] 기존 {composite_key} 점수 제거: pass={prev_pass}, error={prev_error}")

            # global 점수에서 해당 spec 점수 제거
            self.global_pass_cnt = max(0, self.global_pass_cnt - prev_pass)
            self.global_error_cnt = max(0, self.global_error_cnt - prev_error)

        # ✅ 현재 시험 시나리오(spec)의 점수만 초기화
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        # ✅ step_pass_counts, step_error_counts 배열도 초기화
        if hasattr(self, 'step_pass_counts'):
            api_count = len(self.videoMessages)
            self.step_pass_counts = [0] * api_count
            self.step_error_counts = [0] * api_count
        # global_pass_cnt, global_error_cnt는 유지 (다른 spec 영향 없음)

        self.cnt = 0
        self.current_retry = 0
        self.init_win()
        self.valResult.append(f"🚀 시험 시작: {self.spec_description}")

    def sbtn_push(self):
        try:
            selected_rows = self.test_field_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "알림", "시험 시나리오를 선택하세요.")
                return
            self.save_current_spec_data()

            # ✅ 로딩 팝업 표시
            self.loading_popup = LoadingPopup()
            self.loading_popup.show()
            QApplication.processEvents()  # UI 즉시 업데이트

            selected_spec_ids = [self.index_to_spec_id[r.row()] for r in selected_rows]
            for spec_id in selected_spec_ids:
                self.current_spec_id = spec_id
                self.load_specs_from_constants()
                self.run_single_spec_test()

            print(f"[DEBUG] ========== 검증 시작: 완전 초기화 ==========")

            # ✅ 1. 기존 타이머 정지
            if self.tick_timer.isActive():
                print(f"[DEBUG] 기존 타이머 중지")
                self.tick_timer.stop()

            # ✅ 2. 기존 서버 스레드 종료
            if self.server_th is not None and self.server_th.isRunning():
                print(f"[DEBUG] 기존 서버 스레드 종료 중...")
                try:
                    self.server_th.httpd.shutdown()
                    self.server_th.wait(2000)  # 최대 2초 대기
                    print(f"[DEBUG] 기존 서버 스레드 종료 완료")
                except Exception as e:
                    print(f"[WARN] 서버 종료 중 오류 (무시): {e}")
                self.server_th = None

            # ✅ 3. trace 디렉토리 초기화
            self._clean_trace_dir_once()

            # ✅ 4. 모든 카운터 및 플래그 초기화 (첫 실행처럼)
            self.cnt = 0
            self.cnt_pre = 0
            self.time_pre = 0
            self.current_retry = 0
            self.realtime_flag = False
            self.tmp_msg_append_flag = False
            
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
            print(f"[DEBUG] step_buffers 재생성 완료: {len(self.step_buffers)}개")

            # ✅ 10. Server 객체 상태 초기화
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

            # ✅ 11. 평가 점수 디스플레이 초기화
            self.update_score_display()

            # ✅ 12. 버튼 상태 변경
            self.sbtn.setDisabled(True)
            self.stop_btn.setEnabled(True)

            # ✅ 12. 버튼 상태 변경
            self.sbtn.setDisabled(True)
            self.stop_btn.setEnabled(True)

            # ✅ 13. JSON 데이터 준비
            json_to_data(self.radio_check_flag)
            timeout = 5
            default_timeout = 5

            # ✅ 15. Server 설정
            print(f"[DEBUG] Server 설정 시작")
            self.Server.message = self.videoMessages
            self.Server.outMessage = self.videoOutMessage
            self.Server.inSchema = self.videoInSchema
            self.Server.outCon = self.videoOutConstraint
            self.Server.webhookData = self.videoWebhookData
            self.Server.webhookCon = self.videoWebhookConstraint
            self.Server.system = "video"
            self.Server.timeout = timeout
            print(f"[DEBUG] Server 설정 완료")

            # ✅ 16. UI 초기화 (init_win 호출 전에 valResult만 먼저 클리어)
            print(f"[DEBUG] UI 초기화 시작")
            self.valResult.clear()
            print(f"[DEBUG] UI 초기화 완료")

            # ✅ 17. 테이블 아이콘 및 데이터 완전 초기화
            print(f"[DEBUG] 테이블 초기화 시작")
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
                self.tableWidget.setCellWidget(i, 1, icon_widget)
                
                # 모든 카운트 0으로 초기화
                for col, value in ((2, "0"), (3, "0"), (4, "0"), (5, "0"), (6, "0%")):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(i, col, item)
            print(f"[DEBUG] 테이블 초기화 완료")

            # ✅ 18. 인증 설정
            print(f"[DEBUG] 인증 설정 시작")
            print(f"[DEBUG] 사용자 인증 방식 : ", self.CONSTANTS.auth_type)

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
            self.valResult.append("=" * 60)
            self.valResult.append("🚀 플랫폼 검증 시작")
            self.valResult.append(f"📋 Spec ID: {self.current_spec_id}")
            self.valResult.append(f"📊 API 개수: {len(self.videoMessages)}개")
            self.valResult.append("=" * 60)
            self.valResult.append("\nStart Validation...\n")

            # ✅ 20. 서버 시작
            print(f"[DEBUG] 서버 시작 준비")
            url = self.url.split(":")
            address_port = int(url[-1])
            # ✅ 0.0.0.0으로 바인딩 (모든 네트워크 인터페이스에서 수신)
            address_ip = "0.0.0.0"

            print(f"[DEBUG] 플랫폼 서버 시작: {address_ip}:{address_port} (외부 접근: {self.url})")
            self.server_th = server_th(handler_class=self.Server, address=address_ip, port=address_port)
            self.server_th.start()

            # 서버 준비 완료까지 대기 (첫 실행 시만)
            if self.first_run:
                self.valResult.append("🔄 플랫폼 서버 초기화 중...")
                time.sleep(5)
                self.valResult.append("✅ 플랫폼 서버 준비 완료")
                self.first_run = False
            else:
                # 두 번째 이후에도 서버 안정화를 위한 짧은 대기
                print("[DEBUG] 서버 재시작 안정화 대기...")
                time.sleep(2)
                self.valResult.append("✅ 서버 준비 완료")

            # ✅ 21. 타이머 시작 (모든 초기화 완료 후)
            print(f"[DEBUG] 타이머 시작")
            self.tick_timer.start(1000)
            print(f"[DEBUG] ========== 검증 시작 준비 완료 ==========")

            # ✅ 로딩 팝업 닫기
            if self.loading_popup:
                self.loading_popup.close()
                self.loading_popup = None

        except Exception as e:
            print(f"[ERROR] sbtn_push에서 예외 발생: {e}")
            import traceback
            traceback.print_exc()

            # ✅ 에러 발생 시 로딩 팝업 닫기
            if self.loading_popup:
                self.loading_popup.close()
                self.loading_popup = None

            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)

    def stop_btn_clicked(self):
        # ✅ 타이머 중지
        if self.tick_timer.isActive():
            self.tick_timer.stop()
            print(f"[DEBUG] 타이머 중지됨")

        # ✅ 서버 스레드 종료
        if self.server_th is not None and self.server_th.isRunning():
            print(f"[DEBUG] 서버 스레드 종료 시작...")
            try:
                self.server_th.httpd.shutdown()
                self.server_th.wait(2000)  # 최대 2초 대기
                print(f"[DEBUG] 서버 스레드 종료 완료")
            except Exception as e:
                print(f"[WARN] 서버 종료 중 오류 (무시): {e}")
            self.server_th = None

        self.valResult.append("검증 절차가 중지되었습니다.")
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)
        self.save_current_spec_data()
        try:
            self.run_status = "진행중"
            result_json = build_result_json(self)
            url = f"{CONSTANTS.management_url}/api/integration/test-results"
            response = requests.post(url, json=result_json)
            print("✅ 시험 결과 전송 상태 코드:", response.status_code)
            print("📥  시험 결과 전송 응답:", response.text)
            json_path = os.path.join(result_dir, "request_results.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)
            print(f"✅ 진행 중 결과가 '{json_path}'에 저장되었습니다.")
            self.valResult.append(f"\n📄 진행 상황 저장 완료: {json_path}")
            self.valResult.append("(일시정지 시점까지의 결과가 저장되었습니다)")
        except Exception as e:
            print(f"❌ JSON 저장 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            self.valResult.append(f"\n⚠️ 결과 저장 실패: {str(e)}")

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
            print(f"전체화면 전환 오류: {e}")

    def exit_btn_clicked(self):
        reply = QMessageBox.question(self, '프로그램 종료',
                                     '정말로 프로그램을 종료하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            result_payload = self.build_result_payload()
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
            print(f"Error loading webhook schema: {e}")
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
            print(f"[URL] 시험 URL 업데이트: {self.pathUrl}")

    def closeEvent(self, event):
        """창 닫기 이벤트 - 서버 스레드 정리"""
        # ✅ 타이머 중지
        if hasattr(self, 'tick_timer') and self.tick_timer.isActive():
            self.tick_timer.stop()
            print(f"[DEBUG] 종료 시 타이머 중지됨")

        # ✅ 서버 스레드 종료
        if hasattr(self, 'server_th') and self.server_th is not None and self.server_th.isRunning():
            print(f"[DEBUG] 종료 시 서버 스레드 종료 중...")
            try:
                self.server_th.httpd.shutdown()
                self.server_th.wait(2000)  # 최대 2초 대기
                print(f"[DEBUG] 서버 스레드 종료 완료")
            except Exception as e:
                print(f"[WARN] 서버 종료 중 오류 (무시): {e}")

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
            print(e)

        print('Starting on ', self.server_address)

    def run(self):
        self.httpd.serve_forever()


class json_data(QThread):
    json_update_data = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        import time
        while True:
            with open(resource_path("spec/rows.json"), "r", encoding="UTF-8") as out_file:
                data = json.load(out_file)
            if data is not None:
                with open(resource_path("spec/rows.json"), "w", encoding="UTF-8") as out_file:
                    json.dump(None, out_file, ensure_ascii=False)
                self.json_update_data.emit(data)
            time.sleep(0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))

    ex = PlatformValidationWindow()
    ex.initialize()
    ex.show()
    sys.exit(app.exec())