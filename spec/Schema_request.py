from json_checker import OptionalKey


# Authentication
cmsy90xd705aarc0quh4je1k0_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmsy90xd705aarc0quh4je1k0_Capabilities_in_schema = {}

# CameraProfiles
cmsy90xd705aarc0quh4je1k0_CameraProfiles_in_schema = {}

# StreamURLs
cmsy90xd705aarc0quh4je1k0_StreamURLs_in_schema = {
    "camList": [{
    "camID": str,
    "streamProtocolType": str,
}],
}

# RealtimeVideoEventInfos
cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_in_schema = {
    "camList": [{
    "camID": str,
}],
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    "duration": int,
    OptionalKey("eventFilter"): str,
    OptionalKey("startTime"): str,
}

# RealtimeVideoEventInfos WebHook OUT Schema
cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_webhook_out_schema = {
    "code": str,
    "message": str,
}

# cmsy90xd705aarc0quh4je1k0 스키마 리스트
cmsy90xd705aarc0quh4je1k0_inSchema = [
    cmsy90xd705aarc0quh4je1k0_Authentication_in_schema,
    cmsy90xd705aarc0quh4je1k0_Capabilities_in_schema,
    cmsy90xd705aarc0quh4je1k0_CameraProfiles_in_schema,
    cmsy90xd705aarc0quh4je1k0_StreamURLs_in_schema,
    cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_in_schema,
]

# cmsy90xd705aarc0quh4je1k0 WebHook 스키마 리스트
cmsy90xd705aarc0quh4je1k0_webhook_OutSchema = [
    None,
    None,
    None,
    None,
    cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_webhook_out_schema,
]

