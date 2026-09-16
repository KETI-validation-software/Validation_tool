# Authentication
cmsmh2go501w6rc0q4s8zyqdp_Authentication_in_validation = {
  "userID": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa"
    ],
    "score": 0
  },
  "userPW": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa_k1!2@"
    ],
    "score": 0
  }
}

# Capabilities
cmsmh2go501w6rc0q4s8zyqdp_Capabilities_in_validation = {}

# SensorDeviceProfiles
cmsmh2go501w6rc0q4s8zyqdp_SensorDeviceProfiles_in_validation = {}

# StoredSensorEventInfos
cmsmh2go501w6rc0q4s8zyqdp_StoredSensorEventInfos_in_validation = {
  "timePeriod.startTime": {
    "enabled": True,
    "validationType": "range-match",
    "rangeMin": "20260817163010123",
    "rangeMax": "20260822163010123",
    "rangeOperator": "between",
    "score": 0
  },
  "timePeriod.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "greater-equal",
    "referenceFieldMin": "timePeriod.startTime",
    "referenceFieldMinId": "cmsmh2h2m022qrc0qn4e8xgpz",
    "referenceEndpointMin": "/StoredSensorEventInfos",
    "score": 0
  },
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmtwr8wqe00ug245t5asqf1bn",
    "referenceField": "sensorDeviceList.sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceProfiles",
    "score": 0,
    "isArrayFieldPath": True
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "sensorEvent",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "HighTemperature",
      "LowTemperature",
      "HighHumidity",
      "LowHumidity/Dry",
      "OverProximity",
      "Smoke",
      "Fire",
      "MotionDetection",
      "OccupancyDetection",
      "ToxicGas",
      "OxygenExcess",
      "OxygenDeficiency",
      "BadFineDust",
      "VibrationDetection",
      "HighWaterLevel",
      "LowWaterLevel",
      "Leak",
      "OverCurrent",
      "AbnormalSound",
      "DoorOpen",
      "DoorClose",
      "AbnormalElectricUses",
      "AbnormalWaterUses",
      "Intrusion",
      "Deviation",
      "Screaming",
      "Yelling",
      "Crying",
      "HeavyBreathing",
      "Break",
      "RescueSignal",
      "HelpSignal",
      "고온",
      "저온",
      "다습",
      "건조",
      "근접",
      "연기",
      "화재",
      "움직임감지",
      "재실감지",
      "유해가스",
      "산소과잉",
      "산소부족",
      "미세먼지나쁨",
      "진동",
      "고수위",
      "저수위",
      "누수",
      "전류과다",
      "이상음감지",
      "문열림",
      "문닫힘",
      "전력량이상",
      "수도사용량이상",
      "침입",
      "이탈",
      "비명",
      "고성",
      "울음",
      "헐떡거림",
      "깨짐",
      "살려주세요",
      "도와주세요"
    ],
    "score": 0
  }
}

# cmsmh2go501w6rc0q4s8zyqdp 검증 리스트
cmsmh2go501w6rc0q4s8zyqdp_inValidation = [
    cmsmh2go501w6rc0q4s8zyqdp_Authentication_in_validation,
    cmsmh2go501w6rc0q4s8zyqdp_Capabilities_in_validation,
    cmsmh2go501w6rc0q4s8zyqdp_SensorDeviceProfiles_in_validation,
    cmsmh2go501w6rc0q4s8zyqdp_StoredSensorEventInfos_in_validation,
]

# Authentication
cmiqr201z00i8ie8fitdg5t1b_Authentication_in_validation = {
  "userID": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa"
    ],
    "score": 0
  },
  "userPW": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa_k1!2@"
    ],
    "score": 0
  }
}

# Capabilities
cmiqr201z00i8ie8fitdg5t1b_Capabilities_in_validation = {}

# SensorDeviceProfiles
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_in_validation = {}

# SensorDeviceControl
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_in_validation = {
  "sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmtwr1ex400q0245trhytuni7",
    "referenceField": "sensorDeviceList.sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceProfiles",
    "score": 0,
    "isArrayFieldPath": True
  },
  "commandType": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "sensorControl",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "AlarmOn",
      "AlarmOff"
    ],
    "score": 0
  }
}

# SensorDeviceControl2
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_in_validation = {
  "sensorDeviceID": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmisg3n7u088o5vy75dl8ge3h",
    "referenceField": "sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceControl",
    "score": 0
  },
  "commandType": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "sensorControl",
    "validValueOperator": "excludeReference",
    "allowedValues": [
      "AlarmOn",
      "AlarmOff"
    ],
    "referenceFieldId": "cmj6hdjek01qsxei0ydzyxlg3",
    "referenceField": "sensorDeviceStatus",
    "referenceEndpoint": "/SensorDeviceControl",
    "score": 0
  }
}

# cmiqr201z00i8ie8fitdg5t1b 검증 리스트
cmiqr201z00i8ie8fitdg5t1b_inValidation = [
    cmiqr201z00i8ie8fitdg5t1b_Authentication_in_validation,
    cmiqr201z00i8ie8fitdg5t1b_Capabilities_in_validation,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_in_validation,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_in_validation,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_in_validation,
]

# Authentication
cmii7shen005i8z1tagevx4qh_Authentication_in_validation = {
  "userID": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa"
    ],
    "score": 0
  },
  "userPW": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "kisa_k1!2@"
    ],
    "score": 0
  }
}

# Capabilities
cmii7shen005i8z1tagevx4qh_Capabilities_in_validation = {}

# SensorDeviceProfiles
cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_in_validation = {}

# RealtimeSensorData
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_in_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmtwphnzq00fa245t2l6b707g",
    "referenceField": "sensorDeviceList.sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceProfiles",
    "score": 0,
    "isArrayFieldPath": True
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "Webhook"
    ],
    "score": 0
  },
  "startTime": {
    "enabled": True,
    "validationType": "request-time-compare",
    "referenceTimeSource": "request-timestamp",
    "timeCompareOperator": "greater-than",
    "score": 0
  }
}

# RealtimeSensorData WebHook OUT Validation
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_out_validation = {
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

# RealtimeSensorEventInfos
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_in_validation = {
  "sensorDeviceList.sensorDeviceID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmtwphnzq00fa245t2l6b707g",
    "referenceField": "sensorDeviceList.sensorDeviceID",
    "referenceEndpoint": "/SensorDeviceProfiles",
    "score": 0,
    "isArrayFieldPath": True
  },
  "transProtocol.transProtocolType": {
    "enabled": True,
    "validationType": "specified-value-match",
    "allowedValues": [
      "Webhook"
    ],
    "score": 0
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "sensorEvent",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "HighTemperature",
      "LowTemperature",
      "HighHumidity",
      "LowHumidity/Dry",
      "OverProximity",
      "Smoke",
      "Fire",
      "MotionDetection",
      "OccupancyDetection",
      "ToxicGas",
      "OxygenExcess",
      "OxygenDeficiency",
      "BadFineDust",
      "VibrationDetection",
      "HighWaterLevel",
      "LowWaterLevel",
      "Leak",
      "OverCurrent",
      "AbnormalSound",
      "DoorOpen",
      "DoorClose",
      "AbnormalElectricUses",
      "AbnormalWaterUses",
      "Intrusion",
      "Deviation",
      "Screaming",
      "Yelling",
      "Crying",
      "HeavyBreathing",
      "Break",
      "RescueSignal",
      "HelpSignal",
      "고온",
      "저온",
      "다습",
      "건조",
      "근접",
      "연기",
      "화재",
      "움직임감지",
      "재실감지",
      "유해가스",
      "산소과잉",
      "산소부족",
      "미세먼지나쁨",
      "진동",
      "고수위",
      "저수위",
      "누수",
      "전류과다",
      "이상음감지",
      "문열림",
      "문닫힘",
      "전력량이상",
      "수도사용량이상",
      "침입",
      "이탈",
      "비명",
      "고성",
      "울음",
      "헐떡거림",
      "깨짐",
      "살려주세요",
      "도와주세요"
    ],
    "score": 0
  },
  "startTime": {
    "enabled": True,
    "validationType": "request-time-compare",
    "referenceTimeSource": "request-timestamp",
    "timeCompareOperator": "greater-than",
    "score": 0
  }
}

# RealtimeSensorEventInfos WebHook OUT Validation
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_out_validation = {
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

# cmii7shen005i8z1tagevx4qh WebHook 검증 리스트
cmii7shen005i8z1tagevx4qh_webhook_outValidation = [
    None,
    None,
    None,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_out_validation,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_out_validation,
]

# cmii7shen005i8z1tagevx4qh 검증 리스트
cmii7shen005i8z1tagevx4qh_inValidation = [
    cmii7shen005i8z1tagevx4qh_Authentication_in_validation,
    cmii7shen005i8z1tagevx4qh_Capabilities_in_validation,
    cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_in_validation,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_in_validation,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_in_validation,
]

