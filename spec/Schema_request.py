from json_checker import OptionalKey


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
    "sensorDeviceList": [{
    "sensorDeviceID": str,
}],
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

