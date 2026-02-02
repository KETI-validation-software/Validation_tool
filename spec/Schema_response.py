from json_checker import OptionalKey


# Authentication
cmii7wfuf006i8z1tcds6q69g_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmii7wfuf006i8z1tcds6q69g_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# SensorDeviceProfiles
cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_out_schema = {
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
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeSensorData WebHook IN Schema
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
    "measureTime": int,
    "sensorDeviceType": str,
    "sensorDeviceUnit": str,
    "sensorDeviceValue": str,
}],
}

# RealtimeSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeSensorEventInfos WebHook IN Schema
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_in_schema = {
    "sensorDeviceList": [{
    "sensorDeviceID": str,
    "eventName": str,
    "eventTime": int,
    OptionalKey("eventDesc"): str,
}],
}

# StoredSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList": [{
    "sensorDeviceID": str,
    "eventName": str,
    "eventTime": int,
    OptionalKey("eventDesc"): str,
}],
}

# cmii7wfuf006i8z1tcds6q69g 스키마 리스트
cmii7wfuf006i8z1tcds6q69g_outSchema = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_out_schema,
    cmii7wfuf006i8z1tcds6q69g_Capabilities_out_schema,
    cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_out_schema,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_out_schema,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_out_schema,
    cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_out_schema,
]

# cmii7wfuf006i8z1tcds6q69g WebHook 스키마 리스트
cmii7wfuf006i8z1tcds6q69g_webhook_inSchema = [
    None,
    None,
    None,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_in_schema,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_in_schema,
    None,
]

