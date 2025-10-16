import re
import requests
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from core.functions import resource_path
from core.opt_loader import OptLoader
import os
from core.schema_generator import SchemaGenerator
from core.data_generator import dataGenerator
from core.validation_generator import ValidationGenerator
from core.constraint_generator import constraintGeneractor
import json

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
        self._steps_cache = {}
        self._test_step_cache = {}
        self._spec_names_cache = {}  # spec_id -> spec_name 매핑
        self.schema_gen = SchemaGenerator()
        self.data_gen = dataGenerator()
        self.validation_gen = ValidationGenerator()
        self.const_gen = constraintGeneractor()

    def _convert_webhook_spec_to_schema(self, webhook_spec):
        """webhook.integrationSpec을 스키마 형식으로 변환"""
        # webhook_spec이 리스트인 경우 (bodyJson 배열이 직접 들어있음)
        if isinstance(webhook_spec, list):
            return self.schema_gen._parse_body_fields(webhook_spec)
        # webhook_spec이 딕셔너리이고 bodyJson 키가 있는 경우
        elif isinstance(webhook_spec, dict) and "bodyJson" in webhook_spec:
            body_json = webhook_spec.get("bodyJson", [])
            return self.schema_gen._parse_body_fields(body_json)
        # 이미 스키마 형식이면 그대로 반환
        return webhook_spec

    def _convert_webhook_spec_to_data(self, webhook_spec):
        """webhook.requestSpec을 데이터 형식으로 변환"""
        # webhook_spec이 bodyJson 형식이면 파싱
        if isinstance(webhook_spec, dict) and "bodyJson" in webhook_spec:
            body_json = webhook_spec.get("bodyJson", [])
            return self.data_gen.build_data_from_spec(body_json)
        # 이미 데이터 형식이면 그대로 반환
        return webhook_spec

    def _generate_files_for_all_specs(self):
        """모든 testSpecIds를 하나의 파일로 합쳐서 생성 (schema + videoData)"""
        try:
            # testSpecIds 추출
            print(f"\n=== 산출물 생성 시작 ===")
            print(f"specIds: {self._steps_cache.items()}")

            schema_content = ""
            data_content = ""
            validation_content = ""
            constraints_content = ""
            spec_list_names = []

            for spec_id, steps in self._steps_cache.items():
                if not isinstance(steps, list):
                    continue
                schema_names = []
                data_names = []
                endpoint_names = []
                validation_names  = []
                constraints_names  = []
                temp_spec_id = spec_id+"_"
                for s in steps:
                    step_id = s.get("id")
                    ts = self._test_step_cache.get(step_id) if hasattr(self, "_test_step_cache") else None

                    if ts:
                        schema_type = ts.get("verificationType")
                        if schema_type == 'request':
                            file_type = 'response'
                        elif schema_type == 'response':
                            file_type = 'request'
                        schema_content, data_content, validation_content,constraints_content = self._generate_files_for_each_steps(
                            schema_type=schema_type,
                            file_type=file_type,
                            ts=ts,
                            schema_content=schema_content,
                            data_content=data_content,
                            schema_names=schema_names,
                            data_names=data_names,
                            endpoint_names=endpoint_names,
                            validation_content=validation_content,
                            validation_names=validation_names,
                            constraints_content=constraints_content,
                            constraints_names=constraints_names,
                            spec_id = temp_spec_id
                        )
                if schema_type == "request":
                    list_name = f"{spec_id}_inSchema"
                else:
                    list_name = f"{spec_id}_outSchema"

                schema_content += f"# {spec_id} 스키마 리스트\n"
                schema_content += f"{list_name} = [\n"
                for name in schema_names:
                    schema_content += f"    {temp_spec_id}{name},\n"
                schema_content += "]\n\n"

                if file_type == "request":
                    data_list_name = f"{spec_id}_inData"
                else:
                    data_list_name = f"{spec_id}_outData"

                data_content += f"# {spec_id} 데이터 리스트\n"
                data_content += f"{data_list_name} = [\n"
                for name in data_names:
                    data_content += f"    {temp_spec_id}{name},\n"
                data_content += "]\n\n"

                # Messages 리스트 생성 (spec별로) - spec_id_safe 사용
                messages_list_name = f"{spec_id}_messages"
                data_content += f"# {spec_id} API endpoint\n"
                data_content += f"{messages_list_name} = [\n"
                for endpoint in endpoint_names:
                    data_content += f'    "{endpoint}",\n'
                data_content += "]\n\n"

                # Validation 리스트
                if schema_type == "request":
                    v_list_name = f"{spec_id}_inValidation"
                else:
                    v_list_name = f"{spec_id}_outValidation"

                validation_content += f"# {spec_id} 검증 리스트\n"
                validation_content += f"{v_list_name} = [\n"
                for vname in validation_names:
                    validation_content += f"    {vname},\n"
                validation_content += "]\n\n"

                # Constraints 리스트
                if file_type == "request":
                    c_list_name = f"{spec_id}_OutConstraints"
                else:
                    c_list_name = f"{spec_id}_inConstraints"

                constraints_content += f"# {spec_id} 검증 리스트\n"
                constraints_content += f"{c_list_name} = [\n"
                for cname in constraints_names:
                    constraints_content += f"    {cname},\n"
                constraints_content += "]\n\n"

                # CONSTANTS.py 업데이트용 리스트 저장
                spec_info = {
                    "spec_id": spec_id,
                    "inSchema": list_name if schema_type == "response" else f"{spec_id}_inSchema",
                    "outData": data_list_name if file_type == "request" else f"{spec_id}_outData",
                    "messages": messages_list_name,
                    "name": ts.get("detail", {}).get("testSpec", {}).get("name", "")

                }
                spec_list_names.append(spec_info)

            schema_content = "from json_checker import OptionalKey\n\n\n" + schema_content
            data_content = f"# {file_type} 모드\n\n" + data_content

            all_spec_list_names = []

            if spec_list_names:
                all_spec_list_names.extend(spec_list_names)

            # 파일 저장
            schema_output = f"spec/Schema_{schema_type}.py"
            data_output = f"spec/Data_{file_type}.py"
            validation_output = f"spec/Validation_{schema_type}.py"
            constraints_output = f"spec/Constraints_{file_type}.py"


            with open(schema_output, 'w', encoding='utf-8') as f:
                f.write(schema_content)
            print(f"Schema_{schema_type}.py 생성 완료")

            with open(data_output, 'w', encoding='utf-8') as f:
                f.write(data_content)
            print(f"Data_{file_type}.py 생성 완료")

            with open(validation_output, 'w', encoding='utf-8') as f:
                f.write(validation_content)
            print(f"Data_{validation_output}.py 생성 완료")

            with open(constraints_output, 'w', encoding='utf-8') as f:
                f.write(constraints_content)
            print(f"Data_{constraints_output}.py 생성 완료")

            # CONSTANTS.py 업데이트
            if all_spec_list_names:
                self._update_constants_specs(all_spec_list_names)

            print(f"\n=== 산출물 생성 완료 ===\n")

        except Exception as e:
            print(f"스키마 파일 생성 실패: {e}")
            import traceback
            traceback.print_exc()

    def _generate_files_for_each_steps(self, schema_type, file_type, ts, schema_content,
                                       data_content, schema_names, data_names, endpoint_names,
                                       validation_content, validation_names,
                                   constraints_content, constraints_names, spec_id):

        # step 레벨에서 protocolType 확인 (소문자 "webhook")
        detail = ts.get("detail", {})
        step = detail.get("step", {})
        protocol_type = step.get("protocolType", "").lower()

        api = step.get("api", {})
        settings = api.get("settings", {})

        # # [DEBUG] WebHook 디버깅
        # print(f"\n[DEBUG] step.protocolType: {step.get('protocolType')}")
        # print(f"[DEBUG] protocol_type (lower): {protocol_type}")
        # print(f"[DEBUG] schema_type: {schema_type}, file_type: {file_type}")
        # print(f"[DEBUG] settings.webhook 존재 여부: {'webhook' in settings}")
        # if 'webhook' in settings:
        #     print(f"[DEBUG] webhook.integrationSpec 존재: {'integrationSpec' in settings.get('webhook', {})}")
        #     print(f"[DEBUG] webhook.requestSpec 존재: {'requestSpec' in settings.get('webhook', {})}")

        schema_info = self.schema_gen.generate_endpoint_schema(ts, schema_type)
        schema_name = schema_info["name"]
        schema_obj = schema_info["content"]
        endpoint_name = schema_info["endpoint"]

        # 스키마 내용 추가
        schema_content += f"# {endpoint_name}\n"
        formatted = self.schema_gen.format_schema_content(schema_obj)
        schema_content += f"{spec_id}{schema_name} = {formatted}\n\n"
        schema_names.append(schema_name)

        # WebHook 처리 - schema_type="request"일 때 webhook_out_schema 생성
        if protocol_type == "webhook" and schema_type == "request":
            webhook_spec = settings.get("webhook", {}).get("integrationSpec", {})
            if webhook_spec:
                webhook_schema_name = f"{endpoint_name}_webhook_out_schema"
                webhook_schema_obj = self._convert_webhook_spec_to_schema(webhook_spec)
                schema_content += f"# {endpoint_name} WebHook OUT Schema\n"
                formatted_webhook = self.schema_gen.format_schema_content(webhook_schema_obj)
                schema_content += f"{spec_id}{webhook_schema_name} = {formatted_webhook}\n\n"
                schema_names.append(webhook_schema_name)
                print(f"  ✓ WebHook OUT Schema 생성: {webhook_schema_name}")

        # WebHook 처리 - schema_type="response"일 때 webhook_in_schema 생성
        if protocol_type == "webhook" and schema_type == "response":
            webhook_spec = settings.get("webhook", {}).get("integrationSpec", {})
            if webhook_spec:
                webhook_schema_name = f"{endpoint_name}_webhook_in_schema"
                webhook_schema_obj = self._convert_webhook_spec_to_schema(webhook_spec)
                schema_content += f"# {endpoint_name} WebHook IN Schema\n"
                formatted_webhook = self.schema_gen.format_schema_content(webhook_schema_obj)
                schema_content += f"{spec_id}{webhook_schema_name} = {formatted_webhook}\n\n"
                schema_names.append(webhook_schema_name)
                print(f"  ✓ WebHook IN Schema 생성: {webhook_schema_name}")

        # Data 생성 (spec별로)
        data_info = self.data_gen.extract_endpoint_data(ts, file_type)
        data_name = data_info["name"]
        data_obj = data_info["content"]
        endpoint_name = data_info["endpoint"]
        if isinstance(data_obj, dict) and isinstance(data_obj.get("bodyJson"), list):
            data_obj = self.data_gen.build_data_from_spec(data_obj["bodyJson"])
        # 데이터 내용 추가
        data_content += f"# {endpoint_name}\n"
        formatted = self.data_gen.format_data_content(data_obj)
        data_content += f"{spec_id}{data_name} = {formatted}\n\n"
        data_names.append(data_name)

        # WebHook 처리 - file_type="response"일 때 webhook_in_data 생성
        if protocol_type == "webhook" and file_type == "response":
            webhook_request_spec = settings.get("webhook", {}).get("requestSpec", {})
            if webhook_request_spec:
                webhook_data_name = f"{endpoint_name}_webhook_in_data"

                # requestSpec이 리스트인 경우 (bodyJson 배열이 직접 들어있음)
                if isinstance(webhook_request_spec, list):
                    webhook_data_obj = self.data_gen.build_data_from_spec(webhook_request_spec)
                else:
                    # requestSpec이 딕셔너리인 경우 (bodyJson 키가 있을 수 있음)
                    webhook_data_obj = self._convert_webhook_spec_to_data(webhook_request_spec)

                data_content += f"# {endpoint_name} WebHook IN Data\n"
                formatted_webhook_data = self.data_gen.format_data_content(webhook_data_obj)
                data_content += f"{spec_id}{webhook_data_name} = {formatted_webhook_data}\n\n"
                data_names.append(webhook_data_name)
                print(f"  ✓ WebHook IN Data 생성: {webhook_data_name}")

        # WebHook 처리 - file_type="request"일 때 webhook_out_data 생성
        if protocol_type == "webhook" and file_type == "request":
            webhook_request_spec = settings.get("webhook", {}).get("requestSpec", {})
            if webhook_request_spec:
                webhook_data_name = f"{endpoint_name}_webhook_out_data"

                # requestSpec이 리스트인 경우 (bodyJson 배열이 직접 들어있음)
                if isinstance(webhook_request_spec, list):
                    webhook_data_obj = self.data_gen.build_data_from_spec(webhook_request_spec)
                else:
                    # requestSpec이 딕셔너리인 경우 (bodyJson 키가 있을 수 있음)
                    webhook_data_obj = self._convert_webhook_spec_to_data(webhook_request_spec)

                data_content += f"# {endpoint_name} WebHook OUT Data\n"
                formatted_webhook_data = self.data_gen.format_data_content(webhook_data_obj)
                data_content += f"{spec_id}{webhook_data_name} = {formatted_webhook_data}\n\n"
                data_names.append(webhook_data_name)
                print(f"  ✓ WebHook OUT Data 생성: {webhook_data_name}")

        endpoint_names.append(endpoint_name)

        #validation 생성
        vinfo = self.validation_gen.extract_enabled_validations(ts,
                                                                schema_type)  # {"endpoint":..., "validation": {...}}
        v_endpoint = vinfo.get("endpoint") or endpoint_name
        v_suffix = "_in_validation" if schema_type == "request" else "_out_validation"
        v_var_name = f"{spec_id}{v_endpoint}{v_suffix}"

        v_map = vinfo.get("validation", {})

        validation_content += f"# {v_endpoint}\n"
        if not v_map:
            # 데이터 없으면 빈 dict 출력
            validation_content += f"{v_var_name} = {{}}\n\n"
        else:
            raw_json = json.dumps(v_map, ensure_ascii=False, indent=2)
            py_style_json = re.sub(r'\btrue\b', 'True', raw_json)
            py_style_json = re.sub(r'\bfalse\b', 'False', py_style_json)
            validation_content += f"{v_var_name} = {py_style_json}\n\n"
        validation_names.append(v_var_name)

        # constraints 생성
        cinfo = self.const_gen.extract_value_type_fields(ts, file_type)
        c_endpoint = cinfo.get("endpoint") or endpoint_name
        c_suffix = "_in_constraints" if file_type == "request" else "_out_constraints"
        c_var_name = f"{spec_id}{c_endpoint}{c_suffix}"

        # extractor는 항상 {"endpoint":..., "validation": {...}} 반환한다고 가정
        c_map = cinfo.get("validation", {})

        constraints_content += f"# {c_endpoint}\n"
        if not c_map:
            # 데이터 없으면 빈 dict로 출력
            constraints_content += f"{c_var_name} = {{}}\n\n"
        else:
            c_raw_json = json.dumps(c_map, ensure_ascii=False, indent=2)
            c_py_style_json = re.sub(r'\btrue\b', 'True', c_raw_json)
            c_py_style_json = re.sub(r'\bfalse\b', 'False', c_py_style_json)
            constraints_content += f"{c_var_name} = {c_py_style_json}\n\n"
        constraints_names.append(c_var_name)

        # 기존과 동일하게 누적본 반환 + validation도 함께 반환
        return schema_content, data_content, validation_content, constraints_content

    def _generate_merged_files(self, spec_file_paths, schema_type, file_type):
        """여러 spec 파일을 하나의 파일에 spec별로 구분하여 생성"""

        if not spec_file_paths:
            return

        # Schema 파일과 Data 파일 내용을 담을 문자열
        schema_content = "from json_checker import OptionalKey\n\n\n"
        data_content = f"# {file_type} 모드\n\n"

        # 각 스펙별 리스트 이름 저장 (CONSTANTS.py 업데이트용)
        spec_list_names = []

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
                                    webhook_schema_str = schema_gen._generate_webhook_schema_from_json_schema(target_schema,
                                                                                                              endpoint_name,
                                                                                                              schema_type)
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
                                    webhook_schema_str = schema_gen._generate_webhook_schema_from_json_schema(target_schema,
                                                                                                              endpoint_name,
                                                                                                              schema_type)
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

                # CONSTANTS.py업데이트용
                spec_list_names.append(spec_info)

            except Exception as e:
                print(f"  경고: {spec_path} 처리 실패: {e}")
                import traceback
                traceback.print_exc()

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

            # 5. API에서 프로토콜/타임아웃 정보 추출 및 SPEC_CONFIG 업데이트
            selected_spec_id = self._get_selected_test_field_spec_id()
            if selected_spec_id:
                # SPEC_CONFIG 딕셔너리 업데이트
                spec_config_data = self._extract_spec_config_from_api(selected_spec_id)
                if spec_config_data:
                    self._update_spec_config(selected_spec_id, spec_config_data)

            # 6. 선택된 시험 분야의 인덱스 저장 (중요!)
            selected_spec_index = self._get_selected_spec_index()
            variables['selected_spec_index'] = selected_spec_index
            print(f"\n[CRITICAL] CONSTANTS.py에 저장할 selected_spec_index: {selected_spec_index}")
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



    def _extract_spec_config_from_api(self, spec_id):
        """test-steps API 캐시에서 spec_id별 프로토콜 설정 추출하여 SPEC_CONFIG 형식으로 반환"""
        try:
            # _steps_cache에서 해당 spec_id의 steps 가져오기
            steps = self._steps_cache.get(spec_id, [])
            if not steps:
                print(f"경고: spec_id={spec_id}에 대한 steps 캐시가 없습니다.")
                return None

            time_out = []
            num_retries = []
            trans_protocol = []

            for step in steps:
                step_id = step.get("id")
                if not step_id:
                    continue

                # _test_step_cache에서 step detail 가져오기
                cached_step = self._test_step_cache.get(step_id)
                if not cached_step:
                    print(f"경고: step_id={step_id}에 대한 캐시가 없습니다.")
                    # 기본값 추가
                    time_out.append(5000)
                    num_retries.append(1)
                    trans_protocol.append(None)
                    continue

                # detail.step.api.settings에서 설정 추출
                detail = cached_step.get("detail", {})
                settings = detail.get("step", {}).get("api", {}).get("settings", {})

                # connectTimeout 추출
                time_out.append(settings.get("connectTimeout", 5000))

                # loadTest.concurrentUsers 추출 (num_retries)
                load_test = settings.get("loadTest", {})
                num_retries.append(load_test.get("concurrentUsers", 1))

                # transProtocol 추출
                trans_protocol_obj = settings.get("transProtocol")
                # transProtocol이 문자열일 경우와 객체일 경우 모두 처리
                if isinstance(trans_protocol_obj, str):
                    # 문자열인 경우: "LongPolling", "WebHook" 등
                    trans_protocol_mode = trans_protocol_obj if trans_protocol_obj else None
                elif isinstance(trans_protocol_obj, dict):
                    # 객체인 경우: {"mode": "LongPolling"}
                    trans_protocol_mode = trans_protocol_obj.get("mode", None)
                else:
                    # null이거나 다른 타입
                    trans_protocol_mode = None
                trans_protocol.append(trans_protocol_mode)

            print(f"{spec_id} 프로토콜 설정 추출 완료: {len(time_out)}개 steps")

            return {
                "trans_protocol": trans_protocol,
                "time_out": time_out,
                "num_retries": num_retries
            }

        except Exception as e:
            print(f"spec_id={spec_id} 프로토콜 설정 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return None


    def _update_spec_config(self, spec_id, config_data):
        """CONSTANTS.py의 SPEC_CONFIG 딕셔너리에 spec_id별 설정 업데이트"""
        try:
            constants_path = "config/CONSTANTS.py"

            with open(constants_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # SPEC_CONFIG 딕셔너리 찾기 (중첩된 구조 처리)
            spec_config_start = content.find('SPEC_CONFIG = {')
            if spec_config_start == -1:
                print("경고: SPEC_CONFIG 딕셔너리를 찾을 수 없습니다.")
                return

            # 중괄호 개수를 세면서 끝 위치 찾기
            brace_count = 0
            start_pos = content.find('{', spec_config_start)
            current_pos = start_pos

            while current_pos < len(content):
                if content[current_pos] == '{':
                    brace_count += 1
                elif content[current_pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # SPEC_CONFIG의 끝 } 발견
                        end_pos = current_pos + 1
                        break
                current_pos += 1

            # 현재 SPEC_CONFIG 추출
            current_config = content[spec_config_start:end_pos]

            # spec_id가 이미 존재하는지 확인 (중첩된 중괄호 고려)
            spec_key_start = current_config.find(f'"{spec_id}":')

            # testSpecs.name 추출 (_spec_names_cache에서 가져오기)
            spec_name = self._spec_names_cache.get(spec_id, "")
            print(f"spec_id={spec_id}에 대한 spec_name: {spec_name}")

            # specs 파일 리스트 생성 (spec_id 기반)
            specs_list = [
                f"{spec_id}_inSchema",
                f"{spec_id}_outData",
                f"{spec_id}_messages"
            ]

            # 새로운 설정 문자열 생성 (순서: test_name, specs, trans_protocol, time_out, num_retries)
            new_spec_config = f'''"{spec_id}": {{
        "test_name": "{spec_name}",
        "specs": {specs_list},
        "trans_protocol": {config_data.get("trans_protocol", [])},
        "time_out": {config_data.get("time_out", [])},
        "num_retries": {config_data.get("num_retries", [])}
    }}'''

            if spec_key_start != -1:
                # 기존 설정 업데이트 - 해당 spec_id 블록 전체를 찾아서 교체
                # spec_id의 시작부터 해당 블록의 끝 }까지 찾기
                brace_start = current_config.find('{', spec_key_start)
                brace_count = 0
                pos = brace_start

                while pos < len(current_config):
                    if current_config[pos] == '{':
                        brace_count += 1
                    elif current_config[pos] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            brace_end = pos + 1
                            break
                    pos += 1

                # 기존 블록 전체 교체
                old_spec_block = current_config[spec_key_start:brace_end]
                new_config = current_config.replace(old_spec_block, new_spec_config)
                print(f"SPEC_CONFIG['{spec_id}'] 업데이트")
            else:
                # 새로운 설정 추가
                # SPEC_CONFIG = { ... } 에서 마지막 }를 찾아서 그 앞에 추가
                closing_brace = current_config.rfind('}')

                # 기존 항목이 있는지 확인 (빈 딕셔너리가 아닌지)
                if '":' in current_config:
                    # 기존 항목이 있으면 콤마 추가
                    new_config = current_config[:closing_brace] + f',\n    {new_spec_config}\n' + current_config[closing_brace:]
                else:
                    # 빈 딕셔너리면 그냥 추가
                    new_config = current_config[:closing_brace] + f'\n    {new_spec_config}\n' + current_config[closing_brace:]

                print(f"SPEC_CONFIG['{spec_id}'] 신규 추가")

            # 전체 내용에서 SPEC_CONFIG 교체
            content = content.replace(current_config, new_config)

            with open(constants_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"CONSTANTS.py SPEC_CONFIG 업데이트 완료")

        except Exception as e:
            print(f"SPEC_CONFIG 업데이트 실패: {e}")
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
                print("경고: 선택된 시험 분야가 없습니다. 기본값 0 사용")
                return 0

            # spec_id로 직접 판단 (파일 경로 대신)
            # spec-001 = 영상보안(index 0), spec-0011 = 보안용센서(index 1)
            spec_id_str = str(selected_spec_id).lower()

            if "spec-0011" in spec_id_str or "spec_0011" in spec_id_str:
                print("보안용 센서 시스템 선택됨 (index 1)")
                return 1  # 보안용 센서 시스템
            elif "spec-001" in spec_id_str or "spec_001" in spec_id_str:
                print("영상보안 시스템 선택됨 (index 0)")
                return 0  # 영상보안 시스템
            else:
                print(f"경고: 알 수 없는 spec_id '{selected_spec_id}'. 기본값 0 사용")
                return 0

        except Exception as e:
            print(f"선택된 spec 인덱스 가져오기 실패: {e}")
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


    def load_opt_files_from_api(self, test_data):
        """API 데이터를 이용하여 OPT 파일 로드 및 스키마 생성"""
        try:
            # test_specs 추출
            test_group = test_data.get("testRequest", {}).get("testGroup", {})
            test_specs = test_group.get("testSpecs", [])

            if not test_specs:
                QMessageBox.warning(self.parent, "데이터 없음", "testSpecs 데이터가 비어있습니다.")
                return

            print(f"\n=== API 기반 OPT 로드 시작 ===")
            print(f"spec 개수: {len(test_specs)}개")

            # 시험 분야 테이블 채우기 (testSpecs 기반)
            self._fill_test_field_table_from_api(test_specs)
            self.preload_all_spec_steps()
            self.preload_test_step_details_from_cache()

            # 모든 spec에 대해 SPEC_CONFIG 업데이트
            print(f"\n=== SPEC_CONFIG 업데이트 시작 ===")
            for spec in test_specs:
                spec_id = spec.get("id", "")
                if spec_id:
                    spec_config_data = self._extract_spec_config_from_api(spec_id)
                    if spec_config_data:
                        self._update_spec_config(spec_id, spec_config_data)
            print(f"=== SPEC_CONFIG 업데이트 완료 ===\n")

            self._generate_files_for_all_specs()
            # API 테이블은 첫 번째 분야를 자동 선택하여 표시 (API 기반)
            if self.parent.test_field_table.rowCount() > 0:
                self.parent.test_field_table.selectRow(0)
                self._fill_api_table_for_selected_field_from_api(0)

            # 버튼 상태 업데이트
            self.parent.check_start_button_state()
            self.parent.check_next_button_state()

        except Exception as e:
            print(f"API 데이터 로드 실패: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.parent, "오류", f"API 데이터 로드 중 오류가 발생했습니다:\n{str(e)}")


    def _fill_test_field_table_from_api(self, test_specs):
        """API testSpecs 배열로부터 시험 분야 테이블 채우기"""
        try:
            table = self.parent.test_field_table
            table.setRowCount(0)

            for i, spec in enumerate(test_specs):
                spec_id = spec.get("id", "")
                spec_name = spec.get("name", "")

                # spec_name을 캐시에 저장
                self._spec_names_cache[spec_id] = spec_name

                table.insertRow(i)

                # 시험 분야명
                field_item = QTableWidgetItem(spec_name)
                field_item.setData(Qt.UserRole, spec_id)  # spec_id 저장
                table.setItem(i, 0, field_item)

            print(f"시험 분야 테이블 채우기 완료: {len(test_specs)}개 항목")

        except Exception as e:
            print(f"시험 분야 테이블 채우기 실패: {e}")
            import traceback
            traceback.print_exc()


    def fetch_test_info_by_ip(self, ip_address):
        """IP 주소로 시험 정보 조회"""
        url = f"http://ect2.iptime.org:20223/api/integration/test-requests/by-ip?ipAddress={ip_address}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("success") and json_data.get("data"):
                print(f"API 호출 성공: {len(json_data['data'])}개 시험 정보 조회됨")
                return json_data["data"][0]
            else:
                raise ValueError("API 응답에 데이터가 없습니다.")
        except requests.exceptions.Timeout:
            print(f"API 호출 타임아웃: 서버 응답 시간 초과")
            return None
        except requests.exceptions.ConnectionError:
            print(f"API 호출 실패: 서버 연결 불가")
            return None
        except Exception as e:
            print(f"API 호출 실패: {e}")
            import traceback
            traceback.print_exc()
            return None


    def fetch_opt_by_spec_id(self, spec_id):
        """spec_id로 OPT 파일 조회 (API 기반)"""
        # TODO: spec_id를 서버에 전송하여 OPT JSON 받아오는 API 구현 필요
        # 현재는 임시로 로컬 파일 조회
        opt_file_path = f"opt_files/{spec_id}.json"

        if os.path.exists(opt_file_path):
            print(f"spec_id {spec_id}에 해당하는 OPT 파일 발견: {opt_file_path}")
            return opt_file_path
        else:
            print(f"spec_id {spec_id}에 해당하는 OPT 파일이 없습니다.")
            return None


    def load_specs_from_api_data(self, test_specs):
        """testSpecs 배열로부터 스펙 목록 동적 로드"""
        spec_file_paths = []

        print(f"testSpecs 배열로부터 {len(test_specs)}개 스펙 로드 시작...")
        for i, spec in enumerate(test_specs, 1):
            spec_id = spec.get("id", "")
            spec_name = spec.get("name", "")
            print(f"  {i}. {spec_name} (ID: {spec_id})")

            opt_path = self.fetch_opt_by_spec_id(spec_id)
            if opt_path:
                spec_file_paths.append(opt_path)

        print(f"총 {len(spec_file_paths)}개 스펙 파일 로드 완료")
        return spec_file_paths


    def fetch_specification_by_id(self, spec_id):
        """spec_id로 specification 상세 정보 조회 (API 기반)"""
        url = f"http://ect2.iptime.org:20223/api/integration/specifications/{spec_id}"
        try:
            print(f"Specification API 호출 중: {spec_id}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            json_data = response.json()
            print(f"Specification 조회 성공: {json_data.get('specification', {}).get('name', '')}")
            return json_data
        except requests.exceptions.Timeout:
            print(f"Specification API 타임아웃: {spec_id}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Specification API 연결 실패: {spec_id}")
            return None
        except Exception as e:
            print(f"Specification 조회 실패 ({spec_id}): {e}")
            return None


    def preload_all_spec_steps(self):
        """test_field_table에 있는 모든 spec_id의 steps(id, name)만 미리 캐싱"""

        table = self.parent.test_field_table
        row_count = table.rowCount()
        loaded, skipped = 0, 0

        for row in range(row_count):
            item = table.item(row, 0)
            if not item:
                continue
            spec_id = item.data(Qt.UserRole)
            if not spec_id:
                continue

            if spec_id in self._steps_cache:
                skipped += 1
                continue

            spec_data = self.fetch_specification_by_id(spec_id)
            if not spec_data:
                continue

            steps = spec_data.get("specification", {}).get("steps", [])
            # hasApi만 필터링하고, id/name만 저장
            trimmed = [
                {"id": s.get("id"), "name": s.get("name", "")}
                for s in steps if s.get("hasApi")
            ]
            self._steps_cache[spec_id] = trimmed
            loaded += 1

        print(f"[preload_all_spec_steps] 로드:{loaded}, 스킵:{skipped}, 총행:{row_count}")


    def _fill_api_table_for_selected_field_from_api(self, row):
        """선택된 시험 분야의 API 테이블 채우기 (API 기반)"""
        try:
            # spec_id 추출
            item = self.parent.test_field_table.item(row, 0)
            if not item:
                return

            spec_id = item.data(Qt.UserRole)
            if not spec_id:
                return

            cached_steps = self._steps_cache.get(spec_id)
            if cached_steps is None:
                # 백업: 혹시 캐시가 안돼있으면 1회 호출 후 최소 데이터로 변환
                spec_data = self.fetch_specification_by_id(spec_id)
                if not spec_data:
                    return
                steps = spec_data.get("specification", {}).get("steps", [])
                cached_steps = [
                    {"id": s.get("id"), "name": s.get("name", "")}
                    for s in steps if s.get("hasApi")
                ]
                # 필요 시 캐시에 저장(선택)
                self._steps_cache[spec_id] = cached_steps
            # API 테이블 초기화
            self.parent.api_test_table.setRowCount(0)

            # steps 순회하여 테이블 채우기
            for step in cached_steps:
                step_id = step.get("id")

                # [변경] _test_step_cache에 저장된 id/name 우선 사용
                ts = self._test_step_cache.get(step_id) if hasattr(self, "_test_step_cache") else None
                name_to_show = ""
                id_to_show = ""

                if ts:
                    # { "id": ..., "name": ..., "detail": {...} } 구조 가정
                    name_to_show = ts.get("name", "")
                    id_to_show = "" if ts.get("endpoint") is None else str(ts.get("endpoint"))
                else:
                    # 백업: 캐시에 없으면 기존 steps 값 사용
                    name_to_show = step.get("name", "")
                    id_to_show = "" if step_id is None else str(step_id)

                r = self.parent.api_test_table.rowCount()
                self.parent.api_test_table.insertRow(r)

                # 기능명 (name) -> 0열
                name_item = QTableWidgetItem(name_to_show)
                name_item.setTextAlignment(Qt.AlignCenter)
                name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.parent.api_test_table.setItem(r, 0, name_item)

                # 1열에는 id
                id_item = QTableWidgetItem(id_to_show)
                id_item.setTextAlignment(Qt.AlignCenter)
                id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.parent.api_test_table.setItem(r, 1, id_item)

            print(f"API 테이블 채우기 완료: {len(cached_steps)}개 API")

        except Exception as e:
            print(f"API 테이블 채우기 실패: {e}")
            import traceback
            traceback.print_exc()


    def fetch_test_step_by_id(self, step_id):
        """step_id로 test-step 상세 정보 조회 (API 기반)"""
        url = f"http://ect2.iptime.org:20223/api/integration/test-steps/{step_id}"
        try:
            print(f"Test-Step API 호출 중: {step_id}")
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # 응답 구조에 따라 이름 키가 다를 수 있어 안전하게 접근
            name = (
                    data.get("step", {}).get("name")
                    or data.get("name")
                    or ""
            )
            print(f"Test-Step 조회 성공: id={step_id}, name={name}")
            return data
        except requests.exceptions.Timeout:
            print(f"Test-Step API 타임아웃: {step_id}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Test-Step API 연결 실패: {step_id}")
            return None
        except Exception as e:
            print(f"Test-Step 조회 실패 ({step_id}): {e}")
            return None


    # [ADD] _steps_cache를 순회하며 step 상세 응답을 _test_step_cache에 저장
    def preload_test_step_details_from_cache(self):
        """
        _steps_cache에 들어있는 step.id로 test-steps API 호출 후
        _test_step_cache에 id, name, detail을 저장
        """
        loaded, skipped, empty = 0, 0, 0

        for spec_id, steps in self._steps_cache.items():
            if not isinstance(steps, list):
                continue

            for s in steps:
                step_id = s.get("id")
                step_name = s.get("name", "")

                if step_id is None:
                    empty += 1
                    continue

                # 이미 캐시에 있으면 스킵
                if step_id in self._test_step_cache:
                    skipped += 1
                    continue

                detail = self.fetch_test_step_by_id(step_id)
                if detail is not None:
                    step_verificationType = detail.get("step", {}).get("verificationType", "")

                    endpoint = (
                        detail.get("step", {})
                            .get("api", {})
                            .get("endpoint", "")
                    )
                    self._test_step_cache[step_id] = {
                        "id": step_id,
                        "name": step_name,
                        "endpoint": endpoint,
                        "verificationType": step_verificationType,
                        "detail": detail
                    }
                    loaded += 1
                    # print(self._test_step_cache[step_id])

        print(
            f"[preload_test_step_details_from_cache] "
            f"로드:{loaded}, 스킵:{skipped}, id없음:{empty}, "
            f"총 step 수(대략): {sum(len(v) for v in self._steps_cache.values())}"
        )
