# Authentication
cmii7shen005i8z1tagevx4qh_Authentication_in_validation = {
  "userID": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa"
    ],
    "score": 0
  },
  "userPW": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa_k1!2@"
    ],
    "score": 0
  }
}

# Capabilities
cmii7shen005i8z1tagevx4qh_Capabilities_in_validation = {}

# SensorDeviceProfiles
cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_in_validation = {}

# RealtimeSensorData
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_in_validation = {}

# RealtimeSensorEventInfos
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_in_validation = {}

# StoredSensorEventInfos
cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_in_validation = {}

# cmii7shen005i8z1tagevx4qh 검증 리스트
cmii7shen005i8z1tagevx4qh_inValidation = [
    cmii7shen005i8z1tagevx4qh_Authentication_in_validation,
    cmii7shen005i8z1tagevx4qh_Capabilities_in_validation,
    cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_in_validation,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_in_validation,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_in_validation,
    cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_in_validation,
]

# Authentication
cmii7pysb004k8z1tts0npxfm_Authentication_in_validation = {
  "userID": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa"
    ],
    "score": 0
  },
  "userPW": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa_k1!2@"
    ],
    "score": 0
  }
}

# Capabilities
cmii7pysb004k8z1tts0npxfm_Capabilities_in_validation = {}

# DoorProfiles
cmii7pysb004k8z1tts0npxfm_DoorProfiles_in_validation = {}

# AccessUserInfos
cmii7pysb004k8z1tts0npxfm_AccessUserInfos_in_validation = {}

# RealtimeVerifEventInfos
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_in_validation = {}

# StoredVerifEventInfos
cmii7pysb004k8z1tts0npxfm_StoredVerifEventInfos_in_validation = {}

# cmii7pysb004k8z1tts0npxfm 검증 리스트
cmii7pysb004k8z1tts0npxfm_inValidation = [
    cmii7pysb004k8z1tts0npxfm_Authentication_in_validation,
    cmii7pysb004k8z1tts0npxfm_Capabilities_in_validation,
    cmii7pysb004k8z1tts0npxfm_DoorProfiles_in_validation,
    cmii7pysb004k8z1tts0npxfm_AccessUserInfos_in_validation,
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_in_validation,
    cmii7pysb004k8z1tts0npxfm_StoredVerifEventInfos_in_validation,
]

# Authentication
cmii7lxbn002s8z1t1i9uudf0_Authentication_in_validation = {
  "userID": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa"
    ],
    "score": 0
  },
  "userPW": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa_k1!2@"
    ],
    "score": 0
  }
}

# Capabilities
cmii7lxbn002s8z1t1i9uudf0_Capabilities_in_validation = {}

# CameraProfiles
cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_in_validation = {}

# StreamURLs
cmii7lxbn002s8z1t1i9uudf0_StreamURLs_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceEndpoint": "/CameraProfiles",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "score": 0
  },
  "camList.streamProtocolType": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "RTSP"
    ],
    "score": 0
  }
}

# RealtimeVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceEndpoint": "/CameraProfiles",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "score": 0
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "LongPolling",
      "Webhook"
    ],
    "score": 0
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "videoEvent",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Loitering",
      "Intrusion"
    ],
    "score": 0
  },
  "classFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "videoObject",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Human"
    ],
    "score": 0
  }
}

# StoredVideoInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_in_validation = {}

# ReplayURL
cmii7lxbn002s8z1t1i9uudf0_ReplayURL_in_validation = {}

# StoredVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_in_validation = {}

# StoredObjectAnalyticsInfos
cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_in_validation = {}

# cmii7lxbn002s8z1t1i9uudf0 검증 리스트
cmii7lxbn002s8z1t1i9uudf0_inValidation = [
    cmii7lxbn002s8z1t1i9uudf0_Authentication_in_validation,
    cmii7lxbn002s8z1t1i9uudf0_Capabilities_in_validation,
    cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_in_validation,
    cmii7lxbn002s8z1t1i9uudf0_StreamURLs_in_validation,
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_in_validation,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_in_validation,
    cmii7lxbn002s8z1t1i9uudf0_ReplayURL_in_validation,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_in_validation,
    cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_in_validation,
]

