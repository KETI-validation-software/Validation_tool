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
    "id": "cmiwuxvlw0cj7p0020pi6tbll",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmiwuxvlx0cj9p002z7xe8th8",
    "valueType": "preset",
    "required": True
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
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_webhook_out_constraints,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_out_constraints,
]

# Authentication
cmii7w683006h8z1t7usnin5g_Authentication_in_constraints = {
  "userID": {
    "id": "cmii80zrr007x8z1tf6e6uj3z",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmii80zrr007z8z1tt0cfjh2a",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmii7w683006h8z1t7usnin5g_Capabilities_in_constraints = {}

# DoorProfiles
cmii7w683006h8z1t7usnin5g_DoorProfiles_in_constraints = {}

# AccessUserInfos
cmii7w683006h8z1t7usnin5g_AccessUserInfos_in_constraints = {}

# RealtimeVerifEventInfos
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_in_constraints = {
  "doorList": {
    "id": "cmiwt9k7008svp002na1owhl9",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwt9k7208sxp002x2a5b3x3",
    "referenceFieldId": "cmiwst3fc05ohp002ocni6ynq",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorID"
  },
  "duration": {
    "id": "cmiwt8b2s08lvp002w46fm85z",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmiwt8mds08nhp002ml0f3em7",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmiwt8s7908oop002b36ni9oh",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmiwt90i808pxp002d7eykna8",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmiwt94g908r6p00262pdfkog",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "validValueField": "acEvent",
    "validValues": [
      "AuthSuccess",
      "AuthFail"
    ]
  },
  "startTime": {
    "id": "cmiwt9aqf08sfp0027rytqfgj",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeVerifEventInfos WebHook OUT Constraints
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_out_constraints = {
  "code": {
    "id": "cmiwtb4o008ubp002kpiy0iwu",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwtb79608ujp002utlpf4wa",
    "valueType": "preset",
    "required": True
  }
}

# StoredVerifEventInfos
cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_in_constraints = {
  "timePeriod": {
    "id": "cmiwtfk8h09swp0029euwvaw2",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmiwtfqcf09t6p002gr25maii",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmiwtfu0609tfp002j5q0gkl4",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmiwthcyj09y5p002062nkgud",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwthcyk09y7p002ovmv3d43",
    "referenceFieldId": "cmiwst3fc05ohp002ocni6ynq",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorID"
  },
  "maxCount": {
    "id": "cmiwtgzxs09wnp002naveumda",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmiwth4c209xkp002mm4lfebj",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredVerifEventInfos",
    "validValueField": "acEvent",
    "validValues": [
      "AuthSuccess",
      "AuthFail"
    ]
  }
}

# cmii7w683006h8z1t7usnin5g 검증 리스트
cmii7w683006h8z1t7usnin5g_inConstraints = [
    cmii7w683006h8z1t7usnin5g_Authentication_in_constraints,
    cmii7w683006h8z1t7usnin5g_Capabilities_in_constraints,
    cmii7w683006h8z1t7usnin5g_DoorProfiles_in_constraints,
    cmii7w683006h8z1t7usnin5g_AccessUserInfos_in_constraints,
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_in_constraints,
    cmii7w683006h8z1t7usnin5g_StoredVerifEventInfos_in_constraints,
]

# cmii7w683006h8z1t7usnin5g WebHook Constraints 리스트
cmii7w683006h8z1t7usnin5g_webhook_outConstraints = [
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_out_constraints,
]

# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_in_constraints = {
  "userID": {
    "id": "cmii7ym04006z8z1tr9r06hrb",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmii7ym0400718z1tyoxfj6ft",
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
    "id": "cmj17qhrx026m12s9s5t7vm2m",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmj17qhrz026o12s9jozkqym7",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "streamProtocolType": {
    "id": "cmiqtlgv700wyie8f8us68hws",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_constraints = {
  "camList": {
    "id": "cmiwrf69g0bu4844gps2e9ac1",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrf69i0bu6844g22ccsjtr",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "transProtocol": {
    "id": "cmiqtpoov00yeie8fv3h8pllf",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmiwrdzrw0bs4844gzg8kzcsq",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmiwre3fr0bt1844gwguauq4q",
    "valueType": "preset",
    "required": False
  },
  "duration": {
    "id": "cmiqtov1n00y8ie8frsppu8ev",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmiqtq1xn00ykie8fqjmg6au9",
    "valueType": "preset",
    "required": False
  },
  "classFilter": {
    "id": "cmiqtqegc00yqie8foi0sc1u9",
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "id": "cmiqtqxt400ywie8f4ir49gl1",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeVideoEventInfos WebHook OUT Constraints
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints = {
  "code": {
    "id": "cmiwrhxdj0ci0844gogcg394u",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmj1820zz02m012s9cxe2wcfn",
    "valueType": "preset",
    "required": True
  }
}

# StoredVideoInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_in_constraints = {
  "timePeriod": {
    "id": "cmiwrl7dr000knkglwk60tug6",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmiwrltxz000vnkgl3m4u2f2s",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmiwrlxaj0013nkgl40nosy7z",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmiwrn6a9003nnkglvme2ccl1",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrn6ab003pnkgl7f78y9t6",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  }
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_in_constraints = {
  "camList": {
    "id": "cmiwrtok001dknkgluevidcla",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrtok201dmnkgl6gzxhft5",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "camList.startTime": {
    "id": "cmiwrtok201donkglhwulnxos",
    "valueType": "preset",
    "required": True
  },
  "camList.endTime": {
    "id": "cmiwrtok301dqnkgl0k66p4py",
    "valueType": "preset",
    "required": True
  },
  "camList.streamProtocolType": {
    "id": "cmiwrtok301dsnkgl3t29d3op",
    "valueType": "preset",
    "required": True
  }
}

# StoredVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_in_constraints = {
  "timePeriod": {
    "id": "cmiws35o105b3nkglj38lr0hx",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmiws3ab605bknkglsndw6cp5",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmiws41yv0005p002amxfzrhq",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmiws5her00alp002y1uhjddp",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiws5hes00anp002ng50q3fc",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "maxCount": {
    "id": "cmiws4rcl005up002n2yhi3pu",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmiws56xa008jp002vhqm6yfn",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "validValueField": "videoEvent",
    "validValues": [
      "Loitering",
      "Intrusion"
    ]
  },
  "classFilter": {
    "id": "cmiws5ggr00aip0022iuh6at3",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "validValueField": "videoObject",
    "validValues": [
      "Human"
    ]
  }
}

# StoredObjectAnalyticsInfos
cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_in_constraints = {
  "timePeriod": {
    "id": "cmiws9wg801l3p002ju1o2yfi",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmiwsa3je01lnp002owjbqng1",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmiwsa57401lsp0021esg4kr1",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmiwsgzru02wyp0022uq3k278",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwsgzrw02x0p002fnxf1f08",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "filterList": {
    "id": "cmiwsgzsc02xap002gifjhi5v",
    "valueType": "preset",
    "required": False
  },
  "filterList.classFilter": {
    "id": "cmiwsgzsh02xgp002vn3dr1fq",
    "valueType": "preset",
    "required": False
  },
  "filterList.attributeFilter": {
    "id": "cmiwsgzsh02xkp002xn001108",
    "valueType": "preset",
    "required": False
  }
}

# cmii7v8pr006g8z1tvo55a50u 검증 리스트
cmii7v8pr006g8z1tvo55a50u_inConstraints = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_ReplayURL_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_in_constraints,
]

# cmii7v8pr006g8z1tvo55a50u WebHook Constraints 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_outConstraints = [
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints,
]

