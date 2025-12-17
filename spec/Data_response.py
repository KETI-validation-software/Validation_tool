# Authentication
cmiqr201z00i8ie8fitdg5t1b_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

# Capabilities
cmii7shen005i8z1tagevx4qh_Capabilities_out_data = {
    "code": "200",
    "message": "성공",
    "transportSupport": [
        {
        "transProtocolType": "LongPolling",
        "transProtocolDesc": ""
    }
]
}

# SensorDeviceProfiles
cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_out_data = {
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
        "alt": "",
        "desc": ""
    }
    }
]
}

# RealtimeSensorData
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_out_data = {
    "code": "200",
    "message": "성공"
}

# RealtimeSensorData WebHook IN Data
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_in_data = {
    "sensorDeviceList": [
        {
        "sensorDeviceID": "",
        "measureTime": 20220822163022124,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "90"
    },
        {
        "sensorDeviceID": "iot0002",
        "measureTime": 20220822163022124,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "36"
    },
        {
        "sensorDeviceID": "iot0003",
        "measureTime": 20220822163022124,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "36"
    }
]
}

# RealtimeSensorEventInfos
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_out_data = {
    "code": "200",
    "message": "성공"
}

# RealtimeSensorEventInfos WebHook IN Data
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_in_data = {
    "sensorDeviceList": [
        {
        "sensorDeviceID": "iot0001",
        "eventName": "",
        "eventTime": 20220822163022124,
        "eventDesc": "100도"
    },
        {
        "sensorDeviceID": "iot0002",
        "eventName": "",
        "eventTime": 20220822163022124,
        "eventDesc": "200도"
    }
]
}

# StoredSensorEventInfos
cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "iot0001",
        "eventName": "화재",
        "eventTime": 20220822163022124,
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

# cmii7shen005i8z1tagevx4qh 데이터 리스트
cmii7shen005i8z1tagevx4qh_outData = [
    cmii7shen005i8z1tagevx4qh_Authentication_out_data,
    cmii7shen005i8z1tagevx4qh_Capabilities_out_data,
    cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_out_data,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_out_data,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_out_data,
    cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_out_data,
]

# cmii7shen005i8z1tagevx4qh WebHook 데이터 리스트
cmii7shen005i8z1tagevx4qh_webhook_inData = [
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_in_data,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_in_data,
]

# cmii7shen005i8z1tagevx4qh API endpoint
cmii7shen005i8z1tagevx4qh_messages = [
    "Authentication",
    "Capabilities",
    "SensorDeviceProfiles",
    "RealtimeSensorData",
    "RealtimeSensorEventInfos",
    "StoredSensorEventInfos",
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
        "transProtocolType": "WebHook",
        "transProtocolDesc": ""
    }
]
}

# DoorProfiles
cmii7pysb004k8z1tts0npxfm_DoorProfiles_out_data = {
    "code": "200",
    "message": "성공",
    "doorList": [
        {
        "doorID": "door0001",
        "doorName": "A건물 출입문",
        "doorRelayStatus": "일반",
        "doorSensor": "0",
        "doorLoc": {
        "lon": "127.127730",
        "lat": "38.439801",
        "alt": "32.131",
        "desc": "3층복도"
    },
        "bioDeviceList": [
            {
            "bioDeviceID": "bio0001",
            "bioDeviceName": "출입문홍채인식기기",
            "bioDeviceAuthTypeList": [
            "홍채",
            "지문"
        ]
        },
            {
            "bioDeviceID": "bio0002",
            "bioDeviceName": "출입문지문인식기기",
            "bioDeviceAuthTypeList": [
            "지문"
        ]
        }
    ],
        "otherDeviceList": [
            {
            "otherDeviceID": "other0001",
            "otherDeviceName": "출입문카드인식기기",
            "otherDeviceAuthTypeList": [
            "카드"
        ]
        }
    ]
    }
]
}

# AccessUserInfos
cmii7pysb004k8z1tts0npxfm_AccessUserInfos_out_data = {
    "code": "200",
    "message": "성공",
    "userList": [
        {
        "userID": "user0001",
        "userName": "홍길동",
        "userDesc": "일반사용자",
        "doorList": [
            {
            "doorID": "door0001",
            "timePeriod": {
            "startTime": 20251105163010124,
            "endTime": 20251115163010124
        }
        }
    ]
    },
        {
        "userID": "user0002",
        "userName": "김철수",
        "userDesc": "관리자",
        "doorList": [
            {
            "doorID": "door0002",
            "timePeriod": {
            "startTime": 20251105163010124,
            "endTime": 20251115163010120
        }
        },
            {
            "doorID": "door0003",
            "timePeriod": {
            "startTime": 20251105163010124,
            "endTime": 20251115163010124
        }
        }
    ]
    }
]
}

# RealtimeVerifEventInfos
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_out_data = {
    "code": "200",
    "message": "성공"
}

# RealtimeVerifEventInfos WebHook IN Data
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_in_data = {
    "doorList": [
        {
        "eventTime": 0,
        "doorID": "door0001",
        "userID": "user0001",
        "bioAuthTypeList": [
        "지문",
        "얼굴"
    ],
        "otherAuthTypeList": [
        "카드"
    ],
        "eventName": "성공",
        "eventDesc": ""
    },
        {
        "eventTime": 20220822163022124,
        "doorID": "door0002",
        "userID": "user0002",
        "bioAuthTypeList": [
        "홍채"
    ],
        "otherAuthTypeList": [
        "카드"
    ],
        "eventName": "성공",
        "eventDesc": "36.5"
    }
]
}

# StoredVerifEventInfos
cmii7pysb004k8z1tts0npxfm_StoredVerifEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "doorList": [
        {
        "eventTime": 20220822163022124,
        "doorID": "door0001",
        "userID": "user0001",
        "bioAuthTypeList": [
        "지문",
        "얼굴"
    ],
        "otherAuthTypeList": [
        "카드"
    ],
        "eventName": "성공",
        "eventDesc": "36.5"
    },
        {
        "eventTime": 20220822163022124,
        "doorID": "door0002",
        "userID": "user0002",
        "bioAuthTypeList": [
        "홍채"
    ],
        "otherAuthTypeList": [
        "카드"
    ],
        "eventName": "",
        "eventDesc": ""
    }
]
}

# cmii7pysb004k8z1tts0npxfm 데이터 리스트
cmii7pysb004k8z1tts0npxfm_outData = [
    cmii7pysb004k8z1tts0npxfm_Authentication_out_data,
    cmii7pysb004k8z1tts0npxfm_Capabilities_out_data,
    cmii7pysb004k8z1tts0npxfm_DoorProfiles_out_data,
    cmii7pysb004k8z1tts0npxfm_AccessUserInfos_out_data,
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_out_data,
    cmii7pysb004k8z1tts0npxfm_StoredVerifEventInfos_out_data,
]

# cmii7pysb004k8z1tts0npxfm WebHook 데이터 리스트
cmii7pysb004k8z1tts0npxfm_webhook_inData = [
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_in_data,
]

# cmii7pysb004k8z1tts0npxfm API endpoint
cmii7pysb004k8z1tts0npxfm_messages = [
    "Authentication",
    "Capabilities",
    "DoorProfiles",
    "AccessUserInfos",
    "RealtimeVerifEventInfos",
    "StoredVerifEventInfos",
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
        "transProtocolType": "LongPolling",
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
    },
        {
        "camID": "cam003",
        "camName": "카메라3",
        "camLoc": {
        "lon": "75",
        "lat": "585",
        "alt": "122",
        "desc": "2층출입문"
    },
        "camConfig": {
        "camType": "PTZ"
    }
    },
        {
        "camID": "cam004",
        "camName": "카메라4",
        "camLoc": {
        "lon": "44",
        "lat": "211",
        "alt": "23",
        "desc": "1층 출입문"
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
        "camID": "",
        "accessID": "",
        "accessPW": "",
        "camURL": "rtsp://192.168.0.1:8000",
        "videoInfo": {
        "resolution": "1920x1080",
        "fps": 30,
        "videoCodec": "H.264",
        "audioCodec": "G.711"
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
        "camID": "",
        "eventUUID": "event01",
        "eventName": "",
        "startTime": 0,
        "endTime": 0,
        "eventDesc": "sfdfEFASDDDLKJFjdkdlfjde"
    }
]
}

# StoredVideoInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_out_data = {
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

# ReplayURL
cmii7lxbn002s8z1t1i9uudf0_ReplayURL_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "",
        "accessID": "conn0001",
        "accessPW": "1234",
        "camURL": "rtsp://192.168.0.1:8000",
        "videoInfo": {
        "resolution": "1920x1080",
        "fps": 30,
        "videoCodec": "H.264",
        "audioCodec": "G.711"
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
        "camID": "",
        "eventUUID": "event01",
        "eventName": "",
        "startTime": 0,
        "endTime": 0,
        "eventDesc": "AAABVVVVCCCDDssvfdd"
    }
]
}

# StoredObjectAnalyticsInfos
cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "",
        "analyticsTime": 0,
        "anlayticsResultList": [
            {
            "anayticsID": "object001",
            "analyticsClass": "",
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

