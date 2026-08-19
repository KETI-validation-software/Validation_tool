# Authentication
cmsy90xd705aarc0quh4je1k0_Authentication_out_constraints = {
  "code": {
    "id": "cmsy933s005b4rc0q1bu7q36u",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmsy933s005b6rc0q9ln4u0gg",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmsy933s105b8rc0qxs8os3sl",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmsy933s105barc0qf0hq1zte",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmsy90xd705aarc0quh4je1k0_Capabilities_out_constraints = {
  "code": {
    "id": "cmsy99cdu05burc0q8dj8o9jl",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmsy99cdv05bwrc0q41gxg72v",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport": {
    "id": "cmsy99ceb05c2rc0q3l9uzsfn",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport.streamProtocolType": {
    "id": "cmsy99ceh05c6rc0qflrweycc",
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "id": "cmsy99ceb05c4rc0q89gxvlbn",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmsy99ceh05c8rc0qikmvauni",
    "valueType": "preset",
    "required": True
  }
}

# CameraProfiles
cmsy90xd705aarc0quh4je1k0_CameraProfiles_out_constraints = {
  "code": {
    "id": "cmsy9cxmi05ctrc0qnkfvw41h",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmsy9cxmi05cvrc0qk5x0ya4e",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmsymtwqs0015ilyr0bu6yo1i",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmsymtwqv0017ilyrzgk96d75",
    "valueType": "preset",
    "required": True
  },
  "camList.camName": {
    "id": "cmsymtwqw0019ilyra2wsox7u",
    "valueType": "preset",
    "required": True
  }
}

# StreamURLs
cmsy90xd705aarc0quh4je1k0_StreamURLs_out_constraints = {
  "code": {
    "id": "cmsyatlx005elrc0q63l19r0r",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmsyatlx105enrc0qd2zf1fop",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmsyatlxe05errc0qit7xzw9g",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmsyatlxi05etrc0qy5seij0n",
    "referenceFieldId": "cmsyartum05e9rc0q3khum64e",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StreamURLs",
    "referenceField": "camID"
  }
}

# RealtimeVideoEventInfos
cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_out_constraints = {
  "code": {
    "id": "cmsyb2knd05fzrc0qrd243jt5",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmsyb2kne05g1rc0qcumena44",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeVideoEventInfos WebHook IN Constraints
cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_webhook_in_constraints = {
  "camList": {
    "id": "cmsyblhqz05gqrc0qzglzm2m6",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmsyblhr605gsrc0q5p1gsf9y",
    "referenceFieldId": "cmsyb27rc05fprc0qj4tneg24",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "referenceField": "camID"
  },
  "camList.eventUUID": {
    "id": "cmsyblhr605gurc0qlthh6a2f",
    "valueType": "preset",
    "required": True
  },
  "camList.eventName": {
    "id": "cmsyblhr705gwrc0qd1te6c1t",
    "referenceFieldId": "cmsybo8m605hlrc0qpu76eu67",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "referenceField": "eventFilter"
  },
  "camList.startTime": {
    "id": "cmsyblhr805gyrc0qv9jwy6ll",
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal",
      "minFieldId": "cmsyblhr805gyrc0qv9jwy6ll",
      "minEndpoint": "/RealtimeVideoEventInfos"
    },
    "requestRangeMinEndpoint": "/RealtimeVideoEventInfos"
  }
}

# cmsy90xd705aarc0quh4je1k0 검증 리스트
cmsy90xd705aarc0quh4je1k0_outConstraints = [
    cmsy90xd705aarc0quh4je1k0_Authentication_out_constraints,
    cmsy90xd705aarc0quh4je1k0_Capabilities_out_constraints,
    cmsy90xd705aarc0quh4je1k0_CameraProfiles_out_constraints,
    cmsy90xd705aarc0quh4je1k0_StreamURLs_out_constraints,
    cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_out_constraints,
]

# cmsy90xd705aarc0quh4je1k0 WebHook Constraints 리스트
cmsy90xd705aarc0quh4je1k0_webhook_inConstraints = [
    None,
    None,
    None,
    None,
    cmsy90xd705aarc0quh4je1k0_RealtimeVideoEventInfos_webhook_in_constraints,
]

