# Authentication
cmh1ua7b00021gxc3rjepbkrm_Authentication_in_data = {
    "userID": "user0001",
    "userPW": "pass0001"
}

# DoorProfiles
cmh1ua7b00021gxc3rjepbkrm_DoorProfiles_in_data = {}

# RealtimeDoorStatus
cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_in_data = {
    "doorList": [
        {
        "doorID": ""
    }
],
    "duration": 10000,
    "transProtocol": {
    "transProtocolType": "WebHook",
    "transProtocolDesc": ""
},
    "startTime": 20251125120922000
}

# RealtimeDoorStatus WebHook OUT Data
cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_webhook_out_data = {
    "code": "",
    "message": ""
}

# DoorControl
cmh1ua7b00021gxc3rjepbkrm_DoorControl_in_data = {
    "doorID": "",
    "commandType": ""
}

# RealtimeDoorStatus
cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_in_data = {
    "doorList": [
        {
        "doorID": ""
    }
],
    "duration": "10000",
    "transProtocol": [
        {
        "transProtocolType": "WebHook",
        "transProtocolDesc": ""
    }
],
    "startTime": 20251125122103000
}

# RealtimeDoorStatus WebHook OUT Data
cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_webhook_out_data = {
    "code": "200",
    "message": "성공"
}

# cmh1ua7b00021gxc3rjepbkrm 데이터 리스트
cmh1ua7b00021gxc3rjepbkrm_inData = [
    cmh1ua7b00021gxc3rjepbkrm_Authentication_in_data,
    cmh1ua7b00021gxc3rjepbkrm_DoorProfiles_in_data,
    cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_in_data,
    cmh1ua7b00021gxc3rjepbkrm_DoorControl_in_data,
    cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_in_data,
]

# cmh1ua7b00021gxc3rjepbkrm WebHook 데이터 리스트
cmh1ua7b00021gxc3rjepbkrm_webhook_outData = [
    cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_webhook_out_data,
    cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_webhook_out_data,
]

# cmh1ua7b00021gxc3rjepbkrm API endpoint
cmh1ua7b00021gxc3rjepbkrm_messages = [
    "Authentication",
    "DoorProfiles",
    "RealtimeDoorStatus",
    "DoorControl",
    "RealtimeDoorStatus",
]

# Authentication
cmgyv3rzl014nvsveidu5jpzp_Authentication_in_data = {
    "userID": "user0001",
    "userPW": "pass0001"
}

# Capabilities
cmgyv3rzl014nvsveidu5jpzp_Capabilities_in_data = {}

# CameraProfiles
cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_in_data = {}

# StoredVideoInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_in_data = {
    "timePeriod": {
    "startTime": 1760948700000,
    "endTime": 1761121500000
},
    "camList": [
        {
        "camID": ""
    }
]
}

# StreamURLs
cmgyv3rzl014nvsveidu5jpzp_StreamURLs_in_data = {
    "camList": [
        {
        "camID": "",
        "streamProtocolType": "RTSP"
    }
]
}

# ReplayURL
cmgyv3rzl014nvsveidu5jpzp_ReplayURL_in_data = {
    "camList": [
        {
        "camID": "",
        "startTime": 1760949060000,
        "endTime": 1761208260000,
        "streamProtocolType": "RTSP"
    }
]
}

# RealtimeVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_in_data = {
    "camList": [
        {
        "camID": ""
    }
],
    "duration": "100",
    "transProtocol": {
    "transProtocolType": "WebHook",
    "transProtocolDesc": "127.0.0.1:8090"
},
    "eventFilter": "",
    "classFilter": "",
    "startTime": 1761110160000
}

# RealtimeVideoEventInfos WebHook OUT Data
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_webhook_out_data = {
    "code": "",
    "message": ""
}

# StoredVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_in_data = {
    "timePeriod": {
    "startTime": 1759221900000,
    "endTime": 1761727500000
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

# cmgyv3rzl014nvsveidu5jpzp 데이터 리스트
cmgyv3rzl014nvsveidu5jpzp_inData = [
    cmgyv3rzl014nvsveidu5jpzp_Authentication_in_data,
    cmgyv3rzl014nvsveidu5jpzp_Capabilities_in_data,
    cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_in_data,
    cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_in_data,
    cmgyv3rzl014nvsveidu5jpzp_StreamURLs_in_data,
    cmgyv3rzl014nvsveidu5jpzp_ReplayURL_in_data,
    cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_in_data,
    cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_in_data,
]

# cmgyv3rzl014nvsveidu5jpzp WebHook 데이터 리스트
cmgyv3rzl014nvsveidu5jpzp_webhook_outData = [
    cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_webhook_out_data,
]

# cmgyv3rzl014nvsveidu5jpzp API endpoint
cmgyv3rzl014nvsveidu5jpzp_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "StoredVideoInfos",
    "StreamURLs",
    "ReplayURL",
    "RealtimeVideoEventInfos",
    "StoredVideoEventInfos",
]

