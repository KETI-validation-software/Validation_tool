from json_checker import OptionalKey


# Authentication
cmsiluan100bvrc0qiag2o6bg_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmsiluan100bvrc0qiag2o6bg_Capabilities_in_schema = {}

# CameraProfiles
cmsiluan100bvrc0qiag2o6bg_CameraProfiles_in_schema = {}

# StoredVideoInfos
cmsiluan100bvrc0qiag2o6bg_StoredVideoInfos_in_schema = {
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
}

# ReplayURL
cmsiluan100bvrc0qiag2o6bg_ReplayURL_in_schema = {
    "camList": [{
    "camID": str,
    "startTime": str,
    "endTime": str,
    "streamProtocolType": str,
}],
}

# StoredVideoEventInfos
cmsiluan100bvrc0qiag2o6bg_StoredVideoEventInfos_in_schema = {
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str,
    OptionalKey("classFilter"): str,
}

# StoredObjectAnalyticsInfos
cmsiluan100bvrc0qiag2o6bg_StoredObjectAnalyticsInfos_in_schema = {
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
    OptionalKey("camList"): [{
    "camID": str,
}],
    OptionalKey("filterList"): [{
    OptionalKey("classFilter"): [str],
    OptionalKey("attributeFilter"): [str],
}],
}

# cmsiluan100bvrc0qiag2o6bg 스키마 리스트
cmsiluan100bvrc0qiag2o6bg_inSchema = [
    cmsiluan100bvrc0qiag2o6bg_Authentication_in_schema,
    cmsiluan100bvrc0qiag2o6bg_Capabilities_in_schema,
    cmsiluan100bvrc0qiag2o6bg_CameraProfiles_in_schema,
    cmsiluan100bvrc0qiag2o6bg_StoredVideoInfos_in_schema,
    cmsiluan100bvrc0qiag2o6bg_ReplayURL_in_schema,
    cmsiluan100bvrc0qiag2o6bg_StoredVideoEventInfos_in_schema,
    cmsiluan100bvrc0qiag2o6bg_StoredObjectAnalyticsInfos_in_schema,
]

# Authentication
cmsmgmbhm01ebrc0qs9uiok8n_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmsmgmbhm01ebrc0qs9uiok8n_Capabilities_in_schema = {}

# DoorProfiles
cmsmgmbhm01ebrc0qs9uiok8n_DoorProfiles_in_schema = {}

# AccessUserInfos
cmsmgmbhm01ebrc0qs9uiok8n_AccessUserInfos_in_schema = {}

# StoredVerifEventInfos
cmsmgmbhm01ebrc0qs9uiok8n_StoredVerifEventInfos_in_schema = {
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str,
}

# cmsmgmbhm01ebrc0qs9uiok8n 스키마 리스트
cmsmgmbhm01ebrc0qs9uiok8n_inSchema = [
    cmsmgmbhm01ebrc0qs9uiok8n_Authentication_in_schema,
    cmsmgmbhm01ebrc0qs9uiok8n_Capabilities_in_schema,
    cmsmgmbhm01ebrc0qs9uiok8n_DoorProfiles_in_schema,
    cmsmgmbhm01ebrc0qs9uiok8n_AccessUserInfos_in_schema,
    cmsmgmbhm01ebrc0qs9uiok8n_StoredVerifEventInfos_in_schema,
]

# Authentication
cmsmh2go501w6rc0q4s8zyqdp_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmsmh2go501w6rc0q4s8zyqdp_Capabilities_in_schema = {}

# SensorDeviceProfiles
cmsmh2go501w6rc0q4s8zyqdp_SensorDeviceProfiles_in_schema = {}

# StoredSensorEventInfos
cmsmh2go501w6rc0q4s8zyqdp_StoredSensorEventInfos_in_schema = {
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
    "sensorDeviceList": [{}],
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str,
}

# cmsmh2go501w6rc0q4s8zyqdp 스키마 리스트
cmsmh2go501w6rc0q4s8zyqdp_inSchema = [
    cmsmh2go501w6rc0q4s8zyqdp_Authentication_in_schema,
    cmsmh2go501w6rc0q4s8zyqdp_Capabilities_in_schema,
    cmsmh2go501w6rc0q4s8zyqdp_SensorDeviceProfiles_in_schema,
    cmsmh2go501w6rc0q4s8zyqdp_StoredSensorEventInfos_in_schema,
]

# Authentication
cmiqr201z00i8ie8fitdg5t1b_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmiqr201z00i8ie8fitdg5t1b_Capabilities_in_schema = {}

# SensorDeviceProfiles
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_in_schema = {}

# SensorDeviceControl
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_in_schema = {
    "sensorDeviceID": str,
    OptionalKey("commandType"): str,
}

# SensorDeviceControl2
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_in_schema = {
    "sensorDeviceID": str,
    "commandType": str,
}

# cmiqr201z00i8ie8fitdg5t1b 스키마 리스트
cmiqr201z00i8ie8fitdg5t1b_inSchema = [
    cmiqr201z00i8ie8fitdg5t1b_Authentication_in_schema,
    cmiqr201z00i8ie8fitdg5t1b_Capabilities_in_schema,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_in_schema,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_in_schema,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_in_schema,
]

# Authentication
cmiqr1acx00i5ie8fi022t1hp_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmiqr1acx00i5ie8fi022t1hp_Capabilities_in_schema = {}

# DoorProfiles
cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_in_schema = {}

# RealtimeDoorStatus
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("duration"): int,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("startTime"): str,
}

# RealtimeDoorStatus WebHook OUT Schema
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_webhook_out_schema = {
    "code": str,
    "message": str,
}

# DoorControl
cmiqr1acx00i5ie8fi022t1hp_DoorControl_in_schema = {
    "doorID": str,
    "commandType": str,
}

# RealtimeDoorStatus2
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_in_schema = {
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("duration"): int,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("startTime"): str,
}

# RealtimeDoorStatus2 WebHook OUT Schema
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_webhook_out_schema = {
    "code": str,
    "message": str,
}

# cmiqr1acx00i5ie8fi022t1hp 스키마 리스트
cmiqr1acx00i5ie8fi022t1hp_inSchema = [
    cmiqr1acx00i5ie8fi022t1hp_Authentication_in_schema,
    cmiqr1acx00i5ie8fi022t1hp_Capabilities_in_schema,
    cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_in_schema,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_in_schema,
    cmiqr1acx00i5ie8fi022t1hp_DoorControl_in_schema,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_in_schema,
]

# cmiqr1acx00i5ie8fi022t1hp WebHook 스키마 리스트
cmiqr1acx00i5ie8fi022t1hp_webhook_OutSchema = [
    None,
    None,
    None,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_webhook_out_schema,
    None,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_webhook_out_schema,
]

# Authentication
cmiqqzrjz00i3ie8figf79cur_Authentication_in_schema = {
    "userID": str,
    "userPW": str,
}

# Capabilities
cmiqqzrjz00i3ie8figf79cur_Capabilities_in_schema = {}

# CameraProfiles
cmiqqzrjz00i3ie8figf79cur_CameraProfiles_in_schema = {}

# PtzStatus
cmiqqzrjz00i3ie8figf79cur_PtzStatus_in_schema = {
    "camID": str,
}

# PtzContinuousMove
cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_in_schema = {
    "camID": str,
    "velocity": {
    OptionalKey("pan"): int,
    OptionalKey("tilt"): int,
    OptionalKey("zoom"): int,
},
    OptionalKey("timeOut"): int,
}

# PtzStop
cmiqqzrjz00i3ie8figf79cur_PtzStop_in_schema = {
    "camID": str,
    OptionalKey("pan"): bool,
    OptionalKey("tilt"): bool,
    OptionalKey("zoom"): bool,
}

# cmiqqzrjz00i3ie8figf79cur 스키마 리스트
cmiqqzrjz00i3ie8figf79cur_inSchema = [
    cmiqqzrjz00i3ie8figf79cur_Authentication_in_schema,
    cmiqqzrjz00i3ie8figf79cur_Capabilities_in_schema,
    cmiqqzrjz00i3ie8figf79cur_CameraProfiles_in_schema,
    cmiqqzrjz00i3ie8figf79cur_PtzStatus_in_schema,
    cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_in_schema,
    cmiqqzrjz00i3ie8figf79cur_PtzStop_in_schema,
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
    OptionalKey("startTime"): str,
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
    OptionalKey("startTime"): str,
}

# RealtimeSensorEventInfos WebHook OUT Schema
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_out_schema = {
    "code": str,
    "message": str,
}

# cmii7shen005i8z1tagevx4qh 스키마 리스트
cmii7shen005i8z1tagevx4qh_inSchema = [
    cmii7shen005i8z1tagevx4qh_Authentication_in_schema,
    cmii7shen005i8z1tagevx4qh_Capabilities_in_schema,
    cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_in_schema,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_in_schema,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_in_schema,
]

# cmii7shen005i8z1tagevx4qh WebHook 스키마 리스트
cmii7shen005i8z1tagevx4qh_webhook_OutSchema = [
    None,
    None,
    None,
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
    "doorList": [{
    "doorID": str,
}],
    OptionalKey("duration"): int,
    "transProtocol": {
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
},
    OptionalKey("eventFilter"): str,
    OptionalKey("startTime"): str,
}

# RealtimeVerifEventInfos WebHook OUT Schema
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_out_schema = {
    "code": str,
    "message": str,
}

# cmii7pysb004k8z1tts0npxfm 스키마 리스트
cmii7pysb004k8z1tts0npxfm_inSchema = [
    cmii7pysb004k8z1tts0npxfm_Authentication_in_schema,
    cmii7pysb004k8z1tts0npxfm_Capabilities_in_schema,
    cmii7pysb004k8z1tts0npxfm_DoorProfiles_in_schema,
    cmii7pysb004k8z1tts0npxfm_AccessUserInfos_in_schema,
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_in_schema,
]

# cmii7pysb004k8z1tts0npxfm WebHook 스키마 리스트
cmii7pysb004k8z1tts0npxfm_webhook_OutSchema = [
    None,
    None,
    None,
    None,
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
    OptionalKey("startTime"): str,
}

# RealtimeVideoEventInfos WebHook OUT Schema
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_out_schema = {
    "code": str,
    "message": str,
}

# cmii7lxbn002s8z1t1i9uudf0 스키마 리스트
cmii7lxbn002s8z1t1i9uudf0_inSchema = [
    cmii7lxbn002s8z1t1i9uudf0_Authentication_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_Capabilities_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_StreamURLs_in_schema,
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_in_schema,
]

# cmii7lxbn002s8z1t1i9uudf0 WebHook 스키마 리스트
cmii7lxbn002s8z1t1i9uudf0_webhook_OutSchema = [
    None,
    None,
    None,
    None,
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_out_schema,
]

