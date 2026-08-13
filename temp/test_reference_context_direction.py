"""참조 자료가 요청/응답끼리 서로 덮어쓰지 않는지 확인.

한 단계에 참조 엔드포인트가 같고 방향만 다른 규칙이 둘 이상 있을 때
(ac003 DoorControl: doorID=요청 / commandType=응답),
뒤 규칙이 앞 규칙의 참조를 지워버리던 문제에 대한 회귀 시험.

실행: .venv\Scripts\python.exe temp\test_reference_context_direction.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.functions import _validate_list_match, ref_context_key

DOORID_RULE = {
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorID",
}
COMMANDTYPE_RULE = {
    "validationType": "valid-value-match",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorSensor",
}

SUBSCRIBE_REQUEST = {"doorList": [{"doorID": "door0001"}, {"doorID": "door0002"}]}
SUBSCRIBE_RESPONSE = {"code": "성공", "message": "200"}


def build_context():
    """검증 직전 참조 자료 적재 — 규칙 등록 순서대로 (doorID 먼저, commandType 나중)"""
    ctx = {}
    for rule, data in ((DOORID_RULE, SUBSCRIBE_REQUEST), (COMMANDTYPE_RULE, SUBSCRIBE_RESPONSE)):
        direction = "REQUEST" if "request-field" in rule["validationType"] else "RESPONSE"
        ctx[ref_context_key(rule["referenceEndpoint"], direction)] = data
        ctx[rule["referenceEndpoint"]] = data
    return ctx


def check_doorid(door_id, ctx):
    errors = []
    ok = _validate_list_match("doorID", door_id, DOORID_RULE, {}, ctx, errors, [])
    return ok, "\n".join(errors)


def main():
    ctx = build_context()

    # commandType 규칙이 응답을 담아도 doorID는 구독 요청을 그대로 본다
    ok, err = check_doorid("door0001", ctx)
    assert ok, f"구독한 문인데 불합격: {err}"

    # 구독하지 않은 문은 여전히 불합격이고, 목록에 중복이 없어야 한다
    ok, err = check_doorid("door9999", ctx)
    assert not ok, "구독하지 않은 문이 통과함"
    assert "door0001 | door0002" in err, f"조회된 목록이 잘못됨:\n{err}"

    # 방향 없는 옛 키만 있어도 동작 (하위 호환)
    ok, _ = check_doorid("door0001", {"/RealtimeDoorStatus": SUBSCRIBE_REQUEST})
    assert ok, "옛 키 폴백이 동작하지 않음"

    print("OK — 참조 자료가 방향별로 분리 보관됨")


if __name__ == "__main__":
    main()
