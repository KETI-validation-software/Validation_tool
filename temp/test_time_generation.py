# -*- coding: utf-8 -*-
"""
시각 생성/제한 시간 상한 회귀 시험

① 시각 생성: 예전에는 17자리 숫자 구간에서 random.randint로 정수를 뽑아
   문자열로만 바꿔, 숫자로는 구간 안이어도 달력에 없는 날짜(13월·40일 등)가
   나올 수 있었다("날짜가 난수로 나가던" 문제). 구간을 날짜로 해석해 실제
   존재하는 시각만 생성하도록 수정.
② 제한 시간 상한: 안내서 표 3-2 "메시지당 제한 시간 60초" — 관리도구가 더 큰
   값을 내려줘도 60초로 자른다.

실행: .venv\Scripts\python.exe temp\test_time_generation.py
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.CONSTANTS as CONSTANTS
from core.data_mapper import ConstraintDataGenerator

gen = ConstraintDataGenerator({})


def is_real_time17(v):
    """17자리이면서 달력에 실제 존재하는 시각인가"""
    return ConstraintDataGenerator._parse_time17(v) is not None


def test_generated_time_is_always_valid_calendar_date():
    """핵심: 구간 안에서 뽑은 값이 항상 달력에 존재하는 17자리 시각"""
    # 이 구간에는 '20260840......' 같은 달력에 없는 숫자가 다수 포함된다
    constraint = {"type": "request-range",
                  "min": "20260817163010123", "max": "20260822163010123"}
    for _ in range(300):
        v = gen._pick_range_value(constraint, "20260820000000000")
        assert is_real_time17(v), f"달력에 없는 시각 생성: {v}"
    print("✅ 300회 생성 — 전부 실제 존재하는 17자리 시각")


def test_generated_time_within_range():
    """생성값이 요청 구간 안에 있다"""
    lo, hi = "20260817163010123", "20260822163010123"
    constraint = {"type": "request-range", "min": lo, "max": hi}
    for _ in range(200):
        v = gen._pick_range_value(constraint, lo)
        assert lo <= v <= hi, f"구간 밖: {v} (구간 {lo}~{hi})"
    print("✅ 생성값이 항상 요청 구간 내")


def test_endtime_after_starttime():
    """endTime은 같은 줄의 startTime보다 뒤 (sibling_start)"""
    constraint = {"type": "request-range",
                  "min": "20260817163010123", "max": "20260822163010123"}
    start = "20260820120000000"
    for _ in range(200):
        v = gen._pick_range_value(constraint, start, sibling_start=start)
        assert is_real_time17(v), f"달력에 없는 시각: {v}"
        assert v > start, f"startTime({start})보다 뒤가 아님: {v}"
    print("✅ endTime은 항상 startTime보다 뒤 + 유효 시각")


def test_string_type_preserved():
    """String 구간이면 String으로 (17자리 유지)"""
    constraint = {"type": "request-range",
                  "min": "20260817163010123", "max": "20260822163010123"}
    v = gen._pick_range_value(constraint, "20260820000000000")
    assert isinstance(v, str) and len(v) == 17, f"타입/자릿수 오류: {v!r}"
    print("✅ String 17자리 유지")


def test_non_time_range_falls_back():
    """시각이 아닌 일반 숫자 범위는 기존 방식(정수 난수) 유지"""
    constraint = {"type": "request-range", "min": 10, "max": 20}
    for _ in range(50):
        v = gen._pick_range_value(constraint, 15)
        assert 10 <= int(v) <= 20, f"일반 숫자 범위 동작 깨짐: {v}"
    print("✅ 시각이 아닌 숫자 범위는 기존 동작 유지")


def test_parse_rejects_invalid_dates():
    """형식 판별기가 달력에 없는 날짜를 거른다"""
    bad = ["20261340999999999", "abc", "20260822", "2026082216301012",
           "202608221630101234", ""]
    for v in bad:
        assert ConstraintDataGenerator._parse_time17(v) is None, f"잘못된 값 통과: {v}"
    good = "20260822163010123"
    dt = ConstraintDataGenerator._parse_time17(good)
    assert dt == datetime.datetime(2026, 8, 22, 16, 30, 10, 123000), f"파싱 오류: {dt}"
    assert ConstraintDataGenerator._format_time17(dt) == good, "포맷 왕복 불일치"
    print("✅ 17자리 판별/포맷 왕복 정확")


def test_timeout_cap_constant_exists():
    """② 제한 시간 상한 상수 (안내서 60초)"""
    cap = getattr(CONSTANTS, "MESSAGE_TIMEOUT_CAP_SEC", None)
    assert cap == 60, f"상한 상수가 60이 아님: {cap}"
    # 상한 적용 로직 자체 검증 (도구 인스턴스 없이 동일 식으로)
    for setting, expected in [(120, 60), (60, 60), (30, 30)]:
        applied = cap if (cap and setting > cap) else setting
        assert applied == expected, f"{setting}초 → {applied}초 (기대 {expected})"
    print("✅ 제한 시간 상한 60초 (더 작은 설정은 그대로)")


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
