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

# Authentication
cmh1u5pef000sgxc3bzl4y9v0_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# DoorProfiles
cmh1u5pef000sgxc3bzl4y9v0_DoorProfiles_in_schema = {}

# RealtimeDoorStatus
cmh1u5pef000sgxc3bzl4y9v0_RealtimeDoorStatus_in_schema = {
    "doorList": [{
    "doorID": str,
    "doorName": str,
    "doorRelaySensor": str,
    "doorSensor": str,
}],
}

# RealtimeDoorStatus WebHook OUT Schema
cmh1u5pef000sgxc3bzl4y9v0_RealtimeDoorStatus_webhook_out_schema = {
    "code": str,
    "message": str,
}

# DoorControl
cmh1u5pef000sgxc3bzl4y9v0_DoorControl_in_schema = {
    "doorID": str,
    "commandType": str,
}

# cmh1u5pef000sgxc3bzl4y9v0 스키마 리스트
cmh1u5pef000sgxc3bzl4y9v0_inSchema = [
    cmh1u5pef000sgxc3bzl4y9v0_Authentication_in_schema,
    cmh1u5pef000sgxc3bzl4y9v0_DoorProfiles_in_schema,
    cmh1u5pef000sgxc3bzl4y9v0_RealtimeDoorStatus_in_schema,
    cmh1u5pef000sgxc3bzl4y9v0_DoorControl_in_schema,
]

# cmh1u5pef000sgxc3bzl4y9v0 WebHook 스키마 리스트
cmh1u5pef000sgxc3bzl4y9v0_webhook_OutSchema = [
    cmh1u5pef000sgxc3bzl4y9v0_RealtimeDoorStatus_webhook_out_schema,
]

