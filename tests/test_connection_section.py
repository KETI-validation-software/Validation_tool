import unittest

from PyQt5.QtWidgets import QApplication

from ui.sections.connection_section import ConnectionSection


class TestConnectionSection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_hides_number_column_in_url_table(self):
        section = ConnectionSection()

        self.assertTrue(section.url_table.isColumnHidden(0))
        self.assertEqual(section.url_header_empty_label.width(), 0)
        self.assertEqual(section.url_header_url_label.width(), 744)


if __name__ == "__main__":
    unittest.main()
