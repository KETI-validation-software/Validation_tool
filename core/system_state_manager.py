from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import traceback
from core.logger import Logger

class SystemStateManager:
    """
    시스템 검증 상태 관리자 (저장/복원)
    SystemMainUI 및 MyApp의 데이터와 UI 상태를 저장하고 복원하는 책임을 담당
    """
    def __init__(self, main_window):
        self.main = main_window

    def save_current_spec_data(self):
        """현재 spec의 테이블 데이터와 상태를 저장"""
        if not hasattr(self.main, 'current_spec_id'):
            Logger.warning("[SAVE] current_spec_id가 없습니다.")
            return

        try:
            # 테이블 데이터 저장 (API 이름 포함)
            table_data = []
            for row in range(self.main.tableWidget.rowCount()):
                # ✅ videoMessages에서 실제 API 이름 가져오기
                if row < len(self.main.videoMessages):
                    api_name = self.main.videoMessages[row]
                else:
                    api_item = self.main.tableWidget.item(row, 1)  # API 명은 컬럼 1
                    api_name = api_item.text() if api_item else ""

                row_data = {
                    'api_name': api_name,
                    'icon_state': self._get_icon_state(row),
                    'retry_count': self.main.tableWidget.item(row, 3).text() if self.main.tableWidget.item(row, 3) else "0",
                    'pass_count': self.main.tableWidget.item(row, 4).text() if self.main.tableWidget.item(row, 4) else "0",
                    'total_count': self.main.tableWidget.item(row, 5).text() if self.main.tableWidget.item(row, 5) else "0",
                    'fail_count': self.main.tableWidget.item(row, 6).text() if self.main.tableWidget.item(row, 6) else "0",
                    'score': self.main.tableWidget.item(row, 7).text() if self.main.tableWidget.item(row, 7) else "0%",
                }
                table_data.append(row_data)

            # 전체 데이터 저장 (✅ 복합키 사용: group_id_spec_id)
            composite_key = f"{self.main.current_group_id}_{self.main.current_spec_id}"

            Logger.debug(f"[DEBUG] 💾 데이터 저장: {composite_key}")
            Logger.debug(f"[DEBUG]   - 테이블 행 수: {len(table_data)}")
            
            # self.main 속성 접근
            step_pass_counts = self.main.step_pass_counts[:] if hasattr(self.main, 'step_pass_counts') else []
            step_error_counts = self.main.step_error_counts[:] if hasattr(self.main, 'step_error_counts') else []
            
            Logger.debug(f"[DEBUG]   - step_pass_counts: {step_pass_counts}")
            Logger.debug(f"[DEBUG]   - step_error_counts: {step_error_counts}")

            self.main.spec_table_data[composite_key] = {
                'table_data': table_data,
                'step_buffers': [buf.copy() for buf in self.main.step_buffers] if self.main.step_buffers else [],
                'total_pass_cnt': self.main.total_pass_cnt,
                'total_error_cnt': self.main.total_error_cnt,
                # ✅ step_pass_counts와 step_error_counts 배열도 저장
                'step_pass_counts': step_pass_counts,
                'step_error_counts': step_error_counts,
                # ✅ 선택 필드 통과/에러 수도 저장
                'step_opt_pass_counts': self.main.step_opt_pass_counts[:] if hasattr(self.main, 'step_opt_pass_counts') else [],
                'step_opt_error_counts': self.main.step_opt_error_counts[:] if hasattr(self.main, 'step_opt_error_counts') else [],
                # ✅ 현재 진행 상태 저장 (cnt, current_retry)
                'cnt': self.main.cnt if hasattr(self.main, 'cnt') else 0,
                'current_retry': self.main.current_retry if hasattr(self.main, 'current_retry') else 0,
            }

            Logger.info(f"[SAVE] ✅ {composite_key} 데이터 저장 완료")

        except Exception as e:
            Logger.error(f"[ERROR] save_current_spec_data 실패: {e}")
            Logger.error(traceback.format_exc())

    def _get_icon_state(self, row):
        """테이블 행의 아이콘 상태 반환 (PASS/FAIL/NONE)"""
        icon_widget = self.main.tableWidget.cellWidget(row, 2)  # 아이콘은 컬럼 2
        if icon_widget:
            icon_label = icon_widget.findChild(QLabel)
            if icon_label:
                tooltip = icon_label.toolTip()
                if "PASS" in tooltip:
                    return "PASS"
                elif "FAIL" in tooltip:
                    return "FAIL"
        return "NONE"

    def restore_spec_data(self, spec_id):
        """저장된 spec 데이터 복원 (✅ 복합키 사용)"""
        composite_key = f"{self.main.current_group_id}_{spec_id}"
        Logger.debug(f"[DEBUG] 📂 데이터 복원 시도: {composite_key}")

        if composite_key not in self.main.spec_table_data:
            Logger.debug(f"[DEBUG] ❌ {composite_key} 저장된 데이터 없음 - 초기화 필요")
            return False

        saved_data = self.main.spec_table_data[composite_key]
        
        # ✅ 방어 로직: 저장된 데이터의 API 개수/이름이 현재와 다르면 복원 취소
        saved_api_list = [row['api_name'] for row in saved_data['table_data']]
        if len(saved_api_list) != len(self.main.videoMessages):
             Logger.warning(f"[RESTORE] ⚠️ 데이터 불일치: 저장된 API 개수({len(saved_api_list)}) != 현재 API 개수({len(self.main.videoMessages)}) -> 복원 취소")
             # 데이터가 맞지 않으면 해당 키 삭제하여 꼬임 방지
             del self.main.spec_table_data[composite_key]
             return False

        Logger.debug(f"[DEBUG] ✅ 저장된 데이터 발견!")
        Logger.debug(f"[DEBUG]   - 테이블 행 수: {len(saved_data['table_data'])}")
        
        # 테이블 복원
        table_data = saved_data['table_data']
        for row, row_data in enumerate(table_data):
            if row >= self.main.tableWidget.rowCount():
                Logger.warning(f"[RESTORE] 경고: row={row}가 범위 초과, 건너뜀")
                break
# ... (생략)
        # ✅ 현재 진행 상태 복원 (cnt, current_retry)
        self.main.cnt = saved_data.get('cnt', 0)
        self.main.current_retry = saved_data.get('current_retry', 0)

        Logger.info(f"[RESTORE] {spec_id} 데이터 복원 완료 (cnt={self.main.cnt}, current_retry={self.main.current_retry})")
        return True