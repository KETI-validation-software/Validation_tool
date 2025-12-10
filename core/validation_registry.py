# core/validation_registry.py

# 검증 규칙 레지스트리 빌드 및 조회 (개선 버전)

import importlib
import re
from functools import lru_cache
from types import ModuleType
import importlib
from typing import Dict, Any, Optional


# 변수명 규칙: {specId}_{apiName}_{in|out}_validation
_PATTERN = re.compile(r'^(?P<spec>[^_]+)_(?P<api>.+)_(?P<dir>in|out)_validation$')


def _collect_from_module(mod: ModuleType) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    모듈에서 검증 규칙 수집
    
    Returns:
        {
            'spec_id': {
                'in': {'API1': {...}, 'API2': {...}},
                'out': {'API1': {...}, 'API2': {...}}
            }
        }
    """
    registry: Dict[str, Dict[str, Dict[str, Any]]] = {}
    
    for name, obj in vars(mod).items():
        if not isinstance(name, str) or not isinstance(obj, dict):
            continue
            
        m = _PATTERN.match(name)
        if not m:
            continue
            
        spec = m.group('spec')
        api = m.group('api')
        direction = m.group('dir')  # 'in' | 'out'
        
        # 레지스트리 구조 생성
        reg_spec = registry.setdefault(spec, {})
        reg_dir = reg_spec.setdefault(direction, {})
        reg_dir[api] = obj
    
    return registry


@lru_cache(maxsize=16)
def build_validation_registry(
    request_module_path: str = "spec.validation_request",
    response_module_path: str = "spec.validation_response",
) -> Dict[str, Dict[str, Dict[str, Any]]]:

    """
    검증 규칙 레지스트리 빌드

    구조:
        - Validation_request.py: _in_validation (플랫폼→시스템 요청)
        - validation_response.py: _out_validation (시스템→플랫폼 응답)

    Returns:
        {
            'spec_id': {
                'in': {'API1': {...}},   # 요청 검증 규칙
                'out': {'API2': {...}}    # 응답 검증 규칙
            }
        }
    """
    import sys
    import os

    reg: Dict[str, Dict[str, Dict[str, Any]]] = {}

    # 각 모듈에서 규칙 수집
    for path in (request_module_path, response_module_path):
        try:
            # PyInstaller 환경에서는 importlib.util로 외부 파일 명시적 로드
            if getattr(sys, 'frozen', False):
                import importlib.util

                exe_dir = os.path.dirname(sys.executable)

                # 모듈 경로를 파일 경로로 변환 (예: "spec.validation_request" -> "validation_request.py")
                module_name = path.split('.')[-1]
                file_path = os.path.join(exe_dir, 'spec', f'{module_name}.py')

                print(f"[VALIDATION REGISTRY] 외부 파일 로드 시도: {file_path}")
                print(f"[VALIDATION REGISTRY] 파일 존재 여부: {os.path.exists(file_path)}")

                if not os.path.exists(file_path):
                    print(f"[WARNING] 파일이 존재하지 않음: {file_path}")
                    continue

                # importlib.util로 명시적 로드
                spec = importlib.util.spec_from_file_location(path, file_path)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[path] = mod
                spec.loader.exec_module(mod)

                print(f"[VALIDATION REGISTRY] ✅ 외부 파일 로드 완료: {file_path}")
                print(f"[VALIDATION REGISTRY] 모듈 __file__: {mod.__file__}")
            else:
                # 일반 환경에서는 기존 import 방식 사용
                import importlib
                mod = importlib.import_module(path)

            part = _collect_from_module(mod)

            # 레지스트리 병합
            for spec, dmap in part.items():
                reg.setdefault(spec, {})
                for direction, amap in dmap.items():
                    reg[spec].setdefault(direction, {})
                    reg[spec][direction].update(amap)

        except ImportError as e:
            print(f"[WARNING] 모듈 로드 실패: {path} - {e}")
            import traceback
            traceback.print_exc()
            continue
        except Exception as e:
            print(f"[ERROR] 예상치 못한 오류: {path} - {e}")
            import traceback
            traceback.print_exc()
            continue

    return reg


def clear_validation_cache():
    """
    레지스트리 캐시 클리어

    Validation_request.py 또는 validation_response.py가 업데이트된 후 호출하여
    다음 조회 시 새로운 데이터로 레지스트리를 다시 빌드하도록 함
    """
    build_validation_registry.cache_clear()
    print("[INFO] validation_registry 캐시가 클리어되었습니다.")


def get_validation_rules(
    spec_id: str,
    api_name: str,
    direction: str,
    request_module_path: str = "spec.validation_request",
    response_module_path: str = "spec.validation_response",
) -> Dict[str, Any]:
    """
    검증 규칙 반환
    
    Args:

        spec_id: 스펙 ID (예: 'cmgvieyak001b6cd04cgaawmm')
        api_name: API 이름 (예: 'StreamURLs', 'StoredVideoInfos')
        direction: 검증 방향
            - "in": 플랫폼→시스템 요청 검증
                   (platformVal에서 사용, Validation_request.py)
            - "out": 시스템→플랫폼 응답 검증
                    (systemVal에서 사용, validation_response.py)
        request_module_path: 요청 검증 규칙 모듈 경로
        response_module_path: 응답 검증 규칙 모듈 경로
    
    Returns:
        검증 규칙 딕셔너리 (없으면 빈 dict)
        
    Example:
        >>> # platformVal에서 플랫폼→시스템 요청 검증
        >>> rules = get_validation_rules(
        ...     spec_id='cmgvieyak001b6cd04cgaawmm',
        ...     api_name='StreamURLs',
        ...     direction='in'
        ... )
        >>> # systemVal에서 시스템→플랫폼 응답 검증
        >>> rules = get_validation_rules(
        ...     spec_id='cmgyv3rzl014nvsveidu5jpzp',
        ...     api_name='StoredVideoInfos',
        ...     direction='out'
        ... )
    """
    # 입력 정규화
    direction = direction.lower().strip()
    if direction not in ("in", "out"):
        raise ValueError(f"direction must be 'in' or 'out', got: {direction}")
    
    # 레지스트리 빌드
    reg = build_validation_registry(request_module_path, response_module_path)
    
    # 디버그 로그 (개선된 형태)
    print(f"\n[DEBUG] 검증 규칙 조회:")
    print(f"  - Spec ID: {spec_id}")
    print(f"  - API Name: {api_name}")
    print(f"  - Direction: {direction} ({'플랫폼→시스템' if direction == 'in' else '시스템→플랫폼'})")
    
    if spec_id not in reg:
        print(f"  [경고] Spec ID '{spec_id}'를 레지스트리에서 찾을 수 없음")
        print(f"  사용 가능한 Spec ID: {list(reg.keys())}")
        return {}
    
    if direction not in reg[spec_id]:
        print(f"  [경고] Direction '{direction}'을 찾을 수 없음")
        print(f"  '{spec_id}'의 사용 가능한 방향: {list(reg[spec_id].keys())}")
        return {}
    
    if api_name not in reg[spec_id][direction]:
        print(f"  [경고] API '{api_name}'을 찾을 수 없음")
        print(f"  '{spec_id}/{direction}'의 사용 가능한 API: {list(reg[spec_id][direction].keys())}")
        return {}
    
    rules = reg[spec_id][direction][api_name]
    print(f"  ✓ 검증 규칙 발견: {len(rules)}개 필드")
    return rules


def list_available_validations(
    request_module_path: str = "spec.validation_request",
    response_module_path: str = "spec.validation_response",
) -> Dict[str, Dict[str, list]]:
    """
    사용 가능한 모든 검증 규칙 목록 반환 (디버깅용)
    
    Returns:
        {
            'spec_id': {
                'in': ['API1', 'API2'],
                'out': ['API3', 'API4']
            }
        }
    """
    reg = build_validation_registry(request_module_path, response_module_path)
    result = {}
    
    for spec_id, directions in reg.items():
        result[spec_id] = {}
        for direction, apis in directions.items():
            result[spec_id][direction] = list(apis.keys())
    
    return result


def validate_registry_structure(
    request_module_path: str = "spec.validation_request",
    response_module_path: str = "spec.validation_response",
) -> bool:
    """
    레지스트리 구조 검증 (단위 테스트용)
    
    Returns:
        True if valid, False otherwise
    """
    try:
        reg = build_validation_registry(request_module_path, response_module_path)
        
        if not reg:
            print("[ERROR] 레지스트리가 비어있음")
            return False
        
        for spec_id, directions in reg.items():
            if not isinstance(directions, dict):
                print(f"[ERROR] {spec_id}의 directions가 dict가 아님")
                return False
            
            for direction, apis in directions.items():
                if direction not in ("in", "out"):
                    print(f"[ERROR] 잘못된 direction: {direction}")
                    return False
                
                if not isinstance(apis, dict):
                    print(f"[ERROR] {spec_id}/{direction}의 apis가 dict가 아님")
                    return False
                
                for api_name, rules in apis.items():
                    if not isinstance(rules, dict):
                        print(f"[ERROR] {spec_id}/{direction}/{api_name}의 rules가 dict가 아님")
                        return False
        
        print("[OK] 레지스트리 구조 검증 성공")
        return True
        
    except Exception as e:
        print(f"[ERROR] 검증 중 예외 발생: {e}")
        return False
