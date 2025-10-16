# Authentication
cmgatbdp000bqihlexmywusvq_Authentication_in_validation = {}

# Capabilities
cmgatbdp000bqihlexmywusvq_Capabilities_in_validation = {}

# SensorDeviceProfiles
cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_in_validation = {}

# RealtimeSensorData
cmgatbdp000bqihlexmywusvq_RealtimeSensorData_in_validation = {}

# RealtimeSensorEventInfos
cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_in_validation = {}

# StoredSensorEventInfos
cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_in_validation = {}

# SensorDeviceControl
cmgatbdp000bqihlexmywusvq_SensorDeviceControl_in_validation = {}

# cmgatbdp000bqihlexmywusvq 검증 리스트
cmgatbdp000bqihlexmywusvq_inValidation = [
    cmgatbdp000bqihlexmywusvq_Authentication_in_validation,
    cmgatbdp000bqihlexmywusvq_Capabilities_in_validation,
    cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_in_validation,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorData_in_validation,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_in_validation,
    cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_in_validation,
    cmgatbdp000bqihlexmywusvq_SensorDeviceControl_in_validation,
]

# Authentication
cmgasj98w009aihlezm0fe6cs_Authentication_in_validation = {}

# Capabilities
cmgasj98w009aihlezm0fe6cs_Capabilities_in_validation = {}

# DoorProfiles
cmgasj98w009aihlezm0fe6cs_DoorProfiles_in_validation = {}

# AccessUserInfos
cmgasj98w009aihlezm0fe6cs_AccessUserInfos_in_validation = {}

# RealtimeVerifEventInfos
cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_in_validation = {}

# StoredVerifEventInfos
cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_in_validation = {}

# RealtimeDoorStatus
cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_in_validation = {}

# DoorControl
cmgasj98w009aihlezm0fe6cs_DoorControl_in_validation = {}

# cmgasj98w009aihlezm0fe6cs 검증 리스트
cmgasj98w009aihlezm0fe6cs_inValidation = [
    cmgasj98w009aihlezm0fe6cs_Authentication_in_validation,
    cmgasj98w009aihlezm0fe6cs_Capabilities_in_validation,
    cmgasj98w009aihlezm0fe6cs_DoorProfiles_in_validation,
    cmgasj98w009aihlezm0fe6cs_AccessUserInfos_in_validation,
    cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_in_validation,
    cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_in_validation,
    cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_in_validation,
    cmgasj98w009aihlezm0fe6cs_DoorControl_in_validation,
]

# Authentication
cmga0l5mh005dihlet5fcoj0o_Authentication_in_validation = {}

# Capabilities
cmga0l5mh005dihlet5fcoj0o_Capabilities_in_validation = {}

# CameraProfiles
cmga0l5mh005dihlet5fcoj0o_CameraProfiles_in_validation = {}

# StoredVideoInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_in_validation = {}

# StreamURLs
cmga0l5mh005dihlet5fcoj0o_StreamURLs_in_validation = {}

# ReplayURL
cmga0l5mh005dihlet5fcoj0o_ReplayURL_in_validation = {}


# StoredVideoEventInfos
cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_in_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID"
  },
  "eventFilter": {
    "score": 1,
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
    "score": 1,
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

# RealtimeVideoEventInfos
cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_in_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID"
  },
  "eventFilter": {
    "score": 1,
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
  "classFilter": {
    "score": 1,
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equals",
    "validValueFieldName": "classFilter",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "사람",
      "트럭",
      "버스"
    ]
  }
}


# StoredObjectAnalyticsInfos
cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_in_validation = {}

# PtzStatus
cmga0l5mh005dihlet5fcoj0o_PtzStatus_in_validation = {}

# PtzContinuousMove
cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_in_validation = {}

# PtzStop

cmg7bve25000114cevhn5o3vr_PtzStop_in_validation = {}

# cmg7bve25000114cevhn5o3vr 검증 리스트
cmg7bve25000114cevhn5o3vr_inValidation = [
    cmg7bve25000114cevhn5o3vr_Authentication_in_validation,
    cmg7bve25000114cevhn5o3vr_Capabilities_in_validation,
    cmg7bve25000114cevhn5o3vr_CameraProfiles_in_validation,
    cmg7bve25000114cevhn5o3vr_StoredVideoInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_StreamURLs_in_validation,
    cmg7bve25000114cevhn5o3vr_ReplayURL_in_validation,
    cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_PtzStatus_in_validation,
    cmg7bve25000114cevhn5o3vr_PtzContinuousMove_in_validation,
    cmg7bve25000114cevhn5o3vr_PtzStop_in_validation,

]

