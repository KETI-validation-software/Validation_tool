"""요청을 되돌려주는 목록은 요청 항목 수만큼 줄이 나가야 한다.

StoredVerifEventInfos에서 문 5개를 요청했는데 userID(AccessUserInfos 참조)가
2명뿐이라 응답이 2줄로 잘렸다 — 줄 수를 모든 참조 값 가짓수의 최솟값으로 정했기
때문이다 (2026-09-14 실측). 줄 수는 요청 항목(request-based)으로만 정하고,
다른 참조 필드는 줄 사이 중복을 허용한다.

실행: .venv\\Scripts\\python.exe temp\\test_mirror_rows_follow_request.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

# 관리도구가 내려준 StoredVerifEventInfos 응답 설정 (2026-09-14)
CONSTRAINTS = {
    "code": {"valueType": "preset", "required": True},
    "message": {"valueType": "preset", "required": True},
    "doorList": {"valueType": "preset", "required": True},
    "doorList.doorID": {"valueType": "request-based", "required": True,
                        "referenceEndpoint": "/StoredVerifEventInfos",
                        "referenceField": "doorList.doorID"},
    "doorList.userID": {"valueType": "random-response", "required": False,
                        "referenceEndpoint": "/AccessUserInfos",
                        "referenceField": "userList.userID"},
    "doorList.eventName": {"valueType": "request-based", "required": True,
                           "referenceEndpoint": "/StoredVerifEventInfos",
                           "referenceField": "eventFilter"},
}
TEMPLATE = {"code": "200", "message": "성공",
            "doorList": [{"doorID": "", "userID": "", "eventName": ""}]}


def generate(door_count, user_count):
    request = {"doorList": [{"doorID": f"door{i:04d}"} for i in range(1, door_count + 1)],
               "eventFilter": "사용자전체삭제성공"}
    users = {"userList": [{"userID": f"user{i:04d}"} for i in range(1, user_count + 1)]}
    events = {"StoredVerifEventInfos": {"REQUEST": {"data": request}},
              "AccessUserInfos": {"RESPONSE": {"data": users}}}
    out = ConstraintDataGenerator(events)._applied_constraints(
        request_data=request, template_data=json.loads(json.dumps(TEMPLATE)),
        constraints=CONSTRAINTS, api_name="StoredVerifEventInfos", door_memory={})
    return request, users, out["doorList"]


def main():
    for door_count, user_count in ((5, 2), (5, 1), (2, 5), (1, 1)):
        for _ in range(20):
            request, users, rows = generate(door_count, user_count)
            requested = sorted(d["doorID"] for d in request["doorList"])
            known_users = {u["userID"] for u in users["userList"]}
            # 요청한 문이 빠짐없이, 한 번씩
            assert sorted(r["doorID"] for r in rows) == requested, (door_count, user_count, rows)
            # userID는 참조 목록 안의 값 (중복 허용)
            assert all(r["userID"] in known_users for r in rows), rows
            assert all(r["eventName"] == "사용자전체삭제성공" for r in rows), rows

    print("OK — 요청 항목 수만큼 줄이 나감 (다른 참조 필드는 중복 허용)")


if __name__ == "__main__":
    main()
