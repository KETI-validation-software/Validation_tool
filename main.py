# main.py
import sys
import urllib3
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QAction, QMessageBox
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt

from login_GUI import LoginWidget
from info_GUI import InfoWidget
from core.functions import resource_path
import platformVal_all as platform_app
import systemVal_all as system_app


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("검증 소프트웨어 통합 실행기")
        self.resize(1200, 720)
        self._orig_flags = self.windowFlags()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 시작 화면
        self.login_widget = LoginWidget()
        self.login_widget.loginSucceeded.connect(self._on_login_success)
        self.stack.addWidget(self.login_widget)  # index 0

        # 접속 후 화면
        self.info_widget = InfoWidget()
        self.stack.addWidget(self.info_widget)  # index 1
        self.info_widget.startTestRequested.connect(self._open_validation_app)

        self._setup_menu()
        self.stack.setCurrentIndex(0)

    def _setup_menu(self):
        menubar = self.menuBar()
        main_menu = menubar.addMenu("메뉴")

        self.act_login = QAction("로그인", self)
        self.act_login.triggered.connect(lambda: self.stack.setCurrentIndex(0))
        main_menu.addAction(self.act_login)

        self.act_logout = QAction("로그아웃", self)
        self.act_logout.triggered.connect(self._logout)
        self.act_logout.setEnabled(False)  # 로그인 전에는 비활성화
        main_menu.addAction(self.act_logout)

        self.act_test_info = QAction("시험 정보", self)
        self.act_test_info.triggered.connect(lambda: self.stack.setCurrentIndex(1))
        self.act_test_info.setEnabled(False)
        main_menu.addAction(self.act_test_info)

        self.act_run_platform = QAction("시험 실행", self)
        self.act_run_platform.setEnabled(False)
        self.act_run_platform.triggered.connect(self._open_validation_app)
        main_menu.addAction(self.act_run_platform)

        act_exit = QAction("종료", self)
        act_exit.triggered.connect(self.close)
        main_menu.addAction(act_exit)

        view_menu = menubar.addMenu("보기")
        act_full = QAction("전체화면 전환", self, checkable=True)
        act_full.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(act_full)

    def _toggle_fullscreen(self, checked: bool):
        """
        On: 최소화/이전크기/종료 버튼만 보이게 하고, 최대화 상태로 전환.
            (이전크기 버튼이 활성화됨)
        Off: 원래 플래그/지오메트리로 복원.
        """
        if checked:
            # 현재 상태/지오메트리 저장(복원용)
            self._saved_geom = self.saveGeometry()
            self._saved_state = self.windowState()

            # 제목표시줄 + 최소화 + 최대화(최대화 시 '이전크기'로 표기) + 종료
            flags = (Qt.Window | Qt.WindowTitleHint |
                     Qt.WindowMinimizeButtonHint |
                     Qt.WindowMaximizeButtonHint |
                     Qt.WindowCloseButtonHint)
            self.setWindowFlags(flags)
            self.show()
            self.showMaximized()
        else:
            self.setWindowFlags(self._orig_flags)
            self.show()
            if self._saved_geom:
                self.restoreGeometry(self._saved_geom)
            self.showNormal()
    def _on_login_success(self, url: str):
        # 접속 성공 → 두 번째 화면으로 전환
        self.stack.setCurrentIndex(1)
        self.act_test_info.setEnabled(True)
        self.act_run_platform.setEnabled(True)
        self.act_logout.setEnabled(True)
        self.act_login.setEnabled(False)
        # 필요 시 selection_widget에 서버 URL 전달:
        # if hasattr(self.selection_widget, 'setServerUrl'): self.selection_widget.setServerUrl(url)

    def _logout(self):
        """로그아웃 처리"""
        # 스택을 로그인 화면으로 전환
        self.stack.setCurrentIndex(0)
        # 시험 관련 메뉴 비활성화
        self.act_test_info.setEnabled(False)
        self.act_run_platform.setEnabled(False)
        self.act_logout.setEnabled(False)
        self.act_login.setEnabled(True)
        # 필요시 platform 화면도 초기화
        if hasattr(self, "_platform_widget"):
            self.stack.removeWidget(self._platform_widget)
            self._platform_widget = None
        QMessageBox.information(self, "로그아웃", "정상적으로 로그아웃되었습니다.")

    def _open_validation_app(self, mode):
        """모드에 따라 다른 검증 앱 실행"""
        if mode in ["request_longpolling", "request_webhook"]:
            # Request 모드 (LongPolling/WebHook) - Platform 검증
            if getattr(self, "_platform_widget", None) is None:
                self._platform_widget = platform_app.MyApp(embedded=True)
                self.stack.addWidget(self._platform_widget)
            self.stack.setCurrentWidget(self._platform_widget)
        elif mode in ["response_longpolling", "response_webhook"]:
            # Response 모드 (LongPolling/WebHook) - System 검증
            if getattr(self, "_system_widget", None) is None:
                self._system_widget = system_app.MyApp(embedded=True)
                self.stack.addWidget(self._system_widget)
            self.stack.setCurrentWidget(self._system_widget)
        else:
            print(f"알 수 없는 모드: {mode}")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '종료', '프로그램을 종료하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    # SSL 경고 무시 (개발환경)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    app = QApplication(sys.argv)

    # 폰트 적용 (원본과 동일)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
