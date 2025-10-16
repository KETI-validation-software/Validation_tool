# main.py
import sys
import urllib3
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QAction, QMessageBox
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt

from info_GUI import InfoWidget
from core.functions import resource_path
import platformVal_all as platform_app
import systemVal_all as system_app
import config.CONSTANTS as CONSTANTS
import importlib


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("검증 소프트웨어 통합 실행기")
        self.resize(1200, 720)
        self._orig_flags = self.windowFlags()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 접속 후 화면
        self.info_widget = InfoWidget()
        self.stack.addWidget(self.info_widget)  # index 0
        self.info_widget.startTestRequested.connect(self._on_start_test_requested)

        # info_widget의 페이지 변경 시그널 연결 (시험 정보 불러오기 완료 시)
        self.info_widget.stacked_widget.currentChanged.connect(self._on_page_changed)

        self._setup_menu()
        self.stack.setCurrentIndex(0)

    def _setup_menu(self):
        menubar = self.menuBar()
        main_menu = menubar.addMenu("메뉴")

        # 1. 시험 정보 (초기 활성화)
        self.act_test_info = QAction("시험 정보", self)
        self.act_test_info.triggered.connect(self._show_test_info)
        self.act_test_info.setEnabled(True)  # 초기 활성화
        main_menu.addAction(self.act_test_info)

        # 2. 시험 설정 (시험 정보 불러오기 후 활성화)
        self.act_test_setup = QAction("시험 설정", self)
        self.act_test_setup.triggered.connect(self._show_test_setup)
        self.act_test_setup.setEnabled(False)
        main_menu.addAction(self.act_test_setup)

        # 3. 시험 실행 (시험 설정 완료 후 활성화)
        self.act_test_run = QAction("시험 실행", self)
        self.act_test_run.setEnabled(False)
        self.act_test_run.triggered.connect(self._run_test_from_menu)
        main_menu.addAction(self.act_test_run)

        # 4. 시험 결과 (시험 실행 완료 후 활성화)
        self.act_test_result = QAction("시험 결과", self)
        self.act_test_result.setEnabled(False)
        self.act_test_result.triggered.connect(self._show_test_result)
        main_menu.addAction(self.act_test_result)

        main_menu.addSeparator()

        # 종료
        act_exit = QAction("종료", self)
        act_exit.triggered.connect(self.close)
        main_menu.addAction(act_exit)

        view_menu = menubar.addMenu("보기")
        act_full = QAction("전체화면 전환", self, checkable=True)
        act_full.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(act_full)

    def _show_test_info(self):
        """시험 정보 페이지로 이동 (1페이지)"""
        # 메인 stack을 info_widget으로 전환
        self.stack.setCurrentWidget(self.info_widget)
        # info_widget 내부를 1페이지로 전환
        self.info_widget.stacked_widget.setCurrentIndex(0)
        print("시험 정보 페이지로 이동")

    def _show_test_setup(self):
        """시험 설정 페이지로 이동 (2페이지)"""
        # 메인 stack을 info_widget으로 전환
        self.stack.setCurrentWidget(self.info_widget)
        # info_widget 내부를 2페이지로 전환
        self.info_widget.stacked_widget.setCurrentIndex(1)
        print("시험 설정 페이지로 이동")

    def _show_test_result(self):
        """시험 결과 페이지로 이동"""
        # 현재 활성화된 검증 위젯 찾기
        validation_widget = None
        
        if hasattr(self, '_system_widget') and self._system_widget is not None:
            validation_widget = self._system_widget
        elif hasattr(self, '_platform_widget') and self._platform_widget is not None:
            validation_widget = self._platform_widget
        
        if validation_widget is None:
            QMessageBox.warning(self, "경고", "시험이 실행되지 않았습니다.\n먼저 시험을 실행해주세요.")
            return
        
        # 시험 결과 위젯 생성 및 스택에 추가
        self._show_result_widget(validation_widget)
        print("✓ 시험 결과 페이지로 이동")

    def _show_result_widget(self, parent_widget):
        """시험 결과 위젯을 스택에 추가하고 전환"""
        # 기존 시험 결과 위젯이 있으면 제거
        if hasattr(self, '_result_widget') and self._result_widget is not None:
            self.stack.removeWidget(self._result_widget)
            self._result_widget.deleteLater()
        
        # 새로운 시험 결과 위젯 생성
        if isinstance(parent_widget, platform_app.MyApp):
            print(f"   → Platform 시험 결과 페이지로 전환")
            self._result_widget = platform_app.ResultPageWidget(parent_widget, embedded=True)
        elif isinstance(parent_widget, system_app.MyApp):
            print(f"   → System 시험 결과 페이지로 전환")
            self._result_widget = system_app.ResultPageWidget(parent_widget, embedded=True)
        else:
            print(f"알 수 없는 parent_widget 타입: {type(parent_widget)}")
            return
        
        # 뒤로가기 시그널 연결
        self._result_widget.backRequested.connect(self._on_back_to_validation)
        
        # 스택에 추가하고 전환
        self.stack.addWidget(self._result_widget)
        self.stack.setCurrentWidget(self._result_widget)
        
        # 시험 결과 메뉴 활성화
        self.act_test_result.setEnabled(True)
        print("✓ 시험 결과 메뉴 활성화")
    
    def _on_back_to_validation(self):
        """뒤로가기: 시험 결과 페이지에서 검증 화면으로 복귀"""
        # 현재 활성화된 검증 위젯으로 전환
        if hasattr(self, '_system_widget') and self._system_widget is not None:
            self.stack.setCurrentWidget(self._system_widget)
            print("✓ 시스템 검증 화면으로 복귀")
        elif hasattr(self, '_platform_widget') and self._platform_widget is not None:
            self.stack.setCurrentWidget(self._platform_widget)
            print("✓ 플랫폼 검증 화면으로 복귀")
        else:
            print("⚠️ 검증 위젯을 찾을 수 없습니다.")

    def _on_show_result_requested(self, parent_widget):
        """검증 화면에서 시험 결과 표시 요청 시 호출 (embedded 모드에서)"""
        print(f"✓ _on_show_result_requested 호출됨")
        print(f"   parent_widget 타입: {type(parent_widget)}")
        print(f"   parent_widget.embedded: {parent_widget.embedded}")
        
        # 스택에 시험 결과 위젯 추가하고 전환
        self._show_result_widget(parent_widget)

    def _on_page_changed(self, index):
        """info_widget의 페이지가 변경될 때 호출되는 함수"""
        if index == 1:
            # 2페이지(시험 설정)로 이동 → 시험 설정 메뉴 활성화
            self.act_test_setup.setEnabled(True)
            print("✓ 시험 설정 메뉴 활성화")

    def _on_start_test_requested(self, mode):
        """시험 시작 버튼 클릭 시 호출 - 시험 실행 메뉴 활성화 후 검증 앱 실행"""
        # 시험 실행 메뉴 활성화
        self.act_test_run.setEnabled(True)
        print("시험 실행 메뉴 활성화")

        # 현재 모드 저장 (메뉴에서 시험 실행 클릭 시 사용)
        self._current_test_mode = mode

        # 검증 앱 실행
        self._open_validation_app(mode)

    def _run_test_from_menu(self):
        """메뉴에서 시험 실행 클릭 시 호출 - 메인 창을 검증 화면으로 전환"""
        if hasattr(self, '_current_test_mode') and self._current_test_mode:
            mode = self._current_test_mode
            print(f"시험 실행 페이지로 이동: verificationType={mode}")

            # 메인 창을 해당 검증 화면으로 전환
            if mode == "request":
                # Request 모드 - 메인 창을 System 검증으로 전환
                if getattr(self, "_system_widget", None) is None:
                    self._system_widget = system_app.MyApp(embedded=True)
                    # Embedded 위젯도 시험 결과 시그널 연결
                    self._system_widget.showResultRequested.connect(self._on_show_result_requested)
                    self.stack.addWidget(self._system_widget)
                self.stack.setCurrentWidget(self._system_widget)
            elif mode == "response":
                # Response 모드 - 메인 창을 Platform 검증으로 전환
                if getattr(self, "_platform_widget", None) is None:
                    self._platform_widget = platform_app.MyApp(embedded=True)
                    # Embedded 위젯도 시험 결과 시그널 연결
                    self._platform_widget.showResultRequested.connect(self._on_show_result_requested)
                    self.stack.addWidget(self._platform_widget)
                self.stack.setCurrentWidget(self._platform_widget)
        else:
            QMessageBox.warning(self, "경고", "시험 모드가 설정되지 않았습니다.\n시험 시작 버튼을 먼저 클릭해주세요.")

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

    def _open_validation_app(self, mode):
        """verificationType에 따라 다른 검증 앱 실행 (API 기반)"""
        importlib.reload(CONSTANTS)  # CONSTANTS 모듈을 다시 로드하여 최신 설정 반영

        print(f"검증 화면 실행: verificationType={mode}")

        if mode == "request":
            # Request 모드 - Platform 검증 (새 창 with 래퍼)
            if hasattr(self, "platform_window") and self.platform_window is not None:
                self.platform_window.close()
            # 래퍼 윈도우 사용 (스택 전환 지원)
            self.platform_window = platform_app.PlatformValidationWindow()
            self.platform_window.initialize()  # MyApp 정의 후 초기화
            self.platform_window.show()

            # Main 화면은 System 검증으로 전환
            if getattr(self, "_system_widget", None) is None:
                self._system_widget = system_app.MyApp(embedded=True)
                # Embedded 위젯도 시험 결과 시그널 연결
                self._system_widget.showResultRequested.connect(self._on_show_result_requested)
                self.stack.addWidget(self._system_widget)
            self.stack.setCurrentWidget(self._system_widget)

        elif mode == "response":
            # Response 모드 - System 검증 (새 창)
            if hasattr(self, "system_window") and self.system_window is not None:
                self.system_window.close()
            self.system_window = system_app.MyApp(embedded=False)
            # 시험 결과 표시 시그널 연결
            self.system_window.showResultRequested.connect(self._on_show_result_requested)
            self.system_window.show()

            # Main 화면은 Platform 검증으로 전환
            if getattr(self, "_platform_widget", None) is None:
                self._platform_widget = platform_app.MyApp(embedded=True)
                # Embedded 위젯도 시험 결과 시그널 연결
                self._platform_widget.showResultRequested.connect(self._on_show_result_requested)
                self.stack.addWidget(self._platform_widget)
            self.stack.setCurrentWidget(self._platform_widget)

        else:
            print(f"알 수 없는 verificationType: {mode}")
            print(f"   (API에서 'request' 또는 'response'를 반환해야 합니다)")

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