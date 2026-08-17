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


def make_server(enabled=True, schema=SCHEMA, in_con=None):
    """소켓을 열지 않고 판정 메서드만 쓰기 위한 최소 인스턴스"""
    srv = object.__new__(Server)
    srv.CONSTANTS = type("C", (), {"ENABLE_ERROR_RESPONSE_CHECK": enabled})
    srv.generator = ConstraintDataGenerator({})
    srv.message = ["StoredVerifEventInfos"]
    srv.inSchema = [schema]
    Server.inCon = [in_con] if in_con is not None else None
    Server.request_has_error = {}
    # 장치 목록은 시험마다 초기화 (비어 있으면 404 판정 안 함)
    Server.valid_ids_by_field = {"camID": set(), "doorID": set(), "sensorDeviceID": set()}
    return srv


def check(request_data, enabled=True, schema=SCHEMA, in_con=None, known_doors=None):
    srv = make_server(enabled, schema, in_con)
    if known_doors:
        Server.valid_ids_by_field["doorID"].update(known_doors)
    return srv._check_request_errors("StoredVerifEventInfos", request_data)


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


def test_missing_required_field_is_400():
    """② 필수 필드(endTime) 누락 → 400. 선택 필드(maxCount) 누락은 정상."""
    gen = ConstraintDataGenerator({})
    missing_required = {
        "timePeriod": {"startTime": "20251105163010124"},  # endTime 제거됨
        "doorList": [{"doorID": "door0001"}],
    }
    result = check(missing_required)
    assert result is not None and result["code"] == "400", f"400이 아님: {result}"

    missing_optional = {k: v for k, v in NORMAL_REQUEST.items() if k != "maxCount"}
    assert check(missing_optional) is None, "선택 필드 누락을 오류로 판정함"
    print("✅ ② 필수 필드 누락 → 400, 선택 필드 누락은 정상")


def test_invalid_value_is_400():
    """④ validValues 목록 밖 값 → 400 (요청 제약 기반, 중첩 경로 포함)"""
    in_con = {
        "eventFilter": {"required": False, "validValues": ["AuthSuccess", "AuthFail"]},
    }
    bad = dict(NORMAL_REQUEST, eventFilter="무단침입")
    result = check(bad, in_con=in_con)
    assert result is not None and result["code"] == "400", f"400이 아님: {result}"

    good = dict(NORMAL_REQUEST, eventFilter="AuthSuccess")
    assert check(good, in_con=in_con) is None, "허용 값인데 오류로 판정함"

    # 제약이 아예 없는 API(inCon=None)는 판정하지 않는다
    assert check(bad) is None, "제약이 없는데 유효 값 판정을 함"
    print("✅ ④ 유효 값 위반 → 400, 허용 값·제약 없음은 정상")


def test_unknown_device_is_404():
    """⑦ 프로필 목록에 없는 doorID → 404 (중첩 doorList.doorID까지)"""
    bad = {
        "timePeriod": dict(NORMAL_REQUEST["timePeriod"]),
        "doorList": [{"doorID": "door9999"}],
    }
    result = check(bad, known_doors={"door0001", "door0002"})
    assert result is not None and result["code"] == "404", f"404가 아님: {result}"
    assert result["message"] == "장치 없음"

    good = check(NORMAL_REQUEST, known_doors={"door0001", "door0002"})
    assert good is None, "등록된 장치인데 404로 판정함"
    print("✅ ⑦ 미등록 doorID → 404 장치 없음, 등록 장치는 정상")


def test_unknown_device_no_list_no_judgment():
    """⑦ 프로필 목록이 비어 있으면(조회 전) 판정하지 않는다 — 오탐 방지"""
    bad = {
        "timePeriod": dict(NORMAL_REQUEST["timePeriod"]),
        "doorList": [{"doorID": "door9999"}],
    }
    assert check(bad) is None, "목록이 없는데 404로 판정함(오탐)"
    print("✅ ⑦ 프로필 조회 전에는 404 판정 안 함 (오탐 방지)")


def test_profiles_response_fills_device_list():
    """프로필 응답이 나가면 장치 목록이 자동으로 채워진다"""
    srv = make_server()
    srv._update_valid_devices("DoorProfiles", {
        "code": "200",
        "doorList": [{"doorID": "door0001"}, {"doorID": "door0002"}],
    })
    srv._update_valid_devices("SensorDeviceProfiles", {
        "sensorDeviceList": [{"sensorDeviceID": "iot0001"}],
    })
    srv._update_valid_devices("StoredVerifEventInfos", {  # 프로필이 아니면 무시
        "doorList": [{"doorID": "doorXXXX"}],
    })
    assert Server.valid_ids_by_field["doorID"] == {"door0001", "door0002"}
    assert Server.valid_ids_by_field["sensorDeviceID"] == {"iot0001"}
    print("✅ 프로필 응답 → 장치 목록 자동 수집 (프로필 아닌 응답은 무시)")


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
