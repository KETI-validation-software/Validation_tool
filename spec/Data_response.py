# response 모드

# Authentication
cmg90br3n002qihleffuljnth_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

# Capabilities
cmg90br3n002qihleffuljnth_Capabilities_out_data = {
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
cmg90br3n002qihleffuljnth_DoorProfiles_out_data = {
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
cmg90br3n002qihleffuljnth_StoredVideoInfos_out_data = {
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
cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_out_data = {
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
cmg90br3n002qihleffuljnth_StoredSensorEventInfos_out_data = {
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
cmg90br3n002qihleffuljnth_RealtimeDoorStatus_out_data = {
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
    cmg90br3n002qihleffuljnth_Authentication_out_data,
    cmg90br3n002qihleffuljnth_Capabilities_out_data,
    cmg90br3n002qihleffuljnth_DoorProfiles_out_data,
    cmg90br3n002qihleffuljnth_StoredVideoInfos_out_data,
    cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_out_data,
    cmg90br3n002qihleffuljnth_StoredSensorEventInfos_out_data,
    cmg90br3n002qihleffuljnth_RealtimeDoorStatus_out_data,
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
cmg7edeo50013124xiux3gbkb_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

# Capabilities
cmg7edeo50013124xiux3gbkb_Capabilities_out_data = {
    "code": "",
    "message": "",
    "transportSupport": [
        {
        "transProtocolType": "LongPolling"
    }
]
}

# DoorProfiles
cmg7edeo50013124xiux3gbkb_DoorProfiles_out_data = {
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
cmg7edeo50013124xiux3gbkb_AccessUserInfos_out_data = {
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
cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_out_data = {
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
cmg7edeo50013124xiux3gbkb_StoredVerifEventInfos_out_data = {
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
cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_out_data = {
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
cmg7edeo50013124xiux3gbkb_DoorControl_out_data = {
    "code": "200",
    "message": "성공"
}

# cmg7edeo50013124xiux3gbkb 데이터 리스트
cmg7edeo50013124xiux3gbkb_inData = [
    cmg7edeo50013124xiux3gbkb_Authentication_out_data,
    cmg7edeo50013124xiux3gbkb_Capabilities_out_data,
    cmg7edeo50013124xiux3gbkb_DoorProfiles_out_data,
    cmg7edeo50013124xiux3gbkb_AccessUserInfos_out_data,
    cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_out_data,
    cmg7edeo50013124xiux3gbkb_StoredVerifEventInfos_out_data,
    cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_out_data,
    cmg7edeo50013124xiux3gbkb_DoorControl_out_data,
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
cmg7bve25000114cevhn5o3vr_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

# Capabilities
cmg7bve25000114cevhn5o3vr_Capabilities_out_data = {
    "code": "",
    "message": "",
    "transportSupport": [
        {
        "transProtocolType": "LongPolling"
    }
]
}

# DoorProfiles
cmg7bve25000114cevhn5o3vr_DoorProfiles_out_data = {
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
cmg7bve25000114cevhn5o3vr_StoredVideoInfos_out_data = {
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
cmg7bve25000114cevhn5o3vr_RealtimeVerifEventInfos_out_data = {
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
cmg7bve25000114cevhn5o3vr_StoredVerifEventInfos_out_data = {
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
cmg7bve25000114cevhn5o3vr_RealtimeDoorStatus_out_data = {
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
cmg7bve25000114cevhn5o3vr_DoorControl_out_data = {
    "code": "200",
    "message": "성공"
}

# StoredObjectAnalyticsInfos
cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_out_data = {
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
cmg7bve25000114cevhn5o3vr_PtzStatus_out_data = {
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
cmg7bve25000114cevhn5o3vr_PtzContinuousMove_out_data = {
    "code": "200",
    "message": "성공"
}

# PtzStop
cmg7bve25000114cevhn5o3vr_PtzStop_out_data = {
    "code": "200",
    "message": "성공"
}

# cmg7bve25000114cevhn5o3vr 데이터 리스트
cmg7bve25000114cevhn5o3vr_inData = [
    cmg7bve25000114cevhn5o3vr_Authentication_out_data,
    cmg7bve25000114cevhn5o3vr_Capabilities_out_data,
    cmg7bve25000114cevhn5o3vr_DoorProfiles_out_data,
    cmg7bve25000114cevhn5o3vr_StoredVideoInfos_out_data,
    cmg7bve25000114cevhn5o3vr_RealtimeVerifEventInfos_out_data,
    cmg7bve25000114cevhn5o3vr_StoredVerifEventInfos_out_data,
    cmg7bve25000114cevhn5o3vr_RealtimeDoorStatus_out_data,
    cmg7bve25000114cevhn5o3vr_DoorControl_out_data,
    cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_out_data,
    cmg7bve25000114cevhn5o3vr_PtzStatus_out_data,
    cmg7bve25000114cevhn5o3vr_PtzContinuousMove_out_data,
    cmg7bve25000114cevhn5o3vr_PtzStop_out_data,
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

