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

    def _update_button_positions(self, group_width=None, group_height=None):
        """버튼 위치 직접 설정 (간격 16px 고정)"""
        if not hasattr(self, 'buttonGroup'):
            return

        # 크기가 전달되지 않으면 현재 크기 사용
        if group_width is None:
            group_width = self.buttonGroup.width()
        if group_height is None:
            group_height = self.buttonGroup.height()

        spacing = self.button_spacing  # 16px

        # 버튼 너비 = (전체 너비 - 간격 3개) / 4
        btn_width = (group_width - spacing * 3) // 4
        btn_height = group_height

        # 각 버튼 크기 및 위치 설정
        x = 0
        self.sbtn.setFixedSize(btn_width, btn_height)
        self.sbtn.move(x, 0)
        x += btn_width + spacing
        self.stop_btn.setFixedSize(btn_width, btn_height)
        self.stop_btn.move(x, 0)
        x += btn_width + spacing
        self.result_btn.setFixedSize(btn_width, btn_height)
        self.result_btn.move(x, 0)
        x += btn_width + spacing
        self.rbtn.setFixedSize(btn_width, btn_height)
        self.rbtn.move(x, 0)

    def resizeEvent(self, event):
        """창 크기 변경 시 배경 이미지 및 왼쪽 패널 크기 재조정"""
        super().resizeEvent(event)

        # content_widget의 배경 이미지 크기 조정
        if hasattr(self, 'content_widget') and self.content_widget:
            if hasattr(self, 'content_bg_label'):
                content_width = self.content_widget.width()
                content_height = self.content_widget.height()
                self.content_bg_label.setGeometry(0, 0, content_width, content_height)

        # ✅ 반응형: 왼쪽 패널 크기 조정
        if hasattr(self, 'original_window_size') and hasattr(self, 'left_col'):
            current_width = self.width()
            current_height = self.height()

            # 비율 계산 (최소 1.0 - 원본 크기 이하로 줄어들지 않음)
            width_ratio = max(1.0, current_width / self.original_window_size[0])
            height_ratio = max(1.0, current_height / self.original_window_size[1])

            # ✅ 왼쪽/오른쪽 패널 정렬을 위한 확장량 계산
            # 컬럼의 추가 높이를 계산하고, 그 추가분만 확장 요소들에 분배
            original_column_height = 898  # 원본 컬럼 높이
            extra_column_height = original_column_height * (height_ratio - 1)

            # 왼쪽 패널 확장 요소: group_table(204) + field_group(526) = 730px
            left_expandable_total = 204 + 526  # 730

            # 오른쪽 패널 확장 요소: api_section(251) + monitor_section(157) = 408px
            right_expandable_total = 251 + 157  # 408

            # bg_root 크기 조정
            if hasattr(self, 'bg_root') and hasattr(self, 'original_bg_root_size'):
                new_bg_width = int(self.original_bg_root_size[0] * width_ratio)
                new_bg_height = int(self.original_bg_root_size[1] * height_ratio)
                self.bg_root.setFixedSize(new_bg_width, new_bg_height)

            # 왼쪽 컬럼 크기 조정
            if hasattr(self, 'original_left_col_size'):
                new_left_width = int(self.original_left_col_size[0] * width_ratio)
                new_left_height = int(self.original_left_col_size[1] * height_ratio)
                self.left_col.setFixedSize(new_left_width, new_left_height)

            # 시험 선택 타이틀 크기 조정
            if hasattr(self, 'spec_panel_title') and hasattr(self, 'original_spec_panel_title_size'):
                new_title_width = int(self.original_spec_panel_title_size[0] * width_ratio)
                self.spec_panel_title.setFixedSize(new_title_width, self.original_spec_panel_title_size[1])
                
                # TestSelectionPanel 자체 너비도 업데이트
                if hasattr(self, 'test_selection_panel'):
                     self.test_selection_panel.setFixedWidth(new_title_width)

            # 그룹 테이블 위젯 크기 조정 (extra_column_height 비례 분배)
            if hasattr(self, 'group_table_widget') and hasattr(self, 'original_group_table_widget_size'):
                new_group_width = int(self.original_group_table_widget_size[0] * width_ratio)
                group_extra = extra_column_height * (204 / left_expandable_total)
                new_group_height = int(204 + group_extra)
                self.group_table_widget.setFixedSize(new_group_width, new_group_height)
                # 내부 테이블 크기도 조정
                if hasattr(self, 'group_table'):
                    self.group_table.setFixedHeight(new_group_height)

            # 시험 시나리오 테이블 크기 조정 (extra_column_height 비례 분배)
            if hasattr(self, 'field_group') and hasattr(self, 'original_field_group_size'):
                new_field_width = int(self.original_field_group_size[0] * width_ratio)
                field_extra = extra_column_height * (526 / left_expandable_total)
                new_field_height = int(526 + field_extra)
                self.field_group.setFixedSize(new_field_width, new_field_height)
                # 내부 테이블 크기도 조정
                if hasattr(self, 'test_field_table'):
                    self.test_field_table.setFixedHeight(new_field_height)

            # ✅ 오른쪽 컬럼 크기 조정
            if hasattr(self, 'right_col') and hasattr(self, 'original_right_col_size'):
                new_right_width = int(self.original_right_col_size[0] * width_ratio)
                new_right_height = int(self.original_right_col_size[1] * height_ratio)
                self.right_col.setFixedSize(new_right_width, new_right_height)

            # URL 행 크기 조정
            if hasattr(self, 'url_row') and hasattr(self, 'original_url_row_size'):
                new_url_width = int(self.original_url_row_size[0] * width_ratio)
                self.url_row.setFixedSize(new_url_width, self.original_url_row_size[1])

            # API 섹션 크기 조정 (extra_column_height 비례 분배)
            if hasattr(self, 'api_section') and hasattr(self, 'original_api_section_size'):
                new_api_width = int(self.original_api_section_size[0] * width_ratio)
                api_extra = extra_column_height * (251 / right_expandable_total)
                new_api_height = int(251 + api_extra)
                self.api_section.setFixedSize(new_api_width, new_api_height)

            # 모니터링 섹션 크기 조정 (extra_column_height 비례 분배)
            if hasattr(self, 'monitor_section') and hasattr(self, 'original_monitor_section_size'):
                new_monitor_width = int(self.original_monitor_section_size[0] * width_ratio)
                monitor_extra = extra_column_height * (157 / right_expandable_total)
                new_monitor_height = int(157 + monitor_extra)
                self.monitor_section.setFixedSize(new_monitor_width, new_monitor_height)

            # ✅ 버튼 그룹 및 버튼 크기 조정 (간격 16px 고정, 세로 크기 고정)
            if hasattr(self, 'original_buttonGroup_size'):
                new_group_width = int(self.original_buttonGroup_size[0] * width_ratio)
                btn_height = self.original_buttonGroup_size[1]  # 세로 크기 고정
                self.buttonGroup.setFixedSize(new_group_width, btn_height)
                self._update_button_positions(new_group_width, btn_height)

            # ✅ 내부 위젯 크기 조정
            # URL 텍스트 박스
            if hasattr(self, 'url_text_box') and hasattr(self, 'original_url_text_box_size'):
                new_url_tb_width = int(self.original_url_text_box_size[0] * width_ratio)
                self.url_text_box.setFixedSize(new_url_tb_width, self.original_url_text_box_size[1])

            # API 라벨
            if hasattr(self, 'api_label') and hasattr(self, 'original_api_label_size'):
                new_api_label_width = int(self.original_api_label_size[0] * width_ratio)
                self.api_label.setFixedSize(new_api_label_width, self.original_api_label_size[1])

            # API 콘텐츠 위젯 (api_section 내부 - 라벨 24px 제외)
            if hasattr(self, 'api_content_widget') and hasattr(self, 'original_api_content_widget_size'):
                new_api_cw_width = int(self.original_api_content_widget_size[0] * width_ratio)
                new_api_cw_height = int(219 + api_extra)  # api_section에서 라벨 제외한 부분
                self.api_content_widget.setFixedSize(new_api_cw_width, new_api_cw_height)

            # 모니터링 라벨
            if hasattr(self, 'monitor_label') and hasattr(self, 'original_monitor_label_size'):
                new_mon_label_width = int(self.original_monitor_label_size[0] * width_ratio)
                self.monitor_label.setFixedSize(new_mon_label_width, self.original_monitor_label_size[1])

            # 텍스트 브라우저 컨테이너 (monitor_section 내부 - 라벨 24px 제외)
            if hasattr(self, 'text_browser_container') and hasattr(self, 'original_text_browser_container_size'):
                new_tbc_width = int(self.original_text_browser_container_size[0] * width_ratio)
                new_tbc_height = int(125 + monitor_extra)  # monitor_section에서 라벨 제외한 부분
                self.text_browser_container.setFixedSize(new_tbc_width, new_tbc_height)

            # valResult (QTextBrowser) (monitor_section 내부)
            if hasattr(self, 'valResult') and hasattr(self, 'original_valResult_size'):
                new_vr_width = int(self.original_valResult_size[0] * width_ratio)
                new_vr_height = int(125 + monitor_extra)
                self.valResult.setFixedSize(new_vr_width, new_vr_height)

            # ✅ 시험 점수 요약 섹션
            # 시험 점수 요약 라벨
            if hasattr(self, 'valmsg') and hasattr(self, 'original_valmsg_size'):
                new_valmsg_width = int(self.original_valmsg_size[0] * width_ratio)
                self.valmsg.setFixedSize(new_valmsg_width, self.original_valmsg_size[1])

            # 분야별 점수 그룹
            if hasattr(self, 'spec_score_group') and hasattr(self, 'original_spec_group_size'):
                new_spec_width = int(self.original_spec_group_size[0] * width_ratio)
                self.spec_score_group.setFixedSize(new_spec_width, self.original_spec_group_size[1])

            # 전체 점수 그룹
            if hasattr(self, 'total_score_group') and hasattr(self, 'original_total_group_size'):
                new_total_width = int(self.original_total_group_size[0] * width_ratio)
                self.total_score_group.setFixedSize(new_total_width, self.original_total_group_size[1])

            # ✅ 시험 점수 요약 내부 데이터 영역 비례 조정
            if hasattr(self, 'spec_data_widget') and hasattr(self, 'original_spec_data_widget_size'):
                new_spec_data_width = int(self.original_spec_data_widget_size[0] * width_ratio)
                self.spec_data_widget.setFixedSize(new_spec_data_width, self.original_spec_data_widget_size[1])

            if hasattr(self, 'total_data_widget') and hasattr(self, 'original_total_data_widget_size'):
                new_total_data_width = int(self.original_total_data_widget_size[0] * width_ratio)
                self.total_data_widget.setFixedSize(new_total_data_width, self.original_total_data_widget_size[1])

            # ✅ 시험 점수 요약 내부 라벨 너비 비례 조정
            if hasattr(self, 'original_pass_label_width'):
                new_pass_width = int(self.original_pass_label_width * width_ratio)
                new_opt_width = int(self.original_opt_label_width * width_ratio)
                new_score_width = int(self.original_score_label_width * width_ratio)
                # 분야별 점수 라벨
                if hasattr(self, 'spec_pass_label'):
                    self.spec_pass_label.setFixedSize(new_pass_width, 60)
                if hasattr(self, 'spec_total_label'):
                    self.spec_total_label.setFixedSize(new_opt_width, 60)
                if hasattr(self, 'spec_score_label'):
                    self.spec_score_label.setFixedSize(new_score_width, 60)
                # 전체 점수 라벨
                if hasattr(self, 'total_pass_label'):
                    self.total_pass_label.setFixedSize(new_pass_width, 60)
                if hasattr(self, 'total_total_label'):
                    self.total_total_label.setFixedSize(new_opt_width, 60)
                if hasattr(self, 'total_score_label'):
                    self.total_score_label.setFixedSize(new_score_width, 60)

            # ✅ 시험 API 테이블 헤더
            if hasattr(self, 'api_header_widget') and hasattr(self, 'original_api_header_widget_size'):
                new_header_width = int(self.original_api_header_widget_size[0] * width_ratio)
                self.api_header_widget.setFixedSize(new_header_width, self.original_api_header_widget_size[1])

            # ✅ 시험 API 테이블 본문 (scroll_area) - 세로도 확장 (api_extra 사용)
            if hasattr(self, 'api_scroll_area') and hasattr(self, 'original_api_scroll_area_size'):
                new_scroll_width = int(self.original_api_scroll_area_size[0] * width_ratio)
                new_scroll_height = int(189 + api_extra)  # api_content_widget 내부 (헤더 30px 제외)
                self.api_scroll_area.setFixedSize(new_scroll_width, new_scroll_height)

            # ✅ 시험 API 테이블 컬럼 너비 비례 조정 (마지막 컬럼이 남은 공간 채움)
            if hasattr(self, 'tableWidget') and hasattr(self, 'original_column_widths'):
                # 스크롤바 표시 여부 확인 (테이블 전체 높이 > 스크롤 영역 높이)
                row_count = self.tableWidget.rowCount()
                total_row_height = row_count * 40  # 각 행 40px
                scrollbar_visible = total_row_height > new_scroll_height
                scrollbar_width = 16 if scrollbar_visible else 2  # 여유분 2px

                available_width = new_scroll_width - scrollbar_width

                # 마지막 컬럼을 제외한 나머지 컬럼 너비 설정
                used_width = 0
                for i, orig_width in enumerate(self.original_column_widths[:-1]):
                    new_col_width = int(orig_width * width_ratio)
                    self.tableWidget.setColumnWidth(i, new_col_width)
                    used_width += new_col_width

                # 마지막 컬럼은 남은 공간을 채움
                last_col_width = available_width - used_width
                self.tableWidget.setColumnWidth(len(self.original_column_widths) - 1, last_col_width)

            # ✅ 시험 API 테이블 헤더 라벨 너비 비례 조정
            if hasattr(self, 'header_labels') and hasattr(self, 'original_header_widths'):
                for i, label in enumerate(self.header_labels):
                    new_label_width = int(self.original_header_widths[i] * width_ratio)
                    label.setFixedSize(new_label_width, 30)

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

    def append_monitor_log(self, step_name, request_json="", result_status="진행중", score=None, details=""):
        """
        Qt 호환성이 보장된 HTML 테이블 구조 로그 출력 함수
        """
        from datetime import datetime
        import html

        # 타임스탬프
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 점수에 따른 색상 결정
        if score is not None:
            if score >= 100:
                node_color = "#10b981"  # 녹색
                text_color = "#10b981"  # 녹색 텍스트
            else:
                node_color = "#ef4444"  # 빨강
                text_color = "#ef4444"  # 빨강 텍스트
        else:
            node_color = "#6b7280"  # 회색
            text_color = "#333"  # 기본 검정

        # 1. 헤더 (Step 이름 + 시간) - Table로 블록 분리
        html_content = f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 15px;">
            <tr>
                <td valign="middle">
                    <span style="font-size: 20px; font-weight: bold; color: {text_color}; font-family: 'Noto Sans KR';">{step_name}</span>
                    <span style="font-size: 16px; color: #9ca3af; font-family: 'Consolas', monospace; margin-left: 8px;">{timestamp}</span>
                </td>
            </tr>
        </table>
        """

        # 2. 내용 영역
        html_content += f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td>
        """

        # 2-1. 상세 내용 (Details)
        if details:
            html_content += f"""
                <div style="margin-bottom: 8px; font-size: 18px; color: #6b7280; font-family: 'Noto Sans KR';">
                    {details}
                </div>
            """

        # 2-2. JSON 데이터 (회색 박스)
        if request_json and request_json.strip():
            escaped_json = html.escape(request_json)
            is_json_structure = request_json.strip().startswith('{') or request_json.strip().startswith('[')

            if is_json_structure:
                html_content += f"""
                <div style="margin-top: 5px; margin-bottom: 10px;">
                    <div style="font-size: 15px; color: #9ca3af; font-weight: bold; margin-bottom: 4px;">📦 데이터</div>
                    <div style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; padding: 10px;">
                        <pre style="margin: 0; font-family: 'Consolas', monospace; font-size: 18px; color: #1f2937;">{escaped_json}</pre>
                    </div>
                </div>
                """
            else:
                # JSON이 아닌 일반 텍스트일 경우
                html_content += f"""
                <div style="margin-top: 5px; margin-bottom: 10px;">
                    <pre style="font-size: 18px; color: #6b7280; font-family: 'Consolas', monospace;">{escaped_json}</pre>
                </div>
                """

        # 2-3. 점수 (Score)
        if score is not None:
            html_content += f"""
                <div style="margin-top: 5px; font-size: 18px; color: #6b7280; font-weight: bold; font-family: 'Consolas', monospace;">
                    점수: {score:.1f}%
                </div>
            """

        # Table 닫기
        html_content += """
                </td>
            </tr>
        </table>
        <div style="margin-bottom: 10px;"></div>
        """

        self.valResult.append(html_content)

        # 자동 스크롤
        self.valResult.verticalScrollBar().setValue(
            self.valResult.verticalScrollBar().maximum()
        )
