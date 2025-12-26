# splash_screen.py
"""
실행 파일 시작 시 표시되는 스플래시 스크린 (로딩 화면)
"""
from PyQt5.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar, QWidget
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QLinearGradient


class SplashScreen(QSplashScreen):
    """
    그라데이션이 적용된 스플래시
    """
    def __init__(self, width=650, height=250):
        # 그라데이션 배경 픽스맵 생성
        pixmap = QPixmap(width, height)
        self._draw_background(pixmap, width, height)

        super().__init__(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.width = width
        self.height = height
        self._setup_ui()

    def _draw_background(self, pixmap, width, height):
        """그라데이션 배경 그리기"""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 그라데이션 설정 (#275554 -> #002B69)
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor("#275554"))
        gradient.setColorAt(1, QColor("#002B69"))

        # 사각형 그리기
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, width, height)
        painter.end()

    def _setup_ui(self):
        """UI 구성 요소 생성"""
        # 메인 위젯
        self._widget = QWidget()
        self._widget.setFixedSize(self.width, self.height)
        self._widget.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(50, 40, 50, 30)

        # 타이틀
        self.title_label = QLabel("물리보안 연동성 검증 도구")
        self.title_label.setStyleSheet("""
            color: white;
            font-size: 22pt;
            font-weight: bold;
            font-family: 'Malgun Gothic', 'Noto Sans KR';
            background: transparent;
        """)
        layout.addWidget(self.title_label)

        # 서브 타이틀
        self.subtitle_label = QLabel("시스템 리소스를 불러오는 중...")
        self.subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 180);
            font-size: 12pt;
            background: transparent;
        """)
        layout.addWidget(self.subtitle_label)

        layout.addStretch()

        # 슬림 프로그레스 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 50);
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: white;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # 진행률 텍스트
        self.percent_label = QLabel("0%")
        self.percent_label.setAlignment(Qt.AlignRight)
        self.percent_label.setStyleSheet("""
            color: white;
            font-size: 10pt;
            font-family: 'Consolas';
            background: transparent;
        """)
        layout.addWidget(self.percent_label)

        self._render_widget()

    def _render_widget(self):
        """현재 UI 상태를 픽스맵으로 변환"""
        pixmap = QPixmap(self.width, self.height)
        self._draw_background(pixmap, self.width, self.height)

        painter = QPainter(pixmap)
        self._widget.render(painter)
        painter.end()

        self.setPixmap(pixmap)

    def update_progress(self, value, message=""):
        """
        프로그레스 바 업데이트

        Args:
            value (int): 진행률 (0-100)
            message (str): 상태 메시지
        """
        self.progress_bar.setValue(value)
        self.percent_label.setText(f"{value}%")
        if message:
            self.subtitle_label.setText(message)

        self._render_widget()
        self.repaint()

        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

    def finish_with_window(self, window):
        """
        메인 윈도우가 표시될 때 스플래시 종료

        Args:
            window: 메인 윈도우 객체
        """
        self.finish(window)


class SpinnerWidget(QWidget):
    """
    미니멀한 디자인의 회전 스피너
    """
    def __init__(self, parent=None, color="#ffffff"):
        super().__init__(parent)
        self.angle = 0
        self.color = QColor(color)
        self.setFixedSize(40, 40)

        # 자체 타이머 제거 (부모가 제어)

    def step(self):
        """외부에서 호출하여 회전 (한 프레임 진행)"""
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        """스피너 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)

        pen = QPen(self.color)
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        # 부드러운 호(Arc) 형태의 스피너 그리기
        painter.drawArc(QRectF(-15, -15, 30, 30), 0, 270 * 16)


class LoadingPopup(QSplashScreen):
    """
    평가 시작 시 로딩 상태를 표시하는 팝업
    """
    def __init__(self, width=400, height=200):
        # 그라데이션 배경 픽스맵 생성
        pixmap = QPixmap(width, height)
        self._draw_background_static(pixmap, width, height)

        super().__init__(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.width = width
        self.height = height
        self._setup_ui()

        # 스피너 애니메이션을 위한 타이머
        self.render_timer = QTimer(self)
        self.render_timer.timeout.connect(self._render_widget)
        self.render_timer.start(50)  # 50ms 간격 (약 20fps)

    @staticmethod
    def _draw_background_static(pixmap, width, height):
        """그라데이션 배경 그리기 (정적 메서드)"""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor("#275554"))
        gradient.setColorAt(1, QColor("#002B69"))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, width, height)
        painter.end()

    def _draw_background(self, pixmap):
        """인스턴스 메서드로 배경 그리기"""
        self._draw_background_static(pixmap, self.width, self.height)

    def _setup_ui(self):
        """UI 구성 요소 생성"""
        # 메인 위젯
        self._widget = QWidget()
        self._widget.setFixedSize(self.width, self.height)
        self._widget.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self._widget)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(8)

        # 메인 메시지
        self.message_label = QLabel("평가 준비 중...")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            color: white;
            font-size: 14pt;
            font-weight: bold;
            font-family: 'Segoe UI', 'Malgun Gothic';
            background: transparent;
        """)
        layout.addWidget(self.message_label)

        # 서브 메시지
        self.subtitle_label = QLabel("잠시만 기다려주세요")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 180);
            font-size: 10pt;
            background: transparent;
        """)
        layout.addWidget(self.subtitle_label)

        layout.addStretch()

        # 회전하는 스피너
        spinner_container = QWidget()
        spinner_container.setStyleSheet("background: transparent;")
        spinner_layout = QVBoxLayout(spinner_container)
        spinner_layout.setContentsMargins(0, 0, 0, 0)
        spinner_layout.setAlignment(Qt.AlignCenter)

        self.spinner = SpinnerWidget(color="#ffffff")
        spinner_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        layout.addWidget(spinner_container)

        layout.addStretch()

        self._render_widget()

    def _render_widget(self):
        """현재 UI 상태를 픽스맵으로 변환 (애니메이션 프레임)"""
        # 스피너 회전 (한 프레임 진행)
        if hasattr(self, 'spinner'):
            self.spinner.step()

        pixmap = QPixmap(self.width, self.height)
        self._draw_background(pixmap)

        painter = QPainter(pixmap)
        # 위젯을 픽스맵에 렌더링
        self._widget.render(painter)
        painter.end()

        self.setPixmap(pixmap)
        
        # UI 반응성 확보
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

    def update_message(self, message, subtitle=""):
        """
        메시지 업데이트

        Args:
            message (str): 메인 메시지
            subtitle (str): 서브 메시지
        """
        self.message_label.setText(message)
        if subtitle:
            self.subtitle_label.setText(subtitle)

        # 메시지 변경 즉시 렌더링
        self._render_widget()
        self.repaint()

    def close(self):
        """팝업 닫기 시 타이머 정지"""
        if hasattr(self, 'render_timer'):
            self.render_timer.stop()
        super().close()


# ===== 사용 예시 =====
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    import time

    app = QApplication(sys.argv)

    # 스플래시 생성 및 표시
    splash = SplashScreen()
    splash.show()

    # 로딩 시뮬레이션
    steps = [
        (0, "프로그램 시작 중..."),
        (20, "폰트 로딩 중..."),
        (40, "핵심 모듈 로딩 중..."),
        (60, "GUI 컴포넌트 준비 중..."),
        (80, "설정 파일 읽는 중..."),
        (100, "시작 완료!")
    ]

    for value, msg in steps:
        splash.update_progress(value, msg)
        time.sleep(0.5)

    # 메인 윈도우 생성
    main_window = QMainWindow()
    main_window.setWindowTitle("메인 화면")
    main_window.resize(800, 600)

    # 스플래시 종료 및 메인 윈도우 표시
    splash.finish_with_window(main_window)
    main_window.show()

    sys.exit(app.exec_())
