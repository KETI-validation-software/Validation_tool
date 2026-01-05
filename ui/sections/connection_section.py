"""
접속 정보 섹션
- ConnectionSection: URL 테이블 (744x376px)
"""
from PyQt5.QtWidgets import (
    QTableWidget, QGroupBox, QVBoxLayout, QHBoxLayout,
    QHeaderView, QAbstractItemView, QWidget, QLabel
)
from PyQt5.QtCore import Qt


class ConnectionSection(QGroupBox):
    """접속 정보 섹션 (744x376px)"""

    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setFixedSize(744, 376)
        self.setStyleSheet("QGroupBox { border: none; margin-top: 0px; padding-top: 0px; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # URL 테이블 (744x376px)
        self.url_table = QTableWidget(0, 2)
        self.url_table.setFixedSize(744, 376)
        self.url_table.setHorizontalHeaderLabels(["", "URL"])
        self.url_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.url_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.url_table.setSelectionMode(QAbstractItemView.NoSelection)

        self._setup_table()
        self._setup_header_overlay()

        layout.addWidget(self.url_table)
        self.setLayout(layout)

        # 부모 위젯에 테이블 참조 설정
        if self.parent_widget:
            self.parent_widget.connection_section = self  # resizeEvent에서 참조
            self.parent_widget.original_connection_section_size = (744, 376)
            self.parent_widget.url_table = self.url_table
            self.parent_widget.original_url_table_size = (744, 376)
            self.parent_widget.original_url_row_height = 39
            self.parent_widget.selected_url_row = None
            self.parent_widget.url_header_overlay = self.url_header_overlay
            self.parent_widget.original_url_header_overlay_geometry = (0, 0, 744, 31)

    def _setup_table(self):
        """테이블 설정"""
        # 헤더 설정
        header = self.url_table.horizontalHeader()
        header.setFixedHeight(31)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.url_table.setColumnWidth(0, 50)

        # 왼쪽 행 번호 헤더 숨김
        vertical_header = self.url_table.verticalHeader()
        vertical_header.setVisible(False)

        # 세로 grid line 제거
        self.url_table.setShowGrid(False)

        # 행 높이 설정
        self.url_table.verticalHeader().setDefaultSectionSize(39)

        # 스타일 설정
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

    def _setup_header_overlay(self):
        """헤더 오버레이 위젯 설정 (스크롤바 상단 영역 덮기)"""
        self.url_header_overlay = QWidget()
        self.url_header_overlay.setParent(self.url_table)
        self.url_header_overlay.setGeometry(0, 0, 744, 31)
        self.url_header_overlay.setStyleSheet("""
            QWidget {
                background-color: #EDF0F3;
                border: 1px solid #CECECE;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        """)

        header_layout = QHBoxLayout(self.url_header_overlay)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # 첫 번째 열 (빈 열)
        self.url_header_empty_label = QLabel("")
        self.url_header_empty_label.setFixedSize(50, 31)
        self.url_header_empty_label.setAlignment(Qt.AlignCenter)
        self.url_header_empty_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(self.url_header_empty_label)

        # URL 라벨
        self.url_header_url_label = QLabel("URL")
        self.url_header_url_label.setFixedSize(694, 31)
        self.url_header_url_label.setAlignment(Qt.AlignCenter)
        self.url_header_url_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 600;
                letter-spacing: -0.18px;
            }
        """)
        header_layout.addWidget(self.url_header_url_label)

        self.url_header_overlay.show()
        self.url_header_overlay.raise_()
