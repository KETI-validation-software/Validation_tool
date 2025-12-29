from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem,
    QStackedWidget, QRadioButton, QFrame, QApplication, QSizePolicy, QGraphicsDropShadowEffect,
    QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QFont, QPainter, QPen, QResizeEvent
import importlib
import re
from core.functions import resource_path
from network_scanner import NetworkScanWorker, ARPScanWorker
from form_validator import FormValidator, ClickableLabel, ClickableCheckboxRowWidget
import config.CONSTANTS as CONSTANTS
from ui.splash_screen import LoadingPopup

# 분리된 섹션 임포트
from ui.sections import (
    BasicInfoPanel,
    AuthSection,
    TestFieldSection,
    TestFieldTableWidget,
    TestApiSection,
    ConnectionSection
)

# 분리된 페이지 임포트
from ui.pages import create_test_info_page, create_test_config_page


class TestInfoWorker(QThread):
    """시험 정보를 백그라운드에서 불러오는 워커 스레드"""
    finished = pyqtSignal(object)  # 성공 시 test_data 전달
    error = pyqtSignal(str)  # 실패 시 에러 메시지 전달

    def __init__(self, form_validator, ip_address):
        super().__init__()
        self.form_validator = form_validator
        self.ip_address = ip_address

    def run(self):
        try:
            # API 호출만 백그라운드에서 실행 (UI 작업은 메인 스레드에서)
            test_data = self.form_validator.fetch_test_info_by_ip(self.ip_address)
            self.finished.emit(test_data)
        except Exception as e:
            self.error.emit(str(e))


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

    # ---------- 반응형 크기 조정 헬퍼 함수들 ----------
    def _resize_widget(self, widget_attr, size_attr, width_ratio, height_ratio=None):
        """위젯 크기 조정 헬퍼 (가로만 또는 가로+세로)"""
        widget = getattr(self, widget_attr, None)
        original_size = getattr(self, size_attr, None)
        if widget and original_size:
            new_width = int(original_size[0] * width_ratio)
            new_height = int(original_size[1] * height_ratio) if height_ratio else original_size[1]
            widget.setFixedSize(new_width, new_height)

    def _resize_table_rows(self, table, row_height_attr, cell_width=None):
        """테이블 셀 위젯 너비 조정 (행 높이는 고정 유지)"""
        original_row_height = getattr(self, row_height_attr, None)
        if not original_row_height:
            return
        # 행 높이는 원본 크기로 고정
        for row in range(table.rowCount()):
            cell_widget = table.cellWidget(row, 0) or table.cellWidget(row, 1)
            if cell_widget and cell_width:
                cell_widget.setFixedSize(cell_width, original_row_height)

    def resizeEvent(self, event):
        """창 크기 변경 시 page1, page2 요소들 위치 재조정"""
        super().resizeEvent(event)

        # ========== Page1 크기 조정 ==========
        if hasattr(self, 'page1') and self.page1:
            if hasattr(self, 'info_panel') and hasattr(self, 'original_window_size') and hasattr(self, 'original_panel_size'):
                # 비율 계산
                width_ratio = max(1.0, self.page1.width() / self.original_window_size[0])
                height_ratio = max(1.0, min(1.2, self.page1.height() / self.original_window_size[1]))

                # 메인 패널
                self._resize_widget('info_panel', 'original_panel_size', width_ratio, height_ratio)

                # 타이틀 영역 (가로만)
                self._resize_widget('panel_title_container', 'original_title_size', width_ratio)
                self._resize_widget('panel_title_text', 'original_title_text_size', width_ratio)
                self._resize_widget('panel_title_desc', 'original_title_desc_size', width_ratio)

                # 인풋 컨테이너 (가로만)
                self._resize_widget('input_container', 'original_input_container_size', width_ratio)

                # 기업명/제품명 필드 (가로만)
                for prefix in ['company', 'product']:
                    self._resize_widget(f'{prefix}_field_widget', f'original_{prefix}_field_size', width_ratio)
                    self._resize_widget(f'{prefix}_label', f'original_{prefix}_label_size', width_ratio)
                    self._resize_widget(f'{prefix}_edit', f'original_{prefix}_edit_size', width_ratio)

                # 버전/모델명 행 (가로만)
                self._resize_widget('version_model_row', 'original_version_model_row_size', width_ratio)
                for prefix in ['version', 'model']:
                    self._resize_widget(f'{prefix}_field_widget', f'original_{prefix}_field_size', width_ratio)
                    self._resize_widget(f'{prefix}_label', f'original_{prefix}_label_size', width_ratio)
                    self._resize_widget(f'{prefix}_edit', f'original_{prefix}_edit_size', width_ratio)

                # 시험유형/시험대상 행 (가로만)
                self._resize_widget('category_target_row', 'original_category_target_row_size', width_ratio)
                for prefix, attr in [('test_category', 'test_category'), ('target_system', 'target_system')]:
                    self._resize_widget(f'{prefix}_widget', f'original_{attr}_field_size', width_ratio)
                    self._resize_widget(f'{prefix}_label', f'original_{attr}_label_size', width_ratio)
                    self._resize_widget(f'{prefix}_edit', f'original_{attr}_edit_size', width_ratio)

                # 시험분야/시험범위 행 (가로만)
                self._resize_widget('group_range_row', 'original_group_range_row_size', width_ratio)
                for prefix, attr in [('test_group', 'test_group'), ('test_range', 'test_range')]:
                    self._resize_widget(f'{prefix}_widget', f'original_{attr}_field_size', width_ratio)
                    self._resize_widget(f'{prefix}_label', f'original_{attr}_label_size', width_ratio)
                    self._resize_widget(f'{prefix}_edit', f'original_{attr}_edit_size', width_ratio)

                # Divider, 관리자 코드 (가로만)
                self._resize_widget('divider', 'original_divider_size', width_ratio)
                self._resize_widget('admin_code_widget', 'original_admin_code_widget_size', width_ratio)
                self._resize_widget('admin_code_label', 'original_admin_code_label_size', width_ratio)
                self._resize_widget('admin_code_input', 'original_admin_code_input_size', width_ratio)

            # 절대 위치 요소들
            page_width = self.page1.width()
            page_height = self.page1.height()

            if hasattr(self, 'page1_content') and self.page1_content:
                content_width = self.page1_content.width()
                content_height = self.page1_content.height()

                if hasattr(self, 'page1_bg_label'):
                    self.page1_bg_label.setGeometry(0, 0, content_width, content_height)
                if hasattr(self, 'ip_input_edit'):
                    self.ip_input_edit.setGeometry(content_width - 411, 24, 200, 40)
                if hasattr(self, 'load_test_info_btn'):
                    self.load_test_info_btn.setGeometry(content_width - 203, 13, 198, 62)

            if hasattr(self, 'management_url_container'):
                self.management_url_container.setGeometry(page_width - 390, page_height - 108, 380, 60)

            # ✅ 반응형: Page1 하단 버튼 영역 가로 확장
            if hasattr(self, 'original_window_size'):
                width_ratio = max(1.0, self.page1.width() / self.original_window_size[0])
                self._resize_widget('page1_button_container', 'original_page1_button_container_size', width_ratio)
                self._resize_widget('next_btn', 'original_next_btn_size', width_ratio)
                self._resize_widget('page1_exit_btn', 'original_page1_exit_btn_size', width_ratio)

        # ========== Page2 크기 조정 ==========
        if hasattr(self, 'page2_content') and self.page2_content:
            content_width = self.page2_content.width()
            content_height = self.page2_content.height()

            if hasattr(self, 'page2_bg_label'):
                self.page2_bg_label.setGeometry(0, 0, content_width, content_height)

            if hasattr(self, 'page2') and self.page2:
                # 비율 계산
                width_ratio = max(1.0, self.page2.width() / 1680)
                height_ratio = max(1.0, self.page2.height() / 1006)

                # bg_root 및 타이틀 컨테이너
                if hasattr(self, 'bg_root') and hasattr(self, 'original_bg_root_size'):
                    new_bg_root_width = int(self.original_bg_root_size[0] * width_ratio)
                    new_bg_root_height = int(self.original_bg_root_size[1] * height_ratio)
                    self.bg_root.setFixedSize(new_bg_root_width, new_bg_root_height)

                    if hasattr(self, 'page2_title_container') and hasattr(self, 'original_page2_title_container_size'):
                        self.page2_title_container.setFixedSize(new_bg_root_width, self.original_page2_title_container_size[1])

                    if hasattr(self, 'page2_title_bg') and hasattr(self, 'original_page2_title_bg_size'):
                        new_title_bg_width = int(self.original_page2_title_bg_size[0] * width_ratio)
                        self.page2_title_bg.setFixedSize(new_title_bg_width, self.original_page2_title_bg_size[1])

                        if hasattr(self, 'panels_container') and hasattr(self, 'original_panels_container_size'):
                            new_panels_height = int(self.original_panels_container_size[1] * height_ratio)
                            self.panels_container.setFixedSize(new_title_bg_width, new_panels_height)

                # 좌측 패널
                self._resize_widget('left_panel', 'original_left_panel_size', width_ratio, height_ratio)
                self._resize_widget('field_scenario_title', 'original_field_scenario_title_size', width_ratio)
                self._resize_widget('field_group', 'original_field_group_size', width_ratio, height_ratio)

                # 시험 분야 테이블
                if hasattr(self, 'test_field_table') and hasattr(self, 'original_test_field_table_size'):
                    new_table_width = int(self.original_test_field_table_size[0] * width_ratio)
                    new_table_height = int(self.original_test_field_table_size[1] * height_ratio)
                    self.test_field_table.setFixedSize(new_table_width, new_table_height)
                    self._resize_table_rows(self.test_field_table, 'original_test_field_row_height', new_table_width)

                # 시나리오 테이블
                if hasattr(self, 'scenario_table') and hasattr(self, 'original_scenario_table_size'):
                    new_table_width = int(self.original_scenario_table_size[0] * width_ratio)
                    new_table_height = int(self.original_scenario_table_size[1] * height_ratio)
                    self.scenario_table.setFixedSize(new_table_width, new_table_height)
                    self._resize_table_rows(self.scenario_table, 'original_scenario_row_height', new_table_width)

                    if hasattr(self, 'scenario_column_background') and hasattr(self, 'original_scenario_column_background_geometry'):
                        orig = self.original_scenario_column_background_geometry
                        self.scenario_column_background.setGeometry(orig[0], orig[1], int(orig[2] * width_ratio), new_table_height)

                    if hasattr(self, 'scenario_placeholder_label') and hasattr(self, 'original_scenario_placeholder_geometry'):
                        orig = self.original_scenario_placeholder_geometry
                        self.scenario_placeholder_label.setGeometry(orig[0], orig[1], int(orig[2] * width_ratio), new_table_height - 31)

                # 시험 API 그룹
                self._resize_widget('api_title', 'original_api_title_size', width_ratio)
                self._resize_widget('api_group', 'original_api_group_size', width_ratio, height_ratio)

                if hasattr(self, 'api_test_table') and hasattr(self, 'original_api_test_table_size'):
                    new_api_table_width = int(self.original_api_test_table_size[0] * width_ratio)
                    new_api_table_height = int(self.original_api_test_table_size[1] * height_ratio)
                    self.api_test_table.setFixedSize(new_api_table_width, new_api_table_height)

                    col_width = (new_api_table_width - 50) // 2
                    self.api_test_table.horizontalHeader().resizeSection(0, col_width)
                    self.api_test_table.horizontalHeader().resizeSection(1, col_width)

                    # 행 높이는 고정 유지 (원본 크기)

                    if hasattr(self, 'api_header_overlay') and hasattr(self, 'original_api_header_overlay_geometry'):
                        orig = self.original_api_header_overlay_geometry
                        self.api_header_overlay.setGeometry(orig[0], orig[1], new_api_table_width, orig[3])

                    if hasattr(self, 'api_header_func_label') and hasattr(self, 'original_api_header_func_label_size'):
                        self.api_header_func_label.setFixedSize(col_width, self.original_api_header_func_label_size[1])
                    if hasattr(self, 'api_header_api_label') and hasattr(self, 'original_api_header_api_label_size'):
                        self.api_header_api_label.setFixedSize(col_width, self.original_api_header_api_label_size[1])

                    if hasattr(self, 'api_placeholder_label') and hasattr(self, 'original_api_placeholder_geometry'):
                        orig = self.original_api_placeholder_geometry
                        self.api_placeholder_label.setGeometry(orig[0], orig[1], new_api_table_width - 50, int(orig[3] * height_ratio))

                # 우측 패널
                self._resize_widget('right_panel', 'original_right_panel_size', width_ratio, height_ratio)
                self._resize_widget('auth_title_widget', 'original_auth_title_size', width_ratio)
                self._resize_widget('auth_section', 'original_auth_section_size', width_ratio, height_ratio)
                self._resize_widget('auth_content_widget', 'original_auth_content_widget_size', width_ratio, height_ratio)

                # 수직 구분선 (특수 처리)
                if hasattr(self, 'auth_divider') and hasattr(self, 'original_auth_divider_size'):
                    new_divider_height = int(self.original_auth_divider_size[1] * height_ratio)
                    self.auth_divider.setFixedSize(1, new_divider_height)
                    divider_pixmap = QPixmap(resource_path("assets/image/test_config/divider.png"))
                    self.auth_divider.setPixmap(divider_pixmap.scaled(1, new_divider_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

                self._resize_widget('auth_type_widget', 'original_auth_type_widget_size', width_ratio, height_ratio)
                self._resize_widget('digest_option', 'original_digest_option_size', width_ratio, height_ratio)
                self._resize_widget('bearer_option', 'original_bearer_option_size', width_ratio, height_ratio)
                self._resize_widget('common_input_widget', 'original_common_input_widget_size', width_ratio, height_ratio)
                self._resize_widget('id_input', 'original_id_input_size', width_ratio)
                self._resize_widget('pw_input', 'original_pw_input_size', width_ratio)

                # 접속주소 탐색
                self._resize_widget('connection_title_row', 'original_connection_title_row_size', width_ratio)
                self._resize_widget('connection_section', 'original_connection_section_size', width_ratio, height_ratio)

                if hasattr(self, 'url_table') and hasattr(self, 'original_url_table_size'):
                    new_url_table_width = int(self.original_url_table_size[0] * width_ratio)
                    new_url_table_height = int(self.original_url_table_size[1] * height_ratio)
                    self.url_table.setFixedSize(new_url_table_width, new_url_table_height)

                    url_col_width = new_url_table_width - 50
                    self.url_table.setColumnWidth(1, url_col_width)

                    # 행 높이는 고정 유지, 셀 위젯 너비만 조정
                    if hasattr(self, 'original_url_row_height'):
                        for row in range(self.url_table.rowCount()):
                            url_widget = self.url_table.cellWidget(row, 1)
                            if url_widget:
                                url_widget.setFixedSize(url_col_width, self.original_url_row_height)

                # 하단 버튼
                self._resize_widget('button_container', 'original_button_container_size', width_ratio)
                self._resize_widget('start_btn', 'original_start_btn_size', width_ratio)
                self._resize_widget('exit_btn', 'original_exit_btn_size', width_ratio)

    def create_page1(self):
        """첫 번째 페이지: 시험 정보 확인"""
        return create_test_info_page(self)

    def create_page2(self):
        """두 번째 페이지: 시험 설정"""
        return create_test_config_page(self)

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
            # 페이지 전환 후 반응형 레이아웃 적용을 위해 resize 이벤트 강제 트리거
            self.resizeEvent(QResizeEvent(self.size(), self.size()))

    def go_to_previous_page(self):
        """이전 페이지로 이동"""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            # 페이지 전환 후 반응형 레이아웃 적용을 위해 resize 이벤트 강제 트리거
            self.resizeEvent(QResizeEvent(self.size(), self.size()))
            # 1페이지로 돌아갈 때 다음 버튼 상태 업데이트
            if self.current_page == 0:
                self.check_next_button_state()

    # ---------- 동작 ----------
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

            # 이미지 경로 (체크박스 분리 - 반응형)
            bg_image = "assets/image/test_config/row.png"
            bg_selected_image = "assets/image/test_config/row_selected.png"
            checkbox_unchecked = "assets/image/test_config/checkbox_unchecked.png"
            checkbox_checked = "assets/image/test_config/checkbox_checked.png"

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

                # 컬럼 1: URL (ClickableCheckboxRowWidget - 체크박스 분리, paintEvent 배경)
                url_widget = ClickableCheckboxRowWidget(
                    url, row, 1,
                    bg_image, bg_selected_image,
                    checkbox_unchecked, checkbox_checked
                )
                url_widget.setProperty("url", url)
                url_widget.clicked.connect(self.on_url_row_selected)
                self.url_table.setCellWidget(row, 1, url_widget)

                self.url_table.setRowHeight(row, 39)

            # 셀 생성 후 현재 창 크기에 맞게 반응형 적용
            self.resizeEvent(QResizeEvent(self.size(), self.size()))

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

            # 물리보안(시스템 검증)일 경우: UI에서 수정한 ID/PW로 Data_request.py 업데이트
            if not hasattr(self, 'target_system') or self.target_system != "통합플랫폼시스템":
                user_id = self.id_input.text().strip()
                password = self.pw_input.text().strip()
                if user_id and password:
                    print(f"[INFO] 물리보안 시험 시작 - Data_request.py 업데이트 (userID={user_id})")
                    update_success = self.form_validator.update_data_request_authentication(spec_id, user_id, password)
                    if not update_success:
                        print("[WARNING] Data_request.py 업데이트 실패, 기존 값으로 진행합니다.")

            # CONSTANTS.py 업데이트
            if self.form_validator.update_constants_py():
                # Heartbeat (busy) 전송 - 시험 시작 시
                test_info = {
                    "testRequestId": getattr(self, 'request_id', ''),
                    "companyName": self.company_edit.text().strip(),
                    "contactPerson": getattr(self, 'contact_person', ''),
                    "productName": self.product_edit.text().strip(),
                    "modelName": self.model_edit.text().strip(),
                    "version": self.version_edit.text().strip(),
                    "testGroups": [
                        {
                            "id": g.get("id", ""),
                            "name": g.get("name", ""),
                            "testRange": g.get("testRange", "")
                        } for g in getattr(self, 'test_groups', [])
                    ]
                }
                self.form_validator.send_heartbeat_busy(test_info)

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

    def exit_btn_clicked(self):
        """종료 버튼 클릭 시 프로그램 종료"""
        reply = QMessageBox.question(self, '프로그램 종료',
                                     '정말로 프로그램을 종료하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()

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
        """시험정보 불러오기 버튼 클릭 이벤트 (API 기반, 비동기)"""
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
        self.loading_popup = LoadingPopup(width=400, height=200)
        self.loading_popup.update_message("시험 정보 불러오는 중...", "잠시만 기다려주세요")
        self.loading_popup.show()

        # 백그라운드 워커 스레드 시작
        self.test_info_worker = TestInfoWorker(self.form_validator, ip_address)
        self.test_info_worker.finished.connect(self._on_test_info_loaded)
        self.test_info_worker.error.connect(self._on_test_info_error)
        self.test_info_worker.start()

    def _on_test_info_loaded(self, test_data):
        """시험 정보 로드 성공 시 호출되는 슬롯"""
        try:
            if not test_data:
                QMessageBox.warning(self, "경고",
                    "시험 정보를 불러올 수 없습니다.\n"
                    "- 서버 연결을 확인해주세요.\n"
                    "- IP 주소에 해당하는 시험 요청이 있는지 확인해주세요.")
                return

            # 1페이지 필드 채우기
            eval_target = test_data.get("testRequest", {}).get("evaluationTarget", {})
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
                CONSTANTS.WEBHOOK_URL = f"https://{CONSTANTS.url}:{CONSTANTS.WEBHOOK_PORT}"

                # 2. CONSTANTS.py 파일 자체도 수정
                try:
                    import sys
                    import os

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
            # (UI 접근이 필요하므로 메인 스레드에서 실행)
            self.form_validator.load_opt_files_from_api(test_data)

            # 플랫폼 검증일 경우 Authentication 정보 자동 입력
            self.auto_fill_authentication_for_platform()

            # 다음 버튼 상태 업데이트
            self.check_next_button_state()

            # Heartbeat (idle) 전송 - 시험 정보 불러오기 성공 시
            self.form_validator.send_heartbeat_idle()

        except Exception as e:
            print(f"시험정보 불러오기 실패: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"시험 정보를 불러오는 중 오류가 발생했습니다:\n{str(e)}")

        finally:
            # 로딩 팝업 닫기
            if hasattr(self, 'loading_popup') and self.loading_popup:
                self.loading_popup.close()
                self.loading_popup = None

    def _on_test_info_error(self, error_message):
        """시험 정보 로드 실패 시 호출되는 슬롯"""
        print(f"시험정보 불러오기 실패: {error_message}")
        QMessageBox.critical(self, "오류", f"시험 정보를 불러오는 중 오류가 발생했습니다:\n{error_message}")

        # 로딩 팝업 닫기
        if hasattr(self, 'loading_popup') and self.loading_popup:
            self.loading_popup.close()
            self.loading_popup = None

    def auto_fill_authentication_for_platform(self):
        """
        플랫폼 검증/시스템 검증에 따라 Authentication 정보를 자동으로 채움
        - 통합플랫폼: Validation_request.py에서 읽어와서 disabled
        - 물리보안(시스템 검증): Data_request.py에서 읽어와서 enabled (수정 가능)
        """
        try:
            # test_specs에서 첫 번째 spec_id 가져오기
            if not hasattr(self, 'test_specs') or not self.test_specs:
                print("[WARNING] test_specs가 없어서 Authentication 자동 입력을 건너뜁니다.")
                return

            first_spec = self.test_specs[0]
            spec_id = first_spec.get("id", "")

            if not spec_id:
                print("[WARNING] spec_id를 찾을 수 없어서 Authentication 자동 입력을 건너뜁니다.")
                return

            # 플랫폼 검증인지 확인
            if not hasattr(self, 'target_system') or self.target_system != "통합플랫폼시스템":
                # 물리보안(시스템 검증): Data_request.py에서 읽어옴
                print("[INFO] 시스템 검증(물리보안) 감지 - Data_request.py에서 Authentication 정보를 읽어옵니다.")
                print(f"[INFO] spec_id={spec_id}로 Data_request.py에서 Authentication 정보를 추출합니다.")

                user_id, password = self.form_validator.get_authentication_from_data_request(spec_id)

                if user_id and password:
                    # 필드에 값 설정
                    self.id_input.setText(user_id)
                    self.pw_input.setText(password)

                    # 필드를 enabled 상태로 설정 (수정 가능)
                    self.id_input.setEnabled(True)
                    self.pw_input.setEnabled(True)

                    print(f"[SUCCESS] 시스템 검증: Authentication 자동 입력 완료 (User ID={user_id})")
                    print(f"[INFO] id_input과 pw_input 필드가 enabled 상태로 설정되었습니다. (수정 가능)")
                else:
                    print("[WARNING] Data_request.py에서 Authentication 정보를 찾을 수 없습니다. 필드를 비워둡니다.")
                    self.id_input.setEnabled(True)
                    self.pw_input.setEnabled(True)
                    self.id_input.clear()
                    self.pw_input.clear()
                return

            # 통합플랫폼: Validation_request.py에서 읽어옴
            print("[INFO] 플랫폼 검증 감지 - Validation_request.py에서 Authentication 자동 입력을 시도합니다.")
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
                print("[WARNING] Authentication 정보를 찾을 수 없습니다. 필드를 비워둡니다.")
                # Authentication 정보가 없으면 필드를 활성화하고 비움
                self.id_input.setEnabled(True)
                self.pw_input.setEnabled(True)
                self.id_input.clear()
                self.pw_input.clear()

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
        """시나리오 테이블 클릭 시 체크박스 상태 변경 및 API 테이블 업데이트"""
        try:
            # 모든 시나리오 행의 체크박스 상태 업데이트
            for i in range(self.scenario_table.rowCount()):
                widget = self.scenario_table.cellWidget(i, 0)
                if widget and hasattr(widget, 'setChecked'):
                    # 클릭된 행은 체크, 나머지는 체크 해제
                    widget.setChecked(i == row)

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

            # 이미지 경로 (체크박스 분리 - 반응형)
            bg_image = "assets/image/test_config/row.png"
            bg_selected_image = "assets/image/test_config/row_selected.png"
            checkbox_unchecked = "assets/image/test_config/checkbox_unchecked.png"
            checkbox_checked = "assets/image/test_config/checkbox_checked.png"

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

            # 컬럼 1: URL (ClickableCheckboxRowWidget - 체크박스 분리, paintEvent 배경)
            url_widget = ClickableCheckboxRowWidget(
                final_url, row, 1,
                bg_image, bg_selected_image,
                checkbox_unchecked, checkbox_checked
            )
            url_widget.setProperty("url", final_url)
            url_widget.clicked.connect(self.on_url_row_selected)
            self.url_table.setCellWidget(row, 1, url_widget)

            self.url_table.setRowHeight(row, 39)

            # 셀 생성 후 현재 창 크기에 맞게 반응형 적용
            self.resizeEvent(QResizeEvent(self.size(), self.size()))

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
        """URL 테이블 행 클릭 시 두 컬럼 모두 스타일 변경 (2컬럼 방식 - ClickableCheckboxRowWidget 사용)"""
        try:
            # 모든 URL 행의 스타일 업데이트
            for i in range(self.url_table.rowCount()):
                row_num_widget = self.url_table.cellWidget(i, 0)  # 행 번호 컬럼
                url_widget = self.url_table.cellWidget(i, 1)  # URL 컬럼 (ClickableCheckboxRowWidget)

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
                    if url_widget and hasattr(url_widget, 'setChecked'):
                        url_widget.setChecked(True)
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
                    if url_widget and hasattr(url_widget, 'setChecked'):
                        url_widget.setChecked(False)

            # 선택된 행 추적
            self.selected_url_row = row

            # UI 업데이트 강제
            QApplication.processEvents()

            # 시작 버튼 상태 체크
            self.check_start_button_state()

        except Exception as e:
            print(f"URL 행 선택 처리 실패: {e}")