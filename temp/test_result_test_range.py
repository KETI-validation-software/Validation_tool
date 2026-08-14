"""결과 전송용 시험범위(testRange)가 항상 enum으로 나가는지 확인.

외부 설정에 "필수 필드, 필수 필드, 필수 필드" 같은 연결 문자열이 남아 있으면
그대로 서버로 전송됐고, 관리시스템이 해석하지 못해 전체 필드로 표시되던
문제에 대한 회귀 시험. (2026-08-13 request_results.json에서 실측)

실행: .venv\Scripts\python.exe temp\test_result_test_range.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.functions import normalize_result_test_range as norm


def main():
    # 정상 값
    assert norm("REQUIRED_FIELDS") == "REQUIRED_FIELDS"
    assert norm("ALL_FIELDS") == "ALL_FIELDS"
    assert norm("필수 필드") == "REQUIRED_FIELDS"
    assert norm("전체 필드") == "ALL_FIELDS"
    assert norm("필수필드") == "REQUIRED_FIELDS"
    assert norm("전체필드") == "ALL_FIELDS"

    # 실제 사고 사례: 그룹별 값이 쉼표로 연결된 문자열
    assert norm("필수 필드, 필수 필드, 필수 필드") == "REQUIRED_FIELDS"
    assert norm("REQUIRED_FIELDS, REQUIRED_FIELDS") == "REQUIRED_FIELDS"
    assert norm("전체 필드, 전체 필드") == "ALL_FIELDS"
    # 혼재 시 ALL이 우선 (하나라도 전체면 전체)
    assert norm("ALL_FIELDS, REQUIRED_FIELDS") == "ALL_FIELDS"

    # 빈 값도 enum으로
    assert norm("") == "REQUIRED_FIELDS"
    assert norm(None) == "REQUIRED_FIELDS"

    print("OK — 시험범위가 항상 enum 값으로 정리됨")


if __name__ == "__main__":
    main()
