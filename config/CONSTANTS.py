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
company_name = "물리보안기업"
product_name = "물리보안테스트제품"
version = "v1.0"
test_category = "MAIN_TEST"
test_target = "물리보안"
test_range = "ALL_FIELDS"
auth_type = "Bearer Token"
auth_info = "a"
admin_code = "1234"
url = "https://10.252.219.95:8080"
contact_person = "김철수"
model_name = "v1.0"
request_id = "cmh2sdyj70001ry7uvsgugy25"
specs = [
    ["cmgvieyak001b6cd04cgaawmm_inSchema", "cmgvieyak001b6cd04cgaawmm_outData", "cmgvieyak001b6cd04cgaawmm_messages",
     ""],
    ["cmh1u5pef000sgxc3bzl4y9v0_inSchema", "cmh1u5pef000sgxc3bzl4y9v0_outData", "cmh1u5pef000sgxc3bzl4y9v0_messages",
     ""]]

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
WEBHOOK_PORT = 8090       # 웹훅 수신 포트

# ✅ 웹훅 공개 IP는 현재 PC의 실제 IP 자동 감지 (socket 사용)
# 플랫폼/시스템이 웹훅 이벤트를 보낼 주소 = 이 PC의 IP:8090
try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # 구글 DNS로 연결 시도 (실제 전송 안 함)
    WEBHOOK_PUBLIC_IP = s.getsockname()[0]  # 현재 PC의 실제 네트워크 IP
    s.close()
    print(f"[CONSTANTS] 웹훅 서버 IP 자동 감지: {WEBHOOK_PUBLIC_IP}")
except Exception as e:
    # 최후의 수단: localhost (네트워크 연결 없는 경우)
    print(f"[CONSTANTS] IP 자동 감지 실패 ({e}), localhost 사용")
    WEBHOOK_PUBLIC_IP = "127.0.0.1"

WEBHOOK_URL = f"https://{WEBHOOK_PUBLIC_IP}:{WEBHOOK_PORT}"  # 플랫폼/시스템이 웹훅을 보낼 주소
print(f"[CONSTANTS] 웹훅 콜백 URL: {WEBHOOK_URL} (플랫폼/시스템 접속 URL: {url})")

SPEC_CONFIG = [
    {
        "group_name": "물리보안",
        "group_id": "cmgzwohuq01y8vsvep0hpuuf4",
        "cmgyv3rzl014nvsveidu5jpzp": {
    "test_name": "영상보안시스템_new",
    "specs": ['cmgyv3rzl014nvsveidu5jpzp_outSchema', 'cmgyv3rzl014nvsveidu5jpzp_inData', 'cmgyv3rzl014nvsveidu5jpzp_messages', 'cmgyv3rzl014nvsveidu5jpzp_webhook_inSchema', 'cmgyv3rzl014nvsveidu5jpzp_webhook_outData'],
    "api_name": ['인증', '전송 지원 기능 정보 연동', '카메라 목록 연동', '저장된 영상 목록 연동', '실시간 영상 정보 연동', '저장된 영상 정보 연동', '실시간 이벤트 분석 정보 연동', '저장된 이벤트 분석 정보 연동'],
    "api_id": ['step-1-s9942zltt', 'step-1-vps6mosa3', 'step-3-dpd47yeve', 'step-4-nbpd1rfle', 'step-5-6juqjc7zt', 'step-6-2hxrdvfry', 'step-7-jgj9l9vf4', 'step-8-57zrt6i4l'],
    "api_endpoint": ['/Authentication', '/Capabilities', '/CameraProfiles', '/StoredVideoInfos', '/StreamURLs', '/ReplayURL', '/RealtimeVideoEventInfos', '/StoredVideoEventInfos'],
    "trans_protocol": ['basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'WebHook', 'basic'],
    "time_out": [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
    "num_retries": [1, 1, 1, 1, 1, 1, 1, 1]
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
