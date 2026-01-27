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

