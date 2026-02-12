"""
클릭 가능한 커스텀 위젯 모듈
- ClickableLabel: 클릭 가능한 QLabel (기존 호환용)
- ClickableRowWidget: 시험 분야 셀용 (텍스트 + 화살표 분리)
- ClickableCheckboxRowWidget: 시나리오 셀용 (체크박스 + 텍스트 분리)
"""

from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QDialog, QPushButton, QVBoxLayout, QGraphicsDropShadowEffect, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
from core.functions import resource_path


class ClickableLabel(QLabel):
    """클릭 가능한 QLabel - 시험 분야 셀용 (기존 호환용)"""
    clicked = pyqtSignal(int, int)  # row, column 전달

    def __init__(self, text, row, col, parent=None):
        super().__init__(text, parent)
        self.row = row
        self.col = col
        self.setCursor(Qt.PointingHandCursor)  # 마우스 커서를 포인터로

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.row, self.col)
        super().mousePressEvent(event)


class ClickableRowWidget(QWidget):
    """클릭 가능한 QWidget - 시험 분야 셀용 (텍스트 + 화살표 분리)"""
    clicked = pyqtSignal(int, int)  # row, column 전달

    def __init__(self, text, row, col, bg_image_path, arrow_image_path, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self._text = text
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(39)  # 행 높이 고정

        # 배경 이미지 설정 (paintEvent에서 그림)
        self.bg_pixmap = QPixmap(resource_path(bg_image_path))

        # 레이아웃 설정: padding 좌32, 상8, 우24, 하8
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 8, 24, 8)
        layout.setSpacing(8)

        # 텍스트 라벨
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("""
            QLabel {
                background: transparent;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-weight: 400;
                color: #000000;
            }
        """)
        layout.addWidget(self.text_label, 1)  # stretch=1로 남은 공간 채우기

        # 화살표 이미지
        self.arrow_label = QLabel()
        self.arrow_label.setStyleSheet("background: transparent;")
        arrow_pixmap = QPixmap(resource_path(arrow_image_path))
        self.arrow_label.setPixmap(arrow_pixmap)
        self.arrow_label.setFixedSize(arrow_pixmap.width(), arrow_pixmap.height())
        layout.addWidget(self.arrow_label)

    def paintEvent(self, event):
        """배경 이미지를 위젯 크기에 맞게 그리기"""
        painter = QPainter(self)
        if not self.bg_pixmap.isNull():
            # 위젯 크기에 맞게 이미지 스케일링
            scaled_pixmap = self.bg_pixmap.scaled(
                self.size(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pixmap)
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.row, self.col)
        super().mousePressEvent(event)

    def text(self):
        """기존 ClickableLabel과 호환을 위한 text() 메서드"""
        return self._text

    def setBackgroundImage(self, bg_image_path):
        """배경 이미지 변경"""
        self.bg_pixmap = QPixmap(resource_path(bg_image_path))
        self.update()  # 다시 그리기


class ClickableCheckboxRowWidget(QWidget):
    """클릭 가능한 QWidget - 시나리오 셀용 (체크박스 + 텍스트 분리)"""
    clicked = pyqtSignal(int, int)  # row, column 전달

    def __init__(self, text, row, col, bg_image_path, bg_selected_image_path, checkbox_unchecked_path, checkbox_checked_path, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self._text = text
        self._is_checked = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(39)  # 행 높이 고정

        # 배경 이미지 경로 저장
        self.bg_image_path = bg_image_path
        self.bg_selected_image_path = bg_selected_image_path

        # 배경 이미지 설정 (paintEvent에서 그림)
        self.bg_pixmap = QPixmap(resource_path(bg_image_path))

        # 체크박스 이미지 경로 저장
        self.checkbox_unchecked_path = checkbox_unchecked_path
        self.checkbox_checked_path = checkbox_checked_path

        # 레이아웃 설정: padding 상하8, 좌우 32 (체크박스 삭제로 좌우 균형 맞춤)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 8, 32, 8)
        layout.setSpacing(8)

        # 텍스트 라벨 (체크박스 삭제)
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("""
            QLabel {
                background: transparent;
                font-family: 'Noto Sans KR';
                font-size: 19px;
                font-weight: 400;
                color: #000000;
            }
        """)
        layout.addWidget(self.text_label, 1)  # stretch=1로 남은 공간 채우기

    def paintEvent(self, event):
        """배경 이미지를 위젯 크기에 맞게 그리기"""
        painter = QPainter(self)
        if not self.bg_pixmap.isNull():
            scaled_pixmap = self.bg_pixmap.scaled(
                self.size(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pixmap)
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.row, self.col)
        super().mousePressEvent(event)

    def text(self):
        """기존 ClickableLabel과 호환을 위한 text() 메서드"""
        return self._text

    def isChecked(self):
        """체크 상태 반환"""
        return self._is_checked

    def setChecked(self, checked):
        """체크 상태 변경 (배경 이미지 변경)"""
        self._is_checked = checked
        if checked:
            self.bg_pixmap = QPixmap(resource_path(self.bg_selected_image_path))
        else:
            self.bg_pixmap = QPixmap(resource_path(self.bg_image_path))
        self.update()  # 배경 다시 그리기

    def setBackgroundImage(self, bg_image_path):
        """배경 이미지 변경"""
        self.bg_pixmap = QPixmap(resource_path(bg_image_path))
        self.update()


class SystemPopup(QDialog):
    """
    스플래시 화면 스타일의 시스템 알림 팝업
    - 배경: 이미지 없이 깔끔한 그라데이션 적용 (#275554 -> #002B69)
    - 스타일: 테두리 없음, 어두운 배경, 흰색 텍스트
    """
    def __init__(self, title="알림", message="", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 배경 투명 (라운드 처리 등을 위해)
        self.setFixedSize(380, 200)  # 크기 축소 (기존 400x240)

        self.title_text = title
        self.message_text = message

        # UI 설정
        self._setup_ui()

    def _setup_ui(self):
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 20)
        layout.setSpacing(10)

        # 제목 (상단)
        self.title_label = QLabel(self.title_text)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 14pt;
            font-weight: bold;
            font-family: 'Malgun Gothic', 'Noto Sans KR';
            background: transparent;
        """)
        layout.addWidget(self.title_label)

        layout.addStretch(1) # 상단 여백 추가하여 가운데 정렬 유도

        # 내용 (중앙)
        self.msg_label = QLabel(self.message_text)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setWordWrap(True)  # 줄바꿈 허용
        self.msg_label.setStyleSheet("""
            color: rgba(255, 255, 255, 220);
            font-size: 10pt;
            font-family: 'Malgun Gothic', 'Noto Sans KR';
            background: transparent;
            line-height: 130%;
        """)
        layout.addWidget(self.msg_label)

        layout.addStretch(1) # 하단 여백 추가하여 가운데 정렬 유도

        # 확인 버튼 (하단)
        self.ok_btn = QPushButton("확인")
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.setFixedSize(120, 36)
        
        # 버튼 스타일 (깔끔한 반투명/유리 느낌)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 18px;
                color: #FFFFFF;
                font-family: 'Malgun Gothic', 'Noto Sans KR';
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.ok_btn.clicked.connect(self.accept)  # 클릭 시 창 닫기 (QDialog.accept)

        # 버튼 컨테이너 (중앙 정렬)
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(btn_container)

    def paintEvent(self, event):
        """배경 그리기 (이미지 없이 그라데이션만)"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 스플래시 테마와 동일한 그라데이션 적용
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#275554")) # 짙은 청록
        gradient.setColorAt(1, QColor("#002B69")) # 짙은 남색
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        # 둥근 모서리 적용 (선택 사항, 여기서는 직각으로 하되 깔끔하게)
        painter.drawRect(self.rect())



class GradientMessageBox(QDialog):
    """QMessageBox ??? ????? ?????"""
    def __init__(self, title, message, detail="", buttons=None, default_button=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(420, 230)
        self._result = QMessageBox.NoButton

        self.title_text = title or "??"
        self.message_text = message or ""
        self.detail_text = detail or ""
        self.buttons = buttons if buttons is not None else QMessageBox.Ok
        self.default_button = default_button if default_button is not None else QMessageBox.NoButton
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 24, 25, 24)
        layout.setSpacing(8)

        title_label = QLabel(self.title_text)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 14pt;
            font-weight: 700;
            font-family: 'Malgun Gothic', 'Noto Sans KR';
            background: transparent;
        """)
        layout.addWidget(title_label)
        layout.addStretch(1)

        message_label = QLabel(self.message_text)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            color: rgba(255, 255, 255, 235);
            font-size: 10.5pt;
            font-family: 'Malgun Gothic', 'Noto Sans KR';
            background: transparent;
            line-height: 130%;
        """)
        layout.addWidget(message_label)

        if self.detail_text:
            detail_label = QLabel(self.detail_text)
            detail_label.setAlignment(Qt.AlignCenter)
            detail_label.setWordWrap(True)
            detail_label.setStyleSheet("""
                color: rgba(255, 255, 255, 200);
                font-size: 9pt;
                font-family: 'Malgun Gothic', 'Noto Sans KR';
                background: transparent;
            """)
            layout.addWidget(detail_label)

        layout.addStretch(1)
        layout.addWidget(self._build_buttons(), 0, Qt.AlignHCenter)

    def _create_button(self, text, standard_value):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(120, 36)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: 18px;
                color: #FFFFFF;
                font-family: 'Malgun Gothic', 'Noto Sans KR';
                font-size: 10pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.28);
                border: 1px solid rgba(255, 255, 255, 0.55);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.10);
            }
        """)
        btn.clicked.connect(lambda: self._set_result_and_close(standard_value))
        return btn

    def _build_buttons(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(container)
        button_layout.setContentsMargins(0, 4, 0, 0)
        button_layout.setSpacing(12)
        button_layout.setAlignment(Qt.AlignCenter)

        button_defs = []
        if self.buttons & QMessageBox.Yes:
            button_defs.append(("\uC608", QMessageBox.Yes))
        if self.buttons & QMessageBox.No:
            button_defs.append(("\uC544\uB2C8\uC624", QMessageBox.No))
        if self.buttons & QMessageBox.Ok:
            button_defs.append(("\uD655\uC778", QMessageBox.Ok))
        if self.buttons & QMessageBox.Cancel:
            button_defs.append(("\uCDE8\uC18C", QMessageBox.Cancel))

        if not button_defs:
            button_defs = [("\uD655\uC778", QMessageBox.Ok)]

        for text, value in button_defs:
            button_layout.addWidget(self._create_button(text, value))
        return container

    def _set_result_and_close(self, value):
        self._result = value
        self.accept()

    def exec_with_result(self):
        self.exec_()
        if self._result == QMessageBox.NoButton:
            if self.default_button != QMessageBox.NoButton:
                return self.default_button
            if self.buttons & QMessageBox.No:
                return QMessageBox.No
            if self.buttons & QMessageBox.Cancel:
                return QMessageBox.Cancel
            return QMessageBox.Ok
        return self._result

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#275554"))
        gradient.setColorAt(1, QColor("#002B69"))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())


def install_gradient_messagebox():
    """QMessageBox ?? ???? ????? ???? ??"""
    if getattr(QMessageBox, "_gradient_patch_installed", False):
        return

    def _resolve_buttons(args, fallback_buttons, fallback_default):
        buttons = fallback_buttons
        default_button = fallback_default
        if len(args) >= 1 and isinstance(args[0], int):
            buttons = args[0]
        if len(args) >= 2 and isinstance(args[1], int):
            default_button = args[1]
        return buttons, default_button

    def _show(parent, title, text, detail, fallback_buttons, fallback_default, args):
        buttons, default_button = _resolve_buttons(args, fallback_buttons, fallback_default)
        dialog = GradientMessageBox(
            title=title,
            message=text,
            detail=detail,
            buttons=buttons,
            default_button=default_button,
            parent=parent
        )
        return dialog.exec_with_result()

    def warning(parent, title, text, *args):
        return _show(parent, title, text, "", QMessageBox.Ok, QMessageBox.NoButton, args)

    def information(parent, title, text, *args):
        return _show(parent, title, text, "", QMessageBox.Ok, QMessageBox.NoButton, args)

    def critical(parent, title, text, *args):
        return _show(parent, title, text, "", QMessageBox.Ok, QMessageBox.NoButton, args)

    def question(parent, title, text, *args):
        return _show(parent, title, text, "", QMessageBox.Yes | QMessageBox.No, QMessageBox.No, args)

    QMessageBox.warning = staticmethod(warning)
    QMessageBox.information = staticmethod(information)
    QMessageBox.critical = staticmethod(critical)
    QMessageBox.question = staticmethod(question)
    QMessageBox._gradient_patch_installed = True
