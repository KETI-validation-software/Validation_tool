# core/validation_registry.py
import importlib
import re
from functools import lru_cache
from types import ModuleType
from typing import Dict, Any

# 변수명 규칙: {specId}_{apiName}_{in|out}_validation
_PATTERN = re.compile(r'^(?P<spec>[^_]+)_(?P<api>.+)_(?P<dir>in|out)_validation$')

def _collect_from_module(mod: ModuleType) -> Dict[str, Dict[str, Dict[str, Any]]]:
    registry: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for name, obj in vars(mod).items():
        if not isinstance(name, str):
            continue
        m = _PATTERN.match(name)
        if not m or not isinstance(obj, dict):
            continue
        spec = m.group('spec')
        api  = m.group('api')
        direction = m.group('dir')   # 'in' | 'out'
        reg_spec = registry.setdefault(spec, {})
        reg_dir  = reg_spec.setdefault(direction, {})
        reg_dir[api] = obj
    return registry

@lru_cache(maxsize=16)
def build_validation_registry(
    request_module_path: str = "spec.validation_request",
    response_module_path: str = "spec.validation_response",
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    reg: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for path in (request_module_path, response_module_path):
        try:
            mod = importlib.import_module(path)
        except Exception:
            continue
        part = _collect_from_module(mod)
        for spec, dmap in part.items():
            reg.setdefault(spec, {})
            for direction, amap in dmap.items():
                reg[spec].setdefault(direction, {})
                reg[spec][direction].update(amap)
    return reg

def get_validation_rules(
    spec_id: str,
    api_name: str,
    direction: str,  # 'in' (응답 검증) | 'out' (요청 검증)
    request_module_path: str = "spec.validation_request",
    response_module_path: str = "spec.validation_response",
) -> Dict[str, Any]:
    """
    검증 규칙 반환
    
    Args:
        spec_id: 스펙 ID
        api_name: API 이름
        direction: 
            - "out": 플랫폼이 시스템 요청 검증 (validation_request 사용)
            - "in": 시스템이 플랫폼 응답 검증 (validation_response 사용)
    """
    direction = direction.lower().strip()
    if direction not in ("in", "out"):
        raise ValueError("direction must be 'in' or 'out'")
    reg = build_validation_registry(request_module_path, response_module_path)
    print(f"[DEBUG][registry] 전체 spec_id: {list(reg.keys())}")
    print(f"[DEBUG][registry] {spec_id}의 direction 목록: {list(reg.get(spec_id, {}).keys())}")
    print(f"[DEBUG][registry] {spec_id}의 {direction}의 api 목록: {list(reg.get(spec_id, {}).get(direction, {}).keys())}")
    print(f"[DEBUG][registry] 조회 spec_id: {spec_id}, api_name: {api_name}, direction: {direction}")
    return reg.get(spec_id, {}).get(direction, {}).get(api_name, {}) or {}
