from json_checker import OptionalKey


# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_in_schema = {
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
    OptionalKey("duration"): float,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("startTime"): float,
}

# RealtimeSensorEventInfos
cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_in_schema = {
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
cmg90br3n002qihleffuljnth_StoredSensorEventInfos_in_schema = {
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
cmg90br3n002qihleffuljnth_SensorDeviceControl_in_schema = {
    "sensorDeviceID": str,
    OptionalKey("commandType"): str,
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
cmg7edeo50013124xiux3gbkb_Capabilities_in_schema = {}

# DoorProfiles
cmg7edeo50013124xiux3gbkb_DoorProfiles_in_schema = {}

# AccessUserInfos
cmg7edeo50013124xiux3gbkb_AccessUserInfos_in_schema = {}

# RealtimeVerifEventInfos
cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("duration"): float,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("eventFilter"): str,
    OptionalKey("startTime"): float,
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
    OptionalKey("maxCount"): float,
    OptionalKey("eventFilter"): str,
}

# RealtimeDoorStatus
cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("duration"): float,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("startTime"): float,
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
cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_schema = {}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
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
    "startTime": float,
    "endTime": float,
    "streamProtocolType": str,
}],
}

# RealtimeVideoEventInfos
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_schema = {
    "camList": [{
    "camID": str,
}],
    OptionalKey("duration"): float,
    "transProtocol": {
    "transProtocolType": str,
    "transProtocolDesc": str,
},
    OptionalKey("eventFilter"): str,
    OptionalKey("classFilter"): str,
    OptionalKey("startTime"): float,
}

# RealtimeVideoEventInfos WebHook OUT Schema
cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_webhook_out_schema = {}

# StoredVideoEventInfos
cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
}

# RealtimeVideoEventInfos WebHook OUT Schema
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_webhook_out_schema = {}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_schema = {
    "timePeriod": {
    "startTime": float,
    "endTime": float,
},
    "camList": [{
    "camID": str,
}],
    OptionalKey("filterList"): [{
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
cmgvieyak001b6cd04cgaawmm_webhook_outSchema = [
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_webhook_out_schema,
]

# cmg7bve25000114cevhn5o3vr WebHook 스키마 리스트
cmg7bve25000114cevhn5o3vr_webhook_outSchema = [
    cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_webhook_out_schema,
]

