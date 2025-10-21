from json_checker import OptionalKey


# Authentication
cmgyv3rzl014nvsveidu5jpzp_Authentication_out_schema = {}

# Capabilities
cmgyv3rzl014nvsveidu5jpzp_Capabilities_out_schema = {}

# CameraProfiles
cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_out_schema = {}

# StoredVideoInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "timeList": [{
    "startTime": float,
    "endTime": float,
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
    OptionalKey("fps"): float,
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
    OptionalKey("fps"): float,
    OptionalKey("videoCodec"): str,
    OptionalKey("audioCodec"): str,
},
}],
}

# RealtimeVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_out_schema = {}

# RealtimeVideoEventInfos WebHook IN Schema
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_webhook_in_schema = {
    "code": str,
    "message": str,
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

