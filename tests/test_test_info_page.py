import unittest

from PyQt5.QtWidgets import QApplication, QVBoxLayout

from ui.pages.test_info_page import (
    _get_header_title_display_size,
    _get_header_title_top_offset,
    _resolve_header_title_path,
    _setup_header,
)


class DummyParent:
    def __init__(self, target_system):
        self.target_system = target_system


class TestTestInfoPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_page1_header_title_is_fixed_when_target_is_platform(self):
        parent = DummyParent("통합시스템")

        self.assertEqual(
            _resolve_header_title_path(parent),
            "assets/image/test_info/header_title.png",
        )

    def test_page1_header_title_is_fixed_when_target_is_system(self):
        parent = DummyParent("단일시스템")

        self.assertEqual(
            _resolve_header_title_path(parent),
            "assets/image/test_info/header_title.png",
        )

    def test_page1_header_title_uses_actual_image_size(self):
        parent = DummyParent("통합시스템")

        self.assertEqual(_get_header_title_display_size(parent).width(), 267)
        self.assertEqual(_get_header_title_display_size(parent).height(), 23)

    def test_page1_header_title_has_three_pixel_top_offset_without_wrapper(self):
        parent = DummyParent("통합시스템")
        layout = QVBoxLayout()

        _setup_header(parent, layout)

        margins = parent.page1_header_title_label.contentsMargins()
        self.assertEqual(margins.top(), 3)
        self.assertEqual(parent.page1_header_title_label.height(), 23 + _get_header_title_top_offset())

if __name__ == "__main__":
    unittest.main()
