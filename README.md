# Validation_tool
<p align="center">
  <img src="https://github.com/user-attachments/assets/d15b5f1f-2052-4b2e-b914-270107ee7431" alt="<프로젝트명> Banner" width="70%" />
</p>

<p align="center">
  <b>Validate and integrate physical security platforms and systems with a unified tool.</b>
</p>

<p align="center">
  <!-- Python 버전 -->
  <img src="https://img.shields.io/badge/python-3.9.13%20-blue" />
  
  <!-- Custom 기능 배지 -->
  <img src="https://img.shields.io/badge/Webhook-supported-brightgreen" />
  <img src="https://img.shields.io/badge/PyIn-ready-orange" />
  <img src="https://img.shields.io/badge/GUI-PyQt5-ff69b4" />
</p>


## Project 
<p align="center">
  <img src="https://github.com/user-attachments/assets/4fab21f4-f604-4669-906e-7dae5c8f8872" alt="splash_logo" />
</p>

A unified validation tool for API integration testing of **integrated systems** and **standalone systems**.  
It retrieves test configurations from the management system and performs scenario-based API send/receive validation.
---

## Runtime Flow

```mermaid
sequenceDiagram
    participant U as User
    participant I as info_GUI
    participant A as APIClient
    participant V as Validation Page
    participant S as Management Server

    U->>I: Load test info
    I->>A: pending heartbeat
    I->>S: GET /api/integration/test-requests/by-ip
    I->>A: ready heartbeat (+testInfo)

    U->>V: Start test
    V->>A: in_progress heartbeat
    V->>V: Execute validation / score
    V->>A: completed or stopped heartbeat
    V->>S: POST /api/integration/test-results

    U->>V: Exit
    V->>A: pending heartbeat
```
---

## ⚙️ Configuration — config.txt
```ini
[Management]
url=http://ect2.iptime.org:20223

[Test]
test_ip=192.168.1.100
```

| Key | Description |
|-----|-------------|
| `url` | Management system address |
| `test_ip` | Target device IP (used for standalone system tests only) |

---

## 🚀 How to Run

### Onefile
1. Download `ValidationTool_onefile.exe` and `config.txt` into the **same folder**
2. Set the management system URL in `config.txt`
3. Double-click the exe to launch

### Onedir
1. Download and extract the zip file
2. Run the exe inside the extracted folder (`config.txt` is already included)

---

## 🔨 Build

**Environment**
- Python 3.9.13
- PyInstaller 5.13.2
- Windows 10

### Onefile (config.txt distributed separately)
```bash
pyinstaller --onefile --windowed --splash=assets/image/splash/splash.png \
  --name ValidationTool_onefile_Level1 \
  --add-data "assets;assets" --add-data "config;config" \
  --add-data "core;core" --add-data "spec;spec" --add-data "ui;ui" main.py
```

### Onedir (config.txt included)
```bash
pyinstaller --onedir --windowed --splash=assets/image/splash/splash.png \
  --name ValidationTool_onedir_Level1 \
  --add-data "config.txt;." --add-data "assets;assets" --add-data "config;config" \
  --add-data "core;core" --add-data "spec;spec" --add-data "ui;ui" main.py
```

> For Level 3 build: remove `--windowed`, add `--console`, and set `DEBUG_LEVEL = 3` in `config/CONSTANTS.py`

---

## 📋 Releases

See the [Releases](../../releases) page for the latest builds and changelogs.
브랜치 설명은 한국어로 되어 있는 이름(정수인, 장예진)이 있어서 뺐어요. 필요하면 다시 넣어드
