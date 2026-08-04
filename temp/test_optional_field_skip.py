# -*- coding: utf-8 -*-
"""
필수 필드 모드(flag_opt=False)에서 선택 필드가 검증 대상에서 완전히 빠지는지 확인.

실행: python temp/test_optional_field_skip.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from json_checker import OptionalKey

import config.CONSTANTS as CONSTANTS
from core.functions import json_check_
from core.json_checker_new import get_flat_fields_from_schema

# 필수 1 + 선택 1 짜리 최소 스키마
SCHEMA = {
    "code": str,
    OptionalKey("desc"): str,
}

# 선택 필드가 원시 타입 배열인 경우 + 선택 컨테이너 하위의 조건부 필수
# (StoredObjectAnalyticsInfos 요청 형태)
ARRAY_SCHEMA = {
    "timePeriod": {
        "startTime": int,
    },
    OptionalKey("camList"): [{
        "camID": str,          # camList를 보냈다면 필수 = 조건부 필수
    }],
    OptionalKey("filterList"): [{
        OptionalKey("classFilter"): [str],
    }],
}


def run(flag_opt, data):
    """json_check_ 호출 (flag_opt는 CONSTANTS 단일 게이트라 직접 세팅)"""
    CONSTANTS.flag_opt = flag_opt
    return json_check_(SCHEMA, data, flag_opt)


def demo():
    saved = CONSTANTS.flag_opt
    try:
        # 1) 필수 모드 + 선택 필드 누락 → 선택 필드는 카운트에 아예 없음
        result, _, total_pass, total_err, opt_pass, opt_err = run(False, {"code": "200"})
        assert (total_pass, total_err) == (1, 0), f"필수만 1건이어야 함: {total_pass}/{total_err}"
        assert (opt_pass, opt_err) == (0, 0), f"선택 카운트가 남아있음: {opt_pass}/{opt_err}"
        assert result == "PASS", result

        # 2) 필수 모드 + 선택 필드에 틀린 타입 → 검증 대상이 아니므로 여전히 PASS
        result, _, total_pass, total_err, opt_pass, opt_err = run(False, {"code": "200", "desc": 12345})
        assert (total_pass, total_err) == (1, 0), f"선택 필드가 검증됨: {total_pass}/{total_err}"
        assert (opt_pass, opt_err) == (0, 0), f"선택 카운트가 남아있음: {opt_pass}/{opt_err}"
        assert result == "PASS", result

        # 3) 전체 모드에서는 기존대로 선택 필드가 잡혀야 함 (회귀 방지)
        result, _, total_pass, total_err, opt_pass, opt_err = run(True, {"code": "200", "desc": 12345})
        assert opt_err == 1, f"전체 모드인데 선택 필드 실패가 안 잡힘: {opt_pass}/{opt_err}"
        assert result == "FAIL", result
    finally:
        CONSTANTS.flag_opt = saved

    # 4) 선택 필드가 원시 배열이어도 선택으로 잡혀야 함
    #    (OptionalKey("classFilter"): [str] 가 "classFilter[]" 경로가 되면서
    #     선택 플래그를 잃고 필수로 등록되던 회귀 방지)
    flat, opt = get_flat_fields_from_schema(ARRAY_SCHEMA)
    assert "filterList.classFilter[]" in flat, sorted(flat)
    assert "filterList.classFilter[]" in opt, f"원시 배열 선택 필드가 필수로 잡힘: {sorted(opt)}"

    # 5) 선택 컨테이너 하위의 조건부 필수도 선택으로 잡혀야 함
    #    camList를 생략할 수 있는 이상 camID는 무조건 필수가 아님
    assert "camList.camID" in opt, f"선택 컨테이너 하위가 필수로 남음: {sorted(opt)}"

    required = [f for f in flat if f not in opt]
    assert sorted(required) == ["timePeriod", "timePeriod.startTime"], sorted(required)

    print("OK: 필수 필드 모드에서 선택 필드 완전 제외 확인")


if __name__ == "__main__":
    demo()
