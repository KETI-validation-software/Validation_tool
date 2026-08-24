# -*- coding: utf-8 -*-
"""
403 거절 기록 회귀 시험 — api/api_server.py의 _reject_403

⑤ 토큰 미포함 403은 이전에는 기록 없이 return해서 통합 UI가 그 단계에서
멈췄다(요청 카운터/이벤트가 안 남음). 수정 후에는 401 실패 경로와 동일하게
카운터 증가 + REQUEST/RESPONSE 이벤트 기록 후 403을 보내야 한다.

실행: .venv\Scripts\python.exe temp\test_reject_403.py
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_server import Server


def make_handler(events):
    """소켓 없이 핸들러 인스턴스를 만들어 전송부만 스텁으로 대체"""
    h = object.__new__(Server)
    h.request_data = {"dummy": 1}
    h._push_event = lambda api, direction, data: events.append((api, direction, data))
    h.send_response = lambda code: events.append(("HTTP", code, None))
    h.send_header = lambda *a: None
    h.end_headers = lambda: None
    h.wfile = io.BytesIO()
    return h


def test_reject_403_records_and_responds():
    Server.request_counter = {}
    events = []
    h = make_handler(events)

    h._reject_403("Capabilities")

    assert Server.request_counter.get("Capabilities") == 1, \
        f"카운터가 안 올라감: {Server.request_counter}"
    dirs = [(e[0], e[1]) for e in events if e[0] != "HTTP"]
    assert ("Capabilities", "REQUEST") in dirs, "REQUEST 이벤트 기록 누락"
    assert ("Capabilities", "RESPONSE") in dirs, "RESPONSE 이벤트 기록 누락"
    resp = [e for e in events if e[1] == "RESPONSE"][0][2]
    assert resp == {"code": "403", "message": "권한 없음"}, f"403 본문 불일치: {resp}"
    http = [e for e in events if e[0] == "HTTP"][0][1]
    assert http == 403, f"HTTP 상태 코드 불일치: {http}"
    body = h.wfile.getvalue().decode("utf-8")
    assert '"403"' in body, f"응답 본문에 403 없음: {body}"
    print("✅ _reject_403 — 카운터 증가 + REQUEST/RESPONSE 기록 + 403 응답")


def test_counter_isolated_per_api():
    Server.request_counter = {"Authentication": 1}
    events = []
    h = make_handler(events)
    h._reject_403("Capabilities")
    assert Server.request_counter == {"Authentication": 1, "Capabilities": 1}
    print("✅ 다른 API 카운터는 건드리지 않음")


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
