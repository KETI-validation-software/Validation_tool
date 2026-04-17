import unittest
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from platformVal_all import MyApp
from systemVal_all import MyApp as SystemMyApp
from ui.ui_components import TestSelectionPanel


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
        widget = MyApp(embedded=False, spec_id="cmii7shen005i8z1tagevx4qh")

        expected_table_height = (
            widget.group_table_widget.height() - widget.group_table_header_widget.height()
        )

        self.assertEqual(widget.group_table.height(), expected_table_height)

    def test_system_start_page_keeps_compact_scenario_panel_height(self):
        widget = SystemMyApp(embedded=False, spec_id="cmii7shen005i8z1tagevx4qh")

        self.assertEqual(widget.original_field_group_size, (424, 483))
        self.assertEqual(widget.field_group.height(), 483)
        self.assertEqual(widget.test_field_table.height(), 483)


if __name__ == "__main__":
    unittest.main()
