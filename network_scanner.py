import socket
from PyQt5.QtCore import QObject, pyqtSignal


class NetworkScanWorker(QObject):
    """
    네트워크 스캔 작업을 수행하는 워커 클래스
    - 백그라운드 스레드에서 실행되어 GUI 스레드 안전성 보장
    - 로컬 IP 주소 탐지 및 사용 가능한 포트 스캔
    """
    scan_completed = pyqtSignal(list)  # 스캔 완료 시 URL 리스트 전달
    scan_failed = pyqtSignal(str)      # 스캔 실패 시 오류 메시지 전달

    def __init__(self, port_range_start=8000, port_range_end=8100, max_ports=10):
        """
        Args:
            port_range_start: 스캔할 포트 범위 시작
            port_range_end: 스캔할 포트 범위 끝
            max_ports: 최대 검색할 포트 개수
        """
        super().__init__()
        self.port_range_start = port_range_start
        self.port_range_end = port_range_end
        self.max_ports = max_ports

    def scan_network(self):
        """네트워크 스캔 메인 메서드"""
        try:
            local_ip = self._get_local_ip()
            if not local_ip:
                self.scan_failed.emit("내 IP 주소를 찾을 수 없습니다.")
                return

            ports = self._scan_available_ports(
                local_ip,
                range(self.port_range_start, self.port_range_end)
            )

            if ports:
                # 상위 3개 포트만 반환
                urls = [f"{local_ip}:{p}" for p in ports[:3]]
                self.scan_completed.emit(urls)
            else:
                self.scan_failed.emit("검색된 사용가능 포트 없음")

        except Exception as e:
            self.scan_failed.emit(f"네트워크 탐색 중 오류 발생:\n{str(e)}")

    def _get_local_ip(self):
        """로컬 IP 주소 획득"""
        try:
            # DNS 서버로 연결을 시도하여 로컬 IP 획득 (실제 연결하지 않음)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            try:
                # 백업 방법: 호스트명으로 IP 획득
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return None

    def _scan_available_ports(self, ip, port_range):
        """지정된 IP에서 사용 가능한 포트 스캔"""
        found = []

        for port in port_range:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.settimeout(0.1)  # 100ms 타임아웃
                    sock.bind((ip, port))  # 바인딩 가능하면 사용 가능한 포트
                    found.append(port)

                    # 최대 개수에 도달하면 중단
                    if len(found) >= self.max_ports:
                        break

            except Exception:
                # 바인딩 실패 = 이미 사용중인 포트
                continue

        return found