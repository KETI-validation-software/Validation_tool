# -*- coding: utf-8 -*-
"""
센서 웹훅 참조 채움 회귀 시험 — core/data_mapper.py

2026-08-20 sensor001 리허설 실측 버그: 웹훅 동적 생성(지름길)이 sensorDeviceID만
채우고 바로 반환해, 관리도구에서 걸어둔 참조 설정(eventName←eventFilter,
eventTime←startTime 범위)이 한 번도 실행되지 않았다. 웹훅이
{"eventName": "", "eventTime": ""} 빈 값으로 나가 단일 쪽 맥락 검증이 FAIL.

실행: .venv\Scripts\python.exe temp\test_sensor_webhook_reference.py
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

# 2026-08-20 리허설 로그의 실제 구조 그대로
TEMPLATE = {
    "sensorDeviceList": [
        {"sensorDeviceID": "", "eventName": "", "eventTime": "", "eventDesc": "100도"}
    ]
}

CONSTRAINTS = {
    "sensorDeviceList": {"valueType": "preset", "required": True},
    "sensorDeviceList.sensorDeviceID": {
        "valueType": "request-based", "required": True,
        "referenceEndpoint": "/RealtimeSensorEventInfos", "referenceField": "sensorDeviceID"},
    "sensorDeviceList.eventName": {
        "valueType": "request-based", "required": True,
        "referenceEndpoint": "/RealtimeSensorEventInfos", "referenceField": "eventFilter"},
    "sensorDeviceList.eventTime": {
        "valueType": "request-range", "required": True,
        "requestRange": {"operator": "greater-equal", "minField": "startTime",
                         "minEndpoint": "/RealtimeSensorEventInfos"}},
    "sensorDeviceList.eventDesc": {"valueType": "preset", "required": False},
}


def generate(request):
    events = {"RealtimeSensorEventInfos": {"REQUEST": {"data": request}}}
    return ConstraintDataGenerator(events)._applied_constraints(
        request_data=request,
        template_data=copy.deepcopy(TEMPLATE),
        constraints=CONSTRAINTS,
        api_name="RealtimeSensorEventInfos",
        is_webhook=True,   # ← 지름길 분기를 태운다 (로그와 동일 경로)
    )


def test_references_filled():
    """실측 재현: eventFilter·startTime이 실린 요청 → 웹훅에 값이 채워져야 한다"""
    request = {"sensorDeviceList": [{"sensorDeviceID": "iot0001"},
                                    {"sensorDeviceID": "iot0002"}],
               "duration": 100,
               "eventFilter": "Leak",
               "startTime": "20260820103000000"}
    rows = generate(request)["sensorDeviceList"]

    assert [r["sensorDeviceID"] for r in rows] == ["iot0001", "iot0002"], \
        f"요청한 ID 순서대로여야 함: {rows}"
    for r in rows:
        assert r["eventName"] == "Leak", f"eventName이 eventFilter에서 안 채워짐: {r}"
        assert isinstance(r["eventTime"], str) and r["eventTime"].isdigit(), \
            f"eventTime이 숫자 문자열이 아님: {r}"
        assert int(r["eventTime"]) >= 20260820103000000, \
            f"eventTime이 구독 시각 이후가 아님: {r}"
        assert r["eventDesc"] == "100도", f"preset 필드가 훼손됨: {r}"
    print("✅ 웹훅 eventName=Leak, eventTime=구독 이후 String — 참조 채움 정상")


def test_no_starttime_still_string():
    """요청이 startTime을 생략해도(선택 필드) eventTime은 String으로 나가야 한다"""
    request = {"sensorDeviceList": [{"sensorDeviceID": "iot0001"}],
               "duration": 100, "eventFilter": "Leak"}
    rows = generate(request)["sensorDeviceList"]
    assert rows[0]["eventName"] == "Leak"
    assert isinstance(rows[0]["eventTime"], str) and rows[0]["eventTime"] != "", \
        f"startTime 생략 시에도 빈 값이면 안 됨: {rows[0]}"
    print("✅ startTime 생략 요청 → eventTime 폴백도 String, 빈 값 없음")


def test_no_constraints_keeps_old_behavior():
    """제약이 없으면 예전 그대로 — ID만 채우고 나머지는 템플릿 값 유지"""
    request = {"sensorDeviceList": [{"sensorDeviceID": "iot0001"}]}
    events = {"RealtimeSensorEventInfos": {"REQUEST": {"data": request}}}
    out = ConstraintDataGenerator(events)._applied_constraints(
        request_data=request, template_data=copy.deepcopy(TEMPLATE),
        constraints={}, api_name="RealtimeSensorEventInfos", is_webhook=True)
    row = out["sensorDeviceList"][0]
    assert row["sensorDeviceID"] == "iot0001"
    assert row["eventDesc"] == "100도"
    print("✅ 제약 없는 스펙은 기존 동작 유지 (ID만 채움)")


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
