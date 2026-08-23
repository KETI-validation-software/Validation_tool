# -*- coding: utf-8 -*-
"""
무작위(random) 설정값 폴백 회귀 시험 — core/data_mapper.py

2026-08-20 실측: 데이터 사전 기반 무작위 필드가 빈 값으로 나감.
- 무작위 + 참조 필드가 "선택된" 규칙은 요청 생성 시점에 참조 응답이 아직 없어
  values가 비고, 폴백이 없어 템플릿 빈 값이 그대로 나갔다
- specifiedValues 형식(StreamURLs 응답 accessID 등)은 아예 미지원이었다
- 최상위 dict 안의 중첩 필드(filter.eventFilter 등) 제약은 조용히 무시됐다

(2026-08-23 다른 AI 제안 검토 후 현행 코드에 이식. 원본 수정은 8/13 이전
베이스라 폐기 — 이 시험이 이식본의 동작을 고정한다)

실행: .venv\Scripts\python.exe temp\test_random_static_values.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator


def gen(latest_events=None):
    return ConstraintDataGenerator(latest_events or {})


def test_random_with_selected_reference_falls_back():
    """무작위 + 참조 필드 선택 + 참조 응답 없음 → validValues로 폴백 (빈 값 금지)"""
    constraints = {
        "eventFilter": {
            "valueType": "random",
            "referenceField": "eventFilter",              # 참조 필드가 "선택됨"
            "referenceEndpoint": "/RealtimeVideoEventInfos",
            "validValues": ["Loitering", "Intrusion"],
        },
    }
    out = gen()._applied_constraints(
        request_data={}, template_data={"eventFilter": ""},
        constraints=constraints, api_name="RealtimeVideoEventInfos")
    assert out["eventFilter"] in ["Loitering", "Intrusion"], f"빈 값: {out}"
    print("✅ 무작위+참조 선택, 응답 없음 → validValues 폴백")


def test_random_unselected_reference_still_works():
    """기존 동작 유지: 참조 필드 미선택 무작위는 validValues에서 뽑는다"""
    constraints = {
        "eventFilter": {
            "valueType": "random",
            "referenceField": "(참조 필드 미선택)",
            "referenceEndpoint": "/RealtimeVideoEventInfos",
            "validValues": ["MotionDetection", "Leak"],
        },
    }
    out = gen()._applied_constraints(
        request_data={}, template_data={"eventFilter": ""},
        constraints=constraints, api_name="StoredSensorEventInfos")
    assert out["eventFilter"] in ["MotionDetection", "Leak"], f"빈 값: {out}"
    print("✅ 무작위(참조 미선택) → validValues 뽑기 유지")


def test_specified_values_supported():
    """specifiedValues 형식(무작위 지정값)도 재료로 인정"""
    constraints = {
        "accessID": {"valueType": "random", "specifiedValues": ["conn0001"]},
    }
    out = gen()._applied_constraints(
        request_data={}, template_data={"accessID": ""},
        constraints=constraints, api_name="StreamURLs")
    assert out["accessID"] == "conn0001", f"specifiedValues 미지원: {out}"
    print("✅ specifiedValues 형식 지원")


def test_reference_present_wins_over_fallback():
    """참조 응답이 실제로 있으면 폴백이 아니라 참조값을 쓴다"""
    events = {"CameraProfiles": {"RESPONSE": {"data": {
        "camList": [{"eventFilter": "Intrusion"}]}}}}
    constraints = {
        "eventFilter": {
            "valueType": "random-response",
            "referenceField": "eventFilter",
            "referenceEndpoint": "/CameraProfiles",
            "validValues": ["Loitering"],       # 폴백용 — 쓰이면 안 됨
        },
    }
    out = gen(events)._applied_constraints(
        request_data={}, template_data={"eventFilter": ""},
        constraints=constraints, api_name="X")
    assert out["eventFilter"] == "Intrusion", f"참조값 우선이어야 함: {out}"
    print("✅ 참조 응답이 있으면 참조값 우선 (폴백 미사용)")


def test_nested_dict_field_constraint_applied():
    """최상위 dict 안의 중첩 필드에도 제약 적용 (다른 키는 보존)"""
    constraints = {
        "filter.eventFilter": {"valueType": "random",
                               "validValues": ["Loitering"]},
    }
    template = {"filter": {"eventFilter": "", "keep": "그대로"}}
    out = gen()._applied_constraints(
        request_data={}, template_data=template,
        constraints=constraints, api_name="X")
    assert out["filter"]["eventFilter"] == "Loitering", f"중첩 제약 미적용: {out}"
    assert out["filter"]["keep"] == "그대로", f"무관 키 훼손: {out}"
    print("✅ 중첩 dict 필드 제약 적용 + 무관 키 보존")


def test_nested_dict_without_constraint_untouched():
    """제약 없는 중첩 dict(transProtocol 등)는 예전처럼 그대로"""
    template = {"transProtocol": {"transProtocolType": "WebHook",
                                  "transProtocolDesc": "https://x:8081"}}
    out = gen()._applied_constraints(
        request_data={}, template_data=dict(template),
        constraints={}, api_name="X")
    assert out["transProtocol"] == template["transProtocol"], f"훼손됨: {out}"
    print("✅ 제약 없는 중첩 dict는 불변 (webhook 주소 등 안전)")


def test_empty_field_name_rule_ignored_gracefully():
    """관리도구의 '' 빈 필드명 규칙은 어떤 필드에도 적용되지 않고 죽지도 않는다"""
    constraints = {
        "": {"valueType": "random", "required": True,
             "referenceEndpoint": "/DoorProfiles",
             "randomType": "exclude-reference-valid-values",
             "validValues": ["Loitering", "Intrusion"]},
    }
    template = {"eventFilter": ""}
    out = gen()._applied_constraints(
        request_data={}, template_data=dict(template),
        constraints=constraints, api_name="X")
    assert out["eventFilter"] == "", "빈 필드명 규칙이 엉뚱한 필드를 채움"
    print("✅ 빈 필드명('') 규칙 — 무시되고 예외 없음 (관리도구에서 고칠 몫)")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed += 1
            print(f"❌ {t.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ {t.__name__}: 예외 {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} 통과")
    sys.exit(1 if failed else 0)
