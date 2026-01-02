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
cmii7wfuf006i8z1tcds6q69g_Authentication_out_validation = {}

# Capabilities
cmii7wfuf006i8z1tcds6q69g_Capabilities_out_validation = {}

# SensorDeviceProfiles
cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_out_validation = {}

# RealtimeSensorData
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_out_validation = {}

# RealtimeSensorData WebHook IN Validation
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_in_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwuxvls0cj1p002zte0s84o",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/RealtimeSensorData",
    "score": 0
  }
}

# RealtimeSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_out_validation = {}

# RealtimeSensorEventInfos WebHook IN Validation
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_in_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmj6feinr01aixei0iwq8v8ia",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/RealtimeSensorEventInfos",
    "score": 0
  },
  "sensorDeviceList.eventName": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmj6fdgsb0184xei0mr9kacqd",
    "referenceField": "eventFilter",
    "referenceEndpoint": "/RealtimeSensorEventInfos",
    "score": 0
  },
  "sensorDeviceList.eventTime": {
    "enabled": True,
    "validationType": "range-match",
    "rangeMin": 20251105163010124,
    "rangeMax": 20251105163010124,
    "rangeOperator": "between",
    "score": 0
  }
}

# StoredSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_out_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmixtx2dx0dlwp002gtco28w8",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/StoredSensorEventInfos",
    "score": 0
  }
}

# cmii7wfuf006i8z1tcds6q69g WebHook 검증 리스트
cmii7wfuf006i8z1tcds6q69g_webhook_inValidation = [
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_in_validation,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_in_validation,
]

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
cmii7w683006h8z1t7usnin5g_Authentication_out_validation = {}

# Capabilities
cmii7w683006h8z1t7usnin5g_Capabilities_out_validation = {}

# DoorProfiles
cmii7w683006h8z1t7usnin5g_DoorProfiles_out_validation = {}

# AccessUserInfos
cmii7w683006h8z1t7usnin5g_AccessUserInfos_out_validation = {}

# RealtimeVerifEventInfos
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_out_validation = {}

# RealtimeVerifEventInfos WebHook IN Validation
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwt9k7208sxp002x2a5b3x3",
    "referenceField": "doorID",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "score": 0
  },
  "doorList.eventName": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmiwt94g908r6p00262pdfkog",
    "referenceField": "eventFilter",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "score": 0
  }
}

# StoredVerifEventInfos
cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_out_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwthcyk09y7p002ovmv3d43",
    "referenceField": "doorID",
    "referenceEndpoint": "/StoredVerifEventInfos",
    "score": 0
  },
  "doorList.eventName": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmiwth4c209xkp002mm4lfebj",
    "referenceField": "eventFilter",
    "referenceEndpoint": "/StoredVerifEventInfos",
    "score": 0
  }
}

# cmii7w683006h8z1t7usnin5g WebHook 검증 리스트
cmii7w683006h8z1t7usnin5g_webhook_inValidation = [
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_in_validation,
]

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

