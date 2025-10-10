# Authentication
Authentication_in_validation = {}

# Capabilities
Capabilities_in_validation = {}

# DoorProfiles
DoorProfiles_in_validation = {}

# StoredVideoInfos
StoredVideoInfos_in_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match"
  }
}

# RealtimeSensorEventInfos
RealtimeSensorEventInfos_in_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "sensorDeviceID"
  },
  "eventFilter": {
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

# StoredSensorEventInfos
StoredSensorEventInfos_in_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "sensorDeviceID"
  },
  "eventFilter": {
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

# RealtimeDoorStatus
RealtimeDoorStatus_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "allowedValues": [
      "LongPolling"
    ],
    "validationType": "specified-value-match"
  }
}

# cmg90br3n002qihleffuljnth 검증 리스트
cmg90br3n002qihleffuljnth_inValidation = [
    Authentication_in_validation,
    Capabilities_in_validation,
    DoorProfiles_in_validation,
    StoredVideoInfos_in_validation,
    RealtimeSensorEventInfos_in_validation,
    StoredSensorEventInfos_in_validation,
    RealtimeDoorStatus_in_validation,
]

# Authentication
Authentication_in_validation = {}

# Capabilities
Capabilities_in_validation = {}

# DoorProfiles
DoorProfiles_in_validation = {}

# AccessUserInfos
AccessUserInfos_in_validation = {}

# RealtimeVerifEventInfos
RealtimeVerifEventInfos_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "allowedValues": [
      "LongPolling"
    ],
    "validationType": "specified-value-match"
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equalsAny",
    "validValueFieldName": "eventFilter_bio",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "성공",
      "실패"
    ]
  }
}

# StoredVerifEventInfos
StoredVerifEventInfos_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equalsAny",
    "validValueFieldName": "eventFilter_bio",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "성공",
      "실패"
    ]
  }
}

# RealtimeDoorStatus
RealtimeDoorStatus_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "allowedValues": [
      "LongPolling"
    ],
    "validationType": "specified-value-match"
  }
}

# DoorControl
DoorControl_in_validation = {
  "doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  }
}

# cmg7edeo50013124xiux3gbkb 검증 리스트
cmg7edeo50013124xiux3gbkb_inValidation = [
    Authentication_in_validation,
    Capabilities_in_validation,
    DoorProfiles_in_validation,
    AccessUserInfos_in_validation,
    RealtimeVerifEventInfos_in_validation,
    StoredVerifEventInfos_in_validation,
    RealtimeDoorStatus_in_validation,
    DoorControl_in_validation,
]

# Authentication
Authentication_in_validation = {}

# Capabilities
Capabilities_in_validation = {}

# DoorProfiles
DoorProfiles_in_validation = {}

# StoredVideoInfos
StoredVideoInfos_in_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match"
  }
}

# RealtimeVerifEventInfos
RealtimeVerifEventInfos_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "allowedValues": [
      "LongPolling"
    ],
    "validationType": "specified-value-match"
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equalsAny",
    "validValueFieldName": "eventFilter_bio",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "성공",
      "실패"
    ]
  }
}

# StoredVerifEventInfos
StoredVerifEventInfos_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equalsAny",
    "validValueFieldName": "eventFilter_bio",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "성공",
      "실패"
    ]
  }
}

# RealtimeDoorStatus
RealtimeDoorStatus_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "allowedValues": [
      "LongPolling"
    ],
    "validationType": "specified-value-match"
  }
}

# DoorControl
DoorControl_in_validation = {
  "doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  }
}

# StoredObjectAnalyticsInfos
StoredObjectAnalyticsInfos_in_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID"
  },
  "filterList.classFilter": {
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
  "filterList.attributeFilter": {
    "score": 1,
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equalsAny",
    "validValueFieldName": "attributeFilter",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "여자",
      "안경"
    ]
  }
}

# PtzStatus
PtzStatus_in_validation = {
  "camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID"
  }
}

# PtzContinuousMove
PtzContinuousMove_in_validation = {
  "camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID"
  }
}

# PtzStop
PtzStop_in_validation = {}

# cmg7bve25000114cevhn5o3vr 검증 리스트
cmg7bve25000114cevhn5o3vr_inValidation = [
    Authentication_in_validation,
    Capabilities_in_validation,
    DoorProfiles_in_validation,
    StoredVideoInfos_in_validation,
    RealtimeVerifEventInfos_in_validation,
    StoredVerifEventInfos_in_validation,
    RealtimeDoorStatus_in_validation,
    DoorControl_in_validation,
    StoredObjectAnalyticsInfos_in_validation,
    PtzStatus_in_validation,
    PtzContinuousMove_in_validation,
    PtzStop_in_validation,
]

