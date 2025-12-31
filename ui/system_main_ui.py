from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer, QSize

from core.functions import resource_path
from ui.ui_components import TestSelectionPanel
from ui.detail_dialog import CombinedDetailDialog
from ui.gui_utils import CustomDialog


class SystemMainUI(QWidget):
    """
    시스템 검증 소프트웨어 메인 화면의 UI 구성 및 반응형 처리를 담당하는 클래스
    """

    def initUI(self):
        # ✅ 반응형: 최소 크기 설정
        self.setMinimumSize(1680, 1006)

        # embedded 속성이 없는 경우 대비
        if not getattr(self, "embedded", False):
            self.setWindowTitle("시스템 연동 검증")

        # ✅ 메인 레이아웃
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ✅ 상단 헤더 영역 (반응형 - 배경 늘어남, 로고/타이틀 가운데 고정)
        header_widget = QWidget()
        header_widget.setFixedHeight(64)
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 배경 이미지 설정 (늘어남 - border-image 사용)
        header_bg_path = resource_path("assets/image/common/header.png").replace(chr(92), "/")
        header_widget.setStyleSheet(
            f"""
            QWidget {{
                border-image: url({header_bg_path}) 0 0 0 0 stretch stretch;
            }}
            QLabel {{
                border-image: none;
                background: transparent;
            }}
        """
        )

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

        # 타이틀 이미지 (408x36)
        header_title_label = QLabel()
        header_title_pixmap = QPixmap(resource_path("assets/image/test_runner/runner_title.png"))
        header_title_label.setPixmap(
            header_title_pixmap.scaled(407, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        header_title_label.setFixedSize(407, 36)
        header_layout.addWidget(header_title_label)

        # 오른쪽 stretch (나머지 공간 채우기)
        header_layout.addStretch()

        mainLayout.addWidget(header_widget)

        # ✅ 본문 영역 컨테이너 (반응형 - main.png 배경)
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 배경 이미지를 QLabel로 설정 (절대 위치)
        main_bg_path = resource_path("assets/image/common/main.png").replace(chr(92), "/")
        self.content_bg_label = QLabel(self.content_widget)
        self.content_bg_label.setPixmap(QPixmap(main_bg_path))
        self.content_bg_label.setScaledContents(True)
        self.content_bg_label.lower()  # 맨 뒤로 보내기

        # ✅ 2컬럼 레이아웃 적용
        self.bg_root = QWidget(self.content_widget)
        self.bg_root.setObjectName("bg_root")
        self.bg_root.setFixedSize(1584, 898)  # left_col(472) + right_col(1112) = 1584
        self.bg_root.setAttribute(Qt.WA_StyledBackground, True)
        self.bg_root.setStyleSheet("QWidget#bg_root { background: transparent; }")

        # ✅ 반응형: 원본 크기 저장
        self.original_window_size = (1680, 1006)
        self.original_bg_root_size = (1584, 898)

        bg_root_layout = QVBoxLayout()
        bg_root_layout.setContentsMargins(0, 0, 0, 0)
        bg_root_layout.setSpacing(0)

        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(0)

        # ✅ 왼쪽 컬럼 (시험 분야 선택) - 472*898, padding: 좌우 24px, 상 36px, 하 80px
        self.left_col = QWidget()
        self.left_col.setFixedSize(472, 898)
        self.left_col.setStyleSheet("background: transparent;")
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(24, 36, 24, 80)
        self.left_layout.setSpacing(0)

        # ✅ 반응형: 왼쪽 패널 원본 크기 저장
        self.original_left_col_size = (472, 898)

        self.create_spec_selection_panel(self.left_layout)
        self.left_col.setLayout(self.left_layout)

        # ✅ 오른쪽 컬럼 (나머지 UI)
        self.right_col = QWidget()
        self.right_col.setFixedSize(1112, 898)
        self.right_col.setStyleSheet("background: transparent;")
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(24, 30, 24, 0)
        self.right_layout.setSpacing(0)
        self.right_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 왼쪽 상단 정렬

        # ✅ 반응형: 오른쪽 패널 원본 크기 저장
        self.original_right_col_size = (1112, 898)

        # ✅ 시험 URL 라벨 + 텍스트 박스 (가로 배치)
        self.url_row = QWidget()
        self.url_row.setFixedSize(1064, 36)
        self.url_row.setStyleSheet("background: transparent;")
        self.original_url_row_size = (1064, 36)

        url_row_layout = QHBoxLayout()
        url_row_layout.setContentsMargins(0, 0, 0, 0)
        url_row_layout.setSpacing(8)  # 라벨과 텍스트 박스 사이 8px gap
        url_row_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 왼쪽 정렬

        # 시험 URL 라벨 (96 × 24, 20px Medium)
        result_label = QLabel("시험 URL")
        result_label.setFixedSize(96, 24)
        result_label.setStyleSheet(
            """
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """
        )
        result_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        url_row_layout.addWidget(result_label)

        # ✅ URL 텍스트 박스
        self.url_text_box = QLineEdit()
        self.url_text_box.setFixedSize(960, 36)
        self.original_url_text_box_size = (960, 36)
        self.url_text_box.setReadOnly(False)
        self.url_text_box.setPlaceholderText("접속 주소를 입력하세요.")

        self.url_text_box.setStyleSheet(
            """
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #868686;
                border-radius: 4px;
                padding: 0 24px;
                font-family: "Noto Sans KR";
                font-size: 18px;
                font-weight: 400;
                color: #000000;
                selection-background-color: #4A90E2;
                selection-color: white;
            }
            QLineEdit::placeholder {
                color: #6B6B6B;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background-color: #FFFFFF;
            }
        """
        )
        url_row_layout.addWidget(self.url_text_box)

        self.url_row.setLayout(url_row_layout)
        self.right_layout.addWidget(self.url_row)

        # 20px gap
        self.right_layout.addSpacing(20)

        # ========== 시험 API 영역 ==========
        self.api_section = QWidget()
        self.api_section.setFixedSize(1064, 251)
        self.api_section.setStyleSheet("background: transparent;")
        self.original_api_section_size = (1064, 251)

        api_section_layout = QVBoxLayout(self.api_section)
        api_section_layout.setContentsMargins(0, 0, 0, 0)
        api_section_layout.setSpacing(8)

        self.api_label = QLabel("시험 API")
        self.api_label.setFixedSize(1064, 24)
        self.original_api_label_size = (1064, 24)
        self.api_label.setStyleSheet(
            """
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """
        )
        api_section_layout.addWidget(self.api_label)

        self.init_centerLayout()
        self.api_content_widget = QWidget()
        self.api_content_widget.setFixedSize(1064, 219)
        self.original_api_content_widget_size = (1064, 219)
        self.api_content_widget.setStyleSheet("background: transparent;")
        self.api_content_widget.setLayout(self.centerLayout)
        api_section_layout.addWidget(self.api_content_widget)

        self.right_layout.addWidget(self.api_section)

        # 20px gap
        self.right_layout.addSpacing(20)

        # ========== 수신 메시지 실시간 모니터링 영역 ==========
        self.monitor_section = QWidget()
        self.monitor_section.setFixedSize(1064, 157)
        self.monitor_section.setStyleSheet("background: transparent;")
        self.original_monitor_section_size = (1064, 157)

        monitor_section_layout = QVBoxLayout(self.monitor_section)
        monitor_section_layout.setContentsMargins(0, 0, 0, 0)
        monitor_section_layout.setSpacing(0)

        self.monitor_label = QLabel("수신 메시지 실시간 모니터링")
        self.monitor_label.setFixedSize(1064, 24)
        self.original_monitor_label_size = (1064, 24)
        self.monitor_label.setStyleSheet(
            """
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """
        )
        monitor_section_layout.addWidget(self.monitor_label)
        monitor_section_layout.addSpacing(8)

        self.text_browser_container = QWidget()
        self.text_browser_container.setFixedSize(1064, 125)
        self.original_text_browser_container_size = (1064, 125)

        self.valResult = QTextBrowser(self.text_browser_container)
        self.valResult.setFixedSize(1064, 125)
        self.original_valResult_size = (1064, 125)
        self.valResult.setStyleSheet(
            """
            QTextBrowser {
                background: #FFF;
                border-radius: 4px;
                border: 1px solid #CECECE;
                font-family: "Noto Sans KR";
                font-size: 32px;
                font-weight: 400;
                color: #1B1B1C;
            }
            QScrollBar:vertical {
                border: none;
                background: #DFDFDF;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #A3A9AD;
                min-height: 20px;
                border-radius: 4px;
                margin: 0px 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8A9094;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """
        )
        self.valResult.setViewportMargins(24, 0, 12, 0)

        self.placeholder_label = QLabel("모니터링 내용이 표출됩니다", self.text_browser_container)
        self.placeholder_label.setGeometry(24, 16, 1000, 30)
        self.placeholder_label.setStyleSheet(
            """
            QLabel {
                color: #CECECE;
                font-family: "Noto Sans KR";
                font-size: 20px;
                font-weight: 400;
                background: transparent;
            }
        """
        )
        self.placeholder_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.valResult.textChanged.connect(self._toggle_placeholder)

        monitor_section_layout.addWidget(self.text_browser_container)
        self.right_layout.addWidget(self.monitor_section)

        self._toggle_placeholder()
        self.right_layout.addSpacing(20)

        # ========== 시험 점수 요약 섹션 ==========
        self.valmsg = QLabel("시험 점수 요약", self)
        self.valmsg.setFixedSize(1064, 24)
        self.original_valmsg_size = (1064, 24)
        self.valmsg.setStyleSheet(
            """
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """
        )
        self.right_layout.addWidget(self.valmsg)
        self.right_layout.addSpacing(6)

        self.score_table = QWidget()
        self.score_table.setFixedSize(1064, 256)
        self.original_score_table_size = (1064, 256)
        self.score_table.setStyleSheet(
            """
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
            }
        """
        )

        score_table_layout = QVBoxLayout()
        score_table_layout.setContentsMargins(0, 0, 0, 0)
        score_table_layout.setSpacing(0)

        self.spec_score_group = self.create_spec_score_display_widget()
        score_table_layout.addWidget(self.spec_score_group)

        self.total_score_group = self.create_total_score_display_widget()
        score_table_layout.addWidget(self.total_score_group)

        self.score_table.setLayout(score_table_layout)
        self.right_layout.addWidget(self.score_table)

        self.right_layout.addSpacing(30)

        # ========== 버튼 그룹 ==========
        self.buttonGroup = QWidget()
        self.buttonGroup.setFixedSize(1064, 48)
        self.original_buttonGroup_size = (1064, 48)
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignRight)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setSpacing(10)
        self.button_spacing = 16

        self.sbtn = self._create_button(
            "assets/image/test_config/btn_시험시작_enabled.png",
            "assets/image/test_config/btn_시험시작_Hover.png",
            self.start_btn_clicked,
            width=108,
            height=48,
        )

        self.stop_btn = self._create_button(
            "assets/image/test_config/btn_일시정지_enabled.png",
            "assets/image/test_config/btn_일시정지_Hover.png",
            self.stop_btn_clicked,
            width=108,
            height=48,
        )
        self.stop_btn.setDisabled(True)

        self.result_btn = self._create_button(
            "assets/image/test_config/btn_결과확인_enabled.png",
            "assets/image/test_config/btn_결과확인_Hover.png",
            self.show_result_page,
            width=108,
            height=48,
        )

        self.rbtn = self._create_button(
            "assets/image/test_config/btn_종료_enabled.png",
            "assets/image/test_config/btn_종료_Hover.png",
            self.exit_btn_clicked,
            width=108,
            height=48,
        )

        self.buttonLayout.addWidget(self.sbtn)
        self.buttonLayout.addWidget(self.stop_btn)
        self.buttonLayout.addWidget(self.result_btn)
        self.buttonLayout.addWidget(self.rbtn)

        self.buttonGroup.setLayout(self.buttonLayout)
        self.right_layout.addWidget(self.buttonGroup)

        self.right_col.setLayout(self.right_layout)

        columns_layout.addWidget(self.left_col)
        columns_layout.addWidget(self.right_col)

        bg_root_layout.addLayout(columns_layout)
        self.bg_root.setLayout(bg_root_layout)

        # content_widget 레이아웃 설정 (좌우 48px, 하단 44px padding, 가운데 정렬)
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(48, 0, 48, 44)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.bg_root, 0, Qt.AlignHCenter | Qt.AlignVCenter)

        mainLayout.addWidget(self.content_widget, 1)
        self.setLayout(mainLayout)

        if not getattr(self, "embedded", False):
            QTimer.singleShot(100, self.select_first_scenario)
            self.show()

    def _create_button(self, normal_img, hover_img, callback, width=108, height=48):
        btn = QPushButton()
        btn.setFixedSize(width, height)

        normal_path = resource_path(normal_img).replace(chr(92), "/")
        hover_path = resource_path(hover_img).replace(chr(92), "/")

        btn.setStyleSheet(
            f"""
            QPushButton {{
                border-image: url({normal_path});
                background-color: transparent;
                border: none;
            }}
            QPushButton:hover {{
                border-image: url({hover_path});
            }}
        """
        )
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        return btn

    def _toggle_placeholder(self):
        """텍스트 브라우저 내용 유무에 따라 placeholder 표시 토글"""
        if hasattr(self, "valResult") and hasattr(self, "placeholder_label"):
            if not self.valResult.toPlainText().strip():
                self.placeholder_label.show()
                self.valResult.setStyleSheet(
                    self.valResult.styleSheet().replace("background: #FFF;", "background: #F4F4F4;")
                )
            else:
                self.placeholder_label.hide()
                self.valResult.setStyleSheet(
                    self.valResult.styleSheet().replace("background: #F4F4F4;", "background: #FFF;")
                )

    def create_spec_selection_panel(self, layout):
        """시험 분야 선택 패널 생성"""
        self.spec_panel_title = QLabel("시험 선택")
        self.spec_panel_title.setFixedSize(424, 24)
        self.original_spec_panel_title_size = (424, 24)
        self.spec_panel_title.setStyleSheet(
            """
            font-size: 20px;
            font-style: normal;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
            letter-spacing: -0.3px;
        """
        )
        layout.addWidget(self.spec_panel_title)
        layout.addSpacing(8)

        self.test_selection_panel = TestSelectionPanel(self.CONSTANTS)
        self.test_selection_panel.groupSelected.connect(self.on_group_selected)
        self.test_selection_panel.scenarioSelected.connect(self.on_test_field_selected)
        layout.addWidget(self.test_selection_panel)

    def create_spec_score_display_widget(self):
        """메인 화면에 표시할 시험 분야별 평가 점수 위젯"""
        spec_group = QGroupBox()
        spec_group.setFixedSize(1064, 128)
        self.original_spec_group_size = (1064, 128)
        spec_group.setStyleSheet(
            """
            QGroupBox {
                background-color: #FFF;
                border: 1px solid #CECECE;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                padding: 0px;
                margin: 0px;
            }
        """
        )

        icon_label = QLabel()
        icon_label.setFixedSize(52, 42)
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_분야별점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(52, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        score_type_label = QLabel("분야별 점수")
        score_type_label.setStyleSheet(
            """
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """
        )

        header_vline = QFrame()
        header_vline.setFixedSize(1, 16)
        header_vline.setStyleSheet("background-color: #CECECE;")

        self.spec_name_label = QLabel("시험 분야 명")
        self.spec_name_label.setStyleSheet(
            """
            color: #666666;
            font-family: "Noto Sans KR";
            font-size: 18px;
            font-weight: 400;
        """
        )

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet(
            """
            QFrame {
                color: #CECECE;
                background-color: #CECECE;
            }
        """
        )
        separator.setFixedHeight(1)

        self.spec_pass_label = QLabel("통과 필드 수")
        self.original_score_label_width = 325
        self.spec_pass_label.setFixedHeight(60)
        self.spec_pass_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.spec_pass_label.setStyleSheet(
            """
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """
        )

        self.spec_total_label = QLabel("전체 필드 수")
        self.spec_total_label.setFixedHeight(60)
        self.spec_total_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.spec_total_label.setStyleSheet(
            """
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """
        )

        self.spec_score_label = QLabel("종합 평가 점수")
        self.spec_score_label.setFixedHeight(60)
        self.spec_score_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.spec_score_label.setStyleSheet(
            """
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """
        )

        spec_layout = QVBoxLayout()
        spec_layout.setContentsMargins(0, 0, 0, 0)
        spec_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedSize(1064, 52)
        self.original_spec_header_widget_size = (1064, 52)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 5, 0, 5)
        header_layout.setSpacing(12)
        header_layout.addWidget(icon_label, alignment=Qt.AlignVCenter)
        header_layout.addWidget(score_type_label, alignment=Qt.AlignVCenter)
        header_layout.addWidget(header_vline, alignment=Qt.AlignVCenter)
        header_layout.addWidget(self.spec_name_label, alignment=Qt.AlignVCenter)
        header_layout.addStretch()

        spec_layout.addWidget(header_widget)
        spec_layout.addWidget(separator)

        self.spec_data_widget = QWidget()
        self.spec_data_widget.setFixedSize(1064, 76)
        self.original_spec_data_widget_size = (1064, 76)
        spec_score_layout = QHBoxLayout(self.spec_data_widget)
        spec_score_layout.setContentsMargins(56, 8, 32, 8)
        spec_score_layout.setSpacing(0)

        spec_score_layout.addWidget(self.spec_pass_label)
        spec_vline1 = QFrame()
        spec_vline1.setFixedSize(2, 60)
        spec_vline1.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline1)
        spec_spacer1 = QWidget()
        spec_spacer1.setFixedSize(24, 60)
        spec_score_layout.addWidget(spec_spacer1)

        spec_score_layout.addWidget(self.spec_total_label)
        spec_vline2 = QFrame()
        spec_vline2.setFixedSize(2, 60)
        spec_vline2.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline2)
        spec_spacer2 = QWidget()
        spec_spacer2.setFixedSize(24, 60)
        spec_score_layout.addWidget(spec_spacer2)

        spec_score_layout.addWidget(self.spec_score_label)
        spec_score_layout.addStretch()

        spec_layout.addWidget(self.spec_data_widget)
        spec_group.setLayout(spec_layout)

        return spec_group

    def create_total_score_display_widget(self):
        """메인 화면에 표시할 전체 평가 점수 위젯"""
        total_group = QGroupBox()
        total_group.setFixedSize(1064, 128)
        self.original_total_group_size = (1064, 128)
        total_group.setStyleSheet(
            """
            QGroupBox {
                background-color: #F0F6FB;
                border: 1px solid #CECECE;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
                padding: 0px;
                margin: 0px;
            }
        """
        )

        icon_label = QLabel()
        icon_label.setFixedSize(52, 42)
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_전체점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(52, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        total_name_label = QLabel("전체 점수")
        total_name_label.setStyleSheet(
            """
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """
        )

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet(
            """
            QFrame {
                color: #CECECE;
                background-color: #CECECE;
            }
        """
        )
        separator.setFixedHeight(1)

        self.total_pass_label = QLabel("통과 필드 수")
        self.total_pass_label.setFixedHeight(60)
        self.total_pass_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.total_pass_label.setStyleSheet(
            """
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """
        )

        self.total_total_label = QLabel("전체 필드 수")
        self.total_total_label.setFixedHeight(60)
        self.total_total_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.total_total_label.setStyleSheet(
            """
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """
        )

        self.total_score_label = QLabel("종합 평가 점수")
        self.total_score_label.setFixedHeight(60)
        self.total_score_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.total_score_label.setStyleSheet(
            """
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """
        )

        total_layout = QVBoxLayout()
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedSize(1064, 52)
        self.original_total_header_widget_size = (1064, 52)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 5, 0, 5)
        header_layout.setSpacing(6)
        header_layout.addWidget(icon_label, alignment=Qt.AlignVCenter)
        header_layout.addWidget(total_name_label, alignment=Qt.AlignVCenter)
        header_layout.addStretch()

        total_layout.addWidget(header_widget)
        total_layout.addWidget(separator)

        self.total_data_widget = QWidget()
        self.total_data_widget.setFixedSize(1064, 76)
        self.original_total_data_widget_size = (1064, 76)
        score_layout = QHBoxLayout(self.total_data_widget)
        score_layout.setContentsMargins(56, 8, 32, 8)
        score_layout.setSpacing(0)

        score_layout.addWidget(self.total_pass_label)
        total_vline1 = QFrame()
        total_vline1.setFixedSize(2, 60)
        total_vline1.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline1)
        total_spacer1 = QWidget()
        total_spacer1.setFixedSize(24, 60)
        score_layout.addWidget(total_spacer1)

        score_layout.addWidget(self.total_total_label)
        total_vline2 = QFrame()
        total_vline2.setFixedSize(2, 60)
        total_vline2.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline2)
        total_spacer2 = QWidget()
        total_spacer2.setFixedSize(24, 60)
        score_layout.addWidget(total_spacer2)

        score_layout.addWidget(self.total_score_label)
        score_layout.addStretch()

        total_layout.addWidget(self.total_data_widget)
        total_group.setLayout(total_layout)

        return total_group

    def init_centerLayout(self):
        # 표 형태로 변경 - 동적 API 개수
        api_count = len(getattr(self, "videoMessages", []))

        self.api_header_widget = QWidget()
        self.api_header_widget.setFixedSize(1064, 30)
        self.original_api_header_widget_size = (1064, 30)
        self.api_header_widget.setStyleSheet(
            """
            QWidget {
                background-color: #EDF0F3;
                border: 1px solid #CECECE;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        """
        )
        header_layout = QHBoxLayout(self.api_header_widget)
        header_layout.setContentsMargins(0, 0, 14, 0)
        header_layout.setSpacing(0)

        header_columns = [
            (40, ""),
            (261, "API 명"),
            (100, "결과"),
            (94, "검증 횟수"),
            (116, "통과 필드 수"),
            (116, "전체 필드 수"),
            (94, "실패 횟수"),
            (94, "평가 점수"),
            (133, "상세 내용"),
        ]

        self.header_labels = []
        self.original_header_widths = [col[0] for col in header_columns]

        for width, text in header_columns:
            label = QLabel(text)
            label.setFixedSize(width, 30)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(
                """
                QLabel {
                    background-color: transparent;
                    border: none;
                    color: #1B1B1C;
                    font-family: 'Noto Sans KR';
                    font-size: 18px;
                    font-weight: 600;
                }
            """
            )
            self.header_labels.append(label)
            header_layout.addWidget(label)

        self.tableWidget = QTableWidget(api_count, 9)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QSize(16, 16))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.tableWidget.setStyleSheet(
            """
            QTableWidget {
                background: #FFF;
                border: none;
                font-size: 18px;
                color: #222;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                border-right: 0px solid transparent;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-style: normal;
                font-weight: 400;
                text-align: center;
            }
        """
        )

        self.tableWidget.setShowGrid(False)

        self.original_column_widths = [40, 261, 100, 94, 116, 116, 94, 94, 133]
        for i, width in enumerate(self.original_column_widths):
            self.tableWidget.setColumnWidth(i, width)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)

        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 40)

        step_names = getattr(self, "videoMessages", [])
        for i, name in enumerate(step_names):
            no_item = QTableWidgetItem(f"{i + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(i, 0, no_item)

            api_item = QTableWidgetItem(name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(i, 1, api_item)

            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)

            icon_label = QLabel()
            if hasattr(self, "img_none"):
                icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)

            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)

            self.tableWidget.setCellWidget(i, 2, icon_widget)

            self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
            self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(i, 4, QTableWidgetItem("0"))
            self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(i, 5, QTableWidgetItem("0"))
            self.tableWidget.item(i, 5).setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(i, 6, QTableWidgetItem("0"))
            self.tableWidget.item(i, 6).setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(i, 7, QTableWidgetItem("0%"))
            self.tableWidget.item(i, 7).setTextAlignment(Qt.AlignCenter)

            detail_label = QLabel()
            img_path = resource_path("assets/image/test_runner/btn_상세내용확인.png").replace(chr(92), "/")
            pixmap = QPixmap(img_path)
            detail_label.setPixmap(pixmap)
            detail_label.setScaledContents(False)
            detail_label.setFixedSize(pixmap.size())
            detail_label.setCursor(Qt.PointingHandCursor)
            detail_label.setAlignment(Qt.AlignCenter)

            detail_label.mousePressEvent = lambda event, row=i: self.show_combined_result(row)

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(i, 8, container)

        self.tableWidget.cellClicked.connect(self.table_cell_clicked)

        self.api_scroll_area = QScrollArea()
        self.api_scroll_area.setWidget(self.tableWidget)
        self.api_scroll_area.setWidgetResizable(True)
        self.api_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.api_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.api_scroll_area.setFixedSize(1064, 189)
        self.original_api_scroll_area_size = (1064, 189)
        self.api_scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: 1px solid #CECECE;
                border-top: none;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #FFFFFF;
            }
            QScrollBar:vertical {
                border: none;
                background: #DFDFDF;
                width: 14px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #A3A9AD;
                min-height: 20px;
                border-radius: 4px;
                margin: 0px 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8A9094;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """
        )

        self.centerLayout = QVBoxLayout()
        self.centerLayout.setContentsMargins(0, 0, 0, 0)
        self.centerLayout.setSpacing(0)
        self.centerLayout.addWidget(self.api_header_widget)
        self.centerLayout.addWidget(self.api_scroll_area)
        self.centerLayout.addStretch()

    def resizeEvent(self, event):
        """창 크기 변경 시 배경 이미지 및 왼쪽 패널 크기 재조정"""
        super().resizeEvent(event)

        if hasattr(self, "content_widget") and self.content_widget:
            if hasattr(self, "content_bg_label"):
                content_width = self.content_widget.width()
                content_height = self.content_widget.height()
                self.content_bg_label.setGeometry(0, 0, content_width, content_height)

        if hasattr(self, "original_window_size") and hasattr(self, "left_col"):
            current_width = self.width()
            current_height = self.height()

            width_ratio = max(1.0, current_width / self.original_window_size[0])
            height_ratio = max(1.0, current_height / self.original_window_size[1])

            original_column_height = 898
            extra_column_height = original_column_height * (height_ratio - 1)

            left_expandable_total = 204 + 526
            right_expandable_total = 251 + 157

            if hasattr(self, "bg_root") and hasattr(self, "original_bg_root_size"):
                new_bg_width = int(self.original_bg_root_size[0] * width_ratio)
                new_bg_height = int(self.original_bg_root_size[1] * height_ratio)
                self.bg_root.setFixedSize(new_bg_width, new_bg_height)

            if hasattr(self, "original_left_col_size"):
                new_left_width = int(self.original_left_col_size[0] * width_ratio)
                new_left_height = int(self.original_left_col_size[1] * height_ratio)
                self.left_col.setFixedSize(new_left_width, new_left_height)

            if hasattr(self, "spec_panel_title") and hasattr(self, "original_spec_panel_title_size"):
                new_title_width = int(self.original_spec_panel_title_size[0] * width_ratio)
                self.spec_panel_title.setFixedSize(new_title_width, self.original_spec_panel_title_size[1])

            if hasattr(self, "group_table_widget") and hasattr(self, "original_group_table_widget_size"):
                new_group_width = int(self.original_group_table_widget_size[0] * width_ratio)
                group_extra = extra_column_height * (204 / left_expandable_total)
                new_group_height = int(204 + group_extra)
                self.group_table_widget.setFixedSize(new_group_width, new_group_height)
                if hasattr(self, "group_table"):
                    self.group_table.setFixedHeight(new_group_height)

            if hasattr(self, "field_group") and hasattr(self, "original_field_group_size"):
                new_field_width = int(self.original_field_group_size[0] * width_ratio)
                field_extra = extra_column_height * (526 / left_expandable_total)
                new_field_height = int(526 + field_extra)
                self.field_group.setFixedSize(new_field_width, new_field_height)
                if hasattr(self, "test_field_table"):
                    self.test_field_table.setFixedHeight(new_field_height)

            if hasattr(self, "right_col") and hasattr(self, "original_right_col_size"):
                new_right_width = int(self.original_right_col_size[0] * width_ratio)
                new_right_height = int(self.original_right_col_size[1] * height_ratio)
                self.right_col.setFixedSize(new_right_width, new_right_height)

            if hasattr(self, "url_row") and hasattr(self, "original_url_row_size"):
                new_url_width = int(self.original_url_row_size[0] * width_ratio)
                self.url_row.setFixedSize(new_url_width, self.original_url_row_size[1])

            if hasattr(self, "api_section") and hasattr(self, "original_api_section_size"):
                new_api_width = int(self.original_api_section_size[0] * width_ratio)
                api_extra = extra_column_height * (251 / right_expandable_total)
                new_api_height = int(251 + api_extra)
                self.api_section.setFixedSize(new_api_width, new_api_height)

            if hasattr(self, "monitor_section") and hasattr(self, "original_monitor_section_size"):
                new_monitor_width = int(self.original_monitor_section_size[0] * width_ratio)
                monitor_extra = extra_column_height * (157 / right_expandable_total)
                new_monitor_height = int(157 + monitor_extra)
                self.monitor_section.setFixedSize(new_monitor_width, new_monitor_height)

            if hasattr(self, "original_buttonGroup_size"):
                new_group_width = int(self.original_buttonGroup_size[0] * width_ratio)
                btn_height = self.original_buttonGroup_size[1]
                self.buttonGroup.setFixedSize(new_group_width, btn_height)
                self._update_button_positions(new_group_width, btn_height)

            if hasattr(self, "url_text_box") and hasattr(self, "original_url_text_box_size"):
                new_url_tb_width = int(self.original_url_text_box_size[0] * width_ratio)
                self.url_text_box.setFixedSize(new_url_tb_width, self.original_url_text_box_size[1])

            if hasattr(self, "api_label") and hasattr(self, "original_api_label_size"):
                new_api_label_width = int(self.original_api_label_size[0] * width_ratio)
                self.api_label.setFixedSize(new_api_label_width, self.original_api_label_size[1])

            if hasattr(self, "api_content_widget") and hasattr(self, "original_api_content_widget_size"):
                new_api_cw_width = int(self.original_api_content_widget_size[0] * width_ratio)
                new_api_cw_height = int(219 + api_extra)
                self.api_content_widget.setFixedSize(new_api_cw_width, new_api_cw_height)

            if hasattr(self, "monitor_label") and hasattr(self, "original_monitor_label_size"):
                new_mon_label_width = int(self.original_monitor_label_size[0] * width_ratio)
                self.monitor_label.setFixedSize(new_mon_label_width, self.original_monitor_label_size[1])

            if hasattr(self, "text_browser_container") and hasattr(self, "original_text_browser_container_size"):
                new_tbc_width = int(self.original_text_browser_container_size[0] * width_ratio)
                new_tbc_height = int(125 + monitor_extra)
                self.text_browser_container.setFixedSize(new_tbc_width, new_tbc_height)

            if hasattr(self, "valResult") and hasattr(self, "original_valResult_size"):
                new_vr_width = int(self.original_valResult_size[0] * width_ratio)
                new_vr_height = int(125 + monitor_extra)
                self.valResult.setFixedSize(new_vr_width, new_vr_height)

            if hasattr(self, "valmsg") and hasattr(self, "original_valmsg_size"):
                new_valmsg_width = int(self.original_valmsg_size[0] * width_ratio)
                self.valmsg.setFixedSize(new_valmsg_width, self.original_valmsg_size[1])

            if hasattr(self, "spec_score_group") and hasattr(self, "original_spec_group_size"):
                new_spec_width = int(self.original_spec_group_size[0] * width_ratio)
                self.spec_score_group.setFixedSize(new_spec_width, self.original_spec_group_size[1])

            if hasattr(self, "total_score_group") and hasattr(self, "original_total_group_size"):
                new_total_width = int(self.original_total_group_size[0] * width_ratio)
                self.total_score_group.setFixedSize(new_total_width, self.original_total_group_size[1])

            if hasattr(self, "spec_data_widget") and hasattr(self, "original_spec_data_widget_size"):
                new_spec_data_width = int(self.original_spec_data_widget_size[0] * width_ratio)
                self.spec_data_widget.setFixedSize(new_spec_data_width, self.original_spec_data_widget_size[1])

            if hasattr(self, "total_data_widget") and hasattr(self, "original_total_data_widget_size"):
                new_total_data_width = int(self.original_total_data_widget_size[0] * width_ratio)
                self.total_data_widget.setFixedSize(new_total_data_width, self.original_total_data_widget_size[1])

            if hasattr(self, "api_header_widget") and hasattr(self, "original_api_header_widget_size"):
                new_header_width = int(self.original_api_header_widget_size[0] * width_ratio)
                self.api_header_widget.setFixedSize(new_header_width, self.original_api_header_widget_size[1])

            if hasattr(self, "api_scroll_area") and hasattr(self, "original_api_scroll_area_size"):
                new_scroll_width = int(self.original_api_scroll_area_size[0] * width_ratio)
                new_scroll_height = int(189 + api_extra)
                self.api_scroll_area.setFixedSize(new_scroll_width, new_scroll_height)

            if hasattr(self, "tableWidget") and hasattr(self, "original_column_widths"):
                row_count = self.tableWidget.rowCount()
                total_row_height = row_count * 40
                scrollbar_visible = total_row_height > new_scroll_height
                scrollbar_width = 16 if scrollbar_visible else 2

                available_width = new_scroll_width - scrollbar_width

                used_width = 0
                for i, orig_width in enumerate(self.original_column_widths[:-1]):
                    new_col_width = int(orig_width * width_ratio)
                    self.tableWidget.setColumnWidth(i, new_col_width)
                    used_width += new_col_width

                last_col_width = available_width - used_width
                self.tableWidget.setColumnWidth(len(self.original_column_widths) - 1, last_col_width)

            if hasattr(self, "header_labels") and hasattr(self, "original_header_widths"):
                for i, label in enumerate(self.header_labels):
                    new_label_width = int(self.original_header_widths[i] * width_ratio)
                    label.setFixedSize(new_label_width, 30)

    def _update_button_positions(self, group_width=None, group_height=None):
        pass

    # placeholder methods
    def start_btn_clicked(self): 
        pass

    def stop_btn_clicked(self): 
        pass

    def exit_btn_clicked(self): 
        pass

    def show_result_page(self): 
        pass

    def show_combined_result(self, row): 
        pass

    def table_cell_clicked(self, row, col): 
        pass

    def on_group_selected(self, row, col): 
        pass

    def on_test_field_selected(self, row, col): 
        pass

    def select_first_scenario(self): 
        pass