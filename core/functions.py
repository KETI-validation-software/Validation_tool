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


def spec_path(system: str, *parts) -> str:
    """
    spec/<system>/... 경로를 절대경로로 만들어 반환
    예: spec_path("video", "ReplayURL_request.json")
    """
    return resource_path(os.path.join("spec", system, *parts))

def spec_json(system: str, filename: str, mode="r", encoding="utf-8"):
    """
    spec/<system>/<filename> 를 열어서 파일 객체를 반환
    with spec_json("video", "ReplayURL_request.json") as f: ...
    """
    return open(spec_path(system, filename), mode, encoding=encoding)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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


def set_auth(file):
    tree = etree.parse(file)
    root = tree.getroot()
    info = "None"
    info2 = []

    for child in root:
        if child.attrib['type'] == 'Bearer Token':
            for a in child[1:]:
                if a.text != "None" or a.text is not None:
                    info = a.text

        if child.attrib['type'] == 'Digest Auth':
            for a in child[1:]:
                info2.append(a.text)

    return info, info2


def set_message(path_):
    try:
        with open(path_, 'r', encoding="UTF-8") as fp:
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
    if type_ == "video":
        paths = videoMessages
        for cnt, path in enumerate(paths):
            path_req = type_ + "/" + path + "_request.json"
            path_res = type_ + "/" + path + "_response.json"
            videoInMessage[cnt] = set_message(path_req)
            videoOutMessage[cnt] = set_message(path_res)

    elif type_ == "bio":
        paths = bioMessages
        for cnt, path in enumerate(paths):
            path_req = type_ + "/" + path + "_request.json"
            path_res = type_ + "/" + path + "_response.json"
            bioInMessage[cnt] = set_message(path_req)
            bioOutMessage[cnt] = set_message(path_res)

    elif type_ == "security":
        paths = securityMessages
        for cnt, path in enumerate(paths):
            path_req = type_ + "/" + path + "_request.json"
            path_res = type_ + "/" + path + "_response.json"
            securityInMessage[cnt] = set_message(path_req)
            securityOutMessage[cnt] = set_message(path_res)

    return True
