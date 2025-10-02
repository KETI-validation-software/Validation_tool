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

# spec_001 스키마 리스트
spec_001_inSchema = [
    Authentication_in_schema,
    Capabilities_in_schema,
    CameraProfiles_in_schema,
    StoredVideoInfos_in_schema,
    StreamURLs_in_schema,
    ReplayURL_in_schema,
    RealtimeVideoEventInfos_in_schema,
    StoredVideoEventInfos_in_schema,
    StoredObjectAnalyticsInfos_in_schema,
]

# Authentication
Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
Capabilities_in_schema = {}

# SensorDeviceProfiles
SensorDeviceProfiles_in_schema = {}

# RealtimeSensorData
RealtimeSensorData_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("duration"): int,
    OptionalKey("startTime"): int,
}

# RealtimeSensorEventInfos
RealtimeSensorEventInfos_in_schema = {
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

# StoredSensorEventInfos
StoredSensorEventInfos_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    "timePeriod": {
    "startTime": int,
    "endTime": int,
},
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str,
}

# SensorDeviceControl
SensorDeviceControl_in_schema = {
    "sensorDeviceID": str,
    OptionalKey("commandType"): str,
}

# spec_0011 스키마 리스트
spec_0011_inSchema = [
    Authentication_in_schema,
    Capabilities_in_schema,
    SensorDeviceProfiles_in_schema,
    RealtimeSensorData_in_schema,
    RealtimeSensorEventInfos_in_schema,
    StoredSensorEventInfos_in_schema,
    SensorDeviceControl_in_schema,
]

# 통합 스키마 리스트 (하위 호환성)
videoInSchema = spec_001_inSchema + spec_0011_inSchema

