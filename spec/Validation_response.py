# Authentication
cmgatbdp000bqihlexmywusvq_Authentication_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userName": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userAff": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "accessToken": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# Capabilities
cmgatbdp000bqihlexmywusvq_Capabilities_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transportSupport": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transportSupport.transProtocolType": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transportSupport.transProtocolDesc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# SensorDeviceProfiles
cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceID": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceType": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceName": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceLoc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceLoc.lon": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceLoc.lat": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceLoc.alt": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceLoc.desc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# RealtimeSensorData
cmgatbdp000bqihlexmywusvq_RealtimeSensorData_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl"
  },
  "sensorDeviceList.measureTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "greater-equal",
    "referenceEndpointMin": "/RealtimeSensorData"
  },
  "sensorDeviceList.sensorDeviceType": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceUnit": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceValue": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# RealtimeSensorEventInfos
cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl"
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
    "referenceEndpointMin": "/RealtimeSensorData"
  },
  "sensorDeviceList.eventDesc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredSensorEventInfos
cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "sensorDeviceList.sensorDeviceID": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl"
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
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/RealtimeSensorData"
  },
  "sensorDeviceList.eventDesc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# SensorDeviceControl
cmgatbdp000bqihlexmywusvq_SensorDeviceControl_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
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
cmgasj98w009aihlezm0fe6cs_Authentication_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userName": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userAff": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "accessToken": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# Capabilities
cmgasj98w009aihlezm0fe6cs_Capabilities_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transportSupport": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transportSupport.transProtocolType": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transportSupport.transProtocolDesc": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# DoorProfiles
cmgasj98w009aihlezm0fe6cs_DoorProfiles_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorName": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorRelayStatus": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorSensor": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorLoc": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorLoc.lon": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorLoc.lat": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorLoc.alt": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorLoc.desc": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.bioDeviceList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.bioDeviceList.bioDeviceID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.bioDeviceList.bioDeviceName": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.bioDeviceList.bioDeviceAuthTypeList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.otherDeviceList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.otherDeviceList.otherDeviceID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.otherDeviceList.otherDeviceName": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.otherDeviceList.otherDeviceAuthTypeList": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# AccessUserInfos
cmgasj98w009aihlezm0fe6cs_AccessUserInfos_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userList.userID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userList.userName": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userList.userDesc": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userList.doorList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userList.doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "/RealtimeVerifEventInfos"
  },
  "userList.doorList.timePeriod": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userList.doorList.timePeriod.startTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userList.doorList.timePeriod.endTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# RealtimeVerifEventInfos
cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
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
  "doorList.userID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.bioAuthTypeList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.otherAuthTypeList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.eventName": {
    "enabled": True,
    "referenceField": "eventFilter",
    "validationType": "request-field-match",
    "referenceEndpoint": "/RealtimeVerifEventInfos"
  },
  "doorList.eventDesc": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredVerifEventInfos
cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.eventTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/RealtimeVerifEventInfos",
    "referenceEndpointMax": "/StoredVerifEventInfos"
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "/RealtimeVerifEventInfos"
  },
  "doorList.userID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.bioAuthTypeList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.otherAuthTypeList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.eventName": {
    "enabled": True,
    "referenceField": "eventFilter",
    "validationType": "request-field-match",
    "referenceEndpoint": "/RealtimeVerifEventInfos"
  },
  "doorList.eventDesc": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# RealtimeDoorStatus
cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "doorID",
    "referenceEndpoint": "/RealtimeVerifEventInfos"
  },
  "doorList.doorName": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorRelaySensor": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "doorList.doorSensor": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# DoorControl
cmgasj98w009aihlezm0fe6cs_DoorControl_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

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
cmga0l5mh005dihlet5fcoj0o_Authentication_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userName": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "userAff": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "accessToken": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# Capabilities
cmga0l5mh005dihlet5fcoj0o_Capabilities_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "streamingSupport": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "streamingSupport.streamProtocolType": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "streamingSupport.streamProtocolDesc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transportSupport": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transportSupport.transProtocolType": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "transportSupport.transProtocolDesc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# CameraProfiles
cmga0l5mh005dihlet5fcoj0o_CameraProfiles_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
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
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camName": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camLoc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camLoc.lon": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camLoc.lat": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camLoc.alt": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camLoc.desc": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camConfig": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camConfig.camType": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredVideoInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
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
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StoredVideoInfos",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoInfos"
  },
  "camList.timeList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.timeList.startTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoInfos",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceRangeOperator": "between"
  },
  "camList.timeList.endTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoInfos",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceRangeOperator": "between"
  }
}

# StreamURLs
cmga0l5mh005dihlet5fcoj0o_StreamURLs_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
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
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/PtzStatus"
  },
  "camList.accessID": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.accessPW": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camURL": {
    "score": 1,
    "enabled": True,
    "urlField": "camURL",
    "validationType": "url-video"
  },
  "camList.videoInfo": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.resolution": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.fps": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.videoCodec": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.audioCodec": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# ReplayURL
cmga0l5mh005dihlet5fcoj0o_ReplayURL_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.accessID": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.accessPW": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.startTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoInfos",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceRangeOperator": "between"
  },
  "camList.endTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoInfos",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceRangeOperator": "between"
  },
  "camList.camURL": {
    "score": 1,
    "enabled": True,
    "urlField": "camURL",
    "validationType": "url-video"
  },
  "camList.videoInfo": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.resolution": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.fps": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.videoCodec": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.audioCodec": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoInfos",
    "referenceEndpoint": "/StoredVideoInfos"
  }
}

# RealtimeVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_RealtimeVideoEventInfos_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
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
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoEventInfos"
  },
  "camList.eventUUID": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.eventName": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceListField": "eventFilter",
    "referenceListEndpoint": "/StoredVideoEventInfos"
  },
  "camList.startTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceRangeOperator": "between"
  },
  "camList.endTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceRangeOperator": "between"
  },
  "camList.eventDesc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredObjectAnalyticsInfos
cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
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
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceEndpoint": "/PtzStatus"
  },
  "camList.analyticsTime": {
    "score": 1,
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceRangeOperator": "between",
    "referenceEndpointMin": "/RealtimeVideoEventInfos",
    "referenceEndpointMax": "/RealtimeVideoEventInfos"
  },
  "camList.anlayticsResultList": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.anlayticsResultList.anayticsID": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
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
  },
  "camList.anlayticsResultList.analyticsConfidence": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.anlayticsResultList.analyticsBoundingBox": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.anlayticsResultList.analyticsBoundingBox.left": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.anlayticsResultList.analyticsBoundingBox.top": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.anlayticsResultList.analyticsBoundingBox.right": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.anlayticsResultList.analyticsBoundingBox.bottom": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.anlayticsResultList.analyticsDesc": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# PtzStatus
cmga0l5mh005dihlet5fcoj0o_PtzStatus_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "position": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "position.pan": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "position.tilt": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "position.zoom": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "moveStatus": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "moveStatus.pan": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "moveStatus.tilt": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "moveStatus.zoom": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# PtzContinuousMove
cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# PtzStop
cmga0l5mh005dihlet5fcoj0o_PtzStop_out_validation = {
  "code": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "score": 1,
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

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

