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

    def _parse_body_json(self, schema_obj: Dict) -> Dict:
        """
        커스텀 포맷:
          {
            "request": {
              "bodyJson": [ { key,type,value,required,children? }, ... ]
            }
          }
          또는 { "bodyJson": [ ... ] }
        """
        fields = None
        if fields is None:
            fields = schema_obj.get("bodyJson", [])
        if not isinstance(fields, list):
            return {}
        return self._parse_body_fields(fields)

    # ### NEW: 커스텀 포맷 필드 리스트 파서(재귀)
    def _parse_body_fields(self, fields: List[Dict]) -> Dict:
        """
        fields: [
          {
            "key": "timePeriod",
            "type": "object",
            "required": true,
            "children": [
              {"key":"startTime","type":"number","required":true},
              {"key":"endTime","type":"number","required":true}
            ]
          },
          ...
        ]
        """
        result: Dict[str, Union[Dict, List, type, str]] = {}
        for field in fields:
            if not isinstance(field, dict):
                continue
            key = field.get("key")
            if not key or key.strip() == "":    # 새로 추가
                continue
            ftype = str(field.get("type", "string")).lower()
            required = bool(field.get("required", False))
            children = field.get("children", [])

            # 타입 매핑
            if ftype == "object":
                # 자식들을 객체 스키마로
                child_schema = self._parse_body_fields(children) if isinstance(children, list) else {}
                py_schema = child_schema

            elif ftype == "array":
                # items 결정: children 기반
                item_schema = str  # 기본
                if isinstance(children, list) and len(children) > 0:
                    # 케이스1) 자식이 여러 개면 '객체 아이템'으로 간주
                    if len(children) > 1:
                        item_schema = self._parse_body_fields(children)  # -> dict
                    else:
                        # 한 개만 있을 때: 스칼라/객체 모두 처리
                        only = children[0]
                        only_type = str(only.get("type", "string")).lower()
                        if only_type in ("object", "array"):
                            # 중첩 구조
                            if only_type == "object":
                                item_schema = self._parse_body_fields(only.get("children", []) or [])
                            else:
                                # 배열의 아이템이 배열인 경우
                                # 재귀적으로 한 번 더 파싱
                                nested_children = only.get("children", []) or []
                                nested_item = str
                                if nested_children:
                                    if len(nested_children) > 1:
                                        nested_item = self._parse_body_fields(nested_children)
                                    else:
                                        leaf = nested_children[0]
                                        nested_item = self._py_type_from_string(leaf.get("type", "string"))
                                item_schema = [nested_item]
                        else:
                            # 스칼라 타입
                            item_schema = self._py_type_from_string(only_type)
                py_schema = [item_schema]

            elif ftype in ("string", "number", "integer", "boolean"):
                py_schema = self._py_type_from_string(ftype)

            else:
                # 알 수 없는 타입은 문자열로 처리
                py_schema = str

            # 필수/선택 키로 기록 (현 구조 유지: 문자열 키)
            if key is None:
                continue
            if required:
                result[f'"{key}"'] = py_schema
            else:
                result[f'OptionalKey("{key}")'] = py_schema

        return result

    # ### NEW: 스칼라 타입 매핑
    def _py_type_from_string(self, t: str):
        t = (t or "").lower()
        if t == "string":
            return str
        if t == "integer":
            return int
        if t == "number":
            return int
        if t == "boolean":
            return bool
        return str
    
    def generate_endpoint_schema(self, step: Dict, schema_type: str = "request") -> Dict[str, Any]:
        """
        각 step의 endpoint별 스키마를 생성합니다.
        
        Args:
            step: API step 정보
            schema_type: "request" 또는 "response"
            
        Returns:
            생성된 스키마 정보
        """
        api = step.get("detail", {}).get("step", {}).get("api", {})
        endpoint = api.get("endpoint", "")
        
        # schema_type에 따라 validation key와 suffix 결정
        if schema_type == "request":
            validation_key = "request"
            suffix = "_in_schema"
        else:  # response
            validation_key = "response"
            suffix = "_out_schema"
        
        validation_data = api.get(validation_key, {})
        # endpoint에서 변수명 생성 (/ 제거, 첫 글자 대문자)
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        schema_name = f"{endpoint}{suffix}"

        # bodyJson이 없으면 빈 딕셔너리 (validation 체크 제거)
        if (not isinstance(validation_data, dict) or
                not isinstance(validation_data.get("bodyJson"), list) or not validation_data["bodyJson"]):
            schema_content = {}
        else:
            # properties가 있으면 각 필드를 변환
            schema_content =self._parse_body_json(validation_data)
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
    

