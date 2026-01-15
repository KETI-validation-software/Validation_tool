import sys
import os
import urllib3
import logging
import traceback
from core.logger import Logger
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt

# ===== PyInstaller 환경에서 외부 config 우선 사용 =====
if getattr(sys, 'frozen', False):
    # PyInstaller로 실행 중
    exe_dir = os.path.dirname(sys.executable)
    external_config_dir = os.path.join(exe_dir, "config")

    # 외부 config 폴더가 없으면 생성
    os.makedirs(external_config_dir, exist_ok=True)

    # sys.path 맨 앞에 추가하여 외부 경로 우선 사용
    if exe_dir not in sys.path:
        sys.path.insert(0, exe_dir)

    # 최초 실행 시 내부 CONSTANTS.py를 외부로 복사
    external_constants = os.path.join(external_config_dir, "CONSTANTS.py")
    if not os.path.exists(external_constants):
        # resource_path는 아직 import 안 됨, 직접 처리
        if hasattr(sys, '_MEIPASS'):
            import shutil
            internal_constants = os.path.join(sys._MEIPASS, "config", "CONSTANTS.py")
            if os.path.exists(internal_constants):
                shutil.copy2(internal_constants, external_constants)
                Logger.info(f"[INIT] 외부 CONSTANTS.py 생성: {external_constants}")
# ===== 외부 config 우선 사용 끝 =====

from ui.info_GUI import InfoWidget
from core.functions import resource_path
import platformVal_all as platform_app
import systemVal_all as system_app
import importlib

# ===== windowed 모드에서 stdout/stderr를 devnull로 리다이렉트 =====
# Windowed 모드(console=False)에서는 sys.stdout/stderr가 None이 됨
# print() 호출 시 서버 스레드 등에서 에러가 발생할 수 있으므로 devnull로 리다이렉트
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')

# ===== 처리되지 않은 예외를 로그에 기록 =====
def exception_hook(exctype, value, tb):
    Logger.error("처리되지 않은 예외 발생!")
    Logger.error(''.join(traceback.format_exception(exctype, value, tb)))
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("검증 소프트웨어 통합 실행기")
        self.setMinimumSize(1680, 1006)  # 최소 크기 설정 (반응형)
        self._center_on_screen()  # 화면 중앙에 배치
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 접속 후 화면
        self.info_widget = InfoWidget()
        self.stack.addWidget(self.info_widget)  # index 0
        self.info_widget.startTestRequested.connect(self._on_start_test_requested)
        self.stack.setCurrentIndex(0)

    def _center_on_screen(self):
        """윈도우를 화면 중앙에 배치"""
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.minimumWidth()) // 2
        y = (screen.height() - self.minimumHeight()) // 2
        self.move(x, y)

    def _show_result_widget(self, parent_widget):
        """시험 결과 위젯을 스택에 추가하고 전환"""
        # 기존 시험 결과 위젯이 있으면 제거
        if hasattr(self, '_result_widget') and self._result_widget is not None:
            self.stack.removeWidget(self._result_widget)
            self._result_widget.deleteLater()

        # 새로운 시험 결과 위젯 생성
        if isinstance(parent_widget, platform_app.MyApp):
            self._result_widget = platform_app.ResultPageWidget(parent_widget, embedded=True)
        elif isinstance(parent_widget, system_app.MyApp):
            self._result_widget = system_app.ResultPageWidget(parent_widget, embedded=True)
        else:
            Logger.error(f"알 수 없는 parent_widget 타입: {type(parent_widget)}")
            return

        # 뒤로가기 시그널 연결
        self._result_widget.backRequested.connect(self._on_back_to_validation)

        # 스택에 추가하고 전환
        self.stack.addWidget(self._result_widget)
        self.stack.setCurrentWidget(self._result_widget)

    def _on_back_to_validation(self):
        """뒤로가기: 시험 결과 페이지에서 검증 화면으로 복귀"""
        # 현재 활성화된 검증 위젯으로 전환
        if hasattr(self, '_system_widget') and self._system_widget is not None:
            self.stack.setCurrentWidget(self._system_widget)
        elif hasattr(self, '_platform_widget') and self._platform_widget is not None:
            self.stack.setCurrentWidget(self._platform_widget)

    def _on_show_result_requested(self, parent_widget):
        """검증 화면에서 시험 결과 표시 요청 시 호출 (embedded 모드에서)"""
        # 스택에 시험 결과 위젯 추가하고 전환
        self._show_result_widget(parent_widget)

    def _on_start_test_requested(self, target_system_edit, verification_type, spec_id):
        """시험 시작 버튼 클릭 시 호출 - 검증 앱 실행"""
        self._open_validation_app(target_system_edit, verification_type, spec_id)

    def _open_validation_app(self, target_system_edit, verification_type, spec_id):
        """target_system_edit에 따라 다른 검증 앱 실행"""
        try:
            # ===== 로깅 추가 시작 =====
            Logger.info(f"=== _open_validation_app 시작 ===")
            Logger.info(f"target_system={target_system_edit}, verificationType={verification_type}, spec_id={spec_id}")
            # ===== 로깅 추가 끝 =====

            # ===== 수정: PyInstaller 환경에서 CONSTANTS reload =====
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

            # target_system_edit에 따라 어떤 검증 앱을 실행할지 결정
            if "물리보안시스템" in target_system_edit:
                # 물리보안: 메인 창=System, 새 창=Platform
                Logger.info("→ 물리보안: 메인 창=System")

                # ===== 수정: 기존 위젯 제거 후 새로 생성 =====
                # Main 화면: System 검증으로 전환
                if getattr(self, "_system_widget", None) is not None:
                    # 기존 위젯이 있으면 제거
                    Logger.info("기존 System 위젯 제거...")
                    self.stack.removeWidget(self._system_widget)
                    self._system_widget.deleteLater()
                    self._system_widget = None

                Logger.info("System 위젯 생성 시작...")  # 로깅 추가
                self._system_widget = system_app.MyApp(embedded=True, spec_id=spec_id)
                Logger.info("System 위젯 생성 완료")  # 로깅 추가
                self._system_widget.showResultRequested.connect(self._on_show_result_requested)
                self.stack.addWidget(self._system_widget)
                # ===== 수정 끝 =====
                self.stack.setCurrentWidget(self._system_widget)
                Logger.info("System 위젯으로 전환 완료")  # 로깅 추가

            # 1.2로 했을때 통합플랫폼으로 들어가야함
            elif "통합플랫폼시스템" in target_system_edit:
                # 통합플랫폼: 메인 창=Platform, 새 창=System
                Logger.info("→ 통합플랫폼: 메인 창=Platform")

                # ===== 수정: 기존 위젯 제거 후 새로 생성 =====
                # Main 화면: Platform 검증으로 전환
                if getattr(self, "_platform_widget", None) is not None:
                    # 기존 위젯이 있으면 제거
                    Logger.info("기존 Platform 위젯 제거...")
                    self.stack.removeWidget(self._platform_widget)
                    self._platform_widget.deleteLater()
                    self._platform_widget = None

                Logger.info("Platform 위젯 생성 시작...")  # 로깅 추가
                self._platform_widget = platform_app.MyApp(embedded=True, spec_id=spec_id)
                Logger.info("Platform 위젯 생성 완료")  # 로깅 추가
                self._platform_widget.showResultRequested.connect(self._on_show_result_requested)
                Logger.info("Signal 연결 완료")  # 로깅 추가
                self.stack.addWidget(self._platform_widget)
                Logger.info("Stack에 위젯 추가 완료")  # 로깅 추가
                # ===== 수정 끝 =====
                Logger.info("Platform 위젯으로 전환 시작...")  # 로깅 추가
                self.stack.setCurrentWidget(self._platform_widget)
                Logger.info("Platform 위젯으로 전환 완료 ✅")  # 로깅 추가

            else:
                Logger.warning(f"알 수 없는 target_system: {target_system_edit}")
                QMessageBox.warning(self, "경고", f"알 수 없는 시험 분야: {target_system_edit}\n'물리보안' 또는 '통합플랫폼'이 포함되어야 합니다.")

            # ===== 로깅 추가 시작 =====
            Logger.info("=== _open_validation_app 완료 ===")
            # ===== 로깅 추가 끝 =====

        except Exception as e:
            # ===== 예외 처리 로깅 추가 시작 =====
            Logger.error(f"❌ _open_validation_app에서 예외 발생: {e}")
            Logger.error(traceback.format_exc())
            raise
            # ===== 예외 처리 로깅 추가 끝 =====

    def resizeEvent(self, event):
        """창 크기 변경 시 자식 위젯들에 전파"""
        super().resizeEvent(event)

        # 현재 보이는 위젯 가져오기
        current_widget = self.stack.currentWidget()

        # 현재 보이는 위젯의 resizeEvent 강제 호출
        if current_widget is not None:
            # QResizeEvent를 생성하여 전달
            from PyQt5.QtGui import QResizeEvent
            resize_event = QResizeEvent(current_widget.size(), current_widget.size())
            current_widget.resizeEvent(resize_event)

    def closeEvent(self, event):
        Logger.debug(f"[MAIN_CLOSE] MainWindow closeEvent 호출됨")

        reply = QMessageBox.question(self, '종료', '프로그램을 종료하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        Logger.debug(f"[MAIN_CLOSE] 사용자 응답: {'Yes' if reply == QMessageBox.Yes else 'No'}")

        if reply == QMessageBox.Yes:
            # ✅ 플랫폼 검증 위젯의 일시정지 파일 정리
            if hasattr(self, '_platform_widget') and self._platform_widget is not None:
                Logger.debug(f"[MAIN_CLOSE] 플랫폼 검증 위젯 정리 중...")
                if hasattr(self._platform_widget, 'cleanup_paused_file'):
                    self._platform_widget.cleanup_paused_file()
                    Logger.debug(f"[MAIN_CLOSE] 플랫폼 일시정지 파일 삭제 완료")

            # ✅ 시스템 검증 위젯의 일시정지 파일 정리
            if hasattr(self, '_system_widget') and self._system_widget is not None:
                Logger.debug(f"[MAIN_CLOSE] 시스템 검증 위젯 정리 중...")
                if hasattr(self._system_widget, 'cleanup_paused_file'):
                    self._system_widget.cleanup_paused_file()
                    Logger.debug(f"[MAIN_CLOSE] 시스템 일시정지 파일 삭제 완료")

            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    # SSL 경고 무시 (개발환경)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # ===== Logger 초기화 (CONSTANTS에서 레벨 가져오기) =====
    import config.CONSTANTS as CONSTANTS
    Logger.set_level(CONSTANTS.DEBUG_LEVEL)
    Logger.info(f"[INIT] 디버그 레벨 설정: {CONSTANTS.DEBUG_LEVEL}")

    app = QApplication(sys.argv)

    # ===== 스플래시 스크린 표시 (즉시!) =====
    from ui.splash_screen import SplashScreen
    splash = SplashScreen()
    splash.show()
    splash.update_progress(10, "프로그램 시작 중...")
    app.processEvents()  # 동적 스플래시 화면 갱신 강제

    # ===== PyInstaller 정적 스플래시 닫기 (동적 스플래시가 보인 후) =====
    if '_PYIBoot_SPLASH' in os.environ:
        try:
            import pyi_splash
            pyi_splash.close()
        except Exception:
            pass

    # 폰트 로딩
    splash.update_progress(20, "폰트 로딩 중...")
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))

    # 메인 윈도우 생성 (무거운 모듈들 자동 로딩)
    splash.update_progress(40, "GUI 모듈 로딩 중...")
    win = MainWindow()
    splash.update_progress(90, "화면 초기화 중...")

    # 완료
    splash.update_progress(100, "시작 완료!")

    # 스플래시 종료 및 메인 윈도우 표시
    splash.finish_with_window(win)
    win.show()

    sys.exit(app.exec_())