import sys, os, time, tempfile, subprocess, re
import threading, queue
from pathlib import Path
import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
from PIL import ImageGrab
from typing import Optional

# ---------- 경로/환경 ----------
_DEFAULT_ROOT = Path(__file__).resolve().parents[0]
FASTVLM_DIR = Path(os.getenv("FASTVLM_DIR", str(_DEFAULT_ROOT)))
PREDICT_PY = FASTVLM_DIR / "predict.py"

# 모델 경로 (Qwen3-VL-4B 기준)
MODEL_PATH = os.getenv("FASTVLM_MODEL", "checkpoints/qwen3_vl_4b_instruct")
PROMPT = os.getenv("FASTVLM_PROMPT", "Describe the objects in the camera accurately and detail their colors and textures.")
USE_VLM = os.getenv("USE_VLM", "1") not in ("0", "false", "False")
PROC_TIMEOUT = int(os.getenv("FASTVLM_TIMEOUT", "60"))
HF_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN") or os.getenv("HF_TOKEN")

# ---------- 유틸: 결과 파싱 및 화면 표시 ----------
def parse_predict_output(out: str) -> str:
    lines = [ln.strip() for ln in out.strip().splitlines() if ln.strip()]
    joined = "\n".join(lines)
    for pat in (r"ASSISTANT:\s*(.*)", r"Answer:\s*(.*)", r"Qwen:\s*(.*)", r"Output:\s*(.*)"):
        m = re.search(pat, joined, flags=re.IGNORECASE | re.DOTALL)
        if m: return m.group(1).strip()
    return lines[-1] if lines else "분석 결과 없음"

def draw_overlay(frame, text):
    if not text: return frame
    H, W = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (W, 80), (0, 0, 0), -1)
    display_text = text[:150] + "..." if len(text) > 150 else text
    cv2.putText(frame, display_text, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
    return frame

# ---------- VLM 워커 스레드 ----------
class VLMWorker(threading.Thread):
    def __init__(self, work_q: queue.Queue, result_q: queue.Queue, model_path: str, hf_token: Optional[str]):
        super().__init__(daemon=True)
        self.work_q, self.result_q = work_q, result_q
        self.model_path, self.hf_token = model_path, hf_token

    def run(self):
        print("[VLMWorker] 모델 추론 스레드 가동 중...")
        while True:
            item = self.work_q.get()
            if item is None: break
            img_path, prompt = item
            cmd = [sys.executable, str(PREDICT_PY), "--model-path", self.model_path, "--image-file", img_path, "--prompt", prompt]
            env = os.environ.copy()
            if self.hf_token: env["HUGGINGFACE_HUB_TOKEN"] = self.hf_token
            try:
                out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=PROC_TIMEOUT, env=env)
                self.result_q.put(("ok", parse_predict_output(out)))
            except Exception as e:
                self.result_q.put(("err", f"추론 에러: {str(e)[:50]}"))
            finally:
                if os.path.exists(img_path): os.remove(img_path)
                self.work_q.task_done()

# ---------- 메인 루프 ----------
def main():
    # 사용자님이 알려주신 창 제목으로 직접 검색
    target_title = "aiot8390p6_64_bsp"
    print(f"[scrcpy-infer] '{target_title}' 창을 찾는 중...")
    
    scrcpy_window = None
    while scrcpy_window is None:
        windows = gw.getWindowsWithTitle(target_title)
        if windows:
            scrcpy_window = windows[0]
            print(f"✅ 성공! [{scrcpy_window.title}] 창을 찾았습니다.")
            try: scrcpy_window.activate()
            except: pass
        else:
            # 보조 수단: 제목에 'aiot'가 포함된 창 찾기
            all_titles = gw.getAllTitles()
            for t in all_titles:
                if "aiot" in t.lower():
                    scrcpy_window = gw.getWindowsWithTitle(t)[0]
                    print(f"✅ 보조 매칭 성공: [{scrcpy_window.title}]")
                    break
            if not scrcpy_window:
                print(f"🔍 '{target_title}' 창이 보이지 않습니다. 창을 띄워주세요.")
                time.sleep(2)

    work_q, result_q = queue.Queue(maxsize=1), queue.Queue()
    vlm = VLMWorker(work_q, result_q, MODEL_PATH, HF_TOKEN) if USE_VLM else None
    if vlm: vlm.start()

    last_vlm_ts, overlay_text = 0.0, "모델 분석 대기 중..."
    
    try:
        while True:
            if scrcpy_window:
                if scrcpy_window.isMinimized:
                    time.sleep(0.1)
                    continue
                
                # 창 영역 캡처
                rect = (scrcpy_window.left, scrcpy_window.top, scrcpy_window.right, scrcpy_window.bottom)
                screenshot = ImageGrab.grab(bbox=rect)
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                now = time.time()
                # 2초마다 VLM 요청 (효율성 강조)
                if USE_VLM and (now - last_vlm_ts > 2.0) and work_q.empty():
                    fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
                    os.close(fd)
                    cv2.imwrite(tmp_path, frame)
                    work_q.put_nowait((tmp_path, PROMPT))
                    last_vlm_ts = now

                try:
                    status, msg = result_q.get_nowait()
                    overlay_text = msg if status == "ok" else msg
                except queue.Empty: pass

                # 화면 표시
                display_frame = draw_overlay(frame, overlay_text)
                cv2.imshow("Qwen3-VL Real-time Inference", display_frame)

            if cv2.waitKey(1) == 27: break
    finally:
        if vlm: work_q.put(None)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()