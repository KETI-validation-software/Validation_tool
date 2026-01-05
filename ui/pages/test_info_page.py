"""
시험 정보 확인 페이지 (Page 1)
- 시험 기본 정보 확인 및 불러오기
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from core.functions import resource_path
from ui.sections import BasicInfoPanel
import config.CONSTANTS as CONSTANTS


def create_test_info_page(parent_widget):
    """
    시험 정보 확인 페이지 생성

    Args:
        parent_widget: InfoWidget 인스턴스 (부모 위젯)

    Returns:
        QWidget: 생성된 페이지 위젯
    """
    parent_widget.page1 = QWidget()
    parent_widget.page1.setObjectName("page1")

    # 페이지 크기 설정
    parent_widget.page1.setMinimumSize(1680, 1006)

    # 전체 레이아웃 (헤더 포함)
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    # 상단 헤더 영역
    _setup_header(main_layout)

    # 본문 영역
    _setup_content(parent_widget, main_layout)

    # 관리자시스템 주소 입력 필드
    _setup_management_url(parent_widget)

    parent_widget.page1.setLayout(main_layout)
    return parent_widget.page1


def _setup_header(main_layout):
    """상단 헤더 영역 설정"""
    header_widget = QWidget()
    header_widget.setFixedHeight(64)
    header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # 배경 이미지 설정
    header_bg_path = resource_path("assets/image/test_info/header.png").replace(chr(92), "/")
    header_widget.setStyleSheet(f"""
        QWidget {{
            border-image: url({header_bg_path}) 0 0 0 0 stretch stretch;
        }}
        QLabel {{
            border-image: none;
            background: transparent;
        }}
    """)

    # 헤더 레이아웃 (가운데 정렬)
    header_layout = QHBoxLayout(header_widget)
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(0)

    header_layout.addStretch()

    # 로고 이미지 (90x32)
    logo_label = QLabel()
    logo_pixmap = QPixmap(resource_path("assets/image/common/logo_KISA.png"))
    logo_label.setPixmap(logo_pixmap)
    logo_label.setFixedSize(90, 32)
    header_layout.addWidget(logo_label)

    header_layout.addSpacing(20)

    # 타이틀 이미지 (269x30)
    header_title_label = QLabel()
    header_title_pixmap = QPixmap(resource_path("assets/image/test_info/header_title.png"))
    header_title_label.setPixmap(header_title_pixmap)
    header_title_label.setFixedSize(269, 30)
    header_layout.addWidget(header_title_label)

    header_layout.addStretch()

    main_layout.addWidget(header_widget)


def _setup_content(parent_widget, main_layout):
    """본문 영역 설정"""
    parent_widget.page1_content = QWidget()
    parent_widget.page1_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # 배경 이미지
    bg_path = resource_path("assets/image/test_info/bg-illust.png").replace(chr(92), "/")
    parent_widget.page1_bg_label = QLabel(parent_widget.page1_content)
    parent_widget.page1_bg_label.setPixmap(QPixmap(bg_path))
    parent_widget.page1_bg_label.setScaledContents(True)
    parent_widget.page1_bg_label.lower()

    content_layout = QVBoxLayout(parent_widget.page1_content)
    content_layout.setContentsMargins(32, 0, 56, 0)
    content_layout.setSpacing(0)

    # 원본 크기 저장 (비율 계산용)
    parent_widget.original_window_size = (1680, 1006)
    parent_widget.original_panel_size = (872, 843)

    # BasicInfoPanel 섹션 사용
    parent_widget.info_panel = BasicInfoPanel(parent_widget)
    parent_widget.info_panel.connect_signals()
    content_layout.addWidget(parent_widget.info_panel, alignment=Qt.AlignHCenter)

    # IP 입력창
    _setup_ip_input(parent_widget)

    # 불러오기 버튼
    _setup_load_button(parent_widget)

    main_layout.addWidget(parent_widget.page1_content, 1)


def _setup_ip_input(parent_widget):
    """IP 입력창 설정"""
    parent_widget.ip_input_edit = QLineEdit(parent_widget.page1_content)
    parent_widget.ip_input_edit.setFixedSize(200, 40)
    parent_widget.ip_input_edit.setPlaceholderText("주소를 입력해주세요.")
    parent_widget.ip_input_edit.setGeometry(1269, 24, 200, 40)
    parent_widget.ip_input_edit.setStyleSheet("""
        QLineEdit {
            font-family: 'Noto Sans KR';
            font-size: 14px;
            padding: 8px 12px;
            border: 1px solid #CECECE;
            border-radius: 4px;
            background-color: white;
            background: white;
        }
        QLineEdit:focus {
            border: 1px solid #4A90E2;
            background-color: white;
        }
    """)


def _setup_load_button(parent_widget):
    """불러오기 버튼 설정"""
    parent_widget.load_test_info_btn = QPushButton(parent_widget.page1_content)
    parent_widget.load_test_info_btn.setFixedSize(198, 62)
    parent_widget.load_test_info_btn.setGeometry(1477, 13, 198, 62)

    btn_enabled = resource_path("assets/image/test_info/btn_불러오기_enabled.png").replace(chr(92), "/")
    btn_hover = resource_path("assets/image/test_info/btn_불러오기_Hover.png").replace(chr(92), "/")

    parent_widget.load_test_info_btn.setStyleSheet(f"""
        QPushButton {{
            border: none;
            background-image: url({btn_enabled});
            background-repeat: no-repeat;
            background-position: center;
        }}
        QPushButton:hover {{
            background-image: url({btn_hover});
        }}
    """)
    parent_widget.load_test_info_btn.clicked.connect(parent_widget.on_load_test_info_clicked)


def _setup_management_url(parent_widget):
    """관리자시스템 주소 입력 필드 설정"""
    parent_widget.management_url_container = QWidget(parent_widget.page1)
    parent_widget.management_url_container.setFixedSize(380, 60)
    parent_widget.management_url_container.setGeometry(1290, 898, 380, 60)
    parent_widget.management_url_container.setStyleSheet("""
        QWidget {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 4px;
            border: 1px solid #E8E8E8;
        }
    """)

    management_url_layout = QHBoxLayout(parent_widget.management_url_container)
    management_url_layout.setContentsMargins(12, 10, 12, 10)
    management_url_layout.setSpacing(8)

    # 라벨
    management_url_label = QLabel("관리자시스템 주소:")
    management_url_label.setStyleSheet("""
        QLabel {
            font-family: 'Noto Sans KR';
            font-size: 13px;
            font-weight: 400;
            color: #333;
            background-color: transparent;
            border: none;
        }
    """)
    management_url_label.setFixedWidth(130)
    management_url_layout.addWidget(management_url_label)

    # 입력 필드
    parent_widget.management_url_edit = QLineEdit()
    parent_widget.management_url_edit.setText(CONSTANTS.management_url)
    parent_widget.management_url_edit.setPlaceholderText("http://ect2.iptime.org:20223")
    parent_widget.management_url_edit.setStyleSheet("""
        QLineEdit {
            font-family: 'Noto Sans KR';
            font-size: 13px;
            padding: 6px 10px;
            border: 1px solid #CECECE;
            border-radius: 3px;
            background-color: #FFFFFF;
        }
        QLineEdit:focus {
            border: 1px solid #4A90E2;
        }
    """)
    parent_widget.management_url_edit.textChanged.connect(parent_widget.on_management_url_changed)
    management_url_layout.addWidget(parent_widget.management_url_edit)

    parent_widget.management_url_container.raise_()
