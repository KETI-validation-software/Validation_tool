import numpy
import json
import pandas as pd
import json_checker
import re

def safe_hash(obj):
    """unhashable 객체를 hashable하게 변환"""
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, sort_keys=True)
    return obj

def safe_compare(a, b):
    """두 값을 안전하게 비교 (딕셔너리/리스트 포함)"""
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
                print(f"[DEBUG] a type: {type(a)}, a: {a}")
                print(f"[DEBUG] b type: {type(b)}, b: {b}")
                # JSON 직렬화가 실패하면 문자열로 비교
                return str(a) == str(b)
        
        # 기본 타입은 직접 비교
        return a == b
    except Exception as e:
        # 모든 예외를 잡아서 False 반환
        print(f"[DEBUG] safe_compare error: {e}")
        print(f"[DEBUG] a type: {type(a)}, a: {repr(a)}")
        print(f"[DEBUG] b type: {type(b)}, b: {repr(b)}")
        import traceback
        traceback.print_exc()
        return False

def safe_in_check(item, container):
    """item이 container에 있는지 안전하게 확인"""
    try:
        if isinstance(item, (dict, list)):
            try:
                item_str = json.dumps(item, sort_keys=True, default=str)
                for c in container:
                    if isinstance(c, (dict, list)):
                        if item_str == json.dumps(c, sort_keys=True, default=str):
                            return True
                    elif item == c:
                        return True
                return False
            except (TypeError, ValueError):
                # JSON 직렬화가 실패하면 문자열로 비교
                item_str = str(item)
                for c in container:
                    if str(c) == item_str:
                        return True
                return False
        return item in container
    except Exception as e:
        print(f"[DEBUG] safe_in_check error: {e}, item={item}")
        return False

def safe_field_in_opt(field_name, opt_field_list):
    """필드가 opt_field_list에 있는지 안전하게 확인"""
    try:
        for tmp in opt_field_list:
            if isinstance(tmp, list) and len(tmp) > 1:
                # field_name이 리스트인 경우
                if isinstance(field_name, list):
                    if safe_compare(field_name, tmp[1]) or (len(field_name) > 0 and safe_compare(field_name[0], tmp[1])):
                        return True
                # field_name이 단일 값인 경우
                elif safe_compare(field_name, tmp[1]):
                    return True
        return False
    except (TypeError, AttributeError, IndexError):
        return False

# OptionalKey 안전 길이 확인 함수
def safe_len(obj):
    """OptionalKey와 같은 객체에 대해 안전하게 len() 호출"""
    try:
        if isinstance(obj, json_checker.core.checkers.OptionalKey):
            return 0
        return len(obj)
    except (TypeError, AttributeError):
        return 0

# 리스트 필드인지 동적으로 확인하는 함수
def is_list_field(value):
    return isinstance(value, list)

# 1단계: validation_request.py에서 규칙 dict 추출 함수
def extract_validation_rules(validation_dict):
    """
    validation_dict: 각 API별 _in_validation dict
    반환: {필드명: 검증규칙 dict, ...} 형태로 평탄화
    """
    rules = {}
    def _flatten(prefix, d):
        for k, v in d.items():
            field_name = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict) and ("validationType" in v or "enabled" in v):
                rules[field_name] = v
            elif isinstance(v, dict):
                _flatten(field_name, v)
    _flatten("", validation_dict)
    return rules

# 2단계: semantic validation logic
def do_semantic_checker(rules_dict, data_dict):
    """
    rules_dict: extract_validation_rules로 추출한 {필드명: 규칙 dict}
    data_dict: 실제 데이터(dict)
    반환: {필드명: {'result': PASS/FAIL, 'score': int, 'msg': str}} + total_score
    """
    results = {}
    total_score = 0
    max_score = 0
    
    for field, rule in rules_dict.items():
        keys = field.split('.')
        value = data_dict
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                value = None
                break
        
        score = rule.get('score', 1)
        max_score += score
        
        if not rule.get('enabled', True):
            results[field] = {'result': 'SKIP', 'score': 0, 'msg': 'Validation disabled'}
            continue
        
        vtype = rule.get('validationType', None)
        msg = ''
        passed = True

        # valid-value-match
        if vtype == 'valid-value-match':
            allowed = rule.get('allowedValues', [])
            operator = rule.get('validValueOperator', 'equalsAny')
            
            if operator == 'equals':
                if not safe_in_check(value, allowed):
                    passed = False
                    msg = f"Value '{value}' not in allowedValues {allowed} (equals)"
            elif operator == 'equalsAny':
                if not safe_in_check(value, allowed):
                    passed = False
                    msg = f"Value '{value}' not in allowedValues {allowed} (equalsAny)"

        # specified-value-match
        elif vtype == 'specified-value-match':
            specified = rule.get('allowedValues', [])
            value_input_type = rule.get('valueInputType', 'single')
            
            if not safe_in_check(value, specified):
                passed = False
                msg = f"Value '{value}' does not match specifiedValue {specified}"

        # range-match
        elif vtype == 'range-match':
            operator = rule.get('rangeOperator', None)
            minv = rule.get('rangeMin', None)
            maxv = rule.get('rangeMax', None)
            try:
                v = float(value)
                if operator == 'less-than':
                    if maxv is not None and v >= maxv:
                        passed = False
                        msg = f"Value {v} not less than {maxv}"
                elif operator == 'less-equal':
                    if maxv is not None and v > maxv:
                        passed = False
                        msg = f"Value {v} not less or equal to {maxv}"
                elif operator == 'between':
                    if (minv is not None and v < minv) or (maxv is not None and v > maxv):
                        passed = False
                        msg = f"Value {v} not between [{minv}, {maxv}]"
                elif operator == 'greater-equal':
                    if minv is not None and v < minv:
                        passed = False
                        msg = f"Value {v} not greater or equal to {minv}"
                elif operator == 'greater-than':
                    if minv is not None and v <= minv:
                        passed = False
                        msg = f"Value {v} not greater than {minv}"
            except Exception:
                passed = False
                msg = f"Value '{value}' is not a number"

        # request-field-match
        elif vtype == 'request-field-match':
            ref_field = rule.get('referenceField', None)
            ref_value = None
            if ref_field:
                ref_keys = ref_field.split('.')
                ref_value = data_dict
                for rk in ref_keys:
                    if isinstance(ref_value, dict) and rk in ref_value:
                        ref_value = ref_value[rk]
                    else:
                        ref_value = None
                        break
            if not safe_compare(value, ref_value):
                passed = False
                msg = f"Value '{value}' does not match referenceField '{ref_field}' value '{ref_value}'"

        # response-field-match
        elif vtype == 'response-field-match':
            ref_field = rule.get('referenceField', None)
            ref_value = None
            if ref_field:
                ref_keys = ref_field.split('.')
                ref_value = data_dict
                for rk in ref_keys:
                    if isinstance(ref_value, dict) and rk in ref_value:
                        ref_value = ref_value[rk]
                    else:
                        ref_value = None
                        break
            if not safe_compare(value, ref_value):
                passed = False
                msg = f"Value '{value}' does not match responseField '{ref_field}' value '{ref_value}'"

        # request-field-list-match
        elif vtype == 'request-field-list-match':
            ref_list_field = rule.get('referenceListField', None)
            ref_list = None
            if ref_list_field:
                ref_keys = ref_list_field.split('.')
                ref_list = data_dict
                for rk in ref_keys:
                    if isinstance(ref_list, dict) and rk in ref_list:
                        ref_list = ref_list[rk]
                    else:
                        ref_list = None
                        break
            if isinstance(ref_list, list):
                if not safe_in_check(value, ref_list):
                    passed = False
                    msg = f"Value '{value}' not in referenceListField {ref_list}"
            else:
                passed = False
                msg = f"referenceListField '{ref_list_field}' is not a list"

        # response-field-list-match
        elif vtype == 'response-field-list-match':
            ref_list_field = rule.get('referenceListField', None)
            ref_list = None
            if ref_list_field:
                ref_keys = ref_list_field.split('.')
                ref_list = data_dict
                for rk in ref_keys:
                    if isinstance(ref_list, dict) and rk in ref_list:
                        ref_list = ref_list[rk]
                    else:
                        ref_list = None
                        break
            if isinstance(ref_list, list):
                if not safe_in_check(value, ref_list):
                    passed = False
                    msg = f"Value '{value}' not in responseListField {ref_list}"
            else:
                passed = False
                msg = f"responseListField '{ref_list_field}' is not a list"

        # length
        elif vtype == 'length':
            minl = rule.get('minLength', None)
            maxl = rule.get('maxLength', None)
            try:
                l = len(value)
                if (minl is not None and l < minl) or (maxl is not None and l > maxl):
                    passed = False
                    msg = f"Length {l} not in range [{minl}, {maxl}]"
            except Exception:
                passed = False
                msg = f"Value '{value}' has no length"
        
        # regex
        elif vtype == 'regex':
            pattern = rule.get('pattern', None)
            if pattern is not None:
                try:
                    if not re.fullmatch(pattern, str(value)):
                        passed = False
                        msg = f"Value '{value}' does not match regex '{pattern}'"
                except Exception as e:
                    passed = False
                    msg = f"Regex error: {e}"
            else:
                passed = False
                msg = "No regex pattern specified"
        
        # required
        elif vtype == 'required':
            if value is None or value == '':
                passed = False
                msg = "Field is required but missing or empty"
        
        # unique
        elif vtype == 'unique':
            if isinstance(value, list):
                try:
                    hashable_value = [safe_hash(v) for v in value]
                    try:
                        if len(hashable_value) != len(set(hashable_value)):
                            passed = False
                            msg = "List contains duplicate values"
                    except TypeError as e:
                        import traceback
                        print("[DEBUG][unhashable] unique validation error in do_semantic_checker")
                        print("value:", value)
                        print("hashable_value:", hashable_value)
                        traceback.print_exc()
                        passed = False
                        msg = f"Unique validation error: {e}"
                except Exception as e:
                    import traceback
                    print("[DEBUG][exception] unique validation error in do_semantic_checker")
                    print("value:", value)
                    traceback.print_exc()
                    passed = False
                    msg = f"Unique validation error: {e}"
            else:
                passed = False
                msg = "Field is not a list for unique validation"
        
        # custom
        elif vtype == 'custom':
            func = rule.get('customFunction', None)
            if callable(func):
                try:
                    if not func(value):
                        passed = False
                        msg = f"Custom function failed for value '{value}'"
                except Exception as e:
                    passed = False
                    msg = f"Custom function error: {e}"
            else:
                passed = False
                msg = "No custom function provided"
        
        if passed:
            results[field] = {'result': 'PASS', 'score': score, 'msg': msg}
            total_score += score
        else:
            results[field] = {'result': 'FAIL', 'score': 0, 'msg': msg}
    
    results['total_score'] = total_score
    results['max_score'] = max_score
    return results

# 필드 개수 세서 반환하는 함수 (필수/선택 필드 추출)
def field_finder(schema):
    schema = pd.DataFrame([schema])
    all_field = []
    fields = []
    fields_opt = []
    step = 0

    for key, value in schema.items():
        if step == 0:
            try:
                # 키를 안전하게 처리
                if hasattr(key, 'expected_data'):
                    key_name = key.expected_data
                    is_optional = True
                else:
                    key_name = str(key)  # 딕셔너리 키를 문자열로 변환
                    is_optional = False
                
                if is_list_field(value):
                    for i in value:
                        if is_optional:
                            fields.append([step, key_name, "OPT", i])
                            fields_opt.append([step, key_name, "OPT", i])
                        else:
                            fields.append([step, key_name, list, i])
                elif type(value[0]) == dict:
                    if is_optional:
                        fields.append([step, key_name, "OPT", value[0]])
                        fields_opt.append([step, key_name, "OPT", value[0]])
                    else:
                        fields.append([step, key_name, dict, value[0]])
                else:
                    if is_optional:
                        fields.append([step, key_name, "OPT", value[0]])
                        fields_opt.append([step, key_name, "OPT", value[0]])
                    else:
                        fields.append([step, key_name, value[0], value[0]])
            except Exception as e:
                print(f"[DEBUG] field_finder error: {e}, key={key}, value={value}")
                try:
                    fields.append([step, str(key), "OPT", str(value)])
                except:
                    fields.append([step, "unknown", "OPT", "unknown"])

    all_field.append([fields])
    
    while True:
        fields = []
        a = all_field[step]
        step += 1
        
        for field in a[0]:
            if type(field[-1]) == dict:
                for key, value in field[-1].items():
                    try:
                        if hasattr(key, 'expected_data'):
                            key_name = key.expected_data
                            is_optional = True
                        else:
                            key_name = key
                            is_optional = False
                        
                        if is_list_field(value):
                            for i in value:
                                fields.append([step, [field[1], key_name], list, i])
                        elif type(value) == dict:
                            if is_optional:
                                fields.append([step, [field[1], key_name], dict, value])
                            else:
                                fields.append([step, [field[1], key_name], dict, value])
                        else:
                            if is_optional:
                                fields.append([step, [field[1], key_name], "OPT", value])
                                fields_opt.append([step, [field[1], key_name], "OPT", value])
                            elif safe_field_in_opt(field[1], fields_opt):
                                fields.append([step, [field[1], key_name], "OPT", value])
                                fields_opt.append([step, [field[1], key_name], "OPT", value])
                            else:
                                fields.append([step, [field[1], key_name], value, value])
                    except:
                        fields.append([step, [field[1], key.expected_data], "OPT", value])
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
                                        fields.append([step, [field[1], key2.expected_data], "OPT", value])
                                        fields_opt.append([step, [field[1], key2.expected_data], "OPT", value])
                                    except:
                                        if safe_field_in_opt(field[1], fields_opt):
                                            fields_opt.append([step, [field[1], key2], "OPT", value])
                                            fields.append([step, [field[1], key2], "OPT", value])
                                        else:
                                            fields.append([step, [field[1], key2], value, value])
                        else:
                            if type(field[-1]) == list:
                                if key == int or key == str:
                                    pass
                            else:
                                fields.append([step, [field[1], key.expected_data], "OPT", field[-1][key]])
                                fields_opt.append([step, [field[1], key.expected_data], "OPT", field[-1][key]])

        if safe_len(fields) != 0:
            all_field.append([fields])
        else:
            break

    return all_field, fields_opt

# 실제 데이터에서 필드 추출하기
def data_finder(schema_):
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

    for key, value in schema.items():
        if step == 0:
            try:
                # 키를 안전하게 처리
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

# 메시지 데이터만 확인
def check_message_data(all_field, datas, opt_filed, flag_opt):
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

# 메시지 규격 확인
def check_message_schema(all_field, datas, opt_field, flag_opt):
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
                            format_errors.append(f"Field '{field[1]}' has incorrect type. Expected {field[-2]}, got {type(raw_data[-2])}.")
                        break
                        
            if not field_found and field[-2] != 'OPT':
                format_errors.append(f"Field '{field[1]}' is missing.")
    
    if safe_len(format_errors) == 0:
        return "PASS", "All fields match the schema."
    else:
        return "FAIL", format_errors

# 메시지 에러
def check_message_error(all_field, datas, opt_field, flag_opt):
    result, error_msg, correct_cnt, error_cnt = do_checker(all_field, datas, opt_field, flag_opt)

    if result == "PASS":
        return "PASS", f"All fields are valid. ({correct_cnt} correct, {error_cnt} errors)"
    else:
        return "FAIL", error_msg

def do_checker(all_field, datas, opt_field, flag_opt):
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
                                            print(f"[DEBUG] cnt_list append error: {e}, raw_data[1]={raw_data[1]}")
                                else:
                                    try:
                                        cnt_list.append(raw_data[1])
                                    except Exception as e:
                                        print(f"[DEBUG] cnt_list append error: {e}, raw_data[1]={raw_data[1]}")

                                if safe_len(cnt_elements) != 0:
                                    flag = False
                                    print(f"[DEBUG] cnt_elements 비교 시작: raw_data[1]={repr(raw_data[1])}")
                                    for i, cnt_element in enumerate(cnt_elements):
                                        try:
                                            if safe_compare(raw_data[1], cnt_element):
                                                flag = True
                                                print(f"[DEBUG] 매치 발견: raw_data[1] == cnt_elements[{i}]")
                                        except Exception as e:
                                            print(f"[DEBUG] cnt_elements 비교 에러: {e}")
                                            print(f"[DEBUG] raw_data[1]: {repr(raw_data[1])}")
                                            print(f"[DEBUG] cnt_element: {repr(cnt_element)}")
                                    if flag == False:
                                        # 딕셔너리나 리스트인 경우 안전하게 추가
                                        try:
                                            print(f"[DEBUG] cnt_elements에 추가: {repr(raw_data[1])}")
                                            cnt_elements.append(raw_data[1])
                                        except Exception as e:
                                            print(f"[DEBUG] cnt_elements append error: {e}, raw_data[1]={raw_data[1]}")
                                            import traceback
                                            traceback.print_exc()
                                else:
                                    # 딕셔너리나 리스트인 경우 안전하게 추가
                                    try:
                                        print(f"[DEBUG] cnt_elements 첫 번째 추가: {repr(raw_data[1])}")
                                        cnt_elements.append(raw_data[1])
                                    except Exception as e:
                                        print(f"[DEBUG] cnt_elements append error: {e}, raw_data[1]={raw_data[1]}")
                                        import traceback
                                        traceback.print_exc()

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
                                    raw_data[-1] = "KeyName OK but Value Type Error: " + str(field[1]) + " " + str(field[-1][0]) + " " + str(raw_data[-2])
                                else:
                                    raw_data[-1] = True
                            else:
                                if field[-1] == int:
                                    if type(raw_data[-1]) == numpy.int64 or type(raw_data[-1]) == numpy.int32 or type(raw_data[-1]) == numpy.float:
                                        raw_data[-1] = True
                                    else:
                                        raw_data[-1] = "Value Type Error: " + str(field[1]) + " " + str(field[-1]) + " " + str(raw_data[-2])
                                elif field[-1] == str:
                                    if type(raw_data[-1]) == str:
                                        raw_data[-1] = True
                                    else:
                                        raw_data[-1] = "Value Type Error: " + str(field[1]) + " " + str(field[-1]) + " " + str(raw_data[-2])
                                else:
                                    if type(field[-1]) == dict and type(raw_data[-1]) == list:
                                        raw_data[-1] = "Data Type Error: " + str(field[1]) + " " + str(raw_data[-1])
                                    elif type(field[-1]) == dict and type(raw_data[-1]) == dict:
                                        raw_data[-1] = True
                                    elif type(field[-1]) == list and type(raw_data[-1]) == dict:
                                        pass
                                    elif isinstance(field[-1], list) and len(field[-1]) > 0 and isinstance(field[-1][0], dict) and type(raw_data[-1]) == list:
                                        raw_data[-1] = True
                                    else:
                                        pass

    all_cnt = []
    print(f"[DEBUG] cnt_elements 개수: {len(cnt_elements)}")
    print(f"[DEBUG] cnt_list 개수: {len(cnt_list)}")
    
    for idx, i in enumerate(cnt_elements):
        try:
            print(f"[DEBUG] cnt_elements[{idx}] 처리 중: type={type(i)}, value={repr(i)}")
            # 딕셔너리나 리스트인 경우 안전하게 카운트
            cnt = 0
            for x_idx, x in enumerate(cnt_list):
                try:
                    if safe_compare(i, x):
                        cnt += 1
                        print(f"[DEBUG] 매치 발견: cnt_elements[{idx}] == cnt_list[{x_idx}]")
                except Exception as e:
                    print(f"[DEBUG] safe_compare 에러: {e}")
                    print(f"[DEBUG] i: {repr(i)}, x: {repr(x)}")
            all_cnt.append([i, cnt])
            print(f"[DEBUG] cnt_elements[{idx}] 최종 카운트: {cnt}")
        except Exception as e:
            print(f"[DEBUG] all_cnt calculation error: {e}")
            print(f"[DEBUG] i type: {type(i)}, i: {repr(i)}")
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
                        check_error.append([field[0], [field[1]], "Data Type Error: " + str(field[1]) + " " + str(field[2])])

                        if type(field[-1]) == dict:
                            for kk in field[-1]:
                                if isinstance(kk, json_checker.core.checkers.OptionalKey):
                                    pass
                                else:
                                    check_error.append([field[0], [field[1], kk], "Missing Key Error: " + str([field[1], kk]) + " " + str(field[-1]) + " " + kk])

                    elif type(field[2]) == dict:
                        check_error.append([field[0], [field[1]], "Data Type Error: " + str(field[1]) + " " + str(field[2])])

                        for kk in field[2]:
                            check_error.append([field[0], [field[1], kk], "Missing Key Error: " + str([field[1], kk]) + " " + str(field[-1]) + " " + kk])

                    elif field[2] == list:
                        check_error.append([field[0], [field[1]], "Data Type Error: " + str(field[1]) + " " + str(field[2])])
                        if type(field[-1]) == list and type(field[-1][0]) == dict:
                            for kks, val in field[-1][0].items():
                                if isinstance(kks, json_checker.core.checkers.OptionalKey):
                                    pass
                                else:
                                    check_error.append([field[0], [field[1], kks], "Missing Key Error: " + str([field[1], kks]) + " " + kks])

                                if val != type and type(val) == dict:
                                    for tmp_val in val:
                                        if isinstance(tmp_val, json_checker.core.checkers.OptionalKey):
                                            pass
                                        else:
                                            check_error.append([field[0], [field[1], kks, tmp_val], "Missing Key Error: " + str([field[1], kks, tmp_val]) + " " + tmp_val])
                        else:
                            check_error.append([field[0], [field[1], field[-1]], "Missing Key Error: " + str([field[1], field[-1]]) + " " + str(field[-1])])

                    elif type(field[-1]) == list and raw_data[2] != type(field[-1]):
                        check_error.append([field[0], [field[1]], "Data Type Error: " + str(field[1]) + " " + str(field[-1])])
                        for kk_ in field[-1]:
                            check_error.append([field[0], [field[1], kk_], "Missing Key Error: " + str([field[1], field[-1]]) + " " + str(kk_)])

                    elif type(field[-1]) == raw_data[-2]:
                        pass
                    else:
                        check_error.append(raw_data)

    for i, field in enumerate(check_list):
        flag = False
        for j in all_cnt:
            if safe_compare(j[0], field[1][0] if isinstance(field[1], list) and len(field[1]) > 0 else field[1]) and j[1] != field[-1] and type(field[1]) != list:
                tmp_cnt = 0
                for l in check_error:
                    if safe_compare(field[1], l[1]):
                        tmp_cnt += 1

                if type(field[-1]) == type:
                    flag = True
                elif type(field[-1]) == dict:
                    flag = True
                elif type(field[-1]) == list:
                    if type(field[-1][0]) == type:
                        flag = True
                elif j[1] != (field[-1] + tmp_cnt):
                    flag = True

            elif safe_compare(j[0], field[1][0] if isinstance(field[1], list) and len(field[1]) > 0 else field[1]) and j[1] != field[-1] and type(field[1]) == list:
                tmp_cnt = 0
                for l in check_error:
                    if safe_compare(field[1], l[1]):
                        tmp_cnt += 1

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
                    error = "Missing Key Error: " + str(field[1]) + " " + str(k[1][-1] if isinstance(k[1], list) and len(k[1]) > 0 else k[1])
                    check_error.append([field[0], [field[1], k[1][-1] if isinstance(k[1], list) and len(k[1]) > 0 else k[1]], error])
                elif isinstance(field[1], list) and isinstance(k[1], list) and len(field[1]) > 0 and len(k[1]) > 0 and safe_compare(field[1][0], k[1][0]):
                    error = "Missing Key Error: " + str(field[1]) + " " + str(k[1][-1])
                    check_error.append([field[0], [field[1], k[1][-1]], error])

            if error == "":
                tmp_flag_ = True
                for lst in check_error:
                    if isinstance(field[1], list) and len(field[1]) > 1 and isinstance(lst[1], list) and len(lst[1]) > 0:
                        if safe_compare(field[1][1], lst[1][-1]):
                            tmp_flag_ = False
                if tmp_flag_ == True:
                    check_error.append([field[0], field[1], "Missing Key Error: " + str(field[1]) + " " + str(field[-1])])

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
                        check_error.append([field[0], field[1], "Missing Key Error: " + str(field[1]) + " " + str(field[-1])])
    
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
                        fields_opt.append([str(step+1), [key.expected_data, val], "OPT", val])
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
                                                fields_opt.append([str(step + 1), [key2.expected_data, val_k], "OPT", val_v])
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