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
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_in_constraints = {}

# RealtimeSensorEventInfos WebHook OUT Constraints
cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_webhook_out_constraints = {}

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
    "id": "cmixtx2dz0dlyp002akqenu1b",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmixtx2e00dm0p0028pfhtwei",
    "valueType": "preset",
    "required": True
  },
  "maxCount": {
    "id": "cmixtwo5i0dkcp00280zysdrq",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmixtwwqg0dlip002jrqkcbsv",
    "valueType": "preset",
    "required": False
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
cmii7w683006h8z1t7usnin5g_DoorProfiles_in_constraints = {
  "": {
    "id": "cmiwsoco904e1p002pqjmtdrc",
    "valueType": "preset",
    "required": True
  }
}

# AccessUserInfos
cmii7w683006h8z1t7usnin5g_AccessUserInfos_in_constraints = {}

# RealtimeVerifEventInfos
cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_in_constraints = {
  "doorList": {
    "id": "cmiwt9k7608t3p0028xpf85fa",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwt9k7708t5p002r3f7arn6",
    "valueType": "preset",
    "required": True
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
    "valueType": "preset",
    "required": False
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
    "id": "cmiwthcyl09y9p002wpikk7v0",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwthcyn09ybp002m6il7q9m",
    "valueType": "preset",
    "required": True
  },
  "maxCount": {
    "id": "cmiwtgzxs09wnp002naveumda",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmiwth4c209xkp002mm4lfebj",
    "valueType": "preset",
    "required": False
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
    "id": "cmiqtkzfm00wsie8f9qmwp4l1",
    "valueType": "preset",
    "required": True,
    "arrayElementType": "object"
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
    "id": "cmiwrf69k0bu8844g1h4w1ynp",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrf69l0bua844gymhbqwgg",
    "valueType": "preset",
    "required": True
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
  "": {
    "id": "cmiwrhxdj0ci0844gogcg394u",
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
    "id": "cmiwrn6ac003rnkglstontwxr",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrn6ae003tnkgl2p9ngmur",
    "valueType": "preset",
    "required": True
  }
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_in_constraints = {
  "camList": {
    "id": "cmiwrtokc01e4nkglvx2ptl9i",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrtoke01e6nkglueywsrx6",
    "valueType": "preset",
    "required": True
  },
  "camList.startTime": {
    "id": "cmiwrtoke01e8nkgl21unl4r9",
    "valueType": "preset",
    "required": True
  },
  "camList.endTime": {
    "id": "cmiwrtoke01eankglhefop5cq",
    "valueType": "preset",
    "required": True
  },
  "camList.streamProtocolType": {
    "id": "cmiwrtokf01ecnkgl581rzlxf",
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
    "id": "cmiws5hew00atp0027lyj4268",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiws5hex00avp0027u5iks5j",
    "valueType": "preset",
    "required": True
  },
  "maxCount": {
    "id": "cmiws4rcl005up002n2yhi3pu",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmiws56xa008jp002vhqm6yfn",
    "valueType": "preset",
    "required": False
  },
  "classFilter": {
    "id": "cmiws5ggr00aip0022iuh6at3",
    "valueType": "preset",
    "required": False
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
    "id": "cmiwsgzs102x6p002ng0c1djh",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwsgzs202x8p0028vugkp8f",
    "valueType": "preset",
    "required": True
  },
  "filterList": {
    "id": "cmiwsgzsk02xmp002crwv84aq",
    "valueType": "preset",
    "required": False
  },
  "filterList.classFilter": {
    "id": "cmiwsgzsp02xup002nt32c37q",
    "valueType": "preset",
    "required": False
  },
  "filterList.attributeFilter": {
    "id": "cmiwsgzsp02xwp002ldmr2dk6",
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

# Authentication
cmiqr2b9j00i9ie8frw439h8i_Authentication_in_constraints = {
  "userID": {
    "id": "cmise8i5a00o75vy7wdfv9o53",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmise8uar00oj5vy7z765mej6",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmiqr2b9j00i9ie8frw439h8i_Capabilities_in_constraints = {}

# SensorDeviceProfiles
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_in_constraints = {}

# SensorDeviceControl
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl_in_constraints = {
  "sensorDeviceID": {
    "id": "cmisfqqxc07ub5vy7ao1d67bu",
    "referenceFieldId": "cmises1w4031z5vy7ftbk3pc6",
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/SensorDeviceProfiles",
    "referenceField": "sensorDeviceID"
  },
  "commandType": {
    "id": "cmisfqvh407uk5vy76f9t60b7",
    "valueType": "preset",
    "required": False
  }
}

# SensorDeviceControl2
cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl2_in_constraints = {
  "sensorDeviceID": {
    "id": "cmisg8fmw08c55vy7eby9fson",
    "referenceFieldId": "cmisfqqxc07ub5vy7ao1d67bu",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID"
  },
  "commandType": {
    "id": "cmisg8hg208ca5vy7ijzfeelo",
    "referenceFieldId": "cmiwl63ld03a0844gt8vw3nsq",
    "valueType": "random",
    "required": False,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceStatus",
    "randomType": "exclude-reference-valid-values",
    "validValueField": "sensorControl",
    "validValues": [
      "AlarmOn",
      "AlarmOff"
    ]
  }
}

# cmiqr2b9j00i9ie8frw439h8i 검증 리스트
cmiqr2b9j00i9ie8frw439h8i_inConstraints = [
    cmiqr2b9j00i9ie8frw439h8i_Authentication_in_constraints,
    cmiqr2b9j00i9ie8frw439h8i_Capabilities_in_constraints,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceProfiles_in_constraints,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl_in_constraints,
    cmiqr2b9j00i9ie8frw439h8i_SensorDeviceControl2_in_constraints,
]

# Authentication
cmiqr1jha00i6ie8fb1scb3go_Authentication_in_constraints = {
  "userID": {
    "id": "cmisgv95008oh5vy7mjspm3wh",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmisgvcex08oq5vy7d84t9tts",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmiqr1jha00i6ie8fb1scb3go_Capabilities_in_constraints = {}

# DoorProfiles
cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_in_constraints = {}

# RealtimeDoorStatus
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_in_constraints = {
  "doorList": {
    "id": "cmixuqxed0h0pp002o46l6jyn",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmixuqxeg0h0rp002qq5d755o",
    "valueType": "preset",
    "required": True
  },
  "duration": {
    "id": "cmixupira0gudp0025a627ml4",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmixupvnn0gw1p002t4oynlxp",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmixuq3qa0gxmp0023qvxro6p",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmixuq6xh0gxzp002nbmk4kcc",
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "id": "cmixuqodk0h00p002xkjhnyca",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeDoorStatus WebHook OUT Constraints
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_out_constraints = {
  "code": {
    "id": "cmixussd70hbkp002351v2o5r",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmixusvcf0hbqp002tdeowl0t",
    "valueType": "preset",
    "required": True
  }
}

# DoorControl
cmiqr1jha00i6ie8fb1scb3go_DoorControl_in_constraints = {
  "doorID": {
    "id": "cmixuu5os0hc9p002st12cpzi",
    "valueType": "preset",
    "required": True
  },
  "commandType": {
    "id": "cmixuu94o0hchp002wh8j30df",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus2
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_in_constraints = {
  "doorList": {
    "id": "cmize9v8a00a096qh8bxm7fe2",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmize9v8b00a296qh1vooije0",
    "valueType": "response-based",
    "required": True,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeDoorStatus2"
  },
  "duration": {
    "id": "cmize7lki002a96qhe5181nqj",
    "valueType": "preset",
    "required": True
  },
  "transProtocol": {
    "id": "cmize811g003m96qhzuj5k87j",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmize8m4g007l96qhwaouhm9t",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmize8y8y008q96qhgmcgwvmc",
    "valueType": "preset",
    "required": True
  },
  "startTime": {
    "id": "cmize9f5s009v96qhrbr6kzd5",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus2 WebHook OUT Constraints
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_out_constraints = {
  "code": {
    "id": "cmixuyvrh0hmqp0025mr6ni0i",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmixuyy530hmzp002tlmh000j",
    "valueType": "preset",
    "required": True
  }
}

# cmiqr1jha00i6ie8fb1scb3go 검증 리스트
cmiqr1jha00i6ie8fb1scb3go_inConstraints = [
    cmiqr1jha00i6ie8fb1scb3go_Authentication_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_Capabilities_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_in_constraints,
]

# cmiqr1jha00i6ie8fb1scb3go WebHook Constraints 리스트
cmiqr1jha00i6ie8fb1scb3go_webhook_outConstraints = [
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_out_constraints,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_out_constraints,
]

# Authentication
cmiqr0kdw00i4ie8fr3firjtg_Authentication_in_constraints = {
  "userID": {
    "id": "cmish1o9m08wq5vy7wvz8a61y",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmish1r4l08wy5vy7up1s9dse",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmiqr0kdw00i4ie8fr3firjtg_Capabilities_in_constraints = {}

# CameraProfiles
cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_in_constraints = {}

# PtzStatus
cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_in_constraints = {
  "camID": {
    "id": "cmixuacz20f85p002l1xbtf6i",
    "referenceFieldId": "cmixu969h0f6lp00297drc0if",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  }
}

# PtzContinuousMove
cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_in_constraints = {
  "camID": {
    "id": "cmixuddil0fbfp00232n3befi",
    "referenceFieldId": "cmixu969h0f6lp00297drc0if",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "velocity": {
    "id": "cmixudm8a0fbop002igjf7hdo",
    "valueType": "preset",
    "required": True
  },
  "velocity.pan  ": {
    "id": "cmixudtav0fbyp002unvnsqca",
    "valueType": "preset",
    "required": False
  },
  "velocity.tilt": {
    "id": "cmixue23t0fc9p002q0o9u5ml",
    "valueType": "preset",
    "required": False
  },
  "velocity.zoom": {
    "id": "cmixueccs0fclp002h9uzky0u",
    "valueType": "preset",
    "required": False
  },
  "timeOut": {
    "id": "cmixuen0z0fcxp002zjz5mexm",
    "valueType": "preset",
    "required": False
  }
}

# PtzStop
cmiqr0kdw00i4ie8fr3firjtg_PtzStop_in_constraints = {
  "camID": {
    "id": "cmixufxre0fe1p002m1w57aeb",
    "referenceFieldId": "cmixu969h0f6lp00297drc0if",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "pan": {
    "id": "cmixugh5u0fesp0024z3tedlc",
    "valueType": "preset",
    "required": False
  },
  "tilt": {
    "id": "cmixugfb10fepp002bv1rp8qr",
    "valueType": "preset",
    "required": False
  },
  "zoom": {
    "id": "cmixugrm30ff3p002dpby0eh7",
    "valueType": "preset",
    "required": False
  }
}

# cmiqr0kdw00i4ie8fr3firjtg 검증 리스트
cmiqr0kdw00i4ie8fr3firjtg_inConstraints = [
    cmiqr0kdw00i4ie8fr3firjtg_Authentication_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_Capabilities_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStop_in_constraints,
]

