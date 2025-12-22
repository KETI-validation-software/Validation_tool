# Authentication
cmii7wfuf006i8z1tcds6q69g_Authentication_in_constraints = {
  "userID": {
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "valueType": "preset",
    "required": True
  }
}

# cmii7wfuf006i8z1tcds6q69g 검증 리스트
cmii7wfuf006i8z1tcds6q69g_inConstraints = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_in_constraints,
]

# Authentication
cmii7w683006h8z1t7usnin5g_Authentication_in_constraints = {
  "userID": {
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "valueType": "preset",
    "required": True
  }
}

# cmii7w683006h8z1t7usnin5g 검증 리스트
cmii7w683006h8z1t7usnin5g_inConstraints = [
    cmii7w683006h8z1t7usnin5g_Authentication_in_constraints,
]

# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_in_constraints = {
  "userID": {
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_in_constraints = {}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_constraints = {}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_constraints = {
  "camList": {
    "valueType": "preset",
    "required": True,
    "arrayElementType": "object"
  },
  "streamProtocolType": {
    "valueType": "preset",
    "required": True
  }
}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_constraints = {
  "camList": {
    "valueType": "preset",
    "required": True,
    "arrayElementType": "object"
  },
  "duration": {
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "valueType": "preset",
    "required": True
  },
  "eventFilter": {
    "valueType": "preset",
    "required": False
  },
  "classFilter": {
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "valueType": "preset",
    "required": False
  }
}

# RealtimeVideoEventInfos WebHook OUT Constraints
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints = {}

# cmii7v8pr006g8z1tvo55a50u 검증 리스트
cmii7v8pr006g8z1tvo55a50u_inConstraints = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_constraints,
]

# cmii7v8pr006g8z1tvo55a50u WebHook Constraints 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_outConstraints = [
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints,
]

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

# cmii7pysb004k8z1tts0npxfm 검증 리스트
cmii7pysb004k8z1tts0npxfm_outConstraints = [
    cmii7pysb004k8z1tts0npxfm_Authentication_out_constraints,
    cmii7pysb004k8z1tts0npxfm_Capabilities_out_constraints,
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
    "required": False
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

# Authentication
cmiqr2b9j00i9ie8frw439h8i_Authentication_in_constraints = {
  "userID": {
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmiqr2b9j00i9ie8frw439h8i_Capabilities_in_constraints = {}

# SensorDeviceProfiles
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_in_constraints = {}

# cmiqr2b9j00i9ie8frw439h8i 검증 리스트
cmiqr2b9j00i9ie8frw439h8i_inConstraints = [
    cmiqr2b9j00i9ie8frw439h8i_Authentication_in_constraints,
    cmiqr2b9j00i9ie8frw439h8i_Capabilities_in_constraints,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_in_constraints,
]

