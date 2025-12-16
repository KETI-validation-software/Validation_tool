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
import cv2

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ================================================================
# 오류 메시지 트리 구조 포매팅
# ================================================================
def format_errors_as_tree(error_messages):
    """
    검증 오류 메시지를 트리 구조로 포매팅
    
    입력 예시:
    [
        "[구조] 타입 불일치: doorList.bioDeviceList - 예상: 모든 요소가 list, 실패한 항목들: [0] {...} (타입: dict)",
        "[구조] 필수 필드 누락: doorList.bioDeviceList.bioDeviceAuthTypeList[]"
    ]
    
    출력 예시:
    ▼ [doorList.bioDeviceList] (2건)
        ├── [X] [타입 오류] index[0] : List가 와야 하는데 Dict가 왔습니다.
        └── [!] [필드 누락] bioDeviceAuthTypeList[]
    """
    if not error_messages:
        return "오류가 없습니다."
    
    # 1. 오류 메시지를 파싱하여 계층 구조로 그룹화
    error_tree = {}
    
    for error_msg in error_messages:
        # [구조] 또는 [의미] 제거
        msg = error_msg.replace("[구조] ", "").replace("[의미] ", "")
        
        # 오류 타입과 필드 경로 파싱
        if "타입 불일치:" in msg:
            error_type = "타입 오류"
            field_info = msg.split("타입 불일치:")[1].strip()
            
            # 필드 경로 추출 (- 이전까지)
            if " - " in field_info:
                field_path = field_info.split(" - ")[0].strip()
                detail = field_info.split(" - ", 1)[1].strip()
            else:
                field_path = field_info.split("(")[0].strip()
                detail = field_info
            
            # 그룹핑 키: 필드 경로 자체
            parent_path = field_path
            
            # 인덱스 정보 파싱
            if "실패한 항목들:" in detail:
                items_str = detail.split("실패한 항목들:")[1].strip()
                # [0] {...} (타입: dict), [1] {...} (타입: dict) 형식 파싱
                matches = re.findall(r'\[(\d+)\].*?\(타입: (\w+)\)', items_str)
                
                if parent_path not in error_tree:
                    error_tree[parent_path] = []
                
                for idx, actual_type in matches:
                    # 예상 타입 추출
                    expected_match = re.search(r'예상: 모든 요소가 (\w+)', detail)
                    expected_type = expected_match.group(1) if expected_match else "List"
                    
                    error_tree[parent_path].append({
                        "type": error_type,
                        "detail": f"index[{idx}] : {expected_type.capitalize()}가 와야 하는데 {actual_type.capitalize()}가 왔습니다."
                    })
            else:
                # 단일 타입 오류
                if parent_path not in error_tree:
                    error_tree[parent_path] = []
                
                # 예상/실제 타입 추출
                expected_match = re.search(r'예상: (\w+)', detail)
                actual_match = re.search(r'실제: (\w+)', detail)
                
                expected = expected_match.group(1) if expected_match else "?"
                actual = actual_match.group(1) if actual_match else "?"
                
                # 필드명만 표시
                field_name = field_path.split(".")[-1] if "." in field_path else field_path
                
                error_tree[parent_path].append({
                    "type": error_type,
                    "detail": f"{field_name} : {expected.capitalize()}가 와야 하는데 {actual.capitalize()}가 왔습니다."
                })
        
        elif "필수 필드 누락:" in msg or "선택 필드 누락:" in msg:
            error_type = "필드 누락"
            field_path = msg.split("필드 누락:")[1].strip()
            
            # 상위 경로 추출
            if "." in field_path:
                parent_path = ".".join(field_path.split(".")[:-1])
                field_name = field_path.split(".")[-1]
            else:
                parent_path = "최상위"
                field_name = field_path
            
            if parent_path not in error_tree:
                error_tree[parent_path] = []
            
            error_tree[parent_path].append({
                "type": error_type,
                "detail": field_name
            })
        
        else:
            # 기타 오류 (의미 검증 등) - 최상위 필드는 그룹핑하지 않음
            # 필드명 추출 시도
            field_match = re.match(r'^(\w+):', msg)
            if field_match:
                field_name = field_match.group(1)
                # 최상위 필드로 직접 저장 (점이 없는 경우)
                parent_path = "__top_level__"  # 특수 키로 최상위 표시
            else:
                parent_path = "기타"
            
            if parent_path not in error_tree:
                error_tree[parent_path] = []
            
            error_tree[parent_path].append({
                "type": "맥락 오류",
                "detail": msg
            })
    
    # 2. 트리 구조로 포매팅
    result_lines = []
    
    # 최상위 레벨 오류 먼저 처리 (그룹핑 없이)
    if "__top_level__" in error_tree:
        top_errors = error_tree.pop("__top_level__")
        for error in top_errors:
            result_lines.append(f"- [{error['type']}] {error['detail']}")
        # 최상위 오류 뒤에 빈 줄 추가 (다른 그룹이 있을 경우)
        if error_tree:
            result_lines.append("")
    
    # 나머지 그룹화된 오류들 처리
    for idx, (parent_path, errors) in enumerate(sorted(error_tree.items())):
        # 그룹 헤더 - 필드 경로를 진하게 표시
        error_count = len(errors)
        result_lines.append(f"<b>[{parent_path}]</b> ({error_count}건)")
        
        # 각 오류 출력 (들여쓰기 유지)
        for error in errors:
            result_lines.append(f"- [{error['type']}] {error['detail']}")
        
        # 마지막 그룹이 아니면 빈 줄 추가
        if idx < len(error_tree) - 1:
            result_lines.append("")
    
    return "\n".join(result_lines)


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
        
        # ✅ 디버그: primitive 배열 필드 확인
        for field_path in flat_fields.keys():
            if field_path.endswith("[]"):
                print(f"[DEBUG] 스키마에 primitive 배열 필드 발견: {field_path} -> {flat_fields[field_path]}")
        
        for field_path in flat_data.keys():
            if field_path.endswith("[]"):
                print(f"[DEBUG] 데이터에 primitive 배열 필드 발견: {field_path} -> {flat_data[field_path]}")


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
        context_validation_failed = False
        code_message_error = None

        # code와 message 필드의 맥락 검증 수행
        for field_name in ['code', 'message']:
            if field_name in flat_data and field_name in rules_dict:
                rule = rules_dict[field_name]

                print(f"\n[맥락검증] {field_name} 필드 검증 시작")
                print(f"[맥락검증] rule: {rule}")

                if not rule.get("enabled", False):
                    print(f"[맥락검증] {field_name} 규칙이 비활성화됨 - 건너뜀")
                    continue

                validation_type = rule.get("validationType")
                print(f"[맥락검증] validationType: {validation_type}")

                if validation_type != "specified-value-match":
                    print(f"[맥락검증] {field_name}은 specified-value-match가 아님 - 건너뜀")
                    continue

                actual_value = flat_data[field_name]

                # ===================================================================
                # allowedValues에서 예상값 추출
                # ===================================================================
                allowed_values = rule.get("allowedValues", [])
                print(f"[맥락검증] allowedValues: {allowed_values}")

                if not allowed_values or len(allowed_values) == 0:
                    print(f"[경고] {field_name}의 allowedValues가 비어있음 - 맥락 검증 건너뜀")
                    continue

                # 단일 값만 허용하는 경우에만 맥락 검증 수행
                if len(allowed_values) > 1:
                    print(f"[맥락검증] {field_name}이 여러 값을 허용 ({allowed_values}) - 맥락 검증 건너뜀")
                    continue

                expected_value = allowed_values[0]
                print(f"[맥락검증] expected_value: {expected_value} (type: {type(expected_value).__name__})")
                print(f"[맥락검증] actual_value: {actual_value} (type: {type(actual_value).__name__})")

                # ===================================================================
                # 맥락 검증 수행 (타입 안전한 비교)
                # ===================================================================

                # 타입 통일 (문자열 "400" vs 숫자 400 비교 문제 방지)
                try:
                    # 숫자로 변환 시도
                    if isinstance(expected_value, str) and expected_value.isdigit():
                        expected_num = int(expected_value)
                    elif isinstance(expected_value, (int, float)):
                        expected_num = int(expected_value)
                    else:
                        # 숫자가 아닌 경우 (message 필드 등)
                        expected_num = None

                    if isinstance(actual_value, str) and actual_value.isdigit():
                        actual_num = int(actual_value)
                    elif isinstance(actual_value, (int, float)):
                        actual_num = int(actual_value)
                    else:
                        actual_num = None

                    print(f"[맥락검증] 변환 후 - expected_num: {expected_num}, actual_num: {actual_num}")

                    # 숫자 비교가 가능한 경우
                    if expected_num is not None and actual_num is not None:
                        # 200이 아닌 값을 기대하는데 실제로 다른 값이 온 경우
                        if expected_num != 200 and actual_num != expected_num:
                            context_validation_failed = True
                            code_message_error = f"{field_name} 맥락 검증 실패: 예상값 {expected_num}, 실제값 {actual_num}"
                            error_messages.append(f"[의미] {code_message_error}")
                            print(f"  ❌ 맥락 검증 실패: {code_message_error}")
                            print(f"  ⚠️ 모든 필드를 실패로 처리합니다.")
                            break
                        else:
                            print(f"[맥락검증] ✅ {field_name} 숫자 검증 통과")

                    # 문자열 비교 (message 필드 등)
                    else:
                        expected_str = str(expected_value)
                        actual_str = str(actual_value)

                        # "200" 또는 200이 아닌 값을 기대하는 경우
                        if expected_str not in ["200", "OK", "Success"] and actual_str != expected_str:
                            context_validation_failed = True
                            code_message_error = f"{field_name} 맥락 검증 실패: 예상값 '{expected_str}', 실제값 '{actual_str}'"
                            error_messages.append(f"[의미] {code_message_error}")
                            print(f"  ❌ 맥락 검증 실패: {code_message_error}")
                            print(f"  ⚠️ 모든 필드를 실패로 처리합니다.")
                            break
                        else:
                            print(f"[맥락검증] ✅ {field_name} 문자열 검증 통과")

                except Exception as e:
                    print(f"[경고] {field_name} 맥락 검증 중 예외 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

        print(f"\n[맥락검증] 최종 결과: {'실패' if context_validation_failed else '통과'}")

        # ===================================================================
        # 맥락 검증 실패 시 모든 필드를 실패로 카운트
        # ===================================================================
        if context_validation_failed:
            total_error = len(flat_fields)
            total_correct = 0

            # 모든 필드에 대해 실패 상태 기록
            for field_path in flat_fields.keys():
                field_results[field_path] = {
                    "struct_pass": False,
                    "semantic_pass": False,
                    "errors": [code_message_error]
                }

            # 최종 결과 반환 (모든 필드 실패)
            final_result = "FAIL"
            error_msg = format_errors_as_tree(error_messages)

            print(f"\n============ 맥락 검증 실패로 조기 종료 ============")
            print(f"최종 결과: {final_result}")
            print(f"통과: {total_correct}, 실패: {total_error}")

            return final_result, error_msg, total_correct, total_error
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

                if CONSTANTS.flag_opt:
                    if field_path not in opt_fields:
                        # 필수 필드 누락
                        error_msg = f"필수 필드 누락: {field_path}"
                        field_results[field_path]["errors"].append(error_msg)
                        error_messages.append(f"[구조] {error_msg}")
                        total_error += 1
                        print(f"  ❌ 구조: 필수 필드 누락")
                        continue
                    else:
                        error_msg = f"선택 필드 누락: {field_path}"
                        field_results[field_path]["errors"].append(error_msg)
                        error_messages.append(f"[구조] {error_msg}")
                        total_error += 1
                        print(f"  ❌ 구조: 선택 필드 누락")
                        continue
                else:
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
        
        # ✅ 오류 메시지를 트리 구조로 포매팅
        if error_messages:
            error_msg = format_errors_as_tree(error_messages)
        else:
            error_msg = "오류가 없습니다."

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
    - Primitive 배열 (경로가 []로 끝남): 배열의 각 요소가 expected_type인지 검증
    - 리스트 내부 필드 (경로에 점 있음): 리스트면 모든 요소 검증

    Args:
        field_path: 필드 경로
        field_value: 실제 값 (스칼라 또는 리스트)
        expected_type: 기대하는 타입

    Returns:
        (is_valid: bool, error_msg: str or None)
    """

    # ✅ 숫자 타입 통합 검증 함수 추가
    def is_numeric_type_match(value, expected):
        """int 또는 float가 예상될 때 둘 다 허용"""
        if expected in (int, float):
            return isinstance(value, (int, float))
        return isinstance(value, expected)

    # ✅ 타입명 표시 함수 추가
    def get_type_name(type_obj):
        """int/float는 'number'로 표시"""
        if type_obj in (int, float):
            return "number"
        return type_obj.__name__

    # ✅ 새로 추가: Primitive 타입 배열 처리 (예: bioDeviceAuthTypeList[] → str)
    # 필드 경로가 []로 끝나면 "문자열 배열" 같은 primitive 배열을 의미
    if field_path.endswith("[]"):
        # 실제 필드명 ([] 제거)
        actual_field = field_path[:-2]

        # 값이 리스트인지 확인
        if not isinstance(field_value, list):
            error_msg = (
                f"타입 불일치: {actual_field} "
                f"(예상: {get_type_name(expected_type)} 배열, "
                f"실제: {type(field_value).__name__})"
            )
            return False, error_msg

        # 배열의 각 요소가 expected_type인지 검증
        invalid_items = []
        for i, item in enumerate(field_value):
            if not is_numeric_type_match(item, expected_type):
                invalid_items.append(
                    f"[{i}] {item} (타입: {get_type_name(type(item))})"
                )

        if invalid_items:
            error_msg = (
                f"타입 불일치: {actual_field} - "
                f"예상: 모든 요소가 {get_type_name(expected_type)}, "
                f"실패한 항목들: {', '.join(invalid_items)}"
            )
            return False, error_msg

        return True, None

    # 최상위 필드 판별 (경로에 점이 없음)
    is_top_level = "." not in field_path

    # 최상위 필드: 값 자체만 검증
    if is_top_level:
        if not is_numeric_type_match(field_value, expected_type):
            error_msg = (
                f"타입 불일치: {field_path} "
                f"(예상: {get_type_name(expected_type)}, "
                f"실제: {get_type_name(type(field_value))})"
            )
            return False, error_msg
        return True, None

    # 리스트 내부 필드: 값이 리스트면 모든 요소 검증
    else:
        if isinstance(field_value, list):
            invalid_items = []

            for i, item in enumerate(field_value):
                if not is_numeric_type_match(item, expected_type):
                    invalid_items.append(
                        f"[{i}] {item} (타입: {get_type_name(type(item))})"
                    )

            if invalid_items:
                error_msg = (
                    f"타입 불일치: {field_path} - "
                    f"예상: 모든 요소가 {get_type_name(expected_type)}, "
                    f"실패한 항목들: {', '.join(invalid_items)}"
                )
                return False, error_msg

            return True, None

        # 단일 값
        else:
            if not is_numeric_type_match(field_value, expected_type):
                error_msg = (
                    f"타입 불일치: {field_path} "
                    f"(예상: {get_type_name(expected_type)}, "
                    f"실제: {get_type_name(type(field_value))}, "
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


    elif validation_type == "url-video":
        return _validate_url_video(field_path, field_value, rule, reference_context,
                                   field_errors, global_errors)
    
    elif validation_type == "array-validation":
        return _validate_array(field_path, field_value, rule, data, reference_context,
                              field_errors, global_errors)
    
    elif validation_type == "object-validation":
        return _validate_object(field_path, field_value, rule, data, reference_context,
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

    print(f"[DEBUG][VALIDATE] field_path: {field_path}, field_value: {field_value}")
    print(f"[DEBUG][VALIDATE] ref_endpoint: {ref_endpoint}, ref_field: {ref_field}")
    print(f"[DEBUG][VALIDATE] reference_context keys: {list(reference_context.keys()) if reference_context else None}")
    print(f"[DEBUG][VALIDATE] reference_context: {reference_context}")

    if not reference_context or ref_endpoint not in reference_context:
        error_msg = f"참조 엔드포인트 없음: {ref_endpoint}"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {error_msg}")
        return False

    ref_data = reference_context[ref_endpoint]
    print(f"[DEBUG][VALIDATE] ref_data: {ref_data}")
    ref_value = get_by_path(ref_data, ref_field)
    
    # ref_value가 None이면 배열 필드 안을 자동 탐색
    if ref_value is None:
        print(f"[DEBUG][VALIDATE] ref_field '{ref_field}' not found, searching in arrays...")
        for key, value in ref_data.items():
            if isinstance(value, list) and value:
                # 배열 안의 객체에서 ref_field 찾기
                array_path = f"{key}.{ref_field}"
                ref_value = get_by_path(ref_data, array_path)
                print(f"[DEBUG][VALIDATE] Tried array_path: {array_path}, result: {ref_value}")
                if ref_value is not None:
                    break

    print(f"[DEBUG][VALIDATE] Final ref_value: {ref_value}")

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


def _validate_array(field_path, field_value, rule, data, reference_context,
                    field_errors, global_errors):
    """배열 검증 (array-validation)"""
    if not isinstance(field_value, list):
        error_msg = f"배열이 아님 (타입: {type(field_value).__name__})"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    all_valid = True
    
    # 1. arrayConstraints 검증 (minItems, maxItems)
    array_constraints = rule.get("arrayConstraints", {})
    if array_constraints:
        min_items = array_constraints.get("minItems")
        max_items = array_constraints.get("maxItems")
        
        if min_items is not None and len(field_value) < min_items:
            error_msg = f"배열 최소 길이 미달: {len(field_value)} < {min_items}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            all_valid = False
        
        if max_items is not None and len(field_value) > max_items:
            error_msg = f"배열 최대 길이 초과: {len(field_value)} > {max_items}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}: {error_msg}")
            all_valid = False
    
    # 2. arrayItemValidation 검증 (배열 요소 개별 검증)
    array_item_validation = rule.get("arrayItemValidation")
    if array_item_validation:
        for idx, item in enumerate(field_value):
            item_path = f"{field_path}[{idx}]"
            item_valid = _validate_field_semantic(
                item_path, item, array_item_validation, data, reference_context,
                field_errors, global_errors
            )
            if not item_valid:
                all_valid = False
    
    # 3. arrayItemSchema 검증 (객체 배열 스키마 검증)
    array_item_schema = rule.get("arrayItemSchema")
    if array_item_schema:
        for idx, item in enumerate(field_value):
            if not isinstance(item, dict):
                error_msg = f"배열 요소가 객체가 아님 (index {idx}, 타입: {type(item).__name__})"
                field_errors.append(error_msg)
                global_errors.append(f"[의미] {field_path}[{idx}]: {error_msg}")
                all_valid = False
                continue
            
            # 각 필드 스키마에 대해 검증
            for field_schema in array_item_schema:
                field_key = field_schema.get("key")
                field_validation = field_schema.get("validation", {})
                
                if not field_validation.get("enabled", False):
                    continue
                
                item_field_path = f"{field_path}[{idx}].{field_key}"
                item_field_value = item.get(field_key)
                
                # children이 있으면 object-validation 처리
                if field_schema.get("children"):
                    child_rule = {
                        "validationType": "object-validation",
                        "enabled": field_validation.get("enabled", True),
                        "children": field_schema.get("children")
                    }
                    child_valid = _validate_object(
                        item_field_path, item_field_value, child_rule, data, reference_context,
                        field_errors, global_errors
                    )
                    if not child_valid:
                        all_valid = False
                else:
                    # 일반 필드 검증
                    field_valid = _validate_field_semantic(
                        item_field_path, item_field_value, field_validation, 
                        data, reference_context, field_errors, global_errors
                    )
                    if not field_valid:
                        all_valid = False
    
    return all_valid


def _validate_object(field_path, field_value, rule, data, reference_context,
                     field_errors, global_errors):
    """객체 검증 (object-validation)"""
    if not isinstance(field_value, dict):
        error_msg = f"객체가 아님 (타입: {type(field_value).__name__})"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False
    
    all_valid = True
    
    # children 필드 검증
    children = rule.get("children", [])
    for child_schema in children:
        child_key = child_schema.get("key")
        child_validation = child_schema.get("validation", {})
        
        if not child_validation.get("enabled", False):
            continue
        
        child_path = f"{field_path}.{child_key}"
        child_value = field_value.get(child_key)
        
        # 중첩 객체 처리
        if child_schema.get("children"):
            nested_rule = {
                "validationType": "object-validation",
                "enabled": child_validation.get("enabled", True),
                "children": child_schema.get("children")
            }
            child_valid = _validate_object(
                child_path, child_value, nested_rule, data, reference_context,
                field_errors, global_errors
            )
            if not child_valid:
                all_valid = False
        else:
            # 일반 필드 검증
            child_valid = _validate_field_semantic(
                child_path, child_value, child_validation, data, reference_context,
                field_errors, global_errors
            )
            if not child_valid:
                all_valid = False
    
    return all_valid


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


def get_test_groups_info():
    """CONSTANTS의 SPEC_CONFIG에서 모든 테스트 그룹 정보 추출 (배열 반환)"""
    if not CONSTANTS.SPEC_CONFIG:
        return [{
            "id": "group-001",
            "name": CONSTANTS.test_target,
            "testRange": CONSTANTS.test_range,
            "testSpecIds": []
        }]

    # 모든 그룹을 순회하면서 배열로 반환
    test_groups = []
    for group in CONSTANTS.SPEC_CONFIG:
        group_id = group.get("group_id", "group-001")
        group_name = group.get("group_name", CONSTANTS.test_target)

        # 그룹 내 모든 spec ID 수집
        test_spec_ids = []
        for key, value in group.items():
            if key not in ["group_name", "group_id"] and isinstance(value, dict):
                test_spec_ids.append(key)

        # testRange는 testSpecIds 개수에 맞춰 생성
        test_range = ", ".join(["ALL_FIELDS"] * len(test_spec_ids))

        test_groups.append({
            "id": group_id,
            "name": group_name,
            "testRange": test_range,
            "testSpecIds": test_spec_ids
        })

    return test_groups


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
    """
    스텝 버퍼에서 검증 데이터 추출 (raw_data_list 우선 사용)

    Args:
        step_buffer: 스텝 버퍼 딕셔너리
        attempt_num: 시도 번호 (1부터 시작)

    Returns:
        dict: {
            "attempt": attempt_num,
            "validationData": {...},
            "validationErrors": [...]
        }
    """
    import re

    validation_data = {}
    validation_errors = []

    # 1. raw_data_list에서 데이터 추출 (우선순위 1)
    if "raw_data_list" in step_buffer and step_buffer["raw_data_list"]:
        raw_data_list = step_buffer["raw_data_list"]
        # attempt_num은 1부터 시작하므로 인덱스는 attempt_num - 1
        if 0 <= attempt_num - 1 < len(raw_data_list):
            validation_data = raw_data_list[attempt_num - 1]
        else:
            validation_data = {}

    # 2. data 텍스트에서 파싱 (raw_data_list가 없는 경우)
    elif step_buffer.get("data"):
        data_text = step_buffer["data"]

        # "[시도 n회차]" 패턴으로 분리
        pattern = r'\[시도 (\d+)회차\]'
        parts = re.split(pattern, data_text)

        # parts는 [앞부분, '1', 데이터1, '2', 데이터2, ...] 형식
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
                validation_data = json.loads(raw_data)
            except:
                validation_data = {"raw_data": raw_data}
        else:
            validation_data = {}

    # 3. 에러 메시지 추출 - attempt별로 분리
    if step_buffer.get("error"):
        error_text = step_buffer["error"]

        # "[검증 n회차]" 또는 "[시도 n회차]" 패턴으로 분리
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
                    # 에러 내용을 줄 단위로 분리
                    error_lines = [line.strip() for line in error_content.split('\n') if line.strip()]
                    attempt_error_map[attempt_idx].extend(error_lines)

        # 현재 attempt_num에 해당하는 에러만 가져오기
        if attempt_num in attempt_error_map:
            validation_errors = attempt_error_map[attempt_num]
        else:
            # 패턴이 없는 경우 첫 번째 시도에만 전체 에러 할당
            if attempt_num == 1 and not attempt_error_map:
                validation_errors = [line.strip() for line in error_text.split('\n') if line.strip()]

    # 4. 결과 반환 - attempt는 전달받은 값 그대로 사용
    return {
        "attempt": attempt_num,
        "validationData": validation_data,
        "validationErrors": validation_errors
    }

def build_result_json(myapp_instance):
    """
    MyApp 인스턴스에서 데이터를 추출하여 JSON 형식으로 변환 (모든 시험 시나리오 포함)

    Args:
        myapp_instance: MyApp 클래스의 인스턴스

    Returns:
        dict: JSON 형식의 결과 데이터
    """

    # 1. Request ID 생성
    request_id = CONSTANTS.request_id

    # 2. 평가 대상 정보
    evaluation_target = {
        "companyName": CONSTANTS.company_name,
        "contactPerson": CONSTANTS.contact_person,
        "productName": CONSTANTS.product_name,
        "modelName": CONSTANTS.model_name,
        "version": CONSTANTS.version
    }

    # 3. 테스트 그룹 정보
    test_groups = get_test_groups_info()

    # 4. 인증 방식
    auth_method = map_auth_method(CONSTANTS.auth_type)

    # 5. 전체 테스트 점수 계산 (모든 spec 합산)
    global_pass = getattr(myapp_instance, 'global_pass_cnt', 0)
    global_error = getattr(myapp_instance, 'global_error_cnt', 0)
    global_total = global_pass + global_error
    global_score = (global_pass / global_total * 100) if global_total > 0 else 0

    test_score = {
        "score": round(global_score, 2),
        "totalFields": global_total,
        "passedFields": global_pass,
        "failedFields": global_error
    }

    # 6. 모든 시험 시나리오 결과 수집
    all_spec_results = {}

    # 6-1. 저장된 spec 데이터 처리 (✅ 복합키 지원)
    if hasattr(myapp_instance, 'spec_table_data'):
        for composite_key, saved_data in myapp_instance.spec_table_data.items():
            # 복합키 파싱: "group_id_spec_id" → group_id, spec_id 추출
            if '_' in composite_key:
                parts = composite_key.split('_', 1)
                if len(parts) == 2:
                    group_id = parts[0]
                    spec_id = parts[1]
                else:
                    group_id = None
                    spec_id = composite_key
            else:
                # 하위 호환: 복합키가 아닌 경우 그대로 사용
                group_id = None
                spec_id = composite_key

            spec_result = _build_spec_result(
                myapp_instance,
                spec_id,
                saved_data['step_buffers'],
                saved_data.get('table_data', []),
                group_id
            )
            if spec_result:
                all_spec_results[composite_key] = spec_result  # 복합키로 저장

    # 6-2. 현재 spec 데이터 처리 (저장되지 않은 경우) (✅ 복합키 지원)
    current_spec_id = getattr(myapp_instance, 'current_spec_id', None)
    current_group_id = getattr(myapp_instance, 'current_group_id', None)
    if current_spec_id:
        composite_key = f"{current_group_id}_{current_spec_id}" if current_group_id else current_spec_id
        if composite_key not in all_spec_results:
            spec_result = _build_spec_result(
                myapp_instance,
                current_spec_id,
                getattr(myapp_instance, 'step_buffers', []),
                None,  # 현재 테이블에서 직접 읽음
                current_group_id
            )
            if spec_result:
                all_spec_results[composite_key] = spec_result

    test_result = list(all_spec_results.values())

    # 7. 실행 상태
    status = getattr(myapp_instance, 'run_status', '진행중')

    # 진행 중인 경우 점수 0으로 처리
    if status == "진행중":
        test_score["score"] = 0.0
        for spec_data in test_result:
            spec_data["score"] = 0.0

    # 8. 완료 시간
    completed_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # 최종 JSON 구성
    result_json = {
        "requestId": request_id,
        "evaluationTarget": evaluation_target,
        "testGroups": test_groups,
        "status": status,
        "authMethod": auth_method,
        "testScore": test_score,
        "testResult": test_result,
        "completedDate": completed_date
    }

    return result_json


def _build_spec_result(myapp_instance, spec_id, step_buffers, table_data=None, group_id=None):
    """
    단일 시험 시나리오(spec)의 결과 구성

    Args:
        myapp_instance: MyApp 인스턴스
        spec_id: 시험 시나리오 ID
        step_buffers: 스텝 버퍼 리스트
        table_data: 테이블 데이터 (None인 경우 현재 테이블에서 읽음)
        group_id: 테스트 그룹 ID (None인 경우 기본값 사용)

    Returns:
        dict: spec 결과 데이터 또는 None (데이터가 없는 경우)
    """

    # 1. spec 설정 가져오기
    api_names_list = []
    api_ids_list = []
    api_endpoints_list = []

    for group in CONSTANTS.SPEC_CONFIG:
        if spec_id in group:
            spec_config = group[spec_id]
            api_names_list = spec_config.get('api_name', [])
            api_ids_list = spec_config.get('api_id', [])
            api_endpoints_list = spec_config.get('api_endpoint', [])
            break

    # step_buffers가 없으면 None 반환
    if not step_buffers:
        return None

    # 2. API 결과 리스트 및 통계 초기화
    apis = []
    total_pass = 0
    total_fields = 0

    # 3. 각 API별 결과 구성
    for i, step_buffer in enumerate(step_buffers):
        # 3-1. 테이블 데이터에서 정보 가져오기
        if table_data and i < len(table_data):
            # 저장된 테이블 데이터 사용
            row_data = table_data[i]
            retries = int(row_data.get('retry_count', '0'))
            pass_cnt = int(row_data.get('pass_count', '0'))
            total_cnt = int(row_data.get('total_count', '0'))
            fail_cnt = int(row_data.get('fail_count', '0'))
            api_score_str = row_data.get('score', '0%')
            api_score = float(api_score_str.replace('%', ''))
        else:
            # 현재 테이블에서 직접 읽기
            table_widget = myapp_instance.tableWidget
            if i >= table_widget.rowCount():
                continue

            retries = int(table_widget.item(i, 2).text()) if table_widget.item(i, 2) else 1
            pass_cnt = int(table_widget.item(i, 3).text()) if table_widget.item(i, 3) else 0
            total_cnt = int(table_widget.item(i, 4).text()) if table_widget.item(i, 4) else 0
            fail_cnt = int(table_widget.item(i, 5).text()) if table_widget.item(i, 5) else 0
            api_score_str = table_widget.item(i, 6).text() if table_widget.item(i, 6) else "0%"
            api_score = float(api_score_str.replace('%', ''))

        # 3-2. API 기본 정보 설정
        api_name = api_names_list[i] if i < len(api_names_list) else f"API-{i + 1}"
        api_id = api_ids_list[i] if i < len(api_ids_list) else f"api-{i + 1}"
        api_endpoint = api_endpoints_list[i] if i < len(api_endpoints_list) else f"/api{i + 1}"

        # API 메서드 가져오기 (기본값: POST)
        method = step_buffer.get("api_info", {}).get("method", "POST")

        # 3-3. 검증 데이터 생성 (retries 횟수만큼 attempt 생성)
        validations = []
        for attempt in range(1, retries + 1):
            validation = generate_validation_data_from_step_buffer(step_buffer, attempt)
            validations.append(validation)

        # 3-4. webhook 존재 여부 확인
        has_webhook = step_buffer.get("is_webhook_api", False)

        # 3-5. Registration API 결과 구성
        registration_id = f"{api_id}-registration" if has_webhook else api_id

        api_result = {
            "id": registration_id,
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

        apis.append(api_result)
        total_pass += pass_cnt
        total_fields += total_cnt

        # 3-6. Webhook API 결과 구성 (있는 경우)
        if has_webhook:
            # webhook 검증 데이터 생성
            webhook_validations = []
            for attempt in range(1, retries + 1):
                webhook_validation = {
                    "attempt": attempt,
                    "validationData": step_buffer.get("webhook_data") or {},
                    "validationErrors": step_buffer.get("webhook_error", "").split('\n') if step_buffer.get(
                        "webhook_error") else []
                }
                webhook_validations.append(webhook_validation)

            # webhook 점수 계산
            webhook_pass = step_buffer.get("webhook_pass_cnt", 0)
            webhook_total = step_buffer.get("webhook_total_cnt", 0)
            webhook_fail = webhook_total - webhook_pass
            webhook_score = (webhook_pass / webhook_total * 100) if webhook_total > 0 else 0

            webhook_result = {
                "id": f"{api_id}-webhook",
                "name": f"{api_name} (Webhook)",
                "method": "POST",
                "endpoint": f"{api_endpoint}/webhook",
                "score": round(webhook_score, 0),
                "validationCnt": retries,
                "totalFields": webhook_total,
                "passFields": webhook_pass,
                "failFields": webhook_fail,
                "validations": webhook_validations
            }

            apis.append(webhook_result)
            total_pass += webhook_pass
            total_fields += webhook_total

    # 4. spec 전체 평균 점수 계산
    spec_score = (total_pass / total_fields * 100) if total_fields > 0 else 0

    # 5. spec 이름 가져오기
    spec_name = get_spec_test_name(spec_id)

    # 6. group_id 기본값 처리
    final_group_id = group_id if group_id is not None else ""

    # 7. 최종 결과 반환
    return {
        "testGroup": final_group_id,
        "testSpecId": spec_id,
        "testSpecName": spec_name,
        "score": round(spec_score, 2),
        "totalFields": total_fields,
        "passedFields": total_pass,
        "failedFields": total_fields - total_pass,
        "apis": apis
    }

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

def _validate_url_video(field_path, field_value, rule, reference_context, field_errors, global_errors):
    """RTSP URL 스트리밍 가능 여부 검증"""
    from core.json_checker_new import collect_all_values_by_key, get_by_path
    import time

    access_id_field = rule.get("accessIDField", "accessID")
    access_pw_field = rule.get("accessPWField", "accessPW")
    ref_endpoint = rule.get("referenceEndpoint")

    # ✅ 1. field_value를 리스트로 정규화
    url_list = field_value if isinstance(field_value, list) else [field_value]

    if not url_list:
        error_msg = f"URL이 비어있습니다"
        field_errors.append(error_msg)
        global_errors.append(f"[의미] {field_path}: {error_msg}")
        return False

    print(f"    [url-video] 검증할 URL 개수: {len(url_list)}")

    # ✅ 2. 각 URL 검증
    all_success = True
    for idx, target_url in enumerate(url_list):
        url_index = f"[{idx}]" if isinstance(field_value, list) else ""
        print(f"    [url-video] {url_index} 검증 시작: {target_url}")

        access_id = None
        access_pw = None

        # 유효성 체크
        if not target_url or not isinstance(target_url, str):
            error_msg = f"{url_index} 유효하지 않은 URL 형식: {target_url}"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}{url_index}: {error_msg}")
            all_success = False
            continue

        # ✅ 3. 인증 정보는 reference_context에서 가져오기
        if reference_context and ref_endpoint and ref_endpoint in reference_context:
            ref_data = reference_context[ref_endpoint]

            # field_path가 "camList.camURL" 형식인 경우
            if "." in field_path:
                parts = field_path.split(".")
                parent_path = ".".join(parts[:-1])  # "camList"

                # ref_data에서 해당 리스트 가져오기
                if isinstance(ref_data, dict):
                    parent_list = get_by_path(ref_data, parent_path)
                elif isinstance(ref_data, list):
                    parent_list = ref_data
                else:
                    parent_list = None

                # 현재 URL과 매칭되는 항목에서 인증 정보 찾기
                if isinstance(parent_list, list):
                    for item in parent_list:
                        if isinstance(item, dict):
                            # 리스트인 경우 해당 인덱스의 값과 비교
                            item_url = item.get(parts[-1])
                            if isinstance(item_url, list) and idx < len(item_url):
                                if item_url[idx] == target_url:
                                    access_id = item.get(access_id_field)
                                    access_pw = item.get(access_pw_field)
                                    break
                            elif item_url == target_url:
                                access_id = item.get(access_id_field)
                                access_pw = item.get(access_pw_field)
                                break
            else:
                # 단일 필드인 경우 ref_data에서 직접 가져오기
                if isinstance(ref_data, dict):
                    access_id = ref_data.get(access_id_field)
                    access_pw = ref_data.get(access_pw_field)

        # ✅ 4. RTSP URL 형식 체크
        if not target_url.startswith("rtsp://"):
            error_msg = f"{url_index} RTSP URL이 아님: {target_url} (rtsp:// 로 시작해야 함)"
            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}{url_index}: {error_msg}")
            all_success = False
            continue

        # ✅ 5. 인증 정보 포함
        actual_test_url = target_url
        if access_id and access_pw:
            # 이미 인증정보가 있는 경우 제거 후 재추가
            if '@' in actual_test_url:
                protocol, rest = actual_test_url.split("://", 1)
                if '@' in rest:
                    _, host = rest.split('@', 1)
                    actual_test_url = f"{protocol}://{host}"

            url_without_protocol = actual_test_url.replace("rtsp://", "")
            actual_test_url = f"rtsp://{access_id}:{access_pw}@{url_without_protocol}"
            print(f"    [url-video] {url_index} 인증 정보 포함된 URL로 변경됨", actual_test_url)

        # ✅ 6. OpenCV로 스트림 검증
        cap = None
        try:
            print(f"    [url-video] {url_index} 연결 시도 중...")
            cap = cv2.VideoCapture(actual_test_url)

            try:
                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)
            except:
                print(f"    [url-video] {url_index} ⚠️ 타임아웃 설정 실패")

            if not cap.isOpened():
                error_msg = f"{url_index} 스트림 연결 실패: {actual_test_url}"
                field_errors.append(error_msg)
                global_errors.append(f"[의미] {field_path}{url_index}: {error_msg}")
                all_success = False
                continue

            # 여러 프레임으로 안정성 확인
            success_count = 0
            for i in range(3):
                ret, frame = cap.read()
                if ret and frame is not None:
                    success_count += 1
                    if i == 0:
                        print(f"    [url-video] {url_index} 프레임 크기: {frame.shape}")
                time.sleep(0.3)

            if success_count < 2:
                error_msg = f"{url_index} 프레임 읽기 불안정: {actual_test_url} ({success_count}/3 성공)"
                field_errors.append(error_msg)
                global_errors.append(f"[의미] {field_path}{url_index}: {error_msg}")
                all_success = False
                continue

            print(f"    [url-video] {url_index} ✅ 스트림 검증 성공: {actual_test_url} ({success_count}/3 프레임)")

        except Exception as e:
            if hasattr(cv2, 'error') and isinstance(e, cv2.error):
                error_msg = f"{url_index}  에러: {actual_test_url} - {str(e)}"
            elif isinstance(e, TimeoutError):
                error_msg = f"{url_index} 연결 타임아웃: {actual_test_url}"
            else:
                error_msg = f"{url_index} 스트림 검증 중 오류: {actual_test_url} - {type(e).__name__}"

            field_errors.append(error_msg)
            global_errors.append(f"[의미] {field_path}{url_index}: {error_msg}")
            all_success = False

        finally:
            if cap is not None:
                cap.release()
                print(f"    [url-video] {url_index} 연결 해제 완료")

    return all_success