import unittest

from PyQt5.QtWidgets import QApplication

from ui.common_main_ui import CommonMainUI, get_header_title_display_size


class TestCommonMainUiHeader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_runner_header_path_for_platform(self):
        widget = CommonMainUI.__new__(CommonMainUI)
        widget.validation_mode = "platform"

        self.assertEqual(
            widget.get_header_title_path("runner"),
            "assets/image/test_runner/platform_runner_title.png",
        )

    def test_runner_header_path_for_system(self):
        widget = CommonMainUI.__new__(CommonMainUI)
        widget.validation_mode = "system"

        self.assertEqual(
            widget.get_header_title_path("runner"),
            "assets/image/test_runner/system_runner_title.png",
        )

    def test_runner_header_uses_original_image_size(self):
        widget = CommonMainUI.__new__(CommonMainUI)
        widget.validation_mode = "platform"

        self.assertEqual(get_header_title_display_size(widget, "runner").width(), 430)
        self.assertEqual(get_header_title_display_size(widget, "runner").height(), 36)


if __name__ == "__main__":
    unittest.main()
