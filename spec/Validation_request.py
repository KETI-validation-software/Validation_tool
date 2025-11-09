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
    "referenceEndpoint": "/StoredVideoInfos",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoInfos",
    "score": 0
  },
  "camList.timeList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoInfos",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceRangeOperator": "between",
    "score": 0
  },
  "camList.timeList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoInfos",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceRangeOperator": "between",
    "score": 0
  }
}

# StreamURLs
cmgyv3rzl014nvsveidu5jpzp_StreamURLs_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StreamURLs",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StreamURLs",
    "score": 0
  },
  "camList.camURL": {
    "enabled": True,
    "urlField": "camURL",
    "validationType": "url-video",
    "referenceEndpoint": "/StreamURLs",
    "score": 0
  }
}

# ReplayURL
cmgyv3rzl014nvsveidu5jpzp_ReplayURL_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/ReplayURL",
    "referenceListField": "camID",
    "referenceListEndpoint": "/ReplayURL",
    "score": 0
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/RealtimeVideoEventInfos",
    "referenceEndpointMin": "/RealtimeVideoEventInfos",
    "referenceRangeOperator": "between",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/RealtimeVideoEventInfos",
    "referenceEndpointMin": "/RealtimeVideoEventInfos",
    "referenceRangeOperator": "between",
    "score": 0
  }
}

# RealtimeVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_out_validation = {}

# StoredVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceListField": "camID",
    "referenceListEndpoint": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.eventName": {
    "enabled": True,
    "referenceField": "eventFilter",
    "validationType": "request-field-match",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceRangeOperator": "between",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "referenceFieldMax": "endTime",
    "referenceFieldMin": "startTime",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceRangeOperator": "between",
    "score": 0
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

# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_in_validation = {}

# Capabilities
cmgvieyak001b6cd04cgaawmm_Capabilities_in_validation = {}

# CameraProfiles
cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_validation = {}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# StreamURLs
cmgvieyak001b6cd04cgaawmm_StreamURLs_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# ReplayURL
cmgvieyak001b6cd04cgaawmm_ReplayURL_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# RealtimeVideoEventInfos
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_validation = {}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceListField": "camID",
    "referenceListEndpoint": "/CameraProfiles",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  },
  "classFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equalsAny",
    "validValueFieldName": "classFilter",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "사람",
      "트럭",
      "버스"
    ],
    "score": 0
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueOperator": "equalsAny",
    "validValueFieldName": "eventFilter",
    "validValueMatchType": "validation-field",
    "allowedValues": [
      "화재",
      "배회"
    ],
    "score": 0
  }
}

# cmgvieyak001b6cd04cgaawmm 검증 리스트
cmgvieyak001b6cd04cgaawmm_inValidation = [
    cmgvieyak001b6cd04cgaawmm_Authentication_in_validation,
    cmgvieyak001b6cd04cgaawmm_Capabilities_in_validation,
    cmgvieyak001b6cd04cgaawmm_CameraProfiles_in_validation,
    cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_in_validation,
    cmgvieyak001b6cd04cgaawmm_StreamURLs_in_validation,
    cmgvieyak001b6cd04cgaawmm_ReplayURL_in_validation,
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_in_validation,
    cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_in_validation,
]

