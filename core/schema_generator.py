"""
JSON Schema를 Python Schema로 변환하는 생성기
JSON 스키마 정의를 json_checker 라이브러리 형식으로 변환합니다.
"""
import json
import os
from typing import Dict, List, Any, Union
from .functions import resource_path


class SchemaGenerator:
    """JSON Schema를 Python Schema로 변환하는 클래스"""
    
    def __init__(self):
        self.generated_schemas = {}
    
    def parse_json_schema(self, schema_obj: Dict, required_fields: List[str] = None) -> Union[Dict, List, str]:
        """
        JSON schema 객체를 Python schema로 변환합니다.
        
        Args:
            schema_obj: JSON schema 객체
            required_fields: 필수 필드 리스트
            
        Returns:
            변환된 Python schema
        """
        if required_fields is None:
            required_fields = []
        
        schema_type = schema_obj.get("type", "object")
        
        if schema_type == "object":
            return self._parse_object_schema(schema_obj, required_fields)
        elif schema_type == "array":
            return self._parse_array_schema(schema_obj)
        elif schema_type == "string":
            return str
        elif schema_type == "integer":
            return int
        elif schema_type == "number":
            return float
        elif schema_type == "boolean":
            return bool
        else:
            return str  # 기본값
    
    def _parse_object_schema(self, schema_obj: Dict, parent_required: List[str] = None) -> Dict:
        """object 타입 스키마를 파싱합니다."""
        if parent_required is None:
            parent_required = []
        
        properties = schema_obj.get("properties", {})
        required_fields = schema_obj.get("required", [])
        
        result = {}
        
        for key, prop_schema in properties.items():
            # 타입 변환
            python_type = self.parse_json_schema(prop_schema, required_fields)
            
            # required 체크
            if key in required_fields:
                result[f'"{key}"'] = python_type
            else:
                result[f'OptionalKey("{key}")'] = python_type
        
        return result
    
    def _parse_array_schema(self, schema_obj: Dict) -> List:
        """array 타입 스키마를 파싱합니다."""
        items_schema = schema_obj.get("items", {"type": "string"})
        item_type = self.parse_json_schema(items_schema)
        return [item_type]
    
    def generate_endpoint_schema(self, step: Dict, schema_type: str = "request") -> Dict[str, Any]:
        """
        각 step의 endpoint별 스키마를 생성합니다.
        
        Args:
            step: API step 정보
            schema_type: "request" 또는 "response"
            
        Returns:
            생성된 스키마 정보
        """
        api = step.get("api", {})
        endpoint = api.get("endpoint", "")
        
        # schema_type에 따라 validation key와 suffix 결정
        if schema_type == "request":
            validation_key = "requestSchema"
            suffix = "_in_schema"
        else:  # response
            validation_key = "responseSchema"
            suffix = "_out_schema"
        
        validation_data = api.get(validation_key, {})
        
        # endpoint에서 변수명 생성 (/ 제거, 첫 글자 대문자)
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        
        schema_name = f"{endpoint}{suffix}"
        
        # validation이 비어있거나 properties가 없으면 빈 딕셔너리
        if (not validation_data or 
            not validation_data.get("properties") or 
            len(validation_data.get("properties", {})) == 0):
            schema_content = {}
        else:
            # properties가 있으면 각 필드를 변환
            schema_content = self.parse_json_schema(validation_data)
        
        return {
            "name": schema_name,
            "content": schema_content,
            "endpoint": endpoint
        }
    
    def format_schema_content(self, content: Union[Dict, List, str]) -> str:
        """스키마 내용을 Python 코드 문자열로 포맷팅합니다."""
        if isinstance(content, dict):
            if not content:
                return "{}"
            
            lines = ["{"]
            for key, value in content.items():
                formatted_value = self.format_schema_content(value)
                lines.append(f"    {key}: {formatted_value},")
            lines.append("}")
            return "\n".join(lines)
        
        elif isinstance(content, list):
            if not content:
                return "[]"
            
            item_content = self.format_schema_content(content[0])
            return f"[{item_content}]"
        
        elif content == str:
            return "str"
        elif content == int:
            return "int"
        elif content == float:
            return "float"
        elif content == bool:
            return "bool"
        else:
            return "str"
    
    def create_schema_file(self, json_path: str, schema_type: str = "request", output_path: str = None, spec_prefix: str = "video") -> str:
        """
        JSON 파일로부터 전체 스키마 파일을 생성합니다.

        Args:
            json_path: 입력 JSON 파일 경로
            schema_type: "request" 또는 "response"
            output_path: 출력 파일 경로
            spec_prefix: 변수명 접두사 (예: "spec-001", "spec-0011")

        Returns:
            생성된 파일 경로
        """
        if not output_path:
            if schema_type == "request":
                output_path = "spec/video/videoSchema_request.py"
            else:  # response
                output_path = "spec/video/videoSchema_response.py"

        # JSON 파일 로드
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        specification = data.get("specification", {})
        spec_id = specification.get("id", "")
        steps = specification.get("steps", [])

        # WebHook 파일인지 확인
        is_webhook = "WebHook" in json_path

        # 파일 내용 생성
        content = "from json_checker import OptionalKey\n\n\n"

        # 각 step별로 스키마 생성
        schema_names = []
        webhook_schemas = []

        for step in steps:
            step_id = step.get("id", "")
            api = step.get("api", {})
            endpoint = api.get("endpoint", "")
            settings = api.get("settings", {})
            trans_protocol = settings.get("transProtocol", {})

            # 콜백 스텝 (endpoint가 없고 urlKey만 있는 스텝)은 건너뛰기
            if not endpoint and api.get("urlKey"):
                continue

            # 일반 스키마 생성
            schema_info = self.generate_endpoint_schema(step, schema_type)
            schema_name = schema_info["name"]
            schema_content = schema_info["content"]
            endpoint_name = schema_info["endpoint"]

            # 주석 추가
            content += f"# {endpoint_name}\n"

            # 스키마 변수 생성
            formatted_content = self.format_schema_content(schema_content)
            content += f"{schema_name} = {formatted_content}\n\n"

            # 리스트를 위해 스키마 이름 저장
            schema_names.append(schema_name)

            # WebHook 모드이고 transProtocol.mode가 "WebHook"인 경우
            if is_webhook and trans_protocol.get("mode") == "WebHook":
                # 해당 스텝과 쌍을 이루는 콜백 스텝 찾기
                callback_step_id = f"{step_id}-1"
                callback_step = None

                for s in steps:
                    if s.get("id") == callback_step_id:
                        callback_step = s
                        break

                if callback_step:
                    callback_api = callback_step.get("api", {})

                    # WebHook 스키마 생성 로직 (schema_type에 따라 다른 소스 사용)
                    if schema_type == "request":
                        # Request 모드: responseSchema 사용 (콜백으로 들어오는 페이로드)
                        target_schema = callback_api.get("responseSchema", {})
                        if target_schema:
                            webhook_payload_schema = self._generate_webhook_schema_from_json_schema(target_schema, endpoint_name, schema_type)
                            webhook_schemas.append(webhook_payload_schema)
                            # Request 모드에서는 ACK 응답 스키마를 생성하지 않음
                    else:  # response 모드
                        # Response 모드: requestSchema 사용 (콜백으로 들어오는 페이로드)
                        target_schema = callback_api.get("requestSchema", {})
                        if target_schema:
                            webhook_payload_schema = self._generate_webhook_schema_from_json_schema(target_schema, endpoint_name, schema_type)
                            webhook_schemas.append(webhook_payload_schema)

                        # Response 모드에서만 ACK 응답 스키마 생성 (우리가 200 OK와 함께 보내는 응답)
                        response_schema = callback_api.get("responseSchema", {})
                        if response_schema:
                            webhook_ack_schema = self._generate_webhook_ack_schema(response_schema)
                            if webhook_ack_schema not in webhook_schemas:  # 중복 방지
                                webhook_schemas.append(webhook_ack_schema)

        # WebHook 전용 스키마들 추가
        webhook_schema_names = []
        for webhook_schema in webhook_schemas:
            content += webhook_schema + "\n"
            # WebHook 스키마 이름 추출
            lines = webhook_schema.strip().split('\n')
            for line in lines:
                if ' = {' in line and ('WebHook_' in line or 'Webhook_' in line):
                    schema_name = line.split(' = ')[0].strip()
                    webhook_schema_names.append(schema_name)
                    break

        # 스키마 리스트 생성 (steps 순서대로) - spec_prefix 사용
        content += f"# {spec_prefix} 스키마 리스트\n"
        if schema_type == "request":
            list_name = f"{spec_prefix}_inSchema"
        else:  # response
            list_name = f"{spec_prefix}_outSchema"

        content += f"{list_name} = [\n"
        for name in schema_names:
            content += f"    {name},\n"
        content += "]\n"

        # WebHook 스키마 리스트 생성 (WebHook 전용) - spec_prefix 사용
        if is_webhook and webhook_schema_names:
            content += f"\n# {spec_prefix} WebHook 전용 스키마 리스트\n"
            content += f"{spec_prefix}_webhookSchema = [\n"
            for name in webhook_schema_names:
                content += f"    {name},\n"
            content += "]\n"

        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 파일 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def _generate_webhook_payload_schema(self, request_data: Dict, endpoint_name: str) -> str:
        """
        WebHook 콜백 페이로드 스키마를 생성합니다.

        Args:
            request_data: 콜백의 requestData
            endpoint_name: 엔드포인트 이름 (Authentication, RealtimeVideoEventInfos 등)

        Returns:
            스키마 코드 문자열
        """
        schema_name = f"WebHook_{endpoint_name}_out_schema"

        # requestData를 기반으로 스키마 생성
        schema_content = self._generate_schema_from_data(request_data)

        # 주석과 스키마 변수 생성
        result = f"# WebHook {endpoint_name}\n"
        formatted_content = self.format_schema_content(schema_content)
        result += f"{schema_name} = {formatted_content}\n"

        return result

    def _generate_webhook_schema_from_json_schema(self, json_schema: Dict, endpoint_name: str, schema_type: str = "request") -> str:
        """
        JSON Schema를 기반으로 WebHook 페이로드 스키마를 생성합니다.

        Args:
            json_schema: JSON Schema 객체
            endpoint_name: 엔드포인트 이름
            schema_type: "request" 또는 "response"

        Returns:
            스키마 코드 문자열
        """
        # schema_type에 따라 suffix 결정
        if schema_type == "request":
            # Request 모드: responseSchema를 보므로 _out_schema
            suffix = "_out_schema"
        else:  # response
            # Response 모드: requestSchema를 보므로 _in_schema
            suffix = "_in_schema"

        schema_name = f"WebHook_{endpoint_name}{suffix}"

        # JSON Schema를 Python Schema로 변환
        schema_content = self.parse_json_schema(json_schema)

        # 주석과 스키마 변수 생성
        result = f"# WebHook {endpoint_name}\n"
        formatted_content = self.format_schema_content(schema_content)
        result += f"{schema_name} = {formatted_content}\n"

        return result

    def _generate_webhook_ack_schema(self, response_schema: Dict) -> str:
        """
        WebHook ACK 응답 스키마를 생성합니다.

        Args:
            response_schema: 콜백의 responseSchema

        Returns:
            스키마 코드 문자열
        """
        schema_name = "Webhook_out_schema"

        # responseSchema를 기반으로 스키마 생성
        schema_content = self.parse_json_schema(response_schema)

        # 주석과 스키마 변수 생성
        result = f"# WebHook ACK 응답\n"
        formatted_content = self.format_schema_content(schema_content)
        result += f"{schema_name} = {formatted_content}\n"

        return result

    def _generate_schema_from_data(self, data: Any) -> Union[Dict, List, str]:
        """
        실제 데이터 값으로부터 스키마를 생성합니다.

        Args:
            data: 실제 데이터 값

        Returns:
            생성된 스키마
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # 모든 필드를 OptionalKey로 처리 (실제 데이터에서는 required 정보가 없음)
                result[f'OptionalKey("{key}")'] = self._generate_schema_from_data(value)
            return result
        elif isinstance(data, list):
            if data:  # 리스트가 비어있지 않은 경우
                return [self._generate_schema_from_data(data[0])]
            else:
                return []
        elif isinstance(data, str):
            return str
        elif isinstance(data, int):
            return int
        elif isinstance(data, float):
            return float
        elif isinstance(data, bool):
            return bool
        else:
            return str  # 기본값


def generate_schema_file(json_path: str, schema_type: str = "request", output_path: str = None, spec_prefix: str = "video") -> str:
    """
    편의 함수: JSON 파일로부터 스키마 파일을 생성합니다.

    Args:
        json_path: 입력 JSON 파일 경로
        schema_type: "request" 또는 "response"
        output_path: 출력 파일 경로
        spec_prefix: 변수명 접두사 (예: "spec-001", "spec-0011")

    Returns:
        생성된 파일 경로
    """
    generator = SchemaGenerator()
    return generator.create_schema_file(json_path, schema_type, output_path, spec_prefix)