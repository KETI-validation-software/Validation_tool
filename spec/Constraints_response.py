# Authentication
cmg90br3n002qihleffuljnth_Authentication_out_constraints = {}

# Capabilities
cmg90br3n002qihleffuljnth_Capabilities_out_constraints = {}

# SensorDeviceProfiles
cmg90br3n002qihleffuljnth_SensorDeviceProfiles_out_constraints = {}

# RealtimeSensorData
cmg90br3n002qihleffuljnth_RealtimeSensorData_out_constraints = {
  "sensorDeviceList.sensorDeviceID": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceList.measureTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal"
    }
  }
}

# RealtimeSensorEventInfos
cmg90br3n002qihleffuljnth_RealtimeSensorEventInfos_out_constraints = {
  "sensorDeviceList.sensorDeviceID": {
    "valueType": "request-based",
    "required": True,
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
    }
  }
}

# StoredSensorEventInfos
cmg90br3n002qihleffuljnth_StoredSensorEventInfos_out_constraints = {
  "sensorDeviceList.sensorDeviceID": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceList.eventName": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredSensorEventInfos",
    "referenceField": "eventFilter"
  },
  "sensorDeviceList.eventTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    }
  }
}

# SensorDeviceControl
cmg90br3n002qihleffuljnth_SensorDeviceControl_out_constraints = {
  "sensorDeviceID": {
    "valueType": "request-based",
    "required": True,

    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceStatus": {
    "valueType": "request-based",
    "required": True,
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
    }
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
    }
  },
  "doorList.doorID": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "doorID"
  },
  "doorList.bioAuthTypeList": {
    "valueType": "random",
    "required": True,
    "randomType": "specified-values",
    "arrayElementType": "array"
  },
  "doorList.otherAuthTypeList": {
    "valueType": "random",
    "required": True,
    "randomType": "specified-values",
    "arrayElementType": "array"
  },
  "doorList.eventName": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVerifEventInfos",
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
cmg7bve25000114cevhn5o3vr_CameraProfiles_out_constraints = {
  "camList.camID": {
    "valueType": "preset",
    "required": True
  }
}

# StoredVideoInfos
cmg7bve25000114cevhn5o3vr_StoredVideoInfos_out_constraints = {
  "camList": {
    "valueType": "preset",
    "required": True,
    "arrayElementType": "object"
  },
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "camID"
  },
  "camList.timeList.startTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    }
  },
  "camList.timeList.endTime": {
    "valueType": "request-range",
    "required": False,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    }
  }
}

# StreamURLs
cmg7bve25000114cevhn5o3vr_StreamURLs_out_constraints = {}

# ReplayURL
cmg7bve25000114cevhn5o3vr_ReplayURL_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "camID"
  },
  "camList.startTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    }
  },
  "camList.endTime": {
    "valueType": "request-range",
    "required": False,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    }
  }
}

# RealtimeVideoEventInfos

cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "camID"
  },
  "camList.eventUUID": {
    "valueType": "random",
    "required": True,
    "randomType": "specified-values",
    "arrayElementType": "array"
  },
  "camList.eventName": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "eventFilter"
  },
  "camList.startTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal"
    }
  },
  "camList.endTime": {
    "valueType": "request-range",
    "required": False,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal"
    }
  }
}

# StoredVideoEventInfos
cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "camID",
    "requestRange": {
      "operator": "between"
    }
  },
  "camList.eventUUID": {
    "valueType": "random",
    "required": True,
    "randomType": "specified-values",
    "arrayElementType": "array"
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
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    }
  },
  "camList.endTime": {
    "valueType": "request-range",
    "required": False,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    }
  }
}

# StoredObjectAnalyticsInfos
cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "camID"
  },
  "camList.analyticsTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between"
    }
  },
  "camList.anlayticsResultList.analyticsClass": {
    "valueType": "request-based",
    "required": True,
    "referenceField": "classFilter"
  },
  "camList.anlayticsResultList.analyticsAttribute": {
    "valueType": "request-based",
    "required": False,
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

# PtzStatus
cmg7bve25000114cevhn5o3vr_PtzStatus_out_constraints = {}

# PtzContinuousMove
cmg7bve25000114cevhn5o3vr_PtzContinuousMove_out_constraints = {}

# PtzStop
cmg7bve25000114cevhn5o3vr_PtzStop_out_constraints = {}

# cmg7bve25000114cevhn5o3vr 검증 리스트
cmg7bve25000114cevhn5o3vr_inConstraints = [
    cmg7bve25000114cevhn5o3vr_Authentication_out_constraints,
    cmg7bve25000114cevhn5o3vr_Capabilities_out_constraints,
    cmg7bve25000114cevhn5o3vr_CameraProfiles_out_constraints,
    cmg7bve25000114cevhn5o3vr_StoredVideoInfos_out_constraints,
    cmg7bve25000114cevhn5o3vr_StreamURLs_out_constraints,
    cmg7bve25000114cevhn5o3vr_ReplayURL_out_constraints,
    cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_out_constraints,
    cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_out_constraints,
    cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_out_constraints,
    cmg7bve25000114cevhn5o3vr_PtzStatus_out_constraints,
    cmg7bve25000114cevhn5o3vr_PtzContinuousMove_out_constraints,
    cmg7bve25000114cevhn5o3vr_PtzStop_out_constraints,
]

