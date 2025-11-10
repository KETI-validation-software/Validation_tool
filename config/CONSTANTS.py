# API-info
import os

headers = {"Content-type": "application/json", "User-Agent": 'test'}
none_request_message = ['Capabilities',
                        'CameraProfiles',
                        'DoorProfiles',
                        'AccessUserInfos',
                        'SensorDeviceProfiles']
# 로컬 테스트용 주소
# test-info -> (주의) auth_info의 id, pw: admin, 1234 아닐 시 digest auth 인증방식 작동하지 않음
company_name = "테스트"
product_name = "통합플랫폼시스템"
version = "v1.0"
test_category = "MAIN_TEST"
test_target = "시험테스트"
test_range = "ALL_FIELDS"
auth_type = "Digest Auth"
auth_info = "abcd,1234"
admin_code = "1234"
url = "https://192.168.0.10:2000"
contact_person = "강정민"
model_name = "v1.0"
request_id = "cmhsm9wys00x23gfr0pco2xh1"

# opt 검증 - False 이면 검증 안함, 현재는 루프문에 의해 True인 상황
flag_opt = False
if test_range == "ALL_FIELDS":
    flag_opt = True

# 선택된 시험 분야의 인덱스 (0: 영상보안, 1: 보안용센서)
selected_spec_index = 0
trace_path = os.path.join("results", "trace")
enable_retry_delay = False  # False 권장: 불필요한 sleep 제거

# test-opt
'''
✅ SPEC_CONFIG: specification.id별 설정 (통합 관리)
- 각 spec의 API별로 trans_protocol, time_out, num_retries 설정
- trans_protocol: 'basic' (일반), 'LongPolling' (실시간), 'WebHook' (웹훅, 현재 미완성)
- time_out: 메시지별 timeout 설정 시간 (ms)
- num_retries: 메시지별 검증 반복 횟수
'''

# ✅ 웹훅 서버 설정 (전역)
WEBHOOK_HOST = "0.0.0.0"  # 서버 바인딩 주소 (모든 인터페이스에서 수신)
WEBHOOK_PORT = 2001       # 웹훅 수신 포트

# ✅ 웹훅 공개 IP 설정: info_GUI에서 선택한 시험 URL의 IP 사용
# 초기값은 URL에서 추출, info_GUI에서 주소 선택 후 자동 업데이트됨
try:
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    WEBHOOK_PUBLIC_IP = parsed_url.hostname  # URL에서 호스트명(IP) 추출
except Exception as e:
    # Fallback: 자동 감지
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        WEBHOOK_PUBLIC_IP = s.getsockname()[0]
        s.close()
    except Exception as e2:
        WEBHOOK_PUBLIC_IP = "127.0.0.1"

WEBHOOK_URL = f"https://{WEBHOOK_PUBLIC_IP}:{WEBHOOK_PORT}"
# 주소 선택 후 form_validator.py에서 자동으로 업데이트됨

SPEC_CONFIG = [
    {
        "group_name": "시험테스트",
        "group_id": "cmhsm87zn00w83gfrd6ymamo9",
        "cmhs9hq0c00yy1fcqzkocftta": {
    "test_name": "vid001",
    "specs": ['cmhs9hq0c00yy1fcqzkocftta_inSchema', 'cmhs9hq0c00yy1fcqzkocftta_outData', 'cmhs9hq0c00yy1fcqzkocftta_messages'],
    "api_name": ['인증', '지원 기능 정보'],
    "api_id": ['step-1-wbttka41b', 'step-1-kzuecf17n'],
    "api_endpoint": ['/Authentication', '/Capabilities'],
    "trans_protocol": ['basic', 'basic'],
    "time_out": [60000, 60000],
    "num_retries": [10, 10]

}
    }
]

digest_security_res = [
    'ae8dd6b1b3b7ebcddccf77e1e1cee42ac3d3d90e4c2cc111c4d2aab17870e8cf',
    '16ba752619484f662586478081c99daeb3126df5988fd7956fbb302de964f958',
    'cbb6f7a008936a0cc32b34b87721eb11af1b141733dfd717627e13fb19e3c27a',
    '5196b2513bbc86a08386720240053b2a29a628aac0e1fdaf372e7f220e984538',
    '99f13e073da1f5e4e6db0d37d9f99285e4439ef57820518067ce56847613239f',
    'a723679b7b81137cb0b560428ea120fc3468ca3f2c3d2bc120a2f9a84b3a5a49'
]
