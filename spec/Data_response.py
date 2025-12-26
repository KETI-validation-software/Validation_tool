# Authentication
cmiqr201z00i8ie8fitdg5t1b_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시",
    "accessToken": "abcde1234"
}

# Capabilities
cmiqr201z00i8ie8fitdg5t1b_Capabilities_out_data = {
    "code": "",
    "message": "",
    "transportSupport": [
        {
        "transProtocolType": "LongPolling",
        "transProtocolDesc": "none"
    },
        {
        "transProtocolType": "Webhook",
        "transProtocolDesc": "none"
    }
]
}

# SensorDeviceProfiles
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_out_data = {
    "code": "",
    "message": "",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "iot0001",
        "sensorDeviceType": "홍채인식",
        "sensorDeviceName": "홍채 센서",
        "sensorDeviceLoc": {
        "lon": "12",
        "lat": "233",
        "alt": "122",
        "desc": "복도"
    }
    },
        {
        "sensorDeviceID": "iot0002",
        "sensorDeviceType": "온도",
        "sensorDeviceName": "온도센서",
        "sensorDeviceLoc": {
        "lon": "24",
        "lat": "367",
        "alt": "234",
        "desc": "출입구"
    }
    },
        {
        "sensorDeviceID": "iot0003",
        "sensorDeviceType": "지문",
        "sensorDeviceName": "지문센서",
        "sensorDeviceLoc": {
        "lon": "486",
        "lat": "54",
        "alt": "6",
        "desc": "후문"
    }
    },
        {
        "sensorDeviceID": "iot0004",
        "sensorDeviceType": "온도",
        "sensorDeviceName": "온도센서",
        "sensorDeviceLoc": {
        "lon": "123",
        "lat": "42",
        "alt": "55",
        "desc": "복도"
    }
    }
]
}

# SensorDeviceControl
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceID": "",
    "sensorDeviceStatus": ""
}

# SensorDeviceControl2
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceID": "",
    "sensorDeviceStatus": ""
}

# cmiqr201z00i8ie8fitdg5t1b 데이터 리스트
cmiqr201z00i8ie8fitdg5t1b_outData = [
    cmiqr201z00i8ie8fitdg5t1b_Authentication_out_data,
    cmiqr201z00i8ie8fitdg5t1b_Capabilities_out_data,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_out_data,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_out_data,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_out_data,
]

# cmiqr201z00i8ie8fitdg5t1b API endpoint
cmiqr201z00i8ie8fitdg5t1b_messages = [
    "Authentication",
    "Capabilities",
    "SensorDeviceProfiles",
    "SensorDeviceControl",
    "SensorDeviceControl2",
]

# Authentication
cmiqr1acx00i5ie8fi022t1hp_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": ""
}

# Capabilities
cmiqr1acx00i5ie8fi022t1hp_Capabilities_out_data = {
    "code": "200",
    "message": "성공",
    "transportSupport": [
        {
        "transProtocolType": "LongPolling",
        "transProtocolDesc": ""
    },
        {
        "transProtocolType": "Webhook",
        "transProtocolDesc": ""
    }
]
}

# DoorProfiles
cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_out_data = {
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
            "otherDeviceName": "출입문홍채인식기기",
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
    },
        {
        "doorID": "door0002",
        "doorName": "B건물 출입문",
        "doorRelayStatus": "수동 개방",
        "doorSensor": "0",
        "doorLoc": {
        "lon": "233",
        "lat": "123",
        "alt": "23",
        "desc": "333"
    },
        "bioDeviceList": [
            {
            "bioDeviceID": "bio0002",
            "bioDeviceName": "정맥인식기기",
            "bioDeviceAuthTypeList": [
            "정맥"
        ]
        }
    ],
        "otherDeviceList": [
            {
            "otherDeviceID": "other0002",
            "otherDeviceName": "카드인식기기",
            "otherDeviceAuthTypeList": [
            "카드"
        ]
        }
    ]
    }
]
}

# RealtimeDoorStatus
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorID": "",
        "doorName": "",
        "doorRelaySensor": "",
        "doorSensor": ""
    }
]
}

# DoorControl
cmiqr1acx00i5ie8fi022t1hp_DoorControl_out_data = {
    "code": "200",
    "message": "성공"
}

# RealtimeDoorStatus2
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorID": "",
        "doorName": "",
        "doorRelaySensor": "",
        "doorSensor": ""
    }
]
}

# cmiqr1acx00i5ie8fi022t1hp 데이터 리스트
cmiqr1acx00i5ie8fi022t1hp_outData = [
    cmiqr1acx00i5ie8fi022t1hp_Authentication_out_data,
    cmiqr1acx00i5ie8fi022t1hp_Capabilities_out_data,
    cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_out_data,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_data,
    cmiqr1acx00i5ie8fi022t1hp_DoorControl_out_data,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_out_data,
]

# cmiqr1acx00i5ie8fi022t1hp API endpoint
cmiqr1acx00i5ie8fi022t1hp_messages = [
    "Authentication",
    "Capabilities",
    "DoorProfiles",
    "RealtimeDoorStatus",
    "DoorControl",
    "RealtimeDoorStatus2",
]

# Authentication
cmiqqzrjz00i3ie8figf79cur_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": ""
}

# Capabilities
cmiqqzrjz00i3ie8figf79cur_Capabilities_out_data = {
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
        "transProtocolType": "LongPolling",
        "transProtocolDesc": ""
    }
]
}

# CameraProfiles
cmiqqzrjz00i3ie8figf79cur_CameraProfiles_out_data = {
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
        "lon": "127.127730",
        "lat": "37.33671",
        "alt": "",
        "desc": ""
    },
        "camConfig": {
        "camType": "dome"
    }
    }
]
}

# PtzStatus
cmiqqzrjz00i3ie8figf79cur_PtzStatus_out_data = {
    "code": "200",
    "message": "성공",
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
cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_out_data = {
    "code": "200",
    "message": "성공"
}

# PtzStop
cmiqqzrjz00i3ie8figf79cur_PtzStop_out_data = {
    "code": "200",
    "message": "성공"
}

# cmiqqzrjz00i3ie8figf79cur 데이터 리스트
cmiqqzrjz00i3ie8figf79cur_outData = [
    cmiqqzrjz00i3ie8figf79cur_Authentication_out_data,
    cmiqqzrjz00i3ie8figf79cur_Capabilities_out_data,
    cmiqqzrjz00i3ie8figf79cur_CameraProfiles_out_data,
    cmiqqzrjz00i3ie8figf79cur_PtzStatus_out_data,
    cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_out_data,
    cmiqqzrjz00i3ie8figf79cur_PtzStop_out_data,
]

# cmiqqzrjz00i3ie8figf79cur API endpoint
cmiqqzrjz00i3ie8figf79cur_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "PtzStatus",
    "PtzContinuousMove",
    "PtzStop",
]

