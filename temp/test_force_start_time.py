# -*- coding: utf-8 -*-
"""
startTime 전송 시점 강제 회귀 시험 — core/data_mapper.py의 force_start_time_now

관리도구에 무슨 값이 들어 있든 요청의 startTime을 "보내는 시점 + N초"로
덮어쓴다. 타입(String/Number)은 유지하고 endTime은 건드리지 않는다.

실행: .venv\Scripts\python.exe temp\test_force_start_time.py
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

gen = ConstraintDataGenerator({})


def as_dt(v):
    return datetime.datetime.strptime(str(v)[:14], "%Y%m%d%H%M%S")


def test_string_type_preserved_and_near_future():
    data = {"timePeriod": {"startTime": "20220101000000000", "endTime": "20221231000000000"}}
    out = gen.force_start_time_now(data, 3)

    st = out["timePeriod"]["startTime"]
    assert isinstance(st, str), f"String이 아님: {type(st).__name__}"
    assert len(st) == 17, f"17자리가 아님: {st}"

    delta = (as_dt(st) - datetime.datetime.now()).total_seconds()
    assert 1 <= delta <= 6, f"현재+3초 근처가 아님: {st} (차이 {delta:.1f}초)"
    assert out["timePeriod"]["endTime"] == "20221231000000000", "endTime이 바뀜"
    assert data["timePeriod"]["startTime"] == "20220101000000000", "원본이 훼손됨"
    print(f"✅ String 유지 + 현재+3초 ({st}), endTime 보존")


def test_number_type_preserved():
    data = {"startTime": 20220101000000000}
    out = gen.force_start_time_now(data, 3)
    assert isinstance(out["startTime"], int), f"Number가 아님: {type(out['startTime']).__name__}"
    assert len(str(out["startTime"])) == 17
    print(f"✅ Number 스펙은 숫자로 유지 ({out['startTime']})")


def test_nested_and_list():
    data = {
        "camList": [
            {"camID": "cam0001", "startTime": "20220101000000000"},
            {"camID": "cam0002", "startTime": "20220101000000000"},
        ],
        "duration": 10,
    }
    out = gen.force_start_time_now(data, 3)
    values = [c["startTime"] for c in out["camList"]]
    assert all(v != "20220101000000000" for v in values), f"리스트 안이 안 바뀜: {values}"
    assert out["duration"] == 10, "다른 필드가 바뀜"
    print("✅ 리스트/중첩 안의 startTime도 모두 적용, 다른 필드는 보존")


def test_offset_respected():
    out = gen.force_start_time_now({"startTime": "20220101000000000"}, 60)
    delta = (as_dt(out["startTime"]) - datetime.datetime.now()).total_seconds()
    assert 55 <= delta <= 65, f"오프셋 60초가 안 맞음: {delta:.1f}초"
    print("✅ 오프셋(60초) 반영")


def test_no_startTime_field_untouched():
    data = {"doorList": [{"doorID": "door0001"}], "endTime": "20221231000000000"}
    out = gen.force_start_time_now(data, 3)
    assert out == data, f"startTime이 없는데 데이터가 바뀜: {out}"
    print("✅ startTime이 없으면 아무것도 만들지 않음")


def test_error_injection_still_wins():
    """201 유도는 이 기능 뒤에 적용되므로 미래 구간이 최종값이어야 한다"""
    forced = gen.force_start_time_now({"startTime": "20220101000000000",
                                       "endTime": "20221231000000000"}, 3)
    injected = gen.replace_start_time(forced)
    assert injected["startTime"] == gen.FUTURE_START_TIME, "201 유도가 덮어쓰지 못함"
    assert injected["endTime"] == gen.FUTURE_END_TIME
    print("✅ 201 유도(미래 구간)가 최종값 — 오류 시험과 충돌 없음")


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
