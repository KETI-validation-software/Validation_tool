# splash_screen.py
"""
실행 파일 시작 시 표시되는 스플래시 스크린 (로딩 화면)
PyQt5로 코드만으로 디자인 (이미지 불필요)
"""
from PyQt5.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar, QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen
import math


class SplashScreen(QSplashScreen):
    """
    프로그램 시작 시 로딩 상태를 표시하는 스플래시 스크린
    """
    def __init__(self, width=500, height=300):
        # 빈 픽스맵 생성 (배경용)
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#f5f6f8"))

        super().__init__(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.width = width
        self.height = height
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성 요소 생성"""
        # 메인 위젯 (레이아웃 사용 위해)
        widget = QWidget()
        widget.setObjectName("splashContainer")
        widget.setFixedSize(self.width, self.height)
        widget.setStyleSheet("""
            #splashContainer {
                background-color: #FFFFFF;
                border: 3px solid #A3A9AD;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # ===== 상단 여백 =====
        layout.addStretch(1)

        # ===== 타이틀 =====
        # self.title_label = QLabel("검증 소프트웨어 통합 실행기")
        # self.title_label.setAlignment(Qt.AlignCenter)
        # self.title_label.setStyleSheet("""
        #     QLabel {
        #         color: #163971;
        #         font-size: 18pt;
        #         font-weight: bold;
        #         padding: 10px;
        #     }
        # """)
        # layout.addWidget(self.title_label)

        # ===== 서브 타이틀 =====
        self.subtitle_label = QLabel("프로그램 시작 중...")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                color: #666666;
                font-size: 18pt;
                font-weight: 500;
                padding: 5px;
            }
        """)
        layout.addWidget(self.subtitle_label)

        # ===== 중간 여백 =====
        layout.addStretch(1)

        # ===== 프로그레스 바 =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                font-family: 'Noto Sans KR';
                border: 1px solid #cfd6e4;
                border-radius: 4px;
                background-color: #ffffff;
                text-align: center;
                font-size: 14pt;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # ===== 상태 메시지 =====
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                color: #888888;
                font-size: 12pt;
                font-weight: 400;
                padding: 5px;
            }
        """)
        layout.addWidget(self.status_label)

        # ===== 하단 여백 =====
        layout.addStretch(1)

        widget.setLayout(layout)

        # 위젯을 스플래시에 직접 설정할 수 없으므로, 렌더링을 위해 저장
        self._widget = widget
        self._render_widget()

    def _render_widget(self):
        """위젯을 픽스맵에 렌더링"""
        pixmap = QPixmap(self.width, self.height)
        pixmap.fill(QColor("#f5f6f8"))

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
        if message:
            self.status_label.setText(message)

        # 위젯 다시 렌더링
        self._render_widget()

        # UI 업데이트 강제 실행
        self.repaint()

        # 이벤트 루프 처리 (애니메이션이 부드럽게 보이도록)
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
    회전하는 스피너 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.setFixedSize(50, 50)

        # 타이머 설정 (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # 50ms = 20 FPS

    def rotate(self):
        """회전 각도 업데이트"""
        self.angle = (self.angle + 60) % 360
        self.update()

    def paintEvent(self, event):
        """스피너 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 중심점
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = 15

        # 8개의 선분을 원형으로 배치
        num_lines = 8
        for i in range(num_lines):
            # 각 선분의 각도 계산
            angle_deg = self.angle + (i * 360 / num_lines)
            angle_rad = math.radians(angle_deg)

            # 투명도 계산 (회전 방향으로 갈수록 진해짐)
            alpha = int(255 * (i + 1) / num_lines)

            # 선분 색상 설정
            color = QColor(59, 130, 246, alpha)  # #3b82f6 with varying alpha
            pen = QPen(color, 3, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)

            # 선분 시작점과 끝점 계산
            inner_radius = radius * 0.5
            outer_radius = radius

            start_x = center_x + inner_radius * math.cos(angle_rad)
            start_y = center_y + inner_radius * math.sin(angle_rad)
            end_x = center_x + outer_radius * math.cos(angle_rad)
            end_y = center_y + outer_radius * math.sin(angle_rad)

            # 선분 그리기
            painter.drawLine(
                QPointF(start_x, start_y),
                QPointF(end_x, end_y)
            )

        painter.end()


class LoadingPopup(QSplashScreen):
    """
    평가 시작 시 로딩 상태를 표시하는 팝업
    """
    def __init__(self, width=400, height=250):
        # 빈 픽스맵 생성 (배경용)
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#f5f6f8"))

        super().__init__(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.width = width
        self.height = height
        self._setup_ui()

        # 스피너 애니메이션을 위한 타이머 (스피너와 동기화)
        self.render_timer = QTimer(self)
        self.render_timer.timeout.connect(self._render_widget)
        self.render_timer.start(50)  # 50ms = 20 FPS

    def _setup_ui(self):
        """UI 구성 요소 생성"""
        # 메인 위젯 (레이아웃 사용 위해)
        widget = QWidget()
        widget.setObjectName("loadingContainer")
        widget.setFixedSize(self.width, self.height)
        widget.setStyleSheet("""
            #loadingContainer {
                background-color: #FFFFFF;
                border: 3px solid #A3A9AD;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # ===== 상단 여백 =====
        layout.addStretch(1)

        # ===== 메시지 =====
        self.message_label = QLabel("평가 준비 중...")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                color: #163971;
                font-size: 14pt;
                font-weight: 500;
                padding: 10px;
            }
        """)
        layout.addWidget(self.message_label)

        # ===== 서브 메시지 =====
        self.subtitle_label = QLabel("잠시만 기다려주세요")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                color: #666666;
                font-size: 12pt;
                font-weight: 400;
                padding: 5px;
            }
        """)
        layout.addWidget(self.subtitle_label)

        # ===== 중간 여백 =====
        layout.addStretch(1)

        # ===== 회전하는 스피너 =====
        spinner_container = QWidget()
        spinner_layout = QVBoxLayout()
        spinner_layout.setContentsMargins(0, 0, 0, 0)
        spinner_layout.setAlignment(Qt.AlignCenter)

        self.spinner = SpinnerWidget()
        spinner_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        spinner_container.setLayout(spinner_layout)
        layout.addWidget(spinner_container)

        # ===== 하단 여백 =====
        layout.addStretch(1)

        widget.setLayout(layout)

        # 위젯을 스플래시에 직접 설정할 수 없으므로, 렌더링을 위해 저장
        self._widget = widget
        self._render_widget()

    def _render_widget(self):
        """위젯을 픽스맵에 렌더링"""
        pixmap = QPixmap(self.width, self.height)
        pixmap.fill(QColor("#f5f6f8"))

        painter = QPainter(pixmap)
        self._widget.render(painter)
        painter.end()

        self.setPixmap(pixmap)

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

        # 위젯 다시 렌더링
        self._render_widget()

        # UI 업데이트 강제 실행
        self.repaint()

        # 이벤트 루프 처리
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

    def close(self):
        """팝업 닫기 시 타이머 정지"""
        if hasattr(self, 'render_timer'):
            self.render_timer.stop()
        if hasattr(self, 'spinner') and hasattr(self.spinner, 'timer'):
            self.spinner.timer.stop()
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
        time.sleep(0.5)  # 실제로는 작업 수행

    # 메인 윈도우 생성
    main_window = QMainWindow()
    main_window.setWindowTitle("메인 화면")
    main_window.resize(800, 600)

    # 스플래시 종료 및 메인 윈도우 표시
    splash.finish_with_window(main_window)
    main_window.show()

    sys.exit(app.exec_())
