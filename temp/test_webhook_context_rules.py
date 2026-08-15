"""웹훅 이벤트의 맥락 검증 규칙이 실제로 동작함을 증명하는 시험.

배경(2026-08-15 확인): 관리도구의 웹훅 맥락 규칙(spec/validation_*.py의
*_webhook_*_validation)은 다운로드·저장까지 되지만, 웹훅 검사 호출부가
validation_rules 인자를 넘기지 않아 한 번도 실행된 적이 없다.
그동안 화면의 "웹훅 통과"는 규격(필드 유무·타입) 검사만 통과했다는 뜻이었다.

이 시험이 보여주는 것:
  1) 규칙을 넘기지 않으면(현 웹훅 경로와 동일) 명백한 규칙 위반도 PASS — 구멍의 증명
  2) 같은 함수에 규칙을 넘기면 정확히 FAIL — 연결만 하면 검증이 성립한다는 증명
웹훅 연결 작업 후에는 2)가 실제 경로의 기대 동작이 된다.

실측 사례: 2026-08-13 11:30 ac003 회차 — 제어 commandType이 ""인데 결과조회
웹훅 doorSensor가 "Lock"으로 왔고(규칙 위반), 당시 화면은 웹훅 전항목 통과였다.

실행: .venv\Scripts\python.exe temp\test_webhook_context_rules.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.functions import json_check_, ref_context_key

# 단일 ac003(cmiqr1jha) RealtimeDoorStatus2 웹훅과 동일 구조
SCHEMA = {"doorList": [{"doorID": str, "doorName": str,
                        "doorRelaySensor": str, "doorSensor": str}]}
RULES = {
    "doorList.doorID": {"enabled": True, "validationType": "request-field-match",
                        "referenceField": "doorID", "referenceEndpoint": "/RealtimeDoorStatus2"},
    "doorList.doorSensor": {"enabled": True, "validationType": "request-field-match",
                            "referenceField": "commandType", "referenceEndpoint": "/DoorControl"},
}


def make_context(subscribed_door, command):
    ctx = {}
    for ep, data in (("/RealtimeDoorStatus2", {"doorList": [{"doorID": subscribed_door}]}),
                     ("/DoorControl", {"doorID": subscribed_door, "commandType": command})):
        ctx[ep] = data
        ctx[ref_context_key(ep, "REQUEST")] = data
    return ctx


def check(event, ctx, with_rules):
    result, text, _, err, _, _ = json_check_(
        schema=SCHEMA, data=event, flag=False,
        validation_rules=RULES if with_rules else None,
        reference_context=ctx,
    )
    return result, err, text


def main():
    ctx = make_context("door0001", "Unlock")

    # 규칙을 정면으로 위반한 이벤트: 구독 안 한 문 + 제어 명령과 반대 상태
    bad = {"doorList": [{"doorID": "door9999", "doorName": "가짜문",
                         "doorRelaySensor": "일반", "doorSensor": "Lock"}]}

    # 1) 규칙 미전달(현 웹훅 경로) — 위반인데도 PASS: 구멍의 증명
    result, err, _ = check(bad, ctx, with_rules=False)
    assert result == "PASS" and err == 0, (result, err)

    # 2) 규칙 전달 — 두 위반 모두 잡힘
    result, err, text = check(bad, ctx, with_rules=True)
    assert result == "FAIL" and err == 2, (result, err, text)
    assert "doorID" in text and "doorSensor" in text, text

    # 3) 규칙에 맞는 정상 이벤트는 규칙을 전달해도 통과 (연결해도 오탐 없음)
    good = {"doorList": [{"doorID": "door0001", "doorName": "A건물 출입문",
                          "doorRelaySensor": "일반", "doorSensor": "Unlock"}]}
    result, err, text = check(good, ctx, with_rules=True)
    assert result == "PASS" and err == 0, (result, err, text)

    print("OK — 웹훅 맥락 규칙: 미전달=무조건 통과(구멍), 전달=위반 검출·정상 통과")


if __name__ == "__main__":
    main()
