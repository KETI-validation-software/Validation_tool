from json_checker import OptionalKey


# Authentication
cmii7wfuf006i8z1tcds6q69g_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# cmii7wfuf006i8z1tcds6q69g 스키마 리스트
cmii7wfuf006i8z1tcds6q69g_outSchema = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_out_schema,
]

# Authentication
cmii7w683006h8z1t7usnin5g_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# cmii7w683006h8z1t7usnin5g 스키마 리스트
cmii7w683006h8z1t7usnin5g_outSchema = [
    cmii7w683006h8z1t7usnin5g_Authentication_out_schema,
]

# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey("accessToken"): str,
}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_out_schema = {}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_schema = {}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_schema = {}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_schema = {}

# RealtimeVideoEventInfos WebHook IN Schema
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_schema = {}

# cmii7v8pr006g8z1tvo55a50u 스키마 리스트
cmii7v8pr006g8z1tvo55a50u_outSchema = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_out_schema,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_out_schema,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_schema,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_schema,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_schema,
]

# cmii7v8pr006g8z1tvo55a50u WebHook 스키마 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_inSchema = [
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_schema,
]

