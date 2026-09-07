# -*- coding: utf-8 -*-
"""
웹훅 API 선별 기준 회귀 시험 — core.utils.webhook_api_names (2026-09-07)

웹훅 자료를 걸러내는 쪽(platformVal)과 꺼내 쓰는 쪽(api_server)이 각자
"이름에 Realtime이 들어가면 웹훅"이라고 판단했다. 이름과 실제 전송 방식은
별개라서, RealtimeDoorStatus처럼 이름은 Realtime이지만 LongPolling인 API가
웹훅 목록에 끼어 번호를 한 칸씩 밀었다.

  이름 기준:  [RealtimeDoorStatus, RealtimeVerifEventInfos]   ← 2칸
              0번                  1번
  실제 자료:  [RealtimeVerifEventInfos것]                      ← 1칸, 0번
  → 1번을 찾는데 자료는 0번에 있어 어긋남

이제 전송 방식(trans_protocol)을 기준으로 판단한다.

실행: .venv\Scripts\python.exe temp\test_webhook_api_selection.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.utils import webhook_api_names  # noqa: E402

AC_APIS = ["Authentication", "Capabilities", "DoorProfiles",
           "RealtimeDoorStatus", "RealtimeVerifEventInfos"]
AC_PROTO = ["basic", "basic", "basic", "LongPolling", "WebHook"]


def _src(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


def test_longpolling_excluded():
    """이름이 Realtime이어도 LongPolling이면 웹훅이 아니다"""
    got = webhook_api_names(AC_APIS, AC_PROTO)
    assert got == ["RealtimeVerifEventInfos"], got
    print(f"✅ LongPolling 제외 → {got}")


def test_index_now_matches():
    """웹훅 API의 번호가 자료 번호와 맞는다"""
    got = webhook_api_names(AC_APIS, AC_PROTO)
    assert got.index("RealtimeVerifEventInfos") == 0, got
    print("✅ 번호 일치 (0번)")


def test_case_insensitive_protocol():
    """전송 방식 표기가 달라도 인식"""
    for p in ("WebHook", "Webhook", "webhook", "WEBHOOK"):
        got = webhook_api_names(["A", "B"], ["basic", p])
        assert got == ["B"], (p, got)
    print("✅ 전송 방식 표기 무관")


def test_multiple_webhooks_keep_order():
    """웹훅이 여럿이면 원래 순서를 유지한다"""
    apis = ["A", "RealtimeX", "B", "RealtimeY"]
    proto = ["basic", "WebHook", "LongPolling", "WebHook"]
    assert webhook_api_names(apis, proto) == ["RealtimeX", "RealtimeY"]
    print("✅ 다중 웹훅 순서 유지")


def test_non_realtime_name_webhook_included():
    """이름에 Realtime이 없어도 웹훅이면 포함 (예전엔 누락됐다)"""
    apis = ["Authentication", "EventStream"]
    proto = ["basic", "WebHook"]
    assert webhook_api_names(apis, proto) == ["EventStream"]
    print("✅ Realtime 아닌 이름의 웹훅도 포함")


def test_fallback_without_protocol():
    """전송 방식 정보가 없으면 예전처럼 이름으로 (하위 호환)"""
    assert webhook_api_names(AC_APIS) == ["RealtimeDoorStatus", "RealtimeVerifEventInfos"]
    assert webhook_api_names(AC_APIS, []) == ["RealtimeDoorStatus", "RealtimeVerifEventInfos"]
    print("✅ 방식 정보 없음 → 이름 기준 폴백")


def test_fallback_when_no_webhook_in_protocols():
    """방식 목록은 있는데 웹훅이 하나도 없으면 이름으로 한 번 더 본다"""
    got = webhook_api_names(AC_APIS, ["basic"] * 5)
    assert got == ["RealtimeDoorStatus", "RealtimeVerifEventInfos"], got
    print("✅ 방식에 웹훅 없음 → 이름 기준 폴백 (기존 동작 보존)")


def test_empty_and_short_lists():
    """빈 목록·길이 불일치에서 예외 없이 동작"""
    assert webhook_api_names([], []) == []
    assert webhook_api_names(None, None) == []
    assert webhook_api_names(["A", "B", "C"], ["WebHook"]) == ["A"]
    print("✅ 빈 목록·길이 불일치 안전")


def test_both_sides_use_helper():
    """양쪽 코드가 같은 헬퍼를 쓴다 (규칙이 갈라지지 않도록)"""
    assert 'webhook_api_names' in _src("api/api_server.py"), "api_server 미적용"
    assert 'webhook_api_names' in _src("platformVal_all.py"), "platformVal 미적용"
    assert '[msg for msg in self.message if "Realtime" in msg]' not in _src("api/api_server.py"), \
        "api_server에 예전 이름 기준이 남아 있음"
    assert 'if "Realtime" in msg:' not in _src("platformVal_all.py"), \
        "platformVal에 예전 이름 기준이 남아 있음"
    print("✅ 양쪽 모두 공용 헬퍼 사용")


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
