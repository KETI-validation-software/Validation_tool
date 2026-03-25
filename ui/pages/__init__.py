"""
페이지 모듈
- test_info_page: 시험 정보 확인 페이지 (Page 1)
- test_config_page: 시험 설정 페이지 (Page 2)
"""
from .test_info_page import create_test_info_page, format_test_group_summary, update_test_info_header_title
from .test_config_page import create_test_config_page, update_test_config_header_title

__all__ = [
    'create_test_info_page',
    'create_test_config_page',
    'format_test_group_summary',
    'update_test_info_header_title',
    'update_test_config_header_title'
]
