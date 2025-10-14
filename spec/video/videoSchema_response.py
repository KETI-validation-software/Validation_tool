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

# RealtimeVideoEventInfos - 구독 응답 검증 (시스템이 플랫폼의 응답을 검증)
RealtimeVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# WebHook RealtimeVideoEventInfos - 웹훅 이벤트 데이터 검증 (시스템이 플랫폼의 웹훅 콜백을 검증)
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

# spec_002 스키마 리스트
spec_002_outSchema = [
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

# spec_002 WebHook 스키마 리스트
spec_002_webhookSchema = [
    WebHook_RealtimeVideoEventInfos_in_schema,  # 플랫폼→시스템: 웹훅 이벤트 데이터 (시스템이 검증)
]

