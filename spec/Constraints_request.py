# Authentication
cmgatbdp000bqihlexmywusvq_Authentication_in_constraints = {}

# Capabilities
cmgatbdp000bqihlexmywusvq_Capabilities_in_constraints = {}

# SensorDeviceProfiles
cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_in_constraints = {}

# RealtimeSensorData
cmgatbdp000bqihlexmywusvq_RealtimeSensorData_in_constraints = {}

# RealtimeSensorEventInfos
cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_in_constraints = {
  "sensorDeviceList.sensorDeviceID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID"
  },
  "eventFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "eventFilter"
  }
}

# StoredSensorEventInfos
cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_in_constraints = {
  "sensorDeviceList.sensorDeviceID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID"
  },
  "eventFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "eventFilter"
  }
}

# SensorDeviceControl
cmgatbdp000bqihlexmywusvq_SensorDeviceControl_in_constraints = {
  "sensorDeviceID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID"
  }
}

# cmgatbdp000bqihlexmywusvq 검증 리스트
cmgatbdp000bqihlexmywusvq_OutConstraints = [
    cmgatbdp000bqihlexmywusvq_Authentication_in_constraints,
    cmgatbdp000bqihlexmywusvq_Capabilities_in_constraints,
    cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_in_constraints,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorData_in_constraints,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_in_constraints,
    cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_in_constraints,
    cmgatbdp000bqihlexmywusvq_SensorDeviceControl_in_constraints,
]

# Authentication
cmgasj98w009aihlezm0fe6cs_Authentication_in_constraints = {}

# Capabilities
cmgasj98w009aihlezm0fe6cs_Capabilities_in_constraints = {}

# DoorProfiles
cmgasj98w009aihlezm0fe6cs_DoorProfiles_in_constraints = {}

# AccessUserInfos
cmgasj98w009aihlezm0fe6cs_AccessUserInfos_in_constraints = {}

# RealtimeVerifEventInfos
cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_in_constraints = {
  "eventFilter": {
    "valueType": "random",
    "required": False,
    "randomType": "valid-values",
    "validValueField": "eventFilter",
    "arrayElementType": "string"
  }
}

# StoredVerifEventInfos
cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_in_constraints = {
  "eventFilter": {
    "valueType": "random",
    "required": True,
    "validValueField": "eventFilter"
  }
}

# RealtimeDoorStatus
cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_in_constraints = {}

# DoorControl
cmgasj98w009aihlezm0fe6cs_DoorControl_in_constraints = {
  "doorID": {
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorID"
  }
}

# cmgasj98w009aihlezm0fe6cs 검증 리스트
cmgasj98w009aihlezm0fe6cs_OutConstraints = [
    cmgasj98w009aihlezm0fe6cs_Authentication_in_constraints,
    cmgasj98w009aihlezm0fe6cs_Capabilities_in_constraints,
    cmgasj98w009aihlezm0fe6cs_DoorProfiles_in_constraints,
    cmgasj98w009aihlezm0fe6cs_AccessUserInfos_in_constraints,
    cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_in_constraints,
    cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_in_constraints,
    cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_in_constraints,
    cmgasj98w009aihlezm0fe6cs_DoorControl_in_constraints,
]

# Authentication
cmga0l5mh005dihlet5fcoj0o_Authentication_in_constraints = {}

# Capabilities
cmga0l5mh005dihlet5fcoj0o_Capabilities_in_constraints = {}

# CameraProfiles
cmga0l5mh005dihlet5fcoj0o_CameraProfiles_in_constraints = {}

# StoredVideoInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/PtzStatus",
    "referenceField": "camID"
  }
}

# StreamURLs
cmga0l5mh005dihlet5fcoj0o_StreamURLs_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True
  }
}

# ReplayURL
cmga0l5mh005dihlet5fcoj0o_ReplayURL_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/PtzStatus",
    "referenceField": "camID"
  }
}

# RealtimeVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_RealtimeVideoEventInfos_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/PtzStatus",
    "referenceField": "camID"
  }
}

# StoredVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/PtzStatus",
    "referenceField": "camID"
  },
  "eventFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "eventFilter"
  },
  "classFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "classFilter"
  }
}

# StoredObjectAnalyticsInfos
cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/PtzStatus",
    "referenceField": "camID"
  },
  "filterList.classFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "classFilter"
  },
  "filterList.attributeFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "attributeFilter"
  }
}

# PtzStatus
cmga0l5mh005dihlet5fcoj0o_PtzStatus_in_constraints = {
  "camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/PtzStatus",
    "referenceField": "camID"
  }
}

# PtzContinuousMove
cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_in_constraints = {
  "camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/PtzStatus",
    "referenceField": "camID"
  }
}

# PtzStop
cmga0l5mh005dihlet5fcoj0o_PtzStop_in_constraints = {
  "camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/PtzStatus",
    "referenceField": "camID"
  }
}

# cmga0l5mh005dihlet5fcoj0o 검증 리스트
cmga0l5mh005dihlet5fcoj0o_OutConstraints = [
    cmga0l5mh005dihlet5fcoj0o_Authentication_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_Capabilities_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_CameraProfiles_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_StreamURLs_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_ReplayURL_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_RealtimeVideoEventInfos_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_PtzStatus_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_in_constraints,
    cmga0l5mh005dihlet5fcoj0o_PtzStop_in_constraints,
]

