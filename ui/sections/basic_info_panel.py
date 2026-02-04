"""
시험 기본 정보 패널
- BasicInfoPanel: 시험 기본 정보 입력 폼 (872x843px)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap
from core.functions import resource_path


class BasicInfoPanel(QWidget):
    """시험 기본 정보 패널 (872x843px)"""

    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget
        self._setup_ui()

    def _setup_ui(self):
        """UI 초기화"""
        self.setFixedSize(872, 843)

        # QWidget에서 스타일시트 배경이 적용되도록 설정
        self.setAttribute(Qt.WA_StyledBackground, True)

        # 배경 이미지 설정
        bg_panel_path = resource_path("assets/image/test_info/시험기본정보입력.png").replace(chr(92), "/")
        self.setObjectName("basic_info_panel")
        self.setStyleSheet(f"""
            QWidget#basic_info_panel {{
                border-image: url({bg_panel_path}) 0 0 0 0 stretch stretch;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(48, 32, 48, 40)
        layout.setSpacing(0)

        layout.addStretch()

        # 타이틀 컨테이너
        self._setup_title_container(layout)

        layout.addSpacing(12)

        # 인풋 컨테이너
        self._setup_input_container(layout)

        # Divider
        self._setup_divider(layout)

        layout.addSpacing(12)

        # 관리자 코드 필드
        self._setup_admin_code_field(layout)

        layout.addSpacing(32)

        # 하단 버튼
        self._setup_buttons(layout)

        layout.addStretch()

        self.setLayout(layout)

        # 부모 위젯에 참조 설정
        self._set_parent_references()

    def _setup_title_container(self, layout):
        """타이틀 컨테이너 설정"""
        self.panel_title_container = QWidget()
        self.panel_title_container.setFixedSize(776, 106)
        self.panel_title_container.setStyleSheet("QWidget { background: transparent; }")

        title_layout = QVBoxLayout(self.panel_title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        # 타이틀 텍스트
        self.panel_title_text = QLabel("시험 기본 정보 확인")
        self.panel_title_text.setFixedSize(776, 38)
        self.panel_title_text.setAlignment(Qt.AlignCenter)
        self.panel_title_text.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 26px;
                font-weight: 500;
                color: #000000;
                background: transparent;
            }
        """)
        title_layout.addWidget(self.panel_title_text)

        title_layout.addSpacing(16)

        # 타이틀 설명 영역
        self.panel_title_desc = QWidget()
        self.panel_title_desc.setFixedSize(776, 52)
        self.panel_title_desc.setObjectName("panel_title_desc")
        title_desc_bg_path = resource_path("assets/image/test_info/시험기본정보확인_header.png").replace(chr(92), "/")
        self.panel_title_desc.setStyleSheet(f"""
            QWidget#panel_title_desc {{
                border-image: url({title_desc_bg_path}) 0 0 0 0 stretch stretch;
            }}
        """)

        desc_layout = QHBoxLayout(self.panel_title_desc)
        desc_layout.setContentsMargins(14, 12, 48, 12)
        desc_layout.setSpacing(13)

        # 체크 아이콘
        self.panel_check_icon = QLabel()
        check_icon_pixmap = QPixmap(resource_path("assets/image/icon/icn_check.png"))
        self.panel_check_icon.setPixmap(check_icon_pixmap.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.panel_check_icon.setFixedSize(18, 18)
        desc_layout.addWidget(self.panel_check_icon, alignment=Qt.AlignVCenter)

        # 설명 텍스트
        self.panel_desc_text = QLabel("시험 기본 정보를 확인하고 다음 버튼을 눌러주세요.")
        self.panel_desc_text.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        self.panel_desc_text.setAlignment(Qt.AlignVCenter)
        desc_layout.addWidget(self.panel_desc_text, alignment=Qt.AlignVCenter)
        desc_layout.addStretch()

        title_layout.addWidget(self.panel_title_desc)

        layout.addWidget(self.panel_title_container, alignment=Qt.AlignHCenter)

    def _setup_input_container(self, layout):
        """인풋 컨테이너 설정"""
        self.input_container = QWidget()
        self.input_container.setFixedSize(776, 479)
        self.input_container.setStyleSheet("QWidget { background: transparent; }")
        input_layout = QVBoxLayout(self.input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)

        # 기업명 필드
        self.company_field_widget, self.company_label, self.company_edit = self._create_readonly_field("기업명", 776)
        input_layout.addWidget(self.company_field_widget, alignment=Qt.AlignHCenter)

        # 제품명 필드
        self.product_field_widget, self.product_label, self.product_edit = self._create_readonly_field("제품명", 776)
        input_layout.addWidget(self.product_field_widget, alignment=Qt.AlignHCenter)

        # 버전/모델명 행
        self._setup_version_model_row(input_layout)

        # 시험유형/시험대상 행
        self._setup_category_target_row(input_layout)

        # 시험분야/시험범위 행
        self._setup_group_range_row(input_layout)

        input_layout.addSpacing(20)

        layout.addWidget(self.input_container, alignment=Qt.AlignHCenter)

    def _create_readonly_field(self, label_text, width):
        """읽기 전용 필드 생성"""
        field_widget = QWidget()
        field_widget.setFixedSize(width, 82)
        field_widget.setStyleSheet("QWidget { background: transparent; }")

        field_layout = QVBoxLayout(field_widget)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)

        # 라벨
        label = QLabel(label_text)
        label.setFixedSize(width, 28)
        label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        field_layout.addWidget(label)

        # 입력칸
        edit = QLineEdit()
        edit_width = 768 if width == 776 else width
        edit.setFixedSize(edit_width, 48)
        edit.setReadOnly(True)

        edit.setObjectName(f"{label_text}_edit")
        edit.setStyleSheet("""
              QLineEdit {
                  font-family: 'Noto Sans KR';
                  font-size: 18px;
                  font-weight: 400;
                  letter-spacing: -0.18px;
                  color: #000000;
                  padding: 0 24px;
                  background-color: #F3F3F3;
                  border: 1px solid #CECECE;
                  border-radius: 4px;
              }
              QLineEdit[hasText="true"] {
                  background-color: #EFEFEF;
                  border: 1px solid #6B6B6B;
              }
          """)       

        # 텍스트 변경 시 배경 이미지 변경
        def update_background():
            has_text = bool(edit.text().strip())
            edit.setProperty("hasText", "true" if has_text else "false")
            edit.style().unpolish(edit)
            edit.style().polish(edit)

        edit.textChanged.connect(update_background)
        edit.setProperty("hasText", "false")

        if width == 776:
            field_layout.addWidget(edit, alignment=Qt.AlignHCenter)
        else:
            field_layout.addWidget(edit)

        return field_widget, label, edit

    def _setup_version_model_row(self, parent_layout):
        """버전/모델명 행 설정"""
        self.version_model_row = QWidget()
        self.version_model_row.setFixedSize(776, 82)
        self.version_model_row.setStyleSheet("QWidget { background: transparent; }")
        row_layout = QHBoxLayout(self.version_model_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(20)

        self.version_field_widget, self.version_label, self.version_edit = self._create_readonly_field("버전", 378)
        row_layout.addWidget(self.version_field_widget)

        self.model_field_widget, self.model_label, self.model_edit = self._create_readonly_field("모델명", 378)
        row_layout.addWidget(self.model_field_widget)

        parent_layout.addWidget(self.version_model_row, alignment=Qt.AlignHCenter)

    def _setup_category_target_row(self, parent_layout):
        """시험유형/시험대상 행 설정"""
        self.category_target_row = QWidget()
        self.category_target_row.setFixedSize(776, 82)
        self.category_target_row.setStyleSheet("QWidget { background: transparent; }")
        row_layout = QHBoxLayout(self.category_target_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(20)

        self.test_category_widget, self.test_category_label, self.test_category_edit = self._create_readonly_field("시험유형", 378)
        row_layout.addWidget(self.test_category_widget)

        self.target_system_widget, self.target_system_label, self.target_system_edit = self._create_readonly_field("시험대상", 378)
        row_layout.addWidget(self.target_system_widget)

        parent_layout.addWidget(self.category_target_row, alignment=Qt.AlignHCenter)

    def _setup_group_range_row(self, parent_layout):
        """시험분야/시험범위 행 설정"""
        self.group_range_row = QWidget()
        self.group_range_row.setFixedSize(776, 82)
        self.group_range_row.setStyleSheet("QWidget { background: transparent; }")
        row_layout = QHBoxLayout(self.group_range_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(20)

        self.test_group_widget, self.test_group_label, self.test_group_edit = self._create_readonly_field("시험분야", 378)
        row_layout.addWidget(self.test_group_widget)

        self.test_range_widget, self.test_range_label, self.test_range_edit = self._create_readonly_field("시험범위", 378)
        row_layout.addWidget(self.test_range_widget)

        parent_layout.addWidget(self.group_range_row, alignment=Qt.AlignHCenter)

    def _setup_divider(self, layout):
        """Divider 설정"""
        self.divider = QLabel()
        self.divider_pixmap = QPixmap(resource_path("assets/image/test_info/divider.png"))
        self.divider.setPixmap(self.divider_pixmap)
        self.divider.setScaledContents(True)
        divider_height = self.divider_pixmap.height() if self.divider_pixmap.height() > 0 else 1
        self.divider.setFixedSize(776, divider_height)
        layout.addWidget(self.divider, alignment=Qt.AlignHCenter)

    def _setup_admin_code_field(self, layout):
        """관리자 코드 필드 설정"""
        self.admin_code_widget = QWidget()
        self.admin_code_widget.setFixedSize(776, 82)

        field_layout = QVBoxLayout(self.admin_code_widget)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)

        # 라벨
        self.admin_code_label = QLabel("관리자 코드 입력")
        self.admin_code_label.setFixedSize(776, 28)
        self.admin_code_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                background: transparent;
            }
        """)
        field_layout.addWidget(self.admin_code_label)

        # 입력칸 컨테이너 (placeholder 라벨 오버레이용)
        self.admin_code_input_container = QWidget()
        self.admin_code_input_container.setFixedSize(768, 48)

        self.admin_code_input = QLineEdit(self.admin_code_input_container)
        self.admin_code_input.setFixedSize(768, 48)
        self.admin_code_input.setObjectName("admin_code_input")
        self.admin_code_input.setEnabled(True)  # 기본값 활성화

        self.admin_code_input.setStyleSheet("""
              QLineEdit#admin_code_input {
                  font-family: 'Noto Sans KR';
                  font-size: 18px;
                  font-weight: 400;
                  letter-spacing: -0.18px;
                  color: #000000;
                  padding: 0 24px;
                  background-color: #FFFFFF;
                  border: 3px solid #2B96ED;
                  border-radius: 4px;
                  outline: none;
              }
              QLineEdit#admin_code_input:focus {
                  background-color: #FFFFFF;
                  border: 3px solid #2B96ED;
                  outline: none;
              }
              QLineEdit#admin_code_input:hover:enabled:!focus[hasText="false"] {
                  background-color: #E9F6FE;
                  border: 1px solid #868686;
              }
              QLineEdit#admin_code_input:disabled {
                  background-color: #F5F5F5;
                  border: 1px solid #CECECE;
              }
              QLineEdit#admin_code_input[hasText="true"] {
                  background-color: #FFFFFF;
                  border: 1px solid #6B6B6B;
              }
          """)

        # 커스텀 placeholder 라벨
        self.admin_code_placeholder = QLabel("관리자 코드를 입력해주세요", self.admin_code_input_container)
        self.admin_code_placeholder.setGeometry(24, 0, 720, 48)
        self.admin_code_placeholder.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 500;
                color: #868686;
                background: transparent;
            }
        """)
        self.admin_code_placeholder.setAlignment(Qt.AlignVCenter)
        self.admin_code_placeholder.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.admin_code_placeholder.hide()  # 기본값으로 숨김 (활성화 상태이므로)

        def update_placeholder_visibility():
            """placeholder 표시 조건: 텍스트 없음 + disabled 상태"""
            has_text = bool(self.admin_code_input.text().strip())
            is_disabled = not self.admin_code_input.isEnabled()
            has_focus = self.admin_code_input.hasFocus()

            # 텍스트가 있거나 focus를 받았으면 무조건 숨김
            if has_text or has_focus:
                self.admin_code_placeholder.hide()
            elif is_disabled:
                self.admin_code_placeholder.show()
            else:
                self.admin_code_placeholder.hide()

        def update_background():
            has_text = bool(self.admin_code_input.text().strip())
            self.admin_code_input.setProperty("hasText", "true" if has_text else "false")
            self.admin_code_input.style().unpolish(self.admin_code_input)
            self.admin_code_input.style().polish(self.admin_code_input)
            update_placeholder_visibility()

        self.admin_code_input.textChanged.connect(update_background)
        self.admin_code_input.setProperty("hasText", "false")

        # hover 이벤트 감지를 위한 이벤트 필터 설치
        self.admin_code_input.installEventFilter(self)
        self._update_placeholder_visibility = update_placeholder_visibility

        field_layout.addWidget(self.admin_code_input_container)

        # form_validator와 info_GUI 호환성을 위한 alias
        if self.parent_widget:
            self.parent_widget.admin_code_edit = self.admin_code_input

        layout.addWidget(self.admin_code_widget, alignment=Qt.AlignHCenter)

    def _setup_buttons(self, layout):
        """하단 버튼 설정"""
        self.page1_button_container = QWidget()
        self.page1_button_container.setFixedSize(776, 48)
        button_layout = QHBoxLayout(self.page1_button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(20)

        # 다음 버튼
        self.next_btn = QPushButton("다음")
        self.next_btn.setFixedSize(378, 48)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #1C5DB1;
                border: none;
                border-radius: 4px;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #3E85E2;
            }
        """)
        if self.parent_widget:
            self.next_btn.clicked.connect(self.parent_widget.go_to_next_page)
        button_layout.addWidget(self.next_btn)

        # 종료 버튼
        self.page1_exit_btn = QPushButton("종료")
        self.page1_exit_btn.setFixedSize(378, 48)
        self.page1_exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #6B6B6B;
                border-radius: 4px;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }
            QPushButton:hover {
                background-color: #EFEFEF;
            }
        """)
        if self.parent_widget:
            self.page1_exit_btn.clicked.connect(self.parent_widget.exit_btn_clicked)
        button_layout.addWidget(self.page1_exit_btn)

        layout.addWidget(self.page1_button_container, alignment=Qt.AlignHCenter)

    def _set_parent_references(self):
        """부모 위젯에 참조 설정"""
        if not self.parent_widget:
            return

        # 원본 크기 저장
        self.parent_widget.original_panel_size = (872, 843)
        self.parent_widget.original_title_size = (776, 106)
        self.parent_widget.original_title_text_size = (776, 38)
        self.parent_widget.original_title_desc_size = (776, 52)
        self.parent_widget.original_input_container_size = (776, 479)
        self.parent_widget.original_divider_size = (776, self.divider_pixmap.height() if self.divider_pixmap.height() > 0 else 1)
        self.parent_widget.original_admin_code_widget_size = (776, 82)
        self.parent_widget.original_admin_code_label_size = (776, 28)
        self.parent_widget.original_admin_code_input_container_size = (768, 48)
        self.parent_widget.original_admin_code_input_size = (768, 48)
        self.parent_widget.original_admin_code_placeholder_size = (720, 48)
        self.parent_widget.original_page1_button_container_size = (776, 48)
        self.parent_widget.original_next_btn_size = (378, 48)
        self.parent_widget.original_page1_exit_btn_size = (378, 48)

        # 필드별 원본 크기
        for prefix in ['company', 'product']:
            setattr(self.parent_widget, f'original_{prefix}_field_size', (776, 82))
            setattr(self.parent_widget, f'original_{prefix}_label_size', (776, 28))
            setattr(self.parent_widget, f'original_{prefix}_edit_size', (768, 48))

        self.parent_widget.original_version_model_row_size = (776, 82)
        for prefix in ['version', 'model']:
            setattr(self.parent_widget, f'original_{prefix}_field_size', (378, 82))
            setattr(self.parent_widget, f'original_{prefix}_label_size', (378, 28))
            setattr(self.parent_widget, f'original_{prefix}_edit_size', (378, 48))

        self.parent_widget.original_category_target_row_size = (776, 82)
        for prefix in ['test_category', 'target_system']:
            setattr(self.parent_widget, f'original_{prefix}_field_size', (378, 82))
            setattr(self.parent_widget, f'original_{prefix}_label_size', (378, 28))
            setattr(self.parent_widget, f'original_{prefix}_edit_size', (378, 48))

        self.parent_widget.original_group_range_row_size = (776, 82)
        for prefix in ['test_group', 'test_range']:
            setattr(self.parent_widget, f'original_{prefix}_field_size', (378, 82))
            setattr(self.parent_widget, f'original_{prefix}_label_size', (378, 28))
            setattr(self.parent_widget, f'original_{prefix}_edit_size', (378, 48))

        # 위젯 참조
        self.parent_widget.info_panel = self
        self.parent_widget.panel_title_container = self.panel_title_container
        self.parent_widget.panel_title_text = self.panel_title_text
        self.parent_widget.panel_title_desc = self.panel_title_desc
        self.parent_widget.input_container = self.input_container
        self.parent_widget.divider = self.divider

        # 필드 참조
        self.parent_widget.company_field_widget = self.company_field_widget
        self.parent_widget.company_label = self.company_label
        self.parent_widget.company_edit = self.company_edit

        self.parent_widget.product_field_widget = self.product_field_widget
        self.parent_widget.product_label = self.product_label
        self.parent_widget.product_edit = self.product_edit

        self.parent_widget.version_model_row = self.version_model_row
        self.parent_widget.version_field_widget = self.version_field_widget
        self.parent_widget.version_label = self.version_label
        self.parent_widget.version_edit = self.version_edit
        self.parent_widget.model_field_widget = self.model_field_widget
        self.parent_widget.model_label = self.model_label
        self.parent_widget.model_edit = self.model_edit

        self.parent_widget.category_target_row = self.category_target_row
        self.parent_widget.test_category_widget = self.test_category_widget
        self.parent_widget.test_category_label = self.test_category_label
        self.parent_widget.test_category_edit = self.test_category_edit
        self.parent_widget.target_system_widget = self.target_system_widget
        self.parent_widget.target_system_label = self.target_system_label
        self.parent_widget.target_system_edit = self.target_system_edit

        self.parent_widget.group_range_row = self.group_range_row
        self.parent_widget.test_group_widget = self.test_group_widget
        self.parent_widget.test_group_label = self.test_group_label
        self.parent_widget.test_group_edit = self.test_group_edit
        self.parent_widget.test_range_widget = self.test_range_widget
        self.parent_widget.test_range_label = self.test_range_label
        self.parent_widget.test_range_edit = self.test_range_edit

        self.parent_widget.admin_code_widget = self.admin_code_widget
        self.parent_widget.admin_code_label = self.admin_code_label
        self.parent_widget.admin_code_input_container = self.admin_code_input_container
        self.parent_widget.admin_code_input = self.admin_code_input
        self.parent_widget.admin_code_placeholder = self.admin_code_placeholder
        self.parent_widget.admin_code_edit = self.admin_code_input  # alias

        self.parent_widget.page1_button_container = self.page1_button_container
        self.parent_widget.next_btn = self.next_btn
        self.parent_widget.page1_exit_btn = self.page1_exit_btn

    def connect_signals(self):
        """시그널 연결 (부모 위젯 초기화 후 호출)"""
        if not self.parent_widget:
            return

        # 시험유형 변경 시 관리자 코드 필드 활성화/비활성화
        if hasattr(self.parent_widget, 'form_validator'):
            self.test_category_edit.textChanged.connect(self.parent_widget.form_validator.handle_test_category_change)
            self.test_range_edit.textChanged.connect(self.parent_widget.form_validator.handle_test_range_change)

        # 버튼 상태 체크
        if hasattr(self.parent_widget, 'check_start_button_state'):
            self.test_category_edit.textChanged.connect(self.parent_widget.check_start_button_state)

        if hasattr(self.parent_widget, 'check_next_button_state'):
            for field in [self.company_edit, self.product_edit, self.version_edit, self.model_edit,
                         self.test_category_edit, self.target_system_edit, self.test_group_edit,
                         self.test_range_edit, self.admin_code_input]:
                field.textChanged.connect(self.parent_widget.check_next_button_state)

        # 관리자 코드 검증
        if hasattr(self.parent_widget, 'form_validator'):
            self.admin_code_input.textChanged.connect(self.parent_widget.form_validator.validate_admin_code)
            self.admin_code_input.textChanged.connect(self.parent_widget.check_start_button_state)

    def eventFilter(self, obj, event):
        """hover/focus 이벤트 감지하여 placeholder 표시/숨김"""
        if obj == self.admin_code_input:
            if event.type() in (QEvent.Enter, QEvent.Leave, QEvent.EnabledChange,
                                QEvent.FocusIn, QEvent.FocusOut):
                if hasattr(self, '_update_placeholder_visibility'):
                    self._update_placeholder_visibility()
        return super().eventFilter(obj, event)
