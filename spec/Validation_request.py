# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_in_validation = {}

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
      "버스"
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
      "배회"
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

