from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem,
    QStackedWidget, QRadioButton, QFrame, QApplication, QSizePolicy, QGraphicsDropShadowEffect,
    QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QFont, QBrush, QPainter, QPen, QResizeEvent
import importlib
import re
from core.functions import resource_path
from network_scanner import NetworkScanWorker, ARPScanWorker
from form_validator import FormValidator, ClickableLabel, ClickableCheckboxRowWidget
import config.CONSTANTS as CONSTANTS
from splash_screen import LoadingPopup


class TestFieldTableWidget(QTableWidget):
    """시험 분야별 시나리오 테이블 - 세로 구분선이 전체 높이까지 표s시되는 커스텀 테이블"""

    def __init__(self, rows, columns):
        super().__init__(rows, columns)

    def paintEvent(self, event):
        """기본 paintEvent 실행 후 세로 구분선 추가"""
        # 기본 테이블 그리기
        super().paintEvent(event)

        # 세로 구분선 그리기
        painter = QPainter(self.viewport())
        pen = QPen(QColor("#CCCCCC"))
        pen.setWidth(1)
        painter.setPen(pen)

        # 첫 번째 컬럼과 두 번째 컬럼 사이의 세로선 (동적으로 컬럼 너비 사용)
        x_position = self.columnWidth(0)

        # 헤더 높이만큼 아래부터 viewport 끝까지 선 그리기
        header_height = self.horizontalHeader().height()
        viewport_height = self.viewport().height()

        painter.drawLine(x_position, 0, x_position, viewport_height)

        painter.end()


class InfoWidget(QWidget):
    """
    접속 후 화면 GUI.
    - 시험 기본/입력 정보, 인증 선택, 주소 탐색, OPT 로드 등
    """
    startTestRequested = pyqtSignal(str, str, str)  # (test_group_name, verification_type, spec_id) 전달

    def __init__(self):
        super().__init__()
        self.form_validator = FormValidator(self)  # 폼 검증 모듈 초기화
        self.scan_thread = None
        self.scan_worker = None
        self.current_mode = None
        self.target_system = ""  # 시험대상 시스템 (물리보안시스템/통합플랫폼시스템)
        self.test_group_name = None  # testGroup.name 저장
        self.test_specs = []  # testSpecs 리스트 저장
        self.current_page = 0
        self.stacked_widget = QStackedWidget()
        self.original_test_category = None  # API에서 받아온 원래 test_category 값 보관
        self.original_test_range = None  # API에서 받아온 원래 test_range 값 보관
        self.initUI()

    def initUI(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout()

        # 스택 위젯에 페이지 추가
        self.stacked_widget.addWidget(self.create_page1())  # 시험 정보 확인
        self.stacked_widget.addWidget(self.create_page2())  # 시험 설정

        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    # ---------- 반응형 크기 조정 헬퍼 함수들 ----------
    def _resize_widget(self, widget_attr, size_attr, width_ratio, height_ratio=None):
        """위젯 크기 조정 헬퍼 (가로만 또는 가로+세로)"""
        widget = getattr(self, widget_attr, None)
        original_size = getattr(self, size_attr, None)
        if widget and original_size:
            new_width = int(original_size[0] * width_ratio)
            new_height = int(original_size[1] * height_ratio) if height_ratio else original_size[1]
            widget.setFixedSize(new_width, new_height)

    def _resize_table_rows(self, table, row_height_attr, cell_width=None):
        """테이블 셀 위젯 너비 조정 (행 높이는 고정 유지)"""
        original_row_height = getattr(self, row_height_attr, None)
        if not original_row_height:
            return
        # 행 높이는 원본 크기로 고정
        for row in range(table.rowCount()):
            cell_widget = table.cellWidget(row, 0) or table.cellWidget(row, 1)
            if cell_widget and cell_width:
                cell_widget.setFixedSize(cell_width, original_row_height)

    def resizeEvent(self, event):
        """창 크기 변경 시 page1, page2 요소들 위치 재조정"""
        super().resizeEvent(event)

        # ========== Page1 크기 조정 ==========
        if hasattr(self, 'page1') and self.page1:
            if hasattr(self, 'info_panel') and hasattr(self, 'original_window_size') and hasattr(self, 'original_panel_size'):
                # 비율 계산
                width_ratio = max(1.0, self.page1.width() / self.original_window_size[0])
                height_ratio = max(1.0, min(1.2, self.page1.height() / self.original_window_size[1]))

                # 메인 패널
                self._resize_widget('info_panel', 'original_panel_size', width_ratio, height_ratio)

                # 타이틀 영역 (가로만)
                self._resize_widget('panel_title_container', 'original_title_size', width_ratio)
                self._resize_widget('panel_title_text', 'original_title_text_size', width_ratio)
                self._resize_widget('panel_title_desc', 'original_title_desc_size', width_ratio)

                # 인풋 컨테이너 (가로만)
                self._resize_widget('input_container', 'original_input_container_size', width_ratio)

                # 기업명/제품명 필드 (가로만)
                for prefix in ['company', 'product']:
                    self._resize_widget(f'{prefix}_field_widget', f'original_{prefix}_field_size', width_ratio)
                    self._resize_widget(f'{prefix}_label', f'original_{prefix}_label_size', width_ratio)
                    self._resize_widget(f'{prefix}_edit', f'original_{prefix}_edit_size', width_ratio)

                # 버전/모델명 행 (가로만)
                self._resize_widget('version_model_row', 'original_version_model_row_size', width_ratio)
                for prefix in ['version', 'model']:
                    self._resize_widget(f'{prefix}_field_widget', f'original_{prefix}_field_size', width_ratio)
                    self._resize_widget(f'{prefix}_label', f'original_{prefix}_label_size', width_ratio)
                    self._resize_widget(f'{prefix}_edit', f'original_{prefix}_edit_size', width_ratio)

                # 시험유형/시험대상 행 (가로만)
                self._resize_widget('category_target_row', 'original_category_target_row_size', width_ratio)
                for prefix, attr in [('test_category', 'test_category'), ('target_system', 'target_system')]:
                    self._resize_widget(f'{prefix}_widget', f'original_{attr}_field_size', width_ratio)
                    self._resize_widget(f'{prefix}_label', f'original_{attr}_label_size', width_ratio)
                    self._resize_widget(f'{prefix}_edit', f'original_{attr}_edit_size', width_ratio)

                # 시험분야/시험범위 행 (가로만)
                self._resize_widget('group_range_row', 'original_group_range_row_size', width_ratio)
                for prefix, attr in [('test_group', 'test_group'), ('test_range', 'test_range')]:
                    self._resize_widget(f'{prefix}_widget', f'original_{attr}_field_size', width_ratio)
                    self._resize_widget(f'{prefix}_label', f'original_{attr}_label_size', width_ratio)
                    self._resize_widget(f'{prefix}_edit', f'original_{attr}_edit_size', width_ratio)

                # Divider, 관리자 코드 (가로만)
                self._resize_widget('divider', 'original_divider_size', width_ratio)
                self._resize_widget('admin_code_widget', 'original_admin_code_widget_size', width_ratio)
                self._resize_widget('admin_code_label', 'original_admin_code_label_size', width_ratio)
                self._resize_widget('admin_code_input', 'original_admin_code_input_size', width_ratio)

            # 절대 위치 요소들
            page_width = self.page1.width()
            page_height = self.page1.height()

            if hasattr(self, 'page1_content') and self.page1_content:
                content_width = self.page1_content.width()
                content_height = self.page1_content.height()

                if hasattr(self, 'page1_bg_label'):
                    self.page1_bg_label.setGeometry(0, 0, content_width, content_height)
                if hasattr(self, 'ip_input_edit'):
                    self.ip_input_edit.setGeometry(content_width - 411, 24, 200, 40)
                if hasattr(self, 'load_test_info_btn'):
                    self.load_test_info_btn.setGeometry(content_width - 203, 13, 198, 62)

            if hasattr(self, 'management_url_container'):
                self.management_url_container.setGeometry(page_width - 390, page_height - 108, 380, 60)

            # ✅ 반응형: Page1 하단 버튼 영역 가로 확장
            if hasattr(self, 'original_window_size'):
                width_ratio = max(1.0, self.page1.width() / self.original_window_size[0])
                self._resize_widget('page1_button_container', 'original_page1_button_container_size', width_ratio)
                self._resize_widget('next_btn', 'original_next_btn_size', width_ratio)
                self._resize_widget('page1_exit_btn', 'original_page1_exit_btn_size', width_ratio)

        # ========== Page2 크기 조정 ==========
        if hasattr(self, 'page2_content') and self.page2_content:
            content_width = self.page2_content.width()
            content_height = self.page2_content.height()

            if hasattr(self, 'page2_bg_label'):
                self.page2_bg_label.setGeometry(0, 0, content_width, content_height)

            if hasattr(self, 'page2') and self.page2:
                # 비율 계산
                width_ratio = max(1.0, self.page2.width() / 1680)
                height_ratio = max(1.0, self.page2.height() / 1006)

                # bg_root 및 타이틀 컨테이너
                if hasattr(self, 'bg_root') and hasattr(self, 'original_bg_root_size'):
                    new_bg_root_width = int(self.original_bg_root_size[0] * width_ratio)
                    new_bg_root_height = int(self.original_bg_root_size[1] * height_ratio)
                    self.bg_root.setFixedSize(new_bg_root_width, new_bg_root_height)

                    if hasattr(self, 'page2_title_container') and hasattr(self, 'original_page2_title_container_size'):
                        self.page2_title_container.setFixedSize(new_bg_root_width, self.original_page2_title_container_size[1])

                    if hasattr(self, 'page2_title_bg') and hasattr(self, 'original_page2_title_bg_size'):
                        new_title_bg_width = int(self.original_page2_title_bg_size[0] * width_ratio)
                        self.page2_title_bg.setFixedSize(new_title_bg_width, self.original_page2_title_bg_size[1])

                        if hasattr(self, 'panels_container') and hasattr(self, 'original_panels_container_size'):
                            new_panels_height = int(self.original_panels_container_size[1] * height_ratio)
                            self.panels_container.setFixedSize(new_title_bg_width, new_panels_height)

                # 좌측 패널
                self._resize_widget('left_panel', 'original_left_panel_size', width_ratio, height_ratio)
                self._resize_widget('field_scenario_title', 'original_field_scenario_title_size', width_ratio)
                self._resize_widget('field_group', 'original_field_group_size', width_ratio, height_ratio)

                # 시험 분야 테이블
                if hasattr(self, 'test_field_table') and hasattr(self, 'original_test_field_table_size'):
                    new_table_width = int(self.original_test_field_table_size[0] * width_ratio)
                    new_table_height = int(self.original_test_field_table_size[1] * height_ratio)
                    self.test_field_table.setFixedSize(new_table_width, new_table_height)
                    self._resize_table_rows(self.test_field_table, 'original_test_field_row_height', new_table_width)

                # 시나리오 테이블
                if hasattr(self, 'scenario_table') and hasattr(self, 'original_scenario_table_size'):
                    new_table_width = int(self.original_scenario_table_size[0] * width_ratio)
                    new_table_height = int(self.original_scenario_table_size[1] * height_ratio)
                    self.scenario_table.setFixedSize(new_table_width, new_table_height)
                    self._resize_table_rows(self.scenario_table, 'original_scenario_row_height', new_table_width)

                    if hasattr(self, 'scenario_column_background') and hasattr(self, 'original_scenario_column_background_geometry'):
                        orig = self.original_scenario_column_background_geometry
                        self.scenario_column_background.setGeometry(orig[0], orig[1], int(orig[2] * width_ratio), new_table_height)

                    if hasattr(self, 'scenario_placeholder_label') and hasattr(self, 'original_scenario_placeholder_geometry'):
                        orig = self.original_scenario_placeholder_geometry
                        self.scenario_placeholder_label.setGeometry(orig[0], orig[1], int(orig[2] * width_ratio), new_table_height - 31)

                # 시험 API 그룹
                self._resize_widget('api_title', 'original_api_title_size', width_ratio)
                self._resize_widget('api_group', 'original_api_group_size', width_ratio, height_ratio)

                if hasattr(self, 'api_test_table') and hasattr(self, 'original_api_test_table_size'):
                    new_api_table_width = int(self.original_api_test_table_size[0] * width_ratio)
                    new_api_table_height = int(self.original_api_test_table_size[1] * height_ratio)
                    self.api_test_table.setFixedSize(new_api_table_width, new_api_table_height)

                    col_width = (new_api_table_width - 50) // 2
                    self.api_test_table.horizontalHeader().resizeSection(0, col_width)
                    self.api_test_table.horizontalHeader().resizeSection(1, col_width)

                    # 행 높이는 고정 유지 (원본 크기)

                    if hasattr(self, 'api_header_overlay') and hasattr(self, 'original_api_header_overlay_geometry'):
                        orig = self.original_api_header_overlay_geometry
                        self.api_header_overlay.setGeometry(orig[0], orig[1], new_api_table_width, orig[3])

                    if hasattr(self, 'api_header_func_label') and hasattr(self, 'original_api_header_func_label_size'):
                        self.api_header_func_label.setFixedSize(col_width, self.original_api_header_func_label_size[1])
                    if hasattr(self, 'api_header_api_label') and hasattr(self, 'original_api_header_api_label_size'):
                        self.api_header_api_label.setFixedSize(col_width, self.original_api_header_api_label_size[1])

                    if hasattr(self, 'api_placeholder_label') and hasattr(self, 'original_api_placeholder_geometry'):
                        orig = self.original_api_placeholder_geometry
                        self.api_placeholder_label.setGeometry(orig[0], orig[1], new_api_table_width - 50, int(orig[3] * height_ratio))

                # 우측 패널
                self._resize_widget('right_panel', 'original_right_panel_size', width_ratio, height_ratio)
                self._resize_widget('auth_title_widget', 'original_auth_title_size', width_ratio)
                self._resize_widget('auth_section', 'original_auth_section_size', width_ratio, height_ratio)
                self._resize_widget('auth_content_widget', 'original_auth_content_widget_size', width_ratio, height_ratio)

                # 수직 구분선 (특수 처리)
                if hasattr(self, 'auth_divider') and hasattr(self, 'original_auth_divider_size'):
                    new_divider_height = int(self.original_auth_divider_size[1] * height_ratio)
                    self.auth_divider.setFixedSize(1, new_divider_height)
                    divider_pixmap = QPixmap(resource_path("assets/image/test_config/divider.png"))
                    self.auth_divider.setPixmap(divider_pixmap.scaled(1, new_divider_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

                self._resize_widget('auth_type_widget', 'original_auth_type_widget_size', width_ratio, height_ratio)
                self._resize_widget('digest_option', 'original_digest_option_size', width_ratio, height_ratio)
                self._resize_widget('bearer_option', 'original_bearer_option_size', width_ratio, height_ratio)
                self._resize_widget('common_input_widget', 'original_common_input_widget_size', width_ratio, height_ratio)
                self._resize_widget('id_input', 'original_id_input_size', width_ratio)
                self._resize_widget('pw_input', 'original_pw_input_size', width_ratio)

                # 접속주소 탐색
                self._resize_widget('connection_title_row', 'original_connection_title_row_size', width_ratio)
                self._resize_widget('connection_section', 'original_connection_section_size', width_ratio, height_ratio)

                if hasattr(self, 'url_table') and hasattr(self, 'original_url_table_size'):
                    new_url_table_width = int(self.original_url_table_size[0] * width_ratio)
                    new_url_table_height = int(self.original_url_table_size[1] * height_ratio)
                    self.url_table.setFixedSize(new_url_table_width, new_url_table_height)

                    url_col_width = new_url_table_width - 50
                    self.url_table.setColumnWidth(1, url_col_width)

                    # 행 높이는 고정 유지, 셀 위젯 너비만 조정
                    if hasattr(self, 'original_url_row_height'):
                        for row in range(self.url_table.rowCount()):
                            url_widget = self.url_table.cellWidget(row, 1)
                            if url_widget:
                                url_widget.setFixedSize(url_col_width, self.original_url_row_height)

                # 하단 버튼
                self._resize_widget('button_container', 'original_button_container_size', width_ratio)
                self._resize_widget('start_btn', 'original_start_btn_size', width_ratio)
                self._resize_widget('exit_btn', 'original_exit_btn_size', width_ratio)

    def create_page1(self):
        """첫 번째 페이지: 시험 정보 확인"""
        self.page1 = QWidget()
        self.page1.setObjectName("page1")

        # 페이지 크기 설정
        self.page1.setMinimumSize(1680, 1006)  # 반응형: 최소 크기 설정

        # 전체 레이아웃 (헤더 포함)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단 헤더 영역 (반응형 - 배경 늘어남, 로고/타이틀 가운데 고정)
        header_widget = QWidget()
        header_widget.setFixedHeight(64)
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 배경 이미지 설정 (늘어남 - border-image 사용)
        header_bg_path = resource_path("assets/image/test_info/header.png").replace(chr(92), "/")
        header_widget.setStyleSheet(f"""
            QWidget {{
                border-image: url({header_bg_path}) 0 0 0 0 stretch stretch;
            }}
            QLabel {{
                border-image: none;
                background: transparent;
            }}
        """)

        # 헤더 레이아웃 (가운데 정렬)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # 왼쪽 stretch (가운데 정렬용)
        header_layout.addStretch()

        # 로고 이미지 (90x32)
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("assets/image/test_info/logo_KISA.png"))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setFixedSize(90, 32)
        header_layout.addWidget(logo_label)

        # 로고와 타이틀 사이 간격 20px
        header_layout.addSpacing(20)

        # 타이틀 이미지 (269x30)
        header_title_label = QLabel()
        header_title_pixmap = QPixmap(resource_path("assets/image/test_info/header_title.png"))
        header_title_label.setPixmap(header_title_pixmap)
        header_title_label.setFixedSize(269, 30)
        header_layout.addWidget(header_title_label)

        # 오른쪽 stretch (가운데 정렬용)
        header_layout.addStretch()

        main_layout.addWidget(header_widget)

        # 본문 영역 컨테이너 (1680x942px, padding: 32/56/0/0)
        self.page1_content = QWidget()
        self.page1_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 배경 이미지를 QLabel로 설정 (절대 위치)
        bg_path = resource_path("assets/image/test_info/bg-illust.png").replace(chr(92), "/")
        self.page1_bg_label = QLabel(self.page1_content)
        self.page1_bg_label.setPixmap(QPixmap(bg_path))
        self.page1_bg_label.setScaledContents(True)
        self.page1_bg_label.lower()  # 맨 뒤로 보내기

        content_layout = QVBoxLayout(self.page1_content)
        content_layout.setContentsMargins(32, 0, 56, 0)  # left: 32, top: 0, right: 56, bottom: 0
        content_layout.setSpacing(0)

        # 시험 기본 정보 (수평 중앙 정렬)
        # 원본 크기 저장 (비율 계산용)
        self.original_window_size = (1680, 1006)
        self.original_panel_size = (872, 843)

        self.info_panel = self.create_basic_info_panel()
        content_layout.addWidget(self.info_panel, alignment=Qt.AlignHCenter)

        # IP 입력창 (content_widget에 절대 위치로 배치 - 오른쪽 상단)
        self.ip_input_edit = QLineEdit(self.page1_content)
        self.ip_input_edit.setFixedSize(200, 40)
        self.ip_input_edit.setPlaceholderText("주소를 입력해주세요.")
        self.ip_input_edit.setGeometry(1269, 24, 200, 40)  # x: 1680-5(우측여백)-200-8-198, y: 24
        self.ip_input_edit.setStyleSheet("""
            QLineEdit {
                font-family: 'Noto Sans KR';
                font-size: 14px;
                padding: 8px 12px;
                border: 1px solid #CECECE;
                border-radius: 4px;
                background-color: white;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background-color: white;
            }
        """)

        # 불러오기 버튼 (content_widget에 절대 위치로 배치 - 오른쪽 상단)
        self.load_test_info_btn = QPushButton(self.page1_content)
        self.load_test_info_btn.setFixedSize(198, 62)
        self.load_test_info_btn.setGeometry(1477, 13, 198, 62)  # x: 1680-5(우측여백)-198, y: 13

        btn_enabled = resource_path("assets/image/test_info/btn_불러오기_enabled.png").replace(chr(92), "/")
        btn_hover = resource_path("assets/image/test_info/btn_불러오기_Hover.png").replace(chr(92), "/")

        self.load_test_info_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url({btn_enabled});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QPushButton:hover {{
                background-image: url({btn_hover});
            }}
        """)
        self.load_test_info_btn.clicked.connect(self.on_load_test_info_clicked)

        main_layout.addWidget(self.page1_content, 1)  # 반응형: stretch=1로 남은 공간 채움
        self.page1.setLayout(main_layout)

        # 관리자시스템 주소 입력 필드
        self.management_url_container = QWidget(self.page1)
        self.management_url_container.setFixedSize(380, 60)  # 라벨 텍스트가 잘 보이도록 증가
        # 오른쪽 끝으로 배치: x = 1680 - 10 - 380, y = 1006 - 60 - 48
        self.management_url_container.setGeometry(1290, 898, 380, 60)
        self.management_url_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 4px;
                border: 1px solid #E8E8E8;
            }
        """)

        management_url_layout = QHBoxLayout(self.management_url_container)
        management_url_layout.setContentsMargins(12, 10, 12, 10)
        management_url_layout.setSpacing(8)

        # 라벨
        management_url_label = QLabel("관리자시스템 주소:")
        management_url_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 13px;
                font-weight: 400;
                color: #333;
                background-color: transparent;
                border: none;
            }
        """)
        management_url_label.setFixedWidth(130)  # 텍스트가 잘리지 않도록 증가
        management_url_layout.addWidget(management_url_label)

        # 입력 필드
        self.management_url_edit = QLineEdit()
        self.management_url_edit.setText(CONSTANTS.management_url)  # 초기값 설정
        self.management_url_edit.setPlaceholderText("http://ect2.iptime.org:20223")
        self.management_url_edit.setStyleSheet("""
            QLineEdit {
                font-family: 'Noto Sans KR';
                font-size: 13px;
                padding: 6px 10px;
                border: 1px solid #CECECE;
                border-radius: 3px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
            }
        """)
        self.management_url_edit.textChanged.connect(self.on_management_url_changed)
        management_url_layout.addWidget(self.management_url_edit)

        # 관리자시스템 주소 컨테이너를 위로 올림
        self.management_url_container.raise_()

        return self.page1

    def create_page2(self):
        """두 번째 페이지: 시험 설정"""
        self.page2 = QWidget()
        self.page2.setObjectName("page2")

        # 페이지 크기 설정 (반응형: 최소 크기만 설정)
        self.page2.setMinimumSize(1680, 1006)

        # 전체 레이아웃 (헤더 포함)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단 헤더 영역 (반응형 - 배경 늘어남, 로고/타이틀 좌측 정렬)
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

        # 타이틀 이미지 (458x36)
        header_title_label = QLabel()
        header_title_pixmap = QPixmap(resource_path("assets/image/test_config/config_title.png"))
        header_title_label.setPixmap(header_title_pixmap.scaled(458, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_title_label.setFixedSize(458, 36)
        header_layout.addWidget(header_title_label)

        # 오른쪽 stretch (나머지 공간 채우기)
        header_layout.addStretch()

        main_layout.addWidget(header_widget)

        # 본문 영역 컨테이너 (반응형 - 가로세로 확장)
        self.page2_content = QWidget()
        self.page2_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.page2_content.setObjectName("content_widget_page2")

        # 배경 이미지를 QLabel로 설정 (절대 위치, 반응형으로 늘어남)
        bg_path2 = resource_path("assets/image/test_config/시험정보설정_main.png").replace(chr(92), "/")
        self.page2_bg_label = QLabel(self.page2_content)
        self.page2_bg_label.setPixmap(QPixmap(bg_path2))
        self.page2_bg_label.setScaledContents(True)
        self.page2_bg_label.lower()  # 맨 뒤로 보내기

        # content_layout: page2_content에 설정 (가운데 정렬용)
        content_layout = QVBoxLayout(self.page2_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 내부 콘텐츠 컨테이너 (bg_root) - 반응형
        self.bg_root = QWidget()
        self.bg_root.setFixedSize(1680, 897)  # 타이틀(52) + 간격(8) + 패널(802) + padding(상36+하4) = 902 → 897 유지
        self.original_bg_root_size = (1680, 897)
        self.bg_root.setStyleSheet("background: transparent;")

        # bg_root 내부 레이아웃
        bg_root_layout = QVBoxLayout(self.bg_root)
        bg_root_layout.setContentsMargins(0, 36, 0, 44)  # 좌, 상(padding36), 우, 하(padding44)
        bg_root_layout.setSpacing(0)

        # 세로 확장 시 컨텐츠를 중앙에 배치 (상단 여백)
        bg_root_layout.addStretch()

        # 타이틀 컨테이너 (1680x52px) - 반응형
        self.page2_title_container = QWidget()
        self.page2_title_container.setFixedSize(1680, 52)
        self.original_page2_title_container_size = (1680, 52)
        self.page2_title_container.setStyleSheet("background: transparent;")

        title_container_layout = QHBoxLayout(self.page2_title_container)
        title_container_layout.setContentsMargins(0, 0, 0, 0)
        title_container_layout.setSpacing(0)

        # 좌우 stretch로 자동 가운데 정렬
        title_container_layout.addStretch()

        # 타이틀 배경 영역 (1584x52px) - border-image로 배경 (패널들과 같은 너비)
        self.page2_title_bg = QWidget()
        self.page2_title_bg.setFixedSize(1584, 52)
        self.original_page2_title_bg_size = (1584, 52)
        self.page2_title_bg.setObjectName("page2_title_bg")

        title_bg_path = resource_path("assets/image/test_config/시험정보설정_title.png").replace(chr(92), "/")
        self.page2_title_bg.setStyleSheet(f"""
            QWidget#page2_title_bg {{
                border-image: url({title_bg_path}) 0 0 0 0 stretch stretch;
            }}
        """)

        # 타이틀 내부 레이아웃 (padding: 좌14, 우48, 상하12)
        title_inner_layout = QHBoxLayout(self.page2_title_bg)
        title_inner_layout.setContentsMargins(14, 12, 48, 12)
        title_inner_layout.setSpacing(0)

        # 아이콘 (icn_notification.png, 18x18)
        self.page2_title_icon = QLabel()
        self.page2_title_icon.setFixedSize(18, 18)
        icon_path = resource_path("assets/image/icon/icn_notification.png")
        self.page2_title_icon.setPixmap(QPixmap(icon_path).scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_inner_layout.addWidget(self.page2_title_icon)

        # gap 13px
        title_inner_layout.addSpacing(13)

        # 텍스트 "시험 분야별 시나리오 확인 및 시험 환경을 설정하세요."
        self.page2_title_text = QLabel("시험 분야별 시나리오 확인 및 시험 환경을 설정하세요.")
        self.page2_title_text.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        title_inner_layout.addWidget(self.page2_title_text)
        title_inner_layout.addStretch()

        title_container_layout.addWidget(self.page2_title_bg)
        title_container_layout.addStretch()  # 우측 stretch
        bg_root_layout.addWidget(self.page2_title_container, 0, Qt.AlignTop | Qt.AlignHCenter)

        # 타이틀과 콘텐츠 사이 간격
        bg_root_layout.addSpacing(8)

        # 기존 콘텐츠 (좌우 패널) - 타이틀 배경과 같은 너비로 제한
        self.panels_container = QWidget()
        self.panels_container.setFixedSize(1584, 802)  # 좌우 패널 합 (792 + 792)
        self.original_panels_container_size = (1584, 802)

        panels_layout = QHBoxLayout(self.panels_container)
        panels_layout.setContentsMargins(0, 0, 0, 0)
        panels_layout.setSpacing(0)

        # 좌측 패널 (792x802px) - 배경 이미지: 시험 분야별 시나리오 + 시험 API (반응형)
        self.left_panel = QGroupBox()
        self.left_panel.setFixedSize(792, 802)
        self.original_left_panel_size = (792, 802)
        self.left_panel.setObjectName("left_panel")

        left_bg_path = resource_path("assets/image/test_config/left_title_sub.png").replace(chr(92), "/")
        self.left_panel.setStyleSheet(f"""
            QGroupBox#left_panel {{
                border: none;
                margin: 0px;
                padding: 0px;
                margin-top: 0px;
                padding-top: 0px;
                border-image: url({left_bg_path}) 0 0 0 0 stretch stretch;
            }}
        """)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(24, 12, 24, 80)  # 좌, 상(12px 패딩), 우, 하
        left_layout.setSpacing(0)

        # "시험 분야별 시나리오" 타이틀 라벨 (744x24px)
        self.field_scenario_title = QLabel("시험 분야별 시나리오")
        self.field_scenario_title.setFixedSize(744, 24)
        self.original_field_scenario_title_size = (744, 24)
        self.field_scenario_title.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #000000;
                background: transparent;
            }
        """)
        left_layout.addWidget(self.field_scenario_title)

        # gap 8px
        left_layout.addSpacing(8)

        # 시험 분야별 시나리오 테이블 (반응형)
        self.field_group = self.create_test_field_group()
        self.original_field_group_size = (744, 240)
        left_layout.addWidget(self.field_group)

        # gap 16px
        left_layout.addSpacing(16)

        # "시험 API" 타이틀 라벨 (744x38px) - 접속 주소 탐색과 동일한 높이
        self.api_title = QLabel("시험 API")
        self.api_title.setFixedSize(744, 38)
        self.original_api_title_size = (744, 38)
        self.api_title.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #000000;
                background: transparent;
            }
        """)
        left_layout.addWidget(self.api_title)

        # gap 8px
        left_layout.addSpacing(8)

        # 시험 API 테이블 (QGroupBox로 감싸기) (반응형)
        self.api_group = self.create_test_api_group()
        self.original_api_group_size = (744, 376)
        left_layout.addWidget(self.api_group)

        # 좌우 패널 정렬 유지를 위한 하단 stretch
        left_layout.addStretch()

        self.left_panel.setLayout(left_layout)

        # 우측 패널 (792x802px) - 반응형
        self.right_panel = QGroupBox()
        self.right_panel.setFixedSize(792, 802)
        self.original_right_panel_size = (792, 802)
        self.right_panel.setStyleSheet("QGroupBox { border: none; margin: 0px; padding: 0px; margin-top: 0px; padding-top: 0px; background: transparent; }")

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(24, 12, 24, 0)  # 좌, 상, 우, 하
        right_layout.setSpacing(0)

        # "사용자 인증 방식" 타이틀 라벨 (744x24px) - 반응형
        self.auth_title_widget = QLabel("사용자 인증 방식")
        self.auth_title_widget.setFixedSize(744, 24)
        self.original_auth_title_size = (744, 24)
        self.auth_title_widget.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #000000;
                background: transparent;
            }
        """)
        right_layout.addWidget(self.auth_title_widget)

        # gap 8px
        right_layout.addSpacing(8)

        # 사용자 인증 방식 박스 (744x240px) - 반응형
        self.auth_section = self.create_auth_section()
        right_layout.addWidget(self.auth_section)

        # gap 16px
        right_layout.addSpacing(16)

        # 접속주소 탐색 타이틀 + 주소탐색 버튼 행 (744x38px) - 반응형
        self.connection_title_row = QWidget()
        self.connection_title_row.setFixedSize(744, 38)
        self.original_connection_title_row_size = (744, 38)
        connection_title_layout = QHBoxLayout()
        connection_title_layout.setContentsMargins(0, 0, 0, 0)
        connection_title_layout.setSpacing(0)

        # "접속 주소 탐색" 타이틀 라벨
        connection_title_widget = QLabel("접속 주소 탐색")
        connection_title_widget.setFixedHeight(38)
        connection_title_widget.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #000000;
                background: transparent;
            }
        """)
        connection_title_layout.addWidget(connection_title_widget)

        connection_title_layout.addStretch()

        # 버튼 그룹 (주소탐색 + 추가)
        buttons_widget = QWidget()
        buttons_widget.setFixedHeight(38)
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(16)  # gap 16px

        # 주소탐색 버튼 (120x38px)
        scan_btn = QPushButton("")
        scan_btn.setFixedSize(120, 38)

        btn_scan_enabled = resource_path("assets/image/test_config/btn_주소탐색_enabled.png").replace(chr(92), "/")
        btn_scan_hover = resource_path("assets/image/test_config/btn_주소탐색_Hover.png").replace(chr(92), "/")

        scan_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url({btn_scan_enabled});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QPushButton:hover {{
                background-image: url({btn_scan_hover});
            }}
        """)
        scan_btn.clicked.connect(self.start_scan)
        buttons_layout.addWidget(scan_btn)

        # 추가 버튼 (90x38px)
        self.add_btn = QPushButton("")
        self.add_btn.setFixedSize(90, 38)
        self.add_btn.setCheckable(True)  # 토글 가능하도록 설정

        btn_add_enabled = resource_path("assets/image/test_config/btn_추가_enabled.png").replace(chr(92), "/")
        btn_add_hover = resource_path("assets/image/test_config/btn_추가_Hover.png").replace(chr(92), "/")
        btn_add_selected = resource_path("assets/image/test_config/btn_추가_selected.png").replace(chr(92), "/")

        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url({btn_add_enabled});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QPushButton:hover {{
                background-image: url({btn_add_hover});
            }}
            QPushButton:checked {{
                background-image: url({btn_add_selected});
            }}
            QPushButton:checked:hover {{
                background-image: url({btn_add_selected});
            }}
        """)
        # 추가 버튼 클릭 이벤트 연결
        self.add_btn.clicked.connect(self.toggle_address_popover)
        buttons_layout.addWidget(self.add_btn)

        buttons_widget.setLayout(buttons_layout)
        connection_title_layout.addWidget(buttons_widget)
        self.connection_title_row.setLayout(connection_title_layout)
        right_layout.addWidget(self.connection_title_row)

        # 주소 추가 팝오버 (392x102px)
        self.address_popover = QWidget()
        self.address_popover.setFixedSize(392, 102)
        self.address_popover.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 12px;
            }
        """)

        # 팝오버 그림자 효과 (Figma: X:0, Y:0, Blur:5, Spread:0, #6B6B6B 80%)
        popover_shadow = QGraphicsDropShadowEffect()
        popover_shadow.setBlurRadius(5)
        popover_shadow.setXOffset(0)
        popover_shadow.setYOffset(0)
        popover_shadow.setColor(QColor(107, 107, 107, 204))  # #6B6B6B 80%
        self.address_popover.setGraphicsEffect(popover_shadow)

        popover_layout = QVBoxLayout()
        popover_layout.setContentsMargins(16, 16, 16, 16)
        popover_layout.setSpacing(0)

        # "주소 추가" 문구 (358x26)
        popover_title = QLabel("주소 추가")
        popover_title.setFixedSize(358, 26)
        popover_title.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        popover_layout.addWidget(popover_title)

        # 4px gap
        popover_layout.addSpacing(4)

        # 입력창 + 추가 버튼 (수평 레이아웃)
        input_row_layout = QHBoxLayout()
        input_row_layout.setContentsMargins(0, 0, 0, 0)
        input_row_layout.setSpacing(6)  # 6px gap

        # 입력창 (287x40)
        self.address_input = QLineEdit()
        self.address_input.setFixedSize(287, 40)
        self.address_input.setPlaceholderText("추가할 주소를 입력해주세요")

        self.address_input.setStyleSheet("""
            QLineEdit {
                padding-left: 24px;
                padding-right: 24px;
                border: 1px solid #868686;
                border-radius: 4px;
                background-color: #FFFFFF;
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
            }
            QLineEdit::placeholder {
                color: #868686;
                font-size: 18px;
                font-weight: 500;
            }
        """)
        input_row_layout.addWidget(self.address_input)

        # 추가 버튼 (65x40)
        popover_add_btn = QPushButton("")
        popover_add_btn.setFixedSize(65, 40)

        btn_add_img = resource_path("assets/image/test_config/btn_추가.png").replace(chr(92), "/")
        popover_add_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 4px;
                background-image: url({btn_add_img});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)
        popover_add_btn.clicked.connect(self.add_address_from_popover)
        input_row_layout.addWidget(popover_add_btn)

        popover_layout.addLayout(input_row_layout)
        self.address_popover.setLayout(popover_layout)

        # 팝오버를 절대 위치로 배치 (레이아웃에 추가하지 않음)
        # parent를 page2_widget으로 설정하여 상대 좌표 사용
        self.address_popover.setParent(self)

        # 초기에는 숨김
        self.address_popover.hide()

        # gap 8px
        right_layout.addSpacing(8)

        # URL 박스 테이블 (744x376px) - 반응형
        self.connection_section = self.create_connection_section()
        right_layout.addWidget(self.connection_section)

        # padding 32px
        right_layout.addSpacing(32)

        # 하단 버튼 (시험시작, 종료) - 반응형 컨테이너 (744x48px)
        self.button_container = QWidget()
        self.button_container.setFixedSize(744, 48)
        self.original_button_container_size = (744, 48)
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(16)  # 버튼 간격 16px 고정

        # 시험 시작 버튼 (왼쪽) - 364x48px 반응형 (텍스트 분리)
        self.start_btn = QPushButton("시험 시작")
        self.start_btn.setFixedSize(364, 48)
        self.original_start_btn_size = (364, 48)

        btn_start_enabled = resource_path("assets/image/test_config/btn_시험시작_enabled.png").replace(chr(92), "/")
        btn_start_hover = resource_path("assets/image/test_config/btn_시험시작_Hover.png").replace(chr(92), "/")

        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url({btn_start_enabled}) 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                border-image: url({btn_start_hover}) 0 0 0 0 stretch stretch;
            }}
        """)
        self.start_btn.clicked.connect(self.start_test)
        self.start_btn.setEnabled(True)
        button_layout.addWidget(self.start_btn)

        # 종료 버튼 (오른쪽) - 364x48px 반응형 (텍스트 분리)
        self.exit_btn = QPushButton("종료")
        self.exit_btn.setFixedSize(364, 48)
        self.original_exit_btn_size = (364, 48)

        btn_exit_enabled = resource_path("assets/image/test_config/btn_종료_enabled.png").replace(chr(92), "/")
        btn_exit_hover = resource_path("assets/image/test_config/btn_종료_Hover.png").replace(chr(92), "/")

        self.exit_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url({btn_exit_enabled}) 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }}
            QPushButton:hover {{
                border-image: url({btn_exit_hover}) 0 0 0 0 stretch stretch;
            }}
        """)
        self.exit_btn.clicked.connect(self.exit_btn_clicked)
        button_layout.addWidget(self.exit_btn)

        right_layout.addWidget(self.button_container)

        # 좌우 패널 정렬 유지를 위한 하단 stretch
        right_layout.addStretch()

        self.right_panel.setLayout(right_layout)

        panels_layout.addWidget(self.left_panel, 0, Qt.AlignTop)
        panels_layout.addWidget(self.right_panel, 0, Qt.AlignTop)

        # panels_container를 bg_root_layout에 상단 가운데 정렬로 추가
        bg_root_layout.addWidget(self.panels_container, 1, Qt.AlignTop | Qt.AlignHCenter)

        # 세로 확장 시 컨텐츠를 중앙에 배치 (하단 여백)
        bg_root_layout.addStretch()

        # bg_root를 content_layout에 가운데 정렬로 추가
        content_layout.addWidget(self.bg_root, 0, Qt.AlignHCenter | Qt.AlignVCenter)

        # 메인 레이아웃에 콘텐츠 영역 추가 (반응형: stretch=1)
        main_layout.addWidget(self.page2_content, 1)

        self.page2.setLayout(main_layout)

        return self.page2

    # ---------- 페이지 전환 메서드 ----------
    def go_to_next_page(self):
        """다음 페이지로 이동 (조건 검증 후)"""
        is_complete = self._is_page1_complete()

        if not is_complete:
            QMessageBox.warning(self,"입력 필요", "시험 정보 페이지의 모든 필수 항목을 입력해주세요.")
            return

        if self.current_page < 1:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            # 페이지 전환 후 반응형 레이아웃 적용을 위해 resize 이벤트 강제 트리거
            self.resizeEvent(QResizeEvent(self.size(), self.size()))

    def go_to_previous_page(self):
        """이전 페이지로 이동"""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            # 페이지 전환 후 반응형 레이아웃 적용을 위해 resize 이벤트 강제 트리거
            self.resizeEvent(QResizeEvent(self.size(), self.size()))
            # 1페이지로 돌아갈 때 다음 버튼 상태 업데이트
            if self.current_page == 0:
                self.check_next_button_state()

    # ---------- 새로운 패널 생성 메서드들 ----------
    def create_basic_info_panel(self):
        """시험 기본 정보만 (불러오기 버튼 + 기본 정보 필드)"""
        panel = QWidget()  # QGroupBox에서 QWidget으로 변경

        # 패널 크기 및 스타일 설정 (872x843px, 배경: 시험기본정보입력.png)
        panel.setFixedSize(872, 843)

        # 배경 이미지 설정 (border-image로 크기에 맞게 늘어남)
        bg_panel_path = resource_path("assets/image/test_info/시험기본정보입력.png").replace(chr(92), "/")
        panel.setObjectName("basic_info_panel")
        panel.setStyleSheet(f"""
            QWidget#basic_info_panel {{
                border-image: url({bg_panel_path}) 0 0 0 0 stretch stretch;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(48, 32, 48, 40)  # left: 48, top: 32, right: 48, bottom: 40
        layout.setSpacing(0)

        # 세로 확장 시 컨텐츠를 중앙에 배치 (상단 여백)
        layout.addStretch()

        # 타이틀 컨테이너 (776x106px)
        self.panel_title_container = QWidget()
        self.panel_title_container.setFixedSize(776, 106)
        self.panel_title_container.setStyleSheet("QWidget { background: transparent; }")
        self.original_title_size = (776, 106)  # 원본 크기 저장

        title_layout = QVBoxLayout(self.panel_title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        # 타이틀 텍스트 (776x38px)
        self.panel_title_text = QLabel("시험 기본 정보 확인")
        self.panel_title_text.setFixedSize(776, 38)
        self.panel_title_text.setAlignment(Qt.AlignCenter)
        self.panel_title_text.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 26px;
                font-weight: 500;
                color: #000000;
                background: transparent;
            }
        """)
        self.original_title_text_size = (776, 38)  # 원본 크기 저장
        title_layout.addWidget(self.panel_title_text)

        # gap 16px
        title_layout.addSpacing(16)

        # 타이틀 설명 영역 (776x52px)
        self.panel_title_desc = QWidget()
        self.panel_title_desc.setFixedSize(776, 52)
        self.panel_title_desc.setObjectName("panel_title_desc")
        title_desc_bg_path = resource_path("assets/image/test_info/시험기본정보확인_header.png").replace(chr(92), "/")
        self.panel_title_desc.setStyleSheet(f"""
            QWidget#panel_title_desc {{
                border-image: url({title_desc_bg_path}) 0 0 0 0 stretch stretch;
            }}
        """)
        self.original_title_desc_size = (776, 52)  # 원본 크기 저장

        desc_layout = QHBoxLayout(self.panel_title_desc)
        desc_layout.setContentsMargins(14, 12, 48, 12)  # 좌 14, 상 12, 우 48, 하 12
        desc_layout.setSpacing(13)  # 아이콘과 텍스트 사이 gap

        # 체크 아이콘 (18x18px)
        self.panel_check_icon = QLabel()
        check_icon_pixmap = QPixmap(resource_path("assets/image/icon/icn_check.png"))
        self.panel_check_icon.setPixmap(check_icon_pixmap.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.panel_check_icon.setFixedSize(18, 18)
        desc_layout.addWidget(self.panel_check_icon, alignment=Qt.AlignVCenter)

        # 설명 텍스트
        self.panel_desc_text = QLabel("시험 기본 정보를 확인하고 다음 버튼을 눌러주세요.")
        self.panel_desc_text.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.panel_desc_text.setAlignment(Qt.AlignVCenter)
        desc_layout.addWidget(self.panel_desc_text, alignment=Qt.AlignVCenter)
        desc_layout.addStretch()  # 오른쪽 여백 채우기

        title_layout.addWidget(self.panel_title_desc)

        layout.addWidget(self.panel_title_container, alignment=Qt.AlignHCenter)

        # 타이틀과 인풋박스 컨테이너 사이 간격
        layout.addSpacing(12)

        # 인풋박스 컨테이너 (776x479px - 기업명~시험범위)
        self.input_container = QWidget()
        self.input_container.setFixedSize(776, 479)
        self.input_container.setStyleSheet("QWidget { background: transparent; }")  # 투명 배경
        self.original_input_container_size = (776, 479)  # 원본 크기 저장
        input_layout = QVBoxLayout(self.input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)  # 필드 간 gap 12px

        # 기업명 필드 (776x82px - 전체 너비)
        self.company_field_widget = QWidget()
        self.company_field_widget.setFixedSize(776, 82)
        self.company_field_widget.setStyleSheet("QWidget { background: transparent; }")
        self.original_company_field_size = (776, 82)  # 원본 크기 저장

        company_field_layout = QVBoxLayout(self.company_field_widget)
        company_field_layout.setContentsMargins(0, 0, 0, 0)
        company_field_layout.setSpacing(6)

        # 기업명 라벨 (776x28px)
        self.company_label = QLabel("기업명")
        self.company_label.setFixedSize(776, 28)
        self.company_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.original_company_label_size = (776, 28)  # 원본 크기 저장
        company_field_layout.addWidget(self.company_label)

        # 입력칸 (768x48px)
        self.company_edit = QLineEdit()
        self.company_edit.setFixedSize(768, 48)
        self.company_edit.setReadOnly(True)
        self.original_company_edit_size = (768, 48)  # 원본 크기 저장

        company_input_default = resource_path("assets/image/test_info/불러온정보_w_default.png").replace(chr(92), "/")
        company_input_filled = resource_path("assets/image/test_info/불러온정보_w_filled.png").replace(chr(92), "/")

        self.company_edit.setObjectName("company_edit")
        self.company_edit.setStyleSheet(f"""
            QLineEdit#company_edit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                border-image: url({company_input_default}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#company_edit[hasText="true"] {{
                border-image: url({company_input_filled}) 0 0 0 0 stretch stretch;
            }}
        """)

        # 텍스트 입력 시 배경 이미지 변경
        def update_company_background():
            has_text = bool(self.company_edit.text().strip())
            self.company_edit.setProperty("hasText", "true" if has_text else "false")
            self.company_edit.style().unpolish(self.company_edit)
            self.company_edit.style().polish(self.company_edit)

        self.company_edit.textChanged.connect(update_company_background)
        self.company_edit.setProperty("hasText", "false")

        company_field_layout.addWidget(self.company_edit, alignment=Qt.AlignHCenter)
        input_layout.addWidget(self.company_field_widget, alignment=Qt.AlignHCenter)

        # 제품명 필드 (776x82px - 전체 너비)
        self.product_field_widget = QWidget()
        self.product_field_widget.setFixedSize(776, 82)
        self.product_field_widget.setStyleSheet("QWidget { background: transparent; }")
        self.original_product_field_size = (776, 82)  # 원본 크기 저장

        product_field_layout = QVBoxLayout(self.product_field_widget)
        product_field_layout.setContentsMargins(0, 0, 0, 0)
        product_field_layout.setSpacing(6)

        # 제품명 라벨 (776x28px)
        self.product_label = QLabel("제품명")
        self.product_label.setFixedSize(776, 28)
        self.product_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.original_product_label_size = (776, 28)  # 원본 크기 저장
        product_field_layout.addWidget(self.product_label)

        # 입력칸 (768x48px)
        self.product_edit = QLineEdit()
        self.product_edit.setFixedSize(768, 48)
        self.product_edit.setReadOnly(True)
        self.original_product_edit_size = (768, 48)  # 원본 크기 저장

        product_input_default = resource_path("assets/image/test_info/불러온정보_w_default.png").replace(chr(92), "/")
        product_input_filled = resource_path("assets/image/test_info/불러온정보_w_filled.png").replace(chr(92), "/")

        self.product_edit.setObjectName("product_edit")
        self.product_edit.setStyleSheet(f"""
            QLineEdit#product_edit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                border-image: url({product_input_default}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#product_edit[hasText="true"] {{
                border-image: url({product_input_filled}) 0 0 0 0 stretch stretch;
            }}
        """)

        # 텍스트 입력 시 배경 이미지 변경
        def update_product_background():
            has_text = bool(self.product_edit.text().strip())
            self.product_edit.setProperty("hasText", "true" if has_text else "false")
            self.product_edit.style().unpolish(self.product_edit)
            self.product_edit.style().polish(self.product_edit)

        self.product_edit.textChanged.connect(update_product_background)
        self.product_edit.setProperty("hasText", "false")

        product_field_layout.addWidget(self.product_edit, alignment=Qt.AlignHCenter)
        input_layout.addWidget(self.product_field_widget, alignment=Qt.AlignHCenter)

        # 버전, 모델명 행 (776x82px)
        self.version_model_row = QWidget()
        self.version_model_row.setFixedSize(776, 82)
        self.version_model_row.setStyleSheet("QWidget { background: transparent; }")
        self.original_version_model_row_size = (776, 82)  # 원본 크기 저장
        version_model_layout = QHBoxLayout(self.version_model_row)
        version_model_layout.setContentsMargins(0, 0, 0, 0)
        version_model_layout.setSpacing(20)  # 간격 20px

        # 버전 필드 (378x82px)
        self.version_field_widget = QWidget()
        self.version_field_widget.setFixedSize(378, 82)
        self.version_field_widget.setStyleSheet("QWidget { background: transparent; }")
        self.original_version_field_size = (378, 82)  # 원본 크기 저장

        version_field_layout = QVBoxLayout(self.version_field_widget)
        version_field_layout.setContentsMargins(0, 0, 0, 0)
        version_field_layout.setSpacing(6)

        # 버전 라벨 (378x28px)
        self.version_label = QLabel("버전")
        self.version_label.setFixedSize(378, 28)
        self.version_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.original_version_label_size = (378, 28)  # 원본 크기 저장
        version_field_layout.addWidget(self.version_label)

        # 버전 입력칸 (378x48px)
        self.version_edit = QLineEdit()
        self.version_edit.setFixedSize(378, 48)
        self.version_edit.setReadOnly(True)
        self.original_version_edit_size = (378, 48)  # 원본 크기 저장

        version_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        version_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.version_edit.setObjectName("version_edit")
        self.version_edit.setStyleSheet(f"""
            QLineEdit#version_edit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                border-image: url({version_input_default}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#version_edit[hasText="true"] {{
                border-image: url({version_input_filled}) 0 0 0 0 stretch stretch;
            }}
        """)

        def update_version_background():
            has_text = bool(self.version_edit.text().strip())
            self.version_edit.setProperty("hasText", "true" if has_text else "false")
            self.version_edit.style().unpolish(self.version_edit)
            self.version_edit.style().polish(self.version_edit)

        self.version_edit.textChanged.connect(update_version_background)
        self.version_edit.setProperty("hasText", "false")

        version_field_layout.addWidget(self.version_edit)
        version_model_layout.addWidget(self.version_field_widget)

        # 모델명 필드 (378x82px)
        self.model_field_widget = QWidget()
        self.model_field_widget.setFixedSize(378, 82)
        self.model_field_widget.setStyleSheet("QWidget { background: transparent; }")
        self.original_model_field_size = (378, 82)  # 원본 크기 저장

        model_field_layout = QVBoxLayout(self.model_field_widget)
        model_field_layout.setContentsMargins(0, 0, 0, 0)
        model_field_layout.setSpacing(6)

        # 모델명 라벨 (378x28px)
        self.model_label = QLabel("모델명")
        self.model_label.setFixedSize(378, 28)
        self.model_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.original_model_label_size = (378, 28)  # 원본 크기 저장
        model_field_layout.addWidget(self.model_label)

        # 모델명 입력칸 (378x48px)
        self.model_edit = QLineEdit()
        self.model_edit.setFixedSize(378, 48)
        self.model_edit.setReadOnly(True)
        self.original_model_edit_size = (378, 48)  # 원본 크기 저장

        model_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        model_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.model_edit.setObjectName("model_edit")
        self.model_edit.setStyleSheet(f"""
            QLineEdit#model_edit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                border-image: url({model_input_default}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#model_edit[hasText="true"] {{
                border-image: url({model_input_filled}) 0 0 0 0 stretch stretch;
            }}
        """)

        def update_model_background():
            has_text = bool(self.model_edit.text().strip())
            self.model_edit.setProperty("hasText", "true" if has_text else "false")
            self.model_edit.style().unpolish(self.model_edit)
            self.model_edit.style().polish(self.model_edit)

        self.model_edit.textChanged.connect(update_model_background)
        self.model_edit.setProperty("hasText", "false")

        model_field_layout.addWidget(self.model_edit)
        version_model_layout.addWidget(self.model_field_widget)

        input_layout.addWidget(self.version_model_row, alignment=Qt.AlignHCenter)

        # 시험유형, 시험대상 행 (776x82px)
        self.category_target_row = QWidget()
        self.category_target_row.setFixedSize(776, 82)
        self.category_target_row.setStyleSheet("QWidget { background: transparent; }")
        self.original_category_target_row_size = (776, 82)  # 원본 크기 저장
        category_target_layout = QHBoxLayout(self.category_target_row)
        category_target_layout.setContentsMargins(0, 0, 0, 0)
        category_target_layout.setSpacing(20)  # 간격 20px

        # 시험유형 필드 (378x82px)
        self.test_category_widget = QWidget()
        self.test_category_widget.setFixedSize(378, 82)
        self.test_category_widget.setStyleSheet("QWidget { background: transparent; }")
        self.original_test_category_field_size = (378, 82)  # 원본 크기 저장

        test_category_layout = QVBoxLayout(self.test_category_widget)
        test_category_layout.setContentsMargins(0, 0, 0, 0)
        test_category_layout.setSpacing(6)

        # 시험유형 라벨 (378x28px)
        self.test_category_label = QLabel("시험유형")
        self.test_category_label.setFixedSize(378, 28)
        self.test_category_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.original_test_category_label_size = (378, 28)  # 원본 크기 저장
        test_category_layout.addWidget(self.test_category_label)

        # 시험유형 입력칸 (378x48px)
        self.test_category_edit = QLineEdit()
        self.test_category_edit.setFixedSize(378, 48)
        self.test_category_edit.setReadOnly(True)
        self.original_test_category_edit_size = (378, 48)  # 원본 크기 저장

        test_category_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        test_category_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.test_category_edit.setObjectName("test_category_edit")
        self.test_category_edit.setStyleSheet(f"""
            QLineEdit#test_category_edit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                border-image: url({test_category_input_default}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#test_category_edit[hasText="true"] {{
                border-image: url({test_category_input_filled}) 0 0 0 0 stretch stretch;
            }}
        """)

        def update_test_category_background():
            has_text = bool(self.test_category_edit.text().strip())
            self.test_category_edit.setProperty("hasText", "true" if has_text else "false")
            self.test_category_edit.style().unpolish(self.test_category_edit)
            self.test_category_edit.style().polish(self.test_category_edit)

        self.test_category_edit.textChanged.connect(update_test_category_background)
        self.test_category_edit.setProperty("hasText", "false")

        test_category_layout.addWidget(self.test_category_edit)
        category_target_layout.addWidget(self.test_category_widget)

        # 시험대상 필드 (378x82px)
        self.target_system_widget = QWidget()
        self.target_system_widget.setFixedSize(378, 82)
        self.target_system_widget.setStyleSheet("QWidget { background: transparent; }")
        self.original_target_system_field_size = (378, 82)  # 원본 크기 저장

        target_system_layout = QVBoxLayout(self.target_system_widget)
        target_system_layout.setContentsMargins(0, 0, 0, 0)
        target_system_layout.setSpacing(6)

        # 시험대상 라벨 (378x28px)
        self.target_system_label = QLabel("시험대상")
        self.target_system_label.setFixedSize(378, 28)
        self.target_system_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.original_target_system_label_size = (378, 28)  # 원본 크기 저장
        target_system_layout.addWidget(self.target_system_label)

        # 시험대상 입력칸 (378x48px)
        self.target_system_edit = QLineEdit()
        self.target_system_edit.setFixedSize(378, 48)
        self.target_system_edit.setReadOnly(True)
        self.original_target_system_edit_size = (378, 48)  # 원본 크기 저장

        target_system_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        target_system_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.target_system_edit.setObjectName("target_system_edit")
        self.target_system_edit.setStyleSheet(f"""
            QLineEdit#target_system_edit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                border-image: url({target_system_input_default}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#target_system_edit[hasText="true"] {{
                border-image: url({target_system_input_filled}) 0 0 0 0 stretch stretch;
            }}
        """)

        def update_target_system_background():
            has_text = bool(self.target_system_edit.text().strip())
            self.target_system_edit.setProperty("hasText", "true" if has_text else "false")
            self.target_system_edit.style().unpolish(self.target_system_edit)
            self.target_system_edit.style().polish(self.target_system_edit)

        self.target_system_edit.textChanged.connect(update_target_system_background)
        self.target_system_edit.setProperty("hasText", "false")

        target_system_layout.addWidget(self.target_system_edit)
        category_target_layout.addWidget(self.target_system_widget)

        input_layout.addWidget(self.category_target_row, alignment=Qt.AlignHCenter)

        # 시험분야, 시험범위 행 (776x82px)
        self.group_range_row = QWidget()
        self.group_range_row.setFixedSize(776, 82)
        self.group_range_row.setStyleSheet("QWidget { background: transparent; }")
        self.original_group_range_row_size = (776, 82)  # 원본 크기 저장
        group_range_layout = QHBoxLayout(self.group_range_row)
        group_range_layout.setContentsMargins(0, 0, 0, 0)
        group_range_layout.setSpacing(20)  # 간격 20px

        # 시험분야 필드 (378x82px)
        self.test_group_widget = QWidget()
        self.test_group_widget.setFixedSize(378, 82)
        self.test_group_widget.setStyleSheet("QWidget { background: transparent; }")
        self.original_test_group_field_size = (378, 82)  # 원본 크기 저장

        test_group_layout = QVBoxLayout(self.test_group_widget)
        test_group_layout.setContentsMargins(0, 0, 0, 0)
        test_group_layout.setSpacing(6)

        # 시험분야 라벨 (378x28px)
        self.test_group_label = QLabel("시험분야")
        self.test_group_label.setFixedSize(378, 28)
        self.test_group_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.original_test_group_label_size = (378, 28)  # 원본 크기 저장
        test_group_layout.addWidget(self.test_group_label)

        # 시험분야 입력칸 (378x48px)
        self.test_group_edit = QLineEdit()
        self.test_group_edit.setFixedSize(378, 48)
        self.test_group_edit.setReadOnly(True)
        self.original_test_group_edit_size = (378, 48)  # 원본 크기 저장

        test_group_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        test_group_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.test_group_edit.setObjectName("test_group_edit")
        self.test_group_edit.setStyleSheet(f"""
            QLineEdit#test_group_edit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                border-image: url({test_group_input_default}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#test_group_edit[hasText="true"] {{
                border-image: url({test_group_input_filled}) 0 0 0 0 stretch stretch;
            }}
        """)

        def update_test_group_background():
            has_text = bool(self.test_group_edit.text().strip())
            self.test_group_edit.setProperty("hasText", "true" if has_text else "false")
            self.test_group_edit.style().unpolish(self.test_group_edit)
            self.test_group_edit.style().polish(self.test_group_edit)

        self.test_group_edit.textChanged.connect(update_test_group_background)
        self.test_group_edit.setProperty("hasText", "false")

        test_group_layout.addWidget(self.test_group_edit)
        group_range_layout.addWidget(self.test_group_widget)

        # 시험범위 필드 (378x82px)
        self.test_range_widget = QWidget()
        self.test_range_widget.setFixedSize(378, 82)
        self.test_range_widget.setStyleSheet("QWidget { background: transparent; }")
        self.original_test_range_field_size = (378, 82)  # 원본 크기 저장

        test_range_layout = QVBoxLayout(self.test_range_widget)
        test_range_layout.setContentsMargins(0, 0, 0, 0)
        test_range_layout.setSpacing(6)

        # 시험범위 라벨 (378x28px)
        self.test_range_label = QLabel("시험범위")
        self.test_range_label.setFixedSize(378, 28)
        self.test_range_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.original_test_range_label_size = (378, 28)  # 원본 크기 저장
        test_range_layout.addWidget(self.test_range_label)

        # 시험범위 입력칸 (378x48px)
        self.test_range_edit = QLineEdit()
        self.test_range_edit.setFixedSize(378, 48)
        self.test_range_edit.setReadOnly(True)
        self.original_test_range_edit_size = (378, 48)  # 원본 크기 저장

        test_range_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        test_range_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.test_range_edit.setObjectName("test_range_edit")
        self.test_range_edit.setStyleSheet(f"""
            QLineEdit#test_range_edit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                border-image: url({test_range_input_default}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#test_range_edit[hasText="true"] {{
                border-image: url({test_range_input_filled}) 0 0 0 0 stretch stretch;
            }}
        """)

        def update_test_range_background():
            has_text = bool(self.test_range_edit.text().strip())
            self.test_range_edit.setProperty("hasText", "true" if has_text else "false")
            self.test_range_edit.style().unpolish(self.test_range_edit)
            self.test_range_edit.style().polish(self.test_range_edit)

        self.test_range_edit.textChanged.connect(update_test_range_background)
        self.test_range_edit.setProperty("hasText", "false")

        test_range_layout.addWidget(self.test_range_edit)
        group_range_layout.addWidget(self.test_range_widget)

        input_layout.addWidget(self.group_range_row, alignment=Qt.AlignHCenter)

        # 시험유형 변경 시 관리자 코드 필드 활성화/비활성화
        self.test_category_edit.textChanged.connect(self.form_validator.handle_test_category_change)
        self.test_category_edit.textChanged.connect(self.check_start_button_state)

        # 시험범위 변경 시 UI 표시 텍스트 변환
        self.test_range_edit.textChanged.connect(self.form_validator.handle_test_range_change)

        # Input Container 하단 여백 20px
        input_layout.addSpacing(20)

        layout.addWidget(self.input_container, alignment=Qt.AlignHCenter)

        # Divider 이미지 (반응형)
        self.divider = QLabel()
        self.divider_pixmap = QPixmap(resource_path("assets/image/test_info/divider.png"))
        self.divider.setPixmap(self.divider_pixmap)
        self.divider.setScaledContents(True)
        divider_height = self.divider_pixmap.height() if self.divider_pixmap.height() > 0 else 1
        self.divider.setFixedSize(776, divider_height)
        self.original_divider_size = (776, divider_height)
        layout.addWidget(self.divider, alignment=Qt.AlignHCenter)

        # Divider와 관리자 코드 사이 간격 12px
        layout.addSpacing(12)

        # 관리자 코드 필드 (776x82px - 전체 너비) - 반응형
        admin_code_field = self.create_admin_code_field()
        self.admin_code_edit = admin_code_field["input"]
        self.admin_code_edit.setEchoMode(QLineEdit.Password)  # 비밀번호 모드
        self.admin_code_edit.setPlaceholderText("관리자 코드를 입력해주세요")
        self.admin_code_edit.setEnabled(False)  # 초기에는 비활성화 (시험 정보 불러오기 전)
        layout.addWidget(admin_code_field["widget"], alignment=Qt.AlignHCenter)

        # 관리자 코드 입력 시 숫자 검증 및 버튼 상태 업데이트
        self.admin_code_edit.textChanged.connect(self.form_validator.validate_admin_code)
        self.admin_code_edit.textChanged.connect(self.check_start_button_state)
        self.admin_code_edit.textChanged.connect(self.check_next_button_state)  # 1페이지 다음 버튼 상태 체크

        # 첫 번째 페이지 필드들의 변경 시 다음 버튼 상태 체크
        for field in [self.company_edit, self.product_edit, self.version_edit, self.model_edit,
                     self.test_category_edit, self.target_system_edit, self.test_group_edit, self.test_range_edit,
                     self.admin_code_edit]:
            field.textChanged.connect(self.check_next_button_state)

        # 관리자 코드와 버튼 사이 간격 32px
        layout.addSpacing(32)

        # 하단 버튼 (다음: 왼쪽, 종료: 오른쪽) - 각 378x48px, gap 20px, 전체 776x48px
        # 고정 크기 컨테이너로 감싸서 간격 유지
        # ✅ 반응형: 인스턴스 변수로 변경
        self.page1_button_container = QWidget()
        self.page1_button_container.setFixedSize(776, 48)
        self.original_page1_button_container_size = (776, 48)
        button_layout = QHBoxLayout(self.page1_button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(20)  # 버튼 간격 20px

        # 다음 버튼 (왼쪽) - 378x48px
        # ✅ 반응형: 원본 크기 저장
        self.next_btn = QPushButton("다음")
        self.next_btn.setFixedSize(378, 48)
        self.original_next_btn_size = (378, 48)
        btn_next_enabled = resource_path("assets/image/test_info/btn_다음_enabled.png").replace(chr(92), "/")
        btn_next_hover = resource_path("assets/image/test_info/btn_다음_Hover.png").replace(chr(92), "/")
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url({btn_next_enabled}) 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                border-image: url({btn_next_hover}) 0 0 0 0 stretch stretch;
            }}
        """)
        self.next_btn.clicked.connect(self.go_to_next_page)
        button_layout.addWidget(self.next_btn)

        # 종료 버튼 (오른쪽) - 378x48px
        # ✅ 반응형: 인스턴스 변수로 변경 및 원본 크기 저장
        self.page1_exit_btn = QPushButton("종료")
        self.page1_exit_btn.setFixedSize(378, 48)
        self.original_page1_exit_btn_size = (378, 48)
        btn_exit_enabled = resource_path("assets/image/test_info/btn_종료_enabled.png").replace(chr(92), "/")
        btn_exit_hover = resource_path("assets/image/test_info/btn_종료_Hover.png").replace(chr(92), "/")
        self.page1_exit_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url({btn_exit_enabled}) 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }}
            QPushButton:hover {{
                border-image: url({btn_exit_hover}) 0 0 0 0 stretch stretch;
            }}
        """)
        self.page1_exit_btn.clicked.connect(self.exit_btn_clicked)
        button_layout.addWidget(self.page1_exit_btn)

        layout.addWidget(self.page1_button_container, alignment=Qt.AlignHCenter)

        # 세로 확장 시 여분의 공간을 하단으로 밀어냄
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def create_input_field(self, label_text, width=768):
        """
        입력 필드 생성
        - 전체 크기: width x 82px
        - 라벨: width x 28px (6px 간격)
        - 입력칸: width x 48px

        Args:
            label_text: 라벨 텍스트
            width: 필드 너비 (기본값: 768, 2열일 경우: 374)
        """
        field_widget = QWidget()
        field_widget.setFixedSize(width, 82)
        field_layout = QVBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)  # 라벨과 입력칸 사이 간격 6px

        # 라벨 (width x 28px)
        label = QLabel(label_text)
        label.setFixedSize(width, 28)
        label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 16px;
                font-weight: 500;
                letter-spacing: -0.16px;
            }
        """)
        field_layout.addWidget(label)

        # 입력칸 (width x 48px)
        input_field = QLineEdit()
        input_field.setFixedSize(width, 48)
        input_field.setStyleSheet("""
            QLineEdit {
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 400;
                letter-spacing: -0.17px;
                color: #000000;
                padding: 0 24px;
                border: 1px solid #E8E8E8;
                border-radius: 4px;
            }
            QLineEdit::placeholder {
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 500;
                letter-spacing: -0.17px;
                color: #868686;
            }
        """)
        field_layout.addWidget(input_field)

        field_widget.setLayout(field_layout)

        return {
            "widget": field_widget,
            "input": input_field
        }

    def create_readonly_input_field(self, label_text, width=776):
        """
        읽기전용 입력 필드 생성 (불러온 정보용 - 이미지 배경)
        - 전체 크기: width x 82px
        - 라벨: width x 28px (6px 간격)
        - 입력칸: width x 48px (이미지 배경 사용)

        Args:
            label_text: 라벨 텍스트
            width: 필드 너비 (776: wide 이미지, 378: small 이미지)
        """
        field_widget = QWidget()
        field_widget.setFixedSize(width, 82)
        field_layout = QVBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)  # 라벨과 입력칸 사이 간격 6px

        # 라벨 (width x 28px)
        label = QLabel(label_text)
        label.setFixedSize(width, 28)
        label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 16px;
                font-weight: 500;
                letter-spacing: -0.16px;
            }
        """)
        field_layout.addWidget(label)

        # 입력칸 (width x 48px) - 이미지 배경
        input_field = QLineEdit()
        input_field.setFixedSize(width, 48)

        # 한글 경로 처리를 위한 절대 경로 사용
        import os
        # 너비에 따라 다른 이미지 사용
        if width >= 768:
            # 전체 너비 (776px) - wide 이미지
            input_default = resource_path("assets/image/test_info/불러온정보_w_default.png").replace(chr(92), "/")
            input_filled = resource_path("assets/image/test_info/불러온정보_w_filled.png").replace(chr(92), "/")
        else:
            # 반 너비 (378px) - small 이미지
            input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
            input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 400;
                letter-spacing: -0.17px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background-image: url({input_default});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QLineEdit[hasText="true"] {{
                background-image: url({input_filled});
            }}
            QLineEdit::placeholder {{
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 500;
                letter-spacing: -0.17px;
                color: #868686;
            }}
        """)

        # 텍스트 입력 시 배경 이미지 변경을 위한 동적 프로퍼티 업데이트
        def update_background():
            has_text = bool(input_field.text().strip())
            input_field.setProperty("hasText", "true" if has_text else "false")
            input_field.style().unpolish(input_field)
            input_field.style().polish(input_field)

        input_field.textChanged.connect(update_background)
        input_field.setProperty("hasText", "false")  # 초기 상태
        field_layout.addWidget(input_field)

        field_widget.setLayout(field_layout)

        return {
            "widget": field_widget,
            "input": input_field
        }

    def create_admin_code_field(self):
        """
        관리자 코드 입력 필드 생성 (776x82px)
        - 라벨: 776x28px (font 18px weight 400)
        - gap: 6px
        - 입력칸: 768x48px
        """
        # 필드 위젯 (776x82px)
        self.admin_code_widget = QWidget()
        self.admin_code_widget.setFixedSize(776, 82)
        self.original_admin_code_widget_size = (776, 82)

        # 레이아웃 설정
        field_layout = QVBoxLayout(self.admin_code_widget)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)

        # 라벨 "관리자 코드 입력" (776x28px)
        self.admin_code_label = QLabel("관리자 코드 입력")
        self.admin_code_label.setFixedSize(776, 28)
        self.original_admin_code_label_size = (776, 28)
        self.admin_code_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        field_layout.addWidget(self.admin_code_label)

        # 입력칸 (768x48px)
        input_field = QLineEdit()
        input_field.setFixedSize(768, 48)
        input_field.setObjectName("admin_code_input")

        # 입력 필드 배경 이미지
        input_enabled = resource_path("assets/image/test_info/input_enabled.png").replace(chr(92), "/")
        input_disabled = resource_path("assets/image/test_info/input_disabled.png").replace(chr(92), "/")
        input_hover = resource_path("assets/image/test_info/input_Hover.png").replace(chr(92), "/")
        input_filled = resource_path("assets/image/test_info/input_filled.png").replace(chr(92), "/")

        input_field.setStyleSheet(f"""
            QLineEdit#admin_code_input {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                outline: none;
                border-image: url({input_enabled}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#admin_code_input::placeholder {{
                font-size: 18px;
                font-weight: 500;
                color: #868686;
            }}
            QLineEdit#admin_code_input:focus {{
                border: none;
                outline: none;
                border-image: url({input_enabled}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#admin_code_input:hover:enabled:!focus[hasText="false"] {{
                border-image: url({input_hover}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#admin_code_input:disabled {{
                border-image: url({input_disabled}) 0 0 0 0 stretch stretch;
            }}
            QLineEdit#admin_code_input[hasText="true"] {{
                border-image: url({input_filled}) 0 0 0 0 stretch stretch;
            }}
        """)

        # 텍스트 입력 시 배경 이미지 변경을 위한 동적 프로퍼티 업데이트
        def update_background():
            has_text = bool(input_field.text().strip())
            input_field.setProperty("hasText", "true" if has_text else "false")
            input_field.style().unpolish(input_field)
            input_field.style().polish(input_field)

        input_field.textChanged.connect(update_background)
        input_field.setProperty("hasText", "false")

        # 인스턴스 변수로 저장 (반응형용)
        self.admin_code_input = input_field
        self.original_admin_code_input_size = (768, 48)

        field_layout.addWidget(input_field)

        return {
            "widget": self.admin_code_widget,
            "input": input_field
        }

    def create_test_field_group(self):
        """시험 분야별 시나리오 그룹 (QGroupBox)"""
        group = QGroupBox()  # 타이틀 제거 (배경 이미지에 포함)
        group.setFixedSize(744, 240)

        # 배경 불투명 설정
        group.setAutoFillBackground(True)
        palette = group.palette()
        palette.setColor(group.backgroundRole(), QColor("#FFFFFF"))
        group.setPalette(palette)

        # QGroupBox 스타일 설정
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                padding-top: 0px;
                background-color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 두 개의 독립적인 테이블을 나란히 배치하기 위한 수평 레이아웃
        tables_layout = QHBoxLayout()
        tables_layout.setContentsMargins(0, 0, 0, 0)
        tables_layout.setSpacing(0)

        # 시험 분야 테이블 (372px x 240px) - 1개 컬럼 (반응형)
        self.test_field_table = TestFieldTableWidget(0, 1)
        self.test_field_table.setFixedSize(372, 240)
        self.original_test_field_table_size = (372, 240)
        self.test_field_table.setHorizontalHeaderLabels(["시험 분야"])

        # 시험 시나리오 테이블 (372px x 240px) - 1개 컬럼 (반응형)
        self.scenario_table = TestFieldTableWidget(0, 1)
        self.scenario_table.setFixedSize(372, 240)
        self.original_scenario_table_size = (372, 240)
        self.scenario_table.setHorizontalHeaderLabels(["시험 시나리오"])

        # === 시험 분야 테이블 설정 ===
        field_header = self.test_field_table.horizontalHeader()
        field_header.setFixedHeight(31)
        field_header.setSectionResizeMode(0, QHeaderView.Stretch)  # 자동으로 테이블 너비 채우기

        # 행 높이 설정
        self.test_field_table.verticalHeader().setDefaultSectionSize(39)
        self.test_field_table.verticalHeader().setVisible(False)
        self.original_test_field_row_height = 39  # 원본 행 높이 저장

        # 편집 불가 설정
        self.test_field_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.test_field_table.setAlternatingRowColors(False)
        self.test_field_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)
        # 스크롤바 비활성화 (공백 방지)
        self.test_field_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.test_field_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # === 시험 시나리오 테이블 설정 ===
        scenario_header = self.scenario_table.horizontalHeader()
        scenario_header.setFixedHeight(31)
        scenario_header.setSectionResizeMode(0, QHeaderView.Stretch)  # 자동으로 테이블 너비 채우기

        # 행 높이 설정
        self.scenario_table.verticalHeader().setDefaultSectionSize(39)
        self.scenario_table.verticalHeader().setVisible(False)
        self.original_scenario_row_height = 39  # 원본 행 높이 저장

        # 편집 불가 설정
        self.scenario_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scenario_table.setAlternatingRowColors(False)
        self.scenario_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.scenario_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scenario_table.cellClicked.connect(self.on_scenario_selected)
        # 스크롤바 비활성화 (공백 방지)
        self.scenario_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scenario_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # === 공통 스타일 정의 ===
        table_style = """
            QTableWidget {
                border: 1px solid #CECECE;
                gridline-color: #CCCCCC;
                show-decoration-selected: 0;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                color: #1B1B1C;
                outline: 0;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
            }
            QTableWidget::item:selected {
                color: #1B1B1C;
                background-color: transparent;
            }
            QTableWidget::item:focus {
                outline: none;
                border: none;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                border-right: 1px solid #CCCCCC;
                color: #1B1B1C;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #EDF0F3;
            }
        """

        # 시험 분야 테이블 스타일 (왼쪽 테두리 + 오른쪽 세로선)
        self.test_field_table.setStyleSheet(table_style + """
            QTableWidget {
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                border-right: 1px solid #CCCCCC;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)

        # 시험 시나리오 테이블 스타일 (오른쪽 테두리만)
        self.scenario_table.setStyleSheet(table_style + """
            QTableWidget {
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                border-left: none;
            }
        """)

        # 마지막으로 클릭된 시험 분야의 행을 추적
        self.selected_test_field_row = None

        # 폰트 설정 (stylesheet 이후에 강제 적용)
        cell_font = QFont("Noto Sans KR")
        cell_font.setPixelSize(19)
        cell_font.setWeight(QFont.Normal)

        header_font = QFont("Noto Sans KR")
        header_font.setPixelSize(18)
        header_font.setWeight(QFont.DemiBold)

        # 시험 분야 테이블 폰트
        self.test_field_table.setFont(cell_font)
        self.test_field_table.horizontalHeader().setFont(header_font)

        # 시험 시나리오 테이블 폰트
        self.scenario_table.setFont(cell_font)
        self.scenario_table.horizontalHeader().setFont(header_font)

        # 시험 분야 테이블 배경색 설정
        from PyQt5.QtGui import QPalette
        self.test_field_table.setAutoFillBackground(True)
        self.test_field_table.setAttribute(Qt.WA_OpaquePaintEvent, True)
        palette = self.test_field_table.palette()
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.test_field_table.setPalette(palette)

        self.test_field_table.viewport().setAutoFillBackground(True)
        viewport_palette = self.test_field_table.viewport().palette()
        viewport_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        viewport_palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.test_field_table.viewport().setPalette(viewport_palette)

        # 시험 시나리오 테이블 배경색 설정
        self.scenario_table.setAutoFillBackground(True)
        self.scenario_table.setAttribute(Qt.WA_OpaquePaintEvent, True)
        scenario_palette = self.scenario_table.palette()
        scenario_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        scenario_palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.scenario_table.setPalette(scenario_palette)

        self.scenario_table.viewport().setAutoFillBackground(True)
        scenario_viewport_palette = self.scenario_table.viewport().palette()
        scenario_viewport_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        scenario_viewport_palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.scenario_table.viewport().setPalette(scenario_viewport_palette)

        # 시험 시나리오 테이블 배경 (viewport 위에 오버레이, 시험 분야 선택 시 #E3F2FF 배경)
        self.scenario_column_background = QLabel("")
        self.scenario_column_background.setParent(self.scenario_table.viewport())
        self.scenario_column_background.setStyleSheet("""
            QLabel {
                background-color: #E3F2FF;
            }
        """)
        # viewport 기준으로 전체 영역 커버 (반응형)
        self.scenario_column_background.setGeometry(0, 0, 372, 240)
        self.original_scenario_column_background_geometry = (0, 0, 372, 240)
        self.scenario_column_background.lower()  # 셀들 뒤로 배치
        self.scenario_column_background.hide()  # 초기에는 숨김

        # 시험 시나리오 안내 문구 QLabel (시나리오 테이블 위에 오버레이)
        self.scenario_placeholder_label = QLabel("시험분야를 선택하면\n시나리오가 표시됩니다.")
        self.scenario_placeholder_label.setParent(self.scenario_table)
        self.scenario_placeholder_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.scenario_placeholder_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #6B6B6B;
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-bottom-right-radius: 4px;
                padding-top: 40px;
            }
        """)
        # 헤더 아래 영역에 배치 (반응형)
        self.scenario_placeholder_label.setGeometry(0, 31, 372, 209)  # x, y, width, height
        self.original_scenario_placeholder_geometry = (0, 31, 372, 209)
        self.scenario_placeholder_label.hide()  # 초기에는 숨김

        # 두 테이블을 수평 레이아웃에 추가
        tables_layout.addWidget(self.test_field_table)
        tables_layout.addWidget(self.scenario_table)

        # 수평 레이아웃을 메인 레이아웃에 추가
        layout.addLayout(tables_layout)

        group.setLayout(layout)
        return group

    def create_test_api_group(self):
        """시험 API 그룹 (QGroupBox)"""
        group = QGroupBox()  # 타이틀 제거 (배경 이미지에 포함)
        group.setFixedSize(744, 376)

        # 배경 불투명 설정
        group.setAutoFillBackground(True)
        palette = group.palette()
        palette.setColor(group.backgroundRole(), QColor("#FFFFFF"))
        group.setPalette(palette)

        # QGroupBox 스타일 설정
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                padding-top: 0px;
                background-color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 시험 API 테이블 (744x376px) (반응형)
        self.api_test_table = QTableWidget(0, 2)
        self.api_test_table.setFixedSize(744, 376)
        self.original_api_test_table_size = (744, 376)

        self.api_test_table.setHorizontalHeaderLabels(["기능명", "API명"])

        # 헤더 설정
        header = self.api_test_table.horizontalHeader()
        header.setFixedHeight(31)  # 31px로 변경

        # 행 번호 열 너비 설정
        self.api_test_table.verticalHeader().setFixedWidth(50)

        header.resizeSection(0, 346)
        header.resizeSection(1, 346)

        # 헤더 폰트 설정 (18px)
        header_font = QFont("Noto Sans KR")
        header_font.setPixelSize(18)
        header_font.setWeight(QFont.DemiBold)
        self.api_test_table.horizontalHeader().setFont(header_font)

        # 셀 높이 설정 (39px)
        self.api_test_table.verticalHeader().setDefaultSectionSize(39)
        self.original_api_row_height = 39  # 원본 행 높이 저장

        # 셀 폰트 설정 (19px)
        cell_font = QFont("Noto Sans KR")
        cell_font.setPixelSize(19)
        self.api_test_table.setFont(cell_font)

        # 편집 비활성화
        self.api_test_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 왼쪽 행 번호 헤더 설정
        vertical_header = self.api_test_table.verticalHeader()
        vertical_header.setFixedWidth(50)  # 행 번호 너비 고정 (시험 API 테이블과 동일)
        vertical_header.setDefaultAlignment(Qt.AlignCenter)

        # 행 번호 폰트 설정 (19px)
        row_number_font = QFont("Noto Sans KR")
        row_number_font.setPixelSize(19)
        vertical_header.setFont(row_number_font)


        # 세로 grid line 제거
        self.api_test_table.setShowGrid(False)

        # 스크롤바 비활성화
        self.api_test_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 테이블 스타일 설정
        self.api_test_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                letter-spacing: 0.098px;
            }
            QTableWidget::item {
                background-color: #FFFFFF;
                border-bottom: 1px solid #CCCCCC;
                border-right: none;
                padding-right: 14px;
                color: #1B1B1C;
            }
            QTableWidget::item:selected {
                background-color: #FFFFFF;
                color: #1B1B1C;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                font-family: 'Noto Sans KR';
                font-weight: 600;
                letter-spacing: -0.156px;
                color: #1B1B1C;
            }
            QHeaderView::section:vertical {
                background-color: #FFFFFF;
                border: none;
                border-right: none;
                border-bottom: 1px solid #CCCCCC;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                letter-spacing: 0.098px;
                color: #1B1B1C;
            }
            QTableCornerButton::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
            }
            QTableWidget::viewport {
                background-color: #FFFFFF;
            }
            QScrollBar:vertical {
                border: none;
                background: #DFDFDF;
                width: 14px;
                margin-top: 31px;
                margin-bottom: 0px;
                margin-left: 0px;
                margin-right: 0px;
                border-radius: 4px;
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
            }
        """)

        # Stylesheet 이후 배경색 강제 설정 (stylesheet보다 나중에 적용)
        self.api_test_table.setAutoFillBackground(True)
        self.api_test_table.setAttribute(Qt.WA_OpaquePaintEvent, True)

        from PyQt5.QtGui import QPalette
        palette = self.api_test_table.palette()
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.api_test_table.setPalette(palette)

        # Viewport 배경색 마지막에 강제 설정
        self.api_test_table.viewport().setAutoFillBackground(True)
        viewport_palette = self.api_test_table.viewport().palette()
        viewport_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        viewport_palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.api_test_table.viewport().setPalette(viewport_palette)

        # 헤더 오버레이 위젯 (테이블 헤더 위에 덮어씌우기) (반응형)
        self.api_header_overlay = QWidget()
        self.api_header_overlay.setParent(self.api_test_table)
        self.api_header_overlay.setGeometry(0, 0, 744, 31)  # 테이블 상단 전체
        self.original_api_header_overlay_geometry = (0, 0, 744, 31)
        self.api_header_overlay.setStyleSheet("""
            QWidget {
                background-color: #EDF0F3;
                border: 1px solid #CECECE;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        """)

        header_layout = QHBoxLayout(self.api_header_overlay)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # 헤더 컬럼: 행번호(50 고정) + 기능명(비율) + API명(비율)
        # 행번호 라벨
        self.api_header_row_label = QLabel("")
        self.api_header_row_label.setFixedSize(50, 31)
        self.api_header_row_label.setAlignment(Qt.AlignCenter)
        self.api_header_row_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(self.api_header_row_label)

        # 기능명 라벨 (반응형)
        self.api_header_func_label = QLabel("기능명")
        self.api_header_func_label.setFixedSize(346, 31)
        self.original_api_header_func_label_size = (346, 31)
        self.api_header_func_label.setAlignment(Qt.AlignCenter)
        self.api_header_func_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 600;
                letter-spacing: -0.156px;
            }
        """)
        header_layout.addWidget(self.api_header_func_label)

        # API명 라벨 (반응형)
        self.api_header_api_label = QLabel("API명")
        self.api_header_api_label.setFixedSize(348, 31)
        self.original_api_header_api_label_size = (348, 31)
        self.api_header_api_label.setAlignment(Qt.AlignCenter)
        self.api_header_api_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 600;
                letter-spacing: -0.156px;
            }
        """)
        header_layout.addWidget(self.api_header_api_label)

        self.api_header_overlay.show()
        self.api_header_overlay.raise_()  # 최상위로 올리기

        # 시험 API 안내 문구 QLabel (테이블 위에 오버레이)
        self.api_placeholder_label = QLabel("시험 시나리오를 선택하면\nAPI가 표시됩니다.")
        self.api_placeholder_label.setParent(self.api_test_table)
        self.api_placeholder_label.setAlignment(Qt.AlignCenter)
        self.api_placeholder_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #6B6B6B;
                background-color: transparent;
                padding-top: 10px;
            }
        """)
        # 헤더 높이(31px) + 행 번호 너비(50px) 고려하여 테이블 중앙에 배치
        self.api_placeholder_label.setGeometry(50, 31, 694, 345)  # x, y, width, height
        self.original_api_placeholder_geometry = (50, 31, 694, 345)
        self.api_placeholder_label.show()  # 초기에는 표시

        layout.addWidget(self.api_test_table)
        group.setLayout(layout)
        return group

    def create_auth_section(self):
        """인증 방식 섹션 (타이틀 제외, 744x240px) - 반응형"""
        section = QGroupBox()
        section.setFixedSize(744, 240)
        self.original_auth_section_size = (744, 240)
        section.setStyleSheet("QGroupBox { border: none; margin-top: 0px; padding-top: 0px; background-color: transparent; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 콘텐츠 영역 (744x240px) - 반응형
        self.auth_content_widget = QWidget()
        self.auth_content_widget.setFixedSize(744, 240)
        self.original_auth_content_widget_size = (744, 240)

        # 배경 색상 설정
        self.auth_content_widget.setStyleSheet("""
            #content_widget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
            }
            QRadioButton {
                border: none;
                background-color: transparent;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
            QLineEdit {
                border: none;
            }
        """)
        self.auth_content_widget.setObjectName("content_widget")

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(24, 16, 24, 16)
        content_layout.setSpacing(0)

        # 왼쪽: 인증 방식 선택 영역 (289x208px) - 반응형
        self.auth_type_widget = QWidget()
        self.auth_type_widget.setFixedSize(289, 208)
        self.original_auth_type_widget_size = (289, 208)
        self.auth_type_widget.setStyleSheet("background-color: transparent;")
        auth_type_layout = QVBoxLayout()
        auth_type_layout.setContentsMargins(0, 12, 0, 12)  # 상하 12px
        auth_type_layout.setSpacing(12)  # gap 12px

        # Digest Auth 박스 (289x86px) - 반응형
        self.digest_option = QWidget()
        self.digest_option.setFixedSize(289, 86)
        self.original_digest_option_size = (289, 86)
        # 초기 상태: 선택됨 (digest_radio가 기본 체크되어 있음)
        self.digest_option.setStyleSheet("""
            QWidget {
                background-color: #E9F6FE;
                border: 1px solid #2B96ED;
                border-radius: 8px;
            }
        """)
        digest_option_main_layout = QHBoxLayout()
        digest_option_main_layout.setContentsMargins(16, 16, 16, 16)  # 상하좌우 16px
        digest_option_main_layout.setSpacing(0)

        # 라디오 버튼 (30x54)
        self.digest_radio = QRadioButton()
        self.digest_radio.setFixedSize(30, 54)
        self.digest_radio.setChecked(True)
        self.digest_radio.setStyleSheet("""
            QRadioButton {
                border: none;
                background: transparent;
                padding-bottom: 26px;
            }
            QRadioButton::indicator {
                width: 28px;
                height: 28px;
            }
        """)
        digest_option_main_layout.addWidget(self.digest_radio, alignment=Qt.AlignTop)

        # 8px gap
        digest_option_main_layout.addSpacing(8)

        # 텍스트 영역 (수직 레이아웃)
        digest_text_layout = QVBoxLayout()
        digest_text_layout.setContentsMargins(0, 0, 0, 0)
        digest_text_layout.setSpacing(0)

        # "Digest Auth" 제목 (120x26)
        digest_label = QLabel("Digest Auth")
        digest_label.setFixedSize(120, 26)
        digest_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 20px;
                letter-spacing: -0.20px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        digest_text_layout.addWidget(digest_label)

        # 2px gap
        digest_text_layout.addSpacing(2)

        # "ID,PW 기반 인증 방식" 설명 (163x26)
        digest_desc = QLabel("ID,PW 기반 인증 방식")
        digest_desc.setFixedSize(163, 26)
        digest_desc.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #6B6B6B;
                border: none;
                background-color: transparent;
            }
        """)
        digest_text_layout.addWidget(digest_desc)

        digest_option_main_layout.addLayout(digest_text_layout)
        digest_option_main_layout.addStretch()

        self.digest_option.setLayout(digest_option_main_layout)
        auth_type_layout.addWidget(self.digest_option)

        # Bearer Token 박스 (289x86px) - 반응형
        self.bearer_option = QWidget()
        self.bearer_option.setFixedSize(289, 86)
        self.original_bearer_option_size = (289, 86)
        # 초기 상태: 선택 안됨
        self.bearer_option.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 8px;
            }
        """)
        bearer_option_main_layout = QHBoxLayout()
        bearer_option_main_layout.setContentsMargins(16, 16, 16, 16)  # 상하좌우 16px
        bearer_option_main_layout.setSpacing(0)

        # 라디오 버튼 (30x54)
        self.bearer_radio = QRadioButton()
        self.bearer_radio.setFixedSize(30, 54)
        self.bearer_radio.setStyleSheet("""
            QRadioButton {
                border: none;
                background: transparent;
                padding-bottom: 26px;
            }
            QRadioButton::indicator {
                width: 27px;
                height: 27px;
            }
        """)
        bearer_option_main_layout.addWidget(self.bearer_radio, alignment=Qt.AlignTop)

        # 8px gap
        bearer_option_main_layout.addSpacing(8)

        # 텍스트 영역 (수직 레이아웃)
        bearer_text_layout = QVBoxLayout()
        bearer_text_layout.setContentsMargins(0, 0, 0, 0)
        bearer_text_layout.setSpacing(0)

        # "Bearer Token" 제목 (130x26)
        bearer_label = QLabel("Bearer Token")
        bearer_label.setFixedSize(130, 26)
        bearer_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 20px;
                letter-spacing: -0.20px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        bearer_text_layout.addWidget(bearer_label)

        # 2px gap
        bearer_text_layout.addSpacing(2)

        # "Token 기반 인증 방식" 설명 (163x26)
        bearer_desc = QLabel("Token 기반 인증 방식")
        bearer_desc.setFixedSize(163, 26)
        bearer_desc.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #6B6B6B;
                border: none;
                background-color: transparent;
            }
        """)
        bearer_text_layout.addWidget(bearer_desc)

        bearer_option_main_layout.addLayout(bearer_text_layout)
        bearer_option_main_layout.addStretch()

        self.bearer_option.setLayout(bearer_option_main_layout)
        auth_type_layout.addWidget(self.bearer_option)

        self.auth_type_widget.setLayout(auth_type_layout)
        content_layout.addWidget(self.auth_type_widget)

        # 라디오 버튼 토글 시 박스 스타일 변경
        self.digest_radio.toggled.connect(self.on_auth_type_changed)
        self.bearer_radio.toggled.connect(self.on_auth_type_changed)

        # 박스 전체 영역 클릭 시 라디오 버튼 선택되도록 클릭 이벤트 추가
        self.digest_option.mousePressEvent = lambda event: self.digest_radio.setChecked(True)
        self.bearer_option.mousePressEvent = lambda event: self.bearer_radio.setChecked(True)

        # divider 왼쪽 gap 12px
        content_layout.addSpacing(12)

        # 수직 divider (1x208px) - 반응형
        self.auth_divider = QLabel()
        self.auth_divider.setFixedSize(1, 208)
        self.original_auth_divider_size = (1, 208)
        divider_pixmap = QPixmap(resource_path("assets/image/test_config/divider.png"))
        self.auth_divider.setPixmap(divider_pixmap.scaled(1, 208, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        content_layout.addWidget(self.auth_divider)

        # divider 오른쪽 gap 12px
        content_layout.addSpacing(12)

        # 오른쪽: User ID/Password 입력 영역 (358x208px) - 반응형
        self.common_input_widget = QWidget()
        self.common_input_widget.setFixedSize(358, 208)
        self.original_common_input_widget_size = (358, 208)
        self.common_input_widget.setStyleSheet("background-color: transparent;")
        common_input_layout = QVBoxLayout()
        common_input_layout.setContentsMargins(0, 12, 0, 12)  # 상하 12px, 12px
        common_input_layout.setSpacing(0)

        # "사용자 ID입력" 문구 (358x29px)
        auth_input_title = QLabel("사용자 ID입력")
        auth_input_title.setFixedSize(358, 29)
        auth_input_title.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 20px;
                letter-spacing: -0.20px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        common_input_layout.addWidget(auth_input_title)

        # gap 10px
        common_input_layout.addSpacing(10)

        # "User ID" 문구 (358x26px)
        userid_label = QLabel("User ID")
        userid_label.setFixedSize(358, 26)
        userid_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        common_input_layout.addWidget(userid_label)

        # gap 4px
        common_input_layout.addSpacing(4)

        # 아이디 입력칸 (358x40px) - 반응형
        self.id_input = QLineEdit()
        self.id_input.setFixedSize(358, 40)
        self.original_id_input_size = (358, 40)
        self.id_input.setPlaceholderText("사용자 ID를 입력해주세요")
        digest_enabled = resource_path("assets/image/test_config/input_DigestAuth_enabled.png").replace(chr(92), "/")
        digest_disabled = resource_path("assets/image/test_config/input_DigestAuth_disabled.png").replace(chr(92), "/")
        self.id_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 24px;
                padding-right: 24px;
                border: none;
                border-image: url({digest_enabled}) 0 0 0 0 stretch stretch;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
            }}
            QLineEdit::placeholder {{
                color: #868686;
                font-size: 18px;
                font-weight: 500;
            }}
            QLineEdit:disabled {{
                border-image: url({digest_disabled}) 0 0 0 0 stretch stretch;
                color: #868686;
            }}
        """)
        common_input_layout.addWidget(self.id_input)

        # gap 6px
        common_input_layout.addSpacing(6)

        # "Password" 문구 (358x26px)
        password_label = QLabel("Password")
        password_label.setFixedSize(358, 26)
        password_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        common_input_layout.addWidget(password_label)

        # gap 4px
        common_input_layout.addSpacing(4)

        # password 입력칸 (358x40px) - 반응형
        self.pw_input = QLineEdit()
        self.pw_input.setFixedSize(358, 40)
        self.original_pw_input_size = (358, 40)
        self.pw_input.setPlaceholderText("암호를 입력해 주세요")
        self.pw_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 24px;
                padding-right: 24px;
                border: none;
                border-image: url({digest_enabled}) 0 0 0 0 stretch stretch;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
            }}
            QLineEdit::placeholder {{
                color: #868686;
                font-size: 18px;
                font-weight: 500;
            }}
            QLineEdit:disabled {{
                border-image: url({digest_disabled}) 0 0 0 0 stretch stretch;
                color: #868686;
            }}
        """)
        common_input_layout.addWidget(self.pw_input)

        self.common_input_widget.setLayout(common_input_layout)
        content_layout.addWidget(self.common_input_widget)

        self.auth_content_widget.setLayout(content_layout)
        layout.addWidget(self.auth_content_widget)

        # 라디오 버튼 그룹 설정
        from PyQt5.QtWidgets import QButtonGroup
        self.auth_button_group = QButtonGroup()
        self.auth_button_group.addButton(self.digest_radio)
        self.auth_button_group.addButton(self.bearer_radio)

        # 라디오 버튼 연결
        self.digest_radio.toggled.connect(self.update_start_button_state)
        self.bearer_radio.toggled.connect(self.update_start_button_state)

        # 입력 필드 변경 시 버튼 상태 체크
        self.id_input.textChanged.connect(self.check_start_button_state)
        self.pw_input.textChanged.connect(self.check_start_button_state)

        section.setLayout(layout)

        return section

    def on_auth_type_changed(self):
        """인증 방식 변경 시 박스 스타일 업데이트"""
        if self.digest_radio.isChecked():
            # Digest Auth 선택됨
            self.digest_option.setStyleSheet("""
                QWidget {
                    background-color: #E9F6FE;
                    border: 1px solid #2B96ED;
                    border-radius: 8px;
                }
            """)
            # Bearer Token 선택 안됨
            self.bearer_option.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    border: 1px solid #CECECE;
                    border-radius: 8px;
                }
            """)
        else:
            # Bearer Token 선택됨
            self.bearer_option.setStyleSheet("""
                QWidget {
                    background-color: #E9F6FE;
                    border: 1px solid #2B96ED;
                    border-radius: 8px;
                }
            """)
            # Digest Auth 선택 안됨
            self.digest_option.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    border: 1px solid #CECECE;
                    border-radius: 8px;
                }
            """)

    def create_connection_section(self):
        """접속 정보 섹션 (타이틀 제외, 744x376px) - 반응형"""
        section = QGroupBox()
        section.setFixedSize(744, 376)
        self.original_connection_section_size = (744, 376)
        section.setStyleSheet("QGroupBox { border: none; margin-top: 0px; padding-top: 0px; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # URL 테이블 (744x376px) - 2개 컬럼 (행번호 + URL) - 반응형 (api_test_table과 동일)
        self.url_table = QTableWidget(0, 2)  # 2개 컬럼: 행번호(50px) + URL(694px)
        self.url_table.setFixedSize(744, 376)
        self.original_url_table_size = (744, 376)
        self.url_table.setHorizontalHeaderLabels(["", "URL"])
        self.url_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.url_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.url_table.setSelectionMode(QAbstractItemView.NoSelection)  # 선택 비활성화 (이미지로 처리)

        # 헤더 설정
        header = self.url_table.horizontalHeader()
        header.setFixedHeight(31)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 행번호 컬럼: 고정
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # URL 컬럼: 전체 공간
        self.url_table.setColumnWidth(0, 50)  # 행번호 컬럼 50px

        # 왼쪽 행 번호 헤더 숨김 (컬럼 0으로 대체)
        vertical_header = self.url_table.verticalHeader()
        vertical_header.setVisible(False)

        # 세로 grid line 제거
        self.url_table.setShowGrid(False)

        # 행 높이 설정
        self.url_table.verticalHeader().setDefaultSectionSize(39)
        self.original_url_row_height = 39  # 원본 행 높이 저장

        # 선택된 URL 행 추적 변수
        self.selected_url_row = None

        # 스타일 설정 (이미지 배경 방식 - setCellWidget 사용)
        self.url_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 19px;
                letter-spacing: -0.19px;
            }
            QTableWidget::item {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
            QTableWidget::item:selected {
                background-color: transparent;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                padding: 4px;
                height: 31px;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 600;
                letter-spacing: -0.18px;
            }
            QTableCornerButton::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
            }
        """)

        # cellClicked는 사용하지 않음 - ClickableLabel의 clicked 시그널 사용
        layout.addWidget(self.url_table)

        section.setLayout(layout)
        return section

    # ---------- 동작 ----------
    def update_start_button_state(self):
        """시험 시작 버튼 상태 업데이트 (항상 활성화, 클릭 시 검증)"""
        try:
            # start_btn이 아직 생성되지 않았으면 건너뛰기
            if not hasattr(self, 'start_btn'):
                return

            # 항상 활성화 - 클릭 시 _check_required_fields()에서 검증
            self.start_btn.setEnabled(True)

        except Exception as e:
            print(f"버튼 상태 업데이트 실패: {e}")

    def start_scan(self):
        """실제 네트워크 스캔으로 사용 가능한 주소 탐지"""
        try:
            # target_system에 따라 분기 처리
            if hasattr(self, 'target_system') and self.target_system == "통합플랫폼시스템":
                # 통합플랫폼시스템: 네트워크 IP 검색
                if hasattr(self, 'test_port') and self.test_port:
                    ip_list = self._get_local_ip_list()

                    if not ip_list:
                        # IP 검색 실패 시 경고 및 직접 입력 안내
                        QMessageBox.warning(
                            self, "네트워크 IP 검색 실패",
                            "네트워크 IP 주소를 검색할 수 없습니다.\n\n"
                            "아래 '직접 입력' 기능을 사용하여 IP 주소를 수동으로 입력해주세요.\n"
                            "예: 192.168.1.1"
                        )
                        return

                    # ip:port 목록 생성
                    urls = [f"{ip}:{self.test_port}" for ip in dict.fromkeys(ip_list)]  # 중복 제거 유지 순서

                    print(f"통합플랫폼시스템 - API testPort 사용 (후보): {urls}")
                    self._populate_url_table(urls)
                    QMessageBox.information(
                        self, "주소 설정 완료",
                        "통합플랫폼시스템: 네트워크 IP로 주소 후보를 설정했습니다.\n"
                        f"후보: {', '.join(urls)}"
                    )
                else:
                    QMessageBox.warning(self, "경고", "testPort 정보가 없습니다.")
                return

            elif hasattr(self, 'target_system') and self.target_system == "물리보안시스템":
                # 물리보안시스템: ARP 스캔으로 동일 네트워크 IP 검색
                # 이미 스캔 중이면 중복 실행 방지
                if hasattr(self, 'arp_scan_thread') and self.arp_scan_thread and self.arp_scan_thread.isRunning():
                    QMessageBox.information(self, "알림", "이미 주소 탐색이 진행 중입니다.")
                    return

                # ARP Worker와 Thread 설정
                from PyQt5.QtCore import QThread

                self.arp_scan_worker = ARPScanWorker(test_port=self.test_port if hasattr(self, 'test_port') else None)
                self.arp_scan_thread = QThread()

                # Worker를 Thread로 이동
                self.arp_scan_worker.moveToThread(self.arp_scan_thread)

                # 시그널 연결
                self.arp_scan_worker.scan_completed.connect(self._on_arp_scan_completed)
                self.arp_scan_worker.scan_failed.connect(self._on_arp_scan_failed)
                self.arp_scan_thread.started.connect(self.arp_scan_worker.scan_arp)
                self.arp_scan_thread.finished.connect(self.arp_scan_thread.deleteLater)

                # 스레드 시작
                self.arp_scan_thread.start()
                QMessageBox.information(self, "ARP 스캔 시작", "동일 네트워크의 장비를 검색합니다.\n잠시만 기다려주세요...")
                return

            # 기타 시스템 또는 testPort가 없는 경우: 기존 네트워크 스캔 수행
            # 이미 스캔 중이면 중복 실행 방지
            if self.scan_thread and self.scan_thread.isRunning():
                QMessageBox.information(self, "알림", "이미 주소 탐색이 진행 중입니다.")
                return

            # Worker와 Thread 설정
            from PyQt5.QtCore import QThread

            self.scan_worker = NetworkScanWorker()
            self.scan_thread = QThread()

            # Worker를 Thread로 이동
            self.scan_worker.moveToThread(self.scan_thread)

            # 시그널 연결
            self.scan_worker.scan_completed.connect(self._on_scan_completed)
            self.scan_worker.scan_failed.connect(self._on_scan_failed)
            self.scan_thread.started.connect(self.scan_worker.scan_network)
            self.scan_thread.finished.connect(self.scan_thread.deleteLater)

            # 스레드 시작
            self.scan_thread.start()

        except Exception as e:
            print(f"주소 탐색 오류: {e}")
            QMessageBox.critical(self, "오류", f"네트워크 탐색 중 오류 발생:\n{str(e)}")

    def _on_scan_completed(self, urls):
        self._populate_url_table(urls)
        QMessageBox.information(self, "탐색 완료", "사용 가능한 주소를 찾았습니다.")

    def _on_scan_failed(self, msg):
        QMessageBox.warning(self, "주소 탐색 실패", msg)

    def _on_arp_scan_completed(self, urls):
        """ARP 스캔 완료 시 호출"""
        self._populate_url_table(urls)
        QMessageBox.information(
            self, "ARP 스캔 완료",
            f"동일 네트워크에서 {len(urls)}개의 장비를 찾았습니다.\n"
            f"발견된 주소: {', '.join(urls)}"
        )

    def _on_arp_scan_failed(self, msg):
        """ARP 스캔 실패 시 호출"""
        QMessageBox.warning(self, "ARP 스캔 실패", msg)

    def _populate_url_table(self, urls):
        """URL 테이블에 스캔 결과 채우기 (2컬럼: 행번호 + URL)"""
        try:
            self.url_table.setRowCount(0)
            self.selected_url_row = None

            # 이미지 경로 (체크박스 분리 - 반응형)
            bg_image = "assets/image/test_config/row.png"
            bg_selected_image = "assets/image/test_config/row_selected.png"
            checkbox_unchecked = "assets/image/test_config/checkbox_unchecked.png"
            checkbox_checked = "assets/image/test_config/checkbox_checked.png"

            for i, url in enumerate(urls):
                row = self.url_table.rowCount()
                self.url_table.insertRow(row)

                # 컬럼 0: 행 번호 (ClickableLabel - 배경색으로 선택 표시)
                row_num_label = ClickableLabel(str(row + 1), row, 0)
                row_num_label.setAlignment(Qt.AlignCenter)
                row_num_label.setStyleSheet("""
                    QLabel {
                        background-color: #FFFFFF;
                        border: none;
                        border-bottom: 1px solid #CCCCCC;
                        font-family: 'Noto Sans KR';
                        font-size: 19px;
                        font-weight: 400;
                        color: #000000;
                    }
                """)
                row_num_label.clicked.connect(self.on_url_row_selected)
                self.url_table.setCellWidget(row, 0, row_num_label)

                # 컬럼 1: URL (ClickableCheckboxRowWidget - 체크박스 분리, paintEvent 배경)
                url_widget = ClickableCheckboxRowWidget(
                    url, row, 1,
                    bg_image, bg_selected_image,
                    checkbox_unchecked, checkbox_checked
                )
                url_widget.setProperty("url", url)
                url_widget.clicked.connect(self.on_url_row_selected)
                self.url_table.setCellWidget(row, 1, url_widget)

                self.url_table.setRowHeight(row, 39)

            # 셀 생성 후 현재 창 크기에 맞게 반응형 적용
            self.resizeEvent(QResizeEvent(self.size(), self.size()))

        except Exception as e:
            self._show_scan_error(f"테이블 업데이트 중 오류:\n{str(e)}")

    def _show_scan_error(self, message):
        """스캔 오류 메시지 표시"""
        QMessageBox.warning(self, "주소 탐색 실패", message)

    def get_selected_url(self):
        """URL 테이블에서 선택된 URL 반환 (2컬럼 방식 - 컬럼 1에서 URL 가져오기)"""
        # 선택된 행 번호 확인
        if self.selected_url_row is not None:
            widget = self.url_table.cellWidget(self.selected_url_row, 1)  # 컬럼 1: URL
            if widget:
                selected_url = widget.property("url")
                if selected_url:
                    # http://가 없으면 추가
                    if not selected_url.startswith(('http://', 'https://')):
                        selected_url = f"https://{selected_url}"
                    return selected_url
        return None

    def _check_required_fields(self):
        """필수 입력 필드 검증 - 누락된 항목 리스트 반환"""
        missing_fields = []

        # 1. 인증 정보 확인 (공통 필드)
        if not self.id_input.text().strip():
            missing_fields.append("• 인증 ID")
        if not self.pw_input.text().strip():
            missing_fields.append("• 인증 PW")

        # 2. 접속 정보 확인
        if not self.get_selected_url():
            missing_fields.append("• 접속 URL 선택")

        return missing_fields

    def start_test(self):
        """시험 시작 - CONSTANTS.py 업데이트 후 검증 소프트웨어 실행"""
        # ===== 수정: PyInstaller 환경에서 CONSTANTS reload =====
        import sys
        import os
        if getattr(sys, 'frozen', False):
            # PyInstaller 환경 - sys.modules 삭제 후 재import
            if 'config.CONSTANTS' in sys.modules:
                del sys.modules['config.CONSTANTS']
            import config.CONSTANTS
            # 모듈 레벨 전역 변수 업데이트는 필요 없음 (여기서는 사용 안 함)
        else:
            # 로컬 환경에서는 기존 reload 사용
            if 'config.CONSTANTS' in sys.modules:
                importlib.reload(sys.modules['config.CONSTANTS'])  # sys.modules에서 모듈 객체를 가져와 reload
            else:
                import config.CONSTANTS  # 모듈이 없으면 새로 import
        # ===== 수정 끝 =====
        try:
            # 필수 입력 필드 검증
            missing_fields = self._check_required_fields()
            if missing_fields:
                message = "다음 정보를 입력해주세요:\n\n" + "\n".join(missing_fields)
                QMessageBox.warning(self, "입력 정보 부족", message)
                return

            # spec_id 추출 (testSpecs의 첫 번째 항목)
            if not self.test_specs or len(self.test_specs) == 0:
                QMessageBox.warning(self, "오류", "시험 시나리오 정보가 없습니다.")
                return

            # test_specs[0]이 딕셔너리인지 확인
            first_spec = self.test_specs[0]
            if isinstance(first_spec, dict):
                spec_id = first_spec.get("id", "")
            else:
                QMessageBox.warning(self, "오류", f"시험 시나리오 데이터 형식이 올바르지 않습니다: {type(first_spec)}")
                return

            # 물리보안(시스템 검증)일 경우: UI에서 수정한 ID/PW로 Data_request.py 업데이트
            if not hasattr(self, 'target_system') or self.target_system != "통합플랫폼시스템":
                user_id = self.id_input.text().strip()
                password = self.pw_input.text().strip()
                if user_id and password:
                    print(f"[INFO] 물리보안 시험 시작 - Data_request.py 업데이트 (userID={user_id})")
                    update_success = self.form_validator.update_data_request_authentication(spec_id, user_id, password)
                    if not update_success:
                        print("[WARNING] Data_request.py 업데이트 실패, 기존 값으로 진행합니다.")

            # CONSTANTS.py 업데이트
            if self.form_validator.update_constants_py():
                # Heartbeat (busy) 전송 - 시험 시작 시
                test_info = {
                    "testRequestId": getattr(self, 'request_id', ''),
                    "companyName": self.company_edit.text().strip(),
                    "contactPerson": getattr(self, 'contact_person', ''),
                    "productName": self.product_edit.text().strip(),
                    "modelName": self.model_edit.text().strip(),
                    "version": self.version_edit.text().strip(),
                    "testGroups": [
                        {
                            "id": g.get("id", ""),
                            "name": g.get("name", ""),
                            "testRange": g.get("testRange", "")
                        } for g in getattr(self, 'test_groups', [])
                    ]
                }
                self.form_validator.send_heartbeat_busy(test_info)

                # test_group_name, verification_type(current_mode), spec_id를 함께 전달
                print(f"시험 시작: testTarget.name={self.target_system}, verificationType={self.current_mode}, spec_id={spec_id}")
                self.startTestRequested.emit(self.target_system, self.current_mode, spec_id)
            else:
                QMessageBox.warning(self, "저장 실패", "CONSTANTS.py 업데이트에 실패했습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"시험 시작 중 오류가 발생했습니다:\n{str(e)}")    

    def check_start_button_state(self):
        """시험 시작 버튼 활성화 조건 체크 (항상 활성화, 클릭 시 검증)"""
        try:
            # 항상 활성화 - 클릭 시 _check_required_fields()에서 검증
            self.start_btn.setEnabled(True)

        except Exception as e:
            print(f"버튼 상태 체크 실패: {e}")
            self.start_btn.setEnabled(True)  # 오류 발생 시에도 활성화 유지

    def exit_btn_clicked(self):
        """종료 버튼 클릭 시 프로그램 종료"""
        reply = QMessageBox.question(self, '프로그램 종료',
                                     '정말로 프로그램을 종료하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()

    def _determine_mode_from_api(self, test_data):
        """
        test-steps API 캐시에서 verificationType 추출하여 모드 결정

        Returns:
            str: "request" 또는 "response"
        """
        try:
            # testGroups에서 첫 번째 그룹의 testSpecs 가져오기
            test_groups = test_data.get("testRequest", {}).get("testGroups", [])
            if not test_groups:
                print("경고: testGroups 데이터가 없습니다. 기본값 'request' 사용")
                return "request"  # 기본값

            test_specs = test_groups[0].get("testSpecs", [])
            if not test_specs:
                print("경고: testSpecs 데이터가 없습니다. 기본값 'request' 사용")
                return "request"  # 기본값

            first_spec_id = test_specs[0].get("id")
            if not first_spec_id:
                print("경고: 첫 번째 spec_id를 찾을 수 없습니다. 기본값 'request' 사용")
                return "request"

            # form_validator의 캐시에서 steps 가져오기
            steps = self.form_validator._steps_cache.get(first_spec_id, [])
            if not steps:
                print(f"경고: spec_id={first_spec_id}에 대한 steps 캐시가 없습니다. 기본값 'request' 사용")
                return "request"

            first_step_id = steps[0].get("id")
            if not first_step_id:
                print("경고: 첫 번째 step_id를 찾을 수 없습니다. 기본값 'request' 사용")
                return "request"

            # test-step detail 캐시에서 verificationType 가져오기
            step_detail = self.form_validator._test_step_cache.get(first_step_id)
            if not step_detail:
                print(f"경고: step_id={first_step_id}에 대한 캐시가 없습니다. 기본값 'request' 사용")
                return "request"

            verification_type = step_detail.get("verificationType", "request")

            print(f"verificationType 추출 완료: {verification_type}")
            return verification_type

        except Exception as e:
            print(f"verificationType 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return "request"  # 기본값

    def on_load_test_info_clicked(self):
        """시험정보 불러오기 버튼 클릭 이벤트 (API 기반)"""
        # IP 입력창에서 IP 주소 가져오기
        ip_address = self.ip_input_edit.text().strip()

        if not ip_address:
            QMessageBox.warning(self, "경고", "주소를 입력해주세요.")
            return

        # IP 주소 형식 검증
        if not self._validate_ip_address(ip_address):
            QMessageBox.warning(self, "경고",
                "올바른 IP 주소 형식이 아닙니다.\n"
                "예: 192.168.1.1")
            return

        print(f"입력된 IP 주소: {ip_address}")

        # 로딩 팝업 생성 및 표시 (스피너 애니메이션 포함)
        loading_popup = LoadingPopup(width=400, height=200)
        loading_popup.update_message("시험 정보 불러오는 중...", "잠시만 기다려주세요")
        loading_popup.show()

        # UI 즉시 업데이트를 위한 이벤트 루프 처리
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

        try:

            # API 호출하여 시험 정보 가져오기
            test_data = self.form_validator.fetch_test_info_by_ip(ip_address)

            if not test_data:
                QMessageBox.warning(self, "경고",
                    "시험 정보를 불러올 수 없습니다.\n"
                    "- 서버 연결을 확인해주세요.\n"
                    "- IP 주소에 해당하는 시험 요청이 있는지 확인해주세요.")
                return

            # 1페이지 필드 채우기
            eval_target = test_data.get("testRequest", {}).get("evaluationTarget", {})
            test_groups = test_data.get("testRequest", {}).get("testGroups", [])


            test_groups = test_data.get("testRequest", {}).get("testGroups", [])


            # testGroups 배열 처리
            if not test_groups:
                QMessageBox.warning(self, "경고", "testGroups 데이터가 비어있습니다.")
                return

            # 여러 그룹의 이름을 콤마로 연결
            group_names = [g.get("name", "") for g in test_groups]
            combined_group_names = ", ".join(group_names)

            # 여러 그룹의 testRange를 콤마로 연결
            group_ranges = [g.get("testRange", "") for g in test_groups]
            combined_group_ranges = ", ".join(group_ranges)

            # 원본 시험범위 값 저장
            self.original_test_range = combined_group_ranges

            self.company_edit.setText(eval_target.get("companyName", ""))
            self.product_edit.setText(eval_target.get("productName", ""))
            self.version_edit.setText(eval_target.get("version", ""))
            self.model_edit.setText(eval_target.get("modelName", ""))
            self.test_category_edit.setText(eval_target.get("testCategory", ""))

            self.target_system = eval_target.get("targetSystem", "")
            if self.target_system == "PHYSICAL_SECURITY":
                self.target_system = "물리보안시스템"
            elif self.target_system == "INTEGRATED_SYSTEM":
                self.target_system = "통합플랫폼시스템"
            self.target_system_edit.setText(self.target_system)

            self.test_group_edit.setText(combined_group_names)  # 콤마로 연결된 그룹 이름들

            # 시험범위를 UI용 텍스트로 변환하여 표시
            display_test_range = combined_group_ranges
            if combined_group_ranges == "ALL_FIELDS":
                display_test_range = "전체필드"
            elif combined_group_ranges:
                display_test_range = "필수필드"
            self.test_range_edit.setText(display_test_range)

            self.contact_person = eval_target.get("contactPerson", "")
            self.model_name = eval_target.get("modelName", "")
            self.request_id = test_data.get("testRequest", {}).get("id", {})

            # 모든 testGroups 저장 (시험 시작 시 사용)
            self.test_groups = test_groups  # 전체 그룹 배열 저장
            self.test_group_id = test_groups[0].get("id", "") if test_groups else ""  # 첫 번째 그룹 ID
            self.test_group_name = test_groups[0].get("name", "") if test_groups else ""  # 첫 번째 그룹 이름
            print(f"testGroups 저장: {len(test_groups)}개 그룹, 첫 번째 id={self.test_group_id}, name={self.test_group_name}")

            # 모든 그룹의 testSpecs를 합침 (2페이지에서 사용)
            all_test_specs = []
            for group in test_groups:
                all_test_specs.extend(group.get("testSpecs", []))

            self.test_specs = all_test_specs
            self.test_port = test_data.get("schedule", {}).get("testPort", None)

            # testPort 기반 WEBHOOK_PORT 업데이트
            if self.test_port:
                # 1. 메모리상의 값 업데이트
                CONSTANTS.WEBHOOK_PORT = self.test_port + 1
                CONSTANTS.WEBHOOK_URL = f"https://{CONSTANTS.url}:{CONSTANTS.WEBHOOK_PORT}"

                # 2. CONSTANTS.py 파일 자체도 수정
                try:
                    import re
                    import sys
                    import os
                    from core.functions import resource_path

                    # CONSTANTS.py 파일 경로 설정
                    if getattr(sys, 'frozen', False):
                        exe_dir = os.path.dirname(sys.executable)
                        constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
                    else:
                        constants_path = resource_path("config/CONSTANTS.py")

                    # 파일 읽기
                    with open(constants_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # WEBHOOK_PORT = 숫자 패턴 찾아서 치환
                    pattern_port = r'^WEBHOOK_PORT\s*=\s*\d+.*$'
                    new_port_line = f'WEBHOOK_PORT = {self.test_port + 1}       # 웹훅 수신 포트'
                    content = re.sub(pattern_port, new_port_line, content, flags=re.MULTILINE)

                    # 파일 저장
                    with open(constants_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    print(f"WEBHOOK_PORT 업데이트 완료: {CONSTANTS.WEBHOOK_PORT} (testPort: {self.test_port})")
                    print(f"  - 메모리: {CONSTANTS.WEBHOOK_PORT}")
                    print(f"  - 파일: CONSTANTS.py 수정 완료")

                except Exception as e:
                    print(f"CONSTANTS.py 파일 수정 실패: {e}")
                    # 파일 수정 실패해도 메모리상의 값은 이미 업데이트되었으므로 계속 진행

            # verificationType 기반 모드 설정 (API 기반)
            self.current_mode = self._determine_mode_from_api(test_data)

            # API 데이터를 이용하여 OPT 파일 로드 및 스키마 생성
            self.form_validator.load_opt_files_from_api(test_data)

            # 플랫폼 검증일 경우 Authentication 정보 자동 입력
            self.auto_fill_authentication_for_platform()

            # 다음 버튼 상태 업데이트
            self.check_next_button_state()

            # Heartbeat (idle) 전송 - 시험 정보 불러오기 성공 시
            self.form_validator.send_heartbeat_idle()

        except Exception as e:
            print(f"시험정보 불러오기 실패: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"시험 정보를 불러오는 중 오류가 발생했습니다:\n{str(e)}")

        finally:
            # 로딩 팝업 닫기 (성공/실패 여부와 관계없이 항상 실행)
            loading_popup.close()

    def auto_fill_authentication_for_platform(self):
        """
        플랫폼 검증/시스템 검증에 따라 Authentication 정보를 자동으로 채움
        - 통합플랫폼: Validation_request.py에서 읽어와서 disabled
        - 물리보안(시스템 검증): Data_request.py에서 읽어와서 enabled (수정 가능)
        """
        try:
            # test_specs에서 첫 번째 spec_id 가져오기
            if not hasattr(self, 'test_specs') or not self.test_specs:
                print("[WARNING] test_specs가 없어서 Authentication 자동 입력을 건너뜁니다.")
                return

            first_spec = self.test_specs[0]
            spec_id = first_spec.get("id", "")

            if not spec_id:
                print("[WARNING] spec_id를 찾을 수 없어서 Authentication 자동 입력을 건너뜁니다.")
                return

            # 플랫폼 검증인지 확인
            if not hasattr(self, 'target_system') or self.target_system != "통합플랫폼시스템":
                # 물리보안(시스템 검증): Data_request.py에서 읽어옴
                print("[INFO] 시스템 검증(물리보안) 감지 - Data_request.py에서 Authentication 정보를 읽어옵니다.")
                print(f"[INFO] spec_id={spec_id}로 Data_request.py에서 Authentication 정보를 추출합니다.")

                user_id, password = self.form_validator.get_authentication_from_data_request(spec_id)

                if user_id and password:
                    # 필드에 값 설정
                    self.id_input.setText(user_id)
                    self.pw_input.setText(password)

                    # 필드를 enabled 상태로 설정 (수정 가능)
                    self.id_input.setEnabled(True)
                    self.pw_input.setEnabled(True)

                    print(f"[SUCCESS] 시스템 검증: Authentication 자동 입력 완료 (User ID={user_id})")
                    print(f"[INFO] id_input과 pw_input 필드가 enabled 상태로 설정되었습니다. (수정 가능)")
                else:
                    print("[WARNING] Data_request.py에서 Authentication 정보를 찾을 수 없습니다. 필드를 비워둡니다.")
                    self.id_input.setEnabled(True)
                    self.pw_input.setEnabled(True)
                    self.id_input.clear()
                    self.pw_input.clear()
                return

            # 통합플랫폼: Validation_request.py에서 읽어옴
            print("[INFO] 플랫폼 검증 감지 - Validation_request.py에서 Authentication 자동 입력을 시도합니다.")
            print(f"[INFO] spec_id={spec_id}로 Authentication 정보를 추출합니다.")

            # FormValidator의 get_authentication_credentials 메서드 호출
            user_id, password = self.form_validator.get_authentication_credentials(spec_id)

            if user_id and password:
                # 필드에 값 설정
                self.id_input.setText(user_id)
                self.pw_input.setText(password)

                # 필드를 disabled 상태로 설정
                self.id_input.setEnabled(False)
                self.pw_input.setEnabled(False)

                print(f"[SUCCESS] 플랫폼 검증: Authentication 자동 입력 완료 (User ID={user_id})")
                print(f"[INFO] id_input과 pw_input 필드가 disabled 상태로 설정되었습니다.")
            else:
                print("[WARNING] Authentication 정보를 찾을 수 없습니다. 필드를 비워둡니다.")
                # Authentication 정보가 없으면 필드를 활성화하고 비움
                self.id_input.setEnabled(True)
                self.pw_input.setEnabled(True)
                self.id_input.clear()
                self.pw_input.clear()

        except Exception as e:
            print(f"[ERROR] Authentication 자동 입력 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            # 오류 발생 시 필드를 활성화
            self.id_input.setEnabled(True)
            self.pw_input.setEnabled(True)

    def on_management_url_changed(self):
        """관리자시스템 주소 변경 시 처리"""
        try:
            new_url = self.management_url_edit.text().strip()
            if new_url:
                # CONSTANTS에 저장 (메모리 + config.txt 파일)
                success = CONSTANTS.save_management_url(new_url)
                if success:
                    print(f"관리자시스템 주소가 업데이트되었습니다: {new_url}")
                else:
                    print("관리자시스템 주소 저장에 실패했습니다.")
        except Exception as e:
            print(f"관리자시스템 주소 변경 처리 실패: {e}")

    def _validate_ip_address(self, ip):
        """IP 주소 형식 검증"""
        # IP 주소 정규식 패턴
        ip_pattern = re.compile(
            r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        return bool(ip_pattern.match(ip))

    def get_local_ip(self):
        """로컬 네트워크 IP 주소 가져오기"""
        import socket

        ip_list = []

        try:
            # socket을 사용하여 로컬 IP 확인
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip and not local_ip.startswith('127.'):
                ip_list.append(local_ip)
        except Exception as e:
            print(f"socket을 사용한 IP 검색 실패: {e}")

        # 위 방법 실패 시 호스트명으로 IP 가져오기
        if not ip_list:
            try:
                hostname_ip = socket.gethostbyname(socket.gethostname())
                if hostname_ip and not hostname_ip.startswith('127.'):
                    ip_list.append(hostname_ip)
            except Exception as e2:
                print(f"hostname을 사용한 IP 검색 실패: {e2}")

        # 중복 제거
        ip_list = list(dict.fromkeys(ip_list))

        print(f"검색된 네트워크 IP 목록: {ip_list}")

        # 리스트를 쉼표로 구분된 문자열로 반환
        if ip_list:
            return ", ".join(ip_list)
        else:
            return None

    def _get_local_ip_list(self):
        """get_local_ip() 결과를 안전하게 리스트로 변환 (최대 3개)"""
        raw = self.get_local_ip()
        ip_list = []

        if isinstance(raw, str):
            ip_list = [ip.strip() for ip in raw.split(',') if ip.strip()]
        elif isinstance(raw, (list, tuple, set)):
            ip_list = [str(ip).strip() for ip in raw if str(ip).strip()]

        # 최대 3개만 반환
        return ip_list[:3]

    def check_next_button_state(self):
        """첫 번째 페이지의 다음 버튼 활성화 조건 체크"""
        try:
            if hasattr(self, 'next_btn'):
                # 다음 버튼은 항상 활성화 (클릭 시 검증)
                self.next_btn.setEnabled(True)
        except Exception as e:
            print(f"다음 버튼 상태 체크 실패: {e}")

    def _is_page1_complete(self):
        """첫 번째 페이지 완료 조건 검사"""
        try:
            # 1. 모드 선택 확인 (불러오기 버튼 중 하나를 눌렀는지)
            if not self.current_mode:
                return False

            # 2. 시험 기본 정보 모든 필드 입력 확인
            basic_info_filled = all([
                self.company_edit.text().strip(),
                self.product_edit.text().strip(),
                self.version_edit.text().strip(),
                self.model_edit.text().strip(),
                self.test_category_edit.text().strip(),
                self.target_system_edit.text().strip(),
                self.test_group_edit.text().strip(),
                self.test_range_edit.text().strip()
            ])

            # 3. 관리자 코드 유효성 확인
            admin_code_valid = self.form_validator.is_admin_code_valid()

            # 4. 시험 시나리오명 테이블에 데이터가 있는지 확인
            test_field_filled = self.test_field_table.rowCount() > 0

            # 모든 조건이 충족되면 완료
            return basic_info_filled and admin_code_valid and test_field_filled

        except Exception as e:
            print(f"페이지 완료 조건 체크 실패: {e}")
            return False

    def on_test_field_selected(self, row, col):
        """시험 분야 테이블 클릭 시 시나리오 테이블 업데이트"""
        try:
            # 클릭된 행 번호 저장
            self.selected_test_field_row = row

            # 선택된 그룹명 가져오기 (위젯에서 가져오기)
            selected_widget = self.test_field_table.cellWidget(row, 0)
            if selected_widget:
                group_name = selected_widget.text()
                # 해당 그룹의 시나리오들을 시나리오 테이블에 채우기
                self.form_validator._fill_scenarios_for_group(row, group_name)

            # 테이블 강제 업데이트
            self.test_field_table.viewport().update()
            self.scenario_table.viewport().update()

            # API 테이블 초기 메시지로 리셋
            self.form_validator._show_initial_api_message()

        except Exception as e:
            print(f"시험 분야 선택 처리 실패: {e}")
            QMessageBox.warning(self, "오류", f"시험 분야 데이터 로드 중 오류가 발생했습니다:\n{str(e)}")

    def on_scenario_selected(self, row, col):
        """시나리오 테이블 클릭 시 체크박스 상태 변경 및 API 테이블 업데이트"""
        try:
            # 모든 시나리오 행의 체크박스 상태 업데이트
            for i in range(self.scenario_table.rowCount()):
                widget = self.scenario_table.cellWidget(i, 0)
                if widget and hasattr(widget, 'setChecked'):
                    # 클릭된 행은 체크, 나머지는 체크 해제
                    widget.setChecked(i == row)

            # UI 업데이트 강제 (체크박스 이미지가 먼저 보이도록)
            QApplication.processEvents()

            # specifications API 호출하여 API 테이블 채우기
            self.form_validator._fill_api_table_for_selected_field_from_api(row)

        except Exception as e:
            print(f"시나리오 선택 처리 실패: {e}")
            QMessageBox.warning(self, "오류", f"시나리오 데이터 로드 중 오류가 발생했습니다:\n{str(e)}")

    def toggle_address_popover(self):
        """주소 추가 팝오버 표시/숨김 토글"""
        if self.address_popover.isVisible():
            self.address_popover.hide()
            self.add_btn.setChecked(False)
        else:
            # 추가 버튼의 전역 좌표를 가져옴
            btn_global_pos = self.add_btn.mapToGlobal(self.add_btn.rect().bottomLeft())
            # InfoWidget의 전역 좌표를 가져와서 상대 좌표로 변환
            widget_global_pos = self.mapToGlobal(self.rect().topLeft())
            relative_x = btn_global_pos.x() - widget_global_pos.x()
            relative_y = btn_global_pos.y() - widget_global_pos.y()

            # 팝오버를 오른쪽 정렬 (추가 버튼 오른쪽 끝 기준)
            popover_x = relative_x + self.add_btn.width() - self.address_popover.width()
            popover_y = relative_y + 4  # 버튼 아래 4px gap

            # 팝오버 위치 설정
            self.address_popover.move(popover_x, popover_y)
            self.address_popover.raise_()  # 최상위로 올림
            self.address_popover.show()
            self.add_btn.setChecked(True)
            self.address_input.setFocus()  # 입력창에 포커스

    def add_address_from_popover(self):
        """팝오버에서 IP 주소 추가 (2컬럼: 행번호 + URL)"""
        try:
            # 입력값 가져오기
            ip_port = self.address_input.text().strip()

            if not ip_port:
                QMessageBox.warning(self, "입력 오류", "IP 주소를 입력해주세요.\n예: 192.168.1.1")
                return

            # Port 포함 여부 확인 - Port는 입력하지 않아야 함
            if ':' in ip_port:
                QMessageBox.warning(self, "입력 오류", "IP 주소만 입력해주세요.\nPort는 시험정보의 testPort로 자동 설정됩니다.\n예: 192.168.1.1")
                return

            # IP 검증
            if not self._validate_ip_address(ip_port):
                QMessageBox.warning(self, "IP 오류", "올바른 IP 주소를 입력해주세요.\n예: 192.168.1.100")
                return

            # testPort 확인 및 자동 추가
            if not hasattr(self, 'test_port') or not self.test_port:
                QMessageBox.warning(self, "testPort 없음", "시험정보를 먼저 불러와주세요.\ntestPort 정보가 필요합니다.")
                return

            # IP와 testPort 결합
            final_url = f"{ip_port}:{self.test_port}"

            # 중복 확인 (컬럼 1의 ClickableLabel에서 url property 가져오기)
            for row in range(self.url_table.rowCount()):
                widget = self.url_table.cellWidget(row, 1)
                if widget and widget.property("url") == final_url:
                    QMessageBox.information(self, "알림", "이미 추가된 주소입니다.")
                    return

            # 이미지 경로 (체크박스 분리 - 반응형)
            bg_image = "assets/image/test_config/row.png"
            bg_selected_image = "assets/image/test_config/row_selected.png"
            checkbox_unchecked = "assets/image/test_config/checkbox_unchecked.png"
            checkbox_checked = "assets/image/test_config/checkbox_checked.png"

            # 테이블에 추가
            row = self.url_table.rowCount()
            self.url_table.insertRow(row)

            # 컬럼 0: 행 번호 (ClickableLabel - 배경색으로 선택 표시)
            row_num_label = ClickableLabel(str(row + 1), row, 0)
            row_num_label.setAlignment(Qt.AlignCenter)
            row_num_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: none;
                    border-bottom: 1px solid #CCCCCC;
                    font-family: 'Noto Sans KR';
                    font-size: 19px;
                    font-weight: 400;
                    color: #000000;
                }
            """)
            row_num_label.clicked.connect(self.on_url_row_selected)
            self.url_table.setCellWidget(row, 0, row_num_label)

            # 컬럼 1: URL (ClickableCheckboxRowWidget - 체크박스 분리, paintEvent 배경)
            url_widget = ClickableCheckboxRowWidget(
                final_url, row, 1,
                bg_image, bg_selected_image,
                checkbox_unchecked, checkbox_checked
            )
            url_widget.setProperty("url", final_url)
            url_widget.clicked.connect(self.on_url_row_selected)
            self.url_table.setCellWidget(row, 1, url_widget)

            self.url_table.setRowHeight(row, 39)

            # 셀 생성 후 현재 창 크기에 맞게 반응형 적용
            self.resizeEvent(QResizeEvent(self.size(), self.size()))

            # 입력창 초기화
            self.address_input.clear()

            # 팝오버 닫기
            self.address_popover.hide()
            self.add_btn.setChecked(False)

            QMessageBox.information(self, "추가 완료", f"주소가 추가되었습니다.\n{final_url}")

        except Exception as e:
            print(f"IP 추가 오류: {e}")
            QMessageBox.critical(self, "오류", f"주소 추가 중 오류가 발생했습니다:\n{str(e)}")

    def on_url_row_selected(self, row, col):
        """URL 테이블 행 클릭 시 두 컬럼 모두 스타일 변경 (2컬럼 방식 - ClickableCheckboxRowWidget 사용)"""
        try:
            # 모든 URL 행의 스타일 업데이트
            for i in range(self.url_table.rowCount()):
                row_num_widget = self.url_table.cellWidget(i, 0)  # 행 번호 컬럼
                url_widget = self.url_table.cellWidget(i, 1)  # URL 컬럼 (ClickableCheckboxRowWidget)

                if i == row:
                    # 클릭된 행: 선택 스타일 적용
                    if row_num_widget:
                        row_num_widget.setStyleSheet("""
                            QLabel {
                                background-color: #E3F2FF;
                                border: none;
                                border-bottom: 1px solid #CCCCCC;
                                font-family: 'Noto Sans KR';
                                font-size: 19px;
                                font-weight: 400;
                                color: #000000;
                            }
                        """)
                    if url_widget and hasattr(url_widget, 'setChecked'):
                        url_widget.setChecked(True)
                else:
                    # 나머지 행: 기본 스타일 적용
                    if row_num_widget:
                        row_num_widget.setStyleSheet("""
                            QLabel {
                                background-color: #FFFFFF;
                                border: none;
                                border-bottom: 1px solid #CCCCCC;
                                font-family: 'Noto Sans KR';
                                font-size: 19px;
                                font-weight: 400;
                                color: #000000;
                            }
                        """)
                    if url_widget and hasattr(url_widget, 'setChecked'):
                        url_widget.setChecked(False)

            # 선택된 행 추적
            self.selected_url_row = row

            # UI 업데이트 강제
            QApplication.processEvents()

            # 시작 버튼 상태 체크
            self.check_start_button_state()

        except Exception as e:
            print(f"URL 행 선택 처리 실패: {e}")
