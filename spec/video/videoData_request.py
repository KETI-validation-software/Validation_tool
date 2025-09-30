# request 모드

# Authentication
Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

# Capabilities
Capabilities_out_data = {
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
        "transProtocolType": "REST_API",
        "transProtocolDesc": "desc"
    }
]
}

# CameraProfiles
CameraProfiles_out_data = {
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
        "lat": "37.33671"
    },
        "camConfig": {
        "camType": "dome"
    }
    }
]
}

# StoredVideoInfos
StoredVideoInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "timeList": [
            {
            "startTime": 20220822163022123,
            "endTime": 20220822163025123
        }
    ]
    },
        {
        "camID": "cam0002",
        "timeList": [
            {
            "startTime": 20220822163022123,
            "endTime": 20220822163025123
        }
    ]
    }
]
}

# StreamURLs
StreamURLs_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam001",
        "accessID": "conn001",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.1:8000"
    },
        {
        "camID": "cam002",
        "accessID": "conn002",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.2:8000"
    },
        {
        "camID": "cam003",
        "accessID": "conn003",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.3:8000"
    }
]
}

# ReplayURL
ReplayURL_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "accessID": "conn0001",
        "accessPW": "1234",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "camURL": "rtsp://192.168.0.1:8000"
    },
        {
        "camID": "cam0002",
        "accessID": "conn0002",
        "accessPW": "1234",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "camURL": "rtsp://192.168.0.2:8000"
    },
        {
        "camID": "cam0003",
        "accessID": "conn0003",
        "accessPW": "1234",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "camURL": "rtsp://192.168.0.3:8000"
    }
]
}

# RealtimeVideoEventInfos
RealtimeVideoEventInfos_out_data = {
    "camList": [
        {
        "camID": "cam0001",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "eventDesc": "sfdfEFASDDDLKJFjdkdlfjde"
    },
        {
        "camID": "cam0002",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "eventDesc": "dddddeeeeeAAFEDFiikjf"
    }
]
}

# StoredVideoEventInfos
StoredVideoEventInfos_out_data = {
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
StoredObjectAnalyticsInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "analyticsTime": 20220822163022123,
        "anlayticsResultList": [
            {
            "anayticsID": "object001",
            "analyticsClass": "차량",
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
            "analyticsConfidence": 0.9,
            "analyticsBoundingBox": {
            "left": 0.3,
            "top": 0.1,
            "right": 0.5,
            "bottom": 0.7
        }
        }
    ]
    }
]
}


# steps 순서대로 출력 메시지 생성
videoOutMessage = [
    Authentication_out_data,
    Capabilities_out_data,
    CameraProfiles_out_data,
    StoredVideoInfos_out_data,
    StreamURLs_out_data,
    ReplayURL_out_data,
    RealtimeVideoEventInfos_out_data,
    StoredVideoEventInfos_out_data,
    StoredObjectAnalyticsInfos_out_data,
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
