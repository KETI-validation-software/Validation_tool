from json_checker import OptionalKey


# Authentication
cmg90br3n002qihleffuljnth_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmg90br3n002qihleffuljnth_Capabilities_in_schema = {}

# SensorDeviceProfiles
cmg90br3n002qihleffuljnth_SensorDeviceProfiles_in_schema = {}

# RealtimeSensorData
cmg90br3n002qihleffuljnth_RealtimeSensorData_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
    "duration": str,
    "transProtocol": str,
    "startTime": str,
}

# RealtimeSensorEventInfos
cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_in_schema = {
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
cmg90br3n002qihleffuljnth_StoredSensorEventInfos_in_schema = {
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

# SensorDeviceControl
cmg90br3n002qihleffuljnth_SensorDeviceControl_in_schema = {
    "sensorDeviceID": str,
    "commandType": str,
}

# cmg90br3n002qihleffuljnth 스키마 리스트
cmg90br3n002qihleffuljnth_inSchema = [
    cmg90br3n002qihleffuljnth_Authentication_in_schema,
    cmg90br3n002qihleffuljnth_Capabilities_in_schema,
    cmg90br3n002qihleffuljnth_SensorDeviceProfiles_in_schema,
    cmg90br3n002qihleffuljnth_RealtimeSensorData_in_schema,
    cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_in_schema,
    cmg90br3n002qihleffuljnth_StoredSensorEventInfos_in_schema,
    cmg90br3n002qihleffuljnth_SensorDeviceControl_in_schema,
]

# Authentication
cmg7edeo50013124xiux3gbkb_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmg7edeo50013124xiux3gbkb_Capabilities_in_schema = {
    "": str,
}

# DoorProfiles
cmg7edeo50013124xiux3gbkb_DoorProfiles_in_schema = {}

# AccessUserInfos
cmg7edeo50013124xiux3gbkb_AccessUserInfos_in_schema = {
    "": str,
}

# RealtimeVerifEventInfos
cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_in_schema = {
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
cmg7edeo50013124xiux3gbkb_StoredVerifEventInfos_in_schema = {
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
cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_in_schema = {
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
cmg7edeo50013124xiux3gbkb_DoorControl_in_schema = {
    "doorID": str,
    "commandType": str,
}

# cmg7edeo50013124xiux3gbkb 스키마 리스트
cmg7edeo50013124xiux3gbkb_inSchema = [
    cmg7edeo50013124xiux3gbkb_Authentication_in_schema,
    cmg7edeo50013124xiux3gbkb_Capabilities_in_schema,
    cmg7edeo50013124xiux3gbkb_DoorProfiles_in_schema,
    cmg7edeo50013124xiux3gbkb_AccessUserInfos_in_schema,
    cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_in_schema,
    cmg7edeo50013124xiux3gbkb_StoredVerifEventInfos_in_schema,
    cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_in_schema,
    cmg7edeo50013124xiux3gbkb_DoorControl_in_schema,
]

# Authentication
cmg7bve25000114cevhn5o3vr_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmg7bve25000114cevhn5o3vr_Capabilities_in_schema = {}

# CameraProfiles
cmg7bve25000114cevhn5o3vr_CameraProfiles_in_schema = {}

# StoredVideoInfos
cmg7bve25000114cevhn5o3vr_StoredVideoInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
}

# StreamURLs
cmg7bve25000114cevhn5o3vr_StreamURLs_in_schema = {
    "camList": [{
    "camID": str,
    "streamProtocolType": str,
}],
}

# ReplayURL
cmg7bve25000114cevhn5o3vr_ReplayURL_in_schema = {
    "camList": [{
    "camID": str,
    "startTime": float,
    "endTime": float,
    "streamProtocolType": str,
}],
}

# RealtimeVideoEventInfos
cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_in_schema = {
    "camList": [{
    "camID": str,
}],
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("eventFilter"): str,
    OptionalKey("classFilter"): str,
    OptionalKey("startTime"): float,
}


# StoredVideoEventInfos
cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_in_schema = {
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

# StoredObjectAnalyticsInfos
cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_in_schema = {
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
cmg7bve25000114cevhn5o3vr_PtzStatus_in_schema = {
    "camID": str,
}

# PtzContinuousMove
cmg7bve25000114cevhn5o3vr_PtzContinuousMove_in_schema = {
    "camID": str,
    "velocity": {
    OptionalKey("pan"): float,
    OptionalKey("tilt"): float,
    OptionalKey("zoom"): float,
},
    OptionalKey("timeOut"): float,
}

# PtzStop
cmg7bve25000114cevhn5o3vr_PtzStop_in_schema = {
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
    cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_in_schema,
    cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_in_schema,
    cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_in_schema,
    cmg7bve25000114cevhn5o3vr_PtzStatus_in_schema,
    cmg7bve25000114cevhn5o3vr_PtzContinuousMove_in_schema,
    cmg7bve25000114cevhn5o3vr_PtzStop_in_schema,
]

