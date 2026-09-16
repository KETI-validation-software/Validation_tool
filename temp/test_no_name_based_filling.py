"""API·칸 이름을 보고 값을 채우는 전용 경로가 없는지 확인.

2026-09-14: 관리도구에서 RealtimeDoorStatus2 요청의 doorList.doorID를 뺐는데
DoorProfiles의 문 5개가 채워져 나갔다. 2026-01에 넣은 전용 경로가
"doorList가 있으면 참조가 없어도 DoorProfiles에서 문을 전부 가져온다"는 기본값을
갖고 있었다. 전용 경로(doorList·sensorDeviceList·commandType)와 문 상태 기록을
걷어내고, 관리도구 설정에 있는 것만 채운다.

실행: .venv\\Scripts\\python.exe temp\\test_no_name_based_filling.py
"""
import copy
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.data_mapper import ConstraintDataGenerator as G

DOORS = {"doorList": [{"doorID": f"door000{i}", "doorSensor": "Lock"} for i in range(1, 6)]}
EVENTS = {
    "DoorProfiles": {"RESPONSE": {"data": DOORS}},
    "RealtimeDoorStatus": {"REQUEST": {"data": {"doorList": [{"doorID": "door0002"}]}},
                           "RESPONSE": {"data": DOORS}},
    "DoorControl": {"REQUEST": {"data": {"doorID": "door0003", "commandType": "Unlock"}}},
}
PRESET = {"valueType": "preset", "required": True}


def run(template, constraints, request=None, api="X", webhook=False):
    out = G(copy.deepcopy(EVENTS))._applied_constraints(
        request_data=copy.deepcopy(request or {}), template_data=copy.deepcopy(template),
        constraints=copy.deepcopy(constraints), api_name=api, is_webhook=webhook)
    return out


def test_removed_door_id_stays_removed():
    """doorID를 뺀 요청(doorList만 preset)은 채우지 않는다 — 실제 사례"""
    for rows in ([], [{}]):
        tpl = {"doorList": rows, "duration": 60}
        out = run(tpl, {"doorList": PRESET, "duration": PRESET}, api="RealtimeDoorStatus2")
        assert out == tpl, out
    print("✅ doorID 뺀 요청에 문을 채우지 않음")


def test_empty_door_id_without_rule_stays_empty():
    """doorID 칸은 있지만 값 설정이 없으면 템플릿 값(빈 값) 그대로"""
    tpl = {"doorList": [{"doorID": ""}]}
    assert run(tpl, {"doorList": PRESET}, api="RealtimeDoorStatus") == tpl
    print("✅ 설정 없는 doorID는 템플릿 그대로")


def test_preset_response_rows_not_filtered():
    """고정 기록 응답을 요청 조건으로 몰래 걸러내지 않는다"""
    tpl = {"code": "200", "doorList": [{"doorID": "door0001"}, {"doorID": "door0002"}]}
    out = run(tpl, {}, request={"doorList": [{"doorID": "door0001"}]}, api="StoredVerifEventInfos")
    assert out == tpl, out
    print("✅ 고정 기록 응답을 걸러내지 않음")


def test_webhook_rows_not_built_without_rule():
    """설정 없는 웹훅은 요청을 보고 줄을 만들지 않는다 (doorList·sensorDeviceList)"""
    for key, idf in (("doorList", "doorID"), ("sensorDeviceList", "sensorDeviceID")):
        tpl = {key: [{idf: "", "eventName": ""}]}
        req = {key: [{idf: "a1"}, {idf: "a2"}]}
        assert run(tpl, {}, request=req, api="RealtimeX", webhook=True) == tpl, key
    print("✅ 설정 없는 웹훅 줄은 템플릿 그대로")


def test_command_without_rule_untouched():
    """commandType 설정이 없으면 이름만 보고 토글하지 않는다"""
    tpl = {"doorID": "door0001", "commandType": "Lock"}
    assert run(tpl, {}, api="DoorControl") == tpl
    print("✅ 설정 없는 commandType은 템플릿 그대로")


def test_settings_still_fill():
    """설정이 있으면 채운다 — 요청 되돌려주기는 요청 순서, 참조 제외는 같은 문 기준"""
    req = {"doorList": [{"doorID": "door0004"}, {"doorID": "door0001"}]}
    ev = copy.deepcopy(EVENTS); ev["RealtimeDoorStatus"]["REQUEST"]["data"] = req
    tpl = {"code": "200", "doorList": [{"doorID": ""}]}
    cons = {"doorList.doorID": {"valueType": "request-based", "referenceEndpoint": "/RealtimeDoorStatus",
                                "referenceField": "doorList.doorID"}}
    out = G(ev)._applied_constraints(req, copy.deepcopy(tpl), cons, api_name="RealtimeDoorStatus")
    assert [r["doorID"] for r in out["doorList"]] == ["door0004", "door0001"], out

    cons = {"doorID": PRESET,
            "commandType": {"valueType": "random", "randomType": "exclude-reference-valid-values",
                            "validValues": ["Lock", "Unlock"], "referenceEndpoint": "/RealtimeDoorStatus",
                            "referenceField": "doorList.doorSensor"}}
    for _ in range(30):
        out = run({"doorID": "door0003", "commandType": ""}, cons, api="DoorControl")
        assert out["commandType"] == "Unlock", out   # door0003은 Lock
    print("✅ 설정이 있으면 설정대로 채움")


def test_no_hardcoded_api_names_in_generator():
    """생성기 코드에 API 이름 기본값이 다시 들어오지 않는다 (주석 제외)"""
    src = io.open(os.path.join(ROOT, "core", "data_mapper.py"), encoding="utf-8").read()
    code = "\n".join(ln.split("#")[0] for ln in src.splitlines())
    code = re.sub(r'"""[\s\S]*?"""', "", code)
    for name in ("DoorProfiles", "RealtimeDoorStatus", "DoorControl", "doorList", "sensorDeviceList",
                 "commandType", "door_memory"):
        assert f'"{name}"' not in code and f"'{name}'" not in code, f"생성기에 이름 하드코딩: {name}"
    print("✅ 생성기에 API·칸 이름 하드코딩 없음")


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
