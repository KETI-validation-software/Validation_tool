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


## Project Structure

```text
validation-tool/
├─ requirements.txt
├─ config/                     # 설정 관련
│   ├─ CONSTANTS.py
│   ├─ config.txt
│   └─ key0627/                # 인증 키 파일
│
├─ core/                       # 공통 엔진 / 도메인
│   ├─ functions.py            # 공통 유틸
│   └─ json_checker.py         # JSON 스키마 검증
│
├─ api/                        # API 서버/웹훅
│   ├─ api_server.py
│   ├─ webhook_server.py
│   └─ routes/                 # 엔드포인트별 처리
│
├─ specs/                      # 명세 (Request/Response + Schema)
│   ├─ bio/
│   │   ├─ bioRequest.py
│   │   ├─ bioSchema.py
│   │   └─ requests/           # JSON 예제
│   ├─ security/
│   │   ├─ securityRequest.py
│   │   ├─ securitySchema.py
│   │   └─ requests/
│   └─ video/
│       ├─ videoRequest.py
│       ├─ videoSchema.py
│       └─ requests/
│
│
├─ assets/                     # 리소스
│   ├─ fonts/
│   │   ├─ NamuGothic.ttf
│   │   └─ NamuGothic.pkl
│   └─ images/
│       └─ 버튼 이미지들
│
├─ launcher_GUI.py            # 장예진 담당
├─ platformVal_all.py         # 정수인 담당
├─ systemVal_app.py           # 정수인 담당
└─ 
```
<img width="3544" height="1660" alt="image" src="https://github.com/user-attachments/assets/0e296baf-8829-415f-8ab6-ce84c86d23de" />

## 브랜치
runner: 시험 진행 GUI (정수인)

info: 시험 정보 GUI (장예진)
