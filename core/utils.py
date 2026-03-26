import re
import os
import json
from pathlib import Path
import traceback
import sys
import importlib
import importlib.util
import types
import html
from core.logger import Logger

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

# transprotocoldesc UI 표시용 함수 (실제 받은 값 그대로 표시)
def replace_transport_desc_for_display(json_str):
    """
    UI 표시용 - 실제 받은 transProtocolDesc 값을 그대로 표시
    """
    # 원본 그대로 반환 (하드코딩 치환 제거)
    return json_str


def _k(*codepoints):
    return "".join(chr(code) for code in codepoints)


def build_monitor_header_text(type_label, step_name):
    if not isinstance(step_name, str):
        return f"[{type_label}] {step_name}"

    if step_name.startswith("["):
        return step_name

    plain_title_prefixes = (
        f"{_k(0xACB0, 0xACFC)}:",
        f"{_k(0xAC80, 0xC99D, 0x20, 0xACB0, 0xACFC)}:",
        f"{_k(0xC2DC, 0xD5D8, 0x20, 0x41, 0x50, 0x49, 0x20, 0xACB0, 0xACFC)}:",
        _k(0xC2DC, 0xD5D8, 0x20, 0xC644, 0xB8CC),
        _k(0xC2DC, 0xD5D8, 0x20, 0xC2DC, 0xC791),
    )
    plain_titles = {
        _k(0xAD00, 0xB9AC, 0xC2DC, 0xC2A4, 0xD15C, 0x20, 0xACB0, 0xACFC, 0x20, 0xC804, 0xC1A1, 0x20, 0xC644, 0xB8CC),
    }

    if step_name.startswith(plain_title_prefixes) or step_name in plain_titles:
        return step_name

    return f"[{type_label}] {step_name}"


def normalize_monitor_step_name(step_name):
    if not isinstance(step_name, str):
        return step_name

    return step_name.replace(f" ({_k(0xC751, 0xB2F5)})", "")


def normalize_monitor_request_json(type_label, step_name, request_json, details=""):
    if request_json:
        return request_json

    if details:
        return request_json

    header_text = build_monitor_header_text(type_label, step_name)
    if isinstance(header_text, str) and header_text.startswith("["):
        return _k(0xBA54, 0xC2DC, 0xC9C0, 0x20, 0xC5C6, 0xC74C)

    return request_json


def build_monitor_step_name(api_name, kind):
    label_map = {
        "request": _k(0xC694, 0xCCAD),
        "response": _k(0xC751, 0xB2F5),
    }
    suffix = label_map.get(kind, kind)
    return f"{api_name} ({suffix})" if suffix else str(api_name)


def build_webhook_monitor_step_name(api_name, kind, role="platform"):
    role_lower = str(role).lower()

    if role_lower == "system":
        label_map = {
            "event": f"[{_k(0xC6F9, 0xD6C5, 0x20, 0xC218, 0xC2E0)}] {api_name} ({_k(0xC694, 0xCCAD)})",
            "ack": f"[{_k(0xC6F9, 0xD6C5, 0x20, 0xC1A1, 0xC2E0)}] {api_name} ({_k(0xC751, 0xB2F5)})",
        }
    else:
        label_map = {
            "event": f"[{_k(0xC6F9, 0xD6C5, 0x20, 0xC1A1, 0xC2E0)}] {api_name} ({_k(0xC694, 0xCCAD)})",
            "ack": f"[{_k(0xC6F9, 0xD6C5, 0x20, 0xC218, 0xC2E0)}] {api_name} ({_k(0xC751, 0xB2F5)})",
        }

    return label_map.get(kind, str(api_name))


def build_monitor_result_title(api_name, completed_attempts, suffix=""):
    title = f"{_k(0xAC80, 0xC99D, 0x20, 0xACB0, 0xACFC)}: {api_name}"
    if suffix:
        title += f" - {suffix}"
    return f"{title} ({completed_attempts}{_k(0xD68C, 0x20, 0xAC80, 0xC99D, 0x20, 0xC644, 0xB8CC)})"


def build_monitor_start_title():
    return _k(0xC2DC, 0xD5D8, 0x20, 0xC2DC, 0xC791)


def build_monitor_start_details(api_count):
    return f"API {_k(0xAC1C, 0xC218)} {int(api_count)}{_k(0xAC1C)}"


def generate_monitor_notice_html(message, accent_color="#275554", background_color="#F8FAFC", text_color="#1F2937"):
    escaped_message = html.escape(str(message))
    return (
        f"<div style=\"margin-top: 10px; margin-bottom: 10px; padding: 12px 14px; "
        f"border-left: 4px solid {accent_color}; background-color: {background_color}; "
        f"border-radius: 4px; font-size: 17px; font-weight: 500; color: {text_color}; "
        f"font-family: 'Noto Sans KR';\">{escaped_message}</div>"
    )


def _format_seconds_for_monitor_display(milliseconds):
    if milliseconds is None:
        return ""

    seconds = float(milliseconds) / 1000
    if seconds.is_integer():
        return f"{int(seconds)}{_k(0xCD08)}"
    return f"{seconds:.2f}".rstrip("0").rstrip(".") + _k(0xCD08)


def build_monitor_response_time_text(response_time_ms=None, total_timeout_ms=None):
    if response_time_ms is None:
        return ""

    response_time_text = f"{_k(0xC751, 0xB2F5, 0x20, 0xC18C, 0xC694, 0x20, 0xC2DC, 0xAC04)}: {float(response_time_ms) / 1000:.2f}{_k(0xCD08)}"
    timeout_text = _format_seconds_for_monitor_display(total_timeout_ms)
    if timeout_text:
        response_time_text += f" ({timeout_text})"
    return response_time_text


def build_monitor_progress_details(protocol):
    protocol_lower = str(protocol).lower()
    if protocol_lower == "basic":
        protocol_text = _k(0xC77C, 0xBC18, 0x20, 0xBA54, 0xC2DC, 0xC9C0)
    elif protocol_lower == "webhook":
        protocol_text = _k(0xC6F9, 0xD6C5, 0xBA54, 0xC2DC, 0xC9C0)
    else:
        protocol_text = f"{_k(0xC2E4, 0xC2DC, 0xAC04, 0x20, 0xBA54, 0xC2DC, 0xC9C0)}: {protocol}"
    return f"{_k(0xAC80, 0xC99D, 0x20, 0xC9C4, 0xD589, 0x20, 0xC911)}... | {protocol_text}"


def build_monitor_result_details(pass_count, error_count, protocol, response_time_ms=None, extra_detail=""):
    protocol_lower = str(protocol).lower()
    if protocol_lower == "basic":
        protocol_text = _k(0xC77C, 0xBC18, 0x20, 0xBA54, 0xC2DC, 0xC9C0)
    elif protocol_lower == "webhook":
        protocol_text = _k(0xC6F9, 0xD6C5, 0xBA54, 0xC2DC, 0xC9C0)
    else:
        protocol_text = f"{_k(0xC2E4, 0xC2DC, 0xAC04, 0x20, 0xBA54, 0xC2DC, 0xC9C0)}: {protocol}"
    parts = [
        f"{_k(0xD1B5, 0xACFC, 0x20, 0xD544, 0xB4DC, 0x20, 0xC218)}: {pass_count}, {_k(0xC2E4, 0xD328, 0x20, 0xD544, 0xB4DC, 0x20, 0xC218)}: {error_count}",
        protocol_text,
    ]
    if response_time_ms is not None:
        parts.append(f"{_k(0xC751, 0xB2F5, 0x20, 0xC18C, 0xC694, 0x20, 0xC2DC, 0xAC04)}: {float(response_time_ms) / 1000:.2f}{_k(0xCD08)}")
    if extra_detail:
        parts.append(f"{_k(0xC0C1, 0xC138)}: {extra_detail}")
    return " | ".join(parts)


    return " | ".join(parts)


def build_monitor_log_text(step_name, request_json="", score=None, details="", direction="RECV", response_time_ms=None, total_timeout_ms=None, timestamp=None):
    from datetime import datetime

    type_label = _k(0xC1A1, 0xC2E0) if direction == "SEND" else _k(0xC218, 0xC2E0)
    header_text = build_monitor_header_text(type_label, step_name)

    if request_json:
        request_json = replace_transport_desc_for_display(request_json)
    request_json = normalize_monitor_request_json(type_label, step_name, request_json, details)

    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M:%S")

    header_line = f"{header_text} {timestamp}"
    response_time_text = build_monitor_response_time_text(response_time_ms, total_timeout_ms)
    if response_time_text:
        header_line += f" | {response_time_text}"

    parts = [header_line]

    if details:
        parts.extend(["", str(details)])

    if request_json:
        parts.extend(["", request_json])

    if direction == "RECV" and score is not None:
        try:
            score_display = f"{float(score):.1f}"
        except (TypeError, ValueError):
            score_display = str(score)
        parts.extend(["", f"{_k(0xD3C9, 0xAC00, 0x20, 0xC810, 0xC218)}: {score_display}%"])

    return "\n".join(parts).strip()


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
    Logger.debug(f" 디렉토리 정리 시작: {trace_path}")
    
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
                Logger.debug(f" 삭제: {name}")
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
                    # 딕셔너리가 비어있는지 확인
                    if not value:
                        result += f"{spaces}{key_name}: {{}}\n"
                    else:
                        result += f"{spaces}{key_name}: {{\n"
                        result += schema_to_string(value, indent + 1)
                        result += f"{spaces}}}\n"
                elif isinstance(value, list):
                    if len(value) == 0:
                        result += f"{spaces}{key_name}: []\n"
                    elif len(value) > 0 and isinstance(value[0], dict):
                        # 리스트 안의 딕셔너리가 비어있는지 확인
                        if not value[0]:
                            result += f"{spaces}{key_name}: [{{}}]\n"
                        else:
                            result += f"{spaces}{key_name}: [{{\n"
                            result += schema_to_string(value[0], indent + 1)
                            result += f"{spaces}}}]\n"
                    else:
                        result += f"{spaces}{key_name}: [{value[0]}]\n"
                else:
                    val_str = value.__name__ if hasattr(value, '__name__') else str(value)
                    result += f"{spaces}{key_name}: {val_str}\n"
        return result

    return schema_to_string(schema)

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
                        Logger.debug(f" ✅ 매칭 성공: {file_name} (검색어: {api_name_clean})")
                        break
            
            if trace_file is None or not trace_file.exists():
                Logger.debug(f" trace 파일 없음 (검색어: {api_name_clean})")
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
                Logger.debug(f" trace 파일에서 {api_name} {direction} 로드 완료: {len(str(latest_data))} bytes")
                return latest_data
            else:
                Logger.debug(f" trace 파일에 {api_name} {direction} 없음")
                return None

    except Exception as e:
        Logger.error(f" trace 파일 로드 실패: {e}")
        traceback.print_exc() 
        return None

# pyinstaller로 빌드된 실행 파일 환경에서 외부에 있는 constants에서 설정값 읽어오는 함수
def load_external_constants(constants_module):

    spec_config = getattr(constants_module, "SPEC_CONFIG", [])

    # 현재 exe 실행환경 파일인지 확인
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        external_constants_path = os.path.join(exe_dir, "config", "CONSTANTS.py")

        if os.path.exists(external_constants_path):
            try:
                with open(external_constants_path, 'r', encoding='utf-8') as f:
                    constants_code = f.read()
                
                namespace = {'__file__': external_constants_path}
                exec(constants_code, namespace)

                if 'SPEC_CONFIG' in namespace:
                    spec_config = namespace['SPEC_CONFIG']
                    if hasattr(constants_module, 'SPEC_CONFIG'):
                        setattr(constants_module, 'SPEC_CONFIG', spec_config)
                
                keys_to_update = [
                    'url', 'auth_type', 'auth_info', 'company_name', 'product_name',
                    'version', 'test_category', 'test_target', 'test_range'
                ]

                # 덮어씌우기
                for key in keys_to_update:
                    if key in namespace and hasattr(constants_module, key):
                        setattr(constants_module, key, namespace[key])
                
                for i, g in enumerate(spec_config): 
                    group_name = g.get('group_name', '이름없음')
                    group_keys = [k for k in g.keys() if k not in ['group_name', 'group_id']]
                    Logger.debug(f" 그룹 {i}: {group_name} - 키: {group_keys}")
            
            except Exception as e:
                Logger.error(f" 외부 CONSTANTS.py 로드 실패: {e}")
                
    return spec_config

# spec폴더에서 모듈 로드하는 함수
def setup_external_spec_modules():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        external_spec_parent = exe_dir
    
    else:
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)

        exe_dir = os.path.dirname(current_dir)
        external_spec_parent = exe_dir
    
    external_spec_dir = os.path.join(external_spec_parent, 'spec')
    if os.path.exists(external_spec_dir):
        if external_spec_parent in sys.path:
            sys.path.remove(external_spec_parent)
        sys.path.insert(0, external_spec_parent)

        modules_to_remove = [
            'spec.Schema_request',
            'spec.Schema_response',
            'spec.Constraints_response'
        ]
        for mod_name in modules_to_remove:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        
        if 'spec' not in sys.modules:
            sys.modules['spec'] = types.ModuleType('spec')
        
        try:
            schema_file = os.path.join(exe_dir, 'spec', 'Schema_request.py')
            data_file = os.path.join(exe_dir, 'spec', 'Data_response.py')
            constraints_file = os.path.join(exe_dir, 'spec', 'Constraints_response.py')

            # Schema_request 모듈 로드
            spec = importlib.util.spec_from_file_location('spec.Schema_request', schema_file)
            schema_module = importlib.util.module_from_spec(spec)
            sys.modules['spec.Schema_request'] = schema_module
            spec.loader.exec_module(schema_module)

            # Data_response 모듈 로드
            spec = importlib.util.spec_from_file_location('spec.Data_response', data_file)
            data_module = importlib.util.module_from_spec(spec)
            sys.modules['spec.Data_response'] = data_module
            spec.loader.exec_module(data_module)

            # Constraints_response 모듈 로드
            spec = importlib.util.spec_from_file_location('spec.Constraints_response', constraints_file)
            constraints_module = importlib.util.module_from_spec(spec)
            sys.modules['spec.Constraints_response'] = constraints_module
            spec.loader.exec_module(constraints_module)

            return schema_module, data_module, constraints_module
        
        except Exception as e:
            Logger.error(f" 외부 모듈 로드 실패: {e}")

    try:
        if 'spec.Schema_request' in sys.modules:
            import spec.Schema_request
            importlib.reload(spec.Schema_request)
        if 'spec.Data_response' in sys.modules:
            import spec.Data_response
            importlib.reload(spec.Data_response)
        if 'spec.Constraints_response' in sys.modules:
            import spec.Constraints_response
            importlib.reload(spec.Constraints_response)
        
        import spec.Schema_request as schema
        import spec.Data_response as data
        import spec.Constraints_response as constraints
        return schema, data, constraints
    
    except Exception as e:
        Logger.error(f" 내부 모듈 로드 실패: {e}")
        return None, None, None

def calculate_percentage(part, total):
    """
    백분율 계산 함수 (0으로 나누기 방지)
    """
    if total > 0:
        return (part / total) * 100
    return 0

def generate_monitor_log_html(step_name, timestamp, request_json="", score=None, details=""):
    """
    모니터링 로그를 위한 HTML 생성
    """
    # 점수에 따른 색상 결정
    if score is not None:
        if score >= 100:
            text_color = "#10b981"  # 녹색 텍스트
        else:
            text_color = "#ef4444"  # 빨강 텍스트
    else:
        text_color = "#333"  # 기본 검정

    # 1. 헤더 (Step 이름 + 시간) - Table로 블록 분리
    html_content = f"""
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 15px;">
        <tr>
            <td valign="middle">
                <span style="font-size: 20px; font-weight: bold; color: {text_color}; font-family: 'Noto Sans KR';">{step_name}</span>
                <span style="font-size: 16px; color: #9ca3af; font-family: 'Consolas', monospace; margin-left: 8px;">{timestamp}</span>
            </td>
        </tr>
    </table>
    """

    # 2. 내용 영역
    html_content += f"""
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td>
    """

    # 2-1. 상세 내용 (Details)
    if details:
        html_content += f"""
            <div style="margin-bottom: 8px; font-size: 18px; color: #6b7280; font-family: 'Noto Sans KR';">
                {details}
            </div>
        """

    # 2-2. JSON 데이터 (회색 박스)
    if request_json and request_json.strip():
        escaped_json = html.escape(request_json)
        is_json_structure = request_json.strip().startswith('{') or request_json.strip().startswith('[')

        if is_json_structure:
            html_content += f"""
            <div style="margin-top: 5px; margin-bottom: 10px;">
                <div style="font-size: 15px; color: #9ca3af; font-weight: bold; margin-bottom: 4px;">📦 데이터</div>
                <div style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; padding: 10px;">
                    <pre style="margin: 0; font-family: 'Consolas', monospace; font-size: 18px; color: #1f2937;">{escaped_json}</pre>
                </div>
            </div>
            """
        else:
            # JSON이 아닌 일반 텍스트일 경우
            html_content += f"""
            <div style="margin-top: 5px; margin-bottom: 10px;">
                <pre style="font-size: 18px; color: #6b7280; font-family: 'Consolas', monospace;">{escaped_json}</pre>
            </div>
            """

    # 2-3. 점수 (Score)
    if score is not None:
        html_content += f"""
            <div style="margin-top: 5px; font-size: 18px; color: #6b7280; font-weight: bold; font-family: 'Consolas', monospace;">
                점수: {score:.1f}%
            </div>
        """

    # Table 닫기
    html_content += """
            </td>
        </tr>
    </table>
    <div style="margin-bottom: 10px;"></div>
    """
    
    return html_content

def format_result_message(auth, result, text):
    """
    결과 상태에 따른 툴팁 메시지 포맷팅
    """
    if result == "PASS":
        return f"{auth}\n\nResult: PASS\n{text}\n"
    elif result == "진행중":
        return f"{auth}\n\nStatus: {text}\n"
    else:
        return f"{auth}\n\nResult: FAIL\nResult details:\n{text}\n"

def get_result_icon_path(result, img_pass, img_fail, img_none):
    """
    결과 상태에 따른 아이콘 경로 반환
    """
    if result == "PASS":
        return img_pass
    elif result == "FAIL":
        return img_fail
    return img_none

