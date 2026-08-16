# -*- coding: utf-8 -*-
"""
오류 응답 판정(장치 역할) 회귀 시험 — api_server._check_request_errors

플랫폼 역할이 요청을 변조해 오류를 유도하면, 장치 역할이 그 요청을 판정해
오류 코드로 응답해야 한다. 유도 방식과 판정 기준이 짝이 맞는지 확인한다.

  startTime → 0 / "0" 변조   → 201 정보 없음
  임의 leaf의 타입 변조      → 400 잘못된 요청
  정상 요청                  → 오류 없음(None)

실행: .venv\Scripts\python.exe temp\test_error_response_check.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from json_checker import OptionalKey

from api.api_server import Server
from core.data_mapper import ConstraintDataGenerator


# 실제 규격(ac002 StoredVerifEventInfos)과 같은 중첩 구조
SCHEMA = {
    "timePeriod": {
        "startTime": str,
        "endTime": str,
    },
    "doorList": [{
        "doorID": str,
    }],
    OptionalKey("maxCount"): int,
}

NORMAL_REQUEST = {
    "timePeriod": {
        "startTime": "20251105163010124",
        "endTime": "20251115163010124",
    },
    "doorList": [{"doorID": "door0001"}],
    "maxCount": 10,
}


def make_server(enabled=True, schema=SCHEMA):
    """소켓을 열지 않고 판정 메서드만 쓰기 위한 최소 인스턴스"""
    srv = object.__new__(Server)
    srv.CONSTANTS = type("C", (), {"ENABLE_ERROR_RESPONSE_CHECK": enabled})
    srv.generator = ConstraintDataGenerator({})
    srv.message = ["StoredVerifEventInfos"]
    srv.inSchema = [schema]
    Server.request_has_error = {}
    return srv


def check(request_data, enabled=True, schema=SCHEMA):
    return make_server(enabled, schema)._check_request_errors(
        "StoredVerifEventInfos", request_data
    )


def test_normal_request_passes():
    assert check(NORMAL_REQUEST) is None, "정상 요청이 오류로 판정됨"
    print("✅ 정상 요청 → 오류 없음")


def test_string_zero_start_time_is_201():
    """시각 필드 String 전환 후에도 201이 잡혀야 한다 (이게 안 되면 오류 회차 전패)"""
    gen = ConstraintDataGenerator({})
    mutated = gen.replace_start_time(NORMAL_REQUEST)
    assert mutated["timePeriod"]["startTime"] == "0", "변조가 문자열 타입을 유지하지 않음"

    result = check(mutated)
    assert result is not None, "변조된 startTime을 판정하지 못함"
    assert result["code"] == "201", f"201이어야 하는데 {result['code']}"
    print("✅ startTime=\"0\"(String) → 201 정보 없음")


def test_number_zero_start_time_is_201():
    """Number 시각을 쓰는 옛 규격도 그대로 잡혀야 한다"""
    number_request = {
        "timePeriod": {"startTime": 20251105163010124, "endTime": 20251115163010124},
        "doorList": [{"doorID": "door0001"}],
    }
    gen = ConstraintDataGenerator({})
    mutated = gen.replace_start_time(number_request)
    assert mutated["timePeriod"]["startTime"] == 0, "변조가 숫자 타입을 유지하지 않음"

    number_schema = {
        "timePeriod": {"startTime": int, "endTime": int},
        "doorList": [{"doorID": str}],
    }
    result = check(mutated, schema=number_schema)
    assert result is not None and result["code"] == "201", f"201이 아님: {result}"
    print("✅ startTime=0(Number) → 201 정보 없음")


def test_nested_type_mutation_is_400():
    """중첩된 필드의 타입이 깨져도 잡혀야 한다 (최상위만 보면 놓친다)"""
    mutated = {
        "timePeriod": dict(NORMAL_REQUEST["timePeriod"]),
        "doorList": [{"doorID": 1234}],   # str이어야 하는데 int
        "maxCount": 10,
    }
    result = check(mutated)
    assert result is not None, "중첩 필드의 타입 오류를 놓침"
    assert result["code"] == "400", f"400이어야 하는데 {result['code']}"
    print("✅ doorList[0].doorID 타입 변조 → 400 잘못된 요청")


def test_optional_key_type_mutation_is_400():
    mutated = dict(NORMAL_REQUEST, maxCount="10")  # int여야 하는데 str
    result = check(mutated)
    assert result is not None and result["code"] == "400", f"400이 아님: {result}"
    print("✅ OptionalKey(maxCount) 타입 변조 → 400 잘못된 요청")


def test_201_wins_over_400():
    """startTime 변조는 형식은 유효하므로 400이 아니라 201로 나가야 한다"""
    gen = ConstraintDataGenerator({})
    mutated = gen.replace_start_time(NORMAL_REQUEST)
    result = check(mutated)
    assert result["code"] == "201", f"201이어야 하는데 {result['code']}"
    print("✅ startTime 변조는 400이 아니라 201로 판정")


def test_empty_schema_api_does_not_false_400():
    """요청 스키마가 빈 API(DoorProfiles 등)는 타입 검사를 건너뛴다"""
    assert check({"anything": 1}, schema={}) is None
    print("✅ 요청 스키마 없는 API → 오류 없음")


def test_switch_off_disables_everything():
    """롤백 스위치: False면 판정 자체를 안 한다"""
    gen = ConstraintDataGenerator({})
    mutated = gen.replace_start_time(NORMAL_REQUEST)
    assert check(mutated, enabled=False) is None, "스위치를 꺼도 오류를 판정함"
    print("✅ ENABLE_ERROR_RESPONSE_CHECK=False → 항상 정상 응답(이전 동작)")


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
