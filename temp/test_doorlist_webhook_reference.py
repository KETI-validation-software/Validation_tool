# -*- coding: utf-8 -*-
"""
doorList 웹훅 참조 채움 회귀 시험 — core/data_mapper.py의 _applied_constraints

RealtimeVerifEventInfos 웹훅 이벤트를 통합이 만들 때, doorList 줄(doorID)만
채우고 즉시 반환해 eventName(←요청의 eventFilter) 같은 참조 설정이 한 번도
실행되지 않았다 — 웹훅이 템플릿 빈 값 그대로 나가던 원인.
(sensor 웹훅 3cea01b와 동일 유형. 2026-08-26 리허설 실측.)

실행: .venv\Scripts\python.exe temp\test_doorlist_webhook_reference.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

# RealtimeVerifEventInfos 웹훅 이벤트 템플릿 (통합이 보낼 데이터)
TEMPLATE = {
    "doorList": [
        {"doorID": "door0001", "eventName": "", "eventTime": "20251105163010124", "userID": "user0001"},
    ]
}
# 단일이 보낸 구독 요청 (eventFilter 포함)
REQUEST = {
    "doorList": [{"doorID": "door0001"}, {"doorID": "door0002"}],
    "eventFilter": "AuthSuccess",
    "transProtocol": {"transProtocolType": "WebHook"},
}
# 웹훅 out 제약: eventName은 요청의 eventFilter를 참조
CONSTRAINTS = {
    "doorList.doorID": {"valueType": "request-based", "required": True,
                        "referenceEndpoint": "/RealtimeVerifEventInfos",
                        "referenceField": "doorID"},
    "doorList.eventName": {"valueType": "request-based", "required": True,
                           "referenceEndpoint": "/RealtimeVerifEventInfos",
                           "referenceField": "eventFilter"},
    "doorList.eventTime": {"valueType": "preset", "required": True},
}
EVENTS = {"RealtimeVerifEventInfos": {"REQUEST": {"data": REQUEST}}}


def generate():
    gen = ConstraintDataGenerator({k: dict(v) for k, v in EVENTS.items()})
    import copy
    return gen._applied_constraints(request_data=copy.deepcopy(REQUEST),
                                    template_data=copy.deepcopy(TEMPLATE),
                                    constraints=dict(CONSTRAINTS),
                                    api_name="RealtimeVerifEventInfos",
                                    is_webhook=True)


def test_event_name_filled_from_event_filter():
    """핵심: eventName이 요청의 eventFilter 값으로 채워진다"""
    out = generate()
    names = [d.get("eventName") for d in out["doorList"]]
    assert names and all(n == "AuthSuccess" for n in names), \
        f"eventName이 eventFilter를 참조하지 못함: {names}"
    print(f"✅ eventName ← eventFilter 참조 채움: {names}")


def test_door_ids_follow_request():
    """doorList 줄은 요청한 doorID 순서대로 (기존 동작 유지)"""
    out = generate()
    ids = [d.get("doorID") for d in out["doorList"]]
    assert ids == ["door0001", "door0002"], f"요청 doorID 순서가 깨짐: {ids}"
    print(f"✅ 요청 doorID대로 줄 생성: {ids}")


def test_preset_fields_kept():
    """preset 필드(eventTime)는 템플릿 값 유지"""
    out = generate()
    times = [d.get("eventTime") for d in out["doorList"]]
    assert all(t == "20251105163010124" for t in times), f"preset 시각 훼손: {times}"
    print("✅ preset eventTime 템플릿 값 유지")


def test_no_constraints_unchanged():
    """제약이 없으면 기존 동작(ID만 채움) 그대로"""
    import copy
    gen = ConstraintDataGenerator({})
    out = gen._applied_constraints(request_data=copy.deepcopy(REQUEST),
                                   template_data=copy.deepcopy(TEMPLATE),
                                   constraints={}, api_name="RealtimeVerifEventInfos",
                                   is_webhook=True)
    ids = [d.get("doorID") for d in out["doorList"]]
    assert ids == ["door0001", "door0002"], f"제약 없음 경로가 깨짐: {out}"
    print("✅ 제약 없으면 기존 동작 그대로")


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
