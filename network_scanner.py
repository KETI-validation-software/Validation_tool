import socket
from PyQt5.QtCore import QObject, pyqtSignal
try:
    from scapy.all import ARP, Ether, srp
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("scapy 라이브러리가 설치되지 않았습니다. ARP 스캔 기능을 사용할 수 없습니다.")


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
                # 상위 10개 포트만 반환
                urls = [f"{local_ip}:{p}" for p in ports[:10]]
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


class ARPScanWorker(QObject):
    """
    ARP 스캔으로 동일 네트워크의 활성 IP를 검색하는 워커 클래스
    - 물리보안시스템용
    - 백그라운드 스레드에서 실행되어 GUI 스레드 안전성 보장
    """
    scan_completed = pyqtSignal(list)  # 스캔 완료 시 IP 리스트 전달
    scan_failed = pyqtSignal(str)      # 스캔 실패 시 오류 메시지 전달

    def __init__(self, test_port=None):
        """
        Args:
            test_port: URL에 사용할 포트 번호 (예: 8080)
        """
        super().__init__()
        self.test_port = test_port

    def scan_arp(self):
        """ARP 스캔 메인 메서드"""
        try:
            if not SCAPY_AVAILABLE:
                self.scan_failed.emit(
                    "scapy 라이브러리가 설치되지 않았습니다."
                )
                return

            # 1. 내 IP와 네트워크 대역 감지
            my_ip = self._get_local_ip()
            if not my_ip:
                self.scan_failed.emit("로컬 IP 주소를 가져올 수 없습니다.")
                return

            network = self._get_network_range(my_ip)
            if not network:
                self.scan_failed.emit("네트워크 대역을 계산할 수 없습니다.")
                return

            print(f"ARP 스캔 시작: {network}")

            # 2. ARP 스캔 실행
            try:
                arp_request = ARP(pdst=network)
                broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
                arp_request_broadcast = broadcast / arp_request

                # timeout 3초, verbose=0 (출력 억제)
                answered_list = srp(arp_request_broadcast, timeout=3, verbose=0)[0]
            except Exception as arp_error:
                # Npcap 미설치 오류 감지
                error_msg = str(arp_error).lower()
                if "winpcap" in error_msg or "npcap" in error_msg or "layer2" in error_msg:
                    self.scan_failed.emit(
                        "❌ Npcap이 설치되지 않았습니다.\n\n"
                        "ARP 스캔 기능을 사용하려면 Npcap 설치가 필요합니다.\n\n"
                        "📥 다운로드: https://npcap.com/\n\n"
                        "설치 후 프로그램을 재시작해주세요.\n"
                        "또는 '직접 입력' 기능을 사용해주세요."
                    )
                    return
                else:
                    raise  # 다른 에러는 상위로 전달

            # 3. 응답받은 IP 수집 (내 IP 제외)
            found_ips = []
            for element in answered_list:
                ip = element[1].psrc
                if ip != my_ip:  # 내 IP 제외
                    found_ips.append(ip)

            # [임시] 본인 IP도 검색 결과에 추가
            found_ips.append(my_ip)

            if not found_ips:
                self.scan_failed.emit(
                    "동일 네트워크에서 활성 장비를 찾을 수 없습니다.\n"
                    "'직접 입력' 기능을 사용해주세요."
                )
                return

            # 4. 최대 10개로 제한
            found_ips = found_ips[:10]

            # 5. IP:Port 형식으로 변환
            if self.test_port:
                urls = [f"{ip}:{self.test_port}" for ip in found_ips]
            else:
                urls = found_ips  # 포트 없이 IP만

            print(f"ARP 스캔 완료: {urls}")
            self.scan_completed.emit(urls)

        except Exception as e:
            print(f"ARP 스캔 오류: {e}")
            import traceback
            traceback.print_exc()
            self.scan_failed.emit(f"ARP 스캔 중 오류 발생:\n{str(e)}")

    def _get_local_ip(self):
        """로컬 IP 주소 획득"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return None

    def _get_network_range(self, ip):
        """IP 주소로부터 네트워크 대역 계산 (예: 192.168.1.0/24)"""
        try:
            # IP를 . 으로 분리
            parts = ip.split('.')
            if len(parts) != 4:
                return None

            # /24 서브넷 가정 (Class C)
            network = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            return network

        except Exception as e:
            print(f"네트워크 대역 계산 오류: {e}")
            return None