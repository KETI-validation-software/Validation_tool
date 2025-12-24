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

# SensorDeviceControl
cmiqr1jha00i6ie8fb1scb3go_SensorDeviceControl_in_data = {
    "sensorDeviceID": "iot0001",
    "commandType": "Alarm|on"
}

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
    cmiqr1jha00i6ie8fb1scb3go_SensorDeviceControl_in_data,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_in_data,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_in_data,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_in_data,
]

# cmiqr1jha00i6ie8fb1scb3go WebHook 데이터 리스트
cmiqr1jha00i6ie8fb1scb3go_webhook_outData = [
    None,
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
    "SensorDeviceControl",
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

