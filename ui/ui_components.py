from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QHeaderView, 
                             QAbstractItemView, QTableWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from core.utils import load_external_constants

class TestSelectionPanel(QWidget):
    # Signals to notify parent about selection changes
    groupSelected = pyqtSignal(int, int)  # row, col
    scenarioSelected = pyqtSignal(int, int) # row, col

    def __init__(self, constants, parent=None):
        super().__init__(parent)
        self.CONSTANTS = constants
        
        # 미리 초기화하여 참조 에러 방지
        self.spec_id_to_index = {}
        self.index_to_spec_id = {}
        self.group_name_to_index = {}
        self.index_to_group_name = {}
        
        # ✅ 검증 모드 접미사 (기본값: 요청 검증)
        self.mode_suffix = " (요청 검증)"
        
        self.initUI()

    def initUI(self):
        # Fixed width for the panel
        self.setFixedWidth(424)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Title "시험 선택"
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
        layout.addWidget(self.spec_panel_title)
        
        # Original size for responsive resizing in parent
        self.original_spec_panel_title_size = (424, 24)

        layout.addSpacing(8)

        # 2. Group Selection Table
        self.group_table_widget = self.create_group_selection_table()
        layout.addWidget(self.group_table_widget)

        layout.addSpacing(20)

        # 3. Scenario Selection Table
        self.field_group = self.create_test_field_group()
        layout.addWidget(self.field_group)

        self.setLayout(layout)

    def create_group_selection_table(self):
        """시험 분야명 테이블"""
        group_box = QWidget()
        group_box.setFixedSize(424, 204)
        group_box.setStyleSheet("background: transparent;")

        # Original size for responsive resizing
        self.original_group_table_widget_size = (424, 204)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.group_table = QTableWidget(0, 1)
        self.group_table.setHorizontalHeaderLabels(["시험 분야"])
        self.group_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.group_table.horizontalHeader().setFixedHeight(31)
        self.group_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.group_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.group_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.group_table.setFocusPolicy(Qt.NoFocus)
        self.group_table.verticalHeader().setVisible(False)
        self.group_table.verticalHeader().setDefaultSectionSize(39)
        self.group_table.setFixedHeight(204)

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
            QTableWidget::item:focus {
                outline: none;
                border-bottom: 1px solid #CCCCCC;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
                border: none;
                outline: none;
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

        # Load data
        SPEC_CONFIG = load_external_constants(self.CONSTANTS)
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

        # Connect signal
        self.group_table.cellClicked.connect(self._on_group_clicked)

        layout.addWidget(self.group_table)
        group_box.setLayout(layout)
        return group_box

    def create_test_field_group(self):
        """시험 시나리오 테이블"""
        group_box = QWidget()
        group_box.setFixedSize(424, 526)
        group_box.setStyleSheet("background: transparent;")
        
        # Original size
        self.original_field_group_size = (424, 526)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.test_field_table = QTableWidget(0, 1)
        self.test_field_table.setHorizontalHeaderLabels(["시험 시나리오"])
        self.test_field_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_field_table.horizontalHeader().setFixedHeight(31)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.test_field_table.setFocusPolicy(Qt.NoFocus)
        self.test_field_table.verticalHeader().setVisible(False)
        self.test_field_table.verticalHeader().setDefaultSectionSize(39)
        self.test_field_table.setFixedHeight(526)

        self.test_field_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: "Noto Sans KR";
                font-size: 19px;
                color: #1B1B1C;
                outline: none;
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
            QTableWidget::item:focus {
                outline: none;
                border-bottom: 1px solid #CCCCCC;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
                outline: none;
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

        self.test_field_table.setShowGrid(False)

        # Connect signal
        self.test_field_table.cellClicked.connect(self._on_scenario_clicked)

        layout.addWidget(self.test_field_table)
        group_box.setLayout(layout)
        return group_box

    def _on_group_clicked(self, row, col):
        self.groupSelected.emit(row, col)

    def _on_scenario_clicked(self, row, col):
        self.scenarioSelected.emit(row, col)

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
            desc_with_role = f"{desc}{self.mode_suffix}"
            item = QTableWidgetItem(desc_with_role)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.test_field_table.setItem(idx, 0, item)
            self.spec_id_to_index[spec_id] = idx
            self.index_to_spec_id[idx] = spec_id
