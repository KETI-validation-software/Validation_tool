"""조회 응답이 요청 조건에 맞는 기록만 돌려주는지 확인.

장치 역할일 때 저장된 기록(관리도구 응답 템플릿)을 조회 조건과 무관하게
전부 돌려주던 문제에 대한 회귀 시험. 줄을 그대로 두고 걸러내기만 하며,
값을 바꾸거나 줄을 복제하지 않는다.

실행: .venv\Scripts\python.exe temp\test_response_row_filter.py
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

# spec/Data_response.py 의 통합 ac002 StoredVerifEventInfos 응답 템플릿과 동일 구조
STORED = {
    "code": "200",
    "message": "성공",
    "doorList": [
        {"doorID": "door0001", "userID": "user0001", "eventName": "성공", "eventDesc": "36.5"},
        {"doorID": "door0002", "userID": "user0002", "eventName": "", "eventDesc": ""},
    ],
}
# 영상 계열: 템플릿 줄의 ID가 비어 있고 요청 개수만큼 채워 쓰는 구조 (걸러내기 대상 아님)
VIDEO = {"code": "200", "message": "성공", "camList": [{"camID": "", "eventName": ""}]}


def respond(template, request):
    return ConstraintDataGenerator()._applied_constraints(
        request_data=request,
        template_data=copy.deepcopy(template),
        constraints={},
        api_name="StoredVerifEventInfos",
    )


def door_ids(response):
    return [item["doorID"] for item in response["doorList"]]


def main():
    # 요청한 문의 기록만 응답한다
    r = respond(STORED, {"doorList": [{"doorID": "door0001"}]})
    assert door_ids(r) == ["door0001"], r

    r = respond(STORED, {"doorList": [{"doorID": "door0002"}]})
    assert door_ids(r) == ["door0002"], r

    # 둘 다 요청하면 둘 다
    r = respond(STORED, {"doorList": [{"doorID": "door0001"}, {"doorID": "door0002"}]})
    assert door_ids(r) == ["door0001", "door0002"], r

    # 기록에 없는 문은 빈 목록
    r = respond(STORED, {"doorList": [{"doorID": "door9999"}]})
    assert door_ids(r) == [], r

    # 남은 줄의 다른 값은 그대로 유지된다 (복제·치환 없음)
    r = respond(STORED, {"doorList": [{"doorID": "door0002"}]})
    assert r["doorList"][0] == STORED["doorList"][1], r["doorList"][0]

    # 조회 조건이 없는 API(DoorProfiles 등)는 전체를 그대로 응답
    r = respond(STORED, {})
    assert door_ids(r) == ["door0001", "door0002"], r

    # 템플릿 ID가 비어 있는 영상 계열은 걸러내지 않는다
    r = ConstraintDataGenerator()._applied_constraints(
        request_data={"camList": [{"camID": "cam0002"}]},
        template_data=copy.deepcopy(VIDEO),
        constraints={},
        api_name="StoredVideoEventInfos",
    )
    assert len(r["camList"]) == 1, r

    print("OK — 조회 응답이 요청 조건에 맞는 기록만 돌려줌")


if __name__ == "__main__":
    main()
