# ui/platform_window.py
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt
from ui.result_page import ResultPageWidget

class PlatformValidationWindow(QMainWindow):
    """
    플랫폼 검증을 위한 래퍼 윈도우 (standalone 모드에서 스택 전환 지원)
    """
    def __init__(self, my_app_class):
        super().__init__()
        self.my_app_class = my_app_class
        self.setWindowTitle("통합플랫폼 연동 검증")
        self.resize(1200, 720)

        # 스택 위젯 생성
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 플랫폼 검증 위젯은 나중에 생성 (순환 참조 방지)
        self.validation_widget = None
        self._result_widget = None

    def initialize(self):
        """검증 위젯 초기화"""
        if self.validation_widget is None:
            # 전달받은 MyApp 클래스 인스턴스 생성
            self.validation_widget = self.my_app_class(embedded=False)
            self.validation_widget._wrapper_window = self  # 래퍼 참조 전달
            self.stack.addWidget(self.validation_widget)
            self.stack.setCurrentWidget(self.validation_widget)

    def _show_result_page(self):
        """시험 결과 페이지로 전환 (스택 내부)"""
        # 기존 결과 위젯 제거
        if self._result_widget is not None:
            self.stack.removeWidget(self._result_widget)
            self._result_widget.deleteLater()

        # 새로운 결과 위젯 생성
        self._result_widget = ResultPageWidget(self.validation_widget, embedded=True)
        self._result_widget.backRequested.connect(self._on_back_to_validation)

        # 스택에 추가하고 전환
        self.stack.addWidget(self._result_widget)
        self.stack.setCurrentWidget(self._result_widget)

    def _on_back_to_validation(self):
        """뒤로가기: 시험 결과에서 검증 화면으로 복귀"""
        self.stack.setCurrentWidget(self.validation_widget)
        self.resize(1200, 720)

    def closeEvent(self, event):
        """래퍼 윈도우 닫기 이벤트 - validation_widget의 정리 작업 호출"""
        print(f"[WRAPPER_CLOSE] PlatformValidationWindow closeEvent 호출됨")

        # ✅ 종료 확인 대화상자
        reply = QMessageBox.question(
            self, '프로그램 종료',
            '정말로 프로그램을 종료하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # ✅ validation_widget의 정리 작업 호출
            if self.validation_widget is not None:
                print(f"[WRAPPER_CLOSE] validation_widget 정리 시작")
                # 타이머 중지
                if hasattr(self.validation_widget, 'tick_timer') and self.validation_widget.tick_timer.isActive():
                    self.validation_widget.tick_timer.stop()

                # 서버 스레드 종료
                if hasattr(self.validation_widget, 'server_th') and self.validation_widget.server_th is not None and self.validation_widget.server_th.isRunning():
                    try:
                        self.validation_widget.server_th.httpd.shutdown()
                        self.validation_widget.server_th.wait(2000)
                    except Exception as e:
                        print(f"[WARN] 서버 종료 중 오류 (무시): {e}")

                # 일시정지 파일 삭제
                if hasattr(self.validation_widget, 'cleanup_paused_file'):
                    self.validation_widget.cleanup_paused_file()
                print(f"[WRAPPER_CLOSE] 정리 완료")

            event.accept()
        else:
            event.ignore()
