# -*- coding: utf-8 -*-
"""
doorList 조기 반환 회귀 시험 — core/data_mapper.py의 _applied_constraints

StoredVerifEventInfos처럼 doorList와 다른 최상위 필드(eventFilter)가 함께 있는
요청에서, doorList 동적 생성 블록이 채우자마자 return해 버려 eventFilter의
값 설정(무작위)이 한 번도 적용되지 않았다 — 빈 값으로 전송되던 원인.
(sensor 웹훅 3cea01b와 동일 유형. 2026-08-26 단일 리허설 실측.)

실행: .venv\Scripts\python.exe temp\test_doorlist_early_return.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

TEMPLATE = {
    "timePeriod": {"startTime": "20251105163010124", "endTime": "20251115163010124"},
    "doorList": [{"doorID": ""}],
    "maxCount": 10,
    "eventFilter": "",
}
CONSTRAINTS = {
    "timePeriod.startTime": {"valueType": "preset", "required": True},
    "doorList.doorID": {"valueType": "response-based", "required": True,
                        "referenceEndpoint": "/DoorProfiles", "referenceField": "doorID"},
    "maxCount": {"valueType": "preset", "required": False},
    "eventFilter": {
        "valueType": "random", "required": False,
        "referenceField": "(참조 필드 미선택)",
        "referenceEndpoint": "/StoredVerifEventInfos",
        "validValueField": "acEvent",
        "validValues": ["AuthSuccess", "AuthFail"],
    },
}
EVENTS = {"DoorProfiles": {"RESPONSE": {"data": {
    "doorList": [{"doorID": "door0001"}, {"doorID": "door0002"}]}}}}


def generate():
    gen = ConstraintDataGenerator(dict(EVENTS))
    return gen._applied_constraints(request_data={}, template_data=dict(TEMPLATE),
                                    constraints=dict(CONSTRAINTS),
                                    api_name="StoredVerifEventInfos")


def test_event_filter_filled():
    """핵심: doorList와 함께 있어도 eventFilter가 무작위 값으로 채워진다"""
    for _ in range(10):
        out = generate()
        assert out["eventFilter"] in ("AuthSuccess", "AuthFail"), \
            f"eventFilter가 빈 값: {out['eventFilter']!r}"
    print("✅ eventFilter 무작위 채움 (10회 확인)")


def test_doorlist_preserved():
    """doorList는 기존 동적 생성 결과(DoorProfiles의 문)를 그대로 유지"""
    for _ in range(10):
        out = generate()
        ids = [d.get("doorID") for d in out["doorList"]]
        assert ids and all(i in ("door0001", "door0002") for i in ids), \
            f"doorList 훼손: {out['doorList']}"
    print("✅ doorList 보존 (동적 생성 결과 유지)")


def test_other_fields_untouched():
    """preset 필드들은 템플릿 값 그대로"""
    out = generate()
    assert out["timePeriod"]["startTime"] == "20251105163010124"
    assert out["maxCount"] == 10
    print("✅ preset 필드(timePeriod/maxCount) 유지")


def test_doorlist_only_request_unchanged():
    """eventFilter 없는 doorList 단독 요청(RealtimeDoorStatus류)은 기존과 동일"""
    template = {"doorList": [{"doorID": ""}]}
    constraints = {"doorList.doorID": {"valueType": "response-based", "required": True,
                                       "referenceEndpoint": "/DoorProfiles",
                                       "referenceField": "doorID"}}
    gen = ConstraintDataGenerator(dict(EVENTS))
    out = gen._applied_constraints(request_data={}, template_data=template,
                                   constraints=constraints, api_name="RealtimeDoorStatus")
    ids = [d.get("doorID") for d in out["doorList"]]
    assert ids and all(i in ("door0001", "door0002") for i in ids), f"기존 동작 깨짐: {out}"
    print("✅ doorList 단독 요청은 기존 동작 그대로")


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
