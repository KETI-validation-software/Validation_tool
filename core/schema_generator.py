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
    
    def create_schema_file(self, json_path: str, schema_type: str = "request", output_path: str = None) -> str:
        """
        JSON 파일로부터 전체 스키마 파일을 생성합니다.
        
        Args:
            json_path: 입력 JSON 파일 경로
            schema_type: "request" 또는 "response"
            output_path: 출력 파일 경로
            
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
        steps = specification.get("steps", [])
        
        # 파일 내용 생성
        content = "from json_checker import OptionalKey\n\n\n"
        
        # 각 step별로 스키마 생성
        schema_names = []
        for step in steps:
            schema_info = self.generate_endpoint_schema(step, schema_type)
            schema_name = schema_info["name"]
            schema_content = schema_info["content"]
            endpoint = schema_info["endpoint"]
            
            # 주석 추가
            content += f"# {endpoint}\n"
            
            # 스키마 변수 생성
            formatted_content = self.format_schema_content(schema_content)
            content += f"{schema_name} = {formatted_content}\n\n"
            
            # 리스트를 위해 스키마 이름 저장
            schema_names.append(schema_name)
        
        # 스키마 리스트 생성 (steps 순서대로)
        content += "# steps 순서대로 스키마 리스트 생성\n"
        if schema_type == "request":
            list_name = "videoInSchema"
        else:  # response
            list_name = "videoOutSchema"
        
        content += f"{list_name} = [\n"
        for name in schema_names:
            content += f"    {name},\n"
        content += "]\n"
        
        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 파일 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path


def generate_schema_file(json_path: str, schema_type: str = "request", output_path: str = None) -> str:
    """
    편의 함수: JSON 파일로부터 스키마 파일을 생성합니다.
    
    Args:
        json_path: 입력 JSON 파일 경로
        schema_type: "request" 또는 "response"
        output_path: 출력 파일 경로
        
    Returns:
        생성된 파일 경로
    """
    generator = SchemaGenerator()
    return generator.create_schema_file(json_path, schema_type, output_path)