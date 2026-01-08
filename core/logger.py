"""
디버그 레벨별 로깅 시스템
- 0 (ERROR): 에러만 출력
- 1 (WARN): 중요 정보 (API 요청/응답 요약)
- 2 (INFO): 검증 과정, 매핑 정보
- 3 (DEBUG): 모든 디버그 정보 출력
"""

class Logger:
    LEVEL_ERROR = 0    # 에러만
    LEVEL_WARN = 1     # 중요 정보 (API 요청/응답 요약)
    LEVEL_INFO = 2     # 검증 과정, 매핑 정보
    LEVEL_DEBUG = 3    # 모든 디버그 정보
    
    current_level = 1  # 기본값: WARN
    
    @classmethod
    def set_level(cls, level):
        """디버그 레벨 설정"""
        cls.current_level = level
    
    @classmethod
    def error(cls, msg):
        """에러 메시지 (항상 출력)"""
        print(f"[ERROR] {msg}")
    
    @classmethod
    def warn(cls, msg):
        """중요 정보 (레벨 1 이상)"""
        if cls.current_level >= cls.LEVEL_WARN:
            print(f"[WARN] {msg}")
    
    @classmethod
    def info(cls, msg):
        """일반 정보 (레벨 2 이상)"""
        if cls.current_level >= cls.LEVEL_INFO:
            print(f"[INFO] {msg}")
    
    @classmethod
    def debug(cls, msg):
        """상세 디버그 정보 (레벨 3)"""
        if cls.current_level >= cls.LEVEL_DEBUG:
            print(f"[DEBUG] {msg}")


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
