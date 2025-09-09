# launcher_first_toggle_back.py
import sys
import hashlib
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QRadioButton, QPushButton, QLabel, QStackedWidget, QAction,
    QLineEdit, QMessageBox, QFormLayout, QGroupBox, QCheckBox,
    QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem
)
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt, QObject, pyqtSignal

# 두 앱 모듈 (둘 다 MyApp(QWidget) 제공) - GUI 자동실행 방지를 위해 클래스만 import
import platformVal_all as platform_app
import systemVal_all as system_app

from core.functions import resource_path
from core.opt_loader import OptLoader
import socket


class LoginWidget(QWidget):
    """로그인 화면: 관리자 코드와 접속 URL 입력"""

    def __init__(self, login_callback):
        super().__init__()
        self.login_callback = login_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 제목
        title = QLabel("검증 소프트웨어 로그인")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 20pt; font-weight: bold; margin: 20px;')
        layout.addWidget(title)

        # 로그인 폼 그룹
        login_group = QGroupBox("접속 정보")
        form_layout = QFormLayout()

        self.admin_code_input = QLineEdit()
        self.admin_code_input.setPlaceholderText("관리자 코드를 입력하세요")
        form_layout.addRow("관리자 코드:", self.admin_code_input)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://127.0.0.1:8008")
        self.url_input.setText("https://127.0.0.1:8008")
        form_layout.addRow("접속 URL:", self.url_input)

        login_group.setLayout(form_layout)
        layout.addWidget(login_group)

        # 로그인 버튼
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.login_btn = QPushButton("접속")
        self.login_btn.setFixedSize(100, 40)
        self.login_btn.clicked.connect(self._on_login)
        self.login_btn.setDefault(True)  # Enter 키로 실행 가능
        btn_layout.addWidget(self.login_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Enter 키 이벤트 처리
        self.admin_code_input.returnPressed.connect(self._on_login)
        self.url_input.returnPressed.connect(self._on_login)

        layout.addStretch()
        self.setLayout(layout)

    def _on_login(self):
        admin_code = self.admin_code_input.text().strip()
        url = self.url_input.text().strip()

        if not admin_code:
            QMessageBox.warning(self, "입력 오류", "관리자 코드를 입력해주세요.")
            self.admin_code_input.setFocus()
            return

        if not url:
            QMessageBox.warning(self, "입력 오류", "접속 URL을 입력해주세요.")
            self.url_input.setFocus()
            return

        # 로그인 검증 수행
        if self._validate_credentials(admin_code, url):
            self.login_callback(url)
        else:
            QMessageBox.critical(self, "접속 실패", "관리자 코드 또는 접속 URL이 올바르지 않습니다.\n다시 입력 및 확인해주세요.")
            self.admin_code_input.clear()
            self.admin_code_input.setFocus()

    def _validate_credentials(self, admin_code, url):
        """관리자 코드와 URL 검증"""
        try:
            # 1. 관리자 코드 검증 (예시: 해시 검증)
            # 실제 환경에서는 더 안전한 검증 방식을 사용해야 합니다
            expected_code = "1234"

            if admin_code != expected_code:
                return False

            # 2. URL 접속 테스트
            if not url.startswith(('http://', 'https://')):
                return False

            # 간단한 연결 테스트 (타임아웃 3초)
            try:
                response = requests.get(f"{url}/health", timeout=3, verify=False)
                # 응답이 있으면 접속 가능한 것으로 판단
                return True
            except:
                # health 엔드포인트가 없을 수 있으므로, 기본 URL로 테스트
                try:
                    response = requests.get(url, timeout=3, verify=False)
                    return True
                except:
                    # URL이 유효한 형식이면 통과 (실제 연결 실패는 나중에 처리)
                    import urllib.parse
                    parsed = urllib.parse.urlparse(url)
                    return bool(parsed.netloc)

        except Exception as e:
            print(f"로그인 검증 중 오류: {e}")
            return False


class NetworkScanWorker(QObject):
    """네트워크 스캔 작업을 위한 Worker 클래스"""
    scan_completed = pyqtSignal(list)  # 스캔 완료 시 URL 리스트 전송
    scan_failed = pyqtSignal(str)      # 스캔 실패 시 에러 메시지 전송
    
    def __init__(self):
        super().__init__()
    
    def scan_network(self):
        """네트워크 스캔 수행"""
        try:
            
            # 1. 내 IP 주소 탐지
            local_ip = self._get_local_ip()
            
            if not local_ip:
                self.scan_failed.emit("내 IP 주소를 찾을 수 없습니다.")
                return
            
            # 2. 사용 가능한 포트 스캔 (8000-8099 범위)
            available_ports = self._scan_available_ports(local_ip, range(8000, 8100))
            print(f"사용 가능한 포트들: {available_ports}")
            
            # 3. 결과 처리
            if available_ports:
                # 상위 3개 포트 선택
                recommended_ports = available_ports[:3]
                urls = [f"{local_ip}:{port}" for port in recommended_ports]
                print(f"추천 URL: {urls}")
                
                # 시그널로 결과 전송
                self.scan_completed.emit(urls)
            else:
                self.scan_failed.emit("검색된 사용가능 포트 없음")
                
        except Exception as e:
            self.scan_failed.emit(f"네트워크 탐색 중 오류 발생:\n{str(e)}")
    
    def _get_local_ip(self):
        """로컬 IP 주소 탐지"""
        try:
            # 외부 서버에 연결해서 로컬 IP 확인 (실제 연결하지 않음)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                return local_ip
        except Exception:
            try:
                # 대안: 호스트명으로 IP 얻기
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return None
    
    def _scan_available_ports(self, ip, port_range):
        """지정된 IP에서 바인드 가능한 포트 스캔"""
        available_ports = []
        scanned_count = 0
        
        for port in port_range:
            scanned_count += 1
            try:
                # 포트가 사용 가능한지 확인 (바인드 테스트)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.settimeout(0.1)  # 타임아웃 설정으로 속도 향상
                    result = sock.bind((ip, port))
                    available_ports.append(port)
                    
                    # 너무 많이 찾으면 상위 10개로 제한
                    if len(available_ports) >= 10:
                        break
                        
            except OSError as e:
                # 포트가 이미 사용 중이거나 바인드 불가
                if scanned_count % 20 == 0:  # 20개마다 로그
                    print(f"스캔 중... {scanned_count}/{len(list(port_range))}, 발견: {len(available_ports)}개")
                continue
            except Exception as e:
                # 기타 오류는 무시하고 계속
                continue
        
        return available_ports


class SelectionWidget(QWidget):
    """두 번째 화면: 플랫폼/시스템 선택 및 적용"""

    def __init__(self, apply_callback):
        super().__init__()
        self.apply_callback = apply_callback

        # OPT 로더
        self.opt_loader = OptLoader()
        
        # 네트워크 스캔 워커 초기화
        self.scan_worker = None
        self.scan_thread = None
        
        self.initUI()

    def initUI(self):

        # 메인 레이아웃 (좌/우 2컬럼)
        main_layout = QHBoxLayout()
        
        # 좌측 패널: 시험 기본
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel,1)

        # 우측 패널: 시험 입력 정보
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)

        # 전체 레이아웃
        layout = QVBoxLayout() 
        layout.addLayout(main_layout, 1)

        # 하단 버튼 바
        bottom_buttons = self.create_bottom_buttons()
        layout.addWidget(bottom_buttons)

        self.setLayout(layout)
    
    def create_left_panel(self):
        """좌측 패널: 시험 기본 정보"""
        panel = QGroupBox("시험 기본 정보")
        layout = QVBoxLayout()

        # 불러오기 버튼
        btn_row = QHBoxLayout() 
        btn_row.addStretch() 

        load_btn = QPushButton("불러오기")
        load_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        load_btn.clicked.connect(self.load_opt_files)
        btn_row.addWidget(load_btn) 
        layout.addLayout(btn_row)
    
        # 기본 정보 폼
        form_layout = QFormLayout()

        self.company_edit = QLineEdit()
        self.product_edit = QLineEdit()
        self.version_edit = QLineEdit()
        self.model_edit = QLineEdit()
        self.test_category_edit = QLineEdit()
        self.target_system_edit = QLineEdit()
        self.test_group_edit = QLineEdit()
        self.test_range_edit = QLineEdit()

        form_layout.addRow("기업명", self.company_edit)
        form_layout.addRow("제품명", self.product_edit)
        form_layout.addRow("버전", self.version_edit)
        form_layout.addRow("모델명", self.model_edit)
        form_layout.addRow("시험유형", self.test_category_edit)
        form_layout.addRow("시험대상", self.target_system_edit)
        form_layout.addRow("시험분야", self.test_group_edit)
        form_layout.addRow("시험범위", self.test_range_edit)

        layout.addLayout(form_layout)

        # 시험항목(API) 테이블
        api_label = QLabel("시험항목(API)")
        api_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(api_label)

        self.api_test_table = QTableWidget(0, 3)
        self.api_test_table.setHorizontalHeaderLabels(["시험 항목", "기능명", "API명"])

        # 테이블 크기 조정
        header = self.api_test_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.api_test_table)

        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """우측 패널: 시험 입력 정보"""
        panel = QGroupBox("시험 입력 정보")
        layout = QVBoxLayout()
        
        # 인증 정보 토글
        auth_label = QLabel("사용자 인증 방식")
        auth_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(auth_label)

        auth_widget = QWidget()
        auth_layout = QVBoxLayout(auth_widget)
                
        self.digest_radio = QRadioButton("Digest Auth")
        self.digest_radio.setChecked(True)
        auth_layout.addWidget(self.digest_radio)
        
        digest_row = QWidget()
        digest_layout = QHBoxLayout(digest_row)
        digest_layout.setContentsMargins(20, 0, 0, 0)
        self.id_input = QLineEdit()
        self.pw_input = QLineEdit()
        digest_layout.addWidget(QLabel("ID:"))
        digest_layout.addWidget(self.id_input)
        digest_layout.addWidget(QLabel("PW:"))
        digest_layout.addWidget(self.pw_input)
        auth_layout.addWidget(digest_row)

        auth_layout.addSpacing(8)

        # Bearer Token
        self.bearer_radio = QRadioButton("Bearer Token")
        auth_layout.addWidget(self.bearer_radio)

        token_row = QWidget()
        token_layout = QHBoxLayout(token_row)
        token_layout.setContentsMargins(20, 0, 0, 0)
        self.token_input = QLineEdit()
        token_layout.addWidget(QLabel("Token:"))
        token_layout.addWidget(self.token_input)
        auth_layout.addWidget(token_row)

        layout.addWidget(auth_widget)

        self.digest_radio.toggled.connect(self.update_auth_fields)
        self.bearer_radio.toggled.connect(self.update_auth_fields)

        self.update_auth_fields()
        
        # 주소 검색
        scan_label = QLabel("시험 접속 정보")
        scan_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(scan_label)    

        scan_layout = QVBoxLayout()
        
        # 버튼을 우측 상단에 배치
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        scan_btn = QPushButton("🔍주소 탐색")
        scan_btn.setStyleSheet("QPushButton { background-color: #E1EBF4; color: #3987C1; font-weight: bold; }")
        btn_row.addWidget(scan_btn)
        scan_layout.addLayout(btn_row)
        
        self.url_table = QTableWidget(0, 2)  # 체크, URL
        self.url_table.setHorizontalHeaderLabels(["☑", "URL"])
        self.url_table.verticalHeader().setVisible(False)
        self.url_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.url_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.url_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.url_table.horizontalHeader().setStretchLastSection(True)
        self.url_table.setColumnWidth(0, 36)
        scan_layout.addWidget(self.url_table)

        scan_widget = QWidget()
        scan_widget.setLayout(scan_layout)
        layout.addWidget(scan_widget)

        scan_btn.clicked.connect(self.populate_demo_urls)
        self.url_table.cellClicked.connect(self.select_url_row)
        
        # 시험데이터 테이블
        input_label = QLabel("시험데이터")
        input_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(input_label)
        
        self.input_table = QTableWidget(0, 3)
        self.input_table.setHorizontalHeaderLabels(["API명", "입력 요청 정보", "입력 값"])

        self.input_table.verticalHeader().setVisible(False)
        
        # 테이블 크기 조정
        input_header = self.input_table.horizontalHeader()
        input_header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.input_table)

        rows = [("Authentication", "camID")]  # (API명, 입력 요청 정보)

        self.input_table.setRowCount(0)

        for api_name, req_info in rows:
            r = self.input_table.rowCount()
            self.input_table.insertRow(r)

            # 1열: API명
            item_api = QTableWidgetItem(api_name)
            item_api.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_api.setTextAlignment(Qt.AlignCenter)
            self.input_table.setItem(r, 0, item_api)

            # 2열: 입력 요청 정보
            item_req = QTableWidgetItem(req_info)
            item_req.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_req.setTextAlignment(Qt.AlignCenter)
            self.input_table.setItem(r, 1, item_req)

            # 3열: 입력 값
            edit = QLineEdit()
            edit.setPlaceholderText(f"입력하세요")
            self.input_table.setCellWidget(r, 2, edit)

        
        panel.setLayout(layout)
        return panel
    
    def update_auth_fields(self):
        if self.digest_radio.isChecked():
            # Digest Auth 활성화
            self.id_input.setEnabled(True)
            self.pw_input.setEnabled(True)
            # Token 비활성화
            self.token_input.setEnabled(False)
        else:
            # Bearer Token 활성화
            self.id_input.setEnabled(False)
            self.pw_input.setEnabled(False)
            self.token_input.setEnabled(True)

    def populate_demo_urls(self):
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
        """스캔 완료 시 호출되는 슬롯"""
        print(f"스캔 완료 신호 수신: {urls}")
        self._populate_url_table(urls)
    
    def _on_scan_failed(self, error_message):
        """스캔 실패 시 호출되는 슬롯"""
        print(f"스캔 실패 신호 수신: {error_message}")
        self._show_scan_error(error_message)
    
    def _populate_url_table(self, urls):
        """URL 테이블에 스캔 결과 채우기"""
        try:
            self.url_table.setRowCount(0)
            
            for i, url in enumerate(urls):
                row = self.url_table.rowCount()
                self.url_table.insertRow(row)

                # 체크 아이템 (사용자 체크 가능)
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
            
            # 성공 메시지
            message = f"사용 가능한 주소를 찾았습니다."
            QMessageBox.information(self, "탐색 완료", message)
            
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

    def create_bottom_buttons(self):
        """하단 버튼 바"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # 시험 시작 버튼
        start_btn = QPushButton("시험 시작")
        start_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        layout.addWidget(start_btn)

        # 초기화 버튼
        reset_btn = QPushButton("초기화")
        reset_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        layout.addWidget(reset_btn)

        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def load_opt_files(self):
        """temp 폴더의 OPT 파일들을 자동 로드"""
        try:
            # temp 폴더의 예시 파일들 로드
            exp_opt_path = resource_path("temp/(temp)exp_opt_requestVal.json")
            exp_opt2_path = resource_path("temp/(temp)exp_opt2_requestVal.json")
            
            # exp_opt.json 로드 (시험 요청 데이터)
            exp_opt_data = self.opt_loader.load_opt_json(exp_opt_path)
            
            # exp_opt2.json 로드 (명세서 데이터)  
            exp_opt2_data = self.opt_loader.load_opt_json(exp_opt2_path)
            
            if exp_opt_data and exp_opt2_data:
                # 기본 정보 필드 채우기
                self.populate_basic_info(exp_opt_data)
                
                # 시험항목(API) 테이블 채우기
                self.populate_api_table(exp_opt_data, exp_opt2_data)
                
                QMessageBox.information(self, "로드 완료", "OPT 파일들이 성공적으로 로드되었습니다!")
            else:
                QMessageBox.warning(self, "로드 실패", "OPT 파일을 읽을 수 없습니다.")
                
        except Exception as e:
            QMessageBox.critical(self, "오류", f"OPT 파일 로드 중 오류가 발생했습니다:\n{str(e)}")
    
    def populate_basic_info(self, exp_opt_data):
        """exp_opt.json 데이터로 기본 정보 필드 채우기"""
        try:
            if not exp_opt_data or "testRequests" not in exp_opt_data:
                return
                
            # 첫 번째 시험 요청 데이터 사용
            first_request = exp_opt_data["testRequests"][0]
            evaluation_target = first_request.get("evaluationTarget", {})
            test_group = first_request.get("testGroup", {})
            
            # 매핑
            self.company_edit.setText(evaluation_target.get("companyName", ""))
            self.product_edit.setText(evaluation_target.get("productName", ""))
            self.version_edit.setText(evaluation_target.get("version", ""))
            self.model_edit.setText(evaluation_target.get("modelName", ""))
            self.test_category_edit.setText(evaluation_target.get("testCategory", ""))
            self.target_system_edit.setText(evaluation_target.get("targetSystem", ""))
            self.test_group_edit.setText(test_group.get("name", ""))
            self.test_range_edit.setText(test_group.get("testRange", ""))
            
            print(f"기본 정보 채우기 완료")
            
        except Exception as e:
            print(f"기본 정보 채우기 실패: {e}")
    
    def populate_api_table(self, exp_opt_data, exp_opt2_data):
        """API 테이블 데이터 채우기"""
        try:
            if not exp_opt_data or not exp_opt2_data:
                return
                
            # exp_opt.json에서 시험 그룹 이름 가져오기
            first_request = exp_opt_data["testRequests"][0]
            test_group_name = first_request.get("testGroup", {}).get("name", "")
            
            # exp_opt2.json에서 API 단계 정보 가져오기
            if "specification" not in exp_opt2_data:
                return
                
            steps = exp_opt2_data["specification"].get("steps", [])
            
            # 테이블 초기화
            self.api_test_table.setRowCount(0)
            
            # 각 단계를 테이블에 추가
            for step in steps:
                api_info = step.get("api", {})
                
                row = self.api_test_table.rowCount()
                self.api_test_table.insertRow(row)
                
                # 1열: 시험 항목 (test_group_name)
                test_item = QTableWidgetItem(test_group_name)
                test_item.setTextAlignment(Qt.AlignCenter)
                test_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.api_test_table.setItem(row, 0, test_item)
                
                # 2열: 기능명 (API name)
                function_name = QTableWidgetItem(api_info.get("name", ""))
                function_name.setTextAlignment(Qt.AlignCenter)
                function_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.api_test_table.setItem(row, 1, function_name)
                
                # 3열: API명 (Endpoint)
                api_endpoint = QTableWidgetItem(api_info.get("endpoint", ""))
                api_endpoint.setTextAlignment(Qt.AlignCenter)
                api_endpoint.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.api_test_table.setItem(row, 2, api_endpoint)
            
        except Exception as e:
            print(f"API 테이블 채우기 실패: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("검증 소프트웨어 통합 실행기")
        self.resize(1200, 720)

        # 중앙 스택: 0=로그인화면, 1=선택화면, 2=플랫폼, 3=시스템
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 로그인 화면
        self.login_widget = LoginWidget(self.on_login_success)
        self.stack.addWidget(self.login_widget)  # index 0

        # 선택화면
        self.selection_widget = SelectionWidget(self.apply_selection)
        self.stack.addWidget(self.selection_widget)  # index 1

        # 실제 GUI 위젯 준비 (임베드 전용) - 필요할 때만 생성
        self.platform_widget = None
        self.system_widget = None

        # 현재 선택 상태 (0=플랫폼, 1=시스템, None=미선택)
        self.selected_index = None
        self.server_url = None

        # 메뉴바 설정
        self.setup_menubar()

        # 초기에는 로그인 화면 표시
        self.stack.setCurrentIndex(0)

    def setup_menubar(self):
        """메뉴바 설정"""
        menubar = self.menuBar()

        # 메뉴 (기존 파일, 모드 메뉴 통합)
        main_menu = menubar.addMenu("메뉴")

        # 로그인
        self.act_login = QAction("로그인", self)
        self.act_login.triggered.connect(self.go_to_login)
        main_menu.addAction(self.act_login)

        # 로그아웃
        self.act_logout = QAction("로그아웃", self)
        self.act_logout.triggered.connect(self.logout)
        self.act_logout.setEnabled(False)  # 초기에는 비활성화
        main_menu.addAction(self.act_logout)

        main_menu.addSeparator()

        # 시험 정보
        self.act_test_info = QAction("시험 정보", self)
        self.act_test_info.triggered.connect(self.go_to_test_info)
        self.act_test_info.setEnabled(False)  # 초기에는 비활성화
        main_menu.addAction(self.act_test_info)

        # 시험 진행
        self.act_test_progress = QAction("시험 진행", self)
        self.act_test_progress.triggered.connect(self.go_to_test_progress)
        self.act_test_progress.setEnabled(False)  # 초기에는 비활성화
        main_menu.addAction(self.act_test_progress)

        main_menu.addSeparator()

        # 종료
        act_exit = QAction("종료", self)
        act_exit.triggered.connect(self.close)
        main_menu.addAction(act_exit)

        # 보기 메뉴: 전체화면
        view_menu = menubar.addMenu("보기")

        act_full = QAction("전체화면 전환", self, checkable=True)
        act_full.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(act_full)

    def on_login_success(self, url):
        """로그인 성공 시 메뉴 활성화 및 선택 화면으로 이동"""
        self.server_url = url
        self.stack.setCurrentIndex(1)  # 선택 화면으로 이동

        # 메뉴 상태 업데이트
        self.act_login.setEnabled(False)
        self.act_logout.setEnabled(True)
        self.act_test_info.setEnabled(True)
        self.act_test_progress.setEnabled(True)

    def logout(self):
        """로그아웃: 로그인 화면으로 돌아가기"""
        reply = QMessageBox.question(self, '로그아웃', '로그아웃 하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.server_url = None
            self.selected_index = None
            self.stack.setCurrentIndex(0)  # 로그인 화면으로

            # 메뉴 상태 업데이트
            self.act_login.setEnabled(True)
            self.act_logout.setEnabled(False)
            self.act_test_info.setEnabled(False)
            self.act_test_progress.setEnabled(False)

            # 로그인 입력 필드 초기화
            self.login_widget.admin_code_input.clear()
            self.login_widget.admin_code_input.setFocus()

    def go_to_login(self):
        """로그인 화면으로 이동"""
        self.stack.setCurrentIndex(0)

    def go_to_test_info(self):
        """시험 정보 화면으로 이동 (선택 화면)"""
        self.stack.setCurrentIndex(1)

    def go_to_test_progress(self):
        """시험 진행 화면으로 이동 (선택된 검증 소프트웨어 실행)"""
        if self.selected_index is not None:
            self.show_selected_app()
        else:
            # 아직 선택하지 않았다면 선택 화면으로
            self.stack.setCurrentIndex(1)
            QMessageBox.information(self, "안내", "먼저 검증 유형을 선택하고 적용해주세요.")

    def apply_selection(self, idx: int):
        """선택화면에서 '적용' 눌렀을 때: 선택 저장 후 즉시 표시"""
        self.selected_index = idx
        self.show_selected_app()

    def show_selected_app(self):
        """현재 선택된 GUI 표시 (없으면 선택화면 유지)"""
        if self.selected_index is None:
            self.stack.setCurrentIndex(1)
            return

        # 선택된 위젯이 아직 생성되지 않았다면 생성
        if self.selected_index == 0 and self.platform_widget is None:
            self.platform_widget = platform_app.MyApp(embedded=True)  # embedded=True 전달
            self.platform_widget.setWindowFlags(Qt.Widget)  # 외부 독립창 방지

            # 서버 URL 설정 (필요한 경우)
            if hasattr(self.platform_widget, 'linkUrl'):
                self.platform_widget.linkUrl.setText(self.server_url)

            self.stack.addWidget(self.platform_widget)  # index 2

        elif self.selected_index == 1 and self.system_widget is None:
            self.system_widget = system_app.MyApp(embedded=True)  # embedded=True 전달
            self.system_widget.setWindowFlags(Qt.Widget)  # 외부 독립창 방지

            # 서버 URL 설정 (필요한 경우)
            if hasattr(self.system_widget, 'linkUrl'):
                self.system_widget.linkUrl.setText(self.server_url)

            self.stack.addWidget(self.system_widget)  # index 3

        # 해당 위젯으로 전환
        if self.selected_index == 0:
            widget_index = self.stack.indexOf(self.platform_widget)
        else:
            widget_index = self.stack.indexOf(self.system_widget)

        self.stack.setCurrentIndex(widget_index)

    def toggle_fullscreen(self, checked: bool):
        self.showFullScreen() if checked else self.showNormal()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # SSL 경고 무시 설정 (필요한 경우)
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # 폰트 통합 적용
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())