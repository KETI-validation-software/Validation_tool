# -*- coding: utf-8 -*-
"""오류 유도용 시각 변조 회귀 시험 — 의도별 값 분리 (2026-08-23 개편)

  201 유도(replace_start_time): 형식이 완벽한 "미래 구간"으로 이동.
    예전 "0" 방식은 형식 검사를 하는 업체에서 400으로 판정돼 업체별로
    201/400이 갈렸다(시험장 논쟁). 문서 표 4·6·8 예시(2027-01)와 통일.
  400 유도(corrupt_time_format): 자리수만 17로 맞고 날짜로는 무효인 0 채움.

둘 다 원본 타입(String/Number)을 유지한다 — 타입까지 깨지면 의도한 오류가
아니라 타입 오류로 먼저 걸린다. (2026-08-14 sensor002 실측의 교훈)

실행: .venv\Scripts\python.exe temp\test_error_mutation.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

FUT_S = ConstraintDataGenerator.FUTURE_START_TIME      # "20270101000000000"
FUT_E = ConstraintDataGenerator.FUTURE_END_TIME        # "20270131000000000"
ZEROS = ConstraintDataGenerator.INVALID_TIME_FORMAT    # "0"*17


def main():
    gen = ConstraintDataGenerator()

    # ── 201 유도: 미래 구간, start·end 함께 이동 (구간 역전 방지) ──
    out = gen.replace_start_time({
        "timePeriod": {"startTime": "20251105163010124", "endTime": "20251115163010124"},
    })
    assert out["timePeriod"]["startTime"] == FUT_S, out
    assert out["timePeriod"]["endTime"] == FUT_E, out
    assert out["timePeriod"]["startTime"] < out["timePeriod"]["endTime"], "구간 역전"

    # Number 스펙(미전환): 숫자로 유지
    out = gen.replace_start_time({
        "timePeriod": {"startTime": 20251105163010124, "endTime": 20251115163010124},
    })
    assert out["timePeriod"]["startTime"] == int(FUT_S), out
    assert out["timePeriod"]["endTime"] == int(FUT_E), out

    # 중첩 목록 안의 시각도 동일하게 (ReplayURL 등 camList[].startTime 구조)
    out = gen.replace_start_time({
        "camList": [{"camID": "cam0001", "startTime": "20251105163010124"}],
    })
    assert out["camList"][0]["startTime"] == FUT_S, out

    # ── 400 유도: 0 채움 17자리 (String) / 숫자 0 (Number) ──
    out = gen.corrupt_time_format({
        "timePeriod": {"startTime": "20251105163010124", "endTime": "20251115163010124"},
    })
    assert out["timePeriod"]["startTime"] == ZEROS, out
    assert len(out["timePeriod"]["startTime"]) == 17, "자리수가 17이 아님"
    assert out["timePeriod"]["endTime"] == "20251115163010124", "endTime은 유지"

    out = gen.corrupt_time_format({"timePeriod": {"startTime": 20251105163010124}})
    assert out["timePeriod"]["startTime"] == 0, out

    # ── 원본 불변 (deepcopy) ──
    src = {"timePeriod": {"startTime": "20251105163010124"}}
    gen.replace_start_time(src)
    gen.corrupt_time_format(src)
    assert src["timePeriod"]["startTime"] == "20251105163010124", src

    print("OK — 201=미래 구간(형식 유효), 400=0 채움 17자리, 타입 보존")


if __name__ == "__main__":
    main()
