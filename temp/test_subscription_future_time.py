# -*- coding: utf-8 -*-
"""
실시간 구독의 미래 startTime 회귀 시험 — api/api_server.Server._judge_time_fields

201('정보 없음') 판정은 저장 데이터 조회를 위한 것이다 — 미래 구간을 조회하면
저장된 영상이 있을 리 없으므로. 그런데 API를 가리지 않고 적용해,
실시간 구독(RealtimeVerifEventInfos 등)의 startTime이 조금이라도 미래면
구독 요청 자체를 201로 거절했다 (2026-09-02 실측).

구독의 startTime은 "언제부터 이벤트를 받을지"라 미래가 정상이다.
형식 위반(0 값·날짜 불성립 → 400)은 어느 API든 오류이므로 그대로 판정한다.

실행: .venv\Scripts\python.exe temp\test_subscription_future_time.py
"""
import datetime
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_server import Server
from core.data_mapper import ConstraintDataGenerator


def _judge(request_data, api_name):
    stub = SimpleNamespace(generator=ConstraintDataGenerator({}),
                           _is_subscription_api=Server._is_subscription_api)
    return Server._judge_time_fields(stub, request_data, api_name)


def _future(minutes=10):
    dt = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    return dt.strftime("%Y%m%d%H%M%S") + "000"


def _past():
    dt = datetime.datetime.now() - datetime.timedelta(days=3)
    return dt.strftime("%Y%m%d%H%M%S") + "000"


def test_subscription_future_is_ok():
    """실시간 구독의 미래 startTime은 정상"""
    for api in ("RealtimeVerifEventInfos", "RealtimeVideoEventInfos",
                "RealtimeDoorStatus", "/realtimevideoeventinfos"):
        v = _judge({"startTime": _future()}, api)
        assert v is None, f"{api}: 201로 거절됨 → {v}"
    print("✅ 실시간 구독 미래 시각 통과")


def test_query_future_still_201():
    """저장 조회의 미래 구간은 여전히 201 (기존 동작 유지)"""
    v = _judge({"timePeriod": {"startTime": _future()}}, "StoredVideoInfos")
    assert v and v[0] == "201", v
    print(f"✅ 저장 조회 미래 구간 201 유지: {v[1]}")


def test_query_past_is_ok():
    """저장 조회의 과거 구간은 정상"""
    assert _judge({"timePeriod": {"startTime": _past()}}, "StoredVideoInfos") is None
    print("✅ 저장 조회 과거 구간 통과")


def test_zero_still_400_everywhere():
    """0 값은 어느 API든 400 (형식 위반)"""
    for api in ("RealtimeVerifEventInfos", "StoredVideoInfos"):
        v = _judge({"startTime": "0"}, api)
        assert v and v[0] == "400", f"{api}: {v}"
        v = _judge({"startTime": "0" * 17}, api)
        assert v and v[0] == "400", f"{api}: {v}"
    print("✅ 0 값은 전 API 400 유지")


def test_impossible_date_still_400_everywhere():
    """달력에 없는 날짜는 어느 API든 400"""
    for api in ("RealtimeVerifEventInfos", "StoredVideoInfos"):
        v = _judge({"startTime": "20261340999999000"}, api)
        assert v and v[0] == "400", f"{api}: {v}"
    print("✅ 날짜 불성립은 전 API 400 유지")


def test_subscription_detection():
    """구독 API 판별"""
    for name in ("RealtimeDoorStatus", "realtimeverifeventinfos", "/RealtimeVideoEventInfos"):
        assert Server._is_subscription_api(name), name
    for name in ("StoredVideoInfos", "ReplayURL", "PtzStatus", "", None):
        assert not Server._is_subscription_api(name), name
    print("✅ 구독 API 판별")


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
