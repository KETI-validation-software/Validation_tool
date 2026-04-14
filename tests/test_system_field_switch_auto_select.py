import unittest
from unittest.mock import Mock
from types import SimpleNamespace

from systemVal_all import MyApp


class SystemFieldSwitchAutoSelectTests(unittest.TestCase):
    def _build_dummy_app(self, row_count):
        spec_config = [
            {"group_name": "group-a", "group_id": "group-a-id", "spec-1": {"test_name": "sensor002"}},
        ]

        table = Mock()
        table.rowCount.return_value = row_count

        dummy = type("DummyApp", (), {})()
        dummy.index_to_group_name = {0: "group-a"}
        dummy.LOADED_SPEC_CONFIG = spec_config
        dummy.CONSTANTS = type("Constants", (), {"SPEC_CONFIG": spec_config})()
        dummy.current_group_id = "old-group-id"
        dummy.current_spec_id = "old-spec-id"
        dummy.test_field_table = table
        dummy.update_test_field_table = Mock()
        dummy.on_test_field_selected = Mock()
        dummy._auto_select_first_scenario = lambda: MyApp._auto_select_first_scenario(dummy)
        return dummy, spec_config[0], table

    def test_on_group_selected_auto_selects_first_scenario_for_new_group(self):
        dummy, selected_group, table = self._build_dummy_app(row_count=2)

        MyApp.on_group_selected(dummy, 0, 0)

        dummy.update_test_field_table.assert_called_once_with(selected_group)
        table.selectRow.assert_called_once_with(0)
        dummy.on_test_field_selected.assert_called_once_with(0, 0)
        self.assertEqual(dummy.current_group_id, "group-a-id")
        self.assertIsNone(dummy.current_spec_id)

    def test_on_group_selected_skips_auto_select_when_group_has_no_scenarios(self):
        dummy, selected_group, table = self._build_dummy_app(row_count=0)

        MyApp.on_group_selected(dummy, 0, 0)

        dummy.update_test_field_table.assert_called_once_with(selected_group)
        table.selectRow.assert_not_called()
        dummy.on_test_field_selected.assert_not_called()

    def test_on_group_selected_skips_auto_select_when_restore_suppression_is_enabled(self):
        dummy, selected_group, table = self._build_dummy_app(row_count=2)
        dummy._suppress_group_auto_select = True

        MyApp.on_group_selected(dummy, 0, 0)

        dummy.update_test_field_table.assert_called_once_with(selected_group)
        table.selectRow.assert_not_called()
        dummy.on_test_field_selected.assert_not_called()

    def test_on_test_field_selected_forced_restore_refreshes_same_spec_without_saving_stale_table(self):
        table = Mock()
        table.rowCount.return_value = 0

        dummy = type("DummyApp", (), {})()
        dummy.index_to_spec_id = {1: "spec-2"}
        dummy.current_spec_id = "spec-2"
        dummy.current_group_id = "group-a-id"
        dummy._force_result_page_restore = True
        dummy.tableWidget = table
        dummy.save_current_spec_data = Mock()
        dummy.load_specs_from_constants = Mock()
        dummy.update_result_table_structure = Mock()
        dummy.restore_spec_data = Mock(return_value=True)
        dummy.get_setting = Mock()
        dummy.update_score_display = Mock()
        dummy.valResult = Mock()
        dummy.videoMessages = ["api-a", "api-b"]
        dummy.videoMessagesDisplay = ["api-a", "api-b"]
        dummy.videoOutMessage = []
        dummy.videoOutConstraint = []
        dummy.videoInSchema = []
        dummy.trace = Mock()
        dummy.latest_events = {}
        dummy.step_buffers = []
        dummy.Server = SimpleNamespace()
        dummy.spec_config = {"test_name": "vid002"}
        dummy.spec_description = "video scenario"
        dummy._original_base_url = "https://example.test"
        dummy.CONSTANTS = type("Constants", (), {"url": "https://example.test"})()
        dummy.url_text_box = Mock()

        MyApp.on_test_field_selected(dummy, 1, 0)

        dummy.save_current_spec_data.assert_not_called()
        dummy.load_specs_from_constants.assert_called_once()
        dummy.update_result_table_structure.assert_called_once_with(dummy.videoMessages)
        dummy.restore_spec_data.assert_called_once_with("spec-2")


if __name__ == "__main__":
    unittest.main()
