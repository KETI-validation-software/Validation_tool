# response 모드

# Authentication
cmg90br3n002qihleffuljnth_Authentication_out_data = {
    "code": "",
    "message": "",
    "userName": "",
    "userAff": "",
    "accessToken": ""
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

# SensorDeviceProfiles
cmg90br3n002qihleffuljnth_SensorDeviceProfiles_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "iot0001",
        "sensorDeviceType": "온도",
        "sensorDeviceName": "홍채 센서",
        "sensorDeviceLoc": {
        "lon": "12.7127730",
        "lat": "38.439801",
        "alt": "32.131",
        "desc": "3층복도"
    }
    }
]
}

# RealtimeSensorData
cmg90br3n002qihleffuljnth_RealtimeSensorData_out_data = {
    "code": "",
    "message": "",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "",
        "measureTime": 0,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "100"
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

# SensorDeviceControl
cmg90br3n002qihleffuljnth_SensorDeviceControl_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceID": "",
    "sensorDeviceStatus": ""
}

# cmg90br3n002qihleffuljnth 데이터 리스트
cmg90br3n002qihleffuljnth_outData = [
    cmg90br3n002qihleffuljnth_Authentication_out_data,
    cmg90br3n002qihleffuljnth_Capabilities_out_data,
    cmg90br3n002qihleffuljnth_SensorDeviceProfiles_out_data,
    cmg90br3n002qihleffuljnth_RealtimeSensorData_out_data,
    cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_out_data,
    cmg90br3n002qihleffuljnth_StoredSensorEventInfos_out_data,
    cmg90br3n002qihleffuljnth_SensorDeviceControl_out_data,
]

# cmg90br3n002qihleffuljnth API endpoint
cmg90br3n002qihleffuljnth_messages = [
    "Authentication",
    "Capabilities",
    "SensorDeviceProfiles",
    "RealtimeSensorData",
    "RealtimeSensorEventInfos",
    "StoredSensorEventInfos",
    "SensorDeviceControl",
]

# Authentication
cmg7edeo50013124xiux3gbkb_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcd1234"
}

# Capabilities
cmg7edeo50013124xiux3gbkb_Capabilities_out_data = {
    "code": "",
    "message": "",
    "transportSupport": [
        {
        "transProtocolType": "LongPolling",
        "transProtocolDesc": ""
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
cmg7edeo50013124xiux3gbkb_outData = [
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
cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_out_data = {
    "code": "",
    "message": ""
}

# RealtimeVideoEventInfos WebHook IN Data
cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_webhook_in_data = {
    "camList": [
        {
        "camID": "",
        "eventUUID": "",
        "eventName": "",
        "startTime": 1760935020000,
        "endTime": 1761280620000,
        "eventDesc": "aaabbbAAA"
    }
]
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

# cmg7bve25000114cevhn5o3vr WebHook 데이터 리스트
cmg7bve25000114cevhn5o3vr_webhook_inData = [
    cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_webhook_in_data,
]

# cmg7bve25000114cevhn5o3vr API endpoint
cmg7bve25000114cevhn5o3vr_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "StoredVideoInfos",
    "StreamURLs",
    "ReplayURL",
    "RealtimeVideoEventInfos",
    "StoredVideoEventInfos",
]

