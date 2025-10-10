# Authentication
cmg90br3n002qihleffuljnth_Authentication_in_validation = {}

# Capabilities
cmg90br3n002qihleffuljnth_Capabilities_in_validation = {}

# DoorProfiles
cmg90br3n002qihleffuljnth_DoorProfiles_in_validation = {}

# StoredVideoInfos
cmg90br3n002qihleffuljnth_StoredVideoInfos_in_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match"
  }
}

# RealtimeSensorEventInfos
cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_in_validation = {
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
cmg90br3n002qihleffuljnth_StoredSensorEventInfos_in_validation = {
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
cmg90br3n002qihleffuljnth_RealtimeDoorStatus_in_validation = {
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
    cmg90br3n002qihleffuljnth_Authentication_in_validation,
    cmg90br3n002qihleffuljnth_Capabilities_in_validation,
    cmg90br3n002qihleffuljnth_DoorProfiles_in_validation,
    cmg90br3n002qihleffuljnth_StoredVideoInfos_in_validation,
    cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_in_validation,
    cmg90br3n002qihleffuljnth_StoredSensorEventInfos_in_validation,
    cmg90br3n002qihleffuljnth_RealtimeDoorStatus_in_validation,
]

# Authentication
cmg7edeo50013124xiux3gbkb_Authentication_in_validation = {}

# Capabilities
cmg7edeo50013124xiux3gbkb_Capabilities_in_validation = {}

# DoorProfiles
cmg7edeo50013124xiux3gbkb_DoorProfiles_in_validation = {}

# AccessUserInfos
cmg7edeo50013124xiux3gbkb_AccessUserInfos_in_validation = {}

# RealtimeVerifEventInfos
cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_in_validation = {
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
cmg7edeo50013124xiux3gbkb_StoredVerifEventInfos_in_validation = {
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
cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_in_validation = {
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
cmg7edeo50013124xiux3gbkb_DoorControl_in_validation = {
  "doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  }
}

# cmg7edeo50013124xiux3gbkb 검증 리스트
cmg7edeo50013124xiux3gbkb_inValidation = [
    cmg7edeo50013124xiux3gbkb_Authentication_in_validation,
    cmg7edeo50013124xiux3gbkb_Capabilities_in_validation,
    cmg7edeo50013124xiux3gbkb_DoorProfiles_in_validation,
    cmg7edeo50013124xiux3gbkb_AccessUserInfos_in_validation,
    cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_in_validation,
    cmg7edeo50013124xiux3gbkb_StoredVerifEventInfos_in_validation,
    cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_in_validation,
    cmg7edeo50013124xiux3gbkb_DoorControl_in_validation,
]

# Authentication
cmg7bve25000114cevhn5o3vr_Authentication_in_validation = {}

# Capabilities
cmg7bve25000114cevhn5o3vr_Capabilities_in_validation = {}

# DoorProfiles
cmg7bve25000114cevhn5o3vr_DoorProfiles_in_validation = {}

# StoredVideoInfos
cmg7bve25000114cevhn5o3vr_StoredVideoInfos_in_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match"
  }
}

# RealtimeVerifEventInfos
cmg7bve25000114cevhn5o3vr_RealtimeVerifEventInfos_in_validation = {
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
cmg7bve25000114cevhn5o3vr_StoredVerifEventInfos_in_validation = {
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
cmg7bve25000114cevhn5o3vr_RealtimeDoorStatus_in_validation = {
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
cmg7bve25000114cevhn5o3vr_DoorControl_in_validation = {
  "doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID"
  }
}

# StoredObjectAnalyticsInfos
cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_in_validation = {
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
cmg7bve25000114cevhn5o3vr_PtzStatus_in_validation = {
  "camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID"
  }
}

# PtzContinuousMove
cmg7bve25000114cevhn5o3vr_PtzContinuousMove_in_validation = {
  "camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID"
  }
}

# PtzStop
cmg7bve25000114cevhn5o3vr_PtzStop_in_validation = {}

# cmg7bve25000114cevhn5o3vr 검증 리스트
cmg7bve25000114cevhn5o3vr_inValidation = [
    cmg7bve25000114cevhn5o3vr_Authentication_in_validation,
    cmg7bve25000114cevhn5o3vr_Capabilities_in_validation,
    cmg7bve25000114cevhn5o3vr_DoorProfiles_in_validation,
    cmg7bve25000114cevhn5o3vr_StoredVideoInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_RealtimeVerifEventInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_StoredVerifEventInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_RealtimeDoorStatus_in_validation,
    cmg7bve25000114cevhn5o3vr_DoorControl_in_validation,
    cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_PtzStatus_in_validation,
    cmg7bve25000114cevhn5o3vr_PtzContinuousMove_in_validation,
    cmg7bve25000114cevhn5o3vr_PtzStop_in_validation,
]

