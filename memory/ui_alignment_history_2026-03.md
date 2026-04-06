# UI Alignment History (2026-03)

## Purpose
- 2026-03 기간의 UI 정렬, 결과 테이블 구조, 실시간 상태 표현 변경 이력을 한 문서로 묶는다.
- 기존 분산 문서:
- `archive/06_2026-03-18_ui_alignment_summary.md`
- `archive/07_2026-03-19_ui_alignment_summary_page4.md`
- `archive/08_2026-03-19_webhook_badge_and_timer_alignment.md`
- `archive/09_2026-03-20_ui_refinement_summary.md`

## 2026-03-18 Page 3 Alignment

### Scope
- Page 3 (시험 시작 페이지) Figma 정렬
- 주요 대상:
- 좌측 내비게이션
- 분할 배경
- URL 헤더 행
- API 테이블 clipping
- 모니터/점수 요약 간격
- fullscreen resize 동작

### Main changes
- 좌측 상단 이전 화면 내비게이션 추가 및 SVG 아이콘 교체
- 배경을 이미지 의존 방식에서 코드 기반 split background로 전환
- 시험 URL 행을 `시험 API` 헤더와 같은 수평선에 배치
- 공통/UI별 resize 로직을 맞춰 API 테이블 하단 clipping 수정
- 모니터와 점수 요약 영역의 세로 리듬 정렬

### Preserve as baseline
- score-summary 영역은 현재 anchor 위치를 기준으로 유지
- monitor 간격 조정이 필요해도 score-summary를 먼저 움직이지 않음
- divider 폭은 좌측 선택 박스와 같은 체감 폭으로 유지
- fullscreen에서도 URL 입력창이 API 헤더 폭과 함께 확장되어야 함

## 2026-03-19 Page 4 Alignment

### Result table structure
- 결과 테이블을 9컬럼에서 10컬럼으로 확장
- 컬럼 구성:
- 0: No
- 1: API Name + Webhook Badge
- 2: Timer Icon / Status Badge
- 3: Result Icon
- 4-8: Total / Pass / Fail / Retry / Score
- 9: Detail Button

### Visual sync
- 헤더 배경을 `#F8F9FA`로 조정
- 헤더 하단 border 추가
- API 명 셀을 좌측 정렬로 통일
- `WebhookBadgeLabel`을 API 이름 셀에 다시 통합

## 2026-03-19 Webhook Badge And Timer Column

### Interactive badge
- `WebhookBadgeLabel` hover tooltip 적용
- Page 2 / Page 3 / Page 4 모두 같은 badge 정책 사용

### Timer column
- Column 2에 타이머/상태 전용 컬럼 추가
- 상태 아이콘:
- `waiting_timer.png`
- `running_timer.png`
- `success_timer.png`
- `timeover_timer.png`

### State persistence impact
- `SystemStateManager`가 타이머 상태와 숫자 컬럼 이동을 같이 복원하도록 수정

## 2026-03-20 Final Refinements

### Spacing and margins
- Page 3 `api_section_layout` spacing을 2px로 조정
- Page 4 `info_title`/`result_label` 간격을 미세 조정

### Final Page 4 widths
- 최종 폭 기준:
- `[40, 243, 90, 100, 107, 107, 107, 90, 90, 90]`

### Bug fixes
- 헤더와 테이블 본문 시작선 12px 어긋남 수정
- scrollbar 유무에 따라 헤더 오른쪽 margin을 동기화
- resize 시 생기던 white line gap 수정

### UX refinements
- 이전 화면 내비게이션에 hand cursor 적용
- URL input 박스와 URL row 폭 확장

## Final Keep Rules
- Page 3는 `시험 URL`과 `시험 API`가 한 줄에서 정렬되어야 함
- Page 3/4 모두 실시간 상태 컬럼은 Column 2 기준 유지
- Page 4 결과 테이블은 Page 3와 같은 구조/정렬 원칙을 사용
- fullscreen/windowed 양쪽에서 동일한 정렬 기준을 유지해야 함

## Verification Pattern
- `python -m py_compile` 로 UI 파일 문법 확인
- 필요 시 결과 테이블/선택 동기화 관련 unittest 추가
