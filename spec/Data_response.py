# response 모드

# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "a"
}

# Capabilities
cmgvieyak001b6cd04cgaawmm_Capabilities_out_data = {
    "code": "",
    "message": "",
    "streamingSupport": [
        {
        "streamProtocolType": "",
        "streamProtocolDesc": ""
    }
],
    "transportSupport": [
        {
        "transProtocolType": "",
        "transProtocolDesc": ""
    }
]
}

# CameraProfiles
cmgvieyak001b6cd04cgaawmm_CameraProfiles_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "camName": "",
        "camLoc": {
        "lon": "",
        "lat": "",
        "alt": "",
        "desc": ""
    },
        "camConfig": {
        "camType": ""
    }
    },
        {
        "camID": "",
        "camName": "",
        "camLoc": {
        "lon": "",
        "lat": "",
        "alt": "",
        "desc": ""
    },
        "camConfig": {
        "camType": ""
    }
    }
]
}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "timeList": [
            {
            "startTime": 0,
            "endTime": 0
        }
    ]
    }
]
}

# StreamURLs
cmgvieyak001b6cd04cgaawmm_StreamURLs_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "accessID": "",
        "accessPW": "",
        "camURL": "",
        "videoInfo": {
        "resolution": "",
        "fps": "",
        "videoCodec": "",
        "audioCodec": ""
    }
    }
]
}

# ReplayURL
cmgvieyak001b6cd04cgaawmm_ReplayURL_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "accessID": "",
        "accessPW": "",
        "startTime": "",
        "endTime": "",
        "camURL": "",
        "videoInfo": {
        "resolution": "",
        "fps": "",
        "videoCodec": "",
        "audioCodec": ""
    }
    }
]
}

# RealtimeVideoEventInfos
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_out_data = {
    "code": "",
    "message": ""
}

# RealtimeVideoEventInfos WebHook IN Data
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_webhook_in_data = {
    "camList": [
        {
        "camID": "",
        "eventUUID": "",
        "eventName": "",
        "startTime": "",
        "endTime": "",
        "eventDesc": ""
    }
]
}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "eventUUID": "",
        "eventName": "",
        "startTime": "",
        "endTime": "",
        "eventDesc": ""
    }
]
}

# cmgvieyak001b6cd04cgaawmm 데이터 리스트
cmgvieyak001b6cd04cgaawmm_outData = [
    cmgvieyak001b6cd04cgaawmm_Authentication_out_data,
    cmgvieyak001b6cd04cgaawmm_Capabilities_out_data,
    cmgvieyak001b6cd04cgaawmm_CameraProfiles_out_data,
    cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_out_data,
    cmgvieyak001b6cd04cgaawmm_StreamURLs_out_data,
    cmgvieyak001b6cd04cgaawmm_ReplayURL_out_data,
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_out_data,
    cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_out_data,
]

# cmgvieyak001b6cd04cgaawmm WebHook 데이터 리스트
cmgvieyak001b6cd04cgaawmm_webhook_inData = [
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_webhook_in_data,
]

# cmgvieyak001b6cd04cgaawmm API endpoint
cmgvieyak001b6cd04cgaawmm_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "StoredVideoInfos",
    "StreamURLs",
    "ReplayURL",
    "RealtimeVideoEventInfos",
    "StoredVideoEventInfos",
]

