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

## Architecture

```mermaid
flowchart TD
    A[main.py\nApp entry / window routing] --> B[ui/info_GUI.py\nTest setup page]
    B --> C[platformVal_all.py\nPlatform validation page]
    B --> D[systemVal_all.py\nSystem validation page]

    B --> E[api/client.py\nManagement API client]
    C --> E
    D --> E

    C --> F[core/functions.py\nValidation utils / result JSON builder]
    D --> F

    C --> G[api/api_server.py\nLocal receiver server]
    D --> G

    C --> H[results/\nIntermediate/final outputs]
    D --> H

    E --> I[(Management Server)]
```

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
