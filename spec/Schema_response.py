from json_checker import OptionalKey


# Authentication
cmiqr2b9j00i9ie8frw439h8i_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmiqr2b9j00i9ie8frw439h8i_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# SensorDeviceProfiles
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList": [{
    "sensorDeviceID": str,
    "sensorDeviceType": str,
    "sensorDeviceName": str,
    OptionalKey("sensorDeviceLoc"): {
    "lon": str,
    "lat": str,
    OptionalKey("alt"): str,
    OptionalKey("desc"): str,
},
}],
}

# SensorDeviceControl
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceID": str,
    "sensorDeviceStatus": str,
}

# SensorDeviceControl2
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl2_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceID": str,
    "sensorDeviceStatus": str,
}

# cmiqr2b9j00i9ie8frw439h8i 스키마 리스트
cmiqr2b9j00i9ie8frw439h8i_outSchema = [
    cmiqr2b9j00i9ie8frw439h8i_Authentication_out_schema,
    cmiqr2b9j00i9ie8frw439h8i_Capabilities_out_schema,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_out_schema,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl_out_schema,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl2_out_schema,
]

# Authentication
cmiqr1jha00i6ie8fb1scb3go_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmiqr1jha00i6ie8fb1scb3go_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# DoorProfiles
cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_out_schema = {
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

# RealtimeDoorStatus
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeDoorStatus WebHook IN Schema
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_in_schema = {
    "doorList": [{
    "doorID": str,
    "doorName": str,
    OptionalKey("doorRelaySensor"): str,
    "doorSensor": str,
}],
}

# DoorControl
cmiqr1jha00i6ie8fb1scb3go_DoorControl_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeDoorStatus2
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeDoorStatus2 WebHook IN Schema
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_in_schema = {
    "doorList": [{
    "doorID": str,
    "doorName": str,
    "doorRelaySensor": str,
    "doorSensor": str,
}],
}

# cmiqr1jha00i6ie8fb1scb3go 스키마 리스트
cmiqr1jha00i6ie8fb1scb3go_outSchema = [
    cmiqr1jha00i6ie8fb1scb3go_Authentication_out_schema,
    cmiqr1jha00i6ie8fb1scb3go_Capabilities_out_schema,
    cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_out_schema,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_out_schema,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_out_schema,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_out_schema,
]

# cmiqr1jha00i6ie8fb1scb3go WebHook 스키마 리스트
cmiqr1jha00i6ie8fb1scb3go_webhook_inSchema = [
    None,
    None,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_in_schema,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_in_schema,
]

# Authentication
cmiqr0kdw00i4ie8fr3firjtg_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmiqr0kdw00i4ie8fr3firjtg_Capabilities_out_schema = {
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
cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_out_schema = {
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

# PtzStatus
cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_out_schema = {
    "code": str,
    "message": str,
    OptionalKey("position"): {
    OptionalKey("pan"): int,
    OptionalKey("tilt"): int,
    OptionalKey("zoom"): int,
},
    "moveStatus": {
    OptionalKey("pan"): str,
    OptionalKey("tilt"): str,
    OptionalKey("zoom"): str,
},
}

# PtzContinuousMove
cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_out_schema = {
    "code": str,
    "message": str,
}

# PtzStop
cmiqr0kdw00i4ie8fr3firjtg_PtzStop_out_schema = {
    "code": str,
    "message": str,
}

# cmiqr0kdw00i4ie8fr3firjtg 스키마 리스트
cmiqr0kdw00i4ie8fr3firjtg_outSchema = [
    cmiqr0kdw00i4ie8fr3firjtg_Authentication_out_schema,
    cmiqr0kdw00i4ie8fr3firjtg_Capabilities_out_schema,
    cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_out_schema,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_out_schema,
    cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_out_schema,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStop_out_schema,
]

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
    "sensorDeviceID": str,
    "sensorDeviceType": str,
    "sensorDeviceName": str,
    OptionalKey("sensorDeviceLoc"): {
    "lon": str,
    "lat": str,
    OptionalKey("alt"): str,
    OptionalKey("desc"): str,
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
    "sensorDeviceID": str,
    "measureTime": int,
    "sensorDeviceType": str,
    "sensorDeviceUnit": str,
    "sensorDeviceValue": str,
}],
}

# RealtimeSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeSensorEventInfos WebHook IN Schema
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
    "eventName": str,
    "eventTime": int,
    OptionalKey("eventDesc"): str,
}],
}

# StoredSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList": [{
    "sensorDeviceID": str,
    "eventName": str,
    "eventTime": int,
    OptionalKey("eventDesc"): str,
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
    None,
    None,
    None,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_in_schema,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_in_schema,
    None,
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
    "userID": str,
    "userName": str,
    OptionalKey("userDesc"): str,
    "doorList": [{
    "doorID": str,
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
}],
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
    "eventTime": int,
    "doorID": str,
    OptionalKey("userID"): str,
    OptionalKey("bioAuthTypeList"): [str],
    OptionalKey("otherAuthTypeList"): [str],
    "eventName": str,
    OptionalKey("eventDesc"): str,
}],
}

# StoredVerifEventInfos
cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "eventTime": int,
    "doorID": str,
    OptionalKey("userID"): str,
    OptionalKey("bioAuthTypeList"): [str],
    OptionalKey("otherAuthTypeList"): [str],
    "eventName": str,
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
    None,
    None,
    None,
    None,
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_in_schema,
    None,
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
    None,
    None,
    None,
    None,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_schema,
    None,
    None,
    None,
    None,
]

