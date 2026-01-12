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
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_in_validation = {
  "sensorDeviceList": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueOperator": "equals",
    "score": 0
  },
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmiwkpl7i01cx844gojdnwjps",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceProfiles",
    "score": 0
  }
}

# RealtimeSensorData WebHook OUT Validation
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_out_validation = {}

# RealtimeSensorEventInfos
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_in_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmiwkpl7i01cx844gojdnwjps",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceProfiles",
    "score": 0
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "sensorEvent",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "MotionDetection",
      "Leak"
    ],
    "score": 0
  }
}

# RealtimeSensorEventInfos WebHook OUT Validation
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_out_validation = {}

# StoredSensorEventInfos
cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_in_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmiwkpl7i01cx844gojdnwjps",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceProfiles",
    "score": 0
  }
}

# cmii7shen005i8z1tagevx4qh WebHook 검증 리스트
cmii7shen005i8z1tagevx4qh_webhook_outValidation = [
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_out_validation,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_out_validation,
]

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
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmisk9y5l0db35vy74nn3utak",
    "referenceField": "doorID",
    "referenceEndpoint": "/DoorProfiles",
    "score": 0
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acEvent",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "AuthSuccess",
      "AuthFail"
    ],
    "score": 0
  }
}

# RealtimeVerifEventInfos WebHook OUT Validation
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_out_validation = {}

# StoredVerifEventInfos
cmii7pysb004k8z1tts0npxfm_StoredVerifEventInfos_in_validation = {
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acEvent",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "AuthSuccess",
      "AuthFail"
    ],
    "score": 0
  }
}

# cmii7pysb004k8z1tts0npxfm WebHook 검증 리스트
cmii7pysb004k8z1tts0npxfm_webhook_outValidation = [
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_out_validation,
]

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
    "referenceFieldId": "cmir0b7u9005f4m396k05nfzt",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# RealtimeVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmir0b7u9005f4m396k05nfzt",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
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

# RealtimeVideoEventInfos WebHook OUT Validation
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_out_validation = {}

# StoredVideoInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmir0b7u9005f4m396k05nfzt",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# ReplayURL
cmii7lxbn002s8z1t1i9uudf0_ReplayURL_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmir0b7u9005f4m396k05nfzt",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# StoredVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmir0b7u9005f4m396k05nfzt",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
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

# StoredObjectAnalyticsInfos
cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmir0b7u9005f4m396k05nfzt",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  },
  "filterList.classFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "videoObject",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Human"
    ],
    "score": 0
  },
  "filterList.attributeFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "videoAttribute",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Male",
      "Female"
    ],
    "score": 0
  }
}

# cmii7lxbn002s8z1t1i9uudf0 WebHook 검증 리스트
cmii7lxbn002s8z1t1i9uudf0_webhook_outValidation = [
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_out_validation,
]

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

