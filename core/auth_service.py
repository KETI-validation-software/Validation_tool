"""
인증 서비스 모듈
- 인증 정보 추출 및 업데이트
- Data_request.py의 Authentication 관리
"""

import sys
import os
import re


class AuthService:
    """인증 관련 로직을 담당하는 서비스 클래스"""

    def __init__(self):
        pass

    def get_authentication_credentials(self, spec_id):
        """
        플랫폼 검증 시 spec_id로부터 Authentication 인증 정보를 추출

        Args:
            spec_id: 스펙 ID (예: 'cmgvieyak001b6cd04cgaawmm')

        Returns:
            tuple: (user_id, password) 또는 (None, None) if not found

        Example:
            >>> user_id, password = self.get_authentication_credentials('cmgvieyak001b6cd04cgaawmm')
            >>> # Returns: ('kisa', 'kisa_k1!2@')
        """
        try:
            from core.validation_registry import get_validation_rules

            # Authentication API의 검증 규칙 가져오기 (direction='in'은 플랫폼→시스템 요청)
            rules = get_validation_rules(spec_id, 'Authentication', 'in')

            if not rules:
                print(f"[WARNING] spec_id={spec_id}에 대한 Authentication 검증 규칙을 찾을 수 없습니다.")
                return None, None

            # userID 추출
            user_id = None
            if 'userID' in rules:
                user_id_rule = rules['userID']
                allowed_values = user_id_rule.get('allowedValues', [])
                if allowed_values and len(allowed_values) > 0:
                    user_id = allowed_values[0]

            # userPW 추출
            password = None
            if 'userPW' in rules:
                user_pw_rule = rules['userPW']
                allowed_values = user_pw_rule.get('allowedValues', [])
                if allowed_values and len(allowed_values) > 0:
                    password = allowed_values[0]

            if user_id and password:
                print(f"[INFO] Authentication 인증 정보 추출 완료: user_id={user_id}")
                return user_id, password
            else:
                print(f"[WARNING] Authentication 규칙에서 userID 또는 userPW를 찾을 수 없습니다.")
                return None, None

        except Exception as e:
            print(f"[ERROR] Authentication 인증 정보 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def get_authentication_from_data_request(self, spec_id):
        """
        물리보안(시스템 검증) 시 Data_request.py에서 Authentication 인증 정보를 추출
        (통합플랫폼과 동일한 방식: 특정 spec_id의 Authentication에서 가져옴)

        Args:
            spec_id: 스펙 ID (예: 'cmii7wfuf006i8z1tcds6q69g')

        Returns:
            tuple: (user_id, password) 또는 (None, None) if not found
        """
        try:
            # 파일 경로 결정
            if getattr(sys, 'frozen', False):
                # PyInstaller 환경
                exe_dir = os.path.dirname(sys.executable)
                file_path = os.path.join(exe_dir, 'spec', 'Data_request.py')
            else:
                # 개발 환경
                base_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(os.path.dirname(base_dir), 'spec', 'Data_request.py')

            print(f"[DATA_REQUEST] 파일 경로: {file_path}")
            print(f"[DATA_REQUEST] spec_id: {spec_id}")

            if not os.path.exists(file_path):
                print(f"[WARNING] Data_request.py 파일이 존재하지 않음: {file_path}")
                return None, None

            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 특정 {spec_id}_Authentication_in_data 딕셔너리에서 값 추출
            var_name = f"{spec_id}_Authentication_in_data"

            # 패턴: {spec_id}_Authentication_in_data = { "userID": "...", "userPW": "..." }
            pattern = rf'{re.escape(var_name)}\s*=\s*\{{[^}}]*"userID"\s*:\s*"([^"]*)"[^}}]*"userPW"\s*:\s*"([^"]*)"[^}}]*\}}'

            match = re.search(pattern, content)

            if match:
                user_id = match.group(1)
                password = match.group(2)
                print(f"[INFO] Data_request.py에서 인증 정보 추출 완료: {var_name} -> user_id={user_id}")
                return user_id, password
            else:
                # userPW가 userID 앞에 있는 경우도 체크
                pattern_reverse = rf'{re.escape(var_name)}\s*=\s*\{{[^}}]*"userPW"\s*:\s*"([^"]*)"[^}}]*"userID"\s*:\s*"([^"]*)"[^}}]*\}}'
                match_reverse = re.search(pattern_reverse, content)

                if match_reverse:
                    password = match_reverse.group(1)
                    user_id = match_reverse.group(2)
                    print(f"[INFO] Data_request.py에서 인증 정보 추출 완료: {var_name} -> user_id={user_id}")
                    return user_id, password

                print(f"[WARNING] {var_name}에서 userID/userPW를 찾을 수 없음")
                return None, None

        except Exception as e:
            print(f"[ERROR] Data_request.py 인증 정보 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def update_data_request_authentication(self, spec_id, user_id, password):
        """
        물리보안(시스템 검증) 시 Data_request.py의 모든 Authentication 인증 정보를 업데이트

        Args:
            spec_id: 스펙 ID (사용하지 않음, 모든 Authentication 업데이트)
            user_id: 새로운 userID
            password: 새로운 userPW

        Returns:
            bool: 성공 여부
        """
        try:
            # 파일 경로 결정
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                file_path = os.path.join(exe_dir, 'spec', 'Data_request.py')
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(os.path.dirname(base_dir), 'spec', 'Data_request.py')

            print(f"[UPDATE_DATA_REQUEST] 파일 경로: {file_path}")
            print(f"[UPDATE_DATA_REQUEST] 새 userID: {user_id}")

            if not os.path.exists(file_path):
                print(f"[ERROR] Data_request.py 파일이 존재하지 않음: {file_path}")
                return False

            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 모든 {any_spec_id}_Authentication_in_data 딕셔너리 패턴 찾기 및 교체
            # 패턴: {spec_id}_Authentication_in_data = { ... }
            # [a-zA-Z0-9]+ 로 모든 spec_id를 매칭
            pattern = r'([a-zA-Z0-9]+_Authentication_in_data\s*=\s*)\{[^}]*\}'

            # 매칭되는 모든 패턴 찾기
            matches = re.findall(r'([a-zA-Z0-9]+)_Authentication_in_data\s*=', content)
            print(f"[UPDATE_DATA_REQUEST] 발견된 Authentication 변수: {len(matches)}개")

            if not matches:
                print(f"[ERROR] Authentication_in_data 패턴을 찾을 수 없음")
                return False

            # 각 매칭에 대해 교체 함수
            def replace_auth(match):
                var_prefix = match.group(1)  # {spec_id}_Authentication_in_data =
                return f'{var_prefix}{{\n    "userID": "{user_id}",\n    "userPW": "{password}"\n}}'

            # 모든 패턴 교체
            new_content = re.sub(pattern, replace_auth, content)

            # 파일 쓰기
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"[INFO] Data_request.py 업데이트 완료 - {len(matches)}개의 Authentication 업데이트됨")
            return True

        except Exception as e:
            print(f"[ERROR] Data_request.py 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
