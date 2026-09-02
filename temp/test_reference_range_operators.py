# -*- coding: utf-8 -*-
"""
참조 기반 범위 검증 회귀 시험 — core/functions._validate_range_match
(validationType: request-field-range-match)

2026-09-02 실측으로 드러난 버그 3건:
  ① 연산자 키를 referenceRangeOperator로만 읽어, 관리도구가 보내는
     rangeOperator를 못 찾고 늘 기본값 between으로 떨어졌다.
  ② between 외 연산자가 미구현이라 '이상'으로 설정하면 max가 없다며 실패.
  ③ 리스트 요소가 int/float가 아니면 조용히 건너뛰어, 17자리 시각(문자열)
     배열이 검증 없이 통과했다 (ReplayURL이 검증 없이 100점).

실행: .venv\Scripts\python.exe temp\test_reference_range_operators.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.functions import _validate_range_match

START = "20260817191012000"
END_OK = "20260822161012000"      # start 이후
END_BAD = "20260810000000000"     # start 이전

CTX = {"/StoredVideoEventInfos": {"timePeriod": {"startTime": START}}}


def _rule(operator, **extra):
    r = {"validationType": "request-field-range-match",
         "rangeOperator": operator,
         "referenceFieldMin": "startTime",
         "referenceEndpointMin": "/StoredVideoEventInfos"}
    r.update(extra)
    return r


def _run(rule, value, ctx=CTX):
    errs, gerrs = [], []
    ok = _validate_range_match("timePeriod.endTime", value, rule, ctx, errs, gerrs)
    return ok, errs


def test_greater_equal_passes():
    """이상: start 이후 값은 통과 (max 없이도 판정)"""
    ok, errs = _run(_rule("greater-equal"), END_OK)
    assert ok, errs
    print("✅ greater-equal 통과")


def test_greater_equal_fails():
    """이상: start 이전 값은 실패"""
    ok, errs = _run(_rule("greater-equal"), END_BAD)
    assert not ok and errs, errs
    assert "미만" in errs[0], errs
    print(f"✅ greater-equal 실패 판정: {errs[0]}")


def test_greater_equal_boundary():
    """이상: 경계값(= start)은 통과"""
    assert _run(_rule("greater-equal"), START)[0]
    assert not _run(_rule("greater-than"), START)[0], "초과는 경계값이 실패여야 함"
    print("✅ 경계값 처리 (이상 통과 / 초과 실패)")


def test_legacy_operator_key():
    """예전 키(referenceRangeOperator)도 계속 읽는다"""
    rule = {"validationType": "request-field-range-match",
            "referenceRangeOperator": "greater-equal",
            "referenceFieldMin": "startTime",
            "referenceEndpointMin": "/StoredVideoEventInfos"}
    assert _run(rule, END_OK)[0]
    print("✅ 예전 연산자 키 호환")


def test_string_list_is_validated():
    """문자열 시각 배열도 실제로 검증한다 (예전엔 조용히 통과)"""
    ok, errs = _run(_rule("greater-equal"), [END_BAD])
    assert not ok, "문자열 배열이 검증 없이 통과함"
    print(f"✅ 문자열 배열 검증: {errs[0]}")

    ok, _ = _run(_rule("greater-equal"), [END_OK])
    assert ok, "정상 값인데 실패"
    print("✅ 문자열 배열 정상값 통과")


def test_unconvertible_value_fails():
    """숫자로 못 바꾸는 값은 통과가 아니라 실패"""
    ok, errs = _run(_rule("greater-equal"), ["", "abc"])
    assert not ok and len(errs) >= 2, errs
    print("✅ 변환 불가 값 실패 처리")


def test_between_still_works():
    """between 기존 동작 유지"""
    ctx = {"/X": {"a": "100", "b": "200"}}
    rule = {"validationType": "request-field-range-match",
            "rangeOperator": "between",
            "referenceFieldMin": "a", "referenceEndpointMin": "/X",
            "referenceFieldMax": "b", "referenceEndpointMax": "/X"}
    assert _run(rule, "150", ctx)[0]
    assert not _run(rule, "250", ctx)[0]
    print("✅ between 기존 동작 유지")


def test_between_missing_bound_fails():
    """between인데 한쪽 경계가 없으면 실패 + 사유 명시"""
    ok, errs = _run(_rule("between"), END_OK)
    assert not ok and "구간 양끝" in errs[0], errs
    print(f"✅ between 경계 부족: {errs[0]}")


def test_unknown_operator_fails():
    """모르는 연산자는 조용히 통과시키지 않는다"""
    ok, errs = _run(_rule("weird-op"), END_OK)
    assert not ok and "지원하지 않는 연산자" in errs[0], errs
    print("✅ 미지원 연산자 실패 처리")


def test_17digit_precision():
    """17자리 시각은 정수로 비교 — 1ms 차이도 구분"""
    ctx = {"/X": {"a": "20260817191012000"}}
    rule = {"validationType": "request-field-range-match",
            "rangeOperator": "greater-than",
            "referenceFieldMin": "a", "referenceEndpointMin": "/X"}
    assert _run(rule, "20260817191012001", ctx)[0], "1ms 뒤인데 실패"
    assert not _run(rule, "20260817191011999", ctx)[0], "1ms 앞인데 통과"
    print("✅ 17자리 1ms 정밀도 유지")


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
