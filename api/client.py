"""
API 클라이언트 모듈
- 서버와의 HTTP 통신을 담당
- 시험 정보, 스펙, 테스트 스텝 등의 API 호출
"""

import requests
import socket
import os
import config.CONSTANTS as CONSTANTS


class APIClient:
    """API 통신을 담당하는 클라이언트 클래스"""

    def __init__(self):
        self.base_url = CONSTANTS.management_url
        self.timeout = 10

    def fetch_test_info_by_ip(self, ip_address):
        """IP 주소로 시험 정보 조회"""
        url = f"{self.base_url}/api/integration/test-requests/by-ip?ipAddress={ip_address}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("success") and json_data.get("data"):
                print(f"API 호출 성공: {len(json_data['data'])}개 시험 정보 조회됨")
                return json_data["data"][0]
            else:
                raise ValueError("API 응답에 데이터가 없습니다.")
        except requests.exceptions.Timeout:
            print(f"API 호출 타임아웃: 서버 응답 시간 초과")
            return None
        except requests.exceptions.ConnectionError:
            print(f"API 호출 실패: 서버 연결 불가")
            return None
        except Exception as e:
            print(f"API 호출 실패: {e}")
            import traceback
            traceback.print_exc()
            return None

    def fetch_opt_by_spec_id(self, spec_id):
        """spec_id로 OPT 파일 조회 (API 기반)"""
        # TODO: spec_id를 서버에 전송하여 OPT JSON 받아오는 API 구현 필요
        # 현재는 임시로 로컬 파일 조회
        opt_file_path = f"opt_files/{spec_id}.json"

        if os.path.exists(opt_file_path):
            print(f"spec_id {spec_id}에 해당하는 OPT 파일 발견: {opt_file_path}")
            return opt_file_path
        else:
            print(f"spec_id {spec_id}에 해당하는 OPT 파일이 없습니다.")
            return None

    def fetch_specification_by_id(self, spec_id):
        """spec_id로 specification 상세 정보 조회 (API 기반)"""
        url = f"{self.base_url}/api/integration/specifications/{spec_id}"
        try:
            print(f"Specification API 호출 중: {spec_id}")
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()
            print(f"Specification 조회 성공: {json_data.get('specification', {}).get('name', '')}")
            return json_data
        except requests.exceptions.Timeout:
            print(f"Specification API 타임아웃: {spec_id}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Specification API 연결 실패: {spec_id}")
            return None
        except Exception as e:
            print(f"Specification 조회 실패 ({spec_id}): {e}")
            return None

    def fetch_test_step_by_id(self, step_id):
        """step_id로 test-step 상세 정보 조회 (API 기반)"""
        url = f"{self.base_url}/api/integration/test-steps/{step_id}"
        try:
            print(f"Test-Step API 호출 중: {step_id}")
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # 응답 구조에 따라 이름 키가 다를 수 있어 안전하게 접근
            name = (
                    data.get("step", {}).get("name")
                    or data.get("name")
                    or ""
            )
            print(f"Test-Step 조회 성공: id={step_id}, name={name}")
            return data
        except requests.exceptions.Timeout:
            print(f"Test-Step API 타임아웃: {step_id}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Test-Step API 연결 실패: {step_id}")
            return None
        except Exception as e:
            print(f"Test-Step 조회 실패 ({step_id}): {e}")
            return None

    def fetch_response_codes(self):
        """API에서 response-codes 가져오기"""
        url = f"{self.base_url}/api/integration/response-codes"
        try:
            print(f"ResponseCode API 호출 중: {url}")
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("success") and json_data.get("data"):
                return json_data["data"]
            else:
                print("ResponseCode API 응답에 데이터가 없습니다.")
                return None
        except requests.exceptions.Timeout:
            print("ResponseCode API 타임아웃")
            return None
        except Exception as e:
            print(f"ResponseCode API 호출 실패: {e}")
            return None

    def load_specs_from_api_data(self, test_specs):
        """testSpecs 배열로부터 스펙 목록 동적 로드"""
        spec_file_paths = []

        print(f"testSpecs 배열로부터 {len(test_specs)}개 스펙 로드 시작...")
        for i, spec in enumerate(test_specs, 1):
            spec_id = spec.get("id", "")
            spec_name = spec.get("name", "")
            print(f"  {i}. {spec_name} (ID: {spec_id})")

            opt_path = self.fetch_opt_by_spec_id(spec_id)
            if opt_path:
                spec_file_paths.append(opt_path)

        print(f"총 {len(spec_file_paths)}개 스펙 파일 로드 완료")
        return spec_file_paths

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
            print(f"[WARNING] IP 주소 가져오기 실패: {e}")
            return "127.0.0.1"

    def send_heartbeat_idle(self):
        """시험 정보 불러오기 시 idle 상태 전송"""
        url = "http://ect2.iptime.org:20223/api/heartbeat"
        try:
            ip_address = self.get_local_ip_address()
            payload = {
                "ipAddress": ip_address,
                "status": "idle"
            }
            response = requests.post(url, json=payload, timeout=self.timeout)
            print(f"[INFO] Heartbeat (idle) 응답 코드: {response.status_code}")
            response.raise_for_status()
            print(f"[INFO] Heartbeat (idle) 전송 성공: {payload}")
            return True
        except Exception as e:
            print(f"[WARNING] Heartbeat (idle) 전송 실패: {e}")
            return False

    def send_heartbeat_busy(self, test_info):
        """시험 시작 시 busy 상태 + 시험 정보 전송"""
        url = "http://ect2.iptime.org:20223/api/heartbeat"
        try:
            ip_address = self.get_local_ip_address()
            payload = {
                "ipAddress": ip_address,
                "status": "busy",
                "testInfo": test_info
            }
            response = requests.post(url, json=payload, timeout=self.timeout)
            print(f"[INFO] Heartbeat (busy) 응답 코드: {response.status_code}")
            response.raise_for_status()
            print(f"[INFO] Heartbeat (busy) 전송 성공: ipAddress={ip_address}")
            return True
        except Exception as e:
            print(f"[WARNING] Heartbeat (busy) 전송 실패: {e}")
            return False
