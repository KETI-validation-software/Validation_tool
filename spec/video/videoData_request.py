# request 모드 - 시스템 측 메시지 데이터 확인에 뜨는 내용

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

# RealtimeVideoEventInfos - 플랫폼이 시스템에 보내는 웹훅 요청 응답 메시지
RealtimeVideoEventInfos_out_data = {
    "code": "200",
    "message": "성공",
}

# WebHook RealtimeVideoEventInfos - 플랫폼이 시스템에 보내는 웹훅 데이터 메시지
WebHook_RealtimeVideoEventInfos_in_data = {
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

# spec_001 데이터 리스트
spec_001_outData = [
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

# spec_001 API endpoint
spec_001_messages = [
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

# spec_001 WebHook 데이터 리스트
# ✅ API 개수(9개)만큼 확장 (웹훅이 없는 API는 None)
spec_001_webhookData = [
    None,  # Authentication - 웹훅 없음
    None,  # Capabilities - 웹훅 없음
    None,  # CameraProfiles - 웹훅 없음
    None,  # StoredVideoInfos - 웹훅 없음
    None,  # StreamURLs - 웹훅 없음
    None,  # ReplayURL - 웹훅 없음
    WebHook_RealtimeVideoEventInfos_in_data,  # RealtimeVideoEventInfos - 웹훅 있음!
    None,  # StoredVideoEventInfos - 웹훅 없음
    None,  # StoredObjectAnalyticsInfos - 웹훅 없음
]

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
    "transportSupport": [
        {
        "transProtocolType": "HTTP_API",
        "transProtocolDesc": "description"
    }
]
}

# SensorDeviceProfiles
SensorDeviceProfiles_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "iot0001",
        "sensorDeviceType": "온도",
        "sensorDeviceName": "온도 센서",
        "sensorDeviceLoc": {
        "lon": "127.127730",
        "lat": "38.439801",
        "alt": "32.131",
        "desc": "3층복도"
    }
    },
        {
        "sensorDeviceID": "iot0002",
        "sensorDeviceType": "온도",
        "sensorDeviceName": "온도 센서",
        "sensorDeviceLoc": {
        "lon": "127.127730",
        "lat": "38.439801",
        "alt": "32.131",
        "desc": "3층복도"
    }
    }
]
}

# RealtimeSensorData
RealtimeSensorData_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "iot0001",
        "measureTime": 20220822163022123,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "90"
    },
        {
        "sensorDeviceID": "iot0002",
        "measureTime": 20220822163022123,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "36"
    },
        {
        "sensorDeviceID": "iot0003",
        "measureTime": 20220822163022123,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "36"
    }
]
}

# RealtimeSensorEventInfos
RealtimeSensorEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "iot0001",
        "eventName": "화재",
        "eventTime": 20220822163022123,
        "eventDesc": "100도"
    },
        {
        "sensorDeviceID": "iot0002",
        "eventName": "화재",
        "eventTime": 20220822163022123,
        "eventDesc": "200도"
    }
]
}

# StoredSensorEventInfos
StoredSensorEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "iot0001",
        "eventName": "화재",
        "eventTime": 20220822163022123,
        "eventDesc": "100도"
    },
        {
        "sensorDeviceID": "iot0002",
        "eventName": "화재",
        "eventTime": 20220822163022123,
        "eventDesc": "100도"
    }
]
}

# SensorDeviceControl
SensorDeviceControl_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceID": "iot0001",
    "sensorDeviceStatus": "Alarm"
}

# spec_0011 데이터 리스트
spec_0011_outData = [
    Authentication_out_data,
    Capabilities_out_data,
    SensorDeviceProfiles_out_data,
    RealtimeSensorData_out_data,
    RealtimeSensorEventInfos_out_data,
    StoredSensorEventInfos_out_data,
    SensorDeviceControl_out_data,
]

# spec_0011 API endpoint
spec_0011_messages = [
    "Authentication",
    "Capabilities",
    "SensorDeviceProfiles",
    "RealtimeSensorData",
    "RealtimeSensorEventInfos",
    "StoredSensorEventInfos",
    "SensorDeviceControl",
]

