import unittest

from core import functions


class WebhookStepBufferFieldsTests(unittest.TestCase):
    def test_update_webhook_step_buffer_fields_sets_expected_keys(self):
        step_buffer = {"data": "", "error": "", "result": "PASS"}
        webhook_data = {"eventId": "evt-001", "eventType": "motion"}

        functions.update_webhook_step_buffer_fields(
            step_buffer=step_buffer,
            webhook_data=webhook_data,
            webhook_error_text="timestamp validation failed",
            webhook_pass_cnt=2,
            webhook_total_cnt=3,
        )

        self.assertEqual(step_buffer["webhook_data"], webhook_data)
        self.assertEqual(step_buffer["webhook_error"], "timestamp validation failed")
        self.assertEqual(step_buffer["webhook_pass_cnt"], 2)
        self.assertEqual(step_buffer["webhook_total_cnt"], 3)

    def test_update_webhook_step_buffer_fields_copies_webhook_data(self):
        original_payload = {"eventId": "evt-002", "nested": {"k": "v"}}
        step_buffer = {}

        functions.update_webhook_step_buffer_fields(
            step_buffer=step_buffer,
            webhook_data=original_payload,
            webhook_error_text="",
            webhook_pass_cnt=1,
            webhook_total_cnt=1,
        )

        original_payload["nested"]["k"] = "changed"

        self.assertEqual(step_buffer["webhook_data"]["nested"]["k"], "v")


if __name__ == "__main__":
    unittest.main()
