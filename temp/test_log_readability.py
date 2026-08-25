# -*- coding: utf-8 -*-
"""
로그 가독성 회귀 시험 — core/functions.py의 json_check_ 출력

목적: 검증 결과(카운트·PASS/FAIL)는 그대로 두고, 실패했을 때
"어느 필드가 왜 틀렸는지"가 로그에 남는지 확인한다.
  ① 실패 줄에 필드명과 사유가 함께 나온다
  ② 검증 끝에 실패 필드 목록이 한 번 더 모여 나온다
  ③ 참조 자료를 통째로 덤프하지 않는다(키만)

실행: .venv\Scripts\python.exe temp\test_log_readability.py
"""
import io
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.CONSTANTS as CONSTANTS
from core.functions import json_check_
from core.logger import Logger

Logger.set_level(Logger.LEVEL_DEBUG)  # 모든 로그를 켜고 본다
CONSTANTS.flag_opt = False

SCHEMA = {"code": str, "message": str, "doorList": list, "doorList.doorID": str}
RULES = {
    "doorList.doorID": {
        "enabled": True,
        "validationType": "request-field-list-match",
        "referenceField": "doorID",
        "referenceEndpoint": "/RealtimeDoorStatus",
    }
}
REF = {"/RealtimeDoorStatus#REQUEST": {"doorList": [{"doorID": "door0001"}]}}


def run(data, rules=None, ref=None):
    """json_check_를 돌리고 (결과, 출력된 로그)를 돌려준다"""
    buf = io.StringIO()
    with redirect_stdout(buf):
        result = json_check_(SCHEMA, data, CONSTANTS.flag_opt,
                             validation_rules=rules, reference_context=ref)
    return result, buf.getvalue()


def test_semantic_failure_shows_field_and_reason():
    """① 의미 검증 실패 — 필드명과 사유가 로그에 있어야 한다"""
    data = {"code": "200", "message": "성공", "doorList": [{"doorID": "door9999"}]}
    (val_result, _, _, err_cnt, _, _), log = run(data, RULES, REF)

    assert val_result == "FAIL" and err_cnt == 1, f"판정이 바뀜: {val_result}, {err_cnt}"
    fail_lines = [l for l in log.splitlines() if "❌ [실패]" in l]
    assert fail_lines, f"실패 줄을 못 찾음:\n{log}"
    line = fail_lines[0]
    assert "doorList.doorID" in line, f"필드명이 없음: {line}"
    assert "door9999" in line, f"실패 사유(입력값)가 없음: {line}"
    print(f"✅ ① 실패 줄에 필드·사유 포함: {line.strip()[:90]}…")


def test_missing_field_shows_path():
    """① 구조(필수 누락) 실패도 필드명이 보여야 한다"""
    data = {"code": "200", "message": "성공"}  # doorList 통째 누락
    (val_result, _, _, err_cnt, _, _), log = run(data)

    assert val_result == "FAIL" and err_cnt >= 1
    assert any("❌ [실패]" in l and "doorList" in l for l in log.splitlines()), \
        f"누락 필드명이 로그에 없음:\n{log}"
    print("✅ ① 필수 필드 누락도 필드명과 함께 표시")


def test_failure_summary_at_end():
    """② 검증 끝에 실패 필드 목록이 다시 나온다"""
    data = {"code": "200", "message": "성공", "doorList": [{"doorID": "door9999"}]}
    _, log = run(data, RULES, REF)

    assert "실패 필드" in log, f"실패 요약이 없음:\n{log}"
    tail = log.split("검증 상태:")[-1]
    assert "doorList.doorID" in tail, f"요약에 필드가 안 나옴:\n{tail}"
    print("✅ ② 검증 끝에 실패 필드 요약 출력")


def test_no_summary_when_all_pass():
    """통과했으면 실패 요약을 찍지 않는다(소음 방지)"""
    data = {"code": "200", "message": "성공", "doorList": [{"doorID": "door0001"}]}
    (val_result, _, _, err_cnt, _, _), log = run(data, RULES, REF)

    assert val_result == "PASS" and err_cnt == 0, f"판정이 바뀜: {val_result}"
    assert "실패 필드" not in log, "통과인데 실패 요약이 나옴"
    print("✅ 통과 시에는 실패 요약 없음")


def test_reference_context_not_dumped():
    """③ 참조 자료를 통째로 찍지 않는다 (키만) — 단일 필드 대조 경로"""
    schema = {"doorID": str}
    rules = {
        "doorID": {
            "enabled": True,
            "validationType": "request-field-match",
            "referenceField": "doorID",
            "referenceEndpoint": "/RealtimeDoorStatus",
        }
    }
    # 감시 문자열은 '값'에 둔다 — 키 목록만 찍히는지 보는 것이므로
    ref = {
        "/RealtimeDoorStatus#REQUEST": {
            "doorID": "door0001",
            "memo": "이_값이_통째로_찍히면_안_됨",
        }
    }

    buf = io.StringIO()
    with redirect_stdout(buf):
        json_check_(schema, {"doorID": "door0001"}, CONSTANTS.flag_opt,
                    validation_rules=rules, reference_context=ref)
    log = buf.getvalue()

    assert "이_값이_통째로_찍히면_안_됨" not in log, f"참조 자료가 통째로 덤프됨(축약 실패):\n{log}"
    assert "참조 보관함" in log, f"참조 키 요약 줄이 없음:\n{log}"
    print("✅ ③ 참조 자료는 키만 표시 (전체 덤프 없음)")


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
