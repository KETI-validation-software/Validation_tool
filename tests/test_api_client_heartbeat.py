import unittest
from unittest.mock import Mock, patch

from api.client import APIClient


class TestAPIClientHeartbeat(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def _mock_ok_response(self):
        response = Mock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        return response

    @patch("api.client.requests.post")
    def test_pending_payload(self, mock_post):
        mock_post.return_value = self._mock_ok_response()
        with patch.object(self.client, "get_local_ip_address", return_value="192.168.1.100"):
            ok = self.client.send_heartbeat_pending()

        self.assertTrue(ok)
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload, {"ipAddress": "192.168.1.100", "status": "pending"})

    @patch("api.client.requests.post")
    def test_ready_payload_with_full_test_info(self, mock_post):
        mock_post.return_value = self._mock_ok_response()
        test_info = {
            "testRequestId": "clxxx1234567890abcdef",
            "companyName": "테스트 주식회사",
            "contactPerson": "홍길동",
            "productName": "스마트 IoT 디바이스",
            "modelName": "IoT-2024",
            "version": "1.0.0",
            "testGroups": [{"id": "group-001", "name": "기본 기능 테스트", "testRange": "API 호출 및 응답"}],
            "scheduledDate": "2024-01-15",
            "startTime": "09:00",
            "endTime": "18:00",
        }

        with patch.object(self.client, "get_local_ip_address", return_value="192.168.1.100"):
            ok = self.client.send_heartbeat_ready(test_info)

        self.assertTrue(ok)
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["testInfo"], test_info)

    @patch("api.client.requests.post")
    def test_in_progress_payload_has_only_test_request_id(self, mock_post):
        mock_post.return_value = self._mock_ok_response()

        with patch.object(self.client, "get_local_ip_address", return_value="192.168.1.100"):
            ok = self.client.send_heartbeat_in_progress("clxxx1234567890abcdef")

        self.assertTrue(ok)
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload, {
            "ipAddress": "192.168.1.100",
            "status": "in_progress",
            "testInfo": {"testRequestId": "clxxx1234567890abcdef"},
        })

    @patch("api.client.requests.post")
    def test_error_payload_has_error_message(self, mock_post):
        mock_post.return_value = self._mock_ok_response()

        with patch.object(self.client, "get_local_ip_address", return_value="192.168.1.100"):
            ok = self.client.send_heartbeat_error("데이터베이스 연결 실패: Connection timeout after 30s")

        self.assertTrue(ok)
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload, {
            "ipAddress": "192.168.1.100",
            "status": "error",
            "errorMessage": "데이터베이스 연결 실패: Connection timeout after 30s",
        })


if __name__ == "__main__":
    unittest.main()
