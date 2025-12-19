# data.py
from typing import Dict, List, Any, Union


class dataGenerator:
    """key/type/value 규격 스펙을 실제 JSON 데이터로 변환하는 클래스"""

    def __init__(self):
        pass

    def extract_endpoint_data(self, step: Dict, data_type: str) -> Dict[str, Any]:
        """
        엔드포인트 스텝에서 request/response 데이터를 추출하고,
        bodyJson 스펙이 있으면 실제 JSON 데이터로 변환
        """
        api = step.get("detail", {}).get("step", {}).get("api", {})
        endpoint = api.get("endpoint", "")
        endpoint_name = endpoint[1:] if endpoint.startswith("/") else endpoint

        request_source = api.get("request", {}) or {}
        response_source = api.get("response", {}) or {}

        if data_type == "request":
            data_source = request_source
            suffix = "_in_data"
        else:
            data_source = response_source
            suffix = "_out_data"

        variable_name = f"{endpoint_name}{suffix}"
        data_content = dict(data_source) if isinstance(data_source, dict) else {}

        # ✅ bodyJson이 key/type/value 구조라면 실제 데이터로 변환
        if isinstance(data_content.get("bodyJson"), list):
            spec_list = data_content["bodyJson"]
            data_content = self.build_data_from_spec(spec_list)
        else:
            pass  # bodyJson이 없으면 그대로 유지

        return {
            "name": variable_name,
            "content": data_content,
            "endpoint": endpoint_name
        }

    # -----------------------------
    # 스펙 → 데이터 생성기
    # -----------------------------
    def build_data_from_spec(self, spec_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        key/type/value/children 기반 스펙 리스트를 실제 JSON(dict) 데이터로 변환
        """
        result: Dict[str, Any] = {}
        for item in spec_list:
            if not isinstance(item, dict):
                continue

            key = item.get("key", "")
            t = (item.get("type") or "string").lower()
            required = bool(item.get("required", False))
            value = item.get("value", None)
            children = item.get("children", None)
            array_elem_type = (item.get("arrayElementType") or "").lower()

            if t == "object":
                obj = self._build_object_from_children(children, required)
                if key:
                    result[key] = obj
                continue

            if t == "array":
                arr = self._build_array_from_spec(value, array_elem_type, children, required)
                if key:
                    result[key] = arr
                continue

            coerced = self._coerce_primitive(value, t, required)
            if key:
                result[key] = coerced

        return result

    def _build_object_from_children(self, children: Any, required: bool) -> Dict[str, Any]:
        if not isinstance(children, list):
            return {} if required else {}
        obj: Dict[str, Any] = {}
        for child in children:
            if not isinstance(child, dict):
                continue
            k = child.get("key", "")
            t = (child.get("type") or "string").lower()
            v = child.get("value", None)
            req = bool(child.get("required", False))
            sub_children = child.get("children", None)

            if t == "object":
                obj_val = self._build_object_from_children(sub_children, req)
                if k:
                    obj[k] = obj_val
                else:
                    # ✅ key가 빈 object면 내부를 상위에 병합
                    if isinstance(obj_val, dict):
                        obj.update(obj_val)
                continue

            if t == "array":
                obj_val = self._build_array_from_spec(
                    child.get("value", None),
                    (child.get("arrayElementType") or "").lower(),
                    sub_children,
                    req
                )
                if k:
                    obj[k] = obj_val
                # k가 빈 배열은 보통 정의용이므로 무시
                continue

            obj_val = self._coerce_primitive(v, t, req)
            if k:
                obj[k] = obj_val
        return obj

    def _build_array_from_spec(
            self,
            value: Any,
            array_elem_type: str,
            children: Any,
            required: bool
    ) -> List[Any]:
        # ✅ object 배열 처리 강화
        if array_elem_type == "object" and isinstance(children, list):
            # (A) children에 여러 개의 object 항목이 이미 "나열"되어 있는 경우
            object_items = [
                c for c in children
                if isinstance(c, dict) and (c.get("type", "").lower() == "object")
            ]
            if len(object_items) > 1:
                result = []
                for c in object_items:
                    sub_children = c.get("children")

                    # unwrap: "children=[{key:'', type:'object', children:[...]}]" 형태 방어
                    if (isinstance(sub_children, list) and len(sub_children) == 1 and
                            isinstance(sub_children[0], dict) and
                            sub_children[0].get("type", "").lower() == "object" and
                            sub_children[0].get("key", "") == "" and
                            isinstance(sub_children[0].get("children"), list)):
                        sub_children = sub_children[0]["children"]

                    obj = self._build_object_from_children(sub_children, required=True)
                    result.append(obj)
                return result

            # (B) 기존 로직: 템플릿 1개인 경우 한 개 객체로 리스트 구성
            real_children = children
            if len(children) == 1 and isinstance(children[0], dict):
                c0 = children[0]
                if (c0.get("type", "").lower() == "object") and (c0.get("key", "") == "") and isinstance(
                        c0.get("children"), list):
                    real_children = c0["children"]
            obj = self._build_object_from_children(real_children, required=True)
            return [obj]

        # ✅ primitive 배열(string, number 등)인데 children에 값이 있는 경우 처리
        if array_elem_type != "object" and isinstance(children, list) and children:
            result = []
            for child in children:
                if isinstance(child, dict):
                    child_value = child.get("value")
                    if child_value is not None and child_value != "":
                        result.append(child_value)
            if result:
                return result

        # ✅ value 기반 처리 (primitive/문자열 리스트)
        if value is None or value == "":
            return [] if required else []

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            parts = [p.strip() for p in value.split(",") if p.strip() != ""]
            return parts

        return [value]

    def _coerce_primitive(self, value: Any, t: str, required: bool) -> Any:
        """string/number/boolean 등 기본 타입 처리"""
        if value in (None, ""):
            default_map = {
                "string": "",
                "number": 0,
                "integer": 0,
                "float": 0.0,
                "boolean": False,
            }
            return default_map.get(t, "")

        try:
            if t == "string":
                return str(value)
            if t in ("number", "integer", "float"):
                if isinstance(value, (int, float)):
                    return value
                s = str(value).strip()
                return float(s) if "." in s else int(s)
            if t == "boolean":
                if isinstance(value, bool):
                    return value
                s = str(value).strip().lower()
                return s in ("true", "1", "yes", "y")
        except Exception:
            return "" if t == "string" else (0 if t in ("number", "integer", "float") else False)

        return str(value)

    def format_data_content(self, content: Union[Dict, List, str, int, float, bool]) -> str:
        """데이터 내용을 Python 코드 문자열로 포맷팅합니다."""
        if isinstance(content, dict):
            if not content:
                return "{}"

            lines = ["{"]
            items = list(content.items())
            for i, (key, value) in enumerate(items):
                formatted_value = self.format_data_content(value)
                comma = "," if i < len(items) - 1 else ""
                lines.append(f'    "{key}": {formatted_value}{comma}')
            lines.append("}")
            return "\n".join(lines)

        elif isinstance(content, list):
            if not content:
                return "[]"

            lines = ["["]
            for i, item in enumerate(content):
                formatted_item = self.format_data_content(item)
                comma = "," if i < len(content) - 1 else ""
                # 들여쓰기 추가
                if "\n" in formatted_item:
                    indented_item = "\n".join("    " + line for line in formatted_item.split("\n"))
                    lines.append(f"    {indented_item}{comma}")
                else:
                    lines.append(f"    {formatted_item}{comma}")
            lines.append("]")
            return "\n".join(lines)

        elif isinstance(content, str):
            return f'"{content}"'
        elif isinstance(content, (int, float)):
            return str(content)
        elif isinstance(content, bool):
            return "True" if content else "False"
        else:
            return f'"{str(content)}"'