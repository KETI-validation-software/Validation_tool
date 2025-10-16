# Authentication
cmgatbdp000bqihlexmywusvq_Authentication_out_constraints = {}

# Capabilities
cmgatbdp000bqihlexmywusvq_Capabilities_out_constraints = {}

# SensorDeviceProfiles
cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_out_constraints = {}

# RealtimeSensorData
cmg90br3n002qihleffuljnth_RealtimeSensorData_out_constraints = {
  "sensorDeviceList.sensorDeviceID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeSensorData",
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
cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_out_constraints = {}

# StoredSensorEventInfos
cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_out_constraints = {}

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
cmgasj98w009aihlezm0fe6cs_Authentication_out_constraints = {}

# Capabilities
cmgasj98w009aihlezm0fe6cs_Capabilities_out_constraints = {}

# DoorProfiles
cmgasj98w009aihlezm0fe6cs_DoorProfiles_out_constraints = {}

# AccessUserInfos
cmgasj98w009aihlezm0fe6cs_AccessUserInfos_out_constraints = {}

# RealtimeVerifEventInfos
cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_out_constraints = {}

# StoredVerifEventInfos
cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_out_constraints = {}

# RealtimeDoorStatus
cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_out_constraints = {}

# DoorControl
cmgasj98w009aihlezm0fe6cs_DoorControl_out_constraints = {}

# cmgasj98w009aihlezm0fe6cs 검증 리스트
cmgasj98w009aihlezm0fe6cs_inConstraints = [
    cmgasj98w009aihlezm0fe6cs_Authentication_out_constraints,
    cmgasj98w009aihlezm0fe6cs_Capabilities_out_constraints,
    cmgasj98w009aihlezm0fe6cs_DoorProfiles_out_constraints,
    cmgasj98w009aihlezm0fe6cs_AccessUserInfos_out_constraints,
    cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_out_constraints,
    cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_out_constraints,
    cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_out_constraints,
    cmgasj98w009aihlezm0fe6cs_DoorControl_out_constraints,
]

# Authentication
cmga0l5mh005dihlet5fcoj0o_Authentication_out_constraints = {}

# Capabilities
cmga0l5mh005dihlet5fcoj0o_Capabilities_out_constraints = {}

# CameraProfiles
cmga0l5mh005dihlet5fcoj0o_CameraProfiles_out_constraints = {}

# StoredVideoInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_out_constraints = {}

# StreamURLs
cmga0l5mh005dihlet5fcoj0o_StreamURLs_out_constraints = {}

# ReplayURL
cmga0l5mh005dihlet5fcoj0o_ReplayURL_out_constraints = {}


# StoredVideoEventInfos
cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoEventInfos",
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


# StoredObjectAnalyticsInfos
cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_out_constraints = {}

# PtzStatus
cmga0l5mh005dihlet5fcoj0o_PtzStatus_out_constraints = {}

# PtzContinuousMove
cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_out_constraints = {}

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
    cmg7bve25000114cevhn5o3vr_StoredVideoEventInfos_out_constraints,
    cmg7bve25000114cevhn5o3vr_RealtimeVideoEventInfos_out_constraints,
    cmg7bve25000114cevhn5o3vr_StoredObjectAnalyticsInfos_out_constraints,
    cmg7bve25000114cevhn5o3vr_PtzStatus_out_constraints,
    cmg7bve25000114cevhn5o3vr_PtzContinuousMove_out_constraints,
    cmg7bve25000114cevhn5o3vr_PtzStop_out_constraints,

]

