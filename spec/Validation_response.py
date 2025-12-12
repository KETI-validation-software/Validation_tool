# Authentication
cmii7wfuf006i8z1tcds6q69g_Authentication_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "400"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "잘못된 요청"
    ],
    "score": 0
  }
}

# Capabilities
cmii7wfuf006i8z1tcds6q69g_Capabilities_out_validation = {}

# SensorDeviceProfiles
cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_out_validation = {}

# RealtimeSensorData
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_out_validation = {}

# RealtimeSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_out_validation = {}

# StoredSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_out_validation = {}

# cmii7wfuf006i8z1tcds6q69g 검증 리스트
cmii7wfuf006i8z1tcds6q69g_outValidation = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_out_validation,
    cmii7wfuf006i8z1tcds6q69g_Capabilities_out_validation,
    cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_out_validation,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_out_validation,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_out_validation,
    cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_out_validation,
]

# Authentication
cmii7w683006h8z1t7usnin5g_Authentication_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "400"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "잘못된 요청"
    ],
    "score": 0
  }
}

# Capabilities
cmii7w683006h8z1t7usnin5g_Capabilities_out_validation = {}

# DoorProfiles
cmii7w683006h8z1t7usnin5g_DoorProfiles_out_validation = {}

# AccessUserInfos
cmii7w683006h8z1t7usnin5g_AccessUserInfos_out_validation = {}

# RealtimeVerifEventInfos
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_out_validation = {}

# StoredVerifEventInfos
cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_out_validation = {}

# cmii7w683006h8z1t7usnin5g 검증 리스트
cmii7w683006h8z1t7usnin5g_outValidation = [
    cmii7w683006h8z1t7usnin5g_Authentication_out_validation,
    cmii7w683006h8z1t7usnin5g_Capabilities_out_validation,
    cmii7w683006h8z1t7usnin5g_DoorProfiles_out_validation,
    cmii7w683006h8z1t7usnin5g_AccessUserInfos_out_validation,
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_out_validation,
    cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_out_validation,
]

# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "400"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "잘못된 요청"
    ],
    "score": 0
  }
}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_out_validation = {}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_validation = {}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_validation = {}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_validation = {}

# StoredVideoInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StoredVideoInfos",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoInfos",
    "score": 0
  },
  "camList.timeList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMax": "endTime",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceEndpointMax": "/StoredVideoInfos",
    "score": 0
  },
  "camList.timeList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMax": "endTime",
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
    "referenceEndpoint": "/ReplayURL",
    "referenceListField": "camID",
    "referenceListEndpoint": "/ReplayURL",
    "score": 0
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMax": "endTime",
    "referenceEndpointMin": "/ReplayURL",
    "referenceEndpointMax": "/ReplayURL",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMax": "endTime",
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
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoEventInfos",
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
    "referenceFieldMax": "endTime",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMax": "endTime",
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
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.analyticsTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMax": "endTime",
    "referenceEndpointMin": "/StoredObjectAnalyticsInfos",
    "referenceEndpointMax": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.anlayticsResultList": {
    "enabled": True,
    "validationType": "request-field-match",
    "score": 0
  },
  "camList.anlayticsResultList.analyticsClass": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "referenceListField": "classFilter",
    "referenceListEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.anlayticsResultList.analyticsAttribute": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "referenceListField": "attributeFilter",
    "referenceListEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  }
}

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

