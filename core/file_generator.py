"""
파일 생성 서비스 모듈
- Schema, Data, Validation, Constraints 파일 생성
- CONSTANTS.py 업데이트
- ResponseCode 파일 생성
"""

import sys
import os
import re
import json
from typing import Dict, List
from pathlib import Path

from api.client import APIClient
from core.schema_generator import SchemaGenerator
from core.data_generator import dataGenerator
from core.validation_generator import ValidationGenerator
from core.constraint_generator import constraintGeneractor
from core.key_generator import KeyIdGenerator
import config.CONSTANTS as CONSTANTS
from core.logger import Logger


class FileGeneratorService:
    """파일 생성을 담당하는 서비스 클래스"""

    def __init__(self):
        self.api_client = APIClient()
        self.schema_gen = SchemaGenerator()
        self.data_gen = dataGenerator()
        self.validation_gen = ValidationGenerator()
        self.const_gen = constraintGeneractor()
        self.key_id_gen = KeyIdGenerator()

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

    def generate_response_code_file(self):
        """API에서 response-codes를 가져와 spec/ResponseCode.py 파일 생성"""
        try:
            response_codes = self.api_client.fetch_response_codes()
            if not response_codes:
                return False

            # 데이터 변환: code는 그대로, description을 message로
            error_message = []
            for item in response_codes:
                error_message.append({
                    "code": item["code"],
                    "message": item["description"]
                })

            # Python 파일 생성
            content = "error_message = [\n"
            for i, msg in enumerate(error_message):
                comma = "," if i < len(error_message) - 1 else ""
                content += f'    {{"code": "{msg["code"]}", "message": "{msg["message"]}"}}{comma}\n'
            content += "]\n"

            # 파일 저장
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                spec_dir = os.path.join(exe_dir, "spec")
                os.makedirs(spec_dir, exist_ok=True)
                output_path = os.path.join(spec_dir, "ResponseCode.py")
            else:
                from core.functions import resource_path
                output_path = resource_path("spec/ResponseCode.py")

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            Logger.info(f"ResponseCode.py 생성 완료: {len(error_message)}개 응답 코드")
            Logger.info(f"[SPEC FILES] ResponseCode.py 저장 경로: {output_path}")
            return True

        except Exception as e:
            Logger.error(f"ResponseCode 파일 생성 실패: {e}")
            import traceback
            Logger.error(traceback.format_exc())
            return False

    def generate_files_for_all_specs(self, steps_cache, test_step_cache, spec_names_cache):
        """모든 testSpecIds를 하나의 파일로 합쳐서 생성 (schema + videoData)"""
        from PyQt5.QtWidgets import QApplication

        try:
            Logger.info(f"\n=== 산출물 생성 시작 ===")
            Logger.debug(f"specIds: {steps_cache.items()}")

            schema_content = ""
            data_content = ""
            validation_content = ""
            constraints_content = ""
            spec_list_names = []

            # 모든 spec의 중복 API명을 모으기 위한 전체 목록
            all_duplicate_endpoints = []

            for spec_id, steps in steps_cache.items():
                QApplication.processEvents()
                if not isinstance(steps, list):
                    continue

                schema_names = []
                data_names = []
                endpoint_names = []
                validation_names = []
                constraints_names = []
                webhook_schema_names = []
                webhook_data_names = []
                webhook_constraints_names = []
                webhook_validation_names = []
                schema_type = None
                file_type = None

                # 중복 API명 처리를 위한 카운터 (spec별로 초기화)
                endpoint_count = {}
                spec_duplicate_endpoints = []

                temp_spec_id = spec_id + "_"
                for s in steps:
                    QApplication.processEvents()
                    step_id = s.get("id")
                    ts = test_step_cache.get(step_id)

                    if ts:
                        schema_type = ts.get("verificationType")
                        if schema_type == 'request':
                            file_type = 'response'
                        elif schema_type == 'response':
                            file_type = 'request'

                        # endpoint명 추출 및 numbered_endpoint 계산
                        detail = ts.get("detail", {})
                        step_data = detail.get("step", {})
                        api = step_data.get("api", {})
                        raw_endpoint = api.get("endpoint", "")
                        base_endpoint = raw_endpoint[1:] if raw_endpoint.startswith("/") else raw_endpoint

                        if base_endpoint in endpoint_count:
                            endpoint_count[base_endpoint] += 1
                            numbered_endpoint = f"{base_endpoint}{endpoint_count[base_endpoint]}"
                        else:
                            endpoint_count[base_endpoint] = 1
                            numbered_endpoint = base_endpoint

                        ts["_numbered_endpoint"] = numbered_endpoint

                        schema_content, data_content, validation_content, constraints_content = self._generate_files_for_each_steps(
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
                            webhook_schema_names=webhook_schema_names,
                            webhook_data_names=webhook_data_names,
                            webhook_constraints_names=webhook_constraints_names,
                            webhook_validation_names=webhook_validation_names,
                            spec_id=temp_spec_id,
                            numbered_endpoint=numbered_endpoint
                        )

                # 모든 step 처리 후 KeyId 파일 생성
                if file_type:
                    self.key_id_gen.generate_keyid_files(
                        steps_cache,
                        test_step_cache,
                        file_type
                    )

                # 이 spec의 중복 API명 추출 (count >= 2)
                spec_duplicate_endpoints = [ep for ep, count in endpoint_count.items() if count >= 2]
                if spec_duplicate_endpoints:
                    all_duplicate_endpoints.extend(spec_duplicate_endpoints)
                    Logger.info(f"  [spec_id={spec_id}] 중복 API 감지: {spec_duplicate_endpoints}")

                if schema_type is None:
                    Logger.warning(f"[WARNING] spec_id={spec_id}: schema_type이 설정되지 않음, 건너뜁니다.")
                    continue

                # 스키마 리스트 생성
                if schema_type == "request":
                    list_name = f"{spec_id}_inSchema"
                else:
                    list_name = f"{spec_id}_outSchema"

                schema_content += f"# {spec_id} 스키마 리스트\n"
                schema_content += f"{list_name} = [\n"
                for name in schema_names:
                    schema_content += f"    {temp_spec_id}{name},\n"
                schema_content += "]\n\n"

                # WebHook 전용 스키마 리스트 생성
                if webhook_schema_names:
                    if file_type == "request":
                        webhook_schema_list_name = f"{spec_id}_webhook_inSchema"
                    else:
                        webhook_schema_list_name = f"{spec_id}_webhook_OutSchema"

                    schema_content += f"# {spec_id} WebHook 스키마 리스트\n"
                    schema_content += f"{webhook_schema_list_name} = [\n"

                    for endpoint in endpoint_names:
                        webhook_schema_name = f"{endpoint}_webhook_in_schema" if file_type == "request" else f"{endpoint}_webhook_out_schema"
                        if webhook_schema_name in webhook_schema_names:
                            schema_content += f"    {temp_spec_id}{webhook_schema_name},\n"
                        else:
                            schema_content += f"    None,\n"
                    schema_content += "]\n\n"

                # WebHook Validation 리스트 생성
                if webhook_validation_names:
                    if schema_type == "request":
                        webhook_v_list_name = f"{spec_id}_webhook_outValidation"
                    else:
                        webhook_v_list_name = f"{spec_id}_webhook_inValidation"

                    validation_content += f"# {spec_id} WebHook 검증 리스트\n"
                    validation_content += f"{webhook_v_list_name} = [\n"
                    for vname in webhook_validation_names:
                        validation_content += f"    {temp_spec_id}{vname},\n"
                    validation_content += "]\n\n"

                # 데이터 리스트 생성
                if file_type == "request":
                    data_list_name = f"{spec_id}_inData"
                else:
                    data_list_name = f"{spec_id}_outData"

                data_content += f"# {spec_id} 데이터 리스트\n"
                data_content += f"{data_list_name} = [\n"
                for name in data_names:
                    data_content += f"    {temp_spec_id}{name},\n"
                data_content += "]\n\n"

                # WebHook 전용 데이터 리스트 생성
                if webhook_data_names:
                    if file_type == "response":
                        webhook_data_list_name = f"{spec_id}_webhook_inData"
                    else:
                        webhook_data_list_name = f"{spec_id}_webhook_outData"

                    data_content += f"# {spec_id} WebHook 데이터 리스트\n"
                    data_content += f"{webhook_data_list_name} = [\n"

                    for endpoint in endpoint_names:
                        webhook_data_name = f"{endpoint}_webhook_out_data" if file_type == "request" else f"{endpoint}_webhook_in_data"
                        if webhook_data_name in webhook_data_names:
                            data_content += f"    {temp_spec_id}{webhook_data_name},\n"
                        else:
                            data_content += f"    None,\n"
                    data_content += "]\n\n"

                # Messages 리스트 생성
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
                if file_type == "response":
                    c_list_name = f"{spec_id}_outConstraints"
                else:
                    c_list_name = f"{spec_id}_inConstraints"

                constraints_content += f"# {spec_id} 검증 리스트\n"
                constraints_content += f"{c_list_name} = [\n"
                for cname in constraints_names:
                    constraints_content += f"    {cname},\n"
                constraints_content += "]\n\n"

                # WebHook Constraints 리스트 생성
                if webhook_constraints_names:
                    if file_type == "response":
                        webhook_c_list_name = f"{spec_id}_webhook_inConstraints"
                    else:
                        webhook_c_list_name = f"{spec_id}_webhook_outConstraints"

                    constraints_content += f"# {spec_id} WebHook Constraints 리스트\n"
                    constraints_content += f"{webhook_c_list_name} = [\n"

                    for endpoint in endpoint_names:
                        webhook_c_name = f"{endpoint}_webhook_in_constraints" if file_type == "response" else f"{endpoint}_webhook_out_constraints"
                        if webhook_c_name in webhook_constraints_names:
                            constraints_content += f"    {temp_spec_id}{webhook_c_name},\n"
                        else:
                            constraints_content += f"    None,\n"
                    constraints_content += "]\n\n"

                # CONSTANTS.py 업데이트용 리스트 저장
                spec_info = {
                    "spec_id": spec_id,
                    "inSchema": list_name if schema_type == "response" else f"{spec_id}_inSchema",
                    "outData": data_list_name if file_type == "request" else f"{spec_id}_outData",
                    "messages": messages_list_name,
                    "name": ts.get("detail", {}).get("testSpec", {}).get("name", "") if ts else ""
                }
                spec_list_names.append(spec_info)

            all_spec_list_names = []
            if spec_list_names:
                all_spec_list_names.extend(spec_list_names)

            # 역매핑 생성 및 referenceEndpoint 업데이트
            if file_type and all_duplicate_endpoints:
                Logger.info(f"\n  [전체 중복 API 목록] {all_duplicate_endpoints}")

                response_reverse_map = self.key_id_gen.build_field_id_to_endpoint_map(
                    steps_cache, test_step_cache, "response"
                )
                request_reverse_map = self.key_id_gen.build_field_id_to_endpoint_map(
                    steps_cache, test_step_cache, "request"
                )
                combined_reverse_map = {**request_reverse_map, **response_reverse_map}

                if schema_type == "request":
                    validation_content = self._update_reference_endpoints(validation_content, combined_reverse_map, "Validation_request", all_duplicate_endpoints)
                    constraints_content = self._update_reference_endpoints(constraints_content, combined_reverse_map, "Constraints_response", all_duplicate_endpoints)
                else:
                    validation_content = self._update_reference_endpoints(validation_content, combined_reverse_map, "Validation_response", all_duplicate_endpoints)
                    constraints_content = self._update_reference_endpoints(constraints_content, combined_reverse_map, "Constraints_request", all_duplicate_endpoints)

            # 파일 저장
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                spec_dir = os.path.join(exe_dir, "spec")
                os.makedirs(spec_dir, exist_ok=True)
                Logger.info(f"[SPEC FILES] 외부 spec 디렉토리 사용: {spec_dir}")

                schema_output = os.path.join(spec_dir, f"Schema_{schema_type}.py")
                data_output = os.path.join(spec_dir, f"Data_{file_type}.py")
                validation_output = os.path.join(spec_dir, f"validation_{schema_type}.py")
                constraints_output = os.path.join(spec_dir, f"Constraints_{file_type}.py")
            else:
                from core.functions import resource_path
                schema_output = resource_path(f"spec/Schema_{schema_type}.py")
                data_output = resource_path(f"spec/Data_{file_type}.py")
                validation_output = resource_path(f"spec/validation_{schema_type}.py")
                constraints_output = resource_path(f"spec/Constraints_{file_type}.py")

            output_files = [
                (schema_output, schema_content, "Schema"),
                (data_output, data_content, "Data"),
                (validation_output, validation_content, "Validation"),
                (constraints_output, constraints_content, "Constraints"),
            ]

            for path, content, label in output_files:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        Logger.info(f"[삭제 완료] 기존 {label} 파일 제거: {path}")

                    if "Schema_" in os.path.basename(path):
                        header = "from json_checker import OptionalKey\n\n\n"
                        content = header + content

                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    abs_path = os.path.abspath(path)
                    Logger.info(f"[생성 완료] {label} 파일 생성: {path} ({len(content.splitlines())} lines)")
                    Logger.info(f"[생성 완료] 절대 경로: {abs_path}")

                except Exception as e:
                    Logger.warning(f"[경고] {label} 파일 생성 실패: {path}, 사유: {e}")

            # CONSTANTS.py 업데이트
            if all_spec_list_names:
                self.update_constants_specs(all_spec_list_names)

            # ResponseCode 파일 생성
            self.generate_response_code_file()

            # Validation 캐시 클리어
            from core.validation_registry import clear_validation_cache
            clear_validation_cache()

            Logger.info(f"\n=== 산출물 생성 완료 ===\n")
            return all_spec_list_names

        except Exception as e:
            Logger.error(f"스키마 파일 생성 실패: {e}")
            import traceback
            Logger.error(traceback.format_exc())
            return []

    def _update_reference_endpoints(self, content: str, reverse_map: dict, file_label: str = "", duplicate_endpoints: list = None) -> str:
        """validation/constraints 내용에서 referenceFieldId를 기반으로 referenceEndpoint를 업데이트"""
        total_duplicate_endpoints = 0
        success_list = []
        fail_no_field_id = []
        fail_not_in_keyid = []

        if not reverse_map:
            return content

        if not duplicate_endpoints:
            duplicate_endpoints = []

        lines = content.split('\n')
        result_lines = []
        skip_current_block = False
        current_field_id = None
        current_block_key = None

        for line in lines:
            block_key_match = re.search(r'"(\w+)":\s*\{', line)
            if block_key_match:
                current_block_key = block_key_match.group(1)
                skip_current_block = False

            reference_field_match = re.search(r'"referenceField":\s*"([^"]+)"', line)
            if reference_field_match:
                reference_field_value = reference_field_match.group(1)
                if reference_field_value == "(참조 필드 미선택)":
                    skip_current_block = True

            field_id_match = re.search(r'"referenceFieldId":\s*"([^"]+)"', line)
            if field_id_match and not skip_current_block:
                current_field_id = field_id_match.group(1)

            endpoint_match = re.search(r'"referenceEndpoint":\s*"(/[^"]+)"', line)
            if endpoint_match and not skip_current_block:
                old_endpoint = endpoint_match.group(1)
                endpoint_name = old_endpoint[1:] if old_endpoint.startswith("/") else old_endpoint

                if endpoint_name in duplicate_endpoints:
                    total_duplicate_endpoints += 1

                    if current_field_id:
                        if current_field_id in reverse_map:
                            new_endpoint_name = reverse_map[current_field_id]
                            new_endpoint = f"/{new_endpoint_name}"
                            if old_endpoint != new_endpoint:
                                line = line.replace(f'"referenceEndpoint": "{old_endpoint}"', f'"referenceEndpoint": "{new_endpoint}"')
                            success_list.append({
                                "key": current_block_key,
                                "referenceEndpoint": old_endpoint,
                                "referenceFieldId": current_field_id,
                                "newReferenceEndpoint": new_endpoint
                            })
                        else:
                            fail_not_in_keyid.append({
                                "key": current_block_key,
                                "referenceEndpoint": old_endpoint,
                                "referenceFieldId": current_field_id
                            })
                    else:
                        fail_no_field_id.append({
                            "key": current_block_key,
                            "referenceEndpoint": old_endpoint
                        })

            if line.strip() == '}' or line.strip() == '},':
                current_field_id = None
                current_block_key = None

            result_lines.append(line)

        if total_duplicate_endpoints > 0:
            fail_count = len(fail_no_field_id) + len(fail_not_in_keyid)
            Logger.info(f"\n  [{file_label}] 중복 API referenceEndpoint 매핑 통계:")
            Logger.info(f"    - 중복 API명 목록: {duplicate_endpoints}")
            Logger.info(f"    - 중복 API referenceEndpoint 개수: {total_duplicate_endpoints}")
            Logger.info(f"    - 매핑 성공: {len(success_list)}")
            Logger.info(f"    - 매핑 실패: {fail_count}")

        return '\n'.join(result_lines)

    def _generate_files_for_each_steps(self, schema_type, file_type, ts, schema_content,
                                       data_content, schema_names, data_names, endpoint_names,
                                       validation_content, validation_names,
                                       constraints_content, constraints_names,
                                       webhook_schema_names, webhook_data_names, webhook_constraints_names, webhook_validation_names, spec_id,
                                       numbered_endpoint=None):
        """각 step에 대해 파일 내용 생성"""
        detail = ts.get("detail", {})
        step = detail.get("step", {})
        protocol_type = step.get("protocolType", "").lower()

        api = step.get("api", {})
        settings = api.get("settings", {})

        schema_info = self.schema_gen.generate_endpoint_schema(ts, schema_type)
        schema_name_orig = schema_info["name"]
        schema_obj = schema_info["content"]
        endpoint_name = schema_info["endpoint"]

        if numbered_endpoint is None:
            numbered_endpoint = endpoint_name

        schema_name = schema_name_orig.replace(endpoint_name, numbered_endpoint)

        schema_content += f"# {numbered_endpoint}\n"
        formatted = self.schema_gen.format_schema_content(schema_obj)
        schema_content += f"{spec_id}{schema_name} = {formatted}\n\n"
        schema_names.append(schema_name)

        # WebHook Schema 처리
        if protocol_type == "webhook" and schema_type == "request":
            webhook_spec = settings.get("webhook", {}).get("integrationSpec") or {}
            webhook_schema_name = f"{numbered_endpoint}_webhook_out_schema"
            webhook_schema_obj = self._convert_webhook_spec_to_schema(webhook_spec)
            schema_content += f"# {numbered_endpoint} WebHook OUT Schema\n"
            formatted_webhook = self.schema_gen.format_schema_content(webhook_schema_obj)
            schema_content += f"{spec_id}{webhook_schema_name} = {formatted_webhook}\n\n"
            webhook_schema_names.append(webhook_schema_name)
            Logger.info(f"  ✓ WebHook OUT Schema 생성: {webhook_schema_name}" + (" (빈 딕셔너리)" if not webhook_spec else ""))

        if protocol_type == "webhook" and schema_type == "response":
            webhook_spec = settings.get("webhook", {}).get("requestSpec") or {}
            webhook_schema_name = f"{numbered_endpoint}_webhook_in_schema"
            webhook_schema_obj = self._convert_webhook_spec_to_schema(webhook_spec)
            schema_content += f"# {numbered_endpoint} WebHook IN Schema\n"
            formatted_webhook = self.schema_gen.format_schema_content(webhook_schema_obj)
            schema_content += f"{spec_id}{webhook_schema_name} = {formatted_webhook}\n\n"
            webhook_schema_names.append(webhook_schema_name)
            Logger.info(f"  ✓ WebHook IN Schema 생성: {webhook_schema_name}" + (" (빈 딕셔너리)" if not webhook_spec else ""))

        # Data 생성
        data_info = self.data_gen.extract_endpoint_data(ts, file_type)
        data_name_orig = data_info["name"]
        data_obj = data_info["content"]
        if isinstance(data_obj, dict) and isinstance(data_obj.get("bodyJson"), list):
            data_obj = self.data_gen.build_data_from_spec(data_obj["bodyJson"])

        data_name = data_name_orig.replace(endpoint_name, numbered_endpoint)

        data_content += f"# {numbered_endpoint}\n"
        formatted = self.data_gen.format_data_content(data_obj)
        data_content += f"{spec_id}{data_name} = {formatted}\n\n"
        data_names.append(data_name)

        # WebHook Data 처리
        if protocol_type == "webhook" and file_type == "request":
            webhook_request_spec = settings.get("webhook", {}).get("integrationSpec") or {}
            webhook_data_name = f"{numbered_endpoint}_webhook_out_data"

            if isinstance(webhook_request_spec, list):
                webhook_data_obj = self.data_gen.build_data_from_spec(webhook_request_spec)
            else:
                webhook_data_obj = self._convert_webhook_spec_to_data(webhook_request_spec)

            data_content += f"# {numbered_endpoint} WebHook OUT Data\n"
            formatted_webhook_data = self.data_gen.format_data_content(webhook_data_obj)
            data_content += f"{spec_id}{webhook_data_name} = {formatted_webhook_data}\n\n"
            webhook_data_names.append(webhook_data_name)
            Logger.info(f"  ✓ WebHook OUT Data 생성: {webhook_data_name}" + (" (빈 딕셔너리)" if not webhook_request_spec else ""))

        if protocol_type == "webhook" and file_type == "response":
            webhook_request_spec = settings.get("webhook", {}).get("requestSpec") or {}
            webhook_data_name = f"{numbered_endpoint}_webhook_in_data"

            if isinstance(webhook_request_spec, list):
                webhook_data_obj = self.data_gen.build_data_from_spec(webhook_request_spec)
            else:
                webhook_data_obj = self._convert_webhook_spec_to_data(webhook_request_spec)

            data_content += f"# {numbered_endpoint} WebHook IN Data\n"
            formatted_webhook_data = self.data_gen.format_data_content(webhook_data_obj)
            data_content += f"{spec_id}{webhook_data_name} = {formatted_webhook_data}\n\n"
            webhook_data_names.append(webhook_data_name)
            Logger.info(f"  ✓ WebHook IN Data 생성: {webhook_data_name}" + (" (빈 딕셔너리)" if not webhook_request_spec else ""))

        endpoint_names.append(numbered_endpoint)

        # Validation 생성
        vinfo = self.validation_gen.extract_enabled_validations(ts, schema_type)
        v_endpoint = numbered_endpoint
        v_suffix = "_in_validation" if schema_type == "request" else "_out_validation"
        v_var_name = f"{spec_id}{v_endpoint}{v_suffix}"

        v_map = vinfo.get("validation", {})

        validation_content += f"# {v_endpoint}\n"
        if not v_map:
            validation_content += f"{v_var_name} = {{}}\n\n"
        else:
            raw_json = json.dumps(v_map, ensure_ascii=False, indent=2)
            py_style_json = re.sub(r'\btrue\b', 'True', raw_json)
            py_style_json = re.sub(r'\bfalse\b', 'False', py_style_json)
            validation_content += f"{v_var_name} = {py_style_json}\n\n"
        validation_names.append(v_var_name)

        # Constraints 생성
        cinfo = self.const_gen.extract_value_type_fields(ts, file_type)
        c_endpoint = numbered_endpoint
        c_suffix = "_in_constraints" if file_type == "request" else "_out_constraints"
        c_var_name = f"{spec_id}{c_endpoint}{c_suffix}"

        c_map = cinfo.get("validation", {})

        constraints_content += f"# {c_endpoint}\n"
        if not c_map:
            constraints_content += f"{c_var_name} = {{}}\n\n"
        else:
            c_raw_json = json.dumps(c_map, ensure_ascii=False, indent=2)
            c_py_style_json = re.sub(r'\btrue\b', 'True', c_raw_json)
            c_py_style_json = re.sub(r'\bfalse\b', 'False', c_py_style_json)
            constraints_content += f"{c_var_name} = {c_py_style_json}\n\n"
        constraints_names.append(c_var_name)

        # WebHook Constraints 처리
        if protocol_type == "webhook" and file_type == "response":
            webhook_request_spec = settings.get("webhook", {}).get("requestSpec") or {}
            webhook_c_name = f"{numbered_endpoint}_webhook_in_constraints"

            webhook_body_json = None
            if isinstance(webhook_request_spec, list):
                webhook_body_json = webhook_request_spec
            elif isinstance(webhook_request_spec, dict) and "bodyJson" in webhook_request_spec:
                webhook_body_json = webhook_request_spec.get("bodyJson")

            webhook_c_map = {}
            if webhook_body_json:
                webhook_c_map = self.const_gen.build_validation_map(webhook_body_json)

            constraints_content += f"# {numbered_endpoint} WebHook IN Constraints\n"
            if not webhook_c_map:
                constraints_content += f"{spec_id}{webhook_c_name} = {{}}\n\n"
            else:
                webhook_c_raw_json = json.dumps(webhook_c_map, ensure_ascii=False, indent=2)
                webhook_c_py_style_json = re.sub(r'\btrue\b', 'True', webhook_c_raw_json)
                webhook_c_py_style_json = re.sub(r'\bfalse\b', 'False', webhook_c_py_style_json)
                constraints_content += f"{spec_id}{webhook_c_name} = {webhook_c_py_style_json}\n\n"
            webhook_constraints_names.append(webhook_c_name)
            Logger.info(f"  ✓ WebHook IN Constraints 생성: {webhook_c_name}" + (" (빈 딕셔너리)" if not webhook_c_map else ""))

        if protocol_type == "webhook" and file_type == "request":
            webhook_request_spec = settings.get("webhook", {}).get("integrationSpec") or {}
            webhook_c_name = f"{numbered_endpoint}_webhook_out_constraints"

            webhook_body_json = None
            if isinstance(webhook_request_spec, list):
                webhook_body_json = webhook_request_spec
            elif isinstance(webhook_request_spec, dict) and "bodyJson" in webhook_request_spec:
                webhook_body_json = webhook_request_spec.get("bodyJson")

            webhook_c_map = {}
            if webhook_body_json:
                webhook_c_map = self.const_gen.build_validation_map(webhook_body_json)

            constraints_content += f"# {numbered_endpoint} WebHook OUT Constraints\n"
            if not webhook_c_map:
                constraints_content += f"{spec_id}{webhook_c_name} = {{}}\n\n"
            else:
                webhook_c_raw_json = json.dumps(webhook_c_map, ensure_ascii=False, indent=2)
                webhook_c_py_style_json = re.sub(r'\btrue\b', 'True', webhook_c_raw_json)
                webhook_c_py_style_json = re.sub(r'\bfalse\b', 'False', webhook_c_py_style_json)
                constraints_content += f"{spec_id}{webhook_c_name} = {webhook_c_py_style_json}\n\n"
            webhook_constraints_names.append(webhook_c_name)
            Logger.info(f"  ✓ WebHook OUT Constraints 생성: {webhook_c_name}" + (" (빈 딕셔너리)" if not webhook_c_map else ""))

        # WebHook Validation 처리
        if protocol_type == "webhook" and schema_type == "request":
            webhook_spec = settings.get("webhook", {}).get("integrationSpec") or []
            webhook_v_name = f"{numbered_endpoint}_webhook_out_validation"
            webhook_v_map = self.validation_gen._extract_webhook_validation(webhook_spec)

            validation_content += f"# {numbered_endpoint} WebHook OUT Validation\n"
            if not webhook_v_map:
                validation_content += f"{spec_id}{webhook_v_name} = {{}}\n\n"
            else:
                raw_json = json.dumps(webhook_v_map, ensure_ascii=False, indent=2)
                py_style_json = re.sub(r'\btrue\b', 'True', raw_json)
                py_style_json = re.sub(r'\bfalse\b', 'False', py_style_json)
                validation_content += f"{spec_id}{webhook_v_name} = {py_style_json}\n\n"

            webhook_validation_names.append(webhook_v_name)
            Logger.info(f"  ✓ WebHook OUT Validation 생성: {webhook_v_name}" + (" (빈 딕셔너리)" if not webhook_v_map else ""))

        if protocol_type == "webhook" and schema_type == "response":
            webhook_spec = settings.get("webhook", {}).get("requestSpec") or []
            webhook_v_name = f"{numbered_endpoint}_webhook_in_validation"
            webhook_v_map = self.validation_gen._extract_webhook_validation(webhook_spec)

            validation_content += f"# {numbered_endpoint} WebHook IN Validation\n"
            if not webhook_v_map:
                validation_content += f"{spec_id}{webhook_v_name} = {{}}\n\n"
            else:
                raw_json = json.dumps(webhook_v_map, ensure_ascii=False, indent=2)
                py_style_json = re.sub(r'\btrue\b', 'True', raw_json)
                py_style_json = re.sub(r'\bfalse\b', 'False', py_style_json)
                validation_content += f"{spec_id}{webhook_v_name} = {py_style_json}\n\n"

            webhook_validation_names.append(webhook_v_name)
            Logger.info(f"  ✓ WebHook IN Validation 생성: {webhook_v_name}" + (" (빈 딕셔너리)" if not webhook_v_map else ""))

        return schema_content, data_content, validation_content, constraints_content

    def update_constants_specs(self, spec_list_names):
        """CONSTANTS.py의 specs 리스트를 업데이트"""
        try:
            from core.functions import resource_path

            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
            else:
                constants_path = resource_path("config/CONSTANTS.py")

            with open(constants_path, 'r', encoding='utf-8') as f:
                content = f.read()

            specs_lines = []
            for spec_info in spec_list_names:
                in_schema = spec_info.get("inSchema", "")
                out_data = spec_info.get("outData", "")
                messages = spec_info.get("messages", "")
                webhook_schema = spec_info.get("webhookSchema", "")
                webhook_data = spec_info.get("webhookData", "")
                name = spec_info.get("name", "")

                if webhook_schema and webhook_data:
                    spec_line = f'["{in_schema}","{out_data}","{messages}","{webhook_schema}","{webhook_data}","{name}"]'
                else:
                    spec_line = f'["{in_schema}","{out_data}","{messages}","{name}"]'

                specs_lines.append(spec_line)

            specs_str = "specs = [" + ",\n         ".join(specs_lines) + "]"

            pattern = r'specs\s*=\s*\[\[.*?\]\]'

            if re.search(pattern, content, re.DOTALL):
                new_content = re.sub(pattern, specs_str, content, flags=re.DOTALL)
            else:
                url_pattern = r'(# 관리자시스템 주소\nmanagement_url\s*=\s*load_management_url\(\)\n)'
                if re.search(url_pattern, content):
                    new_content = re.sub(url_pattern, r'\1' + specs_str + '\n', content)
                else:
                    none_msg_pattern = r'(none_request_message\s*=)'
                    new_content = re.sub(none_msg_pattern, specs_str + '\n' + r'\1', content)

            with open(constants_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            Logger.info(f"CONSTANTS.py specs 리스트 업데이트 완료")

        except Exception as e:
            Logger.error(f"  경고: CONSTANTS.py specs 업데이트 실패: {e}")
            import traceback
            Logger.error(traceback.format_exc())

    def merge_list_prefix_mappings(self, file_a: str, file_b: str) -> Dict[str, Dict[str, List[str]]]:
        """두 파일에서 리스트 변수를 추출하여 prefix별로 병합"""
        result: Dict[str, Dict[str, List[str]]] = {}

        for file_path in (file_a, file_b):
            if not os.path.exists(file_path):
                Logger.warning(f"[WARNING] 파일이 존재하지 않음: {file_path}")
                continue

            file_name = os.path.basename(file_path)
            lists = self.extract_lists(file_path)

            for var_name, _items in lists.items():
                parts = var_name.split("_", 1)
                if len(parts) < 2:
                    continue
                prefix = parts[0]

                if prefix not in result:
                    result[prefix] = {}
                if file_name not in result[prefix]:
                    result[prefix][file_name] = []
                result[prefix][file_name].append(var_name)

        return result

    def extract_lists(self, file_path: str) -> Dict[str, List[str]]:
        """파일에서 리스트 변수들을 추출"""
        result: Dict[str, List[str]] = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\['
            for match in re.finditer(pattern, content, re.MULTILINE):
                var_name = match.group(1)
                result[var_name] = []

        except Exception as e:
            Logger.error(f"[ERROR] 파일 읽기 실패 ({file_path}): {e}")

        return result
