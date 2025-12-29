"""
시험 API 섹션
- TestApiSection: 시험 API 테이블 그룹 (744x376px)
"""
from PyQt5.QtWidgets import (
    QTableWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPalette


class TestApiSection(QGroupBox):
    """시험 API 그룹 (744x376px)"""

    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setFixedSize(744, 376)

        # 배경 불투명 설정
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#FFFFFF"))
        self.setPalette(palette)

        # QGroupBox 스타일 설정
        self.setStyleSheet("""
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

        # 시험 API 테이블 (744x376px)
        self.api_test_table = QTableWidget(0, 2)
        self.api_test_table.setFixedSize(744, 376)
        self.api_test_table.setHorizontalHeaderLabels(["기능명", "API명"])

        self._setup_table()
        self._setup_header_overlay()
        self._setup_placeholder()

        layout.addWidget(self.api_test_table)
        self.setLayout(layout)

        # 부모 위젯에 테이블 참조 설정
        if self.parent_widget:
            self.parent_widget.api_test_table = self.api_test_table
            self.parent_widget.original_api_test_table_size = (744, 376)
            self.parent_widget.original_api_row_height = 39
            self.parent_widget.api_header_overlay = self.api_header_overlay
            self.parent_widget.api_header_row_label = self.api_header_row_label
            self.parent_widget.api_header_func_label = self.api_header_func_label
            self.parent_widget.api_header_api_label = self.api_header_api_label
            self.parent_widget.api_placeholder_label = self.api_placeholder_label
            self.parent_widget.original_api_header_overlay_geometry = (0, 0, 744, 31)
            self.parent_widget.original_api_header_func_label_size = (346, 31)
            self.parent_widget.original_api_header_api_label_size = (348, 31)
            self.parent_widget.original_api_placeholder_geometry = (50, 31, 694, 345)

    def _setup_table(self):
        """테이블 설정"""
        # 헤더 설정
        header = self.api_test_table.horizontalHeader()
        header.setFixedHeight(31)

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

        # 셀 폰트 설정 (19px)
        cell_font = QFont("Noto Sans KR")
        cell_font.setPixelSize(19)
        self.api_test_table.setFont(cell_font)

        # 편집 비활성화
        self.api_test_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 왼쪽 행 번호 헤더 설정
        vertical_header = self.api_test_table.verticalHeader()
        vertical_header.setFixedWidth(50)
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

        # 배경색 강제 설정
        self.api_test_table.setAutoFillBackground(True)
        self.api_test_table.setAttribute(Qt.WA_OpaquePaintEvent, True)

        palette = self.api_test_table.palette()
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.api_test_table.setPalette(palette)

        # Viewport 배경색 설정
        self.api_test_table.viewport().setAutoFillBackground(True)
        viewport_palette = self.api_test_table.viewport().palette()
        viewport_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        viewport_palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.api_test_table.viewport().setPalette(viewport_palette)

    def _setup_header_overlay(self):
        """헤더 오버레이 위젯 설정"""
        self.api_header_overlay = QWidget()
        self.api_header_overlay.setParent(self.api_test_table)
        self.api_header_overlay.setGeometry(0, 0, 744, 31)
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

        # 기능명 라벨
        self.api_header_func_label = QLabel("기능명")
        self.api_header_func_label.setFixedSize(346, 31)
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

        # API명 라벨
        self.api_header_api_label = QLabel("API명")
        self.api_header_api_label.setFixedSize(348, 31)
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
        self.api_header_overlay.raise_()

    def _setup_placeholder(self):
        """시험 API 안내 문구 설정"""
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
        self.api_placeholder_label.setGeometry(50, 31, 694, 345)
        self.api_placeholder_label.show()
