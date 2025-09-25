#API-info
headers = {"Content-type": "application/json", "User-Agent":'test'}
none_request_message = ['Capabilities',
                        'CameraProfiles',
                        'DoorProfiles',
                        'AccessUserInfos',
                        'SensorDeviceProfiles']

#test-info
company_name = "스마트홈 테크놀로지"
product_name = "물리보안 시스템"
version = "v2.1.0"
test_category = "사전시험"
test_target = "통합시스템"
test_range = "전체필드"
auth_type = "Digest Auth"
auth_info = "user001,pass001"
admin_code = ""
url = "https://127.0.0.1:8000"

specs = [["spec-001_inSchema","spec-001_outData","spec001_messages","영상보안 시스템 검증(요청검증)"],
         ["spec-0011_inSchema","spec-0011_outData","spec0011_messages","보안용 센서 시스템 검증(요청검증"]]
#test-opt
'''
opt2의 메시지의 settings 내 정보 보고 작성, 메시지 순차별로
trans_protocol : 메시지별 실시간 송수신 메시지 여부, None-실시간 아님, LongPolling, WebHook은 설정에 따라 동작 
time_out : 메시지별 timeout 설정 시간
num_retries : 메시지별 메시지 검증 횟수
'''

trans_protocol = [None,None,None,None,None,None,"LongPolling",None,None] #"LongPolling" #WebHook
time_out = [5000,5000,8000,8000,8000,8000,5000,5000,8000]   # time_out = [5000,5000,8000,8000,8000,8000,5000,5000,8000]
num_retries = [1, 1, 3, 3, 3, 2, 1, 1, 2]


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