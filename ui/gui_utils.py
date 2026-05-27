from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTextBrowser, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QPoint, QObject, QEvent, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from core.functions import resource_path

# 팝업창과 같은 작은 것들

class WebhookBadgeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tooltip_window = None
        self.hover_image_path = resource_path("assets/image/icon/webhook_mousehover.png").replace("\\", "/")
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover)

    def enterEvent(self, event):
        if not self.tooltip_window:
            self.tooltip_window = QLabel(None, Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.tooltip_window.setAttribute(Qt.WA_TranslucentBackground)
            self.tooltip_window.setAttribute(Qt.WA_ShowWithoutActivating)
            
            pixmap = QPixmap(self.hover_image_path)
            if not pixmap.isNull():
                self.tooltip_window.setPixmap(pixmap)
                self.tooltip_window.setFixedSize(pixmap.size())
            else:
                self.tooltip_window.setText("WebHook API")
                self.tooltip_window.setStyleSheet("background-color: #333; color: white; padding: 5px; border-radius: 4px;")
                self.tooltip_window.adjustSize()

        global_pos = self.mapToGlobal(QPoint(0, 0))
        x = global_pos.x() - (self.tooltip_window.width() - self.width()) // 2
        y = global_pos.y() - self.tooltip_window.height() - 5
        
        self.tooltip_window.move(x, y)
        self.tooltip_window.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.tooltip_window:
            self.tooltip_window.hide()
        super().leaveEvent(event)


class TruncationPopup(QLabel):
    """텍스트 잘림 팝업 - 은은한 스타일"""

    def __init__(self):
        super().__init__(None, Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QLabel {
                background-color: #FAFAFA;
                color: #707070;
                font-family: 'Noto Sans KR';
                font-size: 14px;
                padding: 5px 11px;
                border: 1px solid #E0E0E0;
                border-radius: 2px;
            }
        """)


class TruncatedLineEdit(QLineEdit):
    """텍스트가 잘릴 때 hover 시 위쪽에 연한 회색 팝업으로 전체 텍스트 표시"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._popup = None

    def _is_truncated(self):
        text = self.text()
        if not text or self.width() == 0:
            return False
        padding = 48  # padding: 0 24px → 양쪽 합산
        return self.fontMetrics().horizontalAdvance(text) > self.width() - padding

    def _ensure_popup(self):
        if not self._popup:
            self._popup = TruncationPopup()

    def enterEvent(self, event):
        if self._is_truncated():
            self._ensure_popup()
            self._popup.setText(self.text())
            self._popup.adjustSize()
            gp = self.mapToGlobal(QPoint(0, 0))
            self._popup.move(gp.x() + 70, gp.y() - self._popup.height() - 5)
            self._popup.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._popup:
            self._popup.hide()
        super().leaveEvent(event)


class TableTruncationFilter(QObject):
    """QTableWidget 셀 hover 시 잘린 텍스트를 위쪽 팝업으로 표시하는 이벤트 필터"""

    def __init__(self, table, col=0, parent=None):
        super().__init__(parent)
        self.table = table
        self.col = col
        self._popup = None
        self._last_cell = (-1, -1)
        # setItem 기반 셀 대비 뷰포트 필터 유지
        table.viewport().installEventFilter(self)
        table.viewport().setMouseTracking(True)
        # setCellWidget 기반 셀: 행 삽입 시 자동으로 셀 위젯에 필터 설치
        table.model().rowsInserted.connect(self._on_rows_inserted)

    def _on_rows_inserted(self, parent_index, first, last):
        # insertRow 직후에는 setCellWidget이 아직 호출 안 됨 → 다음 이벤트 루프에서 설치
        for row in range(first, last + 1):
            QTimer.singleShot(0, lambda r=row: self._install_widget_filter(r))

    def _install_widget_filter(self, row):
        widget = self.table.cellWidget(row, self.col)
        if widget:
            widget.installEventFilter(self)

    def _ensure_popup(self):
        if not self._popup:
            self._popup = TruncationPopup()

    def _get_cell_text(self, row, col):
        item = self.table.item(row, col)
        if item:
            return item.text()
        widget = self.table.cellWidget(row, col)
        if widget and hasattr(widget, 'text'):
            return widget.text()
        return None

    def _is_truncated(self, text, row, col):
        if not text:
            return False
        widget = self.table.cellWidget(row, col)
        if widget and hasattr(widget, 'text_label'):
            label = widget.text_label
            available = label.width()
            if available > 0:
                return label.fontMetrics().horizontalAdvance(text) > available
        fm = self.table.fontMetrics()
        available = self.table.columnWidth(col) - 10
        return fm.horizontalAdvance(text) > available

    def _find_row_for_widget(self, obj):
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, self.col) is obj:
                return row
        return -1

    def _show_popup_for_cell(self, row, col):
        text = self._get_cell_text(row, col)
        if text and self._is_truncated(text, row, col):
            self._ensure_popup()
            self._popup.setText(text)
            self._popup.adjustSize()
            index = self.table.model().index(row, col)
            cell_rect = self.table.visualRect(index)
            gp = self.table.viewport().mapToGlobal(cell_rect.topLeft())
            self._popup.move(gp.x() + 70, gp.y() - self._popup.height() - 5)
            self._popup.show()

    def eventFilter(self, obj, event):
        try:
            return self._eventFilter_impl(obj, event)
        except RuntimeError:
            # Qt C++ 객체가 이미 삭제된 경우 (페이지 전환 등)
            if self._popup:
                self._popup.hide()
            return False

    def _eventFilter_impl(self, obj, event):
        # 셀 위젯(ClickableRowWidget 등) Enter/Leave로 팝업 제어
        if obj is not self.table.viewport():
            row = self._find_row_for_widget(obj)
            if row >= 0:
                if event.type() == QEvent.Enter:
                    self._show_popup_for_cell(row, self.col)
                elif event.type() == QEvent.Leave:
                    if self._popup:
                        self._popup.hide()
            return False

        # 뷰포트 MouseMove: setItem 기반 셀 처리
        if event.type() == QEvent.MouseMove:
            pos = event.pos()
            row = self.table.rowAt(pos.y())
            col = self.table.columnAt(pos.x())
            if (row, col) == self._last_cell:
                return False
            self._last_cell = (row, col)
            if self._popup:
                self._popup.hide()
            if row >= 0 and col >= 0:
                text = self._get_cell_text(row, col)
                if text and self._is_truncated(text, row, col):
                    self._ensure_popup()
                    self._popup.setText(text)
                    self._popup.adjustSize()
                    index = self.table.model().index(row, col)
                    cell_rect = self.table.visualRect(index)
                    gp = self.table.viewport().mapToGlobal(cell_rect.topLeft())
                    self._popup.move(gp.x() + 70, gp.y() - self._popup.height() - 5)
                    self._popup.show()

        elif event.type() == QEvent.Leave:
            if self._popup:
                self._popup.hide()
            self._last_cell = (-1, -1)

        return False


class CustomDialog(QDialog):
    def __init__(self, dmsg, dstep):
        super().__init__()

        self.setWindowTitle(dstep)
        self.setGeometry(800, 600, 400, 600)
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
