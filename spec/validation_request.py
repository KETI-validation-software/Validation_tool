# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_in_validation = {
  "userID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userPW": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# Capabilities
cmgvieyak001b6cd04cgaawmm_Capabilities_in_validation = {}

# CameraProfiles
cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_validation = {}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_validation = {
  "timePeriod": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.endTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
  }
}

# StreamURLs
cmgvieyak001b6cd04cgaawmm_StreamURLs_in_validation = {
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
  },
  "camList.streamProtocolType": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# ReplayURL
cmgvieyak001b6cd04cgaawmm_ReplayURL_in_validation = {
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
  },
  "camList.startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.endTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.streamProtocolType": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# RealtimeVideoEventInfos
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_validation = {
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
  },
  "duration": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolType": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolDesc": {
    "enabled": False,
    "validationType": "specified-value-match"
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
    ]
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
    ]
  },
  "startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_validation = {
  "timePeriod": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.endTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
  },
  "maxCount": {
    "enabled": False,
    "validationType": "specified-value-match"
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
    ]
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
    ]
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

