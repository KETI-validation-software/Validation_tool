from json_checker import OptionalKey


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
    "sensorDeviceList": [{}],
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
    "sensorDeviceList": [{}],
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
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_out_schema,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_out_schema,
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
    "doorList": [{}],
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
    "doorList": [{}],
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
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_out_schema,
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
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_out_schema,
]

