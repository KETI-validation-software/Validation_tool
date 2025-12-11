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
    "referenceEndpoint": "/SensorDeviceControl",
    "score": 0
  },
  "sensorDeviceStatus": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmisg8hg208ca5vy7ijzfeelo",
    "referenceField": "commandType",
    "referenceEndpoint": "/SensorDeviceControl",
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

# DoorControl
cmiqr1jha00i6ie8fb1scb3go_DoorControl_out_validation = {}

# RealtimeDoorStatus
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_out_validation = {}

# cmiqr1jha00i6ie8fb1scb3go 검증 리스트
cmiqr1jha00i6ie8fb1scb3go_outValidation = [
    cmiqr1jha00i6ie8fb1scb3go_Authentication_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_Capabilities_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_out_validation,
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

