"""
시험 설정 페이지 (Page 2)
- 시험 분야별 시나리오, 시험 API, 인증 방식, 접속 주소 설정
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from core.functions import resource_path
from ui.sections import (
    TestFieldSection, TestApiSection,
    AuthSection, ConnectionSection
)


def create_test_config_page(parent_widget):
    """
    시험 설정 페이지 생성

    Args:
        parent_widget: InfoWidget 인스턴스 (부모 위젯)

    Returns:
        QWidget: 생성된 페이지 위젯
    """
    parent_widget.page2 = QWidget()
    parent_widget.page2.setObjectName("page2")
    parent_widget.page2.setMinimumSize(1680, 1006)

    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    # 상단 헤더 영역
    _setup_header(main_layout)

    # 본문 영역
    _setup_content(parent_widget, main_layout)

    parent_widget.page2.setLayout(main_layout)
    return parent_widget.page2


def _setup_header(main_layout):
    """상단 헤더 영역 설정"""
    header_widget = QWidget()
    header_widget.setFixedHeight(64)
    header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    header_bg_path = resource_path("assets/image/common/header.png").replace(chr(92), "/")
    header_widget.setStyleSheet(f"""
        QWidget {{
            border-image: url({header_bg_path}) 0 0 0 0 stretch stretch;
        }}
        QLabel {{
            border-image: none;
            background: transparent;
        }}
    """)

    header_layout = QHBoxLayout(header_widget)
    header_layout.setContentsMargins(48, 10, 48, 10)
    header_layout.setSpacing(0)

    # 로고 이미지
    logo_label = QLabel()
    logo_pixmap = QPixmap(resource_path("assets/image/common/logo_KISA.png"))
    logo_label.setPixmap(logo_pixmap)
    logo_label.setFixedSize(90, 32)
    header_layout.addWidget(logo_label)

    header_layout.addSpacing(20)

    # 타이틀 이미지
    header_title_label = QLabel()
    header_title_pixmap = QPixmap(resource_path("assets/image/test_config/config_title.png"))
    header_title_label.setPixmap(header_title_pixmap.scaled(458, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    header_title_label.setFixedSize(458, 36)
    header_layout.addWidget(header_title_label)

    header_layout.addStretch()

    main_layout.addWidget(header_widget)


def _setup_content(parent_widget, main_layout):
    """본문 영역 설정"""
    parent_widget.page2_content = QWidget()
    parent_widget.page2_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    parent_widget.page2_content.setObjectName("content_widget_page2")

    # 배경 이미지
    bg_path2 = resource_path("assets/image/test_config/시험정보설정_main.png").replace(chr(92), "/")
    parent_widget.page2_bg_label = QLabel(parent_widget.page2_content)
    parent_widget.page2_bg_label.setPixmap(QPixmap(bg_path2))
    parent_widget.page2_bg_label.setScaledContents(True)
    parent_widget.page2_bg_label.lower()

    content_layout = QVBoxLayout(parent_widget.page2_content)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(0)

    # bg_root 컨테이너
    _setup_bg_root(parent_widget, content_layout)

    main_layout.addWidget(parent_widget.page2_content, 1)


def _setup_bg_root(parent_widget, content_layout):
    """bg_root 컨테이너 설정"""
    parent_widget.bg_root = QWidget()
    parent_widget.bg_root.setFixedSize(1680, 897)
    parent_widget.original_bg_root_size = (1680, 897)
    parent_widget.bg_root.setStyleSheet("background: transparent;")

    bg_root_layout = QVBoxLayout(parent_widget.bg_root)
    bg_root_layout.setContentsMargins(0, 36, 0, 44)
    bg_root_layout.setSpacing(0)

    # 타이틀 컨테이너
    _setup_title_container(parent_widget, bg_root_layout)

    bg_root_layout.addSpacing(8)

    # 패널 컨테이너
    _setup_panels_container(parent_widget, bg_root_layout)

    content_layout.addWidget(parent_widget.bg_root, 0, Qt.AlignHCenter | Qt.AlignTop)


def _setup_title_container(parent_widget, bg_root_layout):
    """타이틀 컨테이너 설정"""
    parent_widget.page2_title_container = QWidget()
    parent_widget.page2_title_container.setFixedSize(1680, 52)
    parent_widget.original_page2_title_container_size = (1680, 52)
    parent_widget.page2_title_container.setStyleSheet("background: transparent;")

    title_container_layout = QHBoxLayout(parent_widget.page2_title_container)
    title_container_layout.setContentsMargins(0, 0, 0, 0)
    title_container_layout.setSpacing(0)

    title_container_layout.addStretch()

    # 타이틀 배경
    parent_widget.page2_title_bg = QWidget()
    parent_widget.page2_title_bg.setFixedSize(1584, 52)
    parent_widget.original_page2_title_bg_size = (1584, 52)
    parent_widget.page2_title_bg.setObjectName("page2_title_bg")

    title_bg_path = resource_path("assets/image/test_config/시험정보설정_title.png").replace(chr(92), "/")
    parent_widget.page2_title_bg.setStyleSheet(f"""
        QWidget#page2_title_bg {{
            border-image: url({title_bg_path}) 0 0 0 0 stretch stretch;
        }}
    """)

    title_inner_layout = QHBoxLayout(parent_widget.page2_title_bg)
    title_inner_layout.setContentsMargins(14, 12, 48, 12)
    title_inner_layout.setSpacing(0)

    # 아이콘
    parent_widget.page2_title_icon = QLabel()
    parent_widget.page2_title_icon.setFixedSize(18, 18)
    icon_path = resource_path("assets/image/icon/icn_notification.png")
    parent_widget.page2_title_icon.setPixmap(QPixmap(icon_path).scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    title_inner_layout.addWidget(parent_widget.page2_title_icon)

    title_inner_layout.addSpacing(13)

    # 텍스트
    parent_widget.page2_title_text = QLabel("시험 분야별로 시나리오를 확인하고 시험 환경을 설정하세요.")
    parent_widget.page2_title_text.setStyleSheet("""
        QLabel {
            font-family: 'Noto Sans KR';
            font-size: 19px;
            font-weight: 400;
            color: #000000;
            background: transparent;
        }
    """)
    title_inner_layout.addWidget(parent_widget.page2_title_text)
    title_inner_layout.addStretch()

    title_container_layout.addWidget(parent_widget.page2_title_bg)
    title_container_layout.addStretch()

    bg_root_layout.addWidget(parent_widget.page2_title_container, 0, Qt.AlignTop | Qt.AlignHCenter)


def _setup_panels_container(parent_widget, bg_root_layout):
    """패널 컨테이너 설정"""
    parent_widget.panels_container = QWidget()
    parent_widget.panels_container.setFixedSize(1584, 802)
    parent_widget.original_panels_container_size = (1584, 802)

    panels_layout = QHBoxLayout(parent_widget.panels_container)
    panels_layout.setContentsMargins(0, 0, 0, 0)
    panels_layout.setSpacing(0)

    # 좌측 패널
    _setup_left_panel(parent_widget, panels_layout)

    # 우측 패널
    _setup_right_panel(parent_widget, panels_layout)

    bg_root_layout.addWidget(parent_widget.panels_container, 1, Qt.AlignTop | Qt.AlignHCenter)


def _setup_left_panel(parent_widget, panels_layout):
    """좌측 패널 설정 (시험 분야별 시나리오 + 시험 API)"""
    parent_widget.left_panel = QGroupBox()
    parent_widget.left_panel.setFixedSize(792, 802)
    parent_widget.original_left_panel_size = (792, 802)
    parent_widget.left_panel.setObjectName("left_panel")

    left_bg_path = resource_path("assets/image/test_config/left_title_sub.png").replace(chr(92), "/")
    parent_widget.left_panel.setStyleSheet(f"""
        QGroupBox#left_panel {{
            border: none;
            margin: 0px;
            padding: 0px;
            margin-top: 0px;
            padding-top: 0px;
            border-image: url({left_bg_path}) 0 0 0 0 stretch stretch;
        }}
    """)

    left_layout = QVBoxLayout()
    left_layout.setContentsMargins(24, 12, 24, 80)
    left_layout.setSpacing(0)

    # 시험 분야별 시나리오 타이틀
    parent_widget.field_scenario_title = QLabel("시험 분야별 시나리오")
    parent_widget.field_scenario_title.setFixedSize(744, 24)
    parent_widget.original_field_scenario_title_size = (744, 24)
    parent_widget.field_scenario_title.setStyleSheet("""
        QLabel {
            font-family: 'Noto Sans KR';
            font-size: 20px;
            font-weight: 500;
            color: #000000;
            background: transparent;
        }
    """)
    left_layout.addWidget(parent_widget.field_scenario_title)

    left_layout.addSpacing(8)

    # TestFieldSection
    parent_widget.field_group = TestFieldSection(parent_widget)
    parent_widget.original_field_group_size = (744, 240)
    left_layout.addWidget(parent_widget.field_group)

    left_layout.addSpacing(16)

    # 시험 API 타이틀
    parent_widget.api_title = QLabel("시험 API")
    parent_widget.api_title.setFixedSize(744, 38)
    parent_widget.original_api_title_size = (744, 38)
    parent_widget.api_title.setStyleSheet("""
        QLabel {
            font-family: 'Noto Sans KR';
            font-size: 20px;
            font-weight: 500;
            color: #000000;
            background: transparent;
        }
    """)
    left_layout.addWidget(parent_widget.api_title)

    left_layout.addSpacing(8)

    # TestApiSection
    parent_widget.api_group = TestApiSection(parent_widget)
    parent_widget.original_api_group_size = (744, 376)
    left_layout.addWidget(parent_widget.api_group)

    parent_widget.left_panel.setLayout(left_layout)
    panels_layout.addWidget(parent_widget.left_panel, 0, Qt.AlignTop)


def _setup_right_panel(parent_widget, panels_layout):
    """우측 패널 설정 (인증 방식 + 접속 주소)"""
    parent_widget.right_panel = QGroupBox()
    parent_widget.right_panel.setFixedSize(792, 802)
    parent_widget.original_right_panel_size = (792, 802)
    parent_widget.right_panel.setStyleSheet("QGroupBox { border: none; margin: 0px; padding: 0px; margin-top: 0px; padding-top: 0px; background: transparent; }")

    right_layout = QVBoxLayout()
    right_layout.setContentsMargins(24, 12, 24, 0)
    right_layout.setSpacing(0)

    # 사용자 인증 방식 타이틀
    parent_widget.auth_title_widget = QLabel("사용자 인증 방식")
    parent_widget.auth_title_widget.setFixedSize(744, 24)
    parent_widget.original_auth_title_size = (744, 24)
    parent_widget.auth_title_widget.setStyleSheet("""
        QLabel {
            font-family: 'Noto Sans KR';
            font-size: 20px;
            font-weight: 500;
            color: #000000;
            background: transparent;
        }
    """)
    right_layout.addWidget(parent_widget.auth_title_widget)

    right_layout.addSpacing(8)

    # AuthSection
    parent_widget.auth_section_widget = AuthSection(parent_widget)
    parent_widget.original_auth_section_widget_size = (744, 240)
    right_layout.addWidget(parent_widget.auth_section_widget)

    right_layout.addSpacing(16)

    # 접속 주소 탐색 타이틀 행
    _setup_connection_title_row(parent_widget, right_layout)

    # 주소 추가 팝오버
    _setup_address_popover(parent_widget)

    right_layout.addSpacing(8)

    # ConnectionSection
    parent_widget.connection_section_widget = ConnectionSection(parent_widget)
    parent_widget.original_connection_section_widget_size = (744, 376)
    right_layout.addWidget(parent_widget.connection_section_widget)

    right_layout.addSpacing(32)

    # 하단 버튼
    _setup_bottom_buttons(parent_widget, right_layout)

    parent_widget.right_panel.setLayout(right_layout)
    panels_layout.addWidget(parent_widget.right_panel, 0, Qt.AlignTop)


def _setup_connection_title_row(parent_widget, right_layout):
    """접속 주소 탐색 타이틀 행 설정"""
    parent_widget.connection_title_row = QWidget()
    parent_widget.connection_title_row.setFixedSize(744, 38)
    parent_widget.original_connection_title_row_size = (744, 38)

    connection_title_layout = QHBoxLayout()
    connection_title_layout.setContentsMargins(0, 0, 0, 0)
    connection_title_layout.setSpacing(0)

    connection_title_widget = QLabel("접속 주소 탐색")
    connection_title_widget.setFixedHeight(38)
    connection_title_widget.setStyleSheet("""
        QLabel {
            font-family: 'Noto Sans KR';
            font-size: 20px;
            font-weight: 500;
            color: #000000;
            background: transparent;
        }
    """)
    connection_title_layout.addWidget(connection_title_widget)

    connection_title_layout.addStretch()

    # 버튼 그룹
    buttons_widget = QWidget()
    buttons_widget.setFixedHeight(38)
    buttons_layout = QHBoxLayout()
    buttons_layout.setContentsMargins(0, 0, 0, 0)
    buttons_layout.setSpacing(16)

    # 주소탐색 버튼
    parent_widget.scan_btn = QPushButton("")
    scan_btn = parent_widget.scan_btn
    scan_btn.setFixedSize(120, 38)
    scan_btn.setFocusPolicy(Qt.NoFocus)

    btn_scan_enabled = resource_path("assets/image/test_config/btn_주소탐색_enabled.png").replace(chr(92), "/")
    btn_scan_hover = resource_path("assets/image/test_config/btn_주소탐색_Hover.png").replace(chr(92), "/")

    scan_btn.setStyleSheet(f"""
        QPushButton {{
            border: none;
            background-image: url({btn_scan_enabled});
            background-repeat: no-repeat;
            background-position: center;
        }}
        QPushButton:hover {{
            background-image: url({btn_scan_hover});
        }}
    """)
    scan_btn.clicked.connect(parent_widget.start_scan)
    buttons_layout.addWidget(scan_btn)

    # 추가 버튼
    parent_widget.add_btn = QPushButton("")
    parent_widget.add_btn.setFixedSize(90, 38)
    parent_widget.add_btn.setCheckable(True)

    btn_add_enabled = resource_path("assets/image/test_config/btn_추가_enabled.png").replace(chr(92), "/")
    btn_add_hover = resource_path("assets/image/test_config/btn_추가_Hover.png").replace(chr(92), "/")
    btn_add_selected = resource_path("assets/image/test_config/btn_추가_selected.png").replace(chr(92), "/")

    parent_widget.add_btn.setStyleSheet(f"""
        QPushButton {{
            border: none;
            background-image: url({btn_add_enabled});
            background-repeat: no-repeat;
            background-position: center;
        }}
        QPushButton:hover {{
            background-image: url({btn_add_hover});
        }}
        QPushButton:checked {{
            background-image: url({btn_add_selected});
        }}
        QPushButton:checked:hover {{
            background-image: url({btn_add_selected});
        }}
    """)
    parent_widget.add_btn.clicked.connect(parent_widget.toggle_address_popover)
    buttons_layout.addWidget(parent_widget.add_btn)

    buttons_widget.setLayout(buttons_layout)
    connection_title_layout.addWidget(buttons_widget)
    parent_widget.connection_title_row.setLayout(connection_title_layout)
    right_layout.addWidget(parent_widget.connection_title_row)


def _setup_address_popover(parent_widget):
    """주소 추가 팝오버 설정"""
    parent_widget.address_popover = QWidget()
    parent_widget.address_popover.setFixedSize(392, 102)
    parent_widget.address_popover.setStyleSheet("""
        QWidget {
            background-color: #FFFFFF;
            border: 1px solid #CECECE;
            border-radius: 12px;
        }
    """)

    popover_shadow = QGraphicsDropShadowEffect()
    popover_shadow.setBlurRadius(5)
    popover_shadow.setXOffset(0)
    popover_shadow.setYOffset(0)
    popover_shadow.setColor(QColor(107, 107, 107, 204))
    parent_widget.address_popover.setGraphicsEffect(popover_shadow)

    popover_layout = QVBoxLayout()
    popover_layout.setContentsMargins(16, 16, 16, 16)
    popover_layout.setSpacing(0)

    popover_title = QLabel("주소 추가")
    popover_title.setFixedSize(358, 26)
    popover_title.setStyleSheet("""
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
    popover_layout.addWidget(popover_title)

    popover_layout.addSpacing(4)

    input_row_layout = QHBoxLayout()
    input_row_layout.setContentsMargins(0, 0, 0, 0)
    input_row_layout.setSpacing(6)

    parent_widget.address_input = QLineEdit()
    parent_widget.address_input.setFixedSize(287, 40)
    parent_widget.address_input.setPlaceholderText("추가할 주소를 입력해주세요")
    parent_widget.address_input.setStyleSheet("""
        QLineEdit {
            padding-left: 24px;
            padding-right: 24px;
            border: 1px solid #868686;
            border-radius: 4px;
            background-color: #FFFFFF;
            font-family: 'Noto Sans KR';
            font-weight: 500;
            font-size: 18px;
            letter-spacing: -0.18px;
            color: #000000;
        }
        QLineEdit::placeholder {
            color: #868686;
            font-size: 18px;
            font-weight: 500;
        }
    """)
    input_row_layout.addWidget(parent_widget.address_input)

    popover_add_btn = QPushButton("")
    popover_add_btn.setFixedSize(65, 40)

    btn_add_img = resource_path("assets/image/test_config/btn_추가.png").replace(chr(92), "/")
    popover_add_btn.setStyleSheet(f"""
        QPushButton {{
            border: none;
            border-radius: 4px;
            background-image: url({btn_add_img});
            background-repeat: no-repeat;
            background-position: center;
        }}
    """)
    popover_add_btn.clicked.connect(parent_widget.add_address_from_popover)
    input_row_layout.addWidget(popover_add_btn)

    popover_layout.addLayout(input_row_layout)
    parent_widget.address_popover.setLayout(popover_layout)

    parent_widget.address_popover.setParent(parent_widget)
    parent_widget.address_popover.hide()


def _setup_bottom_buttons(parent_widget, right_layout):
    """하단 버튼 설정"""
    parent_widget.button_container = QWidget()
    parent_widget.button_container.setFixedSize(744, 48)
    parent_widget.original_button_container_size = (744, 48)

    button_layout = QHBoxLayout(parent_widget.button_container)
    button_layout.setContentsMargins(0, 0, 0, 0)
    button_layout.setSpacing(16)

    # 시험 시작 버튼
    parent_widget.start_btn = QPushButton("시험 시작")
    parent_widget.start_btn.setFixedSize(364, 48)
    parent_widget.original_start_btn_size = (364, 48)
    parent_widget.start_btn.setFocusPolicy(Qt.NoFocus)

    parent_widget.start_btn.setStyleSheet("""
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
    parent_widget.start_btn.clicked.connect(parent_widget.start_test)
    parent_widget.start_btn.setEnabled(True)
    button_layout.addWidget(parent_widget.start_btn)

    # 종료 버튼
    parent_widget.exit_btn = QPushButton("종료")
    parent_widget.exit_btn.setFixedSize(364, 48)
    parent_widget.original_exit_btn_size = (364, 48)
    parent_widget.exit_btn.setFocusPolicy(Qt.NoFocus)
    parent_widget.exit_btn.setStyleSheet("""
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
    parent_widget.exit_btn.clicked.connect(parent_widget.exit_btn_clicked)
    button_layout.addWidget(parent_widget.exit_btn)

    right_layout.addWidget(parent_widget.button_container)
