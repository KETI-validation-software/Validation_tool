from json_checker import OptionalKey


# Authentication
cmtwtwdiz02o1245txoqxczwz_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmtwtwdiz02o1245txoqxczwz_Capabilities_out_schema = {
    "code": str,
    "message": str,
}

# DoorProfiles
cmtwtwdiz02o1245txoqxczwz_DoorProfiles_out_schema = {
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
cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "doorID": str,
    "doorName": str,
    "doorRelaySensor": str,
    "doorSensor": str,
}],
}

# DoorControl
cmtwtwdiz02o1245txoqxczwz_DoorControl_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeDoorStatus2
cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus2_out_schema = {
    "code": str,
    "message": str,
}

# cmtwtwdiz02o1245txoqxczwz 스키마 리스트
cmtwtwdiz02o1245txoqxczwz_outSchema = [
    cmtwtwdiz02o1245txoqxczwz_Authentication_out_schema,
    cmtwtwdiz02o1245txoqxczwz_Capabilities_out_schema,
    cmtwtwdiz02o1245txoqxczwz_DoorProfiles_out_schema,
    cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus_out_schema,
    cmtwtwdiz02o1245txoqxczwz_DoorControl_out_schema,
    cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus2_out_schema,
]

# Authentication
cmtwtvuyb02i1245t2su90084_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmtwtvuyb02i1245t2su90084_Capabilities_out_schema = {
    "code": str,
    "message": str,
}

# DoorProfiles
cmtwtvuyb02i1245t2su90084_DoorProfiles_out_schema = {
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

# AccessUserInfos
cmtwtvuyb02i1245t2su90084_AccessUserInfos_out_schema = {
    "code": str,
    "message": str,
    "userList": [{
    "userID": str,
    "userName": str,
    OptionalKey("userDesc"): str,
    "doorList": [{
    "doorID": str,
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
}],
}],
}

# StoredVerifEventInfos
cmtwtvuyb02i1245t2su90084_StoredVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# cmtwtvuyb02i1245t2su90084 스키마 리스트
cmtwtvuyb02i1245t2su90084_outSchema = [
    cmtwtvuyb02i1245t2su90084_Authentication_out_schema,
    cmtwtvuyb02i1245t2su90084_Capabilities_out_schema,
    cmtwtvuyb02i1245t2su90084_DoorProfiles_out_schema,
    cmtwtvuyb02i1245t2su90084_AccessUserInfos_out_schema,
    cmtwtvuyb02i1245t2su90084_StoredVerifEventInfos_out_schema,
]

# Authentication
cmtwtvjfm02br245tbzi9gej7_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmtwtvjfm02br245tbzi9gej7_Capabilities_out_schema = {
    "code": str,
    "message": str,
}

# DoorProfiles
cmtwtvjfm02br245tbzi9gej7_DoorProfiles_out_schema = {
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

# AccessUserInfos
cmtwtvjfm02br245tbzi9gej7_AccessUserInfos_out_schema = {
    "code": str,
    "message": str,
    "userList": [{
    "userID": str,
    "userName": str,
    OptionalKey("userDesc"): str,
    "doorList": [{
    "doorID": str,
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
}],
}],
}

# RealtimeVerifEventInfos
cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeVerifEventInfos WebHook IN Schema
cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_webhook_in_schema = {
    "doorList": [{
    "eventTime": str,
    "doorID": str,
    OptionalKey("userID"): str,
    OptionalKey("bioAuthTypeList"): [str],
    OptionalKey("otherAuthTypeList"): [str],
    "eventName": str,
    OptionalKey("eventDesc"): str,
}],
}

# cmtwtvjfm02br245tbzi9gej7 스키마 리스트
cmtwtvjfm02br245tbzi9gej7_outSchema = [
    cmtwtvjfm02br245tbzi9gej7_Authentication_out_schema,
    cmtwtvjfm02br245tbzi9gej7_Capabilities_out_schema,
    cmtwtvjfm02br245tbzi9gej7_DoorProfiles_out_schema,
    cmtwtvjfm02br245tbzi9gej7_AccessUserInfos_out_schema,
    cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_out_schema,
]

# cmtwtvjfm02br245tbzi9gej7 WebHook 스키마 리스트
cmtwtvjfm02br245tbzi9gej7_webhook_inSchema = [
    None,
    None,
    None,
    None,
    cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_webhook_in_schema,
]

# Authentication
cmtwil1oo00ztt4ht7y9se1ur_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmtwil1oo00ztt4ht7y9se1ur_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# DoorProfiles
cmtwil1oo00ztt4ht7y9se1ur_DoorProfiles_out_schema = {
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
cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "doorID": str,
    "doorName": str,
    "doorRelaySensor": str,
    "doorSensor": str,
}],
}

# DoorControl
cmtwil1oo00ztt4ht7y9se1ur_DoorControl_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeDoorStatus2
cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus2_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "doorID": str,
    "doorName": str,
    OptionalKey("doorRelaySensor"): str,
    OptionalKey("doorSensor"): str,
}],
}

# cmtwil1oo00ztt4ht7y9se1ur 스키마 리스트
cmtwil1oo00ztt4ht7y9se1ur_outSchema = [
    cmtwil1oo00ztt4ht7y9se1ur_Authentication_out_schema,
    cmtwil1oo00ztt4ht7y9se1ur_Capabilities_out_schema,
    cmtwil1oo00ztt4ht7y9se1ur_DoorProfiles_out_schema,
    cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus_out_schema,
    cmtwil1oo00ztt4ht7y9se1ur_DoorControl_out_schema,
    cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus2_out_schema,
]

# Authentication
cmtwfeiw4003dt4htizadqzzr_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmtwfeiw4003dt4htizadqzzr_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# DoorProfiles
cmtwfeiw4003dt4htizadqzzr_DoorProfiles_out_schema = {
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

# AccessUserInfos
cmtwfeiw4003dt4htizadqzzr_AccessUserInfos_out_schema = {
    "code": str,
    "message": str,
    "userList": [{
    "userID": str,
    "userName": str,
    OptionalKey("userDesc"): str,
    "doorList": [{
    "doorID": str,
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
}],
}],
}

# StoredVerifEventInfos
cmtwfeiw4003dt4htizadqzzr_StoredVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
    "doorList": [{
    "eventTime": str,
    "doorID": str,
    OptionalKey("userID"): str,
    OptionalKey("bioAuthTypeList"): [str],
    OptionalKey("otherAuthTypeList"): [str],
    "eventName": str,
    "eventDesc": str,
}],
}

# cmtwfeiw4003dt4htizadqzzr 스키마 리스트
cmtwfeiw4003dt4htizadqzzr_outSchema = [
    cmtwfeiw4003dt4htizadqzzr_Authentication_out_schema,
    cmtwfeiw4003dt4htizadqzzr_Capabilities_out_schema,
    cmtwfeiw4003dt4htizadqzzr_DoorProfiles_out_schema,
    cmtwfeiw4003dt4htizadqzzr_AccessUserInfos_out_schema,
    cmtwfeiw4003dt4htizadqzzr_StoredVerifEventInfos_out_schema,
]

# Authentication
cmtw8wcts00o1126muckytfg2_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmtw8wcts00o1126muckytfg2_Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport": [{
    "transProtocolType": str,
    OptionalKey("transProtocolDesc"): str,
}],
}

# DoorProfiles
cmtw8wcts00o1126muckytfg2_DoorProfiles_out_schema = {
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

# AccessUserInfos
cmtw8wcts00o1126muckytfg2_AccessUserInfos_out_schema = {
    "code": str,
    "message": str,
    "userList": [{
    "userID": str,
    "userName": str,
    OptionalKey("userDesc"): str,
    "doorList": [{
    "doorID": str,
    "timePeriod": {
    "startTime": str,
    "endTime": str,
},
}],
}],
}

# RealtimeVerifEventInfos
cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
}

# RealtimeVerifEventInfos WebHook IN Schema
cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_webhook_in_schema = {
    "doorList": [{
    "eventTime": str,
    "doorID": str,
    OptionalKey("userID"): str,
    OptionalKey("bioAuthTypeList"): [str],
    OptionalKey("otherAuthTypeList"): [str],
    "eventName": str,
    OptionalKey("eventDesc"): str,
}],
}

# cmtw8wcts00o1126muckytfg2 스키마 리스트
cmtw8wcts00o1126muckytfg2_outSchema = [
    cmtw8wcts00o1126muckytfg2_Authentication_out_schema,
    cmtw8wcts00o1126muckytfg2_Capabilities_out_schema,
    cmtw8wcts00o1126muckytfg2_DoorProfiles_out_schema,
    cmtw8wcts00o1126muckytfg2_AccessUserInfos_out_schema,
    cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_out_schema,
]

# cmtw8wcts00o1126muckytfg2 WebHook 스키마 리스트
cmtw8wcts00o1126muckytfg2_webhook_inSchema = [
    None,
    None,
    None,
    None,
    cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_webhook_in_schema,
]

