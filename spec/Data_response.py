# Authentication
cmii7shen005i8z1tagevx4qh_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

# cmii7shen005i8z1tagevx4qh 데이터 리스트
cmii7shen005i8z1tagevx4qh_outData = [
    cmii7shen005i8z1tagevx4qh_Authentication_out_data,
]

# cmii7shen005i8z1tagevx4qh API endpoint
cmii7shen005i8z1tagevx4qh_messages = [
    "Authentication",
]

# Authentication
cmii7pysb004k8z1tts0npxfm_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

# Capabilities
cmii7pysb004k8z1tts0npxfm_Capabilities_out_data = {
    "code": "200",
    "message": "성공",
    "transportSupport": [
        {
        "transProtocolType": "LongPolling",
        "transProtocolDesc": ""
    }
]
}

# cmii7pysb004k8z1tts0npxfm 데이터 리스트
cmii7pysb004k8z1tts0npxfm_outData = [
    cmii7pysb004k8z1tts0npxfm_Authentication_out_data,
    cmii7pysb004k8z1tts0npxfm_Capabilities_out_data,
]

# cmii7pysb004k8z1tts0npxfm API endpoint
cmii7pysb004k8z1tts0npxfm_messages = [
    "Authentication",
    "Capabilities",
]

# Authentication
cmii7lxbn002s8z1t1i9uudf0_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

# Capabilities
cmii7lxbn002s8z1t1i9uudf0_Capabilities_out_data = {
    "code": "200",
    "message": "성공",
    "streamingSupport": [
        {
        "streamProtocolType": "Unicast"
    }
],
    "transportSupport": [
        {
        "transportProtocolType": "LongPolling",
        "transProtocolDesc": ""
    }
]
}

# CameraProfiles
cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_out_data = {
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
        "lon": "127.2887",
        "lat": "37.33671",
        "alt": ""
    },
        "camConfig": {
        "camType": "dome"
    }
    }
]
}

# StreamURLs
cmii7lxbn002s8z1t1i9uudf0_StreamURLs_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "accessID": "conn0001",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.1:8000",
        "videoInfo": {
        "resolution": "1920x1080",
        "fps": 30,
        "videoCodec": "H.264",
        "audioCodec": "G.711"
    }
    },
        {
        "camID": "cam0002",
        "accessID": "conn0002",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.2:8000",
        "videoInfo": {
        "resolution": "1920x1080",
        "fps": 30,
        "videoCodec": "H.264",
        "audioCodec": "G.711"
    }
    },
        {
        "camID": "cam0003",
        "accessID": "conn0003",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.3:8000",
        "videoInfo": {
        "resolution": "",
        "fps": 0,
        "videoCodec": "",
        "audioCodec": ""
    }
    }
]
}

# RealtimeVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_out_data = {
    "code": "200",
    "message": "성공"
}

# RealtimeVideoEventInfos WebHook IN Data
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_in_data = {
    "camList": [
        {
        "camID": "cam0001",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20251105163010124,
        "endTime": 20251115163010124,
        "eventDesc": "sfdfEFASDDDLKJFjdkdlfjde"
    },
        {
        "camID": "cam0002",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20251105163010124,
        "endTime": 20251115163010124,
        "eventDesc": "dddddeeeeeAAFEDFiikjf"
    }
]
}

# StoredVideoInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "timeList": [
            {
            "startTime": 20251105163010124,
            "endTime": 20251115163010124
        }
    ]
    },
        {
        "camID": "cam0002",
        "timeList": [
            {
            "startTime": 20251105163010124,
            "endTime": 20251115163010124
        }
    ]
    }
]
}

# ReplayURL
cmii7lxbn002s8z1t1i9uudf0_ReplayURL_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "accessID": "conn0001",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.1:8000",
        "videoInfo": {
        "resolution": "1920x1080",
        "fps": 30,
        "videoCodec": "H.264",
        "audioCodec": "G.711"
    }
    },
        {
        "camID": "cam0002",
        "accessID": "conn0002",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.2:8000",
        "videoInfo": {
        "resolution": "1920x1080",
        "fps": 30,
        "videoCodec": "H.264",
        "audioCodec": "G.711"
    }
    },
        {
        "camID": "cam0003",
        "accessID": "conn0003",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.3:8000",
        "videoInfo": {
        "resolution": "",
        "fps": 0,
        "videoCodec": "",
        "audioCodec": ""
    }
    }
]
}

# StoredVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20251105163010124,
        "endTime": 20251115163010124,
        "eventDesc": "AAABVVVVCCCDDssvfdd"
    },
        {
        "camID": "cam0002",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20251105163010123,
        "endTime": 20251115163010124,
        "eventDesc": "FFFeeiiiWWkdjflskdjfoEKK"
    },
        {
        "camID": "cam0003",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20251105163010123,
        "endTime": 20251115163010124,
        "eventDesc": "iVUhEUgAAACAAAAAgCAYAAA"
    }
]
}

# StoredObjectAnalyticsInfos
cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "analyticsTime": 20220822163022124,
        "anlayticsResultList": [
            {
            "anayticsID": "object001",
            "analyticsClass": "트럭",
            "analyticsAttribute": [
            "빨간색"
        ],
            "analyticsConfidence": 0.8,
            "analyticsBoundingBox": {
            "left": 0.2,
            "top": 0.1,
            "right": 0.5,
            "bottom": 0.6
        },
            "analyticsDesc": "13가 4567"
        }
    ]
    },
        {
        "camID": "cam0002",
        "analyticsTime": 20220822163022123,
        "anlayticsResultList": [
            {
            "anayticsID": "object002",
            "analyticsClass": "사람",
            "analyticsAttribute": [
            "여자",
            "안경"
        ],
            "analyticsConfidence": 0.9,
            "analyticsBoundingBox": {
            "left": 0.3,
            "top": 0.1,
            "right": 0.5,
            "bottom": 0.7
        },
            "analyticsDesc": ""
        }
    ]
    }
]
}

# cmii7lxbn002s8z1t1i9uudf0 데이터 리스트
cmii7lxbn002s8z1t1i9uudf0_outData = [
    cmii7lxbn002s8z1t1i9uudf0_Authentication_out_data,
    cmii7lxbn002s8z1t1i9uudf0_Capabilities_out_data,
    cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_out_data,
    cmii7lxbn002s8z1t1i9uudf0_StreamURLs_out_data,
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_out_data,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_out_data,
    cmii7lxbn002s8z1t1i9uudf0_ReplayURL_out_data,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_out_data,
    cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_out_data,
]

# cmii7lxbn002s8z1t1i9uudf0 WebHook 데이터 리스트
cmii7lxbn002s8z1t1i9uudf0_webhook_inData = [
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_in_data,
]

# cmii7lxbn002s8z1t1i9uudf0 API endpoint
cmii7lxbn002s8z1t1i9uudf0_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "StreamURLs",
    "RealtimeVideoEventInfos",
    "StoredVideoInfos",
    "ReplayURL",
    "StoredVideoEventInfos",
    "StoredObjectAnalyticsInfos",
]

