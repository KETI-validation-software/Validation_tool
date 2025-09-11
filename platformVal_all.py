# 물리보안 통합플랫폼 검증 소프트웨어
# physical security integrated platform validation software
# 아직 UI 수정 안됌

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
        
        # 3열 테이블
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
        self.auth_flag = True  # CONSTANTS.py에서 인증 정보를 가져오므로 True로 설정
        self.Server = Server

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

            if time_interval < 5:  # CONSTANTS에서 기본 timeout 값 사용
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
                                            # 기본값: CONSTANTS.py에서 URL 사용
                                            webhook_url = CONSTANTS.url
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

            elif time_interval > 5 and self.cnt == self.cnt_pre:  # CONSTANTS에서 기본 timeout 값 사용
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
    
    def load_test_info_from_constants(self):
        """CONSTANTS.py에서 시험정보를 로드 (읽기 전용)"""
        return [
            ("기업명", CONSTANTS.company_name),
            ("제품명", CONSTANTS.product_name),
            ("버전", CONSTANTS.version),
            ("시험유형", CONSTANTS.test_category),
            ("시험대상", CONSTANTS.test_target),
            ("시험범위", CONSTANTS.test_range),
            ("사용자 인증 방식", CONSTANTS.auth_type),
            ("관리자 코드", CONSTANTS.admin_code),
            ("시험 접속 정보", CONSTANTS.url)
        ]

    def initUI(self):
        # 최상위 레이아웃 - 2열로 구성 (temp와 동일)
        outerLayout = QHBoxLayout()  # 전체를 가로 2열로 변경
        leftLayout = QVBoxLayout()   # 왼쪽 열: 시험정보 + 버튼들
        rightLayout = QVBoxLayout()  # 오른쪽 열: 평가점수 + 시험결과 + 모니터링
        
        empty = QLabel(" ")
        empty.setStyleSheet('font-size:5pt')
        
        # ==================== 왼쪽 열 구성 ====================
        leftLayout.addWidget(empty)  # empty
        
        # 시험 정보 테이블 (세로 컬럼 형태) - CONSTANTS.py에서 동적으로 로드
        self.settingGroup = QGroupBox("시험정보")
        self.settingGroup.setMaximumWidth(460)  # temp와 동일한 너비
        
        # 시험 정보 위젯 생성 (temp와 동일한 구조)
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
        
        # 테이블 전체를 읽기 전용으로 설정
        self.info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # 각 행의 높이를 조정하여 모든 내용이 보이도록 설정
        for i in range(9):
            self.info_table.setRowHeight(i, 40)  # 각 행 높이를 40px로 설정
        
        # CONSTANTS.py에서 테이블 데이터 로드
        table_data = self.load_test_info_from_constants()
        
        # 테이블에 데이터 입력 (모두 읽기 전용)
        for row, (label, value) in enumerate(table_data):
            # 첫 번째 컬럼 (항목명) - 회색 배경
            item_label = QTableWidgetItem(label)
            item_label.setFlags(Qt.ItemIsEnabled)  # 편집 불가
            item_label.setBackground(QColor(240, 240, 240))  # 회색 배경
            self.info_table.setItem(row, 0, item_label)
            
            # 두 번째 컬럼 (내용) - 흰색 배경, 읽기 전용
            item_value = QTableWidgetItem(str(value))
            item_value.setFlags(Qt.ItemIsEnabled)  # 편집 불가
            item_value.setBackground(QColor(255, 255, 255))  # 흰색 배경
            self.info_table.setItem(row, 1, item_value)
        
        # 테이블 레이아웃
        settingLayout = QVBoxLayout()
        settingLayout.addWidget(self.info_table)
        self.settingGroup.setLayout(settingLayout)
        
        # 검증 버튼들 (temp와 동일한 구조)
        buttonGroup = QWidget()  # QGroupBox에서 QWidget으로 변경
        buttonGroup.setMaximumWidth(500)  # 가로 배치에 맞게 너비 증가
        buttonLayout = QHBoxLayout()  # 세로에서 가로로 변경
        
        self.sbtn = QPushButton(self)
        self.sbtn.setText('평가 시작')
        self.sbtn.setFixedSize(140, 50)  # temp와 동일한 크기
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
        self.stop_btn.setFixedSize(140, 50)  # temp와 동일한 크기
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
        
        # ------------------ 종료 버튼 ------------------------
        self.rbtn = QPushButton(self)
        self.rbtn.setText('종료')
        self.rbtn.setFixedSize(140, 50)  # temp와 동일한 크기
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
        
        buttonLayout.addStretch()  # 왼쪽 여백 추가로 중앙 정렬
        buttonLayout.addWidget(self.sbtn)
        buttonLayout.addSpacing(20)  # 버튼 사이에 20px 간격 추가
        buttonLayout.addWidget(self.stop_btn)
        buttonLayout.addSpacing(20)  # 버튼 사이에 20px 간격 추가
        buttonLayout.addWidget(self.rbtn)
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
        contentWidget.setMaximumSize(1050, 400)  # temp와 유사한 크기
        contentWidget.setMinimumSize(950, 300)
        rightLayout.addWidget(contentWidget)
        
        rightLayout.addSpacing(15)
        
        # 수신 메시지 실시간 모니터링
        rightLayout.addWidget(QLabel("수신 메시지 실시간 모니터링"))
        self.valResult = QTextBrowser(self)
        self.valResult.setMaximumHeight(200)
        self.valResult.setMaximumWidth(1050)  # temp와 유사한 크기
        self.valResult.setMinimumWidth(950)
        rightLayout.addWidget(self.valResult)
        
        # 전체 레이아웃 구성 (2열) - temp와 동일
        outerLayout.addLayout(leftLayout, 1)   # 왼쪽 열 (비율 1)
        outerLayout.addSpacing(20)  # 열 사이 간격
        outerLayout.addLayout(rightLayout, 2)  # 오른쪽 열 (비율 2, 더 넓게)
        self.setLayout(outerLayout)
        self.setWindowTitle('물리보안 통합플랫폼 연동 검증 소프트웨어')
        self.setGeometry(100, 100, 1600, 900)  # 2열 레이아웃에 맞게 너비를 더 크게 조정
        
        if not self.embedded:
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
        self.tableWidget.setColumnWidth(7, 150)  # 상세 내용 컬럼 너비 


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
        # 영상보안 시스템으로 고정되어 있고, CONSTANTS.py에서 인증 정보를 가져오므로
        # 별도의 검증 없이 바로 시작
        self.total_error_cnt = 0
        self.total_pass_cnt = 0
        # 평가 점수 디스플레이 초기화
        self.update_score_display()
        
        self.sbtn.setDisabled(True)
        self.stop_btn.setEnabled(True)

        # self.Server = api_server.Server# -> MyApp init()으로
        json_to_data(self.radio_check_flag)

        timeout = 5  # CONSTANTS에서 기본값 사용
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
        
        # CONSTANTS.py에서 URL 가져오기
        self.pathUrl = CONSTANTS.url

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

        # 기본값으로 LongPolling 사용
        self.Server.transProtocolInput = "LongPolling"

        self.valResult.append("Start Validation...\n")

        # CONSTANTS.py의 URL 사용
        url = CONSTANTS.url.split(":")
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
        self.Server.system = "video"  # 영상보안 시스템으로 고정
        
        self.r2 = CONSTANTS.auth_type
        if self.r2 == "Digest Auth":
            self.r2 = "D"
        elif self.r2 == "Bearer Token":
            self.r2 = "B"
        else:
            self.r2 = "None"

    def closeEvent(self, event):
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