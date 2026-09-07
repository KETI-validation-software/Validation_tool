# -*- coding: utf-8 -*-
"""
response-field-match 순서 무관 비교 회귀 시험 (2026-09-07)

어느 카메라를 조회할지의 '순서'는 규격이 정하는 바가 아니다. 상대 시스템이
임의 순서로 응답해도 정상인데, 리스트를 통째로 비교해 같은 5개가 순서만
달라도 실패로 잡혔다.

참조가 1개일 때는 다른 분기를 타서 이 문제가 안 드러났다 —
카메라 1대일 때는 통과하다가 5대가 되니 실패한 이유다.
(specified-value-match의 RTSP 배열 오판 8014621과 같은 유형)

같은 ID가 두 번 들어오는 경우는 없으므로 정렬 후 비교한다.
순서만 무시하고 개수·내용은 그대로 확인한다.

실행: .venv\Scripts\python.exe temp\test_field_match_order.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.functions import _validate_field_match  # noqa: E402

RULE = {"validationType": "response-field-match",
        "referenceEndpoint": "/CameraProfiles", "referenceField": "camID"}


def _run(response_ids, reference_ids):
    ctx = {"/CameraProfiles": {"code": "200",
                               "camList": [{"camID": c} for c in reference_ids]}}
    errs, gerrs = [], []
    ok = _validate_field_match("camList.camID", response_ids, RULE, ctx, errs, gerrs)
    return ok, errs


FIVE = ["cam0001", "cam0002", "cam0003", "cam0004", "cam0005"]


def test_shuffled_passes():
    """순서만 다르면 통과 — 실측 실패 사례"""
    ok, errs = _run(["cam0005", "cam0003", "cam0001", "cam0004", "cam0002"], FIVE)
    assert ok, errs
    print("✅ 순서 뒤바뀜 → 통과")


def test_same_order_passes():
    """같은 순서도 당연히 통과"""
    assert _run(FIVE, FIVE)[0]
    print("✅ 같은 순서 → 통과")


def test_missing_fails():
    """빠진 값이 있으면 실패 + 무엇이 빠졌는지 표시"""
    ok, errs = _run(["cam0001", "cam0002", "cam0003"], FIVE)
    assert not ok, "빠졌는데 통과함"
    assert "빠진 값" in errs[0] and "cam0004" in errs[0], errs[0]
    print(f"✅ 빠진 값 실패: {errs[0].splitlines()[-1].strip()}")


def test_extra_fails():
    """목록에 없는 값이 오면 실패 + 무엇이 남는지 표시"""
    ok, errs = _run(FIVE + ["cam9999"], FIVE)
    assert not ok, "없는 값인데 통과함"
    assert "없는 값" in errs[0] and "cam9999" in errs[0], errs[0]
    print(f"✅ 목록 밖 값 실패: {errs[0].splitlines()[-1].strip()}")


def test_swapped_value_fails():
    """개수는 같은데 내용이 다르면 실패"""
    ok, errs = _run(["cam0001", "cam0002", "cam0003", "cam0004", "cam9999"], FIVE)
    assert not ok, errs
    print("✅ 내용 불일치 실패")


def test_single_reference_unchanged():
    """참조가 1개일 때 기존 동작 유지 (모든 원소가 그 값이면 통과)"""
    assert _run(["cam0001"], ["cam0001"])[0]
    assert _run(["cam0001", "cam0001"], ["cam0001"])[0], "단일 참조 브로드캐스트가 깨짐"
    assert not _run(["cam0001", "cam0002"], ["cam0001"])[0]
    print("✅ 단일 참조 분기 기존 동작 유지")


def test_scalar_response():
    """응답이 낱값이어도 동작"""
    assert _run("cam0001", ["cam0001"])[0]
    print("✅ 낱값 응답 처리")


def test_mixed_types_no_crash():
    """숫자·문자 섞여도 정렬 중 예외가 나지 않는다"""
    ok, errs = _run([1, "cam0001"], ["cam0001", 1])
    assert ok, errs
    print("✅ 자료형 혼재 안전")


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
