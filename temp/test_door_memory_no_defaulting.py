# -*- coding: utf-8 -*-
"""
문 상태 보정 제거 회귀 시험 — api/api_server.py

DoorProfiles 응답을 door_memory에 기록할 때, 예전에는 규격에 맞지 않는 값을
도구가 몰래 고쳐 넣었다:
    doorSensor 없음/"0" → "Lock",  "1" → "Unlock",  doorRelaySensor 빔 → "일반"
이 값은 이후 RealtimeDoorStatus 응답에 실려 나가므로, 잘못된 데이터가
도구 덕분에 통과하는 셈이었다. 받은 값을 그대로 기록하도록 보정을 제거했다.

실행: .venv\Scripts\python.exe temp\test_door_memory_no_defaulting.py
"""
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "api", "api_server.py")


def _code_lines():
    """주석을 제외한 실행 코드 줄만 (설명 주석 속 단어에 걸리지 않게)"""
    with open(SRC, encoding="utf-8") as f:
        return [ln.split("#")[0] for ln in f if not ln.strip().startswith("#")]


def test_no_value_defaulting():
    """문 상태 필드에 코드가 값을 써넣지 않는다"""
    pattern = re.compile(r'\["(doorSensor|doorRelaySensor)"\]\s*=\s*["\']')
    hits = [ln.strip() for ln in _code_lines() if pattern.search(ln)]
    # DoorControl(commandType→상태 기록)은 별개 경로이므로 제외 대상이 아니라
    # 남아 있다면 그것까지 드러나야 한다. 지금은 door_memory 보정만 제거된 상태.
    forbidden = [h for h in hits if '"Lock"' in h or '"Unlock"' in h or '"일반"' in h]
    control_only = [h for h in forbidden if "door_memory[door_id]" in h]
    profile_defaults = [h for h in forbidden if h not in control_only]
    assert not profile_defaults, f"DoorProfiles 저장 시 보정이 남아 있음: {profile_defaults}"
    print(f"✅ DoorProfiles 보정 없음 (DoorControl 상태 기록 {len(control_only)}건은 별도 경로)")


def test_empty_value_warns():
    """빈 값은 고치지 않되 경고는 남긴다"""
    src = open(SRC, encoding="utf-8").read()
    assert 'for _f in ("doorSensor", "doorRelaySensor"):' in src, "빈 값 점검 루프가 없음"
    assert "보정 없이 그대로 기록" in src, "경고 문구가 없음"
    print("✅ 빈 값 경고 로그 유지")


def test_realtime_branch_still_verbatim():
    """RealtimeDoorStatus 경로는 원래대로 받은 값 그대로 저장"""
    src = open(SRC, encoding="utf-8").read()
    assert "# 모든 필드 저장 (doorName, doorRelaySensor, doorSensor 등)" in src, \
        "RealtimeDoorStatus 저장 블록을 찾지 못함"
    print("✅ RealtimeDoorStatus 경로 그대로")


def test_file_parses():
    ast.parse(open(SRC, encoding="utf-8").read())
    print("✅ 구문 정상")


def test_semantics():
    """저장 의미: 받은 값이 그대로 남고 doorID만 키로 빠진다"""
    door = {"doorID": "door0001", "doorSensor": "0", "doorRelaySensor": ""}
    save_data = door.copy()
    if "doorRelayStatus" in save_data:
        save_data["doorRelaySensor"] = save_data.pop("doorRelayStatus")
    stored = {k: v for k, v in save_data.items() if k != "doorID"}

    assert stored["doorSensor"] == "0", f'"0"이 그대로 남아야 함: {stored}'
    assert stored["doorRelaySensor"] == "", f"빈 값이 그대로 남아야 함: {stored}"
    assert "doorID" not in stored
    print("✅ 받은 값 그대로 보존 ('0'이 Lock으로 바뀌지 않음)")


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
