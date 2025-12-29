"""
오류 메시지 트리 포매팅 테스트
"""

from .functions import format_errors_as_tree

# 테스트 케이스 1: 사용자가 제공한 실제 오류 메시지
test_errors_1 = [
    "[구조] 타입 불일치: doorList.bioDeviceList - 예상: 모든 요소가 list, 실패한 항목들: [0] {'bioDeviceID': 'bio0001', 'bioDeviceName': '출입문홍채인식기기', 'bioDeviceAuthTypeList': ['홍채', '지문']} (타입: dict), [1] {'bioDeviceID': 'bio0002', 'bioDeviceName': '출입문지문인식기기', 'bioDeviceAuthTypeList': ['지문']} (타입: dict)",
    "[구조] 필수 필드 누락: doorList.bioDeviceList.bioDeviceAuthTypeList[]",
    "[구조] 타입 불일치: doorList.otherDeviceList - 예상: 모든 요소가 list, 실패한 항목들: [0] {'otherDeviceID': 'other0001', 'otherDeviceName': '출입문카드인식기기', 'otherDeviceAuthTypeList': ['카드']} (타입: dict)",
    "[구조] 타입 불일치: doorList.otherDeviceList.otherDeviceAuthTypeList - 예상: 모든 요소가 list, 실패한 항목들: [0] 카드 (타입: str)",
    "[구조] 필수 필드 누락: doorList.otherDeviceList.otherDeviceAuthTypeList[]"
]

print("=" * 80)
print("테스트 케이스 1: 실제 오류 메시지")
print("=" * 80)
print("\n[원본 오류 메시지]")
for err in test_errors_1:
    print(f"  - {err}")

print("\n\n[트리 구조 포매팅 결과]")
result_1 = format_errors_as_tree(test_errors_1)
print(result_1)

# 테스트 케이스 2: 다양한 오류 타입
test_errors_2 = [
    "[구조] 타입 불일치: user.name (예상: str, 실제: int)",
    "[구조] 필수 필드 누락: user.email",
    "[의미] 범위 검증 실패: user.age는 0-150 범위여야 함"
]

print("\n\n" + "=" * 80)
print("테스트 케이스 2: 다양한 오류 타입")
print("=" * 80)
print("\n[원본 오류 메시지]")
for err in test_errors_2:
    print(f"  - {err}")

print("\n\n[트리 구조 포매팅 결과]")
result_2 = format_errors_as_tree(test_errors_2)
print(result_2)

# 테스트 케이스 3: 빈 오류
print("\n\n" + "=" * 80)
print("테스트 케이스 3: 오류 없음")
print("=" * 80)
result_3 = format_errors_as_tree([])
print(result_3)
