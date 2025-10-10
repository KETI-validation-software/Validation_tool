"""
VideoRequest 파일 생성기
JSON 파일에서 데이터를 추출하여 videoRequest_request.py와 videoRequest_response.py 파일을 생성합니다.
"""
import json
import os
from typing import Dict, List, Any, Union
from .functions import resource_path


class VideoRequestGenerator:
    """JSON 데이터를 기반으로 videoRequest 파일을 생성하는 클래스"""

    def __init__(self):
        pass

    def extract_endpoint_data(self, step: Dict, data_type: str) -> Dict[str, Any]:
        """
        각 step에서 endpoint 데이터를 추출합니다.

        Args:
            step: API step 정보
            data_type: "request" (requestData 사용) 또는 "response" (responseData 사용)

        Returns:
            추출된 데이터 정보
        """
        api = step.get("detail", {}).get("step", {}).get("api", {})
        endpoint = api.get("endpoint", "")

        # endpoint에서 변수명 생성 (/ 제거)
        if endpoint.startswith("/"):
            endpoint_name = endpoint[1:]
        else:
            endpoint_name = endpoint

        # data_type에 따라 데이터 소스와 suffix 결정
        if data_type == "request":
            # Request 버튼: responseData를 가져와서 _out_data 생성
            data_source = api.get("request", {})
            suffix = "_in_data"
        else:  # response
            # Response 버튼: requestData를 가져와서 _in_data 생성
            data_source = api.get("response", {})
            suffix = "_out_data"

        variable_name = f"{endpoint_name}{suffix}"

        # 데이터가 없으면 빈 딕셔너리
        if not data_source:
            data_content = {}
        else:
            data_content = dict(data_source)  # 복사본 생성

        return {
            "name": variable_name,
            "content": data_content,
            "endpoint": endpoint_name
        }

    def format_data_content(self, content: Union[Dict, List, str, int, float, bool]) -> str:
        """데이터 내용을 Python 코드 문자열로 포맷팅합니다."""
        if isinstance(content, dict):
            if not content:
                return "{}"

            lines = ["{"]
            items = list(content.items())
            for i, (key, value) in enumerate(items):
                formatted_value = self.format_data_content(value)
                comma = "," if i < len(items) - 1 else ""
                lines.append(f'    "{key}": {formatted_value}{comma}')
            lines.append("}")
            return "\n".join(lines)

        elif isinstance(content, list):
            if not content:
                return "[]"

            lines = ["["]
            for i, item in enumerate(content):
                formatted_item = self.format_data_content(item)
                comma = "," if i < len(content) - 1 else ""
                # 들여쓰기 추가
                if "\n" in formatted_item:
                    indented_item = "\n".join("    " + line for line in formatted_item.split("\n"))
                    lines.append(f"    {indented_item}{comma}")
                else:
                    lines.append(f"    {formatted_item}{comma}")
            lines.append("]")
            return "\n".join(lines)

        elif isinstance(content, str):
            return f'"{content}"'
        elif isinstance(content, (int, float)):
            return str(content)
        elif isinstance(content, bool):
            return "True" if content else "False"
        else:
            return f'"{str(content)}"'

    def create_video_request_file(self, json_path: str, file_type: str, output_path: str = None, spec_prefix: str = "video") -> str:
        """
        JSON 파일로부터 videoRequest 파일을 생성합니다.

        Args:
            json_path: 입력 JSON 파일 경로
            file_type: "request" 또는 "response"
            output_path: 출력 파일 경로
            spec_prefix: 변수명 접두사 (예: "spec-001", "spec-0011")

        Returns:
            생성된 파일 경로
        """
        if not output_path:
            if file_type == "request":
                output_path = "spec/video/videoRequest_request.py"
            else:  # response
                output_path = "spec/video/videoRequest_response.py"

        # JSON 파일 로드
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        specification = data.get("specification", {})
        spec_id = specification.get("id", "")
        steps = specification.get("steps", [])

        # WebHook 파일인지 확인
        is_webhook = "WebHook" in json_path

        # 파일 내용 생성
        content = f"# {file_type} 모드\n\n"

        # 각 step별로 데이터 생성
        data_names = []
        endpoint_names = []
        webhook_data = []

        for step in steps:
            step_id = step.get("id", "")
            api = step.get("api", {})
            endpoint = api.get("endpoint", "")
            settings = api.get("settings", {})
            trans_protocol = settings.get("transProtocol", {})

            # 콜백 스텝 (endpoint가 없고 urlKey만 있는 스텝)은 건너뛰기
            if not endpoint and api.get("urlKey"):
                continue

            data_info = self.extract_endpoint_data(step, file_type)
            data_name = data_info["name"]
            data_content = data_info["content"]
            endpoint_name = data_info["endpoint"]

            # 주석 추가
            content += f"# {endpoint_name}\n"

            # 데이터 변수 생성
            formatted_content = self.format_data_content(data_content)
            content += f"{data_name} = {formatted_content}\n\n"

            # 리스트를 위해 이름 저장
            data_names.append(data_name)

            # WebHook 모드이고 transProtocol.mode가 "WebHook"인 경우
            if is_webhook and trans_protocol.get("mode") == "WebHook":
                # 해당 스텝과 쌍을 이루는 콜백 스텝 찾기
                callback_step_id = f"{step_id}-1"
                callback_step = None

                for s in steps:
                    if s.get("id") == callback_step_id:
                        callback_step = s
                        break

                if callback_step:
                    webhook_data_info = self._generate_webhook_data(callback_step, endpoint_name, file_type)
                    if webhook_data_info:
                        webhook_data.append(webhook_data_info)
            endpoint_names.append(endpoint_name)

        # WebHook 전용 데이터들 추가
        webhook_data_names = []
        for webhook_info in webhook_data:
            content += webhook_info + "\n"
            # WebHook 데이터 이름 추출
            lines = webhook_info.strip().split('\n')
            for line in lines:
                if ' = {' in line or ' = [' in line:
                    data_name = line.split(' = ')[0].strip()
                    webhook_data_names.append(data_name)
                    break

        # 메시지 리스트 생성 (steps 순서대로) - spec_prefix 사용
        if file_type == "request":
            # Request 파일: responseData로 _out_data 생성했으므로 outData
            content += f"# {spec_prefix} 출력 메시지 리스트\n"
            content += f"{spec_prefix}_outData = [\n"
        else:  # response
            # Response 파일: requestData로 _in_data 생성했으므로 inData
            content += f"# {spec_prefix} 입력 메시지 리스트\n"
            content += f"{spec_prefix}_inData = [\n"

        for name in data_names:
            content += f"    {name},\n"
        content += "]\n\n"

        # messages 리스트 생성 (endpoint) - spec_prefix 사용
        content += f"# {spec_prefix} API endpoint\n"
        content += f"{spec_prefix}_messages = [\n"
        for endpoint in endpoint_names:
            content += f'    "{endpoint}",\n'
        content += "]\n"

        # WebHook 데이터 리스트 생성 (WebHook) - spec_prefix 사용
        if is_webhook and webhook_data_names:
            content += f"\n# {spec_prefix} WebHook\n"
            content += f"{spec_prefix}_webhookData = [\n"
            for name in webhook_data_names:
                content += f"    {name},\n"
            content += "]\n"

        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 파일 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def _generate_webhook_data(self, callback_step: Dict, endpoint_name: str, file_type: str) -> str:
        """
        WebHook 콜백 데이터를 생성합니다.

        Args:
            callback_step: 콜백 스텝 정보
            endpoint_name: 앞 스텝의 엔드포인트 이름 (RealtimeVideoEventInfos)
            file_type: "request" 또는 "response"

        Returns:
            WebHook 데이터 코드 문자열
        """
        callback_api = callback_step.get("api", {})

        # file_type에 따라 데이터 소스와 suffix 결정
        if file_type == "request":
            # Request 모드: requestData 사용, _in_data 생성
            data_source_key = "requestData"
            suffix = "_in_data"
        else:  # response
            # Response 모드: responseData 사용, _out_data 생성
            data_source_key = "responseData"
            suffix = "_out_data"

        data_source = callback_api.get(data_source_key, {})
        if not data_source:
            return ""

        # 데이터 변수명 생성 (앞 스텝의 endpoint명 사용)
        data_name = f"WebHook_{endpoint_name}{suffix}"

        # 주석과 데이터 변수 생성
        result = f"# WebHook {endpoint_name}\n"
        formatted_content = self.format_data_content(data_source)
        result += f"{data_name} = {formatted_content}\n"

        return result


def generate_video_request_file(json_path: str, file_type: str, output_path: str = None, spec_prefix: str = "video") -> str:
    """
    편의 함수: JSON 파일로부터 videoRequest 파일을 생성합니다.

    Args:
        json_path: 입력 JSON 파일 경로
        file_type: "request" 또는 "response"
        output_path: 출력 파일 경로
        spec_prefix: 변수명 접두사 (예: "spec-001", "spec-0011")

    Returns:
        생성된 파일 경로
    """
    generator = VideoRequestGenerator()
    return generator.create_video_request_file(json_path, file_type, output_path, spec_prefix)