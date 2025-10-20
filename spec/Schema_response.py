from json_checker import OptionalKey


# Authentication
cmgatbdp000bqihlexmywusvq_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmgatbdp000bqihlexmywusvq_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# SensorDeviceProfiles
cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_out_schema = {
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
cmgatbdp000bqihlexmywusvq_RealtimeSensorData_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList": [{
    "sensorDeviceID": str,
    "measureTime": float,
    "sensorDeviceType": str,
    "sensorDeviceUnit": str,
    "sensorDeviceValue": str,
}],
}

# RealtimeSensorEventInfos
cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList": [{
    "sensorDeviceID": str,
    "eventName": str,
    "eventTime": float,
    OptionalKey("eventDesc"): str,
}],
}

# StoredSensorEventInfos
cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList": [{
    "sensorDeviceID": str,
    "eventName": str,
    "eventTime": float,
    OptionalKey("eventDesc"): str,
}],
}

# SensorDeviceControl
cmgatbdp000bqihlexmywusvq_SensorDeviceControl_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceID": str,
    "sensorDeviceStatus": str,
}

# cmgatbdp000bqihlexmywusvq 스키마 리스트
cmgatbdp000bqihlexmywusvq_outSchema = [
    cmgatbdp000bqihlexmywusvq_Authentication_out_schema,
    cmgatbdp000bqihlexmywusvq_Capabilities_out_schema,
    cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_out_schema,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorData_out_schema,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_out_schema,
    cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_out_schema,
    cmgatbdp000bqihlexmywusvq_SensorDeviceControl_out_schema,
]

# Authentication
cmgasj98w009aihlezm0fe6cs_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmgasj98w009aihlezm0fe6cs_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    "transProtocolDesc": str,
}],
}

# DoorProfiles
cmgasj98w009aihlezm0fe6cs_DoorProfiles_out_schema = {
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
cmgasj98w009aihlezm0fe6cs_AccessUserInfos_out_schema = {
    "code": str,
    "message": str,
    "userList": [{
    "userID": str,
    "userName": str,
    OptionalKey("userDesc"): str,
    "doorList": [{
    "doorID": str,
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
}],
}],
}

# RealtimeVerifEventInfos
cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "eventTime": float,
    "doorID": str,
    OptionalKey("userID"): str,
    OptionalKey("bioAuthTypeList"): [str],
    OptionalKey("otherAuthTypeList"): [str],
    "eventName": str,
    OptionalKey("eventDesc"): str,
}],
}

# StoredVerifEventInfos
cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "eventTime": float,
    "doorID": str,
    OptionalKey("userID"): str,
    OptionalKey("bioAuthTypeList"): [str],
    OptionalKey("otherAuthTypeList"): [str],
    "eventName": str,
    OptionalKey("eventDesc"): str,
}],
}

# RealtimeDoorStatus
cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "doorID": str,
    "doorName": str,
    OptionalKey("doorRelaySensor"): str,
    OptionalKey("doorSensor"): str,
}],
}

# DoorControl
cmgasj98w009aihlezm0fe6cs_DoorControl_out_schema = {
    "code": str,
    "message": str,
}

# cmgasj98w009aihlezm0fe6cs 스키마 리스트
cmgasj98w009aihlezm0fe6cs_outSchema = [
    cmgasj98w009aihlezm0fe6cs_Authentication_out_schema,
    cmgasj98w009aihlezm0fe6cs_Capabilities_out_schema,
    cmgasj98w009aihlezm0fe6cs_DoorProfiles_out_schema,
    cmgasj98w009aihlezm0fe6cs_AccessUserInfos_out_schema,
    cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_out_schema,
    cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_out_schema,
    cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_out_schema,
    cmgasj98w009aihlezm0fe6cs_DoorControl_out_schema,
]

# Authentication
cmga0l5mh005dihlet5fcoj0o_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmga0l5mh005dihlet5fcoj0o_Capabilities_out_schema = {
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
cmga0l5mh005dihlet5fcoj0o_CameraProfiles_out_schema = {
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
cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "timeList": [{
    "startTime": float,
    OptionalKey("endTime"): float,
}],
}],
}

# StreamURLs
cmga0l5mh005dihlet5fcoj0o_StreamURLs_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    OptionalKey("accessID"): str,
    OptionalKey("accessPW"): str,
    "camURL": str,
    OptionalKey("videoInfo"): {
    OptionalKey("resolution"): str,
    OptionalKey("fps"): float,
    OptionalKey("videoCodec"): str,
    OptionalKey("audioCodec"): str,
},
}],
}

# ReplayURL
cmga0l5mh005dihlet5fcoj0o_ReplayURL_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    OptionalKey("accessID"): str,
    OptionalKey("accessPW"): str,
    "startTime": float,
    OptionalKey("endTime"): float,
    "camURL": str,
    OptionalKey("videoInfo"): {
    OptionalKey("resolution"): str,
    OptionalKey("fps"): float,
    OptionalKey("videoCodec"): str,
    OptionalKey("audioCodec"): str,
},
}],
}

# RealtimeVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_RealtimeVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": float,
    OptionalKey("endTime"): float,
    OptionalKey("eventDesc"): str,
}],
}

# StoredVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
    "camList": [{
    "camID": str,
    "eventUUID": str,
    "eventName": str,
    "startTime": float,
    OptionalKey("endTime"): float,
    OptionalKey("eventDesc"): str,
}],
}

# StoredObjectAnalyticsInfos
cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_out_schema = {
    "code": str,
    "message": str,
    OptionalKey("camList"): [{
    "camID": str,
    "analyticsTime": float,
    "anlayticsResultList": [{
    "anayticsID": str,
    "analyticsClass": str,
    OptionalKey("analyticsAttribute"): [str],
    OptionalKey("analyticsConfidence"): float,
    OptionalKey("analyticsBoundingBox"): {
    "left": float,
    "top": float,
    "right": float,
    "bottom": float,
},
    OptionalKey("analyticsDesc"): str,
}],
}],
}

# PtzStatus
cmga0l5mh005dihlet5fcoj0o_PtzStatus_out_schema = {
    "code": str,
    "message": str,
    OptionalKey("position"): {
    OptionalKey("pan"): float,
    OptionalKey("tilt"): float,
    OptionalKey("zoom"): float,
},
    "moveStatus": {
    OptionalKey("pan"): str,
    OptionalKey("tilt"): str,
    OptionalKey("zoom"): str,
},
}

# PtzContinuousMove
cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_out_schema = {
    "code": str,
    "message": str,
}

# PtzStop
cmga0l5mh005dihlet5fcoj0o_PtzStop_out_schema = {
    "code": str,
    "message": str,
}

# cmga0l5mh005dihlet5fcoj0o 스키마 리스트
cmga0l5mh005dihlet5fcoj0o_outSchema = [
    cmga0l5mh005dihlet5fcoj0o_Authentication_out_schema,
    cmga0l5mh005dihlet5fcoj0o_Capabilities_out_schema,
    cmga0l5mh005dihlet5fcoj0o_CameraProfiles_out_schema,
    cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_out_schema,
    cmga0l5mh005dihlet5fcoj0o_StreamURLs_out_schema,
    cmga0l5mh005dihlet5fcoj0o_ReplayURL_out_schema,
    cmga0l5mh005dihlet5fcoj0o_RealtimeVideoEventInfos_out_schema,
    cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_out_schema,
    cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_out_schema,
    cmga0l5mh005dihlet5fcoj0o_PtzStatus_out_schema,
    cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_out_schema,
    cmga0l5mh005dihlet5fcoj0o_PtzStop_out_schema,
]

