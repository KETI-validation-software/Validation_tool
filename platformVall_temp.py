


#################### 임시 화면 -> ui 보여주기만을 위한 파일 ####################
#################### 제대로 작동되지 않습니다 (여기 파일에다가 기능 작업x) ####################

from api.api_server import Server
import time
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor
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
        icon_item = QTableWidgetItem()
        icon_item.setIcon(QIcon(img))
        icon_item.setToolTip(msg)
        # 아이콘을 가운데 정렬
        icon_item.setTextAlignment(Qt.AlignCenter)
        if self.cnt < self.tableWidget.rowCount():
            self.tableWidget.setItem(self.cnt, 1, icon_item)
            # 메시지 저장 (팝업용)
            setattr(self, f"step{self.cnt+1}_msg", msg)

    def initUI(self):

        # 최상위 레이아웃 - 2열로 구성
        outerLayout = QHBoxLayout()  # 전체를 가로 2열로 변경
        leftLayout = QVBoxLayout()   # 왼쪽 열: 시험정보 + 버튼들
        rightLayout = QVBoxLayout()  # 오른쪽 열: 평가점수 + 시험결과 + 모니터링
        
        empty = QLabel(" ")
        empty.setStyleSheet('font-size:5pt')
        
        # ==================== 왼쪽 열 구성 ====================
        leftLayout.addWidget(empty)  # empty
        
        # 시험 정보 테이블 (세로 컬럼 형태)
        self.settingGroup = QGroupBox("시험정보")
        self.settingGroup.setMaximumWidth(460)  # 테이블 너비 조정
        
        # 시험 정보 위젯 생성하는 부분 -> 간격 조절하는거 여기서 하기
        self.info_table = QTableWidget(9, 2)  # 9행 2열 (항목명, 값)
        self.info_table.setMaximumWidth(460)
        self.info_table.setFixedHeight(386)  # 고정 높이로 설정하여 스크롤 완전 제거
        self.info_table.setHorizontalHeaderLabels(["항목", "내용"])
        self.info_table.setColumnWidth(0, 150)  # 첫 번째 열 너비 고정
        self.info_table.setColumnWidth(1, 288)  # 두 번째 열 너비 고정
        
        # 스크롤바 완전 제거
        self.info_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.info_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 테이블 행 레이블 숨기기
        self.info_table.verticalHeader().setVisible(False)
        
        # 각 행의 높이를 조정하여 모든 내용이 보이도록 설정
        for i in range(9):
            self.info_table.setRowHeight(i, 40)  # 각 행 높이를 40px로 설정 (세로 간격 증가)
        
        # 테이블 내용 설정
        table_data = [
            ("기업명", "Company"),
            ("제품명", "DEVICE-01"),
            ("버전", "2"),
            ("시험유형", "사전 시험"),
            ("시험대상", "통합시스템"),
            ("시험범위", "전체"),
            ("사용자 인증 방식", "Digest Auth"),
            ("관리자 코드", "00153250"),
            ("시험 접속 정보", "192.168.0.1:8080")
        ]
        
        # 테이블에 데이터 입력
        for row, (label, value) in enumerate(table_data):
            # 첫 번째 컬럼 (항목명) - 읽기 전용
            item_label = QTableWidgetItem(label)
            item_label.setFlags(Qt.ItemIsEnabled)  # 편집 불가
            item_label.setBackground(QColor(240, 240, 240))  # 회색 배경
            self.info_table.setItem(row, 0, item_label)
            
            # 두 번째 컬럼 (내용) - 편집 가능
            item_value = QTableWidgetItem(value)
            self.info_table.setItem(row, 1, item_value)
        
        # 테이블 레이아웃
        settingLayout = QVBoxLayout()
        settingLayout.addWidget(self.info_table)
        self.settingGroup.setLayout(settingLayout)
        
        # 기존 그룹들 (메시지 송수신, 연동 시스템)
        # self.messageGroup = QGroupBox("메시지 송수신")
        # self.messageGroup.setMaximumWidth(300)
        # messageLayout = QVBoxLayout()
        # # messageLayout.addWidget(self.group3())  # 메시지 송수신
        # messageLayout.addWidget(self.group1())  # 연동 시스템
        # self.messageGroup.setLayout(messageLayout)
        
        # 검증 버튼들 (테두리 없는 컨테이너로 변경)
        buttonGroup = QWidget()  # QGroupBox에서 QWidget으로 변경
        buttonGroup.setMaximumWidth(500)  # 가로 배치에 맞게 너비 증가
        buttonLayout = QHBoxLayout()  # 세로에서 가로로 변경
        
        self.sbtn = QPushButton(self)
        self.sbtn.setText('평가 시작')
        self.sbtn.setFixedSize(140, 50)  # 버튼 크기를 더 크게 (너비 140, 높이 50)
        self.sbtn.clicked.connect(self.sbtn_push)

        self.stop_btn = QPushButton(self)
        self.stop_btn.setText('일시 정지')
        self.stop_btn.setFixedSize(140, 50)  # 버튼 크기를 더 크게 (너비 140, 높이 50)
        self.stop_btn.clicked.connect(self.stop_btn_clicked)
        self.stop_btn.setDisabled(True)
        
        buttonLayout.addStretch()  # 왼쪽 여백 추가로 중앙 정렬
        buttonLayout.addWidget(self.sbtn)
        buttonLayout.addSpacing(20)  # 버튼 사이에 20px 간격 추가
        buttonLayout.addWidget(self.stop_btn)
        buttonLayout.addStretch()  # 오른쪽 여백 추가로 중앙 정렬
        buttonGroup.setLayout(buttonLayout)
        
        # 왼쪽 열에 시험정보와 버튼들 추가
        leftLayout.addWidget(self.settingGroup)
        leftLayout.addSpacing(300)  # 시험정보와 버튼 사이 간격을 300px로 설정
        leftLayout.addWidget(buttonGroup)
        leftLayout.addStretch()  # 남은 공간을 아래쪽으로 밀어내기
        
        # ==================== 오른쪽 열 구성 ====================
        # 평가 점수
        rightLayout.addWidget(self.group_score())
        rightLayout.addSpacing(15)
        
        # 시험 결과
        self.valmsg = QLabel('시험 결과', self)
        rightLayout.addWidget(self.valmsg)
        self.init_centerLayout()
        
        # 시험 결과 영역을 테이블 크기에 맞게 조정
        contentWidget = QWidget()
        contentWidget.setLayout(self.centerLayout)
        contentWidget.setMaximumSize(1000, 400)
        contentWidget.setMinimumSize(900, 300)
        rightLayout.addWidget(contentWidget)
        
        rightLayout.addSpacing(15)
        
        # 수신 메시지 실시간 모니터링
        rightLayout.addWidget(QLabel("수신 메시지 실시간 모니터링"))
        self.valResult = QTextBrowser(self)
        self.valResult.setMaximumHeight(200)
        self.valResult.setMaximumWidth(1000)
        self.valResult.setMinimumWidth(900)
        rightLayout.addWidget(self.valResult)
        
        # 변수 초기화
        self.r1 = ""
        self.r2 = ""
        
        # 전체 레이아웃 구성 (2열) ---------------------------------
        outerLayout.addLayout(leftLayout, 1)   # 왼쪽 열 (비율 1)
        outerLayout.addSpacing(20)  # 열 사이 간격
        outerLayout.addLayout(rightLayout, 2)  # 오른쪽 열 (비율 2, 더 넓게)
        self.setLayout(outerLayout)
        self.setWindowTitle('물리보안 통합플랫폼 연동 검증 소프트웨어 - 임시 화면')
        self.setGeometry(100, 100, 1600, 900)  # 2열 레이아웃에 맞게 너비를 더 크게 조정
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
        self.tableWidget.setMinimumSize(900, 310)  # 최소 크기 설정
        self.tableWidget.resize(1000, 410)  # 기본 크기 설정 (여백을 고려해서 50px 증가)
        
        # 컬럼 너비 설정
        self.tableWidget.setColumnWidth(0, 273)  # API 명 컬럼 너비 (20px 줄임)
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
            # 결과 아이콘
            icon_item = QTableWidgetItem()
            icon_item.setIcon(QIcon(self.img_none))
            icon_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(i, 1, icon_item)
            # 검증 횟수
            self.tableWidget.setItem(i, 2, QTableWidgetItem("0"))
            self.tableWidget.item(i, 2).setTextAlignment(Qt.AlignCenter)
            # 실패 횟수
            self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
            self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
            # 평가 점수
            self.tableWidget.setItem(i, 4, QTableWidgetItem("0%"))
            self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)
            # 메시지 데이터 버튼 (중앙 정렬을 위한 위젯 컨테이너)
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

    def show_detail_result(self, row):
        """상세 결과 확인 버튼 클릭 시 호출되는 함수 (메시지 데이터)"""
        msg = getattr(self, f"step{row+1}_msg", "") # 얘는 아래 수신 메시지 실시간 모니터링에 뜨는 메시지
        if msg:
            CustomDialog(msg, self.tableWidget.item(row, 0).text())
        else:
            CustomDialog("아직 검증 결과가 없습니다.", self.tableWidget.item(row, 0).text())

    def show_schema_result(self, row):
        """메시지 규격 확인 버튼 클릭 시 호출되는 함수"""
        # 임시로 스키마 정보 표시
        schema_msg = f"API {row+1}의 메시지 규격 정보입니다.\n\n규격 스키마가 여기에 표시됩니다."
        CustomDialog(schema_msg, f"{self.tableWidget.item(row, 0).text()} - 메시지 규격")

    def show_error_result(self, row):
        """메시지 오류 확인 버튼 클릭 시 호출되는 함수"""
        # 임시로 오류 정보 표시
        error_msg = f"API {row+1}의 메시지 오류 정보입니다.\n\n오류 세부사항이 여기에 표시됩니다."
        CustomDialog(error_msg, f"{self.tableWidget.item(row, 0).text()} - 메시지 오류")

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
        rgroup = QGroupBox('사용자 인증 방식')
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

    # def group3(self):
    #     fgroup = QGroupBox('메시지 송수신')
    #     fgroup.setMaximumWidth(200)  # 메시지 송수신 박스 너비 제한
        
    #     self.protocol_widget = QComboBox()
    #     self.protocol_widget.addItem("LongPolling")
    #     self.protocol_widget.addItem("WebHook")
    #     self.timeOut_widget = QSpinBox()
    #     self.timeOut_widget.setValue(5)
    #     self.timeOut_widget.setMaximum(1000)

    #     flayout = QFormLayout()
    #     flayout.addRow("transProtocol  ", self.protocol_widget)
    #     flayout.addRow("timeOut(sec):  ", self.timeOut_widget)

    #     fgroup.setLayout(flayout)
    #     return fgroup

    def group4(self):
        fgroup = QGroupBox('시험 URL')
        fgroup.setMaximumWidth(150)  # 시험 URL 박스 너비 제한

        self.linkUrl = QLineEdit(self)
        self.linkUrl.setText("https://127.0.0.1:8008")
        self.linkUrl.setMaximumWidth(130)  # URL 입력 필드 너비 제한

        layout = QVBoxLayout()
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
                # 결과 아이콘
                icon_item = QTableWidgetItem()
                icon_item.setIcon(QIcon(self.img_none))
                icon_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(i, 1, icon_item)
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
                # 결과 아이콘
                icon_item = QTableWidgetItem()
                icon_item.setIcon(QIcon(self.img_none))
                icon_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(i, 1, icon_item)
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
                # 결과 아이콘
                icon_item = QTableWidgetItem()
                icon_item.setIcon(QIcon(self.img_none))
                icon_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(i, 1, icon_item)
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
                icon_item = QTableWidgetItem()
                icon_item.setIcon(QIcon(self.img_none))
                icon_item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(i, 1, icon_item)
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
            icon_item = QTableWidgetItem()
            icon_item.setIcon(QIcon(self.img_none))
            icon_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(i, 1, icon_item)

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
        
        # 시스템 설정
        self.Server.system = self.setting_variables.value('system')
        if hasattr(self, 'g1_radio1') and self.Server.system == "video":
            self.g1_radio1.setChecked(True)
        elif hasattr(self, 'g1_radio2') and self.Server.system == "bio":
            self.g1_radio2.setChecked(True)
        elif hasattr(self, 'g1_radio3') and self.Server.system == "security":
            self.g1_radio3.setChecked(True)

        # 인증 설정
        self.r2 = self.setting_variables.value('auth')
        if hasattr(self, 'g2_radio1') and self.r2 == "D":
            self.g2_radio1.setChecked(True)
        elif hasattr(self, 'g2_radio2') and self.r2 == "B":
            self.g2_radio2.setChecked(True)
        elif hasattr(self, 'g2_radio3') and self.r2 == "None":
            self.g2_radio3.setChecked(True)

        # URL 설정
        tmp = self.setting_variables.value('linkUrl')
        if tmp is None:
            tmp = "https://127.0.0.1:8008"
        if hasattr(self, 'linkUrl'):
            self.linkUrl.setText(tmp)
            
        # 타임아웃 설정
        try:
            tmp = self.setting_variables.value('timeOut')
            if hasattr(self, 'timeOut_widget'):
                self.timeOut_widget.setValue(int(tmp))
        except (TypeError, ValueError):  # None 또는 잘못된 값
            if hasattr(self, 'timeOut_widget'):
                self.timeOut_widget.setValue(5)

        # 프로토콜 설정
        try:
            saved_idx = self.setting_variables.value('protocolWidget', 0, int)
            if hasattr(self, 'protocol_widget'):
                self.protocol_widget.setCurrentIndex(saved_idx)
        except (TypeError, ValueError):
            pass

    def closeEvent(self, event):
        if hasattr(self, 'setting_variables'):
            self.setting_variables.setValue('system', self.Server.system)
            if hasattr(self, 'r2'):
                self.setting_variables.setValue('auth', self.r2)
            if hasattr(self, 'timeOut_widget'):
                self.setting_variables.setValue('timeOut', self.timeOut_widget.text())
            if hasattr(self, 'linkUrl'):
                self.setting_variables.setValue('linkUrl', self.linkUrl.text())
            if hasattr(self, 'protocol_widget'):
                self.setting_variables.setValue('protocolWidget', self.protocol_widget.currentIndex())
        event.accept()


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