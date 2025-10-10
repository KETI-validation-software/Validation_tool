# response 모드

# Authentication
Authentication_out_data = {
    "code": "",
    "message": "",
    "userName": "",
    "userAff": "",
    "accessToken": ""
}

# Capabilities
Capabilities_out_data = {
    "code": "",
    "message": "",
    "transportSupport": [
        {
        "transProtocolType": "",
        "transProtocolDesc": ""
    }
]
}

# DoorProfiles
DoorProfiles_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorID": "door0001",
        "doorName": "",
        "doorRelayStatus": "",
        "doorSensor": "",
        "doorLoc": {
        "lon": "127.127730",
        "lat": "38.439801",
        "alt": "32.131",
        "desc": "3층복도"
    },
        "bioDeviceList": [
            {
            "bioDeviceID": "",
            "bioDeviceName": "",
            "bioDeviceAuthTypeList": [],
            "otherDeviceList": [
                {
                "otherDeviceID": "other0001",
                "otherDeviceName": "출입문카드 인식기기",
                "otherDeviceAuthTypeList": []
            }
        ]
        }
    ]
    }
]
}

# StoredVideoInfos
StoredVideoInfos_out_data = {
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

# RealtimeSensorEventInfos
RealtimeSensorEventInfos_out_data = {
    "code": "",
    "message": "",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "",
        "eventName": "",
        "eventTime": "",
        "eventDesc": "100도"
    }
]
}

# StoredSensorEventInfos
StoredSensorEventInfos_out_data = {
    "code": "",
    "message": "",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "",
        "eventName": "",
        "eventTime": "",
        "eventDesc": "100도"
    }
]
}

# RealtimeDoorStatus
RealtimeDoorStatus_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorName": "A 건물 출입문",
        "doorRelaySensor": "일반",
        "doorSensor": "0"
    }
]
}

# cmg90br3n002qihleffuljnth 데이터 리스트
cmg90br3n002qihleffuljnth_inData = [
    Authentication_out_data,
    Capabilities_out_data,
    DoorProfiles_out_data,
    StoredVideoInfos_out_data,
    RealtimeSensorEventInfos_out_data,
    StoredSensorEventInfos_out_data,
    RealtimeDoorStatus_out_data,
]

# cmg90br3n002qihleffuljnth API endpoint
cmg90br3n002qihleffuljnth_messages = [
    "Authentication",
    "Capabilities",
    "DoorProfiles",
    "StoredVideoInfos",
    "RealtimeSensorEventInfos",
    "StoredSensorEventInfos",
    "RealtimeDoorStatus",
]

# Authentication
Authentication_out_data = {
    "code": "",
    "message": "",
    "userName": "",
    "userAff": "",
    "accessToken": ""
}

# Capabilities
Capabilities_out_data = {
    "code": "",
    "message": "",
    "transportSupport": [
        {
        "transProtocolType": "LongPolling"
    }
]
}

# DoorProfiles
DoorProfiles_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorID": "door0001",
        "doorName": "",
        "doorRelayStatus": "",
        "doorSensor": "",
        "doorLoc": {
        "lon": "127.127730",
        "lat": "38.439801",
        "alt": "32.131",
        "desc": "3층복도"
    },
        "bioDeviceList": [
            {
            "bioDeviceID": "",
            "bioDeviceName": "",
            "bioDeviceAuthTypeList": [],
            "otherDeviceList": [
                {
                "otherDeviceID": "other0001",
                "otherDeviceName": "출입문카드 인식기기",
                "otherDeviceAuthTypeList": []
            }
        ]
        }
    ]
    }
]
}

# AccessUserInfos
AccessUserInfos_out_data = {
    "code": "200",
    "message": "성공",
    "userList": [
        {
        "userID": "user001",
        "userName": "홍길동",
        "userDesc": "일반사용자",
        "doorList": [
            {
            "doorID": "door0001",
            "timePeriod": {
            "startTime": 1759371960000,
            "endTime": 1759371960000
        }
        }
    ]
    }
]
}

# RealtimeVerifEventInfos
RealtimeVerifEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "doorList": [
        {
        "eventTime": 0,
        "doorID": "door001",
        "userID": "user001",
        "bioAuthTypeList": [],
        "otherAuthTypeList": [],
        "eventName": "성공",
        "eventDesc": "36.5"
    }
]
}

# StoredVerifEventInfos
StoredVerifEventInfos_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "eventTime": "",
        "doorID": "",
        "userID": "",
        "bioAuthTypeList": [],
        "otherAuthTypeList": [],
        "eventName": "",
        "eventDesc": "3.65"
    }
]
}

# RealtimeDoorStatus
RealtimeDoorStatus_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorName": "A 건물 출입문",
        "doorRelaySensor": "일반",
        "doorSensor": "0"
    }
]
}

# DoorControl
DoorControl_out_data = {
    "code": "200",
    "message": "성공"
}

# cmg7edeo50013124xiux3gbkb 데이터 리스트
cmg7edeo50013124xiux3gbkb_inData = [
    Authentication_out_data,
    Capabilities_out_data,
    DoorProfiles_out_data,
    AccessUserInfos_out_data,
    RealtimeVerifEventInfos_out_data,
    StoredVerifEventInfos_out_data,
    RealtimeDoorStatus_out_data,
    DoorControl_out_data,
]

# cmg7edeo50013124xiux3gbkb API endpoint
cmg7edeo50013124xiux3gbkb_messages = [
    "Authentication",
    "Capabilities",
    "DoorProfiles",
    "AccessUserInfos",
    "RealtimeVerifEventInfos",
    "StoredVerifEventInfos",
    "RealtimeDoorStatus",
    "DoorControl",
]

# Authentication
Authentication_out_data = {
    "code": "",
    "message": "",
    "userName": "",
    "userAff": "",
    "accessToken": ""
}

# Capabilities
Capabilities_out_data = {
    "code": "",
    "message": "",
    "transportSupport": [
        {
        "transProtocolType": "LongPolling"
    }
]
}

# DoorProfiles
DoorProfiles_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorID": "door0001",
        "doorName": "",
        "doorRelayStatus": "",
        "doorSensor": "",
        "doorLoc": {
        "lon": "127.127730",
        "lat": "38.439801",
        "alt": "32.131",
        "desc": "3층복도"
    },
        "bioDeviceList": [
            {
            "bioDeviceID": "",
            "bioDeviceName": "",
            "bioDeviceAuthTypeList": [],
            "otherDeviceList": [
                {
                "otherDeviceID": "other0001",
                "otherDeviceName": "출입문카드 인식기기",
                "otherDeviceAuthTypeList": []
            }
        ]
        }
    ]
    }
]
}

# StoredVideoInfos
StoredVideoInfos_out_data = {
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

# RealtimeVerifEventInfos
RealtimeVerifEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "doorList": [
        {
        "eventTime": 0,
        "doorID": "door001",
        "userID": "user001",
        "bioAuthTypeList": [],
        "otherAuthTypeList": [],
        "eventName": "성공",
        "eventDesc": "36.5"
    }
]
}

# StoredVerifEventInfos
StoredVerifEventInfos_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "eventTime": "",
        "doorID": "",
        "userID": "",
        "bioAuthTypeList": [],
        "otherAuthTypeList": [],
        "eventName": "",
        "eventDesc": "3.65"
    }
]
}

# RealtimeDoorStatus
RealtimeDoorStatus_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorName": "A 건물 출입문",
        "doorRelaySensor": "일반",
        "doorSensor": "0"
    }
]
}

# DoorControl
DoorControl_out_data = {
    "code": "200",
    "message": "성공"
}

# StoredObjectAnalyticsInfos
StoredObjectAnalyticsInfos_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "analyticsTime": "",
        "anlayticsResultList": [
            {
            "anayticsID": "object001",
            "analyticsClass": "",
            "analyticsAttribute": [],
            "analyticsConfidence": 0.8
        }
    ],
        "analyticsBoundingBox": {
        "left": 0.2,
        "top": 0.1,
        "right": 0.3,
        "bottom": 0.4
    },
        "analyticsDesc": "aaabbb"
    }
]
}

# PtzStatus
PtzStatus_out_data = {
    "code": "",
    "message": "",
    "position": {
    "pan": 10,
    "tilt": 20,
    "zoom": 30
},
    "moveStatus": {
    "pan": "정지",
    "tilt": "이동중",
    "zoom": "정지"
}
}

# PtzContinuousMove
PtzContinuousMove_out_data = {
    "code": "200",
    "message": "성공"
}

# PtzStop
PtzStop_out_data = {
    "code": "200",
    "message": "성공"
}

# cmg7bve25000114cevhn5o3vr 데이터 리스트
cmg7bve25000114cevhn5o3vr_inData = [
    Authentication_out_data,
    Capabilities_out_data,
    DoorProfiles_out_data,
    StoredVideoInfos_out_data,
    RealtimeVerifEventInfos_out_data,
    StoredVerifEventInfos_out_data,
    RealtimeDoorStatus_out_data,
    DoorControl_out_data,
    StoredObjectAnalyticsInfos_out_data,
    PtzStatus_out_data,
    PtzContinuousMove_out_data,
    PtzStop_out_data,
]

# cmg7bve25000114cevhn5o3vr API endpoint
cmg7bve25000114cevhn5o3vr_messages = [
    "Authentication",
    "Capabilities",
    "DoorProfiles",
    "StoredVideoInfos",
    "RealtimeVerifEventInfos",
    "StoredVerifEventInfos",
    "RealtimeDoorStatus",
    "DoorControl",
    "StoredObjectAnalyticsInfos",
    "PtzStatus",
    "PtzContinuousMove",
    "PtzStop",
]

