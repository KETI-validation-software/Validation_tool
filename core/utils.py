import re
import os
import json
from pathlib import Path
from datetime import datetime
import traceback

# ==========================================
# 가벼운 공용 기능 함수들 (독립 모듈)
# ==========================================

def remove_api_number_suffix(api_name):
    """
    API 이름 뒤에 붙은 숫자 접미사를 제거하는 함수
    예: "Authentication1" -> "Authentication"
    """
    if api_name is None:
        return ""
    
    if not isinstance(api_name, str):
        api_name = str(api_name)
        
    return re.sub(r'\d+$', '', api_name)

def safe_str(value):
    """
    UI 표시를 위해 데이터를 안전하게 문자열로 변환하는 함수
    None -> "" 변환, 그 외에는 str(value)
    """
    if value is None:
        return ""
    return str(value)

def to_detail_text(val_text):
    """
    검증 결과 텍스트를 항상 사람이 읽을 문자열로 표준화
    """
    if val_text is None:
        return "오류가 없습니다."
    
    if isinstance(val_text, list):
        return "\n".join(str(x) for x in val_text) if val_text else "오류가 없습니다."
    
    if isinstance(val_text, dict):
        try:
            return json.dumps(val_text, indent=2, ensure_ascii=False)
        except Exception:
            return str(val_text)
            
    return str(val_text)

def redact(payload):
    """
    비밀번호, 토큰 등 민감 정보를 마스킹 처리 (***)
    """
    try:
        if isinstance(payload, dict):
            p = dict(payload)
            for k in ["accessToken", "token", "Authorization", "password", "secret", "apiKey"]:
                if k in p and isinstance(p[k], (str, bytes)):
                    p[k] = "***"
            return p
        return payload
    except Exception:
        return payload

def clean_trace_directory(trace_path):
    """
    지정된 trace 디렉토리 내의 파일들을 삭제 (초기화)
    (경로를 인자로 받아서 처리하도록 수정됨)
    """
    print(f"[TRACE_CLEAN] 디렉토리 정리 시작: {trace_path}")
    
    if not os.path.exists(trace_path):
        try:
            os.makedirs(trace_path, exist_ok=True)
        except Exception:
            pass
        return

    for name in os.listdir(trace_path):
        file_path = os.path.join(trace_path, name)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"[TRACE_CLEAN] 삭제: {name}")
            except OSError:
                pass

def format_schema(schema):
    """
    스키마 구조를 보기 좋은 문자열로 변환 (UI 표시용)
    """
    if not schema:
        return "빈 스키마"

    def schema_to_string(schema_obj, indent=0):
        result = ""
        spaces = "  " * indent

        if isinstance(schema_obj, dict):
            for key, value in schema_obj.items():
                # OptionalKey 처리
                if hasattr(key, 'expected_data'):
                    key_name = f"{key.expected_data} (선택사항)"
                else:
                    key_name = str(key)

                if isinstance(value, dict):
                    result += f"{spaces}{key_name}: {{\n"
                    result += schema_to_string(value, indent + 1)
                    result += f"{spaces}}}\n"
                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    result += f"{spaces}{key_name}: [\n"
                    result += schema_to_string(value[0], indent + 1)
                    result += f"{spaces}]\n"
                else:
                    val_str = value.__name__ if hasattr(value, '__name__') else str(value)
                    result += f"{spaces}{key_name}: {val_str}\n"
        return result

    return schema_to_string(schema)

# ==========================================
# Trace 파일 관련 함수들
# ==========================================

def load_from_trace_file(api_name, direction="RESPONSE"):
    """trace 파일에서 특정 API의 RESPONSE 데이터를 읽어옴"""
    try:
            # API 이름에서 슬래시 제거
            api_name_clean = api_name.lstrip("/")
            api_name_no_prefix = re.sub(r'^\d+_', '', api_name_clean)
            trace_folder = Path("results/trace")
            trace_file = None
            
            if trace_folder.exists():
                # 가능한 파일명 패턴들
                possible_patterns = [
                    f"trace_{api_name_clean}.ndjson",  # trace_CameraProfiles.ndjson
                    f"trace_{api_name_no_prefix}.ndjson",  # 동일하면 중복이지만 안전장치
                ]
                
                # 실제 파일 목록에서 검색
                for ndjson_file in trace_folder.glob("trace_*.ndjson"):
                    file_name = ndjson_file.name
                    api_part = file_name.replace("trace_", "").replace(".ndjson", "")
                    api_part_no_prefix = re.sub(r'^\d+_', '', api_part)
                    
                    # 매칭 확인
                    if api_part == api_name_clean or api_part_no_prefix == api_name_no_prefix:
                        trace_file = ndjson_file
                        print(f"[DEBUG] ✅ 매칭 성공: {file_name} (검색어: {api_name_clean})")
                        break
            
            if trace_file is None or not trace_file.exists():
                print(f"[DEBUG] trace 파일 없음 (검색어: {api_name_clean})")
                return None

            latest_data = None

            with open(trace_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)

                        if entry.get('dir') == direction:
                            latest_data = entry.get('data', {})
                            # 계속 읽어서 가장 마지막 데이터를 가져옴

                    except json.JSONDecodeError:
                        continue

            if latest_data:
                print(f"[DEBUG] trace 파일에서 {api_name} {direction} 로드 완료: {len(str(latest_data))} bytes")
                return latest_data
            else:
                print(f"[DEBUG] trace 파일에 {api_name} {direction} 없음")
                return None

    except Exception as e:
        print(f"[ERROR] trace 파일 로드 실패: {e}")
        traceback.print_exc() 
        return None