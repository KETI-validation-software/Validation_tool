# RealtimeVideoEventInfos
cmh1u5pef000sgxc3bzl4y9v0_RealtimeVideoEventInfos_out_constraints = {}

# RealtimeVideoEventInfos WebHook IN Constraints
cmh1u5pef000sgxc3bzl4y9v0_RealtimeVideoEventInfos_webhook_in_constraints = {}

# cmh1u5pef000sgxc3bzl4y9v0 검증 리스트
cmh1u5pef000sgxc3bzl4y9v0_outConstraints = [
    cmh1u5pef000sgxc3bzl4y9v0_RealtimeVideoEventInfos_out_constraints,
]

# cmh1u5pef000sgxc3bzl4y9v0 WebHook Constraints 리스트
cmh1u5pef000sgxc3bzl4y9v0_webhook_inConstraints = [
    cmh1u5pef000sgxc3bzl4y9v0_RealtimeVideoEventInfos_webhook_in_constraints,
]

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
    "requestRangeMaxEndpoint": "/RealtimeVideoEventInfos"
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
    "requestRangeMaxEndpoint": "/RealtimeVideoEventInfos"
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

# RealtimeVideoEventInfos WebHook IN Constraints
cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_webhook_in_constraints = {
  "camList.camID": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "referenceField": "camID"
  },
  "eventFilter": {
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "referenceField": "eventFilter"
  }
}

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
cmgvieyak001b6cd04cgaawmm_outConstraints = [
    cmgvieyak001b6cd04cgaawmm_Authentication_out_constraints,
    cmgvieyak001b6cd04cgaawmm_Capabilities_out_constraints,
    cmgvieyak001b6cd04cgaawmm_CameraProfiles_out_constraints,
    cmgvieyak001b6cd04cgaawmm_StoredVideoInfos_out_constraints,
    cmgvieyak001b6cd04cgaawmm_StreamURLs_out_constraints,
    cmgvieyak001b6cd04cgaawmm_ReplayURL_out_constraints,
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_out_constraints,
    cmgvieyak001b6cd04cgaawmm_StoredVideoEventInfos_out_constraints,
]

# cmgvieyak001b6cd04cgaawmm WebHook Constraints 리스트
cmgvieyak001b6cd04cgaawmm_webhook_inConstraints = [
    cmgvieyak001b6cd04cgaawmm_RealtimeVideoEventInfos_webhook_in_constraints,
]

# Authentication
cmh1ua7b00021gxc3rjepbkrm_Authentication_in_constraints = {}

# cmh1ua7b00021gxc3rjepbkrm 검증 리스트
cmh1ua7b00021gxc3rjepbkrm_inConstraints = [
    cmh1ua7b00021gxc3rjepbkrm_Authentication_in_constraints,
]

# Authentication
cmgyv3rzl014nvsveidu5jpzp_Authentication_in_constraints = {}

# Capabilities
cmgyv3rzl014nvsveidu5jpzp_Capabilities_in_constraints = {}

# CameraProfiles
cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_in_constraints = {}

# StoredVideoInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  }
}

# StreamURLs
cmgyv3rzl014nvsveidu5jpzp_StreamURLs_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  }
}

# ReplayURL
cmgyv3rzl014nvsveidu5jpzp_ReplayURL_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  }
}

# RealtimeVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_in_constraints = {
  "camList.camID": {
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "eventFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "eventFilter",
    "validValues": [
      "화재",
      "배회",
      "침입",
      "Loitering",
      "Intrusion"
    ]
  },
  "classFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "classFilter",
    "validValues": [
      "사람",
      "트럭",
      "버스",
      "Human"
    ]
  }
}

# RealtimeVideoEventInfos WebHook OUT Constraints
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_webhook_out_constraints = {}

# StoredVideoEventInfos
cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_in_constraints = {
  "camList.camID": {
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "eventFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "eventFilter",
    "validValues": [
      "화재",
      "배회",
      "침입",
      "Loitering",
      "Intrusion"
    ]
  },
  "classFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "classFilter",
    "validValues": [
      "사람",
      "트럭",
      "버스",
      "Human"
    ]
  }
}

# cmgyv3rzl014nvsveidu5jpzp 검증 리스트
cmgyv3rzl014nvsveidu5jpzp_inConstraints = [
    cmgyv3rzl014nvsveidu5jpzp_Authentication_in_constraints,
    cmgyv3rzl014nvsveidu5jpzp_Capabilities_in_constraints,
    cmgyv3rzl014nvsveidu5jpzp_CameraProfiles_in_constraints,
    cmgyv3rzl014nvsveidu5jpzp_StoredVideoInfos_in_constraints,
    cmgyv3rzl014nvsveidu5jpzp_StreamURLs_in_constraints,
    cmgyv3rzl014nvsveidu5jpzp_ReplayURL_in_constraints,
    cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_in_constraints,
    cmgyv3rzl014nvsveidu5jpzp_StoredVideoEventInfos_in_constraints,
]

# cmgyv3rzl014nvsveidu5jpzp WebHook Constraints 리스트
cmgyv3rzl014nvsveidu5jpzp_webhook_outConstraints = [
    cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_webhook_out_constraints,
]

