import numpy
import pandas as pd
import json_checker

# OptionalKey 안전 길이 확인 함수
def safe_len(obj):
    """OptionalKey와 같은 객체에 대해 안전하게 len() 호출"""
    try:
        if isinstance(obj, json_checker.core.checkers.OptionalKey):
            return 0  # OptionalKey는 길이가 없다고 간주
        return len(obj)
    except (TypeError, AttributeError):
        return 0  # len() 호출 불가능한 객체는 길이 0으로 간주


# 리스트 필드인지 동적으로 확인하는 함수
def is_list_field(value):
    if isinstance(value, list): # 내장함수로 객체가 list 타입인지 확인 -> 맞다면 true, 아니라면 종료
        return True
    # elif isinstance(value, tuple) and len(value) > 0:   # 튜플로 맵핑된 경우
    #     return isinstance(value[0], list)
    return False


# 필드 개수 세서 반환하는 함수 (필수/선택 필드 추출)
def field_finder(schema):

    schema = pd.DataFrame([schema])  # , index=[0])
    all_field = []
    fields = []
    fields_opt = [] # 선택적 필드
    step = 0

    for key, value in schema.items():
        if step == 0:
            # OptionalKey 객체 처리
            if hasattr(key, 'expected_data'):
                key_name = key.expected_data
                is_optional = True
            else:
                key_name = key
                is_optional = False
            
            try:
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
            except:
                # 예외가 발생한 경우 (보안상 OptionalKey 처리)
                fields.append([step, key_name, "OPT", value[0]])
                fields_opt.append([step, key_name, "OPT", value[0]])

    all_field.append([fields])
    while True:
        fields = []
        a = all_field[step]
        step += 1
        for field in a[0]:
            if type(field[-1]) == dict:
                for key, value in field[-1].items():
                    try:
                        # OptionalKey 객체 처리
                        if hasattr(key, 'expected_data'):
                            key_name = key.expected_data
                            is_optional = True
                        else:
                            key_name = key
                            is_optional = False
                        
                        if is_list_field(value):
                            for i in value:
                                if is_optional:
                                    fields.append([step, [field[1], key_name], list, i])
                                else:
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
                            elif any(field[1] in tmp for tmp in fields_opt):
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
                                        if any(field[1] in tmp for tmp in fields_opt):
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
    if dataframe_flag == True:
        schema = pd.DataFrame(schema_, index=[0])
    else:
        schema = pd.DataFrame.from_dict([schema_])

    all_field = []
    fields = []
    step = 0    # json에서 중첩 깊이 -> 속의 데이터인지 항목인지 체크

    for key, value in schema.items():
        if step == 0:
            try:
                # List 필드를 자동으로 감지하여 처리
                if is_list_field(value):
                    for i in value:
                        fields.append([step, key, type(i), i])

                elif type(value[0]) == dict:
                    fields.append([step, key, dict, value[0]])
                else:
                    fields.append([step, key, value[0], value[0]])
            except:
                fields.append([step, key.expected_data, value[0], value[0]])

    all_field.append([fields])

    # 0번째 step 끝나고 나서, step 1부터는 while문으로 계속 반복
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
                        # fields
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
        
        total_fields += 1  # 확인해야할 필드 개수 세기

        for data in datas:  # 해당 field마다 list type의 datas 순회하면서 확인
            for raw_data in data[0]:    # raw_data: 들어온 실제 데이터
                if field[1] == raw_data[1]:
                    # 1. 실제 데이터가 스키마 타입과 같은지 or 선택적 데이터인지 or int형인데 numpy int64, int32, float64인 경우 or str형인데 str인 경우 -> 하나라도 참이라면 타당하다! 합격
                    if type(raw_data[-2]) == field[-2] or field[-2] == 'OPT' or (field[-2] == int and type(raw_data[-2]) in [numpy.int64, numpy.int32, numpy.float64]) or (field[-2] == str and type(raw_data[-2]) == str):
                        valid_fields += 1
                    break
            else:
                continue
            break
    
    if valid_fields == total_fields:
        return "PASS", f"{valid_fields}/{total_fields} fields are valid."
    else:
        return "FAIL", f"{valid_fields}/{total_fields} fields are valid."

#메시지 규격 확인
def check_message_schema(all_field, datas, opt_field, flag_opt):
    format_errors = []

    for fields in all_field:
        for field in fields[0]:
            if flag_opt == False and field[-2] == 'OPT':    
                continue

            field_found = False
            for data in datas:
                for raw_data in data[0]:
                    if field[1] == raw_data[1]:
                        field_found = True
                        if not (type(raw_data[-2]) == field[-2] or field[-2] == 'OPT' or (field[-2] == int and type(raw_data[-2]) in [numpy.int64, numpy.int32, numpy.float64]) or (field[-2] == str and type(raw_data[-2]) == str)):
                            format_errors.append(f"Field '{field[1]}' has incorrect type. Expected {field[-2]}, got {type(raw_data[-2])}.")
                        break
                if not field_found and field[-2] != 'OPT':
                    format_errors.append(f"Field '{field[1]}' is missing.")
    if safe_len(format_errors) == 0:
        return "PASS", "All fields match the schema."
    else:
        return "FAIL", format_errors

#메시지 에러
def check_message_error(all_field, datas, opt_field, flag_opt):
    result, error_msg, correct_cnt, error_cnt = do_checker(all_field, datas, opt_field, flag_opt)

    if result == "PASS":
        return "PASS", f"All fields are valid. ({correct_cnt} correct, {error_cnt} errors)"
    else:
        return "FAIL", error_msg

# 결과 반환하는 부분 -> 여기를 3단 분리 -> 일단 남겨두기는 함
# 지금 문제가 모니터링용 함수 호출 1번, 버튼 눌렀을 때 용 함수 호출 1번(2번째 호출) 이렇게 일어나는데
# -> 두번째 호출에서 첫번째 호출로 인해 결과가 덮어씌워지는 문제가 발생해서 결과가 이상한 경우 발생함
# deepcopy
def do_checker(all_field, datas, opt_field ,flag_opt):  # flag_opt => platformVal_none.py, systemVal_none.py 에서!P
    # type and name error
    check_list = []
    # refine_datas = []
    cnt_list = []
    cnt_elements = []
    #flag_opt = True  # True or False

    for fields in all_field:
        for field in fields[0]:

            # OPT 태그가 있는 필드는 OptionalKey에서 나온 것이므로 누락 검사에서 제외
            if field[-2] == 'OPT':  
                pass  # OptionalKey는 선택사항이므로 누락되어도 에러가 아님
            else:
                check_list.append(field)  # 확인해야할 필드 check_list에 추가
                for data in datas:  # 해당 field마다 list type의 datas 순회하면서 확인
                    for raw_data in data[0]:

                        if field[1] == raw_data[1]:  # 스키마와 입력한 데이터 필드명 같은 경우 먼저 확인
                            if raw_data[-2] == list and type(raw_data[-1]) != float:
                                # 리스트 안에 있는 필드 값은 cnt_list 에 raw_data[1] 추가하기

                                # OptionalKey 객체인 경우 len() 에러 방지
                                data_length = safe_len(raw_data[-1])
                                if (data_length > 1 and type(raw_data[-1]) != dict):
                                    for i in range(0, data_length):
                                        cnt_list.append(raw_data[1])
                                else:
                                    cnt_list.append(raw_data[1])

                                # cnt_element가 0이면 무조건 raw_data[1] cnt_elements에 raw_data[1] 추가
                                # 0이상이면, cnt_element와 raw_data[1]이 다른 경우, cnt_elements에 raw_data[1] 추가
                                if safe_len(cnt_elements) != 0:
                                    flag = False
                                    for i, cnt_element in enumerate(cnt_elements):
                                        if raw_data[1] == cnt_element:
                                            flag = True
                                    if flag == False:
                                        cnt_elements.append(raw_data[1])
                                else:
                                    cnt_elements.append(raw_data[1])

                            # 통과된 raw_data는 -1에 True로 표시
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
                                if tmp_flag == False: #이부분 출력되는 경우 없음.
                                    raw_data[-1] = "KeyName OK but Value Type Error: " + str(field[1]) + " " + str(
                                        field[-1][0]) + " " + str(raw_data[-2])
                                else:
                                    raw_data[-1] = True

                            else:
                                if field[-1] == int:
                                    if type(raw_data[-1]) == numpy.int64 or type(raw_data[-1]) == numpy.int32 or type(raw_data[-1]) == numpy.float:
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

                                else:  # int, str 아닌 field[-1]과 raw_data[-1]의 type 비교
                                    if type(field[-1]) == dict and type(raw_data[-1]) == list:  # error
                                        raw_data[-1] = "Data Type Error: " + str(field[1]) + " " + str(raw_data[-1])
                                    elif type(field[-1]) == dict and type(raw_data[-1]) == dict:
                                        raw_data[-1] = True
                                    elif type(field[-1]) == list and type(raw_data[-1]) == dict:
                                        pass
                                    elif type(field[-1][0]) == dict and type(raw_data[-1]) == list:
                                        raw_data[-1] = True
                                    else:
                                        pass
    #  checklist만들고 나서 count
    all_cnt = []
    for i in cnt_elements:
        cnt = cnt_list.count(i)
        all_cnt.append([i, cnt])

    # refine data -> 세부 결과 확인 부분의 에러 메시지 출력 부분
    check_error = []
    for i, field in enumerate(check_list):

        for data in datas:
            for raw_data in data[0]:

                if (field[1] == raw_data[1]) and (raw_data[-1] is True):  # 필드 이름, 필드 타입 맞으면
                    if type(check_list[i][-1]) != int:  # type(field[-1]) != int
                        check_list[i][-1] = 1
                    else:
                        check_list[i][-1] += 1

                elif field[1] == raw_data[1]:  # 필드명만 맞은 경우
                    if field[2] == dict:  # object -> Array<object>로 틀린 경우?

                        check_error.append([field[0], [field[1]],
                                            "Data Type Error: " + str(field[1]) + " " + str(field[2])])

                        if type(field[-1]) == dict:
                            for kk in field[-1]:
                                if isinstance(kk, json_checker.core.checkers.OptionalKey):
                                    # OptionalKey는 선택사항이므로 누락되어도 에러가 아님
                                    pass
                                else:
                                    # 필수 키만 Missing Key Error로 처리
                                    check_error.append([field[0], [field[1], kk],
                                                        "Missing Key Error: " + str([field[1], kk]) + " " + str(
                                                            field[-1]) + " " + kk])

                    elif type(field[2]) == dict:  # object -> Array<object>로 틀린 경우?
                        check_error.append([field[0], [field[1]],
                                            "Data Type Error: " + str(field[1]) + " " + str(field[2])])

                        for kk in field[2]:  # object오류인 경우 하위 필드 또한 오류로 출력하기 위해 추가함
                            check_error.append([field[0], [field[1],kk], "Missing Key Error: " + str([field[1], kk]) + " " + str(field[-1])+" "+kk])

                    elif field[2] == list:  # aryobj-> obj틀린 경우
                        check_error.append([field[0], [field[1]],
                                            "Data Type Error: " + str(field[1]) + " " + str(field[2])])
                        if type(field[-1]) == list and type(field[-1][0]) == dict:  #field[-1]==>[{'transProtocolType': <class 'str'>, OptionalKey(transProtocolDesc): <class 'str'>}]
                            for kks, val in field[-1][0].items():
                                if isinstance(kks, json_checker.core.checkers.OptionalKey):
                                    # OptionalKey는 선택사항이므로 누락되어도 에러가 아님
                                    pass
                                else:
                                    # 필수 키만 Missing Key Error로 처리
                                    check_error.append([field[0], [field[1], kks], "Missing Key Error: " + str(
                                        [field[1], kks]) + " " + kks])

                                if val != type and type(val) == dict:

                                    for tmp_val in val:
                                        if isinstance(tmp_val, json_checker.core.checkers.OptionalKey):
                                            # OptionalKey는 선택사항이므로 누락되어도 에러가 아님
                                            pass
                                        else:
                                            # 필수 키만 Missing Key Error로 처리
                                            check_error.append(
                                                [field[0], [field[1], kks, tmp_val], "Missing Key Error: " + str(
                                                    [field[1], kks, tmp_val]) + " " + tmp_val])

                        else:
                            check_error.append([field[0], [field[1], field[-1]], "Missing Key Error: " + str([field[1], field[-1]]) + " " + str(field[-1])])

                    elif type(field[-1]) == list and raw_data[2] != type(field[-1]):  #aryobj-> obj틀린 경우 # field: [0, 'camList', 'OPT', [{'camID': <class 'str'>}]]
                        check_error.append([field[0], [field[1]],
                                            "Data Type Error: " + str(field[1]) + " " + str(field[-1])])
                        for kk_ in field[-1]:
                            check_error.append([field[0], [field[1], kk_],
                                            "Missing Key Error: " + str([field[1], field[-1]]) + " " + str(kk_)])

                    elif type(field[-1]) == raw_data[-2]:  # 추가함
                        pass

                    else:
                        check_error.append(raw_data)

    for i, field in enumerate(check_list):  # missing key 오류 찾기

        flag = False
        for j in all_cnt:

            if j[0] == field[1][0] and j[1] != field[-1] and type(field[1]) != list:  # != list 조건 추가함

                tmp_cnt = 0


                for l in check_error:
                    #print(l)
                    if field[1] == l[1]:
                        tmp_cnt += 1

                if type(field[-1]) == type:  # if 추가함
                    flag = True

                elif type(field[-1]) == dict:  # 추가함
                    flag = True

                elif type(field[-1]) == list:

                    if type(field[-1][0]) == type:
                        flag = True

                elif j[1] != (field[-1] + tmp_cnt):
                    flag = True

            elif j[0] == field[1][0] and j[1] != field[-1] and type(field[1]) == list:  # == list 조건 추가함

                tmp_cnt = 0
                for l in check_error:

                    if field[1] == l[1]:
                        tmp_cnt += 1

                if type(field[-1]) == type:  # if 추가함
                    if field[-1] == int:  #
                        pass
                    else:
                        flag = True
                elif type(field[-1]) == dict:  #추가함
                    flag = True
                elif type(field[-1]) == list:
                    if type(field[-1][0]) == type:
                        flag = True
                elif j[1] != (field[-1] + tmp_cnt):
                    flag = True

            elif j[0] == field[1][0] and j[1]!= field[-1] and type(field[1]) != list:
                pass

        if flag == True:
            error = ""
            for k in check_list:
                if field[1] == k[1]:  # 추가함 Missing Key Error: ['camList', 'camLoc'] camLoc
                    error = "Missing Key Error: " + str(field[1]) + " " + str(k[1][-1])
                    check_error.append([field[0], [field[1], k[1][-1]], error])

                elif field[1] == k[1][0]:
                    error = "Missing Key Error: " + str(field[1]) + " " + str(k[1][-1])
                    check_error.append([field[0], [field[1], k[1][-1]], error])

            if error == "":
                tmp_flag_ = True
                for lst in check_error:  # 이미 (Data Type Error)있는 경우 Missing Key Error는 없애기 위해 추가함
                    if field[1][1] == lst[1][-1]:
                        tmp_flag_ = False
                if tmp_flag_ == True:
                    check_error.append(
                        [field[0], field[1],
                         "Missing Key Error: " + str(field[1]) + " " + str(field[-1])])

    check_list_tmp = []

    for i, field in enumerate(check_list):
        check_list_tmp.append(field)

        flag = False
        flag_do = False
        #print("??field", field)
        if type(field[-1]) == type:
            flag_do = True
        elif type(field[-1]) == list:

            if type(field[-1][0]) == type:  # [1, ['doorList', 'bioAuthTypeList'], 'OPT', [<class 'str'>]]
                flag_do = True

            elif type(field[-1][0]) == dict:  #
                #print("\t elif field", field)
                flag_do = True  # Array<Object>=> Object 일때, Missing key Error

        elif type(field[-1]) == dict:  # 0911
            flag_do = True  # no_optional, flag_opt = True 일때, Object => Missing key Error

        if flag_do is True:

            for j in check_error:
                if j[1] == field[1]:
                    flag = True
            if flag is False:
                if (flag_opt is False) and any(field[1] in tmp for tmp in opt_field):
                    # flag_opt false일때 optional 필드 하위필수필드 오류발생하지 않도록 추가함
                    pass

                else:
                    _tmp_flag = True

                    for lst in check_error:  # 이미 (Data Type Error)있는 경우 Missing Key Error는 없애기 위해 추가함
                        # OptionalKey 관련 안전 검사
                        if (safe_len(lst[1]) == 1 and field[1] == lst[1][0]):
                            _tmp_flag = False
                        
                        # 추가 조건: 리스트 필드의 중첩 검사 (OptionalKey 안전 처리)
                        if (type(field[1]) is list and type(lst[1]) is list and 
                            safe_len(field[1]) > 1 and safe_len(lst[1]) > 0):
                            try:
                                if field[1][1] == lst[1][-1]:
                                    # code message missing key error 찾기위해 type 비교 추가함
                                    _tmp_flag = False
                            except (IndexError, AttributeError):
                                # 리스트 접근 중 에러 발생 시 무시
                                pass

                    if _tmp_flag == True:

                        check_error.append(
                            [field[0], field[1],
                             "Missing Key Error: " + str(field[1]) + " " + str(field[-1])])
    check_list = check_list_tmp

    error = ""
    error_fields = []

    for i in check_error:
        if safe_len(error_fields) != 0:
            flag = False
            for j, error_field in enumerate(error_fields):
                if i[1] == error_field:
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
        return "FAIL", error, correct_cnt, error_cnt    # 상세 결과 확인 부분에 출력되는 메시지 -> fail인 경우



def timeout_field_finder(schema):

    schema = pd.DataFrame([schema])  # , index=[0])
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
                if type(value[0])==list:
                    for val in value[0]:
                        fields_opt.append([str(step+1), [key.expected_data, val], "OPT",val])
                        if type(val) == list and type(val[0])==dict:
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
                            if any(field[1] in tmp for tmp in fields_opt):
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
                                        #fields.append([step, [field[1], key2.expected_data], "OPT", value])
                                        fields_opt.append([step, [field[1], key2.expected_data], "OPT", value])

                                        if type(value) == dict:
                                            for val_k, val_v in value.items():
                                                fields_opt.append([str(step + 1), [key2.expected_data, val_k], "OPT", val_v])

                                        elif type(value) == list and type(value[0]) == dict:
                                            for val_k, val_v in value[0].items():
                                                fields_opt.append([str(step + 2), [value, val_k], "OPT", val_v])



                                    except:
                                        fields.append([step, [field[1], key2], value, value])
                                        if any(field[1] in tmp for tmp in fields_opt):
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
                            if type(val) == list and type(val[-1])==dict:
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

    return all_field_cnt, fields_opt_cnt # #of required field, #of optional field



