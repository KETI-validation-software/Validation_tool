import unittest

from PyQt5.QtWidgets import QApplication, QVBoxLayout

from ui.pages.test_config_page import (
    _get_header_title_top_offset,
    _resolve_header_title_path,
    _setup_header,
)


class DummyParent:
    def __init__(self, target_system):
        self.target_system = target_system


class TestTestConfigPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_page2_header_title_path_for_platform(self):
        parent = DummyParent("통합시스템")

        self.assertEqual(
            _resolve_header_title_path(parent),
            "assets/image/test_config/platform_config_title.png",
        )

    def test_page2_header_title_path_for_system(self):
        parent = DummyParent("단일시스템")

        self.assertEqual(
            _resolve_header_title_path(parent),
            "assets/image/test_config/system_config_title.png",
        )

    def test_page2_header_title_uses_platform_image_size(self):
        parent = DummyParent("통합시스템")
        layout = QVBoxLayout()

        _setup_header(parent, layout)

        self.assertEqual(parent.page2_header_title_label.pixmap().width(), 481)
        self.assertEqual(parent.page2_header_title_label.pixmap().height(), 36)

    def test_page2_header_title_uses_system_image_size(self):
        parent = DummyParent("단일시스템")
        layout = QVBoxLayout()

        _setup_header(parent, layout)

        self.assertEqual(parent.page2_header_title_label.pixmap().width(), 481)
        self.assertEqual(parent.page2_header_title_label.pixmap().height(), 36)

    def test_page2_header_title_has_negative_one_pixel_top_offset(self):
        parent = DummyParent("통합시스템")
        layout = QVBoxLayout()

        _setup_header(parent, layout)

        margins = parent.page2_header_title_label.contentsMargins()
        self.assertEqual(margins.top(), 0)
        self.assertEqual(margins.bottom(), 2)
        self.assertEqual(parent.page2_header_title_label.height(), 36 + (_get_header_title_top_offset() * 2))


if __name__ == "__main__":
    unittest.main()
