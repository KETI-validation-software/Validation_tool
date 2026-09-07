# -*- coding: utf-8 -*-
"""
로그 반복 정리 회귀 시험 (2026-09-02)

실측: 실시간 시험 로그 6,817줄 / 513,072자 중 63%가 반복이었다.
  33%  1초 폴링 루프가 같은 5줄을 매초 반복
  9.4% out_con 전체 덤프 + BUILD_MAP constraints 전체 덤프 (같은 내용 2번)
  3.9% do_POST 헤더 전문 (Authorization 토큰 포함)
  3.3% _push_event 한 건당 4줄

판정 로직은 건드리지 않고 출력만 줄인다.

실행: .venv\Scripts\python.exe temp\test_log_noise_reduction.py
"""
import os
import re
import sys
import time
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import platformVal_all  # noqa: E402
from api.api_server import Server  # noqa: E402


def _src(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


def test_polling_dedupe_suppresses_repeats():
    """같은 내용이 연달아 오면 첫 줄만 남는다"""
    printed = []
    orig = platformVal_all.Logger.debug
    platformVal_all.Logger.debug = lambda m: printed.append(m)
    try:
        stub = SimpleNamespace(_polling_log_state={})
        for _ in range(60):   # 60초 대기 흉내
            platformVal_all.MyApp._log_polling(stub, "wait:5", "대기 중 (API: ReplayURL)")
    finally:
        platformVal_all.Logger.debug = orig
    assert len(printed) == 1, f"{len(printed)}줄 출력됨 (1줄이어야 함)"
    print(f"✅ 폴링 60회 → {len(printed)}줄")


def test_polling_logs_on_change():
    """내용이 바뀌면 바로 남긴다 (정보 유실 없음)"""
    printed = []
    orig = platformVal_all.Logger.debug
    platformVal_all.Logger.debug = lambda m: printed.append(m)
    try:
        stub = SimpleNamespace(_polling_log_state={})
        platformVal_all.MyApp._log_polling(stub, "wait:5", "실제: 0회")
        platformVal_all.MyApp._log_polling(stub, "wait:5", "실제: 0회")
        platformVal_all.MyApp._log_polling(stub, "wait:5", "실제: 1회")   # 변화
    finally:
        platformVal_all.Logger.debug = orig
    assert printed == ["실제: 0회", "실제: 1회"], printed
    print("✅ 내용 변화 시 즉시 출력")


def test_polling_periodic_heartbeat():
    """오래 같은 상태여도 주기적으로 한 번은 남긴다 (멈춘 게 아님을 확인)"""
    printed = []
    orig = platformVal_all.Logger.debug
    platformVal_all.Logger.debug = lambda m: printed.append(m)
    try:
        stub = SimpleNamespace(_polling_log_state={})
        platformVal_all.MyApp._log_polling(stub, "k", "같은 줄", every=0.05)
        platformVal_all.MyApp._log_polling(stub, "k", "같은 줄", every=0.05)
        time.sleep(0.06)
        platformVal_all.MyApp._log_polling(stub, "k", "같은 줄", every=0.05)
    finally:
        platformVal_all.Logger.debug = orig
    assert len(printed) == 2, f"{len(printed)}줄 (주기 출력 2줄이어야 함)"
    print("✅ 주기적 heartbeat 유지")


def test_polling_keys_independent():
    """단계별로 따로 관리된다 (다른 API 로그를 삼키지 않음)"""
    printed = []
    orig = platformVal_all.Logger.debug
    platformVal_all.Logger.debug = lambda m: printed.append(m)
    try:
        stub = SimpleNamespace(_polling_log_state={})
        platformVal_all.MyApp._log_polling(stub, "wait:1", "A 대기")
        platformVal_all.MyApp._log_polling(stub, "wait:2", "B 대기")
        platformVal_all.MyApp._log_polling(stub, "wait:1", "A 대기")   # 억제
    finally:
        platformVal_all.Logger.debug = orig
    assert printed == ["A 대기", "B 대기"], printed
    print("✅ 단계별 독립 관리")


def test_no_full_constraint_dumps():
    """제약 전체 덤프가 사라졌다 (키 목록만)"""
    assert '[CONSTRAINTS] out_con value: {out_con}' not in _src("api/api_server.py"), \
        "out_con 전체 덤프가 남아 있음"
    assert '[BUILD_MAP] constraints: {constraints}' not in _src("core/data_mapper.py"), \
        "BUILD_MAP constraints 전체 덤프가 남아 있음"
    print("✅ 제약 전체 덤프 제거 (같은 내용 2번 → 키 목록)")


def test_headers_not_dumped_wholesale():
    """헤더 전문·토큰이 로그에 안 나간다"""
    s = _src("api/api_server.py")
    assert "headers={dict(self.headers)}" not in s, "헤더 전문 덤프가 남아 있음"
    assert "Authorization={'있음' if _auth else '없음'}" in s, "인증 헤더 유무 표시가 없음"
    print("✅ 헤더 전문·토큰 미출력, 유무만 표시")


def test_push_event_single_line():
    """_push_event가 한 줄로 줄었다"""
    s = _src("api/api_server.py")
    assert "[_push_event] 저장 전 latest_event 키" not in s
    assert "[_push_event] 저장 후 latest_event 키" not in s
    assert "[_push_event] {api_name} {direction} 저장" in s
    print("✅ _push_event 4줄 → 1줄")


def test_loopback_warning_exists():
    """루프백 웹훅 주소 경고"""
    for url in ("https://127.0.0.1:20000/webhook/abc",
                "http://localhost:8081/hook",
                "https://127.1.2.3:9000/x"):
        assert Server._is_loopback_url(url), url
    for url in ("https://10.20.30.104:8081", "https://example.com/hook", "", None):
        assert not Server._is_loopback_url(url), url
    assert "웹훅 주소가 자기 자신을 가리킴" in _src("api/api_server.py")
    print("✅ 루프백 주소 판별 + 경고 문구")


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
