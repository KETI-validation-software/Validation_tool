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
from core.system_state_manager import SystemStateManager
from requests.auth import HTTPDigestAuth
import config.CONSTANTS as CONSTANTS
from core.validation_registry import get_validation_rules
from pathlib import Path
import spec.Data_request as data_request_module
import spec.Schema_response as schema_response_module
import spec.Constraints_request as constraints_request_module

class CommonMainUI(QWidget):
    def __init__(self):
        super().__init__()
        # 서브클래스에서 오버라이드 가능한 속성
        self.window_title = '시스템 연동 검증'
        self.show_initial_score = False

    def initUI(self):
        # ✅ 반응형: 최소 크기 설정
        self.setMinimumSize(1680, 1006)

        if not self.embedded:
            self.setWindowTitle(self.window_title)

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

        # ✅ 왼쪽 컬럼 (시험 분야 선택) - 472*898, padding: 좌우 24px, 상 36px, 하 0px
        self.left_col = QWidget()
        self.left_col.setFixedSize(472, 898)
        self.left_col.setStyleSheet("background: transparent;")
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(24, 36, 24, 0)
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

        # Stretch를 추가하여 버튼 그룹을 맨 아래로 이동
        self.right_layout.addStretch()

        # ✅ 버튼 그룹 (레이아웃 없이 직접 위치 설정)
        self.buttonGroup = QWidget()
        self.buttonGroup.setFixedSize(1064, 48)
        self.original_buttonGroup_size = (1064, 48)
        self.button_spacing = 16  # 버튼 간격 고정

        # 정지 버튼
        self.stop_btn = QPushButton("일시 정지", self.buttonGroup)  # 텍스트 추가
        stop_enabled = resource_path("assets/image/test_runner/btn_common_enabled.png").replace("\\", "/")
        stop_hover = resource_path("assets/image/test_runner/btn_common_hover.png").replace("\\", "/")
        stop_disabled = resource_path("assets/image/test_runner/btn_common_disabled.png").replace("\\", "/")
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

        # 시험 취소 버튼
        self.cancel_btn = QPushButton("시험 취소", self.buttonGroup)
        cancel_enabled = resource_path("assets/image/test_runner/btn_common_enabled.png").replace("\\", "/")
        cancel_hover = resource_path("assets/image/test_runner/btn_common_hover.png").replace("\\", "/")
        cancel_disabled = resource_path("assets/image/test_runner/btn_common_disabled.png").replace("\\", "/")
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{cancel_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }}
            QPushButton:hover {{
                border-image: url('{cancel_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:pressed {{
                border-image: url('{cancel_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:disabled {{
                border-image: url('{cancel_disabled}') 0 0 0 0 stretch stretch;
                color: #CECECE;
            }}
        """)
        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)
        self.cancel_btn.setDisabled(True)

        # 종료 버튼
        self.rbtn = QPushButton("종료", self.buttonGroup)  # 텍스트 추가
        exit_enabled = resource_path("assets/image/test_runner/btn_common_enabled.png").replace("\\", "/")
        exit_hover = resource_path("assets/image/test_runner/btn_common_hover.png").replace("\\", "/")
        exit_disabled = resource_path("assets/image/test_runner/btn_common_disabled.png").replace("\\", "/")
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
        result_enabled = resource_path("assets/image/test_runner/btn_common_enabled.png").replace("\\", "/")
        result_hover = resource_path("assets/image/test_runner/btn_common_hover.png").replace("\\", "/")
        result_disabled = resource_path("assets/image/test_runner/btn_common_disabled.png").replace("\\", "/")
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

        # 초기 점수 표시 (Platform만 해당)
        if self.show_initial_score and hasattr(self, 'update_score_display'):
            self.update_score_display()

        # 첫 시나리오 선택 (System만 해당)
        if hasattr(self, 'select_first_scenario'):
            QTimer.singleShot(100, self.select_first_scenario)

        # 버튼 연결 (서브클래스에서 구현)
        self.connect_buttons()

        if not self.embedded:
            self.show()

    def connect_buttons(self):
        """Subclass에서 버튼 연결을 구현해야 함"""
        raise NotImplementedError("Subclass must implement connect_buttons")

    def create_spec_selection_panel(self, left_layout):
        raise NotImplementedError("Subclass must implement create_spec_selection_panel")



    def _update_button_positions(self, group_width=None, group_height=None):
        """버튼 위치 직접 설정 (간격 16px 고정) - stop_btn, cancel_btn, result_btn, rbtn 4개"""
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

        # 각 버튼 크기 및 위치 설정 (stop_btn, cancel_btn, result_btn, rbtn)
        x = 0
        self.stop_btn.setFixedSize(btn_width, btn_height)
        self.stop_btn.move(x, 0)
        x += btn_width + spacing
        self.cancel_btn.setFixedSize(btn_width, btn_height)
        self.cancel_btn.move(x, 0)
        x += btn_width + spacing
        self.result_btn.setFixedSize(btn_width, btn_height)
        self.result_btn.move(x, 0)
        x += btn_width + spacing
        self.rbtn.setFixedSize(btn_width, btn_height)
        self.rbtn.move(x, 0)



    def resizeEvent(self, event):
        """창 크기 변경 시 배경 이미지 및 왼쪽 패널 크기 재조정"""
        super().resizeEvent(event)

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

                # TestSelectionPanel 자체 너비도 업데이트 (PlatformMainUI용)
                if hasattr(self, 'test_selection_panel'):
                     self.test_selection_panel.setFixedWidth(new_title_width)

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

            # 시험 시작 버튼 크기 조정 (왼쪽 컬럼에 있음)
            if hasattr(self, 'sbtn') and hasattr(self, 'original_sbtn_size'):
                new_sbtn_width = int(self.original_sbtn_size[0] * width_ratio)
                self.sbtn.setFixedSize(new_sbtn_width, self.original_sbtn_size[1])

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

            # ✅ 시험 점수 요약 내부 라벨 너비 비례 조정 (각 라벨별로 다른 너비 적용)
            if hasattr(self, 'original_pass_label_width'):
                new_pass_width = int(self.original_pass_label_width * width_ratio)
                new_opt_width = int(self.original_opt_label_width * width_ratio)
                new_score_width = int(self.original_score_label_width * width_ratio)
                # 분야별 점수 라벨
                if hasattr(self, 'spec_pass_label'):
                    self.spec_pass_label.setFixedSize(new_pass_width, 60)
                if hasattr(self, 'spec_total_label'):
                    self.spec_total_label.setFixedSize(new_opt_width, 60)
                if hasattr(self, 'spec_score_label'):
                    self.spec_score_label.setFixedSize(new_score_width, 60)
                # 전체 점수 라벨
                if hasattr(self, 'total_pass_label'):
                    self.total_pass_label.setFixedSize(new_pass_width, 60)
                if hasattr(self, 'total_total_label'):
                    self.total_total_label.setFixedSize(new_opt_width, 60)
                if hasattr(self, 'total_score_label'):
                    self.total_score_label.setFixedSize(new_score_width, 60)

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

        # 점수 레이블들 (500 Medium 20px #000000)
        # 원본 크기 저장 (반응형 조정용) - 각 라벨별로 다른 너비 적용
        self.original_pass_label_width = 340
        self.original_opt_label_width = 340
        self.original_score_label_width = 315

        self.spec_pass_label = QLabel(
            f"필수 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"0.0% (0/0)</span>"
        )
        self.spec_pass_label.setFixedSize(340, 60)
        self.spec_pass_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000;")

        self.spec_total_label = QLabel(
            f"선택 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"0.0% (0/0)</span>"
        )
        self.spec_total_label.setFixedSize(340, 60)
        self.spec_total_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000;")

        self.spec_score_label = QLabel(
            f"종합 평가 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"0.0% (0/0)</span>"
        )
        self.spec_score_label.setFixedSize(315, 60)
        self.spec_score_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000;")

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
        self.spec_data_widget.setStyleSheet("background: transparent;")
        self.original_spec_data_widget_size = (1064, 76)
        spec_score_layout = QHBoxLayout(self.spec_data_widget)
        spec_score_layout.setContentsMargins(20, 8, 20, 8)
        spec_score_layout.setSpacing(0)

        # 통과 필드 수 + 구분선 + spacer
        spec_score_layout.addWidget(self.spec_pass_label)
        spec_vline1 = QFrame()
        spec_vline1.setFixedSize(2, 60)
        spec_vline1.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline1)
        spec_spacer1 = QWidget()
        spec_spacer1.setFixedSize(12, 60)
        spec_score_layout.addWidget(spec_spacer1)

        # 전체 필드 수 + 구분선 + spacer
        spec_score_layout.addWidget(self.spec_total_label)
        spec_vline2 = QFrame()
        spec_vline2.setFixedSize(2, 60)
        spec_vline2.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline2)
        spec_spacer2 = QWidget()
        spec_spacer2.setFixedSize(12, 60)
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
        self.total_pass_label = QLabel(
            f"필수 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"0.0% (0/0)</span>"
        )
        self.total_pass_label.setFixedSize(340, 60)
        self.total_pass_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000;")

        self.total_total_label = QLabel(
            f"선택 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"0.0% (0/0)</span>"
        )
        self.total_total_label.setFixedSize(340, 60)
        self.total_total_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000;")

        self.total_score_label = QLabel(
            f"종합 평가 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"0.0% (0/0)</span>"
        )
        self.total_score_label.setFixedSize(315, 60)
        self.total_score_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000;")

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
        self.total_data_widget.setStyleSheet("background: transparent;")
        self.original_total_data_widget_size = (1064, 76)
        score_layout = QHBoxLayout(self.total_data_widget)
        score_layout.setContentsMargins(20, 8, 20, 8)
        score_layout.setSpacing(0)

        # 통과 필드 수 + 구분선 + spacer
        score_layout.addWidget(self.total_pass_label)
        total_vline1 = QFrame()
        total_vline1.setFixedSize(2, 60)
        total_vline1.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline1)
        total_spacer1 = QWidget()
        total_spacer1.setFixedSize(12, 60)
        score_layout.addWidget(total_spacer1)

        # 전체 필드 수 + 구부4선 + spacer
        score_layout.addWidget(self.total_total_label)
        total_vline2 = QFrame()
        total_vline2.setFixedSize(2, 60)
        total_vline2.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline2)
        total_spacer2 = QWidget()
        total_spacer2.setFixedSize(12, 60)
        score_layout.addWidget(total_spacer2)

        # 종합 평가 점수
        score_layout.addWidget(self.total_score_label)
        score_layout.addStretch()

        total_layout.addWidget(self.total_data_widget)
        total_group.setLayout(total_layout)

        return total_group



