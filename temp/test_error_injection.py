# -*- coding: utf-8 -*-
"""
오류 주입(유도) 회귀 시험 — core/data_mapper.py

시험 기준(2026-08-16 "오류 처리 케이스 정리")의 주입 방법과 코드가 맞는지 확인한다.
  ② 필수 필드 누락  → 400   remove_required_field
  ③ 자료형 불일치   → 400   change_random_field_type (범위 제한 포함)
  ④ 유효 값 위반    → 400   violate_valid_value
  ⑦ 미등록 장치 ID  → 404   use_unknown_device_id

실행: .venv\Scripts\python.exe temp\test_error_injection.py
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.CONSTANTS as CONSTANTS
from core.data_mapper import ConstraintDataGenerator


# 실제 규격(ac003 RealtimeDoorStatus)과 같은 형태 — 컨테이너와 잎이 함께 들어 있다
CONSTRAINTS = {
    "doorList": {"valueType": "preset", "required": True},
    "doorList.doorID": {"valueType": "response-based", "required": True},
    "duration": {"valueType": "preset", "required": False},
    "transProtocol": {"valueType": "preset", "required": True},
    "transProtocol.transProtocolType": {
        "required": True,
        "validValues": ["LongPolling", "Webhook"],
    },
    "maxCount": {"required": False, "validValues": [10, 20]},
}

REQUEST = {
    "doorList": [{"doorID": "door0001"}, {"doorID": "door0002"}],
    "duration": 200,
    "transProtocol": {"transProtocolType": "LongPolling"},
    "maxCount": 10,
}

gen = ConstraintDataGenerator({})


def test_missing_required_field():
    """② 필수 잎 필드를 지운다. 컨테이너(doorList)를 통째로 지우면 안 된다."""
    out, path = gen.remove_required_field(REQUEST, CONSTRAINTS)
    assert path == "doorList.doorID", f"필수 잎이 아닌 {path}를 골랐음"
    assert out["doorList"] == [{}, {}], f"모든 줄에서 지워지지 않음: {out['doorList']}"
    assert "duration" in out, "선택 필드까지 지워짐"
    assert REQUEST["doorList"][0]["doorID"] == "door0001", "원본이 훼손됨"
    print("✅ ② 필수 필드 누락 — doorList[].doorID 제거, 컨테이너·선택 필드 보존")


def test_invalid_value_violation():
    """④ 허용 값 목록 밖의 값을 넣는다."""
    out, path = gen.violate_valid_value(REQUEST, CONSTRAINTS)
    assert path == "transProtocol.transProtocolType", f"엉뚱한 필드 선택: {path}"
    bad = out["transProtocol"]["transProtocolType"]
    assert bad not in ["LongPolling", "Webhook"], f"허용 값이 그대로 들어감: {bad}"
    print(f"✅ ④ 유효 값 위반 — transProtocolType → {bad!r}")


def test_invalid_value_respects_required_scope():
    """④ 필수 범위에서는 선택 필드에 주입하지 않는다."""
    opt_only = {"eventFilter": {"required": False, "validValues": ["인증성공", "인증실패"]}}
    data = {"eventFilter": "인증성공"}

    out, path = gen.violate_valid_value(data, opt_only, include_optional=False)
    assert path is None and out == data, "필수 범위인데 선택 필드를 건드림"

    out, path = gen.violate_valid_value(data, opt_only, include_optional=True)
    assert path == "eventFilter" and out["eventFilter"] != "인증성공"
    print("✅ ④ 범위 준수 — 필수 범위에서는 선택 필드 제외, 전체 범위에서는 주입")


def test_unknown_device_id():
    """⑦ 장치 ID를 목록에 없는 값으로 바꾼다 (리스트 안쪽까지)."""
    out, field = gen.use_unknown_device_id(REQUEST)
    assert field == "doorID", f"장치 ID를 못 찾음: {field}"
    assert [d["doorID"] for d in out["doorList"]] == ["door9999", "door9999"]
    assert out["duration"] == 200, "다른 필드가 바뀜"
    print("✅ ⑦ 미등록 장치 ID — doorID → door9999")


def test_unknown_device_id_all_kinds():
    data = {"camID": "cam0001", "sensorDeviceList": [{"sensorDeviceID": "iot0001"}]}
    out, _ = gen.use_unknown_device_id(data)
    assert out["camID"] == "cam9999"
    assert out["sensorDeviceList"][0]["sensorDeviceID"] == "iot9999"
    print("✅ ⑦ camID·sensorDeviceID도 동일하게 처리")


def test_type_mismatch_respects_required_scope():
    """③ 필수 범위에서는 선택 필드(duration, maxCount)를 절대 고르지 않는다."""
    for _ in range(60):
        out = gen.change_random_field_type(REQUEST, CONSTRAINTS, include_optional=False)
        assert out["duration"] == 200, f"선택 필드 duration이 변조됨: {out['duration']}"
        assert out["maxCount"] == 10, f"선택 필드 maxCount가 변조됨: {out['maxCount']}"
    print("✅ ③ 범위 준수 — 필수 범위에서 선택 필드는 변조 대상 제외 (60회 확인)")


def test_type_mismatch_full_scope_can_touch_optional():
    """전체 범위에서는 선택 필드도 대상이 된다"""
    touched = False
    for _ in range(200):
        out = gen.change_random_field_type(REQUEST, CONSTRAINTS, include_optional=True)
        if out["duration"] != 200 or out["maxCount"] != 10:
            touched = True
            break
    assert touched, "전체 범위인데 선택 필드가 한 번도 안 걸림"
    print("✅ ③ 전체 범위에서는 선택 필드도 변조 대상")


def test_type_mismatch_empty_payload():
    """빈 요청에서 4개짜리 튜플을 돌려주던 버그(호출부는 dict를 기대) 회귀"""
    out = gen.change_random_field_type({})
    assert isinstance(out, dict), f"dict가 아닌 {type(out).__name__} 반환"
    print("✅ ③ 빈 요청이어도 dict 반환 (튜플 반환 버그 회귀)")


def test_dispatcher_defaults():
    """기대 코드별 기본 주입 방법"""
    CONSTANTS.ENABLE_ERROR_REQUEST_MUTATION = True
    base = {"timePeriod": {"startTime": "20260517163010123", "endTime": "20260617163010123"},
            "doorList": [{"doorID": "door0001"}]}

    out = gen._applied_codevalue(copy.deepcopy(base), "201")
    assert out["timePeriod"]["startTime"] == "0", "201 → startTime 변조 안 됨"

    out = gen._applied_codevalue(copy.deepcopy(base), "404")
    assert out["doorList"][0]["doorID"] == "door9999", "404 → 미등록 ID 변조 안 됨"

    out = gen._applied_codevalue(copy.deepcopy(base), "200")
    assert out == base, "200인데 변조됨"

    out = gen._applied_codevalue(copy.deepcopy(base), "403")
    assert out == base, "403은 본문을 건드리지 않아야 함(헤더에서 처리)"
    print("✅ 기대 코드별 기본 주입 — 201·404 동작, 200·403은 본문 유지")


def test_dispatcher_explicit_method():
    """관리도구가 주입 방법을 내려줄 때를 대비한 method 지정"""
    CONSTANTS.ENABLE_ERROR_REQUEST_MUTATION = True

    out = gen._applied_codevalue(REQUEST, "400", CONSTRAINTS, method="missing-required")
    assert out["doorList"] == [{}, {}], "method=missing-required가 안 먹음"

    out = gen._applied_codevalue(REQUEST, "400", CONSTRAINTS, method="invalid-value")
    assert out["transProtocol"]["transProtocolType"] not in ["LongPolling", "Webhook"]
    print("✅ method 지정 — 400에서 ②·④를 골라 쓸 수 있음")


def test_switch_off():
    CONSTANTS.ENABLE_ERROR_REQUEST_MUTATION = False
    try:
        out = gen._applied_codevalue(REQUEST, "404", CONSTRAINTS)
        assert out == REQUEST, "스위치를 껐는데 변조됨"
    finally:
        CONSTANTS.ENABLE_ERROR_REQUEST_MUTATION = True
    print("✅ ENABLE_ERROR_REQUEST_MUTATION=False → 주입 안 함")


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
