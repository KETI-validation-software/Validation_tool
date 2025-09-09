# login_view.py
import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal


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
        layout = QVBoxLayout()

        title = QLabel("검증 소프트웨어 로그인")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 20pt; font-weight: bold; margin: 20px;')
        layout.addWidget(title)

        grp = QGroupBox("접속 정보")
        form = QFormLayout()

        self.admin_code_input = QLineEdit()
        self.admin_code_input.setPlaceholderText("관리자 코드를 입력하세요")
        form.addRow("관리자 코드:", self.admin_code_input)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://127.0.0.1:8008")
        self.url_input.setText("https://127.0.0.1:8008")
        form.addRow("접속 URL:", self.url_input)

        grp.setLayout(form)
        layout.addWidget(grp)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.login_btn = QPushButton("접속")
        self.login_btn.setFixedSize(100, 40)
        self.login_btn.setDefault(True)
        self.login_btn.clicked.connect(self._on_login)
        btn_row.addWidget(self.login_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.admin_code_input.returnPressed.connect(self._on_login)
        self.url_input.returnPressed.connect(self._on_login)

        layout.addStretch()
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
