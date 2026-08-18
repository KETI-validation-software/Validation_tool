# -*- coding: utf-8 -*-
"""
오류 회차 채점 회귀 시험 — core/functions.py json_check_

2026-08-18 리허설 실측 버그: ac002 StoredVerifEventInfos에 201 유도 성공
(startTime "0" 송신 → 상대가 201 "정보 없음" 응답)했는데도 화면은 FAIL —
관문 통과 후 정상 응답용 스키마(doorList 등)로 계속 채점해서
"필드 누락"이 쏟아졌다. 오류 응답의 본문은 code·message뿐인 것이 정상이다.

실행: .venv\Scripts\python.exe temp\test_error_round_scoring.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.functions import json_check_

# ac002 StoredVerifEventInfos 응답 스키마와 같은 꼴
SCHEMA = {
    "code": str,
    "message": str,
    "doorList": [{
        "doorID": str,
        "eventName": str,
        "eventTime": str,
    }],
}

# 관리도구에서 실제 내려온 오류 기대 규칙 (2026-08-18 다운로드본과 동일 형태)
ERROR_RULES = {
    "code": {"enabled": True, "validationType": "specified-value-match",
             "allowedValues": ["201"], "score": 0},
    "message": {"enabled": True, "validationType": "specified-value-match",
                "allowedValues": ["정보 없음"], "score": 0},
    "doorList.doorID": {"enabled": True, "validationType": "request-field-list-match",
                        "referenceField": "doorID",
                        "referenceEndpoint": "/StoredVerifEventInfos", "score": 0},
}


def test_error_round_correct_201_passes():
    """오류 회차 성공: 201 응답이면 code·message만 채점하고 PASS"""
    response = {"code": "201", "message": "정보 없음"}
    result, text, ok, err, opt_ok, opt_err = json_check_(
        SCHEMA, response, False, validation_rules=ERROR_RULES)
    assert result == "PASS", f"PASS여야 하는데 {result}\n{text}"
    assert err == 0, f"실패 필드가 없어야 하는데 {err}개\n{text}"
    assert "필드 누락" not in (text or ""), f"필드 누락 오탐:\n{text}"
    print("✅ 201 응답 → code·message만 채점, PASS (doorList 누락 오탐 없음)")


def test_error_round_wrong_200_fails_all():
    """오류 회차 실패: 200으로 오면 기존대로 전체 필드 0점 조기 종료"""
    response = {"code": "200", "message": "성공",
                "doorList": [{"doorID": "door0001", "eventName": "AuthSuccess",
                              "eventTime": "20260517163010123"}]}
    result, text, ok, err, opt_ok, opt_err = json_check_(
        SCHEMA, response, False, validation_rules=ERROR_RULES)
    assert result == "FAIL", f"FAIL이어야 하는데 {result}"
    assert ok == 0, f"통과 필드가 0이어야 하는데 {ok}개"
    print("✅ 기대 201에 200 응답 → 전체 필드 실패 (기존 동작 유지)")


def test_normal_round_unchanged():
    """정상 회차: 오류 규칙이 없으면 전체 필드를 평소대로 채점"""
    response = {"code": "200", "message": "성공",
                "doorList": [{"doorID": "door0001", "eventName": "AuthSuccess",
                              "eventTime": "20260517163010123"}]}
    result, text, ok, err, opt_ok, opt_err = json_check_(
        SCHEMA, response, False, validation_rules={})
    assert result == "PASS", f"정상 응답이 PASS가 아님: {result}\n{text}"
    assert ok >= 5, f"전체 필드가 채점돼야 하는데 통과 {ok}개뿐"

    # 정상 회차에서 필드가 빠지면 여전히 누락으로 잡혀야 한다 (축소 로직 오발동 방지)
    incomplete = {"code": "200", "message": "성공"}
    result2, text2, ok2, err2, _, _ = json_check_(
        SCHEMA, incomplete, False, validation_rules={})
    assert result2 == "FAIL" and err2 > 0, "정상 회차의 필드 누락을 놓침"
    print("✅ 정상 회차 채점은 그대로 (전체 필드 채점·누락 검출 유지)")


def test_message_only_match_does_not_shrink():
    """message가 '성공'처럼 정상 문구와 일치해도 축소 모드가 켜지면 안 된다"""
    rules = {"code": {"enabled": True, "validationType": "specified-value-match",
                      "allowedValues": ["200"], "score": 0},
             "message": {"enabled": True, "validationType": "specified-value-match",
                         "allowedValues": ["성공"], "score": 0}}
    incomplete = {"code": "200", "message": "성공"}  # doorList 없음
    result, text, ok, err, _, _ = json_check_(
        SCHEMA, incomplete, False, validation_rules=rules)
    assert err > 0, "code=200 기대인데 축소 모드가 켜져 누락을 놓침"
    print("✅ 기대가 200이면 축소 모드 미발동 — 누락 정상 검출")


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
