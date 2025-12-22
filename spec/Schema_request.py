from json_checker import OptionalKey


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
    "commandType": str,
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
    "doorName": str,
    "doorRelaySensor": str,
    "doorSensor": str,
}],
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
    OptionalKey("startTime"): int,
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
    None,
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

