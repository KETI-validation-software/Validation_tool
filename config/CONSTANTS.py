# API-info
import os
import sys
import socket

headers = {"Content-type": "application/json", "User-Agent": 'test'}

# 오류 응답(201/400) 유도 시험: 요청값을 변조해 상대의 오류 처리를 검사한다.
# 정상 연동만 확인할 때는 False로 변경한다.
ENABLE_ERROR_REQUEST_MUTATION = True

# 웹훅 이벤트 맥락 검증: 관리도구의 웹훅 검증 규칙(doorID가 구독한 문인지,
# doorSensor가 제어 명령대로 바뀌었는지 등)을 실제로 적용한다.
# 문제가 생기면 False로 바꿔 즉시 이전 동작(규격 검증만)으로 되돌릴 수 있다.
# exe 옆 외부 config/CONSTANTS.py에서 바꾸면 재빌드 없이 적용된다.
ENABLE_WEBHOOK_CONTEXT_VALIDATION = True

# 장치 역할일 때 받은 요청의 오류를 판정해 오류 코드로 응답한다(400/201/404).
# 상대의 유도(ENABLE_ERROR_REQUEST_MUTATION)와 짝이 되는 기능으로, 실제 시험에서는
# 피시험 업체 시스템이 이 역할을 하므로 주로 도구 대 도구 리허설에서 쓴다.
# 오탐이 나면 False로 바꿔 즉시 이전 동작(항상 200 응답)으로 되돌릴 수 있다.
ENABLE_ERROR_RESPONSE_CHECK = True

# 버전4: 모든 로컬 IP 주소 감지 (이더넷, 와이파이 등 모든 네트워크 어댑터)
def get_all_local_ips():
    """로컬 PC의 모든 IP 주소를 리스트로 반환 (이더넷, 와이파이 등)"""
    ip_list = []

    try:
        # 방법 1: 모든 네트워크 인터페이스의 IP 가져오기
        hostname = socket.gethostname()
        # getaddrinfo로 모든 IP 조회
        addrs = socket.getaddrinfo(hostname, None, socket.AF_INET)
        for addr in addrs:
            ip = addr[4][0]
            if ip and not ip.startswith('127.') and ip not in ip_list:
                ip_list.append(ip)
    except Exception:
        pass

    try:
        # 방법 2: 기본 라우팅 IP 추가 (이미 있으면 스킵)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 80))
        default_ip = s.getsockname()[0]
        s.close()
        if default_ip and not default_ip.startswith('127.') and default_ip not in ip_list:
            ip_list.append(default_ip)
    except Exception:
        pass

    try:
        from core.logger import Logger
        Logger.debug(f"버전4: 감지된 모든 로컬 IP - {ip_list}")
    except ImportError:
        pass

    return ip_list if ip_list else []

# config.txt 경로 헬퍼 함수
def get_config_path():
    """실행파일 또는 소스코드 기준으로 config.txt 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 실행파일 → exe 파일 위치 기준
        base_dir = os.path.dirname(sys.executable)
    else:
        # 일반 Python 실행 → 소스코드 위치 기준
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "config.txt")

# 관리자시스템 주소 설정 로딩
def load_management_url():
    """config.txt에서 관리자시스템 주소를 읽어옴"""
    config_path = get_config_path()
    default_url = "http://localhost"  # 기본값 (config.txt 없거나 읽기 실패 시)

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
        try:
            from core.logger import Logger
            Logger.error(f"config.txt 읽기 실패: {e}")
        except ImportError:
            print(f"config.txt 읽기 실패: {e}")

    return default_url

def save_management_url(new_url):
    """관리자시스템 주소를 config.txt에 저장"""
    config_path = get_config_path()

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
        try:
            from core.logger import Logger
            Logger.error(f"config.txt 저장 실패: {e}")
        except ImportError:
            print(f"config.txt 저장 실패: {e}")
        return False

# 관리자시스템 주소
management_url = load_management_url()

none_request_message = ['Capabilities',
                        'CameraProfiles',
                        'DoorProfiles',
                        'AccessUserInfos',
                        'SensorDeviceProfiles']
# 로컬 테스트용 주소
# test-info -> (주의) auth_info의 id, pw: admin, 1234 아닐 시 digest auth 인증방식 작동하지 않음
company_name = "필테 - 통합"
product_name = "필테 - 통합"
version = "필테 - 통합"
test_category = "본시험"
test_target = "[필수] 통합 테스트"
test_range = "필수 필드"
auth_type = "Digest Auth"
auth_info = "kisa,kisa_k1!2@"
admin_code = "123456"
url = "https://192.168.1.30:8080"
contact_person = "필테 - 통합"
model_name = "필테 - 통합"
request_id = "cmszckit9011xilyrbf55edkr"

# opt 검증 - False 이면 검증 안함, 현재는 루프문에 의해 True인 상황
flag_opt = False
if test_range == "전체 필드":
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

# ===== 디버그 레벨 설정 =====
'''
디버그 레벨 설정 (콘솔 출력 제어)
- 0 (ERROR): 에러만 출력 (최소)
- 1 (WARN): 에러 + 중요 정보 (API 요청/응답 요약) [권장]
- 2 (INFO): 1 + 검증 과정, 매핑 정보
- 3 (DEBUG): 모든 디버그 정보 출력 (상세)
'''
DEBUG_LEVEL = 3 # 기본값: WARN (권장)

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
WEBHOOK_PORT = 8081
WEBHOOK_WINDOW_SEC = 10.0  # ✅ 웹훅 창/대기시간(초) — 시스템 수신·플랫폼 송신·플랫폼 join 공통 (단일 소스, 함께 변경됨)
WEBHOOK_PUBLIC_IP = "192.168.1.30"
# ✅ 웹훅 공개 IP 설정: info_GUI에서 선택한 시험 URL의 IP 사용
# 초기값은 URL에서 추출, info_GUI에서 주소 선택 후 자동 업데이트됨

WEBHOOK_URL = "https://192.168.1.30:8081"
# 주소 선택 후 form_validator.py에서 자동으로 업데이트됨

# ✅ 웹훅 외부 접근 주소 (플랫폼에 전송할 주소 - ngrok 등) (01/08 임시로 추가)
WEBHOOK_DISPLAY_URL = "https://webhook2026.ngrok.dev"
# 시스템이 플랫폼에 transProtocolDesc로 전송할 주소
# 각 시스템마다 다른 ngrok 주소를 사용하려면 이 값을 변경

SPEC_CONFIG = [
    {
        "group_name": "[필수] 통합 테스트",
        "group_id": "cmszcjoz4011oilyre63lt0vw",
        "cmsy90xd705aarc0quh4je1k0": {
    "test_name": "req_vid001",
    "specs": ['cmsy90xd705aarc0quh4je1k0_inSchema', 'cmsy90xd705aarc0quh4je1k0_outData', 'cmsy90xd705aarc0quh4je1k0_messages', 'cmsy90xd705aarc0quh4je1k0_webhook_OutSchema', 'cmsy90xd705aarc0quh4je1k0_webhook_inData'],
    "api_name": ['사용자 인증', '전송 지원 기능 정보 연동', '카메라 목록 연동', '실시간 영상(CCTV) 전송 ', '실시간 이벤트 분석 정보 연동'],
    "api_id": ['cmsy91ipk05agrc0qm4x2cf08', 'cmsy93mqm05birc0q5k2fpbqu', 'cmsy99ujz05chrc0qw4kx4kn5', 'cmsyafs4605dprc0qqh72ak77', 'cmsyau2qn05f3rc0qjkcsrloa'],
    "api_endpoint": ['/Authentication', '/Capabilities', '/CameraProfiles', '/StreamURLs', '/RealtimeVideoEventInfos'],
    "trans_protocol": ['basic', 'basic', 'basic', 'basic', 'WebHook'],
    "time_out": [60000, 60000, 60000, 60000, 60000],
    "num_retries": [1, 1, 1, 1, 1]
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
