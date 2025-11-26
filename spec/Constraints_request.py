# Authentication
cmh1ua7b00021gxc3rjepbkrm_Authentication_in_constraints = {}

# DoorProfiles
cmh1ua7b00021gxc3rjepbkrm_DoorProfiles_in_constraints = {}

# RealtimeDoorStatus
cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_in_constraints = {
  "doorList.doorID": {
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorID"
  },
  "transProtocol.transProtocolDesc": {
    "valueType": "test-time",
    "required": True
  }
}

# RealtimeDoorStatus WebHook OUT Constraints
cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_webhook_out_constraints = {}

# DoorControl
cmh1ua7b00021gxc3rjepbkrm_DoorControl_in_constraints = {
  "doorID": {
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorID"
  },
  "commandType": {
    "valueType": "random",
    "required": True,
    "randomType": "exclude-value",
    "validValueField": "eventFilter_bio",
    "validValues": [
      "Lock",
      "UnLock"
    ],
    "validValueFieldName": "doorSensor"
  }
}

# RealtimeDoorStatus
cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_in_constraints = {
  "doorList.doorID": {
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorID"
  },
  "transProtocol.transProtocolDesc": {
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus WebHook OUT Constraints
cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_webhook_out_constraints = {}

# cmh1ua7b00021gxc3rjepbkrm 검증 리스트
cmh1ua7b00021gxc3rjepbkrm_inConstraints = [
    cmh1ua7b00021gxc3rjepbkrm_Authentication_in_constraints,
    cmh1ua7b00021gxc3rjepbkrm_DoorProfiles_in_constraints,
    cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_in_constraints,
    cmh1ua7b00021gxc3rjepbkrm_DoorControl_in_constraints,
    cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_in_constraints,
]

# cmh1ua7b00021gxc3rjepbkrm WebHook Constraints 리스트
cmh1ua7b00021gxc3rjepbkrm_webhook_outConstraints = [
    cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_webhook_out_constraints,
    cmh1ua7b00021gxc3rjepbkrm_RealtimeDoorStatus_webhook_out_constraints,
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

