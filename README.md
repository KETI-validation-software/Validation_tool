## Validation_tool
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
  <img src="https://img.shields.io/badge/PyIn-5.13.2-orange" />
  <img src="https://img.shields.io/badge/GUI-PyQt5-ff69b4" />
</p>


### Project

<p align="center">
  <img src="https://github.com/user-attachments/assets/4fab21f4-f604-4669-906e-7dae5c8f8872" alt="splash_logo" />
</p>

- **GUI 기반 통합 검증 도구**  
  시험 담당자가 복잡한 명령어 없이 화면에서 바로 검증을 수행할 수 있도록 설계된 통합 도구입니다.  
  시험 설정, 실행, 모니터링, 결과 확인까지 하나의 UI 흐름으로 제공합니다.

- **관리 시스템 연동 자동화**  
  시험 관리 시스템과 API로 연동되어 시험 정보 조회, 상태 동기화, 결과 리포팅을 자동 처리합니다.

- **통합시스템 및 단일시스템 시험 지원**  
  하나의 프로젝트에서 통합시스템 시험과 단일시스템 시험을 모두 지원합니다.

- **실시간 검증 및 WebHook 시나리오 지원**  
  일반 API 응답 검증뿐 아니라 WebHook 기반 시나리오까지 지원합니다.  
  검증 결과는 단계별로 시각화되어 즉시 확인할 수 있습니다.

- **표준화된 상태 관리 (Heartbeat)**  
  시험 생명주기 상태를 표준화하여 서버와 동기화합니다.

- **결과 데이터 구조화 및 자동 저장**  
  시험 결과를 JSON 기반 구조로 생성하여 서버 전송 및 로컬 저장을 동시에 수행합니다.

---

### 실행 흐름

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

### 환경설정 — config.txt
```ini
[Management]
url=http://ect2.iptime.org:20223

[Test]
test_ip=192.168.1.100
```

| 항목 | 설명 |
|------|------|
| `url` | 관리시스템 주소 |
| `test_ip` | 시험 대상 IP (단일시스템 시험 시에만 사용) |

---

### 실행 방법

1. `ValidationTool_onefile.exe` 와 `config.txt` 를 **같은 폴더**에 다운로드
2. `config.txt` 에서 관리시스템 URL 설정
3. exe 더블클릭 실행

---

### 빌드 방법

**환경**
- Python 3.9.13
- PyInstaller 5.13.2
- Windows 10

```bash
pyinstaller --onefile --windowed --splash=assets/image/splash/splash.png \
  --name ValidationTool_onefile_Level1 \
  --add-data "assets;assets" --add-data "config;config" \
  --add-data "core;core" --add-data "spec;spec" --add-data "ui;ui" main.py
```

> Level 3 빌드 시: `--windowed` 제거 후 `--console` 추가, `config/CONSTANTS.py` 의 `DEBUG_LEVEL` 을 `3` 으로 변경

---

### 📋 릴리즈

최신 빌드 및 변경 사항은 [Releases](../../releases) 페이지를 참고하세요.
