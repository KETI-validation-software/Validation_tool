"""
API 클라이언트 모듈
- 서버와의 HTTP 통신을 담당
- 시험 정보, 스펙, 테스트 스텝 등의 API 호출
"""

import requests
import socket
import config.CONSTANTS as CONSTANTS
from core.logger import Logger


class APIClient:
    """API 통신을 담당하는 클라이언트 클래스"""

    def __init__(self):
        self.timeout = 10

    @property
    def base_url(self):
        """관리자시스템 주소 (실시간 반영)"""
        return CONSTANTS.management_url

    def fetch_test_info_by_ip(self, ip_address):
        """IP 주소로 시험 정보 조회"""
        url = f"{self.base_url}/api/integration/test-requests/by-ip?ipAddress={ip_address}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("success") and json_data.get("data"):
                Logger.info(f"API 호출 성공: {len(json_data['data'])}개 시험 정보 조회됨")
                return json_data["data"][0]
            else:
                raise ValueError("API 응답에 데이터가 없습니다.")
        except requests.exceptions.Timeout:
            Logger.error(f"API 호출 타임아웃: 서버 응답 시간 초과")
            return None
        except requests.exceptions.ConnectionError:
            Logger.error(f"API 호출 실패: 서버 연결 불가")
            return None
        except Exception as e:
            Logger.error(f"API 호출 실패: {e}")
            import traceback
            Logger.error(traceback.format_exc())
            return None

    def fetch_specification_by_id(self, spec_id):
        """spec_id로 specification 상세 정보 조회 (API 기반)"""
        url = f"{self.base_url}/api/integration/specifications/{spec_id}"
        try:
            Logger.debug(f"Specification API 호출 중: {spec_id}")
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()
            Logger.info(f"Specification 조회 성공: {json_data.get('specification', {}).get('name', '')}")
            return json_data
        except requests.exceptions.Timeout:
            Logger.error(f"Specification API 타임아웃: {spec_id}")
            return None
        except requests.exceptions.ConnectionError:
            Logger.error(f"Specification API 연결 실패: {spec_id}")
            return None
        except Exception as e:
            Logger.error(f"Specification 조회 실패 ({spec_id}): {e}")
            return None

    def fetch_test_step_by_id(self, step_id):
        """step_id로 test-step 상세 정보 조회 (API 기반)"""
        url = f"{self.base_url}/api/integration/test-steps/{step_id}"
        try:
            Logger.debug(f"Test-Step API 호출 중: {step_id}")
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # 응답 구조에 따라 이름 키가 다를 수 있어 안전하게 접근
            name = (
                    data.get("step", {}).get("name")
                    or data.get("name")
                    or ""
            )
            Logger.info(f"Test-Step 조회 성공: id={step_id}, name={name}")
            return data
        except requests.exceptions.Timeout:
            Logger.error(f"Test-Step API 타임아웃: {step_id}")
            return None
        except requests.exceptions.ConnectionError:
            Logger.error(f"Test-Step API 연결 실패: {step_id}")
            return None
        except Exception as e:
            Logger.error(f"Test-Step 조회 실패 ({step_id}): {e}")
            return None

    def fetch_response_codes(self):
        """API에서 response-codes 가져오기"""
        url = f"{self.base_url}/api/integration/response-codes"
        try:
            Logger.debug(f"ResponseCode API 호출 중: {url}")
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("success") and json_data.get("data"):
                return json_data["data"]
            else:
                Logger.warning("ResponseCode API 응답에 데이터가 없습니다.")
                return None
        except requests.exceptions.Timeout:
            Logger.error("ResponseCode API 타임아웃")
            return None
        except Exception as e:
            Logger.error(f"ResponseCode API 호출 실패: {e}")
            return None

    def fetch_admin_code(self, base_url=None):
        """
        API에서 관리자 코드 가져오기
        Args:
            base_url (str, optional): 요청할 기본 URL. None이면 self.base_url 사용.
        """
        target_url = base_url if base_url else self.base_url
        # URL 끝에 슬래시가 있다면 제거
        target_url = target_url.rstrip('/')
        
        url = f"{target_url}/api/integration/admin-code"
        try:
            Logger.debug(f"Admin Code API 호출 중: {url}")
            # 검증 단계이므로 짧은 타임아웃 설정
            response = requests.get(url, timeout=5, verify=False)
            response.raise_for_status()
            json_data = response.json()
            Logger.info(f"Admin Code API 전체 응답: {json_data}")

            # 응답 구조 대응: "adminCode" 또는 "data" 안의 "adminCode" 또는 "data" 안의 "code"
            if "adminCode" in json_data:
                return json_data["adminCode"]
            elif json_data.get("data"):
                data_obj = json_data["data"]
                if isinstance(data_obj, dict):
                    if "adminCode" in data_obj:
                        return data_obj["adminCode"]
                    elif "code" in data_obj:
                        return data_obj["code"]
                
                Logger.warning("Admin Code API 응답의 data 객체 안에 adminCode나 code가 없습니다.")
                return None
            else:
                Logger.warning("Admin Code API 응답에 adminCode나 data 필드가 없습니다.")
                return None
        except requests.exceptions.Timeout:
            Logger.error("Admin Code API 타임아웃")
            return None
        except Exception as e:
            Logger.error(f"Admin Code API 호출 실패: {e}")
            return None

    def get_local_ip_address(self):
        """현재 PC의 로컬 IP 주소를 가져옴"""
        try:
            # 외부에 연결을 시도하여 로컬 IP 확인 (실제 연결하지 않음)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            Logger.warning(f"[WARNING] IP 주소 가져오기 실패: {e}")
            return "127.0.0.1"

    def send_heartbeat_idle(self):
        """시험 정보 불러오기 시 idle 상태 전송"""
        url = f"{self.base_url}/api/heartbeat"
        try:
            ip_address = self.get_local_ip_address()
            payload = {
                "ipAddress": ip_address,
                "status": "idle"
            }
            response = requests.post(url, json=payload, timeout=self.timeout)
            Logger.info(f"[INFO] Heartbeat (idle) 응답 코드: {response.status_code}")
            response.raise_for_status()
            Logger.info(f"[INFO] Heartbeat (idle) 전송 성공: {payload}")
            return True
        except Exception as e:
            Logger.warning(f"[WARNING] Heartbeat (idle) 전송 실패: {e}")
            return False

    def send_heartbeat_busy(self, test_info):
        """시험 시작 시 busy 상태 + 시험 정보 전송"""
        url = f"{self.base_url}/api/heartbeat"
        try:
            ip_address = self.get_local_ip_address()
            payload = {
                "ipAddress": ip_address,
                "status": "busy",
                "testInfo": test_info
            }
            response = requests.post(url, json=payload, timeout=self.timeout)
            Logger.info(f"[INFO] Heartbeat (busy) 응답 코드: {response.status_code}")
            response.raise_for_status()
            Logger.info(f"[INFO] Heartbeat (busy) 전송 성공: ipAddress={ip_address}")
            return True
        except Exception as e:
            Logger.warning(f"[WARNING] Heartbeat (busy) 전송 실패: {e}")
            return False
