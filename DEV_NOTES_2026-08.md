# 개발 노트 — 2026-08-13 ~ 08-14 집중 디버깅 기록

다음 주 시험을 앞두고 두 PC(단일시스템 도구 ↔ 통합시스템 도구)를 서로 붙여 리허설하며
발견·수정한 내용의 전체 기록이다. 처음 보는 개발자가 "왜 이렇게 고쳤는지"와
"무엇이 아직 남았는지"를 이 문서만으로 파악할 수 있게 쓴다.

---

## 0. 전제 지식 (이 문서를 읽는 데 필요한 배경)

### 시험 구성
- **단일시스템 도구** (`systemVal_all.py`) = **플랫폼 역할**. 요청을 만들어 보내고,
  받은 응답/웹훅을 검증한다.
- **통합시스템 도구** (`platformVal_all.py`) = **장치 역할**. 요청을 받아 응답을
  만들어 보내고, 받은 요청을 검증한다.
- 리허설에서는 두 역할을 모두 우리 도구가 수행하므로, **요청 생성·응답 생성·검증
  세 곳의 설정이 서로 아귀가 맞아야** 통과한다. 한 곳만 어긋나도 FAIL이 난다.

### 관리도구(관리시스템)와 spec/ 폴더
- 시험 시작 시 관리시스템에서 시나리오 설정을 내려받아 `spec/*.py`로 저장한다.
  - `Data_request/response.py` — 메시지 템플릿(예시 값)
  - `Constraints_request/response.py` — **값 생성 규칙** (preset/참조/랜덤/범위)
  - `validation_request/response.py` — **검증 규칙** (list-match/field-match/허용값…)
  - `Schema_*.py` — 필드 유무·타입
- **오류 원인 구분법**: `spec/` 파일을 열어 본다.
  - 설정이 제대로 있는데 이상 동작 → **도구 코드 문제**
  - 설정이 비었거나 엉뚱함 → **관리도구 등록 문제**
  - 참조가 있는데 값이 빈 채 나감 → 참조할 기록을 못 찾은 것 (코드 or 단계 순서)

### 오류 화면 읽는 법
- `조회된 doorID 목록` = 규칙의 referenceEndpoint에서 가져온 **기준값**
  (대부분 자기 자신의 **요청**에 적힌 목록이다. "조회된"이라는 문구에 속지 말 것)
- `입력값` = 검사 대상 중 **걸린 항목만** 표시된다. 통과한 항목은 안 보인다.

### 디버깅 팁
- `results/trace/*.ndjson`은 **매 실행 시 초기화**된다. 증상이 보이면 즉시 폴더째 복사.
- `results/request_results.json` = 장치 역할(요청 수신) 결과,
  `results/response_results.json` = 플랫폼 역할(요청 송신) 결과. 송수신 전문이 남는다.
- 콘솔 로그가 최고의 증거다. (§2-6의 String 시각 버그도 로그의 Traceback으로 확정함)

---

## 1. 시각 필드 String 전환 배경

내부 회의로 17자리 시각 필드(startTime/endTime/eventTime 등)를 **Number → String으로
통일**하기로 결정했다(JS의 2^53 정밀도 문제). 관리시스템 스펙은 순차 전환 중이며,
**도구 코드 곳곳에 "시각=숫자" 가정이 남아 있던 것**이 8/13~14 버그 다수의 뿌리다.
새 코드를 쓸 때 시각 필드는 반드시 String/Number 양쪽을 처리할 것.

---

## 2. 고친 것 (커밋 순)

### 2-1. 맥락 검증 참조가 서로 덮어쓰던 문제 — `800866f`
- **증상**: ac003 DoorControl 판정이 회차마다 달라짐. `조회된 doorID 목록`에
  구독 요청이 아닌 웹훅 이벤트 값이 뜸.
- **원인**: 한 단계에 참조 엔드포인트가 같고 방향만 다른 규칙이 둘 있으면
  (DoorControl: doorID=REQUEST 참조 / commandType=RESPONSE 참조) 참조 저장소
  `reference_context`의 키가 엔드포인트뿐이라 나중 규칙이 앞 규칙의 자료를 덮어씀.
- **수정**: 키를 `엔드포인트#방향`으로 분리. `core/functions.py`의
  `ref_context_key()` / `get_reference_data()`, 적재부는 platformVal·systemVal 양쪽.
  방향 없는 옛 키도 폴백으로 유지(하위 호환).

### 2-2. DoorControl 전용 "평탄화" 블록 삭제 — `800866f`
- **증상**: 오류 메시지에 `door0002 | door0002`처럼 같은 값이 두 번 표시.
- **원인**: 2-1을 우회하려고 넣었던 47줄짜리 특례가 doorList의 doorID를 최상위에
  복사해 얹어, 재귀 수집(`collect_all_values_by_key`)이 같은 값을 두 번 셈.
- **수정**: 2-1로 원인이 사라졌으므로 블록 전체 삭제(platformVal_all.py).

### 2-3. commandType 빈 값 + 반대 명령 미선택 — `800866f`
- **증상**: DoorControl 요청의 commandType이 `""`로 전송. 이후엔 Lock 상태 문에
  또 Lock을 보냄.
- **원인 1**: 관리도구 제약은 후보값을 `validValues`로 주는데 생성 코드는
  `allowedValues`만 조회(이름 불일치) → 후보 없음 → 템플릿 빈 문자열 전송.
- **원인 2**: 문 상태 저장소 `door_memory`는 장치 역할일 때만 채워짐. 플랫폼
  역할에선 비어 있어 현재 상태를 모른 채 아무 값이나 선택.
- **수정**: `core/data_mapper.py` — 두 이름 모두 인정 + `_find_reference_state()`로
  플랫폼 역할에선 수신한 웹훅 이벤트에서 현재 상태를 찾아 반대 명령 선택.

### 2-4. (같은 커밋에 동승한 별도 작업)
- `core/validation_registry.py` — `_without_disabled_error_response_expectations()`:
  오류 유도가 꺼진 상태(§3)에서는 code=201 등 오류 응답 전용 code/message 기대
  규칙을 검증에서 제외. **이 변경으로 그동안 code 오류가 검증을 중단시켜 가려져
  있던 후속 필드 오류들이 일제히 드러났다.** 8/13~14에 "갑자기 문제가 늘어난"
  것처럼 보인 주된 이유.
- `core/utils.py` — 외부 CONSTANTS 재로드 목록에 request_id 등 식별자 추가
  (결과가 이전 평가 건으로 전송되던 문제).

### 2-5. 조회 응답 필터 + 줄별 채우기 — `8bb468c` (중간에 `40da25a`→`9e7d549` 시행착오 있음)
- **증상 1**: ac002 StoredVerifEventInfos에서 door0001만 조회했는데 응답에
  door0002 기록이 섞여 나옴 → "요청하지 않은 문" FAIL.
- **증상 2**: (1차 수정 후) door0001 기록이 두 번 복제되어 나옴.
- **원인**: 장치 역할의 조회 응답이 관리도구 예시(2줄)를 조회 조건과 무관하게
  통째로 반환. 1차 수정(40da25a)으로 값 채우기를 열자, 채우기가 "첫 줄만 본으로
  삼아 줄 수만큼 복제"하는 구조라 door0002 줄이 사라지고 door0001이 복제됨 → revert.
- **최종 수정**: `core/data_mapper.py`
  - `_filter_rows_by_request()` — 저장된 줄 중 **요청한 ID의 줄만** 남김.
    조회 조건 없는 요청(DoorProfiles 등)은 전체 유지. 템플릿 ID가 빈
    영상 계열(요청 개수만큼 늘리는 구조)은 자동 제외.
  - `_generate_from_template()` — 템플릿 줄이 **여럿이면 줄별로** 채우고,
    한 줄이면 기존처럼 요청 개수만큼 늘림(영상 계열 유지).
  - 실질 영향 범위는 StoredVerifEventInfos 1곳(다른 다줄 템플릿은 전부 preset이라
    원본 그대로 나감 — 수정 전후 바이트 동일함을 대조로 확인).

### 2-6. String 시각 request-range TypeError — `8bb468c`
- **증상**: vid001 RealtimeVideoEventInfos 웹훅에서 camID·eventName·startTime이
  전부 빈 값. (vid002/sensor002 Stored* 계열도 동일 증상 보고됨)
- **원인**: 시각 String 전환 후 범위 생성(`request-range`)의 `min_val >= max_val`
  비교가 str-int TypeError로 사망 → **예외로 채우기 전체가 중단**되어 웹훅
  페이로드가 템플릿 빈 값 그대로 나감. (로그의 Traceback으로 확정:
  `_generate_item` 내 비교 지점)
- **수정**: `core/data_mapper.py` `_to_number()` — 내부는 숫자로 변환해 비교·생성,
  **원본이 문자열이면 문자열로 출력**. Number 스펙(미전환)은 기존대로 숫자 출력.

### 2-7. 결과 전송 testRange가 관리시스템에서 "전체 필드"로 표시 — `bf96540`
- **증상**: 필수 필드로 검증했는데 관리시스템 결과 화면에는 전체 필드로 표시.
- **원인**: 외부 설정에 남아 있던 `"필수 필드, 필수 필드, 필수 필드"`(그룹별 연결
  문자열)가 그대로 전송됨. 결과 API는 `ALL_FIELDS`/`REQUIRED_FIELDS` enum만
  해석하므로 미해석 값 → 기본 표시(전체 필드). ※ by-ip가 내려주는 값은 두 PC
  모두 REQUIRED_FIELDS 정상임을 실측 — 서버 버그 재발 아님.
- **수정**: `core/functions.py` `normalize_result_test_range()` — 완전일치 판별을
  **포함 판별**로 강화. 연결 문자열·빈 값도 반드시 enum 하나로 정리
  (하나라도 "전체"가 있으면 ALL_FIELDS).

### 2-8. 오류 유도 변조의 타입 유지 — (이 문서와 같은 커밋)
- **증상**: sensor002 StoredSensorEventInfos에서 startTime이 숫자 0으로 수신되어
  "Str가 와야 하는데 Number가 왔습니다" 타입 오류.
- **원인**: 오류 유도(§3)의 `replace_start_time()`이 String 전환 이전 구현이라
  숫자 0을 주입. 201 유도의 의도는 "형식은 유효하되 내용만 무의미한 요청"인데,
  숫자 0은 **규격(타입) 검증에서 먼저 탈락**해 유도가 성립하지 않음.
- **수정**: `core/data_mapper.py` `replace_start_time()` — 원본이 문자열이면
  `"0"`, 숫자면 `0`으로 **타입을 유지한 채** 값만 무효화.

### 2-9. 빌드 설정
- `ValidationTool_onefile_Level1.spec`의 `console=False`(windowed)로 되어 있어
  그동안 콘솔 없는 빌드가 나가고 있었음 → `console=True`로 고정.
  **주의: `*.spec`은 .gitignore 대상이라 이 설정은 로컬에만 있다.** 새 PC에서
  클론 후 빌드하면 다시 확인할 것. (빌드 로그의 부트로더가 `run.exe`면 console,
  `runw.exe`면 windowed)
- 빌드 절차: `.\build.ps1` → `dist\<MMdd>\` 산출. **exe 옆에 `config.txt` 필수**
  (없으면 관리시스템 주소가 localhost로 떨어짐). 마지막의
  "[경고] 예상 산출물을 찾지 못했습니다"는 스크립트가 찾는 이름과 spec `name=`이
  달라서 뜨는 것으로 무시. **새 exe는 반드시 두 PC 모두 교체.**

---

## 3. 오류 유도 시험 기능 (201/400) — 현재 상태

관리도구에 값을 제대로 등록해 두고, **도구가 전송 직전에 일부러 요청을 망가뜨려**
상대의 오류 처리(201 정보 없음 / 400 잘못된 요청)를 검사하는 기능.

- 스위치: `config/CONSTANTS.py`의 `ENABLE_ERROR_REQUEST_MUTATION` (현재 **True**).
  exe 옆 외부 `config/CONSTANTS.py`가 있으면 **그 값이 우선** — 재빌드 없이 현장에서
  켜고 끌 수 있다.
- 변조 방법: `core/data_mapper.py::_applied_codevalue()` —
  응답 검증 규칙의 code 기대값이 "201"이면 `replace_start_time()`(startTime→0/"0"),
  "400"이면 `change_random_field_type()`(임의 필드 타입 변조).
- 대상 API(스펙에 code≠200 기대가 등록된 곳, 전부 단일시스템 스펙): 4곳
  | 스펙 | API | 기대 code |
  |---|---|---|
  | 단일 영상 | StoredVideoInfos | 201 |
  | 단일 영상 | StreamURLs | 400 |
  | 단일 출입 | StoredVerifEventInfos | 201 |
  | 단일 센서 | StoredSensorEventInfos | 201 |
- 403/404 등 나머지 오류 코드: 정의(`spec/ResponseCode.py`)만 있고 **유도 기능 미구현**.
  현재 스펙은 201/400만 요구하므로 문제 없으나, 스펙에 추가되면 구현 필요.

### ⚠️ 리허설에서 201 채점이 절대 통과할 수 없는 이유 (미해결)
장치 역할이 이상한 요청에 201/400/404로 응답하는 로직이
`api/api_server.py::_check_request_errors()`(±237행)에 **구현되어 있으나, 함수
정의와 호출부 2곳(±530행, ±741행)이 전부 `'''` 주석으로 비활성화**되어 있다.
따라서 우리 도구끼리 붙이면 변조 요청에도 항상 200+정상 데이터가 응답되어
201 기대 채점은 반드시 FAIL이다. (실제 업체 장비가 상대라면 그쪽이 201을 주면
되므로 실전에는 영향 없음)

**되살릴 때 함께 손볼 것** (기록만 해둠 — 박사님이 의도적으로 꺼두셨는지 먼저 확인):
1. 주석 해제 (함수 1곳 + 호출부 2곳)
2. `_check_time_range()`가 Unix 초·int 가정 → 17자리 String 시각 대응 필요.
   기준도 "endTime이 2년 전보다 과거"라는 자의적 규칙 대신, 변조 방식과 짝이 맞는
   "startTime이 0/'0'이면 201"로 정리 권장 (유도-응답-채점 삼자가 같은 기준을 봐야 함)
3. `_check_device_exists()`의 valid_device_ids 채움 경로 검증

---

## 4. 남은 과제 — 도구 코드

| # | 내용 | 위치 | 비고 |
|---|---|---|---|
| 1 | **웹훅 이벤트에 맥락 검증 규칙이 아예 전달되지 않음** | registry가 in/out만 지원 + 웹훅 검사 호출부(`platformVal_all.py:±1083`, `systemVal_all.py:±1453`)가 `validation_rules` 미전달 | 관리도구의 `*_webhook_*_validation` 규칙 전체가 다운로드만 되고 한 번도 실행된 적 없음. "제어 후 상태 반영 확인"(결과조회 웹훅 doorSensor=commandType) 같은 핵심 검사가 무효. 연결 시 기존 100% 단계들이 FAIL로 바뀔 수 있어 시험 후 적용 권장 |
| 2 | **DoorControl doorID 생성이 관리도구 설정을 무시하고 템플릿 고정값 사용** | `core/data_mapper.py` commandType 블록 (①받은요청→②door_memory→③템플릿 순서, 플랫폼 역할은 ①②가 항상 빈 상태) | 1차 구독은 무작위 부분집합인데 제어는 고정 door0001 → **약 25% 확률로 ac003 FAIL** (문 2개 기준, 실측 재현됨). 구독한 문(latest_events의 /RealtimeDoorStatus REQUEST)에서 고르도록 수정 필요 |
| 3 | 검증 쪽 `excludeReference` 연산자 미구현 | `core/functions.py::_validate_valid_value_match` — 참조를 인자로 받지도 않고 equalsAny로 동작 | "현재 상태와 반대 명령인가" 검사 불가. **규격서(기술보고서 v2.0)에 근거 없음** — 박사님 확인 후 결정 |
| 4 | 참조 방향이 REQUEST/RESPONSE 둘뿐 (WEBHOOK 표현 불가) | 규칙 적재부의 `direction = "REQUEST" if "request-field" in validationType else "RESPONSE"` | doorSensor처럼 웹훅에만 있는 값을 참조하는 규칙이 엉뚱한 응답({"code":"성공"})을 집음. #1과 함께 설계 필요 |
| 5 | 미지원 validationType은 경고만 남기고 통과 처리 | `core/functions.py` 디스패처 else | 관리시스템에 새 유형이 추가되면 검사 없이 전부 합격됨 |
| 6 | code≠기대값이면 검증 전체 break | `core/functions.py:±329` | 오류 이유가 한 줄로 뭉개짐. §2-4로 정상 모드에선 우회되나 구조는 남음 |
| 7 | §3의 오류 응답 로직(400/201/404) 주석 처리 | `api/api_server.py` | 위 참조 |

## 5. 남은 과제 — 관리도구 설정 (코드 무관, 관리시스템에서 수정)

| # | 위치 | 필드 | 문제 → 조치 |
|---|---|---|---|
| 1 | 통합 sensor003 > SensorDeviceControl > 검증(요청) | sensorDeviceID | 유효값일치+videoEvent(Loitering/Intrusion)로 잘못 등록 → **목록대조** + 참조 `/SensorDeviceProfiles`의 sensorDeviceID |
| 2 | 단일 sensor003 > SensorDeviceControl > 전송(요청) | commandType | preset인데 값 없음 → `AlarmOn` 지정 (4단계엔 제외할 이전 상태가 없음 — SensorDeviceProfiles 응답에 상태 필드 없음) |
| 3 | 단일 ac002 > StoredVerifEventInfos > 전송(요청) | eventFilter | 자기참조+필드미선택 → 참조 제거, 후보값(AuthSuccess/AuthFail)만 (빈 값 전송의 원인) |
| 4 | 통합 ac003 > RealtimeDoorStatus2 > 검증 | doorList.doorID | `request-field-match`(완전일치) → `request-field-list-match` (1차에 두 문 구독 후 제어한 문만 재구독하는 정상 흐름이 불합격됨) |
| 5 | 단일 **신규 스펙** vid002(cmsmhhyl5…)·sensor002(cmsmj2a0g…) > 전송(요청) | camList.camID 등 전 필드 | 전부 preset·참조 없음 → 예시값(cam0001, 2022년 날짜, "배회")이 그대로 전송됨. ac002 신규 스펙(cmsmiz4rk…, 참조 정상)을 본떠 `/CameraProfiles`·`/SensorDeviceProfiles` 참조 걸기 |

- 관리시스템 서버가 간헐적으로 503을 반환(test-steps 조회 실패 — StoredObjectAnalyticsInfos
  단계 설정 미수신 사례 있음). 재현 시 재시도.

## 6. 표기 불일치 — 규격서 vs 관리도구 (박사님 확인 대상)

| 항목 | 규격서(기술보고서 v2.0) | 관리도구/도구 |
|---|---|---|
| DoorControl commandType | `"unlock"` (소문자) | `Lock` / `Unlock` |
| SensorDeviceControl commandType | `"Alarm\|On"` | `AlarmOn` / `AlarmOff` |
| doorSensor 값 체계 | `"0"`=open / `"1"`=closed | `Lock` / `Unlock` 문자열 |
| ac002 eventName | (응답 예시 `"성공"`) | 규칙 기대는 `AuthSuccess`/`AuthFail` |

또한 규격서에는 excludeReference(현재 상태와 반대 명령) 규정이 없다
("반대/현재 상태/상태 변경" 표현 0회).

## 7. 회귀 시험

`temp/` 아래, git 추적됨. 실행: `.venv\Scripts\python.exe temp\test_*.py`

| 파일 | 검증 내용 |
|---|---|
| test_reference_context_direction.py | 참조가 요청/응답끼리 덮어쓰지 않음 (§2-1) |
| test_commandtype_generation.py | commandType이 문 상태의 반대값 (§2-3) |
| test_response_row_filter.py | 조회 응답이 요청 조건의 기록만 반환 (§2-5) |
| test_webhook_string_time.py | String/Number 시각 모두 웹훅 값 정상 생성 (§2-6) |
| test_result_test_range.py | 결과 testRange가 항상 enum (§2-7) |
| test_error_mutation.py | 변조가 원본 타입 유지 (§2-8) |

별도: `tests/test_error_response_rule_suppression.py` (§2-4, 실행 시
`PYTHONPATH=프로젝트루트` 필요)
