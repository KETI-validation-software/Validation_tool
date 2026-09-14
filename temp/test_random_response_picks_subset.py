"""무작위+응답(random-response)도 참조 목록에서 1개~전체 중 무작위 개수를 골라야 한다.

요청의 doorList를 만드는 전용 경로가 response-based만 일부를 뽑고 random-response는
늘 전부(DoorProfiles 5개)를 넣었다 (2026-09-14 확인). 일반 경로의 목록(camList 등)은
이미 1~N 무작위였으므로 두 경로가 같은 규칙을 따르는지 함께 본다.

실행: .venv\\Scripts\\python.exe temp\\test_random_response_picks_subset.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

DOORS = [f"door{i:04d}" for i in range(1, 6)]
CAMS = [f"cam{i:04d}" for i in range(1, 6)]
EVENTS = {
    "DoorProfiles": {"RESPONSE": {"data": {"doorList": [{"doorID": d} for d in DOORS]}}},
    "CameraProfiles": {"RESPONSE": {"data": {"camList": [{"camID": c} for c in CAMS]}}},
    # request-based는 앞서 보낸 요청을 본다
    "RealtimeDoorStatus": {"REQUEST": {"data": {"doorList": [{"doorID": d} for d in DOORS]}}},
}


def door_request(value_type, endpoint="/DoorProfiles"):
    constraints = {"doorList.doorID": {"valueType": value_type, "required": True,
                                       "referenceEndpoint": endpoint,
                                       "referenceField": "doorList.doorID"}}
    template = {"doorList": [{"doorID": ""}], "duration": 60}
    out = ConstraintDataGenerator(EVENTS)._applied_constraints(
        request_data={}, template_data=json.loads(json.dumps(template)),
        constraints=constraints, api_name="RealtimeDoorStatus", door_memory={})
    return [row["doorID"] for row in out["doorList"]]


def cam_request(value_type):
    constraints = {"camList.camID": {"valueType": value_type, "required": True,
                                     "referenceEndpoint": "/CameraProfiles",
                                     "referenceField": "camList.camID"}}
    template = {"camList": [{"camID": ""}]}
    out = ConstraintDataGenerator(EVENTS)._applied_constraints(
        request_data={}, template_data=json.loads(json.dumps(template)),
        constraints=constraints, api_name="StreamURLs", door_memory={})
    return [row["camID"] for row in out["camList"]]


def sizes(make, runs=200):
    seen = set()
    for _ in range(runs):
        ids = make()
        universe = DOORS if ids and ids[0].startswith("door") else CAMS
        assert ids, "빈 목록"
        assert len(ids) == len(set(ids)), f"중복: {ids}"
        assert set(ids) <= set(universe), f"참조에 없는 값: {ids}"
        seen.add(len(ids))
    return seen


def main():
    # 무작위 계열은 1~5개가 골고루 나와야 한다 (200회면 전부 나올 확률이 사실상 1)
    for value_type in ("random-response", "response-based"):
        got = sizes(lambda: door_request(value_type))
        assert got == {1, 2, 3, 4, 5}, (value_type, "doorList", got)
        got = sizes(lambda: cam_request(value_type))
        assert got == {1, 2, 3, 4, 5}, (value_type, "camList", got)

    # 요청을 되돌려주는 설정은 전부 그대로
    got = sizes(lambda: door_request("request-based", "/RealtimeDoorStatus"))
    assert got == {5}, ("request-based", got)

    print("OK — 무작위+응답·응답 기반은 1~N개 무작위, request-based는 전부")


if __name__ == "__main__":
    main()
