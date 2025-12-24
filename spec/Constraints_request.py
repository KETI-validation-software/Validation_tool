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

# SensorDeviceControl
cmiqr1jha00i6ie8fb1scb3go_SensorDeviceControl_in_constraints = {
  "sensorDeviceID": {
    "id": "cmjjjtgj60nlwcfb3isyyownx",
    "valueType": "preset",
    "required": True
  },
  "commandType": {
    "id": "cmjjjti9a0nm2cfb3n3qa371g",
    "valueType": "preset",
    "required": True
  }
}

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
    "randomType": "exclude-reference-valid-values",
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
    cmiqr1jha00i6ie8fb1scb3go_SensorDeviceControl_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_in_constraints,
]

# cmiqr1jha00i6ie8fb1scb3go WebHook Constraints 리스트
cmiqr1jha00i6ie8fb1scb3go_webhook_outConstraints = [
    None,
    None,
    None,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_out_constraints,
    None,
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

