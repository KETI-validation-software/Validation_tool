"""시각 필드 String 전환 후 웹훅/응답 생성이 깨지지 않는지 확인.

17자리 시각 필드가 Number→String 전환되면서 request-range 비교
(min_val >= max_val)가 str-int TypeError로 죽고, 웹훅 페이로드가
빈 값 그대로 나가던 문제에 대한 회귀 시험.
(2026-08-14 로그: vid001 RealtimeVideoEventInfos 웹훅에서 재현)

실행: .venv\Scripts\python.exe temp\test_webhook_string_time.py
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

# vid001 RealtimeVideoEventInfos 웹훅 — 로그에 찍힌 실제 구조 그대로
TEMPLATE = {
    "camList": [
        {"camID": "", "eventUUID": "event01", "eventName": "",
         "startTime": "", "endTime": "", "eventDesc": "sfdf"}
    ]
}
CONSTRAINTS = {
    "camList": {"valueType": "preset", "required": True},
    "camList.camID": {"valueType": "request-based", "required": True,
                      "referenceEndpoint": "/RealtimeVideoEventInfos", "referenceField": "camID"},
    "camList.eventUUID": {"valueType": "preset", "required": True},
    "camList.eventName": {"valueType": "request-based", "required": True,
                          "referenceEndpoint": "/RealtimeVideoEventInfos", "referenceField": "eventFilter"},
    "camList.startTime": {"valueType": "request-range", "required": True,
                          "requestRange": {"operator": "greater-equal", "minField": "startTime"}},
    "camList.endTime": {"valueType": "request-range", "required": False,
                        "requestRange": {"operator": "greater-equal", "minField": "startTime"}},
    "camList.eventDesc": {"valueType": "preset", "required": False},
}


def generate(start_time):
    request = {"camList": [{"camID": "cam0001"}, {"camID": "cam004"}],
               "duration": 10, "eventFilter": "Loitering", "startTime": start_time}
    events = {"RealtimeVideoEventInfos": {"REQUEST": {"data": request}}}
    return ConstraintDataGenerator(events)._applied_constraints(
        request_data=request,
        template_data=copy.deepcopy(TEMPLATE),
        constraints=CONSTRAINTS,
        api_name="RealtimeVideoEventInfos",
        is_webhook=False,   # camList는 웹훅 전용 분기가 없어 공통 경로를 탄다 (로그와 동일)
    )


def main():
    # ✅ 시각이 String으로 온 경우 — 예전에는 여기서 TypeError로 전부 빈 값
    out = generate("20251105163010124")
    cams = out["camList"]
    assert [c["camID"] for c in cams] == ["cam0001", "cam004"], cams
    assert all(c["eventName"] == "Loitering" for c in cams), cams
    for c in cams:
        assert isinstance(c["startTime"], str) and int(c["startTime"]) >= 20251105163010124, c
        assert isinstance(c["endTime"], str) and int(c["endTime"]) > int(c["startTime"]), c

    # ✅ 시각이 Number로 온 경우(미전환 스펙) — 숫자 그대로 유지
    out = generate(20251105163010124)
    for c in out["camList"]:
        assert isinstance(c["startTime"], int) and c["startTime"] >= 20251105163010124, c
        assert isinstance(c["endTime"], int) and c["endTime"] > c["startTime"], c

    # ✅ 요청에 startTime이 아예 없는 경우(선택 필드 생략) — 참조가 비어도
    #    템플릿이 String("17자리 예시")이면 String으로, 템플릿 시각 근방 값으로 나가야 한다.
    #    (2026-08-19 실측: 참조 부재 시 min=0 폴백으로 13자리 Number가 나가던 문제)
    template_with_time = copy.deepcopy(TEMPLATE)
    template_with_time["camList"][0]["startTime"] = "20251105163010124"
    template_with_time["camList"][0]["endTime"] = "20251105163020124"
    request = {"camList": [{"camID": "cam0001"}], "duration": 10,
               "eventFilter": "Loitering"}  # startTime 없음
    events = {"RealtimeVideoEventInfos": {"REQUEST": {"data": request}}}
    out = ConstraintDataGenerator(events)._applied_constraints(
        request_data=request,
        template_data=template_with_time,
        constraints=CONSTRAINTS,
        api_name="RealtimeVideoEventInfos",
        is_webhook=False,
    )
    for c in out["camList"]:
        assert isinstance(c["startTime"], str), f"참조 부재 시 String이어야 함: {c}"
        assert int(c["startTime"]) >= 20251105163010124, f"템플릿 시각 근방이어야 함: {c}"

    print("OK — 시각 String/Number 모두 웹훅 값이 정상 생성됨 (참조 부재 폴백 포함)")


if __name__ == "__main__":
    main()
