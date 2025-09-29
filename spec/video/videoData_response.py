# response 모드

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

# RealtimeVideoEventInfos
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
    "transProtocolType": "LongPolling"
},
    "duration": 10,
    "eventFilter": "배회",
    "startTime": 20220822163022123
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

# WebHook RealtimeVideoEventInfos
WebHook_RealtimeVideoEventInfos_out_data = {
    "code": 200,
    "message": "성공"
}

# steps 순서대로 입력 메시지 생성
videoInMessage = [
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

# API endpoint
videoMessages = [
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

# WebHook
videoWebhookData = [
    WebHook_RealtimeVideoEventInfos_out_data,
]
