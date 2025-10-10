from json_checker import OptionalKey


# Authentication
Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
Capabilities_in_schema = {}

# DoorProfiles
DoorProfiles_in_schema = {}

# StoredVideoInfos
StoredVideoInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
}

# RealtimeSensorEventInfos
RealtimeSensorEventInfos_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    "duration": float,
    "transProtocol": [{
    "transProtocolType": str,
    "transProtocolDesc": str,
}],
    "eventFilter": str,
    "startTime": float,
}

# StoredSensorEventInfos
StoredSensorEventInfos_in_schema = {
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    "maxCount": str,
    "eventFilter": str,
}

# RealtimeDoorStatus
RealtimeDoorStatus_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    "duration": float,
    "transProtocol": {
    "transProtocolType": str,
    "transProtocolDesc": str,
},
    "startTime": float,
}

# cmg90br3n002qihleffuljnth 스키마 리스트
cmg90br3n002qihleffuljnth_inSchema = [
    Authentication_in_schema,
    Capabilities_in_schema,
    DoorProfiles_in_schema,
    StoredVideoInfos_in_schema,
    RealtimeSensorEventInfos_in_schema,
    StoredSensorEventInfos_in_schema,
    RealtimeDoorStatus_in_schema,
]

# Authentication
Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
Capabilities_in_schema = {
    "": str,
}

# DoorProfiles
DoorProfiles_in_schema = {}

# AccessUserInfos
AccessUserInfos_in_schema = {
    "": str,
}

# RealtimeVerifEventInfos
RealtimeVerifEventInfos_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    "duration": float,
    "transProtocol": {
    "transProtocolType": str,
    "transProtocolDesc": str,
},
    "eventFilter": str,
    "startTime": float,
}

# StoredVerifEventInfos
StoredVerifEventInfos_in_schema = {
    "timePeriod": [{
    "startTime": float,
    "endTime": float,
}],
    "doorList": [{
    "doorID": str,
}],
    "maxCount": float,
    "eventFilter": str,
}

# RealtimeDoorStatus
RealtimeDoorStatus_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    "duration": float,
    "transProtocol": {
    "transProtocolType": str,
    "transProtocolDesc": str,
},
    "startTime": float,
}

# DoorControl
DoorControl_in_schema = {
    "doorID": str,
    "commandType": str,
}

# cmg7edeo50013124xiux3gbkb 스키마 리스트
cmg7edeo50013124xiux3gbkb_inSchema = [
    Authentication_in_schema,
    Capabilities_in_schema,
    DoorProfiles_in_schema,
    AccessUserInfos_in_schema,
    RealtimeVerifEventInfos_in_schema,
    StoredVerifEventInfos_in_schema,
    RealtimeDoorStatus_in_schema,
    DoorControl_in_schema,
]

# Authentication
Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
Capabilities_in_schema = {
    "": str,
}

# DoorProfiles
DoorProfiles_in_schema = {}

# StoredVideoInfos
StoredVideoInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
}

# RealtimeVerifEventInfos
RealtimeVerifEventInfos_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    "duration": float,
    "transProtocol": {
    "transProtocolType": str,
    "transProtocolDesc": str,
},
    "eventFilter": str,
    "startTime": float,
}

# StoredVerifEventInfos
StoredVerifEventInfos_in_schema = {
    "timePeriod": [{
    "startTime": float,
    "endTime": float,
}],
    "doorList": [{
    "doorID": str,
}],
    "maxCount": float,
    "eventFilter": str,
}

# RealtimeDoorStatus
RealtimeDoorStatus_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    "duration": float,
    "transProtocol": {
    "transProtocolType": str,
    "transProtocolDesc": str,
},
    "startTime": float,
}

# DoorControl
DoorControl_in_schema = {
    "doorID": str,
    "commandType": str,
}

# StoredObjectAnalyticsInfos
StoredObjectAnalyticsInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
    "filterList": [{
    OptionalKey("classFilter"): [str],
    OptionalKey("attributeFilter"): [str],
}],
}

# PtzStatus
PtzStatus_in_schema = {
    "camID": str,
}

# PtzContinuousMove
PtzContinuousMove_in_schema = {
    "camID": str,
    "velocity": {
    OptionalKey("pan"): float,
    OptionalKey("tilt"): float,
    OptionalKey("zoom"): float,
},
    OptionalKey("timeOut"): float,
}

# PtzStop
PtzStop_in_schema = {
    "camID": str,
    OptionalKey("pan"): bool,
    OptionalKey("tilt"): bool,
    OptionalKey("zoom"): bool,
}

# cmg7bve25000114cevhn5o3vr 스키마 리스트
cmg7bve25000114cevhn5o3vr_inSchema = [
    Authentication_in_schema,
    Capabilities_in_schema,
    DoorProfiles_in_schema,
    StoredVideoInfos_in_schema,
    RealtimeVerifEventInfos_in_schema,
    StoredVerifEventInfos_in_schema,
    RealtimeDoorStatus_in_schema,
    DoorControl_in_schema,
    StoredObjectAnalyticsInfos_in_schema,
    PtzStatus_in_schema,
    PtzContinuousMove_in_schema,
    PtzStop_in_schema,
]

