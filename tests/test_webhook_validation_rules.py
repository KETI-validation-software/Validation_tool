# -*- coding: utf-8 -*-
"""웹훅 검증 규칙이 실제로 채점에 들어가는지 (양쪽 역할)

- 통합플랫폼: 웹훅 응답(ACK)을 registry의 {API}_webhook/out 규칙으로 채점한다.
  규칙 없이 돌면 message "Success"도 통과였다 (2026-09-15 실측).
- 단일시스템: 자리맞춤된 규칙 목록(12597aa 형식)을 단계 번호 그대로 쓴다.
  압축 목록 가정으로 정렬하면 첫 None을 집어 0개가 됐다 (09-07 이후 실측).

실행: .venv/Scripts/python.exe tests/test_webhook_validation_rules.py
"""
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.functions import json_check_
from core.validation_registry import _collect_from_module

ACK_SCHEMA = {"code": str, "message": str}
ACK_RULES = {
    "code": {"enabled": True, "validationType": "specified-value-match", "allowedValues": ["200"], "score": 0},
    "message": {"enabled": True, "validationType": "specified-value-match", "allowedValues": ["성공"], "score": 0},
}


class PlatformAckRulesTests(unittest.TestCase):
    def test_registry_exposes_webhook_out_rules_under_api_webhook(self):
        mod = types.ModuleType("fake_validation")
        mod.cmspec_RealtimeSensorData_webhook_out_validation = ACK_RULES
        mod.cmspec_RealtimeSensorData_in_validation = {}
        reg = _collect_from_module(mod)
        self.assertIn("RealtimeSensorData_webhook", reg["cmspec"]["out"])
        self.assertEqual(reg["cmspec"]["out"]["RealtimeSensorData_webhook"], ACK_RULES)

    def test_ack_success_fails_with_rules(self):
        result = json_check_(ACK_SCHEMA, {"code": "200", "message": "Success"}, True, validation_rules=ACK_RULES)
        self.assertEqual(result[0], "FAIL")

    def test_ack_wrong_code_fails_with_rules(self):
        result = json_check_(ACK_SCHEMA, {"code": "500", "message": "성공"}, True, validation_rules=ACK_RULES)
        self.assertEqual(result[0], "FAIL")

    def test_ack_exact_passes(self):
        result = json_check_(ACK_SCHEMA, {"code": "200", "message": "성공"}, True, validation_rules=ACK_RULES)
        self.assertEqual(result[0], "PASS")

    def test_platform_passes_rules_to_every_ack_scoring_call(self):
        # 세 곳의 ACK 채점 호출 모두 규칙을 넘겨야 한다 — 하나라도 빠지면 그 분기는 구조만 본다
        src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platformVal_all.py"), encoding="utf-8").read()
        import re
        calls = len(re.findall(r"json_check_\(\s*\(self\.videoWebhookSchema\[self\.cnt\]", src))
        with_rules = src.count("validation_rules=webhook_ack_rules")
        self.assertGreaterEqual(calls, 3)
        self.assertEqual(with_rules, calls, "웹훅 ACK 채점 호출 중 규칙을 넘기지 않는 곳이 있음")


class SystemWebhookRuleAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from systemVal_all import MyApp
        cls.align = staticmethod(MyApp._align_webhook_rules)

    def test_padded_list_is_used_as_is(self):
        rules = {"doorList.doorID": {"validationType": "response-field-list-match"}}
        schemas = [None, None, None, None, {"doorList": list}]
        aligned = self.align([None, None, None, None, rules], schemas)
        self.assertEqual(aligned[4], rules)
        self.assertEqual(sum(1 for r in aligned if r), 1)

    def test_legacy_compact_list_is_spread_to_schema_slots(self):
        rules = {"camList.camID": {"validationType": "response-field-list-match"}}
        schemas = [None, None, {"camList": list}, None]
        aligned = self.align([rules], schemas)
        self.assertEqual(aligned[2], rules)
        self.assertEqual(sum(1 for r in aligned if r), 1)

    def test_two_webhook_steps_padded(self):
        r1, r2 = {"a": {}}, {"b": {}}
        schemas = [None, {"x": str}, None, {"y": str}]
        aligned = self.align([None, r1, None, r2], schemas)
        self.assertEqual((aligned[1], aligned[3]), (r1, r2))


if __name__ == "__main__":
    unittest.main()
