# Spec-based Refactoring Summary

## 개요
기존 하드코딩된 9개 API 검증 방식에서 `CONSTANTS.specs` 기반의 동적 spec 로딩 방식으로 리팩토링되었습니다.

## 주요 변경사항

### 1. Import 구조 변경

**이전:**
```python
from spec.video.videoData_response import spec_002_inData, spec_002_messages
from spec.video.videoData_request import spec_001_outData, spec_001_messages
from spec.video.videoSchema_request import spec_001_inSchema
from spec.video.videoSchema_response import spec_002_outSchema
```

**이후:**
```python
import spec.video.videoData_response as video_data_response
import spec.video.videoData_request as video_data_request
import spec.video.videoSchema_request as video_schema_request
import spec.video.videoSchema_response as video_schema_response
```

### 2. CONSTANTS.specs 구조

```python
specs = [
    [
        "spec_001_inSchema",        # Request schema name
        "spec_001_outData",         # Request data name
        "spec_001_messages",        # API message names
        "spec_001_webhookSchema",   # Webhook schema name
        "spec_001_webhookData",     # Webhook data name
        "영상보안 시스템 요청 메시지 검증 API 명세서"  # Description
    ]
]
```

### 3. 새로운 메서드: `load_specs_from_constants()`

두 파일 모두 (`platformVal_all.py`, `systemVal_all.py`)에 추가된 메서드:

```python
def load_specs_from_constants(self):
    """CONSTANTS.specs 설정에 따라 동적으로 spec 데이터 로드"""
    spec = CONSTANTS.specs[0]
    
    # Load request-side data
    self.videoInSchema = getattr(video_schema_request, spec[0], [])
    self.videoOutMessage = getattr(video_data_request, spec[1], [])
    self.videoMessages = getattr(video_data_request, spec[2], [])
    self.videoWebhookSchema = getattr(video_schema_request, spec[3], [])
    
    # Load response-side data (spec_001 -> spec_002 변환)
    self.videoOutSchema = ...
    self.videoInMessage = ...
    self.videoWebhookInSchema = ...
    
    # 디버그 정보 출력
    print(f"[DEBUG] Loaded spec: {self.spec_description}")
    print(f"[DEBUG] API count: {len(self.videoMessages)}")
```

### 4. 동적 테이블 생성

**이전:**
```python
self.tableWidget = QTableWidget(9, 8)  # 고정된 9개 행

self.step_names = [
    "Authentication", "Capabilities", ...  # 하드코딩
]
```

**이후:**
```python
api_count = len(self.videoMessages)  # 동적 계산
self.tableWidget = QTableWidget(api_count, 8)   # 열은 고정이니까 (항목들)

self.step_names = self.videoMessages  # 동적 로드
```

### 5. step_buffers 동적 생성

**이전:**
```python
self.step_buffers = [
    {"data": "", "error": "", "result": "PASS"} for _ in range(9)
]
```

**이후:**
```python
self.step_buffers = [
    {"data": "", "error": "", "result": "PASS"} for _ in range(len(self.videoMessages))
]
```

### 6. 모든 변수 참조 업데이트

전역 변수에서 인스턴스 변수로 변경:
- `videoInSchema` → `self.videoInSchema`
- `videoOutSchema` → `self.videoOutSchema`
- `videoMessages` → `self.videoMessages`
- `videoInMessage` → `self.videoInMessage`
- `videoOutMessage` → `self.videoOutMessage`
- `videoWebhookSchema` → `self.videoWebhookSchema` (또는 `self.videoWebhookInSchema`)

## 파일별 주요 수정

### platformVal_all.py
1. Import 구조 변경
2. `__init__()` 메서드에 `load_specs_from_constants()` 호출 추가
3. `load_specs_from_constants()` 메서드 추가
4. `init_centerLayout()` - 동적 테이블 생성
5. `sbtn_push()` - self.video* 변수 사용
6. `show_combined_result()` - self.videoInSchema 사용
7. `ResultPageDialog` - 동적 API 개수 지원

### systemVal_all.py
1. Import 구조 변경
2. `__init__()` 메서드에 `load_specs_from_constants()` 호출 추가
3. `load_specs_from_constants()` 메서드 추가
4. `init_centerLayout()` - 동적 테이블 생성
5. `get_setting()` - self.video* 변수 사용
6. `show_combined_result()` - self.videoOutSchema 사용
7. `start_btn_clicked()` - 동적 API 카운트 초기화
8. `init_win()` - 동적 버퍼 및 카운트 초기화
9. `ResultPageDialog` - 동적 API 개수 지원

## 향후 확장성

이제 `CONSTANTS.specs`에 새로운 spec을 추가하면:
1. spec 파일만 작성 (예: spec_003_*)
2. CONSTANTS.specs에 항목 추가
3. 코드 수정 없이 자동으로 로드 및 검증

예시:
```python
specs = [
    ["spec_001_inSchema", "spec_001_outData", ...],  # 영상보안
    ["spec_011_inSchema", "spec_011_outData", ...],  # 생체인식
    ["spec_021_inSchema", "spec_021_outData", ...],  # 출입통제
]
```

여러 spec 동시 지원도 가능하도록 구조가 준비되었습니다.

## 테스트 권장사항

1. 기존 9개 API가 정상 작동하는지 확인
2. CONSTANTS.specs 항목 수정 후 동작 확인
3. 새로운 spec 추가 시 동작 확인
4. 테이블 행 개수가 API 개수와 일치하는지 확인
5. 상세 내용 팝업이 정상 표시되는지 확인

## 디버그 로그

프로그램 시작 시 다음 로그가 출력됩니다:
```
[DEBUG] Loaded spec: 영상보안 시스템 요청 메시지 검증 API 명세서
[DEBUG] API count: 9
[DEBUG] API names: ['Authentication', 'Capabilities', ...]
```

이를 통해 spec이 정상 로드되었는지 확인할 수 있습니다.
