# splash_screen.py
"""
실행 파일 시작 시 표시되는 스플래시 스크린 (로딩 화면)
PyQt5로 코드만으로 디자인 (이미지 불필요)
"""
from PyQt5.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont


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
        widget.setFixedSize(self.width, self.height)

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
                color: #666666;
                font-size: 11pt;
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
                border: 1px solid #cfd6e4;
                border-radius: 4px;
                background-color: #ffffff;
                text-align: center;
                font-size: 10pt;
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
                color: #888888;
                font-size: 9pt;
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
