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

