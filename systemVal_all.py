# 시스템 검증 소프트웨어
# physical security integrated system validation software

import time
import threading
import json
import requests
import sys
import spec
from spec.video.videoRequest import videoMessages, videoOutMessage, videoInMessage
from spec.video.videoSchema import videoInSchema, videoOutSchema
from spec.bio.bioRequest import bioMessages, bioOutMessage, bioInMessage
from spec.bio.bioSchema import  bioInSchema, bioOutSchema
from spec.security.securityRequest import securityMessages, securityOutMessage, securityInMessage
from spec.security.securitySchema import securityInSchema, securityOutSchema
from urllib.parse import urlparse
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFontDatabase, QFont
from PyQt5.QtCore import *
from api.webhook_api import WebhookThread
from core.functions import BearerAuth, json_check_, field_finder, save_result, resource_path, set_auth, json_to_data, timeout_field_finder
from requests.auth import HTTPDigestAuth
import config.CONSTANTS as CONSTANTS
import traceback

#  from charset_normalizer import md__mypyc  # A library that helps you read text from an unknown charset encoding
import warnings
warnings.filterwarnings('ignore')


class CustomDialog(QDialog):  # popup window for validation result
    def __init__(self, dmsg, dstep):
        super().__init__()
        self.setWindowTitle(dstep)
        self.setGeometry(1600, 500, 400, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.tb = QTextBrowser()
        self.tb.setAcceptRichText(True)
        self.tb.append(dmsg)
        self.layout.addWidget(self.tb)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.exec_()


class MyApp(QWidget):
    def __init__(self, embedded=False):
        super().__init__()
        self.embedded = embedded
        self.webhook_res = None
        self.res = None
        self.radio_check_flag = False
        self.img_pass = resource_path("image/green.png")
        self.img_fail = resource_path("image/red.png")
        self.img_none = resource_path("image/black.png")

        self.flag_opt = True  # functions.py-json_check_ # 필수필드만 확인 False, optional 필드까지 확인 True #seo 추후 맵핑 필요
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_view)
        self.pathUrl = None
        self.auth_type = None
        self.cnt = 0

        self.auth_flag = False
        self.tmp_msg_append_flag = False  # step1이 여러번 적힘 우선 임시 T.T(?)

        self.time_pre = 0
        self.post_flag = False
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.message_in_cnt = 0
        self.message_error = []
        self.message_name = ""

        self.initUI()

        auth_temp, auth_temp2 = set_auth("config/config.txt")  # config.xml? #tylee
        self.digestInfo = [auth_temp2[0], auth_temp2[1]]
        self.token = auth_temp

        self.get_setting()
        self.webhook_flag = False
        self.webhook_msg = "."
        self.webhook_cnt = 99

    def post(self, path, json_data, time_out):
        self.res = None
        if self.r2 == "B":
            self.auth_type = BearerAuth(self.token)
        elif self.r2 == "D":
            self.auth_type = HTTPDigestAuth(self.digestInfo[0], self.digestInfo[1])
        elif self.r2 == "None":
            self.auth_type = False
        try:
            if self.token is None:
                self.res = requests.post(path,
                                         headers=CONSTANTS.headers, data=json_data,  # headers = head
                                         verify=False, timeout=time_out)
            else:
                self.res = requests.post(path,
                                         headers=CONSTANTS.headers, data=json_data,  # headers = head
                                         auth=self.auth_type, verify=False, timeout=time_out)

                if "Realtime" in path:
                    time.sleep(0.1)
                    try:
                        json_data_dict = json.loads(json_data.decode('utf-8'))
                        trans_protocol = json_data_dict.get("transProtocol", {})

                        if trans_protocol:
                            trans_protocol_type = trans_protocol.get("transProtocolType", {})
                            #if self.res.json()['code'] is not str(200):

                            if "WebHook".lower() in str(trans_protocol_type).lower():
                                path_tmp = trans_protocol.get("transProtocolDesc", {})

                                if "http" not in str(path_tmp):  # tylee
                                    path_tmp = "http://" + str(path_tmp)

                                parsed = urlparse(str(path_tmp))

                                url = parsed.hostname
                                port = parsed.port
                                msg = self.outMessage[-1]
                                self.webhook_flag = True

                                self.webhook_cnt = self.cnt
                                self.webhook_thread = WebhookThread(url, port, msg)
                                self.webhook_thread.result_signal.connect(self.handle_webhook_result)
                                self.webhook_thread.start()

                    except Exception as e:
                        print(e)
                        #print(traceback.format_exc())

        except Exception as e:
            #print(traceback.format_exc())
            #print("post exception", path)
            print(e)


    def handle_webhook_result(self, result):
        self.webhook_flag = True
        self.webhook_res = result
        a = self.webhook_thread.stop()
        self.webhook_thread.wait()
        # tmp_res_auth =

    def get_webhook_result(self):
        tmp_webhook_res = json.dumps(self.webhook_res, indent=4, ensure_ascii=False)
        message_name = "step " + str(self.webhook_cnt + 1) + ": " + self.message[self.webhook_cnt]
        # code&message 제외
        #val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.outSchema[self.webhook_cnt],
        #                                                                self.webhook_res, self.flag_opt)

        val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.webhookSchema[self.webhook_cnt],
                                                                        self.webhook_res, self.flag_opt)



        self.valResult.append(message_name)
        self.valResult.append("\n" + tmp_webhook_res)
        self.valResult.append(val_result)
        self.total_error_cnt += key_error_cnt
        self.total_pass_cnt += key_psss_cnt
        self.valResult.append(
            "Score : " + str((self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
        self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
            self.total_error_cnt) + "(누적 오류 필드 수)\n")

        if val_result == "PASS":
            msg = "\n" + tmp_webhook_res + "\n\n" + "Result: " + val_text + "\n"
            #img = self.img_pass
        else:
            msg = "\n" + tmp_webhook_res + "\n\n" + "Result: " + val_result + "\nResult details:\n" + val_text + "\n"
            #img = self.img_fail

        if self.webhook_cnt == 6:  # step(cnt+1), video 7th, bio 7th,
            self.step7_msg += msg
            if "FAIL" in self.step7_msg:
                self.step7_icon.setIcon(QIcon(self.img_fail))
            else:
                self.step7_icon.setIcon(QIcon(self.img_pass))
        elif self.webhook_cnt == 4:  # step(cnt+1), bio 5th, security 5th
            self.step5_msg += msg
            if "FAIL" in self.step5_msg:
                self.step5_icon.setIcon(QIcon(self.img_fail))
            else:
                self.step5_icon.setIcon(QIcon(self.img_pass))
        elif self.webhook_cnt == 3:  # step(cnt+1), security 4th
            self.step4_msg += msg
            if "FAIL" in self.step4_msg:
                self.step4_icon.setIcon(QIcon(self.img_fail))
            else:
                self.step4_icon.setIcon(QIcon(self.img_pass))

        self.webhook_res = None  # init
        self.webhook_flag = False

    def update_view(self):
        try:
            time_interval = 0
            if self.time_pre == 0:
                self.time_pre = time.time()
            else:
                time_interval = time.time() - self.time_pre

            if self.webhook_flag is True:
                time.sleep(1)
                time_interval += 1

            if time_interval >= int(self.timeInterval_widget.text()):
                if self.post_flag is False:
                    self.message_in_cnt += 1
                    self.time_pre = time.time()

                    self.message_name = "step " + str(self.cnt + 1) + ": " + self.message[self.cnt]

                    # if self.tmp_msg_append_flag:
                    #     self.valResult.append(self.message_name)
                    if self.cnt == 0:
                        self.tmp_msg_append_flag = True

                    if self.message_in_cnt > 1:
                        self.message_error.append([self.message[self.cnt]])
                        self.message_in_ctime_nt = 0
                        self.valResult.append("Message Missing!")

                        # self.total_error_cnt += len(field_finder(self.outSchema[self.cnt]))
                        tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(
                            self.outSchema[self.cnt])
                        self.total_error_cnt += tmp_fields_rqd_cnt
                        if tmp_fields_rqd_cnt == 0:  # {}인 경우 +1
                            self.total_error_cnt += 1
                        if self.flag_opt:  # 오류 필드 수 증가
                            self.total_error_cnt += tmp_fields_opt_cnt

                        self.total_pass_cnt += 0
                        self.icon_update("", "FAIL", "")
                        self.valResult.append("Score : " + str(
                            (self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                        self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 검증 통과 필드 수), " + str(
                            self.total_error_cnt) + "(누적 검증 오류 필드 수)\n")
                        self.cnt += 1

                        if self.cnt >= len(self.message):
                            self.tick_timer.stop()
                            self.valResult.append("검증 절차가 완료되었습니다.")
                            self.cnt = 0
                            self.final_report += "전체 점수: " + str(
                                (self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)) + "\n"
                            self.final_report += "전체 결과: " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                                self.total_error_cnt) + "(누적 오류 필드 수)" + "\n"
                            self.final_report += "\n"
                            self.final_report += "메시지 검증 세부 결과 \n"
                            self.final_report += self.valResult.toPlainText()

                            self.start_btn.setEnabled(True)
                            self.stop_btn.setDisabled(True)
                        return

                    time_ = int(self.timeOut_widget.text())
                    path = self.pathUrl + "/" + self.message[self.cnt]
                    #  self.valResult.append(message_name)
                    inMessage = self.inMessage[self.cnt]
                    json_data = json.dumps(inMessage).encode('utf-8')

                    t = threading.Thread(target=self.post, args=(path, json_data, time_), daemon=True)
                    t.start()
                    self.post_flag = True

                elif self.post_flag == True:
                    #  if self.cnt == 0 and
                    #    self.tmp_msg_append_flag = True
                    if self.res != None:
                        if self.cnt == 0 or self.tmp_msg_append_flag:  # and -> or 수정함- 240710
                            self.valResult.append(self.message_name)

                        res_data = self.res.text
                        res_data = json.loads(res_data)

                        tmp_res_auth = json.dumps(res_data, indent=4, ensure_ascii=False)

                        self.valResult.append(tmp_res_auth)

                        if self.webhook_flag:  # webhook 인 경우
                            val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.outSchema[-1],
                                                                                            res_data, self.flag_opt)
                            self.valResult.append(val_result)
                            try:
                                if self.message[self.cnt] == "Authentication":
                                    self.token = res_data["accessToken"]
                            except:
                                pass

                            self.total_error_cnt += key_error_cnt
                            self.total_pass_cnt += key_psss_cnt
                            self.icon_update(tmp_res_auth, val_result, val_text)
                            self.valResult.append("Score : " + str(
                                (self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                            self.valResult.append(
                                "Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                                    self.total_error_cnt) + "(누적 오류 필드 수)\n")
                            self.cnt += 1
                            self.message_in_cnt = 0

                            if self.webhook_res is not None:
                                self.get_webhook_result()


                        else:  # webhook 아닌경우
                            val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.outSchema[self.cnt],
                                                                                                res_data, self.flag_opt)
                            #print("일반!", val_result, val_text)
                            self.valResult.append(val_result)


                            try:
                                if self.message[self.cnt] == "Authentication":
                                    self.token = res_data["accessToken"]
                            except:
                                pass

                            self.total_error_cnt += key_error_cnt
                            self.total_pass_cnt += key_psss_cnt
                            self.icon_update(tmp_res_auth, val_result, val_text)
                            self.valResult.append("Score : " + str(
                                (self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                            self.valResult.append(
                                "Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                                    self.total_error_cnt) + "(누적 오류 필드 수)\n")
                            self.cnt += 1
                            self.message_in_cnt = 0

                    self.post_flag = False



                # res = requests.post(self.pathUrl + "/"+ self.message[self.cnt],
                #                    headers=CONSTANTS.headers, data=json_data,
                #                    auth=self.auth_type, verify=False, timeout=10)

                if self.cnt == len(self.message):
                    self.tick_timer.stop()
                    self.valResult.append("검증 절차가 완료되었습니다.")

                    self.cnt = 0
                    self.final_report += "전체 점수: "+  str((self.total_pass_cnt/(self.total_pass_cnt+self.total_error_cnt)*100))+"\n"
                    self.final_report += "전체 결과: "+ str(self.total_pass_cnt)+"(누적 통과 필드 수), "+str(self.total_error_cnt)+"(누적 오류 필드 수)"+"\n"
                    self.final_report += "\n"
                    self.final_report += "메시지 검증 세부 결과 \n"
                    self.final_report += self.valResult.toPlainText()
                    self.start_btn.setEnabled(True)
                    self.stop_btn.setDisabled(True)

        except Exception as err:
            #print("오류발생")
            print(err)
            #print(traceback.format_exc())
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error Message: 오류 확인 후 검증 절차를 다시 시작해주세요")
            msg.setInformativeText(str(err))
            msg.setWindowTitle("Error")
            msg.exec_()
            self.tick_timer.stop()
            self.valResult.append("검증 절차가 중지되었습니다.")
            self.start_btn.setEnabled(True)
            self.stop_btn.setDisabled(True)

    def icon_update_step(self, auth_, result_, text_):
        if result_ == "PASS":
            msg = auth_ + "\n\n" + "Result: " + text_
            img = self.img_pass
        else:
            msg = auth_ + "\n\n" + "Result: " + result_ + "\nResult details:\n" + text_
            img = self.img_fail
        return msg, img

    def icon_update(self, tmp_res_auth, val_result, val_text):
        msg, img = self.icon_update_step(tmp_res_auth, val_result, val_text)
        if self.cnt == 0:  # step(cnt+1)
            self.step1_icon.setIcon(QIcon(img))
            self.step1_msg += msg

        elif self.cnt == 1:
            self.step2_icon.setIcon(QIcon(img))
            self.step2_msg += msg

        elif self.cnt == 2:
            self.step3_icon.setIcon(QIcon(img))
            self.step3_msg += msg

        elif self.cnt == 3:
            self.step4_icon.setIcon(QIcon(img))
            self.step4_msg += msg

        elif self.cnt == 4:
            self.step5_icon.setIcon(QIcon(img))
            self.step5_msg += msg

        elif self.cnt == 5:
            self.step6_icon.setIcon(QIcon(img))
            self.step6_msg += msg

        elif self.cnt == 6:
            self.step7_icon.setIcon(QIcon(img))
            self.step7_msg += msg

        elif self.cnt == 7:
            self.step8_icon.setIcon(QIcon(img))
            self.step8_msg += msg

        elif self.cnt == 8:
            self.step9_icon.setIcon(QIcon(img))
            self.step9_msg += msg

    def initUI(self):
        outerLayout = QVBoxLayout()
        contentLayout = QHBoxLayout()
        leftLayout = QVBoxLayout()
        self.centerLayout = QVBoxLayout()
        self.circleLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()
        mainTitle = QLabel("물리보안 시스템 연동 검증\n 소프트웨어", self)
        mainTitle.setAlignment(Qt.AlignLeft)
        mainTitle.setStyleSheet('font-size: 14pt')
        outerLayout.addWidget(mainTitle)
        empty = QLabel(" ")
        empty.setStyleSheet('font-size:5pt')
        outerLayout.addWidget(empty)  # empty
        # left layout
        self.r1 = ""
        self.r2 = ""
        leftLayout.addWidget(self.group1())
        self.settingGroup = QGroupBox("환경설정")
        settingLayout = QVBoxLayout()
        settingLayout.addWidget(self.group2())
        settingLayout.addWidget(self.group3())
        settingLayout.addWidget(self.group4())
        self.settingGroup.setLayout(settingLayout)
        leftLayout.addWidget(self.settingGroup)

        self.start_btn = QPushButton(self)
        self.start_btn.setText('검증 시작')
        self.start_btn.clicked.connect(self.start_btn_clicked)
        leftLayout.addWidget(self.start_btn)

        self.stop_btn = QPushButton(self)
        self.stop_btn.setText('검증 중지')
        self.stop_btn.clicked.connect(self.stop_btn_clicked)
        leftLayout.addWidget(self.stop_btn)
        self.stop_btn.setDisabled(True)

        # center layout
        self.valmsg = QLabel('검증 메시지', self)
        self.centerLayout.addWidget(self.valmsg)
        self.init_centerLayout()
        self.circleLayout.addWidget(QLabel(""))  # align
        self.init_circleLayout()
        # right layout
        rightLayout.addWidget(QLabel("검증 진행 결과"))
        self.valResult = QTextBrowser(self)
        rightLayout.addWidget(self.valResult)
        self.resultsave_btn = QPushButton(self)
        self.resultsave_btn.setText('검증 결과 저장')
        self.resultsave_btn.clicked.connect(self.resultsave_btn_clicked)
        rightLayout.addWidget(self.resultsave_btn)
        contentLayout.addLayout(leftLayout)
        contentLayout.addLayout(self.centerLayout)
        contentLayout.addLayout(self.circleLayout)
        contentLayout.addLayout(rightLayout)

        outerLayout.addLayout(contentLayout)
        outerLayout.addWidget(empty)  # empty
        self.setLayout(outerLayout)
        self.setWindowTitle('물리보안 시스템 연동 검증 소프트웨어')

        self.setGeometry(1300, 500, 1000, 500)
        # showing all the widgets

        if not self.embedded :
            self.show()

    def init_centerLayout(self):
        self.step1 = QPushButton("1. step1")
        self.step2 = QPushButton("2. step2")
        self.step3 = QPushButton("3. step3")
        self.step4 = QPushButton("4. step4")
        self.step5 = QPushButton("5. step5")
        self.step6 = QPushButton("6. step6")
        self.step7 = QPushButton("7. step7")
        self.step8 = QPushButton("8. step8")
        self.step9 = QPushButton("9. step9")

        self.step1.setFixedSize(250, 60)
        self.step2.setFixedSize(250, 60)
        self.step3.setFixedSize(250, 60)
        self.step4.setFixedSize(250, 60)
        self.step5.setFixedSize(250, 60)
        self.step6.setFixedSize(250, 60)
        self.step7.setFixedSize(250, 60)
        self.step8.setFixedSize(250, 60)
        self.step9.setFixedSize(250, 60)

        self.step1.clicked.connect(self.step1_clicked)
        self.step2.clicked.connect(self.step2_clicked)
        self.step3.clicked.connect(self.step3_clicked)
        self.step4.clicked.connect(self.step4_clicked)
        self.step5.clicked.connect(self.step5_clicked)
        self.step6.clicked.connect(self.step6_clicked)
        self.step7.clicked.connect(self.step7_clicked)
        self.step8.clicked.connect(self.step8_clicked)
        self.step9.clicked.connect(self.step9_clicked)

        self.step1_msg = ""
        self.step2_msg = ""
        self.step3_msg = ""
        self.step4_msg = ""
        self.step5_msg = ""
        self.step6_msg = ""
        self.step7_msg = ""
        self.step8_msg = ""
        self.step9_msg = ""

        split1 = QSplitter()
        split1.setFrameShape(QFrame.NoFrame)
        split1.addWidget(self.step1)

        split2 = QSplitter()
        split2.setFrameShape(QFrame.NoFrame)
        split2.addWidget(self.step2)

        split3 = QSplitter()
        split3.setFrameShape(QFrame.NoFrame)
        split3.addWidget(self.step3)

        split4 = QSplitter()
        split4.setFrameShape(QFrame.NoFrame)
        split4.addWidget(self.step4)

        split5 = QSplitter()
        split5.setFrameShape(QFrame.NoFrame)
        split5.addWidget(self.step5)

        split6 = QSplitter()
        split6.setFrameShape(QFrame.NoFrame)
        split6.addWidget(self.step6)

        split7 = QSplitter()
        split7.setFrameShape(QFrame.NoFrame)
        split7.addWidget(self.step7)

        split8 = QSplitter()
        split8.setFrameShape(QFrame.NoFrame)
        split8.addWidget(self.step8)

        split9 = QSplitter()
        split9.setFrameShape(QFrame.NoFrame)
        split9.addWidget(self.step9)

        self.splitwidget = QSplitter(Qt.Vertical)
        self.splitwidget.addWidget(split1)
        self.splitwidget.addWidget(split2)
        self.splitwidget.addWidget(split3)
        self.splitwidget.addWidget(split4)
        self.splitwidget.addWidget(split5)
        self.splitwidget.addWidget(split6)
        self.splitwidget.addWidget(split7)
        self.splitwidget.addWidget(split8)
        self.splitwidget.addWidget(split9)
        self.centerLayout.addWidget(self.splitwidget)

    def init_circleLayout(self):
        self.step1_icon = QPushButton("")
        self.step2_icon = QPushButton("")
        self.step3_icon = QPushButton("")
        self.step4_icon = QPushButton("")
        self.step5_icon = QPushButton("")
        self.step6_icon = QPushButton("")
        self.step7_icon = QPushButton("")
        self.step8_icon = QPushButton("")
        self.step9_icon = QPushButton("")

        self.step1_icon.setStyleSheet('background-color:transparent')
        self.step2_icon.setStyleSheet('background-color:transparent')
        self.step3_icon.setStyleSheet('background-color:transparent')
        self.step4_icon.setStyleSheet('background-color:transparent')
        self.step5_icon.setStyleSheet('background-color:transparent')
        self.step6_icon.setStyleSheet('background-color:transparent')
        self.step7_icon.setStyleSheet('background-color:transparent')
        self.step8_icon.setStyleSheet('background-color:transparent')
        self.step9_icon.setStyleSheet('background-color:transparent')

        self.step1_icon.setIcon(QIcon(self.img_none))
        self.step2_icon.setIcon(QIcon(self.img_none))
        self.step3_icon.setIcon(QIcon(self.img_none))
        self.step4_icon.setIcon(QIcon(self.img_none))
        self.step5_icon.setIcon(QIcon(self.img_none))
        self.step6_icon.setIcon(QIcon(self.img_none))
        self.step7_icon.setIcon(QIcon(self.img_none))
        self.step8_icon.setIcon(QIcon(self.img_none))
        self.step9_icon.setIcon(QIcon(self.img_none))

        split1 = QSplitter()
        split1.setFrameShape(QFrame.NoFrame)
        split1.addWidget(self.step1_icon)

        split2 = QSplitter()
        split2.setFrameShape(QFrame.NoFrame)
        split2.addWidget(self.step2_icon)

        split3 = QSplitter()
        split3.setFrameShape(QFrame.NoFrame)
        split3.addWidget(self.step3_icon)

        split4 = QSplitter()
        split4.setFrameShape(QFrame.NoFrame)
        split4.addWidget(self.step4_icon)

        split5 = QSplitter()
        split5.setFrameShape(QFrame.NoFrame)
        split5.addWidget(self.step5_icon)

        split6 = QSplitter()
        split6.setFrameShape(QFrame.NoFrame)
        split6.addWidget(self.step6_icon)

        split7 = QSplitter()
        split7.setFrameShape(QFrame.NoFrame)
        split7.addWidget(self.step7_icon)

        split8 = QSplitter()
        split8.setFrameShape(QFrame.NoFrame)
        split8.addWidget(self.step8_icon)

        split9 = QSplitter()
        split9.setFrameShape(QFrame.NoFrame)
        split9.addWidget(self.step9_icon)

        self.splitwidget = QSplitter(Qt.Vertical)
        self.splitwidget.addWidget(split1)
        self.splitwidget.addWidget(split2)
        self.splitwidget.addWidget(split3)
        self.splitwidget.addWidget(split4)
        self.splitwidget.addWidget(split5)
        self.splitwidget.addWidget(split6)
        self.splitwidget.addWidget(split7)
        self.splitwidget.addWidget(split8)
        self.splitwidget.addWidget(split9)
        self.circleLayout.addWidget(self.splitwidget)

    def group1(self):
        rgroup = QGroupBox('연동 시스템')
        self.g1_radio1 = QRadioButton('영상보안 시스템')
        self.g1_radio1.toggled.connect(self.g1_radio1_checked)
        self.g1_radio2 = QRadioButton('바이오인식 기반 출입통제 시스템')
        self.g1_radio2.toggled.connect(self.g1_radio2_checked)
        self.g1_radio3 = QRadioButton('보안용 센서 시스템')
        self.g1_radio3.toggled.connect(self.g1_radio3_checked)
        vbox = QVBoxLayout()
        vbox.addWidget(self.g1_radio1)
        vbox.addWidget(self.g1_radio2)
        vbox.addWidget(self.g1_radio3)
        rgroup.setLayout(vbox)
        return rgroup

    def group2(self):
        rgroup = QGroupBox('사용자 인증 방식')
        self.g2_radio1 = QRadioButton('Digest Auth')
        self.g2_radio1.toggled.connect(self.g2_radio_checked)
        self.g2_radio2 = QRadioButton('Bearer Token')
        self.g2_radio2.toggled.connect(self.g2_radio_checked)
        self.g2_radio3 = QRadioButton('None')
        self.g2_radio3.toggled.connect(self.g2_radio_checked)
        #  self.g2_radio2.setChecked(True)
        vbox = QVBoxLayout()
        vbox.addWidget(self.g2_radio1)
        vbox.addWidget(self.g2_radio2)
        vbox.addWidget(self.g2_radio3)
        rgroup.setLayout(vbox)
        return rgroup

    def group3(self):
        fgroup = QGroupBox('메시지 송수신')
        self.timeInterval_widget = QSpinBox()
        self.timeInterval_widget.setValue(2)
        self.timeInterval_widget.setMaximum(1000)
        self.timeOut_widget = QSpinBox()
        self.timeOut_widget.setValue(2)
        self.timeOut_widget.setMaximum(1000)
        self.protocol_widget = QComboBox()
        self.protocol_widget.addItem("LongPolling")
        self.protocol_widget.addItem("WebHook")

        flayout = QFormLayout()
        flayout.addRow("transProtocol  ", self.protocol_widget)
        flayout.addRow("timeInterval(sec):  ", self.timeInterval_widget)
        flayout.addRow("timeOut(sec):  ", self.timeOut_widget)

        fgroup.setLayout(flayout)
        return fgroup

    def group4(self):
        fgroup = QGroupBox('')

        self.linkUrl = QLineEdit(self)
        self.linkUrl.setText("https://127.0.0.1:8008")

        layout = QVBoxLayout()
        layout.addWidget(QLabel('연동 URL'))
        layout.addWidget(self.linkUrl)

        fgroup.setLayout(layout)
        return fgroup

    def g1_radio1_checked(self, checked):
        if checked:
            self.radio_check_flag = True
            self.message = videoMessages
            self.inMessage = videoInMessage
            self.outMessage = videoOutMessage
            self.inSchema = videoInSchema
            self.outSchema = videoOutSchema
            self.webhookSchema = videoWebhookSchema
            self.system = "video"
            self.final_report = "영상보안 시스템-물리보안 통합플랫폼(가상) 검증 결과"+"\n"
            self.step7.setEnabled(True)
            self.step8.setEnabled(True)
            self.step9.setEnabled(True)
            self.step7_icon.setEnabled(True)
            self.step8_icon.setEnabled(True)
            self.step9_icon.setEnabled(True)
            self.step1.setText("1. Authentication")
            self.step2.setText("2. Capabilities")
            self.step3.setText("3. CameraProfiles")
            self.step4.setText("4. StoredVideoInfos")
            self.step5.setText("5. StreamURLs")
            self.step6.setText("6. ReplayURL")
            self.step7.setText("7. RealtimeVideoEventInfos")
            self.step8.setText("8. StoredVideoEventInfos")
            self.step9.setText("9. StoredObjectAnalyticsInfos")

    def g1_radio2_checked(self, checked):
        if checked:
            self.radio_check_flag = True
            self.message = bioMessages
            self.inMessage = bioInMessage
            self.outMessage = bioOutMessage
            self.inSchema = bioInSchema
            self.outSchema = bioOutSchema
            self.webhookSchema = bioWebhookSchema
            self.system = "bio"
            self.final_report = "바이오인식 기반 출입통제 시스템-물리보안 통합플랫폼(가상) 검증 결과"+"\n"
            self.step7.setEnabled(True)
            self.step8.setEnabled(True)
            self.step9.setEnabled(False)

            self.step7_icon.setEnabled(True)
            self.step8_icon.setEnabled(True)
            self.step9_icon.setEnabled(False)

            self.step1.setText("1. Authentication")
            self.step2.setText("2. Capabilities")
            self.step3.setText("3. DoorProfiles")
            self.step4.setText("4. AccessUserInfos")
            self.step5.setText("5. RealtimeVerifEventInfos")
            self.step6.setText("6. StoredVerifEventInfos")
            self.step7.setText("7. RealtimeDoorStatus")
            self.step8.setText("8. DoorControl")
            self.step9.setText("")

    def g1_radio3_checked(self, checked):
        if checked:
            self.radio_check_flag = True
            self.message = securityMessages
            self.inMessage = securityInMessage
            self.outMessage = securityOutMessage
            self.inSchema = securityInSchema
            self.outSchema = securityOutSchema
            self.webhookSchema = securityWebhookSchema
            self.system = "security"
            self.final_report = "보안용 센서 시스템-물리보안 통합플랫폼(가상) 검증 결과"+"\n"
            self.step7.setEnabled(True)
            self.step8.setEnabled(False)
            self.step9.setEnabled(False)

            self.step7_icon.setEnabled(True)
            self.step8_icon.setEnabled(False)
            self.step9_icon.setEnabled(False)

            self.step1.setText("1. Authentication")
            self.step2.setText("2. Capabilities")
            self.step3.setText("3. SensorDeviceProfiles")
            self.step4.setText("4. RealtimeSensorData")
            self.step5.setText("5. RealtimeSensorEventInfos")
            self.step6.setText("6. StoredSensorEventInfos")
            self.step7.setText("7. SensorDeviceControl")
            self.step8.setText("")
            self.step9.setText("")

    def g2_radio_checked(self, checked):
        if checked:
            self.auth_flag = True
            if self.g2_radio1.isChecked():  # digest
                self.r2 = "D"
                msg = QMessageBox()
                msg.setText("Message: 사용자 인증 정보")
                msg.setInformativeText(
                    'ID: ' + str(self.digestInfo[0]) + '  \nPW:' + str(self.digestInfo[1]))
                msg.setWindowTitle("Information")
                msg.exec_()
            elif self.g2_radio2.isChecked():  # bearer token
                self.r2 = "B"
                msg = QMessageBox()
                msg.setText("Message: 사용자 인증 정보")
                if self.token is None:
                    msg.setInformativeText('Bearer Token' + ': ' + '토큰 정보 없음')
                else:
                    msg.setInformativeText('Bearer Token'+': '+self.token)
                msg.setWindowTitle("Information")
                msg.exec_()
            elif self.g2_radio3.isChecked():
                self.r2 = "None"

    def step1_clicked(self):
        CustomDialog(self.step1_msg, self.step1.text())

    def step2_clicked(self):
        CustomDialog(self.step2_msg, self.step2.text())

    def step3_clicked(self):
        CustomDialog(self.step3_msg, self.step3.text())

    def step4_clicked(self):
        CustomDialog(self.step4_msg, self.step4.text())

    def step5_clicked(self):
        CustomDialog(self.step5_msg, self.step5.text())

    def step6_clicked(self):
        CustomDialog(self.step6_msg, self.step6.text())

    def step7_clicked(self):
        CustomDialog(self.step7_msg, self.step7.text())

    def step8_clicked(self):
        CustomDialog(self.step8_msg, self.step8.text())

    def step9_clicked(self):
        CustomDialog(self.step9_msg, self.step9.text())

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # 창 크기가 변할 때 버튼 크기 조정
        min_button_width = 250
        min_button_height = 60

        # 현재 창의 크기를 가져옴
        window_width = self.width()
        window_height = self.height()

        # 버튼의 새로운 크기 계산
        button_width = max(min_button_width, window_width // 3)  # 최소 크기와 폭의 1/3 중 더 큰 값으로 설정
        button_height = max(min_button_height, window_height // 13)

        # # 버튼 크기 설정
        self.step1.setFixedSize(button_width, button_height)
        self.step2.setFixedSize(button_width, button_height)
        self.step3.setFixedSize(button_width, button_height)
        self.step4.setFixedSize(button_width, button_height)
        self.step5.setFixedSize(button_width, button_height)
        self.step6.setFixedSize(button_width, button_height)
        self.step7.setFixedSize(button_width, button_height)
        self.step8.setFixedSize(button_width, button_height)
        self.step9.setFixedSize(button_width, button_height)
        self.valResult.setFixedWidth(window_width // 3)


    def start_btn_clicked(self):
        if self.radio_check_flag == False:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error Message: 연동시스템 선택 오류")
            msg.setInformativeText('물리보안 시스템을 선택해주세요.')
            msg.setWindowTitle("Error")
            msg.exec_()
        elif self.auth_flag == False:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error Message: 사용자 인증 선택 오류")
            msg.setInformativeText('사용자 인증을 선택해주세요.')
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            # system_type self.system 으로 바꿀것 #tylee
            system_type = "video" if self.g1_radio1.isChecked() else "bio" if self.g1_radio2.isChecked() else "security"
            json_to_data(system_type)
            self.start_btn.setDisabled(True)
            self.stop_btn.setEnabled(True)

            self.init_win()
            self.valResult.clear()  # 초기화

            self.final_report = ""  # 초기화
            self.tmp_msg_append_flag = False  # 초기화 . step1이 여러번 적힘 우선 임시 T.T

            self.post_flag = False
            self.total_error_cnt = 0
            self.total_pass_cnt = 0
            self.message_in_cnt = 0
            self.message_error = []

            self.pathUrl = self.linkUrl.text()
            self.valResult.append("Start Validation...\n")
            self.webhook_cnt = 99
            self.tick_timer.start()

    def stop_btn_clicked(self):
        self.tick_timer.stop()
        self.valResult.append("검증 절차가 중지되었습니다.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setDisabled(True)

    def init_win(self):
        self.cnt = 0
        self.valResult.clear()
        self.step1_msg = ""
        self.step2_msg = ""
        self.step3_msg = ""
        self.step4_msg = ""
        self.step5_msg = ""
        self.step6_msg = ""
        self.step7_msg = ""
        self.step8_msg = ""
        self.step9_msg = ""
        self.step1_icon.setIcon(QIcon(self.img_none))
        self.step2_icon.setIcon(QIcon(self.img_none))
        self.step3_icon.setIcon(QIcon(self.img_none))
        self.step4_icon.setIcon(QIcon(self.img_none))
        self.step5_icon.setIcon(QIcon(self.img_none))
        self.step6_icon.setIcon(QIcon(self.img_none))
        self.step7_icon.setIcon(QIcon(self.img_none))
        self.step8_icon.setIcon(QIcon(self.img_none))
        self.step9_icon.setIcon(QIcon(self.img_none))

    def resultsave_btn_clicked(self):
        tmp_result = self.final_report  # + '\n'+ self.valResult.toPlainText()
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        if file != "":
            save_result(tmp_result, file + "/Result_system.pdf")
            self.valResult.append("검증 결과 파일 저장했습니다. " + "\n" + "저장 위치: " + file + "/Result_system.pdf")
        else:
            self.valResult.append("저장 폴더를 선택해주세요.")

    def get_setting(self):
        self.setting_variables = QSettings('My App', 'Variable')

        self.system = self.setting_variables.value('system')
        if self.system == "video":
            self.g1_radio1.setChecked(True)
        elif self.system == "bio":
            self.g1_radio2.setChecked(True)
        elif self.system == "security":
            self.g1_radio3.setChecked(True)

        self.r2 = self.setting_variables.value('auth')
        if self.r2 == "D":
            self.g2_radio1.setChecked(True)
        elif self.r2 == "B":
            self.g2_radio2.setChecked(True)
        elif self.r2 == "None":
            self.g2_radio3.setChecked(True)

        tmp = self.setting_variables.value('linkUrl')
        if tmp is None:
            tmp = "https://127.0.0.1:8008"
        self.linkUrl.setText(tmp)
        try:
            tmp = self.setting_variables.value('timeInterval')
            self.timeInterval_widget.setValue(int(tmp))
        except TypeError:
            self.timeInterval_widget.setValue(2)
        try:
            tmp = self.setting_variables.value('timeOut')
            self.timeOut_widget.setValue(int(tmp))
        except TypeError:
            self.timeOut_widget.setValue(5)

        saved_idx = self.setting_variables.value('protocolWidget',0,int)
        self.protocol_widget.setCurrentIndex(saved_idx)

    def closeEvent(self, event):
        self.setting_variables.setValue('system', self.system)
        self.setting_variables.setValue('auth', self.r2)
        self.setting_variables.setValue('timeInterval', self.timeInterval_widget.text())
        self.setting_variables.setValue('timeOut', self.timeOut_widget.text())
        self.setting_variables.setValue('linkUrl', self.linkUrl.text())
        self.setting_variables.setValue('protocolWidget', self.protocol_widget.currentIndex())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))
    ex = MyApp(embedded=False)
    sys.exit(app.exec())
