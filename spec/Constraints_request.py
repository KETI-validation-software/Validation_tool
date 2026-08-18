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
  "camList.streamProtocolType": {
    "id": "cmjb5nmy1070zdmvoi5u22oxx",
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
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "validValueField": "videoEvent",
    "validValues": [
      "Loitering",
      "Intrusion"
    ]
  },
  "classFilter": {
    "id": "cmiqtqegc00yqie8foi0sc1u9",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "validValueField": "videoObject",
    "validValues": [
      "Human"
    ]
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

# cmii7v8pr006g8z1tvo55a50u 검증 리스트
cmii7v8pr006g8z1tvo55a50u_inConstraints = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_constraints,
]

# cmii7v8pr006g8z1tvo55a50u WebHook Constraints 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_outConstraints = [
    None,
    None,
    None,
    None,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints,
]

# Authentication
cmsmj2a0g037grc0qddx8wie2_Authentication_in_constraints = {
  "userID": {
    "id": "cmsmj2a0u037orc0qpeokownu",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmsmj2a13037qrc0qrce78i41",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmsmj2a0g037grc0qddx8wie2_Capabilities_in_constraints = {}

# SensorDeviceProfiles
cmsmj2a0g037grc0qddx8wie2_SensorDeviceProfiles_in_constraints = {}

# StoredSensorEventInfos
cmsmj2a0g037grc0qddx8wie2_StoredSensorEventInfos_in_constraints = {
  "timePeriod": {
    "id": "cmsmj2ac903cwrc0qd0bb40ia",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmsmj2acc03cyrc0qb5nucw6h",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmsmj2ace03d0rc0qpu8aha27",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList": {
    "id": "cmsmj2acj03d4rc0qn8d590d6",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmsmj2acm03d6rc0qln8u5ijy",
    "referenceFieldId": "cmsmj2a3t0390rc0q8ifdifj1",
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/SensorDeviceProfiles",
    "referenceField": "sensorDeviceID"
  },
  "maxCount": {
    "id": "cmsmj2acp03d8rc0qxlvt6r48",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmsmj2acr03darc0q13di1rio",
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

# cmsmj2a0g037grc0qddx8wie2 검증 리스트
cmsmj2a0g037grc0qddx8wie2_inConstraints = [
    cmsmj2a0g037grc0qddx8wie2_Authentication_in_constraints,
    cmsmj2a0g037grc0qddx8wie2_Capabilities_in_constraints,
    cmsmj2a0g037grc0qddx8wie2_SensorDeviceProfiles_in_constraints,
    cmsmj2a0g037grc0qddx8wie2_StoredSensorEventInfos_in_constraints,
]

# Authentication
cmsmiz4rk030drc0qgs8hvb18_Authentication_in_constraints = {
  "userID": {
    "id": "cmsmiz4rz030lrc0q7sh573cu",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmsmiz4s8030nrc0qpbbtl2vk",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmsmiz4rk030drc0qgs8hvb18_Capabilities_in_constraints = {}

# DoorProfiles
cmsmiz4rk030drc0qgs8hvb18_DoorProfiles_in_constraints = {
  "": {
    "id": "cmsmiz4un031rrc0q70dbn2l7",
    "valueType": "random",
    "required": True,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/DoorProfiles",
    "randomType": "exclude-reference-valid-values",
    "validValueField": "videoEvent",
    "validValues": [
      "Loitering",
      "Intrusion"
    ]
  }
}

# AccessUserInfos
cmsmiz4rk030drc0qgs8hvb18_AccessUserInfos_in_constraints = {}

# StoredVerifEventInfos
cmsmiz4rk030drc0qgs8hvb18_StoredVerifEventInfos_in_constraints = {
  "timePeriod": {
    "id": "cmsmiz55f036drc0qhz5p9bj6",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmsmiz55i036frc0qg5p4g2n0",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmsmiz55k036hrc0q74kv7qfm",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmsmiz55q036lrc0qcijjoyjd",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmsmiz55t036nrc0qstfwj7er",
    "referenceFieldId": "cmsmiz4v40323rc0q2bdq3h17",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorID"
  },
  "maxCount": {
    "id": "cmsmiz55v036prc0q8bz9yixk",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmsmiz55y036rrc0qvnkripmq",
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

# cmsmiz4rk030drc0qgs8hvb18 검증 리스트
cmsmiz4rk030drc0qgs8hvb18_inConstraints = [
    cmsmiz4rk030drc0qgs8hvb18_Authentication_in_constraints,
    cmsmiz4rk030drc0qgs8hvb18_Capabilities_in_constraints,
    cmsmiz4rk030drc0qgs8hvb18_DoorProfiles_in_constraints,
    cmsmiz4rk030drc0qgs8hvb18_AccessUserInfos_in_constraints,
    cmsmiz4rk030drc0qgs8hvb18_StoredVerifEventInfos_in_constraints,
]

# Authentication
cmsmhhyl502ncrc0qnjtvbt43_Authentication_in_constraints = {
  "userID": {
    "id": "cmsmhhylk02nkrc0qlwdz620j",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmsmhhylt02nmrc0q8tqoctzm",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmsmhhyl502ncrc0qnjtvbt43_Capabilities_in_constraints = {}

# CameraProfiles
cmsmhhyl502ncrc0qnjtvbt43_CameraProfiles_in_constraints = {}

# StoredVideoInfos
cmsmhhyl502ncrc0qnjtvbt43_StoredVideoInfos_in_constraints = {
  "timePeriod": {
    "id": "cmsmhrolt02tarc0qla2qvhlo",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmsmhrom602terc0qp4jpxf2w",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmsmhrom702tgrc0qlnxyg4wq",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmsmhrom702tirc0qcb7m4wl9",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmsmhrome02tkrc0qgcwrmibj",
    "valueType": "preset",
    "required": True
  }
}

# ReplayURL
cmsmhhyl502ncrc0qnjtvbt43_ReplayURL_in_constraints = {
  "camList": {
    "id": "cmsmi3wef02uvrc0qd7poxm6a",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmsmi3wel02uxrc0q9ehe83j4",
    "valueType": "preset",
    "required": True
  },
  "camList.startTime": {
    "id": "cmsmi3wel02uzrc0qq61flskq",
    "valueType": "preset",
    "required": True
  },
  "camList.endTime": {
    "id": "cmsmi3wem02v1rc0qb44zzrbm",
    "valueType": "preset",
    "required": True
  },
  "camList.streamProtocolType": {
    "id": "cmsmi3wen02v3rc0qgeoa3lqb",
    "valueType": "preset",
    "required": True
  }
}

# StoredVideoEventInfos
cmsmhhyl502ncrc0qnjtvbt43_StoredVideoEventInfos_in_constraints = {
  "timePeriod": {
    "id": "cmsmifweq02wirc0qaw2b1z0x",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmsmifwf802wsrc0qu34b405n",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmsmifwf902wurc0qlufi8yfu",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmsmihcn102x3rc0qbg2chxrn",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmsmihcn402x5rc0q8dces4ng",
    "valueType": "preset",
    "required": True
  },
  "maxCount": {
    "id": "cmsmifwer02wmrc0qyivx5i97",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmsmifwer02worc0q5byh0n8n",
    "valueType": "preset",
    "required": False
  },
  "classFilter": {
    "id": "cmsmifwes02wqrc0qip3eoy8v",
    "valueType": "preset",
    "required": False
  }
}

# StoredObjectAnalyticsInfos
cmsmhhyl502ncrc0qnjtvbt43_StoredObjectAnalyticsInfos_in_constraints = {
  "timePeriod": {
    "id": "cmsmipu6v02yfrc0qwn3tlp9s",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmsmipu7a02ylrc0q3metw1zc",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmsmipu7a02ynrc0qf5kejqwr",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmsmipu7b02yprc0qv5ixuzkz",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmsmipu7j02ytrc0qc0hu96hx",
    "valueType": "preset",
    "required": True
  },
  "filterList": {
    "id": "cmsmipu7b02yrrc0qgdm0q4lq",
    "valueType": "preset",
    "required": True
  },
  "filterList.classFilter": {
    "id": "cmsmipu7k02yvrc0qfovzyvbz",
    "valueType": "preset",
    "required": False,
    "arrayElementType": "string"
  },
  "filterList.attributeFilter": {
    "id": "cmsmipu7l02yxrc0qgrgjb17k",
    "valueType": "preset",
    "required": True,
    "arrayElementType": "string"
  }
}

# cmsmhhyl502ncrc0qnjtvbt43 검증 리스트
cmsmhhyl502ncrc0qnjtvbt43_inConstraints = [
    cmsmhhyl502ncrc0qnjtvbt43_Authentication_in_constraints,
    cmsmhhyl502ncrc0qnjtvbt43_Capabilities_in_constraints,
    cmsmhhyl502ncrc0qnjtvbt43_CameraProfiles_in_constraints,
    cmsmhhyl502ncrc0qnjtvbt43_StoredVideoInfos_in_constraints,
    cmsmhhyl502ncrc0qnjtvbt43_ReplayURL_in_constraints,
    cmsmhhyl502ncrc0qnjtvbt43_StoredVideoEventInfos_in_constraints,
    cmsmhhyl502ncrc0qnjtvbt43_StoredObjectAnalyticsInfos_in_constraints,
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
    "id": "cmixuqxe80h0lp002efemdw6m",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmixuqxeb0h0np002mwczcz4g",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorID"
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
    "id": "cmj83qob2000isnx0rwhvblif",
    "referenceFieldId": "cmixusnxa0hazp002h9lu2gt7",
    "valueType": "random",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorSensor",
    "randomType": "valid-values",
    "validValueField": "acControl",
    "validValues": [
      "Lock",
      "Unlock"
    ]
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
    "referenceFieldId": "cmixuu5os0hc9p002st12cpzi",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/DoorControl",
    "referenceField": "doorID"
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
    None,
    None,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_out_constraints,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_out_constraints,
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
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/SensorDeviceControl",
    "validValueField": "sensorControl",
    "validValues": [
      "AlarmOn",
      "AlarmOff"
    ]
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
  "velocity.pan": {
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

# cmii7wfuf006i8z1tcds6q69g 검증 리스트
cmii7wfuf006i8z1tcds6q69g_inConstraints = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_in_constraints,
    cmii7wfuf006i8z1tcds6q69g_Capabilities_in_constraints,
    cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_in_constraints,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_in_constraints,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_in_constraints,
]

# cmii7wfuf006i8z1tcds6q69g WebHook Constraints 리스트
cmii7wfuf006i8z1tcds6q69g_webhook_outConstraints = [
    None,
    None,
    None,
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
    "id": "cmjck3xm709kycfb3blmpcv9n",
    "valueType": "random",
    "required": True,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/DoorProfiles",
    "randomType": "exclude-reference-valid-values",
    "validValueField": "videoEvent",
    "validValues": [
      "Loitering",
      "Intrusion"
    ]
  }
}

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

# cmii7w683006h8z1t7usnin5g 검증 리스트
cmii7w683006h8z1t7usnin5g_inConstraints = [
    cmii7w683006h8z1t7usnin5g_Authentication_in_constraints,
    cmii7w683006h8z1t7usnin5g_Capabilities_in_constraints,
    cmii7w683006h8z1t7usnin5g_DoorProfiles_in_constraints,
    cmii7w683006h8z1t7usnin5g_AccessUserInfos_in_constraints,
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_in_constraints,
]

# cmii7w683006h8z1t7usnin5g WebHook Constraints 리스트
cmii7w683006h8z1t7usnin5g_webhook_outConstraints = [
    None,
    None,
    None,
    None,
    cmii7w683006h8z1t7usnin5g_RealtimeVerifEventInfos_webhook_out_constraints,
]

