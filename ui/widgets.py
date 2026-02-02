"""
클릭 가능한 커스텀 위젯 모듈
- ClickableLabel: 클릭 가능한 QLabel (기존 호환용)
- ClickableRowWidget: 시험 분야 셀용 (텍스트 + 화살표 분리)
- ClickableCheckboxRowWidget: 시나리오 셀용 (체크박스 + 텍스트 분리)
"""

from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QDialog, QPushButton, QVBoxLayout, QGraphicsDropShadowEffect
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
        self.setFixedSize(400, 240)  # 크기 고정

        self.title_text = title
        self.message_text = message

        # UI 설정
        self._setup_ui()

    def _setup_ui(self):
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # 제목 (상단)
        self.title_label = QLabel(self.title_text)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 16pt;
            font-weight: bold;
            font-family: 'Malgun Gothic', 'Noto Sans KR';
            background: transparent;
        """)
        layout.addWidget(self.title_label)

        # 내용 (중앙)
        self.msg_label = QLabel(self.message_text)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setWordWrap(True)  # 줄바꿈 허용
        self.msg_label.setStyleSheet("""
            color: rgba(255, 255, 255, 220);
            font-size: 11pt;
            font-family: 'Malgun Gothic', 'Noto Sans KR';
            background: transparent;
            line-height: 140%;
        """)
        layout.addWidget(self.msg_label)

        layout.addStretch()

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
