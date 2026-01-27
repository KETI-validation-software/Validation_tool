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
    "duration": 10000,
    "transProtocol": {
    "transProtocolType": "Webhook",
    "transProtocolDesc": ""
},
    "startTime": 20260112065600000
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

