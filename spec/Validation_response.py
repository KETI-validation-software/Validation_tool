# Authentication
cmgyv3rzl014nvsveidu5jpzp_Authentication_out_validation = {}

# Capabilities
cmgyv3rzl014nvsveidu5jpzp_Capabilities_out_validation = {}

# CameraProfiles
cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_out_validation = {}

# StoredVideoInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoInfos",
    "referenceEndpoint": "/StoredVideoInfos"
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
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StreamURLs",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StreamURLs"
  }
}

# ReplayURL
cmgyv3rzl014nvsveidu5jpzp_ReplayURL_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/ReplayURL",
    "referenceEndpoint": "/ReplayURL"
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
  }
}

# StoredVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoEventInfos"
  },
  "camList.eventName": {
    "enabled": True,
    "referenceField": "eventFilter",
    "validationType": "request-field-match",
    "referenceEndpoint": "/StoredVideoEventInfos"
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceRangeOperator": "between"
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceRangeOperator": "between"
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
    cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_out_validation,
]

