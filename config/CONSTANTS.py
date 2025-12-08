# API-info
import os

headers = {"Content-type": "application/json", "User-Agent": 'test'}

# 관리자시스템 주소 설정 로딩
def load_management_url():
    """config.txt에서 관리자시스템 주소를 읽어옴"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.txt")
    default_url = "http://ect2.iptime.org:20223"

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() == 'management_url':
                                return value.strip()
    except Exception as e:
        print(f"config.txt 읽기 실패: {e}")

    return default_url

def save_management_url(new_url):
    """관리자시스템 주소를 config.txt에 저장"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.txt")

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("# 관리자시스템 주소 설정\n")
            f.write("# 주소 변경이 필요한 경우 아래 URL만 수정하세요\n")
            f.write(f"management_url={new_url}\n")

        # 메모리상의 값도 업데이트
        global management_url
        management_url = new_url

        return True
    except Exception as e:
        print(f"config.txt 저장 실패: {e}")
        return False

# 관리자시스템 주소
management_url = load_management_url()

specs = [["cmii7shen005i8z1tagevx4qh_inSchema","cmii7shen005i8z1tagevx4qh_outData","cmii7shen005i8z1tagevx4qh_messages",""],
         ["cmii7pysb004k8z1tts0npxfm_inSchema","cmii7pysb004k8z1tts0npxfm_outData","cmii7pysb004k8z1tts0npxfm_messages",""],
         ["cmii7lxbn002s8z1t1i9uudf0_inSchema","cmii7lxbn002s8z1t1i9uudf0_outData","cmii7lxbn002s8z1t1i9uudf0_messages",""]]
none_request_message = ['Capabilities',
                        'CameraProfiles',
                        'DoorProfiles',
                        'AccessUserInfos',
                        'SensorDeviceProfiles']
# 로컬 테스트용 주소
# test-info -> (주의) auth_info의 id, pw: admin, 1234 아닐 시 digest auth 인증방식 작동하지 않음
company_name = "통합플랫폼기업"
product_name = "통합플랫폼 시스템-기본"
version = "v1.0"
test_category = "MAIN_TEST"
test_target = "기본 기능 시험-통합시스템"
test_range = "ALL_FIELDS"
auth_type = "Digest Auth"
auth_info = "kisa,kisa_k1!2@"
admin_code = "1234"
url = "https://10.252.219.95:2000"
contact_person = "김철수"
model_name = "v1.0"
request_id = "cmii86ssr00a48z1tqmco6ke8"

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
        "group_name": "기본 기능 시험-통합시스템",
        "group_id": "cmii82nib009f8z1tvo6fz8j2",
        "cmii7shen005i8z1tagevx4qh": {
    "test_name": "sensor001",
    "specs": ['cmii7shen005i8z1tagevx4qh_inSchema', 'cmii7shen005i8z1tagevx4qh_outData', 'cmii7shen005i8z1tagevx4qh_messages'],
    "api_name": ['사용자 인증'],
    "api_id": ['cmii7ubap005m8z1tyhf1yc1r'],
    "api_endpoint": ['/Authentication'],
    "trans_protocol": ['basic'],
    "time_out": [5000],
    "num_retries": [1]
},
        "cmii7pysb004k8z1tts0npxfm": {
    "test_name": "bio001",
    "specs": ['cmii7pysb004k8z1tts0npxfm_inSchema', 'cmii7pysb004k8z1tts0npxfm_outData', 'cmii7pysb004k8z1tts0npxfm_messages'],
<<<<<<< HEAD
    "api_name": ['사용자 인증', '전송 지원 기능 정보 연동', '바이오 및 출입통제 장치 목록 정보', '사용자 권한 정보 연동'],
    "api_id": ['step-1-ve056coia', 'step-2-g0s3yjcf4', 'step-3-e20vlgf8c', 'step-4-8eqsl35wj'],
    "api_endpoint": ['/Authentication', '/Capabilities', '/DoorProfiles', '/AccessUserInfos'],
    "trans_protocol": ['basic', 'basic', 'basic', 'basic'],
    "time_out": [5000, 5000, 5000, 5000],
    "num_retries": [1, 1, 1, 1]
=======
    "api_name": ['사용자 인증', '전송 지원 기능 정보 연동', '바이오 및 출입통제 장치 목록 정보'],
    "api_id": ['cmii7roh5004o8z1t47spn819', 'cmiiby4fo003chl2h8hzgu7m3', 'cmisjhwhq09hi5vy7n59tvsht'],
    "api_endpoint": ['/Authentication', '/Capabilities', '/DoorProfiles'],
    "trans_protocol": ['basic', 'basic', 'basic'],
    "time_out": [5000, 5000, 5000],
    "num_retries": [1, 1, 1]
>>>>>>> b3b1ae7770de1fcc35a61041c241e2445016518f
},
        "cmii7lxbn002s8z1t1i9uudf0": {
    "test_name": "vid001",
    "specs": ['cmii7lxbn002s8z1t1i9uudf0_inSchema', 'cmii7lxbn002s8z1t1i9uudf0_outData', 'cmii7lxbn002s8z1t1i9uudf0_messages', 'cmii7lxbn002s8z1t1i9uudf0_webhook_OutSchema', 'cmii7lxbn002s8z1t1i9uudf0_webhook_inData'],
    "api_name": ['사용자 인증', '전송 지원 기능 정보 연동', '카메라 목록 연동', '실시간 영상(CCTV) 전송', '실시간 이벤트 분석 정보 연동', '저장된 영상 목록 연동', '저장된 영상(CCTV) 전송', '저장된 이벤트 분석 정보 연동', '저장된 객체 분석 정보 연동'],
    "api_id": ['cmii7p0dp002w8z1tcikv3cji', 'cmio328yj007zie8ffqfnxwnl', 'cmiqs6rjd00khie8frmm5c83g', 'cmiqsc74800leie8fsshjqpok', 'cmiqsim3j00mwie8fumvg1qnf', 'cmiqsrgr100p7ie8fzdzjr4hn', 'cmiqsw7ou00qgie8fjt03g03i', 'cmiqt02wa00rhie8fewnh1pn3', 'cmiqt4e5z00t6ie8fxsb3tkbc'],
    "api_endpoint": ['/Authentication', '/Capabilities', '/CameraProfiles', '/StreamURLs', '/RealtimeVideoEventInfos', '/StoredVideoInfos', '/ReplayURL', '/StoredVideoEventInfos', '/StoredObjectAnalyticsInfos'],
    "trans_protocol": ['basic', 'basic', 'basic', 'basic', 'WebHook', 'basic', 'basic', 'basic', 'basic'],
    "time_out": [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
    "num_retries": [1, 1, 1, 1, 1, 1, 1, 1, 1]
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