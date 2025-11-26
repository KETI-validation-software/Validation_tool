# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_in_validation = {
  "userID": {
    "enabled": True,
    "allowedValues": [
      "kisa"
    ],
    "validationType": "specified-value-match",
    "score": 0
  },
  "userPW": {
    "enabled": True,
    "allowedValues": [
      "kisa_k1!2@"
    ],
    "validationType": "specified-value-match",
    "score": 0
  }
}

# Capabilities
cmgvieyak001b6cd04cgaawmm_Capabilities_in_validation = {}

# CameraProfiles
cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_validation = {}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# StreamURLs
cmgvieyak001b6cd04cgaawmm_StreamURLs_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# ReplayURL
cmgvieyak001b6cd04cgaawmm_ReplayURL_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# RealtimeVideoEventInfos
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_validation = {}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  },
  "classFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equalsAny",
    "validValueFieldName": "classFilter",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "사람",
      "트럭",
      "버스",
      "Human"
    ],
    "score": 0
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equalsAny",
    "validValueFieldName": "eventFilter",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "화재",
      "배회",
      "침입",
      "Loitering",
      "Intrusion"
    ],
    "score": 0
  }
}

# cmgvieyak001b6cd04cgaawmm 검증 리스트
cmgvieyak001b6cd04cgaawmm_inValidation = [
    cmgvieyak001b6cd04cgaawmm_Authentication_in_validation,
    cmgvieyak001b6cd04cgaawmm_Capabilities_in_validation,
    cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_validation,
    cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_validation,
    cmgvieyak001b6cd04cgaawmm_StreamURLs_in_validation,
    cmgvieyak001b6cd04cgaawmm_ReplayURL_in_validation,
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_validation,
    cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_validation,
]

# Authentication
cmh1u5pef000sgxc3bzl4y9v0_Authentication_in_validation = {}

# DoorProfiles
cmh1u5pef000sgxc3bzl4y9v0_DoorProfiles_in_validation = {}

# RealtimeDoorStatus
cmh1u5pef000sgxc3bzl4y9v0_RealtimeDoorStatus_in_validation = {}

# DoorControl
cmh1u5pef000sgxc3bzl4y9v0_DoorControl_in_validation = {
  "doorID": {
    "score": 1,
    "enabled": True,
    "allowedValues": [],
    "validationType": "response-field-list-match",
    "referenceListField": "doorID",
    "referenceListEndpoint": "/RealtimeDoorStatus",
    "referenceEndpoint": "/RealtimeDoorStatus"
  },
  "commandType": {
    "score": 1,
    "enabled": True,
    "allowedValues": [
      "Lock",
      "UnLock"
    ],
    "referenceField": "doorSensor",
    "validationType": "valid-value-match",
    "referenceEndpoint": "/DoorProfiles",
    "validValueOperator": "not-equal",
    "validValueFieldName": "eventFilter_bio",
    "validValueMatchType": "validation-field"
  }
}

# cmh1u5pef000sgxc3bzl4y9v0 검증 리스트
cmh1u5pef000sgxc3bzl4y9v0_inValidation = [
    cmh1u5pef000sgxc3bzl4y9v0_Authentication_in_validation,
    cmh1u5pef000sgxc3bzl4y9v0_DoorProfiles_in_validation,
    cmh1u5pef000sgxc3bzl4y9v0_RealtimeDoorStatus_in_validation,
    cmh1u5pef000sgxc3bzl4y9v0_DoorControl_in_validation,
]

