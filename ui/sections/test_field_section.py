"""
시험 분야별 시나리오 섹션
- TestFieldTableWidget: 세로 구분선이 있는 커스텀 테이블
- TestFieldSection: 시험 분야와 시나리오 테이블 그룹
"""
from PyQt5.QtWidgets import (
    QTableWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
    QHeaderView, QAbstractItemView, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QPalette


class TestFieldTableWidget(QTableWidget):
    """시험 분야별 시나리오 테이블"""

    def __init__(self, rows, columns, draw_right_border=False):
        super().__init__(rows, columns)
        self._draw_right_border = draw_right_border

    def paintEvent(self, event):
        """기본 paintEvent 실행 후 세로 구분선 추가 (데이터셀 영역만)"""
        super().paintEvent(event)

        if self._draw_right_border:
            painter = QPainter(self.viewport())
            pen = QPen(QColor("#CCCCCC"))
            pen.setWidth(1)
            painter.setPen(pen)

            # viewport 오른쪽 끝에서 1px 안쪽에 그림
            x_position = self.viewport().width() - 1
            viewport_height = self.viewport().height()

            painter.drawLine(x_position, 0, x_position, viewport_height)
            painter.end()


class TestFieldSection(QGroupBox):
    """시험 분야별 시나리오 그룹 (744x240px)"""

    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setFixedSize(744, 240)

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

        # 두 개의 독립적인 테이블을 나란히 배치
        tables_layout = QHBoxLayout()
        tables_layout.setContentsMargins(0, 0, 0, 0)
        tables_layout.setSpacing(0)

        # 시험 분야 테이블 (371px x 240px)
        self.test_field_table = TestFieldTableWidget(0, 1)
        self.test_field_table.setFixedSize(371, 240)
        self.test_field_table.setHorizontalHeaderLabels(["시험 분야"])

        # 시험 시나리오 테이블 (372px x 240px)
        self.scenario_table = TestFieldTableWidget(0, 1)
        self.scenario_table.setFixedSize(372, 240)
        self.scenario_table.setHorizontalHeaderLabels(["시험 시나리오"])

        # 시험 분야 테이블 설정
        self._setup_field_table()

        # 시험 시나리오 테이블 설정
        self._setup_scenario_table()

        # 공통 스타일 적용
        self._apply_table_styles()

        # 배경색 설정
        self._setup_table_backgrounds()

        # 시나리오 오버레이 설정
        self._setup_scenario_overlays()

        # 두 테이블 사이 세로 구분선 (전체 높이)
        self.divider_line = QFrame()
        self.divider_line.setFixedSize(1, 240)
        self.divider_line.setStyleSheet("background-color: #CCCCCC;")

        # 두 테이블을 수평 레이아웃에 추가
        tables_layout.addWidget(self.test_field_table)
        tables_layout.addWidget(self.divider_line)
        tables_layout.addWidget(self.scenario_table)

        layout.addLayout(tables_layout)
        self.setLayout(layout)

        # 부모 위젯에 테이블 참조 설정
        if self.parent_widget:
            self.parent_widget.test_field_table = self.test_field_table
            self.parent_widget.scenario_table = self.scenario_table
            self.parent_widget.divider_line = self.divider_line
            self.parent_widget.original_test_field_table_size = (371, 240)
            self.parent_widget.original_scenario_table_size = (372, 240)
            self.parent_widget.original_divider_line_height = 240
            self.parent_widget.original_test_field_row_height = 39
            self.parent_widget.original_scenario_row_height = 39
            self.parent_widget.selected_test_field_row = None
            self.parent_widget.scenario_column_background = self.scenario_column_background
            self.parent_widget.scenario_placeholder_label = self.scenario_placeholder_label
            self.parent_widget.original_scenario_column_background_geometry = (0, 0, 372, 240)
            self.parent_widget.original_scenario_placeholder_geometry = (0, 31, 372, 209)

    def _setup_field_table(self):
        """시험 분야 테이블 설정"""
        field_header = self.test_field_table.horizontalHeader()
        field_header.setFixedHeight(31)
        field_header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.test_field_table.verticalHeader().setDefaultSectionSize(39)
        self.test_field_table.verticalHeader().setVisible(False)

        self.test_field_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.test_field_table.setAlternatingRowColors(False)
        self.test_field_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        if self.parent_widget:
            self.test_field_table.cellClicked.connect(self.parent_widget.on_test_field_selected)

        self.test_field_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.test_field_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _setup_scenario_table(self):
        """시험 시나리오 테이블 설정"""
        scenario_header = self.scenario_table.horizontalHeader()
        scenario_header.setFixedHeight(31)
        scenario_header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.scenario_table.verticalHeader().setDefaultSectionSize(39)
        self.scenario_table.verticalHeader().setVisible(False)

        self.scenario_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scenario_table.setAlternatingRowColors(False)
        self.scenario_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.scenario_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        if self.parent_widget:
            self.scenario_table.cellClicked.connect(self.parent_widget.on_scenario_selected)

        self.scenario_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scenario_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _apply_table_styles(self):
        """테이블 스타일 적용"""
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
                color: #1B1B1C;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #EDF0F3;
            }
        """

        # 시험 분야 테이블 스타일
        self.test_field_table.setStyleSheet(table_style + """
            QTableWidget {
                border: none;
                border-top: 1px solid #CECECE;
                border-right: none;
                border-bottom: 1px solid #CECECE;
                border-left: 1px solid #CECECE;
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)

        # 시험 시나리오 테이블 스타일
        self.scenario_table.setStyleSheet(table_style + """
            QTableWidget {
                border: none;
                border-top: 1px solid #CECECE;
                border-right: 1px solid #CECECE;
                border-bottom: 1px solid #CECECE;
                border-left: none;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
        """)

        # 폰트 설정
        cell_font = QFont("Noto Sans KR")
        cell_font.setPixelSize(19)
        cell_font.setWeight(QFont.Normal)

        header_font = QFont("Noto Sans KR")
        header_font.setPixelSize(18)
        header_font.setWeight(QFont.DemiBold)

        self.test_field_table.setFont(cell_font)
        self.test_field_table.horizontalHeader().setFont(header_font)

        self.scenario_table.setFont(cell_font)
        self.scenario_table.horizontalHeader().setFont(header_font)

    def _setup_table_backgrounds(self):
        """테이블 배경색 설정"""
        # 시험 분야 테이블 배경
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

        # 시험 시나리오 테이블 배경
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

    def _setup_scenario_overlays(self):
        """시나리오 테이블 오버레이 설정"""
        # 시나리오 테이블 배경 (선택 시 표시)
        self.scenario_column_background = QLabel("")
        self.scenario_column_background.setParent(self.scenario_table.viewport())
        self.scenario_column_background.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
            }
        """)
        self.scenario_column_background.setGeometry(0, 0, 372, 240)
        self.scenario_column_background.lower()
        self.scenario_column_background.hide()

        # 시나리오 안내 문구
        self.scenario_placeholder_label = QLabel("시험분야를 선택하면\n시험 시나리오가 표시됩니다.")
        self.scenario_placeholder_label.setParent(self.scenario_table)
        self.scenario_placeholder_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.scenario_placeholder_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #6B6B6B;
                background-color: #FFFFFF;
                border-top: 1px solid #CCCCCC;
                border-right: 1px solid #CECECE;
                border-bottom: 1px solid #CECECE;
                border-left: none;
                border-bottom-right-radius: 4px;
                padding-top: 60px;
            }
        """)
        self.scenario_placeholder_label.setGeometry(0, 31, 372, 209)
        self.scenario_placeholder_label.hide()
