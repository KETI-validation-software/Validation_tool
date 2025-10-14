# response 모드 - 플랫폼 측 메시지 데이터 확인에 뜨는 내용

# Authentication
Authentication_in_data = {
    "userID": "user001",
    "userPW": "pass001"
}

# Capabilities
Capabilities_in_data = {}

# CameraProfiles
CameraProfiles_in_data = {}

# StoredVideoInfos
StoredVideoInfos_in_data = {
    "timePeriod": {
    "startTime": 20220822163022123,
    "endTime": 20220822163025123
},
    "camList": [
        {
        "camID": "cam001"
    },
        {
        "camID": "cam002"
    }
]
}

# StreamURLs
StreamURLs_in_data = {
    "camList": [
        {
        "camID": "cam001",
        "streamProtocolType": "RTSP"
    }
]
}

# ReplayURL
ReplayURL_in_data = {
    "camList": [
        {
        "camID": "cam001",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "streamProtocolType": "RTSP"
    },
        {
        "camID": "cam002",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "streamProtocolType": "RTSP"
    },
        {
        "camID": "cam003",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "streamProtocolType": "RTSP"
    }
]
}

# RealtimeVideoEventInfos - 시스템이 플랫폼에 보내는 웹훅
RealtimeVideoEventInfos_in_data = {
    "camList": [
        {
        "camID": "cam001"
    },
        {
        "camID": "cam002"
    }
],
    "transProtocol": {
    "transProtocolType": "WebHook",
    "transProtocolDesc": "https://127.0.0.1:8090/RealtimeVideoEventInfos"
},
    "duration": 10,
    "eventFilter": "배회",
    "startTime": 20220822163022123
}

# WebHook RealtimeVideoEventInfos - 시스템이 플랫폼에 보내는 메시지 잘 받았다는 응답
WebHook_RealtimeVideoEventInfos_out_data = {
    "code": 200,
    "message": "성공"
}

# StoredVideoEventInfos
StoredVideoEventInfos_in_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "eventDesc": "AAABVVVVCCCDDssvfdd"
    },
        {
        "camID": "cam0002",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "eventDesc": "FFFeeiiiWWkdjflskdjfoEKK"
    },
        {
        "camID": "cam0003",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "eventDesc": "iVUhEUgAAACAAAAAgCAYAAA"
    }
]
}

# StoredObjectAnalyticsInfos
StoredObjectAnalyticsInfos_in_data = {
    "timePeriod": {
    "startTime": 20220822163022123,
    "endTime": 20220822163025123
},
    "camList": [
        {
        "camID": "cam0001"
    },
        {
        "camID": "cam0002"
    },
        {
        "camID": "cam0003"
    }
],
    "anayticsFilter": "객체탐지",
    "classFilter": [
    "차량",
    "사람"
]
}

# spec_002 데이터 리스트
spec_002_inData = [
    Authentication_in_data,
    Capabilities_in_data,
    CameraProfiles_in_data,
    StoredVideoInfos_in_data,
    StreamURLs_in_data,
    ReplayURL_in_data,
    RealtimeVideoEventInfos_in_data,
    StoredVideoEventInfos_in_data,
    StoredObjectAnalyticsInfos_in_data,
]

# spec_002 API endpoint
spec_002_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "StoredVideoInfos",
    "StreamURLs",
    "ReplayURL",
    "RealtimeVideoEventInfos",
    "StoredVideoEventInfos",
    "StoredObjectAnalyticsInfos",
]

# spec_002 WebHook 데이터 리스트
# ✅ API 개수(9개)만큼 확장 (웹훅이 없는 API는 None)
spec_002_webhookData = [
    None,  # Authentication - 웹훅 없음
    None,  # Capabilities - 웹훅 없음
    None,  # CameraProfiles - 웹훅 없음
    None,  # StoredVideoInfos - 웹훅 없음
    None,  # StreamURLs - 웹훅 없음
    None,  # ReplayURL - 웹훅 없음
    WebHook_RealtimeVideoEventInfos_out_data,  # RealtimeVideoEventInfos - 웹훅 있음!
    None,  # StoredVideoEventInfos - 웹훅 없음
    None,  # StoredObjectAnalyticsInfos - 웹훅 없음
]

