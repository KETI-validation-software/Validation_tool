from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize
from core.functions import resource_path
from ui.ui_components import TestSelectionPanel
from ui.detail_dialog import CombinedDetailDialog
from ui.gui_utils import CustomDialog
from ui.common_main_ui import CommonMainUI

class PlatformMainUI(CommonMainUI):
    """
    메인 화면의 UI 구성 및 반응형 처리를 담당하는 클래스
    """
    def __init__(self):
        super().__init__()
        # Platform 전용 설정
        self.window_title = '통합플랫폼 연동 검증'
        self.show_initial_score = True  # 초기 점수 표시 활성화

    def initUI(self):
        # CommonMainUI의 initUI 호출
        super().initUI()

    def connect_buttons(self):
        """버튼 이벤트 연결 (Platform 전용)"""
        self.sbtn.clicked.connect(self.sbtn_push)
        self.stop_btn.clicked.connect(self.stop_btn_clicked)
        self.rbtn.clicked.connect(self.exit_btn_clicked)
        self.result_btn.clicked.connect(self.show_result_page)

    def init_centerLayout(self):
        # 동적 API 개수에 따라 테이블 생성
        api_count = len(self.videoMessages)

        # 별도 헤더 위젯 (1064px 전체 너비)
        self.api_header_widget = QWidget()
        self.api_header_widget.setFixedSize(1064, 30)
        self.original_api_header_widget_size = (1064, 30)
        self.api_header_widget.setStyleSheet("""
            QWidget {
                background-color: #EDF0F3;
                border: 1px solid #CECECE;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        """)
        header_layout = QHBoxLayout(self.api_header_widget)
        header_layout.setContentsMargins(0, 0, 14, 0)  # 오른쪽 14px (스크롤바 영역)
        header_layout.setSpacing(0)

        # 헤더 컬럼 정의 (너비, 텍스트) - 9컬럼 구조
        header_columns = [
            (40, ""),            # No.
            (261, "API 명"),
            (100, "결과"),
            (94, "검증 횟수"),
            (116, "통과 필드 수"),
            (116, "전체 필드 수"),
            (94, "실패 횟수"),
            (94, "평가 점수"),
            (133, "상세 내용")
        ]

        # 헤더 라벨 저장 (반응형 조정용)
        self.header_labels = []
        self.original_header_widths = [col[0] for col in header_columns]

        for i, (width, text) in enumerate(header_columns):
            label = QLabel(text)
            label.setFixedSize(width, 30)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                    color: #1B1B1C;
                    font-family: 'Noto Sans KR';
                    font-size: 18px;
                    font-weight: 600;
                }
            """)
            self.header_labels.append(label)
            header_layout.addWidget(label)

        # 테이블 본문 (헤더 숨김)
        self.tableWidget = QTableWidget(api_count, 9)  # 9개 컬럼
        # self.tableWidget.setFixedWidth(1050)  # setWidgetResizable(True) 사용으로 주석 처리
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QSize(16, 16))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.tableWidget.setStyleSheet("""
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
        """)

        self.tableWidget.setShowGrid(False)

        # 컬럼 너비 설정 - 9컬럼 구조 (원본 너비 저장)
        self.original_column_widths = [40, 261, 100, 94, 116, 116, 94, 94, 133]
        for i, width in enumerate(self.original_column_widths):
            self.tableWidget.setColumnWidth(i, width)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)  # 비례 조정을 위해 비활성화

        # 행 높이 설정 (40px)
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 40)

        # 단계명 리스트
        self.step_names = self.videoMessages
        for i, name in enumerate(self.step_names):
            # No. (숫자) - 컬럼 0
            no_item = QTableWidgetItem(f"{i + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(i, 0, no_item)

            # API 명 - 컬럼 1
            api_item = QTableWidgetItem(name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(i, 1, api_item)

            # 결과 아이콘 - 컬럼 2
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)

            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)

            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)

            self.tableWidget.setCellWidget(i, 2, icon_widget)

            # 검증 횟수 - 컬럼 3
            self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
            self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)

            # 통과 필드 수 - 컬럼 4
            self.tableWidget.setItem(i, 4, QTableWidgetItem("0"))
            self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)

            # 전체 필드 수 - 컬럼 5
            self.tableWidget.setItem(i, 5, QTableWidgetItem("0"))
            self.tableWidget.item(i, 5).setTextAlignment(Qt.AlignCenter)

            # 실패 횟수 - 컬럼 6
            self.tableWidget.setItem(i, 6, QTableWidgetItem("0"))
            self.tableWidget.item(i, 6).setTextAlignment(Qt.AlignCenter)

            # 평가 점수 - 컬럼 7
            self.tableWidget.setItem(i, 7, QTableWidgetItem("0%"))
            self.tableWidget.item(i, 7).setTextAlignment(Qt.AlignCenter)

            # 상세 내용 버튼 - 컬럼 8
            detail_label = QLabel()
            img_path = resource_path("assets/image/test_runner/btn_상세내용확인.png").replace("\\", "/")
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

        # 결과 컬럼만 클릭 가능
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)

        # ✅ QScrollArea로 본문만 감싸기 (헤더 아래부터 스크롤)
        self.api_scroll_area = QScrollArea()
        self.api_scroll_area.setWidget(self.tableWidget)
        self.api_scroll_area.setWidgetResizable(True)
        self.api_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.api_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 필요할 때만 스크롤바 표시
        self.api_scroll_area.setFixedSize(1064, 189)  # 헤더 제외 (219 - 30)
        self.original_api_scroll_area_size = (1064, 189)
        self.api_scroll_area.setStyleSheet("""
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
        """)

        # centerLayout을 초기화하고 헤더 + 스크롤 영역 추가
        self.centerLayout = QVBoxLayout()
        self.centerLayout.setContentsMargins(0, 0, 0, 0)
        self.centerLayout.setSpacing(0)
        self.centerLayout.addWidget(self.api_header_widget)
        self.centerLayout.addWidget(self.api_scroll_area)
        self.centerLayout.addStretch()  # 세로 확장 시 여분 공간을 하단으로

    def create_spec_selection_panel(self, parent_layout):
        """시험 선택 패널 - TestSelectionPanel 사용"""
        self.test_selection_panel = TestSelectionPanel(self.CONSTANTS)
        
        # 시그널 연결
        self.test_selection_panel.groupSelected.connect(self.on_group_selected)
        self.test_selection_panel.scenarioSelected.connect(self.on_test_field_selected)
        
        # 멤버 변수 매핑 (기존 코드와의 호환성 유지)
        self.group_table = self.test_selection_panel.group_table
        self.test_field_table = self.test_selection_panel.test_field_table
        self.group_name_to_index = self.test_selection_panel.group_name_to_index
        self.index_to_group_name = self.test_selection_panel.index_to_group_name
        self.spec_id_to_index = self.test_selection_panel.spec_id_to_index
        self.index_to_spec_id = self.test_selection_panel.index_to_spec_id

        # ✅ 반응형 처리를 위한 UI 컴포넌트 매핑
        self.spec_panel_title = self.test_selection_panel.spec_panel_title
        self.group_table_widget = self.test_selection_panel.group_table_widget
        self.field_group = self.test_selection_panel.field_group
        
        # ✅ 반응형 처리를 위한 원본 사이즈 매핑
        self.original_spec_panel_title_size = self.test_selection_panel.original_spec_panel_title_size
        self.original_group_table_widget_size = self.test_selection_panel.original_group_table_widget_size
        self.original_field_group_size = self.test_selection_panel.original_field_group_size

        parent_layout.addWidget(self.test_selection_panel)

    def _toggle_placeholder(self):
        """텍스트 유무에 따라 placeholder 표시/숨김"""
        if hasattr(self, 'placeholder_label'):
            if self.valResult.toPlainText().strip():
                self.placeholder_label.hide()
            else:
                self.placeholder_label.show()

    def create_spec_score_display_widget(self):
        """메인 화면에 표시할 시험 분야별 평가 점수 위젯"""

        spec_group = QGroupBox()
        spec_group.setFixedSize(1064, 128)
        self.original_spec_group_size = (1064, 128)
        spec_group.setStyleSheet("""
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
        """)

        # 분야별 점수 아이콘 (52 × 42)
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_분야별점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(52, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(52, 42)
        icon_label.setAlignment(Qt.AlignCenter)

        # 분야별 점수 레이블 (500 Medium 20px)
        score_type_label = QLabel("분야별 점수")
        score_type_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
        """)

        # 세로선 (27px)
        header_vline = QFrame()
        header_vline.setFrameShape(QFrame.VLine)
        header_vline.setFixedSize(1, 27)
        header_vline.setStyleSheet("background-color: #000000;")

        # spec 정보 레이블 (500 Medium 20px)
        self.spec_name_label = QLabel(f"{self.spec_description} ({len(self.videoMessages)}개 API)")
        self.spec_name_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
        """)

        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet("""
            QFrame {
                color: #CECECE;
                background-color: #CECECE;
            }
        """)
        separator.setFixedHeight(1)

        # 점수 레이블들 - 각 라벨별 다른 너비 (통과 필수/선택은 넓게, 종합 평가는 좁게)
        # 원본 크기 저장 (반응형 조정용)
        self.original_pass_label_width = 340    # 통과 필수 필드 점수
        self.original_opt_label_width = 340     # 통과 선택 필드 점수
        self.original_score_label_width = 315   # 종합 평가 점수

        self.spec_pass_label = QLabel("통과 필수 필드 점수")
        self.spec_pass_label.setFixedSize(340, 60)
        self.spec_pass_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 19px;
            font-weight: 500;
        """)
        self.spec_total_label = QLabel("통과 선택 필드 점수")
        self.spec_total_label.setFixedSize(340, 60)
        self.spec_total_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 19px;
            font-weight: 500;
        """)
        self.spec_score_label = QLabel("종합 평가 점수")
        self.spec_score_label.setFixedSize(315, 60)
        self.spec_score_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 19px;
            font-weight: 500;
        """)

        spec_layout = QVBoxLayout()
        spec_layout.setContentsMargins(0, 0, 0, 0)
        spec_layout.setSpacing(0)

        # 아이콘 + 분야명 (헤더 영역 1064 × 52)
        header_widget = QWidget()
        header_widget.setFixedSize(1064, 52)
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

        # 데이터 영역 (1064 × 76)
        self.spec_data_widget = QWidget()
        self.spec_data_widget.setFixedSize(1064, 76)
        self.original_spec_data_widget_size = (1064, 76)
        spec_score_layout = QHBoxLayout(self.spec_data_widget)
        spec_score_layout.setContentsMargins(20, 8, 20, 8)
        spec_score_layout.setSpacing(0)

        # 통과 필드 수 + 구분선 + spacer
        spec_score_layout.addWidget(self.spec_pass_label)
        spec_vline1 = QFrame()
        spec_vline1.setFixedSize(2, 60)
        spec_vline1.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline1)
        spec_spacer1 = QWidget()
        spec_spacer1.setFixedSize(12, 60)
        spec_score_layout.addWidget(spec_spacer1)

        # 전체 필드 수 + 구분선 + spacer
        spec_score_layout.addWidget(self.spec_total_label)
        spec_vline2 = QFrame()
        spec_vline2.setFixedSize(2, 60)
        spec_vline2.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline2)
        spec_spacer2 = QWidget()
        spec_spacer2.setFixedSize(12, 60)
        spec_score_layout.addWidget(spec_spacer2)

        # 종합 평가 점수
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
        total_group.setStyleSheet("""
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
        """)

        # 전체 점수 아이콘 (52 × 42)
        icon_label = QLabel()
        icon_label.setFixedSize(52, 42)
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_전체점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(52, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 전체 점수 레이블 (500 Medium 20px)
        total_name_label = QLabel("전체 점수")
        total_name_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """)

        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet("""
            QFrame {
                color: #CECECE;
                background-color: #CECECE;
            }
        """)
        separator.setFixedHeight(1)

        # 점수 레이블들 - 각 라벨별 다른 너비 (통과 필수/선택은 넓게, 종합 평가는 좁게)
        self.total_pass_label = QLabel("통과 필수 필드 점수")
        self.total_pass_label.setFixedSize(340, 60)
        self.total_pass_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 19px;
            font-weight: 500;
        """)
        self.total_total_label = QLabel("통과 선택 필드 점수")
        self.total_total_label.setFixedSize(340, 60)
        self.total_total_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 19px;
            font-weight: 500;
        """)
        self.total_score_label = QLabel("종합 평가 점수")
        self.total_score_label.setFixedSize(315, 60)
        self.total_score_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 19px;
            font-weight: 500;
        """)

        total_layout = QVBoxLayout()
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.setSpacing(0)

        # 아이콘 + 전체 점수 텍스트 (헤더 영역 1064 × 52)
        header_widget = QWidget()
        header_widget.setFixedSize(1064, 52)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 5, 0, 5)
        header_layout.setSpacing(6)
        header_layout.addWidget(icon_label, alignment=Qt.AlignVCenter)
        header_layout.addWidget(total_name_label, alignment=Qt.AlignVCenter)
        header_layout.addStretch()
        total_layout.addWidget(header_widget)
        total_layout.addWidget(separator)

        # 데이터 영역 (1064 × 76)
        self.total_data_widget = QWidget()
        self.total_data_widget.setFixedSize(1064, 76)
        self.original_total_data_widget_size = (1064, 76)
        score_layout = QHBoxLayout(self.total_data_widget)
        score_layout.setContentsMargins(20, 8, 20, 8)
        score_layout.setSpacing(0)

        # 통과 필드 수 + 구분선 + spacer
        score_layout.addWidget(self.total_pass_label)
        total_vline1 = QFrame()
        total_vline1.setFixedSize(2, 60)
        total_vline1.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline1)
        total_spacer1 = QWidget()
        total_spacer1.setFixedSize(12, 60)
        score_layout.addWidget(total_spacer1)

        # 전체 필드 수 + 구분선 + spacer
        score_layout.addWidget(self.total_total_label)
        total_vline2 = QFrame()
        total_vline2.setFixedSize(2, 60)
        total_vline2.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline2)
        total_spacer2 = QWidget()
        total_spacer2.setFixedSize(12, 60)
        score_layout.addWidget(total_spacer2)

        # 종합 평가 점수
        score_layout.addWidget(self.total_score_label)
        score_layout.addStretch()

        total_layout.addWidget(self.total_data_widget)
        total_group.setLayout(total_layout)

        return total_group


    def update_score_display(self):
        """평가 점수 디스플레이를 업데이트"""
        if not (hasattr(self, "spec_pass_label") and hasattr(self, "spec_total_label") and hasattr(self, "spec_score_label")):
            return

        # ✅ 분야별 점수 제목 업데이트 (시나리오 명 변경 반영)
        if hasattr(self, "spec_name_label"):
            self.spec_name_label.setText(f"{self.spec_description} ({len(self.videoMessages)}개 API)")

        # ✅ 1️⃣ 분야별 점수 (현재 spec만) - step_pass_counts 배열의 합으로 계산
        if hasattr(self, 'step_pass_counts') and hasattr(self, 'step_error_counts'):
            self.total_pass_cnt = sum(self.step_pass_counts)
            self.total_error_cnt = sum(self.step_error_counts)
        
        # ✅ 선택 필드 통과 수 계산
        if hasattr(self, 'step_opt_pass_counts'):
            self.total_opt_pass_cnt = sum(self.step_opt_pass_counts)
        else:
            self.total_opt_pass_cnt = 0

        # ✅ 선택 필드 에러 수 계산
        if hasattr(self, 'step_opt_error_counts'):
            self.total_opt_error_cnt = sum(self.step_opt_error_counts)
        else:
            self.total_opt_error_cnt = 0

        # 필수 필드 통과 수 = 전체 통과 - 선택 통과
        spec_required_pass = self.total_pass_cnt - self.total_opt_pass_cnt

        spec_total_fields = self.total_pass_cnt + self.total_error_cnt
        # 선택 필드 전체 수 = 선택 통과 + 선택 에러
        spec_opt_total = self.total_opt_pass_cnt + self.total_opt_error_cnt
        # 필수 필드 전체 수 = 전체 필드 - 전체 선택 필드
        spec_required_total = spec_total_fields - spec_opt_total

        if spec_total_fields > 0:
            spec_score = (self.total_pass_cnt / spec_total_fields) * 100
        else:
            spec_score = 0

        # 필수 통과율 계산
        if spec_required_total > 0:
            spec_required_score = (spec_required_pass / spec_required_total) * 100
        else:
            spec_required_score = 0

        # 선택 통과율 계산
        if spec_opt_total > 0:
            spec_opt_score = (self.total_opt_pass_cnt / spec_opt_total) * 100
        else:
            spec_opt_score = 0

        # 필수/선택/종합 점수 표시 (% (통과/전체) 형식)
        self.spec_pass_label.setText(
            f"통과 필수 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 19px; font-weight: 500; color: #000000;'>"
            f"{spec_required_score:.1f}% ({spec_required_pass}/{spec_required_total})</span>"
        )
        self.spec_total_label.setText(
            f"통과 선택 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 19px; font-weight: 500; color: #000000;'>"
            f"{spec_opt_score:.1f}% ({self.total_opt_pass_cnt}/{spec_opt_total})</span>"
        )
        self.spec_score_label.setText(
            f"종합 평가 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 19px; font-weight: 500; color: #000000;'>"
            f"{spec_score:.1f}% ({self.total_pass_cnt}/{spec_total_fields})</span>"
        )

        # ✅ 2️⃣ 전체 점수 (모든 spec 합산)
        if True:
            global_total_fields = self.global_pass_cnt + self.global_error_cnt
            if global_total_fields > 0:
                global_score = (self.global_pass_cnt / global_total_fields) * 100
            else:
                global_score = 0

            # 전체 필수 필드 통과 수 = 전체 통과 - 전체 선택 통과
            global_required_pass = self.global_pass_cnt - self.global_opt_pass_cnt
            # 전체 선택 필드 수 = 전체 선택 통과 + 전체 선택 에러
            global_opt_total = self.global_opt_pass_cnt + self.global_opt_error_cnt
            # 전체 필수 필드 수 = 전체 필드 - 전체 선택 필드
            global_required_total = global_total_fields - global_opt_total

            # 필수 통과율 계산
            if global_required_total > 0:
                global_required_score = (global_required_pass / global_required_total) * 100
            else:
                global_required_score = 0

            # 선택 통과율 계산
            if global_opt_total > 0:
                global_opt_score = (self.global_opt_pass_cnt / global_opt_total) * 100
            else:
                global_opt_score = 0

            # 필수/선택/종합 점수 표시 (% (통과/전체) 형식)
            self.total_pass_label.setText(
                f"통과 필수 필드 점수&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 19px; font-weight: 500; color: #000000;'>"
                f"{global_required_score:.1f}% ({global_required_pass}/{global_required_total})</span>"
            )
            self.total_total_label.setText(
                f"통과 선택 필드 점수&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 19px; font-weight: 500; color: #000000;'>"
                f"{global_opt_score:.1f}% ({self.global_opt_pass_cnt}/{global_opt_total})</span>"
            )
            self.total_score_label.setText(
                f"종합 평가 점수&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 19px; font-weight: 500; color: #000000;'>"
                f"{global_score:.1f}% ({self.global_pass_cnt}/{global_total_fields})</span>"
            )

    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭"""
        if col == 2:  # 아이콘 컬럼
            msg = getattr(self, f"step{row + 1}_msg", "")
            if msg:
                CustomDialog(msg, self.tableWidget.item(row, 1).text())  # API 명은 컬럼 1

    def update_table_row_with_retries(self, row, result, pass_count, error_count, data, error_text, retries):
        if row >= self.tableWidget.rowCount():
            return

        # 아이콘 업데이트 - 컬럼 2
        msg, img = self.icon_update_step(data, result, error_text)

        icon_widget = QWidget()
        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(img).pixmap(84, 20))
        icon_label.setToolTip(msg)
        icon_label.setAlignment(Qt.AlignCenter)

        icon_layout.addWidget(icon_label)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_widget.setLayout(icon_layout)

        self.tableWidget.setCellWidget(row, 2, icon_widget)

        # 실제 검증 횟수 업데이트 - 컬럼 3
        self.tableWidget.setItem(row, 3, QTableWidgetItem(str(retries)))
        self.tableWidget.item(row, 3).setTextAlignment(Qt.AlignCenter)

        # 통과 필드 수 업데이트 - 컬럼 4
        self.tableWidget.setItem(row, 4, QTableWidgetItem(str(pass_count)))
        self.tableWidget.item(row, 4).setTextAlignment(Qt.AlignCenter)

        # 전체 필드 수 업데이트 - 컬럼 5
        total_fields = pass_count + error_count
        self.tableWidget.setItem(row, 5, QTableWidgetItem(str(total_fields)))
        self.tableWidget.item(row, 5).setTextAlignment(Qt.AlignCenter)

        # 실패 필드 수 업데이트 - 컬럼 6
        self.tableWidget.setItem(row, 6, QTableWidgetItem(str(error_count)))
        self.tableWidget.item(row, 6).setTextAlignment(Qt.AlignCenter)

        # 평가 점수 업데이트 - 컬럼 7
        if total_fields > 0:
            score = (pass_count / total_fields) * 100
            self.tableWidget.setItem(row, 7, QTableWidgetItem(f"{score:.1f}%"))
        else:
            self.tableWidget.setItem(row, 7, QTableWidgetItem("0%"))
        self.tableWidget.item(row, 7).setTextAlignment(Qt.AlignCenter)

        # 메시지 저장
        setattr(self, f"step{row + 1}_msg", msg)

    def icon_update_step(self, auth_, result_, text_):
        if result_ == "PASS":
            msg = auth_ + "\n\n" + "Result: PASS" + "\n" + text_ + "\n" 
            img = self.img_pass
        elif result_ == "진행중":
            msg = auth_ + "\n\n" + "Status: " + text_ + "\n" 
            img = self.img_none
        else:
            msg = auth_ + "\n\n" + "Result: FAIL" + "\nResult details:\n" + text_ + "\n" 
            img = self.img_fail
        return msg, img

    def icon_update(self, tmp_res_auth, val_result, val_text):
        msg, img = self.icon_update_step(tmp_res_auth, val_result, val_text)

        if self.cnt < self.tableWidget.rowCount():
            # 아이콘 위젯 생성
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)

            icon_label = QLabel()
            icon_label.setPixmap(QIcon(img).pixmap(84, 20))
            icon_label.setAlignment(Qt.AlignCenter)

            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)

            self.tableWidget.setCellWidget(self.cnt, 1, icon_widget)
            setattr(self, f"step{self.cnt + 1}_msg", msg)
