# -*- coding: utf-8 -*-
"""
목록 구성 개수(5~100) 판정 회귀 시험 — core/functions.py

안내서 표 2-1 "목록 정보" / 부록 표 Ⅰ-12:
프로필 조회 응답의 목록은 5개 이상 100개 이하여야 하며, 미달·초과 시
"송신 조건 불충족"으로 실패 판정한다. 이벤트 목록(RealtimeVideoEventInfos의
camList 등)은 1건 이상이면 정상이므로 대상이 아니다.

실행: .venv\Scripts\python.exe temp\test_list_count.py
"""
import io
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.CONSTANTS as CONSTANTS
from core.functions import json_check_, check_list_counts
from core.logger import Logger

Logger.set_level(Logger.LEVEL_ERROR)  # 매트릭스 소음 제거
CONSTANTS.flag_opt = False
CONSTANTS.ENABLE_LIST_COUNT_CHECK = True

SCHEMA = {"code": str, "message": str, "camList": list, "camList.camID": str}


def cams(n):
    return {"code": "200", "message": "성공",
            "camList": [{"camID": f"cam{i:04d}"} for i in range(1, n + 1)]}


def run(data, api_name):
    buf = io.StringIO()
    with redirect_stdout(buf):
        res = json_check_(SCHEMA, data, CONSTANTS.flag_opt, api_name=api_name)
    return res, buf.getvalue()


def test_valid_count_passes():
    """기준 내(12개) → 통과 (안내서 표 Ⅰ-12 성공 예시)"""
    (result, _, _, err, _, _), _ = run(cams(12), "CameraProfiles")
    assert result == "PASS" and err == 0, f"12개인데 실패: {result}, err={err}"
    print("✅ camList 12개 → 통과")


def test_too_few_fails():
    """기준 미달(3개) → 실패 (안내서 표 Ⅰ-12 실패 예시)"""
    (result, text, _, err, _, _), log = run(cams(3), "CameraProfiles")
    assert result == "FAIL" and err == 1, f"3개인데 통과: {result}, err={err}"
    assert "목록 구성 개수" in text, f"사유가 결과에 없음: {text}"
    assert "3개" in text, f"실제 개수가 결과에 없음: {text}"
    print("✅ camList 3개 → 실패 (사유·개수 표기 확인)")


def test_too_many_fails():
    """상한 초과(101개) → 실패"""
    (result, text, _, err, _, _), _ = run(cams(101), "CameraProfiles")
    assert result == "FAIL" and err == 1, f"101개인데 통과: {result}"
    assert "101개" in text
    print("✅ camList 101개 → 실패")


def test_boundary_5_and_100():
    """경계값 5개·100개는 통과"""
    for n in (5, 100):
        (result, _, _, err, _, _), _ = run(cams(n), "CameraProfiles")
        assert result == "PASS" and err == 0, f"{n}개(경계)인데 실패"
    print("✅ 경계값 5개·100개 → 통과")


def test_event_list_not_target():
    """이벤트 목록은 대상 아님 — 1건이어도 통과"""
    (result, _, _, err, _, _), _ = run(cams(1), "RealtimeVideoEventInfos")
    assert result == "PASS" and err == 0, f"이벤트 목록 1건인데 실패: {result}"
    print("✅ 이벤트 목록(RealtimeVideoEventInfos) 1건 → 판정 안 함")


def test_retry_suffix_api_name():
    """재시도 접미사(CameraProfiles2)도 대상으로 인식"""
    got = check_list_counts("CameraProfiles2", cams(3))
    assert got and got[0][1] == 3 and got[0][2] is False, f"접미사 API 미인식: {got}"
    print("✅ 숫자 접미사 API명(CameraProfiles2)도 판정")


def test_all_four_targets():
    """4종 프로필 목록 모두 대상"""
    cases = [
        ("DoorProfiles", "doorList"),
        ("AccessUserInfos", "userList"),
        ("SensorDeviceProfiles", "sensorDeviceList"),
        ("CameraProfiles", "camList"),
    ]
    for api, field in cases:
        data = {field: [{"id": i} for i in range(3)]}
        got = check_list_counts(api, data)
        assert got and got[0][0] == field and got[0][2] is False, f"{api}.{field} 미판정: {got}"
    print("✅ camList·doorList·userList·sensorDeviceList 4종 모두 판정")


def test_switch_off_restores_old_behavior():
    """스위치를 끄면 이전 동작(판정 안 함)"""
    CONSTANTS.ENABLE_LIST_COUNT_CHECK = False
    try:
        (result, _, _, err, _, _), _ = run(cams(3), "CameraProfiles")
        assert result == "PASS" and err == 0, "스위치 껐는데 판정함"
    finally:
        CONSTANTS.ENABLE_LIST_COUNT_CHECK = True
    print("✅ ENABLE_LIST_COUNT_CHECK=False → 이전 동작")


def test_missing_list_left_to_structure_check():
    """목록 필드 자체가 없으면 개수 판정이 아니라 구조(누락) 검증이 잡는다"""
    (result, text, _, err, _, _), _ = run({"code": "200", "message": "성공"}, "CameraProfiles")
    assert result == "FAIL", "누락인데 통과"
    assert "목록 구성 개수" not in text, f"누락을 개수 미달로 오판: {text}"
    print("✅ 목록 필드 누락은 구조 검증이 담당 (개수 판정 아님)")


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
