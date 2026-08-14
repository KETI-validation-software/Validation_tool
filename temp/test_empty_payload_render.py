# 빈 페이로드 {} 모니터 로그 렌더링 검증 (헤드리스)
# append_monitor_log의 전처리 + HTML 행 생성 파이프라인을 그대로 재현해
# QTextDocument가 실제 몇 줄로 렌더링하는지 확인한다.
import sys, os, re, html
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import replace_transport_desc_for_display, normalize_monitor_request_json

request_json = "{}"

# ── system_main_ui.append_monitor_log 전처리 재현 ──
request_json = replace_transport_desc_for_display(request_json)
if isinstance(request_json, str):
    request_json = request_json.replace("\r\n", "\n").rstrip()
    request_json = re.sub(r"(?:\n[ \t]*){2,}([ \t]*[\}\]])$", r"\n\1", request_json)
    if request_json.strip() == "{}":
        request_json = "{\n}"

print(f"1) 전처리 후: {request_json!r}")

request_json = normalize_monitor_request_json("수신", "테스트 (요청)", request_json, "")
print(f"2) normalize 후: {request_json!r}")

# ── HTML 행 생성 재현 ──
_lines = html.escape(str(request_json)).split('\n')
print(f"3) 분할된 줄: {_lines!r}")
_rows = ''.join(
    f'<tr><td style="padding: 0; margin: 0;">{l.replace(" ", "&nbsp;") or "&nbsp;"}</td></tr>'
    for l in _lines
)
html_content = (
    f'<table cellspacing="0" cellpadding="0" width="100%" bgcolor="#F8FAFC"'
    f' style="border: 1px solid #CBD5E1; border-radius: 4px;">'
    f'<tr><td style="padding: 10px;">'
    f'<table cellspacing="0" cellpadding="0" width="100%"'
    f' style="font-size: 16px; color: #1F2937; font-family: \'Consolas\', monospace;">'
    f'{_rows}</table>'
    f'</td></tr></table>'
)

# ── Qt 렌더링 결과 확인 (QTextDocument는 헤드리스 동작) ──
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QTextDocument
app = QApplication.instance() or QApplication(sys.argv)
doc = QTextDocument()
doc.setHtml(html_content)
plain = doc.toPlainText()
print(f"4) Qt 렌더 결과 줄들: {plain.splitlines()!r}")
print("✅ 두 줄로 렌더링됨" if len(plain.splitlines()) >= 2 else "❌ 한 줄로 합쳐짐 — 렌더링 단계가 원인")
