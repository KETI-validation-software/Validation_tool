"""doorList가 있는 응답도 생성 제약을 적용하는지 확인.

예전 코드는 응답 템플릿(code 포함)에 doorList가 있으면 제약을 전부 무시하고
예시 데이터를 그대로 반환했다. (2025-12-17 cee9e37에서 도입, ac002
StoredVerifEventInfos의 eventName request-based가 실행된 적 없던 원인)

실행: .venv\Scripts\python.exe temp\test_response_doorlist_generation.py
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

# spec/Data_response.py · Constraints_response.py 의 통합 ac002 StoredVerifEventInfos와 동일 구조
SVEI_TEMPLATE = {
    "code": "200",
    "message": "성공",
    "doorList": [
        {"eventTime": "20220822163022124", "doorID": "door0001", "userID": "user0001",
         "eventName": "성공", "eventDesc": "36.5"},
        {"eventTime": "20220822163022124", "doorID": "door0002", "userID": "user0002",
         "eventName": "", "eventDesc": ""},
    ],
}
SVEI_CONSTRAINTS = {
    "code": {"valueType": "preset", "required": True},
    "doorList": {"valueType": "preset", "required": True},
    "doorList.doorID": {"valueType": "preset", "required": True},
    "doorList.eventName": {
        "valueType": "request-based",
        "required": True,
        "referenceEndpoint": "/StoredVerifEventInfos",
        "referenceField": "eventFilter",
    },
}

DOORPROFILES_TEMPLATE = {
    "code": "200",
    "message": "성공",
    "doorList": [
        {"doorID": "door0001", "doorName": "A건물 출입문", "doorSensor": "0"},
        {"doorID": "door0002", "doorName": "B건물 출입문", "doorSensor": "0"},
    ],
}
DOORPROFILES_CONSTRAINTS = {
    "code": {"valueType": "preset", "required": True},
    "doorList": {"valueType": "preset", "required": True},
    "doorList.doorID": {"valueType": "preset", "required": True},
}


def generate(template, constraints, request_data, api_name):
    # 실제 흐름과 동일: api_server가 수신 요청을 latest_events에 REQUEST로 기록한 뒤 응답을 생성한다
    latest_events = {api_name: {"REQUEST": {"data": request_data}}} if request_data else {}
    return ConstraintDataGenerator(latest_events)._applied_constraints(
        request_data=request_data,
        template_data=copy.deepcopy(template),
        constraints=constraints,
        api_name=api_name,
    )


def main():
    # 요청의 eventFilter가 응답 doorList.eventName에 채워져야 한다
    request = {"doorList": [{"doorID": "door0001"}], "eventFilter": "AuthSuccess"}
    result = generate(SVEI_TEMPLATE, SVEI_CONSTRAINTS, request, "StoredVerifEventInfos")
    names = [i.get("eventName") for i in result["doorList"]]
    assert names and all(n == "AuthSuccess" for n in names), names

    # 제약이 preset뿐인 응답(DoorProfiles)은 예전과 동일하게 템플릿 그대로
    result = generate(DOORPROFILES_TEMPLATE, DOORPROFILES_CONSTRAINTS, {}, "DoorProfiles")
    assert result == DOORPROFILES_TEMPLATE, result

    print("OK — 응답 doorList에도 생성 제약 적용, preset 응답은 기존 그대로")


if __name__ == "__main__":
    main()
