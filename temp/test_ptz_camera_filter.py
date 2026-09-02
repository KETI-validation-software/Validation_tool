# -*- coding: utf-8 -*-
"""
PTZ 카메라 선별 회귀 시험 — core/data_mapper

PTZ 제어(PTZStatus 등)는 PTZ 카메라에만 유효한데, CameraProfiles 응답의
camID 전체에서 무작위로 골라 보내다 보니 Dome/Bullet 카메라가 뽑히면
상대가 정상적으로 거절해 실패로 잡혔다.

camType 표기는 시스템마다 제각각이라, 대소문자를 무시하고 문자열에 'ptz'가
들어 있으면 모두 같은 PTZ 카메라로 본다 ('PTZ Camera', '고정형PTZ' 등 포함).
CameraProfiles 자체는 어떤 camType이든 그대로 받는다.

실행: .venv\Scripts\python.exe temp\test_ptz_camera_filter.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator as G


def _cams(*pairs):
    return {"code": "200", "camList": [
        {"camID": cid, "camName": cid, "camConfig": {"camType": ctype}}
        for cid, ctype in pairs
    ]}


def _collect(data, field="camID"):
    return G._collect_ptz_ids(G.__new__(G), data, field)


def test_is_ptz_api():
    """PTZ 계열 API 이름 판별 (대소문자 무시)"""
    for name in ("PTZStatus", "PTZControl", "ptzstatus", "PtzPresets"):
        assert G._is_ptz_api(name), name
    for name in ("CameraProfiles", "StreamURLs", "ReplayURL", "", None):
        assert not G._is_ptz_api(name), name
    print("✅ PTZ API 이름 판별")


def test_case_insensitive_ptz():
    """'PTZ' / 'ptz' / 'Ptz' 전부 PTZ 카메라로 인정"""
    data = _cams(("cam0001", "PTZ"), ("cam0002", "ptz"), ("cam0003", "Ptz"),
                 ("cam0004", " PTZ "))
    assert _collect(data) == ["cam0001", "cam0002", "cam0003", "cam0004"], _collect(data)
    print("✅ 대소문자·공백 무시")


def test_substring_ptz():
    """문자열 어디든 'ptz'가 들어 있으면 PTZ로 인정"""
    data = _cams(("cam0001", "PTZ Camera"), ("cam0002", "ptz-dome"),
                 ("cam0003", "고정형PTZ"), ("cam0004", "Speed_Ptz_01"))
    assert _collect(data) == ["cam0001", "cam0002", "cam0003", "cam0004"], _collect(data)
    print("✅ 부분 문자열 포함도 PTZ로 인정")


def test_non_ptz_excluded():
    """Dome/Bullet/RGB는 제외"""
    data = _cams(("cam0001", "PTZ"), ("cam0002", "Dome"),
                 ("cam0003", "Bullet"), ("cam0004", "RGB"))
    assert _collect(data) == ["cam0001"], _collect(data)
    print("✅ 비-PTZ 제외")


def test_no_ptz_camera_returns_empty():
    """PTZ가 하나도 없으면 빈 목록 (호출부가 경고 후 전체 사용)"""
    data = _cams(("cam0001", "Dome"), ("cam0002", "Bullet"))
    assert _collect(data) == [], _collect(data)
    print("✅ PTZ 없음 → 빈 목록")


def test_no_camtype_field_returns_none():
    """camType 자체가 없는 규격이면 None → 선별 생략"""
    data = {"camList": [{"camID": "cam0001"}, {"camID": "cam0002"}]}
    assert _collect(data) is None, _collect(data)
    print("✅ camType 없음 → 선별 생략(None)")


def test_camtype_directly_on_item():
    """camConfig 없이 camType이 항목 바로 아래 있어도 인식"""
    data = {"camList": [{"camID": "cam0001", "camType": "ptz"},
                        {"camID": "cam0002", "camType": "Dome"}]}
    assert _collect(data) == ["cam0001"], _collect(data)
    print("✅ camConfig 없는 구조도 인식")


def test_empty_and_malformed():
    """빈 응답·비정상 구조에서 예외 없이 처리"""
    assert _collect({}) is None
    assert _collect({"camList": []}) is None
    assert _collect({"camList": ["문자열", 3, None]}) is None
    print("✅ 빈 응답·비정상 구조 안전")


def test_filter_preserves_order_and_subset():
    """선별 결과는 원래 뽑힌 값의 부분집합이며 순서를 유지"""
    data = _cams(("cam0001", "Dome"), ("cam0002", "PTZ"),
                 ("cam0003", "ptz"), ("cam0004", "Bullet"))
    picked_before = ["cam0004", "cam0002", "cam0001", "cam0003"]  # 무작위 선택 결과 가정
    ptz_ids = _collect(data)
    picked = [v for v in picked_before if v in ptz_ids]
    assert picked == ["cam0002", "cam0003"], picked
    print("✅ 부분집합·순서 유지")


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
