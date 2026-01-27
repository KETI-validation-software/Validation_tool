# Authentication
cmiqr1jha00i6ie8fb1scb3go_Authentication_out_validation = {}

# Capabilities
cmiqr1jha00i6ie8fb1scb3go_Capabilities_out_validation = {}

# DoorProfiles
cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_out_validation = {}

# RealtimeDoorStatus
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_out_validation = {}

# RealtimeDoorStatus WebHook IN Validation
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmixusnx90hatp002m3rnln60",
    "referenceField": "doorID",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "score": 0
  },
  "doorList.doorSensor": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acControl",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Lock",
      "Unlock"
    ],
    "score": 0
  }
}

# DoorControl
cmiqr1jha00i6ie8fb1scb3go_DoorControl_out_validation = {}

# RealtimeDoorStatus2
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_out_validation = {}

# RealtimeDoorStatus2 WebHook IN Validation
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_in_validation = {
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmixuykwk0hmep002xddae990",
    "referenceField": "doorID",
    "referenceEndpoint": "/RealtimeDoorStatus2",
    "score": 0
  },
  "doorList.doorSensor": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmj83qob2000isnx0rwhvblif",
    "referenceField": "commandType",
    "referenceEndpoint": "/DoorControl",
    "score": 0
  }
}

# cmiqr1jha00i6ie8fb1scb3go WebHook 검증 리스트
cmiqr1jha00i6ie8fb1scb3go_webhook_inValidation = [
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_in_validation,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_in_validation,
]

# cmiqr1jha00i6ie8fb1scb3go 검증 리스트
cmiqr1jha00i6ie8fb1scb3go_outValidation = [
    cmiqr1jha00i6ie8fb1scb3go_Authentication_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_Capabilities_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_out_validation,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_out_validation,
]

