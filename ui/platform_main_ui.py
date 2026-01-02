from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize
from core.functions import resource_path
from ui.ui_components import TestSelectionPanel
from ui.detail_dialog import CombinedDetailDialog
from ui.gui_utils import CustomDialog
from ui.common_main_ui import CommonMainUI

class PlatformMainUI(CommonMainUI):
    """
    메인 화면의 UI 구성 및 반응형 처리를 담당하는 클래스
    """
    def __init__(self):
        super().__init__()
        
    def create_spec_selection_panel(self, parent_layout):
        """시험 선택 패널 - TestSelectionPanel 사용"""
        self.test_selection_panel = TestSelectionPanel(self.CONSTANTS)
        
        # 시그널 연결
        self.test_selection_panel.groupSelected.connect(self.on_group_selected)
        self.test_selection_panel.scenarioSelected.connect(self.on_test_field_selected)
        
        # 멤버 변수 매핑 (기존 코드와의 호환성 유지)
        self.group_table = self.test_selection_panel.group_table
        self.test_field_table = self.test_selection_panel.test_field_table
        self.group_name_to_index = self.test_selection_panel.group_name_to_index
        self.index_to_group_name = self.test_selection_panel.index_to_group_name
        self.spec_id_to_index = self.test_selection_panel.spec_id_to_index
        self.index_to_spec_id = self.test_selection_panel.index_to_spec_id

        # ✅ 반응형 처리를 위한 UI 컴포넌트 매핑
        self.spec_panel_title = self.test_selection_panel.spec_panel_title
        self.group_table_widget = self.test_selection_panel.group_table_widget
        self.field_group = self.test_selection_panel.field_group
        
        # ✅ 반응형 처리를 위한 원본 사이즈 매핑
        self.original_spec_panel_title_size = self.test_selection_panel.original_spec_panel_title_size
        self.original_group_table_widget_size = self.test_selection_panel.original_group_table_widget_size
        self.original_field_group_size = self.test_selection_panel.original_field_group_size

        parent_layout.addWidget(self.test_selection_panel)

    def start_btn_clicked(self):
        """CommonMainUI의 start_btn_clicked 시그널을 기존 sbtn_push로 연결"""
        if hasattr(self, 'sbtn_push'):
            self.sbtn_push()
