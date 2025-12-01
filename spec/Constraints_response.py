# Authentication
cmii7shen005i8z1tagevx4qh_Authentication_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "valueType": "preset",
    "required": True
  }
}

# cmii7shen005i8z1tagevx4qh 검증 리스트
cmii7shen005i8z1tagevx4qh_outConstraints = [
    cmii7shen005i8z1tagevx4qh_Authentication_out_constraints,
]

# Authentication
cmii7pysb004k8z1tts0npxfm_Authentication_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "valueType": "preset",
    "required": False
  }
}

# Capabilities
cmii7pysb004k8z1tts0npxfm_Capabilities_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "valueType": "preset",
    "required": False
  }
}

# cmii7pysb004k8z1tts0npxfm 검증 리스트
cmii7pysb004k8z1tts0npxfm_outConstraints = [
    cmii7pysb004k8z1tts0npxfm_Authentication_out_constraints,
    cmii7pysb004k8z1tts0npxfm_Capabilities_out_constraints,
]

# Authentication
cmii7lxbn002s8z1t1i9uudf0_Authentication_out_constraints = {
  "code": {
    "valueType": "preset",
    "required": True
  },
  "message": {
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "valueType": "preset",
    "required": False
  }
}

# cmii7lxbn002s8z1t1i9uudf0 검증 리스트
cmii7lxbn002s8z1t1i9uudf0_outConstraints = [
    cmii7lxbn002s8z1t1i9uudf0_Authentication_out_constraints,
]

