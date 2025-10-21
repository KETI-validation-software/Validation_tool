# request 모드

# Authentication
cmgyv3rzl014nvsveidu5jpzp_Authentication_in_data = {
    "userID": "",
    "userPW": ""
}

# Capabilities
cmgyv3rzl014nvsveidu5jpzp_Capabilities_in_data = {}

# CameraProfiles
cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_in_data = {}

# StoredVideoInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_in_data = {
    "timePeriod": {
    "startTime": 0,
    "endTime": 0
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
        "streamProtocolType": ""
    }
]
}

# ReplayURL
cmgyv3rzl014nvsveidu5jpzp_ReplayURL_in_data = {
    "camList": [
        {
        "camID": "",
        "startTime": 0,
        "endTime": 0,
        "streamProtocolType": ""
    }
]
}

# RealtimeVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_in_data = {
    "camList": [
        {
        "camID": "",
        "eventUUID": "",
        "eventName": "",
        "startTime": 0,
        "endTime": 0,
        "eventDesc": ""
    }
]
}

# RealtimeVideoEventInfos WebHook OUT Data
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_webhook_out_data = {
    "camList": [
        {
        "camID": ""
    }
],
    "duration": "",
    "transProtocol": {
    "transProtocolType": "",
    "transProtocolDesc": ""
},
    "eventFilter": "",
    "classFilter": "",
    "startTime": 0
}

# StoredVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_in_data = {
    "timePeriod": {
    "startTime": 0,
    "endTime": 0
},
    "camList": [
        {
        "camID": ""
    }
],
    "maxCount": 0,
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

