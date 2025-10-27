# API-info
import os

headers = {"Content-type": "application/json", "User-Agent": 'test'}
none_request_message = ['Capabilities',
                        'CameraProfiles',
                        'DoorProfiles',
                        'AccessUserInfos',
                        'SensorDeviceProfiles']
# 로컬 테스트용 주소 
<<<<<<< HEAD
# test-info -> (주의) auth_info의 id, pw: admin, 1234 아닐 시 digest auth 인증방식 작동하지 않음
company_name = "통합플랫폼테스트"
product_name = "통합플랫폼테스트제품"
=======
#test-info -> (주의) auth_info의 id, pw: admin, 1234 아닐 시 digest auth 인증방식 작동하지 않음
company_name = "물리보안기업"
product_name = "물리보안테스트제품"
>>>>>>> 4fc0caa98fd2234438b18f224cb618d8eb0de007
version = "v1.0"
test_category = "MAIN_TEST"
test_target = "물리보안"
test_range = "ALL_FIELDS"
auth_type = "Bearer Token"
auth_info = "a"
<<<<<<< HEAD
admin_code = ""
url = "https://127.0.0.1:8080"
contact_person = "김철수"
model_name = "v1.0"
request_id = "cmh1yg49v000t9y0jdr1wwuja"
specs = [
    ["cmgvieyak001b6cd04cgaawmm_inSchema", "cmgvieyak001b6cd04cgaawmm_outData", "cmgvieyak001b6cd04cgaawmm_messages",
     ""]]
=======
admin_code = "1234"
url = "https://127.0.0.1:8080"

specs = [["cmgyv3rzl014nvsveidu5jpzp_outSchema","cmgyv3rzl014nvsveidu5jpzp_inData","cmgyv3rzl014nvsveidu5jpzp_messages",""]]
>>>>>>> 4fc0caa98fd2234438b18f224cb618d8eb0de007

# opt 검증 - False 이면 검증 안함, 현재는 루프문에 의해 True인 상황 
flag_opt = False
if test_range == "ALL_FIELDS":
    flag_opt = True

# 시험 분야별 spec 정의 (인덱스 순서 중요!)
# specs = [
#     ["spec_001_inSchema", "spec_001_outData", "spec_001_messages", "spec_001_webhookSchema", "spec_001_webhookData", "영상보안 시스템 요청 메시지 검증 API 명세서"],
#     ["spec_0011_inSchema", "spec_0011_outData", "spec_0011_messages", "spec_0011_webhookSchema", "spec_0011_webhookData", "보안용 센서 시스템(요청검증)"]
# ]

# 선택된 시험 분야의 인덱스 (0: 영상보안, 1: 보안용센서)
selected_spec_index = 0
trace_path = os.path.join("results", "trace")
enable_retry_delay = False  # False 권장: 불필요한 sleep 제거

# test-opt
'''
✅ SPEC_CONFIG: specification.id별 설정 (통합 관리)
- 각 spec의 API별로 trans_protocol, time_out, num_retries 설정
- trans_protocol: 'basic' (일반), 'LongPolling' (실시간), 'WebHook' (웹훅, 현재 미완성)
- time_out: 메시지별 timeout 설정 시간 (ms)
- num_retries: 메시지별 검증 반복 횟수
'''

# ✅ specification.id별 설정 (신규 통합 방식)
# 플랫폼(cmg90, cmg7e, cmg7b)
# 시스템(cmgat, cmgas, cmga0)

SPEC_CONFIG = [
    {
        "group_name": "물리보안",
        "group_id": "cmgzwohuq01y8vsvep0hpuuf4",
        "cmgyv3rzl014nvsveidu5jpzp": {
    "test_name": "영상보안시스템_new",
    "specs": ['cmgvieyak001b6cd04cgaawmm_inSchema', 'cmgvieyak001b6cd04cgaawmm_outData', 'cmgvieyak001b6cd04cgaawmm_messages', 'cmgvieyak001b6cd04cgaawmm_webhook_OutSchema', 'cmgvieyak001b6cd04cgaawmm_webhook_inData'],
    "api_name": ['인증', '전송 지원 기능 정보 연동', '카메라 목록 연동', '저장된 영상 목록 연동', '실시간 영상 정보 연동', '저장된 영상 정보 연동', '실시간 이벤트 분석 정보 연동', '저장된 이벤트 분석 정보 연동'],
    "api_id": ['step-1-77lxvxrit', 'step-2-ln57b7ahz', 'step-1-354py0pz2', 'step-2-hyto4xrf1', 'step-5-dfxmyzzsw', 'step-6-pflcyt2cp', 'step-7-166n5ivbf', 'step-8-fff2u2432'],
    "api_endpoint": ['/Authentication', '/Capabilities', '/CameraProfiles', '/StoredVideoInfos', '/StreamURLs', '/ReplayURL', '/RealtimeVideoEventInfos', '/StoredVideoEventInfos'],
    "trans_protocol": ['basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'WebHook', 'basic'],
    "time_out": [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
    "num_retries": [1, 1, 1, 1, 1, 1, 1, 1]
}
    }
]

digest_security_res = [
    'ae8dd6b1b3b7ebcddccf77e1e1cee42ac3d3d90e4c2cc111c4d2aab17870e8cf',
    '16ba752619484f662586478081c99daeb3126df5988fd7956fbb302de964f958',
    'cbb6f7a008936a0cc32b34b87721eb11af1b141733dfd717627e13fb19e3c27a',
    '5196b2513bbc86a08386720240053b2a29a628aac0e1fdaf372e7f220e984538',
    '99f13e073da1f5e4e6db0d37d9f99285e4439ef57820518067ce56847613239f',
    'a723679b7b81137cb0b560428ea120fc3468ca3f2c3d2bc120a2f9a84b3a5a49'
]
