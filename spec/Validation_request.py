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
    "referenceEndpoint": "/SensorDeviceProfiles",
    "referenceListField": "sensorDeviceID",
    "referenceListEndpoint": "/SensorDeviceProfiles",
    "score": 0
  }
}

# SensorDeviceControl2
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_in_validation = {
  "sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-match",
    "referenceFieldId": "cmisfgtvs07sy5vy7f2hjy5aa",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceProfiles",
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
    "referenceEndpoint": "/DoorProfiles",
    "referenceListField": "doorID",
    "referenceListEndpoint": "/DoorProfiles",
    "score": 0
  }
}

# DoorControl
cmiqr1acx00i5ie8fi022t1hp_DoorControl_in_validation = {
  "doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceListField": "doorID",
    "referenceListEndpoint": "/RealtimeDoorStatus",
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
    "score": 0
  }
}

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
    "referenceEndpoint": "/CameraProfiles",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# PtzContinuousMove
cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_in_validation = {
  "camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceEndpoint": "/CameraProfiles",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# PtzStop
cmiqqzrjz00i3ie8figf79cur_PtzStop_in_validation = {
  "camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceEndpoint": "/CameraProfiles",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
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

