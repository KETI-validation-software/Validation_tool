# -*- coding: utf-8 -*-
"""
request-range 빈 경계 회귀 시험 — core/data_mapper._pick_range_value

참조 대상이 비어 있으면 관리도구가 min/max를 빈 문자열("")로 내려준다.
빈 문자열도 str이라 "참조 있음"으로 판정돼 0~9999999999999 난수가 뽑혔고,
시각 자리에 13자리 숫자("8949495618687")가 나갔다 (2026-09-01 리허설 로그).

실행: .venv\Scripts\python.exe temp\test_request_range_blank_bound.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator as G


def _pick(constraint, template, sibling=None):
    return G._pick_range_value(G.__new__(G), constraint, template, sibling)


def test_blank_min_gives_17digit_time():
    """min이 빈 문자열 + 템플릿도 비었으면 현재 시각(17자리)을 쓴다"""
    out = _pick({"min": "", "max": 9999999999999}, "")
    assert isinstance(out, str) and len(out) == 17 and out.isdigit(), out
    assert G._parse_time17(out) is not None, f"달력에 없는 시각: {out}"
    print(f"✅ min 빈 문자열: {out}")


def test_blank_max_gives_17digit_time():
    """max가 빈 문자열이어도 마찬가지"""
    out = _pick({"min": 0, "max": ""}, "")
    assert len(str(out)) == 17, out
    assert G._parse_time17(out) is not None, out
    print(f"✅ max 빈 문자열: {out}")


def test_template_time_still_wins():
    """참조가 없어도 템플릿에 시각이 있으면 그 이후 값을 쓴다 (기존 동작)"""
    out = _pick({"min": "", "max": 9999999999999}, "20260817163010123")
    assert len(str(out)) == 17, out
    assert int(out) >= 20260817163010123, out
    print(f"✅ 템플릿 기준 유지: {out}")


def test_real_bounds_unchanged():
    """정상 경계는 그대로 구간 안에서 뽑는다 (판정 무변화)"""
    lo, hi = 20260817163010124, 20260822163010124
    for _ in range(20):
        out = _pick({"min": str(lo), "max": str(hi)}, "20260817163010123")
        assert isinstance(out, str), f"문자열 경계면 문자열로 나와야 함: {out!r}"
        assert lo <= int(out) <= hi, out
        assert G._parse_time17(out) is not None, out
    print("✅ 정상 경계 20회: 구간 내 실재 시각")


def test_numeric_range_still_random():
    """시각이 아닌 일반 숫자 구간은 예전처럼 난수 (시각 강제 아님)"""
    for _ in range(20):
        out = _pick({"min": 5, "max": 10}, 7)
        assert isinstance(out, int) and 5 <= out <= 10, out
    print("✅ 일반 숫자 구간 유지")


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
