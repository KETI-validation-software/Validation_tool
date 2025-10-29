import requests
from json_checker import Checker, OptionalKey
from core.json_checker_new import (
    data_finder, do_checker,
    timeout_field_finder, extract_validation_rules,
    get_flat_fields_from_schema, get_flat_data_from_response
)
from fpdf import FPDF
import sys
import os
import json
from lxml import etree
from PyQt5.QtWidgets import QMessageBox
import json
from datetime import datetime
import uuid
import config.CONSTANTS as CONSTANTS
import re

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ================================================================
# 필드별 순차 검증 (구조 → 의미)
# ================================================================
def json_check_(schema, data, flag, validation_rules=None, reference_context=None):
    """
    각 필드마다 '구조 검증 → 의미 검증'을 순차적으로 수행

    schema: 구조 검증용 응답 스키마
    data:   실제 응답 데이터(dict 권장)
    flag:   옵션(기존 그대로)
    validation_rules: (선택) 의미 검증 규칙 dict
    reference_context: (선택) 다른 엔드포인트 응답 사전

    반환: (result, error_msg, correct_cnt, error_cnt)
    """
    try:

        print("============ 필드별 순차 검증 시작 ============")

        # 1) 필드 목록 및 데이터 추출 (json_checker_new 함수 사용)
        flat_fields, opt_fields = get_flat_fields_from_schema(schema)
        flat_data = get_flat_data_from_response(data)
        print(f"[json_check_] 필드 수: {len(flat_fields)}, 선택 필드: {len(opt_fields)}, 데이터 필드: {len(flat_data)}")

        # 2) 의미 검증 규칙 평탄화
        rules_dict = {}
        if validation_rules:
            if any("." in k for k in validation_rules.keys()):
                rules_dict = validation_rules
            else:
                rules_dict = extract_validation_rules(validation_rules)
            print(f"[json_check_] 의미 검증 규칙 키: {list(rules_dict.keys())}")

        # 3) 필드별 결과 저장
        field_results = {}
        total_correct = 0
        total_error = 0
        error_messages = []

        # 4) 각 필드에 대해 순차 검증
        for field_path in sorted(flat_fields.keys()):
            print(f"\n--- 필드 검증: {field_path} ---")

            field_results[field_path] = {
                "struct_pass": False,
                "semantic_pass": None,  # None: 미수행, True: 통과, False: 실패
                "errors": []
            }

            expected_type = flat_fields[field_path]

            # 4-1) 구조 검증: 필드 존재 여부
            if field_path not in flat_data:
                if field_path not in opt_fields:
                    # 필수 필드 누락
                    error_msg = f"필수 필드 누락: {field_path}"
                    field_results[field_path]["errors"].append(error_msg)
                    error_messages.append(f"[구조] {error_msg}")
                    total_error += 1
                    print(f"  ❌ 구조: 필수 필드 누락")
                    continue
                else:
                    # Optional 필드는 누락 가능 → PASS
                    print(f"  ✅ 구조: Optional 필드 누락 허용")
                    field_results[field_path]["struct_pass"] = True
                    field_results[field_path]["semantic_pass"] = True  # 의미 검증도 자동 PASS
                    total_correct += 1
                    continue

            field_value = flat_data[field_path]

            # 4-2) 구조 검증: 타입 체크 (리스트 내 모든 값 검증 지원)
            is_valid, type_error_msg = _validate_field_type(field_path, field_value, expected_type)

            if not is_valid:
                field_results[field_path]["errors"].append(type_error_msg)
                error_messages.append(f"[구조] {type_error_msg}")
                total_error += 1
                print(f"  ❌ 구조: {type_error_msg}")
                continue  # 구조 실패 시 의미 검증 건너뜀
            else:
                # dict, list인 경우 내부 구조는 최소 검증
                if isinstance(field_value, dict):
                    print(f"  ✅ 구조: dict 타입 검증 통과")
                elif isinstance(field_value, list):
                    # 리스트의 경우 내부 요소들도 검증했으므로
                    if len(field_value) > 0:
                        print(f"  ✅ 구조: list 타입 검증 통과 ({len(field_value)}개 요소 모두 {expected_type.__name__})")
                    else:
                        print(f"  ✅ 구조: 빈 list 검증 통과")
                else:
                    print(f"  ✅ 구조: 타입 일치 ({expected_type.__name__})")
            # 구조 검증 통과
            field_results[field_path]["struct_pass"] = True

            # 4-3) 의미 검증 (구조 통과한 경우에만 수행)
            if field_path not in rules_dict:
                # 의미 검증 규칙 없음 → 자동 PASS
                field_results[field_path]["semantic_pass"] = True
                print(f"  ⊙ 의미: 검증 규칙 없음 (자동 PASS)")
                total_correct += 1  # 구조 + 의미(자동) 통과 → 카운트 1회
                continue

            rule = rules_dict[field_path]

            if not rule.get("enabled", False):
                # 비활성화된 규칙 → 자동 PASS
                field_results[field_path]["semantic_pass"] = True
                print(f"  ⊙ 의미: 규칙 비활성화 (자동 PASS)")
                total_correct += 1  # 구조 + 의미(비활성화) 통과 → 카운트 1회
                continue

            print(f"  → 의미 검증 시작: {rule.get('validationType', 'UNKNOWN')}")

            # 의미 검증 수행
            semantic_pass = _validate_field_semantic(
                field_path, field_value, rule, data, reference_context,
                field_results[field_path]["errors"], error_messages
            )

            field_results[field_path]["semantic_pass"] = semantic_pass

            if semantic_pass:
                total_correct += 1
                print(f"  ✅ 의미: 검증 통과")
            else:
                total_error += 1
                print(f"  ❌ 의미: 검증 실패")

        # 5) 최종 결과 결정
        final_result = "FAIL" if total_error > 0 else "PASS"
        error_msg = "\n".join(error_messages) if error_messages else "오류 없음"

        print(f"\n============ 검증 완료 ============")
        print(f"최종 결과: {final_result}")
        print(f"통과: {total_correct}, 실패: {total_error}")
        print(f"\n필드별 상세 결과:")
        for fp, res in field_results.items():
            struct_icon = "✅" if res["struct_pass"] else "❌"
            sem_icon = "✅" if res["semantic_pass"] is True else ("❌" if res["semantic_pass"] is False else "⊙")
            print(f"  {struct_icon}{sem_icon} {fp}")
            if res["errors"]:
                for err in res["errors"]:
                    print(f"      └─ {err}")

        return final_result, error_msg, total_correct, total_error

    except Exception as e:
        print(f"[json_check_] 에러: {e}")
        import traceback
        traceback.print_exc()
        raise


def _validate_field_type(field_path, field_value, expected_type):
    """
    필드 타입 검증 (리스트 내 모든 값 검증 지원)

    핵심 규칙:
    - 최상위 필드 (경로에 점 없음): 값 자체만 검증
    - 리스트 내부 필드 (경로에 점 있음): 리스트면 모든 요소 검증

    Args:
        field_path: 필드 경로
        field_value: 실제 값 (스칼라 또는 리스트)
        expected_type: 기대하는 타입

    Returns:
        (is_valid: bool, error_msg: str or None)
    """

    # 최상위 필드 판별 (경로에 점이 없음)
    is_top_level = "." not in field_path

    # 최상위 필드: 값 자체만 검증
    if is_top_level:
        if not isinstance(field_value, expected_type):
            error_msg = (
                f"타입 불일치: {field_path} "
                f"(예상: {expected_type.__name__}, "
                f"실제: {type(field_value).__name__})"
            )
            return False, error_msg
        return True, None

    # 리스트 내부 필드: 값이 리스트면 모든 요소 검증
    else:
        if isinstance(field_value, list):
            invalid_items = []

            for i, item in enumerate(field_value):
                if not isinstance(item, expected_type):
                    invalid_items.append(
                        f"[{i}] {item} (타입: {type(item).__name__})"
                    )

            if invalid_items:
                error_msg = (
                    f"타입 불일치: {field_path} - "
                    f"예상: 모든 요소가 {expected_type.__name__}, "
                    f"실패한 항목들: {', '.join(invalid_items)}"
                )
                return False, error_msg

            return True, None

        # 단일 값
        else:
            if not isinstance(field_value, expected_type):
                error_msg = (
                    f"타입 불일치: {field_path} "
                    f"(예상: {expected_type.__name__}, "
                    f"실제: {type(field_value).__name__}, "
                    f"값: {field_value})"
                )
                return False, error_msg

            return True, None


def _validate_field_semantic(field_path, field_value, rule, data, reference_context,
                             field_errors, global_errors):
    """단일 필드의 의미 검증 수행"""
    validation_type = rule.get("validationType")

    if validation_type == "response-field-list-match":
        return _validate_list_match(field_path, field_value, rule, data, reference_context,
                                    field_errors, global_errors)

    elif validation_type == "response-field-match":
        return _validate_field_match(field_path, field_value, rule, reference_context,
                                     field_errors, global_errors)
    
    elif validation_type == "request-field-range-match":
        return _validate_range_match(field_path, field_value, rule, reference_context,
                                     field_errors, global_errors)
    
    elif validation_type == "request-field-list-match":
        return _validate_list_match(field_path, field_value, rule, data, reference_context,
                                    field_errors, global_errors)
    
    elif validation_type == "request-field-match":
        return _validate_field_match(field_path, field_value, rule, reference_context,
                                     field_errors, global_errors)

    elif validation_type == "response-field-range-match":
        return _validate_range_match(field_path, field_value, rule, reference_context,
                                     field_errors, global_errors)
    
    elif validation_type == "valid-value-match":
        return _validate_valid_value_match(field_path, field_value, rule,
                                          field_errors, global_errors)
    
    elif validation_type == "specified-value-match":
        return _validate_specified_value_match(field_path, field_value, rule,
                                               field_errors, global_errors)
    
    elif validation_type == "range-match":
        return _validate_range_match_direct(field_path, field_value, rule,
                                           field_errors, global_errors)
    
    elif validation_type == "length":
        return _validate_length(field_path, field_value, rule,
                               field_errors, global_errors)
    
    elif validation_type == "regex":
        return _validate_regex(field_path, field_value, rule,
                              field_errors, global_errors)
    
    elif validation_type == "required":
        return _validate_required(field_path, field_value, rule,
                                 field_errors, global_errors)
    
    elif validation_type == "unique":
        return _validate_unique(field_path, field_value, rule,
                               field_errors, global_errors)
    
    elif validation_type == "custom":
        return _validate_custom(field_path, field_value, rule,
                               field_errors, global_errors)
    
    else:
        print(f"  ⚠ 미지원 validationType: {validation_type}")
        return True


def _validate_list_match(field_path, field_value, rule, data, reference_context,
                         field_errors, global_errors):
    """리스트 필드의 값들이 참조 리스트에 모두 존재하는지 검증"""
    from core.json_checker_new import collect_all_values_by_key

    ref_endpoint = rule.get("referenceEndpoint")
    ref_list_field = rule.get("referenceListField")

    if not reference_context or ref_endpoint not in reference_context:
        error_msg = f"참조 엔드포인트 없음: {ref_endpoint}"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {error_msg}")
        return False

    ref_data = reference_context[ref_endpoint]

    # collect_all_values_by_key 사용하여 모든 camID 값 수집
    ref_list = collect_all_values_by_key(ref_data, ref_list_field)

    print(f"    참조 리스트 ({ref_list_field}): {ref_list}")

    # 리스트 필드인 경우 (예: camList.camID)
    if "." in field_path:
        parts = field_path.split(".")
        parent_path = ".".join(parts[:-1])
        child_field = parts[-1]

        # 부모 리스트 가져오기
        parent_data = data
        for part in parent_path.split("."):
            if isinstance(parent_data, dict):
                parent_data = parent_data.get(part)
            else:
                break

        if not isinstance(parent_data, list):
            error_msg = f"부모 경로가 리스트가 아님: {parent_path}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {error_msg}")
            return False

        # 각 아이템의 child_field 값 검증
        failed_values = []
        for idx, item in enumerate(parent_data):
            if not isinstance(item, dict):
                continue

            item_value = item.get(child_field)
            if item_value is not None and item_value not in ref_list:
                failed_values.append(f"{item_value} (index {idx})")

        if failed_values:
            error_msg = f"값 불일치: {', '.join(failed_values)}가 {ref_list_field}({ref_list})에 없음"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False

        return True

    # 단일 값 검증
    else:
        if field_value not in ref_list:
            error_msg = f"값 불일치: {field_value}가 {ref_list_field}({ref_list})에 없음"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False

        return True


def _validate_field_match(field_path, field_value, rule, reference_context,
                          field_errors, global_errors):
    """단일 필드 값이 참조 필드 값과 일치하는지 검증"""
    from core.json_checker_new import get_by_path

    ref_endpoint = rule.get("referenceEndpoint")
    ref_field = rule.get("referenceField")

    if not reference_context or ref_endpoint not in reference_context:
        error_msg = f"참조 엔드포인트 없음: {ref_endpoint}"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {error_msg}")
        return False

    ref_data = reference_context[ref_endpoint]
    ref_value = get_by_path(ref_data, ref_field)

    # 보완
    def to_list(v):
        if isinstance(v, list):
            return v
        return [v]
    
    lhs_list = to_list(field_value)
    rhs_list = to_list(ref_value)

    if len(rhs_list) == 1:
        expected = rhs_list[0]
        if not all(item == expected for item in lhs_list):
            error_msg = f"값 불일치: {lhs_list} != 예상값 {expected}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False
        return True
    else:
        if lhs_list != rhs_list:
            error_msg = f"값 불일치: {lhs_list} != {rhs_list}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False
    return True


def _validate_range_match(field_path, field_value, rule, reference_context,
                          field_errors, global_errors):
    """필드 값이 참조 범위 내에 있는지 검증"""
    from core.json_checker_new import collect_all_values_by_key
    
    ref_field_max = rule.get('referenceFieldMax')
    ref_field_min = rule.get('referenceFieldMin')
    ref_endpoint_max = rule.get('referenceEndpointMax')
    ref_endpoint_min = rule.get('referenceEndpointMin')
    ref_operator = rule.get('referenceRangeOperator', 'between')
    
    # ✅ field_value가 리스트인 경우 각 요소를 검증
    if isinstance(field_value, list):
        print(f"  [DEBUG] field_value가 리스트입니다: {field_value}")
        
        if not field_value:
            error_msg = f"빈 리스트: 범위 검증 불가"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False
        
        all_valid = True
        for idx, val in enumerate(field_value):
            if isinstance(val, (int, float)):
                # 각 요소에 대해 범위 검증 수행
                if not _validate_single_value_in_range(
                    field_path, val, ref_endpoint_max, ref_endpoint_min,
                    ref_field_max, ref_field_min, ref_operator,
                    reference_context, field_errors, global_errors, idx
                ):
                    all_valid = False
            else:
                print(f"  [DEBUG] 리스트 요소[{idx}]가 검증 불가능한 타입: {type(val)}")
        
        return all_valid
    
    # ✅ 단일 값인 경우 기존 로직 수행
    return _validate_single_value_in_range(
        field_path, field_value, ref_endpoint_max, ref_endpoint_min,
        ref_field_max, ref_field_min, ref_operator,
        reference_context, field_errors, global_errors
    )


def _validate_single_value_in_range(field_path, field_value, ref_endpoint_max, ref_endpoint_min,
                                     ref_field_max, ref_field_min, ref_operator,
                                     reference_context, field_errors, global_errors, index=None):
    """단일 값에 대한 범위 검증"""
    from core.json_checker_new import collect_all_values_by_key
    
    # 필드명 표시 (리스트 인덱스 포함)
    display_path = f"{field_path}[{index}]" if index is not None else field_path
    
    max_value = None
    min_value = None
    
    # 1) referenceEndpointMax에서 max 값 추출
    if ref_endpoint_max and ref_endpoint_max in reference_context:
        max_data = reference_context[ref_endpoint_max]
        if ref_field_max:
            max_values = collect_all_values_by_key(max_data, ref_field_max)
            if max_values and isinstance(max_values, list) and len(max_values) > 0:
                max_value = max(max_values)
                print(f"  [DEBUG] Max value from {ref_endpoint_max}.{ref_field_max}: {max_value}")
    
    # 2) referenceEndpointMin에서 min 값 추출
    if ref_endpoint_min and ref_endpoint_min in reference_context:
        min_data = reference_context[ref_endpoint_min]
        if ref_field_min:
            min_values = collect_all_values_by_key(min_data, ref_field_min)
            if min_values and isinstance(min_values, list) and len(min_values) > 0:
                min_value = min(min_values)
                print(f"  [DEBUG] Min value from {ref_endpoint_min}.{ref_field_min}: {min_value}")
    
    # 3) range 검증 수행
    if ref_operator == 'between' and min_value is not None and max_value is not None:
        if not (min_value <= field_value <= max_value):
            error_msg = f"범위 초과: {field_value}가 [{min_value}, {max_value}] 범위를 벗어남"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {display_path}: {error_msg}")
            return False
        else:
            print(f"  [DEBUG] ✅ Value {field_value} is between {min_value} and {max_value}")
            return True
    else:
        error_msg = f"범위 검증 실패: min={min_value}, max={max_value}, operator={ref_operator}"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {display_path}: {error_msg}")
        return False


def _validate_valid_value_match(field_path, field_value, rule, field_errors, global_errors):
    """허용된 값 목록과 일치하는지 검증"""
    allowed = rule.get('allowedValues', [])
    operator = rule.get('validValueOperator', 'equalsAny')
    
    if operator == 'equals':
        # 단일 값만 허용 (allowed가 리스트이면 첫 값 기준)
        expected = allowed[0] if allowed else None
        if field_value != expected:
            error_msg = f"값 불일치: {field_value} != 예상값 {expected}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False
    else:  # equalsAny
        if field_value not in allowed:
            error_msg = f"값 불일치: {field_value}가 허용값 목록 {allowed}에 없음"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False
    
    return True


def _validate_specified_value_match(field_path, field_value, rule, field_errors, global_errors):
    """지정된 값과 일치하는지 검증"""
    specified = rule.get('allowedValues', [])
    
    if field_value not in specified:
        error_msg = f"값 불일치: {field_value}가 지정값 {specified}에 없음"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    return True


def _validate_range_match_direct(field_path, field_value, rule, field_errors, global_errors):
    """직접 범위 검증 (reference 없이)"""
    operator = rule.get('rangeOperator')
    min_val = rule.get('rangeMin')
    max_val = rule.get('rangeMax')
    
    # 리스트인 경우 모든 요소 검증
    values = [field_value] if not isinstance(field_value, list) else field_value
    
    for v in values:
        try:
            v_num = float(v)
        except (ValueError, TypeError):
            error_msg = f"숫자 변환 실패: {v}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False
        
        if operator == 'less-than' and max_val is not None:
            if not (v_num < max_val):
                error_msg = f"범위 초과: {v_num} >= {max_val}"
                field_errors.append(error_msg)
                global_errors.append(f"[의미] {field_path}: {error_msg}")
                return False
        
        elif operator == 'less-equal' and max_val is not None:
            if not (v_num <= max_val):
                error_msg = f"범위 초과: {v_num} > {max_val}"
                field_errors.append(error_msg)
                global_errors.append(f"[의미] {field_path}: {error_msg}")
                return False
        
        elif operator == 'between':
            if (min_val is not None and v_num < min_val) or (max_val is not None and v_num > max_val):
                error_msg = f"범위 초과: {v_num}이 [{min_val}, {max_val}] 범위를 벗어남"
                field_errors.append(error_msg)
                global_errors.append(f"[의미] {field_path}: {error_msg}")
                return False
        
        elif operator == 'greater-equal' and min_val is not None:
            if not (v_num >= min_val):
                error_msg = f"범위 미달: {v_num} < {min_val}"
                field_errors.append(error_msg)
                global_errors.append(f"[의미] {field_path}: {error_msg}")
                return False
        
        elif operator == 'greater-than' and min_val is not None:
            if not (v_num > min_val):
                error_msg = f"범위 미달: {v_num} <= {min_val}"
                field_errors.append(error_msg)
                global_errors.append(f"[의미] {field_path}: {error_msg}")
                return False
    
    return True


def _validate_length(field_path, field_value, rule, field_errors, global_errors):
    """길이 검증"""
    min_length = rule.get('minLength')
    max_length = rule.get('maxLength')
    
    # 리스트인 경우 모든 요소 검증
    values = [field_value] if not isinstance(field_value, list) else field_value
    
    for v in values:
        try:
            length = len(v)
        except TypeError:
            error_msg = f"길이 측정 불가: {v}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False
        
        if (min_length is not None and length < min_length) or \
           (max_length is not None and length > max_length):
            error_msg = f"길이 불일치: {length}가 [{min_length}, {max_length}] 범위를 벗어남"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False
    
    return True


def _validate_regex(field_path, field_value, rule, field_errors, global_errors):
    """정규식 검증"""
    pattern = rule.get('pattern')
    
    if pattern is None:
        error_msg = "정규식 패턴이 지정되지 않음"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    # 리스트인 경우 모든 요소 검증
    values = [field_value] if not isinstance(field_value, list) else field_value
    
    try:
        for v in values:
            if re.fullmatch(pattern, str(v)) is None:
                error_msg = f"패턴 불일치: {v}가 패턴 /{pattern}/와 일치하지 않음"
                field_errors.append(error_msg)
                global_errors.append(f"[의미] {field_path}: {error_msg}")
                return False
    except Exception as e:
        error_msg = f"정규식 검증 오류: {e}"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    return True


def _validate_required(field_path, field_value, rule, field_errors, global_errors):
    """필수 필드 검증"""
    # 리스트인 경우 모든 요소 검증
    values = [field_value] if not isinstance(field_value, list) else field_value
    
    if field_value is None or (len(values) == 1 and values[0] in (None, '')):
        error_msg = "필수 필드가 비어있음"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    return True


def _validate_unique(field_path, field_value, rule, field_errors, global_errors):
    """유일성 검증 (리스트 내 중복 체크)"""
    if not isinstance(field_value, list):
        error_msg = "유일성 검증은 리스트에만 적용 가능"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    # 해시 가능한 항목과 불가능한 항목 분리
    hashable_items = []
    unhashable_items = []
    
    for item in field_value:
        try:
            hash(item)
            hashable_items.append(item)
        except TypeError:
            unhashable_items.append(repr(item))
    
    # 해시 가능한 항목 중복 체크
    if hashable_items and len(hashable_items) != len(set(hashable_items)):
        error_msg = "리스트에 중복된 값이 있음"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    # 해시 불가능한 항목 중복 체크 (repr 기반)
    if unhashable_items and len(unhashable_items) != len(set(unhashable_items)):
        error_msg = "리스트에 중복된 복합 객체가 있음"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    return True


def _validate_custom(field_path, field_value, rule, field_errors, global_errors):
    """커스텀 함수 검증"""
    func = rule.get('customFunction')
    
    if not callable(func):
        error_msg = "커스텀 검증 함수가 제공되지 않음"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    try:
        if not func(field_value):
            error_msg = f"커스텀 검증 실패: {field_value}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            return False
    except Exception as e:
        error_msg = f"커스텀 검증 오류: {e}"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    return True


# ================================================================
# 기존 함수들 (수정 없음)
# ================================================================

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def save_result(str_in, path):
    font_file = resource_path('NanumGothic.ttf')
    font_type = 'NanumGothic'
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font(font_type, '', font_file, uni=True)
        pdf.set_font(font_type, '', 10)
        pdf.multi_cell(w=0, h=10, txt=str_in)
        pdf.output(path, 'F')
    except Exception as err:
        print(err)


def set_auth(file=None):
    """CONSTANTS.py에서 인증 정보를 읽어옵니다."""
    try:
        from config.CONSTANTS import auth_type, auth_info
        info = "None"
        info2 = ["", ""]

        if auth_type == "Bearer Token":
            info = auth_info
        elif auth_type == "Digest Auth":
            if "," in auth_info:
                parts = auth_info.split(",")
                info2 = [parts[0], parts[1] if len(parts) > 1 else ""]
            else:
                info2 = [auth_info, ""]

        return info, info2
    except ImportError as e:
        print(f"CONSTANTS.py를 찾을 수 없습니다: {e}")
        return "None", ["", ""]
    except Exception as e:
        print(f"인증 정보 로드 중 오류: {e}")
        return "None", ["", ""]


def set_message(path_):
    try:
        with open(resource_path(path_), 'r', encoding="UTF-8") as fp:
            json_data = json.load(fp)
            message = json_data
        return message
    except json.JSONDecodeError as verr:
        box = QMessageBox()
        box.setIcon(QMessageBox.Critical)
        box.setText("Error Message: " + path_ + " 을 확인하세요")
        box.setInformativeText(str(verr))
        box.setWindowTitle("Error")
        box.exec_()
        return {}
    except Exception as e:
        print(e)
        return {}


def json_to_data(type_):
    def _p(t, name, kind):
        return os.path.join("spec", t, f"{name}_{kind}.json")

    return True


def get_test_group_info():
    """CONSTANTS의 SPEC_CONFIG에서 테스트 그룹 정보 추출"""
    if not CONSTANTS.SPEC_CONFIG:
        return {
            "id": "group-001",
            "name": CONSTANTS.test_target,
            "testRange": CONSTANTS.test_range,
            "testSpecIds": []
        }

    # 첫 번째 그룹 정보 가져오기
    first_group = CONSTANTS.SPEC_CONFIG[0]
    group_id = first_group.get("group_id", "group-001")
    group_name = first_group.get("group_name", CONSTANTS.test_target)

    # 그룹 내 모든 spec ID 수집
    test_spec_ids = []
    for key, value in first_group.items():
        if key not in ["group_name", "group_id"] and isinstance(value, dict):
            test_spec_ids.append(key)

    return {
        "id": group_id,
        "name": group_name,
        "testRange": CONSTANTS.test_range,
        "testSpecIds": test_spec_ids
    }


def get_spec_test_name(spec_id):
    """SPEC_CONFIG에서 spec_id에 해당하는 test_name 가져오기"""
    for group in CONSTANTS.SPEC_CONFIG:
        for key, value in group.items():
            if key == spec_id and isinstance(value, dict):
                return value.get("test_name", spec_id)
    return spec_id


def map_auth_method(auth_type_str):
    """인증 방식 문자열 매핑"""
    auth_map = {
        "Bearer Token": "Bearer Token",
        "Digest Auth": "Digest Auth",
        "None": "None"
    }
    return auth_map.get(auth_type_str, auth_type_str)


def generate_validation_data_from_step_buffer(step_buffer, attempt_num):
    """스텝 버퍼에서 검증 데이터 추출 (raw_data_list 우선 사용)"""
    import re

    validation_data = {}
    validation_errors = []

    if "raw_data_list" in step_buffer and step_buffer["raw_data_list"]:
        raw_data_list = step_buffer["raw_data_list"]
        # attempt_num은 1부터 시작하므로 인덱스는 attempt_num - 1
        if 0 <= attempt_num - 1 < len(raw_data_list):
            validation_data = raw_data_list[attempt_num - 1]
        else:
            validation_data = {}

        # ✅ raw_data_list가 없으면 기존 방식 사용 (하위 호환성)
    elif step_buffer.get("data"):
        data_text = step_buffer["data"]

        # "[시도 n회차]" 패턴으로 분리
        # 패턴: [시도 1회차], [시도 2회차] 등
        pattern = r'\[시도 (\d+)회차\]'
        parts = re.split(pattern, data_text)

        # parts는 [앞부분, '1', 데이터1, '2', 데이터2, ...] 형식
        # 시도 번호와 데이터를 매핑
        attempt_data_map = {}
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                attempt_idx = int(parts[i])
                data_content = parts[i + 1].strip()
                attempt_data_map[attempt_idx] = data_content

        # 현재 attempt_num에 해당하는 데이터 가져오기
        if attempt_num in attempt_data_map:
            raw_data = attempt_data_map[attempt_num]
            try:
                # JSON 파싱 시도
                validation_data = json.loads(raw_data)
            except:
                # JSON 파싱 실패 시 원본 텍스트 그대로 사용
                validation_data = {"raw_data": raw_data}
        else:
            # 해당 시도의 데이터가 없는 경우
            validation_data = {}    # attempt_num은 1부터 시작하므로 인덱스는 attempt_num - 1

    # 에러 메시지 추출 - 시도별로 분리
    if step_buffer.get("error"):
        error_text = step_buffer["error"]

        # 에러도 시도별로 분리
        # 패턴: [검증 n회차] 또는 [시도 n회차]
        error_pattern = r'\[(?:검증|시도) (\d+)회차\]'
        error_parts = re.split(error_pattern, error_text)

        # 에러 메시지 매핑
        attempt_error_map = {}
        for i in range(1, len(error_parts), 2):
            if i + 1 < len(error_parts):
                attempt_idx = int(error_parts[i])
                error_content = error_parts[i + 1].strip()
                if attempt_idx not in attempt_error_map:
                    attempt_error_map[attempt_idx] = []
                if error_content:
                    attempt_error_map[attempt_idx].append(error_content)

        # 현재 attempt_num에 해당하는 에러만 가져오기
        if attempt_num in attempt_error_map:
            validation_errors = attempt_error_map[attempt_num]
        else:
            # 패턴이 없는 경우 전체 에러를 첫 번째 시도에만 할당
            if attempt_num == 1 and not attempt_error_map:
                validation_errors = [line.strip() for line in error_text.split('\n') if line.strip()]

    return {
        "attempt": attempt_num,
        "validationData": validation_data,
        "validationErrors": validation_errors
    }


def build_result_json(myapp_instance):
    """
    MyApp 인스턴스에서 데이터를 추출하여 JSON 형식으로 변환 (CONSTANTS 통합)

    Args:
        myapp_instance: MyApp 클래스의 인스턴스

    Returns:
        dict: JSON 형식의 결과 데이터
    """

    # 1. Request ID 생성 (CONSTANTS에서 가져오거나 신규 생성)
    request_id = CONSTANTS.request_id
    # 2. 평가 대상 정보 (CONSTANTS에서 가져오기)
    evaluation_target = {
        "companyName": CONSTANTS.company_name,
        "contactPerson": CONSTANTS.contact_person,
        "productName": CONSTANTS.product_name,
        "modelName": CONSTANTS.model_name,
        "version": CONSTANTS.version
    }

    # 3. 테스트 그룹 정보 (CONSTANTS.SPEC_CONFIG에서 추출)
    test_group = get_test_group_info()

    # 4. 인증 방식 (CONSTANTS에서 가져오기)
    auth_method = map_auth_method(CONSTANTS.auth_type)

    current_spec_id = myapp_instance.current_spec_id if hasattr(myapp_instance, 'current_spec_id') else None
    api_names_list = []
    api_ids_list = []
    api_endpoints_list = []

    if current_spec_id:
        for group in CONSTANTS.SPEC_CONFIG:
            if current_spec_id in group:
                spec_config = group[current_spec_id]
                api_names_list = spec_config.get('api_name', [])
                api_ids_list = spec_config.get('api_id', [])
                api_endpoints_list = spec_config.get('api_endpoint', [])
                break

    # 5. 테스트 점수 계산
    total_pass = getattr(myapp_instance, 'total_pass_cnt', 0)
    total_error = getattr(myapp_instance, 'total_error_cnt', 0)
    total_fields = total_pass + total_error
    score = (total_pass / total_fields * 100) if total_fields > 0 else 0

    test_score = {
        "score": round(score, 2),
        "totalFields": total_fields,
        "passedFields": total_pass,
        "failedFields": total_error
    }

    # 6. 테스트 결과 상세 정보 구성
    test_result = []
    step_buffers = getattr(myapp_instance, 'step_buffers', [])

    # spec별로 그룹화
    spec_results = {}

    for i, step_buffer in enumerate(step_buffers):
        # 테이블에서 추가 정보 가져오기
        table_widget = myapp_instance.tableWidget
        api_name = table_widget.item(i, 0).text() if table_widget.item(i, 0) else f"API-{i + 1}"
        retries = int(table_widget.item(i, 2).text()) if table_widget.item(i, 2) else 1
        pass_cnt = int(table_widget.item(i, 3).text()) if table_widget.item(i, 3) else 0
        total_cnt = int(table_widget.item(i, 4).text()) if table_widget.item(i, 4) else 0
        fail_cnt = int(table_widget.item(i, 5).text()) if table_widget.item(i, 5) else 0
        api_score_str = table_widget.item(i, 6).text() if table_widget.item(i, 6) else "0%"
        api_score = float(api_score_str.replace('%', ''))

        api_name = api_names_list[i] if i < len(api_names_list) else f"API-{i+1}"
        api_id = api_ids_list[i] if i < len(api_ids_list) else ""
        api_endpoint = api_endpoints_list[i] if i < len(api_endpoints_list) else f"/api{i+1}"

        # API 정보에서 메서드와 엔드포인트 추출
        api_info = step_buffer.get("api_info", {})
        method = api_info.get("method", "POST")
        endpoint = api_info.get("endpoint", api_name)

        # 검증 데이터 생성 (재시도 횟수만큼)
        validations = []
        for attempt in range(1, retries + 1):
            validation = generate_validation_data_from_step_buffer(step_buffer, attempt)
            validations.append(validation)
        # API 결과 구성
        api_result = {
            "id": api_id,
            "name": api_name,
            "method": method,
            "endpoint": api_endpoint,
            "score": round(api_score, 0),
            "validationCnt": retries,
            "totalFields": total_cnt,
            "passFields": pass_cnt,
            "failFields": fail_cnt,
            "validations": validations
        }

        # spec_id 추출 (step_buffer에서 또는 SPEC_CONFIG에서)
        spec_id = step_buffer.get("spec_id")
        if not spec_id and test_group["testSpecIds"]:
            spec_id = test_group["testSpecIds"][0]
        else:
            spec_id = "spec-001"

        if spec_id not in spec_results:
            spec_results[spec_id] = {
                "testSpecId": spec_id,
                "score": 0,
                "apis": []
            }

        spec_results[spec_id]["apis"].append(api_result)

    # spec별 평균 점수 계산
    status = getattr(myapp_instance, 'run_status', 0)
    if status == "진행중":
        test_score = 0.0

    for spec_id, spec_data in spec_results.items():
        if spec_data["apis"]:
            total_pass = sum(api["passFields"] for api in spec_data["apis"])
            total_fields = sum(api["totalFields"] for api in spec_data["apis"])

            if total_fields > 0:
                avg_score = (total_pass / total_fields) * 100
            else:
                avg_score = 0
            if status == "진행중":
                test_score = 0.0
            else :
                spec_data["score"] = round(avg_score, 2)

    test_result = list(spec_results.values())

    # 8. 완료 시간
    completed_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # 최종 JSON 구성
    result_json = {
        "requestId": request_id,
        "evaluationTarget": evaluation_target,
        "testGroup": test_group,
        "status": status,
        "authMethod": auth_method,
        "testScore": test_score,
        "testResult": test_result,
        "completedDate": completed_date
    }

    return result_json


def save_result_json(myapp_instance, output_path="results/validation_result.json"):
    """
    검증 결과를 JSON 파일로 저장

    Args:
        myapp_instance: MyApp 클래스의 인스턴스
        output_path: 저장할 파일 경로

    Returns:
        str: 저장된 파일 경로
    """
    import os

    # 결과 디렉토리 생성
    result_dir = os.path.dirname(output_path)
    if result_dir:
        os.makedirs(result_dir, exist_ok=True)

    # JSON 생성
    result_json = build_result_json(myapp_instance)

    # 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)

    print(f"검증 결과가 '{output_path}'에 저장되었습니다.")
    return output_path