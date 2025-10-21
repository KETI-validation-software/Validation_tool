# Authentication
cmgyv3rzl014nvsveidu5jpzp_Authentication_out_validation = {
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
cmgyv3rzl014nvsveidu5jpzp_Capabilities_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "streamingSupport": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "streamingSupport.streamProtocolType": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "streamingSupport.streamProtocolDesc": {
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

# CameraProfiles
cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": False,
    "validationType": "request-field-list-match"
  },
  "camList.camName": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camLoc": {
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
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camConfig.camType": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# StoredVideoInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoInfos",
    "referenceEndpoint": "/StoredVideoInfos"
  },
  "camList.timeList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.timeList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoInfos",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceRangeOperator": "between"
  },
  "camList.timeList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoInfos",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceRangeOperator": "between"
  }
}

# StreamURLs
cmgyv3rzl014nvsveidu5jpzp_StreamURLs_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StreamURLs",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StreamURLs"
  },
  "camList.accessID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.accessPW": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camURL": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.resolution": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.fps": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.videoCodec": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.audioCodec": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# ReplayURL
cmgyv3rzl014nvsveidu5jpzp_ReplayURL_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/ReplayURL",
    "referenceEndpoint": "/ReplayURL"
  },
  "camList.accessID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.accessPW": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/ReplayURL",
    "referenceEndpointMin": "/ReplayURL",
    "referenceRangeOperator": "between"
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/ReplayURL",
    "referenceEndpointMin": "/ReplayURL",
    "referenceRangeOperator": "between"
  },
  "camList.camURL": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.resolution": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.fps": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.videoCodec": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.videoInfo.audioCodec": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# RealtimeVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_out_validation = {
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
cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_out_validation = {
  "code": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "message": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.camID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.eventUUID": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.eventName": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.startTime": {
    "enabled": False,
    "validationType": "request-field-range-match",
    "referenceRangeOperator": "between"
  },
  "camList.endTime": {
    "enabled": False,
    "validationType": "specified-value-match"
  },
  "camList.eventDesc": {
    "enabled": False,
    "validationType": "specified-value-match"
  }
}

# cmgyv3rzl014nvsveidu5jpzp 검증 리스트
cmgyv3rzl014nvsveidu5jpzp_outValidation = [
    cmgyv3rzl014nvsveidu5jpzp_Authentication_out_validation,
    cmgyv3rzl014nvsveidu5jpzp_Capabilities_out_validation,
    cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_out_validation,
    cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_out_validation,
    cmgyv3rzl014nvsveidu5jpzp_StreamURLs_out_validation,
    cmgyv3rzl014nvsveidu5jpzp_ReplayURL_out_validation,
    cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_out_validation,
    cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_out_validation,
]

