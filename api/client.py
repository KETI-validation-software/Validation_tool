"""
API client helpers for management/integration endpoints.
"""

import socket
from urllib.parse import urlparse

import requests

import config.CONSTANTS as CONSTANTS
from core.logger import Logger


class APIClient:
    """HTTP client wrapper used by UI/services."""

    def __init__(self):
        self.timeout = 10

    @property
    def base_url(self):
        return CONSTANTS.management_url

    def fetch_test_info_by_ip(self, ip_address):
        url = f"{self.base_url}/api/integration/test-requests/by-ip?ipAddress={ip_address}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()
            if json_data.get("success") and json_data.get("data"):
                Logger.info(f"API test info fetched: {len(json_data['data'])} record(s)")
                return json_data["data"][0]
            raise ValueError("No test info in API response")
        except requests.exceptions.Timeout:
            Logger.error("API test info timeout")
            return None
        except requests.exceptions.ConnectionError:
            Logger.error("API test info connection error")
            return None
        except Exception as e:
            Logger.error(f"API test info error: {e}")
            return None

    def fetch_specification_by_id(self, spec_id):
        url = f"{self.base_url}/api/integration/specifications/{spec_id}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            Logger.error(f"Specification timeout: {spec_id}")
            return None
        except requests.exceptions.ConnectionError:
            Logger.error(f"Specification connection error: {spec_id}")
            return None
        except Exception as e:
            Logger.error(f"Specification fetch error ({spec_id}): {e}")
            return None

    def fetch_test_step_by_id(self, step_id):
        url = f"{self.base_url}/api/integration/test-steps/{step_id}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            Logger.error(f"Test-step timeout: {step_id}")
            return None
        except requests.exceptions.ConnectionError:
            Logger.error(f"Test-step connection error: {step_id}")
            return None
        except Exception as e:
            Logger.error(f"Test-step fetch error ({step_id}): {e}")
            return None

    def fetch_response_codes(self):
        url = f"{self.base_url}/api/integration/response-codes"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()
            if json_data.get("success") and json_data.get("data"):
                return json_data["data"]
            Logger.warning("Response code API returned empty data")
            return None
        except requests.exceptions.Timeout:
            Logger.error("Response code API timeout")
            return None
        except Exception as e:
            Logger.error(f"Response code API error: {e}")
            return None

    def fetch_admin_code(self, base_url=None):
        target_url = (base_url or self.base_url).rstrip("/")
        url = f"{target_url}/api/integration/admin-code"
        try:
            response = requests.get(url, timeout=5, verify=False)
            response.raise_for_status()
            json_data = response.json()
            if "adminCode" in json_data:
                return json_data["adminCode"]
            data_obj = json_data.get("data")
            if isinstance(data_obj, dict):
                if "adminCode" in data_obj:
                    return data_obj["adminCode"]
                if "code" in data_obj:
                    return data_obj["code"]
            Logger.warning("Admin code API did not include adminCode/code")
            return None
        except requests.exceptions.Timeout:
            Logger.error("Admin code API timeout")
            return None
        except Exception as e:
            Logger.error(f"Admin code API error: {e}")
            return None

    def get_local_ip_address(self):
        try:
            target_host = "8.8.8.8"
            target_port = 80
            if getattr(CONSTANTS, "url", None):
                parsed = urlparse(CONSTANTS.url)
                if parsed.hostname:
                    target_host = parsed.hostname
                    target_port = parsed.port if parsed.port else (443 if parsed.scheme == "https" else 80)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((target_host, target_port))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except Exception as e:
            Logger.warning(f"Local IP detection failed: {e}")
            return "127.0.0.1"

    def send_heartbeat(self, status, test_info=None, error_message=None):
        url = f"{self.base_url}/api/heartbeat"
        try:
            if status != "stopped" and getattr(CONSTANTS, "HEARTBEAT_STOPPED_LOCK", False):
                Logger.info(f"[INFO] Heartbeat ({status}) suppressed by stopped-lock")
                return True
            payload = {
                "ipAddress": self.get_local_ip_address(),
                "status": status,
            }
            if test_info is not None:
                payload["testInfo"] = test_info
            if error_message:
                payload["errorMessage"] = error_message
            if status in ("in_progress", "stopped"):
                rid = ""
                if isinstance(payload.get("testInfo"), dict):
                    rid = payload["testInfo"].get("testRequestId", "")
                Logger.info(f"[INFO] Heartbeat ({status}) requestId={rid}")

            response = requests.post(url, json=payload, timeout=self.timeout)
            Logger.info(f"[INFO] Heartbeat ({status}) code: {response.status_code}")
            response.raise_for_status()
            return True
        except Exception as e:
            Logger.warning(f"[WARNING] Heartbeat ({status}) failed: {e}")
            return False

    def send_heartbeat_pending(self):
        return self.send_heartbeat("pending")

    def send_heartbeat_ready(self, test_info):
        return self.send_heartbeat("ready", test_info=test_info)

    def send_heartbeat_in_progress(self, test_request_id):
        test_info = {"testRequestId": test_request_id} if test_request_id else {}
        return self.send_heartbeat("in_progress", test_info=test_info)

    def send_heartbeat_completed(self):
        if getattr(CONSTANTS, "SUPPRESS_COMPLETED_HEARTBEAT", False):
            Logger.info("[INFO] Heartbeat (completed) suppressed by pause/stop guard")
            return True
        return self.send_heartbeat("completed")

    def send_heartbeat_stopped(self, test_request_id=None):
        setattr(CONSTANTS, "HEARTBEAT_STOPPED_LOCK", True)
        test_info = {"testRequestId": test_request_id} if test_request_id else None
        return self.send_heartbeat("stopped", test_info=test_info)

    def send_heartbeat_error(self, error_message):
        return self.send_heartbeat("error", error_message=error_message)

    # Backward compatibility
    def send_heartbeat_idle(self):
        return self.send_heartbeat_pending()

    def send_heartbeat_busy(self, test_info):
        test_request_id = ""
        if isinstance(test_info, dict):
            test_request_id = test_info.get("testRequestId", "")
        return self.send_heartbeat_in_progress(test_request_id)
