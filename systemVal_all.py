# 시스템 검증 소프트웨어
# physical security integrated system validation software
import os
import time
import threading
import json
import requests
import sys
from core.functions import build_result_json

import urllib3
import warnings
from datetime import datetime
from collections import defaultdict

# SSL 경고 비활성화 (자체 서명 인증서 사용 시)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

from urllib.parse import urlparse
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor, QPixmap
from PyQt5.QtCore import *
from PyQt5 import QtCore
from api.webhook_api import WebhookThread
from core.functions import json_check_, resource_path, set_auth, json_to_data, timeout_field_finder
from core.data_mapper import ConstraintDataGenerator
from requests.auth import HTTPDigestAuth
import config.CONSTANTS as CONSTANTS
import traceback
import importlib
from core.validation_registry import get_validation_rules
from pathlib import Path
import spec.Data_request as data_request_module
import spec.Schema_response as schema_response_module
import spec.Constraints_request as constraints_request_module

import os

result_dir = os.path.join(os.getcwd(), "results")
os.makedirs(result_dir, exist_ok=True)
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
        #self.webhookInSchema = []

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

        # 기본 스키마 + 웹훅 스키마 결합
        schema_text = self._format_schema(schema_data)
        if self.webhook_schema:
            schema_text += "\n\n=== 웹훅 이벤트 스키마 (플랫폼→시스템) ===\n"
            schema_text += self._format_schema(self.webhook_schema) # 값이 있음

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
        # 오류 설명 추가: 값 자체뿐 아니라 원인도 함께 표시
        error_text = step_buffer["error"] if step_buffer["error"] else ("오류가 없습니다." if result == "PASS" else "오류 내용 없음")
        # 예시: 값이 범위에 맞지 않거나 타입이 다를 때 추가 설명
        # if result == "FAIL" and error_text and isinstance(error_text, str):
        #     # 간단한 규칙 기반 설명 추가 (실제 검증 로직에 맞게 확장 가능) - (10/28) 수정해야함
        #     if "startTime" in error_text or "endTime" in error_text:
        #         error_text += "\n[설명] startTime 또는 endTime 값이 허용된 범위에 맞지 않거나, 요청값과 다릅니다."
        #     if "camID" in error_text and '""' in error_text:
        #         error_text += "\n[설명] camID 값이 비어 있습니다. 실제 카메라 ID가 필요합니다."
        #     if "타입" in error_text or "type" in error_text:
        #         error_text += "\n[설명] 데이터 타입이 스키마와 일치하지 않습니다."
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

        # ✅ 배경 이미지 설정
        self.setObjectName("system_main")
        self.setAttribute(Qt.WA_StyledBackground, True)

        bg_path = resource_path("assets/image/common/bg.png").replace("\\", "/")
        print(f"배경 이미지 경로: {bg_path}")

        self.setStyleSheet(f"""
            #system_main {{
                background-image: url('{bg_path}');
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
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
        self.setWindowTitle('시스템 연동 시험 결과')
        self.resize(1680, 1080)

        # 현재 선택된 spec_id 저장
        self.current_spec_id = parent.current_spec_id

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
                background-size: cover;
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
        title_label = QLabel('시스템 연동 시험 결과', header_widget)
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
        right_layout.setSpacing(10)
        # 시험 결과 라벨
        api_name_label = QLabel('시험 API')
        api_name_label.setStyleSheet("""
                    font-size: 16px; 
                    font-style: normal; 
                    font-family: "Noto Sans KR"; 
                    font-weight: 600; 
                    color: #222; 
                    margin-bottom: 6px;
                    letter-spacing: -0.3px;
                """)
        right_layout.addWidget(api_name_label)

        # 결과 테이블 (크기 키움: 350px)
        self.create_result_table(right_layout)

        right_layout.addSpacing(10)

        result_label = QLabel('시험 점수 요약')
        mainLayout.addWidget(result_label)

        # 결과 테이블 (parent의 테이블 데이터 복사) - 동적 API 개수
        api_count = self.parent.tableWidget.rowCount()
        self.tableWidget = QTableWidget(api_count, 8)
        self.tableWidget.setFixedHeight(274)
        self.tableWidget.setFixedWidth(1064)
        self.tableWidget.setStyleSheet(f"""
            background: #FFF;
            border-radius: 8px;
            border: 1px solid #CECECE;
            font-size: 15px;
            color: #222;
        """)
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

        # 시험 분야별 점수 표시
        self.spec_score_group = self._create_spec_score_display()
        right_layout.addWidget(self.spec_score_group)

        # 전체 점수 표시
        total_score_group = self._create_total_score_display()
        right_layout.addWidget(total_score_group)

        right_layout.addSpacing(32)

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
                        background-size: contain;
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
        group_items = [
            (g.get("group_name", "미지정 그룹"), g.get("group_id", ""))
            for g in CONSTANTS.SPEC_CONFIG
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
        """시험 시나리오 테이블 (크기 줄임: 280px)"""
        group_box = QWidget()
        group_box.setFixedSize(459, 760)
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
        self.test_field_table.setFixedHeight(759)

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
        # 현재 spec_id가 속한 그룹 찾기
        current_group = None
        for group_data in CONSTANTS.SPEC_CONFIG:
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

        selected_group = next(
            (g for g in CONSTANTS.SPEC_CONFIG if g.get("group_name") == group_name), None
        )

        if selected_group:
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
        """시험 분야 클릭 시 해당 시스템으로 동적 전환"""
        try:
            self.selected_test_field_row = row

            if row in self.index_to_spec_id:
                new_spec_id = self.index_to_spec_id[row]

                if new_spec_id == self.current_spec_id:
                    print(f"[SELECT] 이미 선택된 시나리오: {new_spec_id}")
                    return

                print(f"[SELECT] 🔄 시험 분야 전환: {self.current_spec_id} → {new_spec_id}")

                # ✅ 1. 현재 spec의 테이블 데이터 저장
                self.save_current_spec_data()

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

                # ✅ 5. 테이블 완전 재구성 (API 이름 먼저 설정!)
                print(f"[SELECT] 테이블 완전 재구성 시작")
                self.update_result_table_structure(self.videoMessages)

                # ✅ 6. 저장된 데이터가 있으면 복원 (API 이름은 유지!)
                if new_spec_id in self.spec_table_data:
                    print(f"[SELECT] 저장된 데이터 복원 시작")
                    restored = self.restore_spec_data_without_api_names(new_spec_id)

                    if restored:
                        print(f"[SELECT] {new_spec_id} 저장된 결과 로드 완료")
                    else:
                        print(f"[SELECT] 저장된 데이터 복원 실패 - 초기화")
                        self.initialize_empty_table()
                else:
                    # 저장된 데이터가 없으면 초기화
                    print(f"[SELECT] {new_spec_id} 저장된 데이터 없음 - 초기화")
                    self.initialize_empty_table()

                # ✅ 7. trace 및 latest_events 초기화
                self.trace.clear()
                self.latest_events = {}

                # ✅ 8. 설정 다시 로드
                self.get_setting()

                # ✅ 9. 평가 점수 디스플레이 업데이트
                self.update_score_display()

                # ✅ 10. 결과 텍스트 초기화
                self.valResult.clear()
                self.valResult.append(f"✅ 시스템 전환 완료: {self.spec_description}")
                self.valResult.append(f"📋 Spec ID: {self.current_spec_id}")
                self.valResult.append(f"📊 API 개수: {len(self.videoMessages)}개")
                self.valResult.append(f"📋 API 목록: {self.videoMessages}\n")

                print(f"[SELECT] ✅ 시스템 전환 완료")

        except Exception as e:
            print(f"[SELECT] 시험 분야 선택 처리 실패: {e}")
            import traceback
            traceback.print_exc()

    def restore_spec_data_without_api_names(self, spec_id):
        """저장된 spec 데이터 복원 (API 이름은 건드리지 않음!)"""
        if spec_id not in self.spec_table_data:
            print(f"[RESTORE] {spec_id} 저장된 데이터 없음")
            return False

        saved_data = self.spec_table_data[spec_id]
        print(f"[RESTORE] {spec_id} 데이터 복원 시작")

        # 테이블 복원 (API 이름 제외!)
        table_data = saved_data['table_data']
        for row, row_data in enumerate(table_data):
            if row >= self.tableWidget.rowCount():
                print(f"[RESTORE] 경고: row={row}가 범위 초과, 건너뜀")
                break

            # ✅ API 이름은 이미 update_result_table_structure()에서 설정됨 - 건드리지 않음!
            # 대신 현재 API 이름이 제대로 있는지만 확인
            current_api_item = self.tableWidget.item(row, 0)
            if current_api_item:
                print(f"[RESTORE] Row {row} API 이름 유지: {current_api_item.text()}")
            else:
                print(f"[RESTORE] 경고: Row {row} API 이름이 없음!")

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
            icon_label.setPixmap(QIcon(img).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 1, icon_widget)

            # 나머지 컬럼 복원 (안전하게)
            for col, key in [(2, 'retry_count'), (3, 'pass_count'),
                             (4, 'total_count'), (5, 'fail_count'), (6, 'score')]:
                item = self.tableWidget.item(row, col)
                if item:
                    item.setText(row_data[key])
                else:
                    new_item = QTableWidgetItem(row_data[key])
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(row, col, new_item)

        # step_buffers 복원
        self.step_buffers = [buf.copy() for buf in saved_data['step_buffers']]

        # 점수 복원
        self.total_pass_cnt = saved_data['total_pass_cnt']
        self.total_error_cnt = saved_data['total_error_cnt']

        print(f"[RESTORE] {spec_id} 데이터 복원 완료")
        return True

    def initialize_empty_table(self):
        """테이블을 초기 상태로 설정 (API 이름은 유지)"""
        print(f"[INIT] 테이블 초기화 시작")

        # 점수 초기화
        self.total_pass_cnt = 0
        self.total_error_cnt = 0

        # step_buffers 초기화
        api_count = len(self.videoMessages)
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS"} for _ in range(api_count)
        ]

        # 테이블 데이터만 초기화 (API 이름은 이미 설정되어 있음)
        for row in range(self.tableWidget.rowCount()):
            # API 이름 확인
            api_item = self.tableWidget.item(row, 0)
            if api_item:
                print(f"[INIT] Row {row} API 이름 확인: {api_item.text()}")
            else:
                # API 이름이 없으면 다시 설정
                if row < len(self.videoMessages):
                    display_name = f"{row + 1}. {self.videoMessages[row]}"
                    api_item = QTableWidgetItem(display_name)
                    api_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.tableWidget.setItem(row, 0, api_item)
                    print(f"[INIT] Row {row} API 이름 재설정: {display_name}")

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
            self.tableWidget.setCellWidget(row, 1, icon_widget)

            # 카운트 초기화
            for col, value in [(2, "0"), (3, "0"), (4, "0"), (5, "0"), (6, "0%")]:
                item = self.tableWidget.item(row, col)
                if item:
                    item.setText(value)
                else:
                    new_item = QTableWidgetItem(value)
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(row, col, new_item)

        print(f"[INIT] 테이블 초기화 완료")

    def save_current_spec_data(self):
        """현재 spec의 테이블 데이터와 상태를 저장"""
        if not hasattr(self, 'current_spec_id'):
            return

        # 테이블 데이터 저장 (현재 videoMessages 기준으로!)
        table_data = []
        for row in range(self.tableWidget.rowCount()):
            # ✅ 실제 API 이름을 videoMessages에서 가져옴 (테이블 텍스트 아님!)
            if row < len(self.videoMessages):
                api_name = f"{row + 1}. {self.videoMessages[row]}"
            else:
                api_item = self.tableWidget.item(row, 0)
                api_name = api_item.text() if api_item else ""

            row_data = {
                'api_name': api_name,  # ✅ 올바른 API 이름 저장
                'icon_state': self._get_icon_state(row),
                'retry_count': self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else "0",
                'pass_count': self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else "0",
                'total_count': self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else "0",
                'fail_count': self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else "0",
                'score': self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else "0%",
            }
            table_data.append(row_data)

        # 전체 데이터 저장
        self.spec_table_data[self.current_spec_id] = {
            'table_data': table_data,
            'step_buffers': [buf.copy() for buf in self.step_buffers],
            'total_pass_cnt': self.total_pass_cnt,
            'total_error_cnt': self.total_error_cnt,
        }
        print(f"[DEBUG] {self.current_spec_id} 데이터 저장 완료")
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
            api_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, api_item)

            # 기본 아이콘
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.parent.img_none).pixmap(16, 16))
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
            api_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, api_item)

            # 아이콘 상태 복원
            icon_state = row_data['icon_state']
            if icon_state == "PASS":
                img = self.parent.img_pass
            elif icon_state == "FAIL":
                img = self.parent.img_fail
            else:
                img = self.parent.img_none

            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(img).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
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
            # 기존 위젯 제거
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

        # 오른쪽 컬럼의 레이아웃 찾기
        right_col = self.findChildren(QWidget)
        for widget in right_col:
            if widget.width() == 1064 and widget.height() == 906:
                right_layout = widget.layout()
                if right_layout:
                    # 테이블 다음, 전체 점수 앞에 삽입 (인덱스 조정)
                    right_layout.insertWidget(6, self.spec_score_group)
                break

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
        return info_widget

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
                background-size: cover;
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
            self.tableWidget.setRowHeight(i, 28)  # 28 → 32

        # parent 테이블 데이터 복사
        self._copy_table_data()

        # 상세 내용 버튼 클릭 이벤트
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)

        parent_layout.addWidget(self.tableWidget)

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

            # 결과 아이콘
            icon_widget = self.parent.tableWidget.cellWidget(row, 1)
            if icon_widget:
                new_icon_widget = QWidget()
                new_icon_layout = QHBoxLayout()
                new_icon_layout.setContentsMargins(0, 0, 0, 0)

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

        # 전체 누적 점수 사용
        total_pass = self.parent.global_pass_cnt
        total_error = self.parent.global_error_cnt
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
    # 시험 결과 표시 요청 시그널 (main.py와 연동)
    showResultRequested = pyqtSignal(object)  # parent widget을 인자로 전달

    def _load_from_trace_file(self, api_name, direction="RESPONSE"):
        """Trace 파일에서 최신 이벤트 데이터 로드"""
        try:
            trace_file = Path("results/trace") / f"trace_{api_name.replace('/', '_')}.ndjson"

            if not trace_file.exists():
                print(f"[DEBUG] trace 파일 없음: {trace_file}")
                return None

            # 파일에서 가장 최근의 해당 direction 이벤트 찾기
            latest_event = None
            with open(trace_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        if event.get("dir") == direction:
                            latest_event = event
                    except json.JSONDecodeError:
                        continue

            if latest_event:
                # latest_events 업데이트
                api_key = latest_event.get("api", api_name)
                if api_key not in self.latest_events:
                    self.latest_events[api_key] = {}
                self.latest_events[api_key][direction] = latest_event
                print(f"[DEBUG] trace 파일에서 {api_name} {direction} 데이터 로드 완료")
                return latest_event.get("data")
            else:
                print(f"[DEBUG] trace 파일에서 {api_name} {direction} 데이터 없음")
                return None

        except Exception as e:
            print(f"[ERROR] trace 파일 로드 중 오류: {e}")
            return None

    # 
    def _apply_request_constraints(self, request_data, cnt):
        """
        이전 응답 데이터를 기반으로 요청 데이터 업데이트
        - inCon (request constraints)을 사용하여 이전 endpoint 응답에서 값 가져오기
        """
        try:
            # constraints 가져오기
            if cnt >= len(self.inCon) or not self.inCon[cnt]:
                print(f"[DATA_MAPPER] constraints 없음 (cnt={cnt})")
                return request_data

            constraints = self.inCon[cnt]

            if not constraints or not isinstance(constraints, dict):
                print(f"[DATA_MAPPER] constraints가 비어있거나 dict가 아님")
                return request_data

            print(f"[DATA_MAPPER] 요청 데이터 업데이트 시작 (API: {self.message[cnt]})")
            print(f"[DATA_MAPPER] constraints: {list(constraints.keys())}")

            # trace 파일에서 이전 응답 데이터 로드 (필요한 경우)
            for path, rule in constraints.items():
                ref_endpoint = rule.get("referenceEndpoint")
                if ref_endpoint:
                    # 슬래시 제거하여 키 생성
                    ref_key = ref_endpoint.lstrip('/')

                    # latest_events에 없으면 trace 파일에서 로드
                    if ref_key not in self.latest_events or "RESPONSE" not in self.latest_events.get(ref_key, {}):
                        print(f"[DATA_MAPPER] trace 파일에서 {ref_endpoint} RESPONSE 로드 시도")
                        self._load_from_trace_file(ref_key, "RESPONSE")

            # data mapper 적용
            # request_data를 template로, constraints 적용하여 업데이트
            # 빈 dict를 template로 사용하지 않고 request_data 자체를 업데이트
            updated_request = self.generator._applied_constraints(
                request_data={},  # 이전 요청 데이터는 필요 없음
                template_data=request_data.copy(),  # 현재 요청 데이터를 템플릿으로
                constraints=constraints,
                n=3  # 기본 생성 개수
            )

            print(f"[DATA_MAPPER] 요청 데이터 업데이트 완료")
            print(f"[DATA_MAPPER] 업데이트된 필드: {list(updated_request.keys())}")

            return updated_request

        except Exception as e:
            print(f"[ERROR] _apply_request_constraints 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
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

        # ✅ 전체 점수 (모든 spec 합산) - 추가
        self.global_pass_cnt = 0
        self.global_error_cnt = 0

        # ✅ 각 spec_id별 테이블 데이터 저장 (시나리오 전환 시 결과 유지) - 추가
        self.spec_table_data = {}  # {spec_id: {table_data, step_buffers, scores}}
        if getattr(sys, 'frozen', False):
            # PyInstaller 환경 - 외부 CONSTANTS.py를 직접 로드
            exe_dir = os.path.dirname(sys.executable)
            constants_file = os.path.join(exe_dir, "config", "CONSTANTS.py")

            print(f"[SYSTEM] 외부 CONSTANTS 파일 로드: {constants_file}")

            # 파일이 존재하는지 확인
            if not os.path.exists(constants_file):
                raise FileNotFoundError(f"CONSTANTS.py 파일을 찾을 수 없습니다: {constants_file}")

            # 직접 파일을 읽어서 exec로 실행
            import types
            constants_module = types.ModuleType('config.CONSTANTS')
            with open(constants_file, 'r', encoding='utf-8') as f:
                exec(f.read(), constants_module.__dict__)

            self.CONSTANTS = constants_module
            print(f"[SYSTEM] CONSTANTS 직접 로드 완료 - SPEC_CONFIG: {len(constants_module.SPEC_CONFIG)}개 그룹")
        else:
            # 로컬 환경 - 일반 import
            if 'config.CONSTANTS' in sys.modules:
                del sys.modules['config.CONSTANTS']
            import config.CONSTANTS
            self.CONSTANTS = config.CONSTANTS
            print(f"[SYSTEM] CONSTANTS reload 완료 - SPEC_CONFIG: {len(config.CONSTANTS.SPEC_CONFIG)}개 그룹")
        # ===== 수정 끝 =====
        super().__init__()
        self.embedded = embedded

        # 전체화면 관련 변수 초기화
        self._is_fullscreen = False
        self._saved_geom = None
        self._saved_state = None

        self.webhook_res = None
        self.res = None
        self.radio_check_flag = "video"  # 영상보안 시스템으로 고정

        # ✅ spec_id 초기화 (info_GUI에서 전달받거나 기본값 사용)
        if spec_id:
            self.current_spec_id = spec_id
            print(f"[SYSTEM] 📌 전달받은 spec_id 사용: {spec_id}")
        else:
            self.current_spec_id = "cmgatbdp000bqihlexmywusvq"  # 기본값: 보안용센서 시스템 (7개 API) -> 지금은 잠깐 없어짐
            print(f"[SYSTEM] 📌 기본 spec_id 사용: {self.current_spec_id}")
        self.img_pass = resource_path("assets/image/icon/icn_success.png")
        self.img_fail = resource_path("assets/image/icon/icn_fail.png")
        self.img_none = resource_path("assets/image/icon/icn_basic.png")

        self.flag_opt = self.CONSTANTS.flag_opt
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

    def save_current_spec_data(self):
        """현재 spec의 테이블 데이터와 상태를 저장"""
        if not hasattr(self, 'current_spec_id'):
            return

        # 테이블 데이터 저장
        table_data = []
        for row in range(self.tableWidget.rowCount()):
            row_data = {
                'api_name': self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else "",
                'icon_state': self._get_icon_state(row),
                'retry_count': self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else "0",
                'pass_count': self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else "0",
                'total_count': self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else "0",
                'fail_count': self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else "0",
                'score': self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else "0%",
            }
            table_data.append(row_data)

        # 전체 데이터 저장
        self.spec_table_data[self.current_spec_id] = {
            'table_data': table_data,
            'step_buffers': [buf.copy() for buf in self.step_buffers],
            'total_pass_cnt': self.total_pass_cnt,
            'total_error_cnt': self.total_error_cnt,
        }
        print(f"[DEBUG] {self.current_spec_id} 데이터 저장 완료")

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
        """저장된 spec 데이터 복원 (안전성 강화)"""
        if spec_id not in self.spec_table_data:
            print(f"[RESTORE] {spec_id} 저장된 데이터 없음")
            return False

        saved_data = self.spec_table_data[spec_id]
        print(f"[RESTORE] {spec_id} 데이터 복원 시작")

        # 테이블 복원
        table_data = saved_data['table_data']
        for row, row_data in enumerate(table_data):
            if row >= self.tableWidget.rowCount():
                print(f"[RESTORE] 경고: row={row}가 범위 초과, 건너뜀")
                break

            # API 이름
            api_item = self.tableWidget.item(row, 0)
            if api_item:
                api_item.setText(row_data['api_name'])

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
            icon_label.setPixmap(QIcon(img).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 1, icon_widget)

            # 나머지 컬럼 복원 (안전하게)
            for col, key in [(2, 'retry_count'), (3, 'pass_count'),
                             (4, 'total_count'), (5, 'fail_count'), (6, 'score')]:
                item = self.tableWidget.item(row, col)
                if item:
                    item.setText(row_data[key])
                else:
                    new_item = QTableWidgetItem(row_data[key])
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(row, col, new_item)

        # step_buffers 복원
        self.step_buffers = [buf.copy() for buf in saved_data['step_buffers']]

        # 점수 복원
        self.total_pass_cnt = saved_data['total_pass_cnt']
        self.total_error_cnt = saved_data['total_error_cnt']

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

            # ✅ latest_events 업데이트 (data mapper용)
            if api not in self.latest_events:
                self.latest_events[api] = {}
            self.latest_events[api][direction] = evt

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
        # ===== 디버그 로그 추가 =====
        print(f"[SYSTEM DEBUG] SPEC_CONFIG 개수: {len(self.CONSTANTS.SPEC_CONFIG)}")
        print(f"[SYSTEM DEBUG] 찾을 spec_id: {self.current_spec_id}")
        for i, group in enumerate(self.CONSTANTS.SPEC_CONFIG):
            print(f"[SYSTEM DEBUG] Group {i} keys: {list(group.keys())}")
        # ===== 디버그 로그 끝 =====

        config = {}
        # ===== 수정: self.CONSTANTS 사용 (reload된 CONSTANTS) =====
        for group in self.CONSTANTS.SPEC_CONFIG:
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
        # import spec.Data_request as data_request_module
        # import spec.Schema_response as schema_response_module
        # import spec.Constraints_request as constraints_request_module

        # ✅ 시스템은 응답 검증 + 요청 전송 (outSchema/inData 사용)
        print(f"[SYSTEM] 🔧 타입: 응답 검증 + 요청 전송")
        print(spec_names)
        # ✅ Response 검증용 스키마 로드 (시스템이 플랫폼으로부터 받을 응답 검증) - outSchema
        self.videoOutSchema = getattr(schema_response_module, spec_names[0], [])

        # ✅ Request 전송용 데이터 로드 (시스템이 플랫폼에게 보낼 요청) - inData
        self.videoInMessage = getattr(data_request_module, spec_names[1], [])
        self.videoMessages = getattr(data_request_module, spec_names[2], [])
        self.videoInConstraint = getattr(constraints_request_module, self.current_spec_id + "_inConstraints", [])

        # ✅ Webhook 관련 (현재 미사용)
        # self.videoWebhookSchema = []
        # self.videoWebhookData = []
        # self.videoWebhookInSchema = []
        # self.videoWebhookInData = []

        print(f"[SYSTEM] ✅ 로딩 완료: {len(self.videoMessages)}개 API")
        print(f"[SYSTEM] 📋 API 목록: {self.videoMessages}")
        print(f"[SYSTEM] 🔄 프로토콜 설정: {self.trans_protocols}")

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
        icon_label.setPixmap(QIcon(img).pixmap(16, 16))
        icon_label.setToolTip(msg)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_widget.setLayout(icon_layout)

        self.tableWidget.setCellWidget(row, 1, icon_widget)

        # ✅ 3. 각 컬럼 업데이트 (아이템이 없으면 생성)
        updates = [
            (2, str(retries)),  # 검증 횟수
            (3, str(pass_count)),  # 통과 필드 수
            (4, str(pass_count + error_count)),  # 전체 필드 수
            (5, str(error_count)),  # 실패 필드 수
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

        score_item = self.tableWidget.item(row, 6)
        if score_item is None:
            score_item = QTableWidgetItem(score_text)
            score_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row, 6, score_item)
        else:
            score_item.setText(score_text)

        # ✅ 5. 메시지 저장
        setattr(self, f"step{row + 1}_msg", msg)

        # ✅ 6. UI 즉시 업데이트
        QApplication.processEvents()

        print(f"[TABLE UPDATE] 완료: row={row}")

    def load_test_info_from_constants(self):
        return [
            ("기업명", CONSTANTS.company_name),
            ("제품명", CONSTANTS.product_name),
            ("버전", CONSTANTS.version),
            ("시험유형", CONSTANTS.test_category),
            ("시험대상", CONSTANTS.test_target),
            ("시험범위", CONSTANTS.test_range),
            ("사용자 인증 방식", CONSTANTS.auth_type),
            ("시험 접속 정보", CONSTANTS.url)
        ]

    def create_spec_selection_panel(self, parent_layout):

        """시험 분야 선택 패널 생성"""

        parent_layout.setSpacing(0)  # 라벨-테이블 간격 최소화

        # 시험 분야 확인 문구
        title = QLabel("시험 분야")
        title.setStyleSheet("font-size: 16px; font-family: 'Noto Sans KR'; font-style: normal; font-weight: 500; line-height: normal; letter-spacing: -0.16px; margin-bottom: 6px;")
        parent_layout.addWidget(title)

        # 시험 분야명 테이블만 추가 (회색 박스 제거)
        field_group = self.create_test_field_group()
        field_group.setStyleSheet("QGroupBox { border: none; background: transparent; margin: 0; padding: 0; }")  # ← 회색 박스 제거
        parent_layout.addWidget(field_group)


    def create_group_selection_table(self):
        """시험 분야명 테이블 - 투명 배경 효과"""
        group_box = QWidget()
        group_box.setFixedSize(459, 220)
        group_box.setStyleSheet("background: transparent;")  # ✅ 투명 배경

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

        # ✅ 플랫폼과 동일한 스타일 적용
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
        group_items = [
            (g.get("group_name", "미지정 그룹"), g.get("group_id", ""))
            for g in CONSTANTS.SPEC_CONFIG
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

        selected_group = next(
            (g for g in CONSTANTS.SPEC_CONFIG if g.get("group_name") == group_name), None
        )

        if selected_group:
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

        group_box = QWidget()  # ← QGroupBox에서 QWidget로 변경
        group_box.setFixedSize(459, 760)  # 플랫폼과 동일한 크기
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # ← 여백 제거
        layout.setSpacing(0)  # ← 간격 제거


        self.test_field_table = QTableWidget(0, 1)
        self.test_field_table.setHorizontalHeaderLabels(["시험 시나리오"])
        self.test_field_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)
        self.test_field_table.verticalHeader().setVisible(False)
        self.test_field_table.setFixedHeight(759)


        # SPEC_CONFIG에서 spec_id와 config 추출
        spec_items = []
        for group_data in CONSTANTS.SPEC_CONFIG:
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
            description_with_role = f"{description} (요청 검증)"
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

                print(f"[SELECT] 🔄 시험 분야 전환: {self.current_spec_id} → {new_spec_id}")

                # ✅ 1. 현재 spec의 테이블 데이터 저장
                self.save_current_spec_data()

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

                # ✅ 5. 테이블 완전 재구성 (이전 데이터 완전 삭제)
                print(f"[SELECT] 테이블 완전 재구성 시작")
                self.update_result_table_structure(self.videoMessages)

                # ✅ 6. 저장된 데이터 복원 시도
                restored = self.restore_spec_data(new_spec_id)

                if not restored:
                    print(f"[SELECT] 저장된 데이터 없음 - 초기화")
                    # 점수 초기화
                    self.total_pass_cnt = 0
                    self.total_error_cnt = 0

                    # step_buffers 초기화
                    self.step_buffers = [
                        {"data": "", "error": "", "result": "PASS"} for _ in range(len(self.videoMessages))
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

                # ✅ 10. 결과 텍스트 초기화
                self.valResult.clear()
                self.valResult.append(f"✅ 시스템 전환 완료: {self.spec_description}")
                self.valResult.append(f"📋 Spec ID: {self.current_spec_id}")
                self.valResult.append(f"📊 API 개수: {len(self.videoMessages)}개")
                self.valResult.append(f"📋 API 목록: {self.videoMessages}\n")

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
            display_name = f"{row + 1}. {api_name}"

            # 컬럼 0: API 명 - 강제로 새로 생성!
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, api_item)

            print(f"[TABLE] Row {row}: {display_name} 설정 완료")

            # 컬럼 1: 결과 아이콘
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

            # 컬럼 2-6: 검증 횟수, 통과/전체/실패 필드 수, 평가 점수
            col_values = [
                (2, "0"),  # 검증 횟수
                (3, "0"),  # 통과 필드 수
                (4, "0"),  # 전체 필드 수
                (5, "0"),  # 실패 필드 수
                (6, "0%")  # 평가 점수
            ]

            for col, value in col_values:
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # 컬럼 7: 상세 내용 버튼
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

            self.tableWidget.setCellWidget(row, 7, container)

            # 행 높이 설정
            self.tableWidget.setRowHeight(row, 28)

        print(f"[TABLE] 테이블 재구성 완료: {self.tableWidget.rowCount()}개 행")

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

    def post(self, path, json_data, time_out):
        self.res = None
        headers = CONSTANTS.headers.copy()
        auth = None
        if self.r2 == "B":  # Bearer
            if self.token:
                headers['Authorization'] = f"Bearer {self.token}"
        elif self.r2 == "D":  # Digest
            auth = HTTPDigestAuth(self.digestInfo[0], self.digestInfo[1])
        # self.r2 == "None"이면 그대로 None

        try:
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

        # ✅ Webhook 처리 (transProtocol 기반으로만 판단)
        try:
            json_data_dict = json.loads(json_data.decode('utf-8'))
            trans_protocol = json_data_dict.get("transProtocol", {})    # 이 부분 수정해야함
            
            if not trans_protocol:
                if self.cnt < len(self.trans_protocols):
                    current_protocol = self.trans_protocols[self.cnt]

                    if current_protocol == "WebHook":
                        trans_protocol = {
                            "transProtocolType": "WebHook",
                            "transProtocolDesc": "https://127.0.0.1:8008"
                        }
                        json_data_dict["transProtocol"] = trans_protocol
                        # 재직렬화
                        json_data = json.dumps(json_data_dict).encode('utf-8')
                        print(f"[DEBUG] [post] transProtocol 설정 추가됨: {trans_protocol}")
            if trans_protocol:
                trans_protocol_type = trans_protocol.get("transProtocolType", {})
                # 웹훅 서버 시작 (transProtocolType이 WebHook인 경우만)
                if "WebHook".lower() in str(trans_protocol_type).lower():
                    time.sleep(0.1)
                    path_tmp = trans_protocol.get("transProtocolDesc", {})
                    # http/https 접두어 보정
                    if not path_tmp or str(path_tmp).strip() in ["None", "", "desc"]:
                        path_tmp = "https://127.0.0.1:8008"
                    if not str(path_tmp).startswith("http"):
                        path_tmp = "https://" + str(path_tmp)
                    parsed = urlparse(str(path_tmp))
                    url = parsed.hostname if parsed.hostname is not None else "127.0.0.1"
                    port = parsed.port if parsed.port is not None else 8008

                    msg = {}
                    self.webhook_flag = True
                    self.step_buffers[self.cnt]["is_webhook_api"] = True

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

    # 웹훅 검증
    def get_webhook_result(self):
        tmp_webhook_res = json.dumps(self.webhook_res, indent=4, ensure_ascii=False)
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

            # (RealtimeVideoEventInfos 웹훅은 spec_002_webhookSchema[0])
            if len(self.webhookSchema) > 0:
                schema_to_check = self.webhookSchema[0]  # 웹훅 스키마는 첫 번째 요소
                print(f"[DEBUG] 사용 스키마: webhookSchema[0]")
                if isinstance(schema_to_check, dict):
                    schema_keys = list(schema_to_check.keys())[:5]
                    print(f"[DEBUG] 웹훅 스키마 필드 (first 5): {schema_keys}")

        # 실제 검증
        if len(self.webhookSchema) > 0:
            schema_to_check = self.webhookSchema[0]
            val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(
                schema=schema_to_check,
                data=self.webhook_res,
                flag=self.flag_opt,
                reference_context=self.reference_context
            )

            if not hasattr(self, '_webhook_debug_printed') or not self._webhook_debug_printed:
                print(f"[DEBUG] 웹훅 검증 결과: {val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
        else:
            val_result, val_text, key_psss_cnt, key_error_cnt = "FAIL", "webhookSchema not found", 0, 0
            if not hasattr(self, '_webhook_debug_printed') or not self._webhook_debug_printed:
                print(f"[DEBUG] webhookSchema가 없습니다!")

        if not hasattr(self, '_webhook_debug_printed') or not self._webhook_debug_printed:
            print(f"[DEBUG] ==========================================\n")

        self.valResult.append(message_name)
        self.valResult.append("\n=== 웹훅 이벤트 데이터 ===")
        self.valResult.append(tmp_webhook_res)
        self.valResult.append(f"\n웹훅 검증 결과: {val_result}")

        if val_result == "FAIL":
            self.valResult.append("\n⚠️  웹훅 데이터 검증 실패")
        else:
            self.valResult.append("\n✅ 웹훅 데이터 검증 성공")

        # ✅ 이번 회차의 결과만 전체 점수에 추가 (누적된 값이 아님!)
        self.total_error_cnt += key_error_cnt
        self.total_pass_cnt += key_psss_cnt

        # ✅ 전체 누적 점수 업데이트 추가
        self.global_error_cnt += key_error_cnt
        self.global_pass_cnt += key_psss_cnt
        # 평가 점수 디스플레이 업데이트
        self.update_score_display()

        total_fields = self.total_pass_cnt + self.total_error_cnt
        if total_fields > 0:
            score = (self.total_pass_cnt / total_fields) * 100
        else:
            score = 0
        self.valResult.append("Score : " + str(score))
        self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
            self.total_error_cnt) + "(누적 오류 필드 수)\n")

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
                # 웹훅 결과를 기존 누적에 추가
                self.step_pass_counts[self.webhook_cnt] += key_psss_cnt
                self.step_error_counts[self.webhook_cnt] += key_error_cnt

                # 누적된 총 필드 수로 테이블 업데이트
                accumulated_pass = self.step_pass_counts[self.webhook_cnt]
                accumulated_error = self.step_error_counts[self.webhook_cnt]
            else:
                # 누적 배열이 없으면 웹훅 결과만 사용
                accumulated_pass = key_psss_cnt
                accumulated_error = key_error_cnt

            if self.webhook_cnt < len(self.num_retries_list):
                current_retries = self.num_retries_list[self.webhook_cnt]
            else:
                current_retries = 1

            # 누적된 필드 수로 테이블 업데이트
            self.update_table_row_with_retries(self.webhook_cnt, val_result, accumulated_pass, accumulated_error,
                                               tmp_webhook_res, self._to_detail_text(val_text), current_retries)

        # step_buffers 업데이트 추가 (실시간 모니터링과 상세보기 일치)
        if self.webhook_cnt < len(self.step_buffers):
            webhook_data_text = tmp_webhook_res
            webhook_error_text = self._to_detail_text(val_text) if val_result == "FAIL" else "오류가 없습니다."
            # ✅ 웹훅 이벤트 데이터를 명확히 표시
            self.step_buffers[self.webhook_cnt]["data"] += f"\n\n--- Webhook 이벤트 데이터 ---\n{webhook_data_text}"
            self.step_buffers[self.webhook_cnt]["error"] += f"\n\n--- Webhook 검증 ---\n{webhook_error_text}"   # 얘가 문제임 화딱지가 난다
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
                    self.message_name = "step " + str(self.cnt + 1) + ": " + self.message[self.cnt] + retry_info
                else:
                    self.message_name = f"step {self.cnt + 1}: (index out of range)" + retry_info

                # if self.tmp_msg_append_flag:
                #     self.valResult.append(self.message_name)
                if self.cnt == 0 and self.current_retry == 0:
                    self.tmp_msg_append_flag = True

                # 시스템이 플랫폼에 요청 전송
                current_timeout = self.time_outs[self.cnt] / 1000 if self.cnt < len(self.time_outs) else 5.0
                path = self.pathUrl + "/" + (self.message[self.cnt] if self.cnt < len(self.message) else "")
                inMessage = self.inMessage[self.cnt] if self.cnt < len(self.inMessage) else {}
                # ✅ Data Mapper 적용 - 이전 응답 데이터로 요청 업데이트 (trace 파일 != ui)
                self.generator.latest_events = self.latest_events
                #inMessage = self._apply_request_constraints(inMessage, self.cnt)

                json_data = json.dumps(inMessage).encode('utf-8')

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
                # ✅ 전체 누적 점수 업데이트 추가
                self.global_error_cnt += add_err
                self.global_pass_cnt += 0

                # 평가 점수 디스플레이 업데이트
                self.update_score_display()

                total_fields = self.total_pass_cnt + self.total_error_cnt
                if total_fields > 0:
                    score = (self.total_pass_cnt / total_fields) * 100
                else:
                    score = 0
                self.valResult.append("Score : " + str(score))
                self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 검증 통과 필드 수), " + str(
                    self.total_error_cnt) + "(누적 검증 오류 필드 수)\n")

                # 재시도 카운터 증가
                self.current_retry += 1

                # 재시도 완료 여부 확인
                if (self.cnt < len(self.num_retries_list) and
                        self.current_retry >= self.num_retries_list[self.cnt]):
                    # 모든 재시도 완료 - 버퍼에 최종 결과 저장
                    self.step_buffers[self.cnt]["data"] = "타임아웃으로 인해 수신된 데이터가 없습니다."
                    current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                    self.step_buffers[self.cnt]["error"] = f"Message Missing! - 모든 시도({current_retries}회)에서 타임아웃 발생"
                    self.step_buffers[self.cnt]["result"] = "FAIL"
                    self.step_buffers[self.cnt]["events"] = list(self.trace.get(self.cnt, []))

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
                    if total_fields > 0:
                        final_score = (self.total_pass_cnt / total_fields) * 100
                    else:
                        final_score = 0

                    # ✅ JSON 결과 자동 저장 추가
                    try:
                        self.run_status = "완료"
                        result_json = build_result_json(self)
                        json_path = os.path.join(result_dir, "response_results.json")
                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump(result_json, f, ensure_ascii=False, indent=2)
                        print(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                        self.valResult.append(f"\n📄 결과 파일 저장 완료: {json_path}")
                    except Exception as e:
                        print(f"❌ JSON 저장 중 오류 발생: {e}")
                        import traceback
                        traceback.print_exc()
                        self.valResult.append(f"\n⚠️ 결과 저장 실패: {str(e)}")

                    self.sbtn.setEnabled(True)
                    self.stop_btn.setDisabled(True)


            # 응답이 도착한 경우 처리
            elif self.post_flag == True:
                if self.res != None:
                    # 응답 처리 시작
                    if self.res != None:
                        # 응답 처리 시작
                        self.processing_response = True

                        if self.cnt == 0 or self.tmp_msg_append_flag:
                            self.valResult.append(self.message_name)

                        res_data = self.res.text

                        try:
                            res_data = json.loads(res_data)
                        except Exception as e:
                            self._append_text(f"응답 JSON 파싱 오류: {e}")
                            self._append_text({"raw_response": self.res.text})
                            self.post_flag = False
                            self.processing_response = False
                            self.current_retry += 1
                            return

                        self._push_event(self.cnt, "RESPONSE", res_data)

                        # 현재 재시도 정보
                        current_retries = self.num_retries_list[self.cnt] if self.cnt < len(
                            self.num_retries_list) else 1
                        current_protocol = self.trans_protocols[self.cnt] if self.cnt < len(
                            self.trans_protocols) else "Unknown"

                        # 단일 응답에 대한 검증 처리
                        tmp_res_auth = json.dumps(res_data, indent=4, ensure_ascii=False)

                    # ✅ 디버깅: 어떤 스키마로 검증하는지 확인
                    if self.current_retry == 0:  # 첫 시도에만 출력
                        print(f"\n[DEBUG] ========== 스키마 검증 디버깅 ==========")
                        print(
                            f"[DEBUG] cnt={self.cnt}, API={self.message[self.cnt] if self.cnt < len(self.message) else 'N/A'}")
                        print(f"[DEBUG] webhook_flag={self.webhook_flag}")
                        print(f"[DEBUG] current_protocol={current_protocol}")
                        print(f"[DEBUG] outSchema 총 개수={len(self.outSchema)}")

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
                        resp_rules = get_validation_rules(
                            spec_id=self.current_spec_id,
                            api_name=self.message[self.cnt] if self.cnt < len(self.message) else "",

                            direction="out"  # 응답 검증

                        ) or {}
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
                        val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(
                            self.outSchema[self.cnt],
                            res_data,
                            self.flag_opt,
                            validation_rules=resp_rules,
                            reference_context=self.reference_context
                        )
                    except TypeError as te:
                        print(f"[ERROR] 응답 검증 중 TypeError 발생: {te}, 일반 검증으로 재시도")
                        val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(
                            self.outSchema[self.cnt],
                            res_data,
                            self.flag_opt
                        )
                    if self.message[self.cnt] == "Authentication":
                        self.handle_authentication_response(res_data)

                    if self.current_retry == 0:  # 첫 시도에만 출력
                        print(f"[DEBUG] 검증 결과: {val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
                        print(f"[DEBUG] ==========================================\n")

                    # ✅ 의미 검증: 응답 코드가 성공인지 확인
                    if isinstance(res_data, dict):
                        response_code = str(res_data.get("code", "")).strip()
                        response_message = res_data.get("message", "")

                        # 성공 코드가 아니면 FAIL 처리 (10/29)
                        if response_code not in ["200", "201", "성공", "Success", ""]:
                            # print(f"[SYSTEM] 응답 코드 검증 실패: code={response_code}, message={response_message}")
                            val_result = "FAIL"
                            # 기존 오류 메시지에 응답 코드 오류 추가
                            code_error_msg = f"응답 실패: code={response_code}, message={response_message}"
                            if isinstance(val_text, str):
                                val_text = code_error_msg if val_text == "오류가 없습니다." else f"{code_error_msg}\n\n{val_text}"
                            elif isinstance(val_text, list):
                                val_text.insert(0, code_error_msg)
                            else:
                                val_text = code_error_msg

                            # 응답 실패는 오류로 카운트 (스키마는 맞지만 의미상 실패)
                            key_error_cnt += 1

                    # 이번 시도의 결과
                    final_result = val_result

                    # 누적 카운트 로직
                    if not hasattr(self, 'step_pass_counts'):
                        api_count = len(self.videoMessages)
                        self.step_pass_counts = [0] * api_count
                        self.step_error_counts = [0] * api_count
                        self.step_pass_flags = [0] * api_count

                    # 이번 시도 결과를 누적
                    self.step_pass_counts[self.cnt] += key_psss_cnt
                    self.step_error_counts[self.cnt] += key_error_cnt

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
                        error_text = "오류가 없습니다."

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
                    message_name = "step " + str(self.cnt + 1) + ": " + self.message[self.cnt]
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

                    # ✅ 웹훅 API인 경우 명확하게 구분 표시 (transProtocol 기반으로만 판단)
                    if current_protocol == "WebHook":
                        self.valResult.append(f"\n=== 웹훅 구독 요청 응답 ===")
                        self.valResult.append(f"[시도 {self.current_retry + 1}/{current_retries}]")
                    else:
                        self.valResult.append(f"\n검증 진행: {self.current_retry + 1}/{current_retries}회")

                    self.valResult.append(f"프로토콜: {current_protocol}")
                    self.valResult.append("\n" + data_text)
                    self.valResult.append(f"\n검증 결과: {final_result}")

                    # ✅ 이번 회차의 결과만 현재 spec 점수에 추가
                    self.total_error_cnt += key_error_cnt
                    self.total_pass_cnt += key_psss_cnt

                    # ✅ 평가 점수 디스플레이 업데이트 (분야별만)
                    self.update_score_display()

                    total_fields = self.total_pass_cnt + self.total_error_cnt
                    if total_fields > 0:
                        score = (self.total_pass_cnt / total_fields) * 100
                    else:
                        score = 0
                    self.valResult.append("Score : " + str(score))
                    self.valResult.append(
                        "Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                            self.total_error_cnt) + "(누적 오류 필드 수)\n")

                    # 재시도 카운터 증가
                    self.current_retry += 1

                    # ✅ 현재 API의 모든 재시도가 완료되었는지 확인
                    if (self.cnt < len(self.num_retries_list) and
                            self.current_retry >= self.num_retries_list[self.cnt]):
                        # ✅ 모든 재시도 완료 - 이제 전체 점수에 반영!
                        print(f"[SCORE] API {self.cnt} 완료: pass={total_pass_count}, error={total_error_count}")

                        # ✅ 전체 누적 점수 업데이트 (재시도 완료 후 한 번만!)
                        self.global_error_cnt += total_error_count
                        self.global_pass_cnt += total_pass_count

                        print(f"[SCORE] 전체 점수 업데이트: pass={self.global_pass_cnt}, error={self.global_error_cnt}")

                        # ✅ 전체 점수 포함하여 디스플레이 업데이트
                        self.update_score_display()

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

                    if self.webhook_flag and self.webhook_res is not None:
                        self.get_webhook_result()

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
                try:
                    self.run_status = "완료"
                    result_json = build_result_json(self)
                    json_path = os.path.join(result_dir, "response_results.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result_json, f, ensure_ascii=False, indent=2)
                    print(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                    self.valResult.append(f"\n📄 결과 파일 저장 완료: {json_path}")
                except Exception as e:
                    print(f"❌ JSON 저장 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    self.valResult.append(f"\n⚠️ 결과 저장 실패: {str(e)}")

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
            msg.setInformativeText(f"Error at step {self.cnt + 1}: {str(err)}")
            msg.setWindowTitle("Error")
            msg.exec_()
            self.tick_timer.stop()
            self.valResult.append(f"검증 절차가 중지되었습니다. (오류 위치: Step {self.cnt + 1})")
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

        # 배경 이미지 설정
        self.setObjectName("system_main")
        self.setAttribute(Qt.WA_StyledBackground, True)

        bg_path = resource_path("assets/image/common/bg.png").replace("\\", "/")

        self.setStyleSheet(f"""
            #system_main {{
                background-image: url('{bg_path}');
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
            }}
        """)


        if not self.embedded:
            self.setWindowTitle('시스템 연동 검증')


        # 메인 레이아웃
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        mainLayout.setSpacing(0)  # 간격 제거

        # 헤더 영역 (1680x56px)
        header_container = QWidget()
        header_container.setFixedSize(1680, 56)
        header_container_layout = QHBoxLayout()
        header_container_layout.setContentsMargins(0, 8, 0, 0) # 왼, 위, 오, 아

        header_container_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedSize(1680, 56)


        # 헤더 레이아웃 (로고 + 타이틀)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header_layout.setSpacing(10)


        # 헤더 로고 (36x36px)

        logo_label = QLabel(header_widget)
        logo_pixmap = QPixmap(resource_path("assets/image/common/header_logo.png"))
        logo_label.setPixmap(logo_pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(36, 36)
        header_layout.addWidget(logo_label)

        # 헤더 타이틀
        self.title_label = QLabel('시스템 연동 검증 시작하기', header_widget)
        self.title_label.setAlignment(Qt.AlignVCenter)
        title_style = """
            color: #FFF;
            font-family: "Noto Sans KR";
            font-size: 18px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
        """
        self.title_label.setStyleSheet(title_style)
        header_layout.addWidget(self.title_label)

        header_container_layout.addWidget(header_widget)
        header_container.setLayout(header_container_layout)

        mainLayout.addWidget(header_container)

        # ✅ 배경을 칠할 전용 컨테이너(헤더 제외 영역)

        bg_root = QWidget()
        bg_root.setObjectName("bg_root")
        bg_root.setAttribute(Qt.WA_StyledBackground, True)
        bg_root_layout = QVBoxLayout()
        bg_root_layout.setContentsMargins(0, 0, 0, 0)
        bg_root_layout.setSpacing(0)


        # 2컬럼 레이아웃 생성
        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(0)


        # 왼쪽 컬럼 (479x906)
        left_col = QWidget()
        left_col.setFixedSize(479, 906)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # 시험 분야 선택 영역
        self.create_spec_selection_panel(left_layout)
        left_layout.addStretch()

        # 오른쪽 컬럼 (1112x906)
        right_col = QWidget()
        right_col.setFixedSize(1112, 906)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        # 시험 결과 테이블 및 기타 정보
        # 시험 API 라벨 추가
        api_label = QLabel('시험 API')
        api_label.setStyleSheet('font-size: 16px; font-family: "Noto Sans KR"; font-weight: 500; color: #222; margin-bottom: 6px;')
        right_layout.addWidget(api_label)
        self.init_centerLayout()
        contentWidget = QWidget()
        contentWidget.setLayout(self.centerLayout)
        right_layout.addWidget(contentWidget)

        # 수신 메시지 실시간 모니터링
        monitor_label = QLabel("수신 메시지 실시간 모니터링")
        monitor_label.setStyleSheet('font-size: 16px; font-family: "Noto Sans KR"; font-weight: 500; color: #222; margin-top: 20px; margin-bottom: 6px;')
        right_layout.addWidget(monitor_label)

        self.valResult = QTextBrowser(self)
        self.valResult.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.valResult.setFixedHeight(174)
        self.valResult.setFixedWidth(1064)  # 가로 길이 1064px로 고정
        self.valResult.setStyleSheet(f"""
            background: #FFF;
            border-radius: 8px;
            border: 1px solid #CECECE;
            font-size: 15px;
            color: #222;
        """)
        right_layout.addWidget(self.valResult, 1)

        # 시험 결과
        self.valmsg = QLabel('시험 점수 요약', self)
        self.valmsg.setStyleSheet('font-size: 16px; font-family: "Noto Sans KR"; font-weight: 500; color: #222; margin-top: 20px; margin-bottom: 6px;')
        right_layout.addWidget(self.valmsg)  # ← 오른쪽에 추가!


        # 평가 점수 표시
        spec_score_group = self.create_spec_score_display_widget()
        right_layout.addWidget(spec_score_group)
        # 전체 점수 표시
        total_score_group = self.create_total_score_display_widget()
        right_layout.addWidget(total_score_group)

        # ✅ 버튼 그룹 (이미지 기반으로 변경)
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
                background-size: contain;
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
        self.sbtn.clicked.connect(self.start_btn_clicked)

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
                background-size: contain;
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
                background-size: contain;
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
                background-size: contain;
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
        
        buttonGroup.setLayout(buttonLayout)
        right_layout.addSpacing(20)
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


        QTimer.singleShot(100, self.select_first_scenario)

        if not self.embedded:
            self.show()

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

            print(f"[DEBUG] 초기 시나리오 자동 선택 완료: {self.spec_description}")
            QApplication.processEvents()

        except Exception as e:
            print(f"[ERROR] 초기 시나리오 선택 실패: {e}")
            import traceback
            traceback.print_exc()
    def init_centerLayout(self):
        # 표 형태로 변경 - 동적 API 개수
        api_count = len(self.videoMessages)
        self.tableWidget = QTableWidget(api_count, 8)
        self.tableWidget.setHorizontalHeaderLabels(
            ["API 명", "결과", "검증 횟수", "통과 필드 수", "전체 필드 수", "실패 필드 수", "평가 점수", "상세 내용"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))

        # 헤더 리사이즈 모드를 Fixed로 설정 (이게 핵심!)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # 테이블 크기 설정
        self.tableWidget.setFixedHeight(274)
        self.tableWidget.setFixedWidth(1064)

        main_path = resource_path("assets/image/test_runner/main_table.png").replace("\\", "/")
        self.tableWidget.setStyleSheet(f"""
            QTableWidget {{
                background: #FFF;
                background-image: url('{main_path}');
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
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

        # 단계명 리스트 (동적으로 로드된 API 이름 사용)
        self.step_names = self.videoMessages
        for i, name in enumerate(self.step_names):
            # API 명
            self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{i + 1}. {name}"))
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

            # 메인 - 시험 결과 상세 결과 버튼 (중앙 정렬을 위한 위젯 컨테이너) -  상세 내용 확인
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

            self.tableWidget.setCellWidget(i, 7, container)

        # 결과 컬럼만 클릭 가능하도록 설정 (기존 기능 유지)
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)

        # centerLayout을 초기화하고 테이블 추가
        self.centerLayout = QVBoxLayout()
        self.centerLayout.setContentsMargins(0, 0, 0, 0)  # ← 추가
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

            # 웹훅 스키마 데이터 가져오기 (transProtocol 기반으로만 판단)
            webhook_schema = None
            if row < len(self.trans_protocols):
                current_protocol = self.trans_protocols[row]
                if current_protocol == "WebHook":
                    try:
                        # import spec.Schema_response as schema_response_module
                        webhook_schema = f"{self.current_spec_id}_webhook_inSchema"
                        self.webhookInSchema = getattr(schema_response_module, webhook_schema, [])

                        # 확인하고 있는 부분 - 현재 여기 기능은 platformVal에 내장되어 있는 상황
                            # webhook_indices = [i for i, name in enumerate(self.videoMessages) if name is not None]
                            # if webhook_indices:
                            #     print(f"[DEBUG] 웹훅 스키마 인덱스: {webhook_indices}")
                            # else:
                            #     print(f"[DEBUG] 웹훅 스키마 인덱스가 없습니다.")
                        webhook_schema = self.webhookInSchema[0] if len(self.webhookInSchema) > 0 else None
                    except Exception as e:
                        print(f"[ERROR] 웹훅 스키마 로드 실패: {e}")
                        import traceback
                        traceback.print_exc()
                        webhook_schema = None

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

        # ✅ 1️⃣ 분야별 점수 (현재 spec만)
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

            # ✅ 디버그 로그 추가
            print(
                f"[SCORE UPDATE] 분야별 - pass: {self.total_pass_cnt}, error: {self.total_error_cnt}, score: {spec_score:.1f}%")
            print(
                f"[SCORE UPDATE] 전체 - pass: {self.global_pass_cnt}, error: {self.global_error_cnt}, score: {global_score:.1f}%")

    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭 시 호출되는 함수"""
        if col == 1:  # 결과 컬럼 클릭 시에만 동작
            msg = getattr(self, f"step{row + 1}_msg", "")
            if msg:
                api_name = self.step_names[row] if row < len(self.step_names) else f"Step {row + 1}"
                CustomDialog(msg, api_name)

    def create_spec_score_display_widget(self):
        """메인 화면에 표시할 시험 분야별 평가 점수 위젯 생성"""

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

        # ✅ 분야별 점수 아이콘 추가
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

        # 구분선 추가
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

        # ✅ 아이콘을 위한 수직 레이아웃
        icon_vlayout = QVBoxLayout()
        icon_vlayout.setContentsMargins(0, 0, 0, 0)
        icon_vlayout.setSpacing(0)
        icon_vlayout.addSpacing(0)
        icon_vlayout.addWidget(icon_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
        icon_vlayout.addStretch()

        # ✅ 아이콘 + 분야명 레이아웃
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
        """메인 화면에 표시할 전체 평가 점수 위젯 생성"""
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

        # ✅ 전체 점수 아이콘 추가
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

        # 구분선 추가
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

        # ✅ 아이콘을 위한 수직 레이아웃
        icon_vlayout = QVBoxLayout()
        icon_vlayout.setContentsMargins(0, 0, 0, 0)
        icon_vlayout.setSpacing(0)
        icon_vlayout.addSpacing(0)
        icon_vlayout.addWidget(icon_label, alignment=Qt.AlignHCenter | Qt.AlignTop)
        icon_vlayout.addStretch()

        # ✅ 아이콘 + 전체 점수 텍스트 레이아웃
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

    def start_btn_clicked(self):
        """평가 시작 버튼 클릭"""
        # ✅ 1. 시나리오 선택 확인
        if not hasattr(self, 'current_spec_id') or not self.current_spec_id:
            QMessageBox.warning(self, "알림", "시험 시나리오를 먼저 선택하세요.")
            return

        print(f"[START] 시험 시작: {self.current_spec_id} - {self.spec_description}")
        self.update_result_table_structure(self.videoMessages)

        # ✅ 2. trace 디렉토리 초기화
        self._clean_trace_dir_once()

        # ✅ 3. JSON 데이터 준비
        json_to_data("video")

        # ✅ 4. 버튼 상태 변경
        self.sbtn.setDisabled(True)
        self.stop_btn.setEnabled(True)

        # ✅ 5. 이전 시험 결과가 global 점수에 포함되어 있으면 제거
        if self.current_spec_id in self.spec_table_data:
            prev_data = self.spec_table_data[self.current_spec_id]
            prev_pass = prev_data.get('total_pass_cnt', 0)
            prev_error = prev_data.get('total_error_cnt', 0)
            print(f"[SCORE RESET] 기존 {self.current_spec_id} 점수 제거: pass={prev_pass}, error={prev_error}")

            # ✅ global 점수에서 해당 spec 점수 제거
            self.global_pass_cnt = max(0, self.global_pass_cnt - prev_pass)
            self.global_error_cnt = max(0, self.global_error_cnt - prev_error)

            print(f"[SCORE RESET] 조정 후 global 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}")

        # ✅ 6. 현재 spec의 점수만 초기화 (global은 유지)
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.cnt = 0
        self.current_retry = 0
        self.time_pre = 0
        self.cnt_pre = 0
        self.post_flag = False
        self.processing_response = False
        self.message_in_cnt = 0
        self.message_error = []
        self.res = None
        self.webhook_res = None
        self.realtime_flag = False
        self.tmp_msg_append_flag = False

        # ✅ 7. 현재 spec에 맞게 누적 카운트 초기화
        api_count = len(self.videoMessages)
        self.step_pass_counts = [0] * api_count
        self.step_error_counts = [0] * api_count
        self.step_pass_flags = [0] * api_count

        # ✅ 8. step_buffers 재생성 (현재 API 개수에 맞게)
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS"} for _ in range(api_count)
        ]

        # ✅ 9. trace 초기화
        self.trace.clear()
        self.latest_events = {}

        # ✅ 10. 테이블 초기화
        print(f"[START] 테이블 초기화: {api_count}개 API")
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

            # 카운트 초기화
            for col, value in [(2, "0"), (3, "0"), (4, "0"), (5, "0"), (6, "0%")]:
                if self.tableWidget.item(i, col):
                    self.tableWidget.item(i, col).setText(value)

        # ✅ 11. 인증 정보 설정
        auth_temp, auth_temp2 = set_auth("config/config.txt")
        self.digestInfo = [auth_temp2[0], auth_temp2[1]]
        self.token = auth_temp

        # ✅ 12. 평가 점수 디스플레이 초기화 (전체 점수 포함)
        self.update_score_display()

        # ✅ 13. 결과 텍스트 초기화
        self.valResult.clear()

        # ✅ 14. URL 설정
        self.pathUrl = CONSTANTS.url

        # ✅ 15. 시작 메시지
        self.valResult.append("=" * 60)
        self.valResult.append(f"🚀 시험 시작: {self.spec_description}")
        self.valResult.append(f"📋 Spec ID: {self.current_spec_id}")
        self.valResult.append(f"📊 API 개수: {len(self.videoMessages)}개")
        self.valResult.append(f"📋 API 목록: {self.videoMessages}")
        self.valResult.append(f"📊 전체 누적 점수: {self.global_pass_cnt}(통과) / {self.global_error_cnt}(실패)")
        self.valResult.append("=" * 60)
        self.valResult.append("\n시스템이 플랫폼에 요청을 전송하여 응답을 검증합니다\n")

        # ✅ 16. 타이머 시작 (1초 간격)
        self.tick_timer.start(1000)

        print(f"[START] 타이머 시작 완료")
        print(f"[START] 현재 global 점수: pass={self.global_pass_cnt}, error={self.global_error_cnt}")

    def stop_btn_clicked(self):
        self.tick_timer.stop()
        self.valResult.append("검증 절차가 중지되었습니다.")
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)

        self.save_current_spec_data()

        # ✅ JSON 결과 저장 추가
        try:
            self.run_status = "진행중"
            result_json = build_result_json(self)
            json_path = os.path.join(result_dir, "response_results.json")
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
        def init_win(self):
            """검증 시작 전 초기화"""
            self.cnt = 0
            self.current_retry = 0

            # 현재 spec의 API 개수에 맞게 버퍼 생성
            api_count = len(self.videoMessages) if self.videoMessages else 0
            print(f"[INIT] 초기화: {api_count}개 API")

            # 버퍼 초기화
            self.step_buffers = [
                {"data": "", "result": "", "error": ""} for _ in range(api_count)
            ]

            # 누적 카운트 초기화
            self.step_pass_counts = [0] * api_count
            self.step_error_counts = [0] * api_count
            self.step_pass_flags = [0] * api_count

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

                for col, value in ((2, "0"), (3, "0"), (4, "0"), (5, "0"), (6, "0%")):
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

    def resizeEvent(self, event):
        """창 크기 변경 시 반응형 UI 조정"""
        try:
            super().resizeEvent(event)

            # 테이블 위젯 크기 조정
            # if hasattr(self, 'tableWidget'):
                # 현재 창 너비의 95%를 테이블 너비로 설정
            # new_width = int(self.width() * 0.95)
            # new_width = max(950, new_width)  # 최소 950px

                # 컬럼 너비를 창 크기에 맞춰 조정
            # total_width = new_width - 50  # 여백 고려
            # col_widths = [0.22, 0.09, 0.10, 0.11, 0.11, 0.10, 0.11, 0.16]  # 비율
            # for col, ratio in enumerate(col_widths):
            # self.tableWidget.setColumnWidth(col, int(total_width * ratio))

        except Exception as e:
            print(f"resizeEvent 오류: {e}")

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
        reply = QMessageBox.question(self, '프로그램 종료',
                                     '정말로 프로그램을 종료하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            result_payload = self.build_result_payload()
            QApplication.quit()

    def get_setting(self):
        self.setting_variables = QSettings('My App', 'Variable')
        self.system = "video"  # 고정

        # 기본 시스템 설정
        self.radio_check_flag = "video"
        self.message = self.videoMessages
        self.inMessage = self.videoInMessage
        self.outSchema = self.videoOutSchema
        self.inCon = self.videoInConstraint

        # 이 부분 수정해야함
        try:
            webhook_schema_name = f"{self.current_spec_id}_webhook_inSchema"
            self.webhookInSchema = getattr(schema_response_module, webhook_schema_name, [])
        except Exception as e:
            print(f"Error loading webhook schema: {e}")
            self.webhookInSchema = []

        self.webhookSchema = self.webhookInSchema

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