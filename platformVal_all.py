# 물리보안 통합플랫폼 검증 소프트웨어
# physical security integrated platform validation software
# 아직 UI 수정 안됌

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

from core.functions import json_check_, save_result, resource_path, field_finder, json_to_data, set_auth, timeout_field_finder 
from core.json_checker_new import check_message_data, check_message_schema, check_message_error 

from http.server import HTTPServer
import json
import traceback
import warnings
warnings.filterwarnings('ignore')

#  from charset_normalizer import md__mypyc  # A library that helps you read text from an unknown charset encoding


# 팝업창 설정하는 함수
class CustomDialog(QDialog):# popup window for validation result
    def __init__(self, dmsg, dstep):
        ############## 디자인 설정 하는 부분 ######################
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

                    # 평가 점수 디스플레이 업데이트
                    self.update_score_display()

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
                
                # 평가 점수 디스플레이 업데이트
                self.update_score_display()
                
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

    def update_score_display(self):
        """평가 점수 디스플레이를 업데이트"""
        total_fields = self.total_pass_cnt + self.total_error_cnt
        if total_fields > 0:
            score = (self.total_pass_cnt / total_fields) * 100
        else:
            score = 0
            
        self.pass_count_label.setText(f"통과 필드 수: {self.total_pass_cnt}")
        self.total_count_label.setText(f"전체 필드 수: {total_fields}")
        self.score_label.setText(f"평가 점수: {score:.1f}%")

    # 더 정확히는 여기서 데이터 확인의 팝업창 메시지 포맷 형태를 정하고 있음
    def icon_update_step(self, auth_, result_, text_):
        if result_ == "PASS":
            msg = auth_ + "\n\n" + "Result: " + text_ +"\n"
            img = self.img_pass # 아이콘 바꾸ㅓ주는거임
        else:
            msg = auth_ + "\n\n" + "Result: " + result_ + "\nResult details:\n" + text_ +"\n"
            img = self.img_fail
        return msg, img

    def icon_update(self, tmp_res_auth, val_result, val_text):
        msg, img = self.icon_update_step(tmp_res_auth, val_result, val_text)
        
        # 아이콘을 완전히 중앙에 정렬하기 위해 위젯 사용
        icon_widget = QWidget()
        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(img).pixmap(16, 16))
        icon_label.setToolTip(msg)
        icon_label.setAlignment(Qt.AlignCenter)
        
        icon_layout.addWidget(icon_label)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_widget.setLayout(icon_layout)
        
        if self.cnt < self.tableWidget.rowCount():
            self.tableWidget.setCellWidget(self.cnt, 1, icon_widget)
            # 메시지 저장 (팝업용)
            setattr(self, f"step{self.cnt+1}_msg", msg)

    def initUI(self):

        outerLayout = QVBoxLayout()
        topLayout = QHBoxLayout()      # 최상단 환경설정과 버튼들 레이아웃
        contentLayout = QVBoxLayout()  # 시험 결과 레이아웃
        bottomLayout = QVBoxLayout()   # 하단 모니터링 레이아웃
        
        empty = QLabel(" ")
        empty.setStyleSheet('font-size:5pt')
        outerLayout.addWidget(empty)  # empty
        
        # 시험 정보 박스 (가로 배치)
        self.settingGroup = QGroupBox("시험정보")
        self.settingGroup.setMaximumWidth(800)  # 시험정보 박스 전체 너비 확장 (연동 시스템 추가를 위해)
        settingLayout = QHBoxLayout()  # 가로로 변경
        settingLayout.addWidget(self.group2())  # 사용자 인증 방식
        settingLayout.addWidget(self.group3())  # 메시지 송수신
        settingLayout.addWidget(self.group4())  # 연동 URL
        settingLayout.addWidget(self.group1())  # 연동 시스템을 시험정보에 추가
        self.settingGroup.setLayout(settingLayout)
        
        # 검증 버튼들 (가로 배치, 짧은 너비)
        buttonGroup = QGroupBox("")
        buttonGroup.setMaximumWidth(380)  # 버튼 그룹 박스 너비 제한
        buttonLayout = QHBoxLayout()
        
        self.sbtn = QPushButton(self)
        self.sbtn.setText('평가 시작')
        self.sbtn.setMaximumWidth(100)  # 버튼 너비 제한
        self.sbtn.setStyleSheet("""
            QPushButton {
                background-color: #87CEEB;  /* 스카이블루 */
                border: 2px solid #4682B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #191970;  /* 미드나잇 블루 텍스트 */
            }
            QPushButton:hover {
                background-color: #B0E0E6;  /* 호버시 더 밝은 블루 */
                border: 2px solid #1E90FF;
            }
            QPushButton:pressed {
                background-color: #4682B4;  /* 클릭시 더 진한 블루 */
            }
            QPushButton:disabled {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                color: #999999;
            }
        """)
        self.sbtn.clicked.connect(self.sbtn_push)

        self.stop_btn = QPushButton(self)
        self.stop_btn.setText('일시 정지')
        self.stop_btn.setMaximumWidth(100)  # 버튼 너비 제한
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #87CEEB;  /* 스카이블루 */
                border: 2px solid #4682B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #191970;  /* 미드나잇 블루 텍스트 */
            }
            QPushButton:hover {
                background-color: #B0E0E6;  /* 호버시 더 밝은 블루 */
                border: 2px solid #1E90FF;
            }
            QPushButton:pressed {
                background-color: #4682B4;  /* 클릭시 더 진한 블루 */
            }
            QPushButton:disabled {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                color: #999999;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_btn_clicked)
        self.stop_btn.setDisabled(True)
        
        # ------------------ 원래 검증 결과 저장 버튼이었음 -> 추후 종료 기능으로 기능 수정해야함 ------------------------
        self.rbtn = QPushButton(self)
        self.rbtn.setText('종료')
        self.rbtn.setMaximumWidth(120)  # 버튼 너비 제한
        self.rbtn.setStyleSheet("""
            QPushButton {
                background-color: #87CEEB;  /* 스카이블루 */
                border: 2px solid #4682B4;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #191970;  /* 미드나잇 블루 텍스트 */
            }
            QPushButton:hover {
                background-color: #B0E0E6;  /* 호버시 더 밝은 블루 */
                border: 2px solid #1E90FF;
            }
            QPushButton:pressed {
                background-color: #4682B4;  /* 클릭시 더 진한 블루 */
            }
            QPushButton:disabled {
                background-color: #F0F0F0;
                border: 2px solid #CCCCCC;
                color: #999999;
            }
        """)
        self.rbtn.clicked.connect(self.rbtn_push)

        buttonLayout.addWidget(self.sbtn)
        buttonLayout.addWidget(self.stop_btn)
        buttonLayout.addWidget(self.rbtn)
        # buttonLayout.addStretch() 
        buttonGroup.setLayout(buttonLayout)
        
        # 상단 레이아웃 구성 (환경설정 + 버튼들) ---------------------------------
        topLayout.addWidget(self.settingGroup)
        topLayout.addWidget(buttonGroup)
        topLayout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        topLayout.setSpacing(10)  # 위젯 간 간격 조정

        # 중간 레이아웃 구성 (아래까지 포함)---------------------------------
        contentLayout.addWidget(self.group_score()) # 평가 점수 박스 위로 올라감
        contentLayout.addSpacing(15)  # 위젯 간 간격 조정
        self.valmsg = QLabel('시험 결과', self)
        contentLayout.addWidget(self.valmsg)
        self.init_centerLayout()
        
        # 시험 결과 영역을 테이블 크기에 맞게 조정
        contentWidget = QWidget()
        contentWidget.setLayout(self.centerLayout)
        contentWidget.setMaximumSize(1000, 400)  # 테이블 크기와 동일하게 설정
        contentWidget.setMinimumSize(900, 300)   # 테이블 최소 크기와 동일하게 설정
        contentLayout.addWidget(contentWidget)

        # 하단 모니터링 레이아웃 구성 ---------------------------------
        bottomLayout.addWidget(QLabel("수신 메시지 실시간 모니터링"))
        self.valResult = QTextBrowser(self)
        self.valResult.setMaximumHeight(200)  # 높이 제한
        self.valResult.setMaximumWidth(1000)  # 테이블과 동일한 너비로 설정
        self.valResult.setMinimumWidth(900)   # 테이블 최소 너비와 동일하게 설정
        bottomLayout.addWidget(self.valResult)
        
        # 평가 점수를 기존 연동 시스템 위치에 배치
        self.r1 = ""
        self.r2 = ""
        # bottomLayout.addWidget(self.group_score())  # 평가 점수 박스로 변경

        # 전체 레이아웃 구성 ---------------------------------
        outerLayout.addLayout(topLayout)     # 최상단: 환경설정 + 버튼들
        outerLayout.addSpacing(10)  # 위젯 간 간격 조정
        outerLayout.addLayout(contentLayout) # 중단: 평가 점수 + 시험 결과 
        outerLayout.addSpacing(10)  # 위젯 간 간격 조정
        outerLayout.addLayout(bottomLayout)  # 하단: 모니터링 
        outerLayout.addWidget(empty)  # empty
        # outerLayout.setSpacing(10)  # 레이아웃 간 간격 조정
        self.setLayout(outerLayout)
        self.setWindowTitle('물리보안 통합플랫폼 연동 검증 소프트웨어')
        self.setGeometry(500, 300, 1200, 850)  # 창 크기 설정
        # showing all the widgets

        # self.json_th.json_update_data.connect(self.json_update_data)
        # self.json_th.start()
        if not self.embedded :
            self.show()

    def init_centerLayout(self):
        # 표 형태로 변경 (8컬럼으로 확장)
        self.tableWidget = QTableWidget(9, 8)
        self.tableWidget.setHorizontalHeaderLabels(["API 명", "결과", "검증 횟수", "실패 횟수", "평가 점수", "메시지 데이터", "메시지 규격", "메시지 오류"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))
        
        # 테이블 크기 설정
        self.tableWidget.setMinimumSize(900, 300)  # 최소 크기 설정
        self.tableWidget.resize(1000, 400)  # 기본 크기 설정 (여백을 고려해서 50px 증가)
        
        # 컬럼 너비 설정
        self.tableWidget.setColumnWidth(0, 280)  # API 명 컬럼 너비 (20px 줄임)
        self.tableWidget.setColumnWidth(1, 90)   # 결과 컬럼 너비 (10px 줄임)
        self.tableWidget.setColumnWidth(2, 90)   # 검증 횟수 컬럼 너비 (10px 줄임)
        self.tableWidget.setColumnWidth(3, 90)   # 실패 횟수 컬럼 너비 (10px 줄임)
        self.tableWidget.setColumnWidth(4, 90)   # 평가 점수 컬럼 너비 (10px 줄임)
        self.tableWidget.setColumnWidth(5, 110)  # 상세 결과 컬럼 너비 (20px 줄임)
        self.tableWidget.setColumnWidth(6, 110)    # 메시지 데이터 컬럼 숨김
        self.tableWidget.setColumnWidth(7, 110)    # 메시지 규격


        # 행 높이 설정
        for i in range(9):
            self.tableWidget.setRowHeight(i, 40)

        # 단계명 리스트 (기본값)
        self.step_names = [
            "Authentication", "Capabilities", "CameraProfiles", "StoredVideoInfos",
            "StreamURLs", "ReplayURL", "RealtimeVideoEventInfos",
            "StoredVideoEventInfos", "StoredObjectAnalyticsInfos"
        ]
        for i, name in enumerate(self.step_names):
            # API 명
            self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{i+1}. {name}"))
            # 결과 아이콘 (위젯으로 중앙 정렬)
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
            
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            
            self.tableWidget.setCellWidget(i, 1, icon_widget)
            # 검증 횟수
            self.tableWidget.setItem(i, 2, QTableWidgetItem("0"))
            self.tableWidget.item(i, 2).setTextAlignment(Qt.AlignCenter)
            # 실패 횟수
            self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
            self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
            # 평가 점수
            self.tableWidget.setItem(i, 4, QTableWidgetItem("0%"))
            self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)
            # 상세 결과 버튼 (중앙 정렬을 위한 위젯 컨테이너)
            detail_btn = QPushButton("데이터 확인")
            detail_btn.setMaximumHeight(30)
            detail_btn.setMaximumWidth(120)  # 버튼 최대 너비 제한
            detail_btn.clicked.connect(lambda checked, row=i: self.show_detail_result(row))
            
            # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_btn)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)
            
            self.tableWidget.setCellWidget(i, 5, container)

            # 메시지 규격 버튼 (6번 컬럼)
            schema_btn = QPushButton("규격 확인")
            schema_btn.setMaximumHeight(30)
            schema_btn.setMaximumWidth(100)
            schema_btn.clicked.connect(lambda checked, row=i: self.show_schema_result(row))
            
            # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
            schema_container = QWidget()
            schema_layout = QHBoxLayout()
            schema_layout.addWidget(schema_btn)
            schema_layout.setAlignment(Qt.AlignCenter)
            schema_layout.setContentsMargins(0, 0, 0, 0)
            schema_container.setLayout(schema_layout)
            
            self.tableWidget.setCellWidget(i, 6, schema_container)

            # 메시지 오류 버튼 (7번 컬럼)
            error_btn = QPushButton("오류 확인")
            error_btn.setMaximumHeight(30)
            error_btn.setMaximumWidth(100)
            error_btn.clicked.connect(lambda checked, row=i: self.show_error_result(row))
            
            # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
            error_container = QWidget()
            error_layout = QHBoxLayout()
            error_layout.addWidget(error_btn)
            error_layout.setAlignment(Qt.AlignCenter)
            error_layout.setContentsMargins(0, 0, 0, 0)
            error_container.setLayout(error_layout)
            
            self.tableWidget.setCellWidget(i, 7, error_container)

        # 결과 컬럼만 클릭 가능하도록 설정 (기존 기능 유지)
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)
        
        # centerLayout을 초기화하고 테이블 추가
        self.centerLayout = QVBoxLayout()
        self.centerLayout.addWidget(self.tableWidget)


    ##################### 여기 작업해야함 -> 데이터, 규격, 오류 세가지 내용으로 나눠서 세 버튼에 각각 connect 작업 ###########################
    def show_detail_result(self, row):
        """데이터 확인 버튼 - 실제 데이터 내용 표시"""
        try:
            if self.radio_check_flag == "bio":
                out_data = bioOutMessage[row]
                api_name = bioMessages[row]
            elif self.radio_check_flag == "video":
                out_data = videoOutMessage[row]
                api_name = videoMessages[row]
            else:
                out_data = securityOutMessage[row]
                api_name = securityMessages[row]
            
            # 실제 데이터 내용을 JSON 형태로 보여주기
            import json
            data_msg = f"{api_name} API - 실제 메시지 데이터\n\n"
            data_msg += json.dumps(out_data, indent=2, ensure_ascii=False)
            
            CustomDialog(data_msg, f"{api_name} - 실제 데이터")
            
        except Exception as e:
            CustomDialog(f"오류: {str(e)}", "데이터 확인 오류")

    def show_schema_result(self, row):
        """규격 확인 버튼 - 스키마 구조 표시"""
        try:
            if self.radio_check_flag == "bio":
                out_schema = bioOutSchema[row]
                api_name = bioMessages[row]
            elif self.radio_check_flag == "video":
                out_schema = videoOutSchema[row]
                api_name = videoMessages[row]
            else:
                out_schema = securityOutSchema[row]
                api_name = securityMessages[row]
            
            # 스키마 구조를 문자열로 변환해서 보여주기
            def schema_to_string(schema, indent=0):
                result = ""
                spaces = "  " * indent
                for key, value in schema.items():
                    if hasattr(key, 'expected_data'):  # OptionalKey인 경우
                        key_name = f"{key.expected_data} (선택사항)"
                    else:
                        key_name = str(key)
                        
                    if isinstance(value, dict):
                        result += f"{spaces}{key_name}: {{\n"
                        result += schema_to_string(value, indent + 1)
                        result += f"{spaces}}}\n"
                    elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        result += f"{spaces}{key_name}: [\n"
                        result += schema_to_string(value[0], indent + 1)
                        result += f"{spaces}]\n"
                    else:
                        result += f"{spaces}{key_name}: {value.__name__ if hasattr(value, '__name__') else str(value)}\n"
                return result
            
            schema_msg = f"{api_name} API - 메시지 규격 구조\n\n"
            schema_msg += schema_to_string(out_schema)
            
            CustomDialog(schema_msg, f"{api_name} - 규격 구조")
            
        except Exception as e:
            CustomDialog(f"오류: {str(e)}", "규격 확인 오류")

    def show_error_result(self, row):
        """오류 확인 버튼 - 검증 오류 표시"""
        try:
            if self.radio_check_flag == "bio":
                out_schema = bioOutSchema[row]
                out_data = bioOutMessage[row]
                api_name = bioMessages[row]
            elif self.radio_check_flag == "video":
                out_schema = videoOutSchema[row]
                out_data = videoOutMessage[row]
                api_name = videoMessages[row]
            else:
                out_schema = securityOutSchema[row]
                out_data = securityOutMessage[row]
                api_name = securityMessages[row]
            
            # 실제 검증 수행해서 오류만 표시
            all_field, opt_field = field_finder(out_schema)
            datas = json_to_data(out_data)
            result, error_msg = check_message_error(all_field, datas, opt_field, True)
            
            error_msg_display = f"{api_name} API - 검증 오류 결과\n\n"
            error_msg_display += f"검증 결과: {result}\n\n"
            if result == "FAIL":
                error_msg_display += "오류 세부사항:\n"
                error_msg_display += error_msg
            else:
                error_msg_display += "오류가 없습니다."
            
            CustomDialog(error_msg_display, f"{api_name} - 검증 오류")
            
        except Exception as e:
            CustomDialog(f"오류: {str(e)}", "검증 오류")

    def table_cell_clicked(self, row, col):
        """테이블 셀 클릭 시 호출되는 함수 (결과 아이콘 클릭용으로 유지)"""
        if col == 1:  # 결과 컬럼 클릭 시에만 동작
            msg = getattr(self, f"step{row+1}_msg", "")
            if msg:
                CustomDialog(msg, self.tableWidget.item(row, 0).text())

    def init_circleLayout(self):
        pass  # 테이블 형태로 변경했으므로 이 메서드는 더이상 필요 없음

    def group1(self):
        rgroup = QGroupBox('연동 시스템')
        rgroup.setMaximumWidth(200)  # 환경설정에 맞게 너비 조정
        
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
        rgroup = QGroupBox('시험 인증 정보')
        rgroup.setMaximumWidth(180)  # 인증 정보 박스 너비 제한
        
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
        fgroup.setMaximumWidth(200)  # 메시지 송수신 박스 너비 제한
        
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
        fgroup.setMaximumWidth(150)  # 시험 URL 박스 너비 제한

        self.linkUrl = QLineEdit(self)
        self.linkUrl.setText("https://127.0.0.1:8008")
        self.linkUrl.setMaximumWidth(130)  # URL 입력 필드 너비 제한

        layout = QVBoxLayout()
        layout.addWidget(QLabel('시험 URL'))
        layout.addWidget(self.linkUrl)

        fgroup.setLayout(layout)
        return fgroup

    def group_score(self):
        """평가 점수 박스"""
        sgroup = QGroupBox('평가 점수')
        sgroup.setMaximumWidth(1000)  # 테이블과 동일한 너비로 설정
        sgroup.setMinimumWidth(900)   # 테이블 최소 너비와 동일하게 설정
        
        # 점수 표시용 레이블들
        self.pass_count_label = QLabel("통과 필드 수: 0")
        self.total_count_label = QLabel("전체 필드 수: 0")  
        self.score_label = QLabel("평가 점수: 0%")
        
        # 폰트 크기 조정
        font = self.pass_count_label.font()
        font.setPointSize(20)
        self.pass_count_label.setFont(font)
        self.total_count_label.setFont(font)
        self.score_label.setFont(font)
        
        # 가로 배치
        layout = QHBoxLayout()
        layout.setSpacing(90)  # 레이블 간 간격 조정
        layout.addWidget(self.pass_count_label)
        layout.addWidget(self.total_count_label)
        layout.addWidget(self.score_label)
        layout.addStretch()  # 오른쪽 여백 추가
        
        sgroup.setLayout(layout)
        return sgroup

    def g1_radio1_checked(self, checked):
        if checked:
            self.radio_check_flag = "video"
            self.final_report = "영상보안 시스템(가상)-물리보안 통합플랫폼 검증 결과" + "\n"
            self.step_names = [
                "Authentication", "Capabilities", "CameraProfiles", "StoredVideoInfos",
                "StreamURLs", "ReplayURL", "RealtimeVideoEventInfos",
                "StoredVideoEventInfos", "StoredObjectAnalyticsInfos"
            ]
            for i, name in enumerate(self.step_names):
                # API 명
                self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{i+1}. {name}"))
                # 결과 아이콘 (위젯으로 중앙 정렬)
                icon_widget = QWidget()
                icon_layout = QHBoxLayout()
                icon_layout.setContentsMargins(0, 0, 0, 0)
                
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
                icon_label.setAlignment(Qt.AlignCenter)
                
                icon_layout.addWidget(icon_label)
                icon_layout.setAlignment(Qt.AlignCenter)
                icon_widget.setLayout(icon_layout)
                
                self.tableWidget.setCellWidget(i, 1, icon_widget)
                # 검증 횟수
                self.tableWidget.setItem(i, 2, QTableWidgetItem("0"))
                self.tableWidget.item(i, 2).setTextAlignment(Qt.AlignCenter)
                # 실패 횟수
                self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
                self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
                # 평가 점수
                self.tableWidget.setItem(i, 4, QTableWidgetItem("0%"))
                self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)
                # 상세 결과 버튼 (중앙 정렬을 위한 위젯 컨테이너)
                detail_btn = QPushButton("데이터 확인")
                detail_btn.setMaximumHeight(30)
                detail_btn.setMaximumWidth(120)  # 버튼 최대 너비 제한
                detail_btn.clicked.connect(lambda checked, row=i: self.show_detail_result(row))
                
                # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
                container = QWidget()
                layout = QHBoxLayout()
                layout.addWidget(detail_btn)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                container.setLayout(layout)
                
                self.tableWidget.setCellWidget(i, 5, container)

                # 메시지 규격 버튼 (6번 컬럼)
                schema_btn = QPushButton("규격 확인")
                schema_btn.setMaximumHeight(30)
                schema_btn.setMaximumWidth(100)
                schema_btn.clicked.connect(lambda checked, row=i: self.show_schema_result(row))
                
                # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
                schema_container = QWidget()
                schema_layout = QHBoxLayout()
                schema_layout.addWidget(schema_btn)
                schema_layout.setAlignment(Qt.AlignCenter)
                schema_layout.setContentsMargins(0, 0, 0, 0)
                schema_container.setLayout(schema_layout)
                
                self.tableWidget.setCellWidget(i, 6, schema_container)

                # 메시지 오류 버튼 (7번 컬럼)
                error_btn = QPushButton("오류 확인")
                error_btn.setMaximumHeight(30)
                error_btn.setMaximumWidth(100)
                error_btn.clicked.connect(lambda checked, row=i: self.show_error_result(row))
                
                # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
                error_container = QWidget()
                error_layout = QHBoxLayout()
                error_layout.addWidget(error_btn)
                error_layout.setAlignment(Qt.AlignCenter)
                error_layout.setContentsMargins(0, 0, 0, 0)
                error_container.setLayout(error_layout)
                
                self.tableWidget.setCellWidget(i, 7, error_container)

    def g1_radio2_checked(self, checked):
        if checked:
            self.radio_check_flag = "bio"
            self.final_report = "바이오인식 기반 출입통제 시스템(가상)-물리보안 통합플랫폼 검증 결과" + "\n"
            self.step_names = [
                "Authentication", "Capabilities", "DoorProfiles", "AccessUserInfos",
                "RealtimeVerifEventInfos", "StoredVerifEventInfos", "RealtimeDoorStatus",
                "DoorControl", ""
            ]
            for i, name in enumerate(self.step_names):
                # API 명
                self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{i+1}. {name}"))
                # 결과 아이콘 (위젯으로 중앙 정렬)
                icon_widget = QWidget()
                icon_layout = QHBoxLayout()
                icon_layout.setContentsMargins(0, 0, 0, 0)
                
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
                icon_label.setAlignment(Qt.AlignCenter)
                
                icon_layout.addWidget(icon_label)
                icon_layout.setAlignment(Qt.AlignCenter)
                icon_widget.setLayout(icon_layout)
                
                self.tableWidget.setCellWidget(i, 1, icon_widget)
                # 검증 횟수
                self.tableWidget.setItem(i, 2, QTableWidgetItem("0"))
                self.tableWidget.item(i, 2).setTextAlignment(Qt.AlignCenter)
                # 실패 횟수
                self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
                self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
                # 평가 점수
                self.tableWidget.setItem(i, 4, QTableWidgetItem("0%"))
                self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)
                # 상세 결과 버튼 (중앙 정렬을 위한 위젯 컨테이너)
                detail_btn = QPushButton("데이터 확인")
                detail_btn.setMaximumHeight(30)
                detail_btn.setMaximumWidth(120)  # 버튼 최대 너비 제한
                detail_btn.clicked.connect(lambda checked, row=i: self.show_detail_result(row))
                
                # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
                container = QWidget()
                layout = QHBoxLayout()
                layout.addWidget(detail_btn)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                container.setLayout(layout)
                
                self.tableWidget.setCellWidget(i, 5, container)

                # 메시지 규격 버튼 (6번 컬럼)
                schema_btn = QPushButton("규격 확인")
                schema_btn.setMaximumHeight(30)
                schema_btn.setMaximumWidth(100)
                schema_btn.clicked.connect(lambda checked, row=i: self.show_schema_result(row))
                
                # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
                schema_container = QWidget()
                schema_layout = QHBoxLayout()
                schema_layout.addWidget(schema_btn)
                schema_layout.setAlignment(Qt.AlignCenter)
                schema_layout.setContentsMargins(0, 0, 0, 0)
                schema_container.setLayout(schema_layout)
                
                self.tableWidget.setCellWidget(i, 6, schema_container)

                # 메시지 오류 버튼 (7번 컬럼)
                error_btn = QPushButton("오류 확인")
                error_btn.setMaximumHeight(30)
                error_btn.setMaximumWidth(100)
                error_btn.clicked.connect(lambda checked, row=i: self.show_error_result(row))
                
                # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
                error_container = QWidget()
                error_layout = QHBoxLayout()
                error_layout.addWidget(error_btn)
                error_layout.setAlignment(Qt.AlignCenter)
                error_layout.setContentsMargins(0, 0, 0, 0)
                error_container.setLayout(error_layout)
                
                self.tableWidget.setCellWidget(i, 7, error_container)

    def g1_radio3_checked(self, checked):
        if checked:
            self.final_report = "보안용 센서 시스템(가상)-물리보안 통합플랫폼 검증 결과" + "\n"
            self.radio_check_flag = "security"
            self.step_names = [
                "Authentication", "Capabilities", "SensorDeviceProfiles", "RealtimeSensorData",
                "RealtimeSensorEventInfos", "StoredSensorEventInfos", "SensorDeviceControl",
                "", ""
            ]
            for i, name in enumerate(self.step_names):
                # API 명
                self.tableWidget.setItem(i, 0, QTableWidgetItem(f"{i+1}. {name}"))
                # 결과 아이콘 (위젯으로 중앙 정렬)
                icon_widget = QWidget()
                icon_layout = QHBoxLayout()
                icon_layout.setContentsMargins(0, 0, 0, 0)
                
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
                icon_label.setAlignment(Qt.AlignCenter)
                
                icon_layout.addWidget(icon_label)
                icon_layout.setAlignment(Qt.AlignCenter)
                icon_widget.setLayout(icon_layout)
                
                self.tableWidget.setCellWidget(i, 1, icon_widget)
                # 검증 횟수
                self.tableWidget.setItem(i, 2, QTableWidgetItem("0"))
                self.tableWidget.item(i, 2).setTextAlignment(Qt.AlignCenter)
                # 실패 횟수
                self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
                self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
                # 평가 점수
                self.tableWidget.setItem(i, 4, QTableWidgetItem("0%"))
                self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)
                # 상세 결과 버튼 (중앙 정렬을 위한 위젯 컨테이너)
                detail_btn = QPushButton("데이터 확인")
                detail_btn.setMaximumHeight(30)
                detail_btn.setMaximumWidth(120)  # 버튼 최대 너비 제한
                detail_btn.clicked.connect(lambda checked, row=i: self.show_detail_result(row))
                
                # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
                container = QWidget()
                layout = QHBoxLayout()
                layout.addWidget(detail_btn)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                container.setLayout(layout)
                
                self.tableWidget.setCellWidget(i, 5, container)

                # 메시지 규격 버튼 (6번 컬럼)
                schema_btn = QPushButton("규격 확인")
                schema_btn.setMaximumHeight(30)
                schema_btn.setMaximumWidth(100)
                schema_btn.clicked.connect(lambda checked, row=i: self.show_schema_result(row))
                
                # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
                schema_container = QWidget()
                schema_layout = QHBoxLayout()
                schema_layout.addWidget(schema_btn)
                schema_layout.setAlignment(Qt.AlignCenter)
                schema_layout.setContentsMargins(0, 0, 0, 0)
                schema_container.setLayout(schema_layout)
                
                self.tableWidget.setCellWidget(i, 6, schema_container)

                # 메시지 오류 버튼 (7번 컬럼)
                error_btn = QPushButton("오류 확인")
                error_btn.setMaximumHeight(30)
                error_btn.setMaximumWidth(100)
                error_btn.clicked.connect(lambda checked, row=i: self.show_error_result(row))
                
                # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
                error_container = QWidget()
                error_layout = QHBoxLayout()
                error_layout.addWidget(error_btn)
                error_layout.setAlignment(Qt.AlignCenter)
                error_layout.setContentsMargins(0, 0, 0, 0)
                error_container.setLayout(error_layout)
                
                self.tableWidget.setCellWidget(i, 7, error_container)

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

    # 기존 step 클릭 함수들은 table_cell_clicked로 대체됨
    def step1_clicked(self):
        pass
    def step2_clicked(self):
        pass
    def step3_clicked(self):
        pass
    def step4_clicked(self):
        pass
    def step5_clicked(self):
        pass
    def step6_clicked(self):
        pass
    def step7_clicked(self):
        pass
    def step8_clicked(self):
        pass
    def step9_clicked(self):
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 창 크기 변경 시 테이블 크기 조정
        if hasattr(self, 'tableWidget'):
            window_width = self.width()
            window_height = self.height()
            
            # 테이블 크기를 창 크기에 맞게 조정 (3컬럼에 맞게 너비 증가)
            table_width = min(max(600, window_width // 3), 800)  # 최소 600, 최대 800
            table_height = min(max(300, window_height // 2), 500)  # 최소 300, 최대 500
            
            self.tableWidget.resize(table_width, table_height)


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
            # 평가 점수 디스플레이 초기화
            self.update_score_display()
            
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

            # 테이블 아이콘 초기화
            for i in range(self.tableWidget.rowCount()):
                icon_widget = QWidget()
                icon_layout = QHBoxLayout()
                icon_layout.setContentsMargins(0, 0, 0, 0)
                
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
                icon_label.setAlignment(Qt.AlignCenter)
                
                icon_layout.addWidget(icon_label)
                icon_layout.setAlignment(Qt.AlignCenter)
                icon_widget.setLayout(icon_layout)
                
                self.tableWidget.setCellWidget(i, 1, icon_widget)
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
        # 메시지 초기화
        for i in range(1, 10):
            setattr(self, f"step{i}_msg", "")
        # 테이블 아이콘 초기화
        for i in range(self.tableWidget.rowCount()):
            icon_widget = QWidget()
            icon_layout = QHBoxLayout()
            icon_layout.setContentsMargins(0, 0, 0, 0)
            
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(self.img_none).pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
            
            icon_layout.addWidget(icon_label)
            icon_layout.setAlignment(Qt.AlignCenter)
            icon_widget.setLayout(icon_layout)
            
            self.tableWidget.setCellWidget(i, 1, icon_widget)

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