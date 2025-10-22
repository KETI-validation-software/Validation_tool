# core/semantic_handlers.py
# 임시 더미 파일 -> 추후 분리 여지 가능성!

from typing import Any, Dict, Tuple

# 안 쓰이는중
def handle_request_field_range_match(rule: Dict[str, Any], value: Any, data: Dict[str, Any], reference_context: Dict[str, Any]) -> Tuple[bool, str]:
    # 필요 시 구현 (현재 do_semantic_checker에 직접 구현되어 있는데.. 코드 정리할때 분리할 가능성 농후함 너무 길기 때문..)
    return True, ""
