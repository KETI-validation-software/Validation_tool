import socket
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QCheckBox
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread

# 외부 유틸/의존 (원본과 동일 모듈 사용)
from core.functions import resource_path
from core.opt_loader import OptLoader

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
    startTestRequested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.opt_loader = OptLoader()
        self.scan_thread = None
        self.scan_worker = None
        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._build_left_panel(), 1)
        main_layout.addWidget(self._build_right_panel(), 1)

        layout = QVBoxLayout()
        layout.addLayout(main_layout, 1)
        layout.addWidget(self._build_bottom_bar())
        self.setLayout(layout)

    # ---------- 좌측 패널 ----------
    def _build_left_panel(self):
        panel = QGroupBox("시험 기본 정보")
        layout = QVBoxLayout()

        # 불러오기
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        load_btn = QPushButton("불러오기")
        load_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        load_btn.clicked.connect(self.load_opt_files)
        btn_row.addWidget(load_btn)
        layout.addLayout(btn_row)

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
    def _build_right_panel(self):
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

        self.digest_radio.toggled.connect(self._toggle_auth_fields)
        self.bearer_radio.toggled.connect(self._toggle_auth_fields)
        self._toggle_auth_fields()

        # 주소 탐색
        scan_label = QLabel("시험 접속 정보")
        scan_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(scan_label)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        scan_btn = QPushButton("🔍주소 탐색")
        scan_btn.setStyleSheet("QPushButton { background-color: #E1EBF4; color: #3987C1; font-weight: bold; }")
        scan_btn.clicked.connect(self._start_scan)
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
        self.url_table.cellClicked.connect(self._select_url_row)
        layout.addWidget(self.url_table)

        # 입력 테이블
        input_label = QLabel("시험데이터")
        input_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(input_label)

        self.input_table = QTableWidget(0, 3)
        self.input_table.setHorizontalHeaderLabels(["API명", "입력 요청 정보", "입력 값"])
        self.input_table.verticalHeader().setVisible(False)
        self.input_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.input_table)

        # 기본 행
        from PyQt5.QtWidgets import QLineEdit as QLE
        self.input_table.setRowCount(0)
        r = self.input_table.rowCount()
        self.input_table.insertRow(r)
        item_api = QTableWidgetItem("Authentication")
        item_api.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_api.setTextAlignment(Qt.AlignCenter)
        self.input_table.setItem(r, 0, item_api)

        item_req = QTableWidgetItem("camID")
        item_req.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item_req.setTextAlignment(Qt.AlignCenter)
        self.input_table.setItem(r, 1, item_req)

        edit = QLE(); edit.setPlaceholderText("입력하세요")
        self.input_table.setCellWidget(r, 2, edit)

        panel.setLayout(layout)
        return panel

    def _build_bottom_bar(self):
        w = QWidget()
        lay = QHBoxLayout()
        lay.addStretch()

        start_btn = QPushButton("시험 시작")
        start_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        lay.addWidget(start_btn)

        reset_btn = QPushButton("초기화")
        reset_btn.setStyleSheet("QPushButton { background-color: #9FBFE5; color: black; font-weight: bold; }")
        lay.addWidget(reset_btn)

        lay.addStretch()
        w.setLayout(lay)

        start_btn.clicked.connect(self._on_start_clicked)
        return w

    # ---------- 동작 ----------
    def _on_start_clicked(self):
        self.startTestRequested.emit()

    def _toggle_auth_fields(self):
        use_digest = self.digest_radio.isChecked()
        self.id_input.setEnabled(use_digest)
        self.pw_input.setEnabled(use_digest)
        self.token_input.setEnabled(not use_digest)

    def _start_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            QMessageBox.information(self, "알림", "이미 주소 탐색이 진행 중입니다.")
            return
        self.scan_worker = NetworkScanWorker()
        self.scan_thread = QThread()
        self.scan_worker.moveToThread(self.scan_thread)
        self.scan_worker.scan_completed.connect(self._on_scan_completed)
        self.scan_worker.scan_failed.connect(self._on_scan_failed)
        self.scan_thread.started.connect(self.scan_worker.scan_network)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)
        self.scan_thread.start()

    def _on_scan_completed(self, urls):
        self._fill_url_table(urls)
        QMessageBox.information(self, "탐색 완료", "사용 가능한 주소를 찾았습니다.")

    def _on_scan_failed(self, msg):
        QMessageBox.warning(self, "주소 탐색 실패", msg)

    def _fill_url_table(self, urls):
        self.url_table.setRowCount(0)
        for url in urls:
            row = self.url_table.rowCount()
            self.url_table.insertRow(row)

            chk_w = QWidget()
            chk_row = QHBoxLayout(); chk_row.setAlignment(Qt.AlignCenter); chk_row.setContentsMargins(0, 0, 0, 0)
            chk = QCheckBox(); chk.setChecked(False)
            # 단일선택 보장
            chk.clicked.connect(lambda checked, r=row: self._on_checkbox_clicked(r, checked))
            chk_row.addWidget(chk); chk_w.setLayout(chk_row)
            self.url_table.setCellWidget(row, 0, chk_w)

            url_item = QTableWidgetItem(url)
            url_item.setTextAlignment(Qt.AlignCenter)
            self.url_table.setItem(row, 1, url_item)

    def _on_checkbox_clicked(self, clicked_row, checked):
        if checked:
            for r in range(self.url_table.rowCount()):
                if r == clicked_row:
                    continue
                w = self.url_table.cellWidget(r, 0)
                if w:
                    cb = w.findChild(QCheckBox)
                    if cb:
                        cb.setChecked(False)

    def _select_url_row(self, row, col):
        # 행 클릭 시 해당 행만 체크
        for r in range(self.url_table.rowCount()):
            w = self.url_table.cellWidget(r, 0)
            if w:
                cb = w.findChild(QCheckBox)
                if cb:
                    cb.setChecked(False)
        w = self.url_table.cellWidget(row, 0)
        if w:
            cb = w.findChild(QCheckBox)
            if cb:
                cb.setChecked(True)

    # ---------- OPT 로드 ----------
    def load_opt_files(self):
        try:
            exp_opt_path = resource_path("temp/(temp)exp_opt_requestVal.json")
            exp_opt2_path = resource_path("temp/(temp)exp_opt2_requestVal_LongPolling.json")
            exp_opt = self.opt_loader.load_opt_json(exp_opt_path)
            exp_opt2 = self.opt_loader.load_opt_json(exp_opt2_path)
            if not (exp_opt and exp_opt2):
                QMessageBox.warning(self, "로드 실패", "OPT 파일을 읽을 수 없습니다.")
                return
            self._fill_basic_info(exp_opt)
            self._fill_api_table(exp_opt, exp_opt2)
            QMessageBox.information(self, "로드 완료", "OPT 파일들이 성공적으로 로드되었습니다!")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"OPT 파일 로드 중 오류가 발생했습니다:\n{str(e)}")

    def _fill_basic_info(self, exp_opt):
        if not exp_opt or "testRequests" not in exp_opt:
            return
        first = exp_opt["testRequests"][0]
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
        first = exp_opt["testRequests"][0]
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
