from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QCheckBox,
    QStackedWidget, QRadioButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor
import importlib
import re
from config import CONSTANTS
from core.functions import resource_path

# 분리된 모듈들 import
from network_scanner import NetworkScanWorker, ARPScanWorker
from form_validator import FormValidator
from core.functions import resource_path
import importlib
import config.CONSTANTS as CONSTANTS


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

    def create_page1(self):
        """첫 번째 페이지: 시험 정보 확인"""
        page = QWidget()

        # 배경 이미지 설정
        bg_path = resource_path("assets/image/test_info/bg.png").replace(chr(92), "/")
        page.setStyleSheet(f"""
            #page1 {{
                background-image: url({bg_path});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)
        page.setObjectName("page1")

        # 페이지 크기 설정
        page.setFixedSize(1680, 1032)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        layout.setSpacing(0)  # 간격 제거

        # 상단 헤더 영역 (1680x56px)
        header_widget = QWidget(page)
        header_widget.setFixedSize(1680, 56)
        header_widget.setGeometry(0, 0, 1680, 56)  # 절대 좌표로 최상단에 고정

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header_layout.setSpacing(8)

        # 헤더 로고 (36x36px)
        logo_label = QLabel(header_widget)
        logo_pixmap = QPixmap(resource_path("assets/image/test_info/header_logo.png"))
        logo_label.setPixmap(logo_pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(36, 36)
        header_layout.addWidget(logo_label)

        # 헤더 텍스트 이미지 (301x36px)
        header_txt_label = QLabel(header_widget)
        header_txt_pixmap = QPixmap(resource_path("assets/image/test_info/header_txt.png"))
        header_txt_label.setPixmap(header_txt_pixmap.scaled(301, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_txt_label.setFixedSize(301, 36)
        header_layout.addWidget(header_txt_label)

        # 시험 기본 정보 (수평 중앙 정렬)
        info_panel = self.create_basic_info_panel()
        layout.addWidget(info_panel, alignment=Qt.AlignHCenter)

        # 하단 여백 24px (디자이너 요구사항)
        layout.addSpacing(24)

        page.setLayout(layout)

        # 배경 일러스트 이미지 추가 (bg-illust.png) - 레이아웃 설정 후 추가
        illust_label = QLabel(page)
        illust_pixmap = QPixmap(resource_path("assets/image/test_info/bg-illust.png"))
        illust_label.setPixmap(illust_pixmap)
        illust_label.setScaledContents(True)
        # 페이지 전체 크기로 설정하여 bg.png 위에 표시
        illust_label.setGeometry(0, 0, 1680, 1032)
        illust_label.lower()  # 다른 위젯들 뒤로 배치 (하지만 bg.png 앞에)
        illust_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # 마우스 이벤트 통과

        # 헤더를 최상위로 올림
        header_widget.raise_()

        return page

    def create_page2(self):
        """두 번째 페이지: 시험 설정"""
        page = QWidget()
        page.setObjectName("page2")

        # 페이지 크기 설정
        page.setFixedSize(1680, 1032)

        # 배경 이미지 설정 (bg.png)
        bg_path2 = resource_path("assets/image/test_config/bg.png").replace(chr(92), "/")
        page.setStyleSheet(f"""
            #page2 {{
                background-image: url({bg_path2});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 헤더 영역 (1632x56px)
        header_container = QWidget()
        header_container.setFixedSize(1680, 56)
        header_container_layout = QHBoxLayout()
        header_container_layout.setContentsMargins(24, 0, 24, 0)
        header_container_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedSize(1632, 56)

        # 헤더 레이아웃 (로고 + 텍스트는 나중에 추가)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        header_layout.setSpacing(8)

        # TODO: 헤더 로고와 텍스트 추가 예정

        header_container_layout.addWidget(header_widget)
        header_container.setLayout(header_container_layout)

        layout.addWidget(header_container)

        # 콘텐츠 영역 (1680x976px, Fill: #F5F5F5, Padding: 48px 0px 48px 44px)
        content_widget = QWidget()
        content_widget.setFixedSize(1680, 976)
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
            }
        """)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(48, 0, 48, 44)  # 좌, 상, 우, 하
        content_layout.setSpacing(0)

        # 기존 콘텐츠 (좌우 패널)
        main_layout = QHBoxLayout()

        # 좌측 패널 (792x932px, padding: 24px 28px 24px 80px)
        left_panel = QGroupBox()
        left_panel.setFixedSize(792, 932)
        left_panel.setStyleSheet("QGroupBox { border: none; }")

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(24, 28, 24, 80)  # 좌, 상, 우, 하
        left_layout.setSpacing(0)

        # 타이틀 영역 (744x66px)
        title_widget = QWidget()
        title_widget.setFixedSize(744, 66)
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        # 첫 번째 줄: "시험 시나리오 및 API"
        title_line1 = QLabel("시험 시나리오 및 API(미정)")
        title_line1.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_line1)

        # 두 번째 줄: "시험 시나리오 및 API 정보를 확인하세요"
        title_line2 = QLabel("시험 시나리오 및 API 정보를 확인하세요(미정)")
        title_line2.setStyleSheet("font-size: 14px;")
        title_layout.addWidget(title_line2)

        title_widget.setLayout(title_layout)
        left_layout.addWidget(title_widget)

        # 시험 시나리오명 테이블 (QGroupBox로 감싸기)
        field_group = self.create_test_field_group()
        left_layout.addWidget(field_group)

        # 시험 시나리오와 시험 API 사이 간격 12px
        left_layout.addSpacing(12)

        # 시험 API 테이블 (QGroupBox로 감싸기)
        api_group = self.create_test_api_group()
        left_layout.addWidget(api_group)

        left_panel.setLayout(left_layout)

        # 우측 패널 (792x932px, padding: 24px 28px 24px 80px)
        right_panel = QGroupBox()
        right_panel.setFixedSize(792, 932)
        right_panel.setStyleSheet("QGroupBox { border: none; }")

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(24, 28, 24, 24)  # 좌, 상, 우, 하 (하단 padding 조정)
        right_layout.setSpacing(0)

        # 타이틀 영역 (744x66px)
        title_widget = QWidget()
        title_widget.setFixedSize(744, 66)
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        # 첫 번째 줄: "시험 설정 정보"
        title_line1 = QLabel("시험 설정 정보(미정)")
        title_line1.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_line1)

        # 두 번째 줄: "시험 설정 정보를 입력하세요"
        title_line2 = QLabel("시험 설정 정보를 입력하세요(미정)")
        title_line2.setStyleSheet("font-size: 14px;")
        title_layout.addWidget(title_line2)

        title_widget.setLayout(title_layout)
        right_layout.addWidget(title_widget)

        # 기존 우측 패널 내용
        auth_section = self.create_auth_section()
        right_layout.addWidget(auth_section)

        # 사용자 인증방식과 접속 주소 탐색 사이 12px gap
        right_layout.addSpacing(12)

        connection_section = self.create_connection_section()
        right_layout.addWidget(connection_section)

        # URL 테이블과 버튼 사이 32px gap
        right_layout.addSpacing(32)

        # 하단 버튼 (초기화, 시험시작) - 각 364x48px, gap 20px
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)  # 버튼 간격 20px

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

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)

        content_layout.addLayout(main_layout, 1)

        content_widget.setLayout(content_layout)

        # 메인 레이아웃에 콘텐츠 영역 추가
        layout.addWidget(content_widget)

        page.setLayout(layout)

        return page

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

        # 패널 크기 및 스타일 설정 (864x830px, padding: 46 48 58 48, corner radius: 4px)
        panel.setFixedSize(864, 830)
        panel.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(48, 46, 48, 58)  # 좌우 48px, 상단 46px, 하단 58px
        layout.setSpacing(0)

        # 타이틀 박스 (768x66px)
        title_box = QWidget()
        title_box.setFixedSize(768, 66)
        title_box.setStyleSheet("""
            QWidget {
                padding: 0px 0px 4px 0px;
            }
        """)
        title_box_layout = QHBoxLayout()
        title_box_layout.setContentsMargins(0, 0, 0, 4)  # padding: 0 0 4 0
        title_box_layout.setSpacing(0)

        # 타이틀 영역 (570x62px)
        title_area = QWidget()
        title_area.setFixedSize(570, 62)
        title_area_layout = QVBoxLayout()
        title_area_layout.setContentsMargins(0, 0, 0, 0)
        title_area_layout.setSpacing(8)  # gap 8px

        # 1. 타이틀 (시험 기본 정보) - 32px 높이
        title_label = QLabel("시험 기본 정보")
        title_label.setFixedHeight(32)
        title_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 22px;
                font-weight: 500;
                letter-spacing: -0.88px;
            }
        """)
        title_area_layout.addWidget(title_label)

        # 2. 내용 (시험 기본 정보 확인과 관리자 코드를 입력하세요.) - 22px 높이
        description_label = QLabel("시험 기본 정보 확인과 관리자 코드를 입력하세요.")
        description_label.setFixedHeight(22)
        description_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 15px;
                font-weight: 300;
                letter-spacing: -0.6px;
            }
        """)
        title_area_layout.addWidget(description_label)

        title_area.setLayout(title_area_layout)
        title_box_layout.addWidget(title_area)

        # IP 입력창
        self.ip_input_edit = QLineEdit()
        self.ip_input_edit.setFixedSize(200, 40)
        self.ip_input_edit.setPlaceholderText("주소를 입력해주세요.")
        self.ip_input_edit.setStyleSheet("""
            QLineEdit {
                font-family: 'Noto Sans KR';
                font-size: 14px;
                padding: 8px 12px;
                border: 1px solid #CECECE;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
            }
        """)
        title_box_layout.addWidget(self.ip_input_edit, alignment=Qt.AlignVCenter)

        title_box_layout.addStretch()

        # 버튼/불러오기 (198x62px) - 이미지 버튼
        self.load_test_info_btn = QPushButton()
        self.load_test_info_btn.setFixedSize(198, 62)

        # 한글 경로 처리를 위한 절대 경로 사용
        import os
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
        title_box_layout.addWidget(self.load_test_info_btn)

        title_box.setLayout(title_box_layout)
        layout.addWidget(title_box, alignment=Qt.AlignCenter)

        # 디바이더 (구분선) - line weight: 1, color: #E8E8E8
        divider = QLabel()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #E8E8E8;")
        layout.addWidget(divider)

        # 디바이더와 폼 사이 간격 12px
        layout.addSpacing(12)

        # 인풋박스 컨테이너 (768x552px)
        input_container = QWidget()
        input_container.setFixedSize(768, 552)
        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)

        # 기업명 필드 (768x82px - 전체 너비) - 이미지 배경 사용
        company_field = self.create_readonly_input_field("기업명", 768)
        self.company_edit = company_field["input"]
        self.company_edit.setReadOnly(True)  # 읽기 전용
        input_layout.addWidget(company_field["widget"])

        # 제품명 필드 (768x82px - 전체 너비) - 이미지 배경 사용
        product_field = self.create_readonly_input_field("제품명", 768)
        self.product_edit = product_field["input"]
        self.product_edit.setReadOnly(True)  # 읽기 전용
        input_layout.addWidget(product_field["widget"])

        # 버전, 모델명 행 (768x82px) - 이미지 배경 사용
        version_model_row = QWidget()
        version_model_row.setFixedSize(768, 82)
        version_model_layout = QHBoxLayout()
        version_model_layout.setContentsMargins(0, 0, 0, 0)
        version_model_layout.setSpacing(20)  # 간격 20px

        version_field = self.create_readonly_input_field("버전", 374)
        self.version_edit = version_field["input"]
        self.version_edit.setReadOnly(True)  # 읽기 전용
        version_model_layout.addWidget(version_field["widget"])

        model_field = self.create_readonly_input_field("모델명", 374)
        self.model_edit = model_field["input"]
        self.model_edit.setReadOnly(True)  # 읽기 전용
        version_model_layout.addWidget(model_field["widget"])

        version_model_row.setLayout(version_model_layout)
        input_layout.addWidget(version_model_row)

        # 시험유형, 시험대상 행 (768x82px) - 이미지 배경 사용
        category_target_row = QWidget()
        category_target_row.setFixedSize(768, 82)
        category_target_layout = QHBoxLayout()
        category_target_layout.setContentsMargins(0, 0, 0, 0)
        category_target_layout.setSpacing(20)  # 간격 20px

        test_category_field = self.create_readonly_input_field("시험유형", 374)
        self.test_category_edit = test_category_field["input"]
        self.test_category_edit.setReadOnly(True)  # 읽기 전용
        category_target_layout.addWidget(test_category_field["widget"])

        target_system_field = self.create_readonly_input_field("시험대상", 374)
        self.target_system_edit = target_system_field["input"]
        self.target_system_edit.setReadOnly(True)  # 읽기 전용
        category_target_layout.addWidget(target_system_field["widget"])

        category_target_row.setLayout(category_target_layout)
        input_layout.addWidget(category_target_row)

        # 시험분야, 시험범위 행 (768x82px) - 이미지 배경 사용
        group_range_row = QWidget()
        group_range_row.setFixedSize(768, 82)
        group_range_layout = QHBoxLayout()
        group_range_layout.setContentsMargins(0, 0, 0, 0)
        group_range_layout.setSpacing(20)  # 간격 20px

        test_group_field = self.create_readonly_input_field("시험분야", 374)
        self.test_group_edit = test_group_field["input"]
        self.test_group_edit.setReadOnly(True)  # 읽기 전용
        group_range_layout.addWidget(test_group_field["widget"])

        test_range_field = self.create_readonly_input_field("시험범위", 374)
        self.test_range_edit = test_range_field["input"]
        self.test_range_edit.setReadOnly(True)  # 읽기 전용
        group_range_layout.addWidget(test_range_field["widget"])

        group_range_row.setLayout(group_range_layout)
        input_layout.addWidget(group_range_row)

        # 관리자 코드 필드 (768x82px - 전체 너비) - 이미지 배경 사용
        admin_code_field = self.create_admin_code_field()
        self.admin_code_edit = admin_code_field["input"]
        self.admin_code_edit.setEchoMode(QLineEdit.Password)  # 비밀번호 모드
        self.admin_code_edit.setPlaceholderText("")  # 초기에는 placeholder 없음
        self.admin_code_edit.setEnabled(False)  # 초기에는 비활성화 (시험 정보 불러오기 전)
        input_layout.addWidget(admin_code_field["widget"])

        # 관리자 코드 입력 시 숫자 검증 및 버튼 상태 업데이트
        self.admin_code_edit.textChanged.connect(self.form_validator.validate_admin_code)
        self.admin_code_edit.textChanged.connect(self.check_start_button_state)
        self.admin_code_edit.textChanged.connect(self.check_next_button_state)  # 1페이지 다음 버튼 상태 체크

        # 시험유형 변경 시 관리자 코드 필드 활성화/비활성화
        self.test_category_edit.textChanged.connect(self.form_validator.handle_test_category_change)
        self.test_category_edit.textChanged.connect(self.check_start_button_state)

        # 시험범위 변경 시 UI 표시 텍스트 변환
        self.test_range_edit.textChanged.connect(self.form_validator.handle_test_range_change)

        # 첫 번째 페이지 필드들의 변경 시 다음 버튼 상태 체크
        for field in [self.company_edit, self.product_edit, self.version_edit, self.model_edit,
                     self.test_category_edit, self.target_system_edit, self.test_group_edit, self.test_range_edit,
                     self.admin_code_edit]:
            field.textChanged.connect(self.check_next_button_state)

        input_container.setLayout(input_layout)
        layout.addWidget(input_container)

        # 폼과 버튼 사이 간격 48px
        layout.addSpacing(48)

        # 하단 버튼 (초기화: 왼쪽, 다음: 오른쪽)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)  # 버튼 간격 20px

        # 초기화 버튼 (왼쪽)
        reset_btn = QPushButton()
        reset_btn.setFixedSize(374, 82)
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

        # 다음 버튼 (오른쪽)
        self.next_btn = QPushButton()
        self.next_btn.setFixedSize(374, 82)
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
                padding: 0 12px;
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

    def create_readonly_input_field(self, label_text, width=768):
        """
        읽기전용 입력 필드 생성 (불러온 정보용 - 이미지 배경)
        - 전체 크기: width x 82px
        - 라벨: width x 28px (6px 간격)
        - 입력칸: width x 48px (이미지 배경 사용)

        Args:
            label_text: 라벨 텍스트
            width: 필드 너비 (768: wide 이미지, 374: small 이미지)
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
            # 전체 너비 (768px) - wide 이미지
            input_default = resource_path("assets/image/test_info/불러온정보_w_default.png").replace(chr(92), "/")
            input_filled = resource_path("assets/image/test_info/불러온정보_w_filled.png").replace(chr(92), "/")
        else:
            # 반 너비 (374px) - small 이미지
            input_default = resource_path("assets/image/test_info/불러온정보_s_default.png").replace(chr(92), "/")
            input_filled = resource_path("assets/image/test_info/불러온정보_s_filled.png").replace(chr(92), "/")

        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 400;
                letter-spacing: -0.17px;
                color: #000000;
                padding: 0 12px;
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
        관리자 코드 입력 필드 생성 (768x82px)
        - 라벨: 768x28px (6px 간격)
        - 입력칸: 768x48px (상태별 배경 이미지)
        """
        field_widget = QWidget()
        field_widget.setFixedSize(768, 82)
        field_layout = QVBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)  # 라벨과 입력칸 사이 간격 6px

        # 라벨 (768x28px)
        label = QLabel("관리자 코드")
        label.setFixedSize(768, 28)
        label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-size: 16px;
                font-weight: 500;
                letter-spacing: -0.16px;
            }
        """)
        field_layout.addWidget(label)

        # 입력칸 (768x48px) - 상태별 배경 이미지
        input_field = QLineEdit()
        input_field.setFixedSize(768, 48)

        # 한글 경로 처리를 위한 절대 경로 사용
        import os
        input_enabled = resource_path("assets/image/test_info/input_enabled.png").replace(chr(92), "/")
        input_disabled = resource_path("assets/image/test_info/input_disabled.png").replace(chr(92), "/")
        input_hover = resource_path("assets/image/test_info/input_Hover.png").replace(chr(92), "/")

        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Noto Sans KR';
                font-size: 17px;
                font-weight: 400;
                letter-spacing: -0.17px;
                color: #000000;
                padding: 0 12px;
                border: none;
                background-image: url({input_enabled});
                background-repeat: no-repeat;
                background-position: center;
            }}
            QLineEdit:hover:enabled:!focus[hasText="false"] {{
                background-image: url({input_hover});
            }}
            QLineEdit:disabled {{
                background-image: url({input_disabled});
            }}
            QLineEdit[hasText="true"] {{
                background-image: url({input_disabled});
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

    def create_test_field_group(self):
        """시험 시나리오명 그룹 (QGroupBox)"""
        group = QGroupBox("시험 시나리오")
        group.setFixedSize(744, 280)

        # QGroupBox 스타일 설정
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                padding-top: 42px;
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 16px;
                letter-spacing: -0.16px;
                color: #000000;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 0px;
                top: 12px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 시험 시나리오명 테이블 (744x238px) - 2개 컬럼: 시험 분야명, 시험 시나리오명
        self.test_field_table = QTableWidget(0, 2)
        self.test_field_table.setFixedSize(744, 238)
        self.test_field_table.setHorizontalHeaderLabels(["시험 분야명", "시험 시나리오명"])

        # 컬럼 너비 설정 (시험 분야명: 360px, 시험 시나리오명: 360px)
        header = self.test_field_table.horizontalHeader()
        header.setFixedHeight(24)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 360)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 360)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)
        self.test_field_table.verticalHeader().setVisible(False)

        # 테이블 스타일 설정
        self.test_field_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                gridline-color: #CCCCCC;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 14px;
                letter-spacing: 0.098px;
            }
            QTableWidget::item {
                height: 26px;
                background-color: #FFFFFF;
                border-bottom: 1px solid #CCCCCC;
                padding-right: 14px;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 14px;
                letter-spacing: 0.098px;
                color: #000000;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                border-right: 1px solid #CCCCCC;
                font-family: 'Noto Sans KR';
                font-weight: 600;
                font-size: 13px;
                letter-spacing: -0.156px;
                color: #000000;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)

        # 마지막으로 클릭된 시험 분야의 행을 추적
        self.selected_test_field_row = None

        layout.addWidget(self.test_field_table)
        group.setLayout(layout)
        return group

    def create_test_api_group(self):
        """시험 API 그룹 (QGroupBox)"""
        group = QGroupBox("시험 API")
        group.setFixedSize(744, 466)

        # QGroupBox 스타일 설정
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                padding-top: 42px;
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 16px;
                letter-spacing: -0.16px;
                color: #000000;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 0px;
                top: 12px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 시험 API 테이블 (744x424px) - 466 - 36(타이틀) - 6(gap) = 424px
        self.api_test_table = QTableWidget(0, 2)
        self.api_test_table.setFixedSize(744, 424)
        self.api_test_table.setHorizontalHeaderLabels(["기능명", "API명"])

        header = self.api_test_table.horizontalHeader()
        header.setFixedHeight(24)
        header.setSectionResizeMode(QHeaderView.Stretch)

        # 왼쪽 행 번호 헤더 설정
        vertical_header = self.api_test_table.verticalHeader()
        vertical_header.setDefaultAlignment(Qt.AlignCenter)
        vertical_header.setStyleSheet("QHeaderView { background-color: #FFFFFF; }")

        # 세로 grid line 제거
        self.api_test_table.setShowGrid(False)

        # 테이블 스타일 설정
        self.api_test_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 14px;
                letter-spacing: 0.098px;
            }
            QTableWidget::item {
                height: 26px;
                background-color: #FFFFFF;
                border-bottom: 1px solid #CCCCCC;
                border-right: none;
                padding-right: 14px;
                color: #000000;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                font-family: 'Noto Sans KR';
                font-weight: 600;
                font-size: 13px;
                letter-spacing: -0.156px;
                color: #000000;
            }
            QHeaderView::section:vertical {
                background-color: #FFFFFF;
                border: none;
                border-right: none;
                border-bottom: 1px solid #CCCCCC;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 14px;
                letter-spacing: 0.098px;
                color: #000000;
            }
            QTableCornerButton::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
            }
        """)

        layout.addWidget(self.api_test_table)
        group.setLayout(layout)
        return group

    def create_auth_section(self):
        """인증 방식 섹션"""
        section = QGroupBox("사용자 인증 방식")
        section.setFixedSize(744, 280)

        # QGroupBox 스타일 설정
        section.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
                padding-top: 42px;
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 16px;
                letter-spacing: -0.16px;
                color: #000000;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 0px;
                top: 12px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 콘텐츠 영역 (744x238px, 테두리 #CECECE 1px, padding: 8, 8, 20, 18)
        content_widget = QWidget()
        content_widget.setFixedSize(744, 238)
        content_widget.setStyleSheet("""
            #content_widget {
                border: 1px solid #CECECE;
                border-radius: 4px;
                background-color: #F5F5F5;
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
                background-color: #F5F5F5;
            }
        """)
        content_widget.setObjectName("content_widget")

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 8, 20, 18)  # 좌, 상, 우, 하
        content_layout.setSpacing(0)

        # Digest Auth 영역 (716x100px)
        digest_widget = QWidget()
        digest_widget.setFixedSize(716, 100)
        digest_layout = QVBoxLayout()
        digest_layout.setContentsMargins(0, 0, 0, 0)
        digest_layout.setSpacing(0)

        # 라디오 버튼 + 텍스트 (716x30px)
        digest_radio_row = QWidget()
        digest_radio_row.setFixedSize(716, 30)
        digest_radio_layout = QHBoxLayout()
        digest_radio_layout.setContentsMargins(0, 0, 0, 0)
        digest_radio_layout.setSpacing(8)  # 라디오 버튼과 텍스트 사이 8px gap

        self.digest_radio = QRadioButton()
        self.digest_radio.setFixedSize(30, 30)
        self.digest_radio.setChecked(True)
        self.digest_radio.setStyleSheet("""
            QRadioButton {
                padding-left: 5px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        digest_radio_layout.addWidget(self.digest_radio)

        digest_label = QLabel("Digest Auth")
        digest_label.setFixedSize(678, 30)
        digest_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 16px;
                letter-spacing: -0.16px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        digest_radio_layout.addWidget(digest_label)

        digest_radio_row.setLayout(digest_radio_layout)
        digest_layout.addWidget(digest_radio_row)

        # 2px gap
        digest_layout.addSpacing(2)

        # ID/PW 입력 영역 (716x68px, 좌측 padding 38px)
        digest_input_widget = QWidget()
        digest_input_widget.setFixedSize(716, 68)
        digest_input_layout = QHBoxLayout()
        digest_input_layout.setContentsMargins(38, 0, 0, 0)  # 좌측 38px
        digest_input_layout.setSpacing(20)  # User ID와 Password 사이 20px gap

        # User ID 영역 (329x68px)
        userid_widget = QWidget()
        userid_widget.setFixedSize(329, 68)
        userid_layout = QVBoxLayout()
        userid_layout.setContentsMargins(0, 0, 0, 0)
        userid_layout.setSpacing(0)

        userid_label = QLabel("User ID")
        userid_label.setFixedSize(329, 26)
        userid_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 16px;
                letter-spacing: -0.16px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        userid_layout.addWidget(userid_label)

        userid_layout.addSpacing(4)  # 라벨과 입력칸 사이 4px gap

        self.id_input = QLineEdit()
        self.id_input.setFixedSize(329, 38)
        digest_enabled = resource_path("assets/image/test_config/input_DigestAuth_enabled.png").replace(chr(92), "/")
        digest_disabled = resource_path("assets/image/test_config/input_DigestAuth_disabled.png").replace(chr(92), "/")
        self.id_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 20px;
                border: none;
                background-color: #F5F5F5;
                background-image: url({digest_enabled});
                background-repeat: no-repeat;
                background-position: center;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 17px;
                letter-spacing: -0.17px;
                color: #000000;
            }}
            QLineEdit:disabled {{
                background-image: url({digest_disabled});
                color: #868686;
            }}
        """)
        userid_layout.addWidget(self.id_input)

        userid_widget.setLayout(userid_layout)
        digest_input_layout.addWidget(userid_widget)

        # Password 영역 (329x68px)
        password_widget = QWidget()
        password_widget.setFixedSize(329, 68)
        password_layout = QVBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)

        password_label = QLabel("Password")
        password_label.setFixedSize(329, 26)
        password_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 16px;
                letter-spacing: -0.16px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        password_layout.addWidget(password_label)

        password_layout.addSpacing(4)  # 라벨과 입력칸 사이 4px gap

        self.pw_input = QLineEdit()
        self.pw_input.setFixedSize(329, 38)
        self.pw_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 20px;
                border: none;
                background-color: #F5F5F5;
                background-image: url({digest_enabled});
                background-repeat: no-repeat;
                background-position: center;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 17px;
                letter-spacing: -0.17px;
                color: #000000;
            }}
            QLineEdit:disabled {{
                background-image: url({digest_disabled});
                color: #868686;
            }}
        """)
        self.pw_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.pw_input)

        password_widget.setLayout(password_layout)
        digest_input_layout.addWidget(password_widget)

        digest_input_widget.setLayout(digest_input_layout)
        digest_layout.addWidget(digest_input_widget)

        digest_widget.setLayout(digest_layout)
        content_layout.addWidget(digest_widget)

        # Digest와 Bearer 사이 간격 12px
        content_layout.addSpacing(12)

        # Bearer Token 영역 (716x100px)
        bearer_widget = QWidget()
        bearer_widget.setFixedSize(716, 100)
        bearer_layout = QVBoxLayout()
        bearer_layout.setContentsMargins(0, 0, 0, 0)
        bearer_layout.setSpacing(0)

        # 라디오 버튼 + 텍스트 (716x30px)
        bearer_radio_row = QWidget()
        bearer_radio_row.setFixedSize(716, 30)
        bearer_radio_layout = QHBoxLayout()
        bearer_radio_layout.setContentsMargins(0, 0, 0, 0)
        bearer_radio_layout.setSpacing(8)  # 라디오 버튼과 텍스트 사이 8px gap

        self.bearer_radio = QRadioButton()
        self.bearer_radio.setFixedSize(30, 30)
        self.bearer_radio.setStyleSheet("""
            QRadioButton {
                padding-left: 5px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        bearer_radio_layout.addWidget(self.bearer_radio)

        bearer_label = QLabel("Bearer Token")
        bearer_label.setFixedSize(678, 30)
        bearer_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 16px;
                letter-spacing: -0.16px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        bearer_radio_layout.addWidget(bearer_label)

        bearer_radio_row.setLayout(bearer_radio_layout)
        bearer_layout.addWidget(bearer_radio_row)

        # 2px gap
        bearer_layout.addSpacing(2)

        # Token 입력 영역 (716x68px, 좌측 padding 38px)
        token_input_widget = QWidget()
        token_input_widget.setFixedSize(716, 68)
        token_input_layout = QVBoxLayout()
        token_input_layout.setContentsMargins(38, 0, 0, 0)  # 좌측 38px
        token_input_layout.setSpacing(0)

        token_label = QLabel("Token")
        token_label.setFixedSize(678, 26)  # 716 - 38(좌측 padding) = 678
        token_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 16px;
                letter-spacing: -0.16px;
                color: #000000;
                border: none;
                background-color: transparent;
            }
        """)
        token_input_layout.addWidget(token_label)

        token_input_layout.addSpacing(4)  # 라벨과 입력칸 사이 4px gap

        self.token_input = QLineEdit()
        self.token_input.setFixedSize(678, 38)  # 716 - 38(좌측 padding) = 678
        token_enabled = resource_path("assets/image/test_config/input_Token_enabled.png").replace(chr(92), "/")
        token_disabled = resource_path("assets/image/test_config/input_Token_disabled.png").replace(chr(92), "/")
        self.token_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 20px;
                border: none;
                background-color: #F5F5F5;
                background-image: url({token_enabled});
                background-repeat: no-repeat;
                background-position: center;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 17px;
                letter-spacing: -0.17px;
                color: #000000;
            }}
            QLineEdit:disabled {{
                background-image: url({token_disabled});
                color: #868686;
            }}
        """)
        token_input_layout.addWidget(self.token_input)

        token_input_widget.setLayout(token_input_layout)
        bearer_layout.addWidget(token_input_widget)

        bearer_widget.setLayout(bearer_layout)
        content_layout.addWidget(bearer_widget)

        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)

        # 라디오 버튼 그룹 설정 (상호 배타적으로 동작)
        from PyQt5.QtWidgets import QButtonGroup
        self.auth_button_group = QButtonGroup()
        self.auth_button_group.addButton(self.digest_radio)
        self.auth_button_group.addButton(self.bearer_radio)

        # 라디오 버튼 연결
        self.digest_radio.toggled.connect(self.update_auth_fields)
        self.bearer_radio.toggled.connect(self.update_auth_fields)

        # 입력 필드 변경 시 버튼 상태 체크
        self.id_input.textChanged.connect(self.check_start_button_state)
        self.pw_input.textChanged.connect(self.check_start_button_state)
        self.token_input.textChanged.connect(self.check_start_button_state)

        section.setLayout(layout)

        # 초기 상태 설정
        self.update_auth_fields()

        return section

    def create_connection_section(self):
        """접속 정보 섹션"""
        section = QGroupBox()
        section.setFixedSize(744, 466)
        section.setStyleSheet("QGroupBox { border: none; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 접속 주소 탐색 + 주소탐색버튼 영역 (744x36px)
        scan_row = QWidget()
        scan_row.setFixedSize(744, 36)
        scan_layout = QHBoxLayout()
        scan_layout.setContentsMargins(0, 0, 0, 0)
        scan_layout.setSpacing(0)

        # 접속 주소 탐색 라벨 (위로 padding 12px)
        scan_label_widget = QWidget()
        scan_label_layout = QVBoxLayout()
        scan_label_layout.setContentsMargins(0, 12, 0, 0)
        scan_label_layout.setSpacing(0)

        scan_label = QLabel("접속 주소 탐색")
        scan_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 500;
                font-size: 16px;
                letter-spacing: -0.16px;
                color: #000000;
            }
        """)
        scan_label_layout.addWidget(scan_label)
        scan_label_widget.setLayout(scan_label_layout)
        scan_layout.addWidget(scan_label_widget)

        scan_layout.addStretch()

        # 주소탐색 버튼 (120x30px, 위 padding 4px, 아래 padding 2px)
        scan_btn_widget = QWidget()
        scan_btn_widget.setFixedSize(120, 36)
        scan_btn_layout = QVBoxLayout()
        scan_btn_layout.setContentsMargins(0, 4, 0, 2)
        scan_btn_layout.setSpacing(0)

        scan_btn = QPushButton("")
        scan_btn.setFixedSize(120, 30)

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
        scan_btn_layout.addWidget(scan_btn)
        scan_btn_widget.setLayout(scan_btn_layout)

        scan_layout.addWidget(scan_btn_widget)
        scan_row.setLayout(scan_layout)
        layout.addWidget(scan_row)

        # 6px gap
        layout.addSpacing(6)

        # IP 직접 입력 영역 (744x36px) - 기본적으로 비활성화
        ip_direct_row = QWidget()
        ip_direct_row.setFixedSize(744, 36)
        ip_direct_layout = QHBoxLayout()
        ip_direct_layout.setContentsMargins(0, 0, 0, 0)
        ip_direct_layout.setSpacing(8)

        # 직접 입력 라벨
        direct_label = QLabel("")
        direct_label.setFixedWidth(120)
        direct_label.setStyleSheet("""
            QLabel {
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 14px;
                letter-spacing: -0.14px;
                color: #666666;
            }
        """)
        ip_direct_layout.addWidget(direct_label)

        # IP:Port 직접 입력창 - 항상 활성화 (데모용)
        self.page2_ip_direct_input = QLineEdit()
        self.page2_ip_direct_input.setFixedHeight(30)
        self.page2_ip_direct_input.setPlaceholderText("예: 192.168.1.1:8080")
        self.page2_ip_direct_input.setStyleSheet("""
            QLineEdit {
                font-family: 'Noto Sans KR';
                font-size: 13px;
                padding: 6px 10px;
                border: 1px solid #CECECE;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
            }
        """)
        ip_direct_layout.addWidget(self.page2_ip_direct_input)

        # "추가" 버튼 - 항상 활성화 (데모용)
        self.add_ip_btn = QPushButton("추가")
        self.add_ip_btn.setFixedSize(80, 30)
        self.add_ip_btn.setStyleSheet("""
            QPushButton {
                font-family: 'Noto Sans KR';
                font-size: 13px;
                font-weight: 500;
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2E6DA4;
            }
        """)
        self.add_ip_btn.clicked.connect(self.add_ip_to_table)
        ip_direct_layout.addWidget(self.add_ip_btn)

        ip_direct_row.setLayout(ip_direct_layout)
        layout.addWidget(ip_direct_row)

        # 6px gap
        layout.addSpacing(6)

        # URL 테이블 (744x370px) - 높이 줄임
        self.url_table = QTableWidget(0, 2)
        self.url_table.setFixedSize(744, 370)
        self.url_table.setHorizontalHeaderLabels(["", "URL"])  # 첫 번째 헤더는 빈 문자열
        self.url_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.url_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.url_table.setSelectionMode(QAbstractItemView.SingleSelection)

        # 헤더 설정
        header = self.url_table.horizontalHeader()
        header.setFixedHeight(24)
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignCenter)  # 헤더 가운데 정렬

        # 왼쪽 행 번호 헤더 설정
        vertical_header = self.url_table.verticalHeader()
        vertical_header.setVisible(True)
        vertical_header.setDefaultAlignment(Qt.AlignCenter)
        vertical_header.setStyleSheet("QHeaderView { background-color: #FFFFFF; }")

        # 컬럼 너비 설정 (체크박스: 36px, URL: 나머지, 오른쪽 padding: 14px)
        self.url_table.setColumnWidth(0, 36)

        # 세로 grid line 제거
        self.url_table.setShowGrid(False)

        # 행 높이 설정
        self.url_table.verticalHeader().setDefaultSectionSize(26)

        # 스타일 설정
        self.url_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 14px;
                letter-spacing: 0.098px;
            }
            QTableWidget::item {
                background-color: #FFFFFF;
                border-bottom: 1px solid #CCCCCC;
                border-right: none;
                padding-right: 14px;
                color: #000000;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                padding: 4px;
                height: 24px;
                font-family: 'Noto Sans KR';
                font-size: 13px;
                font-weight: 600;
                letter-spacing: -0.156px;
            }
            QHeaderView::section:vertical {
                background-color: #FFFFFF;
                border: none;
                border-right: none;
                border-bottom: 1px solid #CCCCCC;
                font-family: 'Noto Sans KR';
                font-weight: 400;
                font-size: 14px;
                letter-spacing: 0.098px;
                color: #000000;
            }
            QHeaderView::section:vertical:checked {
                background-color: #E3F2FF;
            }
            QTableCornerButton::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CCCCCC;
            }
        """)

        self.url_table.cellClicked.connect(self.select_url_row)
        layout.addWidget(self.url_table)

        section.setLayout(layout)
        return section

    # ---------- 공통 기능 메서드들 ----------

    # ---------- 우측 패널 ----------
    def create_right_panel(self):
        panel = QGroupBox("시험 입력 정보")
        layout = QVBoxLayout()

        # 인증 방식
        auth_label = QLabel("사용자 인증 방식")
        auth_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(auth_label)

        # Digest
        from PyQt5.QtWidgets import QRadioButton
        self.digest_radio = QRadioButton("Digest Auth")
        self.digest_radio.setChecked(True)
        layout.addWidget(self.digest_radio)
        digest_row = QHBoxLayout()
        self.id_input = QLineEdit()
        self.pw_input = QLineEdit()
        digest_row.addWidget(QLabel("ID:"))
        digest_row.addWidget(self.id_input)
        digest_row.addWidget(QLabel("PW:"))
        digest_row.addWidget(self.pw_input)
        digest_w = QWidget(); digest_w.setLayout(digest_row)
        digest_row.setContentsMargins(20, 0, 0, 0)
        layout.addWidget(digest_w)

        # Bearer
        self.bearer_radio = QRadioButton("Bearer Token")
        layout.addWidget(self.bearer_radio)
        token_row = QHBoxLayout()
        self.token_input = QLineEdit()
        token_row.addWidget(QLabel("Token:"))
        token_row.addWidget(self.token_input)
        token_w = QWidget(); token_w.setLayout(token_row)
        token_row.setContentsMargins(20, 0, 0, 0)
        layout.addWidget(token_w)

        self.digest_radio.toggled.connect(self.update_auth_fields)
        self.bearer_radio.toggled.connect(self.update_auth_fields)
        
        # 입력 필드 변경 시 버튼 상태 체크
        self.id_input.textChanged.connect(self.check_start_button_state)
        self.pw_input.textChanged.connect(self.check_start_button_state)
        self.token_input.textChanged.connect(self.check_start_button_state)

        self.update_auth_fields()

        panel.setLayout(layout)
        return panel

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
        self.startTestRequested.emit()

    def update_auth_fields(self):
        if self.digest_radio.isChecked():
            # Digest Auth 활성화
            self.id_input.setEnabled(True)
            self.pw_input.setEnabled(True)
            # Token 비활성화, 값 비움
            self.token_input.setEnabled(False)
            self.token_input.clear()
        else:
            # Bearer Token 활성화
            self.token_input.setEnabled(True)
            # ID, PW 비활성화, 값 비움
            self.id_input.setEnabled(False)
            self.pw_input.setEnabled(False)
            self.id_input.clear()
            self.pw_input.clear()

        # 필드 변경 시 버튼 상태 업데이트
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
                            "아래 '직접 입력' 기능을 사용하여 IP:Port를 수동으로 입력해주세요.\n"
                            "예: 192.168.1.1:8080"
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
        """URL 테이블에 스캔 결과 채우기"""
        try:
            self.url_table.setRowCount(0)
            
            for i, url in enumerate(urls):
                row = self.url_table.rowCount()
                self.url_table.insertRow(row)

                checkbox_widget = QWidget()
                checkbox_widget.setStyleSheet("background-color: #FFFFFF;")
                checkbox_layout = QHBoxLayout()
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)

                checkbox = QCheckBox()
                checkbox.setChecked(False)
                checkbox.clicked.connect(lambda checked, r=row: self.on_checkbox_clicked(r, checked))
                checkbox_layout.addWidget(checkbox)
                checkbox_widget.setLayout(checkbox_layout)
                
                self.url_table.setCellWidget(row, 0, checkbox_widget)

                # URL 텍스트
                url_item = QTableWidgetItem(url)
                url_item.setTextAlignment(Qt.AlignCenter)  
                self.url_table.setItem(row, 1, url_item)
            
        except Exception as e:
            self._show_scan_error(f"테이블 업데이트 중 오류:\n{str(e)}")
    
    def _show_scan_error(self, message):
        """스캔 오류 메시지 표시"""
        QMessageBox.warning(self, "주소 탐색 실패", message)

    def add_ip_to_table(self):
        """직접 입력한 IP:Port를 URL 테이블에 추가"""
        try:
            # 입력값 가져오기
            ip_port = self.page2_ip_direct_input.text().strip()

            if not ip_port:
                QMessageBox.warning(self, "입력 오류", "IP:Port를 입력해주세요.\n예: 192.168.1.1:8080")
                return

            # 기본적인 형식 검증 (IP:Port)
            if ':' not in ip_port:
                QMessageBox.warning(self, "형식 오류", "올바른 형식으로 입력해주세요.\n예: 192.168.1.1:8080")
                return

            parts = ip_port.split(':')
            if len(parts) != 2:
                QMessageBox.warning(self, "형식 오류", "올바른 형식으로 입력해주세요.\n예: 192.168.1.1:8080")
                return

            ip_part = parts[0]
            port_part = parts[1]

            # IP 검증
            if not self._validate_ip_address(ip_part):
                QMessageBox.warning(self, "IP 오류", "올바른 IP 주소를 입력해주세요.\n예: 192.168.1.100")
                return

            # Port 검증
            try:
                port = int(port_part)
                if port < 1 or port > 65535:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Port 오류", "올바른 Port 번호를 입력해주세요. (1-65535)")
                return

            # 중복 확인
            for row in range(self.url_table.rowCount()):
                item = self.url_table.item(row, 1)
                if item and item.text() == ip_port:
                    QMessageBox.information(self, "알림", "이미 추가된 주소입니다.")
                    return

            # 테이블에 추가
            row = self.url_table.rowCount()
            self.url_table.insertRow(row)

            # 체크박스 추가
            checkbox_widget = QWidget()
            checkbox_widget.setStyleSheet("background-color: #FFFFFF;")
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)

            checkbox = QCheckBox()
            checkbox.setChecked(False)
            checkbox.clicked.connect(lambda checked, r=row: self.on_checkbox_clicked(r, checked))
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)

            self.url_table.setCellWidget(row, 0, checkbox_widget)

            # URL 텍스트 추가
            url_item = QTableWidgetItem(ip_port)
            url_item.setTextAlignment(Qt.AlignCenter)
            self.url_table.setItem(row, 1, url_item)

            # 입력창 초기화
            self.page2_ip_direct_input.clear()

            QMessageBox.information(self, "추가 완료", f"주소가 추가되었습니다.\n{ip_port}")

        except Exception as e:
            print(f"IP 추가 오류: {e}")
            QMessageBox.critical(self, "오류", f"주소 추가 중 오류가 발생했습니다:\n{str(e)}")

    def on_checkbox_clicked(self, clicked_row, checked):
        """체크박스 클릭 시: 단일 선택 처리"""
        if checked:  # 체크된 경우에만 처리
            # 모든 행 체크 해제
            for r in range(self.url_table.rowCount()):
                if r != clicked_row:  # 클릭된 행 제외
                    checkbox_widget = self.url_table.cellWidget(r, 0)
                    if checkbox_widget:
                        checkbox = checkbox_widget.findChild(QCheckBox)
                        if checkbox:
                            checkbox.setChecked(False)
                        # 체크박스 위젯 배경색 흰색으로
                        checkbox_widget.setStyleSheet("background-color: #FFFFFF;")

            # 체크된 행 선택 (stylesheet의 :selected로 배경색 자동 적용)
            self.url_table.selectRow(clicked_row)
            # 체크박스 위젯 배경색도 변경
            checkbox_widget = self.url_table.cellWidget(clicked_row, 0)
            if checkbox_widget:
                checkbox_widget.setStyleSheet("background-color: #E3F2FF;")
        else:
            # 체크 해제 시 선택 해제
            self.url_table.clearSelection()
            checkbox_widget = self.url_table.cellWidget(clicked_row, 0)
            if checkbox_widget:
                checkbox_widget.setStyleSheet("background-color: #FFFFFF;")

        # URL 선택 변경 시 버튼 상태 체크
        self.check_start_button_state()

    def select_url_row(self, row, col):
        """행 클릭 시: 체크 단일 선택"""
        # 모든 행 체크 해제
        for r in range(self.url_table.rowCount()):
            checkbox_widget = self.url_table.cellWidget(r, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)
                # 체크박스 위젯 배경색 흰색으로
                checkbox_widget.setStyleSheet("background-color: #FFFFFF;")

        # 선택된 행 체크
        selected_checkbox_widget = self.url_table.cellWidget(row, 0)
        if selected_checkbox_widget:
            checkbox = selected_checkbox_widget.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(True)
            # 체크박스 위젯 배경색 변경
            selected_checkbox_widget.setStyleSheet("background-color: #E3F2FF;")

        # 행 선택 (stylesheet의 :selected로 배경색 자동 적용)
        self.url_table.selectRow(row)

        # URL 선택 변경 시 버튼 상태 체크
        self.check_start_button_state()

    def get_selected_url(self):
        """URL 테이블에서 선택된 URL 반환"""
        for row in range(self.url_table.rowCount()):
            checkbox_widget = self.url_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    url_item = self.url_table.item(row, 1)
                    if url_item:
                        selected_url = url_item.text().strip()
                        # http://가 없으면 추가
                        if not selected_url.startswith(('http://', 'https://')):
                            selected_url = f"https://{selected_url}"
                        return selected_url
        return None

    def _check_required_fields(self):
        """필수 입력 필드 검증 - 누락된 항목 리스트 반환 (인증 정보 및 접속 URL만 체크)"""
        missing_fields = []

        # 1. 인증 정보 확인
        if self.digest_radio.isChecked():
            if not self.id_input.text().strip():
                missing_fields.append("• 인증 ID (Digest Auth)")
            if not self.pw_input.text().strip():
                missing_fields.append("• 인증 PW (Digest Auth)")
        else:  # Bearer Token
            if not self.token_input.text().strip():
                missing_fields.append("• 인증 토큰 (Bearer Token)")

        # 2. 접속 정보 확인 (URL 선택됨)
        if not self.get_selected_url():
            missing_fields.append("• 접속 URL 선택")

        return missing_fields

    def start_test(self):
        """시험 시작 - CONSTANTS.py 업데이트 후 검증 소프트웨어 실행"""
        importlib.reload(CONSTANTS)  # CONSTANTS 모듈을 다시 로드하여 최신 설정 반영
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
            if self.test_field_table.rowCount() > 0 or self.api_test_table.rowCount() > 0:
                return True

            # 인증 정보에 입력값이 있는지 확인
            auth_fields = [
                self.id_input.text().strip(),
                self.pw_input.text().strip(),
                self.token_input.text().strip()
            ]

            if any(field for field in auth_fields):
                return True

            # URL 테이블에서 선택된 항목이 있는지 확인
            for row in range(self.url_table.rowCount()):
                checkbox_widget = self.url_table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        return True

            # 인증 방식이 Bearer Token으로 선택되어 있다면 초기화 필요
            if self.bearer_radio.isChecked():
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
            self.api_test_table.setRowCount(0)

            # 인증 정보 초기화
            self.id_input.clear()
            self.pw_input.clear()
            self.token_input.clear()

            # 인증 방식을 Digest Auth로 초기화
            self.digest_radio.setChecked(True)

            # 주소 탐색 테이블 초기화
            self.url_table.setRowCount(0)

            # 현재 모드 초기화
            self.current_mode = None

            # update_auth_fields() 호출하여 필드 상태 초기화
            self.update_auth_fields()

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
        try:
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

            # verificationType 기반 모드 설정 (API 기반)
            self.current_mode = self._determine_mode_from_api(test_data)

            # API 데이터를 이용하여 OPT 파일 로드 및 스키마 생성
            self.form_validator.load_opt_files_from_api(test_data)

            # 다음 버튼 상태 업데이트
            self.check_next_button_state()

        except Exception as e:
            print(f"시험정보 불러오기 실패: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"시험 정보를 불러오는 중 오류가 발생했습니다:\n{str(e)}")
    
    def _validate_ip_address(self, ip):
        """IP 주소 형식 검증"""
        # IP 주소 정규식 패턴
        ip_pattern = re.compile(
            r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        return bool(ip_pattern.match(ip))

    def get_local_ip(self):
        return "192.168.1.2, 127.0.0.1"
    
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
        """시험 분야명 행 클릭 시 해당 API 테이블 표시 (API 기반)"""
        try:
            # 클릭된 행 번호 저장
            self.selected_test_field_row = row

            # specifications API 호출하여 API 테이블 채우기
            self.form_validator._fill_api_table_for_selected_field_from_api(row)
        except Exception as e:
            print(f"시험 분야 선택 처리 실패: {e}")
            QMessageBox.warning(self, "오류", f"시험 분야 데이터 로드 중 오류가 발생했습니다:\n{str(e)}")
