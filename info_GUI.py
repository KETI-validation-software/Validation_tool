from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QCheckBox,
    QStackedWidget, QRadioButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# 분리된 모듈들 import
from network_scanner import NetworkScanWorker
from form_validator import FormValidator


class InfoWidget(QWidget):
    """
    접속 후 화면 GUI.
    - 시험 기본/입력 정보, 인증 선택, 주소 탐색, OPT 로드 등
    """
    startTestRequested = pyqtSignal(str)  # 모드를 전달

    def __init__(self):
        super().__init__()
        self.form_validator = FormValidator(self)  # 폼 검증 모듈 초기화
        self.scan_thread = None
        self.scan_worker = None
        self.current_mode = None
        self.current_page = 0
        self.stacked_widget = QStackedWidget()
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
        layout = QVBoxLayout()

        # 상단 타이틀
        title = QLabel("시험 정보를 확인하세요.")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; text-align: center;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 시험 기본 정보 (기존 좌측 패널에서 API 테이블 제외)
        info_panel = self.create_basic_info_panel()
        layout.addWidget(info_panel)

        # 하단 버튼
        buttons = self.create_page1_buttons()
        layout.addWidget(buttons)

        page.setLayout(layout)
        return page

    def create_page2(self):
        """두 번째 페이지: 시험 설정"""
        page = QWidget()
        main_layout = QHBoxLayout()

        # 좌측 패널
        left_panel = QGroupBox()
        left_layout = QVBoxLayout()

        # 시험 분야 확인 문구
        left_title = QLabel("시험 분야를 확인하세요.")
        left_title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        left_layout.addWidget(left_title)

        # 새로운 시험 분야 테이블
        field_table = self.create_test_field_table()
        left_layout.addWidget(field_table)

        # 기존 API 테이블 (시험분야(API)로 변경)
        api_table = self.create_test_field_api_table()
        left_layout.addWidget(api_table)

        left_panel.setLayout(left_layout)

        # 우측 패널
        right_panel = QGroupBox()
        right_layout = QVBoxLayout()

        # 시험 설정 정보 문구
        right_title = QLabel("시험 설정 정보를 입력하세요.")
        right_title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        right_layout.addWidget(right_title)

        # 기존 우측 패널 내용
        auth_section = self.create_auth_section()
        connection_section = self.create_connection_section()
        right_layout.addWidget(auth_section)
        right_layout.addWidget(connection_section)

        right_panel.setLayout(right_layout)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)

        # 하단 버튼
        page_layout = QVBoxLayout()
        page_layout.addLayout(main_layout, 1)
        page_layout.addWidget(self.create_page2_buttons())

        page.setLayout(page_layout)
        return page

    # ---------- 페이지 전환 메서드 ----------
    def go_to_next_page(self):
        """다음 페이지로 이동"""
        if self.current_page < 1:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)

    def go_to_previous_page(self):
        """이전 페이지로 이동"""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)

    def create_page1_buttons(self):
        """첫 번째 페이지 버튼들"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addStretch()

        # 다음 버튼
        next_btn = QPushButton("다음")
        next_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        next_btn.clicked.connect(self.go_to_next_page)
        layout.addWidget(next_btn)

        # 초기화 버튼
        reset_btn = QPushButton("초기화")
        reset_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        reset_btn.clicked.connect(self.reset_all_fields)
        layout.addWidget(reset_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_page2_buttons(self):
        """두 번째 페이지 버튼들"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addStretch()

        # 시험 시작 버튼
        self.start_btn = QPushButton("시험 시작")
        self.start_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        self.start_btn.clicked.connect(self.start_test)
        self.start_btn.setEnabled(False)  # 초기에는 비활성화
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
        panel = QGroupBox("시험 기본 정보")
        layout = QVBoxLayout()

        # 불러오기 버튼들 (Request/Response - 일반/WebHook)
        btn_row1 = QHBoxLayout()
        btn_row1.addStretch()

        self.load_request_btn = QPushButton("Long Polling|Request")
        self.load_request_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        self.load_request_btn.clicked.connect(lambda: self.form_validator.load_opt_files("request_longpolling"))
        btn_row1.addWidget(self.load_request_btn)

        self.load_response_btn = QPushButton("Long Polling|Response")
        self.load_response_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        self.load_response_btn.clicked.connect(lambda: self.form_validator.load_opt_files("response_longpolling"))
        btn_row1.addWidget(self.load_response_btn)

        layout.addLayout(btn_row1)

        # WebHook 버전 버튼들
        btn_row2 = QHBoxLayout()
        btn_row2.addStretch()

        self.load_request_webhook_btn = QPushButton("WebHook|Request")
        self.load_request_webhook_btn.setStyleSheet("QPushButton { background-color: #C4BEE2; color: black; font-weight: bold; }")
        self.load_request_webhook_btn.clicked.connect(lambda: self.form_validator.load_opt_files("request_webhook"))
        btn_row2.addWidget(self.load_request_webhook_btn)

        self.load_response_webhook_btn = QPushButton("WebHook|Response")
        self.load_response_webhook_btn.setStyleSheet("QPushButton { background-color: #C4BEE2; color: black; font-weight: bold; }")
        self.load_response_webhook_btn.clicked.connect(lambda: self.form_validator.load_opt_files("response_webhook"))
        btn_row2.addWidget(self.load_response_webhook_btn)

        layout.addLayout(btn_row2)

        form = QFormLayout()
        self.company_edit = QLineEdit()
        self.product_edit = QLineEdit()
        self.version_edit = QLineEdit()
        self.model_edit = QLineEdit()
        self.test_category_edit = QLineEdit()
        self.target_system_edit = QLineEdit()
        self.test_group_edit = QLineEdit()
        self.test_range_edit = QLineEdit()

        # 관리자 코드 입력 필드 추가
        self.admin_code_edit = QLineEdit()
        self.admin_code_edit.setEchoMode(QLineEdit.Password)  # 비밀번호 모드
        self.admin_code_edit.setPlaceholderText("입력해주세요")

        # 관리자 코드 입력 시 숫자 검증 및 버튼 상태 업데이트
        self.admin_code_edit.textChanged.connect(self.form_validator.validate_admin_code)
        self.admin_code_edit.textChanged.connect(self.check_start_button_state)

        form.addRow("기업명:", self.company_edit)
        form.addRow("제품명:", self.product_edit)
        form.addRow("버전:", self.version_edit)
        form.addRow("모델명:", self.model_edit)
        form.addRow("시험유형:", self.test_category_edit)
        form.addRow("시험대상:", self.target_system_edit)
        form.addRow("시험분야:", self.test_group_edit)
        form.addRow("시험범위:", self.test_range_edit)
        form.addRow("관리자 코드:", self.admin_code_edit)

        # 시험유형 변경 시 관리자 코드 필드 활성화/비활성화
        self.test_category_edit.textChanged.connect(self.form_validator.handle_test_category_change)
        self.test_category_edit.textChanged.connect(self.check_start_button_state)

        layout.addLayout(form)
        panel.setLayout(layout)
        return panel

    def create_test_field_table(self):
        """시험 분야명  테이블"""
        table = QTableWidget(0, 1)
        table.setHorizontalHeaderLabels(["시험 분야명"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def create_test_field_api_table(self):
        """시험분야(API) 테이블"""
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["시험 분야", "기능명", "API명"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.api_test_table = table 
        return table

    def create_auth_section(self):
        """인증 방식 섹션"""
        section = QGroupBox("사용자 인증 방식")
        layout = QVBoxLayout()

        # Digest
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
        digest_w = QWidget()
        digest_w.setLayout(digest_row)
        digest_row.setContentsMargins(20, 0, 0, 0)
        layout.addWidget(digest_w)

        # Bearer
        self.bearer_radio = QRadioButton("Bearer Token")
        layout.addWidget(self.bearer_radio)
        token_row = QHBoxLayout()
        self.token_input = QLineEdit()
        token_row.addWidget(QLabel("Token:"))
        token_row.addWidget(self.token_input)
        token_w = QWidget()
        token_w.setLayout(token_row)
        token_row.setContentsMargins(20, 0, 0, 0)
        layout.addWidget(token_w)

        # 라디오 버튼 연결
        self.digest_radio.toggled.connect(self.update_auth_fields)
        self.bearer_radio.toggled.connect(self.update_auth_fields)

        # 입력 필드 변경 시 버튼 상태 체크
        self.id_input.textChanged.connect(self.check_start_button_state)
        self.pw_input.textChanged.connect(self.check_start_button_state)
        self.token_input.textChanged.connect(self.check_start_button_state)

        section.setLayout(layout)
        return section

    def create_connection_section(self):
        """접속 정보 섹션"""
        section = QGroupBox("시험 접속 정보")
        layout = QVBoxLayout()

        scan_label = QLabel("주소 탐색")
        scan_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(scan_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        scan_btn = QPushButton("🔍주소 탐색")
        scan_btn.setStyleSheet("QPushButton { background-color: #E1EBF4; color: #3987C1; font-weight: bold; }")
        scan_btn.clicked.connect(self.start_scan)
        btn_row.addWidget(scan_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.url_table = QTableWidget(0, 2)
        self.url_table.setHorizontalHeaderLabels(["☑", "URL"])
        self.url_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

        # 주소 탐색
        scan_label = QLabel("시험 접속 정보")
        scan_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(scan_label)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        scan_btn = QPushButton("🔍주소 탐색")
        scan_btn.setStyleSheet("QPushButton { background-color: #E1EBF4; color: #3987C1; font-weight: bold; }")
        scan_btn.clicked.connect(self.start_scan)
        btn_row.addWidget(scan_btn)
        layout.addLayout(btn_row)

        self.url_table = QTableWidget(0, 2)
        self.url_table.setHorizontalHeaderLabels(["☑", "URL"])
        self.url_table.verticalHeader().setVisible(False)
        self.url_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.url_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.url_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.url_table.horizontalHeader().setStretchLastSection(True)
        self.url_table.setColumnWidth(0, 36)
        self.url_table.cellClicked.connect(self.select_url_row)
        layout.addWidget(self.url_table)

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
        self.start_btn.setEnabled(False)  # 초기에는 비활성화
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
        """필수값 입력 여부에 따른 시험 시작 버튼 상태 업데이트"""
        try:
            # start_btn이 아직 생성되지 않았으면 건너뛰기
            if not hasattr(self, 'start_btn'):
                return
                
            auth_valid = False
            
            # 인증 정보 유효성 검사
            if self.digest_radio.isChecked():
                # Digest Auth: ID와 PW가 모두 입력되어야 함
                auth_valid = bool(self.id_input.text().strip() and self.pw_input.text().strip())
            else:
                # Bearer Token: Token이 입력되어야 함
                auth_valid = bool(self.token_input.text().strip())
            
            # 인증 정보만으로 버튼 활성화
            self.start_btn.setEnabled(auth_valid)
            
        except Exception as e:
            print(f"버튼 상태 업데이트 실패: {e}")

    def start_scan(self):
        """실제 네트워크 스캔으로 사용 가능한 주소 탐지"""
        try:
            
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

    def _populate_url_table(self, urls):
        """URL 테이블에 스캔 결과 채우기"""
        try:
            self.url_table.setRowCount(0)
            
            for i, url in enumerate(urls):
                row = self.url_table.rowCount()
                self.url_table.insertRow(row)

                checkbox_widget = QWidget()
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

        # 선택된 행 체크
        selected_checkbox_widget = self.url_table.cellWidget(row, 0)
        if selected_checkbox_widget:
            checkbox = selected_checkbox_widget.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(True)
        
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

    def start_test(self):
        """시험 시작 - CONSTANTS.py 업데이트 후 검증 소프트웨어 실행"""
        try:
            # 모드 선택 확인
            if not self.current_mode:
                QMessageBox.warning(self, "모드 미선택", "먼저 불러오기 버튼 중 하나를 눌러 모드를 선택해주세요.")
                return
            
            # CONSTANTS.py 업데이트
            if self.form_validator.update_constants_py():
                self.startTestRequested.emit(self.current_mode)
            else:
                QMessageBox.warning(self, "저장 실패", "CONSTANTS.py 업데이트에 실패했습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"시험 시작 중 오류가 발생했습니다:\n{str(e)}")    

    def check_start_button_state(self):
        """시험 시작 버튼 활성화 조건 체크"""
        try:
            # 1. 모드 선택 확인
            if not self.current_mode:
                self.start_btn.setEnabled(False)
                return
            
            # 2. 시험 기본 정보 확인
            basic_info_filled = all([
                self.company_edit.text().strip(),
                self.product_edit.text().strip(),
                self.version_edit.text().strip(),
                self.test_category_edit.text().strip(),
                self.target_system_edit.text().strip(),
                self.test_range_edit.text().strip()
            ])

            # 2-1. 관리자 코드 검증 추가
            admin_code_valid = self.form_validator.is_admin_code_valid()
            
            # 3. 시험항목(API) 테이블 확인
            api_table_filled = self.api_test_table.rowCount() > 0
            
            # 4. 인증 정보 확인
            auth_filled = False
            if self.digest_radio.isChecked():
                auth_filled = bool(self.id_input.text().strip() and self.pw_input.text().strip())
            else:  # Bearer Token
                auth_filled = bool(self.token_input.text().strip())
            
            # 5. 접속 정보 확인 (URL 선택됨)
            url_selected = bool(self.get_selected_url())
            
            # 모든 조건이 충족되면 활성화 (관리자 코드 유효성 포함)
            all_conditions_met = basic_info_filled and admin_code_valid and api_table_filled and auth_filled and url_selected
            self.start_btn.setEnabled(all_conditions_met)
            
        except Exception as e:
            print(f"버튼 상태 체크 실패: {e}")
            self.start_btn.setEnabled(False)

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

            # API 테이블에 데이터가 있는지 확인
            if self.api_test_table.rowCount() > 0:
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

            # 관리자 코드 필드를 기본 상태로 되돌림
            self.admin_code_edit.setEnabled(True)
            self.admin_code_edit.setPlaceholderText("입력해주세요")

            # API 테이블 초기화
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

            print("모든 필드 초기화 완료")
            QMessageBox.information(self, "초기화 완료", "모든 입력값이 초기화되었습니다.")

        except Exception as e:
            print(f"초기화 실패: {e}")
            raise

