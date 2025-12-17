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
    "referenceFieldId": "cmixuu94o0hchp002wh8j30df",
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
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmizh2j7y028k7eoekmch7neb",
    "referenceField": "doorID",
    "referenceEndpoint": "/DoorProfiles",
    "score": 0
  }
}

# RealtimeDoorStatus WebHook OUT Validation
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_webhook_out_validation = {}

# DoorControl
cmiqr1acx00i5ie8fi022t1hp_DoorControl_in_validation = {
  "doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwqkuoj0aj9844g5oec97p9",
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
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmiwqovgn0az6844g1iuqahpi",
    "referenceField": "doorID",
    "referenceEndpoint": "/DoorControl",
    "referenceListField": "doorID",
    "referenceListFieldId": "cmiwqkuoj0aj9844g5oec97p9",
    "score": 0
  }
}

# RealtimeDoorStatus2 WebHook OUT Validation
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_webhook_out_validation = {}

# cmiqr1acx00i5ie8fi022t1hp WebHook 검증 리스트
cmiqr1acx00i5ie8fi022t1hp_webhook_outValidation = [
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_webhook_out_validation,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_webhook_out_validation,
]

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

