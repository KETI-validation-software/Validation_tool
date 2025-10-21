# Authentication
cmgvieyak001b6cd04cgaawmm_Authentication_out_constraints = {}

# Capabilities
cmgvieyak001b6cd04cgaawmm_Capabilities_out_constraints = {}

# CameraProfiles
cmgvieyak001b6cd04cgaawmm_CameraProfiles_out_constraints = {}

# StoredVideoInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoInfos",
    "referenceField": "camID"
  },
  "camList.timeList.startTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between",
      "minEndpoint": "/StoredVideoInfos"
    },
    "requestRangeMinEndpoint": "/StoredVideoInfos",
    "requestRangeMaxEndpoint": "/StoredVideoInfos"
  },
  "camList.timeList.endTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between",
      "minEndpoint": "/StoredVideoInfos"
    },
    "requestRangeMinEndpoint": "/StoredVideoInfos",
    "requestRangeMaxEndpoint": "/StoredVideoInfos"
  }
}

# StreamURLs
cmgvieyak001b6cd04cgaawmm_StreamURLs_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StreamURLs",
    "referenceField": "camID"
  }
}

# ReplayURL
cmgvieyak001b6cd04cgaawmm_ReplayURL_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/ReplayURL",
    "referenceField": "camID"
  },
  "camList.startTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between",
      "maxEndpoint": "/ReplayURL",
      "minEndpoint": "/ReplayURL"
    },
    "requestRangeMinEndpoint": "/ReplayURL",
    "requestRangeMaxEndpoint": "/ReplayURL"
  },
  "camList.endTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "operator": "between",
      "maxEndpoint": "/ReplayURL",
      "minEndpoint": "/ReplayURL"
    },
    "requestRangeMinEndpoint": "/ReplayURL",
    "requestRangeMaxEndpoint": "/ReplayURL"
  }
}

# RealtimeVideoEventInfos
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_out_constraints = {}

# StoredVideoEventInfos
cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_out_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceField": "camID"
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
      "minField": "startTime",
      "operator": "greater-equal",
      "minEndpoint": "/StoredVideoEventInfos"
    },
    "requestRangeMinEndpoint": "/StoredVideoEventInfos"
  },
  "camList.endTime": {
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal",
      "minEndpoint": "/StoredVideoEventInfos"
    },
    "requestRangeMinEndpoint": "/StoredVideoEventInfos"
  }
}

# cmgvieyak001b6cd04cgaawmm 검증 리스트
cmgvieyak001b6cd04cgaawmm_inConstraints = [
    cmgvieyak001b6cd04cgaawmm_Authentication_out_constraints,
    cmgvieyak001b6cd04cgaawmm_Capabilities_out_constraints,
    cmgvieyak001b6cd04cgaawmm_CameraProfiles_out_constraints,
    cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_out_constraints,
    cmgvieyak001b6cd04cgaawmm_StreamURLs_out_constraints,
    cmgvieyak001b6cd04cgaawmm_ReplayURL_out_constraints,
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_out_constraints,
    cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_out_constraints,
]

