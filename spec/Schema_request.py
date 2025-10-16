from json_checker import OptionalKey


# Authentication
cmgatbdp000bqihlexmywusvq_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmgatbdp000bqihlexmywusvq_Capabilities_in_schema = {}

# SensorDeviceProfiles
cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_in_schema = {}

# RealtimeSensorData
cmgatbdp000bqihlexmywusvq_RealtimeSensorData_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    OptionalKey("duration"): float,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("startTime"): float,
}

# RealtimeSensorEventInfos
cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    OptionalKey("duration"): float,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("eventFilter"): str,
    OptionalKey("startTime"): float,
}

# StoredSensorEventInfos
cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    OptionalKey("maxCount"): float,
    OptionalKey("eventFilter"): str,
}

# SensorDeviceControl
cmgatbdp000bqihlexmywusvq_SensorDeviceControl_in_schema = {
    "sensorDeviceID": str,
    OptionalKey("commandType"): str,
}

# cmgatbdp000bqihlexmywusvq 스키마 리스트
cmgatbdp000bqihlexmywusvq_inSchema = [
    cmgatbdp000bqihlexmywusvq_Authentication_in_schema,
    cmgatbdp000bqihlexmywusvq_Capabilities_in_schema,
    cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_in_schema,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorData_in_schema,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_in_schema,
    cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_in_schema,
    cmgatbdp000bqihlexmywusvq_SensorDeviceControl_in_schema,
]

# Authentication
cmgasj98w009aihlezm0fe6cs_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmgasj98w009aihlezm0fe6cs_Capabilities_in_schema = {}

# DoorProfiles
cmgasj98w009aihlezm0fe6cs_DoorProfiles_in_schema = {}

# AccessUserInfos
cmgasj98w009aihlezm0fe6cs_AccessUserInfos_in_schema = {}

# RealtimeVerifEventInfos
cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("duration"): float,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("eventFilter"): [str],
    OptionalKey("startTime"): float,
}

# StoredVerifEventInfos
cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
    "doorList": [{
    "doorID": str,
}],
    "maxCount": float,
    "eventFilter": str,
}

# RealtimeDoorStatus
cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("duration"): float,
    "transProtocol": {
    "transProtocolType": str,
    "transProtocolDesc": str,
},
    OptionalKey("startTime"): float,
}

# DoorControl
cmgasj98w009aihlezm0fe6cs_DoorControl_in_schema = {
    "doorID": str,
    "commandType": str,
}

# cmgasj98w009aihlezm0fe6cs 스키마 리스트
cmgasj98w009aihlezm0fe6cs_inSchema = [
    cmgasj98w009aihlezm0fe6cs_Authentication_in_schema,
    cmgasj98w009aihlezm0fe6cs_Capabilities_in_schema,
    cmgasj98w009aihlezm0fe6cs_DoorProfiles_in_schema,
    cmgasj98w009aihlezm0fe6cs_AccessUserInfos_in_schema,
    cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_in_schema,
    cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_in_schema,
    cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_in_schema,
    cmgasj98w009aihlezm0fe6cs_DoorControl_in_schema,
]

# Authentication
cmga0l5mh005dihlet5fcoj0o_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmga0l5mh005dihlet5fcoj0o_Capabilities_in_schema = {}

# CameraProfiles
cmga0l5mh005dihlet5fcoj0o_CameraProfiles_in_schema = {}

# StoredVideoInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_in_schema = {
    "timePeriod": [{
    "startTime": float,
    "endTime": float,
}],
    OptionalKey("camList"): [{
    "camID": str,
}],
}

# StreamURLs
cmga0l5mh005dihlet5fcoj0o_StreamURLs_in_schema = {
    "camList": [{
    "camID": str,
    "streamProtocolType": str,
}],
}

# ReplayURL
cmga0l5mh005dihlet5fcoj0o_ReplayURL_in_schema = {
    "camList": [{
    "camID": str,
    "startTime": float,
    "endTime": float,
    "streamProtocolType": str,
}],
}


# StoredVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
    OptionalKey("maxCount"): float,
    OptionalKey("eventFilter"): str,
    OptionalKey("classFilter"): str,
}

# RealtimeVideoEventInfos
cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_in_schema = {
    "camList": [{
    "camID": str,
}],
    OptionalKey("duration"): str,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("eventFilter"): str,
    OptionalKey("classFilter"): str,
    OptionalKey("startTime"): float,
}

# StoredObjectAnalyticsInfos
cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
    OptionalKey("filterList"): [{
    OptionalKey("classFilter"): str,
    OptionalKey("attributeFilter"): str,
}],
}

# PtzStatus
cmga0l5mh005dihlet5fcoj0o_PtzStatus_in_schema = {
    "camID": str,
}

# PtzContinuousMove
cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_in_schema = {
    "camID": str,
    "velocity": {
    OptionalKey("pan"): float,
    OptionalKey("tilt"): float,
    OptionalKey("zoom"): float,
},
    OptionalKey("timeOut"): float,
}

# PtzStop
cmga0l5mh005dihlet5fcoj0o_PtzStop_in_schema = {
    "camID": str,
    OptionalKey("pan"): bool,
    OptionalKey("tilt"): bool,
    OptionalKey("zoom"): bool,
}


# cmg7bve25000114cevhn5o3vr 스키마 리스트
cmg7bve25000114cevhn5o3vr_inSchema = [
    cmg7bve25000114cevhn5o3vr_Authentication_in_schema,
    cmg7bve25000114cevhn5o3vr_Capabilities_in_schema,
    cmg7bve25000114cevhn5o3vr_CameraProfiles_in_schema,
    cmg7bve25000114cevhn5o3vr_StoredVideoInfos_in_schema,
    cmg7bve25000114cevhn5o3vr_StreamURLs_in_schema,
    cmg7bve25000114cevhn5o3vr_ReplayURL_in_schema,
    cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_in_schema,
    cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_in_schema,
    cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_in_schema,
    cmg7bve25000114cevhn5o3vr_PtzStatus_in_schema,
    cmg7bve25000114cevhn5o3vr_PtzContinuousMove_in_schema,
    cmg7bve25000114cevhn5o3vr_PtzStop_in_schema,

]

