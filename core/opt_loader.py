"""
OPT JSON 로더 모듈
시험 정보와 명세서 데이터를 JSON 파일에서 로드하고 GUI 매핑용 데이터로 변환
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from .functions import resource_path
from core.logger import Logger


class OptLoader:
    """OPT JSON 파일 로더 클래스"""
    
    def __init__(self):
        self.test_requests_data = None
        self.specification_data = None
        
    def load_opt_json(self, file_path: str) -> Dict:
        """
        OPT JSON 파일을 로드합니다.
        
        Args:
            file_path: JSON 파일 경로
            
        Returns:
            로드된 JSON 데이터 (dict)
            
        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            json.JSONDecodeError: JSON 파싱 오류
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"OPT JSON 파일을 찾을 수 없습니다: {file_path}")
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # JSON 파일 타입 자동 감지
            if "testRequest" in data:
                self.test_requests_data = data
                Logger.info(f"시험 요청 데이터 로드 완료")
            elif "specification" in data:
                self.specification_data = data
                Logger.info(f"명세서 데이터 로드 완료")
                
            return data
            
        except FileNotFoundError as e:
            Logger.error(f"파일 오류: {e}")
            raise
        except json.JSONDecodeError as e:
            Logger.error(f"JSON 파싱 오류: {e}")
            raise
        except Exception as e:
            Logger.error(f"예상치 못한 오류: {e}")
            raise
    
    def parse_test_info(self, test_request_data: Dict) -> Dict:
        """
        시험 요청 데이터에서 GUI 매핑용 시험 정보를 추출합니다.
        
        Args:
            test_request_data: testRequest JSON 데이터
            
        Returns:
            GUI 매핑용 시험 정보 딕셔너리
        """
        if not test_request_data or "testRequest" not in test_request_data:
            return {}

        # 시험 요청 데이터 사용
        first_request = test_request_data["testRequest"]
        evaluation_target = first_request.get("evaluationTarget", {})
        test_group = first_request.get("testGroup", {})
        
        test_info = {
            # 시험 기본 정보
            "company_name": evaluation_target.get("companyName", ""),
            "product_name": evaluation_target.get("productName", ""),
            "version": evaluation_target.get("version", ""),    
            "model_name": evaluation_target.get("modelName", ""),
            
            "test_category": test_group.get("testCategory", ""),
            "target_system": test_group.get("targetSystem", []),
            "test_name": test_group.get("name", ""),
            "test_range": test_group.get("testRange", ""),
            
        }
        
        return test_info
    
    
    def get_gui_mapping_data(self, file_path: str) -> Tuple[Dict, Dict]:
        """
        OPT JSON 파일을 로드하고 GUI 매핑용 데이터를 반환합니다.
        
        Args:
            file_path: OPT JSON 파일 경로
            
        Returns:
            (test_info, auth_info) 튜플
        """
        try:
            data = self.load_opt_json(file_path)
            
            test_info = {}
            auth_info = {}
            
            if "testRequest" in data:
                test_info = self.parse_test_info(data)
                
            if "specification" in data:
                auth_info = self.parse_auth_info(data)
                
            return test_info, auth_info
            
        except Exception as e:
            Logger.error(f"GUI 매핑 데이터 생성 실패: {e}")
            return {}, {}
    
    def validate_opt_json(self, data: Dict) -> bool:
        """
        OPT JSON 데이터의 유효성을 검증합니다.
        
        Args:
            data: 검증할 JSON 데이터
            
        Returns:
            유효성 여부 (bool)
        """
        if not isinstance(data, dict):
            return False
            
        # 시험 요청 데이터 검증
        if "testRequest" in data:
            test_request = data["testRequest"]
            if not isinstance(test_request, dict):
                return False

            # 필수 필드 검증
            required_fields = ["id", "evaluationTarget", "testGroup"]
            first_request = test_request
            
            for field in required_fields:
                if field not in first_request:
                    return False
                    
        # 명세서 데이터 검증
        elif "specification" in data:
            spec = data["specification"]
            required_fields = ["id", "name", "version", "steps"]
            
            for field in required_fields:
                if field not in spec:
                    return False
                    
        else:
            return False  # 알 수 없는 데이터 구조
            
        return True
    
    def get_available_test_specs(self) -> List[str]:
        """
        사용 가능한 시험 명세 ID 목록을 반환합니다.
        
        Returns:
            시험 명세 ID 리스트
        """
        if self.test_requests_data and "testRequest" in self.test_requests_data:
            first_request = self.test_requests_data["testRequest"]
            test_group = first_request.get("testGroup", {})
            return test_group.get("testSpecIds", [])
        return []