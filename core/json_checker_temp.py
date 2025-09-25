import numpy
import json_checker.core.checkers
from typing import List, Dict, Any, Tuple, Union
import pandas as pd

from collections.abc import Mapping, Sequence
from voluptuous import Optional as OptionalKey




class DataChecker:
    """데이터 검증을 위한 클래스"""

    def __init__(self, flag_opt: bool = True):
        self.flag_opt = flag_opt  # Optional 필드 검사 여부
        self.check_list = []
        self.check_errors = []
        self.cnt_list = []
        self.cnt_elements = []

    def do_checker(self, all_field: List, datas: List, opt_field: List, flag_opt: bool = None) -> Tuple[
        str, str, int, int]:
        """
        메인 검증 함수

        Args:
            all_field: 스키마 필드 정보
            datas: 검증할 데이터
            opt_field: 선택적 필드 정보
            flag_opt: 선택적 필드 검사 여부

        Returns:
            (결과상태, 에러메시지, 성공개수, 실패개수)
        """
        if flag_opt is not None:
            self.flag_opt = flag_opt

        # 초기화
        self._reset_state()

        # 1. 검사할 필드 목록 생성
        self._build_check_list(all_field)

        # 2. 타입 및 이름 검증
        self._validate_fields(datas)

        # 3. 카운트 계산
        count_info = self._calculate_counts()

        # 4. 세부 에러 검사
        self._check_detailed_errors(datas, count_info)

        # 5. 누락된 키 검사
        self._check_missing_keys(count_info, opt_field)

        # 6. 결과 반환
        return self._generate_result()

    def _reset_state(self):
        """상태 초기화"""
        self.check_list = []
        self.check_errors = []
        self.cnt_list = []
        self.cnt_elements = []

    def _build_check_list(self, all_field: List):
        """검사할 필드 목록 생성"""
        for fields in all_field:
            for field in fields[0]:
                # Optional 필드 검사 안하는 경우 제외
                if not self.flag_opt and field[-2] == 'OPT':
                    continue
                self.check_list.append(field)

    def _validate_fields(self, datas: List):
        """필드 타입 및 이름 검증"""
        for field in self.check_list:
            for data in datas:
                for raw_data in data[0]:
                    if field[1] == raw_data[1]:
                        self._process_matching_field(field, raw_data)

    def _process_matching_field(self, field: List, raw_data: List):
        """매칭된 필드 처리"""
        # 리스트 타입 카운팅
        if raw_data[-2] == list and type(raw_data[-1]) != float:
            self._count_list_elements(raw_data)

        # 타입 검증
        self._validate_field_type(field, raw_data)

    def _count_list_elements(self, raw_data: List):
        """리스트 요소 카운팅"""
        if len(raw_data[-1]) > 1 and type(raw_data[-1]) != dict:
            for i in range(len(raw_data[-1])):
                self.cnt_list.append(raw_data[1])
        else:
            self.cnt_list.append(raw_data[1])

        # 중복 제거하여 cnt_elements에 추가
        if raw_data[1] not in self.cnt_elements:
            self.cnt_elements.append(raw_data[1])

    def _validate_field_type(self, field: List, raw_data: List):
        """필드 타입 검증"""
        field_type = field[-2]
        field_value = field[-1]
        raw_type = raw_data[-2]
        raw_value = raw_data[-1]

        # 타입 매칭 검사
        if self._types_match(field_type, raw_type, field_value, raw_value):
            raw_data[-1] = True
        else:
            raw_data[-1] = self._generate_type_error_message(field, raw_data)

    def _types_match(self, field_type: Any, raw_type: Any, field_value: Any, raw_value: Any) -> bool:
        """타입 매칭 검사"""
        # 기본 타입 매칭
        if type(raw_type) == field_type:
            return True

        # 특별한 경우들
        if field_type == 'OPT' and type(raw_type) == field_value:
            return True

        if field_type == int:
            return self._is_numeric_type(raw_value)

        if field_type == str:
            return type(raw_value) == str

        if isinstance(field_value, list) and isinstance(raw_type, type(field_value)):
            return self._validate_list_content(field_value, raw_value)

        if isinstance(field_value, dict) and isinstance(raw_value, dict):
            return True

        return False

    def _is_numeric_type(self, value: Any) -> bool:
        """숫자 타입인지 확인"""
        return type(value) in [numpy.int64, numpy.int32, numpy.float, int, float]

    def _validate_list_content(self, field_list: List, raw_list: List) -> bool:
        """리스트 내용 검증"""
        if not field_list or not raw_list:
            return True

        field_item_type = type(field_list[0])

        for item in raw_list:
            if field_item_type == dict and type(item) != dict:
                return False

        return True

    def _generate_type_error_message(self, field: List, raw_data: List) -> str:
        """타입 에러 메시지 생성"""
        field_name = field[1]
        expected_type = field[-1]
        actual_type = raw_data[-2]

        return f"Value Type Error: {field_name} expected {expected_type} but got {actual_type}"

    def _calculate_counts(self) -> Dict[str, int]:
        """각 필드별 카운트 계산"""
        count_info = {}
        for element in self.cnt_elements:
            count_info[element] = self.cnt_list.count(element)
        return count_info

    def _check_detailed_errors(self, datas: List, count_info: Dict[str, int]):
        """세부 에러 검사"""
        for i, field in enumerate(self.check_list):
            field_matched = False

            for data in datas:
                for raw_data in data[0]:
                    if field[1] == raw_data[1]:
                        field_matched = True

                        if raw_data[-1] is True:
                            # 성공한 경우 카운트 증가
                            self._increment_success_count(i)
                        else:
                            # 실패한 경우 에러 추가
                            self._add_detailed_error(field, raw_data)

            if not field_matched:
                # 매칭되지 않은 필드는 누락 에러
                self._add_missing_field_error(field)

    def _increment_success_count(self, field_index: int):
        """성공 카운트 증가"""
        if not isinstance(self.check_list[field_index][-1], int):
            self.check_list[field_index][-1] = 1
        else:
            self.check_list[field_index][-1] += 1

    def _add_detailed_error(self, field: List, raw_data: List):
        """세부 에러 추가"""
        field_name = field[1]
        field_type = field[-2]

        if field_type == dict:
            self._add_dict_error(field)
        elif field_type == list:
            self._add_list_error(field)
        else:
            error_msg = f"Type mismatch for {field_name}: {raw_data[-1]}"
            self.check_errors.append([field[0], field_name, error_msg])

    def _add_dict_error(self, field: List):
        """딕셔너리 타입 에러 추가"""
        field_name = field[1]
        error_msg = f"Data Type Error: {field_name} expected dict"
        self.check_errors.append([field[0], field_name, error_msg])

        # 하위 필드들도 누락 에러로 추가
        if isinstance(field[-1], dict):
            for key in field[-1]:
                key_name = self._extract_key_name(key)
                if self._should_check_optional_key(key):
                    sub_error = f"Missing Key Error: {[field_name, key_name]}"
                    self.check_errors.append([field[0], [field_name, key_name], sub_error])

    def _add_list_error(self, field: List):
        """리스트 타입 에러 추가"""
        field_name = field[1]
        error_msg = f"Data Type Error: {field_name} expected list"
        self.check_errors.append([field[0], field_name, error_msg])

        # 리스트 아이템의 하위 필드들도 처리
        if isinstance(field[-1], list) and field[-1] and isinstance(field[-1][0], dict):
            for key, value in field[-1][0].items():
                key_name = self._extract_key_name(key)
                if self._should_check_optional_key(key):
                    sub_error = f"Missing Key Error: {[field_name, key_name]}"
                    self.check_errors.append([field[0], [field_name, key_name], sub_error])

                    # 중첩된 딕셔너리 처리
                    if isinstance(value, dict):
                        self._add_nested_dict_errors(field, field_name, key_name, value)

    def _add_nested_dict_errors(self, field: List, parent_name: str, key_name: str, nested_dict: Dict):
        """중첩된 딕셔너리 에러 추가"""
        for nested_key in nested_dict:
            nested_key_name = self._extract_key_name(nested_key)
            if self._should_check_optional_key(nested_key):
                sub_error = f"Missing Key Error: {[parent_name, key_name, nested_key_name]}"
                self.check_errors.append([field[0], [parent_name, key_name, nested_key_name], sub_error])

    def _add_missing_field_error(self, field: List):
        """누락된 필드 에러 추가"""
        field_name = field[1]
        error_msg = f"Missing Key Error: {field_name}"
        self.check_errors.append([field[0], field_name, error_msg])

    def _check_missing_keys(self, count_info: Dict[str, int], opt_field: List):
        """누락된 키 검사"""
        for field in self.check_list:
            if self._should_check_missing_key(field, count_info, opt_field):
                self._add_missing_key_error(field)

    def _should_check_missing_key(self, field: List, count_info: Dict[str, int], opt_field: List) -> bool:
        """누락된 키를 검사해야 하는지 확인"""
        # Optional 필드이고 flag_opt가 False인 경우 제외
        if not self.flag_opt and any(field[1] in tmp for tmp in opt_field):
            return False

        # 이미 에러가 있는 필드는 제외
        for error in self.check_errors:
            if error[1] == field[1]:
                return False

        # 타입별 검사 필요성 판단
        field_type = type(field[-1])
        if field_type in [type, dict, list]:
            return True

        return False

    def _add_missing_key_error(self, field: List):
        """누락된 키 에러 추가"""
        field_name = field[1]
        error_msg = f"Missing Key Error: {field_name}"

        # 중복 에러 체크
        if not self._error_already_exists(field_name):
            self.check_errors.append([field[0], field_name, error_msg])

    def _error_already_exists(self, field_name) -> bool:
        """에러가 이미 존재하는지 확인"""
        for error in self.check_errors:
            if error[1] == field_name:
                return True
        return False

    def _extract_key_name(self, key: Any) -> str:
        """키 이름 추출 (OptionalKey 처리)"""
        if isinstance(key, json_checker.core.checkers.OptionalKey):
            key_str = str(key)
            return key_str[12:-1]  # "OptionalKey(" 제거
        return str(key)

    def _should_check_optional_key(self, key: Any) -> bool:
        """Optional 키를 체크해야 하는지 확인"""
        is_optional = isinstance(key, json_checker.core.checkers.OptionalKey)

        if is_optional and self.flag_opt:
            return True
        elif not is_optional:
            return True

        return False

    def _generate_result(self) -> Tuple[str, str, int, int]:
        """최종 결과 생성"""
        # 에러 필드 중복 제거
        error_fields = []
        for error in self.check_errors:
            if error[1] not in error_fields:
                error_fields.append(error[1])

        # 에러 메시지 생성
        error_message = "\n".join([error[-1] for error in self.check_errors])

        # 카운트 계산
        error_count = len(error_fields)
        correct_count = len(self.check_list) - error_count

        if error_count == 0:
            return "PASS", "PASS", len(self.check_list), 0
        else:
            return "FAIL", error_message, correct_count, error_count


# 기존 함수와 호환성을 위한 래퍼 함수
def do_checker(all_field: List, datas: List, opt_field: List, flag_opt: bool = True) -> Tuple[str, str, int, int]:
    """
    기존 do_checker 함수와 동일한 인터페이스 제공

    Args:
        all_field: 스키마 필드 정보
        datas: 검증할 데이터
        opt_field: 선택적 필드 정보
        flag_opt: 선택적 필드 검사 여부

    Returns:
        (결과상태, 에러메시지, 성공개수, 실패개수)
    """
    checker = DataChecker(flag_opt)
    return checker.do_checker(all_field, datas, opt_field, flag_opt)

def _is_seq(x):
    return isinstance(x, Sequence) and not isinstance(x, (str, bytes, bytearray))

def _normalize_key(k):
    # OptionalKey("foo") -> "foo", 일반 문자열 키는 그대로
    return getattr(k, "expected_data", k)

def _make_path(parent_path, key_str):
    # 원 코드처럼 중첩 리스트 경로 유지
    return key_str if parent_path is None else [parent_path, key_str]

def field_finder(schema: Mapping):
    """
    입력: dict 형태의 스키마 (OptionalKey 포함 가능)
    출력:
      - all_field: 각 단계(step)의 필드 레코드 목록을 담은 리스트. 각 단계는 [fields]로 감싸짐.
                   fields의 원소는 [step, path, kind, payload]
                     * kind: dict / list / 스칼라 타입(type 객체) / "OPT"
                     * path: "키" 또는 ["부모경로", "키"] 형태로 중첩
      - fields_opt: 선택(옵션) 필드만 모은 동일 포맷의 레코드 리스트
    """
    if not isinstance(schema, Mapping):
        raise TypeError("schema must be a Mapping (dict-like)")

    all_field = []
    fields_opt = []

    def add_record(step, path, kind, payload, is_opt):
        rec = [step, path, ("OPT" if is_opt else kind), payload]
        return rec

    # step 0: 최상위 dict만 처리
    step = 0
    fields = []
    for k, v in schema.items():
        key_str = _normalize_key(k)
        is_opt = (key_str is not k)  # OptionalKey면 True
        path = _make_path(None, key_str)

        if isinstance(v, Mapping):
            rec = add_record(step, path, dict, v, is_opt)
        elif _is_seq(v):
            # 원 코드처럼 리스트 요소별로 모두 push (빈 리스트면 비어있는 리스트를 payload로)
            if len(v) == 0:
                rec = add_record(step, path, list, [], is_opt)
                fields.append(rec)
                if is_opt: fields_opt.append(rec[:])
            else:
                for elem in v:
                    rec = add_record(step, path, list, elem, is_opt)
                    fields.append(rec)
                    if is_opt: fields_opt.append(rec[:])
                continue  # 이미 append 완료
        else:
            # 스칼라(타입 혹은 기본값)
            rec = add_record(step, path, (v if not is_opt else "OPT"), v, is_opt)

        fields.append(rec)
        if is_opt:
            fields_opt.append(rec[:])

    all_field.append([fields])

    # 이후 단계: 직전 단계의 컨테이너를 펼치기 (BFS/레벨 순회)
    while True:
        prev_fields = all_field[step][0]  # 직전 단계
        step += 1
        fields = []

        for pf in prev_fields:
            _, parent_path, kind_or_opt, payload = pf
            parent_is_opt = (kind_or_opt == "OPT")

            # dict를 펼치기
            if isinstance(payload, Mapping):
                for ck, cv in payload.items():
                    child_key = _normalize_key(ck)
                    child_is_opt = parent_is_opt or (child_key is not ck)
                    child_path = _make_path(parent_path, child_key)

                    if isinstance(cv, Mapping):
                        rec = add_record(step, child_path, dict, cv, child_is_opt)
                    elif _is_seq(cv):
                        if len(cv) == 0:
                            rec = add_record(step, child_path, list, [], child_is_opt)
                            fields.append(rec)
                            if child_is_opt: fields_opt.append(rec[:])
                            continue
                        else:
                            for elem in cv:
                                rec = add_record(step, child_path, list, elem, child_is_opt)
                                fields.append(rec)
                                if child_is_opt: fields_opt.append(rec[:])
                            continue
                    else:
                        rec = add_record(step, child_path, (cv if not child_is_opt else "OPT"), cv, child_is_opt)

                    fields.append(rec)
                    if child_is_opt:
                        fields_opt.append(rec[:])

            # list를 펼치기 (요소가 dict/list면 더 내려감, 스칼라면 해당 단계에서 멈춤)
            elif _is_seq(payload):
                for elem in (payload if len(payload) > 0 else []):
                    # 리스트 요소에는 키가 없으므로, 경로에 "[]" 같은 마커를 한 단계 넣어 구분
                    child_path = _make_path(parent_path, "[]")
                    child_is_opt = parent_is_opt

                    if isinstance(elem, Mapping):
                        rec = add_record(step, child_path, dict, elem, child_is_opt)
                    elif _is_seq(elem):
                        rec = add_record(step, child_path, list, elem, child_is_opt)
                    else:
                        rec = add_record(step, child_path, (elem if not child_is_opt else "OPT"), elem, child_is_opt)

                    fields.append(rec)
                    if child_is_opt:
                        fields_opt.append(rec[:])

        if fields:
            all_field.append([fields])
        else:
            break

    return all_field, fields_opt

# 실제 데이터에서 필드 추출하기
def data_finder(schema_):
    """
    입력: dict 기반 스키마(중첩 dict/list 포함, OptionalKey 허용)
    출력: all_field
      - all_field[step] == [fields]
      - fields[i] == [step, path, kind, payload]
        * path: "키" 또는 ["부모경로", "키"] / 리스트 요소는 "[]"
        * kind: dict / list / (스칼라: 예컨대 str, int 등)
        * payload: 그 단계의 실제 객체(하위 펼침의 재료)
    """
    if not isinstance(schema_, Mapping):
        raise TypeError("schema_ must be a Mapping (dict-like).")

    all_field = []
    step = 0

    # === step 0: 최상위 필드 수집 ===
    fields = []
    for k, v in schema_.items():
        key_str = _normalize_key(k)
        path = _make_path(None, key_str)

        if isinstance(v, Mapping):
            fields.append([step, path, dict, v])
        elif _is_seq(v):
            if len(v) == 0:
                # 빈 리스트도 한 레코드로 표현
                fields.append([step, path, list, []])
            else:
                # 리스트는 요소 단위로 레코드 생성
                for elem in v:
                    fields.append([step, path, list, elem])
        else:
            # 스칼라(타입/기본값). 원 코드처럼 값 자체를 kind에 두는 패턴 유지
            fields.append([step, path, v, v])

    all_field.append([fields])

    # === 이후 단계: 이전 단계의 payload를 펼치기 (BFS) ===
    while True:
        prev_fields = all_field[step][0]
        step += 1
        fields = []

        for pf in prev_fields:
            _, parent_path, kind, payload = pf

            if isinstance(payload, Mapping):
                for ck, cv in payload.items():
                    child_key = _normalize_key(ck)
                    child_path = _make_path(parent_path, child_key)

                    if isinstance(cv, Mapping):
                        fields.append([step, child_path, dict, cv])
                    elif _is_seq(cv):
                        if len(cv) == 0:
                            fields.append([step, child_path, list, []])
                        else:
                            for elem in cv:
                                fields.append([step, child_path, list, elem])
                    else:
                        fields.append([step, child_path, cv, cv])

            elif _is_seq(payload):
                # 리스트 요소는 키가 없으므로 "[]" 마커를 경로에 추가
                if len(payload) == 0:
                    # 이미 상위에서 빈 리스트로 표현했으므로 더 펼칠 내용 없음
                    pass
                else:
                    for elem in payload:
                        child_path = _make_path(parent_path, "[]")
                        if isinstance(elem, Mapping):
                            fields.append([step, child_path, dict, elem])
                        elif _is_seq(elem):
                            fields.append([step, child_path, list, elem])
                        else:
                            fields.append([step, child_path, elem, elem])

            else:
                # 스칼라는 더 펼칠 내용 없음
                pass

        if fields:
            all_field.append([fields])
        else:
            break

    return all_field

def timeout_field_finder(schema):

    schema = pd.DataFrame([schema])  # , index=[0])
    all_field = []
    fields = []
    fields_opt = []
    step = 0

    for key, value in schema.items():
        if step == 0:
            try:
                if key[-4:] == "List" or key[-4:] == "port":
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
                        if key[-4:] == "List" or key[-4:] == "port":
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
                        elif key[-4:] == "List" or key[-4:] == "port":
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
                                    elif key2[-4:] == "List" or key2[-4:] == "port":
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



        if len(fields) != 0:
            all_field.append([fields])
        else:
            break


    all_field_cnt = len(all_field[0][0])
    fields_opt_cnt = len(fields_opt)

    for fields_tmp in all_field[0][0]:


        if type(fields_tmp) == list and type(fields_tmp[-1]) == list:

            for field_tmp in fields_tmp[-1]:
                if type(field_tmp) == list:
                    all_field_cnt += len(field_tmp)
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