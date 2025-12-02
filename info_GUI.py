from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem,
    QStackedWidget, QRadioButton, QFrame, QApplication, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QFont, QBrush, QPainter, QPen
import importlib
import re
from core.functions import resource_path

# 분리된 모듈들 import
from network_scanner import NetworkScanWorker, ARPScanWorker
from form_validator import FormValidator, ClickableLabel
import config.CONSTANTS as CONSTANTS
from splash_screen import LoadingPopup


class TestFieldTableWidget(QTableWidget):
    """시험 분야별 시나리오 테이블 - 세로 구분선이 전체 높이까지 표시되는 커스텀 테이블"""

    def __init__(self, rows, columns):
        super().__init__(rows, columns)

    def paintEvent(self, event):
        """기본 paintEvent 실행 후 세로 구분선 추가"""
        # 기본 테이블 그리기
        super().paintEvent(event)

        # 세로 구분선 그리기
        painter = QPainter(self.viewport())
        pen = QPen(QColor("#CCCCCC"))
        pen.setWidth(1)
        painter.setPen(pen)

        # 첫 번째 컬럼과 두 번째 컬럼 사이의 세로선
        # 첫 번째 컬럼 너비: 372px
        x_position = 372

        # 헤더 높이만큼 아래부터 viewport 끝까지 선 그리기
        header_height = self.horizontalHeader().height()
        viewport_height = self.viewport().height()

        painter.drawLine(x_position, 0, x_position, viewport_height)

        painter.end()


class InfoWidget(QWidget):
    """
    접속 후 화면 GUI.
    - 시험 기본/입력 정보, 인증 선택, 주소 탐색, OPT 로드 등
    """
    startTestRequested = pyqtSignal(str, str, str)  # (test_group_name, verification_type, spec_id) 전달

    def __init__(self):
        super().__init__()
        self.form_validator = FormValidator(self)  # 폼 검증 모듈 초기화
        self.scan_thread = None
        self.scan_worker = None
        self.current_mode = None
        self.target_system = ""  # 시험대상 시스템 (물리보안시스템/통합플랫폼시스템)
        self.test_group_name = None  # testGroup.name 저장
        self.test_specs = []  # testSpecs 리스트 저장
        self.current_page = 0
        self.stacked_widget = QStackedWidget()
        self.original_test_category = None  # API에서 받아온 원래 test_category 값 보관
        self.original_test_range = None  # API에서 받아온 원래 test_range 값 보관
        self.initUI()

    def initUI(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout()

        # 스택 위젯에 페이지 추가
        self.stacked_widget.addWidget(self.create_page1())  # 시험 정보 확인
        self.stacked_widget.addWidget(self.create_page2())  # 시험 설정

        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """창 크기 변경 시 page1, page2 요소들 위치 재조정"""
        super().resizeEvent(event)

        # page1의 요소들 위치 재조정
        if hasattr(self, 'page1') and self.page1:
            page_width = self.page1.width()
            page_height = self.page1.height()

            # content_widget 크기 (ip_input_edit, load_test_info_btn의 부모)
            if hasattr(self, 'page1_content') and self.page1_content:
                content_width = self.page1_content.width()
                content_height = self.page1_content.height()

                # 배경 이미지 크기 조정
                if hasattr(self, 'page1_bg_label'):
                    self.page1_bg_label.setGeometry(0, 0, content_width, content_height)

                # ip_input_edit: 오른쪽에서 211px, 위에서 24px (content_widget 기준)
                if hasattr(self, 'ip_input_edit'):
                    self.ip_input_edit.setGeometry(content_width - 211 - 200, 24, 200, 40)

                # load_test_info_btn: 오른쪽에서 5px, 위에서 13px (content_widget 기준)
                if hasattr(self, 'load_test_info_btn'):
                    self.load_test_info_btn.setGeometry(content_width - 5 - 198, 13, 198, 62)

            # management_url_container: 오른쪽에서 10px, 아래에서 48px (page1 기준)
            if hasattr(self, 'management_url_container'):
                self.management_url_container.setGeometry(page_width - 10 - 380, page_height - 48 - 60, 380, 60)

        # page2의 배경 이미지 크기 재조정
        if hasattr(self, 'page2_content') and self.page2_content:
            content_width = self.page2_content.width()
            content_height = self.page2_content.height()

            # 배경 이미지 크기 조정
            if hasattr(self, 'page2_bg_label'):
                self.page2_bg_label.setGeometry(0, 0, content_width, content_height)

    def create_page1(self):
        """첫 번째 페이지: 시험 정보 확인"""
        self.page1 = QWidget()
        self.page1.setObjectName("page1")

        # 페이지 크기 설정
        self.page1.setMinimumSize(1680, 1006)  # 반응형: 최소 크기 설정

        # 전체 레이아웃 (헤더 포함)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단 헤더 영역 (반응형 - 배경 늘어남, 로고/타이틀 가운데 고정)
        header_widget = QWidget()
        header_widget.setFixedHeight(64)
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 배경 이미지 설정 (늘어남 - border-image 사용)
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

        # 왼쪽 stretch (가운데 정렬용)
        header_layout.addStretch()

        # 로고 이미지 (90x32)
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("assets/image/test_info/logo_KISA.png"))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setFixedSize(90, 32)
        header_layout.addWidget(logo_label)

        # 로고와 타이틀 사이 간격 20px
        header_layout.addSpacing(20)

        # 타이틀 이미지 (269x30)
        header_title_label = QLabel()
        header_title_pixmap = QPixmap(resource_path("assets/image/test_info/header_title.png"))
        header_title_label.setPixmap(header_title_pixmap)
        header_title_label.setFixedSize(269, 30)
        header_layout.addWidget(header_title_label)

        # 오른쪽 stretch (가운데 정렬용)
        header_layout.addStretch()

        main_layout.addWidget(header_widget)

        # 본문 영역 컨테이너 (1680x942px, padding: 32/56/0/0)
        self.page1_content = QWidget()
        self.page1_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 배경 이미지를 QLabel로 설정 (절대 위치)
        bg_path = resource_path("assets/image/test_info/bg-illust.png").replace(chr(92), "/")
        self.page1_bg_label = QLabel(self.page1_content)
        self.page1_bg_label.setPixmap(QPixmap(bg_path))
        self.page1_bg_label.setScaledContents(True)
        self.page1_bg_label.lower()  # 맨 뒤로 보내기

        content_layout = QVBoxLayout(self.page1_content)
        content_layout.setContentsMargins(32, 0, 56, 0)  # left: 32, top: 0, right: 56, bottom: 0
        content_layout.setSpacing(0)

        # 시험 기본 정보 (수평 중앙 정렬)
        info_panel = self.create_basic_info_panel()
        content_layout.addWidget(info_panel, alignment=Qt.AlignHCenter)

        # IP 입력창 (content_widget에 절대 위치로 배치 - 오른쪽 상단)
        self.ip_input_edit = QLineEdit(self.page1_content)
        self.ip_input_edit.setFixedSize(200, 40)
        self.ip_input_edit.setPlaceholderText("주소를 입력해주세요.")
        self.ip_input_edit.setGeometry(1269, 24, 200, 40)  # x: 1680-5(우측여백)-200-8-198, y: 24
        self.ip_input_edit.setStyleSheet("""
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

        # 불러오기 버튼 (content_widget에 절대 위치로 배치 - 오른쪽 상단)
        self.load_test_info_btn = QPushButton(self.page1_content)
        self.load_test_info_btn.setFixedSize(198, 62)
        self.load_test_info_btn.setGeometry(1477, 13, 198, 62)  # x: 1680-5(우측여백)-198, y: 13

        btn_enabled = resource_path("assets/image/test_info/btn_불러오기_enabled.png").replace(chr(92), "/")
        btn_hover = resource_path("assets/image/test_info/btn_불러오기_Hover.png").replace(chr(92), "/")

        self.load_test_info_btn.setStyleSheet(f"""
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
        self.load_test_info_btn.clicked.connect(self.on_load_test_info_clicked)

        main_layout.addWidget(self.page1_content, 1)  # 반응형: stretch=1로 남은 공간 채움
        self.page1.setLayout(main_layout)

        # 관리자시스템 주소 입력 필드
        self.management_url_container = QWidget(self.page1)
        self.management_url_container.setFixedSize(380, 60)  # 라벨 텍스트가 잘 보이도록 증가
        # 오른쪽 끝으로 배치: x = 1680 - 10 - 380, y = 1006 - 60 - 48
        self.management_url_container.setGeometry(1290, 898, 380, 60)
        self.management_url_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 4px;
                border: 1px solid #E8E8E8;
            }
        """)

        management_url_layout = QHBoxLayout(self.management_url_container)
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
        management_url_label.setFixedWidth(130)  # 텍스트가 잘리지 않도록 증가
        management_url_layout.addWidget(management_url_label)

        # 입력 필드
        self.management_url_edit = QLineEdit()
        self.management_url_edit.setText(CONSTANTS.management_url)  # 초기값 설정
        self.management_url_edit.setPlaceholderText("http://ect2.iptime.org:20223")
        self.management_url_edit.setStyleSheet("""
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
        self.management_url_edit.textChanged.connect(self.on_management_url_changed)
        management_url_layout.addWidget(self.management_url_edit)

        # 관리자시스템 주소 컨테이너를 위로 올림
        self.management_url_container.raise_()

        return self.page1

    def create_page2(self):
        """두 번째 페이지: 시험 설정"""
        self.page2 = QWidget()
        self.page2.setObjectName("page2")

        # 페이지 크기 설정 (반응형: 최소 크기만 설정)
        self.page2.setMinimumSize(1680, 1006)

        # 전체 레이아웃 (헤더 포함)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단 헤더 영역 (반응형 - 배경 늘어남, 로고/타이틀 좌측 정렬)
        header_widget = QWidget()
        header_widget.setFixedHeight(64)
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 배경 이미지 설정 (늘어남 - border-image 사용)
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

        # 헤더 레이아웃 (좌측 정렬, padding: 좌우 48px, 상하 10px)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(48, 10, 48, 10)
        header_layout.setSpacing(0)

        # 로고 이미지 (90x32)
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("assets/image/common/logo_KISA.png"))
        logo_label.setPixmap(logo_pixmap)
        logo_label.setFixedSize(90, 32)
        header_layout.addWidget(logo_label)

        # 로고와 타이틀 사이 간격 20px
        header_layout.addSpacing(20)

        # 타이틀 이미지 (458x36)
        header_title_label = QLabel()
        header_title_pixmap = QPixmap(resource_path("assets/image/test_config/config_title.png"))
        header_title_label.setPixmap(header_title_pixmap.scaled(458, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_title_label.setFixedSize(458, 36)
        header_layout.addWidget(header_title_label)

        # 오른쪽 stretch (나머지 공간 채우기)
        header_layout.addStretch()

        main_layout.addWidget(header_widget)

        # 본문 영역 컨테이너 (반응형 - 가로세로 확장)
        self.page2_content = QWidget()
        self.page2_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.page2_content.setObjectName("content_widget_page2")

        # 배경 이미지를 QLabel로 설정 (절대 위치, 반응형으로 늘어남)
        bg_path2 = resource_path("assets/image/test_config/시험정보설정_main.png").replace(chr(92), "/")
        self.page2_bg_label = QLabel(self.page2_content)
        self.page2_bg_label.setPixmap(QPixmap(bg_path2))
        self.page2_bg_label.setScaledContents(True)
        self.page2_bg_label.lower()  # 맨 뒤로 보내기

        # content_layout: page2_content에 설정 (가운데 정렬용)
        content_layout = QVBoxLayout(self.page2_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 내부 콘텐츠 컨테이너 (bg_root) - 고정 크기, 가운데 정렬됨
        bg_root = QWidget()
        bg_root.setFixedSize(1680, 897)  # 타이틀(47) + 간격(8) + 패널(802) + padding(상36+하4)
        bg_root.setStyleSheet("background: transparent;")

        # bg_root 내부 레이아웃
        bg_root_layout = QVBoxLayout(bg_root)
        bg_root_layout.setContentsMargins(0, 36, 0, 4)  # 좌, 상(padding36), 우, 하
        bg_root_layout.setSpacing(0)

        # 타이틀 이미지 (1680x47px, 고정 크기)
        title_label = QLabel()
        title_label.setFixedSize(1680, 47)
        title_label.setContentsMargins(0, 0, 0, 0)
        title_label.setStyleSheet("QLabel { margin: 0px; padding: 0px; border: none; background: transparent; }")

        # 타이틀 이미지 설정
        title_pixmap = QPixmap(resource_path("assets/image/test_config/시험정보설정_title.png"))
        title_label.setPixmap(title_pixmap.scaled(1680, 47, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        title_label.setScaledContents(True)
        bg_root_layout.addWidget(title_label, 0, Qt.AlignTop)

        # 타이틀과 콘텐츠 사이 간격
        bg_root_layout.addSpacing(8)

        # 기존 콘텐츠 (좌우 패널) - 좌우 48px padding
        panels_layout = QHBoxLayout()
        panels_layout.setContentsMargins(48, 0, 48, 0)  # 좌, 상, 우, 하
        panels_layout.setSpacing(0)

        # 좌측 패널 (792x802px) - 배경 이미지: 시험 분야별 시나리오 + 시험 API
        left_panel = QGroupBox()
        left_panel.setFixedSize(792, 802)

        left_bg_path = resource_path("assets/image/test_config/left_title_sub.png").replace(chr(92), "/")
        left_panel.setStyleSheet(f"""
            QGroupBox {{
                border: none;
                background-image: url({left_bg_path});
                background-repeat: no-repeat;
                background-position: top left;
            }}
        """)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(24, 44, 24, 80)  # 좌, 상(12+24+8), 우, 하
        left_layout.setSpacing(0)

        # 시험 분야별 시나리오 테이블
        field_group = self.create_test_field_group()
        left_layout.addWidget(field_group)

        # 간격: 16px(gap) + 38px(시험 API 제목) + 8px(gap) = 62px
        left_layout.addSpacing(62)

        # 시험 API 테이블 (QGroupBox로 감싸기)
        api_group = self.create_test_api_group()
        left_layout.addWidget(api_group)

        left_panel.setLayout(left_layout)

        # 우측 패널 (792x802px)
        right_panel = QGroupBox()
        right_panel.setFixedSize(792, 802)
        right_panel.setStyleSheet("QGroupBox { border: none; background: transparent; }")

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(24, 12, 24, 0)  # 좌, 상, 우, 하
        right_layout.setSpacing(0)

        # 사용자 인증 방식 타이틀 이미지 (744x24px)
        auth_title_widget = QLabel()
        auth_title_pixmap = QPixmap(resource_path("assets/image/test_config/사용자인증방식_title.png"))
        auth_title_widget.setPixmap(auth_title_pixmap.scaled(744, 24, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        auth_title_widget.setFixedSize(744, 24)
        right_layout.addWidget(auth_title_widget)

        # gap 8px
        right_layout.addSpacing(8)

        # 사용자 인증 방식 박스 (744x240px)
        auth_section = self.create_auth_section()
        right_layout.addWidget(auth_section)

        # gap 16px
        right_layout.addSpacing(16)

        # 접속주소 탐색 타이틀 + 주소탐색 버튼 행 (744x38px)
        connection_title_row = QWidget()
        connection_title_row.setFixedSize(744, 38)
        connection_title_layout = QHBoxLayout()
        connection_title_layout.setContentsMargins(0, 0, 0, 0)
        connection_title_layout.setSpacing(0)

        # 접속주소 탐색 타이틀 이미지
        connection_title_widget = QLabel()
        connection_title_pixmap = QPixmap(resource_path("assets/image/test_config/접속주소탐색_title.png"))
        connection_title_widget.setPixmap(connection_title_pixmap)
        connection_title_widget.setFixedHeight(38)
        connection_title_layout.addWidget(connection_title_widget)

        connection_title_layout.addStretch()

        # 버튼 그룹 (주소탐색 + 추가)
        buttons_widget = QWidget()
        buttons_widget.setFixedHeight(38)
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(16)  # gap 16px

        # 주소탐색 버튼 (120x38px)
        scan_btn = QPushButton("")
        scan_btn.setFixedSize(120, 38)

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
        scan_btn.clicked.connect(self.start_scan)
        buttons_layout.addWidget(scan_btn)

        # 추가 버튼 (90x38px)
        self.add_btn = QPushButton("")
        self.add_btn.setFixedSize(90, 38)
        self.add_btn.setCheckable(True)  # 토글 가능하도록 설정

        btn_add_enabled = resource_path("assets/image/test_config/btn_추가_enabled.png").replace(chr(92), "/")
        btn_add_hover = resource_path("assets/image/test_config/btn_추가_Hover.png").replace(chr(92), "/")
        btn_add_selected = resource_path("assets/image/test_config/btn_추가_selected.png").replace(chr(92), "/")

        self.add_btn.setStyleSheet(f"""
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
        # 추가 버튼 클릭 이벤트 연결
        self.add_btn.clicked.connect(self.toggle_address_popover)
        buttons_layout.addWidget(self.add_btn)

        buttons_widget.setLayout(buttons_layout)
        connection_title_layout.addWidget(buttons_widget)
        connection_title_row.setLayout(connection_title_layout)
        right_layout.addWidget(connection_title_row)

        # 주소 추가 팝오버 (392x102px)
        self.address_popover = QWidget()
        self.address_popover.setFixedSize(392, 102)
        self.address_popover.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 12px;
            }
        """)

        # 팝오버 그림자 효과 (Figma: X:0, Y:0, Blur:5, Spread:0, #6B6B6B 80%)
        popover_shadow = QGraphicsDropShadowEffect()
        popover_shadow.setBlurRadius(5)
        popover_shadow.setXOffset(0)
        popover_shadow.setYOffset(0)
        popover_shadow.setColor(QColor(107, 107, 107, 204))  # #6B6B6B 80%
        self.address_popover.setGraphicsEffect(popover_shadow)

        popover_layout = QVBoxLayout()
        popover_layout.setContentsMargins(16, 16, 16, 16)
        popover_layout.setSpacing(0)

        # "주소 추가" 문구 (358x26)
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

        # 4px gap
        popover_layout.addSpacing(4)

        # 입력창 + 추가 버튼 (수평 레이아웃)
        input_row_layout = QHBoxLayout()
        input_row_layout.setContentsMargins(0, 0, 0, 0)
        input_row_layout.setSpacing(6)  # 6px gap

        # 입력창 (287x40)
        self.address_input = QLineEdit()
        self.address_input.setFixedSize(287, 40)
        self.address_input.setPlaceholderText("추가할 주소를 입력해주세요")

        self.address_input.setStyleSheet("""
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
        input_row_layout.addWidget(self.address_input)

        # 추가 버튼 (65x40)
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
        popover_add_btn.clicked.connect(self.add_address_from_popover)
        input_row_layout.addWidget(popover_add_btn)

        popover_layout.addLayout(input_row_layout)
        self.address_popover.setLayout(popover_layout)

        # 팝오버를 절대 위치로 배치 (레이아웃에 추가하지 않음)
        # parent를 page2_widget으로 설정하여 상대 좌표 사용
        self.address_popover.setParent(self)

        # 초기에는 숨김
        self.address_popover.hide()

        # gap 8px
        right_layout.addSpacing(8)

        # URL 박스 테이블 (744x376px)
        connection_section = self.create_connection_section()
        right_layout.addWidget(connection_section)

        # padding 32px
        right_layout.addSpacing(32)

        # 하단 버튼 (초기화, 시험시작) - 전체 744x48px, 각 버튼 364x48px, gap 16px
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)  # 버튼 간격 16px

        # 초기화 버튼 (364x48px)
        reset_btn = QPushButton("")
        reset_btn.setFixedSize(364, 48)

        btn_reset_enabled = resource_path("assets/image/test_config/btn_초기화_enabled.png").replace(chr(92), "/")
        btn_reset_hover = resource_path("assets/image/test_config/btn_초기화_Hover.png").replace(chr(92), "/")

        reset_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url({btn_reset_enabled});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QPushButton:hover {{
                background-image: url({btn_reset_hover});
            }}
        """)
        reset_btn.clicked.connect(self.reset_all_fields)
        button_layout.addWidget(reset_btn)

        # 시험 시작 버튼 (364x48px)
        self.start_btn = QPushButton("")
        self.start_btn.setFixedSize(364, 48)

        btn_start_enabled = resource_path("assets/image/test_config/btn_시험시작_enabled.png").replace(chr(92), "/")
        btn_start_hover = resource_path("assets/image/test_config/btn_시험시작_Hover.png").replace(chr(92), "/")

        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url({btn_start_enabled});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QPushButton:hover {{
                background-image: url({btn_start_hover});
            }}
        """)
        self.start_btn.clicked.connect(self.start_test)
        self.start_btn.setEnabled(True)
        button_layout.addWidget(self.start_btn)

        right_layout.addLayout(button_layout)

        right_panel.setLayout(right_layout)

        panels_layout.addWidget(left_panel, 1)
        panels_layout.addWidget(right_panel, 1)

        # panels_layout을 bg_root_layout에 추가
        bg_root_layout.addLayout(panels_layout, 1)

        # bg_root를 content_layout에 가운데 정렬로 추가
        content_layout.addWidget(bg_root, 0, Qt.AlignHCenter | Qt.AlignVCenter)

        # 메인 레이아웃에 콘텐츠 영역 추가 (반응형: stretch=1)
        main_layout.addWidget(self.page2_content, 1)

        self.page2.setLayout(main_layout)

        return self.page2

    # ---------- 페이지 전환 메서드 ----------
    def go_to_next_page(self):
        """다음 페이지로 이동 (조건 검증 후)"""
        is_complete = self._is_page1_complete()

        if not is_complete:
            QMessageBox.warning(self,"입력 필요", "시험 정보 페이지의 모든 필수 항목을 입력해주세요.")
            return

        if self.current_page < 1:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)

    def go_to_previous_page(self):
        """이전 페이지로 이동"""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            # 1페이지로 돌아갈 때 다음 버튼 상태 업데이트
            if self.current_page == 0:
                self.check_next_button_state()


    def create_page2_buttons(self):
        """두 번째 페이지 버튼들"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addStretch()

        # 시험 시작 버튼
        self.start_btn = QPushButton("시험 시작")
        self.start_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        self.start_btn.clicked.connect(self.start_test)
        self.start_btn.setEnabled(True)  # 항상 활성화 (클릭 시 검증)
        layout.addWidget(self.start_btn)

        # 초기화 버튼
        reset_btn = QPushButton("초기화")
        reset_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        reset_btn.clicked.connect(self.reset_all_fields)
        layout.addWidget(reset_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    # ---------- 새로운 패널 생성 메서드들 ----------
    def create_basic_info_panel(self):
        """시험 기본 정보만 (불러오기 버튼 + 기본 정보 필드)"""
        panel = QWidget()  # QGroupBox에서 QWidget으로 변경

        # 패널 크기 및 스타일 설정 (872x843px, 배경: 시험기본정보입력.png)
        panel.setFixedSize(872, 843)

        # 배경 이미지 설정
        bg_panel_path = resource_path("assets/image/test_info/시험기본정보입력.png").replace(chr(92), "/")
        panel.setStyleSheet(f"""
            QWidget {{
                background-image: url({bg_panel_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(48, 32, 48, 40)  # left: 48, top: 32, right: 48, bottom: 40
        layout.setSpacing(0)

        # 타이틀 이미지 (776x106px - 시험기본정보확인.png)
        title_widget = QLabel()
        title_pixmap = QPixmap(resource_path("assets/image/test_info/시험기본정보확인.png"))
        title_widget.setPixmap(title_pixmap.scaled(776, 106, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        title_widget.setFixedSize(776, 106)
        title_widget.setScaledContents(True)
        layout.addWidget(title_widget)

        # 타이틀과 인풋박스 컨테이너 사이 간격
        layout.addSpacing(12)

        # 인풋박스 컨테이너 (776x479px - 기업명~시험범위)
        input_container = QWidget()
        input_container.setFixedSize(776, 479)
        input_container.setStyleSheet("QWidget { background: transparent; }")  # 투명 배경
        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)  # 필드 간 gap 12px

        # 기업명 필드 (776x82px - 전체 너비) - 기업명.png 배경 사용
        company_field_widget = QWidget()
        company_field_widget.setFixedSize(776, 82)

        # 배경 이미지 설정
        company_bg_path = resource_path("assets/image/test_info/기업명.png").replace(chr(92), "/")
        company_field_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                background-image: url({company_bg_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        company_field_layout = QVBoxLayout()
        company_field_layout.setContentsMargins(0, 0, 0, 0)
        company_field_layout.setSpacing(6)

        # 상단 여백 (라벨 영역 28px)
        company_field_layout.addSpacing(28)

        # 입력칸 (768x48px)
        self.company_edit = QLineEdit()
        self.company_edit.setFixedSize(768, 48)
        self.company_edit.setReadOnly(True)

        company_input_default = resource_path("assets/image/test_info/불러온정보_w_default.png").replace(chr(92), "/")
        company_input_filled = resource_path("assets/image/test_info/불러온정보_w_filled.png").replace(chr(92), "/")

        self.company_edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background: transparent url({company_input_default}) no-repeat center;
            }}
            QLineEdit[hasText="true"] {{
                background: transparent url({company_input_filled}) no-repeat center;
            }}
        """)

        # 텍스트 입력 시 배경 이미지 변경
        def update_company_background():
            has_text = bool(self.company_edit.text().strip())
            self.company_edit.setProperty("hasText", "true" if has_text else "false")
            self.company_edit.style().unpolish(self.company_edit)
            self.company_edit.style().polish(self.company_edit)

        self.company_edit.textChanged.connect(update_company_background)
        self.company_edit.setProperty("hasText", "false")

        company_field_layout.addWidget(self.company_edit)
        company_field_widget.setLayout(company_field_layout)
        input_layout.addWidget(company_field_widget)

        # 제품명 필드 (776x82px - 전체 너비) - 제품명.png 배경 사용
        product_field_widget = QWidget()
        product_field_widget.setFixedSize(776, 82)

        # 배경 이미지 설정
        product_bg_path = resource_path("assets/image/test_info/제품명.png").replace(chr(92), "/")
        product_field_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                background-image: url({product_bg_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        product_field_layout = QVBoxLayout()
        product_field_layout.setContentsMargins(0, 0, 0, 0)
        product_field_layout.setSpacing(6)

        # 상단 여백 (라벨 영역 28px)
        product_field_layout.addSpacing(28)

        # 입력칸 (768x48px)
        self.product_edit = QLineEdit()
        self.product_edit.setFixedSize(768, 48)
        self.product_edit.setReadOnly(True)

        product_input_default = resource_path("assets/image/test_info/불러온정보_w_default.png").replace(chr(92), "/")
        product_input_filled = resource_path("assets/image/test_info/불러온정보_w_filled.png").replace(chr(92), "/")

        self.product_edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background: transparent url({product_input_default}) no-repeat center;
            }}
            QLineEdit[hasText="true"] {{
                background: transparent url({product_input_filled}) no-repeat center;
            }}
        """)

        # 텍스트 입력 시 배경 이미지 변경
        def update_product_background():
            has_text = bool(self.product_edit.text().strip())
            self.product_edit.setProperty("hasText", "true" if has_text else "false")
            self.product_edit.style().unpolish(self.product_edit)
            self.product_edit.style().polish(self.product_edit)

        self.product_edit.textChanged.connect(update_product_background)
        self.product_edit.setProperty("hasText", "false")

        product_field_layout.addWidget(self.product_edit)
        product_field_widget.setLayout(product_field_layout)
        input_layout.addWidget(product_field_widget)

        # 버전, 모델명 행 (776x82px) - 이미지 배경 사용
        version_model_row = QWidget()
        version_model_row.setFixedSize(776, 82)
        version_model_layout = QHBoxLayout()
        version_model_layout.setContentsMargins(0, 0, 0, 0)
        version_model_layout.setSpacing(20)  # 간격 20px

        # 버전 필드 (378x82px) - 버전.png 배경 사용
        version_field_widget = QWidget()
        version_field_widget.setFixedSize(378, 82)

        version_bg_path = resource_path("assets/image/test_info/버전.png").replace(chr(92), "/")
        version_field_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                background-image: url({version_bg_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        version_field_layout = QVBoxLayout()
        version_field_layout.setContentsMargins(0, 0, 0, 0)
        version_field_layout.setSpacing(6)
        version_field_layout.addSpacing(28)

        self.version_edit = QLineEdit()
        self.version_edit.setFixedSize(378, 48)
        self.version_edit.setReadOnly(True)

        version_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        version_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.version_edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background: transparent url({version_input_default}) no-repeat center;
            }}
            QLineEdit[hasText="true"] {{
                background: transparent url({version_input_filled}) no-repeat center;
            }}
        """)

        def update_version_background():
            has_text = bool(self.version_edit.text().strip())
            self.version_edit.setProperty("hasText", "true" if has_text else "false")
            self.version_edit.style().unpolish(self.version_edit)
            self.version_edit.style().polish(self.version_edit)

        self.version_edit.textChanged.connect(update_version_background)
        self.version_edit.setProperty("hasText", "false")

        version_field_layout.addWidget(self.version_edit)
        version_field_widget.setLayout(version_field_layout)
        version_model_layout.addWidget(version_field_widget)

        # 모델명 필드 (378x82px) - 모델명.png 배경 사용
        model_field_widget = QWidget()
        model_field_widget.setFixedSize(378, 82)

        model_bg_path = resource_path("assets/image/test_info/모델명.png").replace(chr(92), "/")
        model_field_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                background-image: url({model_bg_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        model_field_layout = QVBoxLayout()
        model_field_layout.setContentsMargins(0, 0, 0, 0)
        model_field_layout.setSpacing(6)
        model_field_layout.addSpacing(28)

        self.model_edit = QLineEdit()
        self.model_edit.setFixedSize(378, 48)
        self.model_edit.setReadOnly(True)

        model_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        model_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.model_edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background: transparent url({model_input_default}) no-repeat center;
            }}
            QLineEdit[hasText="true"] {{
                background: transparent url({model_input_filled}) no-repeat center;
            }}
        """)

        def update_model_background():
            has_text = bool(self.model_edit.text().strip())
            self.model_edit.setProperty("hasText", "true" if has_text else "false")
            self.model_edit.style().unpolish(self.model_edit)
            self.model_edit.style().polish(self.model_edit)

        self.model_edit.textChanged.connect(update_model_background)
        self.model_edit.setProperty("hasText", "false")

        model_field_layout.addWidget(self.model_edit)
        model_field_widget.setLayout(model_field_layout)
        version_model_layout.addWidget(model_field_widget)

        version_model_row.setLayout(version_model_layout)
        input_layout.addWidget(version_model_row)

        # 시험유형, 시험대상 행 (776x82px) - 이미지 배경 사용
        category_target_row = QWidget()
        category_target_row.setFixedSize(776, 82)
        category_target_layout = QHBoxLayout()
        category_target_layout.setContentsMargins(0, 0, 0, 0)
        category_target_layout.setSpacing(20)  # 간격 20px

        # 시험유형 필드 (378x82px) - 시험유형.png 배경 사용
        test_category_widget = QWidget()
        test_category_widget.setFixedSize(378, 82)

        test_category_bg_path = resource_path("assets/image/test_info/시험유형.png").replace(chr(92), "/")
        test_category_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                background-image: url({test_category_bg_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        test_category_layout = QVBoxLayout()
        test_category_layout.setContentsMargins(0, 0, 0, 0)
        test_category_layout.setSpacing(6)
        test_category_layout.addSpacing(28)

        self.test_category_edit = QLineEdit()
        self.test_category_edit.setFixedSize(378, 48)
        self.test_category_edit.setReadOnly(True)

        test_category_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        test_category_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.test_category_edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background: transparent url({test_category_input_default}) no-repeat center;
            }}
            QLineEdit[hasText="true"] {{
                background: transparent url({test_category_input_filled}) no-repeat center;
            }}
        """)

        def update_test_category_background():
            has_text = bool(self.test_category_edit.text().strip())
            self.test_category_edit.setProperty("hasText", "true" if has_text else "false")
            self.test_category_edit.style().unpolish(self.test_category_edit)
            self.test_category_edit.style().polish(self.test_category_edit)

        self.test_category_edit.textChanged.connect(update_test_category_background)
        self.test_category_edit.setProperty("hasText", "false")

        test_category_layout.addWidget(self.test_category_edit)
        test_category_widget.setLayout(test_category_layout)
        category_target_layout.addWidget(test_category_widget)

        # 시험대상 필드 (378x82px) - 시험대상.png 배경 사용
        target_system_widget = QWidget()
        target_system_widget.setFixedSize(378, 82)

        target_system_bg_path = resource_path("assets/image/test_info/시험대상.png").replace(chr(92), "/")
        target_system_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                background-image: url({target_system_bg_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        target_system_layout = QVBoxLayout()
        target_system_layout.setContentsMargins(0, 0, 0, 0)
        target_system_layout.setSpacing(6)
        target_system_layout.addSpacing(28)

        self.target_system_edit = QLineEdit()
        self.target_system_edit.setFixedSize(378, 48)
        self.target_system_edit.setReadOnly(True)

        target_system_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        target_system_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.target_system_edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background: transparent url({target_system_input_default}) no-repeat center;
            }}
            QLineEdit[hasText="true"] {{
                background: transparent url({target_system_input_filled}) no-repeat center;
            }}
        """)

        def update_target_system_background():
            has_text = bool(self.target_system_edit.text().strip())
            self.target_system_edit.setProperty("hasText", "true" if has_text else "false")
            self.target_system_edit.style().unpolish(self.target_system_edit)
            self.target_system_edit.style().polish(self.target_system_edit)

        self.target_system_edit.textChanged.connect(update_target_system_background)
        self.target_system_edit.setProperty("hasText", "false")

        target_system_layout.addWidget(self.target_system_edit)
        target_system_widget.setLayout(target_system_layout)
        category_target_layout.addWidget(target_system_widget)

        category_target_row.setLayout(category_target_layout)
        input_layout.addWidget(category_target_row)

        # 시험분야, 시험범위 행 (776x82px) - 이미지 배경 사용
        group_range_row = QWidget()
        group_range_row.setFixedSize(776, 82)
        group_range_layout = QHBoxLayout()
        group_range_layout.setContentsMargins(0, 0, 0, 0)
        group_range_layout.setSpacing(20)  # 간격 20px

        # 시험분야 필드 (378x82px) - 시험분야.png 배경 사용
        test_group_widget = QWidget()
        test_group_widget.setFixedSize(378, 82)

        test_group_bg_path = resource_path("assets/image/test_info/시험분야.png").replace(chr(92), "/")
        test_group_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                background-image: url({test_group_bg_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        test_group_layout = QVBoxLayout()
        test_group_layout.setContentsMargins(0, 0, 0, 0)
        test_group_layout.setSpacing(6)
        test_group_layout.addSpacing(28)

        self.test_group_edit = QLineEdit()
        self.test_group_edit.setFixedSize(378, 48)
        self.test_group_edit.setReadOnly(True)

        test_group_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        test_group_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.test_group_edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background: transparent url({test_group_input_default}) no-repeat center;
            }}
            QLineEdit[hasText="true"] {{
                background: transparent url({test_group_input_filled}) no-repeat center;
            }}
        """)

        def update_test_group_background():
            has_text = bool(self.test_group_edit.text().strip())
            self.test_group_edit.setProperty("hasText", "true" if has_text else "false")
            self.test_group_edit.style().unpolish(self.test_group_edit)
            self.test_group_edit.style().polish(self.test_group_edit)

        self.test_group_edit.textChanged.connect(update_test_group_background)
        self.test_group_edit.setProperty("hasText", "false")

        test_group_layout.addWidget(self.test_group_edit)
        test_group_widget.setLayout(test_group_layout)
        group_range_layout.addWidget(test_group_widget)

        # 시험범위 필드 (378x82px) - 시험범위.png 배경 사용
        test_range_widget = QWidget()
        test_range_widget.setFixedSize(378, 82)

        test_range_bg_path = resource_path("assets/image/test_info/시험범위.png").replace(chr(92), "/")
        test_range_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                background-image: url({test_range_bg_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        test_range_layout = QVBoxLayout()
        test_range_layout.setContentsMargins(0, 0, 0, 0)
        test_range_layout.setSpacing(6)
        test_range_layout.addSpacing(28)

        self.test_range_edit = QLineEdit()
        self.test_range_edit.setFixedSize(378, 48)
        self.test_range_edit.setReadOnly(True)

        test_range_input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
        test_range_input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        self.test_range_edit.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background: transparent url({test_range_input_default}) no-repeat center;
            }}
            QLineEdit[hasText="true"] {{
                background: transparent url({test_range_input_filled}) no-repeat center;
            }}
        """)

        def update_test_range_background():
            has_text = bool(self.test_range_edit.text().strip())
            self.test_range_edit.setProperty("hasText", "true" if has_text else "false")
            self.test_range_edit.style().unpolish(self.test_range_edit)
            self.test_range_edit.style().polish(self.test_range_edit)

        self.test_range_edit.textChanged.connect(update_test_range_background)
        self.test_range_edit.setProperty("hasText", "false")

        test_range_layout.addWidget(self.test_range_edit)
        test_range_widget.setLayout(test_range_layout)
        group_range_layout.addWidget(test_range_widget)

        group_range_row.setLayout(group_range_layout)
        input_layout.addWidget(group_range_row)

        # 시험유형 변경 시 관리자 코드 필드 활성화/비활성화
        self.test_category_edit.textChanged.connect(self.form_validator.handle_test_category_change)
        self.test_category_edit.textChanged.connect(self.check_start_button_state)

        # 시험범위 변경 시 UI 표시 텍스트 변환
        self.test_range_edit.textChanged.connect(self.form_validator.handle_test_range_change)

        # Input Container 하단 여백 20px
        input_layout.addSpacing(20)

        input_container.setLayout(input_layout)
        layout.addWidget(input_container)

        # Divider 이미지
        divider = QLabel()
        divider_pixmap = QPixmap(resource_path("assets/image/test_info/divider.png"))
        divider.setPixmap(divider_pixmap)
        divider.setScaledContents(True)
        divider.setFixedSize(776, divider_pixmap.height() if divider_pixmap.height() > 0 else 1)
        layout.addWidget(divider)

        # Divider와 관리자 코드 사이 간격 12px
        layout.addSpacing(12)

        # 관리자 코드 필드 (776x82px - 전체 너비) - 이미지 배경 사용
        admin_code_field = self.create_admin_code_field()
        self.admin_code_edit = admin_code_field["input"]
        self.admin_code_edit.setEchoMode(QLineEdit.Password)  # 비밀번호 모드
        self.admin_code_edit.setPlaceholderText("")  # 초기에는 placeholder 없음
        self.admin_code_edit.setEnabled(False)  # 초기에는 비활성화 (시험 정보 불러오기 전)
        layout.addWidget(admin_code_field["widget"])

        # 관리자 코드 입력 시 숫자 검증 및 버튼 상태 업데이트
        self.admin_code_edit.textChanged.connect(self.form_validator.validate_admin_code)
        self.admin_code_edit.textChanged.connect(self.check_start_button_state)
        self.admin_code_edit.textChanged.connect(self.check_next_button_state)  # 1페이지 다음 버튼 상태 체크

        # 첫 번째 페이지 필드들의 변경 시 다음 버튼 상태 체크
        for field in [self.company_edit, self.product_edit, self.version_edit, self.model_edit,
                     self.test_category_edit, self.target_system_edit, self.test_group_edit, self.test_range_edit,
                     self.admin_code_edit]:
            field.textChanged.connect(self.check_next_button_state)

        # 관리자 코드와 버튼 사이 간격 32px
        layout.addSpacing(32)

        # 하단 버튼 (초기화: 왼쪽, 다음: 오른쪽) - 각 378x48px, gap 20px, 전체 776x48px
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)  # 버튼 간격 20px

        # 초기화 버튼 (왼쪽) - 378x48px
        reset_btn = QPushButton()
        reset_btn.setFixedSize(378, 48)
        import os
        btn_reset_enabled = resource_path("assets/image/test_info/btn_초기화_enabled.png").replace(chr(92), "/")
        btn_reset_hover = resource_path("assets/image/test_info/btn_초기화_Hover.png").replace(chr(92), "/")
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url({btn_reset_enabled});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QPushButton:hover {{
                background-image: url({btn_reset_hover});
            }}
        """)
        reset_btn.clicked.connect(self.reset_all_fields)
        button_layout.addWidget(reset_btn)

        # 다음 버튼 (오른쪽) - 378x48px
        self.next_btn = QPushButton()
        self.next_btn.setFixedSize(378, 48)
        btn_next_enabled = resource_path("assets/image/test_info/btn_다음_enabled.png").replace(chr(92), "/")
        btn_next_hover = resource_path("assets/image/test_info/btn_다음_Hover.png").replace(chr(92), "/")
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-image: url({btn_next_enabled});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QPushButton:hover {{
                background-image: url({btn_next_hover});
            }}
        """)
        self.next_btn.clicked.connect(self.go_to_next_page)
        button_layout.addWidget(self.next_btn)

        layout.addLayout(button_layout)

        panel.setLayout(layout)
        return panel

    def create_input_field(self, label_text, width=768):
        """
        입력 필드 생성
        - 전체 크기: width x 82px
        - 라벨: width x 28px (6px 간격)
        - 입력칸: width x 48px

        Args:
            label_text: 라벨 텍스트
            width: 필드 너비 (기본값: 768, 2열일 경우: 374)
        """
        field_widget = QWidget()
        field_widget.setFixedSize(width, 82)
        field_layout = QVBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)  # 라벨과 입력칸 사이 간격 6px

        # 라벨 (width x 28px)
        label = QLabel(label_text)
        label.setFixedSize(width, 28)
        label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 16px;
                font-weight: 500;
                letter-spacing: -0.16px;
            }
        """)
        field_layout.addWidget(label)

        # 입력칸 (width x 48px)
        input_field = QLineEdit()
        input_field.setFixedSize(width, 48)
        input_field.setStyleSheet("""
            QLineEdit {
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 400;
                letter-spacing: -0.17px;
                color: #000000;
                padding: 0 24px;
                border: 1px solid #E8E8E8;
                border-radius: 4px;
            }
            QLineEdit::placeholder {
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 500;
                letter-spacing: -0.17px;
                color: #868686;
            }
        """)
        field_layout.addWidget(input_field)

        field_widget.setLayout(field_layout)

        return {
            "widget": field_widget,
            "input": input_field
        }

    def create_readonly_input_field(self, label_text, width=776):
        """
        읽기전용 입력 필드 생성 (불러온 정보용 - 이미지 배경)
        - 전체 크기: width x 82px
        - 라벨: width x 28px (6px 간격)
        - 입력칸: width x 48px (이미지 배경 사용)

        Args:
            label_text: 라벨 텍스트
            width: 필드 너비 (776: wide 이미지, 378: small 이미지)
        """
        field_widget = QWidget()
        field_widget.setFixedSize(width, 82)
        field_layout = QVBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)  # 라벨과 입력칸 사이 간격 6px

        # 라벨 (width x 28px)
        label = QLabel(label_text)
        label.setFixedSize(width, 28)
        label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 16px;
                font-weight: 500;
                letter-spacing: -0.16px;
            }
        """)
        field_layout.addWidget(label)

        # 입력칸 (width x 48px) - 이미지 배경
        input_field = QLineEdit()
        input_field.setFixedSize(width, 48)

        # 한글 경로 처리를 위한 절대 경로 사용
        import os
        # 너비에 따라 다른 이미지 사용
        if width >= 768:
            # 전체 너비 (776px) - wide 이미지
            input_default = resource_path("assets/image/test_info/불러온정보_w_default.png").replace(chr(92), "/")
            input_filled = resource_path("assets/image/test_info/불러온정보_w_filled.png").replace(chr(92), "/")
        else:
            # 반 너비 (378px) - small 이미지
            input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
            input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 400;
                letter-spacing: -0.17px;
                color: #000000;
                padding: 0 24px;
                border: none;
                background-image: url({input_default});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QLineEdit[hasText="true"] {{
                background-image: url({input_filled});
            }}
            QLineEdit::placeholder {{
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 500;
                letter-spacing: -0.17px;
                color: #868686;
            }}
        """)

        # 텍스트 입력 시 배경 이미지 변경을 위한 동적 프로퍼티 업데이트
        def update_background():
            has_text = bool(input_field.text().strip())
            input_field.setProperty("hasText", "true" if has_text else "false")
            input_field.style().unpolish(input_field)
            input_field.style().polish(input_field)

        input_field.textChanged.connect(update_background)
        input_field.setProperty("hasText", "false")  # 초기 상태
        field_layout.addWidget(input_field)

        field_widget.setLayout(field_layout)

        return {
            "widget": field_widget,
            "input": input_field
        }

    def create_admin_code_field(self):
        """
        관리자 코드 입력 필드 생성 (776x82px)
        - 배경 이미지: 776x82px (관리자 코드 입력.png)
        - 입력칸: 배경 이미지 위에 배치
        """
        field_widget = QWidget()
        field_widget.setFixedSize(776, 82)

        # field_widget에 배경 이미지 설정
        bg_img_path = resource_path("assets/image/test_info/관리자 코드 입력.png").replace(chr(92), "/")
        field_widget.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                background-image: url({bg_img_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        # 레이아웃 설정
        field_layout = QVBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)

        # 상단 여백 (라벨 영역 28px)
        field_layout.addSpacing(28)

        # 입력칸 (768x48px)
        input_field = QLineEdit()
        input_field.setFixedSize(768, 48)

        # 입력 필드 배경 이미지
        input_enabled = resource_path("assets/image/test_info/input_enabled.png").replace(chr(92), "/")
        input_disabled = resource_path("assets/image/test_info/input_disabled.png").replace(chr(92), "/")
        input_hover = resource_path("assets/image/test_info/input_Hover.png").replace(chr(92), "/")
        input_filled = resource_path("assets/image/test_info/input_filled.png").replace(chr(92), "/")

        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                letter-spacing: -0.18px;
                color: #000000;
                padding: 0 24px;
                border: none;
                outline: none;
                background: transparent url({input_enabled}) no-repeat center;
            }}
            QLineEdit:focus {{
                border: none;
                outline: none;
                background: transparent url({input_enabled}) no-repeat center;
            }}
            QLineEdit:hover:enabled:!focus[hasText="false"] {{
                background: transparent url({input_hover}) no-repeat center;
            }}
            QLineEdit:disabled {{
                background: transparent url({input_disabled}) no-repeat center;
            }}
            QLineEdit[hasText="true"] {{
                background: transparent url({input_filled}) no-repeat center;
            }}
        """)

        # 텍스트 입력 시 배경 이미지 변경을 위한 동적 프로퍼티 업데이트
        def update_background():
            has_text = bool(input_field.text().strip())
            input_field.setProperty("hasText", "true" if has_text else "false")
            input_field.style().unpolish(input_field)
            input_field.style().polish(input_field)

        input_field.textChanged.connect(update_background)
        input_field.setProperty("hasText", "false")

        field_layout.addWidget(input_field)

        field_widget.setLayout(field_layout)

        return {
            "widget": field_widget,
            "input": input_field
        }

    def create_test_field_group(self):
        """시험 분야별 시나리오 그룹 (QGroupBox)"""
        group = QGroupBox()  # 타이틀 제거 (배경 이미지에 포함)
        group.setFixedSize(744, 240)

        # 배경 불투명 설정
        group.setAutoFillBackground(True)
        palette = group.palette()
        palette.setColor(group.backgroundRole(), QColor("#FFFFFF"))
        group.setPalette(palette)

        # QGroupBox 스타일 설정
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                padding-top: 0px;
                background-color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 두 개의 독립적인 테이블을 나란히 배치하기 위한 수평 레이아웃
        tables_layout = QHBoxLayout()
        tables_layout.setContentsMargins(0, 0, 0, 0)
        tables_layout.setSpacing(0)

        # 시험 분야 테이블 (372px x 240px) - 1개 컬럼
        self.test_field_table = TestFieldTableWidget(0, 1)
        self.test_field_table.setFixedSize(372, 240)
        self.test_field_table.setHorizontalHeaderLabels(["시험 분야"])

        # 시험 시나리오 테이블 (372px x 240px) - 1개 컬럼
        self.scenario_table = TestFieldTableWidget(0, 1)
        self.scenario_table.setFixedSize(372, 240)
        self.scenario_table.setHorizontalHeaderLabels(["시험 시나리오"])

        # === 시험 분야 테이블 설정 ===
        field_header = self.test_field_table.horizontalHeader()
        field_header.setFixedHeight(31)
        field_header.setSectionResizeMode(0, QHeaderView.Fixed)
        field_header.resizeSection(0, 372)

        # 행 높이 설정
        self.test_field_table.verticalHeader().setDefaultSectionSize(39)
        self.test_field_table.verticalHeader().setVisible(False)

        # 편집 불가 설정
        self.test_field_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.test_field_table.setAlternatingRowColors(False)
        self.test_field_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)

        # === 시험 시나리오 테이블 설정 ===
        scenario_header = self.scenario_table.horizontalHeader()
        scenario_header.setFixedHeight(31)
        scenario_header.setSectionResizeMode(0, QHeaderView.Fixed)
        scenario_header.resizeSection(0, 372)

        # 행 높이 설정
        self.scenario_table.verticalHeader().setDefaultSectionSize(39)
        self.scenario_table.verticalHeader().setVisible(False)

        # 편집 불가 설정
        self.scenario_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scenario_table.setAlternatingRowColors(False)
        self.scenario_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.scenario_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scenario_table.cellClicked.connect(self.on_scenario_selected)

        # === 공통 스타일 정의 ===
        table_style = """
            QTableWidget {
                border: 1px solid #CECECE;
                gridline-color: #CCCCCC;
                show-decoration-selected: 0;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                padding-right: 14px;
                color: #1B1B1C;
                outline: 0;
                background-color: transparent;
            }
            QTableWidget::item:selected {
                color: #1B1B1C;
                background-color: transparent;
            }
            QTableWidget::item:focus {
                outline: none;
                border: none;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                border-right: 1px solid #CCCCCC;
                color: #1B1B1C;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #EDF0F3;
            }
        """

        # 시험 분야 테이블 스타일 (왼쪽 테두리 + 오른쪽 세로선)
        self.test_field_table.setStyleSheet(table_style + """
            QTableWidget {
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                border-right: 1px solid #CCCCCC;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)

        # 시험 시나리오 테이블 스타일 (오른쪽 테두리만)
        self.scenario_table.setStyleSheet(table_style + """
            QTableWidget {
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                border-left: none;
            }
        """)

        # 마지막으로 클릭된 시험 분야의 행을 추적
        self.selected_test_field_row = None

        # 폰트 설정 (stylesheet 이후에 강제 적용)
        cell_font = QFont("Noto Sans KR")
        cell_font.setPixelSize(19)
        cell_font.setWeight(QFont.Normal)

        header_font = QFont("Noto Sans KR")
        header_font.setPixelSize(18)
        header_font.setWeight(QFont.DemiBold)

        # 시험 분야 테이블 폰트
        self.test_field_table.setFont(cell_font)
        self.test_field_table.horizontalHeader().setFont(header_font)

        # 시험 시나리오 테이블 폰트
        self.scenario_table.setFont(cell_font)
        self.scenario_table.horizontalHeader().setFont(header_font)

        # 시험 분야 테이블 배경색 설정
        from PyQt5.QtGui import QPalette
        self.test_field_table.setAutoFillBackground(True)
        self.test_field_table.setAttribute(Qt.WA_OpaquePaintEvent, True)
        palette = self.test_field_table.palette()
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.test_field_table.setPalette(palette)

        self.test_field_table.viewport().setAutoFillBackground(True)
        viewport_palette = self.test_field_table.viewport().palette()
        viewport_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        viewport_palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.test_field_table.viewport().setPalette(viewport_palette)

        # 시험 시나리오 테이블 배경색 설정
        self.scenario_table.setAutoFillBackground(True)
        self.scenario_table.setAttribute(Qt.WA_OpaquePaintEvent, True)
        scenario_palette = self.scenario_table.palette()
        scenario_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        scenario_palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.scenario_table.setPalette(scenario_palette)

        self.scenario_table.viewport().setAutoFillBackground(True)
        scenario_viewport_palette = self.scenario_table.viewport().palette()
        scenario_viewport_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        scenario_viewport_palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.scenario_table.viewport().setPalette(scenario_viewport_palette)

        # 시험 시나리오 테이블 배경 (viewport 위에 오버레이, 시험 분야 선택 시 #E3F2FF 배경)
        self.scenario_column_background = QLabel("")
        self.scenario_column_background.setParent(self.scenario_table.viewport())
        self.scenario_column_background.setStyleSheet("""
            QLabel {
                background-color: #E3F2FF;
            }
        """)
        # viewport 기준으로 전체 영역 커버
        self.scenario_column_background.setGeometry(0, 0, 372, 240)
        self.scenario_column_background.lower()  # 셀들 뒤로 배치
        self.scenario_column_background.hide()  # 초기에는 숨김

        # 시험 시나리오 안내 문구 QLabel (시나리오 테이블 위에 오버레이)
        self.scenario_placeholder_label = QLabel("시험분야를 선택하면\n시나리오가 표시됩니다.")
        self.scenario_placeholder_label.setParent(self.scenario_table)
        self.scenario_placeholder_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.scenario_placeholder_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #6B6B6B;
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-bottom-right-radius: 4px;
                padding-top: 40px;
            }
        """)
        # 헤더 아래 영역에 배치
        self.scenario_placeholder_label.setGeometry(0, 31, 372, 209)  # x, y, width, height
        self.scenario_placeholder_label.hide()  # 초기에는 숨김

        # 두 테이블을 수평 레이아웃에 추가
        tables_layout.addWidget(self.test_field_table)
        tables_layout.addWidget(self.scenario_table)

        # 수평 레이아웃을 메인 레이아웃에 추가
        layout.addLayout(tables_layout)

        group.setLayout(layout)
        return group

    def create_test_api_group(self):
        """시험 API 그룹 (QGroupBox)"""
        group = QGroupBox()  # 타이틀 제거 (배경 이미지에 포함)
        group.setFixedSize(744, 376)

        # 배경 불투명 설정
        group.setAutoFillBackground(True)
        palette = group.palette()
        palette.setColor(group.backgroundRole(), QColor("#FFFFFF"))
        group.setPalette(palette)

        # QGroupBox 스타일 설정
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                padding-top: 0px;
                background-color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 시험 API 테이블 (744x376px)
        self.api_test_table = QTableWidget(0, 2)
        self.api_test_table.setFixedSize(744, 376)

        self.api_test_table.setHorizontalHeaderLabels(["기능명", "API명"])

        # 헤더 설정
        header = self.api_test_table.horizontalHeader()
        header.setFixedHeight(31)  # 31px로 변경

        # 행 번호 열 너비 설정
        self.api_test_table.verticalHeader().setFixedWidth(50)

        header.resizeSection(0, 346)
        header.resizeSection(1, 346)

        # 헤더 폰트 설정 (18px)
        header_font = QFont("Noto Sans KR")
        header_font.setPixelSize(18)
        header_font.setWeight(QFont.DemiBold)
        self.api_test_table.horizontalHeader().setFont(header_font)

        # 셀 높이 설정 (39px)
        self.api_test_table.verticalHeader().setDefaultSectionSize(39)

        # 셀 폰트 설정 (19px)
        cell_font = QFont("Noto Sans KR")
        cell_font.setPixelSize(19)
        self.api_test_table.setFont(cell_font)

        # 편집 비활성화
        self.api_test_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 왼쪽 행 번호 헤더 설정
        vertical_header = self.api_test_table.verticalHeader()
        vertical_header.setFixedWidth(50)  # 행 번호 너비 고정 (시험 API 테이블과 동일)
        vertical_header.setDefaultAlignment(Qt.AlignCenter)

        # 행 번호 폰트 설정 (19px)
        row_number_font = QFont("Noto Sans KR")
        row_number_font.setPixelSize(19)
        vertical_header.setFont(row_number_font)


        # 세로 grid line 제거
        self.api_test_table.setShowGrid(False)

        # 스크롤바 비활성화
        self.api_test_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 테이블 스타일 설정
        self.api_test_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                letter-spacing: 0.098px;
            }
            QTableWidget::item {
                background-color: #FFFFFF;
                border-bottom: 1px solid #CCCCCC;
                border-right: none;
                padding-right: 14px;
                color: #1B1B1C;
            }
            QTableWidget::item:selected {
                background-color: #FFFFFF;
                color: #1B1B1C;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                font-family: 'Noto Sans KR';
                font-weight: 600;
                letter-spacing: -0.156px;
                color: #1B1B1C;
            }
            QHeaderView::section:vertical {
                background-color: #FFFFFF;
                border: none;
                border-right: none;
                border-bottom: 1px solid #CCCCCC;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                letter-spacing: 0.098px;
                color: #1B1B1C;
            }
            QTableCornerButton::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
            }
            QTableWidget::viewport {
                background-color: #FFFFFF;
            }
        """)

        # Stylesheet 이후 배경색 강제 설정 (stylesheet보다 나중에 적용)
        self.api_test_table.setAutoFillBackground(True)
        self.api_test_table.setAttribute(Qt.WA_OpaquePaintEvent, True)

        from PyQt5.QtGui import QPalette
        palette = self.api_test_table.palette()
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.api_test_table.setPalette(palette)

        # Viewport 배경색 마지막에 강제 설정
        self.api_test_table.viewport().setAutoFillBackground(True)
        viewport_palette = self.api_test_table.viewport().palette()
        viewport_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        viewport_palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        self.api_test_table.viewport().setPalette(viewport_palette)

        # 시험 API 안내 문구 QLabel (테이블 위에 오버레이)
        self.api_placeholder_label = QLabel("시험 시나리오를 선택하면\nAPI가 표시됩니다.")
        self.api_placeholder_label.setParent(self.api_test_table)
        self.api_placeholder_label.setAlignment(Qt.AlignCenter)
        self.api_placeholder_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 400;
                color: #6B6B6B;
                background-color: transparent;
                padding-top: 10px;
            }
        """)
        # 헤더 높이(31px) + 행 번호 너비(50px) 고려하여 테이블 중앙에 배치
        self.api_placeholder_label.setGeometry(50, 31, 694, 345)  # x, y, width, height
        self.api_placeholder_label.show()  # 초기에는 표시

        layout.addWidget(self.api_test_table)
        group.setLayout(layout)
        return group

    def create_auth_section(self):
        """인증 방식 섹션 (타이틀 제외, 744x240px)"""
        section = QGroupBox()
        section.setFixedSize(744, 240)
        section.setStyleSheet("QGroupBox { border: none; background-color: transparent; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 콘텐츠 영역 (744x240px)
        content_widget = QWidget()
        content_widget.setFixedSize(744, 240)

        # 배경 색상 설정
        content_widget.setStyleSheet("""
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
        content_widget.setObjectName("content_widget")

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(24, 16, 24, 16)
        content_layout.setSpacing(0)

        # 왼쪽: 인증 방식 선택 영역 (289x208px)
        auth_type_widget = QWidget()
        auth_type_widget.setFixedSize(289, 208)
        auth_type_widget.setStyleSheet("background-color: transparent;")
        auth_type_layout = QVBoxLayout()
        auth_type_layout.setContentsMargins(0, 12, 0, 12)  # 상하 12px
        auth_type_layout.setSpacing(12)  # gap 12px

        # Digest Auth 박스 (289x86px)
        self.digest_option = QWidget()
        self.digest_option.setFixedSize(289, 86)
        # 초기 상태: 선택됨 (digest_radio가 기본 체크되어 있음)
        self.digest_option.setStyleSheet("""
            QWidget {
                background-color: #E9F6FE;
                border: 1px solid #2B96ED;
                border-radius: 8px;
            }
        """)
        digest_option_main_layout = QHBoxLayout()
        digest_option_main_layout.setContentsMargins(16, 16, 16, 16)  # 상하좌우 16px
        digest_option_main_layout.setSpacing(0)

        # 라디오 버튼 (30x54)
        self.digest_radio = QRadioButton()
        self.digest_radio.setFixedSize(30, 54)
        self.digest_radio.setChecked(True)
        self.digest_radio.setStyleSheet("""
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
        digest_option_main_layout.addWidget(self.digest_radio, alignment=Qt.AlignTop)

        # 8px gap
        digest_option_main_layout.addSpacing(8)

        # 텍스트 영역 (수직 레이아웃)
        digest_text_layout = QVBoxLayout()
        digest_text_layout.setContentsMargins(0, 0, 0, 0)
        digest_text_layout.setSpacing(0)

        # "Digest Auth" 제목 (120x26)
        digest_label = QLabel("Digest Auth")
        digest_label.setFixedSize(120, 26)
        digest_label.setStyleSheet("""
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
        digest_text_layout.addWidget(digest_label)

        # 2px gap
        digest_text_layout.addSpacing(2)

        # "ID,PW 기반 인증 방식" 설명 (163x26)
        digest_desc = QLabel("ID,PW 기반 인증 방식")
        digest_desc.setFixedSize(163, 26)
        digest_desc.setStyleSheet("""
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
        digest_text_layout.addWidget(digest_desc)

        digest_option_main_layout.addLayout(digest_text_layout)
        digest_option_main_layout.addStretch()

        self.digest_option.setLayout(digest_option_main_layout)
        auth_type_layout.addWidget(self.digest_option)

        # Bearer Token 박스 (289x86px)
        self.bearer_option = QWidget()
        self.bearer_option.setFixedSize(289, 86)
        # 초기 상태: 선택 안됨
        self.bearer_option.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 8px;
            }
        """)
        bearer_option_main_layout = QHBoxLayout()
        bearer_option_main_layout.setContentsMargins(16, 16, 16, 16)  # 상하좌우 16px
        bearer_option_main_layout.setSpacing(0)

        # 라디오 버튼 (30x54)
        self.bearer_radio = QRadioButton()
        self.bearer_radio.setFixedSize(30, 54)
        self.bearer_radio.setStyleSheet("""
            QRadioButton {
                border: none;
                background: transparent;
                padding-bottom: 26px;
            }
            QRadioButton::indicator {
                width: 27px;
                height: 27px;
            }
        """)
        bearer_option_main_layout.addWidget(self.bearer_radio, alignment=Qt.AlignTop)

        # 8px gap
        bearer_option_main_layout.addSpacing(8)

        # 텍스트 영역 (수직 레이아웃)
        bearer_text_layout = QVBoxLayout()
        bearer_text_layout.setContentsMargins(0, 0, 0, 0)
        bearer_text_layout.setSpacing(0)

        # "Bearer Token" 제목 (130x26)
        bearer_label = QLabel("Bearer Token")
        bearer_label.setFixedSize(130, 26)
        bearer_label.setStyleSheet("""
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
        bearer_text_layout.addWidget(bearer_label)

        # 2px gap
        bearer_text_layout.addSpacing(2)

        # "Token 기반 인증 방식" 설명 (163x26)
        bearer_desc = QLabel("Token 기반 인증 방식")
        bearer_desc.setFixedSize(163, 26)
        bearer_desc.setStyleSheet("""
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
        bearer_text_layout.addWidget(bearer_desc)

        bearer_option_main_layout.addLayout(bearer_text_layout)
        bearer_option_main_layout.addStretch()

        self.bearer_option.setLayout(bearer_option_main_layout)
        auth_type_layout.addWidget(self.bearer_option)

        auth_type_widget.setLayout(auth_type_layout)
        content_layout.addWidget(auth_type_widget)

        # 라디오 버튼 토글 시 박스 스타일 변경
        self.digest_radio.toggled.connect(self.on_auth_type_changed)
        self.bearer_radio.toggled.connect(self.on_auth_type_changed)

        # divider 왼쪽 gap 12px
        content_layout.addSpacing(12)

        # 수직 divider (1x208px)
        divider = QLabel()
        divider.setFixedSize(1, 208)
        divider_pixmap = QPixmap(resource_path("assets/image/test_config/divider.png"))
        divider.setPixmap(divider_pixmap.scaled(1, 208, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        content_layout.addWidget(divider)

        # divider 오른쪽 gap 12px
        content_layout.addSpacing(12)

        # 오른쪽: User ID/Password 입력 영역 (358x208px)
        common_input_widget = QWidget()
        common_input_widget.setFixedSize(358, 208)
        common_input_widget.setStyleSheet("background-color: transparent;")
        common_input_layout = QVBoxLayout()
        common_input_layout.setContentsMargins(0, 12, 0, 12)  # 상하 12px, 12px
        common_input_layout.setSpacing(0)

        # "사용자 ID입력" 문구 (358x29px)
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

        # "User ID" 문구 (358x26px)
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

        # 아이디 입력칸 (358x40px)
        self.id_input = QLineEdit()
        self.id_input.setFixedSize(358, 40)
        self.id_input.setPlaceholderText("사용자 ID를 입력해주세요")
        digest_enabled = resource_path("assets/image/test_config/input_DigestAuth_enabled.png").replace(chr(92), "/")
        digest_disabled = resource_path("assets/image/test_config/input_DigestAuth_disabled.png").replace(chr(92), "/")
        self.id_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 24px;
                padding-right: 24px;
                border: none;
                background-color: #FFFFFF;
                background-image: url({digest_enabled});
                background-repeat: no-repeat;
                background-position: center;
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
                background-image: url({digest_disabled});
                color: #868686;
            }}
        """)
        common_input_layout.addWidget(self.id_input)

        # gap 6px
        common_input_layout.addSpacing(6)

        # "Password" 문구 (358x26px)
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

        # password 입력칸 (358x40px)
        self.pw_input = QLineEdit()
        self.pw_input.setFixedSize(358, 40)
        self.pw_input.setPlaceholderText("암호를 입력해 주세요")
        self.pw_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 24px;
                padding-right: 24px;
                border: none;
                background-color: #FFFFFF;
                background-image: url({digest_enabled});
                background-repeat: no-repeat;
                background-position: center;
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
                background-image: url({digest_disabled});
                color: #868686;
            }}
        """)
        common_input_layout.addWidget(self.pw_input)

        common_input_widget.setLayout(common_input_layout)
        content_layout.addWidget(common_input_widget)

        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)

        # 라디오 버튼 그룹 설정
        from PyQt5.QtWidgets import QButtonGroup
        self.auth_button_group = QButtonGroup()
        self.auth_button_group.addButton(self.digest_radio)
        self.auth_button_group.addButton(self.bearer_radio)

        # 라디오 버튼 연결
        self.digest_radio.toggled.connect(self.update_start_button_state)
        self.bearer_radio.toggled.connect(self.update_start_button_state)

        # 입력 필드 변경 시 버튼 상태 체크
        self.id_input.textChanged.connect(self.check_start_button_state)
        self.pw_input.textChanged.connect(self.check_start_button_state)

        section.setLayout(layout)

        return section

    def on_auth_type_changed(self):
        """인증 방식 변경 시 박스 스타일 업데이트"""
        if self.digest_radio.isChecked():
            # Digest Auth 선택됨
            self.digest_option.setStyleSheet("""
                QWidget {
                    background-color: #E9F6FE;
                    border: 1px solid #2B96ED;
                    border-radius: 8px;
                }
            """)
            # Bearer Token 선택 안됨
            self.bearer_option.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    border: 1px solid #CECECE;
                    border-radius: 8px;
                }
            """)
        else:
            # Bearer Token 선택됨
            self.bearer_option.setStyleSheet("""
                QWidget {
                    background-color: #E9F6FE;
                    border: 1px solid #2B96ED;
                    border-radius: 8px;
                }
            """)
            # Digest Auth 선택 안됨
            self.digest_option.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    border: 1px solid #CECECE;
                    border-radius: 8px;
                }
            """)

    def create_connection_section(self):
        """접속 정보 섹션 (타이틀 제외, 744x376px)"""
        section = QGroupBox()
        section.setFixedSize(744, 376)
        section.setStyleSheet("QGroupBox { border: none; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # URL 테이블 (744x370px) - 2개 컬럼 (행번호 + URL)
        self.url_table = QTableWidget(0, 2)  # 2개 컬럼: 행번호(50px) + URL(694px)
        self.url_table.setFixedSize(744, 370)
        self.url_table.setHorizontalHeaderLabels(["", "URL"])
        self.url_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.url_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.url_table.setSelectionMode(QAbstractItemView.NoSelection)  # 선택 비활성화 (이미지로 처리)

        # 헤더 설정
        header = self.url_table.horizontalHeader()
        header.setFixedHeight(31)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 행번호 컬럼: 고정
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # URL 컬럼: 전체 공간
        self.url_table.setColumnWidth(0, 50)  # 행번호 컬럼 50px

        # 왼쪽 행 번호 헤더 숨김 (컬럼 0으로 대체)
        vertical_header = self.url_table.verticalHeader()
        vertical_header.setVisible(False)

        # 세로 grid line 제거
        self.url_table.setShowGrid(False)

        # 행 높이 설정
        self.url_table.verticalHeader().setDefaultSectionSize(39)

        # 선택된 URL 행 추적 변수
        self.selected_url_row = None

        # 스타일 설정 (이미지 배경 방식 - setCellWidget 사용)
        self.url_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 19px;
                letter-spacing: -0.19px;
            }
            QTableWidget::item {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
            QTableWidget::item:selected {
                background-color: transparent;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                padding: 4px;
                height: 31px;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 600;
                letter-spacing: -0.18px;
            }
            QTableCornerButton::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
            }
        """)

        # cellClicked는 사용하지 않음 - ClickableLabel의 clicked 시그널 사용
        layout.addWidget(self.url_table)

        section.setLayout(layout)
        return section

    # ---------- 공통 기능 메서드들 ----------

    # ---------- 우측 패널 ----------
    # ========== 데드 코드: 2025-11-13 주석처리 ==========
    # 원래 설계: Digest Auth(ID/PW)와 Bearer Token(별도 필드)이 분리되어 있었음
    # 변경 후: 두 방식 모두 통합된 ID/Password 필드 사용으로 변경
    # 현재: create_auth_section() 메서드가 실제 사용됨 (info_GUI.py:1133)
    #
    # def create_right_panel(self):
    #     panel = QGroupBox("시험 입력 정보")
    #     layout = QVBoxLayout()
    #
    #     # 인증 방식
    #     auth_label = QLabel("사용자 인증 방식")
    #     auth_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
    #     layout.addWidget(auth_label)
    #
    #     # 라디오 버튼
    #     auth_radio_layout = QHBoxLayout()
    #     self.digest_radio = QRadioButton("Digest Auth")
    #     self.digest_radio.setChecked(True)
    #     self.bearer_radio = QRadioButton("Bearer Token")
    #     auth_radio_layout.addWidget(self.digest_radio)
    #     auth_radio_layout.addWidget(self.bearer_radio)
    #     auth_radio_layout.addStretch()
    #     layout.addLayout(auth_radio_layout)
    #
    #     # 공통 입력 필드
    #     common_row = QHBoxLayout()
    #     self.id_input = QLineEdit()
    #     self.pw_input = QLineEdit()
    #     common_row.addWidget(QLabel("ID:"))
    #     common_row.addWidget(self.id_input)
    #     common_row.addWidget(QLabel("PW:"))
    #     common_row.addWidget(self.pw_input)
    #     layout.addLayout(common_row)
    #
    #     # 연결
    #     self.digest_radio.toggled.connect(self.update_auth_fields)
    #     self.bearer_radio.toggled.connect(self.update_auth_fields)
    #     self.id_input.textChanged.connect(self.check_start_button_state)
    #     self.pw_input.textChanged.connect(self.check_start_button_state)
    #
    #     self.update_auth_fields()
    #
    #     panel.setLayout(layout)
    #     return panel
    # ========== 데드 코드 끝 ==========

    def create_bottom_buttons(self):
        """하단 버튼 바"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # 시험 시작 버튼
        self.start_btn = QPushButton("시험 시작")
        self.start_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        self.start_btn.clicked.connect(self.start_test)
        self.start_btn.setEnabled(True)  # 항상 활성화 (클릭 시 검증)
        layout.addWidget(self.start_btn)

        # 초기화 버튼
        self.reset_btn = QPushButton("초기화")
        self.reset_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        self.reset_btn.clicked.connect(self.reset_all_fields)
        layout.addWidget(self.reset_btn)

        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    # ---------- 동작 ----------
    def _on_start_clicked(self):
        self.update_start_button_state()
    
    def update_start_button_state(self):
        """시험 시작 버튼 상태 업데이트 (항상 활성화, 클릭 시 검증)"""
        try:
            # start_btn이 아직 생성되지 않았으면 건너뛰기
            if not hasattr(self, 'start_btn'):
                return

            # 항상 활성화 - 클릭 시 _check_required_fields()에서 검증
            self.start_btn.setEnabled(True)

        except Exception as e:
            print(f"버튼 상태 업데이트 실패: {e}")

    # 2025-11-13: update_auth_fields 메서드 제거
    # 호출하는 곳이 모두 주석처리되어 사용되지 않음
    # 실제 사용: update_start_button_state()가 대체 역할 수행
    #
    # def update_auth_fields(self):
    #     """인증 방식에 따른 필드 업데이트 (현재는 공통 필드 사용으로 별도 처리 없음)"""
    #     try:
    #         # 현재 UI 구조에서는 Digest Auth와 Bearer Token 모두 ID/PW 필드를 공통으로 사용
    #         # 나중에 인증 방식별로 다른 필드가 필요한 경우 여기에 로직 추가
    #         pass
    #
    #     except Exception as e:
    #         print(f"인증 필드 업데이트 실패: {e}")

    def start_scan(self):
        """실제 네트워크 스캔으로 사용 가능한 주소 탐지"""
        try:
            # target_system에 따라 분기 처리
            if hasattr(self, 'target_system') and self.target_system == "통합플랫폼시스템":
                # 통합플랫폼시스템: 네트워크 IP 검색
                if hasattr(self, 'test_port') and self.test_port:
                    ip_list = self._get_local_ip_list()

                    if not ip_list:
                        # IP 검색 실패 시 경고 및 직접 입력 안내
                        QMessageBox.warning(
                            self, "네트워크 IP 검색 실패",
                            "네트워크 IP 주소를 검색할 수 없습니다.\n\n"
                            "아래 '직접 입력' 기능을 사용하여 IP 주소를 수동으로 입력해주세요.\n"
                            "예: 192.168.1.1"
                        )
                        return

                    # ip:port 목록 생성
                    urls = [f"{ip}:{self.test_port}" for ip in dict.fromkeys(ip_list)]  # 중복 제거 유지 순서

                    print(f"통합플랫폼시스템 - API testPort 사용 (후보): {urls}")
                    self._populate_url_table(urls)
                    QMessageBox.information(
                        self, "주소 설정 완료",
                        "통합플랫폼시스템: 네트워크 IP로 주소 후보를 설정했습니다.\n"
                        f"후보: {', '.join(urls)}"
                    )
                else:
                    QMessageBox.warning(self, "경고", "testPort 정보가 없습니다.")
                return

            elif hasattr(self, 'target_system') and self.target_system == "물리보안시스템":
                # 물리보안시스템: ARP 스캔으로 동일 네트워크 IP 검색
                # 이미 스캔 중이면 중복 실행 방지
                if hasattr(self, 'arp_scan_thread') and self.arp_scan_thread and self.arp_scan_thread.isRunning():
                    QMessageBox.information(self, "알림", "이미 주소 탐색이 진행 중입니다.")
                    return

                # ARP Worker와 Thread 설정
                from PyQt5.QtCore import QThread

                self.arp_scan_worker = ARPScanWorker(test_port=self.test_port if hasattr(self, 'test_port') else None)
                self.arp_scan_thread = QThread()

                # Worker를 Thread로 이동
                self.arp_scan_worker.moveToThread(self.arp_scan_thread)

                # 시그널 연결
                self.arp_scan_worker.scan_completed.connect(self._on_arp_scan_completed)
                self.arp_scan_worker.scan_failed.connect(self._on_arp_scan_failed)
                self.arp_scan_thread.started.connect(self.arp_scan_worker.scan_arp)
                self.arp_scan_thread.finished.connect(self.arp_scan_thread.deleteLater)

                # 스레드 시작
                self.arp_scan_thread.start()
                QMessageBox.information(self, "ARP 스캔 시작", "동일 네트워크의 장비를 검색합니다.\n잠시만 기다려주세요...")
                return

            # 기타 시스템 또는 testPort가 없는 경우: 기존 네트워크 스캔 수행
            # 이미 스캔 중이면 중복 실행 방지
            if self.scan_thread and self.scan_thread.isRunning():
                QMessageBox.information(self, "알림", "이미 주소 탐색이 진행 중입니다.")
                return

            # Worker와 Thread 설정
            from PyQt5.QtCore import QThread

            self.scan_worker = NetworkScanWorker()
            self.scan_thread = QThread()

            # Worker를 Thread로 이동
            self.scan_worker.moveToThread(self.scan_thread)

            # 시그널 연결
            self.scan_worker.scan_completed.connect(self._on_scan_completed)
            self.scan_worker.scan_failed.connect(self._on_scan_failed)
            self.scan_thread.started.connect(self.scan_worker.scan_network)
            self.scan_thread.finished.connect(self.scan_thread.deleteLater)

            # 스레드 시작
            self.scan_thread.start()

        except Exception as e:
            print(f"주소 탐색 오류: {e}")
            QMessageBox.critical(self, "오류", f"네트워크 탐색 중 오류 발생:\n{str(e)}")

    def _on_scan_completed(self, urls):
        self._populate_url_table(urls)
        QMessageBox.information(self, "탐색 완료", "사용 가능한 주소를 찾았습니다.")

    def _on_scan_failed(self, msg):
        QMessageBox.warning(self, "주소 탐색 실패", msg)

    def _on_arp_scan_completed(self, urls):
        """ARP 스캔 완료 시 호출"""
        self._populate_url_table(urls)
        QMessageBox.information(
            self, "ARP 스캔 완료",
            f"동일 네트워크에서 {len(urls)}개의 장비를 찾았습니다.\n"
            f"발견된 주소: {', '.join(urls)}"
        )

    def _on_arp_scan_failed(self, msg):
        """ARP 스캔 실패 시 호출"""
        QMessageBox.warning(self, "ARP 스캔 실패", msg)

    def _populate_url_table(self, urls):
        """URL 테이블에 스캔 결과 채우기 (2컬럼: 행번호 + URL)"""
        try:
            self.url_table.setRowCount(0)
            self.selected_url_row = None

            # 이미지 경로 (Windows 경로 슬래시 변환)
            unchecked_img = resource_path("assets/image/test_config/url_row_checkbox_unchecked.png").replace(chr(92), "/")

            for i, url in enumerate(urls):
                row = self.url_table.rowCount()
                self.url_table.insertRow(row)

                # 컬럼 0: 행 번호 (ClickableLabel - 배경색으로 선택 표시)
                row_num_label = ClickableLabel(str(row + 1), row, 0)
                row_num_label.setAlignment(Qt.AlignCenter)
                row_num_label.setStyleSheet("""
                    QLabel {
                        background-color: #FFFFFF;
                        border: none;
                        border-bottom: 1px solid #CCCCCC;
                        font-family: 'Noto Sans KR';
                        font-size: 19px;
                        font-weight: 400;
                        color: #000000;
                    }
                """)
                row_num_label.clicked.connect(self.on_url_row_selected)
                self.url_table.setCellWidget(row, 0, row_num_label)

                # 컬럼 1: URL (ClickableLabel - 이미지 배경)
                url_label = ClickableLabel(url, row, 1)
                url_label.setAlignment(Qt.AlignCenter)
                url_label.setStyleSheet(f"""
                    QLabel {{
                        background-image: url('{unchecked_img}');
                        background-position: left center;
                        background-repeat: no-repeat;
                        border: none;
                        border-bottom: 1px solid #CCCCCC;
                        font-family: 'Noto Sans KR';
                        font-size: 19px;
                        font-weight: 400;
                        color: #000000;
                        margin: 0px;
                        padding: 0px;
                    }}
                """)
                url_label.setProperty("url", url)
                url_label.clicked.connect(self.on_url_row_selected)
                self.url_table.setCellWidget(row, 1, url_label)

                self.url_table.setRowHeight(row, 39)

        except Exception as e:
            self._show_scan_error(f"테이블 업데이트 중 오류:\n{str(e)}")
    
    def _show_scan_error(self, message):
        """스캔 오류 메시지 표시"""
        QMessageBox.warning(self, "주소 탐색 실패", message)

    def get_selected_url(self):
        """URL 테이블에서 선택된 URL 반환 (2컬럼 방식 - 컬럼 1에서 URL 가져오기)"""
        # 선택된 행 번호 확인
        if self.selected_url_row is not None:
            widget = self.url_table.cellWidget(self.selected_url_row, 1)  # 컬럼 1: URL
            if widget:
                selected_url = widget.property("url")
                if selected_url:
                    # http://가 없으면 추가
                    if not selected_url.startswith(('http://', 'https://')):
                        selected_url = f"https://{selected_url}"
                    return selected_url
        return None

    def _check_required_fields(self):
        """필수 입력 필드 검증 - 누락된 항목 리스트 반환"""
        missing_fields = []

        # 1. 인증 정보 확인 (공통 필드)
        if not self.id_input.text().strip():
            missing_fields.append("• 인증 ID")
        if not self.pw_input.text().strip():
            missing_fields.append("• 인증 PW")

        # 2. 접속 정보 확인
        if not self.get_selected_url():
            missing_fields.append("• 접속 URL 선택")

        return missing_fields

    def start_test(self):
        """시험 시작 - CONSTANTS.py 업데이트 후 검증 소프트웨어 실행"""
        # ===== 수정: PyInstaller 환경에서 CONSTANTS reload =====
        import sys
        import os
        if getattr(sys, 'frozen', False):
            # PyInstaller 환경 - sys.modules 삭제 후 재import
            if 'config.CONSTANTS' in sys.modules:
                del sys.modules['config.CONSTANTS']
            import config.CONSTANTS
            # 모듈 레벨 전역 변수 업데이트는 필요 없음 (여기서는 사용 안 함)
        else:
            # 로컬 환경에서는 기존 reload 사용
            if 'config.CONSTANTS' in sys.modules:
                importlib.reload(sys.modules['config.CONSTANTS'])  # sys.modules에서 모듈 객체를 가져와 reload
            else:
                import config.CONSTANTS  # 모듈이 없으면 새로 import
        # ===== 수정 끝 =====
        try:
            # 필수 입력 필드 검증
            missing_fields = self._check_required_fields()
            if missing_fields:
                message = "다음 정보를 입력해주세요:\n\n" + "\n".join(missing_fields)
                QMessageBox.warning(self, "입력 정보 부족", message)
                return

            # spec_id 추출 (testSpecs의 첫 번째 항목)
            if not self.test_specs or len(self.test_specs) == 0:
                QMessageBox.warning(self, "오류", "시험 시나리오 정보가 없습니다.")
                return

            # test_specs[0]이 딕셔너리인지 확인
            first_spec = self.test_specs[0]
            if isinstance(first_spec, dict):
                spec_id = first_spec.get("id", "")
            else:
                QMessageBox.warning(self, "오류", f"시험 시나리오 데이터 형식이 올바르지 않습니다: {type(first_spec)}")
                return

            # CONSTANTS.py 업데이트
            if self.form_validator.update_constants_py():
                # test_group_name, verification_type(current_mode), spec_id를 함께 전달
                print(f"시험 시작: testTarget.name={self.target_system}, verificationType={self.current_mode}, spec_id={spec_id}")
                self.startTestRequested.emit(self.target_system, self.current_mode, spec_id)
            else:
                QMessageBox.warning(self, "저장 실패", "CONSTANTS.py 업데이트에 실패했습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"시험 시작 중 오류가 발생했습니다:\n{str(e)}")    

    def check_start_button_state(self):
        """시험 시작 버튼 활성화 조건 체크 (항상 활성화, 클릭 시 검증)"""
        try:
            # 항상 활성화 - 클릭 시 _check_required_fields()에서 검증
            self.start_btn.setEnabled(True)

        except Exception as e:
            print(f"버튼 상태 체크 실패: {e}")
            self.start_btn.setEnabled(True)  # 오류 발생 시에도 활성화 유지


    def reset_all_fields(self):
        """모든 필드 초기화"""
        try:
            # 초기화할 내용이 있는지 확인
            if not self._has_data_to_reset():
                QMessageBox.information(self, "초기화", "초기화할 입력값이 없습니다.")
                return

            # 확인 메시지
            reply = QMessageBox.question(self, '초기화',
                                       '모든 입력값을 초기화하시겠습니까?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self._perform_reset()

        except Exception as e:
            QMessageBox.critical(self, "오류", f"초기화 중 오류가 발생했습니다:\n{str(e)}")

    def _has_data_to_reset(self):
        """초기화할 데이터가 있는지 확인"""
        try:
            # 기본 정보 필드에 입력값이 있는지 확인
            basic_fields = [
                self.company_edit.text().strip(),
                self.product_edit.text().strip(),
                self.version_edit.text().strip(),
                self.model_edit.text().strip(),
                self.test_category_edit.text().strip(),
                self.target_system_edit.text().strip(),
                self.test_group_edit.text().strip(),
                self.test_range_edit.text().strip(),
                self.admin_code_edit.text().strip()
            ]

            if any(field for field in basic_fields):
                return True

            # 테이블들에 데이터가 있는지 확인
            if self.test_field_table.rowCount() > 0 or self.scenario_table.rowCount() > 0 or self.api_test_table.rowCount() > 0:
                return True

            # 인증 정보에 입력값이 있는지 확인
            auth_fields = [
                self.id_input.text().strip(),
                self.pw_input.text().strip()
            ]

            if any(field for field in auth_fields):
                return True

            # 주소 입력창들에 입력값이 있는지 확인
            address_fields = [
                self.ip_input_edit.text().strip()
            ]

            if any(field for field in address_fields):
                return True

            # URL 테이블에 데이터가 있는지 확인
            if self.url_table.rowCount() > 0:
                return True

            return False

        except Exception as e:
            print(f"데이터 확인 중 오류: {e}")
            return True

    def _perform_reset(self):
        """실제 초기화 작업 수행"""
        try:
            # 기본 정보 필드 초기화
            self.company_edit.clear()
            self.product_edit.clear()
            self.version_edit.clear()
            self.model_edit.clear()
            self.test_category_edit.clear()
            self.target_system_edit.clear()
            self.test_group_edit.clear()
            self.test_range_edit.clear()
            self.admin_code_edit.clear()

            # 관리자 코드 필드를 초기 상태로 되돌림 (비활성화, placeholder 제거)
            self.admin_code_edit.setEnabled(False)
            self.admin_code_edit.setPlaceholderText("")

            # 테이블들 초기화
            self.test_field_table.setRowCount(0)
            self.scenario_table.setRowCount(0)
            self.api_test_table.setRowCount(0)

            # 시나리오 테이블 관련 UI 요소 초기화
            self.scenario_column_background.hide()
            self.scenario_placeholder_label.hide()

            # 인증 정보 초기화
            self.id_input.clear()
            self.pw_input.clear()

            # 인증 방식을 Digest Auth로 초기화
            self.digest_radio.setChecked(True)

            # 주소 입력창 초기화
            self.ip_input_edit.clear()

            # 주소 탐색 테이블 초기화
            self.url_table.setRowCount(0)

            # 현재 모드 초기화
            self.current_mode = None

            # 2025-11-13: update_auth_fields() 호출 제거
            # 이유: 인증 방식이 통합되면서 더 이상 필요 없음
            # 라디오 버튼 변경 시 update_start_button_state()가 자동으로 호출됨
            # self.update_auth_fields()

            # 버튼 상태 업데이트
            self.check_start_button_state()
            self.check_next_button_state()  # 다음 버튼 상태도 업데이트

            print("모든 필드 초기화 완료")
            QMessageBox.information(self, "초기화 완료", "모든 입력값이 초기화되었습니다.")

        except Exception as e:
            print(f"초기화 실패: {e}")
            raise

    def _determine_mode_from_api(self, test_data):
        """
        test-steps API 캐시에서 verificationType 추출하여 모드 결정

        Returns:
            str: "request" 또는 "response"
        """
        try:
            # testGroups에서 첫 번째 그룹의 testSpecs 가져오기
            test_groups = test_data.get("testRequest", {}).get("testGroups", [])
            if not test_groups:
                print("경고: testGroups 데이터가 없습니다. 기본값 'request' 사용")
                return "request"  # 기본값

            test_specs = test_groups[0].get("testSpecs", [])
            if not test_specs:
                print("경고: testSpecs 데이터가 없습니다. 기본값 'request' 사용")
                return "request"  # 기본값

            first_spec_id = test_specs[0].get("id")
            if not first_spec_id:
                print("경고: 첫 번째 spec_id를 찾을 수 없습니다. 기본값 'request' 사용")
                return "request"

            # form_validator의 캐시에서 steps 가져오기
            steps = self.form_validator._steps_cache.get(first_spec_id, [])
            if not steps:
                print(f"경고: spec_id={first_spec_id}에 대한 steps 캐시가 없습니다. 기본값 'request' 사용")
                return "request"

            first_step_id = steps[0].get("id")
            if not first_step_id:
                print("경고: 첫 번째 step_id를 찾을 수 없습니다. 기본값 'request' 사용")
                return "request"

            # test-step detail 캐시에서 verificationType 가져오기
            step_detail = self.form_validator._test_step_cache.get(first_step_id)
            if not step_detail:
                print(f"경고: step_id={first_step_id}에 대한 캐시가 없습니다. 기본값 'request' 사용")
                return "request"

            verification_type = step_detail.get("verificationType", "request")

            print(f"verificationType 추출 완료: {verification_type}")
            return verification_type

        except Exception as e:
            print(f"verificationType 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return "request"  # 기본값

    def on_load_test_info_clicked(self):
        """시험정보 불러오기 버튼 클릭 이벤트 (API 기반)"""
        # IP 입력창에서 IP 주소 가져오기
        ip_address = self.ip_input_edit.text().strip()

        if not ip_address:
            QMessageBox.warning(self, "경고", "주소를 입력해주세요.")
            return

        # IP 주소 형식 검증
        if not self._validate_ip_address(ip_address):
            QMessageBox.warning(self, "경고",
                "올바른 IP 주소 형식이 아닙니다.\n"
                "예: 192.168.1.1")
            return

        print(f"입력된 IP 주소: {ip_address}")

        # 로딩 팝업 생성 및 표시 (스피너 애니메이션 포함)
        loading_popup = LoadingPopup(width=400, height=200)
        loading_popup.update_message("시험 정보 불러오는 중...", "잠시만 기다려주세요")
        loading_popup.show()

        # UI 즉시 업데이트를 위한 이벤트 루프 처리
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

        try:

            # API 호출하여 시험 정보 가져오기
            test_data = self.form_validator.fetch_test_info_by_ip(ip_address)

            if not test_data:
                QMessageBox.warning(self, "경고",
                    "시험 정보를 불러올 수 없습니다.\n"
                    "- 서버 연결을 확인해주세요.\n"
                    "- IP 주소에 해당하는 시험 요청이 있는지 확인해주세요.")
                return

            # 1페이지 필드 채우기
            eval_target = test_data.get("testRequest", {}).get("evaluationTarget", {})
            test_groups = test_data.get("testRequest", {}).get("testGroups", [])


            test_groups = test_data.get("testRequest", {}).get("testGroups", [])


            # testGroups 배열 처리
            if not test_groups:
                QMessageBox.warning(self, "경고", "testGroups 데이터가 비어있습니다.")
                return

            # 여러 그룹의 이름을 콤마로 연결
            group_names = [g.get("name", "") for g in test_groups]
            combined_group_names = ", ".join(group_names)

            # 여러 그룹의 testRange를 콤마로 연결
            group_ranges = [g.get("testRange", "") for g in test_groups]
            combined_group_ranges = ", ".join(group_ranges)

            # 원본 시험범위 값 저장
            self.original_test_range = combined_group_ranges

            self.company_edit.setText(eval_target.get("companyName", ""))
            self.product_edit.setText(eval_target.get("productName", ""))
            self.version_edit.setText(eval_target.get("version", ""))
            self.model_edit.setText(eval_target.get("modelName", ""))
            self.test_category_edit.setText(eval_target.get("testCategory", ""))

            self.target_system = eval_target.get("targetSystem", "")
            if self.target_system == "PHYSICAL_SECURITY":
                self.target_system = "물리보안시스템"
            elif self.target_system == "INTEGRATED_SYSTEM":
                self.target_system = "통합플랫폼시스템"
            self.target_system_edit.setText(self.target_system)

            self.test_group_edit.setText(combined_group_names)  # 콤마로 연결된 그룹 이름들

            # 시험범위를 UI용 텍스트로 변환하여 표시
            display_test_range = combined_group_ranges
            if combined_group_ranges == "ALL_FIELDS":
                display_test_range = "전체필드"
            elif combined_group_ranges:
                display_test_range = "필수필드"
            self.test_range_edit.setText(display_test_range)

            self.contact_person = eval_target.get("contactPerson", "")
            self.model_name = eval_target.get("modelName", "")
            self.request_id = test_data.get("testRequest", {}).get("id", {})

            # 모든 testGroups 저장 (시험 시작 시 사용)
            self.test_groups = test_groups  # 전체 그룹 배열 저장
            self.test_group_id = test_groups[0].get("id", "") if test_groups else ""  # 첫 번째 그룹 ID
            self.test_group_name = test_groups[0].get("name", "") if test_groups else ""  # 첫 번째 그룹 이름
            print(f"testGroups 저장: {len(test_groups)}개 그룹, 첫 번째 id={self.test_group_id}, name={self.test_group_name}")

            # 모든 그룹의 testSpecs를 합침 (2페이지에서 사용)
            all_test_specs = []
            for group in test_groups:
                all_test_specs.extend(group.get("testSpecs", []))

            self.test_specs = all_test_specs
            self.test_port = test_data.get("schedule", {}).get("testPort", None)

            # testPort 기반 WEBHOOK_PORT 업데이트
            if self.test_port:
                # 1. 메모리상의 값 업데이트
                CONSTANTS.WEBHOOK_PORT = self.test_port + 1
                CONSTANTS.WEBHOOK_URL = f"https://{CONSTANTS.WEBHOOK_PUBLIC_IP}:{CONSTANTS.WEBHOOK_PORT}"

                # 2. CONSTANTS.py 파일 자체도 수정
                try:
                    import re
                    import sys
                    import os
                    from core.functions import resource_path

                    # CONSTANTS.py 파일 경로 설정
                    if getattr(sys, 'frozen', False):
                        exe_dir = os.path.dirname(sys.executable)
                        constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
                    else:
                        constants_path = resource_path("config/CONSTANTS.py")

                    # 파일 읽기
                    with open(constants_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # WEBHOOK_PORT = 숫자 패턴 찾아서 치환
                    pattern_port = r'^WEBHOOK_PORT\s*=\s*\d+.*$'
                    new_port_line = f'WEBHOOK_PORT = {self.test_port + 1}       # 웹훅 수신 포트'
                    content = re.sub(pattern_port, new_port_line, content, flags=re.MULTILINE)

                    # 파일 저장
                    with open(constants_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    print(f"WEBHOOK_PORT 업데이트 완료: {CONSTANTS.WEBHOOK_PORT} (testPort: {self.test_port})")
                    print(f"  - 메모리: {CONSTANTS.WEBHOOK_PORT}")
                    print(f"  - 파일: CONSTANTS.py 수정 완료")

                except Exception as e:
                    print(f"CONSTANTS.py 파일 수정 실패: {e}")
                    # 파일 수정 실패해도 메모리상의 값은 이미 업데이트되었으므로 계속 진행

            # verificationType 기반 모드 설정 (API 기반)
            self.current_mode = self._determine_mode_from_api(test_data)

            # API 데이터를 이용하여 OPT 파일 로드 및 스키마 생성
            self.form_validator.load_opt_files_from_api(test_data)

            # 플랫폼 검증일 경우 Authentication 정보 자동 입력
            self.auto_fill_authentication_for_platform()

            # 다음 버튼 상태 업데이트
            self.check_next_button_state()

        except Exception as e:
            print(f"시험정보 불러오기 실패: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"시험 정보를 불러오는 중 오류가 발생했습니다:\n{str(e)}")

        finally:
            # 로딩 팝업 닫기 (성공/실패 여부와 관계없이 항상 실행)
            loading_popup.close()

    def auto_fill_authentication_for_platform(self):
        """
        플랫폼 검증일 경우 Authentication 정보를 자동으로 채우고 필드를 disabled 상태로 설정
        """
        try:
            # 플랫폼 검증인지 확인
            if not hasattr(self, 'target_system') or self.target_system != "통합플랫폼시스템":
                print("[INFO] 시스템 검증이므로 Authentication 자동 입력을 건너뜁니다.")
                # 시스템 검증일 경우 필드를 활성화하고 비워둠
                self.id_input.setEnabled(True)
                self.pw_input.setEnabled(True)
                self.id_input.clear()
                self.pw_input.clear()
                return

            print("[INFO] 플랫폼 검증 감지 - Authentication 자동 입력을 시도합니다.")

            # test_specs에서 첫 번째 spec_id 가져오기
            if not hasattr(self, 'test_specs') or not self.test_specs:
                print("[WARNING] test_specs가 없어서 Authentication 자동 입력을 건너뜁니다.")
                return

            first_spec = self.test_specs[0]
            spec_id = first_spec.get("id", "")

            if not spec_id:
                print("[WARNING] spec_id를 찾을 수 없어서 Authentication 자동 입력을 건너뜁니다.")
                return

            print(f"[INFO] spec_id={spec_id}로 Authentication 정보를 추출합니다.")

            # FormValidator의 get_authentication_credentials 메서드 호출
            user_id, password = self.form_validator.get_authentication_credentials(spec_id)

            if user_id and password:
                # 필드에 값 설정
                self.id_input.setText(user_id)
                self.pw_input.setText(password)

                # 필드를 disabled 상태로 설정
                self.id_input.setEnabled(False)
                self.pw_input.setEnabled(False)

                print(f"[SUCCESS] 플랫폼 검증: Authentication 자동 입력 완료 (User ID={user_id})")
                print(f"[INFO] id_input과 pw_input 필드가 disabled 상태로 설정되었습니다.")
            else:
                print("[WARNING] Authentication 정보를 찾을 수 없습니다. 필드를 활성화합니다.")
                # Authentication 정보가 없으면 필드를 활성화
                self.id_input.setEnabled(True)
                self.pw_input.setEnabled(True)

        except Exception as e:
            print(f"[ERROR] Authentication 자동 입력 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            # 오류 발생 시 필드를 활성화
            self.id_input.setEnabled(True)
            self.pw_input.setEnabled(True)

    def on_management_url_changed(self):
        """관리자시스템 주소 변경 시 처리"""
        try:
            new_url = self.management_url_edit.text().strip()
            if new_url:
                # CONSTANTS에 저장 (메모리 + config.txt 파일)
                success = CONSTANTS.save_management_url(new_url)
                if success:
                    print(f"관리자시스템 주소가 업데이트되었습니다: {new_url}")
                else:
                    print("관리자시스템 주소 저장에 실패했습니다.")
        except Exception as e:
            print(f"관리자시스템 주소 변경 처리 실패: {e}")

    def _validate_ip_address(self, ip):
        """IP 주소 형식 검증"""
        # IP 주소 정규식 패턴
        ip_pattern = re.compile(
            r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        return bool(ip_pattern.match(ip))

    def get_local_ip(self):
        """로컬 네트워크 IP 주소 가져오기"""
        import socket

        ip_list = []

        try:
            # socket을 사용하여 로컬 IP 확인
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip and not local_ip.startswith('127.'):
                ip_list.append(local_ip)
        except Exception as e:
            print(f"socket을 사용한 IP 검색 실패: {e}")

        # 위 방법 실패 시 호스트명으로 IP 가져오기
        if not ip_list:
            try:
                hostname_ip = socket.gethostbyname(socket.gethostname())
                if hostname_ip and not hostname_ip.startswith('127.'):
                    ip_list.append(hostname_ip)
            except Exception as e2:
                print(f"hostname을 사용한 IP 검색 실패: {e2}")

        # 중복 제거
        ip_list = list(dict.fromkeys(ip_list))

        print(f"검색된 네트워크 IP 목록: {ip_list}")

        # 리스트를 쉼표로 구분된 문자열로 반환
        if ip_list:
            return ", ".join(ip_list)
        else:
            return None

    def _get_local_ip_list(self):
        """get_local_ip() 결과를 안전하게 리스트로 변환 (최대 3개)"""
        raw = self.get_local_ip()
        ip_list = []

        if isinstance(raw, str):
            ip_list = [ip.strip() for ip in raw.split(',') if ip.strip()]
        elif isinstance(raw, (list, tuple, set)):
            ip_list = [str(ip).strip() for ip in raw if str(ip).strip()]

        # 최대 3개만 반환
        return ip_list[:3]

    def check_next_button_state(self):
        """첫 번째 페이지의 다음 버튼 활성화 조건 체크"""
        try:
            if hasattr(self, 'next_btn'):
                # 다음 버튼은 항상 활성화 (클릭 시 검증)
                self.next_btn.setEnabled(True)
        except Exception as e:
            print(f"다음 버튼 상태 체크 실패: {e}")

    def _is_page1_complete(self):
        """첫 번째 페이지 완료 조건 검사"""
        try:
            # 1. 모드 선택 확인 (불러오기 버튼 중 하나를 눌렀는지)
            if not self.current_mode:
                return False

            # 2. 시험 기본 정보 모든 필드 입력 확인
            basic_info_filled = all([
                self.company_edit.text().strip(),
                self.product_edit.text().strip(),
                self.version_edit.text().strip(),
                self.model_edit.text().strip(),
                self.test_category_edit.text().strip(),
                self.target_system_edit.text().strip(),
                self.test_group_edit.text().strip(),
                self.test_range_edit.text().strip()
            ])

            # 3. 관리자 코드 유효성 확인
            admin_code_valid = self.form_validator.is_admin_code_valid()

            # 4. 시험 시나리오명 테이블에 데이터가 있는지 확인
            test_field_filled = self.test_field_table.rowCount() > 0

            # 모든 조건이 충족되면 완료
            return basic_info_filled and admin_code_valid and test_field_filled

        except Exception as e:
            print(f"페이지 완료 조건 체크 실패: {e}")
            return False

    def on_test_field_selected(self, row, col):
        """시험 분야 테이블 클릭 시 시나리오 테이블 업데이트"""
        try:
            # 클릭된 행 번호 저장
            self.selected_test_field_row = row

            # 선택된 그룹명 가져오기 (위젯에서 가져오기)
            selected_widget = self.test_field_table.cellWidget(row, 0)
            if selected_widget:
                group_name = selected_widget.text()
                # 해당 그룹의 시나리오들을 시나리오 테이블에 채우기
                self.form_validator._fill_scenarios_for_group(row, group_name)

            # 테이블 강제 업데이트
            self.test_field_table.viewport().update()
            self.scenario_table.viewport().update()

            # API 테이블 초기 메시지로 리셋
            self.form_validator._show_initial_api_message()

        except Exception as e:
            print(f"시험 분야 선택 처리 실패: {e}")
            QMessageBox.warning(self, "오류", f"시험 분야 데이터 로드 중 오류가 발생했습니다:\n{str(e)}")

    def on_scenario_selected(self, row, col):
        """시나리오 테이블 클릭 시 체크박스 이미지 변경 및 API 테이블 업데이트"""
        try:
            # 모든 시나리오 행의 배경 이미지 업데이트
            for i in range(self.scenario_table.rowCount()):
                widget = self.scenario_table.cellWidget(i, 0)
                if widget:
                    if i == row:
                        # 클릭된 행: 체크된 이미지로 변경
                        widget.setStyleSheet("""
                            QLabel {
                                background-image: url('assets/image/test_config/row_checkbox_checked.png');
                                background-position: center;
                                background-repeat: no-repeat;
                                border: none;
                                border-bottom: 1px solid #CCCCCC;
                                font-family: 'Noto Sans KR';
                                font-size: 19px;
                                font-weight: 400;
                                color: #000000;
                                margin: 0px;
                                padding: 0px;
                                min-width: 371.5px;
                                min-height: 39px;
                            }
                        """)
                    else:
                        # 나머지 행: 체크 안 된 이미지로 변경
                        widget.setStyleSheet("""
                            QLabel {
                                background-image: url('assets/image/test_config/row_checkbox_unchecked.png');
                                background-position: center;
                                background-repeat: no-repeat;
                                border: none;
                                border-bottom: 1px solid #CCCCCC;
                                font-family: 'Noto Sans KR';
                                font-size: 19px;
                                font-weight: 400;
                                color: #000000;
                                margin: 0px;
                                padding: 0px;
                                min-width: 371.5px;
                                min-height: 39px;
                            }
                        """)

            # UI 업데이트 강제 (체크박스 이미지가 먼저 보이도록)
            QApplication.processEvents()

            # specifications API 호출하여 API 테이블 채우기
            self.form_validator._fill_api_table_for_selected_field_from_api(row)

        except Exception as e:
            print(f"시나리오 선택 처리 실패: {e}")
            QMessageBox.warning(self, "오류", f"시나리오 데이터 로드 중 오류가 발생했습니다:\n{str(e)}")

    def toggle_address_popover(self):
        """주소 추가 팝오버 표시/숨김 토글"""
        if self.address_popover.isVisible():
            self.address_popover.hide()
            self.add_btn.setChecked(False)
        else:
            # 추가 버튼의 전역 좌표를 가져옴
            btn_global_pos = self.add_btn.mapToGlobal(self.add_btn.rect().bottomLeft())
            # InfoWidget의 전역 좌표를 가져와서 상대 좌표로 변환
            widget_global_pos = self.mapToGlobal(self.rect().topLeft())
            relative_x = btn_global_pos.x() - widget_global_pos.x()
            relative_y = btn_global_pos.y() - widget_global_pos.y()

            # 팝오버를 오른쪽 정렬 (추가 버튼 오른쪽 끝 기준)
            popover_x = relative_x + self.add_btn.width() - self.address_popover.width()
            popover_y = relative_y + 4  # 버튼 아래 4px gap

            # 팝오버 위치 설정
            self.address_popover.move(popover_x, popover_y)
            self.address_popover.raise_()  # 최상위로 올림
            self.address_popover.show()
            self.add_btn.setChecked(True)
            self.address_input.setFocus()  # 입력창에 포커스

    def add_address_from_popover(self):
        """팝오버에서 IP 주소 추가 (2컬럼: 행번호 + URL)"""
        try:
            # 입력값 가져오기
            ip_port = self.address_input.text().strip()

            if not ip_port:
                QMessageBox.warning(self, "입력 오류", "IP 주소를 입력해주세요.\n예: 192.168.1.1")
                return

            # Port 포함 여부 확인 - Port는 입력하지 않아야 함
            if ':' in ip_port:
                QMessageBox.warning(self, "입력 오류", "IP 주소만 입력해주세요.\nPort는 시험정보의 testPort로 자동 설정됩니다.\n예: 192.168.1.1")
                return

            # IP 검증
            if not self._validate_ip_address(ip_port):
                QMessageBox.warning(self, "IP 오류", "올바른 IP 주소를 입력해주세요.\n예: 192.168.1.100")
                return

            # testPort 확인 및 자동 추가
            if not hasattr(self, 'test_port') or not self.test_port:
                QMessageBox.warning(self, "testPort 없음", "시험정보를 먼저 불러와주세요.\ntestPort 정보가 필요합니다.")
                return

            # IP와 testPort 결합
            final_url = f"{ip_port}:{self.test_port}"

            # 중복 확인 (컬럼 1의 ClickableLabel에서 url property 가져오기)
            for row in range(self.url_table.rowCount()):
                widget = self.url_table.cellWidget(row, 1)
                if widget and widget.property("url") == final_url:
                    QMessageBox.information(self, "알림", "이미 추가된 주소입니다.")
                    return

            # 이미지 경로 (Windows 경로 슬래시 변환)
            unchecked_img = resource_path("assets/image/test_config/url_row_checkbox_unchecked.png").replace(chr(92), "/")

            # 테이블에 추가
            row = self.url_table.rowCount()
            self.url_table.insertRow(row)

            # 컬럼 0: 행 번호 (ClickableLabel - 배경색으로 선택 표시)
            row_num_label = ClickableLabel(str(row + 1), row, 0)
            row_num_label.setAlignment(Qt.AlignCenter)
            row_num_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: none;
                    border-bottom: 1px solid #CCCCCC;
                    font-family: 'Noto Sans KR';
                    font-size: 19px;
                    font-weight: 400;
                    color: #000000;
                }
            """)
            row_num_label.clicked.connect(self.on_url_row_selected)
            self.url_table.setCellWidget(row, 0, row_num_label)

            # 컬럼 1: URL (ClickableLabel - 이미지 배경)
            url_label = ClickableLabel(final_url, row, 1)
            url_label.setAlignment(Qt.AlignCenter)
            url_label.setStyleSheet(f"""
                QLabel {{
                    background-image: url('{unchecked_img}');
                    background-position: left center;
                    background-repeat: no-repeat;
                    border: none;
                    border-bottom: 1px solid #CCCCCC;
                    font-family: 'Noto Sans KR';
                    font-size: 19px;
                    font-weight: 400;
                    color: #000000;
                    margin: 0px;
                    padding: 0px;
                }}
            """)
            url_label.setProperty("url", final_url)
            url_label.clicked.connect(self.on_url_row_selected)
            self.url_table.setCellWidget(row, 1, url_label)

            self.url_table.setRowHeight(row, 39)

            # 입력창 초기화
            self.address_input.clear()

            # 팝오버 닫기
            self.address_popover.hide()
            self.add_btn.setChecked(False)

            QMessageBox.information(self, "추가 완료", f"주소가 추가되었습니다.\n{final_url}")

        except Exception as e:
            print(f"IP 추가 오류: {e}")
            QMessageBox.critical(self, "오류", f"주소 추가 중 오류가 발생했습니다:\n{str(e)}")

    def on_url_row_selected(self, row, col):
        """URL 테이블 행 클릭 시 두 컬럼 모두 스타일 변경 (2컬럼 방식)"""
        try:
            # 이미지 경로 (Windows 경로 슬래시 변환)
            checked_img = resource_path("assets/image/test_config/url_row_checkbox_checked.png").replace(chr(92), "/")
            unchecked_img = resource_path("assets/image/test_config/url_row_checkbox_unchecked.png").replace(chr(92), "/")

            # 모든 URL 행의 스타일 업데이트
            for i in range(self.url_table.rowCount()):
                row_num_widget = self.url_table.cellWidget(i, 0)  # 행 번호 컬럼
                url_widget = self.url_table.cellWidget(i, 1)  # URL 컬럼

                if i == row:
                    # 클릭된 행: 선택 스타일 적용
                    if row_num_widget:
                        row_num_widget.setStyleSheet("""
                            QLabel {
                                background-color: #E3F2FF;
                                border: none;
                                border-bottom: 1px solid #CCCCCC;
                                font-family: 'Noto Sans KR';
                                font-size: 19px;
                                font-weight: 400;
                                color: #000000;
                            }
                        """)
                    if url_widget:
                        url_widget.setStyleSheet(f"""
                            QLabel {{
                                background-image: url('{checked_img}');
                                background-position: left center;
                                background-repeat: no-repeat;
                                border: none;
                                border-bottom: 1px solid #CCCCCC;
                                font-family: 'Noto Sans KR';
                                font-size: 19px;
                                font-weight: 400;
                                color: #000000;
                                margin: 0px;
                                padding: 0px;
                            }}
                        """)
                else:
                    # 나머지 행: 기본 스타일 적용
                    if row_num_widget:
                        row_num_widget.setStyleSheet("""
                            QLabel {
                                background-color: #FFFFFF;
                                border: none;
                                border-bottom: 1px solid #CCCCCC;
                                font-family: 'Noto Sans KR';
                                font-size: 19px;
                                font-weight: 400;
                                color: #000000;
                            }
                        """)
                    if url_widget:
                        url_widget.setStyleSheet(f"""
                            QLabel {{
                                background-image: url('{unchecked_img}');
                                background-position: left center;
                                background-repeat: no-repeat;
                                border: none;
                                border-bottom: 1px solid #CCCCCC;
                                font-family: 'Noto Sans KR';
                                font-size: 19px;
                                font-weight: 400;
                                color: #000000;
                                margin: 0px;
                                padding: 0px;
                            }}
                        """)

            # 선택된 행 추적
            self.selected_url_row = row

            # UI 업데이트 강제
            QApplication.processEvents()

            # 시작 버튼 상태 체크
            self.check_start_button_state()

        except Exception as e:
            print(f"URL 행 선택 처리 실패: {e}")
