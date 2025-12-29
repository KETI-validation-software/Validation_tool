"""
인증 방식 섹션
- AuthSection: 인증 방식 선택 및 사용자 ID/PW 입력 (744x240px)
"""
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QRadioButton, QLineEdit, QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from core.functions import resource_path


class AuthSection(QGroupBox):
    """인증 방식 섹션 (744x240px)"""

    # 시그널 정의
    authTypeChanged = pyqtSignal()

    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setFixedSize(744, 240)
        self.setStyleSheet("QGroupBox { border: none; margin-top: 0px; padding-top: 0px; background-color: transparent; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 콘텐츠 영역 (744x240px)
        self.auth_content_widget = QWidget()
        self.auth_content_widget.setFixedSize(744, 240)
        self.auth_content_widget.setStyleSheet("""
            #content_widget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
            }
            QRadioButton {
                border: none;
                background-color: transparent;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
            QLineEdit {
                border: none;
            }
        """)
        self.auth_content_widget.setObjectName("content_widget")

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(24, 16, 24, 16)
        content_layout.setSpacing(0)

        # 왼쪽: 인증 방식 선택 영역
        self._setup_auth_type_selection(content_layout)

        # divider 왼쪽 gap 12px
        content_layout.addSpacing(12)

        # 수직 divider
        self._setup_divider(content_layout)

        # divider 오른쪽 gap 12px
        content_layout.addSpacing(12)

        # 오른쪽: User ID/Password 입력 영역
        self._setup_input_fields(content_layout)

        self.auth_content_widget.setLayout(content_layout)
        layout.addWidget(self.auth_content_widget)

        # 라디오 버튼 그룹 설정
        self.auth_button_group = QButtonGroup()
        self.auth_button_group.addButton(self.digest_radio)
        self.auth_button_group.addButton(self.bearer_radio)

        # 라디오 버튼 연결
        self.digest_radio.toggled.connect(self._on_auth_type_changed)
        self.bearer_radio.toggled.connect(self._on_auth_type_changed)

        self.setLayout(layout)

        # 부모 위젯에 참조 설정
        if self.parent_widget:
            self.parent_widget.auth_section = self
            self.parent_widget.original_auth_section_size = (744, 240)
            self.parent_widget.auth_content_widget = self.auth_content_widget
            self.parent_widget.original_auth_content_widget_size = (744, 240)
            self.parent_widget.auth_type_widget = self.auth_type_widget
            self.parent_widget.original_auth_type_widget_size = (289, 208)
            self.parent_widget.digest_option = self.digest_option
            self.parent_widget.original_digest_option_size = (289, 86)
            self.parent_widget.bearer_option = self.bearer_option
            self.parent_widget.original_bearer_option_size = (289, 86)
            self.parent_widget.digest_radio = self.digest_radio
            self.parent_widget.bearer_radio = self.bearer_radio
            self.parent_widget.auth_divider = self.auth_divider
            self.parent_widget.original_auth_divider_size = (1, 208)
            self.parent_widget.common_input_widget = self.common_input_widget
            self.parent_widget.original_common_input_widget_size = (358, 208)
            self.parent_widget.id_input = self.id_input
            self.parent_widget.original_id_input_size = (358, 40)
            self.parent_widget.pw_input = self.pw_input
            self.parent_widget.original_pw_input_size = (358, 40)
            self.parent_widget.auth_button_group = self.auth_button_group

    def _setup_auth_type_selection(self, parent_layout):
        """인증 방식 선택 영역 설정"""
        self.auth_type_widget = QWidget()
        self.auth_type_widget.setFixedSize(289, 208)
        self.auth_type_widget.setStyleSheet("background-color: transparent;")
        auth_type_layout = QVBoxLayout()
        auth_type_layout.setContentsMargins(0, 12, 0, 12)
        auth_type_layout.setSpacing(12)

        # Digest Auth 박스
        self.digest_option = self._create_auth_option(
            "Digest Auth", "ID,PW 기반 인증 방식", is_selected=True
        )
        self.digest_radio = self.digest_option.findChild(QRadioButton)
        self.digest_radio.setChecked(True)
        auth_type_layout.addWidget(self.digest_option)

        # Bearer Token 박스
        self.bearer_option = self._create_auth_option(
            "Bearer Token", "Token 기반 인증 방식", is_selected=False
        )
        self.bearer_radio = self.bearer_option.findChild(QRadioButton)
        auth_type_layout.addWidget(self.bearer_option)

        self.auth_type_widget.setLayout(auth_type_layout)
        parent_layout.addWidget(self.auth_type_widget)

        # 박스 클릭 시 라디오 버튼 선택
        self.digest_option.mousePressEvent = lambda event: self.digest_radio.setChecked(True)
        self.bearer_option.mousePressEvent = lambda event: self.bearer_radio.setChecked(True)

    def _create_auth_option(self, title, description, is_selected=False):
        """인증 옵션 박스 생성"""
        option = QWidget()
        option.setFixedSize(289, 86)

        if is_selected:
            option.setStyleSheet("""
                QWidget {
                    background-color: #E9F6FE;
                    border: 1px solid #2B96ED;
                    border-radius: 8px;
                }
            """)
        else:
            option.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    border: 1px solid #CECECE;
                    border-radius: 8px;
                }
            """)

        option_layout = QHBoxLayout()
        option_layout.setContentsMargins(16, 16, 16, 16)
        option_layout.setSpacing(0)

        # 라디오 버튼
        radio = QRadioButton()
        radio.setFixedSize(30, 54)
        radio.setStyleSheet("""
            QRadioButton {
                border: none;
                background: transparent;
                padding-bottom: 26px;
            }
            QRadioButton::indicator {
                width: 28px;
                height: 28px;
            }
        """)
        option_layout.addWidget(radio, alignment=Qt.AlignTop)

        # 8px gap
        option_layout.addSpacing(8)

        # 텍스트 영역
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        # 제목
        title_label = QLabel(title)
        title_label.setFixedSize(130 if title == "Bearer Token" else 120, 26)
        title_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 20px;
                letter-spacing: -0.20px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        text_layout.addWidget(title_label)

        # 2px gap
        text_layout.addSpacing(2)

        # 설명
        desc_label = QLabel(description)
        desc_label.setFixedSize(163, 26)
        desc_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #6B6B6B;
                border: none;
                background-color: transparent;
            }
        """)
        text_layout.addWidget(desc_label)

        option_layout.addLayout(text_layout)
        option_layout.addStretch()

        option.setLayout(option_layout)
        return option

    def _setup_divider(self, parent_layout):
        """수직 divider 설정"""
        self.auth_divider = QLabel()
        self.auth_divider.setFixedSize(1, 208)
        divider_pixmap = QPixmap(resource_path("assets/image/test_config/divider.png"))
        self.auth_divider.setPixmap(divider_pixmap.scaled(1, 208, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        parent_layout.addWidget(self.auth_divider)

    def _setup_input_fields(self, parent_layout):
        """User ID/Password 입력 영역 설정"""
        self.common_input_widget = QWidget()
        self.common_input_widget.setFixedSize(358, 208)
        self.common_input_widget.setStyleSheet("background-color: transparent;")
        common_input_layout = QVBoxLayout()
        common_input_layout.setContentsMargins(0, 12, 0, 12)
        common_input_layout.setSpacing(0)

        # "사용자 ID입력" 문구
        auth_input_title = QLabel("사용자 ID입력")
        auth_input_title.setFixedSize(358, 29)
        auth_input_title.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 20px;
                letter-spacing: -0.20px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        common_input_layout.addWidget(auth_input_title)

        # gap 10px
        common_input_layout.addSpacing(10)

        # "User ID" 문구
        userid_label = QLabel("User ID")
        userid_label.setFixedSize(358, 26)
        userid_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        common_input_layout.addWidget(userid_label)

        # gap 4px
        common_input_layout.addSpacing(4)

        # 아이디 입력칸
        digest_enabled = resource_path("assets/image/test_config/input_DigestAuth_enabled.png").replace(chr(92), "/")
        digest_disabled = resource_path("assets/image/test_config/input_DigestAuth_disabled.png").replace(chr(92), "/")

        self.id_input = QLineEdit()
        self.id_input.setFixedSize(358, 40)
        self.id_input.setPlaceholderText("사용자 ID를 입력해주세요")
        self.id_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 24px;
                padding-right: 24px;
                border: none;
                border-image: url({digest_enabled}) 0 0 0 0 stretch stretch;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
            }}
            QLineEdit::placeholder {{
                color: #868686;
                font-size: 18px;
                font-weight: 500;
            }}
            QLineEdit:disabled {{
                border-image: url({digest_disabled}) 0 0 0 0 stretch stretch;
                color: #868686;
            }}
        """)
        common_input_layout.addWidget(self.id_input)

        # gap 6px
        common_input_layout.addSpacing(6)

        # "Password" 문구
        password_label = QLabel("Password")
        password_label.setFixedSize(358, 26)
        password_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        common_input_layout.addWidget(password_label)

        # gap 4px
        common_input_layout.addSpacing(4)

        # password 입력칸
        self.pw_input = QLineEdit()
        self.pw_input.setFixedSize(358, 40)
        self.pw_input.setPlaceholderText("암호를 입력해 주세요")
        self.pw_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 24px;
                padding-right: 24px;
                border: none;
                border-image: url({digest_enabled}) 0 0 0 0 stretch stretch;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 18px;
                letter-spacing: -0.18px;
                color: #000000;
            }}
            QLineEdit::placeholder {{
                color: #868686;
                font-size: 18px;
                font-weight: 500;
            }}
            QLineEdit:disabled {{
                border-image: url({digest_disabled}) 0 0 0 0 stretch stretch;
                color: #868686;
            }}
        """)
        common_input_layout.addWidget(self.pw_input)

        self.common_input_widget.setLayout(common_input_layout)
        parent_layout.addWidget(self.common_input_widget)

        # 입력 필드 변경 시 버튼 상태 체크
        if self.parent_widget:
            self.id_input.textChanged.connect(self.parent_widget.check_start_button_state)
            self.pw_input.textChanged.connect(self.parent_widget.check_start_button_state)

    def _on_auth_type_changed(self):
        """인증 방식 변경 시 박스 스타일 업데이트"""
        if self.digest_radio.isChecked():
            self.digest_option.setStyleSheet("""
                QWidget {
                    background-color: #E9F6FE;
                    border: 1px solid #2B96ED;
                    border-radius: 8px;
                }
            """)
            self.bearer_option.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    border: 1px solid #CECECE;
                    border-radius: 8px;
                }
            """)
        else:
            self.bearer_option.setStyleSheet("""
                QWidget {
                    background-color: #E9F6FE;
                    border: 1px solid #2B96ED;
                    border-radius: 8px;
                }
            """)
            self.digest_option.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    border: 1px solid #CECECE;
                    border-radius: 8px;
                }
            """)

        # 시그널 emit
        self.authTypeChanged.emit()

        # 부모 위젯의 update_start_button_state 호출
        if self.parent_widget and hasattr(self.parent_widget, 'update_start_button_state'):
            self.parent_widget.update_start_button_state()
