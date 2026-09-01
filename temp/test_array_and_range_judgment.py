# -*- coding: utf-8 -*-
"""
배열 필드 지정값 대조 / 시각 범위 표기 회귀 시험 — core/functions.py

2026-09-01 통합 리허설 실측:
① specified-value-match가 배열을 통째로 비교해
   ['RTSP','RTSP','RTSP','RTSP']가 ['RTSP']에 없다고 오판 (요소별 대조로 수정,
   valid-value-match 2ed16e4와 같은 유형)
② range-match가 17자리 시각을 float로 변환해 오류 문구에 2.02e+16으로 찍힘
   (정밀도 손실 + 사람이 읽을 수 없음 → 정수 변환 우선)

실행: .venv\Scripts\python.exe temp\test_array_and_range_judgment.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.functions import _validate_specified_value_match, _validate_range_match_direct


def test_array_all_allowed_passes():
    """① 배열 요소가 모두 허용값이면 통과 (실측 오탐 케이스)"""
    errs, gerrs = [], []
    ok = _validate_specified_value_match(
        "camList.streamProtocolType", ["RTSP", "RTSP", "RTSP", "RTSP"],
        {"allowedValues": ["RTSP"]}, errs, gerrs)
    assert ok and not errs, f"배열 전체 허용값인데 실패: {errs}"
    print("✅ ['RTSP']×4 vs 지정값 ['RTSP'] → 통과")


def test_array_with_invalid_element_fails():
    """① 요소 중 하나라도 허용값 밖이면 실패 + 그 값만 표기"""
    errs, gerrs = [], []
    ok = _validate_specified_value_match(
        "camList.streamProtocolType", ["RTSP", "HTTP", "RTSP"],
        {"allowedValues": ["RTSP"]}, errs, gerrs)
    assert not ok, "위반 요소가 있는데 통과"
    assert "HTTP" in errs[0] and "RTSP'," not in errs[0].split("가")[0], \
        f"위반 값만 표기되어야 함: {errs[0]}"
    print(f"✅ 위반 요소만 표기: {errs[0]}")


def test_scalar_still_works():
    """① 단일 값 동작은 그대로"""
    errs, gerrs = [], []
    assert _validate_specified_value_match("code", "200", {"allowedValues": ["200"]}, errs, gerrs)
    errs, gerrs = [], []
    assert not _validate_specified_value_match("code", "400", {"allowedValues": ["200"]}, errs, gerrs)
    print("✅ 단일 값 대조 기존 동작 유지")


def test_time_range_error_shows_full_digits():
    """② 17자리 시각이 지수 표기로 뭉개지지 않는다"""
    errs, gerrs = [], []
    ok = _validate_range_match_direct(
        "timePeriod.startTime", "20220822163022124",
        {"rangeOperator": "between",
         "rangeMin": 20260817163010124, "rangeMax": 20260822163010124},
        errs, gerrs)
    assert not ok, "범위 밖인데 통과"
    assert "20220822163022124" in errs[0], f"지수 표기로 뭉개짐: {errs[0]}"
    assert "e+" not in errs[0], f"지수 표기 잔존: {errs[0]}"
    print(f"✅ 시각 범위 오류 문구 정상: {errs[0][:60]}…")


def test_time_range_within_passes():
    """② 범위 안 시각은 통과 (정수 비교 정확성)"""
    errs, gerrs = [], []
    ok = _validate_range_match_direct(
        "timePeriod.startTime", "20260820120000000",
        {"rangeOperator": "between",
         "rangeMin": 20260817163010124, "rangeMax": 20260822163010124},
        errs, gerrs)
    assert ok and not errs, f"범위 안인데 실패: {errs}"
    print("✅ 범위 내 시각 → 통과")


def test_float_values_still_work():
    """② 소수 값(신뢰도 등)도 기존대로 처리"""
    errs, gerrs = [], []
    ok = _validate_range_match_direct(
        "analyticsConfidence", 0.85,
        {"rangeOperator": "between", "rangeMin": 0, "rangeMax": 1}, errs, gerrs)
    assert ok, f"소수 처리 깨짐: {errs}"
    print("✅ 소수 값 범위 검증 유지")


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
