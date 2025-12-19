# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_out_validation = {}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_out_validation = {}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_validation = {}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_validation = {}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_validation = {}

# RealtimeVideoEventInfos WebHook IN Validation
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwrf69i0bu6844g22ccsjtr",
    "referenceField": "camID",
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "score": 0
  }
}

# StoredVideoInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwrn6ab003pnkgl7f78y9t6",
    "referenceField": "camID",
    "referenceEndpoint": "/StoredVideoInfos",
    "score": 0
  },
  "camList.timeList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrltxz000vnkgl3m4u2f2s",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrlxaj0013nkgl40nosy7z",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceEndpointMax": "/StoredVideoInfos",
    "score": 0
  },
  "camList.timeList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrltxz000vnkgl3m4u2f2s",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrlxaj0013nkgl40nosy7z",
    "referenceEndpointMin": "/StoredVideoInfos",
    "referenceEndpointMax": "/StoredVideoInfos",
    "score": 0
  }
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwrtok201dmnkgl6gzxhft5",
    "referenceField": "camID",
    "referenceEndpoint": "/ReplayURL",
    "score": 0
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrtok201donkglhwulnxos",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrtok301dqnkgl0k66p4py",
    "referenceEndpointMin": "/ReplayURL",
    "referenceEndpointMax": "/ReplayURL",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwrtok201donkglhwulnxos",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwrtok301dqnkgl0k66p4py",
    "referenceEndpointMin": "/ReplayURL",
    "referenceEndpointMax": "/ReplayURL",
    "score": 0
  }
}

# StoredVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiws5hes00anp002ng50q3fc",
    "referenceField": "camID",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.eventName": {
    "enabled": True,
    "validationType": "request-field-match",
    "referenceFieldId": "cmiws56xa008jp002vhqm6yfn",
    "referenceField": "eventFilter",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.startTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiws3ab605bknkglsndw6cp5",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiws41yv0005p002amxfzrhq",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "score": 0
  },
  "camList.endTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiws3ab605bknkglsndw6cp5",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiws41yv0005p002amxfzrhq",
    "referenceEndpointMin": "/StoredVideoEventInfos",
    "referenceEndpointMax": "/StoredVideoEventInfos",
    "score": 0
  }
}

# StoredObjectAnalyticsInfos
cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_out_validation = {
  "camList.camID": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwsgzrw02x0p002fnxf1f08",
    "referenceField": "camID",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.analyticsTime": {
    "enabled": True,
    "validationType": "request-field-range-match",
    "rangeOperator": "between",
    "referenceFieldMin": "startTime",
    "referenceFieldMinId": "cmiwsa3je01lnp002owjbqng1",
    "referenceFieldMax": "endTime",
    "referenceFieldMaxId": "cmiwsa57401lsp0021esg4kr1",
    "referenceEndpointMin": "/StoredObjectAnalyticsInfos",
    "referenceEndpointMax": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.anlayticsResultList.analyticsClass": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwsgzse02xcp002b6pfp72a",
    "referenceField": "classFilter",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  },
  "camList.anlayticsResultList.analyticsAttribute": {
    "enabled": True,
    "validationType": "request-field-list-match",
    "referenceFieldId": "cmiwsgzse02xep0024ycdnvrw",
    "referenceField": "attributeFilter",
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "score": 0
  }
}

# cmii7v8pr006g8z1tvo55a50u WebHook 검증 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_inValidation = [
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_in_validation,
]

# cmii7v8pr006g8z1tvo55a50u 검증 리스트
cmii7v8pr006g8z1tvo55a50u_outValidation = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_out_validation,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_out_validation,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_out_validation,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_out_validation,
    cmii7v8pr006g8z1tvo55a50u_ReplayURL_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_out_validation,
    cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_out_validation,
]

