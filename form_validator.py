import re
from PyQt5.QtWidgets import QMessageBox
from core.functions import resource_path
from core.opt_loader import OptLoader
from core.schema_generator import generate_schema_file
from core.video_request_generator import generate_video_request_file


class FormValidator:
    """
    폼 검증 및 데이터 처리를 담당하는 클래스
    - OPT 파일 로드 및 처리
    - CONSTANTS.py 업데이트
    - 관리자 코드 검증
    - 폼 유효성 검사
    """

    def __init__(self, parent_widget):
        """
        Args:
            parent_widget: InfoWidget 인스턴스 (UI 컴포넌트 접근용)
        """
        self.parent = parent_widget
        self.opt_loader = OptLoader()

    # ---------- OPT 파일 로드 관련 ----------

    def load_opt_files(self, mode):
        """OPT 파일 로드 및 스키마 생성"""
        try:
            # 모드에 따라 다른 파일 경로 설정
            exp_opt_path, exp_opt2_path = self._get_file_paths(mode)
            if not exp_opt_path or not exp_opt2_path:
                QMessageBox.warning(self.parent, "모드 오류", f"알 수 없는 모드: {mode}")
                return

            # OPT 파일 로드
            exp_opt = self.opt_loader.load_opt_json(exp_opt_path)
            exp_opt2 = self.opt_loader.load_opt_json(exp_opt2_path)

            if not (exp_opt and exp_opt2):
                QMessageBox.warning(self.parent, "로드 실패", f"{mode.upper()} 모드 OPT 파일을 읽을 수 없습니다.")
                return

            # 현재 모드 저장 및 UI 업데이트
            self.parent.current_mode = mode
            self._fill_basic_info(exp_opt)
            self._fill_api_table(exp_opt, exp_opt2)

            # 모드에 따른 파일 생성
            self._generate_schema_files(mode, exp_opt2_path)

            # 버튼 상태 업데이트
            self.parent.check_start_button_state()

            QMessageBox.information(self.parent, "로드 완료", f"{mode.upper()} 모드 파일들이 성공적으로 로드되었습니다!")

        except Exception as e:
            QMessageBox.critical(self.parent, "오류", f"OPT 파일 로드 중 오류가 발생했습니다:\n{str(e)}")

    def _get_file_paths(self, mode):
        """모드에 따른 파일 경로 반환"""
        if mode == "request_longpolling":
            return (
                resource_path("temp/(temp)exp_opt_requestVal.json"),
                resource_path("temp/(temp)exp_opt2_requestVal_LongPolling.json")
            )
        elif mode == "response_longpolling":
            return (
                resource_path("temp/(temp)exp_opt_responseVal.json"),
                resource_path("temp/(temp)exp_opt2_responseVal_LongPolling.json")
            )
        elif mode == "request_webhook":
            return (
                resource_path("temp/(temp)exp_opt_requestVal.json"),
                resource_path("temp/(temp)exp_opt2_requestVal_WebHook.json")
            )
        elif mode == "response_webhook":
            return (
                resource_path("temp/(temp)exp_opt_responseVal.json"),
                resource_path("temp/(temp)exp_opt2_responseVal_WebHook.json")
            )
        else:
            return None, None

    def _generate_schema_files(self, mode, exp_opt2_path):
        """모드에 따른 스키마 파일 생성"""
        try:
            if mode in ["request_longpolling", "request_webhook"]:
                # Request 모드
                schema_path = generate_schema_file(
                    exp_opt2_path,
                    schema_type="request",
                    output_path="spec/video/videoSchema_request.py"
                )
                print(f"videoSchema_request.py 생성 완료: {schema_path}")

                request_path = generate_video_request_file(
                    exp_opt2_path,
                    file_type="request",
                    output_path="spec/video/videoData_request.py"
                )
                print(f"videoData_request.py 생성 완료: {request_path}")

            elif mode in ["response_longpolling", "response_webhook"]:
                # Response 모드
                schema_path = generate_schema_file(
                    exp_opt2_path,
                    schema_type="response",
                    output_path="spec/video/videoSchema_response.py"
                )
                print(f"videoSchema_response.py 생성 완료: {schema_path}")

                request_path = generate_video_request_file(
                    exp_opt2_path,
                    file_type="response",
                    output_path="spec/video/videoData_response.py"
                )
                print(f"videoData_response.py 생성 완료: {request_path}")

        except Exception as e:
            print(f"스키마 파일 생성 실패: {e}")

    def _fill_basic_info(self, exp_opt):
        """기본 정보 필드 채우기"""
        if not exp_opt or "testRequest" not in exp_opt:
            return

        first = exp_opt["testRequest"]
        et = first.get("evaluationTarget", {})
        tg = first.get("testGroup", {})

        self.parent.company_edit.setText(et.get("companyName", ""))
        self.parent.product_edit.setText(et.get("productName", ""))
        self.parent.version_edit.setText(et.get("version", ""))
        self.parent.model_edit.setText(et.get("modelName", ""))
        self.parent.test_category_edit.setText(et.get("testCategory", ""))
        self.parent.target_system_edit.setText(et.get("targetSystem", ""))
        self.parent.test_group_edit.setText(tg.get("name", ""))
        self.parent.test_range_edit.setText(tg.get("testRange", ""))

    def _fill_api_table(self, exp_opt, exp_opt2):
        """API 테이블 채우기"""
        if not exp_opt or not exp_opt2 or "specification" not in exp_opt2:
            return

        first = exp_opt["testRequest"]
        test_group_name = first.get("testGroup", {}).get("name", "")
        steps = exp_opt2["specification"].get("steps", [])

        self.parent.api_test_table.setRowCount(0)
        prev_endpoint = None

        for step in steps:
            api_info = step.get("api", {})
            r = self.parent.api_test_table.rowCount()
            self.parent.api_test_table.insertRow(r)

            # 시험 항목
            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtCore import Qt

            item0 = QTableWidgetItem(test_group_name)
            item0.setTextAlignment(Qt.AlignCenter)
            item0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.parent.api_test_table.setItem(r, 0, item0)

            # 기능명
            item1 = QTableWidgetItem(api_info.get("name", ""))
            item1.setTextAlignment(Qt.AlignCenter)
            item1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.parent.api_test_table.setItem(r, 1, item1)

            # API명
            endpoint = api_info.get("endpoint")
            if not endpoint and prev_endpoint:
                endpoint = prev_endpoint

            item2 = QTableWidgetItem(endpoint or "")
            item2.setTextAlignment(Qt.AlignCenter)
            item2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.parent.api_test_table.setItem(r, 2, item2)

            # 이번 step endpoint 저장
            if api_info.get("endpoint"):
                prev_endpoint = api_info["endpoint"]

    # ---------- 관리자 코드 검증 ----------

    def validate_admin_code(self):
        """관리자 코드 숫자 입력 검증"""
        text = self.parent.admin_code_edit.text()
        filtered_text = ''.join(filter(str.isdigit, text))

        if text != filtered_text:
            # 커서 위치 저장 및 복원
            cursor_pos = self.parent.admin_code_edit.cursorPosition()
            self.parent.admin_code_edit.setText(filtered_text)
            new_pos = cursor_pos - (len(text) - len(filtered_text))
            self.parent.admin_code_edit.setCursorPosition(max(0, new_pos))

    def is_admin_code_required(self):
        """관리자 코드 입력이 필요한지 확인"""
        test_category = self.parent.test_category_edit.text().strip()
        return test_category == "본시험"

    def is_admin_code_valid(self):
        """관리자 코드 유효성 검사"""
        if not self.is_admin_code_required():
            # 사전시험인 경우 관리자 코드가 필요하지 않으므로 유효
            return True

        admin_code = self.parent.admin_code_edit.text().strip()
        # 본시험인 경우 숫자가 입력되어야 함
        return bool(admin_code and admin_code.isdigit())

    def handle_test_category_change(self):
        """시험유형 변경 시 관리자 코드 필드 활성화/비활성화"""
        test_category = self.parent.test_category_edit.text().strip()

        if test_category == "사전시험":
            self.parent.admin_code_edit.setEnabled(False)
            self.parent.admin_code_edit.clear()
            self.parent.admin_code_edit.setPlaceholderText("사전시험은 관리자 코드가 불필요합니다")
        elif test_category == "본시험":
            self.parent.admin_code_edit.setEnabled(True)
            self.parent.admin_code_edit.setPlaceholderText("숫자만 입력 가능합니다")
        else:
            # 다른 값이거나 빈 값일 때는 기본 상태 유지
            self.parent.admin_code_edit.setEnabled(True)
            self.parent.admin_code_edit.setPlaceholderText("숫자만 입력 가능합니다")

    # ---------- CONSTANTS.py 업데이트 ----------

    def update_constants_py(self):
        """CONSTANTS.py 파일의 변수들을 GUI 입력값으로 업데이트"""
        try:
            constants_path = "config/CONSTANTS.py"

            # 1. 시험 기본 정보 수집
            variables = self._collect_basic_info()

            # 2. 접속 정보
            variables['url'] = self.parent.get_selected_url()

            # 3. 인증 정보
            auth_type, auth_info = self._collect_auth_info()
            variables['auth_type'] = auth_type
            variables['auth_info'] = auth_info

            # 4. 관리자 코드 (GUI 입력값만 사용)
            variables['admin_code'] = self.parent.admin_code_edit.text().strip()

            # 5. OPT2 파일에서 프로토콜/타임아웃 정보 추출
            protocol_info = self._extract_protocol_info()
            variables.update(protocol_info)

            # 6. CONSTANTS.py 파일 업데이트
            self._update_constants_file(constants_path, variables)

            return True

        except Exception as e:
            print(f"CONSTANTS.py 업데이트 실패: {e}")
            return False

    def _collect_basic_info(self):
        """시험 기본 정보 수집"""
        return {
            'company_name': self.parent.company_edit.text().strip(),
            'product_name': self.parent.product_edit.text().strip(),
            'version': self.parent.version_edit.text().strip(),
            'test_category': self.parent.test_category_edit.text().strip(),
            'test_target': self.parent.target_system_edit.text().strip(),
            'test_range': self.parent.test_range_edit.text().strip()
        }

    def _collect_auth_info(self):
        """인증 정보 수집"""
        if self.parent.digest_radio.isChecked():
            auth_type = "Digest Auth"
            auth_info = f"{self.parent.id_input.text().strip()},{self.parent.pw_input.text().strip()}"
        else:
            auth_type = "Bearer Token"
            auth_info = self.parent.token_input.text().strip()

        return auth_type, auth_info

    def _extract_protocol_info(self):
        """OPT2 파일에서 프로토콜/타임아웃 정보 추출"""
        # 현재 모드에 따라 파일 선택
        mode_files = {
            "request": "temp/(temp)exp_opt2_requestVal_LongPolling.json",
            "response": "temp/(temp)exp_opt2_responseVal_LongPolling.json",
            "request_webhook": "temp/(temp)exp_opt2_requestVal_WebHook.json",
            "response_webhook": "temp/(temp)exp_opt2_responseVal_WebHook.json"
        }

        exp_opt2_path = resource_path(mode_files.get(
            self.parent.current_mode,
            "temp/(temp)exp_opt2_requestVal_LongPolling.json"
        ))

        exp_opt2 = self.opt_loader.load_opt_json(exp_opt2_path)
        print(f"CONSTANTS.py 업데이트 - 현재 모드: {self.parent.current_mode}")
        print(f"선택된 OPT2 파일: {exp_opt2_path}")

        steps = exp_opt2.get("specification", {}).get("steps", [])

        time_out = []
        num_retries = []
        trans_protocol = []

        for step in steps:
            settings = step.get("api", {}).get("settings", {})
            time_out.append(settings.get("connectTimeout", 30))
            num_retries.append(settings.get("numRetries", 3))

            # transProtocol.mode 추출
            trans_protocol_obj = settings.get("transProtocol", {})
            trans_protocol_mode = trans_protocol_obj.get("mode", None)
            trans_protocol.append(trans_protocol_mode)

        return {
            'trans_protocol': trans_protocol,
            'time_out': time_out,
            'num_retries': num_retries
        }

    def _update_constants_file(self, file_path, variables):
        """CONSTANTS.py 파일의 특정 변수들을 업데이트"""
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