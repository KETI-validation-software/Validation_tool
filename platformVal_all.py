# 물리보안 통합플랫폼 검증 소프트웨어
# physical security integrated platform validation software

from api.api_server import Server
import time
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFontDatabase, QFont
from PyQt5.QtCore import Qt, QSettings, QTimer, QThread
import sys
import ssl

from core.functions import json_check_, save_result, resource_path, field_finder, json_to_data, set_auth, timeout_field_finder

import spec
from spec.video.videoRequest import videoMessages, videoOutMessage, videoInMessage
from spec.video.videoSchema import videoInSchema, videoOutSchema
from spec.bio.bioRequest import bioMessages, bioOutMessage, bioInMessage
from spec.bio.bioSchema import  bioInSchema, bioOutSchema
from spec.security.securityRequest import securityMessages, securityOutMessage, securityInMessage
from spec.security.securitySchema import securityInSchema, securityOutSchema
import config.CONSTANTS as CONSTANTS

from http.server import HTTPServer
import json
import traceback
import warnings
warnings.filterwarnings('ignore')

#  from charset_normalizer import md__mypyc  # A library that helps you read text from an unknown charset encoding


class CustomDialog(QDialog):# popup window for validation result
    def __init__(self, dmsg, dstep):
        super().__init__()

        self.setWindowTitle(dstep)
        self.setGeometry(800, 600, 400, 600)  # tylee # 800, 500, 400, 600)  # tylee
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
        self.radio_check_flag = False
        self.img_pass = resource_path("assets/image/green.png")
        self.img_fail = resource_path("assets/image/red.png")
        self.img_none = resource_path("assets/image/black.png")

        self.flag_opt = True  # functions.py-json_check_ # 필수필드만 확인 False, optional 필드까지 확인 True
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self.update_view)
        self.auth_flag = False
        # self.setFixedSize(QSize(850, 500))
        self.Server = Server
        self.valid_field = [25, 11, 11]

        auth_temp, auth_temp2 = set_auth("config/config.txt")
        self.digestInfo = [auth_temp2[0], auth_temp2[1]]
        self.token = auth_temp

        self.initUI()
        self.realtime_flag = False
        self.cnt = 0
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        self.time_pre = 0
        self.cnt_pre = 0
        self.final_report = ""
        self.get_setting()

        with open(resource_path("spec/rows.json"), "w") as out_file:
            json.dump(None, out_file, ensure_ascii=False)

    def update_view(self):
        try:
            time_interval = 0
            if self.time_pre == 0 or self.cnt != self.cnt_pre:
                self.time_pre = time.time()
                self.cnt_pre = self.cnt
            else:
                time_interval = time.time() - self.time_pre

            if self.cnt == 1 and self.r2 == "B":
                data = self.Server.outMessage[0]
                try:
                    self.auth_Info = data['accessToken']
                    self.Server.auth_Info[0] = self.auth_Info
                except:
                    pass

            if self.realtime_flag is True:
                time.sleep(1)
                time_interval += 1

            if time_interval < int(self.timeOut_widget.text()):
                try:
                    with open(resource_path("spec/" + self.Server.system + "/" + self.Server.message[self.cnt] +
                                            ".json"), "r", encoding="UTF-8") as out_file:
                        data = json.load(out_file)

                except json.JSONDecodeError as verr:
                    #print(traceback.format_exc())
                    box = QMessageBox()
                    box.setIcon(QMessageBox.Critical)
                    # box.setText("Error Message: " + path_ + " 을 확인하세요")
                    box.setInformativeText(str(verr))
                    box.setWindowTitle("Error")

                    box.exec_()
                    return ""
                except Exception as err:
                    #print(traceback.format_exc())
                    box = QMessageBox()
                    box.setIcon(QMessageBox.Critical)
                    # box.setText("Error Message: " + path_ + " 을 확인하세요")
                    box.setInformativeText(str(err))
                    box.setWindowTitle("Error")

                    box.exec_()
                    return ""

                if data != None:
                    # with open(self.Server.message[self.cnt] + ".json", "w") as out_file:
                    #    json.dump(None, out_file)
                    message_name = "step " + str(self.cnt + 1) + ": " + self.Server.message[self.cnt]
                    inMessage = dict()


                    val_result = ""
                    val_text = ""
                    key_psss_cnt = 0
                    key_error_cnt = 0
                    if self.Server.message[self.cnt] in CONSTANTS.none_request_message:

                        if (len(data) != 0) and data != "{}":
                            val_result = "FAIL"
                            val_text = ""
                            key_psss_cnt = 0
                            key_error_cnt = 1
                        elif (len(data) != 0) or data != "{}":
                            val_result = "PASS"
                            val_text = "PASS"
                            key_psss_cnt = 1
                            key_error_cnt = 0

                    else:
                        #print("통플검증sw이 받은 ->", data)
                        val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.Server.inSchema[self.cnt],
                                                                                    data, self.flag_opt)
#############################################################################################################
 # 아래 수정중


                        if "Realtime" in str(self.Server.message[self.cnt]):  # realtime 어찌구인지 확인해야함
                            if "Webhook".lower() in str(data).lower():
                                try:
                                    with open(resource_path(
                                            "spec/" + self.Server.system + "/" + "webhook_" + self.Server.message[self.cnt] + ".json"), "r",
                                              encoding="UTF-8") as out_file2:
                                        self.realtime_flag = True
                                        webhook_data = json.load(out_file2)
                                        tmp_webhook_data = json.dumps(webhook_data, indent=4, ensure_ascii=False)
                                        webhook_val_result, webhook_val_text, webhook_key_psss_cnt, webhook_key_error_cnt = json_check_(self.Server.outSchema[-1],
                                                                                                                webhook_data, self.flag_opt)

                                        #print("webhook!!!->",tmp_webhook_data)
                                        self.icon_update(tmp_webhook_data, webhook_val_result, webhook_val_text)

                                        self.valResult.append(message_name)
                                        self.valResult.append("\n" +tmp_webhook_data)
                                        self.valResult.append(webhook_val_result)

                                        self.total_error_cnt += webhook_key_error_cnt
                                        self.total_pass_cnt += webhook_key_psss_cnt
                                        self.valResult.append(
                                            "Score : " + str((self.total_pass_cnt / (
                                                        self.total_pass_cnt + self.total_error_cnt) * 100)))
                                        self.valResult.append(
                                            "Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                                                self.total_error_cnt) + "(누적 오류 필드 수)\n")

                                        if "FAIL" in webhook_val_text:  # webhook fail 인 경우 step(?) fail -> icon_update()
                                            val_text = "FAIL"

                                except json.JSONDecodeError as verr:
                                    box = QMessageBox()
                                    box.setIcon(QMessageBox.Critical)
                                    box.setInformativeText(str(verr))
                                    box.setWindowTitle("Error")
                                    box.exec_()
                                    #print(traceback.format_exc())

                                    return ""

# 위 수정중
#############################################################################################################
                    self.valResult.append(message_name)
                    tmp_res_auth = json.dumps(data, indent=4, ensure_ascii=False)
                    self.valResult.append(tmp_res_auth)

                    self.valResult.append(val_result)
                    self.total_error_cnt += key_error_cnt
                    self.total_pass_cnt += key_psss_cnt

                    self.valResult.append(
                        "Score : " + str((self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                    self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                        self.total_error_cnt) + "(누적 오류 필드 수)\n")
                    self.icon_update(tmp_res_auth, val_result, val_text)
                    self.cnt += 1
                self.realtime_flag = False

            elif time_interval > int(self.timeOut_widget.text()) and self.cnt == self.cnt_pre:
                # self.valResult.append(self.Server.message[self.cnt])
                message_name = "step " + str(self.cnt + 1) + ": " + self.Server.message[self.cnt]
                self.valResult.append(message_name)
                # self.valResult.append("FAIL")
                self.valResult.append("Message Missing!")
                tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(self.Server.inSchema[self.cnt])

                self.total_error_cnt += tmp_fields_rqd_cnt
                if tmp_fields_rqd_cnt == 0:  # {}인 경우 +1
                    self.total_error_cnt += 1
                if self.flag_opt:
                    self.total_error_cnt += tmp_fields_opt_cnt
                # self.total_error_cnt += len(field_finder(self.Server.inSchema[self.cnt]))

                self.total_pass_cnt += 0
                self.valResult.append(
                    "Score : " + str((self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                    self.total_error_cnt) + "(누적 오류 필드 수)\n")
                self.icon_update("", "FAIL", "")
                self.cnt += 1

            if self.cnt == len(self.Server.message):
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
                self.sbtn.setEnabled(True)
                self.stop_btn.setDisabled(True)

        except Exception as err:
            #print(traceback.format_exc())
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error Message: 오류 확인 후 검증 절차를 다시 시작해주세요")
            msg.setInformativeText(str(err))
            msg.setWindowTitle("Error")
            msg.exec_()
            self.tick_timer.stop()
            self.valResult.append("검증 절차가 중지되었습니다.")
            self.sbtn.setEnabled(True)
            self.stop_btn.setDisabled(True)

        time.sleep(0.05)

    def icon_update_step(self, auth_, result_, text_):
        if result_ == "PASS":
            msg = auth_ + "\n\n" + "Result: " + text_ +"\n"
            img = self.img_pass
        else:
            msg = auth_ + "\n\n" + "Result: " + result_ + "\nResult details:\n" + text_ +"\n"
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
        mainTitle = QLabel("물리보안 통합플랫폼 검증\n 소프트웨어", self)
        mainTitle.setAlignment(Qt.AlignLeft)
        mainTitle.setStyleSheet('font-size: 18pt')
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
        #settingTitle = QLabel("환경설정")
        #self.label.setFixedSize(200, 100)  #
        
        #leftLayout.addWidget(settingTitle)
        #leftLayout.addWidget(self.group2())
        #leftLayout.addWidget(self.group3())
        #leftLayout.addWidget(self.group4())

        self.sbtn = QPushButton(self)
        self.sbtn.setText('검증 시작')
        self.sbtn.clicked.connect(self.sbtn_push)
        leftLayout.addWidget(self.sbtn)

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
        self.rbtn = QPushButton(self)
        self.rbtn.setText('검증 결과 저장')
        self.rbtn.clicked.connect(self.rbtn_push)
        rightLayout.addWidget(self.rbtn)
        contentLayout.addLayout(leftLayout)
        contentLayout.addLayout(self.centerLayout)
        contentLayout.addLayout(self.circleLayout)
        contentLayout.addLayout(rightLayout)

        outerLayout.addLayout(contentLayout)
        outerLayout.addWidget(empty)  # empty
        self.setLayout(outerLayout)
        self.setWindowTitle('물리보안 통합플랫폼 연동 검증 소프트웨어')
        self.setGeometry(500, 500, 1000, 10)  # 500, 500, 1000, 10)
        # showing all the widgets

        # self.json_th.json_update_data.connect(self.json_update_data)
        # self.json_th.start()
        if not self.embedded :
            self.show()

    def init_centerLayout(self):
        # self.stepLayout = QVBoxLayout()

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
        # self.stepLayout = QVBoxLayout()
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

        vbox = QVBoxLayout()
        vbox.addWidget(self.g2_radio1)
        vbox.addWidget(self.g2_radio2)
        vbox.addWidget(self.g2_radio3)
        rgroup.setLayout(vbox)
        return rgroup

    def group3(self):
        fgroup = QGroupBox('메시지 송수신')
        self.protocol_widget = QComboBox()
        self.protocol_widget.addItem("LongPolling")
        self.protocol_widget.addItem("WebHook")
        self.timeOut_widget = QSpinBox()
        self.timeOut_widget.setValue(5)
        self.timeOut_widget.setMaximum(1000)

        flayout = QFormLayout()
        flayout.addRow("transProtocol  ", self.protocol_widget)
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
            self.radio_check_flag = "video"
            self.final_report = "영상보안 시스템(가상)-물리보안 통합플랫폼 검증 결과" + "\n"
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

            self.radio_check_flag = "bio"
            self.final_report = "바이오인식 기반 출입통제 시스템(가상)-물리보안 통합플랫폼 검증 결과" + "\n"
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
            self.final_report = "보안용 센서 시스템(가상)-물리보안 통합플랫폼 검증 결과" + "\n"
            self.step7.setEnabled(True)
            self.step8.setEnabled(False)
            self.step9.setEnabled(False)

            self.step7_icon.setEnabled(True)
            self.step8_icon.setEnabled(False)
            self.step9_icon.setEnabled(False)
            self.radio_check_flag = "security"
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
                if self.token == None:
                    msg.setInformativeText('Bearer Token' + ': ' + '토큰 정보 없음')
                else:
                    msg.setInformativeText('Bearer Token' + ': ' + self.token)

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
        button_width = max(min_button_width, window_width // 3)  # 최소 크기와 창 폭의 1/3 중 더 큰 값으로 설정
        button_height = max(min_button_height, window_height // 13)
        #
        # # 버튼 크기 설정
        # self.step1.setFixedWidth(button_width)
        self.step1.setFixedSize(button_width, button_height)
        self.step2.setFixedSize(button_width, button_height)
        self.step3.setFixedSize(button_width, button_height)
        self.step4.setFixedSize(button_width, button_height)
        self.step5.setFixedSize(button_width, button_height)
        self.step6.setFixedSize(button_width, button_height)
        self.step7.setFixedSize(button_width, button_height)
        self.step8.setFixedSize(button_width, button_height)
        self.step9.setFixedSize(button_width, button_height)
        self.valResult.setFixedWidth(window_width//3)


    def sbtn_push(self):
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
            self.total_error_cnt = 0
            self.total_pass_cnt = 0
            self.sbtn.setDisabled(True)
            self.stop_btn.setEnabled(True)

            # self.Server = api_server.Server# -> MyApp init()으로
            json_to_data(self.radio_check_flag)

            timeout = int(self.timeOut_widget.text())
            if self.radio_check_flag == "video":
                if self.r2 == "B":
                    videoOutMessage[0]['accessToken'] = self.token
                self.Server.message = videoMessages
                self.Server.inMessage = videoInMessage
                self.Server.outMessage = videoOutMessage
                self.Server.inSchema = videoInSchema
                self.Server.outSchema = videoOutSchema
                self.Server.system = "video"
                self.Server.timeout = timeout

            elif self.radio_check_flag == "bio":
                if self.r2 == "B":
                    bioOutMessage[0]['accessToken'] = self.token
                self.Server.message = bioMessages
                self.Server.inMessage = bioInMessage
                self.Server.outMessage = bioOutMessage
                self.Server.inSchema = bioInSchema
                self.Server.outSchema = bioOutSchema
                self.Server.system = "bio"
                self.Server.timeout = timeout

            elif self.radio_check_flag == "security":
                if self.r2 == "B":
                    securityOutMessage[0]['accessToken'] = self.token
                self.Server.message = securityMessages
                self.Server.inMessage = securityInMessage
                self.Server.outMessage = securityOutMessage
                self.Server.inSchema = securityInSchema
                self.Server.outSchema = securityOutSchema
                self.Server.system = "security"
                self.Server.timeout = timeout

            self.init_win()
            self.valResult.clear()  # 초기화
            self.final_report = ""  # 초기화

            self.step1_icon.setIcon(QIcon(self.img_none))
            self.step2_icon.setIcon(QIcon(self.img_none))
            self.step3_icon.setIcon(QIcon(self.img_none))
            self.step4_icon.setIcon(QIcon(self.img_none))
            self.step5_icon.setIcon(QIcon(self.img_none))
            self.step6_icon.setIcon(QIcon(self.img_none))
            self.step7_icon.setIcon(QIcon(self.img_none))
            self.step8_icon.setIcon(QIcon(self.img_none))
            self.step9_icon.setIcon(QIcon(self.img_none))
            self.pathUrl = self.linkUrl.text()

            if self.r2 == "B":
                self.Server.auth_type = "B"
                self.Server.auth_Info[0] = str(self.token)
            elif self.r2 == "D":
                self.Server.auth_type = "D"
                self.Server.auth_Info[0] = self.digestInfo[0]
                self.Server.auth_Info[1] = self.digestInfo[1]
            elif self.r2 == "None":
                self.Server.auth_type = "None"
                self.Server.auth_Info[0] = None
            # radio2

            self.Server.transProtocolInput = self.protocol_widget.currentText()

            self.valResult.append("Start Validation...\n")

            url = self.linkUrl.text().split(":")
            address_ip = url[-2].split("/")[-1]
            address_port = int(url[-1])

            self.server_th = server_th(handler_class=self.Server, address=address_ip, port=address_port)
            self.server_th.start()
            self.tick_timer.start()

    def stop_btn_clicked(self):
        self.tick_timer.stop()
        self.valResult.append("검증 절차가 중지되었습니다.")
        self.sbtn.setEnabled(True)
        self.stop_btn.setDisabled(True)

    def init_win(self):
        self.cnt = 0
        for i in range(0, len(self.Server.message)):
            with open(resource_path("spec/"+self.Server.system + "/" + self.Server.message[i] + ".json"), "w",
                      encoding="UTF-8") as out_file:  # 수정해야함
                json.dump(None, out_file, ensure_ascii=False)

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

    def rbtn_push(self):

        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file != "":
            tmp_result = self.final_report  # + '\n'+ self.valResult.toPlainText()
            save_result(tmp_result, file + "/Result_platform.pdf")
            self.valResult.append("검증 결과 파일 저장했습니다. " + "\n" + "저장 위치: " + file + "/Result_platform.pdf")
        else:
            self.valResult.append("저장 폴더를 선택해주세요.")

    def get_setting(self):
        self.setting_variables = QSettings('My App', 'Variable')
        #  QSettings('My App', 'Variable').clear()#tylee
        self.Server.system = self.setting_variables.value('system')
        if self.Server.system == "video":
            self.g1_radio1.setChecked(True)
        elif self.Server.system == "bio":
            self.g1_radio2.setChecked(True)
        elif self.Server.system == "security":
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
            tmp = self.setting_variables.value('timeOut')
            self.timeOut_widget.setValue(int(tmp))
        except TypeError:  # None
            self.timeOut_widget.setValue(5)

        saved_idx = self.setting_variables.value('protocolWidget',0,int)
        self.protocol_widget.setCurrentIndex(saved_idx)

    def closeEvent(self, event):
        self.setting_variables.setValue('system', self.Server.system)
        self.setting_variables.setValue('auth', self.r2)
        self.setting_variables.setValue('timeOut', self.timeOut_widget.text())
        self.setting_variables.setValue('linkUrl', self.linkUrl.text())
        self.setting_variables.setValue('protocolWidget', self.protocol_widget.currentIndex())


class server_th(QThread):
    def __init__(self, handler_class=None, address='127.0.0.1', port=8008):
        super().__init__()
        self.handler_class = handler_class
        self.address_ip = address
        self.address_port = port
        self.server_address = (self.address_ip, self.address_port)
        self.httpd = HTTPServer(self.server_address, self.handler_class)

        certificate_private = resource_path('config/key0627/server.crt')
        certificate_key = resource_path('config/key0627/server.key')
        try:
            self.httpd.socket = ssl.wrap_socket(self.httpd.socket, certfile=certificate_private,
                                                keyfile=certificate_key, server_side=True)
        except Exception as e:
            #print(traceback.format_exc())
            print(e)

        print('Starting on ', self.server_address)

    def run(self):
        self.httpd.serve_forever()


#  ?
class json_data(QThread):
    json_update_data = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            with open(resource_path("spec/rows.json"), "r", encoding="UTF-8") as out_file:
                data = json.load(out_file)
            if data is not None:
                with open(resource_path("spec/rows.json"), "w", encoding="UTF-8") as out_file:
                    json.dump(None, out_file, ensure_ascii=False)
                self.json_update_data.emit(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(resource_path('NanumGothic.ttf'))
    app.setFont(QFont('NanumGothic'))
    ex = MyApp(embedded=False)
    sys.exit(app.exec())
