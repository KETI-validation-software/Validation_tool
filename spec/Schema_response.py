from json_checker import OptionalKey


# Authentication
cmii7wfuf006i8z1tcds6q69g_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmii7wfuf006i8z1tcds6q69g_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# SensorDeviceProfiles
cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList": [{
    "": {
    "sensorDeviceID": str,
    "sensorDeviceType": str,
    "sensorDeviceName": str,
    OptionalKey("sensorDeviceLoc"): {
    "lon": str,
    "lat": str,
    OptionalKey("alt"): str,
    OptionalKey("desc"): str,
},
},
}],
}

# RealtimeSensorData
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeSensorData WebHook IN Schema
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_in_schema = {
    "sensorDeviceList": [{
    "": {
    "sensorDeviceID": str,
    "measureTime": int,
    "sensorDeviceType": str,
    "sensorDeviceUnit": str,
    "sensorDeviceValue": str,
},
}],
}

# RealtimeSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_out_schema = {}

# RealtimeSensorEventInfos WebHook IN Schema
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_in_schema = {}

# StoredSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList": [{
    "": {
    "sensorDeviceID": str,
    "eventName": str,
    "eventTime": int,
    OptionalKey("eventDesc"): str,
},
}],
}

# cmii7wfuf006i8z1tcds6q69g 스키마 리스트
cmii7wfuf006i8z1tcds6q69g_outSchema = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_out_schema,
    cmii7wfuf006i8z1tcds6q69g_Capabilities_out_schema,
    cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_out_schema,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_out_schema,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_out_schema,
    cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_out_schema,
]

# cmii7wfuf006i8z1tcds6q69g WebHook 스키마 리스트
cmii7wfuf006i8z1tcds6q69g_webhook_inSchema = [
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_in_schema,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_in_schema,
]

# Authentication
cmii7w683006h8z1t7usnin5g_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmii7w683006h8z1t7usnin5g_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# DoorProfiles
cmii7w683006h8z1t7usnin5g_DoorProfiles_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "doorID": str,
    "doorName": str,
    "doorRelayStatus": str,
    OptionalKey("doorSensor"): str,
    OptionalKey("doorLoc"): {
    "lon": str,
    "lat": str,
    OptionalKey("alt"): str,
    OptionalKey("desc"): str,
},
    OptionalKey("bioDeviceList"): [{
    OptionalKey("bioDeviceID"): str,
    OptionalKey("bioDeviceName"): str,
    "bioDeviceAuthTypeList": [str],
}],
    OptionalKey("otherDeviceList"): [{
    OptionalKey("otherDeviceID"): str,
    OptionalKey("otherDeviceName"): str,
    "otherDeviceAuthTypeList": [str],
}],
}],
}

# AccessUserInfos
cmii7w683006h8z1t7usnin5g_AccessUserInfos_out_schema = {
    "code": str,
    "message": str,
    "userList": [{
    "": {
    "userID": str,
    "userName": str,
    OptionalKey("userDesc"): str,
    "doorList": [{
    "": {
    "doorID": str,
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
},
}],
},
}],
}

# RealtimeVerifEventInfos
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeVerifEventInfos WebHook IN Schema
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_in_schema = {
    "doorList": [{
    "": {
    "eventTime": int,
    "doorID": str,
    OptionalKey("userID"): str,
    OptionalKey("bioAuthTypeList"): [str],
    OptionalKey("otherAuthTypeList"): [str],
    "eventName": str,
    OptionalKey("eventDesc"): str,
},
}],
}

# StoredVerifEventInfos
cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "": {
    "eventTime": int,
    "doorID": str,
    OptionalKey("userID"): str,
    OptionalKey("bioAuthTypeList"): [str],
    OptionalKey("otherAuthTypeList"): [str],
    "eventName": str,
},
}],
}

# cmii7w683006h8z1t7usnin5g 스키마 리스트
cmii7w683006h8z1t7usnin5g_outSchema = [
    cmii7w683006h8z1t7usnin5g_Authentication_out_schema,
    cmii7w683006h8z1t7usnin5g_Capabilities_out_schema,
    cmii7w683006h8z1t7usnin5g_DoorProfiles_out_schema,
    cmii7w683006h8z1t7usnin5g_AccessUserInfos_out_schema,
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_out_schema,
    cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_out_schema,
]

# cmii7w683006h8z1t7usnin5g WebHook 스키마 리스트
cmii7w683006h8z1t7usnin5g_webhook_inSchema = [
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_in_schema,
]

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
    "streamingSupport": [str],
    "transportSupport": [str],
}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_schema = {
    "code": str,
    "message": str,
    "camList": [str],
}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_schema = {
    "code": str,
    "message": str,
    "camList": [str],
}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeVideoEventInfos WebHook IN Schema
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_schema = {
    "camList": [{
    "": {
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": int,
    OptionalKey("endTime"): int,
    OptionalKey("eventDesc"): str,
},
}],
}

# StoredVideoInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "": {
    "camID": str,
    "timeList": [{
    "startTime": int,
    OptionalKey("endTime"): int,
}],
},
}],
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "": {
    "camID": str,
    OptionalKey("accessID"): str,
    OptionalKey("accessPW"): str,
    "startTime": int,
    OptionalKey("endTime"): str,
    "camURL": str,
    OptionalKey("videoInfo"): {
    OptionalKey("resolution"): str,
    OptionalKey("fps"): int,
    OptionalKey("videoCodec"): str,
    OptionalKey("audioCodec"): str,
},
},
}],
}

# StoredVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "": {
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": int,
    OptionalKey("endTime"): int,
    OptionalKey("eventDesc"): str,
},
}],
}

# StoredObjectAnalyticsInfos
cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "": {
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": int,
    OptionalKey("endTime"): int,
    OptionalKey("eventDesc"): str,
},
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

