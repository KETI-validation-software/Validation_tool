import requests
from json_checker import Checker, OptionalKey   # 커스텀 라이브러리 아니고, venv에 깔려있는 공식 라이브러리 (착각x)
from core.json_checker_new import data_finder, field_finder, do_checker, timeout_field_finder, do_semantic_checker, extract_validation_rules
from fpdf import FPDF
import sys
import os
import json
#from charset_normalizer import md__mypyc  # A library that helps you read text from an unknown charset encoding
# from spec.bio.bioRequest import *
# from spec.security.securityRequest import *
from lxml import etree
from PyQt5.QtWidgets import QMessageBox


opt_checker = Checker((OptionalKey))
int_checker = Checker(int)
str_checker = Checker(str)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# pass/fail 판별 -> 여기에 연동 맥락 ㄱㅓㅁ증 추가하기
def json_check_(schema, data, flag, validation_rules=None, reference_context=None):
    """
    schema: 구조 검증용 응답 스키마
    data:   실제 응답 데이터(dict 권장)
    flag:   옵션(기존 그대로)
    validation_rules: (선택) 의미 검증 규칙 dict
        - 예: validation_request.py 의 각 *_in_validation 중 해당 API 것
        - 없으면 의미 검증을 건너뜀
    reference_context: (선택) 다른 엔드포인트 응답 사전
        - 예: {"/CameraProfiles": <CameraProfiles 응답 dict>, ...}
    반환: (result, error_msg, correct_cnt, error_cnt)
        - result: 구조&의미 최종 결과 ("PASS"/"FAIL")
        - error_msg: 구조/의미 에러 메시지 합본 (없으면 "오류 없음")
        - correct_cnt: 구조 통과 필드 + 의미 통과 필드
        - error_cnt:   구조 실패 필드 + 의미 실패 필드
    """
    try:
        print("~~~~~~~~~~~~ 구조검증 시작 ~~~~~~~~~~~~ json_check_ 시작")

        # 1) 구조 검증 준비
        all_field, opt_field = field_finder(schema)
        print(f"[json_check] field_finder 완료: all_field={len(all_field)}, opt_field={len(opt_field)}")

        all_data = data_finder(data)
        print(f"[json_check] data_finder 완료: all_data={len(all_data)}")

        # 2) 구조 검증 수행
        struct_result, struct_error_msg, struct_correct_cnt, struct_error_cnt = do_checker(
            all_field, all_data, opt_field, flag
        )
        print(f"[json_check] do_checker 완료: result={struct_result}, "
              f"correct={struct_correct_cnt}, error={struct_error_cnt}")

        # 구조 FAIL이면 즉시 반환
        if struct_result != "PASS":
            return struct_result, (struct_error_msg or "구조 검증 실패"), struct_correct_cnt, struct_error_cnt

        # 3) (선택) 의미 검증 수행
        sem_result = "PASS"
        sem_error_msg = ""
        sem_correct_cnt = 0
        sem_error_cnt = 0

        if validation_rules:
            print("++++++++++ 구조 PASS → 의미 검증 시작 ++++++++++")
            # from core.json_checker_new import do_semantic_checker, extract_validation_rules

            # validation_rules는 이미 “점 포함 키” 기반 dict일 수도 있고(예: {"camList.camID": {...}})
            # 중첩 dict에서 평탄화가 필요하면 extract_validation_rules 사용
            if any("." in k for k in validation_rules.keys()):
                rules_dict = validation_rules  # 이미 평탄화된 형태
            else:
                rules_dict = extract_validation_rules(validation_rules)

            sem_result, sem_error_msg, sem_correct_cnt, sem_error_cnt = do_semantic_checker(
                rules_dict, data, reference_context=reference_context
            )
            print(f"[functions.py의 json_check_] 완료: result={sem_result}, correct={sem_correct_cnt}, error={sem_error_cnt}")
        else:
            print("[functions.py의 json_check_] 규칙(validation_rules) 없음 → 의미 검증 건너뜀")

        # 4) 결과 합산/결정
        final_result = "PASS" if (struct_result == "PASS" and sem_result == "PASS") else "FAIL"

        # 메시지 병합(가독성)
        merged_msg_parts = []
        if struct_error_msg:
            merged_msg_parts.append(f"[구조] {struct_error_msg}")
        if validation_rules:
            if sem_error_msg and sem_result != "PASS":
                merged_msg_parts.append(f"[의미] {sem_error_msg}")
            elif not sem_error_msg:
                merged_msg_parts.append("[의미] 오류 없음")
        error_msg = "\n".join(merged_msg_parts) if merged_msg_parts else "오류 없음"

        # 카운트 합산
        correct_cnt = (struct_correct_cnt or 0) + (sem_correct_cnt or 0)
        error_cnt   = (struct_error_cnt or 0)   + (sem_error_cnt or 0)

        return final_result, error_msg, correct_cnt, error_cnt

    except Exception as e:
        print(f"[json_check] 에러: {e}")
        import traceback
        traceback.print_exc()
        raise



class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def save_result(str_in, path):
    font_file = resource_path('NanumGothic.ttf')

    font_type = 'NanumGothic'
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font(font_type, '', font_file, uni=True)
        # header
        pdf.set_font(font_type, '', 10)

        # content
        pdf.set_font(font_type, '', 10)
        pdf.multi_cell(w=0, h=10, txt=str_in)

        pdf.output(path, 'F')
    except Exception as err:
        print(err)


def set_auth(file=None):
    """
    CONSTANTS.py에서 인증 정보를 읽어옵니다.
    file 매개변수는 하위 호환성을 위해 유지하지만 사용하지 않습니다.
    """
    try:
        # CONSTANTS.py에서 인증 정보 가져오기
        from config.CONSTANTS import auth_type, auth_info

        info = "None"
        info2 = ["", ""]  # 기본값을 2개 요소로 초기화

        if auth_type == "Bearer Token":
            info = auth_info  # Bearer Token인 경우 토큰 문자열
        elif auth_type == "Digest Auth":
            # Digest Auth인 경우 "id,pass" 형태를 분리
            if "," in auth_info:
                parts = auth_info.split(",")
                info2 = [parts[0], parts[1] if len(parts) > 1 else ""]
            else:
                info2 = [auth_info, ""]  # 기본값

        return info, info2

    except ImportError as e:
        # CONSTANTS.py를 찾을 수 없는 경우
        print(f"CONSTANTS.py를 찾을 수 없습니다: {e}")
        return "None", ["", ""]  # 2개 요소 보장
    except Exception as e:
        # 기타 오류
        print(f"인증 정보 로드 중 오류: {e}")
        return "None", ["", ""]  # 2개 요소 보장


def set_message(path_):
    try:
        with open(resource_path(path_), 'r', encoding="UTF-8") as fp:
            json_data = json.load(fp)
            message = json_data
        return message

    except json.JSONDecodeError as verr:
        box = QMessageBox()
        box.setIcon(QMessageBox.Critical)
        box.setText("Error Message: "+path_+" 을 확인하세요")
        box.setInformativeText(str(verr))
        box.setWindowTitle("Error")
        box.exec_()
        return {}
    except Exception as e:
        print(e)
        return {}


def json_to_data(type_):
    def _p(t, name, kind):  # kind: "request" | "response"
        return os.path.join("spec", t, f"{name}_{kind}.json")


    # elif type_ == "bio":
    #     paths = bioMessages
    #     for cnt, path in enumerate(paths):
    #         path_req = _p(type_, path, "request")
    #         path_res = _p(type_, path, "response")
    #         bioInMessage.append(set_message(path_req))
    #         bioOutMessage.append(set_message(path_res))

    # elif type_ == "security":
    #     paths = securityMessages
    #     for cnt, path in enumerate(paths):
    #         path_req = _p(type_, path, "request")
    #         path_res = _p(type_, path, "response")
    #         securityInMessage.append(set_message(path_req))
    #         securityOutMessage.append(set_message(path_res))

    return True

