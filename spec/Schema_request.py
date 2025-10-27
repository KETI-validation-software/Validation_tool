from json_checker import OptionalKey


# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmgvieyak001b6cd04cgaawmm_Capabilities_in_schema = {}

# CameraProfiles
cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_schema = {}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_schema = {
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
}

# StreamURLs
cmgvieyak001b6cd04cgaawmm_StreamURLs_in_schema = {
    "camList": [{
    "camID": str,
    "streamProtocolType": str,
}],
}

# ReplayURL
cmgvieyak001b6cd04cgaawmm_ReplayURL_in_schema = {
    "camList": [{
    "camID": str,
    "startTime": int,
    "endTime": int,
    "streamProtocolType": str,
}],
}

# RealtimeVideoEventInfos
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_schema = {
    "camList": [{
    "camID": str,
}],
    "duration": int,
    "transProtocol": {
    "transProtocolType": str,
    "transProtocolDesc": str,
},
    "eventFilter": str,
    "classFilter": str,
    "startTime": int,
}

# RealtimeVideoEventInfos WebHook OUT Schema
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_webhook_out_schema = {
    "code": str,
    "message": str,
}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_schema = {
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    "camList": [{
    "camID": str,
}],
    "maxCount": int,
    "classFilter": str,
    "eventFilter": str,
}

# cmgvieyak001b6cd04cgaawmm 스키마 리스트
cmgvieyak001b6cd04cgaawmm_inSchema = [
    cmgvieyak001b6cd04cgaawmm_Authentication_in_schema,
    cmgvieyak001b6cd04cgaawmm_Capabilities_in_schema,
    cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_schema,
    cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_schema,
    cmgvieyak001b6cd04cgaawmm_StreamURLs_in_schema,
    cmgvieyak001b6cd04cgaawmm_ReplayURL_in_schema,
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_schema,
    cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_schema,
]

# cmgvieyak001b6cd04cgaawmm WebHook 스키마 리스트
cmgvieyak001b6cd04cgaawmm_webhook_OutSchema = [
    None,
    None,
    None,
    None,
    None,
    None,
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_webhook_out_schema,
    None,
]

