# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_out_constraints = {}

# Capabilities
cmg90br3n002qihleffuljnth_Capabilities_out_constraints = {}

# SensorDeviceProfiles
cmg90br3n002qihleffuljnth_SensorDeviceProfiles_out_constraints = {}

# RealtimeSensorData
cmg90br3n002qihleffuljnth_RealtimeSensorData_out_constraints = {
  "sensorDeviceList.sensorDeviceID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceList.measureTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal"
    },
    "requestRangeMinEndpoint": "/RealtimeSensorEventInfos"
  }
}

# RealtimeSensorEventInfos
cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_out_constraints = {
  "sensorDeviceList.sensorDeviceID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID",
    "requestRange": {
      "operator": "between"
    }
  },
  "sensorDeviceList.eventName": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeSensorEventInfos",
    "referenceField": "eventFilter"
  },
  "sensorDeviceList.eventTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal"
    },
    "requestRangeMinEndpoint": "/RealtimeSensorEventInfos"
  }
}

# StoredSensorEventInfos
cmg90br3n002qihleffuljnth_StoredSensorEventInfos_out_constraints = {
  "sensorDeviceList.sensorDeviceID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceList.eventName": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeSensorEventInfos",
    "referenceField": "eventFilter"
  },
  "sensorDeviceList.eventTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    },
    "requestRangeMinEndpoint": "/RealtimeSensorEventInfos",
    "requestRangeMaxEndpoint": "/StoredSensorEventInfos"
  }
}

# SensorDeviceControl
cmg90br3n002qihleffuljnth_SensorDeviceControl_out_constraints = {
  "sensorDeviceID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceStatus": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "commandType"
  }
}

# cmg90br3n002qihleffuljnth 검증 리스트
cmg90br3n002qihleffuljnth_inConstraints = [
    cmg90br3n002qihleffuljnth_Authentication_out_constraints,
    cmg90br3n002qihleffuljnth_Capabilities_out_constraints,
    cmg90br3n002qihleffuljnth_SensorDeviceProfiles_out_constraints,
    cmg90br3n002qihleffuljnth_RealtimeSensorData_out_constraints,
    cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_out_constraints,
    cmg90br3n002qihleffuljnth_StoredSensorEventInfos_out_constraints,
    cmg90br3n002qihleffuljnth_SensorDeviceControl_out_constraints,
]

# Authentication
cmg7edeo50013124xiux3gbkb_Authentication_out_constraints = {}

# Capabilities
cmg7edeo50013124xiux3gbkb_Capabilities_out_constraints = {}

# DoorProfiles
cmg7edeo50013124xiux3gbkb_DoorProfiles_out_constraints = {}

# AccessUserInfos
cmg7edeo50013124xiux3gbkb_AccessUserInfos_out_constraints = {}

# RealtimeVerifEventInfos
cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_out_constraints = {
  "doorList.eventTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal"
    },
    "requestRangeMinEndpoint": "RealtimeVerifEventInfos"
  }
}

# StoredVerifEventInfos
cmg7edeo50013124xiux3gbkb_StoredVerifEventInfos_out_constraints = {
  "doorList.eventTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    },
    "requestRangeMinEndpoint": "RealtimeVerifEventInfos",
    "requestRangeMaxEndpoint": "/StoredVerifEventInfos"
  },
  "doorList.doorID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "RealtimeVerifEventInfos",
    "referenceField": "doorID"
  },
  "doorList.bioAuthTypeList": {
    "valueType": "random",
    "required": False,
    "randomType": "specified-values",
    "arrayElementType": "array"
  },
  "doorList.otherAuthTypeList": {
    "valueType": "random",
    "required": False,
    "randomType": "specified-values",
    "arrayElementType": "array"
  },
  "doorList.eventName": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "RealtimeVerifEventInfos",
    "referenceField": "eventFilter"
  }
}

# RealtimeDoorStatus
cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_out_constraints = {}

# DoorControl
cmg7edeo50013124xiux3gbkb_DoorControl_out_constraints = {}

# cmg7edeo50013124xiux3gbkb 검증 리스트
cmg7edeo50013124xiux3gbkb_inConstraints = [
    cmg7edeo50013124xiux3gbkb_Authentication_out_constraints,
    cmg7edeo50013124xiux3gbkb_Capabilities_out_constraints,
    cmg7edeo50013124xiux3gbkb_DoorProfiles_out_constraints,
    cmg7edeo50013124xiux3gbkb_AccessUserInfos_out_constraints,
    cmg7edeo50013124xiux3gbkb_RealtimeVerifEventInfos_out_constraints,
    cmg7edeo50013124xiux3gbkb_StoredVerifEventInfos_out_constraints,
    cmg7edeo50013124xiux3gbkb_RealtimeDoorStatus_out_constraints,
    cmg7edeo50013124xiux3gbkb_DoorControl_out_constraints,
]

# Authentication
cmg7bve25000114cevhn5o3vr_Authentication_out_constraints = {}

# Capabilities
cmg7bve25000114cevhn5o3vr_Capabilities_out_constraints = {}

# CameraProfiles
cmgvieyak001b6cd04cgaawmm_CameraProfiles_out_constraints = {}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoInfos",
    "referenceField": "camID"
  },
  "camList.timeList.startTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between",
      "minEndpoint": "/StoredVideoInfos"
    },
    "requestRangeMinEndpoint": "/RealtimeVideoEventInfos",
    "requestRangeMaxEndpoint": "/StoredObjectAnalyticsInfos"
  },
  "camList.timeList.endTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between",
      "maxEndpoint": "/StoredVideoInfos"
    },
    "requestRangeMinEndpoint": "/RealtimeVideoEventInfos",
    "requestRangeMaxEndpoint": "/StoredVideoInfos"
  }
}

# StreamURLs
cmgvieyak001b6cd04cgaawmm_StreamURLs_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StreamURLs",
    "referenceField": "camID"
  }
}

# ReplayURL
cmgvieyak001b6cd04cgaawmm_ReplayURL_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoInfos",
    "referenceField": "camID"
  },
  "camList.startTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between",
      "minEndpoint": "/StoredVideoInfos"
    },
    "requestRangeMinEndpoint": "/StoredVideoInfos",
    "requestRangeMaxEndpoint": "/StoredObjectAnalyticsInfos"
  },
  "camList.endTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between",
      "maxEndpoint": "/ReplayURL",
      "minEndpoint": "/ReplayURL"
    },
    "requestRangeMinEndpoint": "/RealtimeVideoEventInfos",
    "requestRangeMaxEndpoint": "/StoredObjectAnalyticsInfos"
  }
}

# RealtimeVideoEventInfos
cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_out_constraints = {}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceField": "camID"
  },
  "camList.eventName": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceField": "eventFilter"
  },
  "camList.startTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal",
      "minEndpoint": "/StoredVideoEventInfos"
    },
    "requestRangeMinEndpoint": "/RealtimeVideoEventInfos",
    "requestRangeMaxEndpoint": "/StoredObjectAnalyticsInfos"
  },
  "camList.endTime": {
    "valueType": "request-range",
    "required": False,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    },
    "requestRangeMinEndpoint": "/RealtimeVideoEventInfos",
    "requestRangeMaxEndpoint": "/StoredObjectAnalyticsInfos"
  }
}

# StoredObjectAnalyticsInfos
cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/PtzStatus",
    "referenceField": "camID"
  },
  "camList.analyticsTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal",
      "minEndpoint": "/StoredVideoEventInfos"
    },
    "requestRangeMinEndpoint": "/RealtimeVideoEventInfos",
    "requestRangeMaxEndpoint": "/StoredObjectAnalyticsInfos"
  },
  "camList.anlayticsResultList.analyticsClass": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "referenceField": "classFilter"
  },
  "camList.anlayticsResultList.analyticsAttribute": {
    "valueType": "request-based",
    "required": False,
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "referenceField": "attributeFilter",
    "requestRange": {
      "operator": "between"
    }
  },
  "camList.anlayticsResultList.analyticsConfidence": {
    "valueType": "preset",
    "required": False
  }
}

# cmgvieyak001b6cd04cgaawmm 검증 리스트
cmgvieyak001b6cd04cgaawmm_inConstraints = [
    cmgvieyak001b6cd04cgaawmm_Authentication_out_constraints,
    cmgvieyak001b6cd04cgaawmm_Capabilities_out_constraints,
    cmgvieyak001b6cd04cgaawmm_CameraProfiles_out_constraints,
    cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_out_constraints,
    cmgvieyak001b6cd04cgaawmm_StreamURLs_out_constraints,
    cmgvieyak001b6cd04cgaawmm_ReplayURL_out_constraints,
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_out_constraints,
    cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_out_constraints,
]

