# launcher_first_toggle_back.py
import sys
import hashlib
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QRadioButton, QPushButton, QLabel, QStackedWidget, QAction,
    QLineEdit, QMessageBox, QFormLayout, QGroupBox,
    QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem
)
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt

# 두 앱 모듈 (둘 다 MyApp(QWidget) 제공) - GUI 자동실행 방지를 위해 클래스만 import
import platformVal_all as platform_app
import systemVal_all as system_app

from core.functions import resource_path


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
        self.admin_code_input.setEchoMode(QLineEdit.Password)
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


class SelectionWidget(QWidget):
    """두 번째 화면: 플랫폼/시스템 선택 및 적용"""

    def __init__(self, apply_callback):
        super().__init__()
        self.apply_callback = apply_callback

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
        #테이블 행 번호 숨기기
        self.api_test_table.verticalHeader().setVisible(False)
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
        """하드코딩된 IP:Port 목록을 표에 표시"""
        demo_urls = [
            "192.168.0.1:8080",
            "192.168.0.2:8080",
        ]
        self.url_table.setRowCount(0)
        for url in demo_urls:
            row = self.url_table.rowCount()
            self.url_table.insertRow(row)

            # 체크 아이템 (사용자 체크 가능)
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            check_item.setCheckState(Qt.Unchecked)
            check_item.setTextAlignment(Qt.AlignCenter)
            self.url_table.setItem(row, 0, check_item)

            # URL 텍스트
            url_item = QTableWidgetItem(url)
            url_item.setTextAlignment(Qt.AlignCenter)  
            self.url_table.setItem(row, 1, url_item)

    def select_url_row(self, row, col):
        """행 클릭 시: 체크 단일 선택"""
        # 모든 행 체크 해제
        for r in range(self.url_table.rowCount()):
            item = self.url_table.item(r, 0)
            if item is not None:
                item.setCheckState(Qt.Unchecked)

        # 선택된 행 체크
        sel_item = self.url_table.item(row, 0)
        if sel_item is not None:
            sel_item.setCheckState(Qt.Checked)

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