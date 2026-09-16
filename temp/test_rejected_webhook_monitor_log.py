"""구독이 거절된 웹훅 회차도 응답·검증 결과가 모니터에 찍혀야 한다.

RealtimeVerifEventInfos 오류 회차(없는 문 door9999)에서 상대가 404로 구독을 거절하면
post()는 웹훅 창을 닫고 is_webhook_api=False로 내린다. 그런데 응답 처리는 시나리오
설정(WebHook)만 보고 수신 로그·결과 카드·필드 수를 전부 "웹훅 경로 담당"으로 넘겨,
모니터에 [송신] 요청 다음 곧바로 "시험 완료"가 떴다 (2026-09-14 단일시스템 모니터 로그).

실행: .venv\\Scripts\\python.exe temp\\test_rejected_webhook_monitor_log.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systemVal_all import MyApp


def main():
    eff = MyApp._effective_protocol
    emit = MyApp._should_emit_primary_result_log

    # 구독 거절 → 일반 응답으로 처리 → 마지막 회차 결과 카드가 찍힌다
    rejected = eff("WebHook", {"is_webhook_api": False})
    assert rejected == "basic", rejected
    assert emit(rejected, 0, 1) is True

    # 웹훅 정상 진행 → 그대로 WebHook → 결과 카드는 웹훅 집계(get_webhook_result)가 찍는다
    accepted = eff("WebHook", {"is_webhook_api": True})
    assert accepted == "WebHook", accepted
    assert emit(accepted, 0, 1) is False

    # 웹훅이 아닌 설정은 건드리지 않는다
    for protocol in ("basic", "LongPolling"):
        assert eff(protocol, {"is_webhook_api": False}) == protocol
    # 버퍼가 없으면(방어) 설정값 유지
    assert eff("WebHook", None) == "WebHook"

    print("OK — 거절된 웹훅 회차는 일반 응답으로 로그·결과 기록")


if __name__ == "__main__":
    main()
