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
  "transProtocol.transProtocolType": {
    "enabled": False,
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
    "referenceEndpoint": "/SensorDeviceProfiles"
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
    "referenceEndpoint": "/SensorDeviceProfiles"
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
    "referenceEndpoint": "/SensorDeviceProfiles"
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
cmg7edeo50013124xiux3gbkb_Capabilities_in_validation = {}

# DoorProfiles
cmg7edeo50013124xiux3gbkb_DoorProfiles_in_validation = {}

# AccessUserInfos
cmg7edeo50013124xiux3gbkb_AccessUserInfos_in_validation = {}

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
cmgvieyak001b6cd04cgaawmm_Capabilities_in_validation = {}

# CameraProfiles
cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_validation = {}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
  }
}

# StreamURLs
cmgvieyak001b6cd04cgaawmm_StreamURLs_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
  }
}

# ReplayURL
cmgvieyak001b6cd04cgaawmm_ReplayURL_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
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
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
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
  "classFilter": {
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
  "startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles"
  },
  "classFilter": {
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

# cmgvieyak001b6cd04cgaawmm 검증 리스트
cmgvieyak001b6cd04cgaawmm_inValidation = [
    cmgvieyak001b6cd04cgaawmm_Authentication_in_validation,
    cmgvieyak001b6cd04cgaawmm_Capabilities_in_validation,
    cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_validation,
    cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_validation,
    cmgvieyak001b6cd04cgaawmm_StreamURLs_in_validation,
    cmgvieyak001b6cd04cgaawmm_ReplayURL_in_validation,
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_validation,
    cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_validation,
]

