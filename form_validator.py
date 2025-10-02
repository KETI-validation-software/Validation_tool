import re
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from core.functions import resource_path
from core.opt_loader import OptLoader
from core.schema_generator import generate_schema_file
from core.video_request_generator import generate_video_request_file
import os


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

            all_spec_list_names = []

            if mode in ["request_longpolling", "request_webhook"]:
                # Request 모드 - 모든 spec을 하나의 파일로
                print("\n[Request 모드 산출물 생성]")
                spec_list_names = self._generate_merged_files(
                    spec_file_paths,
                    schema_type="request",
                    file_type="request"
                )
                if spec_list_names:
                    all_spec_list_names.extend(spec_list_names)

            elif mode in ["response_longpolling", "response_webhook"]:
                # Response 모드 - 모든 spec을 하나의 파일로
                print("\n[Response 모드 산출물 생성]")
                spec_list_names = self._generate_merged_files(
                    spec_file_paths,
                    schema_type="response",
                    file_type="response"
                )
                if spec_list_names:
                    all_spec_list_names.extend(spec_list_names)

            # CONSTANTS.py 업데이트
            if all_spec_list_names:
                self._update_constants_specs(all_spec_list_names)

            # trans_protocol, time_out, num_retries 업데이트
            print("\n[CONSTANTS.py 프로토콜 정보 업데이트]")
            protocol_info = self._extract_protocol_info()
            if protocol_info:
                self._update_protocol_in_constants(protocol_info)

            print(f"\n=== 산출물 생성 완료 ===\n")

        except Exception as e:
            print(f"스키마 파일 생성 실패: {e}")
            import traceback
            traceback.print_exc()

    def _generate_merged_files(self, spec_file_paths, schema_type, file_type):
        """여러 spec 파일을 하나의 파일에 spec별로 구분하여 생성"""

        if not spec_file_paths:
            return

        # Schema 파일과 Data 파일 내용을 담을 문자열
        schema_content = "from json_checker import OptionalKey\n\n\n"
        data_content = f"# {file_type} 모드\n\n"

        # 각 스펙별 리스트 이름 저장 (CONSTANTS.py 업데이트용)
        spec_list_names = []

        # 통합 리스트 생성용 (하위 호환성)
        # all_schema_list_names = []
        # all_data_list_names = []
        # all_messages_list_names = []

        # 각 spec 파일별로 처리
        for spec_path in spec_file_paths:
            try:
                spec_data = self.opt_loader.load_opt_json(spec_path)
                if not spec_data or "specification" not in spec_data:
                    continue

                spec_id = spec_data["specification"].get("id", "")
                spec_name = spec_data["specification"].get("name", "")
                # spec_id의 -을 _로 변경
                spec_id_safe = spec_id.replace("-", "_")
                print(f"  - [{spec_id}] {spec_name}")

                # WebHook 파일인지 확인
                is_webhook = "WebHook" in spec_path

                # SchemaGenerator와 VideoRequestGenerator 인스턴스 생성
                from core.schema_generator import SchemaGenerator
                from core.video_request_generator import VideoRequestGenerator

                schema_gen = SchemaGenerator()
                data_gen = VideoRequestGenerator()

                # 각 spec의 steps 처리
                steps = spec_data["specification"].get("steps", [])

                # WebHook 관련 리스트
                webhook_schema_names = []
                webhook_data_names = []

                # Schema 생성 (spec별로)
                schema_names = []
                for step in steps:
                    step_id = step.get("id", "")
                    api = step.get("api", {})
                    endpoint = api.get("endpoint", "")
                    settings = api.get("settings", {})
                    trans_protocol = settings.get("transProtocol", {})

                    # 콜백 스텝은 건너뛰기
                    if not endpoint and api.get("urlKey"):
                        continue

                    schema_info = schema_gen.generate_endpoint_schema(step, schema_type)
                    schema_name = schema_info["name"]
                    schema_obj = schema_info["content"]
                    endpoint_name = schema_info["endpoint"]

                    # 스키마 내용 추가
                    schema_content += f"# {endpoint_name}\n"
                    formatted = schema_gen.format_schema_content(schema_obj)
                    schema_content += f"{schema_name} = {formatted}\n\n"
                    schema_names.append(schema_name)

                    # WebHook 모드이고 transProtocol.mode가 "WebHook"인 경우
                    if is_webhook and trans_protocol.get("mode") == "WebHook":
                        # 콜백 스텝 찾기
                        callback_step_id = f"{step_id}-1"
                        callback_step = None
                        for s in steps:
                            if s.get("id") == callback_step_id:
                                callback_step = s
                                break

                        if callback_step:
                            callback_api = callback_step.get("api", {})

                            # WebHook 스키마 생성
                            if schema_type == "request":
                                target_schema = callback_api.get("responseSchema", {})
                                if target_schema:
                                    webhook_schema_str = schema_gen._generate_webhook_schema_from_json_schema(target_schema, endpoint_name, schema_type)
                                    schema_content += webhook_schema_str + "\n"
                                    # 스키마 이름 추출
                                    for line in webhook_schema_str.split('\n'):
                                        if ' = {' in line and 'WebHook_' in line:
                                            wh_name = line.split(' = ')[0].strip()
                                            webhook_schema_names.append(wh_name)
                                            break
                            else:  # response
                                target_schema = callback_api.get("requestSchema", {})
                                if target_schema:
                                    webhook_schema_str = schema_gen._generate_webhook_schema_from_json_schema(target_schema, endpoint_name, schema_type)
                                    schema_content += webhook_schema_str + "\n"
                                    for line in webhook_schema_str.split('\n'):
                                        if ' = {' in line and 'WebHook_' in line:
                                            wh_name = line.split(' = ')[0].strip()
                                            webhook_schema_names.append(wh_name)
                                            break

                                # ACK 응답 스키마 생성
                                response_schema = callback_api.get("responseSchema", {})
                                if response_schema:
                                    ack_schema_str = schema_gen._generate_webhook_ack_schema(response_schema)
                                    if ack_schema_str:
                                        schema_content += ack_schema_str + "\n"
                                        for line in ack_schema_str.split('\n'):
                                            if ' = {' in line and 'Webhook_' in line:
                                                wh_name = line.split(' = ')[0].strip()
                                                if wh_name not in webhook_schema_names:
                                                    webhook_schema_names.append(wh_name)
                                                break

                # Schema 리스트 생성 (spec별로) - spec_id_safe 사용
                if schema_type == "request":
                    list_name = f"{spec_id_safe}_inSchema"
                else:
                    list_name = f"{spec_id_safe}_outSchema"

                schema_content += f"# {spec_id_safe} 스키마 리스트\n"
                schema_content += f"{list_name} = [\n"
                for name in schema_names:
                    schema_content += f"    {name},\n"
                schema_content += "]\n\n"

                # WebHook 스키마 리스트 생성
                if is_webhook and webhook_schema_names:
                    webhook_list_name = f"{spec_id_safe}_webhookSchema"
                    schema_content += f"# {spec_id_safe} WebHook 스키마 리스트\n"
                    schema_content += f"{webhook_list_name} = [\n"
                    for name in webhook_schema_names:
                        schema_content += f"    {name},\n"
                    schema_content += "]\n\n"

                # Data 생성 (spec별로)
                data_names = []
                endpoint_names = []
                for step in steps:
                    step_id = step.get("id", "")
                    api = step.get("api", {})
                    endpoint = api.get("endpoint", "")
                    settings = api.get("settings", {})
                    trans_protocol = settings.get("transProtocol", {})

                    # 콜백 스텝은 건너뛰기
                    if not endpoint and api.get("urlKey"):
                        continue

                    data_info = data_gen.extract_endpoint_data(step, file_type)
                    data_name = data_info["name"]
                    data_obj = data_info["content"]
                    endpoint_name = data_info["endpoint"]

                    # 데이터 내용 추가
                    data_content += f"# {endpoint_name}\n"
                    formatted = data_gen.format_data_content(data_obj)
                    data_content += f"{data_name} = {formatted}\n\n"
                    data_names.append(data_name)
                    endpoint_names.append(endpoint_name)

                    # WebHook 모드이고 transProtocol.mode가 "WebHook"인 경우
                    if is_webhook and trans_protocol.get("mode") == "WebHook":
                        # 콜백 스텝 찾기
                        callback_step_id = f"{step_id}-1"
                        callback_step = None
                        for s in steps:
                            if s.get("id") == callback_step_id:
                                callback_step = s
                                break

                        if callback_step:
                            webhook_data_str = data_gen._generate_webhook_data(callback_step, endpoint_name, file_type)
                            if webhook_data_str:
                                data_content += webhook_data_str + "\n"
                                # 데이터 이름 추출
                                for line in webhook_data_str.split('\n'):
                                    if ' = {' in line or ' = [' in line:
                                        wh_data_name = line.split(' = ')[0].strip()
                                        webhook_data_names.append(wh_data_name)
                                        break

                # Data 리스트 생성 (spec별로) - spec_id_safe 사용
                if file_type == "request":
                    data_list_name = f"{spec_id_safe}_outData"
                else:
                    data_list_name = f"{spec_id_safe}_inData"

                data_content += f"# {spec_id_safe} 데이터 리스트\n"
                data_content += f"{data_list_name} = [\n"
                for name in data_names:
                    data_content += f"    {name},\n"
                data_content += "]\n\n"

                # Messages 리스트 생성 (spec별로) - spec_id_safe 사용
                messages_list_name = f"{spec_id_safe}_messages"
                data_content += f"# {spec_id_safe} API endpoint\n"
                data_content += f"{messages_list_name} = [\n"
                for endpoint in endpoint_names:
                    data_content += f'    "{endpoint}",\n'
                data_content += "]\n\n"

                # WebHook 데이터 리스트 생성
                if is_webhook and webhook_data_names:
                    webhook_data_list_name = f"{spec_id_safe}_webhookData"
                    data_content += f"# {spec_id_safe} WebHook 데이터 리스트\n"
                    data_content += f"{webhook_data_list_name} = [\n"
                    for name in webhook_data_names:
                        data_content += f"    {name},\n"
                    data_content += "]\n\n"

                # CONSTANTS.py 업데이트용 리스트 저장
                spec_info = {
                    "spec_id": spec_id,
                    "inSchema": list_name if schema_type == "response" else f"{spec_id_safe}_inSchema",
                    "outData": data_list_name if file_type == "request" else f"{spec_id_safe}_outData",
                    "messages": messages_list_name,
                    "name": spec_name
                }

                # webhook 리스트 추가 (있을 경우)
                if is_webhook:
                    if webhook_schema_names:
                        spec_info["webhookSchema"] = f"{spec_id_safe}_webhookSchema"
                    if webhook_data_names:
                        spec_info["webhookData"] = f"{spec_id_safe}_webhookData"

                #CONSTANTS.py업데이트용
                spec_list_names.append(spec_info)

                # 통합 리스트 생성용 이름 수집
                # all_schema_list_names.append(list_name)
                # all_data_list_names.append(data_list_name)
                # all_messages_list_names.append(messages_list_name)

            except Exception as e:
                print(f"  경고: {spec_path} 처리 실패: {e}")
                import traceback
                traceback.print_exc()

        # # 통합 리스트 생성 (하위 호환성 유지)
        # if all_schema_list_names:
        #     if schema_type == "request":
        #         unified_schema_name = "videoInSchema"
        #     else:
        #         unified_schema_name = "videoOutSchema"

        #     schema_content += f"# 통합 스키마 리스트 (하위 호환성)\n"
        #     schema_content += f"{unified_schema_name} = " + " + ".join(all_schema_list_names) + "\n\n"

        # if all_data_list_names:
        #     if file_type == "request":
        #         unified_data_name = "videoOutMessage"
        #     else:
        #         unified_data_name = "videoInMessage"

        #     data_content += f"# 통합 데이터 리스트 (하위 호환성)\n"
        #     data_content += f"{unified_data_name} = " + " + ".join(all_data_list_names) + "\n\n"

        # if all_messages_list_names:
        #     data_content += f"# 통합 API endpoint 리스트 (하위 호환성)\n"
        #     data_content += f"videoMessages = " + " + ".join(all_messages_list_names) + "\n\n"

        # 파일 저장
        schema_output = f"spec/video/videoSchema_{file_type}.py"
        data_output = f"spec/video/videoData_{file_type}.py"

        os.makedirs("spec/video", exist_ok=True)

        with open(schema_output, 'w', encoding='utf-8') as f:
            f.write(schema_content)
        print(f"videoSchema_{file_type}.py 생성 완료")

        with open(data_output, 'w', encoding='utf-8') as f:
            f.write(data_content)
        print(f"videoData_{file_type}.py 생성 완료")

        # CONSTANTS.py의 specs 리스트 업데이트
        return spec_list_names

    def _update_constants_specs(self, spec_list_names):
        """CONSTANTS.py의 specs 리스트를 업데이트"""
        try:
            import re
            constants_path = "config/CONSTANTS.py"

            # CONSTANTS.py 파일 읽기
            with open(constants_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # specs 리스트 생성
            specs_lines = []
            for spec_info in spec_list_names:
                in_schema = spec_info.get("inSchema", "")
                out_data = spec_info.get("outData", "")
                messages = spec_info.get("messages", "")
                webhook_schema = spec_info.get("webhookSchema", "")
                webhook_data = spec_info.get("webhookData", "")
                name = spec_info.get("name", "")

                # webhook이 있으면 포함, 없으면 제외
                if webhook_schema and webhook_data:
                    spec_line = f'["{in_schema}","{out_data}","{messages}","{webhook_schema}","{webhook_data}","{name}"]'
                else:
                    spec_line = f'["{in_schema}","{out_data}","{messages}","{name}"]'

                specs_lines.append(spec_line)

            # specs 리스트 문자열 생성
            specs_str = "specs = [" + ",\n         ".join(specs_lines) + "]"

            # 기존 specs 패턴 찾기 및 교체
            pattern = r'specs\s*=\s*\[\[.*?\]\]'

            if re.search(pattern, content, re.DOTALL):
                # 기존 specs가 있으면 교체
                new_content = re.sub(pattern, specs_str, content, flags=re.DOTALL)
            else:
                # specs가 없으면 추가 (url 다음에)
                url_pattern = r'(url\s*=\s*"[^"]*"\n\n)'
                new_content = re.sub(url_pattern, r'\1\n' + specs_str + '\n', content)

            # 파일에 쓰기
            with open(constants_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"CONSTANTS.py specs 리스트 업데이트 완료")

        except Exception as e:
            print(f"  경고: CONSTANTS.py specs 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()

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

            # 5. OPT 파일에서 프로토콜/타임아웃 정보 추출
            protocol_info = self._extract_protocol_info()
            variables.update(protocol_info)

            # 6. 선택된 시험 분야의 인덱스 저장 (중요!)
            selected_spec_index = self._get_selected_spec_index()
            variables['selected_spec_index'] = selected_spec_index
            print(f"\n🎯 [CRITICAL] CONSTANTS.py에 저장할 selected_spec_index: {selected_spec_index}")
            print(f"   변수 타입: {type(selected_spec_index)}")
            print(f"   전체 variables: {variables}\n")

            # 7. CONSTANTS.py 파일 업데이트
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

    # 기본값 []으로 설정하시면 안됩니다. 무조건 9개 API에 대한 기본값이 들어가야 합니다!!! 검증 작동이 아예 안돼서 테스트가 안됩니다..
    def _extract_protocol_info(self):
        """선택된 시험 분야의 프로토콜/타임아웃 정보 추출"""
        # 선택된 시험 분야의 spec_id 가져오기
        selected_spec_id = self._get_selected_test_field_spec_id()
        if not selected_spec_id:
            print("경고: 선택된 시험 분야가 없습니다.")
            print("기본값을 사용합니다: 9개 API, 각 30초 타임아웃, 3회 재시도")
            # 기본값 반환 (9개 API 기준)
            return {
                'trans_protocol': [None, None, None, None, None, None, "LongPolling", None, None],
                'time_out': [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
                'num_retries': [1, 2, 3, 3, 3, 2, 1, 1, 1]
            }

        print(f"CONSTANTS.py 업데이트 - 현재 모드: {self.parent.current_mode}")
        print(f"선택된 시험 분야: {selected_spec_id}")

        # 선택된 spec_id에 해당하는 파일 경로 가져오기
        spec_file_path = self._get_spec_file_mapping(selected_spec_id)
        if not spec_file_path:
            print(f"경고: spec_id '{selected_spec_id}'에 대한 매핑을 찾을 수 없습니다.")
            print(f"기본값을 사용합니다: 9개 API, 각 30초 타임아웃, 3회 재시도")
            # 기본값 반환 (9개 API 기준)
            return {
                'trans_protocol': [None, None, None, None, None, None, "LongPolling", None, None],
                'time_out': [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
                'num_retries': [1, 2, 3, 3, 3, 2, 1, 1, 1]
            }

        print(f"  파일: {spec_file_path}")

        # 파일 로드
        spec_data = self.opt_loader.load_opt_json(resource_path(spec_file_path))
        if not spec_data:
            print(f"경고: {spec_file_path} 파일을 로드할 수 없습니다.")
            print(f"기본값을 사용합니다: 9개 API, 각 30초 타임아웃, 3회 재시도")
            # 기본값 반환 (9개 API 기준)
            return {
                'trans_protocol': [None, None, None, None, None, None, "LongPolling", None, None],
                'time_out': [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
                'num_retries': [1, 2, 3, 3, 3, 2, 1, 1, 1]
            }

        # steps에서 프로토콜 정보 추출
        steps = spec_data.get("specification", {}).get("steps", [])
        time_out = []
        num_retries = []
        trans_protocol = []

        # print(f"  추출 시작: {len(steps)}개 steps")

        for step in steps:
            settings = step.get("api", {}).get("settings", {})
            time_out.append(settings.get("connectTimeout", 30))
            num_retries.append(settings.get("numRetries", 3))

            # transProtocol.mode 추출
            trans_protocol_obj = settings.get("transProtocol", {})
            trans_protocol_mode = trans_protocol_obj.get("mode", None)
            trans_protocol.append(trans_protocol_mode)
            # print(f"    step {step.get('id')}: timeout={settings.get('connectTimeout', 30)}, retries={settings.get('numRetries', 3)}, protocol={trans_protocol_mode}")

        # print(f"  추출된 프로토콜 정보: {len(time_out)}개 스텝")
        # print(f"  trans_protocol: {trans_protocol}")
        # print(f"  time_out: {time_out}")
        # print(f"  num_retries: {num_retries}")

        return {
            'trans_protocol': trans_protocol,
            'time_out': time_out,
            'num_retries': num_retries
        }

    def _update_protocol_in_constants(self, protocol_info):
        """CONSTANTS.py의 trans_protocol, time_out, num_retries만 업데이트"""
        try:
            import re
            constants_path = "config/CONSTANTS.py"

            with open(constants_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # trans_protocol, time_out, num_retries 업데이트
            for var_name in ['trans_protocol', 'time_out', 'num_retries']:
                var_value = protocol_info.get(var_name)
                if var_value is not None:
                    new_line = f'{var_name} = {var_value}'
                    pattern = rf'^{var_name}\s*=.*$'
                    content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
                    print(f"{var_name} 업데이트: {var_value}")

            with open(constants_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"CONSTANTS.py 프로토콜 정보 업데이트 완료")

        except Exception as e:
            print(f"  경고: CONSTANTS.py 프로토콜 정보 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()

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

    def _get_selected_spec_index(self):
        """선택된 시험 분야의 CONSTANTS.specs 인덱스 반환"""
        try:
            print("\n=== _get_selected_spec_index 시작 ===")
            selected_spec_id = self._get_selected_test_field_spec_id()
            print(f"[DEBUG] selected_spec_id: {selected_spec_id}")
            
            if not selected_spec_id:
                print("⚠️ 경고: 선택된 시험 분야가 없습니다. 기본값 0 사용")
                return 0
            
            # spec_id로 직접 판단 (파일 경로 대신)
            # spec-001 = 영상보안(index 0), spec-0011 = 보안용센서(index 1)
            spec_id_str = str(selected_spec_id).lower()
            
            if "spec-0011" in spec_id_str or "spec_0011" in spec_id_str:
                print("✅ 보안용 센서 시스템 선택됨 (index 1)")
                return 1  # 보안용 센서 시스템
            elif "spec-001" in spec_id_str or "spec_001" in spec_id_str:
                print("✅ 영상보안 시스템 선택됨 (index 0)")
                return 0  # 영상보안 시스템
            else:
                # 추가: 파일 경로로도 확인 (이중 체크)
                spec_file_path = self._get_spec_file_mapping(selected_spec_id)
                print(f"[DEBUG] spec_file_path: {spec_file_path}")
                
                if spec_file_path:
                    if "opt3" in spec_file_path or "0011" in spec_file_path:
                        print("✅ 보안용 센서 시스템 선택됨 (index 1) - 파일 경로로 판단")
                        return 1
                    elif "opt2" in spec_file_path or "_001" in spec_file_path:
                        print("✅ 영상보안 시스템 선택됨 (index 0) - 파일 경로로 판단")
                        return 0
                
                print(f"⚠️ 경고: 알 수 없는 spec_id '{selected_spec_id}'. 기본값 0 사용")
                return 0
                
        except Exception as e:
            print(f"❌ 선택된 spec 인덱스 가져오기 실패: {e}")
            import traceback
            traceback.print_exc()
            return 0

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