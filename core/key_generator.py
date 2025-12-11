# key_id_generator.py
from typing import Dict, List, Any


class KeyIdGenerator:
    """key -> field ID 매핑을 생성하고 파일로 저장하는 클래스"""

    def __init__(self):
        pass

    def generate_keyid_files(
            self,
            steps_cache: Dict,
            test_step_cache: Dict,
            file_type: str
    ):
        """
        모든 spec의 key-fieldID 매핑(request + response)을 생성하고
        file_type에 따라 KeyId_request.py 또는 KeyId_response.py에 저장

        Args:
            steps_cache: spec_id -> steps 매핑 딕셔너리
            test_step_cache: step_id -> step detail 매핑 딕셔너리
            file_type: "request" 또는 "response" - 저장할 파일명 결정
        """
        try:
            print(f"\n=== KeyId_{file_type}.py 파일 생성 시작 ===")

            # Request와 Response 데이터 모두 생성
            request_content = self._generate_content(steps_cache, test_step_cache, "request")
            response_content = self._generate_content(steps_cache, test_step_cache, "response")

            # 두 데이터를 합쳐서 하나의 파일 내용으로 생성
            combined_content = "# Key to Field ID Mapping\n"
            combined_content += "# Contains both Request and Response mappings\n\n"
            combined_content += "# ========== REQUEST MAPPINGS ==========\n"
            combined_content += request_content.split('\n', 1)[1] if '\n' in request_content else request_content
            combined_content += "\n# ========== RESPONSE MAPPINGS ==========\n"
            combined_content += response_content.split('\n', 1)[1] if '\n' in response_content else response_content

            # file_type에 따라 파일 저장
            self._save_keyid_file(combined_content, file_type)

            print(f"=== KeyId_{file_type}.py 파일 생성 완료 ===")
            print(f"[INFO] Request + Response 데이터 모두 포함됨\n")

        except Exception as e:
            print(f"KeyId 파일 생성 실패: {e}")
            import traceback
            traceback.print_exc()

    def _generate_content(
            self,
            steps_cache: Dict,
            test_step_cache: Dict,
            direction: str
    ) -> str:
        """
        특정 direction에 대한 파일 내용 생성

        Args:
            steps_cache: spec_id -> steps 매핑 딕셔너리
            test_step_cache: step_id -> step detail 매핑 딕셔너리
            direction: "request" 또는 "response"

        Returns:
            생성된 파일 내용 문자열
        """
        content = f"# {direction.capitalize()} Key to Field ID Mapping\n\n"

        for spec_id, steps in steps_cache.items():
            if not isinstance(steps, list):
                continue

            spec_mappings = {}  # {endpoint: {key: field_id}}

            temp_spec_id = spec_id + "_"

            for s in steps:
                step_id = s.get("id")
                ts = test_step_cache.get(step_id)

                if not ts:
                    continue

                # numbered_endpoint 가져오기
                numbered_endpoint = ts.get("_numbered_endpoint")
                if not numbered_endpoint:
                    detail = ts.get("detail", {})
                    step_data = detail.get("step", {})
                    api = step_data.get("api", {})
                    endpoint = api.get("endpoint", "")
                    numbered_endpoint = endpoint[1:] if endpoint.startswith("/") else endpoint

                # key-fieldID 매핑 추출
                key_id_mappings = self.extract_key_field_id_mapping(ts)

                # direction에 해당하는 데이터만 저장
                if key_id_mappings[direction]:
                    spec_mappings[numbered_endpoint] = key_id_mappings[direction]

            # 파일 내용 생성
            if spec_mappings:
                content += self._format_spec_content(
                    spec_id,
                    temp_spec_id,
                    spec_mappings,
                    direction
                )

        return content

    def extract_key_field_id_mapping(self, ts: Dict) -> Dict[str, Dict[str, str]]:
        """
        step의 request/response bodyJson에서 key -> field ID 매핑 추출
        WebHook이 있는 경우 requestSpec, integrationSpec도 추출

        Args:
            ts: _test_step_cache에서 가져온 step 데이터

        Returns:
            dict: {
                "request": {key: field_id, ...},
                "response": {key: field_id, ...}
            }
        """
        result = {
            "request": {},
            "response": {}
        }

        detail = ts.get("detail", {})
        step_data = detail.get("step", {})
        api = step_data.get("api", {})

        # request와 response 각각 처리
        for direction in ["request", "response"]:
            body_data = api.get(direction, {})
            if isinstance(body_data, dict):
                body_json = body_data.get("bodyJson", [])
                if isinstance(body_json, list):
                    self._collect_key_field_id_mapping(
                        body_json,
                        result[direction],
                        prefix=""
                    )

        # WebHook 데이터 처리
        settings = api.get("settings", {})
        webhook = settings.get("webhook", {})
        if webhook:
            # requestSpec → response_key_ids에 병합
            request_spec = webhook.get("requestSpec")
            if request_spec:
                if isinstance(request_spec, list):
                    # requestSpec이 리스트인 경우 (bodyJson 배열이 직접 들어있음)
                    self._collect_key_field_id_mapping(
                        request_spec,
                        result["response"],
                        prefix=""
                    )
                elif isinstance(request_spec, dict) and "bodyJson" in request_spec:
                    # requestSpec이 딕셔너리인 경우 (bodyJson 키가 있음)
                    self._collect_key_field_id_mapping(
                        request_spec.get("bodyJson", []),
                        result["response"],
                        prefix=""
                    )

            # integrationSpec → request_key_ids에 병합
            integration_spec = webhook.get("integrationSpec")
            if integration_spec:
                if isinstance(integration_spec, list):
                    # integrationSpec이 리스트인 경우 (bodyJson 배열이 직접 들어있음)
                    self._collect_key_field_id_mapping(
                        integration_spec,
                        result["request"],
                        prefix=""
                    )
                elif isinstance(integration_spec, dict) and "bodyJson" in integration_spec:
                    # integrationSpec이 딕셔너리인 경우 (bodyJson 키가 있음)
                    self._collect_key_field_id_mapping(
                        integration_spec.get("bodyJson", []),
                        result["request"],
                        prefix=""
                    )

        return result

    def _collect_key_field_id_mapping(
            self,
            fields: List[Dict],
            mapping_dict: Dict[str, str],
            prefix: str = ""
    ):
        """
        재귀적으로 필드를 순회하며 key -> field ID 매핑을 수집
        중첩된 객체는 dot notation으로 표현 (예: "sensorDeviceLoc.lon")

        Args:
            fields: bodyJson 필드 리스트
            mapping_dict: 매핑을 저장할 딕셔너리 (참조로 전달)
            prefix: 현재까지의 key 경로 (dot notation)
        """
        if not isinstance(fields, list):
            return

        for field in fields:
            if not isinstance(field, dict):
                continue

            key = field.get("key", "")
            field_id = field.get("id")
            field_type = field.get("type", "")

            # key가 있고 (빈 문자열이 아니고) id가 있으면 수집
            if key and key.strip() != "" and field_id:
                # dot notation으로 전체 경로 생성
                full_key = f"{prefix}.{key}" if prefix else key
                mapping_dict[full_key] = field_id

            # children이 있으면 재귀 호출 (object나 array의 경우)
            children = field.get("children")
            if children and field_type in ["object", "array"]:
                # 현재 key를 prefix에 추가 (key가 있는 경우에만)
                new_prefix = f"{prefix}.{key}" if (prefix and key and key.strip() != "") else (
                    key if key and key.strip() != "" else prefix)
                self._collect_key_field_id_mapping(children, mapping_dict, new_prefix)

    def _format_spec_content(
            self,
            spec_id: str,
            temp_spec_id: str,
            mappings: Dict[str, Dict[str, str]],
            direction: str
    ) -> str:
        """
        spec별 파일 내용 포맷팅

        Args:
            spec_id: 스펙 ID
            temp_spec_id: 스펙 ID with underscore (spec_id + "_")
            mappings: endpoint -> {key: field_id} 매핑
            direction: "request" 또는 "response"

        Returns:
            포맷팅된 문자열
        """
        content = f"# {spec_id}\n"

        # 각 endpoint별 딕셔너리 생성
        for endpoint, key_id_map in mappings.items():
            var_name = f"{temp_spec_id}{endpoint}_{direction}_key_ids"
            content += f"{var_name} = {{\n"
            for key, field_id in key_id_map.items():
                content += f'    "{key}": "{field_id}",\n'
            content += "}\n\n"

        # 리스트 묶음 생성
        list_name = f"{spec_id}_{direction}_key_ids"
        content += f"# {spec_id} {direction.capitalize()} Key-ID Mapping 리스트\n"
        content += f"{list_name} = [\n"
        for endpoint in mappings.keys():
            content += f"    {temp_spec_id}{endpoint}_{direction}_key_ids,\n"
        content += "]\n\n"

        return content

    def _save_keyid_file(self, content: str, file_type: str):
        """
        KeyId 파일을 디스크에 저장

        Args:
            content: 파일 내용 (request + response 모두 포함)
            file_type: "request" 또는 "response" - 저장할 파일명
        """
        import sys
        import os

        filename = f"KeyId_{file_type}.py"

        # 저장 경로 결정
        if getattr(sys, 'frozen', False):
            # PyInstaller 환경
            exe_dir = os.path.dirname(sys.executable)
            spec_dir = os.path.join(exe_dir, "spec")
            os.makedirs(spec_dir, exist_ok=True)
            output_path = os.path.join(spec_dir, filename)
        else:
            # 일반 실행
            from core.functions import resource_path
            output_path = resource_path(f"spec/{filename}")

        # 파일 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        abs_path = os.path.abspath(output_path)
        print(f"[생성 완료] {filename}: {output_path}")
        print(f"[생성 완료] 절대 경로: {abs_path}")