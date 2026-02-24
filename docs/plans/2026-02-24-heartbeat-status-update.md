# Heartbeat Status Update Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 시험 상태 heartbeat를 2개(idle/busy)에서 6개(pending/ready/in_progress/completed/stopped/error) 규격으로 전환한다.

**Architecture:** APIClient에 공통 heartbeat 전송 메서드를 두고 상태별 래퍼를 제공한다. UI/실행 엔진(info_GUI, systemVal_all, platformVal_all)의 기존 전송 지점을 새 상태 정의에 매핑한다. 에러 경로는 errorMessage를 포함한 heartbeat를 추가 전송한다.

**Tech Stack:** Python, PyQt5, requests, pytest

---

### Task 1: APIClient heartbeat 공통화
- Modify: `api/client.py`
- Add: `send_heartbeat(status, test_info=None, error_message=None)`
- Add: `send_heartbeat_pending/ready/in_progress/completed/stopped/error`
- Keep: 기존 `send_heartbeat_idle/busy`는 하위호환 래퍼 유지

### Task 2: Info 페이지 상태 전송 매핑
- Modify: `ui/info_GUI.py`
- 시험정보 로드 성공 시 `ready` + full `testInfo` 전송
- 시험 시작 시 `in_progress` + `testRequestId`만 전송

### Task 3: 검증 실행기 상태 매핑
- Modify: `systemVal_all.py`, `platformVal_all.py`
- 완료 시 `completed`
- 중지/취소/실행중 창 종료 시 `stopped`
- update_view 예외 시 `error` + 에러 메시지

### Task 4: 회귀 테스트
- Add: `tests/test_api_client_heartbeat.py`
- requests.post mock으로 상태별 payload 검증
- 최소 대상: pending/ready/in_progress/error
