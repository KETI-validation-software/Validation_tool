# -*- coding: utf-8 -*-
"""
웹훅 전송 시 transProtocolType 보존 회귀 시험 — systemVal_all.py

단일 도구가 웹훅 요청을 보낼 때 수신 주소(transProtocolDesc)를 실행 PC의
실제 IP/포트로 갈아끼운다. 예전에는 transProtocol 객체를 통째로 새로 만들며
내부 프로토콜 이름 "WebHook"(대문자 H)을 transProtocolType에 같이 써버렸다.
관리도구에 "Webhook"(소문자 h)으로 설정해도 전송 시점에 값이 바뀌어
받는 쪽 지정값 대조에서 실패했다 (2026-09-01 리허설).

실행: .venv\Scripts\python.exe temp\test_webhook_protocol_type_preserved.py
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "systemVal_all.py")


def _source():
    with open(SRC, encoding="utf-8") as f:
        return f.read()


def _code_lines():
    """주석·문자열 안쪽을 뺀 실행 코드 줄만 (설명 주석에 든 단어는 무시)"""
    out = []
    for line in _source().splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        out.append(line.split("#")[0])
    return out


def test_no_hardcoded_type_assignment():
    """전송 메시지에 transProtocolType을 하드코딩하지 않는다"""
    hits = [ln.strip() for ln in _code_lines()
            if '"transProtocolType"' in ln and ":" in ln and "get(" not in ln]
    assert not hits, f"transProtocolType을 직접 써넣는 줄이 남아 있음: {hits}"
    print("✅ transProtocolType 하드코딩 없음")


def test_desc_only_replaced():
    """수신 주소(Desc)만 갈아끼운다"""
    src = _source()
    assert 'trans_protocol["transProtocolDesc"] = WEBHOOK_URL' in src, \
        "Desc 교체 줄을 찾지 못함 — 로직이 바뀌었는지 확인 필요"
    assert "trans_protocol = dict(trans_protocol)" in src, \
        "원본 dict를 복사해 쓰는 줄이 없음 (원본 훼손 위험)"
    print("✅ Desc만 교체 + 원본 복사")


def test_detection_is_case_insensitive():
    """감지는 대소문자를 무시해야 Webhook/WebHook 둘 다 잡힌다"""
    src = _source()
    assert '"WebHook".lower() in str(trans_protocol_type).lower()' in src, \
        "대소문자 무시 감지 조건이 사라짐 — Webhook 설정이 웹훅으로 안 잡힐 수 있음"
    print("✅ 감지 조건 대소문자 무시 유지")


def test_semantics():
    """실제 변환 의미: Type 보존, Desc 교체, 원본 불변"""
    original = {"transProtocolType": "Webhook", "transProtocolDesc": "https://old:9999"}
    trans_protocol = dict(original)
    trans_protocol["transProtocolDesc"] = "https://10.20.30.104:8081"

    assert trans_protocol["transProtocolType"] == "Webhook", trans_protocol
    assert trans_protocol["transProtocolDesc"] == "https://10.20.30.104:8081"
    assert original["transProtocolDesc"] == "https://old:9999", "원본이 바뀜"
    print("✅ Type 보존 / Desc 교체 / 원본 불변")


def test_file_parses():
    """수정 후에도 파일이 정상 파싱된다"""
    ast.parse(_source())
    print("✅ 구문 정상")


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
