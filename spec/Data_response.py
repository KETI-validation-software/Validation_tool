# Authentication
cmsy90xd705aarc0quh4je1k0_Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청"
}

# Capabilities
cmsy90xd705aarc0quh4je1k0_Capabilities_out_data = {
    "code": "200",
    "message": "성공",
    "streamingSupport": [
        {
        "streamProtocolType": ""
    }
],
    "transportSupport": [
        {
        "transProtocolType": "Webhook"
    }
]
}

# CameraProfiles
cmsy90xd705aarc0quh4je1k0_CameraProfiles_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "camName": "카메라1"
    },
        {
        "camID": "cam0002",
        "camName": "카메라2"
    },
        {
        "camID": "cam003",
        "camName": "카메라3"
    },
        {
        "camID": "cam004",
        "camName": "카메라4"
    }
]
}

# StreamURLs
cmsy90xd705aarc0quh4je1k0_StreamURLs_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": ""
    }
]
}

# RealtimeVideoEventInfos
cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_out_data = {
    "code": "200",
    "message": "성공"
}

# RealtimeVideoEventInfos WebHook IN Data
cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_webhook_in_data = {
    "camList": [
        {
        "camID": "",
        "eventUUID": "event01",
        "eventName": "",
        "startTime": ""
    }
]
}

# cmsy90xd705aarc0quh4je1k0 데이터 리스트
cmsy90xd705aarc0quh4je1k0_outData = [
    cmsy90xd705aarc0quh4je1k0_Authentication_out_data,
    cmsy90xd705aarc0quh4je1k0_Capabilities_out_data,
    cmsy90xd705aarc0quh4je1k0_CameraProfiles_out_data,
    cmsy90xd705aarc0quh4je1k0_StreamURLs_out_data,
    cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_out_data,
]

# cmsy90xd705aarc0quh4je1k0 WebHook 데이터 리스트
cmsy90xd705aarc0quh4je1k0_webhook_inData = [
    None,
    None,
    None,
    None,
    cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_webhook_in_data,
]

# cmsy90xd705aarc0quh4je1k0 API endpoint
cmsy90xd705aarc0quh4je1k0_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "StreamURLs",
    "RealtimeVideoEventInfos",
]

