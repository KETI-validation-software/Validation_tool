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
    "id": "cmixuqxe80h0lp002efemdw6m",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmixuqxeb0h0np002mwczcz4g",
    "referenceFieldId": "cmixusnx90hatp002m3rnln60",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
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
    "referenceFieldId": "cmixusnx90hatp002m3rnln60",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
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

# Authentication
cmiqr201z00i8ie8fitdg5t1b_Authentication_out_constraints = {
  "code": {
    "id": "cmise6h0700lj5vy7s4v9c10v",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmise6px400my5vy7g75s15nw",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmise6roq00n75vy7ybrbiod8",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmise6tse00ne5vy7nh2re28j",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmise6vhr00nj5vy79f6dpfuy",
    "valueType": "preset",
    "required": False
  }
}

# Capabilities
cmiqr201z00i8ie8fitdg5t1b_Capabilities_out_constraints = {
  "code": {
    "id": "cmisel8x7017z5vy7ec1e56cu",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisele87018w5vy7kc760njz",
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "id": "cmisencfu01gm5vy7g5psolwh",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmisencfx01go5vy7jrh8pa2a",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmisencfx01gq5vy7uokgn8u3",
    "valueType": "preset",
    "required": False
  }
}

# SensorDeviceProfiles
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_out_constraints = {
  "code": {
    "id": "cmisev4br03dj5vy7q8tww5gm",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiseva9203e25vy7xh9ygo6s",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList": {
    "id": "cmisfgtvo07sw5vy7k8kfq13x",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmisfgtvs07sy5vy7f2hjy5aa",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceType": {
    "id": "cmisfgtvt07t05vy7qd9tbtc9",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceName": {
    "id": "cmisfgtvt07t25vy79eg4cnlj",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceLoc": {
    "id": "cmisfgtvu07t45vy7oxufjeba",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.sensorDeviceLoc.lon": {
    "id": "cmisfgtvz07t65vy7n4m3aoe0",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceLoc.lat": {
    "id": "cmisfgtw007t85vy7jrmgllyc",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceLoc.alt": {
    "id": "cmisfgtw007ta5vy7ut58i0y3",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.sensorDeviceLoc.desc": {
    "id": "cmisfgtw107tc5vy7as5hqx5m",
    "valueType": "preset",
    "required": False
  }
}

# SensorDeviceControl
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_out_constraints = {
  "code": {
    "id": "cmisg4vxz089s5vy7qhna151g",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisg4zcn08a05vy7gzrw0rbp",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceID": {
    "id": "cmisg51v408a85vy7mrhteunz",
    "referenceFieldId": "cmisg3n7u088o5vy75dl8ge3h",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceStatus": {
    "id": "cmj6hdjek01qsxei0ydzyxlg3",
    "valueType": "random",
    "required": True,
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
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_out_constraints = {
  "code": {
    "id": "cmisgsmo108me5vy7a070ga4t",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisgsssu08n85vy7rhriw5bx",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceID": {
    "id": "cmisgsuft08nf5vy70cyl59az",
    "referenceFieldId": "cmisgef0108e15vy7pvj4b2yg",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl2",
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceStatus": {
    "id": "cmisgsyrq08nn5vy7ggcm5ezc",
    "referenceFieldId": "cmiskmz17000kugxnuas8675t",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl2",
    "referenceField": "commandType"
  }
}

# cmiqr201z00i8ie8fitdg5t1b 검증 리스트
cmiqr201z00i8ie8fitdg5t1b_outConstraints = [
    cmiqr201z00i8ie8fitdg5t1b_Authentication_out_constraints,
    cmiqr201z00i8ie8fitdg5t1b_Capabilities_out_constraints,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_out_constraints,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_out_constraints,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_out_constraints,
]

# Authentication
cmiqr1acx00i5ie8fi022t1hp_Authentication_out_constraints = {
  "code": {
    "id": "cmisgxzw808ul5vy7gr8s98dc",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisgy1gp08uq5vy7194x1gfs",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmisgy8mc08v85vy7nzg2ozx6",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmisgyadj08vd5vy7s0zp2y9b",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmisgzrk508w65vy79bmeve7p",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {}
    }
  }
}

# Capabilities
cmiqr1acx00i5ie8fi022t1hp_Capabilities_out_constraints = {
  "code": {
    "id": "cmisjt9640bnb5vy7c6mmpnzy",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisjtb5g0bol5vy730bd9uun",
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "id": "cmisjube90c0s5vy7tdfvfpnq",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmisjubeb0c0u5vy736142p3j",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmisjubec0c0w5vy7rtgcn5qu",
    "valueType": "preset",
    "required": False
  }
}

# DoorProfiles
cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_out_constraints = {
  "code": {
    "id": "cmiwq39sh07fz844gn5ojv8iv",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwq3ewx07g8844gfdjstgru",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmizh2j7v028i7eoei30z6if0",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmizh2j7y028k7eoekmch7neb",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorName": {
    "id": "cmizh2j7y028m7eoe561v1og0",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorRelayStatus": {
    "id": "cmizh2j7y028o7eoe7oum45e5",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorSensor": {
    "id": "cmizh2j7z028q7eoeh327meza",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc": {
    "id": "cmizh2j7z028s7eoem1q5umty",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.lon": {
    "id": "cmizh2j86028y7eoe7rnz5oci",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.lat": {
    "id": "cmizh2j8702907eoe17manciv",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.alt": {
    "id": "cmizh2j8702927eoetki8hmas",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.desc": {
    "id": "cmizh2j8702947eoe5ivm78fe",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList": {
    "id": "cmizh2j8802967eoear3svcpn",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.bioDeviceID": {
    "id": "cmizh2j8f029a7eoenj3oor7e",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.otherDeviceName": {
    "id": "cmiwqea340abf844g15xesdtc",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList.bioDeviceAuthTypeList": {
    "id": "cmizh2j8m029m7eoemeq1ifjn",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.bioDeviceName": {
    "id": "cmizh2j8f029c7eoemcuopjxw",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList": {
    "id": "cmizh2j8802987eoe9kemqk9s",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList.otherDeviceID": {
    "id": "cmizh2j8g029g7eoe4aae2xlo",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList.otherDeviceName": {
    "id": "cmizh2j8g029i7eoeps66od7e",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList.otherDeviceAuthTypeList": {
    "id": "cmizh2j8h029k7eoeaadch6yi",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_constraints = {
  "code": {
    "id": "cmizg2tx300fg7eoezo3qr162",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmizg2xab00fm7eoe1bhmlgrw",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus WebHook IN Constraints
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_webhook_in_constraints = {
  "doorList": {
    "id": "cmiwqkuoh0aj7844gfnoaur3g",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwqkuoj0aj9844g5oec97p9",
    "referenceFieldId": "cmiwqkuoj0aj9844g5oec97p9",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorID"
  },
  "doorList.doorName": {
    "id": "cmizg3epb00gy7eoeiefmp1lr",
    "referenceFieldId": "cmizh2j7y028m7eoe561v1og0",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorName"
  },
  "doorList.doorRelaySensor": {
    "id": "cmizg3ghq00h67eoeuthieru9",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorSensor": {
    "id": "cmj13a9eu01vx12s9wja5mxt7",
    "valueType": "random",
    "required": True,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "validValueField": "acControl",
    "validValues": [
      "Lock",
      "Unlock"
    ]
  }
}

# DoorControl
cmiqr1acx00i5ie8fi022t1hp_DoorControl_out_constraints = {
  "code": {
    "id": "cmiwqp4z80azq844gf2xm9qtt",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwqpbp70b00844gr7gg59fr",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus2
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_out_constraints = {
  "code": {
    "id": "cmiwqsqrw0b7y844gtn3rzf7y",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwqsvzu0b88844gjdzch27v",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus2 WebHook IN Constraints
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_webhook_in_constraints = {
  "doorList": {
    "id": "cmiwqvxns0bng844g9w4ruqq0",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwqvxnv0bni844g3f2pyz9t",
    "referenceFieldId": "cmiwqovgn0az6844g1iuqahpi",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/DoorControl",
    "referenceField": "doorID"
  },
  "doorList.doorName": {
    "id": "cmiwqvxnv0bnk844gwotx0gqu",
    "referenceFieldId": "cmizh2j7y028m7eoe561v1og0",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorName"
  },
  "doorList.doorRelaySensor": {
    "id": "cmiwqvxnv0bnm844g0ndzntyu",
    "valueType": "preset",
    "required": False
  },
  "doorList.doorSensor": {
    "id": "cmiwqvxnw0bno844gj9p4t49o",
    "referenceFieldId": "cmiwqozju0azf844gr4zk31m8",
    "valueType": "request-based",
    "required": False,
    "referenceEndpoint": "/DoorControl",
    "referenceField": "commandType"
  }
}

# cmiqr1acx00i5ie8fi022t1hp 검증 리스트
cmiqr1acx00i5ie8fi022t1hp_outConstraints = [
    cmiqr1acx00i5ie8fi022t1hp_Authentication_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_Capabilities_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_DoorControl_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_out_constraints,
]

# cmiqr1acx00i5ie8fi022t1hp WebHook Constraints 리스트
cmiqr1acx00i5ie8fi022t1hp_webhook_inConstraints = [
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_webhook_in_constraints,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_webhook_in_constraints,
]

# Authentication
cmiqqzrjz00i3ie8figf79cur_Authentication_out_constraints = {
  "code": {
    "id": "cmish3lv5090t5vy7ppk8nh5y",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmish3n4c090y5vy7vozpz3c9",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmish3roj091m5vy70dja7bsr",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmish3th3091t5vy7hnm0qk5t",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmish3v9b091y5vy7b8isryog",
    "valueType": "test-time",
    "required": False
  }
}

# Capabilities
cmiqqzrjz00i3ie8figf79cur_Capabilities_out_constraints = {
  "code": {
    "id": "cmiwp7rmz05kq844gqqw69i5s",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwp7ycr05kz844gpry7r479",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport": {
    "id": "cmiwp9wl305qy844gnfzg8d6v",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport.streamProtocolType": {
    "id": "cmiwp9wl405r0844gevqq7thx",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport.streamProtocolDesc": {
    "id": "cmiwp9wl505r2844gnotixjmo",
    "valueType": "preset",
    "required": False
  },
  "transportSupport": {
    "id": "cmiwp9wld05r4844gwbrgvweo",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmiwp9wlf05r6844g337ki5mc",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmiwp9wlf05r8844gnxagb6rb",
    "valueType": "preset",
    "required": False
  }
}

# CameraProfiles
cmiqqzrjz00i3ie8figf79cur_CameraProfiles_out_constraints = {
  "code ": {
    "id": "cmiwpbac505rs844g0w11qcj8",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwpbir605s2844gy6l7ht7i",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmiwpi3sx076w844g20jekxkx",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwpi3sz076y844gftp3b99j",
    "valueType": "preset",
    "required": True
  },
  "camList.camName": {
    "id": "cmiwpi3t00770844gdctr9fw1",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc": {
    "id": "cmiwpi3t00772844gts4nv5ql",
    "valueType": "preset",
    "required": False
  },
  "camList.camLoc.lon": {
    "id": "cmiwpi3t50776844gcy9byurz",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.lat": {
    "id": "cmiwpi3t50778844guj8t5it2",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.alt": {
    "id": "cmiwpi3t6077a844g0b0yeqx8",
    "valueType": "preset",
    "required": False
  },
  "camList.camLoc.desc": {
    "id": "cmiwpi3t6077c844gk3w5sd4w",
    "valueType": "preset",
    "required": False
  },
  "camList.camConfig": {
    "id": "cmiwpi3t00774844g2zghfgzy",
    "valueType": "preset",
    "required": False
  },
  "camList.camConfig.camType": {
    "id": "cmiwpi3t6077e844gn2ohl1ou",
    "valueType": "preset",
    "required": True
  }
}

# PtzStatus
cmiqqzrjz00i3ie8figf79cur_PtzStatus_out_constraints = {
  "code": {
    "id": "cmiwpo8gz0789844gz619d01h",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwpoeoi078i844g85lop6oe",
    "valueType": "preset",
    "required": True
  },
  "position": {
    "id": "cmiwpojna078r844g6ulioxop",
    "valueType": "preset",
    "required": False
  },
  "position.pan": {
    "id": "cmiwppn930791844g4wbst740",
    "valueType": "preset",
    "required": False
  },
  "position.tilt": {
    "id": "cmiwpptx8079b844g1f7xa2y6",
    "valueType": "preset",
    "required": False
  },
  "position.zoom": {
    "id": "cmiwpq2d4079l844gn2uy03vw",
    "valueType": "preset",
    "required": False
  },
  "moveStatus": {
    "id": "cmiwpqqwx079z844gkr7zhzg3",
    "valueType": "preset",
    "required": True
  },
  "moveStatus.pan": {
    "id": "cmiwpqw4u07a9844g8w3hl36p",
    "valueType": "preset",
    "required": False
  },
  "moveStatus.tilt": {
    "id": "cmiwpr18g07aj844g12ft2m11",
    "valueType": "preset",
    "required": False
  },
  "moveStatus.zoom": {
    "id": "cmiwpr6ja07as844gp1ll94fb",
    "valueType": "preset",
    "required": False
  }
}

# PtzContinuousMove
cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_out_constraints = {
  "code": {
    "id": "cmiwpuitl07d5844gzj2zay1m",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwpupho07de844ghl7x9u0q",
    "valueType": "preset",
    "required": True
  }
}

# PtzStop
cmiqqzrjz00i3ie8figf79cur_PtzStop_out_constraints = {
  "code": {
    "id": "cmiwpx90h07f1844glcuw528e",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwpxflk07fb844ge0ye0ib7",
    "valueType": "preset",
    "required": True
  }
}

# cmiqqzrjz00i3ie8figf79cur 검증 리스트
cmiqqzrjz00i3ie8figf79cur_outConstraints = [
    cmiqqzrjz00i3ie8figf79cur_Authentication_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_Capabilities_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_CameraProfiles_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_PtzStatus_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_PtzStop_out_constraints,
]

