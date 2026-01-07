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
cmii7shen005i8z1tagevx4qh_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmii7shen005i8z1tagevx4qh_Capabilities_in_schema = {}

# SensorDeviceProfiles
cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_in_schema = {}

# RealtimeSensorData
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    "duration": int,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("startTime"): int,
}

# RealtimeSensorData WebHook OUT Schema
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeSensorEventInfos
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("duration"): int,
    OptionalKey("eventFilter"): str,
    OptionalKey("startTime"): int,
}

# RealtimeSensorEventInfos WebHook OUT Schema
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_out_schema = {
    "code": str,
    "message": str,
}

# StoredSensorEventInfos
cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_in_schema = {
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    "sensorDeviceList": [{}],
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str,
}

# cmii7shen005i8z1tagevx4qh 스키마 리스트
cmii7shen005i8z1tagevx4qh_inSchema = [
    cmii7shen005i8z1tagevx4qh_Authentication_in_schema,
    cmii7shen005i8z1tagevx4qh_Capabilities_in_schema,
    cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_in_schema,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_in_schema,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_in_schema,
    cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_in_schema,
]

# cmii7shen005i8z1tagevx4qh WebHook 스키마 리스트
cmii7shen005i8z1tagevx4qh_webhook_OutSchema = [
    None,
    None,
    None,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_out_schema,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_out_schema,
    None,
]

# Authentication
cmii7pysb004k8z1tts0npxfm_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmii7pysb004k8z1tts0npxfm_Capabilities_in_schema = {}

# DoorProfiles
cmii7pysb004k8z1tts0npxfm_DoorProfiles_in_schema = {}

# AccessUserInfos
cmii7pysb004k8z1tts0npxfm_AccessUserInfos_in_schema = {}

# RealtimeVerifEventInfos
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("duration"): int,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("eventFilter"): str,
    OptionalKey("startTime"): int,
}

# RealtimeVerifEventInfos WebHook OUT Schema
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_out_schema = {
    "code": str,
    "message": str,
}

# StoredVerifEventInfos
cmii7pysb004k8z1tts0npxfm_StoredVerifEventInfos_in_schema = {
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str,
}

# cmii7pysb004k8z1tts0npxfm 스키마 리스트
cmii7pysb004k8z1tts0npxfm_inSchema = [
    cmii7pysb004k8z1tts0npxfm_Authentication_in_schema,
    cmii7pysb004k8z1tts0npxfm_Capabilities_in_schema,
    cmii7pysb004k8z1tts0npxfm_DoorProfiles_in_schema,
    cmii7pysb004k8z1tts0npxfm_AccessUserInfos_in_schema,
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_in_schema,
    cmii7pysb004k8z1tts0npxfm_StoredVerifEventInfos_in_schema,
]

# cmii7pysb004k8z1tts0npxfm WebHook 스키마 리스트
cmii7pysb004k8z1tts0npxfm_webhook_OutSchema = [
    None,
    None,
    None,
    None,
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_out_schema,
    None,
]

# Authentication
cmii7lxbn002s8z1t1i9uudf0_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmii7lxbn002s8z1t1i9uudf0_Capabilities_in_schema = {}

# CameraProfiles
cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_in_schema = {}

# StreamURLs
cmii7lxbn002s8z1t1i9uudf0_StreamURLs_in_schema = {
    "camList": [{
    "camID": str,
    "streamProtocolType": str,
}],
}

# RealtimeVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_in_schema = {
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

# RealtimeVideoEventInfos WebHook OUT Schema
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_out_schema = {
    "code": str,
    "message": str,
}

# StoredVideoInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_in_schema = {
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
}

# ReplayURL
cmii7lxbn002s8z1t1i9uudf0_ReplayURL_in_schema = {
    "camList": [{
    "camID": str,
    "startTime": int,
    "endTime": int,
    "streamProtocolType": str,
}],
}

# StoredVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_in_schema = {
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
cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_in_schema = {
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
    OptionalKey("filterList"): [{
    OptionalKey("classFilter"): [str],
    OptionalKey("attributeFilter"): [str],
}],
}

# cmii7lxbn002s8z1t1i9uudf0 스키마 리스트
cmii7lxbn002s8z1t1i9uudf0_inSchema = [
    cmii7lxbn002s8z1t1i9uudf0_Authentication_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_Capabilities_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_StreamURLs_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_ReplayURL_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_in_schema,
]

# cmii7lxbn002s8z1t1i9uudf0 WebHook 스키마 리스트
cmii7lxbn002s8z1t1i9uudf0_webhook_OutSchema = [
    None,
    None,
    None,
    None,
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_out_schema,
    None,
    None,
    None,
    None,
]

