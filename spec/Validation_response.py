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
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "201"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "정보 없음"
    ],
    "score": 0
  },
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

