# response 모드

# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "v"
}

# Capabilities
cmgvieyak001b6cd04cgaawmm_Capabilities_out_data = {
    "code": "200",
    "message": "성공",
    "streamingSupport": [
        {
        "streamProtocolType": "RTSP",
        "streamProtocolDesc": "Unicast"
    }
],
    "transportSupport": [
        {
        "transProtocolType": "WebHook",
        "transProtocolDesc": ""
    }
]
}

# CameraProfiles
cmgvieyak001b6cd04cgaawmm_CameraProfiles_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "camName": "카메라1",
        "camLoc": {
        "lon": "127.127730",
        "lat": "38.439801",
        "alt": "32.131",
        "desc": "3층복도"
    },
        "camConfig": {
        "camType": "PTZ"
    }
    },
        {
        "camID": "cam0002",
        "camName": "카메라2",
        "camLoc": {
        "lon": "126",
        "lat": "32",
        "alt": "31",
        "desc": "2층복도"
    },
        "camConfig": {
        "camType": "PTZ"
    }
    }
]
}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_out_data = {
    "code": "200",
    "message": "성공",
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
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "",
        "accessID": "conn0001",
        "accessPW": "1234",
        "camURL": "rtsp://127.0.01:8554",
        "videoInfo": {
        "resolution": "1920x1080",
        "fps": "30",
        "videoCodec": "H.264",
        "audioCodec": "G.711"
    }
    }
]
}

# ReplayURL
cmgvieyak001b6cd04cgaawmm_ReplayURL_out_data = {
    "code": "성공",
    "message": "200",
    "camList": [
        {
        "camID": "",
        "accessID": "cam0001",
        "accessPW": "conn0001",
        "startTime": "",
        "endTime": "",
        "camURL": "rtsp://192.168.0.5:8000",
        "videoInfo": {
        "resolution": "1920x1080",
        "fps": "30",
        "videoCodec": "H.264",
        "audioCodec": "G.711"
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
        "camID": ""
    }
],
    "duration": 0,
    "transProtocol": {
    "transProtocolType": "",
    "transProtocolDesc": ""
},
    "eventFilter": "",
    "classFilter": "",
    "startTime": 0
}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "",
        "eventUUID": "event01",
        "eventName": "",
        "startTime": "",
        "endTime": "",
        "eventDesc": "aaabbbAAA"
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

