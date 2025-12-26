# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_out_validation = {}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_out_validation = {}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_validation = {}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_validation = {}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_validation = {}

# RealtimeVideoEventInfos WebHook IN Validation
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwrf69i0bu6844g22ccsjtr",
    "referenceField": "camID",
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "score": 0
  }
}

# StoredVideoInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwrn6ab003pnkgl7f78y9t6",
    "referenceField": "camID",
    "referenceEndpoint": "/StoredVideoInfos",
    "score": 0
  },
  "camList.timeList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrltxz000vnkgl3m4u2f2s",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrlxaj0013nkgl40nosy7z",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceEndpointMax": "/StoredVideoInfos",
    "score": 0
  },
  "camList.timeList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrltxz000vnkgl3m4u2f2s",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrlxaj0013nkgl40nosy7z",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceEndpointMax": "/StoredVideoInfos",
    "score": 0
  }
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwrtok201dmnkgl6gzxhft5",
    "referenceField": "camID",
    "referenceEndpoint": "/ReplayURL",
    "score": 0
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrtok201donkglhwulnxos",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrtok301dqnkgl0k66p4py",
    "referenceEndpointMin": "/ReplayURL",
    "referenceEndpointMax": "/ReplayURL",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrtok201donkglhwulnxos",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrtok301dqnkgl0k66p4py",
    "referenceEndpointMin": "/ReplayURL",
    "referenceEndpointMax": "/ReplayURL",
    "score": 0
  }
}

# StoredVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiws5hes00anp002ng50q3fc",
    "referenceField": "camID",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.eventName": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmiws56xa008jp002vhqm6yfn",
    "referenceField": "eventFilter",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiws3ab605bknkglsndw6cp5",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiws41yv0005p002amxfzrhq",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiws3ab605bknkglsndw6cp5",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiws41yv0005p002amxfzrhq",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "score": 0
  }
}

# StoredObjectAnalyticsInfos
cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwsgzrw02x0p002fnxf1f08",
    "referenceField": "camID",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.analyticsTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwsa3je01lnp002owjbqng1",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwsa57401lsp0021esg4kr1",
    "referenceEndpointMin": "/StoredObjectAnalyticsInfos",
    "referenceEndpointMax": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.anlayticsResultList.analyticsClass": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwsgzse02xcp002b6pfp72a",
    "referenceField": "classFilter",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.anlayticsResultList.analyticsAttribute": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwsgzse02xep0024ycdnvrw",
    "referenceField": "attributeFilter",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  }
}

# cmii7v8pr006g8z1tvo55a50u WebHook 검증 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_inValidation = [
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_validation,
]

# cmii7v8pr006g8z1tvo55a50u 검증 리스트
cmii7v8pr006g8z1tvo55a50u_outValidation = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_out_validation,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_out_validation,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_validation,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_validation,
    cmii7v8pr006g8z1tvo55a50u_ReplayURL_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_out_validation,
]

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
  }
}

# RealtimeSensorData WebHook OUT Validation
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_out_validation = {}

# RealtimeSensorEventInfos
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_in_validation = {
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
cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_in_validation = {}

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

# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_out_validation = {}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_out_validation = {}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_validation = {}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_validation = {}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_validation = {}

# RealtimeVideoEventInfos WebHook IN Validation
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwrf69i0bu6844g22ccsjtr",
    "referenceField": "camID",
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "score": 0
  }
}

# StoredVideoInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwrn6ab003pnkgl7f78y9t6",
    "referenceField": "camID",
    "referenceEndpoint": "/StoredVideoInfos",
    "score": 0
  },
  "camList.timeList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrltxz000vnkgl3m4u2f2s",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrlxaj0013nkgl40nosy7z",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceEndpointMax": "/StoredVideoInfos",
    "score": 0
  },
  "camList.timeList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrltxz000vnkgl3m4u2f2s",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrlxaj0013nkgl40nosy7z",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceEndpointMax": "/StoredVideoInfos",
    "score": 0
  }
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwrtok201dmnkgl6gzxhft5",
    "referenceField": "camID",
    "referenceEndpoint": "/ReplayURL",
    "score": 0
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrtok201donkglhwulnxos",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrtok301dqnkgl0k66p4py",
    "referenceEndpointMin": "/ReplayURL",
    "referenceEndpointMax": "/ReplayURL",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrtok201donkglhwulnxos",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrtok301dqnkgl0k66p4py",
    "referenceEndpointMin": "/ReplayURL",
    "referenceEndpointMax": "/ReplayURL",
    "score": 0
  }
}

# StoredVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiws5hes00anp002ng50q3fc",
    "referenceField": "camID",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.eventName": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmiws56xa008jp002vhqm6yfn",
    "referenceField": "eventFilter",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiws3ab605bknkglsndw6cp5",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiws41yv0005p002amxfzrhq",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiws3ab605bknkglsndw6cp5",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiws41yv0005p002amxfzrhq",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "score": 0
  }
}

# StoredObjectAnalyticsInfos
cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwsgzrw02x0p002fnxf1f08",
    "referenceField": "camID",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.analyticsTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwsa3je01lnp002owjbqng1",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwsa57401lsp0021esg4kr1",
    "referenceEndpointMin": "/StoredObjectAnalyticsInfos",
    "referenceEndpointMax": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.anlayticsResultList.analyticsClass": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwsgzse02xcp002b6pfp72a",
    "referenceField": "classFilter",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.anlayticsResultList.analyticsAttribute": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwsgzse02xep0024ycdnvrw",
    "referenceField": "attributeFilter",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  }
}

# cmii7v8pr006g8z1tvo55a50u WebHook 검증 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_inValidation = [
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_validation,
]

# cmii7v8pr006g8z1tvo55a50u 검증 리스트
cmii7v8pr006g8z1tvo55a50u_outValidation = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_out_validation,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_out_validation,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_validation,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_validation,
    cmii7v8pr006g8z1tvo55a50u_ReplayURL_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_out_validation,
]

# Authentication
cmiqr2b9j00i9ie8frw439h8i_Authentication_out_validation = {}

# Capabilities
cmiqr2b9j00i9ie8frw439h8i_Capabilities_out_validation = {}

# SensorDeviceProfiles
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_out_validation = {}

# SensorDeviceControl
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl_out_validation = {
  "sensorDeviceID": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmisfqqxc07ub5vy7ao1d67bu",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl",
    "score": 0
  },
  "sensorDeviceStatus": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "sensorControl",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "AlarmOn",
      "AlarmOff"
    ],
    "score": 0
  }
}

# SensorDeviceControl2
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl2_out_validation = {
  "sensorDeviceID": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmisg8fmw08c55vy7eby9fson",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl2",
    "score": 0
  },
  "sensorDeviceStatus": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmisg8hg208ca5vy7ijzfeelo",
    "referenceField": "commandType",
    "referenceEndpoint": "/SensorDeviceControl2",
    "score": 0
  }
}

# cmiqr2b9j00i9ie8frw439h8i 검증 리스트
cmiqr2b9j00i9ie8frw439h8i_outValidation = [
    cmiqr2b9j00i9ie8frw439h8i_Authentication_out_validation,
    cmiqr2b9j00i9ie8frw439h8i_Capabilities_out_validation,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_out_validation,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl_out_validation,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl2_out_validation,
]

# Authentication
cmiqr1jha00i6ie8fb1scb3go_Authentication_out_validation = {}

# Capabilities
cmiqr1jha00i6ie8fb1scb3go_Capabilities_out_validation = {}

# DoorProfiles
cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_out_validation = {}

# RealtimeDoorStatus
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_out_validation = {}

# RealtimeDoorStatus WebHook IN Validation
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmixusnx90hatp002m3rnln60",
    "referenceField": "doorID",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "score": 0
  },
  "doorList.doorSensor": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acControl",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Lock",
      "Unlock"
    ],
    "score": 0
  }
}

# DoorControl
cmiqr1jha00i6ie8fb1scb3go_DoorControl_out_validation = {}

# RealtimeDoorStatus2
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_out_validation = {}

# RealtimeDoorStatus2 WebHook IN Validation
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmixuykwk0hmep002xddae990",
    "referenceField": "doorID",
    "referenceEndpoint": "/RealtimeDoorStatus2",
    "score": 0
  },
  "doorList.doorSensor": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmj83qob2000isnx0rwhvblif",
    "referenceField": "commandType",
    "referenceEndpoint": "/DoorControl",
    "score": 0
  }
}

# cmiqr1jha00i6ie8fb1scb3go WebHook 검증 리스트
cmiqr1jha00i6ie8fb1scb3go_webhook_inValidation = [
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_in_validation,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_in_validation,
]

# cmiqr1jha00i6ie8fb1scb3go 검증 리스트
cmiqr1jha00i6ie8fb1scb3go_outValidation = [
    cmiqr1jha00i6ie8fb1scb3go_Authentication_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_Capabilities_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_out_validation,
]

# Authentication
cmiqr0kdw00i4ie8fr3firjtg_Authentication_out_validation = {}

# Capabilities
cmiqr0kdw00i4ie8fr3firjtg_Capabilities_out_validation = {}

# CameraProfiles
cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_out_validation = {}

# PtzStatus
cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_out_validation = {}

# PtzContinuousMove
cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_out_validation = {}

# PtzStop
cmiqr0kdw00i4ie8fr3firjtg_PtzStop_out_validation = {}

# cmiqr0kdw00i4ie8fr3firjtg 검증 리스트
cmiqr0kdw00i4ie8fr3firjtg_outValidation = [
    cmiqr0kdw00i4ie8fr3firjtg_Authentication_out_validation,
    cmiqr0kdw00i4ie8fr3firjtg_Capabilities_out_validation,
    cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_out_validation,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_out_validation,
    cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_out_validation,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStop_out_validation,
]

# Authentication
cmiqr201z00i8ie8fitdg5t1b_Authentication_in_validation = {
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
cmiqr201z00i8ie8fitdg5t1b_Capabilities_in_validation = {}

# SensorDeviceProfiles
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_in_validation = {}

# SensorDeviceControl
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_in_validation = {
  "sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmisfgtvs07sy5vy7f2hjy5aa",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceProfiles",
    "score": 0
  },
  "commandType": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "score": 0
  }
}

# SensorDeviceControl2
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_in_validation = {
  "sensorDeviceID": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmisg3n7u088o5vy75dl8ge3h",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl",
    "score": 0
  },
  "commandType": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "sensorControl",
    "validValueOperator": "excludeReference",
    "allowedValues": [
      "AlarmOn",
      "AlarmOff"
    ],
    "referenceFieldId": "cmj6hdjek01qsxei0ydzyxlg3",
    "referenceField": "sensorDeviceStatus",
    "referenceEndpoint": "/SensorDeviceControl",
    "score": 0
  }
}

# cmiqr201z00i8ie8fitdg5t1b 검증 리스트
cmiqr201z00i8ie8fitdg5t1b_inValidation = [
    cmiqr201z00i8ie8fitdg5t1b_Authentication_in_validation,
    cmiqr201z00i8ie8fitdg5t1b_Capabilities_in_validation,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_in_validation,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_in_validation,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_in_validation,
]

# Authentication
cmiqr1acx00i5ie8fi022t1hp_Authentication_in_validation = {
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
cmiqr1acx00i5ie8fi022t1hp_Capabilities_in_validation = {}

# DoorProfiles
cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_in_validation = {}

# RealtimeDoorStatus
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_in_validation = {}

# DoorControl
cmiqr1acx00i5ie8fi022t1hp_DoorControl_in_validation = {
  "doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmj6i9tmk023gxei0fwmi1vp0",
    "referenceField": "doorID",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "score": 0
  },
  "commandType": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acControl",
    "validValueOperator": "excludeReference",
    "allowedValues": [
      "Lock",
      "Unlock"
    ],
    "referenceFieldId": "cmj13a9eu01vx12s9wja5mxt7",
    "referenceField": "doorSensor",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "score": 0
  }
}

# RealtimeDoorStatus2
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_in_validation = {}

# cmiqr1acx00i5ie8fi022t1hp 검증 리스트
cmiqr1acx00i5ie8fi022t1hp_inValidation = [
    cmiqr1acx00i5ie8fi022t1hp_Authentication_in_validation,
    cmiqr1acx00i5ie8fi022t1hp_Capabilities_in_validation,
    cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_in_validation,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_in_validation,
    cmiqr1acx00i5ie8fi022t1hp_DoorControl_in_validation,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_in_validation,
]

# Authentication
cmiqqzrjz00i3ie8figf79cur_Authentication_in_validation = {
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
cmiqqzrjz00i3ie8figf79cur_Capabilities_in_validation = {}

# CameraProfiles
cmiqqzrjz00i3ie8figf79cur_CameraProfiles_in_validation = {}

# PtzStatus
cmiqqzrjz00i3ie8figf79cur_PtzStatus_in_validation = {
  "camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmiwpi3sm076e844gan3rcpwr",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# PtzContinuousMove
cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_in_validation = {
  "camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmiwpi3sm076e844gan3rcpwr",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# PtzStop
cmiqqzrjz00i3ie8figf79cur_PtzStop_in_validation = {
  "camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmiwpi3sz076y844gftp3b99j",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# cmiqqzrjz00i3ie8figf79cur 검증 리스트
cmiqqzrjz00i3ie8figf79cur_inValidation = [
    cmiqqzrjz00i3ie8figf79cur_Authentication_in_validation,
    cmiqqzrjz00i3ie8figf79cur_Capabilities_in_validation,
    cmiqqzrjz00i3ie8figf79cur_CameraProfiles_in_validation,
    cmiqqzrjz00i3ie8figf79cur_PtzStatus_in_validation,
    cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_in_validation,
    cmiqqzrjz00i3ie8figf79cur_PtzStop_in_validation,
]

