"""
클릭 가능한 커스텀 위젯 모듈
- ClickableLabel: 클릭 가능한 QLabel (기존 호환용)
- ClickableRowWidget: 시험 분야 셀용 (텍스트 + 화살표 분리)
- ClickableCheckboxRowWidget: 시나리오 셀용 (체크박스 + 텍스트 분리)
"""

from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter
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

        # 레이아웃 설정: padding 좌24, 상8, 우32, 하8
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 8, 32, 8)
        layout.setSpacing(8)

        # 체크박스 이미지 (왼쪽)
        self.checkbox_label = QLabel()
        self.checkbox_label.setStyleSheet("background: transparent;")
        checkbox_pixmap = QPixmap(resource_path(checkbox_unchecked_path))
        self.checkbox_label.setPixmap(checkbox_pixmap)
        self.checkbox_label.setFixedSize(checkbox_pixmap.width(), checkbox_pixmap.height())
        layout.addWidget(self.checkbox_label)

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
        """체크 상태 변경 (체크박스 + 배경 이미지 모두 변경)"""
        self._is_checked = checked
        if checked:
            checkbox_pixmap = QPixmap(resource_path(self.checkbox_checked_path))
            self.bg_pixmap = QPixmap(resource_path(self.bg_selected_image_path))
        else:
            checkbox_pixmap = QPixmap(resource_path(self.checkbox_unchecked_path))
            self.bg_pixmap = QPixmap(resource_path(self.bg_image_path))
        self.checkbox_label.setPixmap(checkbox_pixmap)
        self.checkbox_label.setFixedSize(checkbox_pixmap.width(), checkbox_pixmap.height())
        self.update()  # 배경 다시 그리기

    def setBackgroundImage(self, bg_image_path):
        """배경 이미지 변경"""
        self.bg_pixmap = QPixmap(resource_path(bg_image_path))
        self.update()
