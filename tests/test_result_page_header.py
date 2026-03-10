import unittest

from PyQt5.QtWidgets import QApplication

from ui.result_page import ResultPageWidget, get_result_header_title_display_size


class DummyParent:
    def __init__(self, validation_mode):
        self.validation_mode = validation_mode


class TestResultPageHeader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_result_header_path_for_platform(self):
        widget = ResultPageWidget.__new__(ResultPageWidget)
        widget.parent = DummyParent("platform")

        self.assertEqual(
            widget._get_result_header_title_path(),
            "assets/image/test_runner/platform_result_title.png",
        )

    def test_result_header_path_for_system(self):
        widget = ResultPageWidget.__new__(ResultPageWidget)
        widget.parent = DummyParent("system")

        self.assertEqual(
            widget._get_result_header_title_path(),
            "assets/image/test_runner/system_result_title.png",
        )

    def test_result_header_uses_original_image_size(self):
        widget = ResultPageWidget.__new__(ResultPageWidget)
        widget.parent = DummyParent("platform")

        self.assertEqual(get_result_header_title_display_size(widget).width(), 430)
        self.assertEqual(get_result_header_title_display_size(widget).height(), 36)


if __name__ == "__main__":
    unittest.main()
