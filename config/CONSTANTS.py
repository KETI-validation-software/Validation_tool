# API-info
import os
import sys

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

specs = [["cmii7v8pr006g8z1tvo55a50u_outSchema","cmii7v8pr006g8z1tvo55a50u_inData","cmii7v8pr006g8z1tvo55a50u_messages",""]]
none_request_message = ['Capabilities',
                        'CameraProfiles',
                        'DoorProfiles',
                        'AccessUserInfos',
                        'SensorDeviceProfiles']
# 로컬 테스트용 주소
# test-info -> (주의) auth_info의 id, pw: admin, 1234 아닐 시 digest auth 인증방식 작동하지 않음
company_name = "물리보안기업"
product_name = "물리보안시스템-기본"
version = "v1.0"
test_category = "MAIN_TEST"
test_target = "기본 기능 시험-영상보안시스템"
test_range = "ALL_FIELDS"
auth_type = "Digest Auth"
auth_info = "kisa,kisa_k1!2@"
admin_code = "1234"
url = "https://192.168.0.3:2000"
contact_person = "김철수"
model_name = "v1.0"
request_id = "cmii85wjq009z8z1tv0d3d7r1"

# opt 검증 - False 이면 검증 안함, 현재는 루프문에 의해 True인 상황
flag_opt = False
if test_range == "ALL_FIELDS":
    flag_opt = True

# 선택된 시험 분야의 인덱스 (0: 영상보안, 1: 보안용센서)
selected_spec_index = 0
# ===== 기본 경로 설정 =====
if getattr(sys, 'frozen', False):
    # PyInstaller 실행파일
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 일반 Python 실행 (config 폴더 기준)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ===== 결과 디렉토리 설정 =====
result_dir = os.path.join(BASE_DIR, "results")
trace_path = os.path.join(result_dir, "trace")

# 디렉토리 생성
os.makedirs(result_dir, exist_ok=True)
os.makedirs(trace_path, exist_ok=True)

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
WEBHOOK_PUBLIC_IP = "192.168.0.3"
# ✅ 웹훅 공개 IP 설정: info_GUI에서 선택한 시험 URL의 IP 사용
# 초기값은 URL에서 추출, info_GUI에서 주소 선택 후 자동 업데이트됨

WEBHOOK_URL = f"https://{WEBHOOK_PUBLIC_IP}:{WEBHOOK_PORT}"
# 주소 선택 후 form_validator.py에서 자동으로 업데이트됨

SPEC_CONFIG = [
    {
        "group_name": "기본 기능 시험-영상보안시스템",
        "group_id": "cmjcefmh8070gcfb35wjptcsl",
        "cmii7v8pr006g8z1tvo55a50u": {
    "test_name": "vid001",
    "specs": ['cmii7v8pr006g8z1tvo55a50u_outSchema', 'cmii7v8pr006g8z1tvo55a50u_inData', 'cmii7v8pr006g8z1tvo55a50u_messages', 'cmii7v8pr006g8z1tvo55a50u_webhook_inSchema', 'cmii7v8pr006g8z1tvo55a50u_webhook_outData'],
    "api_name": ['사용자 인증', '전송 지원 기능 정보 연동', '카메라 목록 연동', '실시간 영상(CCTV) 전송 ', '실시간 이벤트 분석 정보 연동', '저장된 영상 목록 연동', '저장된 영상(CCTV) 전송', '저장된 이벤트 분석 정보 연동', '저장된 객체 분석 정보 연동'],
    "api_id": ['cmii7ylxn006m8z1tqq8dard1', 'cmiqtf9x600upie8ft45b1h1w', 'cmiqthu4900voie8f1evs0kfm', 'cmiqtkefj00whie8fd8odtc1m', 'cmiqtnwm200xoie8fxzfhodj5', 'cmiwrkvjq0005nkgl04g93wwy', 'cmiwrq4r200kqnkgluspxeyu7', 'cmiws2qij05apnkgli7hun3bl', 'cmiws9btu01ksp0028h4uc4az'],
    "api_endpoint": ['/Authentication', '/Capabilities', '/CameraProfiles', '/StreamURLs', '/RealtimeVideoEventInfos', '/StoredVideoInfos', '/ReplayURL', '/StoredVideoEventInfos', '/StoredObjectAnalyticsInfos'],
    "trans_protocol": ['basic', 'basic', 'basic', 'basic', 'WebHook', 'basic', 'basic', 'basic', 'basic'],
    "time_out": [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000],
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