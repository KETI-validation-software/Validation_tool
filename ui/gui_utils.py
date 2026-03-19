from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTextBrowser, QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap
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
