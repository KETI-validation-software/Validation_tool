# response 모드

# Authentication
cmgatbdp000bqihlexmywusvq_Authentication_out_data = {
    "code": "",
    "message": "",
    "userName": "",
    "userAff": "",
    "accessToken": ""
}

# Capabilities
cmgatbdp000bqihlexmywusvq_Capabilities_out_data = {
    "code": "",
    "message": "",
    "transportSupport": [
        {
        "transProtocolType": "",
        "transProtocolDesc": ""
    }
]
}

# SensorDeviceProfiles
cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_out_data = {
    "code": "",
    "message": "",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "",
        "sensorDeviceType": "",
        "sensorDeviceName": "",
        "sensorDeviceLoc": {
        "lon": "",
        "lat": "",
        "alt": "",
        "desc": ""
    }
    }
]
}

# RealtimeSensorData
cmgatbdp000bqihlexmywusvq_RealtimeSensorData_out_data = {
    "code": "",
    "message": "",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "",
        "measureTime": 0,
        "sensorDeviceType": "",
        "sensorDeviceUnit": "",
        "sensorDeviceValue": ""
    }
]
}

# RealtimeSensorEventInfos
cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_out_data = {
    "code": "",
    "message": "",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "",
        "eventName": "",
        "eventTime": 0,
        "eventDesc": ""
    }
]
}

# StoredSensorEventInfos
cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_out_data = {
    "code": "",
    "message": "",
    "sensorDeviceList": [
        {
        "sensorDeviceID": "",
        "eventName": "",
        "eventTime": 0,
        "eventDesc": ""
    }
]
}

# SensorDeviceControl
cmgatbdp000bqihlexmywusvq_SensorDeviceControl_out_data = {
    "code": "",
    "message": "",
    "sensorDeviceID": "",
    "sensorDeviceStatus": ""
}

# cmgatbdp000bqihlexmywusvq 데이터 리스트
cmgatbdp000bqihlexmywusvq_inData = [
    cmgatbdp000bqihlexmywusvq_Authentication_out_data,
    cmgatbdp000bqihlexmywusvq_Capabilities_out_data,
    cmgatbdp000bqihlexmywusvq_SensorDeviceProfiles_out_data,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorData_out_data,
    cmgatbdp000bqihlexmywusvq_RealtimeSensorEventInfos_out_data,
    cmgatbdp000bqihlexmywusvq_StoredSensorEventInfos_out_data,
    cmgatbdp000bqihlexmywusvq_SensorDeviceControl_out_data,
]

# cmgatbdp000bqihlexmywusvq API endpoint
cmgatbdp000bqihlexmywusvq_messages = [
    "Authentication",
    "Capabilities",
    "SensorDeviceProfiles",
    "RealtimeSensorData",
    "RealtimeSensorEventInfos",
    "StoredSensorEventInfos",
    "SensorDeviceControl",
]

# Authentication
cmgasj98w009aihlezm0fe6cs_Authentication_out_data = {
    "code": "",
    "message": "",
    "userName": "",
    "userAff": "",
    "accessToken": ""
}

# Capabilities
cmgasj98w009aihlezm0fe6cs_Capabilities_out_data = {
    "code": "",
    "message": "",
    "transportSupport": [
        {
        "transProtocolType": "",
        "transProtocolDesc": ""
    }
]
}

# DoorProfiles
cmgasj98w009aihlezm0fe6cs_DoorProfiles_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorID": "",
        "doorName": "",
        "doorRelayStatus": "",
        "doorSensor": "",
        "doorLoc": {
        "lon": "",
        "lat": "",
        "alt": "",
        "desc": ""
    },
        "bioDeviceList": [
            {
            "bioDeviceID": "",
            "bioDeviceName": "",
            "bioDeviceAuthTypeList": []
        }
    ],
        "otherDeviceList": [
            {
            "otherDeviceID": "",
            "otherDeviceName": "",
            "otherDeviceAuthTypeList": []
        }
    ]
    }
]
}

# AccessUserInfos
cmgasj98w009aihlezm0fe6cs_AccessUserInfos_out_data = {
    "code": "",
    "message": "",
    "userList": [
        {
        "userID": "",
        "userName": "",
        "userDesc": "",
        "doorList": [
            {
            "doorID": "",
            "timePeriod": {
            "startTime": 0,
            "endTime": 0
        }
        }
    ]
    }
]
}

# RealtimeVerifEventInfos
cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "eventTime": 0,
        "doorID": "",
        "userID": "",
        "bioAuthTypeList": [],
        "otherAuthTypeList": [],
        "eventName": "",
        "eventDesc": ""
    }
]
}

# StoredVerifEventInfos
cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "eventTime": 0,
        "doorID": "",
        "userID": "",
        "bioAuthTypeList": [],
        "otherAuthTypeList": [],
        "eventName": "",
        "eventDesc": ""
    }
]
}

# RealtimeDoorStatus
cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_out_data = {
    "code": "",
    "message": "",
    "doorList": [
        {
        "doorID": "",
        "doorName": "",
        "doorRelaySensor": "",
        "doorSensor": ""
    }
]
}

# DoorControl
cmgasj98w009aihlezm0fe6cs_DoorControl_out_data = {
    "code": "",
    "message": ""
}

# cmgasj98w009aihlezm0fe6cs 데이터 리스트
cmgasj98w009aihlezm0fe6cs_inData = [
    cmgasj98w009aihlezm0fe6cs_Authentication_out_data,
    cmgasj98w009aihlezm0fe6cs_Capabilities_out_data,
    cmgasj98w009aihlezm0fe6cs_DoorProfiles_out_data,
    cmgasj98w009aihlezm0fe6cs_AccessUserInfos_out_data,
    cmgasj98w009aihlezm0fe6cs_RealtimeVerifEventInfos_out_data,
    cmgasj98w009aihlezm0fe6cs_StoredVerifEventInfos_out_data,
    cmgasj98w009aihlezm0fe6cs_RealtimeDoorStatus_out_data,
    cmgasj98w009aihlezm0fe6cs_DoorControl_out_data,
]

# cmgasj98w009aihlezm0fe6cs API endpoint
cmgasj98w009aihlezm0fe6cs_messages = [
    "Authentication",
    "Capabilities",
    "DoorProfiles",
    "AccessUserInfos",
    "RealtimeVerifEventInfos",
    "StoredVerifEventInfos",
    "RealtimeDoorStatus",
    "DoorControl",
]

# Authentication
cmga0l5mh005dihlet5fcoj0o_Authentication_out_data = {
    "code": "",
    "message": "",
    "userName": "",
    "userAff": "",
    "accessToken": ""
}

# Capabilities
cmga0l5mh005dihlet5fcoj0o_Capabilities_out_data = {
    "code": "",
    "message": "",
    "streamingSupport": [
        {
        "streamProtocolType": "",
        "streamProtocolDesc": ""
    }
],
    "transportSupport": [
        {
        "transProtocolType": "",
        "transProtocolDesc": ""
    }
]
}

# CameraProfiles
cmga0l5mh005dihlet5fcoj0o_CameraProfiles_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "camName": "",
        "camLoc": {
        "lon": "",
        "lat": "",
        "alt": "",
        "desc": ""
    },
        "camConfig": {
        "camType": ""
    }
    }
]
}

# StoredVideoInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "timeList": [
            {
            "startTime": 0,
            "endTime": 0
        }
    ]
    }
],
    "camID2": ""
}

# StreamURLs
cmga0l5mh005dihlet5fcoj0o_StreamURLs_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "accessID": "",
        "accessPW": "",
        "camURL": "",
        "videoInfo": {
        "resolution": "",
        "fps": 0,
        "videoCodec": "",
        "audioCodec": ""
    }
    }
]
}

# ReplayURL
cmga0l5mh005dihlet5fcoj0o_ReplayURL_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "accessID": "",
        "accessPW": "",
        "startTime": 0,
        "endTime": 0,
        "camURL": "",
        "videoInfo": {
        "resolution": "",
        "fps": 0,
        "videoCodec": "",
        "audioCodec": ""
    }
    }
]
}

# RealtimeVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_RealtimeVideoEventInfos_out_data = {
    "code": "",
    "message": ""
}

# StoredVideoEventInfos
cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "eventUUID": "",
        "eventName": "",
        "startTime": 0,
        "endTime": 0,
        "eventDesc": ""
    }
]
}

# StoredObjectAnalyticsInfos
cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_out_data = {
    "code": "",
    "message": "",
    "camList": [
        {
        "camID": "",
        "analyticsTime": 0,
        "anlayticsResultList": [
            {
            "anayticsID": "",
            "analyticsClass": "",
            "analyticsAttribute": [],
            "analyticsConfidence": 0,
            "analyticsBoundingBox": {
            "left": 0,
            "top": 0,
            "right": 0,
            "bottom": 0
        },
            "analyticsDesc": ""
        }
    ]
    }
]
}

# PtzStatus
cmga0l5mh005dihlet5fcoj0o_PtzStatus_out_data = {
    "code": "",
    "message": "",
    "position": {
    "pan": 0,
    "tilt": 0,
    "zoom": 0
},
    "moveStatus": {
    "pan": "",
    "tilt": "",
    "zoom": ""
}
}

# PtzContinuousMove
cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_out_data = {
    "code": "",
    "message": ""
}

# PtzStop
cmga0l5mh005dihlet5fcoj0o_PtzStop_out_data = {
    "code": "",
    "message": ""
}

# cmga0l5mh005dihlet5fcoj0o 데이터 리스트
cmga0l5mh005dihlet5fcoj0o_inData = [
    cmga0l5mh005dihlet5fcoj0o_Authentication_out_data,
    cmga0l5mh005dihlet5fcoj0o_Capabilities_out_data,
    cmga0l5mh005dihlet5fcoj0o_CameraProfiles_out_data,
    cmga0l5mh005dihlet5fcoj0o_StoredVideoInfos_out_data,
    cmga0l5mh005dihlet5fcoj0o_StreamURLs_out_data,
    cmga0l5mh005dihlet5fcoj0o_ReplayURL_out_data,
    cmga0l5mh005dihlet5fcoj0o_RealtimeVideoEventInfos_out_data,
    cmga0l5mh005dihlet5fcoj0o_StoredVideoEventInfos_out_data,
    cmga0l5mh005dihlet5fcoj0o_StoredObjectAnalyticsInfos_out_data,
    cmga0l5mh005dihlet5fcoj0o_PtzStatus_out_data,
    cmga0l5mh005dihlet5fcoj0o_PtzContinuousMove_out_data,
    cmga0l5mh005dihlet5fcoj0o_PtzStop_out_data,
]

# cmga0l5mh005dihlet5fcoj0o API endpoint
cmga0l5mh005dihlet5fcoj0o_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "StoredVideoInfos",
    "StreamURLs",
    "ReplayURL",
    "RealtimeVideoEventInfos",
    "StoredVideoEventInfos",
    "StoredObjectAnalyticsInfos",
    "PtzStatus",
    "PtzContinuousMove",
    "PtzStop",
]

