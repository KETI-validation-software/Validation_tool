import unittest
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

import config.CONSTANTS as CONSTANTS
from platformVal_all import MyApp
from systemVal_all import MyApp as SystemMyApp
from ui.ui_components import TestSelectionPanel


def _any_spec_id():
    """지금 로드된 SPEC_CONFIG에서 시험 ID 하나를 고른다.

    예전에는 특정 ID를 박아뒀는데, 등록된 시험이 바뀌면 그 ID가 사라져
    "설정을 찾을 수 없습니다"로 늘 실패했다.
    """
    for group in getattr(CONSTANTS, "SPEC_CONFIG", []) or []:
        if not isinstance(group, dict):
            continue
        for spec_id, entry in group.items():
            if spec_id not in ("group_name", "group_id") and isinstance(entry, dict):
                return spec_id
    return None


class TestTestSelectionPanelLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    @patch("ui.ui_components.load_external_constants")
    def test_common_test_selection_panel_keeps_compact_scenario_height(self, mock_load_external_constants):
        mock_load_external_constants.return_value = [
            {"group_name": "그룹 A", "group_id": "group-a"},
        ]

        panel = TestSelectionPanel(constants=object())

        self.assertEqual(panel.original_field_group_size, (424, 483))
        self.assertEqual(panel.field_group.height(), 483)
        self.assertEqual(panel.test_field_table.height(), 483)

    def test_platform_start_page_group_table_height_excludes_header(self):
        spec_id = _any_spec_id()
        if not spec_id:
            self.skipTest("SPEC_CONFIG에 시험이 없다")
        widget = MyApp(embedded=False, spec_id=spec_id)

        expected_table_height = (
            widget.group_table_widget.height() - widget.group_table_header_widget.height()
        )

        self.assertEqual(widget.group_table.height(), expected_table_height)

    def test_system_start_page_keeps_compact_scenario_panel_height(self):
        spec_id = _any_spec_id()
        if not spec_id:
            self.skipTest("SPEC_CONFIG에 시험이 없다")
        widget = SystemMyApp(embedded=False, spec_id=spec_id)

        self.assertEqual(widget.original_field_group_size, (424, 483))
        self.assertEqual(widget.field_group.height(), 483)
        self.assertEqual(widget.test_field_table.height(), 483)


if __name__ == "__main__":
    unittest.main()
