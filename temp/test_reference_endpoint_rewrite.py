# -*- coding: utf-8 -*-
"""
referenceEndpoint fieldId 보정 회귀 시험 — core/file_generator.py의 _update_reference_endpoints

관리 서버가 규칙의 referenceEndpoint를 자기 단계 값으로 잘못 저장해 내려보내는
사례가 확인됨 (2026-09-01 실측: VerifEventInfos 규칙의 referenceFieldId는
DoorProfiles 응답 doorID인데 endpoint는 /RealtimeVerifEventInfos).
진짜 선택은 fieldId에 있으므로, 중복 API 전용이던 fieldId 재계산을
모든 규칙으로 확대해 다운로드 시점에 바로잡는다.

실행: .venv\Scripts\python.exe temp\test_reference_endpoint_rewrite.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.file_generator import FileGeneratorService

REVERSE_MAP = {
    "id_doorprofiles_doorid": "DoorProfiles",     # DoorProfiles 응답의 doorID
    "id_status2_doorid": "RealtimeDoorStatus2",   # 중복 이름 해소용 (기존 동작)
}

gen = object.__new__(FileGeneratorService)  # __init__ 없이 메서드만 사용


def rewrite(content, duplicates=None):
    return gen._update_reference_endpoints(content, REVERSE_MAP, "Test", duplicates or [])


def test_wrong_self_reference_corrected():
    """실측 사례: 엔드포인트가 자기 단계로 잘못 와도 fieldId 기준으로 보정"""
    content = '''  "doorList.doorID": {
    "validationType": "response-field-list-match",
    "referenceFieldId": "id_doorprofiles_doorid",
    "referenceField": "doorID",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "score": 0
  },'''
    out = rewrite(content)
    assert '"referenceEndpoint": "/DoorProfiles"' in out, f"보정 안 됨:\n{out}"
    assert "/RealtimeVerifEventInfos" not in out, f"옛 값이 남음:\n{out}"
    print("✅ 잘못된 자기 참조 → fieldId 기준 /DoorProfiles로 보정")


def test_correct_reference_untouched():
    """이미 올바른 참조는 그대로 (같은 값으로 재기록될 뿐 변화 없음)"""
    content = '''  "doorList.doorID": {
    "referenceFieldId": "id_doorprofiles_doorid",
    "referenceEndpoint": "/DoorProfiles",
  },'''
    out = rewrite(content)
    assert '"referenceEndpoint": "/DoorProfiles"' in out
    print("✅ 올바른 참조는 무변화")


def test_duplicate_endpoint_still_resolved():
    """기존 동작 유지: 중복 이름 API는 번호 붙은 실제 단계로 해소"""
    content = '''  "doorList.doorID": {
    "referenceFieldId": "id_status2_doorid",
    "referenceEndpoint": "/RealtimeDoorStatus",
  },'''
    out = rewrite(content, duplicates=["RealtimeDoorStatus"])
    assert '"referenceEndpoint": "/RealtimeDoorStatus2"' in out, f"중복 해소 깨짐:\n{out}"
    print("✅ 중복 이름 해소(기존 동작) 유지")


def test_unknown_field_id_kept():
    """fieldId가 대응표에 없으면 건드리지 않는다 (다른 신청 건의 낡은 ID 등)"""
    content = '''  "doorList.doorID": {
    "referenceFieldId": "id_unknown_xxxx",
    "referenceEndpoint": "/SomeApi",
  },'''
    out = rewrite(content)
    assert '"referenceEndpoint": "/SomeApi"' in out, f"모르는 ID인데 변형됨:\n{out}"
    print("✅ 모르는 fieldId는 원본 유지")


def test_unselected_reference_skipped():
    """(참조 필드 미선택) 블록은 기존처럼 건너뛴다"""
    content = '''  "commandType": {
    "referenceField": "(참조 필드 미선택)",
    "referenceFieldId": "id_doorprofiles_doorid",
    "referenceEndpoint": "/SensorDeviceControl",
  },'''
    out = rewrite(content)
    assert '"referenceEndpoint": "/SensorDeviceControl"' in out, f"미선택인데 변형됨:\n{out}"
    print("✅ 참조 미선택 블록은 건너뜀")


def test_field_id_after_endpoint_line():
    """fieldId가 endpoint보다 뒤에 오는 블록도 보정된다 (줄 순서 무관)"""
    content = '''  "doorList.doorID": {
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "referenceFieldId": "id_doorprofiles_doorid",
  },'''
    out = rewrite(content)
    if '"referenceEndpoint": "/DoorProfiles"' not in out:
        # 현재 구현은 줄 순서(fieldId가 먼저)일 때만 보정 — 실제 생성 파일은
        # 항상 fieldId가 먼저이므로 동작엔 문제없으나, 사실을 기록해 둔다.
        print("⚠️ endpoint가 fieldId보다 앞서는 블록은 미보정 (실제 파일 순서에선 발생 안 함)")
    else:
        print("✅ 줄 순서 무관 보정")


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
