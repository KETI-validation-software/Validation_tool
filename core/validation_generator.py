"""
ValidationGenerator
- JSON step 구조에서 validation.rule.enabled == True 인 항목만 추출
- type, OptionalKey, children 제거
- 키는 상위~하위 경로를 '.'로 연결해 평탄화
- data_gen 스타일로 Python 코드(True/False, 따옴표 유지)로 저장 가능
"""

from typing import Dict, List, Any

class ValidationGenerator:
    def extract_enabled_validations(self, step: Dict, schema_type: str = "request") -> Dict[str, Any]:
        """
        validation.enabled == True 인 rule만 추출

        Args:
            step (dict): step 구조(JSON). {"step": {...}} 또는 {"detail": {"step": {...}}} 모두 허용
            schema_type (str): "request" | "response"

        Returns:
            dict: {"endpoint": str, "validation": {<dotted_path>: <rule_dict>, ...}}
        """
        step_obj = step.get("detail", {}).get("step") or step.get("step") or step
        api = step_obj.get("api", {}) if isinstance(step_obj, dict) else {}
        endpoint = (api.get("endpoint") or "").lstrip("/")
        data_block = api.get(schema_type, {}) or {}
        validations = data_block.get("validation", []) or []

        result: Dict[str, Any] = {}
        self._collect_enabled(validations, result, prefix="")


        return {"endpoint": endpoint, "validation": result}

    def _collect_enabled(self, nodes: List[Dict[str, Any]], out: Dict[str, Any], prefix: str):
        """재귀적으로 enabled==True 인 validation.rule만 수집"""
        if not isinstance(nodes, list):
            return
        for node in nodes:
            if not isinstance(node, dict):
                continue
            key = node.get("key", "")
            path = f"{prefix}.{key}" if (prefix and key) else (key or prefix)
            rule = node.get("validation", {})
            if isinstance(rule, dict) and rule.get("enabled") is True:
                out[path] = rule
            children = node.get("children", [])
            if children:
                self._collect_enabled(children, out, path)

    def _extract_webhook_validation(self, webhook_spec, parent_key=""):
        """
        webhook spec에서 validation 정보 추출 (재귀적으로 처리)

        Args:
            webhook_spec: webhook의 requestSpec 또는 integrationSpec 배열
            parent_key: 부모 키 (중첩 구조 처리용)

        Returns:
            validation 맵 딕셔너리
        """
        validation_map = {}

        if not webhook_spec or not isinstance(webhook_spec, list):
            return validation_map

        for field in webhook_spec:
            if not isinstance(field, dict):
                continue

            field_key = field.get("key", "")
            field_type = field.get("type", "")
            validation_info = field.get("validation", {})
            children = field.get("children", [])

            # 현재 필드의 전체 키 경로 생성
            if parent_key:
                full_key = f"{parent_key}.{field_key}" if field_key else parent_key
            else:
                full_key = field_key

            # validation이 enabled=True인 경우 추가
            if validation_info and validation_info.get("enabled") == True:
                # validation 정보에서 score 추가 (기본값 0)
                if "score" not in validation_info:
                    validation_info["score"] = 0
                validation_map[full_key] = validation_info

            # array 타입이고 children이 있는 경우 재귀 처리
            if field_type == "array" and children:
                # array의 children 처리
                child_validations = self._extract_webhook_validation(children, full_key)
                validation_map.update(child_validations)

            # object 타입이고 children이 있는 경우 재귀 처리
            elif field_type == "object" and children:
                child_validations = self._extract_webhook_validation(children, full_key)
                validation_map.update(child_validations)

        return validation_map