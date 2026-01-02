# Authentication
cmiqr2b9j00i9ie8frw439h8i_Authentication_in_data = {
    "userID": "kisa",
    "userPW": "kisa_k1!2@"
}

# Capabilities
cmiqr2b9j00i9ie8frw439h8i_Capabilities_in_data = {}

# SensorDeviceProfiles
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_in_data = {}

# SensorDeviceControl
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl_in_data = {
    "sensorDeviceID": "",
    "commandType": ""
}

# SensorDeviceControl2
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl2_in_data = {
    "sensorDeviceID": "",
    "commandType": ""
}

# cmiqr2b9j00i9ie8frw439h8i 데이터 리스트
cmiqr2b9j00i9ie8frw439h8i_inData = [
    cmiqr2b9j00i9ie8frw439h8i_Authentication_in_data,
    cmiqr2b9j00i9ie8frw439h8i_Capabilities_in_data,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_in_data,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl_in_data,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl2_in_data,
]

# cmiqr2b9j00i9ie8frw439h8i API endpoint
cmiqr2b9j00i9ie8frw439h8i_messages = [
    "Authentication",
    "Capabilities",
    "SensorDeviceProfiles",
    "SensorDeviceControl",
    "SensorDeviceControl2",
]

# Authentication
cmiqr1jha00i6ie8fb1scb3go_Authentication_in_data = {
    "userID": "kisa",
    "userPW": "kisa_k1!2@"
}

# Capabilities
cmiqr1jha00i6ie8fb1scb3go_Capabilities_in_data = {}

# DoorProfiles
cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_in_data = {}

# RealtimeDoorStatus
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_in_data = {
    "doorList": [
        {
        "doorID": ""
    }
],
    "duration": 200,
    "transProtocol": {
    "transProtocolType": "Webhook",
    "transProtocolDesc": ""
},
    "startTime": 20251105163010124
}

# RealtimeDoorStatus WebHook OUT Data
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_out_data = {
    "code": "200",
    "message": "성공"
}

# DoorControl
cmiqr1jha00i6ie8fb1scb3go_DoorControl_in_data = {
    "doorID": "door0001",
    "commandType": ""
}

# RealtimeDoorStatus2
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_in_data = {
    "doorList": [
        {
        "doorID": ""
    }
],
    "duration": 10000,
    "transProtocol": {
    "transProtocolType": "Webhook",
    "transProtocolDesc": ""
},
    "startTime": 20251105163010124
}

# RealtimeDoorStatus2 WebHook OUT Data
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_out_data = {
    "code": "200",
    "message": "성공"
}

# cmiqr1jha00i6ie8fb1scb3go 데이터 리스트
cmiqr1jha00i6ie8fb1scb3go_inData = [
    cmiqr1jha00i6ie8fb1scb3go_Authentication_in_data,
    cmiqr1jha00i6ie8fb1scb3go_Capabilities_in_data,
    cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_in_data,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_in_data,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_in_data,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_in_data,
]

# cmiqr1jha00i6ie8fb1scb3go WebHook 데이터 리스트
cmiqr1jha00i6ie8fb1scb3go_webhook_outData = [
    None,
    None,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_out_data,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_out_data,
]

# cmiqr1jha00i6ie8fb1scb3go API endpoint
cmiqr1jha00i6ie8fb1scb3go_messages = [
    "Authentication",
    "Capabilities",
    "DoorProfiles",
    "RealtimeDoorStatus",
    "DoorControl",
    "RealtimeDoorStatus2",
]

# Authentication
cmiqr0kdw00i4ie8fr3firjtg_Authentication_in_data = {
    "userID": "kisa",
    "userPW": "kisa_k1!2@"
}

# Capabilities
cmiqr0kdw00i4ie8fr3firjtg_Capabilities_in_data = {}

# CameraProfiles
cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_in_data = {}

# PtzStatus
cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_in_data = {
    "camID": ""
}

# PtzContinuousMove
cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_in_data = {
    "camID": "",
    "velocity": {
    "pan": 10,
    "tilt": -20,
    "zoom": 30
},
    "timeOut": 5
}

# PtzStop
cmiqr0kdw00i4ie8fr3firjtg_PtzStop_in_data = {
    "camID": "",
    "pan": True,
    "tilt": True,
    "zoom": False
}

# cmiqr0kdw00i4ie8fr3firjtg 데이터 리스트
cmiqr0kdw00i4ie8fr3firjtg_inData = [
    cmiqr0kdw00i4ie8fr3firjtg_Authentication_in_data,
    cmiqr0kdw00i4ie8fr3firjtg_Capabilities_in_data,
    cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_in_data,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_in_data,
    cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_in_data,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStop_in_data,
]

# cmiqr0kdw00i4ie8fr3firjtg API endpoint
cmiqr0kdw00i4ie8fr3firjtg_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "PtzStatus",
    "PtzContinuousMove",
    "PtzStop",
]

# Authentication
cmii7wfuf006i8z1tcds6q69g_Authentication_in_data = {
    "userID": "kisa",
    "userPW": "kisa_k1!2@"
}

# Capabilities
cmii7wfuf006i8z1tcds6q69g_Capabilities_in_data = {}

# SensorDeviceProfiles
cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_in_data = {}

# RealtimeSensorData
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_in_data = {
    "sensorDeviceList": [
        {
        "sensorDeviceID": ""
    }
],
    "duration": 100,
    "transProtocol": {
    "transProtocolType": "Webhook",
    "transProtocolDesc": ""
},
    "startTime": 20251105163010124
}

# RealtimeSensorData WebHook OUT Data
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_out_data = {
    "code": "200",
    "message": "성공"
}

# RealtimeSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_in_data = {
    "sensorDeviceList": [
        {
        "sensorDeviceID": ""
    }
],
    "duration": 1000,
    "transProtocol": {
    "transProtocolType": "Webhook",
    "transProtocolDesc": ""
},
    "eventFilter": "",
    "startTime": 20251105163010123
}

# RealtimeSensorEventInfos WebHook OUT Data
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_out_data = {
    "code": "200",
    "message": "성공"
}

# StoredSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_in_data = {
    "timePeriod": {
    "startTime": 20251105163010124,
    "endTime": 20251115163010124
},
    "sensorDeviceList": [
        {
        "sensorDeviceID": ""
    }
],
    "maxCount": 8,
    "eventFilter": ""
}

# cmii7wfuf006i8z1tcds6q69g 데이터 리스트
cmii7wfuf006i8z1tcds6q69g_inData = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_in_data,
    cmii7wfuf006i8z1tcds6q69g_Capabilities_in_data,
    cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_in_data,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_in_data,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_in_data,
    cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_in_data,
]

# cmii7wfuf006i8z1tcds6q69g WebHook 데이터 리스트
cmii7wfuf006i8z1tcds6q69g_webhook_outData = [
    None,
    None,
    None,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_out_data,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_out_data,
    None,
]

# cmii7wfuf006i8z1tcds6q69g API endpoint
cmii7wfuf006i8z1tcds6q69g_messages = [
    "Authentication",
    "Capabilities",
    "SensorDeviceProfiles",
    "RealtimeSensorData",
    "RealtimeSensorEventInfos",
    "StoredSensorEventInfos",
]

# Authentication
cmii7w683006h8z1t7usnin5g_Authentication_in_data = {
    "userID": "kisa",
    "userPW": "kisa_k1!2@"
}

# Capabilities
cmii7w683006h8z1t7usnin5g_Capabilities_in_data = {}

# DoorProfiles
cmii7w683006h8z1t7usnin5g_DoorProfiles_in_data = {
    "testest": {
    "f1": "1123",
    "f2": "11233"
}
}

# AccessUserInfos
cmii7w683006h8z1t7usnin5g_AccessUserInfos_in_data = {}

# RealtimeVerifEventInfos
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_in_data = {
    "doorList": [
        {
        "doorID": ""
    }
],
    "duration": 500,
    "transProtocol": {
    "transProtocolType": "WebHook",
    "transProtocolDesc": ""
},
    "eventFilter": "",
    "startTime": 20251105163010124
}

# RealtimeVerifEventInfos WebHook OUT Data
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_out_data = {
    "code": "200",
    "message": ""
}

# StoredVerifEventInfos
cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_in_data = {
    "timePeriod": {
    "startTime": 20251105163010124,
    "endTime": 20251115163010124
},
    "doorList": [
        {
        "doorID": ""
    }
],
    "maxCount": 10,
    "eventFilter": ""
}

# cmii7w683006h8z1t7usnin5g 데이터 리스트
cmii7w683006h8z1t7usnin5g_inData = [
    cmii7w683006h8z1t7usnin5g_Authentication_in_data,
    cmii7w683006h8z1t7usnin5g_Capabilities_in_data,
    cmii7w683006h8z1t7usnin5g_DoorProfiles_in_data,
    cmii7w683006h8z1t7usnin5g_AccessUserInfos_in_data,
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_in_data,
    cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_in_data,
]

# cmii7w683006h8z1t7usnin5g WebHook 데이터 리스트
cmii7w683006h8z1t7usnin5g_webhook_outData = [
    None,
    None,
    None,
    None,
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_out_data,
    None,
]

# cmii7w683006h8z1t7usnin5g API endpoint
cmii7w683006h8z1t7usnin5g_messages = [
    "Authentication",
    "Capabilities",
    "DoorProfiles",
    "AccessUserInfos",
    "RealtimeVerifEventInfos",
    "StoredVerifEventInfos",
]

# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_in_data = {
    "userID": "kisa",
    "userPW": "kisa_k1!2@"
}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_in_data = {}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_data = {}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_data = {
    "camList": [
        {
        "camID": "",
        "streamProtocolType": "RTSP"
    }
]
}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_data = {
    "camList": [
        {
        "camID": ""
    }
],
    "transProtocol": {
    "transProtocolType": "Webhook",
    "transProtocolDesc": ""
},
    "duration": 10,
    "eventFilter": "",
    "classFilter": "",
    "startTime": 20251105163010124
}

# RealtimeVideoEventInfos WebHook OUT Data
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_data = {
    "code": "200",
    "message": "성공"
}

# StoredVideoInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_in_data = {
    "timePeriod": {
    "startTime": 20251105163010124,
    "endTime": 20251115163010124
},
    "camList": [
        {
        "camID": ""
    }
]
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_in_data = {
    "camList": [
        {
        "camID": "",
        "startTime": 20251105163010124,
        "endTime": 20251115163010123,
        "streamProtocolType": "RTSP"
    }
]
}

# StoredVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_in_data = {
    "timePeriod": {
    "startTime": 20251105163010124,
    "endTime": 20251115163010124
},
    "camList": [
        {
        "camID": ""
    }
],
    "maxCount": 3,
    "eventFilter": "",
    "classFilter": ""
}

# StoredObjectAnalyticsInfos
cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_in_data = {
    "timePeriod": {
    "startTime": 20251105163010124,
    "endTime": 20251115163010124
},
    "camList": [
        {
        "camID": ""
    }
],
    "filterList": [
        {
        "classFilter": [
        "Human"
    ],
        "attributeFilter": [
        "Male",
        "Female"
    ]
    }
]
}

# cmii7v8pr006g8z1tvo55a50u 데이터 리스트
cmii7v8pr006g8z1tvo55a50u_inData = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_in_data,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_in_data,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_data,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_data,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_data,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_in_data,
    cmii7v8pr006g8z1tvo55a50u_ReplayURL_in_data,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_in_data,
    cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_in_data,
]

# cmii7v8pr006g8z1tvo55a50u WebHook 데이터 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_outData = [
    None,
    None,
    None,
    None,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_data,
    None,
    None,
    None,
    None,
]

# cmii7v8pr006g8z1tvo55a50u API endpoint
cmii7v8pr006g8z1tvo55a50u_messages = [
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

