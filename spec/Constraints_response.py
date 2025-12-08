# Authentication
cmii7shen005i8z1tagevx4qh_Authentication_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "valueType": "preset",
    "required": True
  }
}

# cmii7shen005i8z1tagevx4qh 검증 리스트
cmii7shen005i8z1tagevx4qh_outConstraints = [
    cmii7shen005i8z1tagevx4qh_Authentication_out_constraints,
]

# Authentication
cmii7pysb004k8z1tts0npxfm_Authentication_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "valueType": "preset",
    "required": False
  }
}

# Capabilities
cmii7pysb004k8z1tts0npxfm_Capabilities_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "valueType": "preset",
    "required": False
  }
}

# DoorProfiles
cmii7pysb004k8z1tts0npxfm_DoorProfiles_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "valueType": "preset",
    "required": True
  },
  "doorList.doorName": {
    "valueType": "preset",
    "required": True
  },
  "doorList.doorRelayStatus": {
    "valueType": "preset",
    "required": True
  },
  "doorList.doorSensor": {
    "valueType": "preset",
    "required": False
  },
  "doorList.doorLoc": {
    "valueType": "preset",
    "required": False
  },
  "doorList.doorLoc.lon": {
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.lat": {
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.alt": {
    "valueType": "preset",
    "required": False
  },
  "doorList.doorLoc.desc": {
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList": {
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.bioDeviceID": {
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList.bioDeviceName": {
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList.bioDeviceAuthTypeList": {
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList": {
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList.otherDeviceID": {
    "valueType": "preset",
    "required": False
  },
  "doorList.otherDeviceList.otherDeviceName": {
    "valueType": "preset",
    "required": False
  },
  "doorList.otherDeviceList.otherDeviceAuthTypeList": {
    "valueType": "preset",
    "required": True
  }
}

# cmii7pysb004k8z1tts0npxfm 검증 리스트
cmii7pysb004k8z1tts0npxfm_outConstraints = [
    cmii7pysb004k8z1tts0npxfm_Authentication_out_constraints,
    cmii7pysb004k8z1tts0npxfm_Capabilities_out_constraints,
    cmii7pysb004k8z1tts0npxfm_DoorProfiles_out_constraints,
]

# Authentication
cmii7lxbn002s8z1t1i9uudf0_Authentication_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "valueType": "preset",
    "required": False
  }
}

# Capabilities
cmii7lxbn002s8z1t1i9uudf0_Capabilities_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "streamingSupport": {
    "valueType": "preset",
    "required": True
  },
  "streamingSupport.streamProtocolType": {
    "valueType": "preset",
    "required": False
  },
  "transportSupport": {
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transportProtocolType": {
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "valueType": "preset",
    "required": False
  }
}

# CameraProfiles
cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "valueType": "preset",
    "required": True
  },
  "camList.camName": {
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc": {
    "valueType": "preset",
    "required": False
  },
  "camList.camLoc.lon": {
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.lat": {
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.alt": {
    "valueType": "preset",
    "required": False
  },
  "camList.camLoc.desc": {
    "valueType": "preset",
    "required": False
  },
  "camList.camConfig": {
    "valueType": "preset",
    "required": False
  },
  "camList.camConfig.camType": {
    "valueType": "preset",
    "required": True
  }
}

# StreamURLs
cmii7lxbn002s8z1t1i9uudf0_StreamURLs_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "valueType": "preset",
    "required": True
  },
  "camList.accessID": {
    "valueType": "preset",
    "required": False
  },
  "camList.accessPW": {
    "valueType": "preset",
    "required": False
  },
  "camList.camURL": {
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo": {
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.resolution": {
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.fps": {
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.videoCodec": {
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.audioCodec": {
    "valueType": "preset",
    "required": False
  }
}

# RealtimeVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  }
}

# RealtimeVideoEventInfos WebHook IN Constraints
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_in_constraints = {
  "camList": {
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "valueType": "preset",
    "required": True
  },
  "camList.eventUUID": {
    "valueType": "preset",
    "required": True
  },
  "camList.eventName": {
    "valueType": "preset",
    "required": True
  },
  "camList.startTime": {
    "valueType": "preset",
    "required": True
  },
  "camList.endTime": {
    "valueType": "preset",
    "required": False
  },
  "camList.eventDesc": {
    "valueType": "preset",
    "required": False
  }
}

# StoredVideoInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "valueType": "preset",
    "required": True
  },
  "camList.timeList": {
    "valueType": "preset",
    "required": True
  },
  "camList.timeList.startTime": {
    "valueType": "preset",
    "required": True
  },
  "camList.timeList.endTime": {
    "valueType": "preset",
    "required": False
  }
}

# ReplayURL
cmii7lxbn002s8z1t1i9uudf0_ReplayURL_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "valueType": "preset",
    "required": True
  },
  "camList.accessID": {
    "valueType": "preset",
    "required": False
  },
  "camList.accessPW": {
    "valueType": "preset",
    "required": False
  },
  "camList.camURL": {
    "valueType": "preset",
    "required": True
  },
  "camList.videoInfo": {
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.resolution": {
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.fps": {
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.videoCodec": {
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.audioCodec": {
    "valueType": "preset",
    "required": False
  }
}

# StoredVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "valueType": "preset",
    "required": True
  },
  "camList.eventUUID": {
    "valueType": "preset",
    "required": True
  },
  "camList.eventName": {
    "valueType": "preset",
    "required": True
  },
  "camList.startTime": {
    "valueType": "preset",
    "required": True
  },
  "camList.endTime": {
    "valueType": "preset",
    "required": False
  },
  "camList.eventDesc": {
    "valueType": "preset",
    "required": False
  }
}

# StoredObjectAnalyticsInfos
cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "valueType": "preset",
    "required": True
  },
  "camList.analyticsTime": {
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList": {
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.anayticsID": {
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsClass": {
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsAttribute": {
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsConfidence": {
    "valueType": "preset",
    "required": False
  },
  "camList.anlayticsResultList.analyticsBoundingBox": {
    "valueType": "preset",
    "required": False
  },
  "camList.anlayticsResultList.analyticsBoundingBox.left": {
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsBoundingBox.top": {
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsBoundingBox.right": {
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsBoundingBox.bottom": {
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsDesc": {
    "valueType": "preset",
    "required": False
  }
}

# cmii7lxbn002s8z1t1i9uudf0 검증 리스트
cmii7lxbn002s8z1t1i9uudf0_outConstraints = [
    cmii7lxbn002s8z1t1i9uudf0_Authentication_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_Capabilities_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_StreamURLs_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_ReplayURL_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_out_constraints,
]

# cmii7lxbn002s8z1t1i9uudf0 WebHook Constraints 리스트
cmii7lxbn002s8z1t1i9uudf0_webhook_inConstraints = [
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_in_constraints,
]

