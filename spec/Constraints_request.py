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
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_in_constraints = {}

# RealtimeVideoEventInfos WebHook OUT Constraints
cmgyv3rzl014nvsveidu5jpzp_RealtimeVideoEventInfos_webhook_out_constraints = {
  "camList.camID": {
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID",
    "validation": {
      "enabled": False,
      "validationType": "specified-value-match"
    }
  },
  "eventFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "eventFilter",
    "validValues": [
      "화재",
      "배회"
    ],
    "validation": {
      "enabled": False,
      "validationType": "specified-value-match"
    }
  },
  "classFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "classFilter",
    "validValues": [
      "사람",
      "트럭",
      "버스"
    ],
    "validation": {
      "enabled": False,
      "validationType": "specified-value-match"
    }
  }
}

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
      "배회"
    ]
  },
  "classFilter": {
    "valueType": "random",
    "required": False,
    "validValueField": "classFilter",
    "validValues": [
      "사람",
      "트럭",
      "버스"
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

