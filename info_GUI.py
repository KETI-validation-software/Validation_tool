import socket
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QCheckBox
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread

# 외부 유틸/의존 (원본과 동일 모듈 사용)
from core.functions import resource_path
from core.opt_loader import OptLoader
from core.schema_generator import generate_schema_file
from core.video_request_generator import generate_video_request_file

class NetworkScanWorker(QObject):
    scan_completed = pyqtSignal(list)
    scan_failed = pyqtSignal(str)

    def scan_network(self):
        try:
            local_ip = self._get_local_ip()
            if not local_ip:
                self.scan_failed.emit("내 IP 주소를 찾을 수 없습니다.")
                return

            ports = self._scan_available_ports(local_ip, range(8000, 8100))
            if ports:
                urls = [f"{local_ip}:{p}" for p in ports[:3]]
                self.scan_completed.emit(urls)
            else:
                self.scan_failed.emit("검색된 사용가능 포트 없음")
        except Exception as e:
            self.scan_failed.emit(f"네트워크 탐색 중 오류 발생:\n{str(e)}")

    def _get_local_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return None

    def _scan_available_ports(self, ip, port_range):
        found = []
        for port in port_range:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.settimeout(0.1)
                    sock.bind((ip, port))
                    found.append(port)
                    if len(found) >= 10:
                        break
            except Exception:
                continue
        return found


class InfoWidget(QWidget):
    """
    접속 후 화면 GUI.
    - 시험 기본/입력 정보, 인증 선택, 주소 탐색, OPT 로드 등
    """
    startTestRequested = pyqtSignal(str)  # 모드를 전달

    def __init__(self):
        super().__init__()
        self.opt_loader = OptLoader()
        self.scan_thread = None
        self.scan_worker = None
        self.current_mode = None
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.create_left_panel(), 1)
        main_layout.addWidget(self.create_right_panel(), 1)

        layout = QVBoxLayout()
        layout.addLayout(main_layout, 1)
        layout.addWidget(self.create_bottom_buttons())
        self.setLayout(layout)

    # ---------- 좌측 패널 ----------
    def create_left_panel(self):
        panel = QGroupBox("시험 기본 정보")
        layout = QVBoxLayout()

        # 불러오기 버튼들 (Request/Response - 일반/WebHook)
        btn_row1 = QHBoxLayout()
        btn_row1.addStretch()

        self.load_request_btn = QPushButton("Long Polling|Request")
        self.load_request_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        self.load_request_btn.clicked.connect(lambda: self.load_opt_files("request_longpolling"))
        btn_row1.addWidget(self.load_request_btn)

        self.load_response_btn = QPushButton("Long Polling|Response")
        self.load_response_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        self.load_response_btn.clicked.connect(lambda: self.load_opt_files("response_longpolling"))
        btn_row1.addWidget(self.load_response_btn)

        layout.addLayout(btn_row1)

        # WebHook 버전 버튼들
        btn_row2 = QHBoxLayout()
        btn_row2.addStretch()

        self.load_request_webhook_btn = QPushButton("WebHook|Request")
        self.load_request_webhook_btn.setStyleSheet("QPushButton { background-color: #C4BEE2; color: black; font-weight: bold; }")
        self.load_request_webhook_btn.clicked.connect(lambda: self.load_opt_files("request_webhook"))
        btn_row2.addWidget(self.load_request_webhook_btn)

        self.load_response_webhook_btn = QPushButton("WebHook|Response")
        self.load_response_webhook_btn.setStyleSheet("QPushButton { background-color: #C4BEE2; color: black; font-weight: bold; }")
        self.load_response_webhook_btn.clicked.connect(lambda: self.load_opt_files("response_webhook"))
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

        form.addRow("기업명", self.company_edit)
        form.addRow("제품명", self.product_edit)
        form.addRow("버전", self.version_edit)
        form.addRow("모델명", self.model_edit)
        form.addRow("시험유형", self.test_category_edit)
        form.addRow("시험대상", self.target_system_edit)
        form.addRow("시험분야", self.test_group_edit)
        form.addRow("시험범위", self.test_range_edit)
        layout.addLayout(form)

        api_label = QLabel("시험항목(API)")
        api_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(api_label)

        self.api_test_table = QTableWidget(0, 3)
        self.api_test_table.setHorizontalHeaderLabels(["시험 항목", "기능명", "API명"])
        self.api_test_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.api_test_table)

        panel.setLayout(layout)
        return panel

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
            if self.update_constants_py():
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
            
            # 모든 조건이 충족되면 활성화
            all_conditions_met = basic_info_filled and api_table_filled and auth_filled and url_selected
            self.start_btn.setEnabled(all_conditions_met)
            
        except Exception as e:
            print(f"버튼 상태 체크 실패: {e}")
            self.start_btn.setEnabled(False)

    def update_constants_py(self):
        """CONSTANTS.py 파일의 변수들을 GUI 입력값으로 업데이트"""
        try:
            constants_path = "config/CONSTANTS.py"

            # 1. 시험 기본 정보 수집
            company_name = self.company_edit.text().strip()
            product_name = self.product_edit.text().strip()
            version = self.version_edit.text().strip()
            test_category = self.test_category_edit.text().strip()
            test_target = self.target_system_edit.text().strip()
            test_range = self.test_range_edit.text().strip()

            # 2. 접속 정보
            url = self.get_selected_url()

            # 3. 인증 정보
            if self.digest_radio.isChecked():
                auth_type = "Digest Auth"
                auth_info = f"{self.id_input.text().strip()},{self.pw_input.text().strip()}"
            else:
                auth_type = "Bearer Token"
                auth_info = self.token_input.text().strip()

            # 4. OPT 파일에서 admin_code 추출
            exp_opt_path = resource_path("temp/(temp)exp_opt_requestVal.json")
            exp_opt = self.opt_loader.load_opt_json(exp_opt_path)
            admin_code = ""
            if exp_opt and "testRequest" in exp_opt:
                test_group = exp_opt["testRequest"].get("testGroup", {})
                admin_code = test_group.get("adminCode", "")

            # 5. OPT2 파일에서 프로토콜/타임아웃 정보 추출
            exp_opt2_path = resource_path("temp/(temp)exp_opt2_requestVal_LongPolling.json")
            exp_opt2 = self.opt_loader.load_opt_json(exp_opt2_path)

            steps = exp_opt2.get("specification", {}).get("steps", [])
            step_count = len(steps)

            # connectTimeout, numRetries, transportMode를 step 개수만큼 리스트로 생성
            time_out = []
            num_retries = []
            trans_protocol = []

            for step in steps:
                # 각 step의 api.settings에서 값 추출
                settings = step.get("api", {}).get("settings", {})
                time_out.append(settings.get("connectTimeout", 30))  # 기본값 30
                num_retries.append(settings.get("numRetries", 3))    # 기본값 3
                
                # transportMode 추출 (settings에서 또는 api에서)
                transport_mode = settings.get("transportMode", None)
                if transport_mode is None:
                    # settings에 없으면 api 레벨에서 찾기
                    transport_mode = step.get("api", {}).get("transportMode", None)
                trans_protocol.append(transport_mode)

            # 6. CONSTANTS.py 파일 업데이트
            self._update_constants_file(constants_path, {
                'company_name': company_name,
                'product_name': product_name,
                'version': version,
                'test_category': test_category,
                'test_target': test_target,
                'test_range': test_range,
                'url': url,
                'auth_type': auth_type,
                'auth_info': auth_info,
                'admin_code': admin_code,
                'trans_protocol': trans_protocol,
                'time_out': time_out,
                'num_retries': num_retries
            })

            return True

        except Exception as e:
            print(f"CONSTANTS.py 업데이트 실패: {e}")
            return False

    def _update_constants_file(self, file_path, variables):
        """CONSTANTS.py 파일의 특정 변수들을 업데이트"""
        import re

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for var_name, var_value in variables.items():
            # 변수 형태에 따른 패턴 매칭
            if isinstance(var_value, str):
                new_line = f'{var_name} = "{var_value}"'
            elif isinstance(var_value, list):
                new_line = f'{var_name} = {var_value}'
            elif var_value is None:
                new_line = f'{var_name} = None'
            else:
                new_line = f'{var_name} = {var_value}'

            # 기존 변수 라인을 찾아서 교체
            pattern = rf'^{var_name}\s*=.*$'
            content = re.sub(pattern, new_line, content, flags=re.MULTILINE)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)



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
            # === 좌측 패널 확인 ===
            
            # 기본 정보 필드에 입력값이 있는지 확인
            basic_fields = [
                self.company_edit.text().strip(),
                self.product_edit.text().strip(),
                self.version_edit.text().strip(),
                self.model_edit.text().strip(),
                self.test_category_edit.text().strip(),
                self.target_system_edit.text().strip(),
                self.test_group_edit.text().strip(),
                self.test_range_edit.text().strip()
            ]
            
            # 하나라도 값이 있으면 초기화 필요
            if any(field for field in basic_fields):
                return True
            
            # API 테이블에 데이터가 있는지 확인
            if self.api_test_table.rowCount() > 0:
                return True
            
            # === 우측 패널 확인 ===
            
            # 인증 정보에 입력값이 있는지 확인
            auth_fields = [
                self.id_input.text().strip(),
                self.pw_input.text().strip(),
                self.token_input.text().strip()
            ]
            
            if any(field for field in auth_fields):
                return True
            
            # 주소 탐색 테이블에서 선택된 항목이 있는지 확인
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
            # === 좌측 패널 초기화 ===
            
            # 기본 정보 필드 초기화
            self.company_edit.clear()
            self.product_edit.clear()
            self.version_edit.clear()
            self.model_edit.clear()
            self.test_category_edit.clear()
            self.target_system_edit.clear()
            self.test_group_edit.clear()
            self.test_range_edit.clear()
            
            # API 테이블 초기화
            self.api_test_table.setRowCount(0)
            
            # === 우측 패널 초기화 ===
            
            # 인증 정보 초기화
            self.id_input.clear()
            self.pw_input.clear()
            self.token_input.clear()
            
            # 인증 방식을 Digest Auth로 초기화
            self.digest_radio.setChecked(True)
            
            # 주소 탐색 테이블 초기화 (테이블 자체를 비움)
            self.url_table.setRowCount(0)
            
            # === 버튼 상태 초기화 ===

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

    # ---------- OPT 로드 ----------
    def load_opt_files(self, mode):
        try:
            # 모드에 따라 다른 파일 경로 설정
            if mode == "request_longpolling":
                exp_opt_path = resource_path("temp/(temp)exp_opt_requestVal.json")
                exp_opt2_path = resource_path("temp/(temp)exp_opt2_requestVal_LongPolling.json")
            elif mode == "response_longpolling":
                exp_opt_path = resource_path("temp/(temp)exp_opt_responseVal.json")
                exp_opt2_path = resource_path("temp/(temp)exp_opt2_responseVal_LongPolling.json")
            elif mode == "request_webhook":
                exp_opt_path = resource_path("temp/(temp)exp_opt_requestVal.json")
                exp_opt2_path = resource_path("temp/(temp)exp_opt2_requestVal_WebHook.json")
            elif mode == "response_webhook":
                exp_opt_path = resource_path("temp/(temp)exp_opt_responseVal.json")
                exp_opt2_path = resource_path("temp/(temp)exp_opt2_responseVal_WebHook.json")
            else:
                QMessageBox.warning(self, "모드 오류", f"알 수 없는 모드: {mode}")
                return
            
            exp_opt = self.opt_loader.load_opt_json(exp_opt_path)
            exp_opt2 = self.opt_loader.load_opt_json(exp_opt2_path)
            if not (exp_opt and exp_opt2):
                QMessageBox.warning(self, "로드 실패", f"{mode.upper()} 모드 OPT 파일을 읽을 수 없습니다.")
                return
            
            # 현재 모드 저장 및 UI 업데이트
            self.current_mode = mode
            
            self._fill_basic_info(exp_opt)
            self._fill_api_table(exp_opt, exp_opt2)
            
            # 모드에 따른 파일 생성
            try:
                if mode in ["request_longpolling", "request_webhook"]:
                    # Request 모드 (일반/WebHook)
                    schema_path = generate_schema_file(
                        exp_opt2_path,
                        schema_type="request",
                        output_path="spec/video/videoSchema_request.py"
                    )
                    print(f"videoSchema_request.py 생성 완료: {schema_path}")

                    # videoRequest_request.py 생성
                    request_path = generate_video_request_file(
                        exp_opt2_path,
                        file_type="request",
                        output_path="spec/video/videoData_request.py"
                    )
                    print(f"videoRequest_request.py 생성 완료: {request_path}")

                elif mode in ["response_longpolling", "response_webhook"]:
                    schema_path = generate_schema_file(
                        exp_opt2_path,
                        schema_type="response", 
                        output_path="spec/video/videoSchema_response.py"
                    )
                    print(f"videoSchema_response.py 생성 완료: {schema_path}")

                    # videoRequest_response.py 생성
                    request_path = generate_video_request_file(
                        exp_opt2_path,
                        file_type="response",
                        output_path="spec/video/videoData_response.py"
                    )
                    print(f"videoRequest_response.py 생성 완료: {request_path}")

            except Exception as e:
                print(f"스키마 파일 생성 실패: {e}")
            
            # 버튼 상태 업데이트
            self.check_start_button_state()
            
            QMessageBox.information(self, "로드 완료", f"{mode.upper()} 모드 파일들이 성공적으로 로드되었습니다!")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"OPT 파일 로드 중 오류가 발생했습니다:\n{str(e)}")

    def _fill_basic_info(self, exp_opt):
        if not exp_opt or "testRequest" not in exp_opt:
            return
        first = exp_opt["testRequest"]
        et = first.get("evaluationTarget", {})
        tg = first.get("testGroup", {})
        self.company_edit.setText(et.get("companyName", ""))
        self.product_edit.setText(et.get("productName", ""))
        self.version_edit.setText(et.get("version", ""))
        self.model_edit.setText(et.get("modelName", ""))
        self.test_category_edit.setText(et.get("testCategory", ""))
        self.target_system_edit.setText(et.get("targetSystem", ""))
        self.test_group_edit.setText(tg.get("name", ""))
        self.test_range_edit.setText(tg.get("testRange", ""))

    def _fill_api_table(self, exp_opt, exp_opt2):
        if not exp_opt or not exp_opt2 or "specification" not in exp_opt2:
            return
        first = exp_opt["testRequest"]
        test_group_name = first.get("testGroup", {}).get("name", "")
        steps = exp_opt2["specification"].get("steps", [])
        self.api_test_table.setRowCount(0)
        for step in steps:
            api_info = step.get("api", {})
            r = self.api_test_table.rowCount()
            self.api_test_table.insertRow(r)

            item0 = QTableWidgetItem(test_group_name)
            item0.setTextAlignment(Qt.AlignCenter)
            item0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.api_test_table.setItem(r, 0, item0)

            item1 = QTableWidgetItem(api_info.get("name", ""))
            item1.setTextAlignment(Qt.AlignCenter)
            item1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.api_test_table.setItem(r, 1, item1)

            item2 = QTableWidgetItem(api_info.get("endpoint", ""))
            item2.setTextAlignment(Qt.AlignCenter)
            item2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.api_test_table.setItem(r, 2, item2)
