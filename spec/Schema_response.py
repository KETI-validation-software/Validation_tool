from json_checker import OptionalKey


# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_out_schema = {
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
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_schema = {
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

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_schema = {
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

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeVideoEventInfos WebHook IN Schema
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_schema = {
    "camList": [{
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": int,
    OptionalKey("endTime"): int,
    OptionalKey("eventDesc"): str,
}],
}

# StoredVideoInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "timeList": [{
    "startTime": int,
    OptionalKey("endTime"): int,
}],
}],
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    OptionalKey("accessID"): str,
    OptionalKey("accessPW"): str,
    "startTime": int,
    OptionalKey("endTime"): int,
    "camURL": str,
    OptionalKey("videoInfo"): {
    OptionalKey("resolution"): str,
    OptionalKey("fps"): int,
    OptionalKey("videoCodec"): str,
    OptionalKey("audioCodec"): str,
},
}],
}

# StoredVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": int,
    OptionalKey("endTime"): int,
    OptionalKey("eventDesc"): str,
}],
}

# StoredObjectAnalyticsInfos
cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "analyticsTime": int,
    "anlayticsResultList": [{
    "anayticsID": str,
    "analyticsClass": str,
    OptionalKey("analyticsAttribute"): [str],
    OptionalKey("analyticsConfidence"): int,
    OptionalKey("analyticsBoundingBox"): {
    "left": int,
    "top": int,
    "right": int,
    "bottom": int,
},
    OptionalKey("analyticsDesc"): str,
}],
}],
}

# cmii7v8pr006g8z1tvo55a50u 스키마 리스트
cmii7v8pr006g8z1tvo55a50u_outSchema = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_out_schema,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_out_schema,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_schema,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_schema,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_schema,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_schema,
    cmii7v8pr006g8z1tvo55a50u_ReplayURL_out_schema,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_out_schema,
    cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_out_schema,
]

# cmii7v8pr006g8z1tvo55a50u WebHook 스키마 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_inSchema = [
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_schema,
]

