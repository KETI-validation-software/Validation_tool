import unittest
from unittest.mock import patch

from network_scanner import ARPScanWorker


class _AnsweredPacket:
    def __init__(self, ip):
        self.psrc = ip


class TestArpScanWorker(unittest.TestCase):
    @patch("network_scanner.srp")
    @patch("network_scanner.get_local_ip", return_value="192.168.0.10")
    def test_scan_arp_excludes_local_ip_from_results(self, _mock_local_ip, mock_srp):
        worker = ARPScanWorker(test_port=8080)
        captured = []
        failures = []

        mock_srp.return_value = (
            [
                (None, _AnsweredPacket("192.168.0.10")),
                (None, _AnsweredPacket("192.168.0.20")),
            ],
            [],
        )

        worker.scan_completed.connect(captured.append)
        worker.scan_failed.connect(failures.append)

        worker.scan_arp()

        self.assertEqual(failures, [])
        self.assertEqual(captured, [["192.168.0.20:8080"]])


if __name__ == "__main__":
    unittest.main()
