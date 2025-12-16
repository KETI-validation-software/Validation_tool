import numpy
import json
import pandas as pd
import json_checker
from json_checker import OptionalKey


# ================================================================
# 1. 유틸리티 함수들 (안전한 비교 및 변환)
# ================================================================

def safe_hash(obj):
    """unhashable 객체를 hashable하게 변환"""
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, sort_keys=True)
    return obj


def safe_compare(a, b):
    """
    두 값을 안전하게 비교 (딕셔너리/리스트 포함)
    
    Returns:
        bool: 두 값이 같으면 True
    """
    try:
        # None 체크
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False

        # 타입이 다르면 False
        if type(a) != type(b):
            return False

        # 딕셔너리나 리스트인 경우 JSON 문자열로 비교
        if isinstance(a, (dict, list)):
            try:
                return json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
            except (TypeError, ValueError) as e:
                print(f"[DEBUG] safe_compare JSON error: {e}")
                # JSON 직렬화가 실패하면 문자열로 비교
                return str(a) == str(b)

        # 기본 타입은 직접 비교
        return a == b
    except Exception as e:
        print(f"[DEBUG] safe_compare error: {e}")
        print(f"[DEBUG] a type: {type(a)}, a: {repr(a)}")
        print(f"[DEBUG] b type: {type(b)}, b: {repr(b)}")
        import traceback
        traceback.print_exc()
        return False


def safe_field_in_opt(field_name, opt_field_list):
    """필드가 opt_field_list에 있는지 안전하게 확인"""
    try:
        for tmp in opt_field_list:
            if isinstance(tmp, list) and len(tmp) > 1:
                # field_name이 리스트인 경우
                if isinstance(field_name, list):
                    if safe_compare(field_name, tmp[1]) or (
                            len(field_name) > 0 and safe_compare(field_name[0], tmp[1])):
                        return True
                # field_name이 단일 값인 경우
                elif safe_compare(field_name, tmp[1]):
                    return True
        return False
    except (TypeError, AttributeError, IndexError):
        return False


def safe_len(obj):
    """OptionalKey와 같은 객체에 대해 안전하게 len() 호출"""
    try:
        if isinstance(obj, json_checker.core.checkers.OptionalKey):
            return 0
        return len(obj)
    except (TypeError, AttributeError):
        return 0


def is_list_field(value):
    """리스트 필드인지 확인"""
    return isinstance(value, list)


def to_list(x):
    """값을 리스트로 변환 (이미 리스트면 그대로, None이면 빈 리스트)"""
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


# ================================================================
# 2. 데이터 수집 및 경로 처리 함수들
# ================================================================

def collect_all_values_by_key(data, key):
    """
    중첩된 dict/list 구조에서 특정 키의 모든 값을 재귀적으로 수집

    Args:
        data: 검색할 데이터 (dict, list, 또는 기타)
        key: 찾을 키 이름 (예: "camID")

    Returns:
        list: 해당 키의 모든 값들의 리스트

    Example:
        data = {
            "camList": [
                {"camID": "cam1", "name": "Camera 1"},
                {"camID": "cam2", "name": "Camera 2"}
            ],
            "extra": {"camID": "cam3"}
        }
        collect_all_values_by_key(data, "camID")
        # Returns: ["cam1", "cam2", "cam3"]
    """
    results = []

    def _recursive_search(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    # 값이 리스트면 펼치고, 아니면 그대로 추가
                    if isinstance(v, list):
                        results.extend(v)
                    else:
                        results.append(v)
                # 재귀적으로 계속 탐색
                _recursive_search(v)
        elif isinstance(obj, list):
            for item in obj:
                _recursive_search(item)

    _recursive_search(data)
    return results


def get_by_path(data, path):
    """
    dot-path를 따라 값을 가져온다.
    - 중간에 list를 만나면 각 원소에 대해 계속 탐색하여 '값들의 리스트'를 반환
    - 최종 결과가 단일 값이면 스칼라, 여러 값이면 리스트로 반환
    
    Args:
        data: 탐색할 데이터
        path: 점으로 구분된 경로 (예: "camList.camID")
    
    Returns:
        값 또는 값들의 리스트 (없으면 None)
    """
    parts = path.split(".")
    current = [data]  # 항상 리스트로 유지해 누적 확장

    for key in parts:
        next_level = []
        for item in current:
            if isinstance(item, dict) and key in item:
                next_level.append(item[key])
            elif isinstance(item, list):
                # 리스트면 각 원소에서 같은 key를 찾는다
                for elem in item:
                    if isinstance(elem, dict) and key in elem:
                        next_level.append(elem[key])
        current = next_level

        if not current:  # 더 이상 진행 불가
            return None

    # 결과 평탄화: 단 하나면 스칼라, 2개 이상이면 그대로 리스트
    if len(current) == 1:
        return current[0]
    return current


# ================================================================
# 3. Validation 규칙 추출
# ================================================================

def extract_validation_rules(validation_dict):
    """
    validation_dict에서 규칙 dict를 평탄화하여 추출
    
    Args:
        validation_dict: 각 API별 _in_validation dict
    
    Returns:
        dict: {필드명: 검증규칙 dict, ...} 형태
    """
    print(f"\n🔍 [EXTRACT VALIDATION RULES] 시작")
    print(f"📋 입력 데이터 타입: {type(validation_dict)}")
    print(f"📊 입력 데이터 크기: {len(validation_dict) if isinstance(validation_dict, dict) else 'N/A'}")

    rules = {}

    def _flatten(prefix, d):
        for k, v in d.items():
            field_name = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict) and ("validationType" in v or "enabled" in v):
                rules[field_name] = v
                print(f"   ✅ 규칙 발견: '{field_name}' -> {v.get('validationType', 'N/A')}")
            elif isinstance(v, dict):
                print(f"   🔍 중첩 구조 탐색: '{field_name}'")
                _flatten(field_name, v)

    _flatten("", validation_dict)

    print(f"📊 추출된 규칙 개수: {len(rules)}")
    print(f"📝 규칙 목록: {list(rules.keys())}")

    return rules


# ================================================================
# 4. 스키마 분석 함수들
# ================================================================

def data_finder(schema_):
    """
    스키마에서 모든 필드를 재귀적으로 추출
    
    Returns:
        list: 계층별로 필드 정보를 담은 리스트
    """
    dataframe_flag = True
    for schema_value in schema_.values():
        if type(schema_value) == dict or type(schema_value) == list:
            dataframe_flag = False

    if dataframe_flag:
        schema = pd.DataFrame(schema_, index=[0])
    else:
        schema = pd.DataFrame.from_dict([schema_])

    all_field = []
    fields = []
    step = 0

    # 최상위 레벨 처리
    for key, value in schema.items():
        if step == 0:
            try:
                key_name = str(key) if not hasattr(key, 'expected_data') else key.expected_data

                if is_list_field(value):
                    for i in value:
                        fields.append([step, key_name, type(i), i])
                elif type(value[0]) == dict:
                    fields.append([step, key_name, dict, value[0]])
                else:
                    fields.append([step, key_name, value[0], value[0]])
            except Exception as e:
                print(f"[DEBUG] data_finder error: {e}, key={key}, value={value}")
                try:
                    fields.append([step, str(key), "OPT", str(value)])
                except:
                    fields.append([step, "unknown", "OPT", "unknown"])

    all_field.append([fields])

    # 중첩 레벨 재귀 처리
    while True:
        fields = []
        a = all_field[step]
        step += 1

        for field in a[0]:
            if type(field[-1]) == dict:
                for key, value in field[-1].items():
                    try:
                        if is_list_field(value):
                            for i in value:
                                fields.append([step, [field[1], key], list, i])
                        elif type(value) == dict:
                            fields.append([step, [field[1], key], dict, value])
                        else:
                            fields.append([step, [field[1], key], value, value])
                    except:
                        fields.append([step, [field[1], key.expected_data], value, value])

            elif type(field[-1]) == list:
                for key in field[-1]:
                    try:
                        if type(field[-1][key]) == dict:
                            fields.append([step, [field[1], key], dict, field[-1][key]])
                        elif is_list_field(field[-1][key]):
                            for i in field[-1][key]:
                                fields.append([step, [field[1], key], list, i])
                        else:
                            fields.append([step, [field[1], key], field[-1][key], field[-1][key]])
                    except:
                        if type(key) == dict:
                            for key2, value in key.items():
                                try:
                                    if type(field[-1][key2]) == dict:
                                        fields.append([step, [field[1], key2], dict, field[-1][key2]])
                                    elif is_list_field(field[-1][key2]):
                                        for i in field[-1][key2]:
                                            fields.append([step, [field[1], key2], list, i])
                                    else:
                                        fields.append([step, [field[1], key2], field[-1][key2], field[-1][key2]])
                                except:
                                    fields.append([step, [field[1], key2], value, value])
                        else:
                            if type(field[-1]) == list:
                                if key == int or key == str:
                                    pass
                            else:
                                fields.append([step, [field[1], key.expected_data], field[-1][key], field[-1][key]])

        if safe_len(fields) != 0:
            all_field.append([fields])
        else:
            break

    return all_field


def get_flat_fields_from_schema(schema, prefix=""):
    """
    스키마를 평탄화하여 {경로: 타입} 형태로 반환
    - primitive 배열은 '경로[]' 형태로 저장
    - object 배열은 각 필드별로 '경로[].field' 형태로 저장
    """
    fields = {}
    opt_fields = []

    if not isinstance(schema, dict):
        return fields, opt_fields

    for key, value in schema.items():
        # OptionalKey 처리
        is_optional = isinstance(key, OptionalKey)
        actual_key = key.expected_data if is_optional else key
        current_path = f"{prefix}.{actual_key}" if prefix else actual_key

        if is_optional:
            opt_fields.append(current_path)

        if isinstance(value, list):
            if len(value) == 0:
                continue
            elif isinstance(value[0], dict):
                # ✅ 수정: Object 배열 - 재귀적으로 처리하되 prefix에 [] 추가
                nested_fields, nested_opts = get_flat_fields_from_schema(
                    value[0],
                    f"{current_path}[]"  # array[].field 형태로 경로 생성
                )
                fields.update(nested_fields)
                opt_fields.extend(nested_opts)
            elif isinstance(value[0], type):
                # Primitive 배열
                fields[f"{current_path}[]"] = value[0]

        elif isinstance(value, dict):
            # 중첩 객체
            nested_fields, nested_opts = get_flat_fields_from_schema(value, current_path)
            fields.update(nested_fields)
            opt_fields.extend(nested_opts)
        elif isinstance(value, type):
            # 단일 필드
            fields[current_path] = value

    return fields, opt_fields


def get_flat_data_from_response(data, prefix=""):
    """
    실제 응답 데이터를 평탄화하여 {경로: 값} 형태로 반환
    - primitive 배열은 '경로[]' 형태로 저장
    - object 배열은 각 인덱스별로 '경로[idx].field' 형태로 저장
    """
    result = {}

    if not isinstance(data, dict):
        return result

    for key, value in data.items():
        current_path = f"{prefix}.{key}" if prefix else key

        if isinstance(value, list):
            if len(value) == 0:
                # 빈 배열
                result[f"{current_path}[]"] = []
            elif isinstance(value[0], dict):
                # ✅ 수정: Object 배열 - 모든 인덱스를 순회하며 재귀 처리
                for idx, item in enumerate(value):
                    # 각 object의 필드를 재귀적으로 처리
                    nested = get_flat_data_from_response(item, f"{current_path}[]")

                    # 중첩 배열 처리: nested에 이미 [] 형태의 키가 있으면 그대로 병합
                    for nested_key, nested_value in nested.items():
                        if nested_key.endswith("[]"):
                            # primitive 배열인 경우
                            if nested_key not in result:
                                result[nested_key] = []
                            # ✅ 모든 인덱스의 배열 값을 수집
                            if isinstance(nested_value, list):
                                result[nested_key].extend(nested_value)
                            else:
                                result[nested_key].append(nested_value)
                        else:
                            # 일반 필드는 첫 번째 인덱스 값만 저장 (타입 검증용)
                            if nested_key not in result:
                                result[nested_key] = nested_value
            else:
                # Primitive 배열
                result[f"{current_path}[]"] = value

        elif isinstance(value, dict):
            # 중첩 객체
            nested = get_flat_data_from_response(value, current_path)
            result.update(nested)
        else:
            # 단일 값
            result[current_path] = value
    return result


# ================================================================
# 5. 메시지 검증 함수들
# ================================================================

def check_message_data(all_field, datas, opt_filed, flag_opt):
    """메시지 데이터만 확인"""
    valid_fields = 0
    total_fields = 0

    for fields in all_field:
        for field in fields[0]:
            if flag_opt == False and field[-2] == 'OPT':
                continue

            total_fields += 1

            for data in datas:
                for raw_data in data[0]:
                    if safe_compare(field[1], raw_data[1]):
                        if type(raw_data[-2]) == field[-2] or field[-2] == 'OPT' or \
                                (field[-2] == int and type(raw_data[-2]) in [numpy.int64, numpy.int32, numpy.float64]) or \
                                (field[-2] == str and type(raw_data[-2]) == str):
                            valid_fields += 1
                        break
                else:
                    continue
                break

    if valid_fields == total_fields:
        return "PASS", f"{valid_fields}/{total_fields} fields are valid."
    else:
        return "FAIL", f"{valid_fields}/{total_fields} fields are valid."


def check_message_schema(all_field, datas, opt_field, flag_opt):
    """메시지 규격 확인"""
    format_errors = []

    for fields in all_field:
        for field in fields[0]:
            if flag_opt == False and field[-2] == 'OPT':
                continue

            field_found = False
            for data in datas:
                for raw_data in data[0]:
                    if safe_compare(field[1], raw_data[1]):
                        field_found = True
                        if not (type(raw_data[-2]) == field[-2] or field[-2] == 'OPT' or \
                                (field[-2] == int and type(raw_data[-2]) in [numpy.int64, numpy.int32, numpy.float64]) or \
                                (field[-2] == str and type(raw_data[-2]) == str)):
                            format_errors.append(
                                f"Field '{field[1]}' has incorrect type. Expected {field[-2]}, got {type(raw_data[-2])}.")
                        break

            if not field_found and field[-2] != 'OPT':
                format_errors.append(f"Field '{field[1]}' is missing.")

    if safe_len(format_errors) == 0:
        return "PASS", "All fields match the schema."
    else:
        return "FAIL", format_errors


def check_message_error(all_field, datas, opt_field, flag_opt):
    """메시지 에러 체크"""
    result, error_msg, correct_cnt, error_cnt = do_checker(all_field, datas, opt_field, flag_opt)

    if result == "PASS":
        return "PASS", f"All fields are valid. ({correct_cnt} correct, {error_cnt} errors)"
    else:
        return "FAIL", error_msg


def do_checker(all_field, datas, opt_field, flag_opt):
    """
    실제 필드 검증 로직을 수행하는 핵심 함수
    (기존 코드 유지 - 너무 복잡하여 리팩토링 제외)
    """
    check_list = []
    cnt_list = []
    cnt_elements = []

    for fields in all_field:
        for field in fields[0]:
            if flag_opt is False and field[-2] == 'OPT':
                pass
            else:
                check_list.append(field)
                for data in datas:
                    for raw_data in data[0]:
                        if safe_compare(field[1], raw_data[1]):
                            if raw_data[-2] == list and type(raw_data[-1]) != float:
                                data_length = safe_len(raw_data[-1])
                                if (data_length > 1 and type(raw_data[-1]) != dict):
                                    for i in range(0, data_length):
                                        try:
                                            cnt_list.append(raw_data[1])
                                        except Exception as e:
                                            print(f"[DEBUG] cnt_list append error: {e}")
                                else:
                                    try:
                                        cnt_list.append(raw_data[1])
                                    except Exception as e:
                                        print(f"[DEBUG] cnt_list append error: {e}")

                                if safe_len(cnt_elements) != 0:
                                    flag = False
                                    for i, cnt_element in enumerate(cnt_elements):
                                        try:
                                            if safe_compare(raw_data[1], cnt_element):
                                                flag = True
                                        except Exception as e:
                                            print(f"[DEBUG] cnt_elements 비교 에러: {e}")
                                    if flag == False:
                                        try:
                                            cnt_elements.append(raw_data[1])
                                        except Exception as e:
                                            print(f"[DEBUG] cnt_elements append error: {e}")
                                else:
                                    try:
                                        cnt_elements.append(raw_data[1])
                                    except Exception as e:
                                        print(f"[DEBUG] cnt_elements append error: {e}")

                            if type(raw_data[-2]) == field[-2]:
                                raw_data[-1] = True
                            elif raw_data[-2] == list and raw_data[-2] == field[-2]:
                                raw_data[-1] = True
                            elif raw_data[-2] == dict and raw_data[-2] == field[-2]:
                                raw_data[-1] = True
                            elif field[-2] == 'OPT' and type(raw_data[-2]) == field[-1]:
                                raw_data[-1] = True
                            elif type(field[-1]) == list and type(raw_data[-2]) == type(field[-1]):
                                tmp_flag = True
                                for i in raw_data[-2]:
                                    if type(i) == dict and type(i) != type(field[-1][0]):
                                        tmp_flag = False
                                if tmp_flag == False:
                                    raw_data[-1] = "KeyName OK but Value Type Error: " + str(field[1]) + " " + str(
                                        field[-1][0]) + " " + str(raw_data[-2])
                                else:
                                    raw_data[-1] = True
                            else:
                                if field[-1] == int:
                                    if type(raw_data[-1]) == numpy.int64 or type(raw_data[-1]) == numpy.int32 or type(
                                            raw_data[-1]) == numpy.float:
                                        raw_data[-1] = True
                                    else:
                                        raw_data[-1] = "Value Type Error: " + str(field[1]) + " " + str(
                                            field[-1]) + " " + str(raw_data[-2])
                                elif field[-1] == str:
                                    if type(raw_data[-1]) == str:
                                        raw_data[-1] = True
                                    else:
                                        raw_data[-1] = "Value Type Error: " + str(field[1]) + " " + str(
                                            field[-1]) + " " + str(raw_data[-2])
                                else:
                                    if type(field[-1]) == dict and type(raw_data[-1]) == list:
                                        raw_data[-1] = "Data Type Error: " + str(field[1]) + " " + str(raw_data[-1])
                                    elif type(field[-1]) == dict and type(raw_data[-1]) == dict:
                                        raw_data[-1] = True
                                    elif type(field[-1]) == list and type(raw_data[-1]) == dict:
                                        pass
                                    elif isinstance(field[-1], list) and len(field[-1]) > 0 and isinstance(field[-1][0],
                                                                                                           dict) and type(
                                        raw_data[-1]) == list:
                                        raw_data[-1] = True
                                    else:
                                        pass

    all_cnt = []

    for idx, i in enumerate(cnt_elements):
        try:
            cnt = sum(1 for x in cnt_list if safe_compare(i, x))
            all_cnt.append([i, cnt])
        except Exception as e:
            print(f"[DEBUG] all_cnt calculation error: {e}")
            import traceback
            traceback.print_exc()
            all_cnt.append([i, 0])

    check_error = []
    for i, field in enumerate(check_list):
        for data in datas:
            for raw_data in data[0]:
                if safe_compare(field[1], raw_data[1]) and (raw_data[-1] is True):
                    if type(check_list[i][-1]) != int:
                        check_list[i][-1] = 1
                    else:
                        check_list[i][-1] += 1
                elif safe_compare(field[1], raw_data[1]):
                    if field[2] == dict:
                        check_error.append(
                            [field[0], [field[1]], "Data Type Error: " + str(field[1]) + " " + str(field[2])])

                        if type(field[-1]) == dict:
                            for kk in field[-1]:
                                if isinstance(kk, json_checker.core.checkers.OptionalKey):
                                    pass
                                else:
                                    check_error.append([field[0], [field[1], kk],
                                                        "Missing Key Error: " + str([field[1], kk]) + " " + str(
                                                            field[-1]) + " " + kk])

                    elif type(field[2]) == dict:
                        check_error.append(
                            [field[0], [field[1]], "Data Type Error: " + str(field[1]) + " " + str(field[2])])

                        for kk in field[2]:
                            check_error.append([field[0], [field[1], kk],
                                                "Missing Key Error: " + str([field[1], kk]) + " " + str(
                                                    field[-1]) + " " + kk])

                    elif field[2] == list:
                        check_error.append(
                            [field[0], [field[1]], "Data Type Error: " + str(field[1]) + " " + str(field[2])])
                        if type(field[-1]) == list and type(field[-1][0]) == dict:
                            for kks, val in field[-1][0].items():
                                if isinstance(kks, json_checker.core.checkers.OptionalKey):
                                    pass
                                else:
                                    check_error.append([field[0], [field[1], kks],
                                                        "Missing Key Error: " + str([field[1], kks]) + " " + kks])

                                if val != type and type(val) == dict:
                                    for tmp_val in val:
                                        if isinstance(tmp_val, json_checker.core.checkers.OptionalKey):
                                            pass
                                        else:
                                            check_error.append([field[0], [field[1], kks, tmp_val],
                                                                "Missing Key Error: " + str(
                                                                    [field[1], kks, tmp_val]) + " " + tmp_val])
                        else:
                            check_error.append([field[0], [field[1], field[-1]],
                                                "Missing Key Error: " + str([field[1], field[-1]]) + " " + str(
                                                    field[-1])])

                    elif type(field[-1]) == list and raw_data[2] != type(field[-1]):
                        check_error.append(
                            [field[0], [field[1]], "Data Type Error: " + str(field[1]) + " " + str(field[-1])])
                        for kk_ in field[-1]:
                            check_error.append([field[0], [field[1], kk_],
                                                "Missing Key Error: " + str([field[1], field[-1]]) + " " + str(kk_)])

                    elif type(field[-1]) == raw_data[-2]:
                        pass
                    else:
                        check_error.append(raw_data)

    for i, field in enumerate(check_list):
        flag = False
        for j in all_cnt:
            if safe_compare(j[0], field[1][0] if isinstance(field[1], list) and len(field[1]) > 0 else field[1]) and j[
                1] != field[-1] and type(field[1]) != list:
                tmp_cnt = sum(1 for l in check_error if safe_compare(field[1], l[1]))

                if type(field[-1]) == type:
                    flag = True
                elif type(field[-1]) == dict:
                    flag = True
                elif type(field[-1]) == list:
                    if type(field[-1][0]) == type:
                        flag = True
                elif j[1] != (field[-1] + tmp_cnt):
                    flag = True

            elif safe_compare(j[0], field[1][0] if isinstance(field[1], list) and len(field[1]) > 0 else field[1]) and \
                    j[1] != field[-1] and type(field[1]) == list:
                tmp_cnt = sum(1 for l in check_error if safe_compare(field[1], l[1]))

                if type(field[-1]) == type:
                    if field[-1] == int:
                        pass
                    else:
                        flag = True
                elif type(field[-1]) == dict:
                    flag = True
                elif type(field[-1]) == list:
                    if type(field[-1][0]) == type:
                        flag = True
                elif j[1] != (field[-1] + tmp_cnt):
                    flag = True

        if flag == True:
            error = ""
            for k in check_list:
                if safe_compare(field[1], k[1]):
                    error = "Missing Key Error: " + str(field[1]) + " " + str(
                        k[1][-1] if isinstance(k[1], list) and len(k[1]) > 0 else k[1])
                    check_error.append(
                        [field[0], [field[1], k[1][-1] if isinstance(k[1], list) and len(k[1]) > 0 else k[1]], error])
                elif isinstance(field[1], list) and isinstance(k[1], list) and len(field[1]) > 0 and len(
                        k[1]) > 0 and safe_compare(field[1][0], k[1][0]):
                    error = "Missing Key Error: " + str(field[1]) + " " + str(k[1][-1])
                    check_error.append([field[0], [field[1], k[1][-1]], error])

            if error == "":
                tmp_flag_ = True
                for lst in check_error:
                    if isinstance(field[1], list) and len(field[1]) > 1 and isinstance(lst[1], list) and len(
                            lst[1]) > 0:
                        if safe_compare(field[1][1], lst[1][-1]):
                            tmp_flag_ = False
                if tmp_flag_ == True:
                    check_error.append(
                        [field[0], field[1], "Missing Key Error: " + str(field[1]) + " " + str(field[-1])])

    check_list_tmp = []

    for i, field in enumerate(check_list):
        check_list_tmp.append(field)

        flag = False
        flag_do = False

        if type(field[-1]) == type:
            flag_do = True
        elif type(field[-1]) == list:
            if type(field[-1][0]) == type:
                flag_do = True
            elif type(field[-1][0]) == dict:
                flag_do = True
        elif type(field[-1]) == dict:
            flag_do = True

        if flag_do is True:
            for j in check_error:
                if safe_compare(j[1], field[1]):
                    flag = True

            if flag is False:
                if (flag_opt is False) and safe_field_in_opt(field[1], opt_field):
                    pass
                else:
                    _tmp_flag = True

                    for lst in check_error:
                        if (safe_len(lst[1]) == 1 and safe_compare(field[1], lst[1][0])):
                            _tmp_flag = False

                        if (type(field[1]) is list and type(lst[1]) is list and
                                safe_len(field[1]) > 1 and safe_len(lst[1]) > 0):
                            try:
                                if safe_compare(field[1][1], lst[1][-1]):
                                    _tmp_flag = False
                            except (IndexError, AttributeError):
                                pass

                    if _tmp_flag == True:
                        check_error.append(
                            [field[0], field[1], "Missing Key Error: " + str(field[1]) + " " + str(field[-1])])

    check_list = check_list_tmp

    error = ""
    error_fields = []

    for i in check_error:
        if safe_len(error_fields) != 0:
            flag = False
            for j, error_field in enumerate(error_fields):
                if safe_compare(i[1], error_field):
                    flag = True
            if flag is False:
                error_fields.append(i[1])
        else:
            error_fields.append(i[1])

        error += str(i[-1]) + "\n"

    error_cnt = safe_len(error_fields)
    correct_cnt = safe_len(check_list) - error_cnt

    if error_cnt == 0:
        return "PASS", "PASS", safe_len(check_list), 0
    else:
        return "FAIL", error, correct_cnt, error_cnt


def timeout_field_finder(schema):
    """
    타임아웃 필드 카운터
    (기존 로직 유지 - 복잡하여 리팩토링 제외)
    """
    schema = pd.DataFrame([schema])
    all_field = []
    fields = []
    fields_opt = []
    step = 0

    for key, value in schema.items():
        if step == 0:
            try:
                if is_list_field(value):
                    for i in value:
                        fields.append([step, key, list, i])
                elif type(value[0]) == dict:
                    fields.append([step, key, dict, value[0]])
                else:
                    fields.append([step, key, value[0], value[0]])
            except:
                fields_opt.append([step, key.expected_data, "OPT", value[0]])
                if type(value[0]) == list:
                    for val in value[0]:
                        fields_opt.append([str(step + 1), [key.expected_data, val], "OPT", val])
                        if type(val) == list and type(val[0]) == dict:
                            for val_k, val_v in val.items():
                                fields_opt.append([str(step + 2), [val, val_k], "OPT", val_v])
                elif type(value[0]) == dict:
                    for val_k, val_v in value[0].items():
                        fields_opt.append([str(step + 1), [key.expected_data, val_k], "OPT", val_v])

    all_field.append([fields])

    while True:
        fields = []
        a = all_field[step]
        step += 1

        for field in a[0]:
            if type(field[-1]) == dict:
                for key, value in field[-1].items():
                    try:
                        if is_list_field(value):
                            for i in value:
                                fields.append([step, [field[1], key], list, i])
                        elif type(value) == dict:
                            fields.append([step, [field[1], key], dict, value])
                        else:
                            fields.append([step, [field[1], key], value, value])
                            if safe_field_in_opt(field[1], fields_opt):
                                fields_opt.append([step, [field[1], key], value, value])
                    except:
                        fields_opt.append([step, [field[1], key.expected_data], "OPT", value])

            elif type(field[-1]) == list:
                for key in field[-1]:
                    try:
                        if type(field[-1][key]) == dict:
                            fields.append([step, [field[1], key], dict, field[-1][key]])
                        elif is_list_field(field[-1][key]):
                            for i in field[-1][key]:
                                fields.append([step, [field[1], key], list, i])
                        else:
                            fields.append([step, [field[1], key], field[-1][key], field[-1][key]])
                    except:
                        if type(key) == dict:
                            for key2, value in key.items():
                                try:
                                    if type(field[-1][key2]) == dict:
                                        fields.append([step, [field[1], key2], dict, field[-1][key2]])
                                    elif is_list_field(field[-1][key2]):
                                        for i in field[-1][key2]:
                                            fields.append([step, [field[1], key2], list, i])
                                    else:
                                        fields.append([step, [field[1], key2], field[-1][key2], field[-1][key2]])
                                except:
                                    try:
                                        fields_opt.append([step, [field[1], key2.expected_data], "OPT", value])

                                        if type(value) == dict:
                                            for val_k, val_v in value.items():
                                                fields_opt.append(
                                                    [str(step + 1), [key2.expected_data, val_k], "OPT", val_v])
                                        elif type(value) == list and type(value[0]) == dict:
                                            for val_k, val_v in value[0].items():
                                                fields_opt.append([str(step + 2), [value, val_k], "OPT", val_v])
                                    except:
                                        fields.append([step, [field[1], key2], value, value])
                                        if safe_field_in_opt(field[1], fields_opt):
                                            fields_opt.append([step, [field[1], key2], value, value])
                        else:
                            if type(field[-1]) == list:
                                if key == int or key == str:
                                    pass
                            else:
                                fields_opt.append([step, [field[1], key.expected_data], "OPT", field[-1][key]])

        if safe_len(fields) != 0:
            all_field.append([fields])
        else:
            break

    all_field_cnt = safe_len(all_field[0][0])
    fields_opt_cnt = safe_len(fields_opt)

    for fields_tmp in all_field[0][0]:
        if type(fields_tmp) == list and type(fields_tmp[-1]) == list:
            for field_tmp in fields_tmp[-1]:
                if type(field_tmp) == list:
                    all_field_cnt += safe_len(field_tmp)
                elif type(field_tmp) == dict:
                    for key, val in field_tmp.items():
                        if isinstance(key, json_checker.core.checkers.OptionalKey):
                            pass
                        else:
                            all_field_cnt += 1
                            if type(val) == list and safe_len(val) > 0 and type(val[-1]) == dict:
                                for k, v in val[-1].items():
                                    if isinstance(k, json_checker.core.checkers.OptionalKey):
                                        pass
                                    else:
                                        all_field_cnt += 1
                                        if type(v) == dict:
                                            for tmp_k, tmp_v in v.items():
                                                if isinstance(tmp_k, json_checker.core.checkers.OptionalKey):
                                                    pass
                                                else:
                                                    all_field_cnt += 1

        elif type(fields_tmp) == list and type(fields_tmp[-1]) == dict:
            for field_tmp in fields_tmp[-1]:
                if isinstance(field_tmp, json_checker.core.checkers.OptionalKey):
                    pass
                else:
                    all_field_cnt += 1

    return all_field_cnt, fields_opt_cnt