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
from ui.common_main_ui import CommonMainUI

class SystemMainUI(CommonMainUI):
    def __init__(self):
        super().__init__()

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

    def update_score_display(self):
        """평가 점수 디스플레이를 업데이트"""
        if not (hasattr(self, "spec_pass_label") and hasattr(self, "spec_total_label") and hasattr(self, "spec_score_label")):
            return

        # ✅ 분야별 점수 제목 업데이트 (시나리오 명 변경 반영)
        if hasattr(self, "spec_name_label"):
            self.spec_name_label.setText(f"{self.spec_description} ({len(self.videoMessages)}개 API)")

        # ✅ 1️⃣ 분야별 점수 (현재 spec만) - step_pass_counts 배열의 합으로 계산
        if hasattr(self, 'step_pass_counts') and hasattr(self, 'step_error_counts'):
            self.total_pass_cnt = sum(self.step_pass_counts)
            self.total_error_cnt = sum(self.step_error_counts)
        
        # ✅ 선택 필드 통과 수 계산
        if hasattr(self, 'step_opt_pass_counts'):
            self.total_opt_pass_cnt = sum(self.step_opt_pass_counts)
        else:
            self.total_opt_pass_cnt = 0

        # ✅ 선택 필드 에러 수 계산
        if hasattr(self, 'step_opt_error_counts'):
            self.total_opt_error_cnt = sum(self.step_opt_error_counts)
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
        if hasattr(self, "total_pass_label") and hasattr(self, "total_total_label") and hasattr(self, "total_score_label"):
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

    def select_first_scenario(self):
        """프로그램 시작 시 첫 번째 그룹의 첫 번째 시나리오 자동 선택"""
        try:
            # 1. 첫 번째 그룹이 있는지 확인
            if self.group_table.rowCount() > 0:
                self.group_table.selectRow(0)
                self.on_group_selected(0, 0)

            # 2. 시나리오 테이블에 첫 번째 항목이 있는지 확인
            if self.test_field_table.rowCount() > 0:
                self.test_field_table.selectRow(0)
                # first_spec_id = self.index_to_spec_id.get(0) # Unused but logic implies selection
                self.on_test_field_selected(0, 0)
                # URL 생성 (test_name 사용)
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', self.current_spec_id)
                    self.pathUrl = self.url + "/" + test_name
                else:
                    self.pathUrl = self.url + "/" + self.current_spec_id
                self.url_text_box.setText(self.pathUrl)
        except Exception as e:
            print(f"[ERROR] 초기 시나리오 선택 실패: {e}")