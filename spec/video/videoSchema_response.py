from json_checker import OptionalKey


# Authentication
Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
Capabilities_out_schema = {
    "code": str,
    "message": str,
    "streamingSupport": [{
    "streamProtocolType": str,
    OptionalKey("streamProtocolDesc"): str,
}],
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# CameraProfiles
CameraProfiles_out_schema = {
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
StoredVideoInfos_out_schema = {
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

# StreamURLs
StreamURLs_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    OptionalKey("accessID"): str,
    OptionalKey("accessPW"): str,
    "camURL": str,
}],
}

# ReplayURL
ReplayURL_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "startTime": int,
    "camURL": str,
    OptionalKey("accessID"): str,
    OptionalKey("accessPW"): str,
    OptionalKey("endTime"): int,
}],
}

# RealtimeVideoEventInfos
RealtimeVideoEventInfos_out_schema = {
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

# StoredVideoEventInfos
StoredVideoEventInfos_out_schema = {
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
StoredObjectAnalyticsInfos_out_schema = {
    "code": str,
    "message": str,
    OptionalKey("camList"): [{
    "camID": str,
    "analyticsTime": int,
    OptionalKey("anlayticsResultList"): [{
    "anayticsID": str,
    "analyticsClass": str,
    OptionalKey("analyticsAttribute"): [str],
    OptionalKey("analyticsConfidence"): int,
    OptionalKey("aanalyticsDesc"): str,
    OptionalKey("analyticsBoundingBox"): {
    "left": int,
    "top": int,
    "right": int,
    "bottom": int,
},
}],
}],
}

# WebHook RealtimeVideoEventInfos
WebHook_RealtimeVideoEventInfos_in_schema = {
    "camList": [{
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": int,
    OptionalKey("endTime"): int,
    OptionalKey("eventDesc"): str,
}],
}

# steps 순서대로 스키마 리스트 생성
videoOutSchema = [
    Authentication_out_schema,
    Capabilities_out_schema,
    CameraProfiles_out_schema,
    StoredVideoInfos_out_schema,
    StreamURLs_out_schema,
    ReplayURL_out_schema,
    RealtimeVideoEventInfos_out_schema,
    StoredVideoEventInfos_out_schema,
    StoredObjectAnalyticsInfos_out_schema,
]

# WebHook 전용 스키마 리스트
videoWebhookSchema = [
    WebHook_RealtimeVideoEventInfos_in_schema,
]
