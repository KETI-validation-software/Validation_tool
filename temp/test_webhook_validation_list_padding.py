# -*- coding: utf-8 -*-
"""
웹훅 검증 규칙 목록 자리 맞춤 회귀 시험 — core/file_generator

웹훅 관련 목록은 4종류(스키마·데이터·제약·검증규칙)인데, 읽는 쪽은 모두
단계 번호(webhook_cnt)로 접근한다. 스키마·데이터·제약은 웹훅이 아닌 자리를
None으로 채워 API 수만큼 길이를 맞추는데, **검증 규칙만 빠져 있었다.**

실측(2026-09-02, 주신 validation_request.py):
  inValidation          = [Authentication, Capabilities, CameraProfiles,
                           StreamURLs, RealtimeVideoEventInfos]   ← 5칸
  webhook_outValidation = [RealtimeVideoEventInfos_webhook_out]   ← 1칸
웹훅 API는 4번인데 목록에는 0번에 있어, rules_list[4]가 없어서 규칙 없이
검증이 돌았다. 웹훅 API가 둘 이상이면 다른 API 규칙을 집을 수도 있었다.

실행: .venv\Scripts\python.exe temp\test_webhook_validation_list_padding.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

SRC = os.path.join(ROOT, "core", "file_generator.py")


def _emit(endpoint_names, webhook_validation_names, schema_type):
    """생성기의 목록 작성 로직과 동일한 규칙"""
    out = []
    for endpoint in endpoint_names:
        name = (f"{endpoint}_webhook_out_validation" if schema_type == "request"
                else f"{endpoint}_webhook_in_validation")
        out.append(name if name in webhook_validation_names else None)
    return out


APIS = ["Authentication", "Capabilities", "CameraProfiles",
        "StreamURLs", "RealtimeVideoEventInfos"]


def test_length_matches_api_count():
    """목록 길이가 API 수와 같다"""
    got = _emit(APIS, ["RealtimeVideoEventInfos_webhook_out_validation"], "request")
    assert len(got) == len(APIS), f"{len(got)}칸 (API {len(APIS)}개)"
    print(f"✅ 길이 일치 ({len(got)}칸)")


def test_webhook_rule_at_its_own_index():
    """웹훅 API의 규칙이 그 API의 번호 자리에 온다"""
    got = _emit(APIS, ["RealtimeVideoEventInfos_webhook_out_validation"], "request")
    idx = APIS.index("RealtimeVideoEventInfos")
    assert got[idx] == "RealtimeVideoEventInfos_webhook_out_validation", got
    assert all(v is None for i, v in enumerate(got) if i != idx), got
    print(f"✅ {idx}번 자리에 규칙, 나머지는 None")


def test_multiple_webhook_apis():
    """웹훅 API가 둘 이상이어도 각자 자리에"""
    apis = ["Authentication", "RealtimeDoorStatus", "DoorProfiles",
            "RealtimeVerifEventInfos"]
    names = ["RealtimeDoorStatus_webhook_out_validation",
             "RealtimeVerifEventInfos_webhook_out_validation"]
    got = _emit(apis, names, "request")
    assert got[1] == names[0] and got[3] == names[1], got
    assert got[0] is None and got[2] is None, got
    print("✅ 웹훅 2개 — 각자 자리(1번·3번)")


def test_response_direction_naming():
    """응답 방향은 _webhook_in_validation 이름을 쓴다"""
    got = _emit(APIS, ["RealtimeVideoEventInfos_webhook_in_validation"], "response")
    assert got[4] == "RealtimeVideoEventInfos_webhook_in_validation", got
    print("✅ 응답 방향 이름 규칙")


def test_no_webhook_api():
    """웹훅 API가 없으면 전부 None (길이는 유지)"""
    got = _emit(APIS, [], "request")
    assert len(got) == len(APIS) and all(v is None for v in got), got
    print("✅ 웹훅 없음 — 전부 None, 길이 유지")


def test_generator_source_uses_padding():
    """생성기가 실제로 endpoint_names를 돌며 None을 채운다"""
    src = open(SRC, encoding="utf-8").read()
    m = re.search(r"WebHook Validation 리스트 생성(.{0,1400}?)validation_content \+= \"\]",
                  src, re.S)
    assert m, "웹훅 검증 리스트 생성 블록을 찾지 못함"
    block = m.group(1)
    assert "for endpoint in endpoint_names:" in block, "자리 맞춤 순회가 없음"
    assert 'None,\\n' in block or "None,\\n" in block, "None 채우기가 없음"
    assert "for vname in webhook_validation_names:" not in block, \
        "예전 방식(있는 것만 나열)이 남아 있음"
    print("✅ 생성기 소스 — 자리 맞춤 적용 확인")


def test_matches_schema_list_style():
    """스키마 목록과 같은 방식인지 (두 블록 모두 endpoint_names 순회 + None)"""
    src = open(SRC, encoding="utf-8").read()
    for label in ("WebHook 스키마 리스트", "WebHook 검증 리스트"):
        m = re.search(re.escape(label) + r"(.{0,1400}?)validation_content \+= \"\]|"
                      + re.escape(label) + r"(.{0,1400}?)schema_content \+= \"\]",
                      src, re.S)
        assert m, f"{label} 블록을 찾지 못함"
        block = (m.group(1) or m.group(2) or "")
        assert "for endpoint in endpoint_names:" in block, f"{label}: 순회 없음"
    print("✅ 스키마 목록과 동일한 방식")


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
