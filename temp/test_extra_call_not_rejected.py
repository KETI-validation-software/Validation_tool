# -*- coding: utf-8 -*-
"""
여분 호출 처리 회귀 시험 — api/api_server.Server._numbered_or_base

시나리오에 한 단계만 등록된 API를 상대가 두 번 호출하면, 예전에는 이름을
'X2'로 바꿨다가 목록에서 못 찾아 404 '호출 횟수 초과'를 냈다.
한도의 근거인 num_retries는 부하시험 동시 사용자 수(기본 1)라서,
보내는 쪽·받는 쪽 시나리오 설정이 다르면 그대로 어긋났다.

결정(2026-09-02): 여분 호출도 정상 응답하되 채점은 첫 회차만 반영한다.
→ 등록되지 않은 번호 이름이면 기본 이름으로 되돌린다.

실행: .venv\Scripts\python.exe temp\test_extra_call_not_rejected.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_server import Server


def _with_message(names):
    Server.message = list(names)


def test_registered_number_is_used():
    """시나리오에 X2가 있으면 번호 이름을 그대로 쓴다 (회차 구분 유지)"""
    _with_message(["Authentication", "PtzStatus", "PtzStatus2"])
    assert Server._numbered_or_base("PtzStatus2", "PtzStatus") == "PtzStatus2"
    print("✅ 등록된 번호는 유지")


def test_unregistered_number_falls_back():
    """X2가 없으면 기본 이름으로 되돌린다 (404 대신 정상 응답)"""
    _with_message(["Authentication", "PtzStatus"])
    assert Server._numbered_or_base("PtzStatus2", "PtzStatus") == "PtzStatus"
    print("✅ 미등록 번호는 기본 이름으로 폴백")


def test_third_call_also_falls_back():
    """3번째 호출도 마찬가지 (X2까지만 등록된 경우)"""
    _with_message(["PtzStatus", "PtzStatus2"])
    assert Server._numbered_or_base("PtzStatus3", "PtzStatus") == "PtzStatus"
    assert Server._numbered_or_base("PtzStatus2", "PtzStatus") == "PtzStatus2"
    print("✅ 등록된 데까지만 번호 사용")


def test_no_message_list():
    """목록이 비어 있거나 없어도 예외 없이 기본 이름"""
    Server.message = []
    assert Server._numbered_or_base("PtzStatus2", "PtzStatus") == "PtzStatus"
    Server.message = None
    assert Server._numbered_or_base("PtzStatus2", "PtzStatus") == "PtzStatus"
    print("✅ 목록 없음 안전 처리")


def test_no_404_for_extra_call():
    """폴백된 이름은 끝에 숫자가 없어 404 경로를 타지 않는다"""
    import re
    _with_message(["PtzStatus"])
    resolved = Server._numbered_or_base("PtzStatus2", "PtzStatus")
    # api_res()의 404 판정: 이름 끝에 숫자가 붙어 있으면 '호출 횟수 초과'
    assert not re.match(r"^(.*?)(\d+)$", resolved), f"404 경로를 탐: {resolved}"
    assert resolved in Server.message, "목록에 없으면 API를 찾을 수 없음 404"
    print("✅ 여분 호출이 404로 떨어지지 않음")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed += 1
            print(f"❌ {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} 통과")
    sys.exit(1 if failed else 0)
