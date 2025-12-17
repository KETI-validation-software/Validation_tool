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
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_in_schema,
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
}],
    "duration": int,
    "transProtocol": {
    "transProtocolType": str,
    "transProtocolDesc": str,
},
    "startTime": int,
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
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_webhook_out_schema,
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

