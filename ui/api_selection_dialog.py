from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
                             QScrollArea, QWidget, QCheckBox, QDialogButtonBox)
from PyQt5.QtCore import Qt
from core.functions import resource_path

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
