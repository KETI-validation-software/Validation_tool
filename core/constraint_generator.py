from typing import Any, Dict, List, Union, Optional
from copy import deepcopy

class constraintGeneractor:
    """
    bodyJson 트리에서 valueType이 있는 '영역'만 골라
    점(.) 경로 key로 정리하여 StoredXXX_in_validation 형태의 dict를 생성한다.

    규칙
    - 수집 대상: valueType이 존재하는 dict 노드
    - 제외: 'type', 'value' 키는 수집/병합에서 제외
    - 보존: required, referenceField, requestRange, arrayElementType, valueType 등은 보존
    - 경로: 상위~하위 key를 '.'로 연결(빈 문자열 key는 경로 생략)
    - 기본 템플릿: {"score": 1, "enabled": True, "validationType": "response-field-list-match"}
      → 필요 시 생성자 인자로 커스터마이징 가능
    """

    EXCLUDE_KEYS = {"type", "value"}
    CHILD_KEYS = ("children", "items", "properties", "fields")  # 다양한 스키마 호환

    def __init__(self, default_entry: Optional[Dict[str, Any]] = None):
        self.default_entry = default_entry or {
        }

    def build_validation_map(
        self,
        body_json: Union[List[Any], Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Args:
            body_json: 주신 예시처럼 'bodyJson' 위치의 리스트(또는 dict)
        Returns:
            { "<dotted.path>": {score, enabled, validationType, ...보존필드}, ... }
        """
        acc: Dict[str, Dict[str, Any]] = {}
        self._walk(node=body_json, prefix="", acc=acc)
        return acc

    # -------------------- 내부 구현 -------------------- #

    def _walk(
        self,
        node: Union[List[Any], Dict[str, Any], Any],
        prefix: str,
        acc: Dict[str, Dict[str, Any]],
    ) -> None:
        if node is None:
            return

        if isinstance(node, list):
            for child in node:
                self._walk(child, prefix, acc)
            return

        if not isinstance(node, dict):
            return

        # 경로 계산 (빈 문자열 key는 경로에 포함하지 않음)
        key = node.get("key")
        path = self._join_path(prefix, key)

        # valueType이 있으면 '영역'으로 간주하고 엔트리 생성
        if "valueType" in node:
            entry = self._build_entry(node)
            if entry:  # 빈 dict가 아니면 기록
                acc[path] = entry

        # 하위 노드 순회
        for ck in self.CHILD_KEYS:
            if ck in node and isinstance(node[ck], (list, dict)):
                self._walk(node[ck], path, acc)

    def _build_entry(self, region: Dict[str, Any]) -> Dict[str, Any]:
        # region(dict) 자체에서 보존 필드만 추출
        kept = {}
        for k, v in region.items():
            if k in self.EXCLUDE_KEYS:
                continue
            if k in ("key", *self.CHILD_KEYS):
                continue
            kept[k] = v

        # region 내부에 흔히 쓰는 'data' 블록이 있다면 동일 규칙으로 병합
        data_block = region.get("data")
        if isinstance(data_block, dict):
            for k, v in data_block.items():
                if k in self.EXCLUDE_KEYS:
                    continue
                kept[k] = v

        # 기본 템플릿 + 보존 필드 병합
        entry = deepcopy(self.default_entry)
        entry.update(kept)
        return entry

    @staticmethod
    def _join_path(prefix: str, key: Optional[str]) -> str:
        if not key:
            # 빈 문자열/None은 경로 생략
            return prefix
        return f"{prefix}.{key}" if prefix else key

    def extract_value_type_fields(self, step: Dict[str, Any], schema_type: str = "response") -> Dict[str, Any]:
        step_obj = step.get("detail", {}).get("step") or step.get("step") or step
        api = step_obj.get("api", {}) if isinstance(step_obj, dict) else {}
        endpoint = (api.get("endpoint") or "").lstrip("/")

        if schema_type == "request":
            request_source = api.get("request", {}) or {}
            data_source = request_source
        else:
            response_source = api.get("response", {}) or {}
            data_source = response_source
        data_content = dict(data_source) if isinstance(data_source, dict) else {}

        if isinstance(data_content.get("bodyJson"), list):
            spec_list = data_content["bodyJson"]
        validation_map = self.build_validation_map(spec_list)

        return {"endpoint": endpoint, "validation": validation_map}