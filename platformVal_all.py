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
import config.CONSTANTS as CONSTANTS

from core.functions import json_check_, save_result, resource_path, field_finder, json_to_data, set_auth, timeout_field_finder 
from core.json_checker_new import check_message_data, check_message_schema, check_message_error 

from http.server import HTTPServer
import json
import traceback
import warnings
warnings.filterwarnings('ignore')

#  from charset_normalizer import md__mypyc  # A library that helps you read text from an unknown charset encoding


# 통합된 상세 내용 확인 팝업창 클래스 (세가지 내용 다 들어가있어야함)
class CombinedDetailDialog(QDialog):
    def __init__(self, api_name, step_buffer, schema_data):
        super().__init__()
        
        self.setWindowTitle(f"{api_name} - 통합 상세 정보")
        self.setGeometry(400, 300, 1200, 600)  # 가로로 넓게 설정
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # 전체 레이아웃
        main_layout = QVBoxLayout()
        
        # 상단 제목
        title_label = QLabel(f"{api_name} API 상세 정보")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 3열 테이블 형태로 배치
        content_layout = QHBoxLayout()
        
        # 1열: 메시지 데이터
        data_group = QGroupBox("메시지 데이터")
        data_layout = QVBoxLayout()
        self.data_browser = QTextBrowser()
        self.data_browser.setAcceptRichText(True)
        data_text = step_buffer["data"] if step_buffer["data"] else "아직 수신된 데이터가 없습니다."
        self.data_browser.setPlainText(data_text)
        data_layout.addWidget(self.data_browser)
        data_group.setLayout(data_layout)
        
        # 2열: 메시지 규격
        schema_group = QGroupBox("메시지 규격")
        schema_layout = QVBoxLayout()
        self.schema_browser = QTextBrowser()
        self.schema_browser.setAcceptRichText(True)
        schema_text = self._format_schema(schema_data)
        self.schema_browser.setPlainText(schema_text)
        schema_layout.addWidget(self.schema_browser)
        schema_group.setLayout(schema_layout)
        
        # 3열: 검증 오류
        error_group = QGroupBox("검증 오류")
        error_layout = QVBoxLayout()
        self.error_browser = QTextBrowser()
        self.error_browser.setAcceptRichText(True)
        result = step_buffer["result"]
        error_text = step_buffer["error"] if step_buffer["error"] else ("오류가 없습니다." if result=="PASS" else "")
        error_msg = f"검증 결과: {result}\n\n"
        if result == "FAIL":
            error_msg += "오류 세부사항:\n" + error_text
        else:
            error_msg += "오류가 없습니다."
        self.error_browser.setPlainText(error_msg)
        error_layout.addWidget(self.error_browser)
        error_group.setLayout(error_layout)
        
        # 3개 그룹을 가로로 배치
        content_layout.addWidget(data_group)
        content_layout.addWidget(schema_group)
        content_layout.addWidget(error_group)
        
        # 확인 버튼
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        
        # 레이아웃 구성
        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.buttonBox)
        
        self.setLayout(main_layout)
        
    def _format_schema(self, schema):
        """스키마 구조를 문자열로 변환"""
        if not schema:
            return "스키마 정보가 없습니다."
            
        def schema_to_string(schema_obj, indent=0):
            result = ""
            spaces = "  " * indent
            
            if isinstance(schema_obj, dict):
                for key, value in schema_obj.items():
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
        
        return schema_to_string(schema)


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
        self.radio_check_flag = "video"  # 영상보안 시스템으로 고정
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
        self.valCnt = 0  # 검증 횟수 카운터 추가
        # 스텝별 표시할 버퍼 (데이터, 오류, 결과)
        self.step_buffers = [
            {"data": "", "error": "", "result": "PASS"} for _ in range(9)
        ]
        self.get_setting()

        with open(resource_path("spec/rows.json"), "w") as out_file:
            json.dump(None, out_file, ensure_ascii=False)


    def _to_detail_text(self, val_text):
        """검증 결과 텍스트를 항상 사람이 읽을 문자열로 표준화"""
        if val_text is None:
            return "오류가 없습니다."
        if isinstance(val_text, list):
            return "\n".join(str(x) for x in val_text) if val_text else "오류가 없습니다."
        if isinstance(val_text, dict):
            try:
                import json
                return json.dumps(val_text, indent=2, ensure_ascii=False)
            except Exception:
                return str(val_text)
        return str(val_text)

    def update_table_row(self, row, result, pass_count, error_count, data, error_text):
        """테이블 행 업데이트 (아이콘, 통과/전체 필드 수 포함)"""
        if row >= self.tableWidget.rowCount():
            return
            
        # 아이콘 업데이트
        msg, img = self.icon_update_step(data, result, error_text)
        
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
        
        self.tableWidget.setCellWidget(row, 1, icon_widget)
        
        # 검증 횟수 업데이트 (기본 1회)
        self.tableWidget.setItem(row, 2, QTableWidgetItem("1"))
        self.tableWidget.item(row, 2).setTextAlignment(Qt.AlignCenter)
        
        # 통과 필드 수 업데이트
        self.tableWidget.setItem(row, 3, QTableWidgetItem(str(pass_count)))
        self.tableWidget.item(row, 3).setTextAlignment(Qt.AlignCenter)
        
        # 전체 필드 수 업데이트
        total_fields = pass_count + error_count
        self.tableWidget.setItem(row, 4, QTableWidgetItem(str(total_fields)))
        self.tableWidget.item(row, 4).setTextAlignment(Qt.AlignCenter)
        
        # 실패 횟수 업데이트
        self.tableWidget.setItem(row, 5, QTableWidgetItem(str(error_count)))
        self.tableWidget.item(row, 5).setTextAlignment(Qt.AlignCenter)
        
        # 평가 점수 업데이트
        if total_fields > 0:
            score = (pass_count / total_fields) * 100
            self.tableWidget.setItem(row, 6, QTableWidgetItem(f"{score:.1f}%"))
        else:
            self.tableWidget.setItem(row, 6, QTableWidgetItem("0%"))
        self.tableWidget.item(row, 6).setTextAlignment(Qt.AlignCenter)
        
        # 메시지 저장 (팝업용)
        setattr(self, f"step{row+1}_msg", msg)

    # 실시간 모니터링용
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

                    # ▼ 추가: 이 스텝에서 합칠 버퍼들
                    combined_data_parts = []    # 화면/버튼 "데이터"에 넣을 JSON 문자열들
                    combined_error_parts = []   # 화면/버튼 "오류"에 넣을 오류 문자열들
                    step_result = "PASS"        # 입력/웹훅 둘 중 하나라도 FAIL이면 FAIL
                    add_pass = 0
                    add_err = 0

                    val_result = ""
                    val_text = ""
                    key_psss_cnt = 0
                    key_error_cnt = 0
                    if self.Server.message[self.cnt] in CONSTANTS.none_request_message:
                        tmp_res_auth = json.dumps(data, indent=4, ensure_ascii=False)
                        combined_data_parts.append(tmp_res_auth)

                        if (len(data) != 0) and data != "{}":
                            step_result = "FAIL"
                            add_err = 1
                            combined_error_parts.append("[None Request] 데이터가 있으면 안 됩니다.")
                        elif (len(data) == 0) or data == "{}":
                            step_result = "PASS"
                            add_pass = 1

                    else:
                        #print("통플검증sw이 받은 ->", data)
                        # 입력 데이터 수집
                        tmp_res_auth = json.dumps(data, indent=4, ensure_ascii=False)
                        combined_data_parts.append(tmp_res_auth)
                        
                        # do_chcker 호출 1번
                        val_result, val_text, key_psss_cnt, key_error_cnt = json_check_(self.Server.inSchema[self.cnt],
                                                                                    data, self.flag_opt)
                        add_pass += key_psss_cnt
                        add_err += key_error_cnt
                        
                        inbound_err_txt = self._to_detail_text(val_text)
                        if val_result == "FAIL":
                            step_result = "FAIL"
                            combined_error_parts.append("[Inbound] " + inbound_err_txt)
#############################################################################################################
 # 아래 수정중

                        if "Realtime" in str(self.Server.message[self.cnt]):  # realtime 어찌구인지 확인해야함
                            if "Webhook".lower() in str(data).lower():
                                try:
                                    # 방어적으로 Webhook URL이 잘못된 경우 기본값을 넣어줌
                                    webhook_json_path = resource_path(
                                        "spec/" + self.Server.system + "/" + "webhook_" + self.Server.message[self.cnt] + ".json")
                                    with open(webhook_json_path, "r", encoding="UTF-8") as out_file2:
                                        self.realtime_flag = True
                                        webhook_data = json.load(out_file2)
                                        # Webhook URL 필드명 추정: transProtocolDesc 또는 url 등
                                        # video 모드에서 8번째 이후 메시지에서 잘못된 값이 들어오는 경우 방어
                                        webhook_url = None
                                        # 1. transProtocolDesc가 있으면 검사
                                        if isinstance(webhook_data, dict):
                                            for k in webhook_data:
                                                if k.lower() in ["transprotocoldesc", "url", "webhookurl"]:
                                                    webhook_url = webhook_data[k]
                                                    break
                                        # 2. 잘못된 값이면 기본값으로 대체
                                        if webhook_url in [None, '', 'desc', 'none', 'None'] or (isinstance(webhook_url, str) and not webhook_url.lower().startswith(('http://', 'https://'))):
                                            # 기본값: 현재 입력된 self.linkUrl 값 사용
                                            webhook_url = self.linkUrl.text()
                                            # 실제로도 대입
                                            for k in webhook_data:
                                                if k.lower() in ["transprotocoldesc", "url", "webhookurl"]:
                                                    webhook_data[k] = webhook_url
                                        # 3. 만약 그래도 url이 없으면 아예 Webhook 검증을 skip
                                        if webhook_url in [None, '', 'desc', 'none', 'None']:
                                            pass  # Webhook 검증 스킵
                                        else:
                                            # Webhook 데이터 수집 (UI 갱신 없이)
                                            tmp_webhook_data = json.dumps(webhook_data, indent=4, ensure_ascii=False)
                                            webhook_val_result, webhook_val_text, webhook_key_psss_cnt, webhook_key_error_cnt = json_check_(
                                                self.Server.outSchema[-1], webhook_data, self.flag_opt
                                            )
                                            
                                            combined_data_parts.append("\n--- Webhook ---\n" + tmp_webhook_data)
                                            
                                            add_pass += webhook_key_psss_cnt
                                            add_err += webhook_key_error_cnt
                                            
                                            webhook_err_txt = self._to_detail_text(webhook_val_text)
                                            if webhook_val_result == "FAIL":
                                                step_result = "FAIL"
                                                combined_error_parts.append("[Webhook] " + webhook_err_txt)
                                
                                except json.JSONDecodeError as verr:
                                    box = QMessageBox()
                                    box.setIcon(QMessageBox.Critical)
                                    box.setInformativeText(str(verr))
                                    box.setWindowTitle("Error")
                                    box.exec_()
                                    return ""

                    # (1) 스텝 버퍼 저장
                    data_text = "\n".join(combined_data_parts) if combined_data_parts else "아직 수신된 데이터가 없습니다."
                    error_text = "\n".join(combined_error_parts) if combined_error_parts else "오류가 없습니다."
                    self.step_buffers[self.cnt]["data"] = data_text
                    self.step_buffers[self.cnt]["error"] = error_text
                    self.step_buffers[self.cnt]["result"] = step_result

                    # (2) 아이콘/툴팁 갱신 (툴팁 길이 줄이려면 data_text 대신 tmp_res_auth만 써도 OK)
                    if combined_data_parts:
                        tmp_res_auth = combined_data_parts[0]  # 첫 번째 데이터 사용 (inbound data)
                    else:
                        tmp_res_auth = "No data"
                    
                    # 테이블 업데이트 (통과/전체 필드 수 포함)
                    self.update_table_row(self.cnt, step_result, add_pass, add_err, tmp_res_auth, error_text)

                    # (3) 모니터링 창에는 '한 번만' 붙이기 (입력 + (있다면) Webhook까지 합쳐진 data_text를 보여줌)
                    self.valResult.append(message_name)
                    self.valResult.append("\n" + data_text)
                    self.valResult.append(step_result)

                    # (4) 누적 점수 업데이트 (한 번만)
                    self.total_error_cnt += add_err
                    self.total_pass_cnt += add_pass

                    self.update_score_display()
                    self.valResult.append(
                        "Score : " + str((self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                    self.valResult.append(
                        "Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(self.total_error_cnt) + "(누적 오류 필드 수)\n")
                    
                    self.cnt += 1
                self.realtime_flag = False

            elif time_interval > int(self.timeOut_widget.text()) and self.cnt == self.cnt_pre:
                # self.valResult.append(self.Server.message[self.cnt])
                message_name = "step " + str(self.cnt + 1) + ": " + self.Server.message[self.cnt]
                
                # message missing인 경우에 대해서도 버퍼에 업데이트 -> 오류니까
                self.step_buffers[self.cnt]["data"] = "아직 수신된 데이터가 없습니다."
                self.step_buffers[self.cnt]["error"] = "Message Missing!"
                self.step_buffers[self.cnt]["result"] = "FAIL"

                self.valResult.append(message_name)
                self.valResult.append("Message Missing!")
                tmp_fields_rqd_cnt, tmp_fields_opt_cnt = timeout_field_finder(self.Server.inSchema[self.cnt])

                self.total_error_cnt += tmp_fields_rqd_cnt
                if tmp_fields_rqd_cnt == 0:  # {}인 경우 +1
                    self.total_error_cnt += 1
                if self.flag_opt:
                    self.total_error_cnt += tmp_fields_opt_cnt

                self.total_pass_cnt += 0
                
                # 평가 점수 디스플레이 업데이트
                self.update_score_display()
                
                self.valResult.append(
                    "Score : " + str((self.total_pass_cnt / (self.total_pass_cnt + self.total_error_cnt) * 100)))
                self.valResult.append("Score details : " + str(self.total_pass_cnt) + "(누적 통과 필드 수), " + str(
                    self.total_error_cnt) + "(누적 오류 필드 수)\n")
                
                # 테이블 업데이트 (Message Missing)
                add_err = tmp_fields_rqd_cnt if tmp_fields_rqd_cnt > 0 else 1
                if self.flag_opt:
                    add_err += tmp_fields_opt_cnt
                self.update_table_row(self.cnt, "FAIL", 0, add_err, "", "Message Missing!")
                
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
        self.score_label.setText(f"종합 평가 점수: {score:.1f}%")

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
        contentWidget.setMaximumSize(1050, 400)  # 테이블 크기와 동일하게 설정 (축소)
        contentWidget.setMinimumSize(950, 300)   # 테이블 최소 크기와 동일하게 설정 (축소)
        contentLayout.addWidget(contentWidget)

        # 하단 모니터링 레이아웃 구성 ---------------------------------
        bottomLayout.addWidget(QLabel("수신 메시지 실시간 모니터링"))
        self.valResult = QTextBrowser(self)
        self.valResult.setMaximumHeight(200)  # 높이 제한
        self.valResult.setMaximumWidth(1050)  # 테이블과 동일한 너비로 설정 (축소)
        self.valResult.setMinimumWidth(950)   # 테이블 최소 너비와 동일하게 설정 (축소)
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
        self.setGeometry(500, 300, 1050, 850)  # 창 크기 설정 (너비 축소)
        
        # showing all the widgets

        # self.json_th.json_update_data.connect(self.json_update_data)
        # self.json_th.start()
        if not self.embedded :
            self.show()

    def init_centerLayout(self):
        # 표 형태로 변경 (8컬럼으로 축소)
        self.tableWidget = QTableWidget(9, 8)
        self.tableWidget.setHorizontalHeaderLabels(["API 명", "결과", "검증 횟수", "통과 필드 수", "전체 필드 수", "실패 횟수", "평가 점수", "상세 내용"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableWidget.setIconSize(QtCore.QSize(16, 16))
        
        # 테이블 크기 설정
        self.tableWidget.setMinimumSize(950, 300)  # 최소 크기 조정
        self.tableWidget.resize(1050, 400)  # 기본 크기 조정
        
        # 컬럼 너비 설정
        self.tableWidget.setColumnWidth(0, 240)  # API 명 컬럼 너비 
        self.tableWidget.setColumnWidth(1, 90)   # 결과 컬럼 너비 
        self.tableWidget.setColumnWidth(2, 100)  # 검증 횟수 컬럼 너비 
        self.tableWidget.setColumnWidth(3, 110)  # 통과 필드 수 컬럼 너비 
        self.tableWidget.setColumnWidth(4, 110)  # 전체 필드 수 컬럼 너비 
        self.tableWidget.setColumnWidth(5, 100)  # 실패 횟수 컬럼 너비
        self.tableWidget.setColumnWidth(6, 110)  # 평가 점수 컬럼 너비
        self.tableWidget.setColumnWidth(7, 130)  # 상세 내용 컬럼 너비 (확장) 


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
            # 통과 필드 수
            self.tableWidget.setItem(i, 3, QTableWidgetItem("0"))
            self.tableWidget.item(i, 3).setTextAlignment(Qt.AlignCenter)
            # 전체 필드 수
            self.tableWidget.setItem(i, 4, QTableWidgetItem("0"))
            self.tableWidget.item(i, 4).setTextAlignment(Qt.AlignCenter)
            # 실패 횟수
            self.tableWidget.setItem(i, 5, QTableWidgetItem("0"))
            self.tableWidget.item(i, 5).setTextAlignment(Qt.AlignCenter)
            # 평가 점수
            self.tableWidget.setItem(i, 6, QTableWidgetItem("0%"))
            self.tableWidget.item(i, 6).setTextAlignment(Qt.AlignCenter)
            # 상세 결과 버튼 (중앙 정렬을 위한 위젯 컨테이너)
            detail_btn = QPushButton("상세 내용 확인")
            detail_btn.setMaximumHeight(30)
            detail_btn.setMaximumWidth(130)  # 버튼 최대 너비 증가
            detail_btn.clicked.connect(lambda checked, row=i: self.show_combined_result(row))
            
            # 버튼을 중앙에 배치하기 위한 위젯과 레이아웃
            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_btn)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(layout)
            
            self.tableWidget.setCellWidget(i, 7, container)

        # 결과 컬럼만 클릭 가능하도록 설정 (기존 기능 유지)
        self.tableWidget.cellClicked.connect(self.table_cell_clicked)
        
        # centerLayout을 초기화하고 테이블 추가
        self.centerLayout = QVBoxLayout()
        self.centerLayout.addWidget(self.tableWidget)


    def show_combined_result(self, row):
        """통합 상세 내용 확인 - 데이터, 규격, 오류를 모두 보여주는 3열 팝업"""
        try:
            buf = self.step_buffers[row]
            api_name = self.tableWidget.item(row, 0).text()
            
            # 스키마 데이터 가져오기
            try:
                schema_data = videoOutSchema[row] if row < len(videoOutSchema) else None
            except:
                schema_data = None
            
            # 통합 팝업창 띄우기
            dialog = CombinedDetailDialog(api_name, buf, schema_data)
            dialog.exec_()
            
        except Exception as e:
            CustomDialog(f"오류:\n{str(e)}", "상세 내용 확인 오류")


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
        self.g1_radio1.setChecked(True)  # 기본 선택

        vbox = QVBoxLayout()
        vbox.addWidget(self.g1_radio1)
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
        sgroup.setMaximumWidth(1050)  # 테이블과 동일한 너비로 설정 (축소)
        sgroup.setMinimumWidth(950)   # 테이블 최소 너비와 동일하게 설정 (축소)
        
        # 점수 표시용 레이블들
        self.pass_count_label = QLabel("통과 필드 수: 0")
        self.total_count_label = QLabel("전체 필드 수: 0")  
        self.score_label = QLabel("종합 평가 점수: 0%")
        
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
            # 테이블은 이미 초기화되어 있으므로 재설정하지 않음

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
            
            # 테이블 크기를 창 크기에 맞게 조정 (8컬럼에 맞게 너비 축소)
            table_width = min(max(500, window_width // 3), 700)  # 최소 500, 최대 700
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
            if self.r2 == "B":
                videoOutMessage[0]['accessToken'] = self.token
            self.Server.message = videoMessages
            self.Server.inMessage = videoInMessage
            self.Server.outMessage = videoOutMessage
            self.Server.inSchema = videoInSchema
            self.Server.outSchema = videoOutSchema
            self.Server.system = "video"
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

        # 버퍼 초기화
        self.step_buffers = [{"data": "", "result": "", "error": ""} for _ in range(9)]

        # josn 파일 초기화
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
        self.Server.system = "video"  # 영상보안 시스템으로 고정
        # 라디오 버튼은 이미 group1()에서 setChecked(True)로 설정됨

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