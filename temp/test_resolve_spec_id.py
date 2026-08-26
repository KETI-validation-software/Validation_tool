# -*- coding: utf-8 -*-
"""
시나리오 이름 중복 해석 회귀 시험 — api/api_server.py의 _resolve_spec_id

시나리오 이름(test_name)이 여러 개에서 같으면(예: 셋 다 "sensor") 항상 첫 번째로
매칭돼, 두 번째 시험부터 do_POST의 spec_id 대조에서 400 거절 → 토큰 발급 실패가
났다. 수정 후에는 지금 진행 중인 시나리오(current_spec_id)의 이름과 일치하면
그것을 우선한다. 이름이 서로 다르면 기존 동작 그대로다.

실행: .venv\Scripts\python.exe temp\test_resolve_spec_id.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_server import Server

SPEC_CONFIG_DUP = [{
    "group_name": "sensor_err", "group_id": "g1",
    "spec_A": {"test_name": "sensor"},
    "spec_B": {"test_name": "sensor"},
    "spec_C": {"test_name": "sensor"},
}]

SPEC_CONFIG_UNIQ = [{
    "group_name": "sensor_err", "group_id": "g1",
    "spec_A": {"test_name": "sensor001"},
    "spec_B": {"test_name": "sensor002"},
}]


def make_handler(spec_config, current):
    h = object.__new__(Server)
    h.CONSTANTS = type("C", (), {"SPEC_CONFIG": spec_config})
    Server.current_spec_id = current
    return h


def test_duplicate_name_prefers_current():
    """이름이 겹치면 진행 중인 시나리오를 골라야 한다 (핵심 수정)"""
    for current in ("spec_A", "spec_B", "spec_C"):
        h = make_handler(SPEC_CONFIG_DUP, current)
        got = h._resolve_spec_id("sensor")
        assert got == current, f"진행 중={current}인데 {got}로 매칭됨"
    print("✅ 이름 중복 시 진행 중인 시나리오(A/B/C 각각) 우선 매칭")


def test_unique_names_unchanged():
    """이름이 다르면 기존과 동일 — 이름으로 정확히 찾는다"""
    h = make_handler(SPEC_CONFIG_UNIQ, "spec_A")
    assert h._resolve_spec_id("sensor001") == "spec_A"
    assert h._resolve_spec_id("sensor002") == "spec_B"  # 진행 중이 아니어도 이름대로
    print("✅ 이름이 유일하면 기존 동작 그대로")


def test_cuid_passthrough():
    """spec_id(cuid)가 직접 오면 변환 없이 그대로"""
    h = make_handler(SPEC_CONFIG_DUP, "spec_A")
    cuid = "cm" + "x" * 23
    assert h._resolve_spec_id(cuid) == cuid
    print("✅ cuid 형식은 그대로 통과")


def test_unknown_name_returns_original():
    """모르는 이름은 원본 반환 (기존 동작)"""
    h = make_handler(SPEC_CONFIG_DUP, "spec_A")
    assert h._resolve_spec_id("없는이름") == "없는이름"
    print("✅ 모르는 이름은 원본 반환")


def test_no_current_falls_back_to_first():
    """진행 중인 시나리오가 없으면(시험 전) 기존처럼 첫 번째 매칭"""
    h = make_handler(SPEC_CONFIG_DUP, None)
    assert h._resolve_spec_id("sensor") == "spec_A"
    print("✅ current 없으면 기존 폴백(첫 번째) 유지")


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
