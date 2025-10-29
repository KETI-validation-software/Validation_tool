from json_checker import OptionalKey


# Authentication
cmgyv3rzl014nvsveidu5jpzp_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmgyv3rzl014nvsveidu5jpzp_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "streamingSupport": [{
    "streamProtocolType": str,
    "streamProtocolDesc": str,
}],
    "transportSupport": [{
    "transProtocolType": str,
    "transProtocolDesc": str,
}],
}

# CameraProfiles
cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "camName": str,
    OptionalKey("camLoc"): {
    "lon": str,
    "lat": str,
    OptionalKey("alt"): str,
    OptionalKey("desc"): str,
},
    OptionalKey("camConfig"): {
    "camType": str,
},
}],
}

# StoredVideoInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "timeList": [{
    "startTime": int,
    "endTime": int,
}],
}],
}

# StreamURLs
cmgyv3rzl014nvsveidu5jpzp_StreamURLs_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    OptionalKey("accessID"): str,
    OptionalKey("accessPW"): str,
    "camURL": str,
    OptionalKey("videoInfo"): {
    OptionalKey("resolution"): str,
    OptionalKey("fps"): int,
    OptionalKey("videoCodec"): str,
    OptionalKey("audioCodec"): str,
},
}],
}

# ReplayURL
cmgyv3rzl014nvsveidu5jpzp_ReplayURL_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    OptionalKey("accessID"): str,
    OptionalKey("accessPW"): str,
    "startTime": str,
    OptionalKey("endTime"): str,
    "camURL": str,
    OptionalKey("videoInfo"): {
    OptionalKey("resolution"): str,
    OptionalKey("fps"): int,
    OptionalKey("videoCodec"): str,
    OptionalKey("audioCodec"): str,
},
}],
}

# RealtimeVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeVideoEventInfos WebHook IN Schema
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_webhook_in_schema = {
    "camList": [{
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": int,
    OptionalKey("endTime"): int,
    OptionalKey("eventDesc"): str,
}],
}

# StoredVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": str,
    "endTime": str,
    "eventDesc": str,
}],
}

# cmgyv3rzl014nvsveidu5jpzp 스키마 리스트
cmgyv3rzl014nvsveidu5jpzp_outSchema = [
    cmgyv3rzl014nvsveidu5jpzp_Authentication_out_schema,
    cmgyv3rzl014nvsveidu5jpzp_Capabilities_out_schema,
    cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_out_schema,
    cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_out_schema,
    cmgyv3rzl014nvsveidu5jpzp_StreamURLs_out_schema,
    cmgyv3rzl014nvsveidu5jpzp_ReplayURL_out_schema,
    cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_out_schema,
    cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_out_schema,
]

# cmgyv3rzl014nvsveidu5jpzp WebHook 스키마 리스트
cmgyv3rzl014nvsveidu5jpzp_webhook_inSchema = [
    cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_webhook_in_schema,
]

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
    "eventUUID": str,
    "eventName": str,
    "startTime": str,
    "endTime": str,
    "eventDesc": str,
}],
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
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_webhook_out_schema,
]

