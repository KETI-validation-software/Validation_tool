# Authentication
cmsy90xd705aarc0quh4je1k0_Authentication_in_validation = {
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
cmsy90xd705aarc0quh4je1k0_Capabilities_in_validation = {}

# CameraProfiles
cmsy90xd705aarc0quh4je1k0_CameraProfiles_in_validation = {}

# StreamURLs
cmsy90xd705aarc0quh4je1k0_StreamURLs_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmsyaf0da05derc0qi0xhw722",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  }
}

# RealtimeVideoEventInfos
cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "response-field-list-match",
    "referenceFieldId": "cmsyaf0da05derc0qi0xhw722",
    "referenceField": "camID",
    "referenceEndpoint": "/CameraProfiles",
    "score": 0
  },
  "eventFilter": {
    "enabled": True,
    "validationType": "valid-value-match",
    "validValueMatchType": "validation-field",
    "validValueFieldName": "videoEvent",
    "validValueOperator": "equalsAny",
    "allowedValues": [
      "Loitering",
      "Intrusion"
    ],
    "score": 0
  }
}

# RealtimeVideoEventInfos WebHook OUT Validation
cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_webhook_out_validation = {}

# cmsy90xd705aarc0quh4je1k0 WebHook 검증 리스트
cmsy90xd705aarc0quh4je1k0_webhook_outValidation = [
    cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_webhook_out_validation,
]

# cmsy90xd705aarc0quh4je1k0 검증 리스트
cmsy90xd705aarc0quh4je1k0_inValidation = [
    cmsy90xd705aarc0quh4je1k0_Authentication_in_validation,
    cmsy90xd705aarc0quh4je1k0_Capabilities_in_validation,
    cmsy90xd705aarc0quh4je1k0_CameraProfiles_in_validation,
    cmsy90xd705aarc0quh4je1k0_StreamURLs_in_validation,
    cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_in_validation,
]

