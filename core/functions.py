import requests
from json_checker import Checker, OptionalKey   # 커스텀 라이브러리 아니고, venv에 깔려있는 공식 라이브러리 (착각x)
from core.json_checker_new import data_finder, field_finder, do_checker, timeout_field_finder
from fpdf import FPDF
import sys
import os
import json
#from charset_normalizer import md__mypyc  # A library that helps you read text from an unknown charset encoding
from spec.video.videoRequest import *
from spec.bio.bioRequest import *
from spec.security.securityRequest import *
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

# pass/fail 판별
def json_check_(schema, data, flag):
    all_field, opt_field = field_finder(schema)
    all_data = data_finder(data)
    return do_checker(all_field, all_data, opt_field, flag)


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

    if type_ == "video":
        paths = videoMessages
        for cnt, path in enumerate(paths):
            path_req = _p(type_, path, "request")
            path_res = _p(type_, path, "response")
            videoInMessage.append(set_message(path_req))
            videoOutMessage.append(set_message(path_res))

    elif type_ == "bio":
        paths = bioMessages
        for cnt, path in enumerate(paths):
            path_req = _p(type_, path, "request")
            path_res = _p(type_, path, "response")
            bioInMessage.append(set_message(path_req))
            bioOutMessage.append(set_message(path_res))

    elif type_ == "security":
        paths = securityMessages
        for cnt, path in enumerate(paths):
            path_req = _p(type_, path, "request")
            path_res = _p(type_, path, "response")
            securityInMessage.append(set_message(path_req))
            securityOutMessage.append(set_message(path_res))

    return True

