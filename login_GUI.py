# login_view.py
import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap  # [추가] 아이콘/로고 표시용
from PyQt5.QtWidgets import QSpacerItem,QSizePolicy


class LoginWidget(QWidget):
    """
    시작 화면 GUI.
    - 관리자 코드 + URL 입력
    - 접속 성공 시 loginSucceeded(url: str) 시그널 발행
    """
    loginSucceeded = pyqtSignal(str)

    def __init__(self, expected_code: str = "1234"):
        super().__init__()
        self.expected_code = expected_code
        self._build_ui()

    def _build_ui(self):
        # ----- 윈도우 / 배경 -----
        self.setWindowTitle("검증 소프트웨어 통합 실행기")
        self.setObjectName("root")
        # 업로드한 배경 이미지 적용
        self.setStyleSheet("""
            QWidget#root {
                background-image: url('assets/image/login/로그인-배경.png');
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed;
                background-color: #f5f6f8; /* 이미지 밖 영역 톤 맞춤 */
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # ----- 상단 헤더(로고+타이틀) -----
        header = QWidget()
        header.setStyleSheet("background-color: #163971;")
        header.setFixedHeight(50)
        h = QHBoxLayout(header)
        h.setContentsMargins(20, 8, 20, 8)
        logo = QLabel()
        logo_pix = QPixmap("assets/image/login/헤더-로고.png").scaledToHeight(
            24, Qt.SmoothTransformation
        )
        logo.setPixmap(logo_pix)
        logo.setFixedSize(logo_pix.size())                 # 로고 크기 고정
        logo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        title_bar = QLabel("연동 검증 소프트웨어")
        title_bar.setStyleSheet("color: white; font-weight: bold; font-size: 11pt;")
        title_bar.setFixedHeight(24)                       # 텍스트 높이 고정
        title_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        h.addWidget(logo)
        h.addSpacing(8)
        h.addWidget(title_bar)
        h.addStretch()
        layout.addWidget(header)

        # ----- 상단 여백 -----
        spacer_top = QWidget()
        spacer_top.setFixedHeight(40)
        layout.addWidget(spacer_top)

        # ----- 입력 그룹 -----
        grp = QGroupBox()
        grp.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
            }
            QLineEdit {
                height: 50px;
                padding: 0 12px;
                border: 1px solid #cfd6e4;
                border-radius: 4px;
                background: #ffffff;
                font-size: 12pt;
            }
            QLabel {
                font-weight: bold;       
                font-size: 12pt;
                color: #1e2432;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6;
            } 
        """)

        form = QFormLayout()
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(16)
        form.setContentsMargins(0, 0, 0, 0)

        self.admin_code_input = QLineEdit()
        self.admin_code_input.setPlaceholderText("관리자 코드를 입력하세요")
        self.admin_code_input.setEchoMode(QLineEdit.Password)

        self.admin_code_input.setFixedSize(620, 40)
        form.addRow("관리자 코드", self.admin_code_input)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL을 입력하세요")
        self.url_input.setText("https://127.0.0.1:8008")
        self.url_input.setFixedSize(620, 40)
        form.addRow("접속 URL", self.url_input)

        form.addItem(QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # 버튼을 form layout 안에 추가 (레이블 칸 비우고 버튼만 중앙 정렬)
        self.login_btn = QPushButton("")  # 텍스트 추가
        self.login_btn.setFixedSize(732,40)        # 높이만 고정
        self.login_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                background-image: url('assets/image/login/접속정보입력-버튼-default.png');
            }
            QPushButton:hover {
                background-image: url('assets/image/login/접속정보입력-버튼-hover.png');
            }
        """)
        self.login_btn.setDefault(True)
        self.login_btn.clicked.connect(self._on_login)

        # 버튼 중앙정렬 + 입력창과 동일 폭 유지
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.login_btn)
        btn_layout.addStretch()

        # 버튼을 form 안에 추가
        form.addRow(btn_layout)
        grp.setLayout(form)
        center_wrapper = QVBoxLayout()
        center_wrapper.setAlignment(Qt.AlignCenter)
        spacer_between = QSpacerItem(0, 50, QSizePolicy.Minimum, QSizePolicy.Fixed)
        center_wrapper.addSpacerItem(spacer_between)
        # ----- 상단 일러스트 아이콘 -----
        icon = QLabel()
        icon.setPixmap(
            QPixmap("assets/image/login/접속정보입력-아이콘.png").scaled(
                80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        icon.setFixedSize(80, 80)  # 크기 고정
        center_wrapper.addWidget(icon, alignment=Qt.AlignCenter)



        # ----- 입력 그룹 (앞서 만든 grp) -----
        center_wrapper.addWidget(grp, alignment=Qt.AlignCenter)

        # ===== 최상위 레이아웃에 좌우 스트레치로 감싸기 =====
        outer_layout = QHBoxLayout()
        outer_layout.addStretch()
        outer_layout.addLayout(center_wrapper)
        outer_layout.addStretch()
        layout.addLayout(outer_layout)

        # ----- 하단 일러스트 -----
        illust = QLabel()
        illust.setPixmap(
            QPixmap("assets/image/login/로그인-일러스트.png").scaledToWidth(
                800, Qt.SmoothTransformation
            )
        )
        illust.setFixedSize(800, illust.pixmap().height())
        layout.addStretch()  # 위쪽 공간 확보 -> illust를 아래로 밀어줌
        layout.addWidget(illust, alignment=Qt.AlignRight | Qt.AlignBottom)

        # 엔터키 동작
        self.admin_code_input.returnPressed.connect(self._on_login)
        self.url_input.returnPressed.connect(self._on_login)

        self.setLayout(layout)

    def _on_login(self):
        admin_code = self.admin_code_input.text().strip()
        url = self.url_input.text().strip()

        if not admin_code:
            QMessageBox.warning(self, "입력 오류", "관리자 코드를 입력해주세요.")
            self.admin_code_input.setFocus()
            return
        if not url:
            QMessageBox.warning(self, "입력 오류", "접속 URL을 입력해주세요.")
            self.url_input.setFocus()
            return

        if self._validate_credentials(admin_code, url):
            self.loginSucceeded.emit(url)
        else:
            QMessageBox.critical(self, "접속 실패",
                                 "관리자 코드 또는 접속 URL이 올바르지 않습니다.\n다시 입력 및 확인해주세요.")
            self.admin_code_input.clear()
            self.admin_code_input.setFocus()

    def _validate_credentials(self, admin_code: str, url: str) -> bool:
        # 1) 관리자 코드 확인
        if admin_code != self.expected_code:
            return False

        # 2) URL 형식/접속 확인
        if not url.startswith(('http://', 'https://')):
            return False
        try:
            # health 우선, 없으면 루트로
            try:
                requests.get(f"{url}/health", timeout=1, verify=False)
                return True
            except Exception:
                requests.get(url, timeout=1, verify=False)
                return True
        except Exception:
            # 마지막: 형식만이라도 확인
            from urllib.parse import urlparse
            return bool(urlparse(url).netloc)
