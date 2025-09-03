# launcher_first_toggle_back.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QRadioButton, QPushButton, QLabel, QStackedWidget, QAction
)
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt

# 두 앱 모듈 (둘 다 MyApp(QWidget) 제공) - GUI 자동실행 방지를 위해 클래스만 import
import platformVal_all as platform_app
import systemVal_all as system_app

from core.functions import resource_path


class SelectionWidget(QWidget):
    """첫 화면: 플랫폼/시스템 선택 및 적용"""

    def __init__(self, apply_callback):
        super().__init__()
        self.apply_callback = apply_callback

        layout = QVBoxLayout()
        title = QLabel("검증 소프트웨어 선택")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.radio_platform = QRadioButton("플랫폼 검증")
        self.radio_system = QRadioButton("시스템 검증")
        self.radio_platform.setChecked(True)
        layout.addWidget(self.radio_platform)
        layout.addWidget(self.radio_system)

        btn_apply = QPushButton("적용")
        btn_apply.clicked.connect(self._on_apply)
        layout.addWidget(btn_apply)

        self.setLayout(layout)

    def _on_apply(self):
        idx = 0 if self.radio_platform.isChecked() else 1
        self.apply_callback(idx)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("검증 소프트웨어 통합 실행기 (선택화면 + 돌아가기)")
        self.resize(1200, 720)

        # 중앙 스택: 0=선택화면, 1=플랫폼, 2=시스템
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 선택화면
        self.selection_widget = SelectionWidget(self.apply_selection)
        self.stack.addWidget(self.selection_widget)  # index 0

        # 실제 GUI 위젯 준비 (임베드 전용) - 필요할 때만 생성
        self.platform_widget = None
        self.system_widget = None

        # 현재 선택 상태 (0=플랫폼, 1=시스템, None=미선택)
        self.selected_index = None

        # 메뉴바
        menubar = self.menuBar()

        # 모드 메뉴: 선택 화면으로 돌아가기
        mode_menu = menubar.addMenu("모드")
        act_back = QAction("선택 화면으로 돌아가기", self)
        act_back.triggered.connect(self.back_to_selection)
        mode_menu.addAction(act_back)

        # 보기 메뉴: 선택한 소프트웨어 표시 / 전체화면
        view_menu = menubar.addMenu("보기")

        act_show_selected = QAction("선택한 소프트웨어 표시", self)
        act_show_selected.triggered.connect(self.show_selected_app)
        view_menu.addAction(act_show_selected)

        act_full = QAction("전체화면 전환", self, checkable=True)
        act_full.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(act_full)

    # === 동작 ===
    def apply_selection(self, idx: int):
        """선택화면에서 '적용' 눌렀을 때: 선택 저장 후 즉시 표시"""
        self.selected_index = idx
        self.show_selected_app()

    def show_selected_app(self):
        """현재 선택된 GUI 표시 (없으면 선택화면 유지)"""
        if self.selected_index is None:
            self.stack.setCurrentIndex(0)
            return

        # 선택된 위젯이 아직 생성되지 않았다면 생성
        if self.selected_index == 0 and self.platform_widget is None:
            self.platform_widget = platform_app.MyApp(embedded=True)  # embedded=True 전달
            self.platform_widget.setWindowFlags(Qt.Widget)  # 외부 독립창 방지
            self.stack.addWidget(self.platform_widget)  # index 1

        elif self.selected_index == 1 and self.system_widget is None:
            self.system_widget = system_app.MyApp(embedded=True)  # embedded=True 전달
            self.system_widget.setWindowFlags(Qt.Widget)  # 외부 독립창 방지
            self.stack.addWidget(self.system_widget)  # index 2

        # 해당 위젯으로 전환
        if self.selected_index == 0:
            widget_index = self.stack.indexOf(self.platform_widget)
        else:
            widget_index = self.stack.indexOf(self.system_widget)

        self.stack.setCurrentIndex(widget_index)
        self.stack.currentWidget().show()

    def back_to_selection(self):
        """메뉴에서 선택 화면으로 복귀"""
        self.selected_index = None
        self.stack.setCurrentIndex(0)

    def toggle_fullscreen(self, checked: bool):
        self.showFullScreen() if checked else self.showNormal()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 폰트 통합 적용
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())