# 물리보안 통합플랫폼 검증 소프트웨어
# physical security integrated platform validation software

import os
from api.api_server import Server
import time
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor, QPixmap
from PyQt5.QtCore import Qt, QSettings, QTimer, QThread, pyqtSignal
import sys
import ssl
from datetime import datetime
import json
from core.functions import build_result_json
import requests
import config.CONSTANTS as CONSTANTS
from core.json_checker_new import timeout_field_finder
from core.functions import json_check_, resource_path, json_to_data
from splash_screen import LoadingPopup
import spec.Schema_response as schema_response_module
from http.server import HTTPServer
import warnings
from core.validation_registry import get_validation_rules
from core.utils import remove_api_number_suffix, to_detail_text, redact, clean_trace_directory, format_schema, load_from_trace_file, load_external_constants, setup_external_spec_modules, calculate_percentage, generate_monitor_log_html, format_result_message, get_result_icon_path
from result_page import ResultPageWidget

warnings.filterwarnings('ignore')
result_dir = os.path.join(os.getcwd(), "results")
os.makedirs(result_dir, exist_ok=True)


# 플랫폼 검증을 위한 래퍼 윈도우 (standalone 모드에서 스택 전환 지원)
class PlatformValidationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("통합플랫폼 연동 검증")
        self.resize(1200, 720)

        # 스택 위젯 생성
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 플랫폼 검증 위젯은 나중에 생성 (순환 참조 방지)
        self.validation_widget = None
        self._result_widget = None

    def initialize(self):
        """검증 위젯 초기화 (MyApp 클래스 정의 후 호출)"""
        if self.validation_widget is None:
            self.validation_widget = MyApp(embedded=False)
            self.validation_widget._wrapper_window = self  # 래퍼 참조 전달
            self.stack.addWidget(self.validation_widget)
            self.stack.setCurrentWidget(self.validation_widget)

    def _show_result_page(self):
        """시험 결과 페이지로 전환 (스택 내부)"""
        # 기존 결과 위젯 제거
        if self._result_widget is not None:
            self.stack.removeWidget(self._result_widget)
            self._result_widget.deleteLater()

        # 새로운 결과 위젯 생성
        self._result_widget = ResultPageWidget(self.validation_widget, embedded=True)
        self._result_widget.backRequested.connect(self._on_back_to_validation)

        # 스택에 추가하고 전환
        self.stack.addWidget(self._result_widget)
        self.stack.setCurrentWidget(self._result_widget)

    def _on_back_to_validation(self):
        """뒤로가기: 시험 결과에서 검증 화면으로 복귀"""
        self.stack.setCurrentWidget(self.validation_widget)

    def closeEvent(self, event):
        """래퍼 윈도우 닫기 이벤트 - validation_widget의 정리 작업 호출"""
        print(f"[WRAPPER_CLOSE] PlatformValidationWindow closeEvent 호출됨")

        # ✅ 종료 확인 대화상자
        reply = QMessageBox.question(
            self, '프로그램 종료',
            '정말로 프로그램을 종료하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        print(f"[WRAPPER_CLOSE] 사용자 응답: {'Yes' if reply == QMessageBox.Yes else 'No'}")

        if reply == QMessageBox.Yes:
            # ✅ validation_widget의 정리 작업 호출
            if self.validation_widget is not None:
                print(f"[WRAPPER_CLOSE] validation_widget 정리 시작")
                # 타이머 중지
                if hasattr(self.validation_widget, 'tick_timer') and self.validation_widget.tick_timer.isActive():
                    self.validation_widget.tick_timer.stop()
                    print(f"[WRAPPER_CLOSE] 타이머 중지됨")

                # 서버 스레드 종료
                if hasattr(self.validation_widget, 'server_th') and self.validation_widget.server_th is not None and self.validation_widget.server_th.isRunning():
                    print(f"[WRAPPER_CLOSE] 서버 스레드 종료 중...")
                    try:
                        self.validation_widget.server_th.httpd.shutdown()
                        self.validation_widget.server_th.wait(2000)
                        print(f"[WRAPPER_C1LOSE] 서버 스레드 종료 완료")
                    except Exception as e:
                        print(f"[WARN] 서버 종료 중 오류 (무시): {e}")

                # 일시정지 파일 삭제
                print(f"[WRAPPER_CLOSE] cleanup_paused_file() 호출")
                self.validation_widget.cleanup_paused_file()
                print(f"[WRAPPER_CLOSE] 정리 완료")

            event.accept()
        else:
            event.ignore()


# 통합된 상세 내용 확인 팝업창 클래스
class CombinedDetailDialog(QDialog):
    def __init__(self, api_name, step_buffer, schema_data, webhook_schema=None):
        super().__init__()

        self.setWindowTitle(f"{api_name} 상세 정보")
        self.setMinimumSize(1520, 921)  # 반응형: 최소 크기 설정
        self.resize(1520, 921)  # 초기 크기
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setStyleSheet("background-color: #FFFFFF;")

        # 전체 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(48, 32, 48, 40)  # 좌, 상, 우, 하

        # webhook_schema 저장
        self.webhook_schema = webhook_schema

        # 상단 제목 - 반응형: 높이만 고정, 가로 확장
        title_label = QLabel(f"{api_name} 상세 정보")
        title_label.setMinimumHeight(38)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        title_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 26px; font-weight: 500;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(16)  # 제목 아래 gap

        # 서브 제목 컨테이너 - 반응형: 높이만 고정, 가로 확장
        subtitle_container = QWidget()
        subtitle_container.setObjectName("subtitle_container")
        subtitle_container.setMinimumHeight(47)
        subtitle_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        subtitle_container.setStyleSheet("""
            #subtitle_container {
                border-image: url(assets/image/common/message.png) 0 0 0 0 stretch stretch;
            }
            #subtitle_container QLabel {
                border-image: none;
                background: transparent;
            }
        """)
        subtitle_layout = QHBoxLayout(subtitle_container)
        subtitle_layout.setContentsMargins(14, 12, 48, 12)  # 좌14, 상12, 우48, 하12

        # 체크 아이콘 (고정 크기)
        check_icon = QLabel()
        check_icon.setPixmap(QPixmap(resource_path("assets/image/common/icn_check.png")))
        check_icon.setFixedSize(18, 18)
        subtitle_layout.addWidget(check_icon)

        subtitle_layout.addSpacing(13)  # 아이콘과 텍스트 사이 간격

        # 텍스트
        subtitle_label = QLabel(f"{api_name} API 정보에 대한 상세 내용을 확인합니다.")
        subtitle_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 400;")
        subtitle_layout.addWidget(subtitle_label)
        subtitle_layout.addStretch()
        
        main_layout.addWidget(subtitle_container)
        main_layout.addSpacing(12)  # message.png 아래 gap

        # 3열 콘텐츠 영역 컨테이너 - 반응형: 전체 확장
        content_container = QWidget()
        content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)  # 열 사이 gap

        # 공통 스타일
        title_style = "font-family: 'Noto Sans KR'; font-size: 18px; font-weight: 600;"
        box_style = "border: 1px solid #CECECE; border-radius: 4px; background-color: #FFFFFF; font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 400; padding: 12px;"

        # 1열: 메시지 데이터 - 반응형: 동일 비율 확장
        data_column = QWidget()
        data_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        data_column_layout = QVBoxLayout(data_column)
        data_column_layout.setContentsMargins(0, 0, 0, 0)
        data_column_layout.setSpacing(0)

        data_title = QLabel("메시지 데이터")
        data_title.setMinimumHeight(24)
        data_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        data_title.setStyleSheet(title_style)
        data_column_layout.addWidget(data_title)
        data_column_layout.addSpacing(8)

        self.data_browser = QTextBrowser()
        self.data_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.data_browser.setStyleSheet(box_style)
        self.data_browser.setAcceptRichText(True)
        if step_buffer["data"]:
            data_text = step_buffer["data"]
            self.data_browser.setPlainText(data_text)
        else:
            self.data_browser.setHtml('<span style="color: #CECECE;">아직 수신된 데이터가 없습니다.</span>')
        data_column_layout.addWidget(self.data_browser)

        # 2열: 메시지 규격 - 반응형: 동일 비율 확장
        schema_column = QWidget()
        schema_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        schema_column_layout = QVBoxLayout(schema_column)
        schema_column_layout.setContentsMargins(0, 0, 0, 0)
        schema_column_layout.setSpacing(0)

        schema_title = QLabel("메시지 규격")
        schema_title.setMinimumHeight(24)
        schema_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        schema_title.setStyleSheet(title_style)
        schema_column_layout.addWidget(schema_title)
        schema_column_layout.addSpacing(8)

        self.schema_browser = QTextBrowser()
        self.schema_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.schema_browser.setStyleSheet(box_style)
        self.schema_browser.setAcceptRichText(True)

        # 기본 스키마 + 웹훅 스키마 결합
        schema_text = format_schema(schema_data)
        if self.webhook_schema:
            schema_text += "\n\n=== 웹훅 응답 스키마 (시스템→플랫폼) ===\n"
            schema_text += format_schema(self.webhook_schema)

        self.schema_browser.setPlainText(schema_text)
        schema_column_layout.addWidget(self.schema_browser)

        # 3열: 검증 오류 - 반응형: 동일 비율 확장
        error_column = QWidget()
        error_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        error_column_layout = QVBoxLayout(error_column)
        error_column_layout.setContentsMargins(0, 0, 0, 0)
        error_column_layout.setSpacing(0)

        error_title = QLabel("검증 오류")
        error_title.setMinimumHeight(24)
        error_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        error_title.setStyleSheet(title_style)
        error_column_layout.addWidget(error_title)
        error_column_layout.addSpacing(8)

        self.error_browser = QTextBrowser()
        self.error_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.error_browser.setStyleSheet(box_style)
        self.error_browser.setAcceptRichText(True)
        result = step_buffer["result"]
        error_text = step_buffer["error"] if step_buffer["error"] else ("오류가 없습니다." if result == "PASS" else "")
        error_msg = f"검증 결과: {result}\n\n"
        if result == "FAIL":
            error_msg += error_text
        else:
            error_msg += "오류가 없습니다."
        # HTML 렌더링을 위해 setHtml 사용 (줄바꿈을 <br>로 변환)
        error_msg_html = error_msg.replace('\n', '<br>')
        self.error_browser.setHtml(error_msg_html)
        error_column_layout.addWidget(self.error_browser)

        # 3개 열을 가로로 배치 - 반응형: 동일 비율(stretch=1)
        content_layout.addWidget(data_column, stretch=1)
        content_layout.addWidget(schema_column, stretch=1)
        content_layout.addWidget(error_column, stretch=1)


        main_layout.addWidget(content_container, stretch=1)  # 콘텐츠 영역 확장
        main_layout.addSpacing(24)  # 콘텐츠 영역 아래 gap

        # 확인 버튼 영역 - 반응형: 높이만 고정, 가로 확장
        button_container = QWidget()
        button_container.setFixedHeight(48)
        button_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 확인 버튼 (434x48)
        # ✅ 반응형: 인스턴스 변수로 변경 및 원본 크기 저장
        self.confirm_button = QPushButton("확인")
        self.confirm_button.setFixedSize(434, 48)
        self.original_confirm_btn_size = (434, 48)
        self.original_dialog_size = (1520, 921)
        confirm_enabled = resource_path("assets/image/test_runner/btn_확인_enabled.png").replace("\\", "/")
        confirm_hover = resource_path("assets/image/test_runner/btn_확인_Hover.png").replace("\\", "/")
        self.confirm_button.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{confirm_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                border-image: url('{confirm_hover}') 0 0 0 0 stretch stretch;
            }}
        """)
        self.confirm_button.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(self.confirm_button)
        button_layout.addStretch()

        main_layout.addWidget(button_container)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """다이얼로그 크기 변경 시 확인 버튼 크기 조정"""
        super().resizeEvent(event)

        if hasattr(self, 'confirm_button') and hasattr(self, 'original_confirm_btn_size'):
            width_ratio = max(1.0, self.width() / self.original_dialog_size[0])
            new_btn_width = int(self.original_confirm_btn_size[0] * width_ratio)
            self.confirm_button.setFixedSize(new_btn_width, self.original_confirm_btn_size[1])

# 팝업창 설정하는 함수
class CustomDialog(QDialog):
    def __init__(self, dmsg, dstep):
        super().__init__()

        self.setWindowTitle(dstep)
        self.setGeometry(800, 600, 400, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.tb = QTextBrowser()
        self.tb.setAcceptRichText(True)
        self.tb.append(dmsg)
        self.layout.addWidget(self.tb)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.exec_()


# API 선택 다이얼로그
class APISelectionDialog(QDialog):
    def __init__(self, api_list, selected_indices, parent=None):
        super().__init__(parent)
        self.api_list = api_list
        self.selected_indices = selected_indices.copy()

        self.setWindowTitle("API 선택")
        self.setGeometry(400, 300, 500, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 배경 이미지 설정
        self.setObjectName("platform_main")
        self.setAttribute(Qt.WA_StyledBackground, True)

        bg_path = resource_path("assets/image/common/bg.png").replace("\\", "/")
        print(f"배경 이미지 경로: {bg_path}")

        self.setStyleSheet(f"""
            #platform_main {{
                background-image: url('{bg_path}');
                background-repeat: no-repeat;
                background-position: center;
            }}
            QScrollArea, QScrollArea QWidget, QScrollArea::viewport,
            QGroupBox, QWidget#scroll_widget, QLabel {{
                background: transparent;
            }}
        """)

        # 상단 안내
        info_label = QLabel("시험할 API를 선택하세요 (복수 선택 가능)")
        info_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 10px;")
        layout.addWidget(info_label)

        # 전체 선택/해제 버튼
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("전체 선택")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("전체 해제")
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # API 리스트 (체크박스)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        self.checkboxes = []
        for idx, api_name in enumerate(self.api_list):
            checkbox = QCheckBox(f"{idx + 1}. {api_name}")
            checkbox.setChecked(idx in self.selected_indices)
            self.checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # 하단 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def select_all(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def deselect_all(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)

    def get_selected_indices(self):
        """선택된 API 인덱스 리스트 반환"""
        return [idx for idx, checkbox in enumerate(self.checkboxes) if checkbox.isChecked()]


# 시험 결과 페이지 위젯
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
        main_bg_path = resource_path("assets/image/common/main.png").replace(chr(92), "/")
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

        # 시험 분야 선택 (폰트 효과 추가)
        self.spec_panel_title = QLabel("시험 선택")
        self.spec_panel_title.setFixedSize(424, 24)
        self.spec_panel_title.setStyleSheet("""
            font-size: 20px;
            font-style: normal;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
            letter-spacing: -0.3px;
        """)
        left_layout.addWidget(self.spec_panel_title)
        left_layout.addSpacing(8)

        # 그룹 테이블
        self.group_table_widget = self.create_group_selection_table()
        left_layout.addWidget(self.group_table_widget)
        left_layout.addSpacing(20)

        # 시험 시나리오 테이블
        self.field_group = self.create_test_field_group()
        left_layout.addWidget(self.field_group)

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
                if hasattr(self, 'spec_pass_label'):
                    self.spec_pass_label.setFixedSize(new_label_width, self.original_score_label_size[1])
                if hasattr(self, 'spec_total_label'):
                    self.spec_total_label.setFixedSize(new_label_width, self.original_score_label_size[1])
                if hasattr(self, 'spec_score_label'):
                    self.spec_score_label.setFixedSize(new_label_width, self.original_score_label_size[1])

                # 전체 점수 내부 위젯
                if hasattr(self, 'total_header'):
                    self.total_header.setFixedSize(new_header_width, self.original_score_header_size[1])
                if hasattr(self, 'total_data_area'):
                    self.total_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
                if hasattr(self, 'total_pass_label'):
                    self.total_pass_label.setFixedSize(new_label_width, self.original_score_label_size[1])
                if hasattr(self, 'total_total_label'):
                    self.total_total_label.setFixedSize(new_label_width, self.original_score_label_size[1])
                if hasattr(self, 'total_score_label'):
                    self.total_score_label.setFixedSize(new_label_width, self.original_score_label_size[1])

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
                for i, orig_width in enumerate(self.original_column_widths[:-1]):
                    new_col_width = int(orig_width * width_ratio)
                    self.tableWidget.setColumnWidth(i, new_col_width)
                # 마지막 컬럼은 stretchLastSection으로 자동 확장됨

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
            if hasattr(self, 'spec_pass_label'):
                self.spec_pass_label.setFixedSize(new_label_width, self.original_score_label_size[1])
            if hasattr(self, 'spec_total_label'):
                self.spec_total_label.setFixedSize(new_label_width, self.original_score_label_size[1])
            if hasattr(self, 'spec_score_label'):
                self.spec_score_label.setFixedSize(new_label_width, self.original_score_label_size[1])

            # 전체 점수 내부 위젯
            if hasattr(self, 'total_header'):
                self.total_header.setFixedSize(new_header_width, self.original_score_header_size[1])
            if hasattr(self, 'total_data_area'):
                self.total_data_area.setFixedSize(new_data_width, self.original_score_data_area_size[1])
            if hasattr(self, 'total_pass_label'):
                self.total_pass_label.setFixedSize(new_label_width, self.original_score_label_size[1])
            if hasattr(self, 'total_total_label'):
                self.total_total_label.setFixedSize(new_label_width, self.original_score_label_size[1])
            if hasattr(self, 'total_score_label'):
                self.total_score_label.setFixedSize(new_label_width, self.original_score_label_size[1])

    def create_group_selection_table(self):
        """시험 분야명 테이블"""
        group_box = QWidget()
        group_box.setFixedSize(424, 204)
        group_box.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.group_table = QTableWidget(0, 1)
        self.group_table.setHorizontalHeaderLabels(["시험 분야"])
        self.group_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.group_table.horizontalHeader().setFixedHeight(31)
        self.group_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.group_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.group_table.verticalHeader().setVisible(False)
        self.group_table.verticalHeader().setDefaultSectionSize(39)
        self.group_table.setFixedHeight(204)

        self.group_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                outline: none;
                font-family: "Noto Sans KR";
                font-size: 19px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-weight: 400;
                padding: 8px;
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #F2F8FF;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CECECE;
                color: #1B1B1C;
                text-align: center;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 600;
                letter-spacing: -0.156px;
            }
        """)

        SPEC_CONFIG = load_external_constants(self.CONSTANTS)

        group_items = [
            (g.get("group_name", "미지정 그룹"), g.get("group_id", ""))
            for g in SPEC_CONFIG
        ]
        self.group_table.setRowCount(len(group_items))

        self.group_name_to_index = {}
        self.index_to_group_name = {}

        for idx, (name, gid) in enumerate(group_items):
            item = QTableWidgetItem(name)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.group_table.setItem(idx, 0, item)
            self.group_name_to_index[name] = idx
            self.index_to_group_name[idx] = name

        self.group_table.cellClicked.connect(self.on_group_selected)

        layout.addWidget(self.group_table)
        group_box.setLayout(layout)
        return group_box

    def create_test_field_group(self):
        """시험 시나리오 테이블"""
        group_box = QWidget()
        group_box.setFixedSize(424, 526)
        group_box.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.test_field_table = QTableWidget(0, 1)
        self.test_field_table.setHorizontalHeaderLabels(["시험 시나리오"])
        self.test_field_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_field_table.horizontalHeader().setFixedHeight(31)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)
        self.test_field_table.verticalHeader().setVisible(False)
        self.test_field_table.verticalHeader().setDefaultSectionSize(39)
        self.test_field_table.setFixedHeight(526)

        self.test_field_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: "Noto Sans KR";
                font-size: 19px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                border-right: 0px solid transparent;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-style: normal;
                font-weight: 400;
                letter-spacing: 0.098px;
                text-align: center; 
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
            }
            QTableWidget::item:hover {
                background-color: #E3F2FF;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border-right: 0px solid transparent;
                border-left: 0px solid transparent;
                border-top: 0px solid transparent;
                border-bottom: 1px solid #CECECE;
                color: #1B1B1C;
                text-align: center;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                letter-spacing: -0.156px;
            }
        """)

        # 초기 로드: 현재 그룹의 시나리오 표시
        self.load_initial_scenarios()

        layout.addWidget(self.test_field_table)
        group_box.setLayout(layout)
        return group_box

    def load_initial_scenarios(self):
        SPEC_CONFIG = load_external_constants(self.CONSTANTS)

    def on_group_selected(self, row, col):
        """시험 그룹 선택 시"""
        group_name = self.index_to_group_name.get(row)
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
            self.update_test_field_table(selected_group)

    def update_test_field_table(self, group_data):
        """선택된 그룹의 시나리오 목록 갱신"""
        self.test_field_table.clearContents()

        spec_items = [
            (k, v) for k, v in group_data.items()
            if k not in ['group_name', 'group_id'] and isinstance(v, dict)
        ]
        self.test_field_table.setRowCount(len(spec_items))

        self.spec_id_to_index = {}
        self.index_to_spec_id = {}

        for idx, (spec_id, config) in enumerate(spec_items):
            desc = config.get('test_name', f'시험분야 {idx + 1}')
            desc_with_role = f"{desc} (응답 검증)"
            item = QTableWidgetItem(desc_with_role)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.test_field_table.setItem(idx, 0, item)
            self.spec_id_to_index[spec_id] = idx
            self.index_to_spec_id[idx] = spec_id

    def on_test_field_selected(self, row, col):
        """시나리오 선택 시 해당 결과 표시 (결과 없어도 API 정보 표시)"""

        if row not in self.index_to_spec_id:
            return

        selected_spec_id = self.index_to_spec_id[row]

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
            detail_label.mousePressEvent = lambda event, r=row: self._show_detail(r)

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
                img = self.img_pass
                icon_size = (84, 20)  # tag_성공.png
            elif icon_state == "FAIL":
                img = self.img_fail
                icon_size = (84, 20)  # tag_실패.png
            else:
                img = self.img_none
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
            detail_label.mousePressEvent = lambda event, r=row: self._show_detail(r)

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
        score = calculate_percentage(total_pass, total_fields)

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
            if i == len(header_columns) - 1:  # 마지막 컬럼
                label.setMinimumWidth(width)
                label.setFixedHeight(30)
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            else:
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
        self.tableWidget.horizontalHeader().setStretchLastSection(True)  # 마지막 컬럼 자동 확장

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
            detail_label.mousePressEvent = lambda event, r=row: self._show_detail(r)

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
        score = calculate_percentage(total_pass, total_fields)

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
        if col == 7:
            self._show_detail(row)


class MyApp(QWidget):
    # 시험 결과 표시 요청 시그널
    showResultRequested = pyqtSignal(object)

    def __init__(self, embedded=False, mode=None, spec_id=None):
        # CONSTANTS 사용
        super().__init__()

        self.CONSTANTS = CONSTANTS
        self.current_spec_id = spec_id
        self.current_group_id = None  # ✅ 그룹 ID 저장용

        # ✅ 웹훅 관련 변수 미리 초기화 (load_specs_from_constants 호출 전)
        self.videoWebhookSchema = []
        self.videoWebhookData = []
        self.videoWebhookConstraint = []

        self.load_specs_from_constants()
        self.embedded = embedded
        self.mode = mode
        self.radio_check_flag = "video"
        self.run_status = "진행전"
        self._wrapper_window = None

        # 전체화면 관련 변수 초기화
        self._is_fullscreen = False
        self._saved_geom = None
        self._saved_state = None

        # 로딩 팝업 인스턴스 변수
        self.loading_popup = None

        # 아이콘 경로 (메인 페이지용)
        self.img_pass = resource_path("assets/image/icon/icn_success.png")
        self.img_fail = resource_path("assets/image/icon/icn_fail.png")
        self.img_none = resource_path("assets/image/icon/icn_basic.png")

        self.flag_opt = self.CONSTANTS.flag_opt
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_view)
        self.auth_flag = True
        self.Server = Server
        self.server_th = None  # ✅ 서버 스레드 변수 초기화

        parts = self.auth_info.split(",")
        auth = [parts[0], parts[1] if len(parts) > 1 else ""]
        self.accessInfo = [auth[0], auth[1]]

        # spec_id 초기화
        if spec_id:
            self.current_spec_id = spec_id
            print(f"[PLATFORM] 📌 전달받은 spec_id 사용: {spec_id}")

        # Load specs dynamically from CONSTANTS

        self.initUI()
        self.realtime_flag = False
        self.cnt = 0
        self.current_retry = 0

        # ✅ 분야별 점수 (현재 spec만)
        self.current_retry = 0
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.total_opt_pass_cnt = 0  # 선택 필드 통과 수
        self.total_opt_error_cnt = 0  # 선택 필드 에러 수

        # ✅ 전체 점수 (모든 spec 합산)
        self.global_pass_cnt = 0
        self.global_error_cnt = 0
        self.global_opt_pass_cnt = 0  # 전체 선택 필드 통과 수
        self.global_opt_error_cnt = 0  # 전체 선택 필드 에러 수

        # ✅ 각 spec_id별 테이블 데이터 저장 (시나리오 전환 시 결과 유지)
        self.spec_table_data = {}  # {spec_id: {table_data, step_buffers, scores}}

        self.time_pre = 0
        self.cnt_pre = 0
        self.final_report = ""

        # ✅ 일시정지 및 재개 관련 변수
        self.is_paused = False
        self.last_completed_api_index = -1
        self.paused_valResult_text = ""

        # step_buffers 동적 생성
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS", "raw_data_list": []} for _ in range(len(self.videoMessages))
        ]

        # ✅ 현재 spec에 맞게 누적 카운트 초기화
        api_count = len(self.videoMessages)
        self.step_pass_counts = [0] * api_count
        self.step_error_counts = [0] * api_count
        self.step_opt_pass_counts = [0] * api_count  # API별 선택 필드 통과 수
        self.step_opt_error_counts = [0] * api_count  # API별 선택 필드 에러 수
        self.step_pass_flags = [0] * api_count

        self.get_setting()
        self.first_run = True

        with open(resource_path("spec/rows.json"), "w") as out_file:
            json.dump(None, out_file, ensure_ascii=False)

        self.reference_context = {}

    def load_specs_from_constants(self):

        SPEC_CONFIG = load_external_constants(self.CONSTANTS)

        self.url = getattr(self.CONSTANTS, 'url', None)
        self.auth_type = getattr(self.CONSTANTS, 'auth_type', None)
        self.auth_info = getattr(self.CONSTANTS, 'auth_info', None)

        self.LOADED_SPEC_CONFIG = SPEC_CONFIG

        if not SPEC_CONFIG:
            raise ValueError("CONSTANTS.SPEC_CONFIG가 정의되지 않았습니다!")

        print(f"[PLATFORM DEBUG] SPEC_CONFIG 개수: {len(SPEC_CONFIG)}")
        print(f"[PLATFORM DEBUG] 찾을 spec_id: {self.current_spec_id}")

        config = {}
        for group in SPEC_CONFIG:
            if self.current_spec_id in group:
                config = group[self.current_spec_id]
                break

        if not config:
            raise ValueError(f"spec_id '{self.current_spec_id}'에 대한 설정을 찾을 수 없습니다!")

        self.spec_description = config.get('test_name', 'Unknown Test')
        spec_names = config.get('specs', [])

        # trans_protocol, time_out, num_retries 저장
        self.trans_protocols = config.get('trans_protocol', [])
        self.time_outs = config.get('time_out', [])
        self.num_retries_list = config.get('num_retries', [])

        if len(spec_names) < 3:
            raise ValueError(f"spec_id '{self.current_spec_id}'의 specs 설정이 올바르지 않습니다!")
        print(f"[PLATFORM] 📋 Spec 로딩 시작: {self.spec_description} (ID: {self.current_spec_id})")

        schema_request_module, data_response_module, constraints_response_module = setup_external_spec_modules()
        if schema_request_module is None:
            import spec.Schema_request as schema_request_module
            import spec.Data_response as data_response_module
            import spec.Constraints_response as constraints_response_module

        # 파일 수정 시간 확인
        for module, name in [(schema_request_module, 'Schema_request'),
                              (data_response_module, 'Data_response'),
                              (constraints_response_module, 'Constraints_response')]:
            file_path = module.__file__
            if file_path.endswith('.pyc'):
                file_path = file_path[:-1]  # .pyc -> .py
            if os.path.exists(file_path):
                mtime = os.path.getmtime(file_path)
                from datetime import datetime
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"[PLATFORM SPEC] {name}.py 수정 시간: {mtime_str}")
        # ===== 로그 끝 =====
        print(f"[PLATFORM] 🔧 타입: 요청 검증 + 응답 전송")

        # Request 검증용 데이터 로드
        self.videoInSchema = getattr(schema_request_module, spec_names[0], [])

        # Response 전송용 데이터 로드
        self.videoOutMessage = getattr(data_response_module, spec_names[1], [])
        self.videoMessages = getattr(data_response_module, spec_names[2], [])
        # 표시용 API 이름 (숫자 제거)
        self.videoMessagesDisplay = [remove_api_number_suffix(msg) for msg in self.videoMessages]
        self.videoOutConstraint = getattr(constraints_response_module, self.current_spec_id + "_outConstraints", [])

        # Webhook 관련
        try:
            if len(spec_names) >= 5:
                webhook_schema_name = spec_names[3]
                webhook_data_name = spec_names[4]

                self.videoWebhookSchema = getattr(schema_request_module, webhook_schema_name, [])
                self.videoWebhookData = getattr(data_response_module, webhook_data_name, [])
                self.videoWebhookConstraint = getattr(constraints_response_module,
                                                     self.current_spec_id + "_webhook_inConstraints",
                                                  [])

                print(f"[PLATFORM] 📦 웹훅 스키마 개수: {len(self.videoWebhookSchema)}개 API")
                print(f"[PLATFORM] 📋 웹훅 데이터 개수: {len(self.videoWebhookData)}개")
                print(f"[PLATFORM] 📋 웹훅 constraints 개수: {len(self.videoWebhookConstraint)}개")

                webhook_indices = [i for i, msg in enumerate(self.videoMessages) if "Webhook" in msg]
                if webhook_indices:
                    print(f"[PLATFORM] 🔔 웹훅 API 인덱스: {webhook_indices}")
                else:
                    print(f"[PLATFORM] ⚠️ 웹훅 API가 videoMessages에 없습니다.")
            else:
                print(f"[PLATFORM] ⚠️ 웹훅 스키마 및 데이터가 SPEC_CONFIG에 정의되어 있지 않습니다.")
                self.videoWebhookSchema = []
                self.videoWebhookData = []
                self.videoWebhookConstraint = []
        except Exception as e:
            print(f"[PLATFORM] ⚠️ 웹훅 스키마 및 데이터 로드 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            self.videoWebhookSchema = []
            self.videoWebhookData = []
            self.videoWebhookConstraint = []

        print(f"[PLATFORM] ✅ 로딩 완료: {len(self.videoMessages)}개 API")
        print(f"[PLATFORM] 📋 API 목록: {self.videoMessages}")
        print(f"[PLATFORM] 🔄 프로토콜 설정: {self.trans_protocols}")

        # ✅ spec_config 저장 (URL 생성에 필요)
        self.spec_config = config

    def _push_event(self, api_name, direction, payload):
        """direction: 'REQUEST'|'RESPONSE'|'WEBHOOK'"""
        try:
            if not hasattr(self.Server, "trace") or self.Server.trace is None:
                from collections import defaultdict, deque
                self.Server.trace = defaultdict(lambda: deque(maxlen=500))
            if api_name not in self.Server.trace:
                from collections import deque
                self.Server.trace[api_name] = deque(maxlen=500)
            evt = {
                "time": datetime.utcnow().isoformat() + "Z",
                "api": api_name,
                "dir": direction,
                "data": redact(payload),
            }
            self.Server.trace[api_name].append(evt)
        except Exception:
            pass

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
        score = calculate_percentage(pass_count, total_fields)
        self.tableWidget.setItem(row, 7, QTableWidgetItem(f"{score:.1f}%"))
        self.tableWidget.item(row, 7).setTextAlignment(Qt.AlignCenter)

        # 메시지 저장
        setattr(self, f"step{row + 1}_msg", msg)

    def update_view(self):
        try:
            time_interval = 0

            if self.cnt >= len(self.Server.message):
                print(f"[DEBUG] 모든 API 처리 완료, 타이머 정지")
                self.tick_timer.stop()

                # ✅ 현재 spec 데이터 저장
                self.save_current_spec_data()

                self.sbtn.setEnabled(True)
                self.stop_btn.setDisabled(True)

                # ✅ 완료 메시지 추가
                self.valResult.append("\n" + "=" * 50)
                self.valResult.append("모든 API 검증이 완료되었습니다!")
                self.valResult.append("=" * 50)

                # ✅ 자동 저장
                print(f"[DEBUG] 평가 완료 - 자동 저장 시작")
                try:
                    self.run_status = "완료"
                    result_json = build_result_json(self)
                    url = f"{CONSTANTS.management_url}/api/integration/test-results"
                    response = requests.post(url, json=result_json)
                    print("✅ 시험 결과 전송 상태 코드:", response.status_code)
                    print("📥  시험 결과 전송 응답:", response.text)

                    json_path = os.path.join(result_dir, "request_results.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result_json, f, ensure_ascii=False, indent=2)
                    print(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                    self.append_monitor_log(
                        step_name="결과 파일 저장 완료",
                        details=json_path
                    )
                    print(f"[DEBUG] try 블록 정상 완료")

                except Exception as e:
                    print(f"❌ JSON 저장 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    self.valResult.append(f"\n결과 저장 실패: {str(e)}")
                    print(f"[DEBUG] except 블록 실행됨")

                finally:
                    # ✅ 평가 완료 시 일시정지 파일 정리 (에러 발생 여부와 무관하게 항상 실행)
                    print(f"[DEBUG] ========== finally 블록 진입 ==========")
                    self.cleanup_paused_file()
                    print(f"[DEBUG] ========== finally 블록 종료 ==========")

                return

            # 첫 틱에서는 대기만
            if self.time_pre == 0 or self.cnt != self.cnt_pre:
                self.time_pre = time.time()
                self.cnt_pre = self.cnt
                return
            else:
                time_interval = time.time() - self.time_pre

            # SPEC_CONFIG에서 timeout
            current_timeout = (self.time_outs[self.cnt] / 1000) if self.cnt < len(self.time_outs) else 5.0

            # timeout이 0인 경우
            if current_timeout == 0 or time_interval < current_timeout:
                # 시스템 요청 확인
                api_name = self.Server.message[self.cnt]

                current_validation = {}

                print("++++++++++ 규칙 가져오기 ++++++++++")

                try:
                    current_validation = get_validation_rules(
                        spec_id=self.current_spec_id,
                        api_name=api_name,
                        direction="in",
                    ) or {}
                    if current_validation:
                        print(f"[DEBUG] 현재 API의 검증 규칙 로드 완료: {list(current_validation.keys())}")
                except Exception as e:
                    current_validation = {}
                    print(f"[DEBUG] 현재 API의 검증 규칙 로드 실패: {e}")

                print("++++++++++ 규칙 로드 끝 ++++++++++")

                request_received = False
                expected_count = self.current_retry + 1
                actual_count = 0

                # Server 클래스 변수 request_counter 확인
                if hasattr(self.Server, 'request_counter') and api_name in self.Server.request_counter:
                    actual_count = self.Server.request_counter[api_name]
                    print(f"[DEBUG] API: {api_name}, 예상: {expected_count}, 실제: {actual_count}")
                    if actual_count >= expected_count:
                        request_received = True

                # 요청이 도착하지 않았으면 대기
                if not request_received:
                    if self.current_retry == 0:
                        print(
                            f"[TIMING_DEBUG] ✅ 능동 대기(WAIT): 시스템 요청 대기 중 (API: {api_name}, 예상: {expected_count}회, 실제: {actual_count}회)")
                    return

                request_arrival_time = time.time()
                expected_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                print(f"[TIMING_DEBUG] ✅ 요청 도착 감지! API: {api_name}, 시도: {self.current_retry + 1}/{expected_retries}")

                display_name = self.Server.message_display[self.cnt] if self.cnt < len(self.Server.message_display) else "Unknown"
                message_name = "step " + str(self.cnt + 1) + ": " + display_name

                # SPEC_CONFIG에서 검증 설정 가져오기
                current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                current_protocol = self.trans_protocols[self.cnt] if self.cnt < len(self.trans_protocols) else "basic"

                # API별 누적 데이터 초기화
                if not hasattr(self, 'api_accumulated_data'):
                    self.api_accumulated_data = {}

                api_index = self.cnt
                if self.current_retry == 0 or api_index not in self.api_accumulated_data:
                    self.api_accumulated_data[api_index] = {
                        'data_parts': [],
                        'error_messages': [],
                        'validation_results': [],
                        'total_pass': 0,
                        'total_error': 0,
                        'total_opt_pass': 0,  # 선택 필드 통과 수
                        'total_opt_error': 0,  # 선택 필드 에러 수
                        'raw_data_list': []
                    }

                accumulated = self.api_accumulated_data[api_index]

                retry_attempt = self.current_retry

                combined_error_parts = []
                step_result = "PASS"
                add_pass = 0
                add_err = 0
                add_opt_pass = 0  # 선택 필드 통과 수
                add_opt_error = 0  # 선택 필드 에러 수

                # 실시간 진행률 표시
                if retry_attempt == 0:
                    self.append_monitor_log(
                        step_name=message_name,
                        details=f"총 {current_retries}회 검증 예정"
                    )

                print(
                    f"[PLATFORM] 시스템 요청 수신: {self.Server.message[self.cnt]} (시도 {retry_attempt + 1}/{current_retries})")


                # 테이블에 실시간 진행률 표시
                self.update_table_row_with_retries(self.cnt, "진행중", 0, 0, "검증 진행중...",
                                                   f"시도 {retry_attempt + 1}/{current_retries}", retry_attempt + 1)

                QApplication.processEvents()

                current_data = load_from_trace_file(api_name, "REQUEST") or {}

                if not current_data:
                    print(f"[WARNING] ⚠️ trace 파일에서 요청 데이터를 불러오지 못했습니다!")
                    print(f"[WARNING] API 이름: {api_name}")
                    print(f"[WARNING] Direction: REQUEST")
                else:
                    print(f"[SUCCESS] ✅ trace 파일에서 요청 데이터 로드 완료: {len(str(current_data))} bytes")

                # 1-1. response 데이터 로드
                response_data = load_from_trace_file(api_name, "RESPONSE") or {}

                if not response_data:
                    print(f"[WARNING] ⚠️ trace 파일에서 응답 데이터를 불러오지 못했습니다!")
                    print(f"[WARNING] API 이름: {api_name}")
                    print(f"[WARNING] Direction: RESPONSE")
                else:
                    print(f"[SUCCESS] ✅ trace 파일에서 응답 데이터 로드 완료: {len(str(response_data))} bytes")

                # 2. 맥락 검증용
                if current_validation:

                    for field_path, validation_rule in current_validation.items():
                        validation_type = validation_rule.get("validationType", "")
                        direction = "REQUEST" if "request-field" in validation_type else "RESPONSE"

                        ref_endpoint = validation_rule.get("referenceEndpoint", "")
                        if ref_endpoint:
                            ref_api_name = ref_endpoint.lstrip("/")
                            ref_data = load_from_trace_file(ref_api_name, direction)
                            if ref_data and isinstance(ref_data, dict):
                                self.reference_context[ref_endpoint] = ref_data
                                print(f"[TRACE] {ref_endpoint} {direction}를 trace 파일에서 로드 (from validation rule)")

                        ref_endpoint_max = validation_rule.get("referenceEndpointMax", "")
                        if ref_endpoint_max:
                            ref_api_name_max = ref_endpoint_max.lstrip("/")
                            ref_data_max = load_from_trace_file(ref_api_name_max, direction)
                            if ref_data_max and isinstance(ref_data_max, dict):
                                self.reference_context[ref_endpoint_max] = ref_data_max
                                print(f"[TRACE] {ref_endpoint_max} {direction}를 trace 파일에서 로드 (from validation rule)")

                        ref_endpoint_min = validation_rule.get("referenceEndpointMin", "")
                        if ref_endpoint_min:
                            ref_api_name_min = ref_endpoint_min.lstrip("/")
                            ref_data_min = load_from_trace_file(ref_api_name_min, direction)
                            if ref_data_min and isinstance(ref_data_min, dict):
                                self.reference_context[ref_endpoint_min] = ref_data_min
                                print(f"[TRACE] {ref_endpoint_min} {direction}를 trace 파일에서 로드 (from validation rule)")

                if self.Server.message[self.cnt] in CONSTANTS.none_request_message:
                    # 매 시도마다 데이터 수집
                    tmp_res_auth = json.dumps(current_data, indent=4, ensure_ascii=False)

                    if retry_attempt == 0:
                        accumulated['data_parts'].append(f"{tmp_res_auth}")
                    else:
                        accumulated['data_parts'].append(f"\n{tmp_res_auth}")

                    # 실시간 모니터링 창에 요청 데이터 표시 (API 이름 중복 없이 데이터만)
                    # if retry_attempt == 0:
                    #     self.append_monitor_log(
                    #         step_name="",
                    #         request_json=tmp_res_auth
                    #     )

                    accumulated['raw_data_list'].append(current_data)

                    if (len(current_data) != 0) and current_data != "{}":
                        step_result = "FAIL"
                        add_err = 1
                        combined_error_parts.append(f"[시도 {retry_attempt + 1}/{current_retries}] [None Request] 데이터가 있으면 안 됩니다.")
                    elif (len(current_data) == 0) or current_data == "{}":
                        step_result = "PASS"
                        add_pass = 1

                else:
                    # 매 시도마다 입력 데이터 수집
                    tmp_res_auth = json.dumps(current_data, indent=4, ensure_ascii=False)

                    if retry_attempt == 0:
                        accumulated['data_parts'].append(f"{tmp_res_auth}")
                    else:
                        accumulated['data_parts'].append(f"\n{tmp_res_auth}")

                    accumulated['raw_data_list'].append(current_data)

                    if "DoorControl" in api_name:
                        # 1. 검증 규칙 강제 수정 (혹시 doorList.doorID로 되어있다면 다시 doorID로 원복)
                        if "doorID" in current_validation:
                            current_validation["doorID"]["referenceField"] = "doorID"
                            print(f"[PATCH] 규칙 강제 설정: referenceField = 'doorID'")

                        # 2. 데이터 강제 평탄화 (Flattening)
                        target_key = "/RealtimeDoorStatus"

                        ref_data = self.reference_context.get(target_key, {})
                        
                        # 데이터가 없으면 Trace 파일에서 비상 로드
                        if "doorList" not in ref_data or not ref_data.get("doorList"):
                            try:
                                webhook_data = load_from_trace_file("RealtimeDoorStatus", "WEBHOOK_OUT")
                                if webhook_data and "doorList" in webhook_data:
                                    ref_data = webhook_data
                                    print(f"[PATCH] reference_context에 RealtimeDoorStatus 데이터가 없어 WEBHOOK에서 로드함")
                            except:
                                pass
                        
                        if "doorList" not in ref_data or not ref_data.get("doorList"):
                            try:
                                response_data = load_from_trace_file("RealtimeDoorStatus", "REQUEST")
                                if response_data and "doorList" in response_data:
                                    ref_data = response_data
                                    print(f"[PATCH] reference_context에 RealtimeDoorStatus 데이터가 없어 REQUEST에서 로드함")
                            except:
                                pass
                        
                        extracted_ids = []
                        if "doorList" in ref_data and isinstance(ref_data["doorList"], list):
                            for item in ref_data["doorList"]:
                                if isinstance(item, dict):
                                    val = item.get("doorID") or item.get("doorId")
                                    if val: extracted_ids.append(val)

                        if extracted_ids:
                            ref_data["doorID"] = extracted_ids

                            self.reference_context[target_key] = ref_data
                            print(f"[PATCH] 데이터 평탄화 성공: {extracted_ids}")

                        else:
                            print(f"[PATCH] 경고: doorList는 있지만 내부에 doorID가 없습니다.")                       
                        
                                
                    try:
                        print(f"[DEBUG] json_check_ 호출 시작")

                        val_result, val_text, key_psss_cnt, key_error_cnt, opt_correct, opt_error = json_check_(
                            self.videoInSchema[self.cnt],
                            current_data,
                            self.flag_opt,
                            validation_rules=current_validation,
                            reference_context=self.reference_context
                        )

                        print(
                            f"[DEBUG] json_check_ 성공: result={val_result}, pass={key_psss_cnt}, error={key_error_cnt}")
                    except TypeError as e:
                        print(f"[DEBUG] TypeError 발생, 맥락 검증 제외 하고 다시 시도: {e}")
                        val_result, val_text, key_psss_cnt, key_error_cnt, opt_correct, opt_error = json_check_(
                            self.videoInSchema[self.cnt],
                            current_data,
                            self.flag_opt
                        )

                    except Exception as e:
                        print(f"[DEBUG] json_check_ 기타 에러: {e}")
                        import traceback
                        traceback.print_exc()
                        raise

                    # ✅ 의미 검증: code_value 확인
                    if isinstance(current_data, dict):
                        response_code = str(current_data.get("code", "")).strip()
                        response_message = current_data.get("message", "")
                        code_value = current_data.get("code_value", 200)
                        
                        # code_value 읽은 후 제거 (저장/UI에 포함 안 됨)
                        if "code_value" in current_data:
                            del current_data["code_value"]
                            print(f"[CODE_VALUE] code_value={code_value} 읽고 제거 완료")
                        
                        print(f"[CODE_VALUE] response_code={response_code}, code_value={code_value}")

                        # 케이스 1: code_value=400이고 response_code가 200인 경우
                        # → 잘못된 요청인데 200으로 응답 → 모든 필드 FAIL
                        if code_value == 400 and response_code in ["200", "성공", "Success", ""]:
                            print(f"[PLATFORM] 잘못된 요청인데 200 응답: code_value={code_value}, response_code={response_code}")
                            print(f"[PLATFORM] 모든 필드 FAIL 처리")
                            
                            total_schema_fields = key_psss_cnt + key_error_cnt
                            key_psss_cnt = 0
                            key_error_cnt = total_schema_fields
                            val_result = "FAIL"
                            val_text = f"잘못된 요청 (code_value=400): 모든 필드 자동 FAIL 처리됨"
                            
                            print(f"[PLATFORM] 잘못된 요청 처리 완료: 전체 {total_schema_fields}개 필드 FAIL")
                        
                        # 케이스 2: code_value=400이고 response_code도 400/201/404인 경우
                        # → 의도적 오류 요청, 올바르게 에러 응답 → 모든 필드 PASS
                        elif code_value == 400 and response_code in ["400", "201", "404"]:
                            print(f"[PLATFORM] 에러 응답 감지: code={response_code}, message={response_message}")
                            print(f"[PLATFORM] 동적으로 스키마 필드 자동 PASS 처리 시작")
                            
                            total_schema_fields = key_psss_cnt + key_error_cnt
                            key_psss_cnt = total_schema_fields
                            key_error_cnt = 0
                            val_result = "PASS"
                            val_text = f"에러 응답 (code={response_code}): 모든 필드 자동 PASS 처리됨"
                            
                            print(f"[PLATFORM] 에러 응답 처리 완료: 전체 {total_schema_fields}개 필드 PASS")

                    add_pass += key_psss_cnt
                    add_err += key_error_cnt
                    add_opt_pass += opt_correct  # 선택 필드 통과 수 누적
                    add_opt_error += opt_error  # 선택 필드 에러 수 누적

                    inbound_err_txt = to_detail_text(val_text)
                    if val_result == "FAIL":
                        step_result = "FAIL"
                        combined_error_parts.append(f"[시도 {retry_attempt + 1}/{current_retries}]\n" + inbound_err_txt)

                    # WebHook 프로토콜인 경우
                    if current_protocol == "WebHook":

                        # 웹훅 스레드가 생성될 때까지 짧게 대기
                        wait_count = 0
                        while wait_count < 10:
                            if hasattr(self.Server, 'webhook_thread') and self.Server.webhook_thread:
                                break
                            time.sleep(0.1)
                            wait_count += 1

                        # 웹훅 스레드 완료 대기
                        if hasattr(self.Server, 'webhook_thread') and self.Server.webhook_thread:
                            self.Server.webhook_thread.join(timeout=5)

                        # 실제 웹훅 응답 사용
                        # ✅ 웹훅 응답이 null인 경우에도 검증을 수행하여 실패로 카운트
                        if hasattr(self.Server, 'webhook_response'):
                            # webhook_response가 None이거나 빈 값인 경우 빈 딕셔너리로 처리
                            webhook_response = self.Server.webhook_response if self.Server.webhook_response else {}
                            
                            if webhook_response:
                                tmp_webhook_response = json.dumps(webhook_response, indent=4, ensure_ascii=False)
                                accumulated['data_parts'].append(
                                    f"\n--- Webhook 응답 (시도 {retry_attempt + 1}회차) ---\n{tmp_webhook_response}")
                            else:
                                accumulated['data_parts'].append(f"\n--- Webhook 응답 (시도 {retry_attempt + 1}회차) ---\nnull")
                            
                            if self.cnt < len(self.step_buffers):
                                self.step_buffers[self.cnt]["is_webhook_api"] = True
                            
                            # 웹훅 응답 검증 (null인 경우에도 검증 수행)
                            webhook_resp_val_result, webhook_resp_val_text, webhook_resp_key_psss_cnt, webhook_resp_key_error_cnt, opt_correct, opt_error = json_check_(
                                self.videoWebhookSchema[self.cnt], webhook_response, self.flag_opt
                            )

                            add_pass += webhook_resp_key_psss_cnt
                            add_err += webhook_resp_key_error_cnt
                            add_opt_pass += opt_correct  # 웹훅 선택 필드 통과 수 누적
                            add_opt_error += opt_error  # 웹훅 선택 필드 에러 수 누적

                            webhook_resp_err_txt = to_detail_text(webhook_resp_val_text)
                            if webhook_resp_val_result == "FAIL":
                                step_result = "FAIL"
                                combined_error_parts.append(f"\n--- Webhook 검증 ---\n" + webhook_resp_err_txt)

                            # webhook_response가 None이 아닌 경우에만 reference_context에 저장
                            if webhook_response:
                                webhook_context_key = f"/{api_name}"
                                self.reference_context[webhook_context_key] = webhook_response
                                print(f"[CONTEXT] webhook 응답을 reference_context에 저장: {webhook_context_key}")
                        else:
                            # webhook_response 속성이 없는 경우 (초기화되지 않은 경우)
                            accumulated['data_parts'].append(f"\n--- Webhook 응답 ---\nnull")
                            # 웹훅 스키마가 있는 경우 빈 딕셔너리로 검증 수행
                            webhook_response = {}
                            webhook_resp_val_result, webhook_resp_val_text, webhook_resp_key_psss_cnt, webhook_resp_key_error_cnt, opt_correct, opt_error = json_check_(
                                self.videoWebhookSchema[self.cnt], webhook_response, self.flag_opt
                            )

                            add_pass += webhook_resp_key_psss_cnt
                            add_err += webhook_resp_key_error_cnt
                            add_opt_pass += opt_correct  # 웹훅 선택 필드 통과 수 누적
                            add_opt_error += opt_error  # 웹훅 선택 필드 에러 수 누적

                            webhook_resp_err_txt = to_detail_text(webhook_resp_val_text)
                            if webhook_resp_val_result == "FAIL":
                                step_result = "FAIL"
                                combined_error_parts.append(f"\n--- Webhook 검증 ---\n" + webhook_resp_err_txt)


                    # LongPolling 프로토콜인 경우
                    elif current_protocol == "LongPolling":
                        if retry_attempt == 0:
                            print(f"[LongPolling] 실시간 데이터 수신 대기 중... (API: {api_name})")
                        pass

                # 이번 회차 결과를 누적 데이터에 저장
                accumulated['validation_results'].append(step_result)
                accumulated['error_messages'].extend(combined_error_parts)
                # ✅ 필드 수는 마지막 시도로 덮어쓰기 (누적 X)
                accumulated['total_pass'] = add_pass
                accumulated['total_error'] = add_err
                accumulated['total_opt_pass'] = add_opt_pass  # 선택 필드 통과 수 저장
                accumulated['total_opt_error'] = add_opt_error  # 선택 필드 에러 수 저장

                # ✅ 매 시도마다 테이블 실시간 업데이트 (시스템과 동일)
                self.update_table_row_with_retries(
                    self.cnt, 
                    "진행중" if self.current_retry + 1 < current_retries else step_result,
                    accumulated['total_pass'],
                    accumulated['total_error'],
                    tmp_res_auth if 'tmp_res_auth' in locals() else "검증 진행중...",
                    f"시도 {self.current_retry + 1}/{current_retries}",
                    self.current_retry + 1
                )
                QApplication.processEvents()

                # 플랫폼은 응답 메시지 표시 안 함 (요청만 표시)
                # self.valResult.append(f"\n📤 응답 메시지 송신 [{retry_attempt + 1}/{current_retries}]")
                # if 'tmp_response' in locals():
                #     self.valResult.append(tmp_response)

                # current_retry 증가
                self.current_retry += 1

                # 모든 재시도 완료 여부 확인
                if self.current_retry >= current_retries:
                    # 최종 결과
                    final_result = "FAIL" if "FAIL" in accumulated['validation_results'] else "PASS"

                    # ✅ step_pass_counts 배열에 저장 (배열이 없으면 생성)
                    api_count = len(self.videoMessages)
                    if not hasattr(self, 'step_pass_counts') or len(self.step_pass_counts) != api_count:
                        self.step_pass_counts = [0] * api_count
                        self.step_error_counts = [0] * api_count
                        self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수 배열
                        self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수 배열

                    # 이번 API의 결과 저장
                    self.step_pass_counts[self.cnt] = accumulated['total_pass']
                    self.step_error_counts[self.cnt] = accumulated['total_error']
                    self.step_opt_pass_counts[self.cnt] = accumulated['total_opt_pass']  # 선택 필드 통과 수
                    self.step_opt_error_counts[self.cnt] = accumulated['total_opt_error']  # 선택 필드 에러 수

                    # 스텝 버퍼 저장
                    data_text = "\n".join(accumulated['data_parts']) if accumulated[
                        'data_parts'] else "아직 수신된 데이터가 없습니다."
                    error_text = "\n".join(accumulated['error_messages']) if accumulated[
                        'error_messages'] else "오류가 없습니다."
                    self.step_buffers[self.cnt]["data"] = data_text
                    self.step_buffers[self.cnt]["error"] = error_text
                    self.step_buffers[self.cnt]["result"] = final_result
                    self.step_buffers[self.cnt]["raw_data_list"] = accumulated['raw_data_list']
                    try:
                        api_name = self.Server.message[self.cnt]
                        events = list(self.Server.trace.get(api_name, []))
                        self.step_buffers[self.cnt]["events"] = events
                    except Exception:
                        self.step_buffers[self.cnt]["events"] = []

                    # 아이콘/툴팁 갱신
                    if accumulated['data_parts']:
                        tmp_res_auth = accumulated['data_parts'][0]
                    else:
                        tmp_res_auth = "No data"

                    # 테이블 업데이트
                    self.update_table_row_with_retries(self.cnt, final_result, accumulated['total_pass'],
                                                       accumulated['total_error'], tmp_res_auth, error_text,
                                                       current_retries)

                    # ✅ 전체 누적 점수 업데이트 (모든 spec) - API당 1회만 추가
                    self.global_error_cnt += accumulated['total_error']
                    self.global_pass_cnt += accumulated['total_pass']
                    self.global_opt_pass_cnt += accumulated['total_opt_pass']  # 선택 필드 통과 수
                    self.global_opt_error_cnt += accumulated['total_opt_error']  # 선택 필드 에러 수

                    self.update_score_display()

                    # ✅ 점수 계산은 step_pass_counts 배열의 합으로 (누적 아님!)
                    total_fields = self.total_pass_cnt + self.total_error_cnt
                    score_value = calculate_percentage(self.total_pass_cnt, total_fields)

                    # 모니터링 창에 최종 결과 표시 (HTML 카드 형식)
                    api_name = self.Server.message[self.cnt] if self.cnt < len(self.Server.message) else "Unknown"
                    display_name = self.Server.message_display[self.cnt] if self.cnt < len(self.Server.message_display) else "Unknown"
                    
                    # 최종 결과는 데이터 없이 점수와 상태만 표시 (데이터는 이미 실시간으로 출력됨)
                    self.append_monitor_log(
                        step_name=f"결과: {display_name} ({current_retries}회 검증 완료)",
                        request_json="",  # 데이터는 이미 출력되었으므로 빈 문자열
                        result_status=final_result,
                        score=score_value,
                        details=f"통과: {self.total_pass_cnt}, 오류: {self.total_error_cnt} | 프로토콜: {current_protocol}"
                    )

                    self.cnt += 1
                    self.current_retry = 0

                self.realtime_flag = False

            elif time_interval > current_timeout and self.cnt == self.cnt_pre:
                display_name = self.Server.message_display[self.cnt] if self.cnt < len(self.Server.message_display) else "Unknown"
                message_name = "step " + str(self.cnt + 1) + ": " + display_name

                # message missing인 경우 버퍼 업데이트
                self.step_buffers[self.cnt]["data"] = "아직 수신된 데이터가 없습니다."
                self.step_buffers[self.cnt]["error"] = "Message Missing!"
                self.step_buffers[self.cnt]["result"] = "FAIL"

                tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(self.Server.inSchema[self.cnt])

                # ✅ 웹훅 API인 경우 웹훅 스키마 필드 수도 추가
                current_protocol = self.trans_protocols[self.cnt] if self.cnt < len(self.trans_protocols) else "basic"
                if current_protocol == "WebHook" :
                    webhook_rqd_cnt, webhook_opt_cnt = timeout_field_finder(self.videoWebhookSchema[self.cnt])
                    tmp_fields_rqd_cnt += webhook_rqd_cnt
                    tmp_fields_opt_cnt += webhook_opt_cnt
                    print(f"[PLATFORM] 웹훅 필드 수 추가: 필수={webhook_rqd_cnt}, 선택={webhook_opt_cnt}")
                    # 웹훅 API임을 step_buffers에 표시
                    self.step_buffers[self.cnt]["is_webhook_api"] = True

                self.total_error_cnt += tmp_fields_rqd_cnt
                if tmp_fields_rqd_cnt == 0:
                    self.total_error_cnt += 1
                if self.flag_opt:
                    self.total_error_cnt += tmp_fields_opt_cnt

                self.total_pass_cnt += 0

                # ✅ 전체 점수에도 반영
                self.global_error_cnt += tmp_fields_rqd_cnt
                if tmp_fields_rqd_cnt == 0:
                    self.global_error_cnt += 1
                if self.flag_opt:
                    self.global_error_cnt += tmp_fields_opt_cnt

                # ✅ step_error_counts 배열에도 저장 (타임아웃 경우)
                api_count = len(self.videoMessages)
                if not hasattr(self, 'step_error_counts') or len(self.step_error_counts) != api_count:
                    self.step_error_counts = [0] * api_count
                    self.step_pass_counts = [0] * api_count
                    self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
                    self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수

                # 이미 계산된 값을 배열에 저장
                step_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                opt_err = tmp_fields_opt_cnt if self.flag_opt else 0  # 타임아웃 시 선택 필드 에러
                if self.flag_opt:
                    step_err += tmp_fields_opt_cnt

                self.step_error_counts[self.cnt] = step_err
                self.step_pass_counts[self.cnt] = 0
                self.step_opt_pass_counts[self.cnt] = 0  # 타임아웃 시 선택 필드 통과 0
                self.step_opt_error_counts[self.cnt] = opt_err  # 타임아웃 시 선택 필드 에러

                # 평가 점수 디스플레이 업데이트
                self.update_score_display()

                total_fields = self.total_pass_cnt + self.total_error_cnt
                score_value = calculate_percentage(self.total_pass_cnt, total_fields)

                # 타임아웃 결과를 HTML 카드로 출력
                api_name = self.Server.message[self.cnt] if self.cnt < len(self.Server.message) else "Unknown"
                self.append_monitor_log(
                    step_name=f"Step {self.cnt + 1}: {api_name}",
                    request_json="",
                    score=score_value,
                    details=f"⏱️ Timeout ({current_timeout}초) - Message Missing! | 통과: {self.total_pass_cnt}, 오류: {self.total_error_cnt}"
                )

                # 테이블 업데이트 (Message Missing)
                add_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                if self.flag_opt:
                    add_err += tmp_fields_opt_cnt

                current_retries = self.num_retries_list[self.cnt] if self.cnt < len(self.num_retries_list) else 1
                self.update_table_row_with_retries(self.cnt, "FAIL", 0, add_err, "", "Message Missing!",
                                                   current_retries)

                self.cnt += 1
                self.current_retry = 0
                self.time_pre = time.time()

                if hasattr(self.Server, 'request_counter'):
                    try:
                        del self.Server.request_counter[self.Server.message[self.cnt - 1]]
                    except Exception:
                        pass
                return

            if self.cnt == len(self.Server.message):
                self.tick_timer.stop()
                self.append_monitor_log(
                    step_name="시험 완료",
                    request_json="",
                    details="검증 절차가 완료되었습니다."
                )
                self.cnt = 0

                total_fields = self.total_pass_cnt + self.total_error_cnt
                final_score = calculate_percentage(self.total_pass_cnt, total_fields)

                self.final_report += "전체 점수: " + str(final_score) + "\n"
                self.final_report += "전체 결과: " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                    self.total_error_cnt) + "(누적 오류 필드 수)" + "\n"
                self.final_report += "\n"
                self.final_report += "메시지 검증 세부 결과 \n"
                self.final_report += self.valResult.toPlainText()
                self.sbtn.setEnabled(True)
                self.stop_btn.setDisabled(True)

                # ✅ 현재 spec 데이터 저장
                self.save_current_spec_data()

                # ✅ 자동 저장
                print(f"[DEBUG] 평가 완료 - 자동 저장 시작 (경로2)")
                try:
                    self.run_status = "완료"
                    result_json = build_result_json(self)
                    url = f"{CONSTANTS.management_url}/api/integration/test-results"
                    response = requests.post(url, json=result_json)
                    print("✅ 시험 결과 전송 상태 코드:", response.status_code)
                    print("📥  시험 결과 전송 응답:", response.text)

                    json_path = os.path.join(result_dir, "request_results.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result_json, f, ensure_ascii=False, indent=2)
                    print(f"✅ 시험 결과가 '{json_path}'에 자동 저장되었습니다.")
                    self.append_monitor_log(
                        step_name="결과 파일 저장 완료",
                        details=json_path
                    )
                    print(f"[DEBUG] try 블록 정상 완료 (경로2)")
                except Exception as e:
                    print(f"❌ JSON 저장 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    self.valResult.append(f"\n결과 저장 실패: {str(e)}")
                    print(f"[DEBUG] except 블록 실행됨 (경로2)")
                finally:
                    # ✅ 평가 완료 시 일시정지 파일 정리 (에러 발생 여부와 무관하게 항상 실행)
                    print(f"[DEBUG] ========== finally 블록 진입 (경로2) ==========")
                    self.cleanup_paused_file()
                    print(f"[DEBUG] ========== finally 블록 종료 (경로2) ==========")

        except Exception as err:
            print(f"[ERROR] update_view에서 예외 발생: {err}")
            import traceback
            traceback.print_exc()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error Message: 오류 확인 후 검증 절차를 다시 시작해주세요")
            msg.setInformativeText(str(err))
            msg.setWindowTitle("Error")
            msg.exec_()
            self.tick_timer.stop()
            self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">검증 절차가 중지되었습니다.</div>')
            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)

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
            print(f"[SCORE UPDATE] step_pass_counts: {self.step_pass_counts}, sum: {self.total_pass_cnt}")
            print(f"[SCORE UPDATE] step_error_counts: {self.step_error_counts}, sum: {self.total_error_cnt}")

        # ✅ 선택 필드 통과 수 계산
        if hasattr(self, 'step_opt_pass_counts'):
            self.total_opt_pass_cnt = sum(self.step_opt_pass_counts)
            print(f"[SCORE UPDATE] step_opt_pass_counts: {self.step_opt_pass_counts}, sum: {self.total_opt_pass_cnt}")
        else:
            self.total_opt_pass_cnt = 0

        # ✅ 선택 필드 에러 수 계산
        if hasattr(self, 'step_opt_error_counts'):
            self.total_opt_error_cnt = sum(self.step_opt_error_counts)
            print(f"[SCORE UPDATE] step_opt_error_counts: {self.step_opt_error_counts}, sum: {self.total_opt_error_cnt}")
        else:
            self.total_opt_error_cnt = 0

        # 필수 필드 통과 수 = 전체 통과 - 선택 통과
        spec_required_pass = self.total_pass_cnt - self.total_opt_pass_cnt

        spec_total_fields = self.total_pass_cnt + self.total_error_cnt
        # 선택 필드 전체 수 = 선택 통과 + 선택 에러
        spec_opt_total = self.total_opt_pass_cnt + self.total_opt_error_cnt
        # 필수 필드 전체 수 = 전체 필드 - 선택 필드
        spec_required_total = spec_total_fields - spec_opt_total

        spec_score = calculate_percentage(self.total_pass_cnt, spec_total_fields)

        # 필수/선택 형식으로 표시
        self.spec_pass_label.setText(
            f"통과 필드 수 (필수/선택)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{spec_required_pass}/{self.total_opt_pass_cnt}</span>"
        )
        self.spec_total_label.setText(
            f"전체 필드 수 (필수/선택)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{spec_required_total}/{spec_opt_total}</span>"
        )
        self.spec_score_label.setText(
            f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
            f"{spec_score:.1f}%</span>"
        )

        # ✅ 2️⃣ 전체 점수 (모든 spec 합산)
        if hasattr(self, "total_pass_label") and hasattr(self, "total_total_label") and hasattr(self,
                                                                                                "total_score_label"):
            global_total_fields = self.global_pass_cnt + self.global_error_cnt
            global_score = calculate_percentage(self.global_pass_cnt, global_total_fields)

            # 전체 필수 필드 통과 수 = 전체 통과 - 전체 선택 통과
            global_required_pass = self.global_pass_cnt - self.global_opt_pass_cnt
            # 전체 선택 필드 수 = 전체 선택 통과 + 전체 선택 에러
            global_opt_total = self.global_opt_pass_cnt + self.global_opt_error_cnt
            # 전체 필수 필드 수 = 전체 필드 - 전체 선택 필드
            global_required_total = global_total_fields - global_opt_total

            self.total_pass_label.setText(
                f"통과 필드 수 (필수/선택)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
                f"{global_required_pass}/{self.global_opt_pass_cnt}</span>"
            )
            self.total_total_label.setText(
                f"전체 필드 수 (필수/선택)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
                f"{global_required_total}/{global_opt_total}</span>"
            )
            self.total_score_label.setText(
                f"종합 평가 점수&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"<span style='font-family: \"Noto Sans KR\"; font-size: 25px; font-weight: 500; color: #000000;'>"
                f"{global_score:.1f}%</span>"
            )

    def icon_update_step(self, auth_, result_, text_):
        msg = format_result_message(auth_, result_, text_)
        img = get_result_icon_path(result_, self.img_pass, self.img_fail, self.img_none)
        return msg, img

    def icon_update(self, tmp_res_auth, val_result, val_text):
        msg, img = self.icon_update_step(tmp_res_auth, val_result, val_text)

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

        if self.cnt < self.tableWidget.rowCount():
            self.tableWidget.setCellWidget(self.cnt, 1, icon_widget)
            setattr(self, f"step{self.cnt + 1}_msg", msg)

    def _toggle_placeholder(self):
        """텍스트 유무에 따라 placeholder 표시/숨김"""
        if hasattr(self, 'placeholder_label'):
            if self.valResult.toPlainText().strip():
                self.placeholder_label.hide()
            else:
                self.placeholder_label.show()

    def append_monitor_log(self, step_name, request_json="", result_status="진행중", score=None, details=""):
        """
        Qt 호환성이 보장된 HTML 테이블 구조 로그 출력 함수
        """
        from datetime import datetime

        # 타임스탬프
        timestamp = datetime.now().strftime("%H:%M:%S")

        html_content = generate_monitor_log_html(step_name, timestamp, request_json, score, details)

        self.valResult.append(html_content)

        # 자동 스크롤
        self.valResult.verticalScrollBar().setValue(
            self.valResult.verticalScrollBar().maximum()
        )

    def load_test_info_from_constants(self):
        """CONSTANTS.py에서 시험정보를 로드"""
        return [
            ("기업명", self.CONSTANTS.company_name),
            ("제품명", self.CONSTANTS.product_name),
            ("버전", self.CONSTANTS.version),
            ("시험유형", self.CONSTANTS.test_category),
            ("시험대상", self.CONSTANTS.test_target),
            ("시험범위", self.CONSTANTS.test_range),
            ("사용자 인증 방식", self.auth_type),
            ("시험 접속 정보", self.url)
        ]

    def create_spec_selection_panel(self, parent_layout):
        """시험 선택 패널 - 424px 너비"""
        # 타이틀: 424*24, 폰트 20px Medium
        self.spec_panel_title = QLabel("시험 선택")
        self.spec_panel_title.setFixedSize(424, 24)
        self.spec_panel_title.setStyleSheet("""
            font-size: 20px;
            font-style: normal;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
            letter-spacing: -0.3px;
        """)
        parent_layout.addWidget(self.spec_panel_title)

        # ✅ 반응형: 원본 크기 저장
        self.original_spec_panel_title_size = (424, 24)

        # 타이틀 아래 8px gap
        parent_layout.addSpacing(8)

        # 그룹 테이블 추가 (시험 분야 테이블)
        self.group_table_widget = self.create_group_selection_table()
        parent_layout.addWidget(self.group_table_widget)

        # 20px gap
        parent_layout.addSpacing(20)

        # 시험 시나리오 테이블
        self.field_group = self.create_test_field_group()
        parent_layout.addWidget(self.field_group)

    def on_group_selected(self, row, col):
        group_name = self.index_to_group_name.get(row)
        if not group_name:
            return

        # ===== 외부 로드된 SPEC_CONFIG 사용 (fallback: CONSTANTS 모듈) =====
        SPEC_CONFIG = getattr(self, 'LOADED_SPEC_CONFIG', self.CONSTANTS.SPEC_CONFIG)
        selected_group = next(
            (g for g in SPEC_CONFIG if g.get("group_name") == group_name), None
        )
        # ===== 수정 끝 =====

        if selected_group:
            new_group_id = selected_group.get('group_id')
            old_group_id = getattr(self, 'current_group_id', None)

            print(f"[DEBUG] 🔄 그룹 선택: {old_group_id} → {new_group_id}")

            # ✅ 그룹이 변경되면 current_spec_id 초기화 (다음 시나리오 선택 시 무조건 다시 로드되도록)
            if old_group_id != new_group_id:
                self.current_spec_id = None
                print(f"[DEBUG] ✨ 그룹 변경으로 current_spec_id 초기화")

            # ✅ 그룹 ID 저장
            self.current_group_id = new_group_id
            self.update_test_field_table(selected_group)

    def update_test_field_table(self, group_data):
        """선택된 그룹의 spec_id 목록으로 테이블 갱신"""
        self.test_field_table.clearContents()

        spec_items = [
            (k, v) for k, v in group_data.items()
            if k not in ['group_name', 'group_id'] and isinstance(v, dict)
        ]
        self.test_field_table.setRowCount(len(spec_items))

        self.spec_id_to_index.clear()
        self.index_to_spec_id.clear()

        for idx, (spec_id, config) in enumerate(spec_items):
            desc = config.get('test_name', f'시험분야 {idx + 1}')
            desc_with_role = f"{desc} (요청 검증)"
            item = QTableWidgetItem(desc_with_role)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.test_field_table.setItem(idx, 0, item)
            self.spec_id_to_index[spec_id] = idx
            self.index_to_spec_id[idx] = spec_id

    def create_group_selection_table(self):
        """시험 분야명 테이블 - 424*204, 헤더 31px, 데이터셀 39px"""
        group_box = QWidget()
        group_box.setFixedSize(424, 204)
        group_box.setStyleSheet("background: transparent;")

        # ✅ 반응형: 원본 크기 저장
        self.original_group_table_widget_size = (424, 204)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.group_table = QTableWidget(0, 1)
        self.group_table.setHorizontalHeaderLabels(["시험 분야"])
        self.group_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.group_table.horizontalHeader().setFixedHeight(31)  # 헤더 높이 31px
        self.group_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.group_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.group_table.verticalHeader().setVisible(False)
        self.group_table.setFixedHeight(204)
        self.group_table.verticalHeader().setDefaultSectionSize(39)  # 데이터셀 높이 39px

        self.group_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                outline: none;
                font-family: "Noto Sans KR";
                font-size: 19px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-weight: 400;
                padding: 8px;
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #F2F8FF;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border: none;
                border-bottom: 1px solid #CECECE;
                color: #1B1B1C;
                text-align: center;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-weight: 600;
                letter-spacing: -0.156px;
            }
        """)

        SPEC_CONFIG = load_external_constants(self.CONSTANTS)

        group_items = [
            (g.get("group_name", "미지정 그룹"), g.get("group_id", ""))
            for g in SPEC_CONFIG
        ]
        self.group_table.setRowCount(len(group_items))

        self.group_name_to_index = {}
        self.index_to_group_name = {}

        for idx, (name, gid) in enumerate(group_items):
            display_name = name
            item = QTableWidgetItem(display_name)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.group_table.setItem(idx, 0, item)
            self.group_name_to_index[name] = idx
            self.index_to_group_name[idx] = name

        self.group_table.cellClicked.connect(self.on_group_selected)

        layout.addWidget(self.group_table)
        group_box.setLayout(layout)
        return group_box

    def create_test_field_group(self):
        """시험 시나리오 테이블"""
        group_box = QWidget()
        group_box.setFixedSize(424, 526)
        group_box.setStyleSheet("background: transparent;")

        # ✅ 반응형: 원본 크기 저장
        self.original_field_group_size = (424, 526)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.test_field_table = QTableWidget(0, 1)
        self.test_field_table.setHorizontalHeaderLabels(["시험 시나리오"])
        self.test_field_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_field_table.horizontalHeader().setFixedHeight(31)
        self.test_field_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.test_field_table.cellClicked.connect(self.on_test_field_selected)
        self.test_field_table.verticalHeader().setVisible(False)
        self.test_field_table.verticalHeader().setDefaultSectionSize(39)
        self.test_field_table.setFixedHeight(526)

        self.test_field_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CECECE;
                border-radius: 4px;
                font-family: "Noto Sans KR";
                font-size: 19px;
                color: #1B1B1C;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                border-right: 0px solid transparent;
                color: #1B1B1C;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-style: normal;
                font-weight: 400;
                letter-spacing: 0.098px;
                text-align: center; 
            }
            QTableWidget::item:selected {
                background-color: #E3F2FF;
            }
            QTableWidget::item:hover {
                background-color: #E3F2FF;
            }
            QHeaderView::section {
                background-color: #EDF0F3;
                border-right: 0px solid transparent;
                border-left: 0px solid transparent;
                border-top: 0px solid transparent;
                border-bottom: 1px solid #CECECE;
                color: #1B1B1C;
                text-align: center;
                font-family: 'Noto Sans KR';
                font-size: 18px;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                letter-spacing: -0.156px;
            }
        """)

        # SPEC_CONFIG에서 spec_id와 config 추출
        spec_items = []
        for group_data in self.CONSTANTS.SPEC_CONFIG:
            for key, value in group_data.items():
                if key not in ['group_name', 'group_id'] and isinstance(value, dict):
                    spec_items.append((key, value))

        if spec_items:
            self.test_field_table.setRowCount(len(spec_items))

            self.spec_id_to_index = {}
            self.index_to_spec_id = {}

            for idx, (spec_id, config) in enumerate(spec_items):
                description = config.get('test_name', f'시험 분야 {idx + 1}')
                description_with_role = f"{description} (요청 검증)"
                item = QTableWidgetItem(description_with_role)
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.test_field_table.setItem(idx, 0, item)

                self.spec_id_to_index[spec_id] = idx
                self.index_to_spec_id[idx] = spec_id

            # 현재 로드된 spec_id 선택
            if self.current_spec_id in self.spec_id_to_index:
                current_index = self.spec_id_to_index[self.current_spec_id]
                self.test_field_table.selectRow(current_index)
                self.selected_test_field_row = current_index

        layout.addWidget(self.test_field_table)
        group_box.setLayout(layout)
        return group_box

    def save_current_spec_data(self):
        """현재 spec의 테이블 데이터와 상태를 저장"""
        if not hasattr(self, 'current_spec_id'):
            return

        # 테이블 데이터 저장
        table_data = []
        for row in range(self.tableWidget.rowCount()):
            row_data = {
                'api_name': self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else "",  # API 명은 컬럼 1
                'icon_state': self._get_icon_state(row),  # PASS/FAIL/NONE 상태
                'retry_count': self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else "0",
                'pass_count': self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else "0",
                'total_count': self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else "0",
                'fail_count': self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else "0",
                'score': self.tableWidget.item(row, 7).text() if self.tableWidget.item(row, 7) else "0%",
            }
            table_data.append(row_data)

        # 전체 데이터 저장 (✅ 복합키 사용: group_id_spec_id)
        composite_key = f"{self.current_group_id}_{self.current_spec_id}"

        print(f"[DEBUG] 💾 데이터 저장: {composite_key}")
        print(f"[DEBUG]   - 테이블 행 수: {len(table_data)}")
        print(f"[DEBUG]   - step_pass_counts: {self.step_pass_counts[:] if hasattr(self, 'step_pass_counts') else []}")

        self.spec_table_data[composite_key] = {
            'table_data': table_data,
            'step_buffers': [buf.copy() for buf in self.step_buffers],  # 깊은 복사
            'total_pass_cnt': self.total_pass_cnt,
            'total_error_cnt': self.total_error_cnt,
            'total_opt_pass_cnt': getattr(self, 'total_opt_pass_cnt', 0),  # 선택 필드 통과 수
            'total_opt_error_cnt': getattr(self, 'total_opt_error_cnt', 0),  # 선택 필드 에러 수
            'api_accumulated_data': self.api_accumulated_data.copy() if hasattr(self, 'api_accumulated_data') else {},
            # ✅ step_pass_counts와 step_error_counts 배열도 저장
            'step_pass_counts': self.step_pass_counts[:] if hasattr(self, 'step_pass_counts') else [],
            'step_error_counts': self.step_error_counts[:] if hasattr(self, 'step_error_counts') else [],
            'step_opt_pass_counts': self.step_opt_pass_counts[:] if hasattr(self, 'step_opt_pass_counts') else [],  # 선택 필드 통과 수 배열
            'step_opt_error_counts': self.step_opt_error_counts[:] if hasattr(self, 'step_opt_error_counts') else [],  # 선택 필드 에러 수 배열
        }

        print(f"[DEBUG] ✅ 데이터 저장 완료")

    def _get_icon_state(self, row):
        """테이블 행의 아이콘 상태 반환 (PASS/FAIL/NONE)"""
        icon_widget = self.tableWidget.cellWidget(row, 2)  # 아이콘은 컬럼 2
        if icon_widget:
            icon_label = icon_widget.findChild(QLabel)
            if icon_label:
                tooltip = icon_label.toolTip()
                if "PASS" in tooltip:
                    return "PASS"
                elif "FAIL" in tooltip:
                    return "FAIL"
        return "NONE"

    def restore_spec_data(self, spec_id):
        """저장된 spec 데이터 복원 (✅ 복합키 사용)"""
        composite_key = f"{self.current_group_id}_{spec_id}"
        print(f"[DEBUG] 📂 데이터 복원 시도: {composite_key}")

        if composite_key not in self.spec_table_data:
            print(f"[DEBUG] ❌ {composite_key} 저장된 데이터 없음 - 초기화 필요")
            return False

        saved_data = self.spec_table_data[composite_key]
        print(f"[DEBUG] ✅ 저장된 데이터 발견!")
        print(f"[DEBUG]   - 테이블 행 수: {len(saved_data['table_data'])}")
        print(f"[DEBUG]   - step_pass_counts: {saved_data.get('step_pass_counts', [])}")

        # 테이블 복원
        table_data = saved_data['table_data']
        for row, row_data in enumerate(table_data):
            if row >= self.tableWidget.rowCount():
                break

            # No. (숫자) - 컬럼 0
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # API 이름 - 컬럼 1 (숫자 제거된 이름으로 표시)
            display_name = remove_api_number_suffix(row_data['api_name'])
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            # 아이콘 상태 복원 - 컬럼 2
            icon_state = row_data['icon_state']
            if icon_state == "PASS":
                img = self.img_pass
                icon_size = (84, 20)
            elif icon_state == "FAIL":
                img = self.img_fail
                icon_size = (84, 20)
            else:
                img = self.img_none
                icon_size = (16, 16)

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
                new_item = QTableWidgetItem(row_data[key])
                new_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, new_item)

        # step_buffers 복원
        self.step_buffers = [buf.copy() for buf in saved_data['step_buffers']]

        # 점수 복원
        self.total_pass_cnt = saved_data['total_pass_cnt']
        self.total_error_cnt = saved_data['total_error_cnt']
        self.total_opt_pass_cnt = saved_data.get('total_opt_pass_cnt', 0)  # 선택 필드 통과 수
        self.total_opt_error_cnt = saved_data.get('total_opt_error_cnt', 0)  # 선택 필드 에러 수

        # ✅ step_pass_counts와 step_error_counts 배열 복원
        self.step_pass_counts = saved_data.get('step_pass_counts', [0] * len(self.videoMessages))[:]
        self.step_error_counts = saved_data.get('step_error_counts', [0] * len(self.videoMessages))[:]
        self.step_opt_pass_counts = saved_data.get('step_opt_pass_counts', [0] * len(self.videoMessages))[:]  # 선택 필드 통과
        self.step_opt_error_counts = saved_data.get('step_opt_error_counts', [0] * len(self.videoMessages))[:]  # 선택 필드 에러
        print(f"[RESTORE] step_pass_counts 복원: {self.step_pass_counts}")
        print(f"[RESTORE] step_error_counts 복원: {self.step_error_counts}")
        print(f"[RESTORE] step_opt_pass_counts 복원: {self.step_opt_pass_counts}")
        print(f"[RESTORE] step_opt_error_counts 복원: {self.step_opt_error_counts}")

        # api_accumulated_data 복원
        if 'api_accumulated_data' in saved_data:
            self.api_accumulated_data = saved_data['api_accumulated_data'].copy()

        print(f"[DEBUG] {spec_id} 데이터 복원 완료")
        return True

    def on_test_field_selected(self, row, col):
        """시험 분야 클릭 시 해당 시스템으로 동적 전환"""
        try:
            self.selected_test_field_row = row

            if row in self.index_to_spec_id:
                new_spec_id = self.index_to_spec_id[row]

                if new_spec_id == self.current_spec_id:
                    return

                print(f"[PLATFORM] 🔄 시험 분야 전환: {self.current_spec_id} → {new_spec_id}")
                print(f"[DEBUG] 현재 그룹: {self.current_group_id}")

                # ✅ 1. 현재 spec의 테이블 데이터 저장 (current_spec_id가 None이 아닐 때만)
                if self.current_spec_id is not None:
                    print(f"[DEBUG] 데이터 저장 전 - 테이블 행 수: {self.tableWidget.rowCount()}")
                    self.save_current_spec_data()
                else:
                    print(f"[DEBUG] ⚠️ current_spec_id가 None - 저장 스킵 (그룹 전환 직후)")

                # ✅ 2. spec_id 업데이트
                self.current_spec_id = new_spec_id

                # ✅ 3. spec 데이터 다시 로드
                self.load_specs_from_constants()

                # ✅ 4. 기본 변수 초기화 (테이블 제외)
                self.cnt = 0
                self.current_retry = 0
                self.message_error = []

                # ✅ 5. 테이블 구조 업데이트 (행 수만 조정)
                self.update_result_table_structure(self.videoMessages)

                # ✅ 6. 저장된 데이터가 있으면 복원, 없으면 초기화
                if not self.restore_spec_data(new_spec_id):
                    # 저장된 데이터가 없으면 초기화
                    self.total_pass_cnt = 0
                    self.total_error_cnt = 0
                    self.total_opt_pass_cnt = 0  # 선택 필드 통과 수
                    self.total_opt_error_cnt = 0  # 선택 필드 에러 수

                    # ✅ step_pass_counts와 step_error_counts 배열 초기화
                    api_count = len(self.videoMessages)
                    self.step_pass_counts = [0] * api_count
                    self.step_error_counts = [0] * api_count
                    self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
                    self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수

                    self.step_buffers = [
                        {"data": "", "error": "", "result": "PASS"} for _ in range(len(self.videoMessages))
                    ]
                    # 테이블 초기화
                    print(f"[DEBUG] 💥 저장된 데이터 없음 - 테이블 초기화 시작 ({self.tableWidget.rowCount()}개 행)")
                    for i in range(self.tableWidget.rowCount()):
                        # 아이콘 초기화
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

                        # 카운트 초기화 - ✅ 아이템이 없으면 새로 생성 (9컬럼 구조)
                        for col, value in [(3, "0"), (4, "0"), (5, "0"), (6, "0"), (7, "0%")]:
                            item = self.tableWidget.item(i, col)
                            if item:
                                item.setText(value)
                            else:
                                # ✅ 아이템이 없으면 새로 생성
                                new_item = QTableWidgetItem(value)
                                new_item.setTextAlignment(Qt.AlignCenter)
                                self.tableWidget.setItem(i, col, new_item)
                    print(f"[DEBUG] ✅ 테이블 초기화 완료")

                # trace 초기화 (선택사항 - 필요시)
                # if hasattr(self.Server, 'trace'):
                #     self.Server.trace.clear()

                # Server 객체 초기화
                if hasattr(self, 'Server'):
                    self.Server.cnt = 0
                    self.Server.message = self.videoMessages  # 실제 API 이름 (통신용)
                    self.Server.message_display = self.videoMessagesDisplay  # 표시용 이름
                    self.Server.outMessage = self.videoOutMessage
                    self.Server.outCon = self.videoOutConstraint
                    self.Server.inSchema = self.videoInSchema
                    self.Server.webhookSchema = self.videoWebhookSchema
                    self.Server.webhookData = self.videoWebhookData
                    self.Server.webhookCon = self.videoWebhookConstraint

                # 설정 다시 로드
                self.get_setting()

                # 평가 점수 디스플레이 업데이트
                self.update_score_display()

                # URL 업데이트 (test_name 사용)
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', self.current_spec_id)
                    self.pathUrl = self.url + "/" + test_name
                else:
                    self.pathUrl = self.url + "/" + self.current_spec_id
                self.url_text_box.setText(self.pathUrl)
                self.Server.current_spec_id = self.current_spec_id
                self.Server.num_retries = self.spec_config.get('num_retries', self.current_spec_id)
                self.Server.trans_protocol = self.spec_config.get('trans_protocol', self.current_spec_id)

                # 결과 텍스트 초기화
                self.valResult.clear()
                self.append_monitor_log(
                    step_name=f"플랫폼 전환 완료: {self.spec_description}",
                    details=f"API 목록 ({len(self.videoMessages)}개): {', '.join(self.videoMessagesDisplay)}"
                )

                print(f"[PLATFORM] ✅ 플랫폼 전환 완료: {self.spec_description}, API 수: {len(self.videoMessages)}")
        except Exception as e:
            print(f"시험 분야 선택 처리 실패: {e}")
            import traceback
            traceback.print_exc()

    def update_result_table_structure(self, api_list):
        """테이블 구조만 업데이트 (API 이름 및 행 수만 조정, 결과는 유지)"""
        api_count = len(api_list)
        current_row_count = self.tableWidget.rowCount()

        # 행 수 조정
        if api_count != current_row_count:
            self.tableWidget.setRowCount(api_count)

        # API 이름만 업데이트
        for row, api_name in enumerate(api_list):
            # 표시용 이름 (숫자 제거)
            display_name = remove_api_number_suffix(api_name)
            
            # No. (숫자) - 컬럼 0
            if self.tableWidget.item(row, 0):
                self.tableWidget.item(row, 0).setText(f"{row + 1}")
            else:
                no_item = QTableWidgetItem(f"{row + 1}")
                no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(row, 0, no_item)

            # API 명 - 컬럼 1 (숫자 제거)
            if self.tableWidget.item(row, 1):
                self.tableWidget.item(row, 1).setText(display_name)
            else:
                api_item = QTableWidgetItem(display_name)
                api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(row, 1, api_item)

            # 결과 아이콘이 없으면 추가 - 컬럼 2
            if not self.tableWidget.cellWidget(row, 2):
                icon_widget = QWidget()
                icon_layout = QHBoxLayout()
                icon_layout.setContentsMargins(0, 0, 0, 0)
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
                icon_label.setAlignment(Qt.AlignCenter)
                icon_layout.addWidget(icon_label)
                icon_layout.setAlignment(Qt.AlignCenter)
                icon_widget.setLayout(icon_layout)
                self.tableWidget.setCellWidget(row, 2, icon_widget)

            # 컬럼 3-7 초기화 (검증 횟수, 통과/전체/실패 필드 수, 평가 점수)
            col_values = [
                (3, "0"),  # 검증 횟수
                (4, "0"),  # 통과 필드 수
                (5, "0"),  # 전체 필드 수
                (6, "0"),  # 실패 필드 수
                (7, "0%")  # 평가 점수
            ]
            for col, value in col_values:
                if not self.tableWidget.item(row, col):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(row, col, item)

            # 상세 내용 버튼이 없으면 추가 - 컬럼 8
            if not self.tableWidget.cellWidget(row, 8):
                detail_label = QLabel()
                img_path = resource_path("assets/image/test_runner/btn_상세내용확인.png").replace("\\", "/")
                pixmap = QPixmap(img_path)
                detail_label.setPixmap(pixmap)
                detail_label.setScaledContents(False)
                detail_label.setFixedSize(pixmap.size())
                detail_label.setCursor(Qt.PointingHandCursor)
                detail_label.setAlignment(Qt.AlignCenter)
                detail_label.mousePressEvent = lambda event, r=row: self.show_combined_result(r)

                container = QWidget()
                layout = QHBoxLayout()
                layout.addWidget(detail_label)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                container.setLayout(layout)

                self.tableWidget.setCellWidget(row, 8, container)

            # 행 높이 설정
            self.tableWidget.setRowHeight(row, 40)

    def update_result_table_with_apis(self, api_list):
        """시험 결과 테이블을 새로운 API 목록으로 업데이트"""
        api_count = len(api_list)
        self.tableWidget.setRowCount(api_count)

        for row, api_name in enumerate(api_list):
            # No. (숫자) - 컬럼 0
            no_item = QTableWidgetItem(f"{row + 1}")
            no_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, no_item)

            # API 명 - 컬럼 1
            display_name = remove_api_number_suffix(api_name)
            api_item = QTableWidgetItem(display_name)
            api_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, api_item)

            # 결과 아이콘 초기화 - 컬럼 2
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(84, 20))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            self.tableWidget.setCellWidget(row, 2, icon_widget)

            # 검증 횟수, 통과 필드 수, 전체 필드 수, 실패 필드 수, 평가 점수 - 컬럼 3-7
            for col in range(3, 8):
                item = QTableWidgetItem("0" if col != 7 else "0%")
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, col, item)

            # 상세 내용 버튼 - 컬럼 8
            detail_btn = QPushButton("상세 내용 확인")
            detail_btn.setMaximumHeight(30)
            detail_btn.setMaximumWidth(130)
            detail_btn.clicked.connect(lambda checked, r=row: self.show_combined_result(r))

            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_btn)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)

            self.tableWidget.setCellWidget(row, 8, container)
            self.tableWidget.setRowHeight(row, 40)

    def initUI(self):
        # ✅ 반응형: 최소 크기 설정
        self.setMinimumSize(1680, 1006)

        if not self.embedded:
            self.setWindowTitle('통합플랫폼 연동 검증')

        # 메인 레이아웃
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ✅ 상단 헤더 영역 (반응형 - 배경 늘어남, 로고/타이틀 가운데 고정)
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

        # 타이틀 이미지 (408x36)
        header_title_label = QLabel()
        header_title_pixmap = QPixmap(resource_path("assets/image/test_runner/runner_title.png"))
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
        main_bg_path = resource_path("assets/image/common/main.png").replace(chr(92), "/")
        self.content_bg_label = QLabel(self.content_widget)
        self.content_bg_label.setPixmap(QPixmap(main_bg_path))
        self.content_bg_label.setScaledContents(True)
        self.content_bg_label.lower()  # 맨 뒤로 보내기

        # 배경을 칠할 전용 컨테이너
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

        # 2컬럼 레이아웃
        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(0)

        # 왼쪽 컬럼 - 472*898, padding: 좌우 24px, 상 36px, 하 80px
        self.left_col = QWidget()
        self.left_col.setFixedSize(472, 898)
        self.left_col.setStyleSheet("background: transparent;")
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(24, 36, 24, 80)
        self.left_layout.setSpacing(0)

        # ✅ 반응형: 왼쪽 패널 원본 크기 저장
        self.original_left_col_size = (472, 898)

        # 시험 분야 선택 영역
        self.create_spec_selection_panel(self.left_layout)

        # 오른쪽 컬럼
        self.right_col = QWidget()
        self.right_col.setFixedSize(1112, 898)
        self.right_col.setStyleSheet("background: transparent;")
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(24, 30, 24, 0)
        self.right_layout.setSpacing(0)
        self.right_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 왼쪽 상단 정렬

        # ✅ 반응형: 오른쪽 패널 원본 크기 저장
        self.original_right_col_size = (1112, 898)

        # 시험 API 라벨
        # ✅ 시험 URL 라벨 + 텍스트 박스 (가로 배치)
        self.url_row = QWidget()
        self.url_row.setFixedSize(1064, 36)
        self.original_url_row_size = (1064, 36)
        self.url_row.setStyleSheet("background: transparent;")
        url_row_layout = QHBoxLayout()
        url_row_layout.setContentsMargins(0, 0, 0, 0)
        url_row_layout.setSpacing(8)  # 라벨과 텍스트 박스 사이 8px gap
        url_row_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 왼쪽 정렬

        # 시험 URL 라벨 (96 × 24, 20px Medium)
        result_label = QLabel('시험 URL')
        result_label.setFixedSize(96, 24)
        result_label.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """)
        result_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        url_row_layout.addWidget(result_label)

        # ✅ URL 텍스트 박스 (960 × 36, 내부 좌우 24px padding, 18px Medium)
        self.url_text_box = QLineEdit()
        self.url_text_box.setFixedSize(960, 36)
        self.original_url_text_box_size = (960, 36)
        self.url_text_box.setReadOnly(True)
        self.url_text_box.setPlaceholderText("접속 주소를 입력하세요.")
        self.url_text_box.setStyleSheet("""
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
        """)
        url_row_layout.addWidget(self.url_text_box)

        self.url_row.setLayout(url_row_layout)
        self.right_layout.addWidget(self.url_row)

        # 20px gap
        self.right_layout.addSpacing(20)

        # ========== 시험 API 영역 (1064 × 251) ==========
        self.api_section = QWidget()
        self.api_section.setFixedSize(1064, 251)
        self.api_section.setStyleSheet("background: transparent;")
        self.original_api_section_size = (1064, 251)

        api_section_layout = QVBoxLayout(self.api_section)
        api_section_layout.setContentsMargins(0, 0, 0, 0)
        api_section_layout.setSpacing(8)

        # 시험 API 라벨 (1064 × 24, 20px Medium)
        self.api_label = QLabel('시험 API')
        self.api_label.setFixedSize(1064, 24)
        self.original_api_label_size = (1064, 24)
        self.api_label.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """)
        api_section_layout.addWidget(self.api_label)

        # 시험 API 테이블 (1064 × 219)
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

        # ========== 수신 메시지 실시간 모니터링 영역 (1064 × 157) ==========
        self.monitor_section = QWidget()
        self.monitor_section.setFixedSize(1064, 157)
        self.monitor_section.setStyleSheet("background: transparent;")
        self.original_monitor_section_size = (1064, 157)

        monitor_section_layout = QVBoxLayout(self.monitor_section)
        monitor_section_layout.setContentsMargins(0, 0, 0, 0)
        monitor_section_layout.setSpacing(0)

        # 수신 메시지 실시간 모니터링 라벨 (1064 × 24, 20px Medium)
        self.monitor_label = QLabel("수신 메시지 실시간 모니터링")
        self.monitor_label.setFixedSize(1064, 24)
        self.original_monitor_label_size = (1064, 24)
        self.monitor_label.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """)
        monitor_section_layout.addWidget(self.monitor_label)

        # 8px gap
        monitor_section_layout.addSpacing(8)

        # ✅ QTextBrowser를 담을 컨테이너 생성 (1064 × 125)
        self.text_browser_container = QWidget()
        self.text_browser_container.setFixedSize(1064, 125)
        self.original_text_browser_container_size = (1064, 125)

        self.valResult = QTextBrowser(self.text_browser_container)
        self.valResult.setFixedSize(1064, 125)
        self.original_valResult_size = (1064, 125)
        self.valResult.setStyleSheet("""
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
        """)
        # 텍스트 영역 여백 설정 (좌24, 우12) - 스크롤바는 맨 끝에 위치
        self.valResult.setViewportMargins(24, 0, 12, 0)

        # ✅ 커스텀 placeholder 라벨
        self.placeholder_label = QLabel("모니터링 내용이 표출됩니다", self.text_browser_container)
        self.placeholder_label.setGeometry(24, 16, 1000, 30)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #CECECE;
                font-family: "Noto Sans KR";
                font-size: 20px;
                font-weight: 400;
                background: transparent;
            }
        """)
        self.placeholder_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # ✅ 텍스트 변경 시 placeholder 숨기기
        self.valResult.textChanged.connect(self._toggle_placeholder)

        monitor_section_layout.addWidget(self.text_browser_container)
        self.right_layout.addWidget(self.monitor_section)

        # 초기 상태 설정
        self._toggle_placeholder()

        # 20px gap
        self.right_layout.addSpacing(20)

        self.valmsg = QLabel('시험 점수 요약', self)
        self.valmsg.setFixedSize(1064, 24)
        self.original_valmsg_size = (1064, 24)
        self.valmsg.setStyleSheet("""
            font-size: 20px;
            font-family: "Noto Sans KR";
            font-weight: 500;
            color: #000000;
        """)
        self.right_layout.addWidget(self.valmsg)

        # 6px gap
        self.right_layout.addSpacing(6)

        # 평가 점수 표시
        self.spec_score_group = self.create_spec_score_display_widget()
        self.right_layout.addWidget(self.spec_score_group)
        # 전체 점수 표시
        self.total_score_group = self.create_total_score_display_widget()
        self.right_layout.addWidget(self.total_score_group)

        # 30px gap
        self.right_layout.addSpacing(30)

        # 버튼 그룹 (레이아웃 없이 직접 위치 설정)
        self.buttonGroup = QWidget()
        self.buttonGroup.setFixedSize(1064, 48)
        self.original_buttonGroup_size = (1064, 48)
        self.button_spacing = 16  # 버튼 간격 고정

        # 평가 시작 버튼
        self.sbtn = QPushButton("시험 시작", self.buttonGroup)  # 텍스트 추가, 부모를 buttonGroup으로 설정
        self.original_button_size = (254, 48)  # 버튼 원본 크기 저장
        start_enabled = resource_path("assets/image/test_runner/btn_평가시작_enabled.png").replace("\\", "/")
        start_hover = resource_path("assets/image/test_runner/btn_평가시작_hover.png").replace("\\", "/")
        start_disabled = resource_path("assets/image/test_runner/btn_평가시작_disabled.png").replace("\\", "/")
        self.sbtn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{start_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                border-image: url('{start_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:pressed {{
                border-image: url('{start_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:disabled {{
                border-image: url('{start_disabled}') 0 0 0 0 stretch stretch;
                color: #CECECE;
            }}
        """)
        self.sbtn.clicked.connect(self.sbtn_push)

        # 정지 버튼
        self.stop_btn = QPushButton("일시 정지", self.buttonGroup)  # 텍스트 추가
        stop_enabled = resource_path("assets/image/test_runner/btn_일시정지_enabled.png").replace("\\", "/")
        stop_hover = resource_path("assets/image/test_runner/btn_일시정지_hover.png").replace("\\", "/")
        stop_disabled = resource_path("assets/image/test_runner/btn_일시정지_disabled.png").replace("\\", "/")
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{stop_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }}
            QPushButton:hover {{
                border-image: url('{stop_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:pressed {{
                border-image: url('{stop_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:disabled {{
                border-image: url('{stop_disabled}') 0 0 0 0 stretch stretch;
                color: #CECECE;
            }}
        """)
        self.stop_btn.clicked.connect(self.stop_btn_clicked)
        self.stop_btn.setDisabled(True)

        # 종료 버튼
        self.rbtn = QPushButton("종료", self.buttonGroup)  # 텍스트 추가
        exit_enabled = resource_path("assets/image/test_runner/btn_종료_enabled.png").replace("\\", "/")
        exit_hover = resource_path("assets/image/test_runner/btn_종료_hover.png").replace("\\", "/")
        exit_disabled = resource_path("assets/image/test_runner/btn_종료_disabled.png").replace("\\", "/")
        self.rbtn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{exit_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }}
            QPushButton:hover {{
                border-image: url('{exit_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:pressed {{
                border-image: url('{exit_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:disabled {{
                border-image: url('{exit_disabled}') 0 0 0 0 stretch stretch;
                color: #CECECE;
            }}
        """)
        self.rbtn.clicked.connect(self.exit_btn_clicked)

        # 시험 결과 버튼
        self.result_btn = QPushButton("시험 결과", self.buttonGroup)  # 텍스트 추가
        result_enabled = resource_path("assets/image/test_runner/btn_시험결과_enabled.png").replace("\\", "/")
        result_hover = resource_path("assets/image/test_runner/btn_시험결과_hover.png").replace("\\", "/")
        result_disabled = resource_path("assets/image/test_runner/btn_시험결과_disabled.png").replace("\\", "/")
        self.result_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-image: url('{result_enabled}') 0 0 0 0 stretch stretch;
                padding-left: 20px;
                padding-right: 20px;
                font-family: 'Noto Sans KR';
                font-size: 20px;
                font-weight: 500;
                color: #6B6B6B;
            }}
            QPushButton:hover {{
                border-image: url('{result_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:pressed {{
                border-image: url('{result_hover}') 0 0 0 0 stretch stretch;
            }}
            QPushButton:disabled {{
                border-image: url('{result_disabled}') 0 0 0 0 stretch stretch;
                color: #CECECE;
            }}
        """)
        self.result_btn.clicked.connect(self.show_result_page)

        # 초기 버튼 위치 설정 (레이아웃 없이 직접 배치)
        self._update_button_positions()
        self.right_layout.addWidget(self.buttonGroup)
        self.right_layout.addStretch()  # 남는 공간을 아래로 밀기

        self.left_col.setLayout(self.left_layout)
        self.right_col.setLayout(self.right_layout)

        # 컬럼 레이아웃에 추가
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

        if not self.embedded:
            self.setWindowTitle('물리보안 통합플랫폼 연동 검증 소프트웨어')

        QTimer.singleShot(100, self.select_first_scenario)

        if not self.embedded:
            self.show()

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

        # 파일 로그로 resizeEvent 호출 확인 (PyInstaller 호환)
        try:
            import os
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(base_dir, "resize_debug.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[PLATFORM] width={self.width()}, height={self.height()}\n")
        except:
            pass

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

            width_ratio = max(1.0, current_width / self.original_window_size[0])
            height_ratio = max(1.0, current_height / self.original_window_size[1])
            original_column_height = 898  # 원본 컬럼 높이
            extra_column_height = original_column_height * (height_ratio - 1)

            left_expandable_total = 204 + 526  # 730
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
            if hasattr(self, 'original_score_label_width'):
                new_label_width = int(self.original_score_label_width * width_ratio)
                # 분야별 점수 라벨
                if hasattr(self, 'spec_pass_label'):
                    self.spec_pass_label.setFixedSize(new_label_width, 60)
                if hasattr(self, 'spec_total_label'):
                    self.spec_total_label.setFixedSize(new_label_width, 60)
                if hasattr(self, 'spec_score_label'):
                    self.spec_score_label.setFixedSize(new_label_width, 60)
                # 전체 점수 라벨
                if hasattr(self, 'total_pass_label'):
                    self.total_pass_label.setFixedSize(new_label_width, 60)
                if hasattr(self, 'total_total_label'):
                    self.total_total_label.setFixedSize(new_label_width, 60)
                if hasattr(self, 'total_score_label'):
                    self.total_score_label.setFixedSize(new_label_width, 60)

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

    def select_first_scenario(self):
        """프로그램 시작 시 첫 번째 그룹의 첫 번째 시나리오 자동 선택"""
        try:
            print(f"[DEBUG] 초기 시나리오 자동 선택 시작")

            # 1. 첫 번째 그룹이 있는지 확인
            if self.group_table.rowCount() > 0:
                # 첫 번째 그룹 선택
                self.group_table.selectRow(0)
                print(f"[DEBUG] 첫 번째 그룹 선택: {self.index_to_group_name.get(0)}")

                # 그룹에 해당하는 시나리오 로드
                self.on_group_selected(0, 0)

            # 2. 시나리오 테이블에 첫 번째 항목이 있는지 확인
            if self.test_field_table.rowCount() > 0:
                # 첫 번째 시나리오 선택
                self.test_field_table.selectRow(0)
                first_spec_id = self.index_to_spec_id.get(0)
                print(f"[DEBUG] 첫 번째 시나리오 선택: spec_id={first_spec_id}")
                # URL 생성 (test_name 사용)
                if hasattr(self, 'spec_config'):
                    test_name = self.spec_config.get('test_name', first_spec_id)
                    self.pathUrl = self.url + "/" + test_name
                else:
                    self.pathUrl = self.url + "/" + first_spec_id

                self.Server.current_spec_id = first_spec_id
                self.Server.num_retries = self.spec_config.get('num_retries', first_spec_id)
                self.Server.trans_protocol = self.spec_config.get('trans_protocol', self.current_spec_id)
                # 시나리오 선택 이벤트 수동 트리거 (테이블 업데이트)
                self.on_test_field_selected(0, 0)
            self.url_text_box.setText(self.pathUrl)
            print(f"[DEBUG] 초기 시나리오 자동 선택 완료: {self.spec_description}")

            # 3. UI 업데이트
            QApplication.processEvents()

        except Exception as e:
            print(f"[ERROR] 초기 시나리오 선택 실패: {e}")
            import traceback
            traceback.print_exc()
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
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))
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

    def show_combined_result(self, row):
        """통합 상세 내용 확인"""
        try:
            buf = self.step_buffers[row]
            api_name = self.tableWidget.item(row, 1).text()  # API 명은 컬럼 1

            # 스키마 데이터 가져오기
            try:
                schema_data = self.videoInSchema[row] if row < len(self.videoInSchema) else None
            except:
                schema_data = None

            # 웹훅 검증인 경우에만 웹훅 스키마
            webhook_schema = None
            if row < len(self.trans_protocols):
                current_protocol = self.trans_protocols[row]
                if current_protocol == "WebHook":
                    try:
                        # ✅ row 인덱스 사용 (self.cnt 아님!)
                        webhook_schema = self.videoWebhookSchema[row] if row < len(self.videoWebhookSchema) else None
                        print(f"[DEBUG] 웹훅 스키마 로드: row={row}, schema={'있음' if webhook_schema else '없음'}")
                    except Exception as e:
                        print(f"[ERROR] 웹훅 스키마 로드 실패: {e}")
                        webhook_schema = None
                else:
                    print(f"[DEBUG] 일반 API (프로토콜: {current_protocol})")

            # 통합 팝업창
            dialog = CombinedDetailDialog(api_name, buf, schema_data, webhook_schema)
            dialog.exec_()

        except Exception as e:
            CustomDialog(f"오류:\n{str(e)}", "상세 내용 확인 오류")

    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭"""
        if col == 2:  # 아이콘 컬럼
            msg = getattr(self, f"step{row + 1}_msg", "")
            if msg:
                CustomDialog(msg, self.tableWidget.item(row, 1).text())  # API 명은 컬럼 1

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

        # 점수 레이블들 (500 Medium 20px #000000, 325 × 60)
        # 원본 크기 저장 (반응형 조정용)
        self.original_score_label_width = 325

        self.spec_pass_label = QLabel("통과 필드 수")
        self.spec_pass_label.setFixedSize(325, 60)
        self.spec_pass_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """)
        self.spec_total_label = QLabel("전체 필드 수")
        self.spec_total_label.setFixedSize(325, 60)
        self.spec_total_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """)
        self.spec_score_label = QLabel("종합 평가 점수")
        self.spec_score_label.setFixedSize(325, 60)
        self.spec_score_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
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
        spec_score_layout.setContentsMargins(56, 8, 32, 8)
        spec_score_layout.setSpacing(0)

        # 통과 필드 수 + 구분선 + spacer
        spec_score_layout.addWidget(self.spec_pass_label)
        spec_vline1 = QFrame()
        spec_vline1.setFixedSize(2, 60)
        spec_vline1.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline1)
        spec_spacer1 = QWidget()
        spec_spacer1.setFixedSize(24, 60)
        spec_score_layout.addWidget(spec_spacer1)

        # 전체 필드 수 + 구분선 + spacer
        spec_score_layout.addWidget(self.spec_total_label)
        spec_vline2 = QFrame()
        spec_vline2.setFixedSize(2, 60)
        spec_vline2.setStyleSheet("background-color: #CECECE;")
        spec_score_layout.addWidget(spec_vline2)
        spec_spacer2 = QWidget()
        spec_spacer2.setFixedSize(24, 60)
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

        # 점수 레이블들 (500 Medium 20px #000000, 325 × 60)
        self.total_pass_label = QLabel("통과 필드 수")
        self.total_pass_label.setFixedSize(325, 60)
        self.total_pass_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """)
        self.total_total_label = QLabel("전체 필드 수")
        self.total_total_label.setFixedSize(325, 60)
        self.total_total_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
            font-weight: 500;
        """)
        self.total_score_label = QLabel("종합 평가 점수")
        self.total_score_label.setFixedSize(325, 60)
        self.total_score_label.setStyleSheet("""
            color: #000000;
            font-family: "Noto Sans KR";
            font-size: 20px;
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
        score_layout.setContentsMargins(56, 8, 32, 8)
        score_layout.setSpacing(0)

        # 통과 필드 수 + 구분선 + spacer
        score_layout.addWidget(self.total_pass_label)
        total_vline1 = QFrame()
        total_vline1.setFixedSize(2, 60)
        total_vline1.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline1)
        total_spacer1 = QWidget()
        total_spacer1.setFixedSize(24, 60)
        score_layout.addWidget(total_spacer1)

        # 전체 필드 수 + 구분선 + spacer
        score_layout.addWidget(self.total_total_label)
        total_vline2 = QFrame()
        total_vline2.setFixedSize(2, 60)
        total_vline2.setStyleSheet("background-color: #CECECE;")
        score_layout.addWidget(total_vline2)
        total_spacer2 = QWidget()
        total_spacer2.setFixedSize(24, 60)
        score_layout.addWidget(total_spacer2)

        # 종합 평가 점수
        score_layout.addWidget(self.total_score_label)
        score_layout.addStretch()

        total_layout.addWidget(self.total_data_widget)
        total_group.setLayout(total_layout)

        return total_group

    def run_single_spec_test(self):
        """단일 spec_id에 대한 시험 실행"""
        # ✅ trace 초기화는 sbtn_push()의 신규 시작 모드에서만 수행
        pass

        # ✅ 이전 시험 결과가 global 점수에 포함되어 있으면 제거 (복합키 사용)
        composite_key = f"{self.current_group_id}_{self.current_spec_id}"
        if composite_key in self.spec_table_data:
            prev_data = self.spec_table_data[composite_key]
            prev_pass = prev_data.get('total_pass_cnt', 0)
            prev_error = prev_data.get('total_error_cnt', 0)
            print(f"[SCORE RESET] 기존 {composite_key} 점수 제거: pass={prev_pass}, error={prev_error}")

            # global 점수에서 해당 spec 점수 제거
            self.global_pass_cnt = max(0, self.global_pass_cnt - prev_pass)
            self.global_error_cnt = max(0, self.global_error_cnt - prev_error)

        # ✅ 현재 시험 시나리오(spec)의 점수만 초기화
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.total_opt_pass_cnt = 0  # 선택 필드 통과 수
        self.total_opt_error_cnt = 0  # 선택 필드 에러 수
        # ✅ step_pass_counts, step_error_counts 배열도 초기화
        if hasattr(self, 'step_pass_counts'):
            api_count = len(self.videoMessages)
            self.step_pass_counts = [0] * api_count
            self.step_error_counts = [0] * api_count
            self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
            self.step_opt_error_counts = [0] * api_count  # 선택 필드 에러 수
        # global_pass_cnt, global_error_cnt는 유지 (다른 spec 영향 없음)

        self.cnt = 0
        self.current_retry = 0
        self.init_win()
        self.valResult.append(f"시험 시작: {self.spec_description}")

    def sbtn_push(self):
        try:
            selected_rows = self.test_field_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "알림", "시험 시나리오를 선택하세요.")
                return
            self.save_current_spec_data()

            # ✅ 로딩 팝업 표시
            self.loading_popup = LoadingPopup()
            self.loading_popup.show()
            QApplication.processEvents()  # UI 즉시 업데이트

            selected_spec_ids = [self.index_to_spec_id[r.row()] for r in selected_rows]
            for spec_id in selected_spec_ids:
                self.current_spec_id = spec_id
                self.load_specs_from_constants()
                self.run_single_spec_test()

            # ✅ 일시정지 파일 존재 여부 확인
            paused_file_path = os.path.join(result_dir, "request_results_paused.json")
            resume_mode = os.path.exists(paused_file_path)

            if resume_mode:
                print(f"[DEBUG] ========== 재개 모드: 일시정지 상태 복원 ==========")
                # 재개 모드: 저장된 상태 복원
                if self.load_paused_state():
                    self.is_paused = False  # 재개 시작이므로 paused 플래그 해제
                    print(f"[DEBUG] 재개 모드: {self.last_completed_api_index + 1}번째 API부터 시작")
                else:
                    # 복원 실패 시 신규 시작으로 전환
                    print(f"[WARN] 상태 복원 실패, 신규 시작으로 전환")
                    resume_mode = False

            # ✅ 1. 기존 타이머 정지 (재개/신규 공통)
            if self.tick_timer.isActive():
                print(f"[DEBUG] 기존 타이머 중지")
                self.tick_timer.stop()

            # ✅ 2. 기존 서버 스레드 종료 (재개/신규 공통)
            if self.server_th is not None and self.server_th.isRunning():
                print(f"[DEBUG] 기존 서버 스레드 종료 중...")
                try:
                    self.server_th.httpd.shutdown()
                    self.server_th.wait(2000)  # 최대 2초 대기
                    print(f"[DEBUG] 기존 서버 스레드 종료 완료")
                except Exception as e:
                    print(f"[WARN] 서버 종료 중 오류 (무시): {e}")
                self.server_th = None

            if not resume_mode:
                # ========== 신규 시작 모드: 완전 초기화 ==========
                print(f"[DEBUG] ========== 검증 시작: 완전 초기화 ==========")

                # ✅ 3. trace 디렉토리 초기화
                clean_trace_directory(self.CONSTANTS.trace_path)

                # ✅ 4. 모든 카운터 및 플래그 초기화 (첫 실행처럼)
                self.cnt = 0
                self.cnt_pre = 0
                self.time_pre = 0
                self.current_retry = 0
                self.realtime_flag = False
                self.tmp_msg_append_flag = False

                # ✅ 5. 현재 spec의 점수만 초기화
                self.total_error_cnt = 0
                self.total_pass_cnt = 0

                # ✅ 6. 메시지 및 에러 관련 변수 초기화
                self.message_error = []
                self.final_report = ""

                # ✅ 7. API별 누적 데이터 초기화
                if hasattr(self, 'api_accumulated_data'):
                    self.api_accumulated_data.clear()
                else:
                    self.api_accumulated_data = {}

                # ✅ 8. step별 메시지 초기화
                for i in range(1, 10):
                    setattr(self, f"step{i}_msg", "")

                # ✅ 9. step_buffers 완전 재생성
                api_count = len(self.videoMessages) if self.videoMessages else 9
                self.step_buffers = [
                    {"data": "", "error": "", "result": "PASS", "raw_data_list": []}
                    for _ in range(api_count)
                ]
                print(f"[DEBUG] step_buffers 재생성 완료: {len(self.step_buffers)}개")

                # ✅ 10. 현재 spec에 맞게 누적 카운트 초기화
                self.step_pass_counts = [0] * api_count
                self.step_error_counts = [0] * api_count
                self.step_opt_pass_counts = [0] * api_count  # 선택 필드 통과 수
                print(f"[DEBUG] step_pass_counts, step_error_counts, step_opt_pass_counts 초기화 완료: {api_count}개")

                # ✅ 11. Server 객체 상태 초기화
                if hasattr(self.Server, 'trace'):
                    from collections import defaultdict, deque
                    self.Server.trace = defaultdict(lambda: deque(maxlen=1000))
                if hasattr(self.Server, 'latest_event'):
                    from collections import defaultdict
                    self.Server.latest_event = defaultdict(dict)
                if hasattr(self.Server, 'request_counter'):
                    self.Server.request_counter = {}
                if hasattr(self.Server, 'webhook_thread'):
                    self.Server.webhook_thread = None

                # ✅ 12. 평가 점수 디스플레이 초기화
                self.update_score_display()
            else:
                # ========== 재개 모드: 저장된 상태 사용, 초기화 건너뛰기 ==========
                print(f"[DEBUG] 재개 모드: 초기화 건너뛰기, 저장된 상태 사용")
                # cnt는 last_completed_api_index + 1로 설정
                self.cnt = self.last_completed_api_index + 1
                print(f"[DEBUG] 재개 모드: cnt = {self.cnt}")

                # ✅ 재개 모드에서도 실행 상태 변수는 초기화 필요
                self.current_retry = 0  # 재시도 카운터 초기화 (중요!)
                self.cnt_pre = 0
                self.time_pre = 0
                self.realtime_flag = False
                self.tmp_msg_append_flag = False
                self.message_error = []
                self.final_report = ""
                print(f"[DEBUG] 재개 모드: 실행 상태 변수 초기화 완료")

                # ✅ 미완료 API의 trace 파일 삭제 (완료된 API는 유지)
                trace_dir = os.path.join(result_dir, "trace")
                if os.path.exists(trace_dir):
                    print(f"[DEBUG] 미완료 API trace 파일 삭제 시작 (완료: 0~{self.last_completed_api_index})")
                    for i in range(self.last_completed_api_index + 1, len(self.videoMessages)):
                        api_name = self.videoMessages[i]
                        # ✅ api_server.py와 동일한 방식으로 파일명 변환
                        safe_api = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(api_name))
                        # ✅ 실제 생성되는 파일명 패턴으로 삭제
                        # 주의: api_server.py에서는 step_idx + 1을 사용하므로 여기서도 i + 1 사용
                        trace_patterns = [
                            f"trace_{safe_api}.ndjson",
                            f"trace_{i + 1:02d}_{safe_api}.ndjson"
                        ]
                        for pattern in trace_patterns:
                            trace_file = os.path.join(trace_dir, pattern)
                            if os.path.exists(trace_file):
                                try:
                                    os.remove(trace_file)
                                    print(f"[DEBUG] 삭제: {pattern}")
                                except Exception as e:
                                    print(f"[WARN] trace 파일 삭제 실패: {e}")
                    print(f"[DEBUG] 미완료 API trace 파일 정리 완료")

                # 점수 디스플레이 업데이트 (복원된 점수로)
                self.update_score_display()

                # 모니터링 메시지 복원
                self.valResult.clear()
                if self.paused_valResult_text:
                    self.valResult.setHtml(self.paused_valResult_text)
                    self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 10px;">========== 재개 ==========</div>')
                    self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">마지막 완료 API: {self.last_completed_api_index + 1}번째</div>')
                    self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-bottom: 10px;">{self.last_completed_api_index + 2}번째 API부터 재개합니다.</div>')
                    print(f"[DEBUG] 모니터링 메시지 복원 완료: {len(self.paused_valResult_text)} 문자")

                # ✅ 테이블 데이터 복원 (완료된 API들만)
                print(f"[DEBUG] 테이블 데이터 복원 시작: 0 ~ {self.last_completed_api_index}번째 API")
                for i in range(self.last_completed_api_index + 1):
                    if i < len(self.step_buffers):
                        buffer = self.step_buffers[i]
                        # 실제 데이터가 있는 경우만 테이블 업데이트
                        has_data = (
                            buffer.get('raw_data_list') or
                            buffer.get('data') or
                            buffer.get('error')
                        )
                        if has_data:
                            result = buffer.get('result', 'PASS')
                            data = buffer.get('data', '')
                            error = buffer.get('error', '')
                            pass_count = self.step_pass_counts[i] if i < len(self.step_pass_counts) else 0
                            error_count = self.step_error_counts[i] if i < len(self.step_error_counts) else 0

                            # 부하테스트의 경우 검증 횟수는 raw_data_list 길이
                            retries = len(buffer.get('raw_data_list', [])) if buffer.get('raw_data_list') else 1

                            # 테이블 행 업데이트
                            self.update_table_row_with_retries(
                                i, result, pass_count, error_count, data, error, retries
                            )
                            print(f"[DEBUG] 테이블 복원: API {i+1} - result={result}, pass={pass_count}, error={error_count}, retries={retries}")
                print(f"[DEBUG] 테이블 데이터 복원 완료")

            # ✅ 12. 버튼 상태 변경
            self.sbtn.setDisabled(True)
            self.stop_btn.setEnabled(True)

            # ✅ 12. 버튼 상태 변경
            self.sbtn.setDisabled(True)
            self.stop_btn.setEnabled(True)

            # ✅ 13. JSON 데이터 준비
            json_to_data(self.radio_check_flag)
            timeout = 5
            default_timeout = 5

            # ✅ 15. Server 설정
            print(f"[DEBUG] Server 설정 시작")
            self.Server.message = self.videoMessages  # 실제 API 이름 (통신용)
            self.Server.message_display = self.videoMessagesDisplay  # 표시용 이름
            self.Server.outMessage = self.videoOutMessage
            self.Server.inSchema = self.videoInSchema
            self.Server.outCon = self.videoOutConstraint
            self.Server.webhookData = self.videoWebhookData
            self.Server.webhookCon = self.videoWebhookConstraint
            self.Server.system = "video"
            self.Server.timeout = timeout
            print(f"[DEBUG] Server 설정 완료")

            # ✅ 16. UI 초기화
            print(f"[DEBUG] UI 초기화 시작")
            if not resume_mode:
                # 신규 시작: valResult 클리어
                self.valResult.clear()
            else:
                # 재개 모드: 저장된 모니터링 메시지 복원
                self.valResult.clear()  # 일단 클리어
                if self.paused_valResult_text:
                    self.valResult.setHtml(self.paused_valResult_text)
                    self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 10px;">========== 재개 ==========</div>')
                    self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">마지막 완료 API: {self.last_completed_api_index + 1}번째</div>')
                    self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-bottom: 10px;">{self.last_completed_api_index + 2}번째 API부터 재개합니다.</div>')
                    print(f"[DEBUG] 모니터링 메시지 복원 완료: {len(self.paused_valResult_text)} 문자")
            print(f"[DEBUG] UI 초기화 완료")

            # ✅ 17. 테이블 아이콘 및 데이터 초기화 (신규 시작 시만)
            if not resume_mode:
                print(f"[DEBUG] 테이블 초기화 시작")
                for i in range(self.tableWidget.rowCount()):
                    # 아이콘 초기화
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

                    # 모든 카운트 0으로 초기화 (9컬럼 구조)
                    for col, value in ((3, "0"), (4, "0"), (5, "0"), (6, "0"), (7, "0%")):
                        item = QTableWidgetItem(value)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget.setItem(i, col, item)
                print(f"[DEBUG] 테이블 초기화 완료")
            else:
                print(f"[DEBUG] 재개 모드: 테이블 초기화 건너뛰기 (기존 데이터 유지)")

            # ✅ 18. 인증 설정
            print(f"[DEBUG] 인증 설정 시작")
            print(f"[DEBUG] 사용자 인증 방식 : ", self.CONSTANTS.auth_type)

            if self.r2 == "B":
                self.Server.auth_type = "B"
                self.Server.bearer_credentials[0] = self.accessInfo[0]
                self.Server.bearer_credentials[1] = self.accessInfo[1]
            elif self.r2 == "D":
                self.Server.auth_type = "D"
                self.Server.auth_Info[0] = self.accessInfo[0]
                self.Server.auth_Info[1] = self.accessInfo[1]

            self.Server.transProtocolInput = "LongPolling"
            
            # ✅ 19. 시작 메시지 출력
            self.append_monitor_log(
                step_name="플랫폼 검증 시작",
                details=f"API 개수: {len(self.videoMessages)}개"
            )

            # ✅ 20. 서버 시작
            print(f"[DEBUG] 서버 시작 준비")
            url = self.url.split(":")
            address_port = int(url[-1])
            # ✅ 0.0.0.0으로 바인딩 (모든 네트워크 인터페이스에서 수신)
            address_ip = "0.0.0.0"

            print(f"[DEBUG] 플랫폼 서버 시작: {address_ip}:{address_port} (외부 접근: {self.url})")
            self.server_th = server_th(handler_class=self.Server, address=address_ip, port=address_port)
            self.server_th.start()

            # 서버 준비 완료까지 대기 (첫 실행 시만)
            if self.first_run:
                self.append_monitor_log(
                    step_name="플랫폼 서버 초기화 중..."
                )
                time.sleep(5)
                self.append_monitor_log(
                    step_name="플랫폼 서버 준비 완료"
                )
                self.first_run = False
            else:
                # 두 번째 이후에도 서버 안정화를 위한 짧은 대기
                print("[DEBUG] 서버 재시작 안정화 대기...")
                time.sleep(2)
                self.append_monitor_log(
                    step_name="서버 준비 완료"
                )

            # ✅ 21. 타이머 시작 (모든 초기화 완료 후)
            print(f"[DEBUG] 타이머 시작")
            self.tick_timer.start(1000)
            print(f"[DEBUG] ========== 검증 시작 준비 완료 ==========")

            # ✅ 로딩 팝업 닫기
            if self.loading_popup:
                self.loading_popup.close()
                self.loading_popup = None

        except Exception as e:
            print(f"[ERROR] sbtn_push에서 예외 발생: {e}")
            import traceback
            traceback.print_exc()

            # ✅ 에러 발생 시 로딩 팝업 닫기
            if self.loading_popup:
                self.loading_popup.close()
                self.loading_popup = None

            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)

    def save_paused_state(self):
        """일시정지 시 현재 상태를 JSON 파일로 저장"""
        try:
            from datetime import datetime

            last_completed = -1
            for i, buffer in enumerate(self.step_buffers):
                # ✅ 부하테스트의 경우 모든 retry가 완료되어야 "완료"로 판단
                raw_data_list = buffer.get('raw_data_list', [])
                expected_retries = self.num_retries_list[i] if i < len(self.num_retries_list) else 1

                # 실제 완료된 retry 수가 예상 retry 수와 같거나 크면 완료
                if len(raw_data_list) >= expected_retries:
                    last_completed = i
                # timeout 등으로 데이터 없이 FAIL 처리된 경우도 완료로 간주
                elif buffer.get('result') == 'FAIL' and (buffer.get('data') or buffer.get('error')):
                    has_timeout_error = 'Message Missing' in str(buffer.get('error', ''))
                    if has_timeout_error:
                        last_completed = i

            self.last_completed_api_index = last_completed

            # 저장할 상태 데이터 구성
            paused_state = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_completed_api_index": self.last_completed_api_index,
                "step_buffers": self.step_buffers,
                "step_pass_counts": getattr(self, 'step_pass_counts', [0] * len(self.videoMessages)),
                "step_error_counts": getattr(self, 'step_error_counts', [0] * len(self.videoMessages)),
                "step_opt_pass_counts": getattr(self, 'step_opt_pass_counts', [0] * len(self.videoMessages)),  # 선택 필드 통과
                "step_opt_error_counts": getattr(self, 'step_opt_error_counts', [0] * len(self.videoMessages)),  # 선택 필드 에러
                "total_pass_cnt": self.total_pass_cnt,
                "total_error_cnt": self.total_error_cnt,
                "total_opt_pass_cnt": getattr(self, 'total_opt_pass_cnt', 0),  # 선택 필드 통과 수
                "total_opt_error_cnt": getattr(self, 'total_opt_error_cnt', 0),  # 선택 필드 에러 수
                "valResult_text": self.valResult.toHtml(),
                "current_spec_id": self.current_spec_id,
                "global_pass_cnt": self.global_pass_cnt,
                "global_error_cnt": self.global_error_cnt,
                "global_opt_pass_cnt": getattr(self, 'global_opt_pass_cnt', 0),  # 전체 선택 필드 통과 수
                "global_opt_error_cnt": getattr(self, 'global_opt_error_cnt', 0)  # 전체 선택 필드 에러 수
            }

            # JSON 파일로 저장
            paused_file_path = os.path.join(result_dir, "request_results_paused.json")
            with open(paused_file_path, "w", encoding="utf-8") as f:
                json.dump(paused_state, f, ensure_ascii=False, indent=2)

            print(f"✅ 일시정지 상태 저장 완료: {paused_file_path}")
            print(f"   마지막 완료 API 인덱스: {last_completed}")

            # 모니터링 창에 로그 추가
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\'; margin-top: 10px;">💾 재개 정보 저장 완료: {paused_file_path}</div>')
            self.valResult.append(f'<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">   (마지막 완료 API: {last_completed + 1}번째, 다음 재시작 시 {last_completed + 2}번째 API부터 이어서 실행)</div>')

        except Exception as e:
            print(f"❌ 일시정지 상태 저장 실패: {e}")
            import traceback
            traceback.print_exc()
            self.valResult.append(f'<div style="font-size: 18px; color: #ef4444; font-family: \'Noto Sans KR\'; margin-top: 10px;">재개 정보 저장 실패: {str(e)}</div>')

    def load_paused_state(self):
        """일시정지된 상태를 JSON 파일에서 복원"""
        try:
            paused_file_path = os.path.join(result_dir, "request_results_paused.json")

            if not os.path.exists(paused_file_path):
                print("[INFO] 일시정지 파일이 존재하지 않습니다.")
                return False

            with open(paused_file_path, "r", encoding="utf-8") as f:
                paused_state = json.load(f)

            # 상태 복원
            self.last_completed_api_index = paused_state.get("last_completed_api_index", -1)
            self.step_buffers = paused_state.get("step_buffers", [])
            self.step_pass_counts = paused_state.get("step_pass_counts", [0] * len(self.videoMessages))
            self.step_error_counts = paused_state.get("step_error_counts", [0] * len(self.videoMessages))
            self.step_opt_pass_counts = paused_state.get("step_opt_pass_counts", [0] * len(self.videoMessages))  # 선택 필드 통과
            self.step_opt_error_counts = paused_state.get("step_opt_error_counts", [0] * len(self.videoMessages))  # 선택 필드 에러
            self.total_pass_cnt = paused_state.get("total_pass_cnt", 0)
            self.total_error_cnt = paused_state.get("total_error_cnt", 0)
            self.total_opt_pass_cnt = paused_state.get("total_opt_pass_cnt", 0)  # 선택 필드 통과 수
            self.total_opt_error_cnt = paused_state.get("total_opt_error_cnt", 0)  # 선택 필드 에러 수
            self.paused_valResult_text = paused_state.get("valResult_text", "")
            self.global_pass_cnt = paused_state.get("global_pass_cnt", 0)
            self.global_opt_pass_cnt = paused_state.get("global_opt_pass_cnt", 0)  # 전체 선택 필드 통과 수
            self.global_opt_error_cnt = paused_state.get("global_opt_error_cnt", 0)  # 전체 선택 필드 에러 수
            self.global_error_cnt = paused_state.get("global_error_cnt", 0)

            print(f"✅ 일시정지 상태 복원 완료")
            print(f"   타임스탬프: {paused_state.get('timestamp')}")
            print(f"   마지막 완료 API 인덱스: {self.last_completed_api_index}")
            print(f"   복원된 점수: PASS={self.total_pass_cnt}, FAIL={self.total_error_cnt}")

            return True

        except Exception as e:
            print(f"❌ 일시정지 상태 복원 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup_paused_file(self):
        """평가 완료 후 일시정지 파일 삭제 및 상태 초기화"""
        try:
            paused_file_path = os.path.join(result_dir, "request_results_paused.json")
            print(f"[CLEANUP] cleanup_paused_file() 호출됨")
            print(f"[CLEANUP] 파일 경로: {paused_file_path}")
            print(f"[CLEANUP] 파일 존재 여부: {os.path.exists(paused_file_path)}")

            if os.path.exists(paused_file_path):
                os.remove(paused_file_path)
                print("✅ 일시정지 중간 파일 삭제 완료")
            else:
                print("[CLEANUP] 일시정지 파일이 존재하지 않음 (일시정지하지 않았거나 이미 삭제됨)")

            # 일시정지 상태 초기화
            self.is_paused = False
            self.last_completed_api_index = -1
            self.paused_valResult_text = ""

        except Exception as e:
            print(f"❌ 일시정지 파일 정리 실패: {e}")

    def stop_btn_clicked(self):
        # ✅ 타이머 중지
        if self.tick_timer.isActive():
            self.tick_timer.stop()
            print(f"[DEBUG] 타이머 중지됨")

        # ✅ 서버 스레드 종료
        if self.server_th is not None and self.server_th.isRunning():
            print(f"[DEBUG] 서버 스레드 종료 시작...")
            try:
                self.server_th.httpd.shutdown()
                self.server_th.wait(2000)  # 최대 2초 대기
                print(f"[DEBUG] 서버 스레드 종료 완료")
            except Exception as e:
                print(f"[WARN] 서버 종료 중 오류 (무시): {e}")
            self.server_th = None

        self.valResult.append('<div style="font-size: 18px; color: #6b7280; font-family: \'Noto Sans KR\';">검증 절차가 중지되었습니다.</div>')
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)
        self.save_current_spec_data()

        # ✅ 일시정지 상태 저장
        self.is_paused = True
        self.save_paused_state()

        try:
            self.run_status = "진행중"
            result_json = build_result_json(self)
            url = f"{CONSTANTS.management_url}/api/integration/test-results"
            response = requests.post(url, json=result_json)
            print("✅ 시험 결과 전송 상태 코드:", response.status_code)
            print("📥  시험 결과 전송 응답:", response.text)
            json_path = os.path.join(result_dir, "request_results.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result_json, f, ensure_ascii=False, indent=2)
            print(f"✅ 진행 중 결과가 '{json_path}'에 저장되었습니다.")
            self.append_monitor_log(
                step_name="진행 상황 저장 완료",
                details=f"{json_path} (일시정지 시점까지의 결과가 저장되었습니다)"
            )
        except Exception as e:
            print(f"❌ JSON 저장 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            self.valResult.append(f"\n결과 저장 실패: {str(e)}")

    def init_win(self):
        """기본 초기화 (sbtn_push에서 이미 대부분 처리되므로 최소화)"""
        # 이 함수는 레거시 호환성을 위해 유지되지만, 실제 초기화는 sbtn_push에서 수행
        pass

    def show_result_page(self):
        """시험 결과 페이지 표시"""
        if self.embedded:
            self.showResultRequested.emit(self)
        else:
            if self._wrapper_window is not None:
                self._wrapper_window._show_result_page()
            else:
                if hasattr(self, 'result_window') and self.result_window is not None:
                    self.result_window.close()
                self.result_window = ResultPageWidget(self, embedded=False)
                self.result_window.show()

    def toggle_fullscreen(self):
        """전체화면 전환"""
        try:
            if not self._is_fullscreen:
                self._saved_geom = self.saveGeometry()
                self._saved_state = self.windowState()

                flags = (Qt.Window | Qt.WindowTitleHint |
                         Qt.WindowMinimizeButtonHint |
                         Qt.WindowMaximizeButtonHint |
                         Qt.WindowCloseButtonHint)
                self.setWindowFlags(flags)
                self.show()
                self.showMaximized()
                self._is_fullscreen = True
                if hasattr(self, 'fullscreen_btn'):
                    self.fullscreen_btn.setText("전체화면 해제")
            else:
                self.setWindowFlags(Qt.Window)
                self.show()
                if self._saved_geom:
                    self.restoreGeometry(self._saved_geom)
                self.showNormal()
                self._is_fullscreen = False
                if hasattr(self, 'fullscreen_btn'):
                    self.fullscreen_btn.setText("전체화면")
        except Exception as e:
            print(f"전체화면 전환 오류: {e}")

    def exit_btn_clicked(self):
        reply = QMessageBox.question(self, '프로그램 종료',
                                     '정말로 프로그램을 종료하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            result_payload = self.build_result_payload()

            # ✅ 종료 시 일시정지 파일 삭제
            self.cleanup_paused_file()

            QApplication.quit()

    def get_setting(self):
        self.setting_variables = QSettings('My App', 'Variable')
        self.Server.system = "video"

        # 기본 시스템 설정
        self.message = self.videoMessages
        self.outMessage = self.videoOutMessage
        self.inSchema = self.videoInSchema
        self.outCon = self.videoOutConstraint

        # 이 부분 수정해야함
        try:
            webhook_schema_name = f"{self.current_spec_id}_webhook_inSchema"
            self.webhookSchema = getattr(schema_response_module, webhook_schema_name, [])
        except Exception as e:
            print(f"Error loading webhook schema: {e}")
            self.webhookSchema = []

        self.r2 = self.auth_type
        if self.r2 == "Digest Auth":
            self.r2 = "D"
        elif self.r2 == "Bearer Token":
            self.r2 = "B"
        else:
            self.r2 = "None"

        # ✅ URL 업데이트 (test_name 사용) - spec_config가 로드된 후 실행
        if hasattr(self, 'spec_config') and hasattr(self, 'url_text_box'):
            test_name = self.spec_config.get('test_name', self.current_spec_id)
            self.pathUrl = self.url + "/" + test_name
            self.url_text_box.setText(self.pathUrl)
            print(f"[URL] 시험 URL 업데이트: {self.pathUrl}")

    def closeEvent(self, event):
        """창 닫기 이벤트 - 서버 스레드 정리"""
        # ✅ 타이머 중지
        if hasattr(self, 'tick_timer') and self.tick_timer.isActive():
            self.tick_timer.stop()

        # ✅ 서버 스레드 종료
        if hasattr(self, 'server_th') and self.server_th is not None and self.server_th.isRunning():
            try:
                self.server_th.httpd.shutdown()
                self.server_th.wait(2000)  # 최대 2초 대기
            except Exception as e:
                print(f"[WARN] 서버 종료 중 오류 (무시): {e}")

        event.accept()

    def build_result_payload(self):
        """최종 결과를 dict로 반환"""
        total_fields = self.total_pass_cnt + self.total_error_cnt
        score = calculate_percentage(self.total_pass_cnt, total_fields)
        return {
            "score": score,
            "pass_count": self.total_pass_cnt,
            "error_count": self.total_error_cnt,
            "details": self.final_report if hasattr(self, "final_report") else ""
        }


class server_th(QThread):
    def __init__(self, handler_class=None, address='127.0.0.1', port=8008):
        super().__init__()
        self.handler_class = handler_class
        self.address_ip = address
        self.address_port = port
        self.server_address = (self.address_ip, self.address_port)
        self.httpd = HTTPServer(self.server_address, self.handler_class)

        certificate_private = resource_path('config/key0627/server.crt')
        certificate_key = resource_path('config/key0627/server.key')
        try:
            self.httpd.socket = ssl.wrap_socket(self.httpd.socket, certfile=certificate_private,
                                                keyfile=certificate_key, server_side=True)
        except Exception as e:
            print(e)

        print('Starting on ', self.server_address)

    def run(self):
        self.httpd.serve_forever()


class json_data(QThread):
    json_update_data = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        import time
        while True:
            with open(resource_path("spec/rows.json"), "r", encoding="UTF-8") as out_file:
                data = json.load(out_file)
            if data is not None:
                with open(resource_path("spec/rows.json"), "w", encoding="UTF-8") as out_file:
                    json.dump(None, out_file, ensure_ascii=False)
                self.json_update_data.emit(data)
            time.sleep(0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))

    ex = PlatformValidationWindow()
    ex.initialize()
    ex.show()
    sys.exit(app.exec())