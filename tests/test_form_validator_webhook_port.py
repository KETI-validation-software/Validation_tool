import unittest
from unittest.mock import Mock, patch

from form_validator import FormValidator, derive_webhook_port


class TestFormValidatorWebhookPort(unittest.TestCase):
    def test_uses_test_port_priority(self):
        self.assertEqual(derive_webhook_port(2000, "https://192.168.0.10:8080"), 2001)

    @patch("form_validator.resource_path", return_value="C:/tmp/CONSTANTS.py")
    def test_update_constants_includes_webhook_port_from_test_port(self, _mock_resource_path):
        validator = FormValidator.__new__(FormValidator)
        validator.parent = Mock()
        validator.parent.get_selected_url.return_value = "https://192.168.0.10:2000"
        validator.parent.test_port = 2000
        validator.parent.admin_code_edit = Mock()
        validator.parent.admin_code_edit.text.return_value = "1"
        validator.parent.contact_person = "tester"
        validator.parent.model_name = "model"
        validator.parent.request_id = "req-1"

        validator._collect_basic_info = Mock(return_value={})
        validator._collect_auth_info = Mock(return_value=("Digest Auth", "id,pw"))
        validator.overwrite_spec_config_from_mapping = Mock()
        validator._get_selected_spec_index = Mock(return_value=0)

        captured = {}

        def fake_update(_path, variables):
            captured.update(variables)

        validator._update_constants_file = fake_update

        ok = validator.update_constants_py()

        self.assertTrue(ok)
        self.assertEqual(captured["WEBHOOK_PORT"], 2001)


if __name__ == "__main__":
    unittest.main()
