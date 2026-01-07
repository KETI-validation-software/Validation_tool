import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSizePolicy, QWidget, QHBoxLayout, QTextBrowser, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from core.functions import resource_path
from core.utils import format_schema

class CombinedDetailDialog(QDialog):
    def __init__(self, api_name, step_buffer, schema_data, webhook_schema=None):
        super().__init__()

        self.setWindowTitle(f"{api_name} 상세 정보")
        self.setMinimumSize(1520, 921)  # 반응형: 최소 크기 설정
        self.resize(1520, 921)  # 초기 크기
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setStyleSheet("background-color: #FFFFFF;")

        # 전체 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(48, 32, 48, 40)  # 좌, 상, 우, 하

        # webhook_schema 저장
        self.webhook_schema = webhook_schema

        # 상단 제목 - 반응형: 높이만 고정, 가로 확장
        title_label = QLabel(f"{api_name} 상세 정보")
        title_label.setMinimumHeight(38)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        title_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 26px; font-weight: 500;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(16)  # 제목 아래 gap

        # 서브 제목 컨테이너 - 반응형: 높이만 고정, 가로 확장
        subtitle_container = QWidget()
        subtitle_container.setObjectName("subtitle_container")
        subtitle_container.setMinimumHeight(47)
        subtitle_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        subtitle_container.setStyleSheet("""
            #subtitle_container {
                border-image: url(assets/image/common/message.png) 0 0 0 0 stretch stretch;
            }
            #subtitle_container QLabel {
                border-image: none;
                background: transparent;
            }
        """)
        subtitle_layout = QHBoxLayout(subtitle_container)
        subtitle_layout.setContentsMargins(14, 12, 48, 12)  # 좌14, 상12, 우48, 하12

        # 체크 아이콘 (고정 크기)
        check_icon = QLabel()
        check_icon.setPixmap(QPixmap(resource_path("assets/image/icon/icn_check.png")))
        check_icon.setFixedSize(18, 18)
        subtitle_layout.addWidget(check_icon)

        subtitle_layout.addSpacing(13)  # 아이콘과 텍스트 사이 간격

        # 텍스트
        subtitle_label = QLabel(f"{api_name} API 정보에 대한 상세 내용을 확인합니다.")
        subtitle_label.setStyleSheet("font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 400;")
        subtitle_layout.addWidget(subtitle_label)
        subtitle_layout.addStretch()
        
        main_layout.addWidget(subtitle_container)
        main_layout.addSpacing(12)  # message.png 아래 gap

        # 3열 콘텐츠 영역 컨테이너 - 반응형: 전체 확장
        content_container = QWidget()
        content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)  # 열 사이 gap

        # 공통 스타일
        title_style = "font-family: 'Noto Sans KR'; font-size: 18px; font-weight: 600;"
        box_style = "border: 1px solid #CECECE; border-radius: 4px; background-color: #FFFFFF; font-family: 'Noto Sans KR'; font-size: 19px; font-weight: 400; padding: 12px;"

        # 1열: 메시지 데이터 - 반응형: 동일 비율 확장
        data_column = QWidget()
        data_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        data_column_layout = QVBoxLayout(data_column)
        data_column_layout.setContentsMargins(0, 0, 0, 0)
        data_column_layout.setSpacing(0)

        data_title = QLabel("메시지 데이터")
        data_title.setMinimumHeight(24)
        data_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        data_title.setStyleSheet(title_style)
        data_column_layout.addWidget(data_title)
        data_column_layout.addSpacing(8)

        self.data_browser = QTextBrowser()
        self.data_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.data_browser.setStyleSheet(box_style)
        self.data_browser.setAcceptRichText(True)
        if step_buffer["data"]:
            data_text = step_buffer["data"]
            self.data_browser.setPlainText(data_text)
        else:
            self.data_browser.setHtml('<span style="color: #CECECE;">아직 수신된 데이터가 없습니다.</span>')
        data_column_layout.addWidget(self.data_browser)

        # 2열: 메시지 규격 - 반응형: 동일 비율 확장
        schema_column = QWidget()
        schema_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        schema_column_layout = QVBoxLayout(schema_column)
        schema_column_layout.setContentsMargins(0, 0, 0, 0)
        schema_column_layout.setSpacing(0)

        schema_title = QLabel("메시지 규격")
        schema_title.setMinimumHeight(24)
        schema_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        schema_title.setStyleSheet(title_style)
        schema_column_layout.addWidget(schema_title)
        schema_column_layout.addSpacing(8)

        self.schema_browser = QTextBrowser()
        self.schema_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.schema_browser.setStyleSheet(box_style)
        self.schema_browser.setAcceptRichText(True)

        # 기본 스키마 + 웹훅 스키마 결합
        schema_text = format_schema(schema_data)
        if self.webhook_schema:
            schema_text += "\n\n<b>웹훅 메시지 규격</b>\n"
            schema_text += format_schema(self.webhook_schema)

        # HTML 태그가 포함된 경우 setHtml 사용, 아니면 setPlainText
        if '<b>' in schema_text:
            schema_text_html = schema_text.replace('\n', '<br>')
            self.schema_browser.setHtml(f'<pre style="font-family: \'Noto Sans KR\'; font-size: 19px; white-space: pre-wrap;">{schema_text_html}</pre>')
        else:
            self.schema_browser.setPlainText(schema_text)
        schema_column_layout.addWidget(self.schema_browser)

        # 3열: 검증 오류 - 반응형: 동일 비율 확장
        error_column = QWidget()
        error_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        error_column_layout = QVBoxLayout(error_column)
        error_column_layout.setContentsMargins(0, 0, 0, 0)
        error_column_layout.setSpacing(0)

        error_title = QLabel("검증 오류")
        error_title.setMinimumHeight(24)
        error_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        error_title.setStyleSheet(title_style)
        error_column_layout.addWidget(error_title)
        error_column_layout.addSpacing(8)

        self.error_browser = QTextBrowser()
        self.error_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.error_browser.setStyleSheet(box_style)
        self.error_browser.setAcceptRichText(True)
        result = step_buffer["result"]
        
        # ✅ 검증 결과가 없는 경우 (데이터가 없고 에러도 없는 경우) 처리
        has_data = step_buffer.get("data") and step_buffer["data"] != "아직 수신된 데이터가 없습니다."
        has_error = bool(step_buffer.get("error"))
        
        if not has_data and not has_error:
            # 아직 검증하지 않은 상태 - 회색으로 표시
            self.error_browser.setHtml('<span style="color: #CECECE;">아직 검증이 수행되지 않았습니다.</span>')
        else:
            error_text = step_buffer["error"] if has_error else ("오류가 없습니다." if result == "PASS" else "")
            
            # ✅ 검증 결과를 볼드체로 표시
            if result == "PASS":
                result_html = f'<span style="font-weight: bold; color: #10b981;">검증 결과: {result}</span><br><br>'
            else:
                result_html = f'<span style="font-weight: bold; color: #ef4444;">검증 결과: {result}</span><br><br>'
            
            if result == "FAIL":
                error_msg_html = result_html + error_text.replace('\n', '<br>')
            else:
                error_msg_html = result_html + "오류가 없습니다."
            
            self.error_browser.setHtml(error_msg_html)
        error_column_layout.addWidget(self.error_browser)

        # 3개 열을 가로로 배치 - 반응형: 동일 비율(stretch=1)
        content_layout.addWidget(data_column, stretch=1)
        content_layout.addWidget(schema_column, stretch=1)
        content_layout.addWidget(error_column, stretch=1)


        main_layout.addWidget(content_container, stretch=1)  # 콘텐츠 영역 확장
        main_layout.addSpacing(24)  # 콘텐츠 영역 아래 gap

        # 확인 버튼 영역 - 반응형: 높이만 고정, 가로 확장
        button_container = QWidget()
        button_container.setFixedHeight(48)
        button_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 확인 버튼 (434x48)
        # ✅ 반응형: 인스턴스 변수로 변경 및 원본 크기 저장
        self.confirm_button = QPushButton("확인")
        self.confirm_button.setFixedSize(434, 48)
        self.original_confirm_btn_size = (434, 48)
        self.original_dialog_size = (1520, 921)
        self.confirm_button.setStyleSheet("""
              QPushButton {
                  background-color: #1C5DB1;
                  border: none;
                  border-radius: 4px;
                  padding-left: 20px;
                  padding-right: 20px;
                  font-family: 'Noto Sans KR';
                  font-size: 20px;
                  font-weight: 500;
                  color: #FFFFFF;
              }
              QPushButton:hover {
                  background-color: #3E85E2;
              }
          """)
        
        self.confirm_button.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(self.confirm_button)
        button_layout.addStretch()

        main_layout.addWidget(button_container)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """다이얼로그 크기 변경 시 확인 버튼 크기 조정"""
        super().resizeEvent(event)

        if hasattr(self, 'confirm_button') and hasattr(self, 'original_confirm_btn_size'):
            width_ratio = max(1.0, self.width() / self.original_dialog_size[0])
            new_btn_width = int(self.original_confirm_btn_size[0] * width_ratio)
            self.confirm_button.setFixedSize(new_btn_width, self.original_confirm_btn_size[1])
