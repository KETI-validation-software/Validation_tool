import re
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
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
            # 모드에 따라 exp_opt 파일 경로 설정
            exp_opt_path = self._get_exp_opt_path(mode)
            if not exp_opt_path:
                QMessageBox.warning(self.parent, "모드 오류", f"알 수 없는 모드: {mode}")
                return

            # exp_opt 파일 로드 (testSpecIds 정보 포함)
            exp_opt = self.opt_loader.load_opt_json(exp_opt_path)
            if not exp_opt:
                QMessageBox.warning(self.parent, "로드 실패", f"{mode.upper()} 모드 OPT 파일을 읽을 수 없습니다.")
                return

            # 현재 모드 저장 및 UI 업데이트
            self.parent.current_mode = mode
            self._fill_basic_info(exp_opt)
            self._fill_test_field_table(exp_opt)

            # API 테이블은 첫 번째 분야를 자동 선택하여 표시
            if self.parent.test_field_table.rowCount() > 0:
                self.parent.test_field_table.selectRow(0)
                self._fill_api_table_for_selected_field(0)

            # 모드에 따른 파일 생성 (모든 testSpecIds의 opt2, opt3 등)
            self._generate_files_for_all_specs(mode, exp_opt)

            # 버튼 상태 업데이트
            self.parent.check_start_button_state()
            self.parent.check_next_button_state()

            QMessageBox.information(self.parent, "로드 완료", f"{mode.upper()} 모드 파일들이 성공적으로 로드되었습니다!")

        except Exception as e:
            QMessageBox.critical(self.parent, "오류", f"OPT 파일 로드 중 오류가 발생했습니다:\n{str(e)}")

    def _get_exp_opt_path(self, mode):
        """모드에 따른 exp_opt 파일 경로 반환"""
        if mode in ["request_longpolling", "request_webhook"]:
            return resource_path("temp/(temp)exp_opt_requestVal.json")
        elif mode in ["response_longpolling", "response_webhook"]:
            return resource_path("temp/(temp)exp_opt_responseVal.json")
        else:
            return None

    def _generate_files_for_all_specs(self, mode, exp_opt):
        """모든 testSpecIds를 하나의 파일로 합쳐서 생성 (schema + videoData)"""
        try:
            # testSpecIds 추출
            test_spec_ids = exp_opt.get("testRequest", {}).get("testGroup", {}).get("testSpecIds", [])
            print(f"\n=== 산출물 생성 시작 ===")
            print(f"모드: {mode}")
            print(f"testSpecIds: {test_spec_ids}")

            # 모든 spec 파일 경로 수집
            spec_file_paths = []
            for spec_id in test_spec_ids:
                spec_file_path = self._get_spec_file_mapping(spec_id)
                if spec_file_path:
                    spec_file_paths.append(resource_path(spec_file_path))
                    print(f"  [{spec_id}] {spec_file_path}")
                else:
                    print(f"  경고: spec_id '{spec_id}'에 대한 매핑을 찾을 수 없습니다.")

            if not spec_file_paths:
                print("  경고: 처리할 spec 파일이 없습니다.")
                return

            print(f"\n총 {len(spec_file_paths)}개 spec 파일을 하나로 합쳐서 생성")

            if mode in ["request_longpolling", "request_webhook"]:
                # Request 모드 - 모든 spec을 하나의 파일로
                print("\n[Request 모드 산출물 생성]")
                self._generate_merged_files(
                    spec_file_paths,
                    schema_type="request",
                    file_type="request"
                )

            elif mode in ["response_longpolling", "response_webhook"]:
                # Response 모드 - 모든 spec을 하나의 파일로
                print("\n[Response 모드 산출물 생성]")
                self._generate_merged_files(
                    spec_file_paths,
                    schema_type="response",
                    file_type="response"
                )

            print(f"\n=== 산출물 생성 완료 ===\n")

        except Exception as e:
            print(f"스키마 파일 생성 실패: {e}")
            import traceback
            traceback.print_exc()

    def _generate_merged_files(self, spec_file_paths, schema_type, file_type):
        """여러 spec 파일을 하나로 합쳐서 생성"""
        import json
        import tempfile

        if not spec_file_paths:
            return

        # 모든 spec 파일의 steps를 하나로 합치기
        merged_steps = []
        merged_spec_id = "merged"
        merged_spec_name = "통합 시험 분야"

        for spec_path in spec_file_paths:
            try:
                spec_data = self.opt_loader.load_opt_json(spec_path)
                if spec_data and "specification" in spec_data:
                    steps = spec_data["specification"].get("steps", [])
                    merged_steps.extend(steps)
                    print(f"  - {spec_data['specification'].get('name', '?')}: {len(steps)}개 step")
            except Exception as e:
                print(f"  경고: {spec_path} 로드 실패: {e}")

        print(f"\n총 {len(merged_steps)}개 step을 통합")

        # 합쳐진 데이터로 임시 JSON 파일 생성
        merged_data = {
            "specification": {
                "id": merged_spec_id,
                "name": merged_spec_name,
                "version": "1.0",
                "steps": merged_steps
            }
        }

        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump(merged_data, temp_file, ensure_ascii=False, indent=2)
            temp_file_path = temp_file.name

        try:
            # 임시 파일을 사용하여 산출물 생성
            schema_path = generate_schema_file(
                temp_file_path,
                schema_type=schema_type,
                output_path=f"spec/video/videoSchema_{file_type}.py"
            )
            print(f"videoSchema_{file_type}.py 생성 완료")

            request_path = generate_video_request_file(
                temp_file_path,
                file_type=file_type,
                output_path=f"spec/video/videoData_{file_type}.py"
            )
            print(f"videoData_{file_type}.py 생성 완료")

        finally:
            # 임시 파일 삭제
            import os
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

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

    def _fill_test_field_table(self, exp_opt):
        """시험 분야명 테이블 채우기 (testSpecIds 기반)"""
        if not exp_opt or "testRequest" not in exp_opt:
            return

        test_group = exp_opt["testRequest"].get("testGroup", {})
        test_spec_ids = test_group.get("testSpecIds", [])

        # 시험 분야명 테이블 초기화
        self.parent.test_field_table.setRowCount(0)

        # 각 testSpecId에 대해 해당하는 specification 파일 로드
        for spec_id in test_spec_ids:
            spec_name = self._get_specification_name(spec_id)
            if spec_name:
                row = self.parent.test_field_table.rowCount()
                self.parent.test_field_table.insertRow(row)

                # 시험 분야명
                item = QTableWidgetItem(spec_name)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                # spec_id를 저장해서 나중에 사용
                item.setData(Qt.UserRole, spec_id)
                self.parent.test_field_table.setItem(row, 0, item)

    def _get_specification_name(self, spec_id):
        """testSpecId에 해당하는 specification의 name 가져오기 (하드코딩 매핑)"""
        try:
            # spec_id와 파일명 하드코딩 매핑
            spec_file_map = self._get_spec_file_mapping(spec_id)
            if not spec_file_map:
                return f"시험 분야 {spec_id}"

            from core.functions import resource_path
            spec_file_path = resource_path(spec_file_map)

            # 해당 파일에서 specification.name 가져오기
            spec_data = self.opt_loader.load_opt_json(spec_file_path)
            if spec_data and "specification" in spec_data:
                return spec_data["specification"].get("name", f"시험 분야 {spec_id}")

        except Exception as e:
            print(f"Specification {spec_id} 로드 실패: {e}")

        return f"시험 분야 {spec_id}"  # 기본값

    def _get_spec_file_mapping(self, spec_id):
        """spec_id를 실제 파일 경로로 매핑 (하드코딩)

        매핑 규칙:
        - Request 모드: spec-001 (opt2), spec-0011 (opt3)
        - Response 모드: spec-002 (opt2), spec-0022 (opt3)

        TODO: 향후 API 주소 기반 매핑으로 변경 예정
        """
        mode = self.parent.current_mode

        # Request 모드: spec-001, spec-0011
        if spec_id == "spec-001":
            if mode == "request_longpolling":
                return "temp/(temp)exp_opt2_requestVal_LongPolling.json"
            elif mode == "request_webhook":
                return "temp/(temp)exp_opt2_requestVal_WebHook.json"

        elif spec_id == "spec-0011":
            if mode == "request_longpolling":
                return "temp/(temp)exp_opt3_requestVal_LongPolling.json"
            elif mode == "request_webhook":
                return "temp/(temp)exp_opt3_requestVal_WebHook.json"

        # Response 모드: spec-002, spec-0022
        elif spec_id == "spec-002":
            if mode == "response_longpolling":
                return "temp/(temp)exp_opt2_responseVal_Longpolling.json"
            elif mode == "response_webhook":
                return "temp/(temp)exp_opt2_responseVal_WebHook.json"

        elif spec_id == "spec-0022":
            if mode == "response_longpolling":
                return "temp/(temp)exp_opt3_responseVal_Longpolling.json"
            elif mode == "response_webhook":
                return "temp/(temp)exp_opt3_responseVal_WebHook.json"

        return None

    def _fill_api_table_for_selected_field(self, row):
        """선택된 시험 분야에 해당하는 API 테이블 채우기"""
        try:
            # 선택된 행에서 spec_id 가져오기
            item = self.parent.test_field_table.item(row, 0)
            if not item:
                return

            from PyQt5.QtCore import Qt
            spec_id = item.data(Qt.UserRole)
            if not spec_id:
                return

            # 해당 spec_id의 OPT2 파일 로드
            spec_data = self._load_specification_data(spec_id)
            if not spec_data:
                return

            # API 테이블 초기화
            self.parent.api_test_table.setRowCount(0)

            # specification의 steps에서 API 정보 추출
            steps = spec_data.get("specification", {}).get("steps", [])
            prev_endpoint = None

            for step in steps:
                api_info = step.get("api", {})
                if not api_info:
                    continue

                r = self.parent.api_test_table.rowCount()
                self.parent.api_test_table.insertRow(r)

                from PyQt5.QtWidgets import QTableWidgetItem
                from PyQt5.QtCore import Qt

                # 기능명
                item1 = QTableWidgetItem(api_info.get("name", ""))
                item1.setTextAlignment(Qt.AlignCenter)
                item1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.parent.api_test_table.setItem(r, 0, item1)

                # API명
                endpoint = api_info.get("endpoint")
                if not endpoint and prev_endpoint:
                    endpoint = prev_endpoint

                item2 = QTableWidgetItem(endpoint or "")
                item2.setTextAlignment(Qt.AlignCenter)
                item2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.parent.api_test_table.setItem(r, 1, item2)

                # 이번 step endpoint 저장
                if api_info.get("endpoint"):
                    prev_endpoint = api_info["endpoint"]

        except Exception as e:
            print(f"API 테이블 채우기 실패: {e}")

    def _load_specification_data(self, spec_id):
        """spec_id에 해당하는 specification 데이터 로드 (하드코딩 매핑)"""
        try:
            # spec_id와 파일명 하드코딩 매핑
            spec_file_map = self._get_spec_file_mapping(spec_id)
            if not spec_file_map:
                return None

            from core.functions import resource_path
            spec_file_path = resource_path(spec_file_map)

            # 해당 파일에서 specification 데이터 가져오기
            return self.opt_loader.load_opt_json(spec_file_path)

        except Exception as e:
            print(f"Specification 데이터 로드 실패 ({spec_id}): {e}")
            return None


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
        """선택된 시험 분야의 프로토콜/타임아웃 정보 추출"""
        # 선택된 시험 분야의 spec_id 가져오기
        selected_spec_id = self._get_selected_test_field_spec_id()
        if not selected_spec_id:
            print("경고: 선택된 시험 분야가 없습니다.")
            return {'trans_protocol': [], 'time_out': [], 'num_retries': []}

        print(f"CONSTANTS.py 업데이트 - 현재 모드: {self.parent.current_mode}")
        print(f"선택된 시험 분야: {selected_spec_id}")

        # 선택된 spec_id에 해당하는 파일 경로 가져오기
        spec_file_path = self._get_spec_file_mapping(selected_spec_id)
        if not spec_file_path:
            print(f"경고: spec_id '{selected_spec_id}'에 대한 매핑을 찾을 수 없습니다.")
            return {'trans_protocol': [], 'time_out': [], 'num_retries': []}

        print(f"  파일: {spec_file_path}")

        # 파일 로드
        spec_data = self.opt_loader.load_opt_json(resource_path(spec_file_path))
        if not spec_data:
            print(f"경고: {spec_file_path} 파일을 로드할 수 없습니다.")
            return {'trans_protocol': [], 'time_out': [], 'num_retries': []}

        # steps에서 프로토콜 정보 추출
        steps = spec_data.get("specification", {}).get("steps", [])
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

        #print(f"추출된 프로토콜 정보: {len(time_out)}개 스텝")

        return {
            'trans_protocol': trans_protocol,
            'time_out': time_out,
            'num_retries': num_retries
        }

    def _get_selected_test_field_spec_id(self):
        """시험 분야 테이블에서 마지막으로 클릭된 항목의 spec_id 반환"""
        try:
            # 마지막으로 클릭된 행 번호 사용
            if hasattr(self.parent, 'selected_test_field_row') and self.parent.selected_test_field_row is not None:
                row = self.parent.selected_test_field_row
                item = self.parent.test_field_table.item(row, 0)
                if item:
                    return item.data(Qt.UserRole)
            return None
        except Exception as e:
            print(f"선택된 시험 분야 spec_id 가져오기 실패: {e}")
            return None

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