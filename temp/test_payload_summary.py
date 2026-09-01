# -*- coding: utf-8 -*-
"""
데이터 요약 로그 회귀 시험 — core/utils.summarize_payload

로그에 개수·통과여부만 남아 "무엇이 오갔는지"(cam0001인지 cam9999인지)를
알 수 없었다. 송·수신 시점에 실제 값을 한 줄로 남기기 위한 요약 함수.

실행: .venv\Scripts\python.exe temp\test_payload_summary.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import summarize_payload


def test_object_list_shows_ids():
    """객체 목록은 개수 + 대표 ID들을 보여준다"""
    data = {"camList": [{"camID": f"cam000{i}", "camName": f"카메라{i}"} for i in range(1, 6)]}
    out = summarize_payload(data)
    assert "camList 5건" in out, out
    for i in range(1, 6):
        assert f"cam000{i}" in out, f"cam000{i} 누락: {out}"
    print(f"✅ 객체 목록: {out}")


def test_secrets_masked():
    """비밀번호·토큰은 값 대신 ***"""
    out = summarize_payload({"userID": "kisa", "userPW": "kisa_k1!2@",
                             "accessToken": "abcd1234"})
    assert "userID=kisa" in out, out
    assert "kisa_k1!2@" not in out and "abcd1234" not in out, f"비밀값 노출: {out}"
    assert out.count("***") == 2, out
    print(f"✅ 민감값 마스킹: {out}")


def test_nested_dict_inlined():
    """중첩 객체(timePeriod 등)는 한 줄로 펼친다"""
    out = summarize_payload({"timePeriod": {"startTime": "20260817163010123",
                                            "endTime": "20260822163010123"}})
    assert "startTime=20260817163010123" in out and "endTime=" in out, out
    print(f"✅ 중첩 객체: {out}")


def test_scalar_array():
    """문자열 배열도 값이 보인다"""
    out = summarize_payload({"classFilter": ["Human", "사람"]})
    assert "classFilter 2건" in out and "Human" in out and "사람" in out, out
    print(f"✅ 문자열 배열: {out}")


def test_long_list_truncated():
    """긴 목록은 앞부분만 + 나머지 건수"""
    data = {"doorList": [{"doorID": f"door{i:04d}"} for i in range(1, 31)]}
    out = summarize_payload(data)
    assert "doorList 30건" in out and "외 18건" in out, out
    assert len(out) < 300, f"요약이 너무 김: {len(out)}자"
    print(f"✅ 긴 목록 축약: {out[:90]}…")


def test_empty_and_non_dict():
    """빈 본문·비딕셔너리도 안전"""
    assert summarize_payload({}) == "(빈 메시지)"
    assert summarize_payload("문자열") == "문자열"
    assert summarize_payload(None) == "None"
    print("✅ 빈 본문·비딕셔너리 처리")


def test_long_value_truncated():
    """긴 값은 잘라서 한 줄 유지"""
    out = summarize_payload({"camURL": "rtsp://" + "x" * 200})
    assert "…" in out and len(out) < 120, f"긴 값이 안 잘림: {len(out)}자"
    print("✅ 긴 값 축약")


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
