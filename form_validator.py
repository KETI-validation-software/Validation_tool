import re
import requests
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from core.functions import resource_path
from core.opt_loader import OptLoader
import os
from core.schema_generator import SchemaGenerator
from core.data_generator import dataGenerator
from core.validation_generator import ValidationGenerator
from core.constraint_generator import constraintGeneractor
import json
import ast
from pathlib import Path
from typing import Dict, List
import inspect
import spec.Data_response as Data_response
import config.CONSTANTS as CONSTANTS

class ClickableLabel(QLabel):
    """클릭 가능한 QLabel - 시험 분야 셀용"""
    clicked = pyqtSignal(int, int)  # row, column 전달

    def __init__(self, text, row, col, parent=None):
        super().__init__(text, parent)
        self.row = row
        self.col = col
        self.setCursor(Qt.PointingHandCursor)  # 마우스 커서를 포인터로

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.row, self.col)
        super().mousePressEvent(event)

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

    def _generate_response_code_file(self):
        """API에서 response-codes를 가져와 spec/ResponseCode.py 파일 생성"""
        try:
            import requests
            import sys
            import os

            url = f"{CONSTANTS.management_url}/api/integration/response-codes"
            print(f"ResponseCode API 호출 중: {url}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("success") and json_data.get("data"):
                # 데이터 변환: code는 그대로, description을 message로
                error_message = []
                for item in json_data["data"]:
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
                # ===== PyInstaller 환경에서 외부 spec 디렉토리 우선 사용 =====
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

                print(f"ResponseCode.py 생성 완료: {len(error_message)}개 응답 코드")
                print(f"[SPEC FILES] ResponseCode.py 저장 경로: {output_path}")
                return True
            else:
                print("ResponseCode API 응답에 데이터가 없습니다.")
                return False

        except requests.exceptions.Timeout:
            print("ResponseCode API 타임아웃")
            return False
        except Exception as e:
            print(f"ResponseCode 파일 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

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
                webhook_schema_names = []  # webhook 전용 스키마 리스트
                webhook_data_names = []    # webhook 전용 데이터 리스트
                webhook_constraints_names = []  # webhook 전용 constraints 리스트

                # 기본값 설정 (steps가 비어있거나 ts가 없는 경우 대비)
                schema_type = None
                file_type = None

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
                            webhook_schema_names=webhook_schema_names,
                            webhook_data_names=webhook_data_names,
                            webhook_constraints_names=webhook_constraints_names,
                            spec_id = temp_spec_id
                        )
                # schema_type이 설정되지 않았으면 이 spec 건너뛰기
                if schema_type is None:
                    print(f"[WARNING] spec_id={spec_id}: schema_type이 설정되지 않음, 건너뜁니다.")
                    continue

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
                webhook_schema_list_name = None

                if webhook_schema_names:
                    if file_type == "request":
                        webhook_schema_list_name = f"{spec_id}_webhook_inSchema"
                    else:
                        webhook_schema_list_name = f"{spec_id}_webhook_OutSchema"

                if webhook_schema_list_name:  # ✅ 실제 값이 있을 때만 추가
                    schema_content += f"# {spec_id} WebHook 스키마 리스트\n"
                    schema_content += f"{webhook_schema_list_name} = [\n"
                    for name in webhook_schema_names:
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

                # WebHook 전용 데이터 리스트 생성
                if webhook_data_names:
                    if file_type == "response":
                        webhook_data_list_name = f"{spec_id}_webhook_inData"
                    else :
                        webhook_data_list_name = f"{spec_id}_webhook_outData"
                    data_content += f"# {spec_id} WebHook 데이터 리스트\n"
                    data_content += f"{webhook_data_list_name} = [\n"
                    for name in webhook_data_names:
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
                    for cname in webhook_constraints_names:
                        constraints_content += f"    {temp_spec_id}{cname},\n"
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


            all_spec_list_names = []

            if spec_list_names:
                all_spec_list_names.extend(spec_list_names)

            # 파일 저장
            import sys
            import os

            # ===== PyInstaller 환경에서 외부 spec 디렉토리 우선 사용 =====
            if getattr(sys, 'frozen', False):
                # PyInstaller 환경: 외부 디렉토리 사용 (CONSTANTS.py와 동일)
                exe_dir = os.path.dirname(sys.executable)
                spec_dir = os.path.join(exe_dir, "spec")
                # spec 폴더가 없으면 생성
                os.makedirs(spec_dir, exist_ok=True)
                print(f"[SPEC FILES] 외부 spec 디렉토리 사용: {spec_dir}")

                schema_output = os.path.join(spec_dir, f"Schema_{schema_type}.py")
                data_output = os.path.join(spec_dir, f"Data_{file_type}.py")
                validation_output = os.path.join(spec_dir, f"validation_{schema_type}.py")
                constraints_output = os.path.join(spec_dir, f"Constraints_{file_type}.py")
            else:
                # 일반 실행: resource_path 사용
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
                    # 1️⃣ 기존 파일 삭제
                    if os.path.exists(path):
                        os.remove(path)
                        print(f"[삭제 완료] 기존 {label} 파일 제거: {path}")

                    # 2️⃣ Schema 파일에는 OptionalKey 임포트 추가
                    if "Schema_" in os.path.basename(path):
                        header = "from json_checker import OptionalKey\n\n\n"
                        content = header + content

                    # 3️⃣ 새 파일 생성
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    # ===== 절대 경로 로그 추가 =====
                    abs_path = os.path.abspath(path)
                    print(f"[생성 완료] {label} 파일 생성: {path} ({len(content.splitlines())} lines)")
                    print(f"[생성 완료] 절대 경로: {abs_path}")
                    # ===== 로그 끝 =====

                except Exception as e:
                    print(f"[경고] {label} 파일 생성 실패: {path}, 사유: {e}")

            # CONSTANTS.py 업데이트 (specs 리스트 생성 비활성화)
            if all_spec_list_names:
                self._update_constants_specs(all_spec_list_names)

            # ResponseCode 파일 생성
            self._generate_response_code_file()

            print(f"\n=== 산출물 생성 완료 ===\n")

        except Exception as e:
            print(f"스키마 파일 생성 실패: {e}")
            import traceback
            traceback.print_exc()

    def _generate_files_for_each_steps(self, schema_type, file_type, ts, schema_content,
                                       data_content, schema_names, data_names, endpoint_names,
                                       validation_content, validation_names,
                                   constraints_content, constraints_names,
                                   webhook_schema_names, webhook_data_names, webhook_constraints_names, spec_id):

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
            webhook_spec = settings.get("webhook", {}).get("integrationSpec") or {}
            webhook_schema_name = f"{endpoint_name}_webhook_out_schema"
            webhook_schema_obj = self._convert_webhook_spec_to_schema(webhook_spec)
            schema_content += f"# {endpoint_name} WebHook OUT Schema\n"
            formatted_webhook = self.schema_gen.format_schema_content(webhook_schema_obj)
            schema_content += f"{spec_id}{webhook_schema_name} = {formatted_webhook}\n\n"
            webhook_schema_names.append(webhook_schema_name)  # webhook 전용 리스트에 추가
            print(f"  ✓ WebHook OUT Schema 생성: {webhook_schema_name}" + (" (빈 딕셔너리)" if not webhook_spec else ""))

        # WebHook 처리 - schema_type="response"일 때 webhook_in_schema 생성
        if protocol_type == "webhook" and schema_type == "response":
            webhook_spec = settings.get("webhook", {}).get("requestSpec") or {}
            webhook_schema_name = f"{endpoint_name}_webhook_in_schema"
            webhook_schema_obj = self._convert_webhook_spec_to_schema(webhook_spec)
            schema_content += f"# {endpoint_name} WebHook IN Schema\n"
            formatted_webhook = self.schema_gen.format_schema_content(webhook_schema_obj)
            schema_content += f"{spec_id}{webhook_schema_name} = {formatted_webhook}\n\n"
            webhook_schema_names.append(webhook_schema_name)  # webhook 전용 리스트에 추가
            print(f"  ✓ WebHook IN Schema 생성: {webhook_schema_name}" + (" (빈 딕셔너리)" if not webhook_spec else ""))

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
        if protocol_type == "webhook" and file_type == "request":
            webhook_request_spec = settings.get("webhook", {}).get("integrationSpec") or {}
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
            webhook_data_names.append(webhook_data_name)  # webhook 전용 리스트에 추가
            print(f"  ✓ WebHook OUT Data 생성: {webhook_data_name}" + (" (빈 딕셔너리)" if not webhook_request_spec else ""))

        # WebHook 처리 - file_type="request"일 때 webhook_out_data 생성
        if protocol_type == "webhook" and file_type == "response":
            webhook_request_spec = settings.get("webhook", {}).get("requestSpec") or {}
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
            webhook_data_names.append(webhook_data_name)  # webhook 전용 리스트에 추가
            print(f"  ✓ WebHook IN Data 생성: {webhook_data_name}" + (" (빈 딕셔너리)" if not webhook_request_spec else ""))

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

        # WebHook Constraints 처리 - file_type="response"일 때 webhook_in_constraints 생성
        if protocol_type == "webhook" and file_type == "response":
            webhook_request_spec = settings.get("webhook", {}).get("requestSpec") or {}
            webhook_c_name = f"{endpoint_name}_webhook_in_constraints"

            # requestSpec에서 bodyJson 추출하여 valueType 필드 찾기
            webhook_body_json = None
            if isinstance(webhook_request_spec, list):
                webhook_body_json = webhook_request_spec
            elif isinstance(webhook_request_spec, dict) and "bodyJson" in webhook_request_spec:
                webhook_body_json = webhook_request_spec.get("bodyJson")

            # valueType 필드가 있으면 constraints 생성
            webhook_c_map = {}
            if webhook_body_json:
                webhook_c_map = self.const_gen.build_validation_map(webhook_body_json)

            constraints_content += f"# {endpoint_name} WebHook IN Constraints\n"
            if not webhook_c_map:
                constraints_content += f"{spec_id}{webhook_c_name} = {{}}\n\n"
            else:
                webhook_c_raw_json = json.dumps(webhook_c_map, ensure_ascii=False, indent=2)
                webhook_c_py_style_json = re.sub(r'\btrue\b', 'True', webhook_c_raw_json)
                webhook_c_py_style_json = re.sub(r'\bfalse\b', 'False', webhook_c_py_style_json)
                constraints_content += f"{spec_id}{webhook_c_name} = {webhook_c_py_style_json}\n\n"
            webhook_constraints_names.append(webhook_c_name)
            print(f"  ✓ WebHook IN Constraints 생성: {webhook_c_name}" + (" (빈 딕셔너리)" if not webhook_c_map else ""))

        # WebHook Constraints 처리 - file_type="request"일 때 webhook_out_constraints 생성
        if protocol_type == "webhook" and file_type == "request":
            webhook_request_spec = settings.get("webhook", {}).get("integrationSpec") or {}
            webhook_c_name = f"{endpoint_name}_webhook_out_constraints"

            # requestSpec에서 bodyJson 추출하여 valueType 필드 찾기
            webhook_body_json = None
            if isinstance(webhook_request_spec, list):
                webhook_body_json = webhook_request_spec
            elif isinstance(webhook_request_spec, dict) and "bodyJson" in webhook_request_spec:
                webhook_body_json = webhook_request_spec.get("bodyJson")

            # valueType 필드가 있으면 constraints 생성
            webhook_c_map = {}
            if webhook_body_json:
                webhook_c_map = self.const_gen.build_validation_map(webhook_body_json)

            constraints_content += f"# {endpoint_name} WebHook OUT Constraints\n"
            if not webhook_c_map:
                constraints_content += f"{spec_id}{webhook_c_name} = {{}}\n\n"
            else:
                webhook_c_raw_json = json.dumps(webhook_c_map, ensure_ascii=False, indent=2)
                webhook_c_py_style_json = re.sub(r'\btrue\b', 'True', webhook_c_raw_json)
                webhook_c_py_style_json = re.sub(r'\bfalse\b', 'False', webhook_c_py_style_json)
                constraints_content += f"{spec_id}{webhook_c_name} = {webhook_c_py_style_json}\n\n"
            webhook_constraints_names.append(webhook_c_name)
            print(f"  ✓ WebHook OUT Constraints 생성: {webhook_c_name}" + (" (빈 딕셔너리)" if not webhook_c_map else ""))

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
            import sys
            import os
            from core.functions import resource_path

            # ===== 수정: PyInstaller 환경에서 외부 config 우선 사용 =====
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
            else:
                constants_path = resource_path("config/CONSTANTS.py")
            # ===== 수정 끝 =====

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
                # specs가 없으면 추가 (management_url 라인 다음에)
                # management_url은 전역 변수이므로 함수 밖에 있음
                url_pattern = r'(# 관리자시스템 주소\nmanagement_url\s*=\s*load_management_url\(\)\n)'
                if re.search(url_pattern, content):
                    new_content = re.sub(url_pattern, r'\1' + specs_str + '\n', content)
                else:
                    # management_url도 없으면 none_request_message 앞에 추가
                    none_msg_pattern = r'(none_request_message\s*=)'
                    new_content = re.sub(none_msg_pattern, specs_str + '\n' + r'\1', content)

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
        # MAIN_TEST 또는 UI에 표시되는 "본시험" 모두 체크
        return test_category == "MAIN_TEST" or test_category == "본시험"


    def is_admin_code_valid(self):
        """관리자 코드 유효성 검사"""
        if not self.is_admin_code_required():
            # 사전시험인 경우 관리자 코드가 필요하지 않으므로 유효
            return True

        admin_code = self.parent.admin_code_edit.text().strip()
        # MAIN_TEST인 경우 숫자가 입력되어야 함
        return bool(admin_code and admin_code.isdigit())


    def handle_test_category_change(self):
        """시험유형 변경 시 관리자 코드 필드 활성화/비활성화"""
        test_category = self.parent.test_category_edit.text().strip()

        # 빈 값인 경우는 아무것도 하지 않음
        if not test_category:
            self.parent.admin_code_edit.setEnabled(False)
            self.parent.admin_code_edit.clear()
            self.parent.admin_code_edit.setPlaceholderText("")
            return

        # 이미 변환된 값("본시험", "사전시험")이면 처리하지 않음
        if test_category in ["본시험", "사전시험"]:
            if test_category == "본시험":
                self.parent.admin_code_edit.setEnabled(True)
                self.parent.admin_code_edit.setPlaceholderText("")
            else:  # "사전시험"
                self.parent.admin_code_edit.setEnabled(False)
                self.parent.admin_code_edit.clear()
                self.parent.admin_code_edit.setPlaceholderText("")
            return

        # 원래 값을 보관
        self.parent.original_test_category = test_category

        # MAIN_TEST를 본시험으로 표시
        if test_category == "MAIN_TEST":
            self.parent.test_category_edit.setText("본시험")
            self.parent.admin_code_edit.setEnabled(True)
            self.parent.admin_code_edit.setPlaceholderText("")
        else:
            # MAIN_TEST 이외의 모든 값은 UI에 "사전시험"으로 표시
            self.parent.test_category_edit.setText("사전시험")
            self.parent.admin_code_edit.setEnabled(False)
            self.parent.admin_code_edit.clear()
            self.parent.admin_code_edit.setPlaceholderText("")


    def handle_test_range_change(self):
        """시험범위 변경 시 UI 표시 텍스트 변환"""
        test_range = self.parent.test_range_edit.text().strip()

        # 빈 값인 경우는 아무것도 하지 않음
        if not test_range:
            return

        # 이미 변환된 값("전체필드", "필수필드")이면 처리하지 않음
        if test_range in ["전체필드", "필수필드"]:
            return

        # 원래 값을 보관
        self.parent.original_test_range = test_range

        # ALL_FIELDS를 전체필드로 표시
        if test_range == "ALL_FIELDS":
            self.parent.test_range_edit.setText("전체필드")
        else:
            # ALL_FIELDS 이외의 모든 값은 UI에 "필수필드"로 표시
            self.parent.test_range_edit.setText("필수필드")


    # ---------- CONSTANTS.py 업데이트 ----------

    def update_constants_py(self):
        """CONSTANTS.py 파일의 변수들을 GUI 입력값으로 업데이트"""
        try:
            from core.functions import resource_path
            import sys
            import os

            # ===== 수정: PyInstaller 환경에서 외부 config 우선 사용 =====
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
            else:
                constants_path = resource_path("config/CONSTANTS.py")
            # ===== 수정 끝 =====

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
            variables['contact_person'] = getattr(self.parent, 'contact_person', "")
            variables['model_name'] = getattr(self.parent, 'model_name', "")
            variables['request_id'] = getattr(self.parent, 'request_id', "")

            # 5. SPEC_CONFIG 전체 덮어쓰기 (모든 spec_id 포함)
            self.overwrite_spec_config_from_mapping()

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
        test_category = self.parent.test_category_edit.text().strip()
        test_range = self.parent.test_range_edit.text().strip()

        # 시험유형 UI 표시값을 원래 값으로 복원
        if test_category == "본시험":
            test_category = "MAIN_TEST"
        elif test_category == "사전시험":
            # 원래 값이 보관되어 있으면 복원, 없으면 "사전시험" 그대로
            test_category = self.parent.original_test_category if self.parent.original_test_category else "사전시험"

        # 시험범위 UI 표시값을 원래 값으로 복원
        if test_range == "전체필드":
            test_range = "ALL_FIELDS"
        elif test_range == "필수필드":
            # 원래 값이 보관되어 있으면 복원, 없으면 "필수필드" 그대로
            test_range = self.parent.original_test_range if self.parent.original_test_range else "필수필드"

        return {
            'company_name': self.parent.company_edit.text().strip(),
            'product_name': self.parent.product_edit.text().strip(),
            'version': self.parent.version_edit.text().strip(),
            'test_category': test_category,
            'test_target': self.parent.test_group_edit.text().strip(),
            'test_range': test_range
        }


    def _collect_auth_info(self):
        """인증 정보 수집"""
        if self.parent.digest_radio.isChecked():
            auth_type = "Digest Auth"
        else:
            auth_type = "Bearer Token"
        auth_info = f"{self.parent.id_input.text().strip()},{self.parent.pw_input.text().strip()}"
        '''
            updated = False 
            for name, value in vars(Data_response).items():
                # 리스트 이름에 'Authentication'이 포함된 변수만 찾기
                if "authentication" in name.lower() and isinstance(value, dict):
                    if "accessToken" in value:
                        old_token = value["accessToken"]
                        value["accessToken"] = auth_info
                        print(f"[✅] {name} accessToken updated: {old_token} → {auth_info}")
                        updated = True
                        break

                # 실제 파일 수정 반영 (파일 내 accessToken 문자열 교체)
            if updated:
                # ===== 수정: PyInstaller 환경에서는 파일 업데이트 스킵 =====
                import sys
                if not getattr(sys, 'frozen', False):
                    # 로컬 환경에서만 파일 업데이트
                    file_path = Path(inspect.getfile(Data_response))
                    text = file_path.read_text(encoding="utf-8")

                    # 첫 번째 accessToken 값만 교체
                    new_text = re.sub(
                        r'(["\']accessToken["\']\s*:\s*["\'])([^"\']*)(["\'])',
                        rf'\1{auth_info}\3',
                        text,
                        count=0,
                        flags=re.IGNORECASE
                    )

                    file_path.write_text(new_text, encoding="utf-8")
                    print(f"Data_response.py 파일에 토큰 반영 완료 → {file_path}")
                else:
                    # PyInstaller 환경에서는 메모리만 업데이트 (파일은 read-only)
                    print(f"[PyInstaller] Data_response 메모리에만 토큰 반영 완료")
                # ===== 수정 끝 =====
                
            else:
                print("Authentication 관련 변수를 찾지 못했습니다.")'''

        return auth_type, auth_info



    def _extract_spec_config_from_api(self, spec_id):
        """test-steps API 캐시에서 spec_id별 프로토콜 설정 추출하여 SPEC_CONFIG 형식으로 반환"""
        try:
            # _steps_cache에서 해당 spec_id의 steps 가져오기
            steps = self._steps_cache.get(spec_id, [])
            if not steps:
                print(f"경고: spec_id={spec_id}에 대한 steps 캐시가 없습니다.")
                return None

            # print(f"\n[DEBUG] _extract_spec_config_from_api 호출")
            # print(f"  spec_id: {spec_id}")
            # print(f"  _steps_cache의 step 개수: {len(steps)}")
            # print(f"  steps: {[s.get('id') for s in steps]}")

            time_out = []
            num_retries = []
            trans_protocol = []
            api_name = []
            api_id = []
            api_endpoint = []

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

                api_name.append(detail.get("step", {}).get("api", {}).get("name", {}))
                api_id.append(detail.get("step", {}).get("id", {}))
                api_endpoint.append(detail.get("step", {}).get("api", {}).get("endpoint", {}))

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

            print(f"  {spec_id} 프로토콜 설정 추출 완료: {len(time_out)}개 steps")
            print(f"  trans_protocol: {trans_protocol}")
            print(f"  time_out: {time_out}")
            print(f"  num_retries: {num_retries}\n")

            return {
                "api_name": api_name,
                "api_id": api_id,
                "api_endpoint":api_endpoint,
                "trans_protocol": trans_protocol,
                "time_out": time_out,
                "num_retries": num_retries
            }

        except Exception as e:
            print(f"spec_id={spec_id} 프로토콜 설정 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return None

    def overwrite_spec_config_from_mapping(self,
                                           constants_path: str = None) -> None:
        """
        산출물 파일을 분석하여 CONSTANTS.py의 SPEC_CONFIG 전체 블록을 '덮어쓰기'로 갱신한다.
        각 spec_id별로 API에서 trans_protocol, time_out, num_retries를 추출하여 반영한다.
        """
        try:
            from core.functions import resource_path
            import sys
            import os

            if constants_path is None:
                # ===== 수정: PyInstaller 환경에서 외부 config 우선 사용 =====
                if getattr(sys, 'frozen', False):
                    # PyInstaller로 실행 중 - 외부 경로 사용
                    exe_dir = os.path.dirname(sys.executable)
                    constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
                else:
                    # 일반 실행 - resource_path 사용
                    constants_path = resource_path("config/CONSTANTS.py")
                # ===== 수정 끝 =====

            # 1) CONSTANTS.py 읽기
            with open(constants_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 2) merged_result를 SPEC_CONFIG용 문자열로 재구성
            #    - spec_id는 merged_result의 key
            #    - specs는 해당 파일들에 있는 리스트 변수명을 모두 합쳐 중복 제거 + 정렬
            entries = []

            mode = self.parent.target_system_edit.text().strip()
            print(f"[DEBUG] SPEC_CONFIG 업데이트 - mode: '{mode}'")

            from core.functions import resource_path

            # ===== 수정: PyInstaller 환경에서 외부 spec 디렉토리 우선 사용 =====
            if getattr(sys, 'frozen', False):
                # PyInstaller로 실행 중 - 외부 경로 사용
                exe_dir = os.path.dirname(sys.executable)
                spec_dir = os.path.join(exe_dir, "spec")
            else:
                # 일반 실행 - resource_path 사용
                spec_dir = None  # resource_path로 처리
            # ===== 수정 끝 =====

            if mode == "물리보안시스템":
                priority_order = ["outSchema", "inData", "messages", "webhook"]
                if spec_dir:
                    schema_file = os.path.join(spec_dir, "Schema_response.py")
                    data_file = os.path.join(spec_dir, "Data_request.py")
                else:
                    schema_file = resource_path("spec/Schema_response.py")
                    data_file = resource_path("spec/Data_request.py")
                merged_result = self.merge_list_prefix_mappings(schema_file, data_file)
            elif mode == "통합플랫폼시스템":
                priority_order = ["inSchema", "outData", "messages", "webhook"]
                if spec_dir:
                    schema_file = os.path.join(spec_dir, "Schema_request.py")
                    data_file = os.path.join(spec_dir, "Data_response.py")
                else:
                    schema_file = resource_path("spec/Schema_request.py")
                    data_file = resource_path("spec/Data_response.py")
                merged_result = self.merge_list_prefix_mappings(schema_file, data_file)
            else:
                print(f"[CONFIG SPEC]: 모드 확인해주세요. mode: '{mode}'")
                print("[CONFIG SPEC]: '물리보안시스템' 또는 '통합플랫폼시스템'이어야 합니다.")
                return  # 모드가 올바르지 않으면 조기 종료

            for spec_id in sorted(merged_result.keys()):
                # test_name은 이미 캐시된 이름 사용(없으면 빈 문자열)
                spec_name = self._spec_names_cache.get(spec_id, "")

                # 해당 prefix에 매핑된 모든 리스트 변수 수집 (suffix 무관)
                file_map = merged_result[spec_id]
                all_lists = []

                for _fname, lists in file_map.items():
                    all_lists.extend(lists or [])

                # spec_id로 시작하는 리스트만 취함
                filtered_lists = [name for name in all_lists if name.startswith(spec_id + "_")]

                # 우선순위 기반 정렬 함수 정의
                def sort_by_priority(name: str) -> int:
                    if "webhook" in name.lower():
                        if "schema" in name.lower():
                            return priority_order.index("webhook") * 10 + 0 # webhook schema
                        elif "data" in name.lower():
                            return priority_order.index("webhook") * 10 + 1 # webhook data
                        return priority_order.index("webhook") * 10

                    # 일반 리스트는 마지막 suffix로 판단
                    suffix = name.split("_")[-1]
                    if suffix in priority_order:
                        return priority_order.index(suffix)
                    return len(priority_order)  # 우선순위 밖은 맨 뒤

                # ✅ 중복 제거 후 우선순위 정렬 적용
                specs_list = sorted(set(filtered_lists), key=sort_by_priority)

                # 각 spec_id별로 설정 가져오기 (API에서 추출 또는 기본값)
                spec_config_data = self._extract_spec_config_from_api(spec_id)
                if not spec_config_data:
                    # API에서 가져오지 못하면 기본값 사용
                    spec_config_data = {
                        "api_name": [],
                        "api_id": [],
                        "api_endpoint": [],
                        "trans_protocol": [],
                        "time_out": [],
                        "num_retries": []
                    }

                # 항목 문자열 조립 (순서: test_name, specs, trans_protocol, time_out, num_retries)
                entry = (
                    f'"{spec_id}": {{\n'
                    f'    "test_name": "{spec_name}",\n'
                    f'    "specs": {specs_list},\n' 
                    f'    "api_name": {spec_config_data.get("api_name", [])},\n'
                    f'    "api_id": {spec_config_data.get("api_id", [])},\n'
                    f'    "api_endpoint": {spec_config_data.get("api_endpoint", [])},\n'
                    f'    "trans_protocol": {spec_config_data.get("trans_protocol", [])},\n'
                    f'    "time_out": {spec_config_data.get("time_out", [])},\n'
                    f'    "num_retries": {spec_config_data.get("num_retries", [])}\n'
                    f'}}'
                )
                entries.append(entry)

            # 그룹 정보 추가 (리스트 형태로 여러 그룹 지원)
            # parent에 저장된 모든 그룹 정보 사용
            test_groups = getattr(self.parent, 'test_groups', [])
            # print(f"[DEBUG] overwrite_spec_config_from_mapping - test_groups: {test_groups}")
            # print(f"[DEBUG] test_groups 개수: {len(test_groups)}")

            if not test_groups:
                # 그룹 정보가 없으면 기존 방식 사용
                group_id = getattr(self.parent, 'test_group_id', "")
                group_name = getattr(self.parent, 'test_group_name', "")

                group_fields = []
                if group_name:
                    group_fields.append(f'"group_name": "{group_name}"')
                if group_id:
                    group_fields.append(f'"group_id": "{group_id}"')

                all_group_entries = group_fields + entries
                group_content = ",\n        ".join(all_group_entries)
                new_spec_config_block = f"SPEC_CONFIG = [\n    {{\n        {group_content}\n    }}\n]"
            else:
                # 여러 그룹을 그룹별로 분리하여 저장
                # entries를 spec_id별로 딕셔너리로 변환 (나중에 그룹별로 필터링하기 위함)
                entries_dict = {}
                for entry in entries:
                    # entry는 '"spec_id": {...}' 형태의 문자열
                    # spec_id 추출
                    spec_id = entry.split('"')[1]  # 첫 번째 따옴표 안의 내용
                    entries_dict[spec_id] = entry

                # 각 그룹별로 딕셔너리 생성
                group_blocks = []
                for group in test_groups:
                    group_name = group.get("name", "")
                    group_id = group.get("id", "")
                    group_specs = group.get("testSpecs", [])

                    # 이 그룹에 속한 spec_id만 필터링
                    group_spec_ids = [spec.get("id") for spec in group_specs]
                    group_entries = [entries_dict[sid] for sid in group_spec_ids if sid in entries_dict]

                    # 그룹 필드 생성
                    group_fields = []
                    if group_name:
                        group_fields.append(f'"group_name": "{group_name}"')
                    if group_id:
                        group_fields.append(f'"group_id": "{group_id}"')

                    # 그룹 내부 전체 내용
                    all_group_entries = group_fields + group_entries
                    group_content = ",\n        ".join(all_group_entries)

                    # 각 그룹을 딕셔너리 형태로 추가
                    group_block = f"    {{\n        {group_content}\n    }}"
                    group_blocks.append(group_block)

                # 모든 그룹 블록을 콤마로 연결
                all_groups_content = ",\n".join(group_blocks)
                new_spec_config_block = f"SPEC_CONFIG = [\n{all_groups_content}\n]"

            # 3) 모든 SPEC_CONFIG 블록 찾아서 첫 번째 것만 남기고 모두 삭제, 첫 번째 것은 새 내용으로 교체
            import re
            # SPEC_CONFIG = [ 로 시작해서 대괄호와 중괄호가 모두 닫힐 때까지의 블록 패턴
            pattern = r'SPEC_CONFIG = \[[\s\S]*?\n\]'

            # 모든 SPEC_CONFIG 블록 찾기
            matches = list(re.finditer(pattern, content))

            if not matches:
                # SPEC_CONFIG가 하나도 없으면 "#etc" 주석 위에 새로 생성
                etc_comment = "\n#etc"
                etc_pos = content.find(etc_comment)
                if etc_pos != -1:
                    new_content = content[:etc_pos + 1] + new_spec_config_block + "\n\n" + content[etc_pos + 1:]
                else:
                    # #etc도 없으면 파일 끝에 추가
                    new_content = content + "\n\n" + new_spec_config_block + "\n"
            else:
                # 첫 번째 SPEC_CONFIG를 새로운 내용으로 교체하고, 나머지는 모두 삭제
                # 뒤에서부터 삭제해야 인덱스가 안 꼬임
                temp_content = content
                for match in reversed(matches[1:]):
                    temp_content = temp_content[:match.start()] + temp_content[match.end():]

                # 첫 번째 SPEC_CONFIG를 새로운 내용으로 교체
                first_match_in_temp = re.search(pattern, temp_content)
                if first_match_in_temp:
                    new_content = (temp_content[:first_match_in_temp.start()] +
                                 new_spec_config_block +
                                 temp_content[first_match_in_temp.end():])
                else:
                    new_content = temp_content

            with open(constants_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            # 실제로 업데이트되었는지 검증
            import os
            if os.path.exists(constants_path):
                file_size = os.path.getsize(constants_path)
                print(f"[DEBUG] CONSTANTS.py 업데이트 완료:")
                # print(f"  경로: {constants_path}")
                # print(f"  파일 크기: {file_size} bytes")
                # print(f"  파일 존재: True")
            else:
                print(f"[WARNING] 파일이 존재하지 않습니다: {constants_path}")

            print("CONSTANTS.py SPEC_CONFIG 전체 덮어쓰기 완료")

            # ✅ 메모리의 CONSTANTS.SPEC_CONFIG도 업데이트
            try:
                namespace = {}
                exec(new_spec_config_block, namespace)
                if 'SPEC_CONFIG' in namespace:
                    CONSTANTS.SPEC_CONFIG = namespace['SPEC_CONFIG']
                    print(f"[MEMORY] CONSTANTS.SPEC_CONFIG 메모리 업데이트 완료: {len(CONSTANTS.SPEC_CONFIG)}개 그룹")
            except Exception as mem_err:
                print(f"[WARNING] SPEC_CONFIG 메모리 업데이트 실패: {mem_err}")

        except Exception as e:
            print(f"SPEC_CONFIG 덮어쓰기 실패: {e}")
            import traceback
            traceback.print_exc()

    def _update_spec_config(self, spec_id, config_data):
        """CONSTANTS.py의 SPEC_CONFIG 리스트에 spec_id별 설정 업데이트"""
        try:
            from core.functions import resource_path
            import sys
            import os

            # ===== 수정: PyInstaller 환경에서 외부 config 우선 사용 =====
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
            else:
                constants_path = resource_path("config/CONSTANTS.py")
            # ===== 수정 끝 =====

            with open(constants_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # SPEC_CONFIG 리스트 찾기 (새로운 형태: SPEC_CONFIG = [{...}])
            spec_config_start = content.find('SPEC_CONFIG = [')
            if spec_config_start == -1:
                print("경고: SPEC_CONFIG 리스트를 찾을 수 없습니다.")
                return

            # 대괄호와 중괄호 개수를 세면서 끝 위치 찾기
            bracket_count = 0
            brace_count = 0
            start_pos = content.find('[', spec_config_start)
            current_pos = start_pos

            while current_pos < len(content):
                if content[current_pos] == '[':
                    bracket_count += 1
                elif content[current_pos] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        # SPEC_CONFIG의 끝 ] 발견
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
            # ⚠️ 주의: 이 함수는 개별 spec 업데이트용으로, 기본 리스트만 포함
            # webhook 리스트는 overwrite_spec_config_from_mapping()에서 자동 감지하여 추가됨
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

            # 파일 쓰기
            with open(constants_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"CONSTANTS.py SPEC_CONFIG 업데이트 완료")

        except Exception as e:
            print(f"SPEC_CONFIG 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()

    def merge_list_prefix_mappings(self, file_a: str, file_b: str) -> Dict[str, Dict[str, List[str]]]:
        # 파일별 리스트 추출
        lists_a = self.extract_lists(file_a)
        lists_b = self.extract_lists(file_b)

        # 모든 prefix의 합집합 생성
        all_prefixes = sorted(set(lists_a.keys()) | set(lists_b.keys()))

        merged: Dict[str, Dict[str, List[str]]] = {}
        for prefix in all_prefixes:
            merged[prefix] = {
                Path(file_a).name: lists_a.get(prefix, []),
                Path(file_b).name: lists_b.get(prefix, [])
            }

        return merged

    def extract_lists(self, file_path: str) -> Dict[str, List[str]]:
        """내부용: 파일에서 리스트 변수명 추출 → prefix 기준 그룹화"""
        src = Path(file_path).read_text(encoding="utf-8")
        tree = ast.parse(src, filename=file_path)

        prefix_map: Dict[str, List[str]] = {}
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.List):
                targets = []
                if isinstance(node, ast.Assign):
                    targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    targets = [node.target.id]
                for var_name in targets:
                    prefix = var_name.split("_")[0] if "_" in var_name else var_name
                    prefix_map.setdefault(prefix, []).append(var_name)
        return prefix_map

    def _get_selected_test_field_spec_id(self):
        """시험 시나리오 테이블에서 마지막으로 클릭된 항목의 spec_id 반환"""
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

        # ✅ URL이 업데이트되면 WEBHOOK_PUBLIC_IP도 함께 업데이트
        if 'url' in variables:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(variables['url'])
                webhook_ip = parsed_url.hostname
                if webhook_ip:
                    # WEBHOOK_PUBLIC_IP 업데이트
                    pattern_ip = r'^WEBHOOK_PUBLIC_IP\s*=.*$'
                    new_ip_line = f'WEBHOOK_PUBLIC_IP = "{webhook_ip}"'
                    content = re.sub(pattern_ip, new_ip_line, content, flags=re.MULTILINE)
                    
                    # WEBHOOK_URL 업데이트
                    pattern_url = r'^WEBHOOK_URL\s*=.*$'
                    new_url_line = f'WEBHOOK_URL = f"https://{{WEBHOOK_PUBLIC_IP}}:{{WEBHOOK_PORT}}"'
                    content = re.sub(pattern_url, new_url_line, content, flags=re.MULTILINE)
                    
                    print(f"[WEBHOOK] 시험 URL에서 IP 추출: {webhook_ip}")
                    print(f"[WEBHOOK] 웹훅 콜백 URL 업데이트: https://{webhook_ip}:2001")
            except Exception as e:
                print(f"[WEBHOOK] URL 파싱 실패: {e}")

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

        # 실제로 업데이트되었는지 검증
        import os
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"[DEBUG] CONSTANTS.py 변수 업데이트 완료:")
            # print(f"  경로: {file_path}")
            # print(f"  파일 크기: {file_size} bytes")
            # print(f"  업데이트된 변수: {list(variables.keys())}")
        else:
            print(f"[WARNING] 파일이 존재하지 않습니다: {file_path}")

        # ✅ 메모리의 CONSTANTS 모듈도 업데이트 (중요!)
        for var_name, var_value in variables.items():
            if hasattr(CONSTANTS, var_name):
                setattr(CONSTANTS, var_name, var_value)
                print(f"[MEMORY] CONSTANTS.{var_name} 메모리 업데이트 완료")


    def load_opt_files_from_api(self, test_data):
        """API 데이터를 이용하여 OPT 파일 로드 및 스키마 생성 (모든 그룹 처리)"""
        try:
            # testGroups 배열에서 모든 그룹의 testSpecs 추출
            test_groups = test_data.get("testRequest", {}).get("testGroups", [])
            if not test_groups:
                QMessageBox.warning(self.parent, "데이터 없음", "testGroups 데이터가 비어있습니다.")
                return

            # 모든 그룹의 testSpecs를 합치면서 그룹 이름도 함께 저장
            all_test_specs_with_group = []
            for group in test_groups:
                group_name = group.get("name", "")
                for spec in group.get("testSpecs", []):
                    # 각 spec에 group_name 추가
                    spec_with_group = spec.copy()
                    spec_with_group["group_name"] = group_name
                    all_test_specs_with_group.append(spec_with_group)

            if not all_test_specs_with_group:
                QMessageBox.warning(self.parent, "데이터 없음", "testSpecs 데이터가 비어있습니다.")
                return

            print(f"\n=== API 기반 OPT 로드 시작 ===")
            print(f"그룹 개수: {len(test_groups)}개")
            print(f"전체 시나리오 개수: {len(all_test_specs_with_group)}개")

            # 시험 시나리오 테이블 채우기 (그룹 정보 포함)
            self._fill_test_field_table_from_api(all_test_specs_with_group)
            self.preload_all_spec_steps()
            self.preload_test_step_details_from_cache()

            # 산출물 파일 생성 먼저 (SPEC_CONFIG 업데이트보다 먼저 실행)
            self._generate_files_for_all_specs()

            # 모든 spec에 대해 개별 설정 업데이트 (trans_protocol, time_out, num_retries)
            print(f"\n=== SPEC_CONFIG 업데이트 시작 ===")
            for spec in all_test_specs_with_group:  # all_test_specs_with_group 사용
                spec_id = spec.get("id", "")
                if spec_id:
                    spec_config_data = self._extract_spec_config_from_api(spec_id)
                    if spec_config_data:
                        self._update_spec_config(spec_id, spec_config_data)  # 개별 spec 업데이트
            print(f"=== SPEC_CONFIG 개별 업데이트 완료 ===\n")

            # 산출물 파일 기반으로 SPEC_CONFIG 전체 재구성 (specs 필드 포함)
            print(f"=== SPEC_CONFIG 전체 재구성 시작 ===")
            self.overwrite_spec_config_from_mapping()  # 한 번만 호출, 모든 spec 처리
            print(f"=== SPEC_CONFIG 전체 재구성 완료 ===\n")
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
        """API testSpecs 배열로부터 시험 분야 목록 채우기 (첫 번째 컬럼만)"""
        try:
            from PyQt5.QtGui import QFont, QBrush, QColor

            table = self.parent.test_field_table
            table.setRowCount(0)

            # 그룹별로 spec들을 저장 {group_name: [spec1, spec2, ...]}
            self._group_specs = {}

            for spec in test_specs:
                spec_id = spec.get("id", "")
                spec_name = spec.get("name", "")
                group_name = spec.get("group_name", "")

                # spec_name을 캐시에 저장
                self._spec_names_cache[spec_id] = spec_name

                # 그룹별로 spec 저장
                if group_name not in self._group_specs:
                    self._group_specs[group_name] = []
                self._group_specs[group_name].append({
                    "id": spec_id,
                    "name": spec_name
                })

            # 폰트 설정 (Noto Sans KR, Regular 400, 19px)
            font = QFont("Noto Sans KR")
            font.setPixelSize(19)
            font.setWeight(400)
            font.setLetterSpacing(QFont.PercentageSpacing, 100.7)

            # 그룹별로 한 행씩 추가 (첫 번째 컬럼에만 시험 분야명)
            for i, group_name in enumerate(self._group_specs.keys()):
                table.insertRow(i)

                # 첫 번째 컬럼: 시험 분야명 (배경 이미지 적용, 클릭 가능)
                label = ClickableLabel(group_name, i, 0)
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("""
                    QLabel {
                        background-image: url('assets/image/test_config/row.png');
                        background-position: center;
                        background-repeat: no-repeat;
                        font-family: 'Noto Sans KR';
                        font-size: 19px;
                        font-weight: 400;
                        color: #000000;
                        min-width: 371.5px;
                        min-height: 39px;
                    }
                """)
                label.clicked.connect(self.parent.on_test_field_selected)
                table.setCellWidget(i, 0, label)

            # 초기 상태: 아무것도 선택하지 않음
            table.clearSelection()
            table.setCurrentCell(-1, -1)
            self.parent.selected_test_field_row = None

            # 시나리오 테이블 초기화
            if hasattr(self.parent, 'scenario_table'):
                self.parent.scenario_table.setRowCount(0)
                self.parent.scenario_table.clearContents()

            # placeholder label 표시 (시나리오 테이블 위에 오버레이)
            if hasattr(self.parent, 'scenario_placeholder_label'):
                self.parent.scenario_placeholder_label.show()
                self.parent.scenario_placeholder_label.raise_()

            print(f"시험 분야 테이블 채우기 완료: {len(self._group_specs)}개 그룹")

        except Exception as e:
            print(f"시험 분야 테이블 채우기 실패: {e}")
            import traceback
            traceback.print_exc()


    def fetch_test_info_by_ip(self, ip_address):
        """IP 주소로 시험 정보 조회"""
        url = f"{CONSTANTS.management_url}/api/integration/test-requests/by-ip?ipAddress={ip_address}"
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
        url = f"{CONSTANTS.management_url}/api/integration/specifications/{spec_id}"
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
        """_group_specs에 있는 모든 spec_id의 steps(id, name)만 미리 캐싱"""

        loaded, skipped = 0, 0
        total_specs = 0

        # _group_specs 딕셔너리에서 모든 spec 가져오기
        if not hasattr(self, '_group_specs') or not self._group_specs:
            print(f"[preload_all_spec_steps] 경고: _group_specs가 비어있습니다.")
            return

        for group_name, specs in self._group_specs.items():
            for spec in specs:
                total_specs += 1
                spec_id = spec.get("id")
                if not spec_id:
                    continue

                if spec_id in self._steps_cache:
                    skipped += 1
                    continue

                spec_data = self.fetch_specification_by_id(spec_id)
                if not spec_data:
                    continue

                steps = spec_data.get("specification", {}).get("steps", [])
                # hasApi만 필터링하고, webhook callback step 제외 (id에 '-'가 2번 이상 있는 경우)
                trimmed = [
                    {"id": s.get("id"), "name": s.get("name", "")}
                    for s in steps
                    if s.get("hasApi") and s.get("id", "").count("-") <= 1  # webhook callback step 제외
                ]

                print(f"[DEBUG] preload_all_spec_steps - spec_id: {spec_id}")
                print(f"  전체 steps: {len(steps)}개")
                print(f"  hasApi=True인 steps (callback 제외): {len(trimmed)}개")
                print(f"  step IDs: {[t.get('id') for t in trimmed]}")

                self._steps_cache[spec_id] = trimmed
                loaded += 1

        print(f"[preload_all_spec_steps] 로드:{loaded}, 스킵:{skipped}, 총 spec 수:{total_specs}")


    def _show_initial_scenario_message(self):
        """시험 시나리오 컬럼에 초기 메시지 표시"""
        try:
            from PyQt5.QtGui import QFont, QBrush, QColor

            table = self.parent.test_field_table
            row_count = table.rowCount()

            if row_count > 0:
                # 첫 번째 행의 두 번째 컬럼에 메시지 표시
                message_item = QTableWidgetItem("시험 분야를 선택하면\n시나리오가 표시됩니다.")
                font = QFont("Noto Sans KR")
                font.setPixelSize(16)
                message_item.setFont(font)
                message_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                message_item.setFlags(Qt.ItemIsEnabled)  # 선택 불가
                message_item.setBackground(QBrush(QColor("#FFFFFF")))  # 흰색 배경

                table.setItem(0, 1, message_item)
                # 모든 행의 두 번째 컬럼 병합
                table.setSpan(0, 1, row_count, 1)

        except Exception as e:
            print(f"초기 시나리오 메시지 표시 실패: {e}")

    def _show_scenario_placeholder(self):
        """시험 시나리오 안내 문구 표시 (테이블 위에 오버레이)"""
        try:
            scenario_table = self.parent.scenario_table

            # 시나리오 테이블 비우기
            scenario_table.setRowCount(0)
            scenario_table.clearContents()

            # 시험 시나리오 배경 숨김
            if hasattr(self.parent, 'scenario_column_background'):
                self.parent.scenario_column_background.hide()

            # placeholder label 표시
            if hasattr(self.parent, 'scenario_placeholder_label'):
                self.parent.scenario_placeholder_label.show()
                self.parent.scenario_placeholder_label.raise_()

            print("시험 시나리오 안내 문구 표시")
        except Exception as e:
            print(f"시험 시나리오 안내 문구 표시 실패: {e}")

    def _show_initial_api_message(self):
        """시험 API 테이블에 초기 메시지 표시"""
        try:
            table = self.parent.api_test_table
            table.setRowCount(0)  # 모든 행 제거

            # placeholder label 표시
            if hasattr(self.parent, 'api_placeholder_label'):
                self.parent.api_placeholder_label.show()

        except Exception as e:
            print(f"초기 API 메시지 표시 실패: {e}")

    def _fill_scenarios_for_group(self, clicked_row, group_name):
        """선택된 시험 분야의 시나리오를 시나리오 테이블에 표시"""
        try:
            from PyQt5.QtGui import QFont, QBrush, QColor

            field_table = self.parent.test_field_table
            scenario_table = self.parent.scenario_table

            # 시그널 차단 시작
            field_table.blockSignals(True)
            scenario_table.blockSignals(True)

            # 안내 문구 QLabel 숨김
            if hasattr(self.parent, 'scenario_placeholder_label'):
                self.parent.scenario_placeholder_label.hide()

            # 시험 시나리오 배경 표시 (#E3F2FF)
            if hasattr(self.parent, 'scenario_column_background'):
                self.parent.scenario_column_background.show()
                print(f"배경 위젯 표시: visible={self.parent.scenario_column_background.isVisible()}")

            # 선택된 그룹의 시나리오 가져오기
            scenarios = self._group_specs.get(group_name, [])
            scenario_count = len(scenarios)
            group_count = len(self._group_specs)

            print(f"\n=== 테이블 재구성 시작 ===")
            print(f"선택된 그룹: {group_name} (시나리오 {scenario_count}개)")
            print(f"전체 시험분야 개수: {group_count}")

            # === 시험 분야 테이블 재구성 ===
            field_table.setRowCount(0)
            field_table.clearContents()
            field_table.setRowCount(group_count)

            print(f"\n시험 분야 테이블:")
            for i, gname in enumerate(self._group_specs.keys()):
                # 선택된 시험분야는 row_selected.png, 나머지는 row.png
                if gname == group_name:
                    label = ClickableLabel(gname, i, 0)
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("""
                        QLabel {
                            background-image: url('assets/image/test_config/row_selected.png');
                            background-position: center;
                            background-repeat: no-repeat;
                            font-family: 'Noto Sans KR';
                            font-size: 19px;
                            font-weight: 400;
                            color: #000000;
                            min-width: 371.5px;
                            min-height: 39px;
                        }
                    """)
                    print(f"  행 {i}: [시험분야: {gname}] (선택됨) - 배경: row_selected.png")
                else:
                    label = ClickableLabel(gname, i, 0)
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("""
                        QLabel {
                            background-image: url('assets/image/test_config/row.png');
                            background-position: center;
                            background-repeat: no-repeat;
                            font-family: 'Noto Sans KR';
                            font-size: 19px;
                            font-weight: 400;
                            color: #000000;
                            min-width: 371.5px;
                            min-height: 39px;
                        }
                    """)
                    print(f"  행 {i}: [시험분야: {gname}] - 배경: row.png")

                label.clicked.connect(self.parent.on_test_field_selected)
                field_table.setCellWidget(i, 0, label)
                field_table.setRowHeight(i, 39)

            # === 시나리오 테이블 재구성 ===
            scenario_table.setRowCount(0)
            scenario_table.clearContents()
            scenario_table.setRowCount(scenario_count)

            print(f"\n시나리오 테이블:")
            for i, scenario in enumerate(scenarios):
                # 시나리오명을 표시하는 ClickableLabel 생성
                label = ClickableLabel(scenario["name"], i, 0)  # 시나리오 테이블의 첫 번째(유일한) 컬럼
                label.setAlignment(Qt.AlignCenter)
                # 초기 상태: 모든 시나리오는 체크 안 된 상태로 표시
                label.setStyleSheet("""
                    QLabel {
                        background-image: url('assets/image/test_config/row_checkbox_unchecked.png');
                        background-position: center;
                        background-repeat: no-repeat;
                        border: none;
                        border-bottom: 1px solid #CCCCCC;
                        font-family: 'Noto Sans KR';
                        font-size: 19px;
                        font-weight: 400;
                        color: #000000;
                        margin: 0px;
                        padding: 0px;
                        min-width: 371.5px;
                        min-height: 39px;
                    }
                """)
                # spec_id를 label의 property로 저장
                label.setProperty("spec_id", scenario["id"])
                label.clicked.connect(self.parent.on_scenario_selected)
                scenario_table.setCellWidget(i, 0, label)
                scenario_table.setRowHeight(i, 39)
                print(f"  행 {i}: [시나리오: {scenario['name']}] - 배경: row_checkbox_unchecked.png")

            print(f"\n=== 테이블 재구성 완료 ===")
            print(f"시험 분야 테이블 행 수: {field_table.rowCount()}")
            print(f"시나리오 테이블 행 수: {scenario_table.rowCount()}\n")

            # 선택 상태 제거
            field_table.clearSelection()
            field_table.setCurrentCell(-1, -1)
            scenario_table.clearSelection()
            scenario_table.setCurrentCell(-1, -1)

            # 시그널 차단 해제
            field_table.blockSignals(False)
            scenario_table.blockSignals(False)

            print(f"시나리오 채우기 완료: {group_name} - {scenario_count}개 시나리오 표시")

        except Exception as e:
            print(f"시나리오 채우기 실패: {e}")
            import traceback
            traceback.print_exc()
            # 에러 발생 시에도 시그널 차단 해제
            if 'field_table' in locals():
                field_table.blockSignals(False)
            if 'scenario_table' in locals():
                scenario_table.blockSignals(False)

    def _fill_api_table_for_selected_field_from_api(self, row):
        """선택된 시험 시나리오의 API 테이블 채우기 (API 기반)"""
        try:
            # spec_id 추출 (시나리오 테이블의 위젯에서 가져오기)
            widget = self.parent.scenario_table.cellWidget(row, 0)
            if not widget:
                return

            spec_id = widget.property("spec_id")
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

            # placeholder label 숨기기
            if hasattr(self.parent, 'api_placeholder_label'):
                self.parent.api_placeholder_label.hide()

            # steps 순회하여 테이블 채우기
            for step in cached_steps:
                step_id = step.get("id")

                # [변경] _test_step_cache에 저장된 id/name 우선 사용
                ts = self._test_step_cache.get(step_id) if hasattr(self, "_test_step_cache") else None
                name_to_show = ""
                id_to_show = ""

                if ts:
                    # { "id": ..., "name": ..., "endpoint": ..., "detail": {...} } 구조
                    name_to_show = ts.get("name", "")
                    endpoint = ts.get("endpoint")
                    id_to_show = "" if endpoint is None else str(endpoint)
                else:
                    # 백업: 캐시에 없으면 API 호출해서 endpoint 가져오기
                    step_detail = self.fetch_test_step_by_id(step_id)
                    if step_detail:
                        endpoint = step_detail.get("step", {}).get("api", {}).get("endpoint", "")
                        name_to_show = step_detail.get("step", {}).get("name", step.get("name", ""))
                        id_to_show = str(endpoint) if endpoint else ""
                    else:
                        # API 호출 실패 시 step의 name만 사용
                        name_to_show = step.get("name", "")
                        id_to_show = ""

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
        url = f"{CONSTANTS.management_url}/api/integration/test-steps/{step_id}"
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

    def get_authentication_credentials(self, spec_id):
        """
        플랫폼 검증 시 spec_id로부터 Authentication 인증 정보를 추출

        Args:
            spec_id: 스펙 ID (예: 'cmgvieyak001b6cd04cgaawmm')

        Returns:
            tuple: (user_id, password) 또는 (None, None) if not found

        Example:
            >>> user_id, password = self.get_authentication_credentials('cmgvieyak001b6cd04cgaawmm')
            >>> # Returns: ('kisa', 'kisa_k1!2@')
        """
        try:
            from core.validation_registry import get_validation_rules

            # Authentication API의 검증 규칙 가져오기 (direction='in'은 플랫폼→시스템 요청)
            rules = get_validation_rules(spec_id, 'Authentication', 'in')

            if not rules:
                print(f"[WARNING] spec_id={spec_id}에 대한 Authentication 검증 규칙을 찾을 수 없습니다.")
                return None, None

            # userID 추출
            user_id = None
            if 'userID' in rules:
                user_id_rule = rules['userID']
                allowed_values = user_id_rule.get('allowedValues', [])
                if allowed_values and len(allowed_values) > 0:
                    user_id = allowed_values[0]

            # userPW 추출
            password = None
            if 'userPW' in rules:
                user_pw_rule = rules['userPW']
                allowed_values = user_pw_rule.get('allowedValues', [])
                if allowed_values and len(allowed_values) > 0:
                    password = allowed_values[0]

            if user_id and password:
                print(f"[INFO] Authentication 인증 정보 추출 완료: user_id={user_id}")
                return user_id, password
            else:
                print(f"[WARNING] Authentication 규칙에서 userID 또는 userPW를 찾을 수 없습니다.")
                return None, None

        except Exception as e:
            print(f"[ERROR] Authentication 인증 정보 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return None, None