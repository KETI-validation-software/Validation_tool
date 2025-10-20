# Authentication
cmg90br3n002qihleffuljnth_Authentication_in_validation = {
  "userID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userPW": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# Capabilities
cmg90br3n002qihleffuljnth_Capabilities_in_validation = {}

# SensorDeviceProfiles
cmg90br3n002qihleffuljnth_SensorDeviceProfiles_in_validation = {}

# RealtimeSensorData
cmg90br3n002qihleffuljnth_RealtimeSensorData_in_validation = {
  "sensorDeviceList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match"
  },
  "duration": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# RealtimeSensorEventInfos
cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_in_validation = {
  "sensorDeviceList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl"
  },
  "duration": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolType": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolDesc": {
    "enabled": False,
    "validationType": "specified-value-match"
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
  },
  "startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredSensorEventInfos
cmg90br3n002qihleffuljnth_StoredSensorEventInfos_in_validation = {
  "timePeriod": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.endTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl"
  },
  "maxCount": {
    "enabled": False,
    "validationType": "specified-value-match"
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

# SensorDeviceControl
cmg90br3n002qihleffuljnth_SensorDeviceControl_in_validation = {
  "sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl"
  },
  "commandType": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# cmg90br3n002qihleffuljnth 검증 리스트
cmg90br3n002qihleffuljnth_inValidation = [
    cmg90br3n002qihleffuljnth_Authentication_in_validation,
    cmg90br3n002qihleffuljnth_Capabilities_in_validation,
    cmg90br3n002qihleffuljnth_SensorDeviceProfiles_in_validation,
    cmg90br3n002qihleffuljnth_RealtimeSensorData_in_validation,
    cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_in_validation,
    cmg90br3n002qihleffuljnth_StoredSensorEventInfos_in_validation,
    cmg90br3n002qihleffuljnth_SensorDeviceControl_in_validation,
]

# Authentication
cmg7edeo50013124xiux3gbkb_Authentication_in_validation = {
  "userID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userPW": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# Capabilities
cmg7edeo50013124xiux3gbkb_Capabilities_in_validation = {
  "": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# DoorProfiles
cmg7edeo50013124xiux3gbkb_DoorProfiles_in_validation = {}

# AccessUserInfos
cmg7edeo50013124xiux3gbkb_AccessUserInfos_in_validation = {
  "": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# RealtimeVerifEventInfos
cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_in_validation = {
  "doorList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "DoorProfiles"
  },
  "duration": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "allowedValues": [
      "LongPolling"
    ],
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolDesc": {
    "enabled": False,
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
  },
  "startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredVerifEventInfos
cmg7edeo50013124xiux3gbkb_StoredVerifEventInfos_in_validation = {
  "timePeriod": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.endTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "DoorProfiles"
  },
  "maxCount": {
    "enabled": False,
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

# RealtimeDoorStatus
cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_in_validation = {
  "doorList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "DoorProfiles"
  },
  "duration": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "allowedValues": [
      "LongPolling"
    ],
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolDesc": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# DoorControl
cmg7edeo50013124xiux3gbkb_DoorControl_in_validation = {
  "doorID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "DoorProfiles"
  },
  "commandType": {
    "enabled": False,
    "validationType": "specified-value-match"
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
cmg7bve25000114cevhn5o3vr_Authentication_in_validation = {
  "userID": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userPW": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# Capabilities
cmg7bve25000114cevhn5o3vr_Capabilities_in_validation = {}

# CameraProfiles
cmg7bve25000114cevhn5o3vr_CameraProfiles_in_validation = {}

# StoredVideoInfos
cmg7bve25000114cevhn5o3vr_StoredVideoInfos_in_validation = {
  "timePeriod": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.startTime": {
    "score": 1,
    "enabled": False,
    "validationType": "response-field-range-match",
    "referenceRangeOperator": "between"
  },
  "timePeriod.endTime": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StreamURLs"
  }
}

# StreamURLs
cmg7bve25000114cevhn5o3vr_StreamURLs_in_validation = {
  "camList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StreamURLs"
  },
  "camList.streamProtocolType": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# ReplayURL
cmg7bve25000114cevhn5o3vr_ReplayURL_in_validation = {
  "camList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StreamURLs"
  },
  "camList.startTime": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.endTime": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.streamProtocolType": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# RealtimeVideoEventInfos
cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_in_validation = {
  "camList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StreamURLs"
  },
  "duration": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolType": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transProtocol.transProtocolDesc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
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
  },
  "startTime": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredVideoEventInfos
cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_in_validation = {
  "timePeriod": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.startTime": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.endTime": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StreamURLs"
  },
  "maxCount": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
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

# StoredObjectAnalyticsInfos
cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_in_validation = {
  "timePeriod": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.startTime": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timePeriod.endTime": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StreamURLs"
  },
  "filterList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
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
    "referenceListField": "camID",
    "referenceEndpoint": "/StreamURLs"
  }
}

# PtzContinuousMove
cmg7bve25000114cevhn5o3vr_PtzContinuousMove_in_validation = {
  "camID": {
    "score": 1,
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StreamURLs"
  },
  "velocity": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "velocity.pan": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "velocity.tilt": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "velocity.zoom": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "timeOut": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# PtzStop
cmg7bve25000114cevhn5o3vr_PtzStop_in_validation = {
  "camID": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "pan": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "tilt": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "zoom": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# cmg7bve25000114cevhn5o3vr 검증 리스트
cmg7bve25000114cevhn5o3vr_inValidation = [
    cmg7bve25000114cevhn5o3vr_Authentication_in_validation,
    cmg7bve25000114cevhn5o3vr_Capabilities_in_validation,
    cmg7bve25000114cevhn5o3vr_CameraProfiles_in_validation,
    cmg7bve25000114cevhn5o3vr_StoredVideoInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_StreamURLs_in_validation,
    cmg7bve25000114cevhn5o3vr_ReplayURL_in_validation,
    cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_in_validation,
    cmg7bve25000114cevhn5o3vr_PtzStatus_in_validation,
    cmg7bve25000114cevhn5o3vr_PtzContinuousMove_in_validation,
    cmg7bve25000114cevhn5o3vr_PtzStop_in_validation,
]

