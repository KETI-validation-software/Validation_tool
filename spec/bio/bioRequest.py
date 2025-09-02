
# Authentication
# Input
Authentication_in_data = {
}

# Output
Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

# Capabilities
Capabilities_in_data = {}
Capabilities_out_data = {
    "code": "200",
    "message": "성공",
    "transportSupport":
        [{
            "transProtocolType": "REST_API",
            "transProtocolDesc": "description"
        }]
}

# DoorProfiles
DoorProfiles_in_data = {}
DoorProfiles_out_data = {
    "code": "200",
    "message": "성공",
    "doorList":
        [{
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
            "bioDeviceList": [{
                "bioDeviceID": "bio0001",
                "bioDeviceName": "출입문홍채인식기기",
                "bioDeviceAuthType": "홍채"
            },
                {
                    "bioDeviceID": "bio0002",
                    "bioDeviceName": "출입문지문인식기기",
                    "bioDeviceAuthType": "지문"
                }],
            "otherDeviceList": [{
                "otherDeviceID": "other0001",
                "otherDeviceName": "출입문카드인식기기",
                "otherDeviceAuthType": "카드"
            }]
        }
        ]
}

# AccessUserInfos
AccessUserInfos_in_data = {
}
AccessUserInfos_out_data = {
    "code": "200",
    "message": "성공",
    "userList":
        [
            {
                "userID": "user0001",
                "userName": "홍길동",
                "userDesc": "일반사용자",
                "doorList": [{
                    "doorID": "door0001",
                    "timePeriod": {
                        "startTime": 20220822163022123,
                        "endTime": 20220822163025123
                    }
                }
                ]
            },
            {"userName": "김철수",
             "userDesc": "관리자",
             "doorList": [{
                 "doorID": "door0002",
                 "timePeriod": {
                     "startTime": 20220822163022213,
                     "endTime": 20220822163025123
                 }
             },
                 {
                     "doorID": "door0003",
                     "timePeriod": {
                         "startTime": 20220822162300123,
                         "endTime": 20220822162350123
                     }
                 }
             ]
             }
        ]
}
# RealtimeVerifEventInfos
RealtimeVerifEventInfos_in_data = {
    "doorList":
        [{
            "doorID": "door0001"
        },
            {
            "doorID": "door0002"
        },
            {
            "doorID": "door0003"
        }
        ],
    "duration": 500,
    "transProtocol": {
        "transProtocolType": "REST_API",
        "transProtocolDesc": "description"},
    "startTime": 20220822163022123,
    "eventFilter": "성공"
}

RealtimeVerifEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "doorList":
        [{
            "eventTime": 20220822163022123,
            "doorID": "door0001",
            "userID": "user0001",
            "bioAuthTypeList": ["지문", "얼굴"],
            "otherAuthTypeList": ["카드"],
            "eventName": "성공"},
            {
                "eventTime": 20220822163022123,
                "doorID": "door0002",
                "userID": "user0002",
                "bioAuthTypeList": ["홍채"],
                "otherAuthTypeList": ["카드"],
                "eventName": "성공"
            }]
}
# StoredVerifEventInfos
StoredVerifEventInfos_in_data = {
    "timePeriod":
        {
            "startTime":
                20220822163022123,
            "endTime":
                20220822263022123
        },
    "doorList":  [{
        "doorID": "door0001"
    }, {
        "doorID": "door0002"
    }],
    "maxCount": 10,
    "eventFilter": "성공"
}

StoredVerifEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "doorList":
        [
            {
                "eventTime": 20220822163022123,
                "doorID": "door0001",
                "userID": "user0001",
                "bioAuthTypeList": ["지문", "얼굴"],
                "otherAuthTypeList": ["카드"],
                "eventName": "성공"
            },
            {
                "eventTime": 20220822253022123,
                "doorID": "door0002",
                "userID": "user0002",
                "bioAuthTypeList": ["홍채"],
                "otherAuthTypeList": ["카드"],
                "eventName": "성공"
            }
        ]
}

# RealtimeDoorStatus
RealtimeDoorStatus_in_data = {
    "doorList":
        [{
            "doorID": "door0001"
        },
            {
                "doorID": "door0002"
            }
        ],
    "duration": 200,
    "transProtocol":
        {
            "transProtocolType": "REST_API",
            "transProtocolDesc": "test"
        },
    "startTime": 20220822163022123
}

RealtimeDoorStatus_out_data = {
    "code": "200",
    "message": "성공",
    "doorList": [
        {
            "doorID": "door0001",
            "doorName": "A건물 출입문",
            "doorRelaySensor": "일반",
            "doorSensor": "0"
        },
        {
            "doorID": "door0002",
            "doorName": "B건물 출입문",
            "doorRelaySensor": "수동 개방",
            "doorSensor": "0"
        }]
}

DoorControl_in_data = {
    "doorID": "door001",
    "commandType": "unlock"
}


DoorControl_out_data = {
    "code": "200",
    "message": "성공"
}

Webhook_out_data = {
    "code": "200",
    "message": "성공"
}

bioInMessage = [Authentication_in_data,
                Capabilities_in_data,
                DoorProfiles_in_data,
                AccessUserInfos_in_data,
                RealtimeVerifEventInfos_in_data,
                StoredVerifEventInfos_in_data,
                RealtimeDoorStatus_in_data,
                DoorControl_in_data]

bioOutMessage = [Authentication_out_data,
                 Capabilities_out_data,
                 DoorProfiles_out_data,
                 AccessUserInfos_out_data,
                 RealtimeVerifEventInfos_out_data,
                 StoredVerifEventInfos_out_data,
                 RealtimeDoorStatus_out_data,
                 DoorControl_out_data,
                 Webhook_out_data
                 ]

bioMessages = ["Authentication",
               "Capabilities",
               "DoorProfiles",
               "AccessUserInfos",
               "RealtimeVerifEventInfos",
               "StoredVerifEventInfos",
               "RealtimeDoorStatus",
               "DoorControl"]
