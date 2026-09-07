# -*- coding: utf-8 -*-
"""
2026-09-07 실측 회귀 — 문자열 경계 TypeError + request-array-based 미처리

① range-match(직접) 경계 TypeError
   관리도구가 17자리 시각을 String으로 내리면서 rangeMin/rangeMax도 문자열이
   됐다. 값은 숫자로 바꿔 쓰는데 경계는 그대로여서 int와 str을 비교하다
   TypeError가 났고, 그 예외로 의미 검증 전체가 건너뛰어져
   camList.camID 실패가 있던 회차가 100점으로 통과했다.

② valueType 'request-array-based' 미처리
   우리 코드의 처리 목록에 없어 값이 한 번도 안 채워졌다.
   → camID·eventName이 빈 값("")으로 전송됨.

실행: .venv\Scripts\python.exe temp\test_string_bounds_and_array_type.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.functions import _validate_range_match_direct, json_check_  # noqa: E402
from core.data_mapper import ConstraintDataGenerator as G  # noqa: E402


def _run(rule, value):
    errs, gerrs = [], []
    ok = _validate_range_match_direct("startTime", value, rule, errs, gerrs)
    return ok, errs


# ---------- ① 문자열 경계 ----------

def test_string_bounds_no_typeerror():
    """경계가 문자열이어도 예외 없이 판정한다"""
    rule = {"rangeOperator": "greater-equal", "rangeMin": "20260822163010124"}
    ok, errs = _run(rule, "20260907143457306")     # 기준보다 뒤 → 통과
    assert ok, errs
    ok, errs = _run(rule, "20260101000000000")     # 기준보다 앞 → 실패
    assert not ok and errs, errs
    print("✅ 문자열 경계 — TypeError 없이 판정")


def test_string_bounds_between():
    """between도 문자열 경계로 동작"""
    rule = {"rangeOperator": "between",
            "rangeMin": "20260817163010124", "rangeMax": "20260822163010124"}
    assert _run(rule, "20260820000000000")[0]
    assert not _run(rule, "20260901000000000")[0]
    print("✅ between 문자열 경계")


def test_numeric_bounds_still_work():
    """숫자 경계 기존 동작 유지"""
    rule = {"rangeOperator": "between", "rangeMin": 100, "rangeMax": 200}
    assert _run(rule, 150)[0]
    assert not _run(rule, 250)[0]
    print("✅ 숫자 경계 유지")


def test_17digit_precision_direct():
    """17자리 1ms 차이 구분 (float 변환 시 뭉개짐)"""
    rule = {"rangeOperator": "greater-than", "rangeMin": "20260907143457306"}
    assert _run(rule, "20260907143457307")[0], "1ms 뒤인데 실패"
    assert not _run(rule, "20260907143457305")[0], "1ms 앞인데 통과"
    print("✅ 17자리 1ms 정밀도")


def test_no_silent_pass_on_string_bounds():
    """예전에 100점 오탐을 만든 상황이 이제 정상 판정된다"""
    schema = {"startTime": str}
    rules = {"startTime": {"enabled": True, "validationType": "range-match",
                           "rangeOperator": "greater-equal",
                           "rangeMin": "20260822163010124"}}
    r = json_check_(schema, {"startTime": "20260101000000000"}, False,
                    validation_rules=rules)
    assert r[0] == "FAIL", f"실패해야 하는데 {r[0]} (통과 {r[2]}, 실패 {r[3]})"
    print(f"✅ 문자열 경계 위반 → {r[0]} (예전엔 예외로 전 필드 자동통과)")


# ---------- ② request-array-based ----------

def test_array_type_in_lists():
    """valueType 목록에 request-array-based가 들어 있다"""
    assert "request-array-based" in G.REQUEST_BASED_TYPES, G.REQUEST_BASED_TYPES
    assert "request-array-based" in G.VALUE_PICK_TYPES, G.VALUE_PICK_TYPES
    assert "request-based" in G.REQUEST_BASED_TYPES
    print("✅ request-array-based 처리 목록 포함")


def test_array_type_reads_request_event():
    """요청 이벤트에서 값을 가져온다 (응답이 아니라)"""
    gen = G.__new__(G)
    gen.unrunnable_reason = None
    gen.latest_events = {"RealtimeVideoEventInfos": {
        "REQUEST": {"data": {"camList": [{"camID": "cam0001"}, {"camID": "cam0002"}]}},
        "RESPONSE": {"data": {"camList": [{"camID": "WRONG"}]}},
    }}
    cons = {"camList.camID": {"valueType": "request-array-based",
                              "referenceEndpoint": "/RealtimeVideoEventInfos",
                              "referenceField": "camID"}}
    cmap = gen._build_constraint_map(cons, {}, api_name="RealtimeVideoEventInfos")
    got = cmap["camList.camID"]["values"]
    assert got == ["cam0001", "cam0002"], got
    print(f"✅ 요청 이벤트에서 값 수집: {got}")


def test_array_type_fills_template():
    """템플릿의 빈 값이 실제로 채워진다"""
    gen = G.__new__(G)
    cmap = {"camList.camID": {"type": "request-array-based",
                              "values": ["cam0001", "cam0002"]}}
    out = gen._generate_from_template(
        {"camList": [{"camID": "", "eventUUID": "event01"}]}, cmap)
    filled = [c["camID"] for c in out["camList"]]
    assert filled and all(v for v in filled), f"빈 값이 남음: {out}"
    assert set(filled) <= {"cam0001", "cam0002"}, filled
    print(f"✅ 템플릿 채움: camID={filled}")


def test_unselected_reference_still_empty():
    """참조 필드가 '(참조 필드 미선택)'이면 여전히 채우지 않는다 (관리도구 설정 문제)"""
    gen = G.__new__(G)
    gen.unrunnable_reason = None
    gen.latest_events = {"X": {"REQUEST": {"data": {"camList": [{"camID": "cam0001"}]}}}}
    cons = {"camList.camID": {"valueType": "request-array-based",
                              "referenceEndpoint": "/X",
                              "referenceField": "(참조 필드 미선택)"}}
    cmap = gen._build_constraint_map(cons, {}, api_name="X")
    assert not cmap.get("camList.camID", {}).get("values"), cmap
    print("✅ 참조 필드 미선택은 그대로 (관리도구에서 지정해야 함)")


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
