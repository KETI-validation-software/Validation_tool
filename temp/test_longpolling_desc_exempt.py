# -*- coding: utf-8 -*-
"""
LongPolling 구독의 transProtocolDesc 면제 회귀 시험 — core/functions

RealtimeDoorStatus처럼 전송 방식이 LongPolling으로 고정된 API는 웹훅 수신
주소를 쓰지 않는다. transProtocolDesc에 null·빈 값이 와도 정상인데,
스키마·검증 규칙이 그대로 걸려 있어 실패로 잡혔다 (2026-09-02 결정으로 면제).

판단 기준은 API 이름이 아니라 같은 요청 안의 transProtocolType이다.
같은 API라도 WebHook으로 설정된 회차에서는 평소대로 검사한다.

실행: .venv\Scripts\python.exe temp\test_longpolling_desc_exempt.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.functions import _is_desc_exempt, json_check_

SCHEMA = {
    "doorList": [{"doorID": str}],
    "transProtocol": {"transProtocolType": str, "transProtocolDesc": str},
}


def _req(ptype, desc):
    proto = {"transProtocolType": ptype}
    if desc is not _MISSING:
        proto["transProtocolDesc"] = desc
    return {"doorList": [{"doorID": "door0001"}], "transProtocol": proto}


_MISSING = object()
FIELD = "transProtocol.transProtocolDesc"


def test_longpolling_exempt():
    """LongPolling이면 값이 무엇이든 면제"""
    for desc in (None, "", "아무값", 12345, "https://x"):
        assert _is_desc_exempt(FIELD, _req("LongPolling", desc)), desc
    print("✅ LongPolling — 모든 값 면제")


def test_case_insensitive():
    """표기가 달라도 동일 판단"""
    for ptype in ("LongPolling", "longpolling", "LONGPOLLING", "Long-Polling"):
        assert _is_desc_exempt(FIELD, _req(ptype, None)), ptype
    print("✅ LongPolling 표기 무관")


def test_webhook_not_exempt():
    """WebHook이면 평소대로 검사 (대소문자 무관)"""
    for ptype in ("Webhook", "WebHook", "webhook", "WEBHOOK"):
        assert not _is_desc_exempt(FIELD, _req(ptype, None)), ptype
    print("✅ WebHook — 면제 안 함")


def test_unknown_type_not_exempt():
    """전송 방식을 모르면 평소대로 검사"""
    assert not _is_desc_exempt(FIELD, _req(None, None))
    assert not _is_desc_exempt(FIELD, {"doorList": []})
    assert not _is_desc_exempt(FIELD, {"transProtocol": "문자열"})
    print("✅ 방식 불명 — 면제 안 함")


def test_other_fields_untouched():
    """transProtocolDesc 외의 필드는 영향 없음"""
    data = _req("LongPolling", None)
    for f in ("transProtocol.transProtocolType", "doorList.doorID",
              "startTime", "duration"):
        assert not _is_desc_exempt(f, data), f
    print("✅ 다른 필드 영향 없음")


def test_end_to_end_null_desc_passes():
    """실제 검증: LongPolling + desc=null 이면 전체 통과"""
    data = _req("LongPolling", None)
    r = json_check_(SCHEMA, data, False)
    assert r[0] == "PASS", f"{r[0]} / 실패 {r[3]}건"
    print(f"✅ LongPolling + null desc → {r[0]} (통과 {r[2]}, 실패 {r[3]})")


def test_end_to_end_webhook_null_desc_fails():
    """WebHook + desc=null 은 평소대로 실패로 잡힌다"""
    data = _req("WebHook", None)
    r = json_check_(SCHEMA, data, False)
    assert r[0] == "FAIL", f"WebHook인데 통과함: {r[0]}"
    print(f"✅ WebHook + null desc → {r[0]} (검사 유지)")


def test_end_to_end_webhook_normal_passes():
    """WebHook + 정상 주소는 통과"""
    data = _req("WebHook", "https://10.20.30.104:8081")
    r = json_check_(SCHEMA, data, False)
    assert r[0] == "PASS", f"{r[0]} / 실패 {r[3]}건"
    print("✅ WebHook + 정상 주소 → PASS")


def test_field_count_preserved():
    """면제해도 전체 필드 수는 그대로 (통과로 계상)"""
    lp = json_check_(SCHEMA, _req("LongPolling", None), False)
    wh = json_check_(SCHEMA, _req("WebHook", "https://x"), False)
    assert lp[2] + lp[3] == wh[2] + wh[3], f"{lp[2]}+{lp[3]} vs {wh[2]}+{wh[3]}"
    print(f"✅ 필드 수 동일 ({lp[2] + lp[3]}개) — 채점 분모 유지")


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
