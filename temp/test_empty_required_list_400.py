"""필수 항목 목록이 빈 배열이면 400 (통합 요청 판정).

관리도구에서 RealtimeDoorStatus2 요청의 doorList 줄을 지워 `doorList: []`로 내려오자
통합이 줄 안 doorID 검사를 건너뛰고 200 성공을 보냈다 (2026-09-14). 항목 목록
([{...}])이 필수인데 비어 있으면 필수 누락과 같이 400. 문자열 배열([str])은
빈 배열이 "필터 없음"이므로 그대로 정상.

실행: .venv\\Scripts\\python.exe temp\\test_empty_required_list_400.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from json_checker import OptionalKey
from api.api_server import Server

SCHEMA = {
    "doorList": [{"doorID": str}],
    OptionalKey("camList"): [{"camID": str}],
    "filterList": [{"classFilter": [str], OptionalKey("attributeFilter"): [str]}],
    "transProtocol": {"transProtocolType": str},
}
BASE = {"transProtocol": {"transProtocolType": "LongPolling"},
        "filterList": [{"classFilter": ["Human"]}]}


def judge(**over):
    data = dict(BASE, doorList=[{"doorID": "door0001"}])
    data.update(over)
    return Server.__new__(Server)._walk_type_check(data, SCHEMA, "")


def main():
    assert judge() is None
    assert judge(doorList=[]) == "doorList", "필수 항목 목록이 비어 있는데 통과"
    assert judge(doorList=[{}]) == "doorList[0].doorID"
    assert judge(camList=[]) is None, "선택 목록은 비어도 정상"
    assert judge(filterList=[{"classFilter": []}]) is None, "문자열 배열은 비어도 정상 (필터 없음)"
    assert judge(filterList=[]) == "filterList", "필수 항목 목록(filterList)도 같은 규칙"
    print("OK — 필수 항목 목록이 비면 400, 선택 목록·문자열 배열은 정상")


if __name__ == "__main__":
    main()
