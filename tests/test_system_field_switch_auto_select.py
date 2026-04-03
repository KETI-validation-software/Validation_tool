import unittest
from unittest.mock import Mock

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


if __name__ == "__main__":
    unittest.main()
