import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5 import QtCore

from core.functions import resource_path
from core.utils import remove_api_number_suffix, load_external_constants, calculate_percentage
from ui.gui_utils import CustomDialog
from ui.ui_components import TestSelectionPanel

class ResultPageWidget(QWidget):
    backRequested = pyqtSignal()

    def __init__(self, parent, embedded=False):
        super().__init__()
        self.parent = parent
        self.embedded = embedded
        self.setWindowTitle('통합플랫폼 연동 시험 결과')
        self.resize(1680, 1080)

        # CONSTANTS 초기화
        self.CONSTANTS = parent.CONSTANTS

        # 현재 선택된 spec_id 저장
        self.current_spec_id = parent.current_spec_id

        # ✅ 시험 결과 페이지 전용 아이콘 설정
        self.img_pass = resource_path("assets/image/test_runner/tag_성공.png")
        self.img_fail = resource_path("assets/image/test_runner/tag_실패.png")
        self.img_none = resource_path("assets/image/icon/icn_basic.png")

        self.initUI()

    def initUI(self):
        # ✅ 반응형: 최소 크기 설정
        self.setMinimumSize(1680, 1006)

        # ✅ 메인 레이아웃
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ✅ 상단 헤더 영역 (반응형 - 배경 늘어남)
        header_widget = QWidget()
        header_widget.setFixedHeight(64)
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 배경 이미지 설정 (늘어남 - border-image 사용)
        header_bg_path = resource_path("assets/image/common/header.png").replace("\\", "/")
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

        # 타이틀 이미지 (408x36) - result_title.png 사용
        header_title_label = QLabel()
        header_title_pixmap = QPixmap(resource_path("assets/image/test_runner/result_title.png"))
        header_title_label.setPixmap(header_title_pixmap.scaled(407, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_title_label.setFixedSize(407, 36)
        header_layout.addWidget(header_title_label)

        # 오른쪽 stretch (나머지 공간 채우기)
        header_layout.addStretch()

        mainLayout.addWidget(header_widget)

        # ✅ 본문 영역 컨테이너 (반응형 - main.png 배경)
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 배경 이미지를 QLabel로 설정 (절대 위치)
        main_bg_path = resource_path("assets/image/common/main.png").replace("\\", "/")
        self.content_bg_label = QLabel(self.content_widget)
        self.content_bg_label.setPixmap(QPixmap(main_bg_path))
        self.content_bg_label.setScaledContents(True)
        self.content_bg_label.lower()  # 맨 뒤로 보내기

        # ✅ 반응형: 원본 크기 저장
        self.original_window_size = (1680, 1006)
        self.original_bg_root_size = (1584, 898)
        self.original_left_col_size = (472, 898)
        self.original_right_col_size = (1112, 898)
        self.original_spec_panel_title_size = (424, 24)
        self.original_group_table_widget_size = (424, 204)
        self.original_field_group_size = (424, 526)
        self.original_info_title_size = (1064, 24)
        self.original_info_widget_size = (1064, 134)
        self.original_result_label_size = (1064, 24)
        self.original_result_header_widget_size = (1064, 30)
        self.original_score_title_size = (1064, 24)
        self.original_score_table_size = (1064, 256)
        self.original_spec_group_size = (1064, 128)
        self.original_total_group_size = (1064, 128)
        self.original_buttonGroup_size = (1064, 48)
        # ✅ 점수 테이블 내부 위젯 원본 크기
        self.original_score_header_size = (1064, 52)
        self.original_score_data_area_size = (1064, 76)
        self.original_score_label_size = (325, 60)
        self.original_column_widths = [40, 261, 100, 94, 116, 116, 94, 94, 133]

        # ✅ 2컬럼 레이아웃
        self.bg_root = QWidget(self.content_widget)
        self.bg_root.setObjectName("bg_root")
        self.bg_root.setAttribute(Qt.WA_StyledBackground, True)
        self.bg_root.setStyleSheet("QWidget#bg_root { background: transparent; }")
        bg_root_layout = QVBoxLayout()
        bg_root_layout.setContentsMargins(0, 0, 0, 0)
        bg_root_layout.setSpacing(0)

        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(0)

        # ✅ 왼쪽 컬럼 (시험 분야 + 시나리오 )
        self.left_col = QWidget()
        self.left_col.setFixedSize(472, 898)
        self.left_col.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(24, 36, 24, 80)
        left_layout.setSpacing(0)

        # 시험 선택 패널 - TestSelectionPanel 사용
        self.test_selection_panel = TestSelectionPanel(self.CONSTANTS)
        self.test_selection_panel.groupSelected.connect(self.on_group_selected)
        self.test_selection_panel.scenarioSelected.connect(self.on_test_field_selected)

        # 멤버 변수 매핑 (기존 코드와의 호환성 유지)
        self.spec_panel_title = self.test_selection_panel.spec_panel_title
        self.group_table_widget = self.test_selection_panel.group_table_widget
        self.field_group = self.test_selection_panel.field_group
        self.group_table = self.test_selection_panel.group_table
        self.test_field_table = self.test_selection_panel.test_field_table

        # 원본 사이즈 변수 매핑 (반응형 동작을 위해 필요)
        self.original_spec_panel_title_size = self.test_selection_panel.original_spec_panel_title_size
        self.original_group_table_widget_size = self.test_selection_panel.original_group_table_widget_size
        self.original_field_group_size = self.test_selection_panel.original_field_group_size
        
        # 인덱스 매핑 정보도 연결 (필요 시)
        # self.group_name_to_index = self.test_selection_panel.group_name_to_index 
        # (이건 패널 내부에서 관리되지만, 필요하면 여기서 참조)

        left_layout.addWidget(self.test_selection_panel)

        left_layout.addStretch()
        self.left_col.setLayout(left_layout)

        # ✅ 오른쪽 컬럼 (결과 테이블 및 점수)
        self.right_col = QWidget()
        self.right_col.setFixedSize(1112, 898)
        self.right_col.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(24, 36, 24, 0)
        right_layout.setSpacing(0)

        # 시험 정보 (크기 키움: 360px)
        self.info_title = QLabel("시험 정보")
        self.info_title.setStyleSheet("""
            font-size: 20px;
            font-style: normal;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
            margin-bottom: 8px;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(self.info_title)

        self.info_widget = self._create_simple_info_display()
        right_layout.addWidget(self.info_widget)

        # 시험 결과 라벨
        self.result_label = QLabel('시험 결과')
        self.result_label.setStyleSheet("""
            font-size: 20px;
            font-style: normal;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #222;
            margin-top: 20px;
            margin-bottom: 8px;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(self.result_label)

        # 결과 테이블 (크기 키움: 350px)
        self.create_result_table(right_layout)
        right_layout.addSpacing(20)

        # 시험 점수 요약 타이틀 (1064 × 24)
        self.score_title = QLabel('시험 점수 요약')
        self.score_title.setFixedSize(1064, 24)
        self.score_title.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(self.score_title)
        right_layout.addSpacing(6)

        # 시험 점수 테이블 (1064 × 256) - 분야별 점수 + 전체 점수
        self.score_table = QWidget()
        self.score_table.setFixedSize(1064, 256)
        self.score_table.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
            }
        """)
        score_table_layout = QVBoxLayout()
        score_table_layout.setContentsMargins(0, 0, 0, 0)
        score_table_layout.setSpacing(0)

        # 분야별 점수 표시 (1064 × 128)
        self.spec_score_group = self._create_spec_score_display()
        score_table_layout.addWidget(self.spec_score_group)

        # 전체 점수 표시 (1064 × 128)
        self.total_score_group = self._create_total_score_display()
        score_table_layout.addWidget(self.total_score_group)

        self.score_table.setLayout(score_table_layout)
        right_layout.addWidget(self.score_table)

        right_layout.addSpacing(32)

        # ✅ 버튼 그룹 (오른쪽 정렬)
        self.buttonGroup = QWidget()
        self.buttonGroup.setFixedSize(1064, 48)
        buttonLayout = QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignRight)  # 오른쪽 정렬
        buttonLayout.setContentsMargins(0, 0, 0, 0)

        if self.embedded:
            # Embedded 모드: 이전 화면으로 버튼
            # ✅ 반응형: 인스턴스 변수로 변경 및 원본 크기 저장
            self.back_btn = QPushButton("이전 화면으로", self)
            self.back_btn.setFixedSize(362, 48)
            self.original_back_btn_size = (362, 48)
            try:
                back_enabled = resource_path("assets/image/test_runner/btn_이전화면으로_enabled.png").replace("\\", "/")
                back_hover = resource_path("assets/image/test_runner/btn_이전화면으로_hover.png").replace("\\", "/")
                self.back_btn.setStyleSheet(f"""
                    QPushButton {{
                        border: none;
                        border-image: url('{back_enabled}') 0 0 0 0 stretch stretch;
                        padding-left: 20px;
                        padding-right: 20px;
                        font-family: 'Noto Sans KR';
                        font-size: 20px;
                        font-weight: 500;
                        color: #FFFFFF;
                    }}
                    QPushButton:hover {{
                        border-image: url('{back_hover}') 0 0 0 0 stretch stretch;
                    }}
                    QPushButton:pressed {{
                        border-image: url('{back_hover}') 0 0 0 0 stretch stretch;
                    }}
                """)
            except:
                self.back_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4A90E2;
                        border: none;
                        border-radius: 4px;
                        color: white;
                        font-family: "Noto Sans KR";
                        font-size: 15px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #357ABD;
                    }
                """)
            self.back_btn.clicked.connect(self._on_back_clicked)
            buttonLayout.addWidget(self.back_btn)
        else:
            # Standalone 모드: 닫기 버튼
            close_btn = QPushButton('닫기', self)
            close_btn.setFixedSize(362, 48)
            try:
                exit_enabled = resource_path("assets/image/test_runner/btn_종료_enabled.png").replace("\\", "/")
                exit_hover = resource_path("assets/image/test_runner/btn_종료_hover.png").replace("\\", "/")
                close_btn.setStyleSheet(f"""
                    QPushButton {{
                        border: none;
                        background-image: url('{exit_enabled}');
                        background-repeat: no-repeat;
                        background-position: center;
                        background-color: transparent;
                    }}
                    QPushButton:hover {{
                        background-image: url('{exit_hover}');
                    }}
                    QPushButton:pressed {{
                        background-image: url('{exit_hover}');
                        opacity: 0.8;
                    }}
                """)
            except:
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E74C3C;
                        border: none;
                        border-radius: 4px;
                        color: white;
                        font-family: "Noto Sans KR";
                        font-size: 15px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                """)
            close_btn.clicked.connect(self.close)
            buttonLayout.addWidget(close_btn)

        self.buttonGroup.setLayout(buttonLayout)
        right_layout.addWidget(self.buttonGroup)

        self.right_col.setLayout(right_layout)

        columns_layout.addWidget(self.left_col)
        columns_layout.addWidget(self.right_col)

        bg_root_layout.addLayout(columns_layout)
        self.bg_root.setLayout(bg_root_layout)

        # content_widget 레이아웃 설정 (좌우 48px, 하단 44px padding, 가운데 정렬)
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(48, 0, 48, 44)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.bg_root, 0, Qt.AlignHCenter | Qt.AlignVCenter)

        mainLayout.addWidget(self.content_widget, 1)  # 반응형: stretch=1로 남은 공간 채움

        self.setLayout(mainLayout)

        # 초기 시나리오 로드 (UI 요소 생성 후 호출)
        self.load_initial_scenarios()

    def resizeEvent(self, event):
        """창 크기 변경 시 배경 이미지 및 UI 반응형 조정"""
        super().resizeEvent(event)

        # content_widget의 배경 이미지 크기 조정
        if hasattr(self, 'content_widget') and self.content_widget:
            if hasattr(self, 'content_bg_label'):
                content_width = self.content_widget.width()
                content_height = self.content_widget.height()
                self.content_bg_label.setGeometry(0, 0, content_width, content_height)

        # ✅ 반응형: UI 요소 크기 조정
        if hasattr(self, 'original_window_size') and hasattr(self, 'left_col'):
            current_width = self.width()
            current_height = self.height()

            # 비율 계산 (최소 1.0 - 원본 크기 이하로 줄어들지 않음)
            width_ratio = max(1.0, current_width / self.original_window_size[0])
            height_ratio = max(1.0, current_height / self.original_window_size[1])

            # ✅ 좌우 패널 정렬을 위한 확장량 계산
            original_column_height = 898  # 원본 컬럼 높이
            extra_column_height = original_column_height * (height_ratio - 1)

            # 왼쪽 패널 확장 요소: group_table(204) + field_group(526) = 730px
            left_expandable_total = 204 + 526  # 730

            # bg_root 크기 조정
            if hasattr(self, 'bg_root') and hasattr(self, 'original_bg_root_size'):
                new_bg_width = int(self.original_bg_root_size[0] * width_ratio)
                new_bg_height = int(self.original_bg_root_size[1] * height_ratio)
                self.bg_root.setFixedSize(new_bg_width, new_bg_height)

            # ✅ 왼쪽 컬럼 크기 조정
            if hasattr(self, 'original_left_col_size'):
                new_left_width = int(self.original_left_col_size[0] * width_ratio)
                new_left_height = int(self.original_left_col_size[1] * height_ratio)
                self.left_col.setFixedSize(new_left_width, new_left_height)

            # 시험 선택 타이틀 크기 조정 (가로만 확장)
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

            # 시험 정보 위젯 크기 조정 (가로만 확장)
            if hasattr(self, 'info_widget') and hasattr(self, 'original_info_widget_size'):
                new_info_width = int(self.original_info_widget_size[0] * width_ratio)
                self.info_widget.setFixedSize(new_info_width, self.original_info_widget_size[1])

            # ✅ 결과 테이블 헤더 크기 조정 (가로만 확장)
            if hasattr(self, 'result_header_widget') and hasattr(self, 'original_result_header_widget_size'):
                new_header_width = int(self.original_result_header_widget_size[0] * width_ratio)
                self.result_header_widget.setFixedSize(new_header_width, self.original_result_header_widget_size[1])

                # ✅ 헤더 라벨들도 비례 조정
                if hasattr(self, 'result_header_labels') and hasattr(self, 'original_column_widths'):
                    for i, label in enumerate(self.result_header_labels[:-1]):  # 마지막 컬럼 제외
                        new_label_width = int(self.original_column_widths[i] * width_ratio)
                        label.setFixedSize(new_label_width, 30)
                    # 마지막 컬럼은 Expanding이므로 최소 너비만 조정
                    if len(self.result_header_labels) > 0:
                        last_label = self.result_header_labels[-1]
                        new_min_width = int(self.original_column_widths[-1] * width_ratio)
                        last_label.setMinimumWidth(new_min_width)

            # ✅ 결과 테이블 스크롤 영역 크기 조정 (가로만 확장, 세로 고정)
            if hasattr(self, 'result_scroll_area'):
                new_scroll_width = int(1064 * width_ratio)
                self.result_scroll_area.setFixedWidth(new_scroll_width)

            # 테이블 컨테이너 크기 조정
            if hasattr(self, 'table_container'):
                new_container_width = int(1064 * width_ratio)
                self.table_container.setFixedWidth(new_container_width)

            # 시험 점수 요약 타이틀 크기 조정 (가로만 확장)
            if hasattr(self, 'score_title') and hasattr(self, 'original_score_title_size'):
                new_score_title_width = int(self.original_score_title_size[0] * width_ratio)
                self.score_title.setFixedSize(new_score_title_width, self.original_score_title_size[1])

            # 점수 테이블 크기 조정 (가로만 확장)
            if hasattr(self, 'score_table') and hasattr(self, 'original_score_table_size'):
                new_score_width = int(self.original_score_table_size[0] * width_ratio)
                self.score_table.setFixedSize(new_score_width, self.original_score_table_size[1])

            # 분야별 점수 그룹 크기 조정 (가로만 확장)
            if hasattr(self, 'spec_score_group') and hasattr(self, 'original_spec_group_size'):
                new_spec_width = int(self.original_spec_group_size[0] * width_ratio)
                self.spec_score_group.setFixedSize(new_spec_width, self.original_spec_group_size[1])

            # 전체 점수 그룹 크기 조정 (가로만 확장)
            if hasattr(self, 'total_score_group') and hasattr(self, 'original_total_group_size'):
                new_total_width = int(self.original_total_group_size[0] * width_ratio)
                self.total_score_group.setFixedSize(new_total_width, self.original_total_group_size[1])

            # ✅ 점수 테이블 내부 위젯 크기 조정
            if hasattr(self, 'original_score_header_size'):
                new_header_width = int(self.original_score_header_size[0] * width_ratio)
                new_data_width = int(self.original_score_data_area_size[0] * width_ratio)
                new_label_width = int(self.original_score_label_size[0] * width_ratio)

                # 분야별 점수 내부 위젯
                if hasattr(self, 'spec_header'):
                    self.spec_header.setFixedSize(new_header_width, self.original_score_header_size[1])
                if hasattr(self, 'spec_data_area'):
                    self.spec_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
                # if hasattr(self, 'spec_pass_label'):
                #     self.spec_pass_label.setFixedSize(new_label_width, self.original_score_label_size[1])
                # if hasattr(self, 'spec_total_label'):
                #     self.spec_total_label.setFixedSize(new_label_width, self.original_score_label_size[1])
                # if hasattr(self, 'spec_score_label'):
                #     self.spec_score_label.setFixedSize(new_label_width, self.original_score_label_size[1])

                # 전체 점수 내부 위젯
                if hasattr(self, 'total_header'):
                    self.total_header.setFixedSize(new_header_width, self.original_score_header_size[1])
                if hasattr(self, 'total_data_area'):
                    self.total_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
                # if hasattr(self, 'total_pass_label'):
                #     self.total_pass_label.setFixedSize(new_label_width, self.original_score_label_size[1])
                # if hasattr(self, 'total_total_label'):
                #     self.total_total_label.setFixedSize(new_label_width, self.original_score_label_size[1])
                # if hasattr(self, 'total_score_label'):
                #     self.total_score_label.setFixedSize(new_label_width, self.original_score_label_size[1])

            # ✅ 버튼 그룹 크기 조정 (가로만 확장, 세로 고정)
            if hasattr(self, 'buttonGroup') and hasattr(self, 'original_buttonGroup_size'):
                new_btn_group_width = int(self.original_buttonGroup_size[0] * width_ratio)
                self.buttonGroup.setFixedSize(new_btn_group_width, self.original_buttonGroup_size[1])

            # ✅ 반응형: back_btn 크기 조정
            if hasattr(self, 'back_btn') and hasattr(self, 'original_back_btn_size'):
                new_back_btn_width = int(self.original_back_btn_size[0] * width_ratio)
                self.back_btn.setFixedSize(new_back_btn_width, self.original_back_btn_size[1])

            # ✅ 결과 테이블 컬럼 너비 비례 조정
            if hasattr(self, 'tableWidget') and hasattr(self, 'original_column_widths'):
                for i, orig_width in enumerate(self.original_column_widths):
                    new_col_width = int(orig_width * width_ratio)
                    self.tableWidget.setColumnWidth(i, new_col_width)

    def _apply_score_widget_resize(self):
        """점수 위젯 재생성 후 현재 창 크기에 맞게 반응형 적용"""
        if not hasattr(self, 'original_window_size'):
            return

        current_width = self.width()
        width_ratio = max(1.0, current_width / self.original_window_size[0])

        # 외부 컨테이너 크기 조정
        if hasattr(self, 'spec_score_group') and hasattr(self, 'original_spec_group_size'):
            new_spec_width = int(self.original_spec_group_size[0] * width_ratio)
            self.spec_score_group.setFixedSize(new_spec_width, self.original_spec_group_size[1])

        if hasattr(self, 'total_score_group') and hasattr(self, 'original_total_group_size'):
            new_total_width = int(self.original_total_group_size[0] * width_ratio)
            self.total_score_group.setFixedSize(new_total_width, self.original_total_group_size[1])

        # 내부 위젯 크기 조정
        if hasattr(self, 'original_score_header_size'):
            new_header_width = int(self.original_score_header_size[0] * width_ratio)
            new_data_width = int(self.original_score_data_area_size[0] * width_ratio)
            new_label_width = int(self.original_score_label_size[0] * width_ratio)

            # 분야별 점수 내부 위젯
            if hasattr(self, 'spec_header'):
                self.spec_header.setFixedSize(new_header_width, self.original_score_header_size[1])
            if hasattr(self, 'spec_data_area'):
                self.spec_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
            # if hasattr(self, 'spec_pass_label'):
            #     self.spec_pass_label.setFixedSize(new_label_width, self.original_score_label_size[1])
            # if hasattr(self, 'spec_total_label'):
            #     self.spec_total_label.setFixedSize(new_label_width, self.original_score_label_size[1])
            # if hasattr(self, 'spec_score_label'):
            #     self.spec_score_label.setFixedSize(new_label_width, self.original_score_label_size[1])

            # 전체 점수 내부 위젯
            if hasattr(self, 'total_header'):
                self.total_header.setFixedSize(new_header_width, self.original_score_header_size[1])
            if hasattr(self, 'total_data_area'):
                self.total_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
            # if hasattr(self, 'total_pass_label'):
            #     self.total_pass_label.setFixedSize(new_label_width, self.original_score_label_size[1])
            # if hasattr(self, 'total_total_label'):
            #     self.total_total_label.setFixedSize(new_label_width, self.original_score_label_size[1])
            # if hasattr(self, 'total_score_label'):
            #     self.total_score_label.setFixedSize(new_label_width, self.original_score_label_size[1])

    def load_initial_scenarios(self):
        """초기 로드: 현재 선택된 그룹과 시나리오를 반영하여 UI 갱신"""
        SPEC_CONFIG = load_external_constants(self.CONSTANTS)
        
        # 1. 현재 그룹 ID 확인 (parent에서 가져옴)
        current_group_id = getattr(self.parent, 'current_group_id', None)
        
        # 그룹 ID가 없으면 첫 번째 그룹을 기본으로 선택하거나 종료
        if not current_group_id and SPEC_CONFIG:
            current_group_id = SPEC_CONFIG[0].get('group_id')
            self.parent.current_group_id = current_group_id

        if not current_group_id:
            return

        # 2. 그룹 테이블에서 해당 그룹 선택 및 시나리오 목록 갱신
        selected_group = None
        for idx, group in enumerate(SPEC_CONFIG):
            if group.get('group_id') == current_group_id:
                selected_group = group
                
                # 그룹 테이블 UI 선택 처리
                self.group_table.selectRow(idx)
                # cellClicked 시그널이 프로그래밍 방식 선택으로는 발생하지 않으므로 직접 업데이트 호출
                self.test_selection_panel.update_test_field_table(selected_group)
                break
        
        if not selected_group:
            return

        # 3. 현재 시나리오 ID 확인 및 선택
        current_spec_id = getattr(self.parent, 'current_spec_id', None)
        if current_spec_id:
            # 시나리오 테이블에서 해당 spec_id 찾기
            if hasattr(self.test_selection_panel, 'spec_id_to_index') and current_spec_id in self.test_selection_panel.spec_id_to_index:
                row_idx = self.test_selection_panel.spec_id_to_index[current_spec_id]
                self.test_field_table.selectRow(row_idx)
                
                # 결과 테이블 표시 (on_test_field_selected 로직과 유사하지만, 중복 방지 체크 우회 필요할 수도 있음)
                # 여기서는 직접 호출하여 강제로 갱신
                self.on_test_field_selected(row_idx, 0)

    def on_group_selected(self, row, col):
        """시험 그룹 선택 시"""
        group_name = self.test_selection_panel.index_to_group_name.get(row)
        if not group_name:
            return

        # ===== 외부 로드된 SPEC_CONFIG 사용 (fallback: CONSTANTS 모듈) =====
        SPEC_CONFIG = getattr(self.parent, 'LOADED_SPEC_CONFIG', self.parent.CONSTANTS.SPEC_CONFIG)
        selected_group = next(
            (g for g in SPEC_CONFIG if g.get("group_name") == group_name), None
        )
        # ===== 수정 끝 =====

        if selected_group:
            new_group_id = selected_group.get('group_id')
            old_group_id = getattr(self.parent, 'current_group_id', None)

            print(f"[RESULT DEBUG] 🔄 그룹 선택: {old_group_id} → {new_group_id}")

            # ✅ 그룹이 변경되면 current_spec_id 초기화
            if old_group_id != new_group_id:
                self.current_spec_id = None
                print(f"[RESULT DEBUG] ✨ 그룹 변경으로 current_spec_id 초기화")

            # ✅ 그룹 ID 저장
            self.parent.current_group_id = new_group_id
            self.test_selection_panel.update_test_field_table(selected_group)

    def on_test_field_selected(self, row, col):
        """시나리오 선택 시 해당 결과 표시 (결과 없어도 API 정보 표시)"""

        if row not in self.test_selection_panel.index_to_spec_id:
            return

        selected_spec_id = self.test_selection_panel.index_to_spec_id[row]

        # 선택된 시나리오가 현재와 같으면 무시
        if selected_spec_id == self.current_spec_id:
            return

        print(f"[RESULT] 시나리오 전환: {self.current_spec_id} → {selected_spec_id}")
        print(f"[RESULT DEBUG] 현재 그룹: {self.parent.current_group_id}")

        # ✅ parent의 spec 전환 (API 목록 로드)
        old_spec_id = self.parent.current_spec_id
        old_step_buffers = self.parent.step_buffers.copy() if hasattr(self.parent, 'step_buffers') else []

        try:
            # ✅ 1. spec_id 업데이트
            self.parent.current_spec_id = selected_spec_id
            self.current_spec_id = selected_spec_id

            # ✅ 2. spec 데이터 다시 로드 (스키마, API 목록 등)
            self.parent.load_specs_from_constants()

            # ✅ 3. 설정 다시 로드 (웹훅 스키마 포함)
            self.parent.get_setting()

            print(f"[RESULT] API 개수: {len(self.parent.videoMessages)}")
            print(f"[RESULT] inSchema 개수: {len(self.parent.inSchema)}")
            print(f"[RESULT] webhookSchema 개수: {len(self.parent.webhookSchema)}")

            # ✅ 4. 저장된 결과 데이터가 있으면 로드 (복합키 사용)
            composite_key = f"{self.parent.current_group_id}_{selected_spec_id}"
            print(f"[RESULT DEBUG] 📂 데이터 복원 시도: {composite_key}")
            if composite_key in self.parent.spec_table_data:
                saved_data = self.parent.spec_table_data[composite_key]

                # step_buffers 복원
                saved_buffers = saved_data.get('step_buffers', [])
                if saved_buffers:
                    self.parent.step_buffers = [buf.copy() for buf in saved_buffers]
                    print(f"[RESULT] step_buffers 복원 완료: {len(self.parent.step_buffers)}개")
                else:
                    # 저장된 버퍼가 없으면 빈 버퍼 생성
                    api_count = len(self.parent.videoMessages)
                    self.parent.step_buffers = [
                        {"data": "저장된 데이터가 없습니다.", "error": "", "result": "PASS"}
                        for _ in range(api_count)
                    ]

                # 점수 정보 복원
                self.parent.total_pass_cnt = saved_data.get('total_pass_cnt', 0)
                self.parent.total_error_cnt = saved_data.get('total_error_cnt', 0)

                # ✅ step_pass_counts와 step_error_counts 배열 복원
                self.parent.step_pass_counts = saved_data.get('step_pass_counts', [0] * len(self.parent.videoMessages))[:]
                self.parent.step_error_counts = saved_data.get('step_error_counts', [0] * len(self.parent.videoMessages))[:]
                print(f"[RESULT] step_pass_counts 복원: {self.parent.step_pass_counts}")
                print(f"[RESULT] step_error_counts 복원: {self.parent.step_error_counts}")

                # 테이블 및 점수 표시 업데이트
                self.reload_result_table(saved_data)
                self.update_score_displays(saved_data)

                print(f"[RESULT] {selected_spec_id} 저장된 결과 로드 완료")
            else:
                # 결과가 없으면 빈 테이블 표시
                print(f"[RESULT] {selected_spec_id} 결과 없음 - 빈 테이블 표시")
                self.show_empty_result_table()

        except Exception as e:
            print(f"[ERROR] 시나리오 전환 실패: {e}")
            import traceback
            traceback.print_exc()

            # ✅ 복구 처리
            self.parent.current_spec_id = old_spec_id
            self.current_spec_id = old_spec_id
            if old_step_buffers:
                self.parent.step_buffers = old_step_buffers

            try:
                self.parent.load_specs_from_constants()
                self.parent.get_setting()
            except:
                pass

            QMessageBox.warning(self, "오류", f"시나리오 전환 중 오류가 발생했습니다.\n{str(e)}")

    def show_empty_result_table(self):
        """결과가 없을 때 빈 테이블 표시 (API 목록만)"""
        api_list = self.parent.videoMessagesDisplay  # 표시용 이름 사용
        api_count = len(api_list)

        print(f"[RESULT] 빈 테이블 생성: {api_count}개 API")

        # ✅ step_buffers 초기화 (상세 내용 확인을 위해 필수!)
        self.parent.step_buffers = []
        for i in range(api_count):
            api_name = api_list[i] if i < len(api_list) else f"API {i + 1}"
            self.parent.step_buffers.append({
                "data": f"아직 시험이 진행되지 않았습니다.\n\nAPI: {api_name}",
                "error": "시험 데이터가 없습니다.",
                "result": "PASS"
            })

        print(f"[RESULT] step_buffers 생성 완료: {len(self.parent.step_buffers)}개")

        # ✅ 점수 정보 초기화
        self.parent.total_pass_cnt = 0
        self.parent.total_error_cnt = 0

        # 테이블 행 수 재설정
        self.tableWidget.setRowCount(api_count)

        # ✅ 행 높이 설정 (누락 방지)
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 40)

        for row in range(api_count):
            # No. (숫자) - 컬럼 0
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # API 명 - 컬럼 1 (이미 숫자가 제거된 리스트 사용)
            api_item = QTableWidgetItem(api_list[row])
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            # ✅ 기본 아이콘 (결과 페이지 전용 아이콘 사용) - 컬럼 2
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))  # icn_basic.png는 16x16
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 2, icon_widget)

            # 모든 값 0으로 초기화 (9컬럼 구조) - 컬럼 3-7
            for col, value in [(3, "0"), (4, "0"), (5, "0"), (6, "0"), (7, "0%")]:
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # 상세 내용 버튼 - 컬럼 8
            detail_label = QLabel()
            try:
                img_path = resource_path("assets/image/test_runner/btn_상세내용확인.png").replace("\\", "/")
                pixmap = QPixmap(img_path)
                detail_label.setPixmap(pixmap)
                detail_label.setScaledContents(False)
                detail_label.setFixedSize(pixmap.size())
            except:
                detail_label.setText("확인")
                detail_label.setStyleSheet("color: #4A90E2; font-weight: bold;")

            detail_label.setCursor(Qt.PointingHandCursor)
            detail_label.setAlignment(Qt.AlignCenter)
            # detail_label.mousePressEvent = lambda event, r=row: self._show_detail(r)

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 8, container)

        # 점수 표시도 0으로 업데이트
        empty_data = {
            'total_pass_cnt': 0,
            'total_error_cnt': 0
        }
        self.update_score_displays(empty_data)

    def reload_result_table(self, saved_data):
        """저장된 데이터로 결과 테이블 재구성"""
        table_data = saved_data.get('table_data', [])

        # 테이블 행 수 재설정
        self.tableWidget.setRowCount(len(table_data))

        # ✅ 행 높이 설정 (누락 방지)
        for i in range(len(table_data)):
            self.tableWidget.setRowHeight(i, 40)

        for row, row_data in enumerate(table_data):
            # No. (숫자) - 컬럼 0
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # API 명 - 컬럼 1 (숫자 제거된 이름 표시)
            display_name = remove_api_number_suffix(row_data['api_name'])
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            # ✅ 아이콘 상태 복원 (결과 페이지 전용 아이콘 사용) - 컬럼 2
            icon_state = row_data['icon_state']
            if icon_state == "PASS":
                img = self.img_pass  # tag_성공.png
                icon_size = (84, 20)  # tag_성공.png
            elif icon_state == "FAIL":
                img = self.img_fail  # tag_실패.png
                icon_size = (84, 20)  # tag_실패.png
            else:
                img = self.img_none  # icn_basic.png
                icon_size = (16, 16)  # icn_basic.png

            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(img).pixmap(*icon_size))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setToolTip(f"Result: {icon_state}")
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 2, icon_widget)

            # 나머지 컬럼 복원 - 컬럼 3-7
            for col, key in [(3, 'retry_count'), (4, 'pass_count'),
                             (5, 'total_count'), (6, 'fail_count'), (7, 'score')]:
                item = QTableWidgetItem(row_data[key])
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # 상세 내용 버튼 - 컬럼 8
            detail_label = QLabel()
            try:
                img_path = resource_path("assets/image/test_runner/btn_상세내용확인.png").replace("\\", "/")
                pixmap = QPixmap(img_path)
                detail_label.setPixmap(pixmap)
                detail_label.setScaledContents(False)
                detail_label.setFixedSize(pixmap.size())
            except:
                detail_label.setText("확인")
                detail_label.setStyleSheet("color: #4A90E2; font-weight: bold;")

            detail_label.setCursor(Qt.PointingHandCursor)
            detail_label.setAlignment(Qt.AlignCenter)
            # detail_label.mousePressEvent = lambda event, r=row: self._show_detail(r)

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 8, container)

    def _show_detail(self, row):
        """상세 내용 확인 - parent의 show_combined_result 호출"""
        try:
            self.parent.show_combined_result(row)
        except Exception as e:
            print(f"[ERROR] 상세 내용 확인 오류: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "오류", f"상세 내용을 표시할 수 없습니다.\n{str(e)}")

    def update_score_displays(self, saved_data):
        """점수 표시 업데이트"""
        total_pass = saved_data.get('total_pass_cnt', 0)
        total_error = saved_data.get('total_error_cnt', 0)
        total_fields = total_pass + total_error
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0

        # spec_score_group 재생성
        if hasattr(self, 'spec_score_group'):
            # 기존 위젯의 위치 기억
            parent_widget = self.spec_score_group.parent()
            if parent_widget:
                layout = parent_widget.layout()
                if layout:
                    idx = layout.indexOf(self.spec_score_group)
                    if idx >= 0:
                        layout.removeWidget(self.spec_score_group)
                        self.spec_score_group.deleteLater()
                        
                        # 새로운 점수 위젯 생성
                        self.spec_score_group = self._create_spec_score_display_with_data(
                            total_pass, total_error, score
                        )
                        # 같은 위치에 다시 삽입
                        layout.insertWidget(idx, self.spec_score_group)

        # ✅ 전체 점수 표시도 업데이트
        if hasattr(self, 'total_score_group'):
            # 기존 위젯의 위치 기억
            parent_widget = self.total_score_group.parent()
            if parent_widget:
                layout = parent_widget.layout()
                if layout:
                    idx = layout.indexOf(self.total_score_group)
                    if idx >= 0:
                        layout.removeWidget(self.total_score_group)
                        self.total_score_group.deleteLater()
                        
                        # 새로운 전체 점수 위젯 생성
                        self.total_score_group = self._create_total_score_display()
                        # 같은 위치에 다시 삽입
                        layout.insertWidget(idx, self.total_score_group)

        # ✅ 위젯 재생성 후 현재 창 크기에 맞게 반응형 적용
        self._apply_score_widget_resize()

    def _create_simple_info_display(self):
        """심플한 시험 정보 표시 (단일 텍스트, 테두리 유지)"""
        info_widget = QWidget()
        info_widget.setFixedWidth(1050)
        info_widget.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: none;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 10, 10, 10)
        layout.setSpacing(5)

        # ✅ 시험 정보 불러오기
        test_info = self.parent.load_test_info_from_constants()

        # ✅ 시험 정보를 한 개의 문자열로 합치기
        info_text = "\n".join([f"{label}: {value}" for label, value in test_info])

        # ✅ 한 개의 라벨로 출력
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)  # 줄바꿈 자동 처리
        info_label.setStyleSheet("""
            font-family: "Noto Sans KR";
            font-size: 16px;
            font-weight: 400;
            color: #1B1B1C;
            line-height: 1.8;
            border: none;
        """)

        layout.addWidget(info_label)
        layout.addStretch()
        info_widget.setLayout(layout)

        # ✅ 스크롤 영역 추가
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedSize(1064, 134)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ✅ 스크롤바 스타일
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #CECECE;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QScrollBar:vertical {
                border: none;
                background: #DFDFDF;
                width: 14px;
                margin: 0px;
                border-radius: 4px;
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
            }
        """)
        return scroll_area

    def create_result_table(self, parent_layout):
        """결과 테이블 생성 - 헤더 분리 구조"""
        api_count = self.parent.tableWidget.rowCount()

        # 컨테이너 위젯 (헤더 + 본문)
        self.table_container = QWidget()
        self.table_container.setFixedWidth(1064)
        container_layout = QVBoxLayout(self.table_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 별도 헤더 위젯 (1064px 전체 너비)
        self.result_header_widget = QWidget()
        self.result_header_widget.setFixedSize(1064, 30)
        self.result_header_widget.setStyleSheet("""
            QWidget {
                background-color: #EDF0F3;
                border: 1px solid #CECECE;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        """)
        header_layout = QHBoxLayout(self.result_header_widget)
        header_layout.setContentsMargins(0, 0, 14, 0)
        header_layout.setSpacing(0)

        # 헤더 컬럼 정의 (너비, 텍스트) - 9컬럼 구조
        header_columns = [
            (40, ""),            # No.
            (261, "API 명"),
            (100, "결과"),
            (94, "검증 횟수"),
            (116, "통과 필드 수"),
            (116, "전체 필드 수"),
            (94, "실패 필드 수"),
            (94, "평가 점수"),
            (133, "상세 내용")
        ]

        # ✅ 헤더 라벨들을 저장하여 resizeEvent에서 사용
        self.result_header_labels = []
        for i, (width, text) in enumerate(header_columns):
            label = QLabel(text)
            label.setFixedSize(width, 30)  # 모든 컬럼 고정 너비
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                    color: #1B1B1C;
                    font-family: 'Noto Sans KR';
                    font-size: 18px;
                    font-weight: 600;
                    letter-spacing: -0.156px;
                }
            """)
            header_layout.addWidget(label)
            self.result_header_labels.append(label)

        container_layout.addWidget(self.result_header_widget)

        # 테이블 본문 (헤더 숨김)
        self.tableWidget = QTableWidget(api_count, 9)  # 9개 컬럼
        # self.tableWidget.setFixedWidth(1050)  # setWidgetResizable(True) 사용으로 주석 처리
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # 테이블 스타일
        self.tableWidget.setStyleSheet("""
            QTableWidget {
                background: #FFF;
                border: none;
                font-size: 19px;
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

        # 컬럼 너비 설정 (본문용) - 9컬럼 구조
        self.tableWidget.setColumnWidth(0, 40)    # No. (숫자)
        self.tableWidget.setColumnWidth(1, 261)   # API 명
        self.tableWidget.setColumnWidth(2, 100)   # 결과
        self.tableWidget.setColumnWidth(3, 94)    # 검증 횟수
        self.tableWidget.setColumnWidth(4, 116)   # 통과 필드 수
        self.tableWidget.setColumnWidth(5, 116)   # 전체 필드 수
        self.tableWidget.setColumnWidth(6, 94)    # 실패 횟수
        self.tableWidget.setColumnWidth(7, 94)    # 평가 점수
        self.tableWidget.setColumnWidth(8, 133)   # 상세 내용
        self.tableWidget.horizontalHeader().setStretchLastSection(False)  # ✅ 마지막 컬럼 자동 확장 끔

        # 행 높이 설정
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 40)

        # parent 테이블 데이터 복사
        self._copy_table_data()

        # 상세 내용 버튼 클릭 이벤트
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)

        # QScrollArea로 본문만 감싸기
        self.result_scroll_area = QScrollArea()
        self.result_scroll_area.setWidget(self.tableWidget)
        self.result_scroll_area.setWidgetResizable(True)
        self.result_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.result_scroll_area.setFixedWidth(1064)
        self.result_scroll_area.setStyleSheet("""
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
                border-radius: 4px;
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
            }
        """)

        container_layout.addWidget(self.result_scroll_area)
        parent_layout.addWidget(self.table_container)

    def _on_back_clicked(self):
        """뒤로가기 버튼 클릭 시 시그널 발생"""
        self.backRequested.emit()

    def _copy_table_data(self):
        """parent의 테이블 데이터를 복사 (결과 페이지 전용 아이콘 사용)"""
        api_count = self.parent.tableWidget.rowCount()
        for row in range(api_count):
            # No. (숫자) - 컬럼 0
            no_item = self.parent.tableWidget.item(row, 0)
            if no_item:
                new_no_item = QTableWidgetItem(no_item.text())
                new_no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(row, 0, new_no_item)

            # API 명 - 컬럼 1
            api_item = self.parent.tableWidget.item(row, 1)
            if api_item:
                new_item = QTableWidgetItem(api_item.text())
                new_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(row, 1, new_item)

            # ✅ 결과 아이콘 (결과 페이지 전용 아이콘으로 교체) - 컬럼 2
            icon_widget = self.parent.tableWidget.cellWidget(row, 2)
            if icon_widget:
                old_label = icon_widget.findChild(QLabel)
                if old_label:
                    # ✅ tooltip에서 결과 상태 추출
                    tooltip = old_label.toolTip()

                    # ✅ 결과에 따라 결과 페이지 전용 아이콘 선택
                    if "Result: PASS" in tooltip:
                        img = self.img_pass  # tag_성공.png
                        icon_size = (84, 20)
                    elif "Result: FAIL" in tooltip:
                        img = self.img_fail  # tag_실패.png
                        icon_size = (84, 20)
                    else:
                        img = self.img_none  # icn_basic.png
                        icon_size = (16, 16)

                    new_icon_widget = QWidget()
                    new_icon_layout = QHBoxLayout()
                    new_icon_layout.setContentsMargins(0, 0, 0, 0)

                    new_icon_label = QLabel()
                    new_icon_label.setPixmap(QIcon(img).pixmap(*icon_size))
                    new_icon_label.setToolTip(tooltip)
                    new_icon_label.setAlignment(Qt.AlignCenter)

                    new_icon_layout.addWidget(new_icon_label)
                    new_icon_layout.setAlignment(Qt.AlignCenter)
                    new_icon_widget.setLayout(new_icon_layout)

                    self.tableWidget.setCellWidget(row, 2, new_icon_widget)

            # 나머지 컬럼들 - 컬럼 3-7
            for col in range(3, 8):
                item = self.parent.tableWidget.item(row, col)
                if item:
                    new_item = QTableWidgetItem(item.text())
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(row, col, new_item)

            # 상세 내용 버튼 - 컬럼 8
            detail_label = QLabel()
            try:
                img_path = resource_path("assets/image/test_runner/btn_상세내용확인.png").replace("\\", "/")
                pixmap = QPixmap(img_path)
                detail_label.setPixmap(pixmap)
                detail_label.setScaledContents(False)
                detail_label.setFixedSize(pixmap.size())
            except:
                detail_label.setText("확인")
                detail_label.setStyleSheet("color: #4A90E2; font-weight: bold;")

            detail_label.setCursor(Qt.PointingHandCursor)
            detail_label.setAlignment(Qt.AlignCenter)
            # detail_label.mousePressEvent = lambda event, r=row: self._show_detail(r)

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_label)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 8, container)

    def _create_spec_score_display(self):
        """시험 분야별 점수 표시"""
        spec_description = self.parent.spec_description
        api_count = len(self.parent.videoMessages)
        total_pass = self.parent.total_pass_cnt
        total_error = self.parent.total_error_cnt
        opt_pass = getattr(self.parent, 'total_opt_pass_cnt', 0)  # 선택 필드 통과 수
        opt_error = getattr(self.parent, 'total_opt_error_cnt', 0)  # 선택 필드 에러 수
        total_fields = total_pass + total_error
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0

        return self._create_spec_score_display_with_data(total_pass, total_error, score, opt_pass, opt_error)

    def _create_spec_score_display_with_data(self, total_pass, total_error, score, opt_pass=0, opt_error=0):
        """데이터를 받아서 분야별 점수 표시 위젯 생성 (1064 × 128)"""
        spec_group = QWidget()
        spec_group.setFixedSize(1064, 128)
        spec_group.setStyleSheet("background: transparent; border: none;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 헤더 영역 (1064 × 52)
        self.spec_header = QWidget()
        self.spec_header.setFixedSize(1064, 52)
        self.spec_header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(self.spec_header)
        header_layout.setContentsMargins(0, 5, 0, 5)
        header_layout.setSpacing(12)

        # 분야별 점수 아이콘 (52 × 42)
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_분야별점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(52, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(52, 42)
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label, alignment=Qt.AlignVCenter)

        # 분야별 점수 레이블 (500 Medium 20px)
        score_type_label = QLabel("분야별 점수")
        score_type_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
        """)
        header_layout.addWidget(score_type_label, alignment=Qt.AlignVCenter)

        # 세로선 (27px)
        vline = QFrame()
        vline.setFrameShape(QFrame.VLine)
        vline.setFixedSize(1, 27)
        vline.setStyleSheet("background-color: #000000;")
        header_layout.addWidget(vline, alignment=Qt.AlignVCenter)

        # spec 정보 레이블 (500 Medium 20px)
        spec_description = self.parent.spec_description
        api_count = len(self.parent.videoMessages)
        spec_info_label = QLabel(f"{spec_description} ({api_count}개 API)")
        spec_info_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
        """)
        header_layout.addWidget(spec_info_label, alignment=Qt.AlignVCenter)
        header_layout.addStretch()

        main_layout.addWidget(self.spec_header)

        # 가로선 (헤더 아래 테두리)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #CECECE;")
        main_layout.addWidget(separator)

        # 데이터 영역 (1064 × 76)
        total_fields = total_pass + total_error
        required_pass = total_pass - opt_pass  # 필수 필드 통과 수
        # 선택 필드 전체 수 = 선택 통과 + 선택 에러
        opt_total = opt_pass + opt_error
        # 필수 필드 전체 수 = 전체 필드 - 선택 필드
        required_total = total_fields - opt_total

        self.spec_data_area = QWidget()
        self.spec_data_area.setFixedSize(1064, 76)
        self.spec_data_area.setStyleSheet("background: transparent;")
        data_layout = QHBoxLayout(self.spec_data_area)
        data_layout.setContentsMargins(56, 8, 32, 8)
        data_layout.setSpacing(0)

        # 통과 필드 수 (325 × 60) - 필수/선택 형식
        self.spec_pass_label = QLabel()
        self.spec_pass_label.setFixedSize(325, 60)
        self.spec_pass_label.setText(
            f"통과 필드 수 (필수/선택)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{required_pass}/{opt_pass}</span>"
        )
        self.spec_pass_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 20px; font-weight: 500; color: #000000;")
        data_layout.addWidget(self.spec_pass_label)

        # 구분선 1
        vline1 = QFrame()
        vline1.setFixedSize(2, 60)
        vline1.setStyleSheet("background-color: #CECECE;")
        data_layout.addWidget(vline1)

        # Spacer 1
        spacer1 = QWidget()
        spacer1.setFixedSize(24, 60)
        data_layout.addWidget(spacer1)

        # 전체 필드 수 (325 × 60) - 필수/선택 형식
        self.spec_total_label = QLabel()
        self.spec_total_label.setFixedSize(325, 60)
        self.spec_total_label.setText(
            f"전체 필드 수 (필수/선택)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{required_total}/{opt_total}</span>"
        )
        self.spec_total_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 20px; font-weight: 500; color: #000000;")
        data_layout.addWidget(self.spec_total_label)

        # 구분선 2
        vline2 = QFrame()
        vline2.setFixedSize(2, 60)
        vline2.setStyleSheet("background-color: #CECECE;")
        data_layout.addWidget(vline2)

        # Spacer 2
        spacer2 = QWidget()
        spacer2.setFixedSize(24, 60)
        data_layout.addWidget(spacer2)

        # 종합 평가 점수 (325 × 60)
        self.spec_score_label = QLabel()
        self.spec_score_label.setFixedSize(325, 60)
        self.spec_score_label.setText(
            f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{score:.1f}%</span>"
        )
        self.spec_score_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 20px; font-weight: 500; color: #000000;")
        data_layout.addWidget(self.spec_score_label)
        data_layout.addStretch()
        main_layout.addWidget(self.spec_data_area)

        spec_group.setLayout(main_layout)
        return spec_group

    def _create_total_score_display(self):
        """전체 점수 표시 위젯 생성 (1064 × 128)"""
        total_group = QGroupBox()
        total_group.setFixedSize(1064, 128)
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

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 헤더 영역 (1064 × 52)
        self.total_header = QWidget()
        self.total_header.setFixedSize(1064, 52)
        self.total_header.setStyleSheet("background: transparent; border: none;")
        header_layout = QHBoxLayout(self.total_header)
        header_layout.setContentsMargins(0, 5, 0, 5)
        header_layout.setSpacing(6)

        # 전체 점수 아이콘 (52 × 42)
        icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/image/test_runner/icn_전체점수.png"))
        icon_label.setPixmap(icon_pixmap.scaled(52, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(52, 42)
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label, alignment=Qt.AlignVCenter)

        # 전체 점수 레이블 (500 Medium 20px)
        total_name_label = QLabel("전체 점수")
        total_name_label.setStyleSheet("""
            color: #000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
        """)
        header_layout.addWidget(total_name_label, alignment=Qt.AlignVCenter)
        header_layout.addStretch()

        main_layout.addWidget(self.total_header)

        # 가로선 (헤더 아래 테두리)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #CECECE; border: none;")
        main_layout.addWidget(separator)

        # 데이터 영역 (1064 × 76)
        total_pass = self.parent.global_pass_cnt
        total_error = self.parent.global_error_cnt
        opt_pass = getattr(self.parent, 'global_opt_pass_cnt', 0)  # 선택 필드 통과 수
        opt_error = getattr(self.parent, 'global_opt_error_cnt', 0)  # 선택 필드 에러 수
        required_pass = total_pass - opt_pass  # 필수 필드 통과 수
        total_fields = total_pass + total_error
        # 선택 필드 전체 수 = 선택 통과 + 선택 에러
        opt_total = opt_pass + opt_error
        # 필수 필드 전체 수 = 전체 필드 - 선택 필드
        required_total = total_fields - opt_total
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0

        self.total_data_area = QWidget()
        self.total_data_area.setFixedSize(1064, 76)
        self.total_data_area.setStyleSheet("background: transparent; border: none;")
        data_layout = QHBoxLayout(self.total_data_area)
        data_layout.setContentsMargins(56, 8, 32, 8)
        data_layout.setSpacing(0)

        # 통과 필드 수 (325 × 60) - 필수/선택 형식
        self.total_pass_label = QLabel()
        self.total_pass_label.setFixedSize(325, 60)
        self.total_pass_label.setText(
            f"통과 필드 수 (필수/선택)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{required_pass}/{opt_pass}</span>"
        )
        self.total_pass_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 20px; font-weight: 500; color: #000000; border: none;")
        data_layout.addWidget(self.total_pass_label)

        # 구분선 1
        vline1 = QFrame()
        vline1.setFixedSize(2, 60)
        vline1.setStyleSheet("background-color: #CECECE; border: none;")
        data_layout.addWidget(vline1)

        # Spacer 1
        spacer1 = QWidget()
        spacer1.setFixedSize(24, 60)
        spacer1.setStyleSheet("border: none;")
        data_layout.addWidget(spacer1)

        # 전체 필드 수 (325 × 60) - 필수/선택 형식
        self.total_total_label = QLabel()
        self.total_total_label.setFixedSize(325, 60)
        self.total_total_label.setText(
            f"전체 필드 수 (필수/선택)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{required_total}/{opt_total}</span>"
        )
        self.total_total_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 20px; font-weight: 500; color: #000000; border: none;")
        data_layout.addWidget(self.total_total_label)

        # 구분선 2
        vline2 = QFrame()
        vline2.setFixedSize(2, 60)
        vline2.setStyleSheet("background-color: #CECECE; border: none;")
        data_layout.addWidget(vline2)

        # Spacer 2
        spacer2 = QWidget()
        spacer2.setFixedSize(24, 60)
        spacer2.setStyleSheet("border: none;")
        data_layout.addWidget(spacer2)

        # 종합 평가 점수 (325 × 60)
        self.total_score_label = QLabel()
        self.total_score_label.setFixedSize(325, 60)
        self.total_score_label.setText(
            f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{score:.1f}%</span>"
        )
        self.total_score_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 20px; font-weight: 500; color: #000000; border: none;")
        data_layout.addWidget(self.total_score_label)
        data_layout.addStretch()
        main_layout.addWidget(self.total_data_area)

        total_group.setLayout(main_layout)
        return total_group

    def table_cell_clicked(self, row, col):
        """상세 내용 버튼 클릭 시"""
        if col == 8:  # 'Score' column is 7, 'Detail' column is 8. Corrected to 8
            self._show_detail(row)
