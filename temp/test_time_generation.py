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


def test_message_timeout_is_fixed_60():
    """② 제한 시간은 관리도구 설정과 무관하게 60초 고정 (안내서 표 3-2)"""
    assert getattr(CONSTANTS, "MESSAGE_TIMEOUT_SEC", None) == 60, "상수가 60이 아님"

    from systemVal_all import MyApp
    from types import SimpleNamespace
    # QWidget이라 인스턴스화 없이 메서드만 스텁에 바인딩해 확인
    calc = MyApp._get_effective_timeout_seconds
    tool = SimpleNamespace(CONSTANTS=CONSTANTS, trans_protocols=["basic", "basic", "basic"],
                           WEBHOOK_FAILFAST_TIMEOUT_SEC=MyApp.WEBHOOK_FAILFAST_TIMEOUT_SEC)

    # 관리도구가 뭘 내려주든(작든 크든) 60초
    for time_outs in ([5000, 5000, 5000], [120000, 120000, 120000], []):
        tool.time_outs = time_outs
        got = calc(tool, 0)
        assert got == 60, f"time_out={time_outs} -> {got}초 (기대 60)"
    print("✅ 제한 시간 60초 고정 (설정값 5초·120초·미설정 모두 60)")


def test_webhook_failfast_still_applies():
    """웹훅 구독 ACK용 fail-fast(10초)는 별개 기능이라 그대로 유지"""
    from systemVal_all import MyApp
    from types import SimpleNamespace
    tool = SimpleNamespace(CONSTANTS=CONSTANTS, time_outs=[60000], trans_protocols=["WebHook"],
                           WEBHOOK_FAILFAST_TIMEOUT_SEC=MyApp.WEBHOOK_FAILFAST_TIMEOUT_SEC)
    got = MyApp._get_effective_timeout_seconds(tool, 0)
    assert got == 10.0, f"웹훅 fail-fast가 깨짐: {got}"
    print("✅ 웹훅 구독 ACK fail-fast 10초 유지")


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
