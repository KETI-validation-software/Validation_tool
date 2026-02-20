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

