# -*- coding: utf-8 -*-
"""
값 생성 전수 매트릭스 회귀 시험 — core/data_mapper.py의 _applied_constraints

"설정했는데 조용히 빈 값으로 나가는" 부류의 버그가 반복돼(sensor 웹훅,
doorList 요청/웹훅, eventFilter, classFilter…) 필드가 놓일 수 있는 모양 7가지
× 값 설정 방식 5가지 전 조합을 한 번에 검사한다 (2026-08-26 전수 감사).

제외 1건: 리스트줄 문자열배열 × request-range — 시각 범위를 배열에 거는
조합은 의미가 성립하지 않아 실전에 존재하지 않는다.

실행: .venv\Scripts\python.exe temp\test_generation_matrix.py
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logger import Logger
Logger.set_level(0)  # 매트릭스 실행 소음 제거
from core.data_mapper import ConstraintDataGenerator

EVENTS = {
    "RefApi": {
        "REQUEST": {"data": {"eventFilter": "REQ값", "startTime": "20251105163010124",
                             "doorList": [{"doorID": "door0001"}, {"doorID": "door0002"}]}},
        "RESPONSE": {"data": {"camList": [{"camID": "cam0001"}, {"camID": "cam0002"}]}},
    }
}

SHAPES = [
    ("최상위 낱값",        {"f": ""},                        "f"),
    ("최상위 문자열배열",   {"f": []},                        "f"),
    ("중첩dict 낱값",      {"box": {"f": ""}},               "box.f"),
    ("리스트줄 낱값",      {"rows": [{"f": ""}]},            "rows.f"),
    ("리스트줄 문자열배열", {"rows": [{"f": []}]},            "rows.f"),
    ("리스트줄 중첩dict",  {"rows": [{"box": {"f": ""}}]},   "rows.box.f"),
    ("리스트줄 중첩리스트", {"rows": [{"sub": [{"f": ""}]}]}, "rows.sub.f"),
]
VTS = ["random", "random-response", "request-based", "response-based", "request-range"]
SKIP = {("리스트줄 문자열배열", "request-range")}  # 의미 불성립 조합


def make_rule(vt):
    r = {"valueType": vt, "required": True}
    if vt == "random":
        r.update({"referenceField": "(참조 필드 미선택)", "referenceEndpoint": "/RefApi",
                  "validValues": ["값A", "값B"]})
    elif vt in ("random-response", "response-based"):
        r.update({"referenceEndpoint": "/RefApi", "referenceField": "camID"})
    elif vt == "request-based":
        r.update({"referenceEndpoint": "/RefApi", "referenceField": "eventFilter"})
    elif vt == "request-range":
        r.update({"requestRange": {"minField": "startTime", "operator": "greater-equal",
                                   "minEndpoint": "/RefApi"},
                  "requestRangeMinEndpoint": "/RefApi"})
    return r


def extract(out, path):
    vals = []

    def walk(obj, parts):
        if not parts:
            vals.append(obj)
            return
        head, rest = parts[0], parts[1:]
        if isinstance(obj, dict) and head in obj:
            walk(obj[head], rest)
        elif isinstance(obj, list):
            for item in obj:
                walk(item, parts)

    walk(out, path.split("."))
    return vals


def is_empty(v):
    return v in ("", None, []) or (isinstance(v, list) and all(x in ("", None) for x in v))


def run_matrix():
    failures = []
    for shape_name, template, path in SHAPES:
        for vt in VTS:
            if (shape_name, vt) in SKIP:
                continue
            gen = ConstraintDataGenerator(copy.deepcopy(EVENTS))
            constraints = {path: make_rule(vt)}
            parts = path.split(".")
            for i in range(1, len(parts)):
                constraints[".".join(parts[:i])] = {"valueType": "preset", "required": True}
            out = gen._applied_constraints(request_data={}, template_data=copy.deepcopy(template),
                                           constraints=constraints, api_name="ProbeApi")
            vals = extract(out, path)
            if (not vals) or any(is_empty(v) for v in vals):
                failures.append(f"{shape_name} × {vt}: {vals}")
    return failures


def test_array_stays_array():
    """배열 템플릿은 배열로 유지된다 (classFilter류가 낱값으로 변형 금지)"""
    for shape_name, template, path in SHAPES:
        if "문자열배열" not in shape_name:
            continue
        gen = ConstraintDataGenerator(copy.deepcopy(EVENTS))
        constraints = {path: make_rule("random")}
        for i in range(1, len(path.split("."))):
            constraints[".".join(path.split(".")[:i])] = {"valueType": "preset", "required": True}
        out = gen._applied_constraints(request_data={}, template_data=copy.deepcopy(template),
                                       constraints=constraints, api_name="ProbeApi")
        vals = extract(out, path)
        assert all(isinstance(v, list) for v in vals), \
            f"{shape_name}: 배열이 낱값으로 변형됨 → {vals}"
    print("✅ 배열 필드는 채워져도 배열 타입 유지")


if __name__ == "__main__":
    failures = run_matrix()
    if failures:
        print("❌ 빈 값 조합 발견:")
        for f in failures:
            print("   -", f)
    else:
        print(f"✅ 전 조합({len(SHAPES) * len(VTS) - len(SKIP)}개) 값 채움 확인")
    try:
        test_array_stays_array()
        array_ok = True
    except AssertionError as e:
        array_ok = False
        print(f"❌ {e}")
    ok = (not failures) and array_ok
    print(f"\n{'통과' if ok else '실패'}")
    sys.exit(0 if ok else 1)
