# -*- coding: utf-8 -*-
"""오류 응답 판정 ④ 요청 검증 규칙 → 400 (api_server._check_request_errors)

관리도구가 오류 시나리오로 요청에 틀린 값을 박아 보내면(예: 웹훅 구독의
transProtocolType에 "HTTP"), 통합플랫폼 역할은 400으로 거절해야 한다.
규칙 검사는 채점 검증기와 같은 함수를 쓰고, 규칙 종류별 취급은
Server.REQUEST_RULE_JUDGEMENT 표가 정한다 — 값 규칙만 400, 시각·참조·채점
전용 규칙은 여기서 보지 않는다. 인증 API는 제외(자격 증명은 401 몫).

실행: .venv/Scripts/python.exe tests/test_api_server_valid_value_400.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_server import Server
from core.data_mapper import ConstraintDataGenerator

SUBSCRIBE_REQUEST = {
    "sensorDeviceList": [{"sensorDeviceID": "iot0005"}, {"sensorDeviceID": "iot0004"}],
    "duration": 60,
    "transProtocol": {"transProtocolType": "Webhook", "transProtocolDesc": "https://10.20.30.101:8081"},
    "eventFilter": ["Fire"],
    "startTime": "20260915112739438",
}

SPECIFIED_RULE = {
    "transProtocol.transProtocolType": {
        "enabled": True, "validationType": "specified-value-match",
        "allowedValues": ["Webhook"], "score": 0,
    },
}
VALID_VALUE_RULE = {
    "eventFilter": {
        "enabled": True, "validationType": "valid-value-match",
        "validValueOperator": "equalsAny", "allowedValues": ["Fire", "Smoke"], "score": 0,
    },
}
TIME_RULE = {
    "startTime": {
        "enabled": True, "validationType": "range-match", "rangeOperator": "between",
        "rangeMin": "20260817163010123", "rangeMax": "20260822163010123", "score": 0,
    },
}
REFERENCE_RULE = {
    "sensorDeviceList.sensorDeviceID": {
        "enabled": True, "validationType": "response-field-list-match",
        "referenceField": "sensorDeviceList.sensorDeviceID",
        "referenceEndpoint": "/SensorDeviceProfiles", "isArrayFieldPath": True, "score": 0,
    },
}
UNKNOWN_RULE = {
    "duration": {"enabled": True, "validationType": "some-new-rule", "allowedValues": [1]},
}
AUTH_RULES = {
    "userID": {"enabled": True, "validationType": "specified-value-match", "allowedValues": ["kisa"]},
    "userPW": {"enabled": True, "validationType": "specified-value-match", "allowedValues": ["kisa_k1!2@"]},
}


def make_server(api_name, rules):
    """소켓을 열지 않고 판정 메서드만 쓰기 위한 최소 인스턴스"""
    srv = object.__new__(Server)
    srv.CONSTANTS = type("C", (), {"ENABLE_ERROR_RESPONSE_CHECK": True, "flag_opt": True})
    srv.generator = ConstraintDataGenerator({})
    srv.message = [api_name]
    srv.inSchema = [None]  # 스키마 없음 → 누락/타입 검사 생략, 규칙 판정만 본다
    Server.inCon = [rules]
    Server.current_spec_id = None  # registry 경로 차단 — inCon 오버라이드 사용
    Server.request_has_error = {}
    Server.valid_ids_by_field = {"camID": set(), "doorID": set(), "sensorDeviceID": set()}
    return srv


def judge(rules, request, api_name="RealtimeSensorData"):
    return make_server(api_name, rules)._check_request_errors(api_name, request)


class RequestRuleJudgementTests(unittest.TestCase):
    def test_specified_value_mismatch_is_400(self):
        bad = dict(SUBSCRIBE_REQUEST, transProtocol={"transProtocolType": "HTTP", "transProtocolDesc": ""})
        result = judge(SPECIFIED_RULE, bad)
        self.assertIsNotNone(result, "지정값과 다른 transProtocolType을 정상으로 판정함")
        self.assertEqual(result["code"], "400")

    def test_specified_value_match_passes(self):
        self.assertIsNone(judge(SPECIFIED_RULE, dict(SUBSCRIBE_REQUEST)), "지정값과 같은데 오류로 판정함")

    def test_valid_value_element_mismatch_is_400(self):
        bad = dict(SUBSCRIBE_REQUEST, eventFilter=["Fire", "무단침입"])
        result = judge(VALID_VALUE_RULE, bad)
        self.assertIsNotNone(result, "허용 목록 밖 원소를 정상으로 판정함")
        self.assertEqual(result["code"], "400")

    def test_valid_value_empty_array_passes(self):
        # 빈 배열은 "필터 없음" — 2026-08-19 실측 오판 방지
        self.assertIsNone(judge(VALID_VALUE_RULE, dict(SUBSCRIBE_REQUEST, eventFilter=[])))

    def test_time_rule_not_judged_here(self):
        # 시험 구간 밖 시각이라도 형식이 맞으면 400이 아니다 (시각 판정 몫)
        self.assertIsNone(judge(TIME_RULE, dict(SUBSCRIBE_REQUEST)))

    def test_reference_rule_not_judged_here(self):
        # 참조 꾸러미 없이 판정할 수 없다 (장치 목록은 404 판정 몫)
        self.assertIsNone(judge(REFERENCE_RULE, dict(SUBSCRIBE_REQUEST)))

    def test_unknown_rule_type_does_not_break(self):
        # 표에 없는 종류는 값 규칙으로 보되, 검증기가 모르는 종류면 통과 처리
        self.assertIsNone(judge(UNKNOWN_RULE, dict(SUBSCRIBE_REQUEST)))

    def test_disabled_rule_is_skipped(self):
        rules = {"transProtocol.transProtocolType": dict(SPECIFIED_RULE["transProtocol.transProtocolType"], enabled=False)}
        bad = dict(SUBSCRIBE_REQUEST, transProtocol={"transProtocolType": "HTTP", "transProtocolDesc": ""})
        self.assertIsNone(judge(rules, bad))

    def test_missing_field_is_schema_job(self):
        # 값이 없으면 규칙 판정은 하지 않는다 — 누락은 스키마 검사(②)가 400을 낸다
        without = {k: v for k, v in SUBSCRIBE_REQUEST.items() if k != "transProtocol"}
        self.assertIsNone(judge(SPECIFIED_RULE, without))

    def test_authentication_credentials_not_judged_here(self):
        result = judge(AUTH_RULES, {"userID": "kisa", "userPW": "wrong"}, api_name="Authentication")
        self.assertIsNone(result, "자격 증명은 인증 경로(401) 몫인데 400으로 판정함")

    def test_every_spec_rule_type_is_in_table(self):
        # 실제 산출물에 등장하는 규칙 종류가 표에 빠져 있으면 기본값(value)으로
        # 떨어진다 — 의도한 분류인지 여기서 드러나게 한다.
        import glob, re
        used = set()
        for f in glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spec", "*alidation_request.py")):
            with open(f, encoding="utf-8") as fh:
                used.update(re.findall(r'"validationType": "([a-z-]+)"', fh.read()))
        missing = used - set(Server.REQUEST_RULE_JUDGEMENT)
        self.assertFalse(missing, f"표에 없는 규칙 종류: {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
