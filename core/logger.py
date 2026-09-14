"""
디버그 레벨별 로깅 시스템
- 0 (ERROR): 에러만 출력
- 1 (WARN): 중요 정보 (API 요청/응답 요약)
- 2 (INFO): 검증 과정, 매핑 정보
- 3 (DEBUG): 모든 디버그 정보 출력
"""

import datetime
import os
import sys
import threading


def _log_dir():
    """로그 폴더 — exe 옆(또는 소스 루트)의 results/logs."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "results", "logs")


class Logger:
    LEVEL_ERROR = 0    # 에러만
    LEVEL_WARN = 1     # 중요 정보 (API 요청/응답 요약)
    LEVEL_INFO = 2     # 검증 과정, 매핑 정보
    LEVEL_DEBUG = 3    # 모든 디버그 정보

    current_level = 1  # 기본값: WARN

    # 콘솔 창을 닫으면 로그가 통째로 사라져 원인 추적이 막히던 문제 때문에
    # 파일로도 같이 남긴다. 실행 1회당 파일 1개, append-only.
    _file = None
    _lock = threading.Lock()
    _file_failed = False   # 파일을 못 열면 한 번만 알리고 콘솔 출력만 계속한다

    @classmethod
    def _emit(cls, line):
        print(line)
        if cls._file_failed:
            return
        try:
            with cls._lock:
                if cls._file is None:
                    folder = _log_dir()
                    os.makedirs(folder, exist_ok=True)
                    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    cls._file = open(os.path.join(folder, f"run_{stamp}.log"),
                                     "a", encoding="utf-8")
                cls._file.write(line + "\n")
                cls._file.flush()   # 중간에 죽어도 직전까지 남아야 한다
        except Exception as e:
            cls._file_failed = True
            print(f"[ERROR] 로그 파일 기록 실패 — 콘솔로만 출력합니다: {e}")

    @classmethod
    def set_level(cls, level):
        """디버그 레벨 설정"""
        cls.current_level = level

    @classmethod
    def error(cls, msg):
        """에러 메시지 (항상 출력)"""
        cls._emit(f"[ERROR] {msg}")

    @classmethod
    def warn(cls, msg):
        """중요 정보 (레벨 1 이상)"""
        if cls.current_level >= cls.LEVEL_WARN:
            cls._emit(f"[WARN] {msg}")

    @classmethod
    def warning(cls, msg):
        """warn의 별칭 (표준 logging 모듈 호환성)"""
        cls.warn(msg)

    @classmethod
    def info(cls, msg):
        """일반 정보 (레벨 2 이상)"""
        if cls.current_level >= cls.LEVEL_INFO:
            cls._emit(f"[INFO] {msg}")

    @classmethod
    def debug(cls, msg):
        """상세 디버그 정보 (레벨 3)"""
        if cls.current_level >= cls.LEVEL_DEBUG:
            cls._emit(f"[DEBUG] {msg}")


# 전역 함수로 간편하게 사용 가능
def set_debug_level(level):
    """디버그 레벨 설정 (0~3)"""
    Logger.set_level(level)

def log_error(msg):
    """에러 로그"""
    Logger.error(msg)

def log_warn(msg):
    """경고 로그"""
    Logger.warn(msg)

def log_info(msg):
    """정보 로그"""
    Logger.info(msg)

def log_debug(msg):
    """디버그 로그"""
    Logger.debug(msg)
