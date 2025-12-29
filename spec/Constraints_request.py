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
    "id": "cmiwrn6a9003nnkglvme2ccl1",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrn6ab003pnkgl7f78y9t6",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  }
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_in_constraints = {
  "camList": {
    "id": "cmiwrtok001dknkgluevidcla",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrtok201dmnkgl6gzxhft5",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "camList.startTime": {
    "id": "cmiwrtok201donkglhwulnxos",
    "valueType": "preset",
    "required": True
  },
  "camList.endTime": {
    "id": "cmiwrtok301dqnkgl0k66p4py",
    "valueType": "preset",
    "required": True
  },
  "camList.streamProtocolType": {
    "id": "cmiwrtok301dsnkgl3t29d3op",
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
    "id": "cmiws5her00alp002y1uhjddp",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiws5hes00anp002ng50q3fc",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "maxCount": {
    "id": "cmiws4rcl005up002n2yhi3pu",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmiws56xa008jp002vhqm6yfn",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "validValueField": "videoEvent",
    "validValues": [
      "Loitering",
      "Intrusion"
    ]
  },
  "classFilter": {
    "id": "cmiws5ggr00aip0022iuh6at3",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "validValueField": "videoObject",
    "validValues": [
      "Human"
    ]
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
    "id": "cmiwsgzru02wyp0022uq3k278",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwsgzrw02x0p002fnxf1f08",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "filterList": {
    "id": "cmiwsgzsc02xap002gifjhi5v",
    "valueType": "preset",
    "required": False
  },
  "filterList.classFilter": {
    "id": "cmjbl6af602ascfb33ejplfny",
    "valueType": "preset",
    "required": True
  },
  "filterList.attributeFilter": {
    "id": "cmjbl6afe02awcfb3ourzmfal",
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
    cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_ReplayURL_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_in_constraints,
]

# cmii7v8pr006g8z1tvo55a50u WebHook Constraints 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_outConstraints = [
    None,
    None,
    None,
    None,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints,
    None,
    None,
    None,
    None,
]

