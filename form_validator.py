"""
폼 검증 및 데이터 처리를 담당하는 모듈
- OPT 파일 로드 및 처리
- CONSTANTS.py 업데이트
- 관리자 코드 검증
- 폼 유효성 검사
"""

import re
import os
import sys
import json
from pathlib import Path
from typing import Dict, List

from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QResizeEvent

# 분리된 모듈들 import
from ui.widgets import ClickableLabel, ClickableRowWidget, ClickableCheckboxRowWidget
from api.client import APIClient
from core.auth_service import AuthService
from core.file_generator import FileGeneratorService
from core.opt_loader import OptLoader
from core.functions import resource_path

import config.CONSTANTS as CONSTANTS


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
        self._group_specs = {}  # group_name -> [spec1, spec2, ...]

        # 분리된 서비스 초기화
        self.api_client = APIClient()
        self.auth_service = AuthService()
        self.file_generator = FileGeneratorService()

    # ---------- 관리자 코드 검증 ----------

    def validate_admin_code(self):
        """관리자 코드 숫자 입력 검증"""
        text = self.parent.admin_code_edit.text()
        filtered_text = ''.join(filter(str.isdigit, text))

        if text != filtered_text:
            cursor_pos = self.parent.admin_code_edit.cursorPosition()
            self.parent.admin_code_edit.setText(filtered_text)
            new_pos = cursor_pos - (len(text) - len(filtered_text))
            self.parent.admin_code_edit.setCursorPosition(max(0, new_pos))

    def is_admin_code_required(self):
        """관리자 코드 입력이 필요한지 확인"""
        test_category = self.parent.test_category_edit.text().strip()
        return test_category == "MAIN_TEST" or test_category == "본시험"

    def is_admin_code_valid(self):
        """관리자 코드 유효성 검사"""
        if not self.is_admin_code_required():
            return True
        admin_code = self.parent.admin_code_edit.text().strip()
        return bool(admin_code and admin_code.isdigit())

    def handle_test_category_change(self):
        """시험유형 변경 시 관리자 코드 필드 활성화/비활성화"""
        test_category = self.parent.test_category_edit.text().strip()

        if not test_category:
            self.parent.admin_code_edit.setEnabled(False)
            self.parent.admin_code_edit.clear()
            self.parent.admin_code_edit.setPlaceholderText("")
            return

        if test_category in ["본시험", "사전시험"]:
            if test_category == "본시험":
                self.parent.admin_code_edit.setEnabled(True)
                self.parent.admin_code_edit.setPlaceholderText("")
            else:
                self.parent.admin_code_edit.setEnabled(False)
                self.parent.admin_code_edit.clear()
                self.parent.admin_code_edit.setPlaceholderText("")
            return

        self.parent.original_test_category = test_category

        if test_category == "MAIN_TEST":
            self.parent.test_category_edit.setText("본시험")
            self.parent.admin_code_edit.setEnabled(True)
            self.parent.admin_code_edit.setPlaceholderText("")
        else:
            self.parent.test_category_edit.setText("사전시험")
            self.parent.admin_code_edit.setEnabled(False)
            self.parent.admin_code_edit.clear()
            self.parent.admin_code_edit.setPlaceholderText("")

    def handle_test_range_change(self):
        """시험범위 변경 시 UI 표시 텍스트 변환"""
        test_range = self.parent.test_range_edit.text().strip()

        if not test_range:
            return

        if test_range in ["전체필드", "필수필드"]:
            return

        self.parent.original_test_range = test_range

        if test_range == "ALL_FIELDS":
            self.parent.test_range_edit.setText("전체필드")
        else:
            self.parent.test_range_edit.setText("필수필드")

    # ---------- CONSTANTS.py 업데이트 ----------

    def update_constants_py(self):
        """CONSTANTS.py 파일의 변수들을 GUI 입력값으로 업데이트"""
        try:
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
            else:
                constants_path = resource_path("config/CONSTANTS.py")

            # 1. 시험 기본 정보 수집
            variables = self._collect_basic_info()

            # 2. 접속 정보
            variables['url'] = self.parent.get_selected_url()

            # 3. 인증 정보
            auth_type, auth_info = self._collect_auth_info()
            variables['auth_type'] = auth_type
            variables['auth_info'] = auth_info

            # 4. 관리자 코드
            variables['admin_code'] = self.parent.admin_code_edit.text().strip()
            variables['contact_person'] = getattr(self.parent, 'contact_person', "")
            variables['model_name'] = getattr(self.parent, 'model_name', "")
            variables['request_id'] = getattr(self.parent, 'request_id', "")

            # 5. SPEC_CONFIG 전체 덮어쓰기
            self.overwrite_spec_config_from_mapping()

            # 6. 선택된 시험 분야의 인덱스 저장
            selected_spec_index = self._get_selected_spec_index()
            variables['selected_spec_index'] = selected_spec_index
            print(f"\n[CRITICAL] CONSTANTS.py에 저장할 selected_spec_index: {selected_spec_index}")

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

        if test_category == "본시험":
            test_category = "MAIN_TEST"
        elif test_category == "사전시험":
            test_category = self.parent.original_test_category if self.parent.original_test_category else "사전시험"

        if test_range == "전체필드":
            test_range = "ALL_FIELDS"
        elif test_range == "필수필드":
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
        return auth_type, auth_info

    def _get_selected_test_field_spec_id(self):
        """시험 시나리오 테이블에서 마지막으로 클릭된 항목의 spec_id 반환"""
        try:
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

            spec_id_str = str(selected_spec_id).lower()

            if "spec-0011" in spec_id_str or "spec_0011" in spec_id_str:
                print("보안용 센서 시스템 선택됨 (index 1)")
                return 1
            elif "spec-001" in spec_id_str or "spec_001" in spec_id_str:
                print("영상보안 시스템 선택됨 (index 0)")
                return 0
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

        # URL이 업데이트되면 WEBHOOK_PUBLIC_IP도 함께 업데이트
        if 'url' in variables:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(variables['url'])
                webhook_ip = parsed_url.hostname
                if webhook_ip:
                    pattern_ip = r'^WEBHOOK_PUBLIC_IP\s*=.*$'
                    new_ip_line = f'WEBHOOK_PUBLIC_IP = "{webhook_ip}"'
                    content = re.sub(pattern_ip, new_ip_line, content, flags=re.MULTILINE)

                    pattern_url = r'^WEBHOOK_URL\s*=.*$'
                    new_url_line = f'WEBHOOK_URL = f"https://{{WEBHOOK_PUBLIC_IP}}:{{WEBHOOK_PORT}}"'
                    content = re.sub(pattern_url, new_url_line, content, flags=re.MULTILINE)

                    print(f"[WEBHOOK] 시험 URL에서 IP 추출: {webhook_ip}")
            except Exception as e:
                print(f"[WEBHOOK] URL 파싱 실패: {e}")

        for var_name, var_value in variables.items():
            if isinstance(var_value, str):
                new_line = f'{var_name} = "{var_value}"'
            elif isinstance(var_value, list):
                new_line = f'{var_name} = {var_value}'
            elif var_value is None:
                new_line = f'{var_name} = None'
            else:
                new_line = f'{var_name} = {var_value}'

            pattern = rf'^{var_name}\s*=.*$'
            content = re.sub(pattern, new_line, content, flags=re.MULTILINE)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 메모리의 CONSTANTS 모듈도 업데이트
        for var_name, var_value in variables.items():
            if hasattr(CONSTANTS, var_name):
                setattr(CONSTANTS, var_name, var_value)
                print(f"[MEMORY] CONSTANTS.{var_name} 메모리 업데이트 완료")

    # ---------- SPEC_CONFIG 관련 ----------

    def _extract_spec_config_from_api(self, spec_id):
        """test-steps API 캐시에서 spec_id별 프로토콜 설정 추출"""
        try:
            steps = self._steps_cache.get(spec_id, [])
            if not steps:
                print(f"경고: spec_id={spec_id}에 대한 steps 캐시가 없습니다.")
                return None

            time_out = []
            num_retries = []
            trans_protocol = []
            api_name = []
            api_id = []
            api_endpoint = []
            endpoint_count = {}

            for step in steps:
                step_id = step.get("id")
                if not step_id:
                    continue

                cached_step = self._test_step_cache.get(step_id)
                if not cached_step:
                    print(f"경고: step_id={step_id}에 대한 캐시가 없습니다.")
                    time_out.append(5000)
                    num_retries.append(1)
                    trans_protocol.append(None)
                    continue

                detail = cached_step.get("detail", {})
                settings = detail.get("step", {}).get("api", {}).get("settings", {})

                api_name.append(detail.get("step", {}).get("api", {}).get("name", {}))
                api_id.append(step_id)

                raw_endpoint = detail.get("step", {}).get("api", {}).get("endpoint", "")
                if raw_endpoint:
                    base_endpoint = raw_endpoint[1:] if raw_endpoint.startswith("/") else raw_endpoint
                    if base_endpoint in endpoint_count:
                        endpoint_count[base_endpoint] += 1
                        numbered_endpoint = f"/{base_endpoint}{endpoint_count[base_endpoint]}"
                    else:
                        endpoint_count[base_endpoint] = 1
                        numbered_endpoint = raw_endpoint
                    api_endpoint.append(numbered_endpoint)
                else:
                    api_endpoint.append(raw_endpoint)

                time_out.append(settings.get("timeout", 60000))

                load_test = settings.get("loadTest", {})
                if load_test.get("enabled", False):
                    num_retries.append(load_test.get("concurrentUsers", 1))
                else:
                    num_retries.append(1)

                trans_protocol_obj = settings.get("transProtocol")
                if isinstance(trans_protocol_obj, str):
                    trans_protocol_mode = trans_protocol_obj if trans_protocol_obj else None
                elif isinstance(trans_protocol_obj, dict):
                    trans_protocol_mode = trans_protocol_obj.get("mode", None)
                else:
                    trans_protocol_mode = None
                trans_protocol.append(trans_protocol_mode)

            print(f"  {spec_id} 프로토콜 설정 추출 완료: {len(time_out)}개 steps")

            return {
                "api_name": api_name,
                "api_id": api_id,
                "api_endpoint": api_endpoint,
                "trans_protocol": trans_protocol,
                "time_out": time_out,
                "num_retries": num_retries
            }

        except Exception as e:
            print(f"spec_id={spec_id} 프로토콜 설정 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return None

    def overwrite_spec_config_from_mapping(self, constants_path: str = None) -> None:
        """산출물 파일을 분석하여 CONSTANTS.py의 SPEC_CONFIG 전체 블록을 덮어쓰기로 갱신"""
        from PyQt5.QtWidgets import QApplication

        try:
            if constants_path is None:
                if getattr(sys, 'frozen', False):
                    exe_dir = os.path.dirname(sys.executable)
                    constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
                else:
                    constants_path = resource_path("config/CONSTANTS.py")

            with open(constants_path, "r", encoding="utf-8") as f:
                content = f.read()

            entries = []
            mode = self.parent.target_system_edit.text().strip()
            print(f"[DEBUG] SPEC_CONFIG 업데이트 - mode: '{mode}'")

            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                spec_dir = os.path.join(exe_dir, "spec")
            else:
                spec_dir = None

            if mode == "물리보안시스템":
                priority_order = ["outSchema", "inData", "messages", "webhook"]
                if spec_dir:
                    schema_file = os.path.join(spec_dir, "Schema_response.py")
                    data_file = os.path.join(spec_dir, "Data_request.py")
                else:
                    schema_file = resource_path("spec/Schema_response.py")
                    data_file = resource_path("spec/Data_request.py")
                merged_result = self.file_generator.merge_list_prefix_mappings(schema_file, data_file)
            elif mode == "통합플랫폼시스템":
                priority_order = ["inSchema", "outData", "messages", "webhook"]
                if spec_dir:
                    schema_file = os.path.join(spec_dir, "Schema_request.py")
                    data_file = os.path.join(spec_dir, "Data_response.py")
                else:
                    schema_file = resource_path("spec/Schema_request.py")
                    data_file = resource_path("spec/Data_response.py")
                merged_result = self.file_generator.merge_list_prefix_mappings(schema_file, data_file)
            else:
                print(f"[CONFIG SPEC]: 모드 확인해주세요. mode: '{mode}'")
                return

            for spec_id in sorted(merged_result.keys()):
                QApplication.processEvents()
                spec_name = self._spec_names_cache.get(spec_id, "")
                file_map = merged_result[spec_id]
                all_lists = []

                for _fname, lists in file_map.items():
                    all_lists.extend(lists or [])

                filtered_lists = [name for name in all_lists if name.startswith(spec_id + "_")]

                def sort_by_priority(name: str) -> int:
                    if "webhook" in name.lower():
                        if "schema" in name.lower():
                            return priority_order.index("webhook") * 10 + 0
                        elif "data" in name.lower():
                            return priority_order.index("webhook") * 10 + 1
                        return priority_order.index("webhook") * 10
                    suffix = name.split("_")[-1]
                    if suffix in priority_order:
                        return priority_order.index(suffix)
                    return len(priority_order)

                specs_list = sorted(set(filtered_lists), key=sort_by_priority)

                spec_config_data = self._extract_spec_config_from_api(spec_id)
                if not spec_config_data:
                    spec_config_data = {
                        "api_name": [],
                        "api_id": [],
                        "api_endpoint": [],
                        "trans_protocol": [],
                        "time_out": [],
                        "num_retries": []
                    }

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

            # 그룹 정보 추가
            test_groups = getattr(self.parent, 'test_groups', [])

            if not test_groups:
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
                entries_dict = {}
                for entry in entries:
                    spec_id = entry.split('"')[1]
                    entries_dict[spec_id] = entry

                group_blocks = []
                for group in test_groups:
                    group_name = group.get("name", "")
                    group_id = group.get("id", "")
                    group_specs = group.get("testSpecs", [])

                    group_spec_ids = [spec.get("id") for spec in group_specs]
                    group_entries = [entries_dict[sid] for sid in group_spec_ids if sid in entries_dict]

                    group_fields = []
                    if group_name:
                        group_fields.append(f'"group_name": "{group_name}"')
                    if group_id:
                        group_fields.append(f'"group_id": "{group_id}"')

                    all_group_entries = group_fields + group_entries
                    group_content = ",\n        ".join(all_group_entries)
                    group_block = f"    {{\n        {group_content}\n    }}"
                    group_blocks.append(group_block)

                all_groups_content = ",\n".join(group_blocks)
                new_spec_config_block = f"SPEC_CONFIG = [\n{all_groups_content}\n]"

            # SPEC_CONFIG 블록 교체
            pattern = r'SPEC_CONFIG = \[[\s\S]*?\n\]'
            matches = list(re.finditer(pattern, content))

            if not matches:
                etc_comment = "\n#etc"
                etc_pos = content.find(etc_comment)
                if etc_pos != -1:
                    new_content = content[:etc_pos + 1] + new_spec_config_block + "\n\n" + content[etc_pos + 1:]
                else:
                    new_content = content + "\n\n" + new_spec_config_block + "\n"
            else:
                temp_content = content
                for match in reversed(matches[1:]):
                    temp_content = temp_content[:match.start()] + temp_content[match.end():]

                first_match_in_temp = re.search(pattern, temp_content)
                if first_match_in_temp:
                    new_content = (temp_content[:first_match_in_temp.start()] +
                                 new_spec_config_block +
                                 temp_content[first_match_in_temp.end():])
                else:
                    new_content = temp_content

            with open(constants_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print("CONSTANTS.py SPEC_CONFIG 전체 덮어쓰기 완료")

            # 메모리의 CONSTANTS.SPEC_CONFIG도 업데이트
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
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")
            else:
                constants_path = resource_path("config/CONSTANTS.py")

            with open(constants_path, 'r', encoding='utf-8') as f:
                content = f.read()

            spec_config_start = content.find('SPEC_CONFIG = [')
            if spec_config_start == -1:
                print("경고: SPEC_CONFIG 리스트를 찾을 수 없습니다.")
                return

            bracket_count = 0
            start_pos = content.find('[', spec_config_start)
            current_pos = start_pos
            end_pos = len(content)

            while current_pos < len(content):
                if content[current_pos] == '[':
                    bracket_count += 1
                elif content[current_pos] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = current_pos + 1
                        break
                current_pos += 1

            current_config = content[spec_config_start:end_pos]
            spec_key_start = current_config.find(f'"{spec_id}":')

            spec_name = self._spec_names_cache.get(spec_id, "")
            print(f"spec_id={spec_id}에 대한 spec_name: {spec_name}")

            specs_list = [
                f"{spec_id}_inSchema",
                f"{spec_id}_outData",
                f"{spec_id}_messages"
            ]

            new_spec_config = f'''"{spec_id}": {{
        "test_name": "{spec_name}",
        "specs": {specs_list},
        "trans_protocol": {config_data.get("trans_protocol", [])},
        "time_out": {config_data.get("time_out", [])},
        "num_retries": {config_data.get("num_retries", [])}
    }}'''

            if spec_key_start != -1:
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

                old_spec_block = current_config[spec_key_start:brace_end]
                new_config = current_config.replace(old_spec_block, new_spec_config)
                print(f"SPEC_CONFIG['{spec_id}'] 업데이트")
            else:
                closing_brace = current_config.rfind('}')
                if '":' in current_config:
                    new_config = current_config[:closing_brace] + f',\n    {new_spec_config}\n' + current_config[closing_brace:]
                else:
                    new_config = current_config[:closing_brace] + f'\n    {new_spec_config}\n' + current_config[closing_brace:]
                print(f"SPEC_CONFIG['{spec_id}'] 신규 추가")

            content = content.replace(current_config, new_config)

            with open(constants_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"CONSTANTS.py SPEC_CONFIG 업데이트 완료")

        except Exception as e:
            print(f"SPEC_CONFIG 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()

    # ---------- API 데이터 로드 ----------

    def load_opt_files_from_api(self, test_data):
        """API 데이터를 이용하여 OPT 파일 로드 및 스키마 생성 (모든 그룹 처리)"""
        from PyQt5.QtWidgets import QApplication

        try:
            test_groups = test_data.get("testRequest", {}).get("testGroups", [])
            if not test_groups:
                QMessageBox.warning(self.parent, "데이터 없음", "testGroups 데이터가 비어있습니다.")
                return

            all_test_specs_with_group = []
            for group in test_groups:
                group_name = group.get("name", "")
                for spec in group.get("testSpecs", []):
                    spec_with_group = spec.copy()
                    spec_with_group["group_name"] = group_name
                    all_test_specs_with_group.append(spec_with_group)

            if not all_test_specs_with_group:
                QMessageBox.warning(self.parent, "데이터 없음", "testSpecs 데이터가 비어있습니다.")
                return

            print(f"\n=== API 기반 OPT 로드 시작 ===")
            print(f"그룹 개수: {len(test_groups)}개")
            print(f"전체 시나리오 개수: {len(all_test_specs_with_group)}개")

            self._fill_test_field_table_from_api(all_test_specs_with_group)
            QApplication.processEvents()

            self.preload_all_spec_steps()
            QApplication.processEvents()

            self.preload_test_step_details_from_cache()
            QApplication.processEvents()

            # 산출물 파일 생성 (FileGeneratorService 사용)
            self.file_generator.generate_files_for_all_specs(
                self._steps_cache,
                self._test_step_cache,
                self._spec_names_cache
            )
            QApplication.processEvents()

            # 모든 spec에 대해 개별 설정 업데이트
            print(f"\n=== SPEC_CONFIG 업데이트 시작 ===")
            for spec in all_test_specs_with_group:
                spec_id = spec.get("id", "")
                if spec_id:
                    spec_config_data = self._extract_spec_config_from_api(spec_id)
                    if spec_config_data:
                        self._update_spec_config(spec_id, spec_config_data)
                QApplication.processEvents()
            print(f"=== SPEC_CONFIG 개별 업데이트 완료 ===\n")

            # SPEC_CONFIG 전체 재구성
            print(f"=== SPEC_CONFIG 전체 재구성 시작 ===")
            self.overwrite_spec_config_from_mapping()
            QApplication.processEvents()
            print(f"=== SPEC_CONFIG 전체 재구성 완료 ===\n")

            if self.parent.test_field_table.rowCount() > 0:
                self.parent.test_field_table.selectRow(0)
                self._fill_api_table_for_selected_field_from_api(0)

            self.parent.check_start_button_state()
            self.parent.check_next_button_state()

        except Exception as e:
            print(f"API 데이터 로드 실패: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self.parent, "오류", f"API 데이터 로드 중 오류가 발생했습니다:\n{str(e)}")

    # ---------- 테이블 채우기 ----------

    def _fill_test_field_table_from_api(self, test_specs):
        """API testSpecs 배열로부터 시험 분야 목록 채우기"""
        try:
            from PyQt5.QtWidgets import QApplication

            table = self.parent.test_field_table
            table.setRowCount(0)

            self._group_specs = {}

            for spec in test_specs:
                QApplication.processEvents()
                spec_id = spec.get("id", "")
                spec_name = spec.get("name", "")
                group_name = spec.get("group_name", "")

                self._spec_names_cache[spec_id] = spec_name

                if group_name not in self._group_specs:
                    self._group_specs[group_name] = []
                self._group_specs[group_name].append({
                    "id": spec_id,
                    "name": spec_name
                })

            font = QFont("Noto Sans KR")
            font.setPixelSize(19)
            font.setWeight(400)
            font.setLetterSpacing(QFont.PercentageSpacing, 100.7)

            for i, group_name in enumerate(self._group_specs.keys()):
                QApplication.processEvents()
                table.insertRow(i)

                label = ClickableRowWidget(
                    group_name, i, 0,
                    'assets/image/test_config/row.png',
                    'assets/image/test_config/arrow.png'
                )
                label.clicked.connect(self.parent.on_test_field_selected)
                table.setCellWidget(i, 0, label)
                table.setRowHeight(i, 39)

            table.clearSelection()
            table.setCurrentCell(-1, -1)
            self.parent.selected_test_field_row = None

            if hasattr(self.parent, 'scenario_table'):
                self.parent.scenario_table.setRowCount(0)
                self.parent.scenario_table.clearContents()

            if hasattr(self.parent, 'scenario_placeholder_label'):
                self.parent.scenario_placeholder_label.show()
                self.parent.scenario_placeholder_label.raise_()

            print(f"시험 분야 테이블 채우기 완료: {len(self._group_specs)}개 그룹")

        except Exception as e:
            print(f"시험 분야 테이블 채우기 실패: {e}")
            import traceback
            traceback.print_exc()

    def _fill_scenarios_for_group(self, clicked_row, group_name):
        """선택된 시험 분야의 시나리오를 시나리오 테이블에 표시"""
        try:
            from PyQt5.QtGui import QBrush, QColor

            field_table = self.parent.test_field_table
            scenario_table = self.parent.scenario_table

            field_table.blockSignals(True)
            scenario_table.blockSignals(True)

            if hasattr(self.parent, 'scenario_placeholder_label'):
                self.parent.scenario_placeholder_label.hide()

            if hasattr(self.parent, 'scenario_column_background'):
                self.parent.scenario_column_background.show()

            scenarios = self._group_specs.get(group_name, [])
            scenario_count = len(scenarios)
            group_count = len(self._group_specs)

            print(f"\n=== 테이블 재구성 시작 ===")
            print(f"선택된 그룹: {group_name} (시나리오 {scenario_count}개)")

            field_table.setRowCount(0)
            field_table.clearContents()
            field_table.setRowCount(group_count)

            for i, gname in enumerate(self._group_specs.keys()):
                if gname == group_name:
                    label = ClickableRowWidget(
                        gname, i, 0,
                        'assets/image/test_config/row_selected.png',
                        'assets/image/test_config/arrow.png'
                    )
                else:
                    label = ClickableRowWidget(
                        gname, i, 0,
                        'assets/image/test_config/row.png',
                        'assets/image/test_config/arrow.png'
                    )

                label.clicked.connect(self.parent.on_test_field_selected)
                field_table.setCellWidget(i, 0, label)
                field_table.setRowHeight(i, 39)

            scenario_table.setRowCount(0)
            scenario_table.clearContents()
            scenario_table.setRowCount(scenario_count)

            for i, scenario in enumerate(scenarios):
                label = ClickableCheckboxRowWidget(
                    scenario["name"], i, 0,
                    'assets/image/test_config/row_selected.png',
                    'assets/image/test_config/row_selected.png',
                    'assets/image/test_config/checkbox_unchecked.png',
                    'assets/image/test_config/checkbox_checked.png'
                )
                label.setProperty("spec_id", scenario["id"])
                label.clicked.connect(self.parent.on_scenario_selected)
                scenario_table.setCellWidget(i, 0, label)
                scenario_table.setRowHeight(i, 39)

            field_table.clearSelection()
            field_table.setCurrentCell(-1, -1)
            scenario_table.clearSelection()
            scenario_table.setCurrentCell(-1, -1)

            field_table.blockSignals(False)
            scenario_table.blockSignals(False)

            print(f"시나리오 채우기 완료: {group_name} - {scenario_count}개 시나리오 표시")

            self.parent.resizeEvent(QResizeEvent(self.parent.size(), self.parent.size()))

        except Exception as e:
            print(f"시나리오 채우기 실패: {e}")
            import traceback
            traceback.print_exc()
            if 'field_table' in locals():
                field_table.blockSignals(False)
            if 'scenario_table' in locals():
                scenario_table.blockSignals(False)

    def _fill_api_table_for_selected_field_from_api(self, row):
        """선택된 시험 시나리오의 API 테이블 채우기"""
        try:
            widget = self.parent.scenario_table.cellWidget(row, 0)
            if not widget:
                return

            spec_id = widget.property("spec_id")
            if not spec_id:
                return

            cached_steps = self._steps_cache.get(spec_id)
            if cached_steps is None:
                spec_data = self.api_client.fetch_specification_by_id(spec_id)
                if not spec_data:
                    return
                steps = spec_data.get("specification", {}).get("steps", [])
                cached_steps = [
                    {"id": s.get("id"), "name": s.get("name", "")}
                    for s in steps if s.get("hasApi")
                ]
                self._steps_cache[spec_id] = cached_steps

            self.parent.api_test_table.setRowCount(0)

            if hasattr(self.parent, 'api_placeholder_label'):
                self.parent.api_placeholder_label.hide()

            for step in cached_steps:
                step_id = step.get("id")
                ts = self._test_step_cache.get(step_id) if hasattr(self, "_test_step_cache") else None
                name_to_show = ""
                id_to_show = ""

                if ts:
                    name_to_show = ts.get("name", "")
                    endpoint = ts.get("endpoint")
                    id_to_show = "" if endpoint is None else str(endpoint)
                else:
                    step_detail = self.api_client.fetch_test_step_by_id(step_id)
                    if step_detail:
                        endpoint = step_detail.get("step", {}).get("api", {}).get("endpoint", "")
                        name_to_show = step_detail.get("step", {}).get("name", step.get("name", ""))
                        id_to_show = str(endpoint) if endpoint else ""
                    else:
                        name_to_show = step.get("name", "")
                        id_to_show = ""

                r = self.parent.api_test_table.rowCount()
                self.parent.api_test_table.insertRow(r)

                name_item = QTableWidgetItem(name_to_show)
                name_item.setTextAlignment(Qt.AlignCenter)
                name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.parent.api_test_table.setItem(r, 0, name_item)

                id_item = QTableWidgetItem(id_to_show)
                id_item.setTextAlignment(Qt.AlignCenter)
                id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.parent.api_test_table.setItem(r, 1, id_item)

            print(f"API 테이블 채우기 완료: {len(cached_steps)}개 API")

        except Exception as e:
            print(f"API 테이블 채우기 실패: {e}")
            import traceback
            traceback.print_exc()

    # ---------- Preload ----------

    def preload_all_spec_steps(self):
        """_group_specs에 있는 모든 spec_id의 steps(id, name)만 미리 캐싱"""
        from PyQt5.QtWidgets import QApplication

        loaded, skipped = 0, 0
        total_specs = 0

        if not hasattr(self, '_group_specs') or not self._group_specs:
            print(f"[preload_all_spec_steps] 경고: _group_specs가 비어있습니다.")
            return

        for group_name, specs in self._group_specs.items():
            for spec in specs:
                QApplication.processEvents()
                total_specs += 1
                spec_id = spec.get("id")
                if not spec_id:
                    continue

                if spec_id in self._steps_cache:
                    skipped += 1
                    continue

                spec_data = self.api_client.fetch_specification_by_id(spec_id)
                QApplication.processEvents()
                if not spec_data:
                    continue

                steps = spec_data.get("specification", {}).get("steps", [])
                trimmed = [
                    {"id": s.get("id"), "name": s.get("name", "")}
                    for s in steps
                    if s.get("hasApi") and s.get("id", "").count("-") <= 1
                ]

                self._steps_cache[spec_id] = trimmed
                loaded += 1

        print(f"[preload_all_spec_steps] 로드:{loaded}, 스킵:{skipped}, 총 spec 수:{total_specs}")

    def preload_test_step_details_from_cache(self):
        """_steps_cache를 순회하며 step 상세 응답을 _test_step_cache에 저장"""
        from PyQt5.QtWidgets import QApplication

        loaded, skipped, empty = 0, 0, 0

        for spec_id, steps in self._steps_cache.items():
            QApplication.processEvents()
            if not isinstance(steps, list):
                continue

            for s in steps:
                QApplication.processEvents()
                step_id = s.get("id")
                step_name = s.get("name", "")

                if step_id is None:
                    empty += 1
                    continue

                if step_id in self._test_step_cache:
                    skipped += 1
                    continue

                detail = self.api_client.fetch_test_step_by_id(step_id)
                QApplication.processEvents()
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

        print(
            f"[preload_test_step_details_from_cache] "
            f"로드:{loaded}, 스킵:{skipped}, id없음:{empty}, "
            f"총 step 수(대략): {sum(len(v) for v in self._steps_cache.values())}"
        )

    # ---------- UI Helper ----------

    def _show_initial_scenario_message(self):
        """시험 시나리오 컬럼에 초기 메시지 표시"""
        try:
            from PyQt5.QtGui import QBrush, QColor

            table = self.parent.test_field_table
            row_count = table.rowCount()

            if row_count > 0:
                message_item = QTableWidgetItem("시험 분야를 선택하면\n시나리오가 표시됩니다.")
                font = QFont("Noto Sans KR")
                font.setPixelSize(16)
                message_item.setFont(font)
                message_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                message_item.setFlags(Qt.ItemIsEnabled)
                message_item.setBackground(QBrush(QColor("#FFFFFF")))

                table.setItem(0, 1, message_item)
                table.setSpan(0, 1, row_count, 1)

        except Exception as e:
            print(f"초기 시나리오 메시지 표시 실패: {e}")

    def _show_scenario_placeholder(self):
        """시험 시나리오 안내 문구 표시"""
        try:
            scenario_table = self.parent.scenario_table
            scenario_table.setRowCount(0)
            scenario_table.clearContents()

            if hasattr(self.parent, 'scenario_column_background'):
                self.parent.scenario_column_background.hide()

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
            table.setRowCount(0)

            if hasattr(self.parent, 'api_placeholder_label'):
                self.parent.api_placeholder_label.show()

        except Exception as e:
            print(f"초기 API 메시지 표시 실패: {e}")

    # ---------- API 위임 메서드 (하위 호환성) ----------

    def fetch_test_info_by_ip(self, ip_address):
        """IP 주소로 시험 정보 조회 (APIClient 위임)"""
        return self.api_client.fetch_test_info_by_ip(ip_address)

    def fetch_specification_by_id(self, spec_id):
        """spec_id로 specification 상세 정보 조회 (APIClient 위임)"""
        return self.api_client.fetch_specification_by_id(spec_id)

    def fetch_test_step_by_id(self, step_id):
        """step_id로 test-step 상세 정보 조회 (APIClient 위임)"""
        return self.api_client.fetch_test_step_by_id(step_id)

    def get_local_ip_address(self):
        """현재 PC의 로컬 IP 주소를 가져옴 (APIClient 위임)"""
        return self.api_client.get_local_ip_address()

    def send_heartbeat_idle(self):
        """시험 정보 불러오기 시 idle 상태 전송 (APIClient 위임)"""
        return self.api_client.send_heartbeat_idle()

    def send_heartbeat_busy(self, test_info):
        """시험 시작 시 busy 상태 + 시험 정보 전송 (APIClient 위임)"""
        return self.api_client.send_heartbeat_busy(test_info)

    # ---------- 인증 위임 메서드 (하위 호환성) ----------

    def get_authentication_credentials(self, spec_id):
        """플랫폼 검증 시 Authentication 인증 정보 추출 (AuthService 위임)"""
        return self.auth_service.get_authentication_credentials(spec_id)

    def get_authentication_from_data_request(self, spec_id):
        """물리보안 시 Data_request.py에서 인증 정보 추출 (AuthService 위임)"""
        return self.auth_service.get_authentication_from_data_request(spec_id)

    def update_data_request_authentication(self, spec_id, user_id, password):
        """Data_request.py의 Authentication 인증 정보 업데이트 (AuthService 위임)"""
        return self.auth_service.update_data_request_authentication(spec_id, user_id, password)

    # ---------- 파일 생성 위임 메서드 (하위 호환성) ----------

    def _generate_files_for_all_specs(self):
        """모든 testSpecIds를 하나의 파일로 합쳐서 생성 (FileGeneratorService 위임)"""
        return self.file_generator.generate_files_for_all_specs(
            self._steps_cache,
            self._test_step_cache,
            self._spec_names_cache
        )

    def _generate_response_code_file(self):
        """ResponseCode.py 파일 생성 (FileGeneratorService 위임)"""
        return self.file_generator.generate_response_code_file()

    def merge_list_prefix_mappings(self, file_a: str, file_b: str) -> Dict[str, Dict[str, List[str]]]:
        """두 파일에서 리스트 변수를 추출하여 prefix별로 병합 (FileGeneratorService 위임)"""
        return self.file_generator.merge_list_prefix_mappings(file_a, file_b)

    def extract_lists(self, file_path: str) -> Dict[str, List[str]]:
        """파일에서 리스트 변수들을 추출 (FileGeneratorService 위임)"""
        return self.file_generator.extract_lists(file_path)
