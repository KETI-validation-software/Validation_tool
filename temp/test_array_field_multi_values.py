"""문자열 배열 칸(classFilter 등)은 한 줄 안에 여러 값을 담는다.

예전 동작 (2026-09-14 확인):
- 무작위: 후보가 5개여도 classFilter에 늘 1개
- 무작위+응답: filterList가 1~5줄로 늘고 줄마다 1개 (줄끼리 겹치기도 함)
- 참조한 칸이 배열: [["Human", "Vehicle"]] 이중 배열

원하는 모양: filterList 1줄 × classFilter 여러 개(겹침 없음).

실행: .venv\\Scripts\\python.exe temp\\test_array_field_multi_values.py
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

CLASSES = ["Human", "Vehicle", "Face", "Animal", "Bicycle"]
CAM_RESPONSE = {
    "camList": [{"camID": f"cam000{i}"} for i in range(1, 6)],
    "analyticsList": [{"className": c} for c in CLASSES],
    "classList": list(CLASSES),
}
EVENTS = {"CameraProfiles": {"RESPONSE": {"data": CAM_RESPONSE}}}
TEMPLATE = {"filterList": [{"classFilter": [], "attributeFilter": []}]}
RUNS = 200


def generate(rule, template=TEMPLATE, path="filterList.classFilter", request=None, events=EVENTS):
    constraints = {"filterList": {"valueType": "preset"}, path: rule}
    gen = ConstraintDataGenerator(copy.deepcopy(events))
    return gen._applied_constraints(request_data=request or {}, template_data=copy.deepcopy(template),
                                    constraints=constraints, api_name="StoredObjectAnalyticsInfos")


def check_one_row_many_values(label, rule, allowed):
    sizes = set()
    for _ in range(RUNS):
        rows = generate(rule)["filterList"]
        assert len(rows) == 1, f"{label}: filterList가 {len(rows)}줄로 늘어남 → {rows}"
        cf = rows[0]["classFilter"]
        assert all(isinstance(v, str) for v in cf), f"{label}: 이중 배열 → {cf}"
        assert len(cf) == len(set(cf)), f"{label}: 값 겹침 → {cf}"
        assert set(cf) <= set(allowed), f"{label}: 후보 밖 값 → {cf}"
        sizes.add(len(cf))
    assert sizes == set(range(1, len(allowed) + 1)), f"{label}: 개수가 고르게 나오지 않음 → {sorted(sizes)}"
    print(f"✅ {label}: 1줄, classFilter {min(sizes)}~{max(sizes)}개, 겹침 없음")


def test_random_valid_values():
    check_one_row_many_values("무작위(validValues)",
                              {"valueType": "random", "validValues": CLASSES}, CLASSES)


def test_random_response_scalar_reference():
    check_one_row_many_values("무작위+응답(낱값 참조)",
                              {"valueType": "random-response", "referenceEndpoint": "/CameraProfiles",
                               "referenceField": "analyticsList.className"}, CLASSES)


def test_random_response_array_reference_is_flattened():
    check_one_row_many_values("무작위+응답(배열 참조)",
                              {"valueType": "random-response", "referenceEndpoint": "/CameraProfiles",
                               "referenceField": "classList"}, CLASSES)


def test_request_based_mirrors_request_array():
    request = {"filterList": [{"classFilter": ["Human", "Face"], "attributeFilter": []}]}
    rule = {"valueType": "request-based", "referenceEndpoint": "/StoredObjectAnalyticsInfos",
            "referenceField": "filterList.classFilter"}
    events = {"StoredObjectAnalyticsInfos": {"REQUEST": {"data": request}}}
    for _ in range(20):
        out = generate(rule, request=request, events=events)
        assert out["filterList"] == [{"classFilter": ["Human", "Face"], "attributeFilter": []}], out
    print("✅ 요청 되돌려주기(request-based): 요청의 classFilter 그대로")


def test_top_level_array():
    sizes = set()
    for _ in range(RUNS):
        out = generate({"valueType": "random", "validValues": CLASSES},
                       template={"classFilter": []}, path="classFilter")
        cf = out["classFilter"]
        assert all(isinstance(v, str) for v in cf) and len(cf) == len(set(cf)), cf
        sizes.add(len(cf))
    assert len(sizes) > 1, sizes
    print(f"✅ 최상위 배열 칸: {min(sizes)}~{max(sizes)}개")


def test_scalar_reference_still_sets_row_count():
    """camID처럼 낱값 참조는 예전대로 줄 수를 정한다 (배열 칸만 빠짐)."""
    template = {"camList": [{"camID": "", "classFilter": []}]}
    constraints = {
        "camList": {"valueType": "preset"},
        "camList.camID": {"valueType": "response-based", "referenceEndpoint": "/CameraProfiles",
                          "referenceField": "camList.camID"},
        "camList.classFilter": {"valueType": "random", "validValues": CLASSES},
    }
    row_counts = set()
    for _ in range(RUNS):
        out = ConstraintDataGenerator(copy.deepcopy(EVENTS))._applied_constraints(
            request_data={}, template_data=copy.deepcopy(template),
            constraints=constraints, api_name="StoredVideoInfos")
        rows = out["camList"]
        row_counts.add(len(rows))
        ids = [r["camID"] for r in rows]
        assert len(ids) == len(set(ids)) and all(ids), rows
        assert all(r["classFilter"] and len(r["classFilter"]) == len(set(r["classFilter"])) for r in rows), rows
    assert len(row_counts) > 1, row_counts
    print(f"✅ 낱값 참조(camID)는 줄 수 결정 유지: {min(row_counts)}~{max(row_counts)}줄")


if __name__ == "__main__":
    test_random_valid_values()
    test_random_response_scalar_reference()
    test_random_response_array_reference_is_flattened()
    test_request_based_mirrors_request_array()
    test_top_level_array()
    test_scalar_reference_still_sets_row_count()
    print("OK")
