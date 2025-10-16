# Authentication
cmgatbdp000bqihlexmywusvq_Authentication_out_validation = {}

# Capabilities
cmgatbdp000bqihlexmywusvq_Capabilities_out_validation = {}

# SensorDeviceProfiles
cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_out_validation = {}

# RealtimeSensorData
cmgatbdp000bqihlexmywusvq_RealtimeSensorData_out_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "sensorDeviceID"
  },
  "sensorDeviceList.measureTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "greater-equal",
    "referenceEndpointMin": "/RealtimeSensorData"
  }
}

# RealtimeSensorEventInfos
cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_out_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "sensorDeviceID"
  },
  "sensorDeviceList.eventName": {
    "score": 1,
    "enabled": True,
    "referenceField": "eventFilter",
    "validationType": "request-field-match",
    "referenceEndpoint": "/RealtimeSensorEventInfos"
  },
  "sensorDeviceList.eventTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "greater-equal",
    "referenceEndpointMin": "/RealtimeSensorEventInfos"
  }
}

# StoredSensorEventInfos
cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_out_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "sensorDeviceID"
  },
  "sensorDeviceList.eventName": {
    "score": 1,
    "enabled": True,
    "referenceField": "eventFilter",
    "validationType": "request-field-match",
    "referenceEndpoint": "/StoredSensorEventInfos"
  },
  "sensorDeviceList.eventTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between"
  }
}

# SensorDeviceControl
cmgatbdp000bqihlexmywusvq_SensorDeviceControl_out_validation = {
  "sensorDeviceID": {
    "enabled": True,
    "referenceField": "sensorDeviceID",
    "validationType": "request-field-match",
    "referenceEndpoint": "/SensorDeviceControl"
  },
  "sensorDeviceStatus": {
    "enabled": True,
    "referenceField": "commandType",
    "validationType": "request-field-match",
    "referenceEndpoint": "/SensorDeviceControl"
  }
}

# cmgatbdp000bqihlexmywusvq 검증 리스트
cmgatbdp000bqihlexmywusvq_outValidation = [
    cmgatbdp000bqihlexmywusvq_Authentication_out_validation,
    cmgatbdp000bqihlexmywusvq_Capabilities_out_validation,
    cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_out_validation,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorData_out_validation,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_out_validation,
    cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_out_validation,
    cmgatbdp000bqihlexmywusvq_SensorDeviceControl_out_validation,
]

# Authentication
cmgasj98w009aihlezm0fe6cs_Authentication_out_validation = {}

# Capabilities
cmgasj98w009aihlezm0fe6cs_Capabilities_out_validation = {}

# DoorProfiles
cmgasj98w009aihlezm0fe6cs_DoorProfiles_out_validation = {}

# AccessUserInfos
cmgasj98w009aihlezm0fe6cs_AccessUserInfos_out_validation = {
  "userList.doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "/AccessUserInfos"
  }
}

# RealtimeVerifEventInfos
cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_out_validation = {
  "doorList.eventTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "greater-equal",
    "referenceEndpointMin": "/RealtimeVerifEventInfos"
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "/RealtimeVerifEventInfos"
  },
  "doorList.eventName": {
    "enabled": True,
    "referenceField": "eventFilter",
    "validationType": "request-field-match",
    "referenceEndpoint": "/RealtimeVerifEventInfos"
  }
}

# StoredVerifEventInfos
cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_out_validation = {
  "doorList.eventTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/StoredVerifEventInfos",
    "referenceEndpointMax": "/StoredVerifEventInfos"
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "/StoredVerifEventInfos"
  },
  "doorList.eventName": {
    "enabled": True,
    "referenceField": "eventFilter",
    "validationType": "request-field-match",
    "referenceEndpoint": "/StoredVerifEventInfos"
  }
}

# RealtimeDoorStatus
cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_out_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "/RealtimeDoorStatus"
  }
}

# DoorControl
cmgasj98w009aihlezm0fe6cs_DoorControl_out_validation = {}

# cmgasj98w009aihlezm0fe6cs 검증 리스트
cmgasj98w009aihlezm0fe6cs_outValidation = [
    cmgasj98w009aihlezm0fe6cs_Authentication_out_validation,
    cmgasj98w009aihlezm0fe6cs_Capabilities_out_validation,
    cmgasj98w009aihlezm0fe6cs_DoorProfiles_out_validation,
    cmgasj98w009aihlezm0fe6cs_AccessUserInfos_out_validation,
    cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_out_validation,
    cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_out_validation,
    cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_out_validation,
    cmgasj98w009aihlezm0fe6cs_DoorControl_out_validation,
]

# Authentication
cmga0l5mh005dihlet5fcoj0o_Authentication_out_validation = {}

# Capabilities
cmga0l5mh005dihlet5fcoj0o_Capabilities_out_validation = {}

# CameraProfiles
cmga0l5mh005dihlet5fcoj0o_CameraProfiles_out_validation = {}

# StoredVideoInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_out_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StoredVideoInfos"
  },
  "camList.timeList.startTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceEndpointMax": "/StoredVideoInfos"
  },
  "camList.timeList.endTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceEndpointMax": "/StoredVideoInfos"
  },
  "camID2": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StoredVideoInfos"
  }
}

# StreamURLs
cmga0l5mh005dihlet5fcoj0o_StreamURLs_out_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StreamURLs"
  },
  "camList.camURL": {
    "score": 1,
    "enabled": True,
    "urlField": "camURL",
    "validationType": "url-video"
  }
}

# ReplayURL
cmga0l5mh005dihlet5fcoj0o_ReplayURL_out_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/ReplayURL"
  },
  "camList.startTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/ReplayURL",
    "referenceEndpointMax": "/ReplayURL"
  },
  "camList.endTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/ReplayURL",
    "referenceEndpointMax": "/ReplayURL"
  },
  "camList.camURL": {
    "score": 1,
    "enabled": True,
    "urlField": "camURL",
    "validationType": "url-video"
  }
}

# RealtimeVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_RealtimeVideoEventInfos_out_validation = {}

# StoredVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_out_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StoredVideoEventInfos"
  },
  "camList.eventName": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "eventFilter",
    "referenceEndpoint": "/StoredVideoEventInfos"
  },
  "camList.startTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceEndpointMax": "/StoredVideoEventInfos"
  },
  "camList.endTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceEndpointMax": "/StoredVideoEventInfos"
  }
}

# StoredObjectAnalyticsInfos
cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_out_validation = {
  "camList.camID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos"
  },
  "camList.analyticsTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/StoredObjectAnalyticsInfos",
    "referenceEndpointMax": "/StoredObjectAnalyticsInfos"
  },
  "camList.anlayticsResultList.analyticsClass": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "classFilter",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos"
  },
  "camList.anlayticsResultList.analyticsAttribute": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "attributeFilter",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos"
  }
}

# PtzStatus
cmga0l5mh005dihlet5fcoj0o_PtzStatus_out_validation = {}

# PtzContinuousMove
cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_out_validation = {}

# PtzStop
cmga0l5mh005dihlet5fcoj0o_PtzStop_out_validation = {}

# cmga0l5mh005dihlet5fcoj0o 검증 리스트
cmga0l5mh005dihlet5fcoj0o_outValidation = [
    cmga0l5mh005dihlet5fcoj0o_Authentication_out_validation,
    cmga0l5mh005dihlet5fcoj0o_Capabilities_out_validation,
    cmga0l5mh005dihlet5fcoj0o_CameraProfiles_out_validation,
    cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_out_validation,
    cmga0l5mh005dihlet5fcoj0o_StreamURLs_out_validation,
    cmga0l5mh005dihlet5fcoj0o_ReplayURL_out_validation,
    cmga0l5mh005dihlet5fcoj0o_RealtimeVideoEventInfos_out_validation,
    cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_out_validation,
    cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_out_validation,
    cmga0l5mh005dihlet5fcoj0o_PtzStatus_out_validation,
    cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_out_validation,
    cmga0l5mh005dihlet5fcoj0o_PtzStop_out_validation,
]

