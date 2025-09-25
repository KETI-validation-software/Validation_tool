from json_checker import OptionalKey


# Authentication
Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
Capabilities_in_schema = {}

# CameraProfiles
CameraProfiles_in_schema = {}

# StoredVideoInfos
StoredVideoInfos_in_schema = {
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
}

# StreamURLs
StreamURLs_in_schema = {
    "camList": [{
    "camID": str,
    "streamProtocolType": str,
}],
}

# ReplayURL
ReplayURL_in_schema = {
    "camList": [{
    "camID": str,
    "startTime": int,
    "endTime": int,
    "streamProtocolType": str,
}],
}

# RealtimeVideoEventInfos
RealtimeVideoEventInfos_in_schema = {
    "camList": [{
    "camID": str,
}],
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("duration"): int,
    OptionalKey("eventFilter"): str,
    OptionalKey("classFilter"): str,
    OptionalKey("startTime"): int,
}

# 
_in_schema = {}

# StoredVideoEventInfos
StoredVideoEventInfos_in_schema = {
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str,
    OptionalKey("classFilter"): str,
}

# StoredObjectAnalyticsInfos
StoredObjectAnalyticsInfos_in_schema = {
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
    OptionalKey("filterList"): [{
    OptionalKey("eventFilter"): [str],
    OptionalKey("attributeFilter"): [str],
}],
}

# WebHook RealtimeVideoEventInfos
WebHook_RealtimeVideoEventInfos_out_schema = {
    OptionalKey("code"): str,
    OptionalKey("message"): str,
}

# steps 순서대로 스키마 리스트 생성
videoInSchema = [
    Authentication_in_schema,
    Capabilities_in_schema,
    CameraProfiles_in_schema,
    StoredVideoInfos_in_schema,
    StreamURLs_in_schema,
    ReplayURL_in_schema,
    RealtimeVideoEventInfos_in_schema,
    _in_schema,
    StoredVideoEventInfos_in_schema,
    StoredObjectAnalyticsInfos_in_schema,
]

# WebHook 전용 스키마 리스트
videoWebhookSchema = [
    WebHook_RealtimeVideoEventInfos_out_schema,
]
