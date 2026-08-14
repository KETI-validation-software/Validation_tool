"""오류 유도용 요청 변조가 필드의 원본 타입을 유지하는지 확인.

17자리 시각 필드가 Number→String으로 전환된 뒤에도 replace_start_time이
숫자 0을 넣어서, 201 유도가 아니라 규격(타입) 검증에서 먼저 탈락하던
문제에 대한 회귀 시험. (2026-08-14 sensor002 StoredSensorEventInfos에서 실측)

실행: .venv\Scripts\python.exe temp\test_error_mutation.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator


def main():
    gen = ConstraintDataGenerator()

    # String 스펙: "0" 문자열로 변조 (형식은 유효, 내용만 무효 → 201 유도 성립)
    out = gen.replace_start_time({
        "timePeriod": {"startTime": "20251105163010124", "endTime": "20251115163010124"},
    })
    assert out["timePeriod"]["startTime"] == "0", out
    assert out["timePeriod"]["endTime"] == "20251115163010124", out

    # Number 스펙(미전환): 기존처럼 숫자 0
    out = gen.replace_start_time({
        "timePeriod": {"startTime": 20251105163010124, "endTime": 20251115163010124},
    })
    assert out["timePeriod"]["startTime"] == 0, out

    # 중첩 목록 안의 startTime도 동일하게 (ReplayURL 등 camList[].startTime 구조)
    out = gen.replace_start_time({
        "camList": [{"camID": "cam0001", "startTime": "20251105163010124"}],
    })
    assert out["camList"][0]["startTime"] == "0", out

    # 원본은 건드리지 않는다 (deepcopy)
    src = {"timePeriod": {"startTime": "20251105163010124"}}
    gen.replace_start_time(src)
    assert src["timePeriod"]["startTime"] == "20251105163010124", src

    print("OK — 변조가 원본 타입을 유지함 (String→\"0\", Number→0)")


if __name__ == "__main__":
    main()
