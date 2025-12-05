# Authentication
cmii7wfuf006i8z1tcds6q69g_Authentication_in_constraints = {
  "userID": {
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "valueType": "preset",
    "required": True
  }
}

# cmii7wfuf006i8z1tcds6q69g 검증 리스트
cmii7wfuf006i8z1tcds6q69g_inConstraints = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_in_constraints,
]

# Authentication
cmii7w683006h8z1t7usnin5g_Authentication_in_constraints = {
  "userID": {
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "valueType": "preset",
    "required": True
  }
}

# cmii7w683006h8z1t7usnin5g 검증 리스트
cmii7w683006h8z1t7usnin5g_inConstraints = [
    cmii7w683006h8z1t7usnin5g_Authentication_in_constraints,
]

# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_in_constraints = {
  "userID": {
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_in_constraints = {}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_constraints = {}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_constraints = {
  "camList": {
    "valueType": "preset",
    "required": True,
    "arrayElementType": "object"
  },
  "streamProtocolType": {
    "valueType": "preset",
    "required": True
  }
}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_constraints = {
  "camList": {
    "valueType": "preset",
    "required": True,
    "arrayElementType": "object"
  },
  "duration": {
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "valueType": "preset",
    "required": True
  },
  "eventFilter": {
    "valueType": "preset",
    "required": False
  },
  "classFilter": {
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "valueType": "preset",
    "required": False
  }
}

# RealtimeVideoEventInfos WebHook OUT Constraints
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints = {}

# cmii7v8pr006g8z1tvo55a50u 검증 리스트
cmii7v8pr006g8z1tvo55a50u_inConstraints = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_constraints,
]

# cmii7v8pr006g8z1tvo55a50u WebHook Constraints 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_outConstraints = [
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints,
]

