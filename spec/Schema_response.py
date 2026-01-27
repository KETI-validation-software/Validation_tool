from json_checker import OptionalKey


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
    None,
    None,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_in_schema,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_in_schema,
]

