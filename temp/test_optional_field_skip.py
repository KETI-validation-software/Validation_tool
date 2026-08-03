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

# 필수 1 + 선택 1 짜리 최소 스키마
SCHEMA = {
    "code": str,
    OptionalKey("desc"): str,
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

    print("OK: 필수 필드 모드에서 선택 필드 완전 제외 확인")


if __name__ == "__main__":
    demo()
