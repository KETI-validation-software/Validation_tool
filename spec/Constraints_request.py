# Authentication
cmii7wfuf006i8z1tcds6q69g_Authentication_in_constraints = {
  "userID": {
    "id": "cmii82ahs008x8z1thvfawwei",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmii82ahs008z8z1tvxy4vzwn",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmii7wfuf006i8z1tcds6q69g_Capabilities_in_constraints = {}

# SensorDeviceProfiles
cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_in_constraints = {}

# RealtimeSensorData
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_in_constraints = {
  "sensorDeviceList": {
    "id": "cmiwuxvlq0cizp0028r08c7eg",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmiwuxvls0cj1p002zte0s84o",
    "referenceFieldId": "cmiwtqkuz0bnop0021598be5a",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceProfiles",
    "referenceField": "sensorDeviceID"
  },
  "duration": {
    "id": "cmiwuwqka0cbqp002qx42j8x7",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmiwux3lm0cdpp002n1c75w5l",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmiwuxd090cfbp002sihhj47s",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmiwuxhpy0cgkp002vjpiq17v",
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "id": "cmiwuxprg0ci6p002aq1y8z2s",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeSensorData WebHook OUT Constraints
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_out_constraints = {
  "code": {
    "id": "cmiwttqdg0c1kp002y3l9weoo",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwv0k5n0ddfp0023v94f65d",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_in_constraints = {
  "sensorDeviceList": {
    "id": "cmj6feinp01agxei0i4jq7q14",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmj6feinr01aixei0iwq8v8ia",
    "referenceFieldId": "cmiwtqkuz0bnop0021598be5a",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceProfiles",
    "referenceField": "sensorDeviceID"
  },
  "duration": {
    "id": "cmj6fctgn0140xei0xxeg3jq0",
    "valueType": "preset",
    "required": True
  },
  "transProtocol": {
    "id": "cmj6fcvlz014cxei08bwvc2j4",
    "valueType": "preset",
    "required": False
  },
  "transProtocol.transProtocolType": {
    "id": "cmj6fd4lb016axei0p8g5qjvz",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmj6fd608016mxei081nl2t2v",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmj6fdgsb0184xei0mr9kacqd",
    "valueType": "random",
    "required": True,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeSensorEventInfos",
    "validValueField": "sensorEvent",
    "validValues": [
      "MotionDetection",
      "Leak"
    ]
  },
  "startTime": {
    "id": "cmj6fdk4e018yxei03fzh2owz",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeSensorEventInfos WebHook OUT Constraints
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_out_constraints = {
  "code": {
    "id": "cmj6fgmz201jaxei0x0a0oeio",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmj6fgodk01jgxei0cxvcsc7x",
    "valueType": "preset",
    "required": True
  }
}

# StoredSensorEventInfos
cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_in_constraints = {
  "timePeriod": {
    "id": "cmixtuwas0dgjp002hv5tx59h",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmixtv47x0dgtp002g9gr1j6f",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmixtvivy0dh4p0026kaoqaop",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList": {
    "id": "cmixtx2dw0dlup002aj6sjed8",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmixtx2dx0dlwp002gtco28w8",
    "referenceFieldId": "cmiwtqkuz0bnop0021598be5a",
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/SensorDeviceProfiles",
    "referenceField": "sensorDeviceID"
  },
  "maxCount": {
    "id": "cmixtwo5i0dkcp00280zysdrq",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmixtwwqg0dlip002jrqkcbsv",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredSensorEventInfos",
    "validValueField": "sensorEvent",
    "validValues": [
      "MotionDetection",
      "Leak"
    ]
  }
}

# cmii7wfuf006i8z1tcds6q69g 검증 리스트
cmii7wfuf006i8z1tcds6q69g_inConstraints = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_in_constraints,
    cmii7wfuf006i8z1tcds6q69g_Capabilities_in_constraints,
    cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_in_constraints,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_in_constraints,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_in_constraints,
    cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_in_constraints,
]

# cmii7wfuf006i8z1tcds6q69g WebHook Constraints 리스트
cmii7wfuf006i8z1tcds6q69g_webhook_outConstraints = [
    None,
    None,
    None,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_out_constraints,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_out_constraints,
    None,
]

