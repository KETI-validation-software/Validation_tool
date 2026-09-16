# Authentication
cmtwtwdiz02o1245txoqxczwz_Authentication_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# Capabilities
cmtwtwdiz02o1245txoqxczwz_Capabilities_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "403"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "권한 없음"
    ],
    "score": 0
  }
}

# DoorProfiles
cmtwtwdiz02o1245txoqxczwz_DoorProfiles_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList": {
    "enabled": True,
    "validationType": "object-count-between",
    "rangeMin": 5,
    "rangeMax": 100,
    "score": 0
  },
  "doorList.doorRelayStatus": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acRelay",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Normal",
      "ManualOpen",
      "ManualClose",
      "ScheduleOpen",
      "ScheduleClose",
      "None",
      "Active",
      "Inactive",
      "일반",
      "수동개방",
      "수동폐쇄",
      "스케줄개방",
      "스케줄폐쇄",
      "상태없음",
      "활성",
      "비활성"
    ],
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

# RealtimeDoorStatus
cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-equality",
    "referenceFieldId": "cmtwtwdsr02sf245thyfh74ss",
    "referenceField": "doorList.doorID",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "score": 0,
    "isArrayFieldPath": True,
    "listEqualityMode": "set"
  },
  "doorList.doorName": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmtwtwdny02qj245tdyx3gntu",
    "referenceField": "doorList.doorName",
    "referenceEndpoint": "/DoorProfiles",
    "score": 0,
    "isArrayFieldPath": True
  },
  "doorList.doorRelaySensor": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acRelay",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Normal",
      "ManualOpen",
      "ManualClose",
      "ScheduleOpen",
      "ScheduleClose",
      "None",
      "Active",
      "Inactive",
      "일반",
      "수동개방",
      "수동폐쇄",
      "스케줄개방",
      "스케줄폐쇄",
      "상태없음",
      "활성",
      "비활성"
    ],
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
cmtwtwdiz02o1245txoqxczwz_DoorControl_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# RealtimeDoorStatus2
cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus2_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "400"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "잘못된 요청"
    ],
    "score": 0
  }
}

# cmtwtwdiz02o1245txoqxczwz 검증 리스트
cmtwtwdiz02o1245txoqxczwz_outValidation = [
    cmtwtwdiz02o1245txoqxczwz_Authentication_out_validation,
    cmtwtwdiz02o1245txoqxczwz_Capabilities_out_validation,
    cmtwtwdiz02o1245txoqxczwz_DoorProfiles_out_validation,
    cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus_out_validation,
    cmtwtwdiz02o1245txoqxczwz_DoorControl_out_validation,
    cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus2_out_validation,
]

# Authentication
cmtwtvuyb02i1245t2su90084_Authentication_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# Capabilities
cmtwtvuyb02i1245t2su90084_Capabilities_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "403"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "권한 없음"
    ],
    "score": 0
  }
}

# DoorProfiles
cmtwtvuyb02i1245t2su90084_DoorProfiles_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList": {
    "enabled": True,
    "validationType": "object-count-between",
    "rangeMin": 5,
    "rangeMax": 100,
    "score": 0
  },
  "doorList.doorRelayStatus": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acRelay",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Normal",
      "ManualOpen",
      "ManualClose",
      "ScheduleOpen",
      "ScheduleClose",
      "None",
      "Active",
      "Inactive",
      "일반",
      "수동개방",
      "수동폐쇄",
      "스케줄개방",
      "스케줄폐쇄",
      "상태없음",
      "활성",
      "비활성"
    ],
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

# AccessUserInfos
cmtwtvuyb02i1245t2su90084_AccessUserInfos_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# StoredVerifEventInfos
cmtwtvuyb02i1245t2su90084_StoredVerifEventInfos_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "201"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "정보 없음"
    ],
    "score": 0
  }
}

# cmtwtvuyb02i1245t2su90084 검증 리스트
cmtwtvuyb02i1245t2su90084_outValidation = [
    cmtwtvuyb02i1245t2su90084_Authentication_out_validation,
    cmtwtvuyb02i1245t2su90084_Capabilities_out_validation,
    cmtwtvuyb02i1245t2su90084_DoorProfiles_out_validation,
    cmtwtvuyb02i1245t2su90084_AccessUserInfos_out_validation,
    cmtwtvuyb02i1245t2su90084_StoredVerifEventInfos_out_validation,
]

# Authentication
cmtwtvjfm02br245tbzi9gej7_Authentication_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# Capabilities
cmtwtvjfm02br245tbzi9gej7_Capabilities_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "403"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "권한 없음"
    ],
    "score": 0
  }
}

# DoorProfiles
cmtwtvjfm02br245tbzi9gej7_DoorProfiles_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList": {
    "enabled": True,
    "validationType": "object-count-between",
    "rangeMin": 5,
    "rangeMax": 100,
    "score": 0
  },
  "doorList.doorRelayStatus": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acRelay",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Normal",
      "ManualOpen",
      "ManualClose",
      "ScheduleOpen",
      "ScheduleClose",
      "None",
      "Active",
      "Inactive",
      "일반",
      "수동개방",
      "수동폐쇄",
      "스케줄개방",
      "스케줄폐쇄",
      "상태없음",
      "활성",
      "비활성"
    ],
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

# AccessUserInfos
cmtwtvjfm02br245tbzi9gej7_AccessUserInfos_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# RealtimeVerifEventInfos
cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "404"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "장치 없음"
    ],
    "score": 0
  }
}

# RealtimeVerifEventInfos WebHook IN Validation
cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_webhook_in_validation = {
  "doorList.eventTime": {
    "enabled": True,
    "validationType": "request-time-compare",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmtwtvjnq02fx245thcfe48qa",
    "referenceEndpointMin": "/RealtimeVerifEventInfos",
    "referenceTimeSourceMin": "request-field",
    "referenceTimeSourceMax": "request-timestamp",
    "timeCompareOperator": "between",
    "score": 0
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-equality",
    "referenceFieldId": "cmtwtvjni02fr245tg4lng44z",
    "referenceField": "doorList.doorID",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "isArrayFieldPath": True,
    "listEqualityMode": "set",
    "score": 0
  },
  "doorList.eventName": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmtwtvjnn02fv245t5d4al29w",
    "referenceField": "eventFilter",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "score": 0
  }
}

# cmtwtvjfm02br245tbzi9gej7 WebHook 검증 리스트
cmtwtvjfm02br245tbzi9gej7_webhook_inValidation = [
    None,
    None,
    None,
    None,
    cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_webhook_in_validation,
]

# cmtwtvjfm02br245tbzi9gej7 검증 리스트
cmtwtvjfm02br245tbzi9gej7_outValidation = [
    cmtwtvjfm02br245tbzi9gej7_Authentication_out_validation,
    cmtwtvjfm02br245tbzi9gej7_Capabilities_out_validation,
    cmtwtvjfm02br245tbzi9gej7_DoorProfiles_out_validation,
    cmtwtvjfm02br245tbzi9gej7_AccessUserInfos_out_validation,
    cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_out_validation,
]

# Authentication
cmtwil1oo00ztt4ht7y9se1ur_Authentication_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# Capabilities
cmtwil1oo00ztt4ht7y9se1ur_Capabilities_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "transportSupport.transProtocolType": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "LongPolling",
      "Webhook"
    ],
    "score": 0
  }
}

# DoorProfiles
cmtwil1oo00ztt4ht7y9se1ur_DoorProfiles_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList": {
    "enabled": True,
    "validationType": "object-count-between",
    "rangeMin": 5,
    "rangeMax": 100,
    "score": 0
  },
  "doorList.doorRelayStatus": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acRelay",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Normal",
      "ManualOpen",
      "ManualClose",
      "ScheduleOpen",
      "ScheduleClose",
      "None",
      "Active",
      "Inactive",
      "일반",
      "수동개방",
      "수동폐쇄",
      "스케줄개방",
      "스케줄폐쇄",
      "상태없음",
      "활성",
      "비활성"
    ],
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

# RealtimeDoorStatus
cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-equality",
    "referenceFieldId": "cmtwil1z80137t4ht6cedc5cg",
    "referenceField": "doorList.doorID",
    "referenceEndpoint": "/RealtimeDoorStatus",
    "score": 0,
    "isArrayFieldPath": True,
    "listEqualityMode": "set"
  },
  "doorList.doorName": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmtwil1r7011ht4htnr4eaybb",
    "referenceField": "doorList.doorName",
    "referenceEndpoint": "/DoorProfiles",
    "score": 0,
    "isArrayFieldPath": True
  },
  "doorList.doorRelaySensor": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acRelay",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Normal",
      "ManualOpen",
      "ManualClose",
      "ScheduleOpen",
      "ScheduleClose",
      "None",
      "Active",
      "Inactive",
      "일반",
      "수동개방",
      "수동폐쇄",
      "스케줄개방",
      "스케줄폐쇄",
      "상태없음",
      "활성",
      "비활성"
    ],
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
cmtwil1oo00ztt4ht7y9se1ur_DoorControl_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# RealtimeDoorStatus2
cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus2_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmtwil24j015jt4htlug66sag",
    "referenceField": "doorList.doorID",
    "referenceEndpoint": "/RealtimeDoorStatus2",
    "referenceListField": "doorList.doorID",
    "referenceListEndpoint": "/RealtimeDoorStatus",
    "score": 0,
    "config": {
      "isArrayFieldPath": True
    },
    "isArrayFieldPath": True
  },
  "doorList.doorName": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmtwil1r7011ht4htnr4eaybb",
    "referenceField": "doorList.doorName",
    "referenceEndpoint": "/DoorProfiles",
    "score": 0,
    "config": {
      "isArrayFieldPath": True
    },
    "isArrayFieldPath": True
  },
  "doorList.doorRelaySensor": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acRelay",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Normal",
      "ManualOpen",
      "ManualClose",
      "ScheduleOpen",
      "ScheduleClose",
      "None",
      "Active",
      "Inactive",
      "일반",
      "수동개방",
      "수동폐쇄",
      "스케줄개방",
      "스케줄폐쇄",
      "상태없음",
      "활성",
      "비활성"
    ],
    "score": 0
  },
  "doorList.doorSensor": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmtwil21j0145t4htgsi3ngs4",
    "referenceField": "commandType",
    "referenceEndpoint": "/DoorControl",
    "referenceListEndpoint": "/DoorControl",
    "score": 0
  }
}

# cmtwil1oo00ztt4ht7y9se1ur 검증 리스트
cmtwil1oo00ztt4ht7y9se1ur_outValidation = [
    cmtwil1oo00ztt4ht7y9se1ur_Authentication_out_validation,
    cmtwil1oo00ztt4ht7y9se1ur_Capabilities_out_validation,
    cmtwil1oo00ztt4ht7y9se1ur_DoorProfiles_out_validation,
    cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus_out_validation,
    cmtwil1oo00ztt4ht7y9se1ur_DoorControl_out_validation,
    cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus2_out_validation,
]

# Authentication
cmtwfeiw4003dt4htizadqzzr_Authentication_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# Capabilities
cmtwfeiw4003dt4htizadqzzr_Capabilities_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "transportSupport.transProtocolType": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "LongPolling",
      "Webhook"
    ],
    "score": 0
  }
}

# DoorProfiles
cmtwfeiw4003dt4htizadqzzr_DoorProfiles_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList": {
    "enabled": True,
    "validationType": "object-count-between",
    "rangeMin": 5,
    "rangeMax": 100,
    "score": 0
  },
  "doorList.doorRelayStatus": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acRelay",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Normal",
      "ManualOpen",
      "ManualClose",
      "ScheduleOpen",
      "ScheduleClose",
      "None",
      "Active",
      "Inactive",
      "일반",
      "수동개방",
      "수동폐쇄",
      "스케줄개방",
      "스케줄폐쇄",
      "상태없음",
      "활성",
      "비활성"
    ],
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

# AccessUserInfos
cmtwfeiw4003dt4htizadqzzr_AccessUserInfos_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# StoredVerifEventInfos
cmtwfeiw4003dt4htizadqzzr_StoredVerifEventInfos_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList.eventTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "timePeriod.startTime",
    "referenceFieldMinId": "cmtwfejan0085t4htwdzww0wd",
    "referenceFieldMax": "timePeriod.endTime",
    "referenceFieldMaxId": "cmtwfejaq0087t4htaq13s6mq",
    "referenceEndpointMin": "/StoredVerifEventInfos",
    "referenceEndpointMax": "/StoredVerifEventInfos",
    "score": 0
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-equality",
    "referenceFieldId": "cmtwfejc8008dt4htm61szvt0",
    "referenceField": "doorList.doorID",
    "referenceEndpoint": "/StoredVerifEventInfos",
    "score": 0,
    "isArrayFieldPath": True,
    "listEqualityMode": "set"
  },
  "doorList.eventName": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmtwfejai0081t4htfx2wjpru",
    "referenceField": "eventFilter",
    "referenceEndpoint": "/StoredVerifEventInfos",
    "score": 0
  }
}

# cmtwfeiw4003dt4htizadqzzr 검증 리스트
cmtwfeiw4003dt4htizadqzzr_outValidation = [
    cmtwfeiw4003dt4htizadqzzr_Authentication_out_validation,
    cmtwfeiw4003dt4htizadqzzr_Capabilities_out_validation,
    cmtwfeiw4003dt4htizadqzzr_DoorProfiles_out_validation,
    cmtwfeiw4003dt4htizadqzzr_AccessUserInfos_out_validation,
    cmtwfeiw4003dt4htizadqzzr_StoredVerifEventInfos_out_validation,
]

# Authentication
cmtw8wcts00o1126muckytfg2_Authentication_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# Capabilities
cmtw8wcts00o1126muckytfg2_Capabilities_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "transportSupport.transProtocolType": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "LongPolling",
      "Webhook"
    ],
    "score": 0
  }
}

# DoorProfiles
cmtw8wcts00o1126muckytfg2_DoorProfiles_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  },
  "doorList": {
    "enabled": True,
    "validationType": "object-count-between",
    "rangeMin": 5,
    "rangeMax": 100,
    "score": 0
  },
  "doorList.doorRelayStatus": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "acRelay",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Normal",
      "ManualOpen",
      "ManualClose",
      "ScheduleOpen",
      "ScheduleClose",
      "None",
      "Active",
      "Inactive",
      "일반",
      "수동개방",
      "수동폐쇄",
      "스케줄개방",
      "스케줄폐쇄",
      "상태없음",
      "활성",
      "비활성"
    ],
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

# AccessUserInfos
cmtw8wcts00o1126muckytfg2_AccessUserInfos_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# RealtimeVerifEventInfos
cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_out_validation = {
  "code": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "200"
    ],
    "score": 0
  },
  "message": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "성공"
    ],
    "score": 0
  }
}

# RealtimeVerifEventInfos WebHook IN Validation
cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_webhook_in_validation = {
  "doorList.eventTime": {
    "enabled": True,
    "validationType": "request-time-compare",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmtw8wd8100sp126mxt2kkk06",
    "referenceEndpointMin": "/RealtimeVerifEventInfos",
    "referenceTimeSourceMin": "request-field",
    "referenceTimeSourceMax": "request-timestamp",
    "timeCompareOperator": "between",
    "score": 0
  },
  "doorList.doorID": {
    "enabled": True,
    "validationType": "request-field-list-equality",
    "referenceFieldId": "cmtw8wd9g00sv126mczcjpm2o",
    "referenceField": "doorList.doorID",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "isArrayFieldPath": True,
    "listEqualityMode": "set",
    "score": 0
  },
  "doorList.eventName": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmtw8wd7y00sn126mkvsn6i94",
    "referenceField": "eventFilter",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "score": 0
  }
}

# cmtw8wcts00o1126muckytfg2 WebHook 검증 리스트
cmtw8wcts00o1126muckytfg2_webhook_inValidation = [
    None,
    None,
    None,
    None,
    cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_webhook_in_validation,
]

# cmtw8wcts00o1126muckytfg2 검증 리스트
cmtw8wcts00o1126muckytfg2_outValidation = [
    cmtw8wcts00o1126muckytfg2_Authentication_out_validation,
    cmtw8wcts00o1126muckytfg2_Capabilities_out_validation,
    cmtw8wcts00o1126muckytfg2_DoorProfiles_out_validation,
    cmtw8wcts00o1126muckytfg2_AccessUserInfos_out_validation,
    cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_out_validation,
]

