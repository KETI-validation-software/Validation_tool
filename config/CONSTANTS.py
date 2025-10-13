#API-info
import os
headers = {"Content-type": "application/json", "User-Agent":'test'}
none_request_message = ['Capabilities',
                        'CameraProfiles',
                        'DoorProfiles',
                        'AccessUserInfos',
                        'SensorDeviceProfiles']
# 로컬 테스트용 주소 (플랫폼과 시스템이 같은 PC에서 실행되더야 함, 변경하면 평가 작동 안됌ㅜ)
#test-info -> (주의) auth_info의 id, pw admin, 1234 아닐 시 digest auth 인증방식 작동하지 않음!!!!!!!
company_name = "테스트기업"
product_name = "테스트시스템"
version = "v0.1"
test_category = "본시험"
test_target = "통합시스템"
test_range = "ALL_FIELDS"
auth_type = "Bearer Token"
auth_info = "1234"
admin_code = "123456789"
url = "https://127.0.0.1:8080"




specs = [["cmg90br3n002qihleffuljnth_inSchema","cmg90br3n002qihleffuljnth_outData","cmg90br3n002qihleffuljnth_messages",""],
         ["cmg7edeo50013124xiux3gbkb_inSchema","cmg7edeo50013124xiux3gbkb_outData","cmg7edeo50013124xiux3gbkb_messages",""],
         ["cmg7bve25000114cevhn5o3vr_inSchema","cmg7bve25000114cevhn5o3vr_outData","cmg7bve25000114cevhn5o3vr_messages",""]]

# opt 검증 - False 이면 검증 안함, 현재는 루프문에 의해 True인 상황 
flag_opt = False
if test_range == "ALL_FIELDS":
    flag_opt = True

# 시험 분야별 spec 정의 (인덱스 순서 중요!)
specs = [
    ["spec_001_inSchema", "spec_001_outData", "spec_001_messages", "spec_001_webhookSchema", "spec_001_webhookData", "영상보안 시스템 요청 메시지 검증 API 명세서"],
    ["spec_0011_inSchema", "spec_0011_outData", "spec_0011_messages", "spec_0011_webhookSchema", "spec_0011_webhookData", "보안용 센서 시스템(요청검증)"]
]

# 선택된 시험 분야의 인덱스 (0: 영상보안, 1: 보안용센서)
selected_spec_index = 0
trace_path = os.path.join("results", "trace")
#test-opt
'''
specification.id별 step 설정
각 spec의 steps 순서대로 trans_protocol, time_out, num_retries 설정
trans_protocol : 메시지별 실시간 송수신 메시지 여부, None-실시간 아님, LongPolling, WebHook은 설정에 따라 동작 -> 잠깐 웹훅으로 변경
time_out : 메시지별 timeout 설정 시간 (ms)
num_retries : 메시지별 메시지 검증 횟수
'''

#나중에 삭제
trans_protocol = [None, None, None, None, None, None, 'WebHook', None, None]
time_out = [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000]
num_retries = [1, 2, 3, 2, 1, 2, 3, 2, 1]


# specification.id별 설정
SPEC_CONFIG = {
    "cmg90br3n002qihleffuljnth": {
        "trans_protocol": ['basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'basic'],
        "time_out": [5000, 5000, 5000, 5000, 5000, 5000, 5000],
        "num_retries": [3, 3, 2, 2, 3, 2, 1]
    }
,
    "cmg7edeo50013124xiux3gbkb": {
        "trans_protocol": ['basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'basic'],
        "time_out": [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
        "num_retries": [3, 1, 2, 1, 3, 1, 1, 1]
    }
,
    "cmg7bve25000114cevhn5o3vr": {
        "trans_protocol": ['basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'basic', 'basic'],
        "time_out": [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
        "num_retries": [3, 1, 2, 2, 3, 1, 1, 1, 5, 1, 1, 1]
    }
}


#etc
digest_vid_res = [
 'ae8dd6b1b3b7ebcddccf77e1e1cee42ac3d3d90e4c2cc111c4d2aab17870e8cf',
    '16ba752619484f662586478081c99daeb3126df5988fd7956fbb302de964f958',
    '0b291354cb2338955fbc81c904f7bcb171906852ed52365f958eddf63ec42c97',
    'ebd7297452fb427685a83ccf4cb96b00af3d529a8e3443b0f88e51277c507ded',
    'f92fc4612c8625ab118e759e1238e03957e9146df9da38bfbf4fb0c8e77cf203',
    'c8093c4727aa4aadf69632184eea3080876a398f146db439bad8edf9e6cd56e2',
    '46b0a8a762095f685e6b88218480d45bccbb5f8cd3200423417593f5bff2ed0a',
    'e4151b19d396475ab65881e846873c2f2e8be2ca9d4fa725aa65e2b65e73418d']

digest_bio_res = [
   'ae8dd6b1b3b7ebcddccf77e1e1cee42ac3d3d90e4c2cc111c4d2aab17870e8cf',
   '16ba752619484f662586478081c99daeb3126df5988fd7956fbb302de964f958',
   '541f9497d3e62b19e39117abe07775bc0380c2d54cd565cb23b72cb628103588',
   'f57d4bbd6647d93ebbc4c20065507565c9ea0b127c9ee736e9fa655bca2eeaf1',
   '86c0a2818b29f016af13fd263a93e16cb125db60c02f8a0b241b75d535f03136',
   '1d3c9b533d30652b3130de1816cab2a25e9a6304011419ff90b604d4b73cbe14',
   'acff39c098791c9949bed23d24d2a8bbb029a61f71971bea24fdf48068fd01bf',
]

digest_security_res = [
   'ae8dd6b1b3b7ebcddccf77e1e1cee42ac3d3d90e4c2cc111c4d2aab17870e8cf',
   '16ba752619484f662586478081c99daeb3126df5988fd7956fbb302de964f958',
   'cbb6f7a008936a0cc32b34b87721eb11af1b141733dfd717627e13fb19e3c27a',
   '5196b2513bbc86a08386720240053b2a29a628aac0e1fdaf372e7f220e984538',
   '99f13e073da1f5e4e6db0d37d9f99285e4439ef57820518067ce56847613239f',
   'a723679b7b81137cb0b560428ea120fc3468ca3f2c3d2bc120a2f9a84b3a5a49'
]