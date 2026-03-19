from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5 import QtCore

from core.functions import resource_path
from core.logger import Logger
from core.utils import remove_api_number_suffix, load_external_constants
from ui.ui_components import TestSelectionPanel
from ui.detail_dialog import CombinedDetailDialog


def get_result_header_title_display_size(widget):
    return QPixmap(resource_path(widget._get_result_header_title_path())).size()


def create_embedded_back_navigation(parent, click_handler, width=424, height=46):
    container = QWidget(parent)
    container.setObjectName("top_back_navigation")
    container.setFixedSize(width, height)
    container.setStyleSheet("background: transparent;")
    container.base_width = width

    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.setSpacing(16)

    row = QWidget(container)
    row.setFixedSize(154, 29)
    row.setStyleSheet("background: transparent;")
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_layout.setSpacing(8)

    icon_button = QPushButton(row)
    icon_button.setObjectName("top_back_icon_button")
    icon_button.setFixedSize(22, 29)
    icon_button.setFocusPolicy(Qt.NoFocus)
    arrow_path = resource_path("assets/image/test_config/btn_back.svg").replace("\\", "/")
    icon_button.setStyleSheet(f"""
        QPushButton {{
            border: none;
            background-color: transparent;
            background-image: url('{arrow_path}');
            background-repeat: no-repeat;
            background-position: center;
        }}
    """)
    icon_button.clicked.connect(click_handler)
    row_layout.addWidget(icon_button)

    text_button = QPushButton("이전 화면으로", row)
    text_button.setObjectName("top_back_text_button")
    text_button.setFixedSize(114, 29)
    text_button.setFocusPolicy(Qt.NoFocus)
    text_button.setStyleSheet("""
        QPushButton {
            border: none;
            background-color: transparent;
            color: #262626;
            font-family: 'Noto Sans KR';
            font-size: 20px;
            font-weight: 500;
            text-align: left;
            padding: 0;
        }
    """)
    text_button.clicked.connect(click_handler)
    row_layout.addWidget(text_button)

    container_layout.addWidget(row, 0, Qt.AlignLeft)

    divider = QFrame(container)
    divider.setObjectName("top_back_divider")
    divider.setFixedSize(width, 1)
    divider.setStyleSheet("""
        QFrame {
            background-color: #E5E5E5;
            border: none;
        }
    """)
    container_layout.addWidget(divider, 0, Qt.AlignLeft)
    container.divider = divider

    return container


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

        # ✅ 결과 페이지 진입 시 원래 상태 저장 (돌아갈 때 복원용)
        self.original_spec_id = parent.current_spec_id
        self.original_group_id = getattr(parent, 'current_group_id', None)

        # ✅ 시험 결과 페이지 전용 아이콘 설정
        self.img_pass = resource_path("assets/image/test_runner/tag_성공.png")
        self.img_fail = resource_path("assets/image/test_runner/tag_실패.png")
        self.img_none = resource_path("assets/image/icon/icn_basic.png")
        self.webhook_badge_pixmap = QPixmap(resource_path("assets/image/icon/badge-webhook.png"))

        self.initUI()

    def _get_result_header_title_path(self):
        mode = getattr(self.parent, "validation_mode", "platform")
        title_map = {
            "platform": "assets/image/test_runner/platform_result_title.png",
            "system": "assets/image/test_runner/system_result_title.png",
        }
        return title_map.get(mode, title_map["platform"])

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
        header_title_pixmap = QPixmap(resource_path(self._get_result_header_title_path()))
        title_size = get_result_header_title_display_size(self)
        header_title_label.setPixmap(header_title_pixmap.scaled(title_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_title_label.setFixedSize(title_size)
        header_layout.addWidget(header_title_label)

        # 오른쪽 stretch (나머지 공간 채우기)
        header_layout.addStretch()

        mainLayout.addWidget(header_widget)

        # ✅ 본문 영역 컨테이너 (반응형 - main.png 배경)
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_widget.setStyleSheet("background-color: #FFFFFF;")

        # 배경 이미지를 QLabel로 설정 (절대 위치)
        self.content_bg_label = QLabel(self.content_widget)
        self.content_bg_label.setStyleSheet("background-color: #FFFFFF;")
        
        # ✅ 배경 구분선 및 패널 추가 (3페이지와 동일하게)
        self.left_background_panel = QFrame(self.content_bg_label)
        self.left_background_panel.setStyleSheet("background-color: #F7F7F7; border: none;")
        self.content_background_divider = QFrame(self.content_bg_label)
        self.content_background_divider.setStyleSheet("background-color: #D9D9D9; border: none;")
        self.right_background_panel = QFrame(self.content_bg_label)
        self.right_background_panel.setStyleSheet("background-color: #FFFFFF; border: none;")
        
        self.content_bg_label.lower()  # 맨 뒤로 보내기

        # ✅ 반응형: 원본 크기 저장
        self.original_window_size = (1680, 1006)
        self.original_bg_root_size = (1585, 970)
        self.original_left_col_size = (472, 970)
        self.original_right_col_size = (1112, 970)
        self.original_spec_panel_title_size = (424, 24)
        self.original_group_table_widget_size = (424, 204)
        self.original_field_group_size = (424, 561)
        self.original_info_title_size = (1064, 24)
        self.original_info_widget_size = (1064, 169)
        self.original_result_label_size = (1064, 24)
        self.original_result_header_widget_size = (1064, 38)
        self.original_result_table_height = 335  # ✅ 시험 결과 테이블 기본 높이 소폭 조정 (하단 밸런스)
        self.original_score_title_size = (1064, 24)
        self.original_score_table_size = (1064, 256)
        self.original_spec_group_size = (1064, 128)
        self.original_total_group_size = (1064, 128)
        self.original_buttonGroup_size = (1064, 48)
        # ✅ 점수 테이블 내부 위젯 원본 크기
        self.original_score_header_size = (1062, 52)
        self.original_score_data_area_size = (1064, 76)
        # 각 라벨별 너비 설정 (통과 필수/선택은 넓게, 종합 평가는 좁게)
        self.original_pass_label_size = (340, 60)    # 필수 필드 점수
        self.original_opt_label_size = (340, 60)     # 선택 필드 점수
        self.original_score_label_size = (315, 60)   # 종합 평가 점수
        self.original_column_widths = [40, 304, 100, 94, 116, 116, 94, 94, 90]

        # ✅ 2컬럼 레이아웃
        self.bg_root = QWidget(self.content_widget)
        self.bg_root.setObjectName("bg_root")
        self.bg_root.setFixedSize(1585, 970)
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
        self.left_col.setFixedSize(472, 970)
        self.left_col.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout()
        # ✅ 반응형: 상단 여백 조정 (임베디드 시 20px)
        left_top_margin = 20 if self.embedded else 36
        left_layout.setContentsMargins(24, left_top_margin, 24, 0)
        left_layout.setSpacing(0)

        # ✅ 상단 내비게이션 바 추가 (임베디드 모드일 때만)
        if self.embedded:
            self.top_back_navigation = create_embedded_back_navigation(
                self.left_col,
                self._on_back_clicked,
                width=424,
            )
            left_layout.addWidget(self.top_back_navigation, 0, Qt.AlignLeft | Qt.AlignTop)
            left_layout.addSpacing(16)

        # 시험 선택 패널 - TestSelectionPanel 사용
        self.test_selection_panel = TestSelectionPanel(self.CONSTANTS)
        
        # ✅ 시스템 연동 검증일 경우 '응답 검증'으로 표시 (플랫폼은 기본값 '요청 검증')
        # 상속 관계를 고려하여 MRO 확인
        is_system = any(c.__name__ == 'SystemMainUI' for c in self.parent.__class__.__mro__)
        
        # Fallback: 모듈 이름으로 확인 (SystemMainUI 상속 확인이 실패할 경우 대비)
        if not is_system:
            parent_module = self.parent.__class__.__module__
            if 'systemVal_all' in parent_module or 'system_app' in parent_module:
                is_system = True

        if is_system:
            self.test_selection_panel.mode_suffix = " (응답 검증)"

        self.test_selection_panel.groupSelected.connect(self.on_group_selected)
        self.test_selection_panel.scenarioSelected.connect(self.on_test_field_selected)

        # 멤버 변수 매핑 (기존 코드와의 호환성 유지)
        self.spec_panel_title = self.test_selection_panel.spec_panel_title
        self.group_table_widget = self.test_selection_panel.group_table_widget
        self.field_group = self.test_selection_panel.field_group
        self.group_table = self.test_selection_panel.group_table
        self.test_field_table = self.test_selection_panel.test_field_table

        # ✅ 4페이지 전용 높이 강제 설정 (561px)
        self.field_group.setFixedSize(424, 561)
        self.test_field_table.setFixedHeight(561)

        # 원본 사이즈 변수 매핑 (반응형 동작을 위해 필요)
        self.original_spec_panel_title_size = self.test_selection_panel.original_spec_panel_title_size
        self.original_group_table_widget_size = self.test_selection_panel.original_group_table_widget_size
        # self.original_field_group_size = self.test_selection_panel.original_field_group_size # 제거: 4페이지 고유값 사용
        
        # 인덱스 매핑 정보도 연결 (필요 시)
        # self.group_name_to_index = self.test_selection_panel.group_name_to_index 
        # (이건 패널 내부에서 관리되지만, 필요하면 여기서 참조)

        left_layout.addWidget(self.test_selection_panel)

        left_layout.addStretch()
        self.left_col.setLayout(left_layout)

        self.column_divider = QFrame()
        self.column_divider.setFixedSize(1, 970)
        self.column_divider.setStyleSheet("background: transparent; border: none;")

        # ✅ 오른쪽 컬럼 (스크롤 영역으로 감싸기)
        self.right_scroll_container = QScrollArea()
        self.right_scroll_container.setFixedSize(1112, 970)
        self.right_scroll_container.setWidgetResizable(True)
        self.right_scroll_container.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.right_scroll_container.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.right_scroll_container.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #DFDFDF;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #A3A9AD;
                min-height: 20px;
                border-radius: 6px;
                margin: 0px 2px;
            }
        """)

        self.right_col = QWidget()
        self.right_col.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(self.right_col)
        right_layout.setContentsMargins(24, 36, 24, 40)  # 하단 여백 추가
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
            margin-top: 30px;
            margin-bottom: 8px;
            letter-spacing: -0.3px;
        """)
        right_layout.addWidget(self.result_label)

        # 결과 테이블 (크기 키움: 350px)
        self.create_result_table(right_layout)
        right_layout.addSpacing(30)

        # 시험 점수 요약 타이틀 (1064 × 24)
        self.score_title = QLabel('시험 점수 요약')
        self.score_title.setFixedSize(1064, 24)
        self.score_title.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """)
        right_layout.addWidget(self.score_title)
        right_layout.addSpacing(8)

        # 시험 점수 테이블 (1064 × 256) - 분야별 점수 + 전체 점수
        self.score_table = QWidget()
        self.score_table.setFixedSize(1064, 256)
        self.score_table.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: none;
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

        # ✅ 버튼 그룹 (임베디드 모드가 아닐 때만 하단 간격 및 버튼 추가)
        if not self.embedded:
            right_layout.addSpacing(32)
            self.buttonGroup = QWidget()
            self.buttonGroup.setFixedSize(1064, 48)
            buttonLayout = QHBoxLayout()
            buttonLayout.setAlignment(Qt.AlignRight)  # 오른쪽 정렬
            buttonLayout.setContentsMargins(0, 0, 0, 0)

            # Standalone 모드: 닫기 버튼
            close_btn = QPushButton('닫기', self)
            close_btn.setFixedSize(362, 48)
            try:
                exit_enabled = resource_path("assets/image/test_runner/btn_common_enabled.png").replace("\\", "/")
                exit_hover = resource_path("assets/image/test_runner/btn_common_hover.png").replace("\\", "/")
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
        else:
            # 임베디드 모드일 때는 하단 여백을 주어 점수 요약을 살짝 올림 (5px 추가 상향)
            right_layout.addSpacing(30)

        self.right_col.setLayout(right_layout)

        columns_layout.addWidget(self.left_col)
        columns_layout.addWidget(self.column_divider)
        columns_layout.addWidget(self.right_col)

        bg_root_layout.addLayout(columns_layout)
        self.bg_root.setLayout(bg_root_layout)

        # content_widget 레이아웃 설정 (좌우 47px, 하단 44px padding, 왼쪽 정렬)
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(47, 0, 47, 44)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.bg_root, 0, Qt.AlignLeft | Qt.AlignVCenter)

        mainLayout.addWidget(self.content_widget, 1)  # 반응형: stretch=1로 남은 공간 채움

        self.setLayout(mainLayout)

        # 초기 시나리오 로드 (UI 요소 생성 후 호출)
        self.load_initial_scenarios()
        
        # ✅ 초기 배경 지오메트리 설정
        QtCore.QTimer.singleShot(0, self._update_content_background_geometry)

    def _update_content_background_geometry(self):
        """배경 패널 및 구분선 위치/크기 업데이트 (3페이지와 동일)"""
        if not hasattr(self, 'content_widget') or not self.content_widget:
            return
        if not hasattr(self, 'content_bg_label'):
            return

        content_width = self.content_widget.width()
        content_height = self.content_widget.height()
        self.content_bg_label.setGeometry(0, 0, content_width, content_height)

        if hasattr(self, 'bg_root') and hasattr(self, 'left_background_panel'):
            width_ratio = 1.0
            if hasattr(self, 'original_window_size') and self.original_window_size[0]:
                width_ratio = max(1.0, self.width() / self.original_window_size[0])
            
            # 3페이지(common_main_ui.py)와 동일한 오프셋 계산 적용
            divider_offset = int(round((width_ratio - 1.0) * 28))
            divider_x = self.bg_root.geometry().x() + self.left_col.width() - divider_offset
            
            self.left_background_panel.setGeometry(0, 0, divider_x, content_height)
            self.content_background_divider.setGeometry(divider_x, 0, 1, content_height)
            self.right_background_panel.setGeometry(
                divider_x + 1,
                0,
                max(0, content_width - divider_x - 1),
                content_height,
            )

    def resizeEvent(self, event):
        """창 크기 변경 시 배경 이미지 및 UI 반응형 조정"""
        super().resizeEvent(event)

        # ✅ 배경 지오메트리 실시간 업데이트
        self._update_content_background_geometry()

        # ✅ 반응형: UI 요소 크기 조정
        if hasattr(self, 'original_window_size') and hasattr(self, 'left_col'):
            current_width = self.width()
            current_height = self.height()

            # 비율 계산 (최소 1.0 - 원본 크기 이하로 줄어들지 않음)
            width_ratio = max(1.0, current_width / self.original_window_size[0])
            height_ratio = max(1.0, current_height / self.original_window_size[1])

            # ✅ 좌우 패널 정렬을 위한 확장량 계산
            # 기본 화면(height_ratio=1.0)에서는 561px을 유지하며, 
            # 창이 커질 때는 다른 페이지(3페이지 등)와 동일한 비례 배분 방식을 사용합니다.
            # 컬럼의 전체 높이(970)를 기준으로 확장량을 계산해야 우측과 정렬이 맞음
            original_column_height = 970  # (970)
            extra_column_height = original_column_height * (height_ratio - 1)

            # 왼쪽 패널 확장 요소 (비례 배분 기준)
            # group_table(204) + field_group(561) = 765px
            left_expandable_total = 765

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
                if hasattr(self, 'column_divider'):
                    self.column_divider.setFixedSize(1, new_left_height)
                
                # ✅ 상단 내비게이션 바 크기 조정 (3페이지와 동일)
                if hasattr(self, 'top_back_navigation'):
                    if hasattr(self, 'original_spec_panel_title_size'):
                        new_back_width = int(self.original_spec_panel_title_size[0] * width_ratio)
                    else:
                        new_back_width = int(getattr(self.top_back_navigation, 'base_width', 424) * width_ratio)
                    self.top_back_navigation.setFixedWidth(new_back_width)
                    if hasattr(self.top_back_navigation, 'divider'):
                        self.top_back_navigation.divider.setFixedWidth(new_back_width)

            # 시험 선택 타이틀 크기 조정 (가로만 확장)
            if hasattr(self, 'spec_panel_title') and hasattr(self, 'original_spec_panel_title_size'):
                new_title_width = int(self.original_spec_panel_title_size[0] * width_ratio)
                self.spec_panel_title.setFixedSize(new_title_width, self.original_spec_panel_title_size[1])
                
                # TestSelectionPanel 자체 너비도 업데이트
                if hasattr(self, 'test_selection_panel'):
                     self.test_selection_panel.setFixedWidth(new_title_width)

            # 그룹 테이블 위젯 크기 조정 (비례 배분)
            if hasattr(self, 'group_table_widget') and hasattr(self, 'original_group_table_widget_size'):
                new_group_width = int(self.original_group_table_widget_size[0] * width_ratio)
                group_extra = extra_column_height * (204 / left_expandable_total)
                new_group_height = int(204 + group_extra)
                self.group_table_widget.setFixedSize(new_group_width, new_group_height)
                # 내부 테이블 크기도 조정
                if hasattr(self, 'group_table'):
                    self.group_table.setFixedHeight(new_group_height)

            # 시험 시나리오 테이블 크기 조정 (비례 배분)
            if hasattr(self, 'field_group') and hasattr(self, 'original_field_group_size'):
                new_field_width = int(self.original_field_group_size[0] * width_ratio)
                # 추가 높이를 561/765 비율로 배분하여 너무 극단적이지 않게 확장
                field_extra = extra_column_height * (561 / left_expandable_total)
                new_field_height = int(561 + field_extra)
                
                self.field_group.setFixedSize(new_field_width, new_field_height)
                # 내부 테이블 크기도 조정
                if hasattr(self, 'test_field_table'):
                    self.test_field_table.setFixedHeight(new_field_height)

            # ✅ 오른쪽 컬럼 크기 조정 (스크롤 컨테이너 크기 조정)
            if hasattr(self, 'right_scroll_container') and hasattr(self, 'original_right_col_size'):
                new_right_width = int(self.original_right_col_size[0] * width_ratio)
                new_right_height = int(self.original_right_col_size[1] * height_ratio)
                self.right_scroll_container.setFixedSize(new_right_width, new_right_height)

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
                    for i, label in enumerate(self.result_header_labels):
                        new_label_width = int(self.original_column_widths[i] * width_ratio)
                        label.setFixedSize(new_label_width, 30)
            # ✅ 결과 테이블 스크롤 영역 크기 조정 (3페이지 방식: 남은 공간 모두 차지)
            if hasattr(self, 'result_scroll_area'):
                new_scroll_width = int(1064 * width_ratio)
                
                # 고정된 위젯들의 높이 합산 (마진 및 여유 공간 정밀 반영)
                # 1. 레이아웃 상단 마진: 36
                # 2. 시험 정보 타이틀 영역: 약 40
                # 3. 시험 정보 위젯: 169
                # 4. 시험 결과 라벨 영역 (마진 포함): 약 74 (30 + 24 + 20)
                # 5. 결과 테이블 헤더: 30
                # 6. 중간 간격 (Spacing): 30
                # 7. 시험 점수 요약 타이틀 영역: 약 40
                # 8. 시험 점수 테이블: 256
                # 9. 레이아웃 하단 마진: 40
                # 10. 기타 미세 보정값: 13
                
                fixed_heights = 36 + 40 + 169 + 74 + 30 + 30 + 40 + 256 + 40 + 13
                bottom_gap = 30 if self.embedded else 80
                
                # 전체 컬럼 높이에서 고정 높이들을 뺀 나머지를 할당
                new_scroll_height = new_right_height - fixed_heights - bottom_gap
                
                # 최소 높이 보장
                new_scroll_height = max(150, new_scroll_height)
                
                self.result_scroll_area.setFixedSize(new_scroll_width, new_scroll_height)

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
                # 각 라벨별 다른 너비 적용
                new_pass_width = int(self.original_pass_label_size[0] * width_ratio)
                new_opt_width = int(self.original_opt_label_size[0] * width_ratio)
                new_score_width = int(self.original_score_label_size[0] * width_ratio)

                # 분야별 점수 내부 위젯
                if hasattr(self, 'spec_header'):
                    self.spec_header.setFixedSize(new_header_width, self.original_score_header_size[1])
                if hasattr(self, 'spec_data_area'):
                    self.spec_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
                if hasattr(self, 'spec_pass_label'):
                    self.spec_pass_label.setFixedSize(new_pass_width, self.original_pass_label_size[1])
                if hasattr(self, 'spec_total_label'):
                    self.spec_total_label.setFixedSize(new_opt_width, self.original_opt_label_size[1])
                if hasattr(self, 'spec_score_label'):
                    self.spec_score_label.setFixedSize(new_score_width, self.original_score_label_size[1])

                # 전체 점수 내부 위젯
                if hasattr(self, 'total_header'):
                    self.total_header.setFixedSize(new_header_width, self.original_score_header_size[1])
                if hasattr(self, 'total_data_area'):
                    self.total_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
                if hasattr(self, 'total_pass_label'):
                    self.total_pass_label.setFixedSize(new_pass_width, self.original_pass_label_size[1])
                if hasattr(self, 'total_total_label'):
                    self.total_total_label.setFixedSize(new_opt_width, self.original_opt_label_size[1])
                if hasattr(self, 'total_score_label'):
                    self.total_score_label.setFixedSize(new_score_width, self.original_score_label_size[1])

            # ✅ 버튼 그룹 크기 조정 (가로만 확장, 세로 고정)
            if hasattr(self, 'buttonGroup') and hasattr(self, 'original_buttonGroup_size'):
                new_btn_group_width = int(self.original_buttonGroup_size[0] * width_ratio)
                self.buttonGroup.setFixedSize(new_btn_group_width, self.original_buttonGroup_size[1])

            # ✅ 반응형: back_btn 크기 조정
            if hasattr(self, 'back_btn') and hasattr(self, 'original_back_btn_size'):
                new_back_btn_width = int(self.original_back_btn_size[0] * width_ratio)
                self.back_btn.setFixedSize(new_back_btn_width, self.original_back_btn_size[1])

            # ✅ 결과 테이블 컬럼 너비 비례 조정 (마지막 컬럼이 남은 공간 채움)
            if hasattr(self, 'tableWidget') and hasattr(self, 'original_column_widths'):
                # 스크롤바 표시 여부 확인
                row_count = self.tableWidget.rowCount()
                total_row_height = row_count * 40  # 각 행 40px
                scroll_area_height = self.result_scroll_area.viewport().height() if hasattr(self, 'result_scroll_area') else 189
                scrollbar_visible = total_row_height > scroll_area_height
                scrollbar_width = 16 if scrollbar_visible else 0

                new_scroll_width = int(1064 * width_ratio)
                # border(2) + 스크롤바 + 여유분(2) 고려
                available_width = new_scroll_width - 4 - scrollbar_width

                # 마지막 컬럼을 제외한 나머지 컬럼 너비 설정
                used_width = 0
                for i, orig_width in enumerate(self.original_column_widths[:-1]):
                    new_col_width = int(orig_width * width_ratio)
                    self.tableWidget.setColumnWidth(i, new_col_width)
                    used_width += new_col_width

                # 마지막 컬럼은 남은 공간을 채움
                last_col_width = available_width - used_width
                self.tableWidget.setColumnWidth(len(self.original_column_widths) - 1, last_col_width)

        # ✅ 배경 지오메트리 실시간 업데이트 (리사이징 완료 후 최하단에서 호출 - 3페이지와 동일)
        self._update_content_background_geometry()

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
            # 각 라벨별 다른 너비 적용
            new_pass_width = int(self.original_pass_label_size[0] * width_ratio)
            new_opt_width = int(self.original_opt_label_size[0] * width_ratio)
            new_score_width = int(self.original_score_label_size[0] * width_ratio)

            # 분야별 점수 내부 위젯
            if hasattr(self, 'spec_header'):
                self.spec_header.setFixedSize(new_header_width, self.original_score_header_size[1])
            if hasattr(self, 'spec_data_area'):
                self.spec_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
            if hasattr(self, 'spec_pass_label'):
                self.spec_pass_label.setFixedSize(new_pass_width, self.original_pass_label_size[1])
            if hasattr(self, 'spec_total_label'):
                self.spec_total_label.setFixedSize(new_opt_width, self.original_opt_label_size[1])
            if hasattr(self, 'spec_score_label'):
                self.spec_score_label.setFixedSize(new_score_width, self.original_score_label_size[1])

            # 전체 점수 내부 위젯
            if hasattr(self, 'total_header'):
                self.total_header.setFixedSize(new_header_width, self.original_score_header_size[1])
            if hasattr(self, 'total_data_area'):
                self.total_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
            if hasattr(self, 'total_pass_label'):
                self.total_pass_label.setFixedSize(new_pass_width, self.original_pass_label_size[1])
            if hasattr(self, 'total_total_label'):
                self.total_total_label.setFixedSize(new_opt_width, self.original_opt_label_size[1])
            if hasattr(self, 'total_score_label'):
                self.total_score_label.setFixedSize(new_score_width, self.original_score_label_size[1])

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

            Logger.debug(f"[RESULT DEBUG] 🔄 그룹 선택: {old_group_id} → {new_group_id}")

            # ✅ 그룹이 변경되면 current_spec_id 초기화
            if old_group_id != new_group_id:
                self.current_spec_id = None
                Logger.debug(f"[RESULT DEBUG] ✨ 그룹 변경으로 current_spec_id 초기화")

            # ✅ 그룹 ID 및 그룹명 저장
            self.parent.current_group_id = new_group_id
            self.parent.current_group_name = group_name  # ✅ 그룹명 저장

            self.test_selection_panel.update_test_field_table(selected_group)

            # ✅ 시험 정보 업데이트
            self.update_test_info()

    def on_test_field_selected(self, row, col):
        """시나리오 선택 시 해당 결과 표시 (결과 없어도 API 정보 표시)"""

        if row not in self.test_selection_panel.index_to_spec_id:
            return

        selected_spec_id = self.test_selection_panel.index_to_spec_id[row]

        # 선택된 시나리오가 현재와 같으면 무시
        if selected_spec_id == self.current_spec_id:
            return

        Logger.debug(f" 시나리오 전환: {self.current_spec_id} → {selected_spec_id}")
        Logger.debug(f"[RESULT DEBUG] 현재 그룹: {self.parent.current_group_id}")

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

            Logger.debug(f" API 개수: {len(self.parent.videoMessages)}")
            Logger.debug(f" inSchema 개수: {len(self.parent.inSchema)}")
            Logger.debug(f" webhookSchema 개수: {len(self.parent.webhookSchema)}")

            # ✅ 4. 저장된 결과 데이터가 있으면 로드 (복합키 사용)
            composite_key = f"{self.parent.current_group_id}_{selected_spec_id}"
            Logger.debug(f"[RESULT DEBUG] 📂 데이터 복원 시도: {composite_key}")
            if composite_key in self.parent.spec_table_data:
                saved_data = self.parent.spec_table_data[composite_key]

                # step_buffers 복원
                saved_buffers = saved_data.get('step_buffers', [])
                if saved_buffers:
                    self.parent.step_buffers = [buf.copy() for buf in saved_buffers]
                    Logger.debug(f" step_buffers 복원 완료: {len(self.parent.step_buffers)}개")
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

                # ✅ 선택 필드 점수 정보 복원 (total 값이 없으면 step 배열 합계 사용)
                step_opt_pass = saved_data.get('step_opt_pass_counts', [])
                step_opt_error = saved_data.get('step_opt_error_counts', [])

                # total 값이 저장되어 있으면 사용, 없으면 step 배열 합계로 계산
                if 'total_opt_pass_cnt' in saved_data:
                    self.parent.total_opt_pass_cnt = saved_data['total_opt_pass_cnt']
                else:
                    self.parent.total_opt_pass_cnt = sum(step_opt_pass) if step_opt_pass else 0

                if 'total_opt_error_cnt' in saved_data:
                    self.parent.total_opt_error_cnt = saved_data['total_opt_error_cnt']
                else:
                    self.parent.total_opt_error_cnt = sum(step_opt_error) if step_opt_error else 0

                Logger.debug(f" total_opt_pass_cnt 복원: {self.parent.total_opt_pass_cnt}")
                Logger.debug(f" total_opt_error_cnt 복원: {self.parent.total_opt_error_cnt}")

                # ✅ step_pass_counts와 step_error_counts 배열 복원
                self.parent.step_pass_counts = saved_data.get('step_pass_counts', [0] * len(self.parent.videoMessages))[:]
                self.parent.step_error_counts = saved_data.get('step_error_counts', [0] * len(self.parent.videoMessages))[:]

                # ✅ step_opt_pass_counts와 step_opt_error_counts 배열 복원
                self.parent.step_opt_pass_counts = saved_data.get('step_opt_pass_counts', [0] * len(self.parent.videoMessages))[:]
                self.parent.step_opt_error_counts = saved_data.get('step_opt_error_counts', [0] * len(self.parent.videoMessages))[:]

                Logger.debug(f" step_pass_counts 복원: {self.parent.step_pass_counts}")
                Logger.debug(f" step_error_counts 복원: {self.parent.step_error_counts}")
                Logger.debug(f" total_opt_pass_cnt 복원: {self.parent.total_opt_pass_cnt}")
                Logger.debug(f" total_opt_error_cnt 복원: {self.parent.total_opt_error_cnt}")

                # 테이블 및 점수 표시 업데이트
                self.reload_result_table(saved_data)
                self.update_score_displays(saved_data)

                # ✅ 시험 정보 업데이트
                self.update_test_info()

                Logger.debug(f" {selected_spec_id} 저장된 결과 로드 완료")
            else:
                # 결과가 없으면 빈 테이블 표시
                Logger.debug(f" {selected_spec_id} 결과 없음 - 빈 테이블 표시")
                self.show_empty_result_table()

                # ✅ 시험 정보 업데이트
                self.update_test_info()

        except Exception as e:
            Logger.error(f" 시나리오 전환 실패: {e}")
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

    def _is_webhook_api(self, row):
        if hasattr(self.parent, 'trans_protocols') and row < len(self.parent.trans_protocols):
            protocol = str(self.parent.trans_protocols[row] or "").strip().lower()
            return protocol == "webhook"
        return False

    def _set_api_name_cell(self, row, api_name):
        api_item = QTableWidgetItem(api_name)
        api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        api_item.setData(Qt.UserRole, api_name)
        api_item.setText("")
        self.tableWidget.setItem(row, 1, api_item)

        api_container = QWidget()
        api_layout = QHBoxLayout()
        api_layout.setContentsMargins(6, 0, 6, 0)
        api_layout.setSpacing(4)
        api_layout.addStretch()

        api_name_label = QLabel(api_name)
        api_name_label.setStyleSheet("""
            QLabel {
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-weight: 400;
            }
        """)
        api_name_label.setAlignment(Qt.AlignVCenter)
        api_layout.addWidget(api_name_label)

        if self._is_webhook_api(row) and not self.webhook_badge_pixmap.isNull():
            webhook_badge_label = QLabel()
            webhook_badge_label.setPixmap(self.webhook_badge_pixmap)
            webhook_badge_label.setScaledContents(False)
            webhook_badge_label.setFixedSize(self.webhook_badge_pixmap.size())
            webhook_badge_label.setAlignment(Qt.AlignCenter)
            api_layout.addWidget(webhook_badge_label, 0, Qt.AlignVCenter)

        api_layout.addStretch()
        api_container.setLayout(api_layout)
        self.tableWidget.setCellWidget(row, 1, api_container)

    def show_empty_result_table(self):
        """결과가 없을 때 빈 테이블 표시 (API 목록만)"""
        api_list = self.parent.videoMessagesDisplay  # 표시용 이름 사용
        api_count = len(api_list)

        Logger.debug(f" 빈 테이블 생성: {api_count}개 API")

        # ✅ step_buffers 초기화 (상세 내용 확인을 위해 필수!)
        self.parent.step_buffers = []
        for i in range(api_count):
            api_name = api_list[i] if i < len(api_list) else f"API {i + 1}"
            self.parent.step_buffers.append({
                "data": f"아직 시험이 진행되지 않았습니다.\n\nAPI: {api_name}",
                "error": "시험 데이터가 없습니다.",
                "result": "PASS"
            })

        Logger.debug(f" step_buffers 생성 완료: {len(self.parent.step_buffers)}개")

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
            self._set_api_name_cell(row, api_list[row])

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
            self._set_api_name_cell(row, display_name)

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
        """상세 내용 확인 - 자체 tableWidget 데이터 사용"""
        try:
            # 자체 tableWidget에서 API 이름 가져오기 (부모 테이블 참조 문제 해결)
            api_item = self.tableWidget.item(row, 1)
            if api_item is None:
                QMessageBox.warning(self, "오류", "해당 행의 API 정보를 찾을 수 없습니다.")
                return
            api_name = api_item.data(Qt.UserRole) or api_item.text()

            # parent의 데이터 가져오기
            buf = self.parent.step_buffers[row] if row < len(self.parent.step_buffers) else {"data": "", "error": "", "result": ""}

            # 스키마 데이터 가져오기
            try:
                schema_data = self.parent.videoOutSchema[row] if row < len(self.parent.videoOutSchema) else None
            except:
                schema_data = None

            # 웹훅 스키마 데이터 가져오기
            webhook_schema = None
            if hasattr(self.parent, 'trans_protocols') and row < len(self.parent.trans_protocols):
                current_protocol = self.parent.trans_protocols[row]
                if current_protocol == "WebHook":
                    if hasattr(self.parent, 'webhookInSchema') and row < len(self.parent.webhookInSchema):
                        webhook_schema = self.parent.webhookInSchema[row]

            # 통합 팝업창 띄우기
            dialog = CombinedDetailDialog(api_name, buf, schema_data, webhook_schema)
            dialog.exec_()

        except Exception as e:
            Logger.error(f" 상세 내용 확인 오류: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "오류", f"상세 내용을 표시할 수 없습니다.\n{str(e)}")

    def update_score_displays(self, saved_data):
        """점수 표시 업데이트"""
        # ✅ parent에서 직접 데이터 가져오기 (이미 복원된 상태)
        total_pass = getattr(self.parent, 'total_pass_cnt', saved_data.get('total_pass_cnt', 0))
        total_error = getattr(self.parent, 'total_error_cnt', saved_data.get('total_error_cnt', 0))
        total_fields = total_pass + total_error
        score = (total_pass / total_fields * 100) if total_fields > 0 else 0

        # ✅ 선택 필드 통과/에러 수 - parent에서 직접 가져오기
        opt_pass = getattr(self.parent, 'total_opt_pass_cnt', saved_data.get('total_opt_pass_cnt', 0))
        opt_error = getattr(self.parent, 'total_opt_error_cnt', saved_data.get('total_opt_error_cnt', 0))

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

                        # 새로운 점수 위젯 생성 (opt_pass, opt_error 포함)
                        self.spec_score_group = self._create_spec_score_display_with_data(
                            total_pass, total_error, score, opt_pass, opt_error
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
        self.info_label = QLabel(info_text)  # ✅ 멤버 변수로 저장
        self.info_label.setWordWrap(True)  # 줄바꿈 자동 처리
        self.info_label.setStyleSheet("""
            font-family: "Noto Sans KR";
            font-size: 16px;
            font-weight: 400;
            color: #1B1B1C;
            line-height: 1.8;
            border: none;
        """)

        layout.addWidget(self.info_label)
        layout.addStretch()
        info_widget.setLayout(layout)

        # ✅ 스크롤 영역 추가
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedSize(1064, 169)
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
        """결과 테이블 생성 - 3페이지(common_main_ui) 구조와 동일하게 복구"""
        api_count = self.parent.tableWidget.rowCount()

        # 별도 헤더 위젯 (1064px 전체 너비)
        self.result_header_widget = QWidget()
        self.result_header_widget.setObjectName("result_header_widget")
        self.result_header_widget.setFixedSize(1064, 30)
        self.result_header_widget.setStyleSheet("""
            QWidget#result_header_widget {
                background-color: #EDF0F3;
                border: 1px solid #CECECE;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        """)
        header_layout = QHBoxLayout(self.result_header_widget)
        header_layout.setContentsMargins(0, 0, 14, 0)  # 오른쪽 14px (스크롤바 영역)
        header_layout.setSpacing(0)

        # 헤더 컬럼 정의 (너비, 텍스트) - 9컬럼 구조
        header_columns = [
            (40, ""),            # No.
            (304, "API 명"),
            (100, "결과"),
            (116, "전체 필드 수"),
            (116, "통과 필드 수"),
            (94, "실패 필드 수"),
            (94, "검증 횟수"),
            (94, "평가 점수"),
            (90, "상세 내용")
        ]

        # ✅ 헤더 라벨 저장
        self.result_header_labels = []
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
            header_layout.addWidget(label)
            self.result_header_labels.append(label)

        # 테이블 본문 (헤더 숨김)
        self.tableWidget = QTableWidget(api_count, 9)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setFocusPolicy(Qt.NoFocus)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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

        # 컬럼 너비 설정 - 3페이지와 동일한 베이스 너비 사용
        self.original_column_widths = [40, 304, 100, 116, 116, 94, 94, 94, 90]
        for i, width in enumerate(self.original_column_widths):
            self.tableWidget.setColumnWidth(i, width)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)

        # 행 높이 설정
        for i in range(api_count):
            self.tableWidget.setRowHeight(i, 40)

        # 데이터 복사 및 상세 버튼 클릭 연결
        self._copy_table_data()
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)

        # QScrollArea로 본문 감싸기 (3페이지와 동일 스타일)
        self.result_scroll_area = QScrollArea()
        self.result_scroll_area.setWidget(self.tableWidget)
        self.result_scroll_area.setWidgetResizable(True)
        self.result_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.result_scroll_area.setViewportMargins(0, 0, 0, 2)
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

        # 레이아웃에 직접 추가 (3페이지 방식)
        parent_layout.addWidget(self.result_header_widget)
        parent_layout.addWidget(self.result_scroll_area)

    def _on_back_clicked(self):
        """뒤로가기 버튼 클릭 시 - 원래 시나리오로 복원 후 시그널 발생"""
        try:
            # ✅ 원래 시나리오로 복원 (결과 페이지 진입 시 저장해둔 값)
            if self.original_spec_id and self.original_spec_id != self.parent.current_spec_id:
                Logger.debug(f" 원래 시나리오로 복원: {self.parent.current_spec_id} → {self.original_spec_id}")

                # 1. spec_id 복원
                self.parent.current_spec_id = self.original_spec_id
                if self.original_group_id:
                    self.parent.current_group_id = self.original_group_id

                # 2. 원래 시나리오의 데이터 다시 로드
                self.parent.load_specs_from_constants()
                self.parent.get_setting()

            # ✅ 저장된 결과 데이터 복원 (update_result_table_structure 호출 제거 - 테이블 초기화 방지)
            composite_key = f"{self.parent.current_group_id}_{self.parent.current_spec_id}"
            if hasattr(self.parent, 'spec_table_data') and composite_key in self.parent.spec_table_data:
                saved_data = self.parent.spec_table_data[composite_key]

                # step_buffers 복원
                saved_buffers = saved_data.get('step_buffers', [])
                if saved_buffers:
                    self.parent.step_buffers = [buf.copy() for buf in saved_buffers]

                # 점수 정보 복원
                self.parent.total_pass_cnt = saved_data.get('total_pass_cnt', 0)
                self.parent.total_error_cnt = saved_data.get('total_error_cnt', 0)

                # ✅ 선택 필드 점수 정보 복원
                self.parent.total_opt_pass_cnt = saved_data.get('total_opt_pass_cnt', 0)
                self.parent.total_opt_error_cnt = saved_data.get('total_opt_error_cnt', 0)

                # ✅ step 배열 복원
                self.parent.step_pass_counts = saved_data.get('step_pass_counts', [0] * len(self.parent.videoMessages))[:]
                self.parent.step_error_counts = saved_data.get('step_error_counts', [0] * len(self.parent.videoMessages))[:]
                self.parent.step_opt_pass_counts = saved_data.get('step_opt_pass_counts', [0] * len(self.parent.videoMessages))[:]
                self.parent.step_opt_error_counts = saved_data.get('step_opt_error_counts', [0] * len(self.parent.videoMessages))[:]

                # ✅ 현재 진행 상태 복원 (cnt, current_retry)
                self.parent.cnt = saved_data.get('cnt', 0)
                self.parent.current_retry = saved_data.get('current_retry', 0)

                # 테이블 데이터 복원
                table_data = saved_data.get('table_data', [])
                for row, row_data in enumerate(table_data):
                    if row >= self.parent.tableWidget.rowCount():
                        break

                    # 아이콘 상태 복원 (컬럼 2) - ✅ 84x20 크기로 복원
                    icon_state = row_data.get('icon_state', '')
                    if icon_state in ["PASS", "FAIL"]:
                        img = self.parent.img_pass if icon_state == "PASS" else self.parent.img_fail
                        icon_widget = QWidget()
                        icon_layout = QHBoxLayout()
                        icon_layout.setContentsMargins(0, 0, 0, 0)
                        icon_label = QLabel()
                        icon_label.setPixmap(QIcon(img).pixmap(84, 20))  # ✅ 원래 크기로 복원
                        icon_label.setAlignment(Qt.AlignCenter)
                        icon_label.setToolTip(f"Result: {icon_state}")
                        icon_layout.addWidget(icon_label)
                        icon_layout.setAlignment(Qt.AlignCenter)
                        icon_widget.setLayout(icon_layout)
                        self.parent.tableWidget.setCellWidget(row, 2, icon_widget)

                    # 컬럼 3-7 복원
                    for col, key in [(3, 'total_count'), (4, 'pass_count'),
                                     (5, 'fail_count'), (6, 'retry_count'), (7, 'score')]:
                        value = row_data.get(key, '0')
                        item = self.parent.tableWidget.item(row, col)
                        if item:
                            item.setText(str(value))

                Logger.debug(f" parent 테이블 결과 데이터 복원 완료")

                # ✅ parent의 점수 표시 갱신
                if hasattr(self.parent, 'update_score_display'):
                    self.parent.update_score_display()
                    Logger.debug(f" parent 점수 표시 갱신 완료")

        except Exception as e:
            Logger.error(f" parent 테이블 복원 실패: {e}")
            import traceback
            traceback.print_exc()

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
                api_name = api_item.data(Qt.UserRole) or api_item.text()
                self._set_api_name_cell(row, api_name)

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

    def update_test_info(self):
        """시험 정보 업데이트 (시나리오 선택 시 호출)"""
        if not hasattr(self, 'info_label'):
            Logger.warning("info_label이 없습니다. 시험 정보를 업데이트할 수 없습니다.")
            return

        # ✅ 시험 정보 다시 불러오기
        test_info = self.parent.load_test_info_from_constants()

        # ✅ 시험 정보를 한 개의 문자열로 합치기
        info_text = "\n".join([f"{label}: {value}" for label, value in test_info])

        # ✅ 라벨 텍스트 업데이트
        self.info_label.setText(info_text)

        Logger.debug(f"[RESULT DEBUG] 시험 정보 업데이트 완료")

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
        spec_group = QGroupBox()
        spec_group.setFixedSize(1064, 128)
        spec_group.setStyleSheet("""
            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                padding: 0px;
                margin: 0px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 헤더 영역 (1064 × 52)
        self.spec_header = QWidget()
        self.spec_header.setFixedSize(1062, 52)
        self.spec_header.setStyleSheet("background: #F5F5F5;")
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

        main_layout.addWidget(self.spec_header, alignment=Qt.AlignHCenter)

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

        # 필수 통과율 계산
        if required_total > 0:
            required_score = (required_pass / required_total) * 100
        else:
            required_score = 0

        # 선택 통과율 계산
        if opt_total > 0:
            opt_score = (opt_pass / opt_total) * 100
        else:
            opt_score = 0

        self.spec_data_area = QWidget()
        self.spec_data_area.setFixedSize(1064, 76)
        self.spec_data_area.setStyleSheet("background: transparent;")
        data_layout = QHBoxLayout(self.spec_data_area)
        data_layout.setContentsMargins(20, 8, 20, 8)
        data_layout.setSpacing(0)

        # 필수 필드 점수 - % (통과/전체) 형식
        self.spec_pass_label = QLabel()
        self.spec_pass_label.setFixedSize(340, 60)  # 통과 필수/선택
        self.spec_pass_label.setText(
            f"필수 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"{required_score:.1f}% ({required_pass}/{required_total})</span>"
        )
        self.spec_pass_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000;")
        data_layout.addWidget(self.spec_pass_label)

        # 구분선 1
        vline1 = QFrame()
        vline1.setFixedSize(2, 60)
        vline1.setStyleSheet("background-color: #CECECE;")
        data_layout.addWidget(vline1)

        # Spacer 1
        spacer1 = QWidget()
        spacer1.setFixedSize(12, 60)
        data_layout.addWidget(spacer1)

        # 선택 필드 점수 - % (통과/전체) 형식
        self.spec_total_label = QLabel()
        self.spec_total_label.setFixedSize(340, 60)  # 통과 필수/선택
        self.spec_total_label.setText(
            f"선택 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"{opt_score:.1f}% ({opt_pass}/{opt_total})</span>"
        )
        self.spec_total_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000;")
        data_layout.addWidget(self.spec_total_label)

        # 구분선 2
        vline2 = QFrame()
        vline2.setFixedSize(2, 60)
        vline2.setStyleSheet("background-color: #CECECE;")
        data_layout.addWidget(vline2)

        # Spacer 2
        spacer2 = QWidget()
        spacer2.setFixedSize(12, 60)
        data_layout.addWidget(spacer2)

        # 종합 평가 점수 - % (통과/전체) 형식
        self.spec_score_label = QLabel()
        self.spec_score_label.setFixedSize(315, 60)  # 종합 평가 점수
        self.spec_score_label.setText(
            f"종합 평가 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"{score:.1f}% ({total_pass}/{total_fields})</span>"
        )
        self.spec_score_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000;")
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
        self.total_header.setFixedSize(1062, 52)
        self.total_header.setStyleSheet("background: #F5F5F5; border: none;")
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

        main_layout.addWidget(self.total_header, alignment=Qt.AlignHCenter)

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

        # 필수 통과율 계산
        if required_total > 0:
            required_score = (required_pass / required_total) * 100
        else:
            required_score = 0

        # 선택 통과율 계산
        if opt_total > 0:
            opt_score = (opt_pass / opt_total) * 100
        else:
            opt_score = 0

        self.total_data_area = QWidget()
        self.total_data_area.setFixedSize(1064, 76)
        self.total_data_area.setStyleSheet("background: transparent; border: none;")
        data_layout = QHBoxLayout(self.total_data_area)
        data_layout.setContentsMargins(20, 8, 20, 8)
        data_layout.setSpacing(0)

        # 필수 필드 점수 - % (통과/전체) 형식
        self.total_pass_label = QLabel()
        self.total_pass_label.setFixedSize(340, 60)  # 통과 필수/선택
        self.total_pass_label.setText(
            f"필수 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"{required_score:.1f}% ({required_pass}/{required_total})</span>"
        )
        self.total_pass_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000; border: none;")
        data_layout.addWidget(self.total_pass_label)

        # 구분선 1
        vline1 = QFrame()
        vline1.setFixedSize(2, 60)
        vline1.setStyleSheet("background-color: #CECECE; border: none;")
        data_layout.addWidget(vline1)

        # Spacer 1
        spacer1 = QWidget()
        spacer1.setFixedSize(12, 60)
        spacer1.setStyleSheet("border: none;")
        data_layout.addWidget(spacer1)

        # 선택 필드 점수 - % (통과/전체) 형식
        self.total_total_label = QLabel()
        self.total_total_label.setFixedSize(340, 60)  # 통과 필수/선택
        self.total_total_label.setText(
            f"선택 필드 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"{opt_score:.1f}% ({opt_pass}/{opt_total})</span>"
        )
        self.total_total_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000; border: none;")
        data_layout.addWidget(self.total_total_label)

        # 구분선 2
        vline2 = QFrame()
        vline2.setFixedSize(2, 60)
        vline2.setStyleSheet("background-color: #CECECE; border: none;")
        data_layout.addWidget(vline2)

        # Spacer 2
        spacer2 = QWidget()
        spacer2.setFixedSize(12, 60)
        spacer2.setStyleSheet("border: none;")
        data_layout.addWidget(spacer2)

        # 종합 평가 점수 - % (통과/전체) 형식
        self.total_score_label = QLabel()
        self.total_score_label.setFixedSize(315, 60)  # 종합 평가 점수
        self.total_score_label.setText(
            f"종합 평가 점수&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 21px; font-weight: 500; color: #000000;'>"
            f"{score:.1f}% ({total_pass}/{total_fields})</span>"
        )
        self.total_score_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 500; color: #000000; border: none;")
        data_layout.addWidget(self.total_score_label)
        data_layout.addStretch()
        main_layout.addWidget(self.total_data_area)

        total_group.setLayout(main_layout)
        return total_group

    def table_cell_clicked(self, row, col):
        """상세 내용 버튼 클릭 시"""
        if col == 8:  # 'Score' column is 7, 'Detail' column is 8. Corrected to 8
            self._show_detail(row)
