# response 모드

# Authentication
Authentication_in_data = {
    "userID": "user001",
    "userPW": "pass001"
}

# Capabilities
Capabilities_in_data = {}

# CameraProfiles
CameraProfiles_in_data = {}

# StoredVideoInfos
StoredVideoInfos_in_data = {
    "timePeriod": {
    "startTime": 20220822163022123,
    "endTime": 20220822163025123
},
    "camList": [
        {
        "camID": "cam001"
    },
        {
        "camID": "cam002"
    }
]
}

# StreamURLs
StreamURLs_in_data = {
    "camList": [
        {
        "camID": "cam001",
        "streamProtocolType": "RTSP"
    }
]
}

# ReplayURL
ReplayURL_in_data = {
    "camList": [
        {
        "camID": "cam001",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "streamProtocolType": "RTSP"
    },
        {
        "camID": "cam002",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "streamProtocolType": "RTSP"
    },
        {
        "camID": "cam003",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "streamProtocolType": "RTSP"
    }
]
}

# RealtimeVideoEventInfos
RealtimeVideoEventInfos_in_data = {
    "camList": [
        {
        "camID": "cam001"
    },
        {
        "camID": "cam002"
    }
],
    "transProtocol": {
    "transProtocolType": "WebHook",
    "transProtocolDesc": "https://127.0.0.1:8090/RealtimeVideoEventInfos"
},
    "duration": 10,
    "eventFilter": "배회",
    "startTime": 20220822163022123
}

# WebHook RealtimeVideoEventInfos
WebHook_RealtimeVideoEventInfos_out_data = {
    "code": 200,
    "message": "성공"
}

# StoredVideoEventInfos
StoredVideoEventInfos_in_data = {
    "code": "200",
    "message": "성공",
    "camList": [
        {
        "camID": "cam0001",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "eventDesc": "AAABVVVVCCCDDssvfdd"
    },
        {
        "camID": "cam0002",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "eventDesc": "FFFeeiiiWWkdjflskdjfoEKK"
    },
        {
        "camID": "cam0003",
        "eventUUID": "event01",
        "eventName": "배회",
        "startTime": 20220822163022123,
        "endTime": 20220822163025123,
        "eventDesc": "iVUhEUgAAACAAAAAgCAYAAA"
    }
]
}

# StoredObjectAnalyticsInfos
StoredObjectAnalyticsInfos_in_data = {
    "timePeriod": {
    "startTime": 20220822163022123,
    "endTime": 20220822163025123
},
    "camList": [
        {
        "camID": "cam0001"
    },
        {
        "camID": "cam0002"
    },
        {
        "camID": "cam0003"
    }
],
    "anayticsFilter": "객체탐지",
    "classFilter": [
    "차량",
    "사람"
]
}

# spec_002 데이터 리스트
spec_002_inData = [
    Authentication_in_data,
    Capabilities_in_data,
    CameraProfiles_in_data,
    StoredVideoInfos_in_data,
    StreamURLs_in_data,
    ReplayURL_in_data,
    RealtimeVideoEventInfos_in_data,
    StoredVideoEventInfos_in_data,
    StoredObjectAnalyticsInfos_in_data,
]

# spec_002 API endpoint
spec_002_messages = [
    "Authentication",
    "Capabilities",
    "CameraProfiles",
    "StoredVideoInfos",
    "StreamURLs",
    "ReplayURL",
    "RealtimeVideoEventInfos",
    "StoredVideoEventInfos",
    "StoredObjectAnalyticsInfos",
]

# spec_002 WebHook 데이터 리스트
spec_002_webhookData = [
    WebHook_RealtimeVideoEventInfos_out_data,
]

# 통합 데이터 리스트 (하위 호환성)
videoInMessage = spec_002_inData

# 통합 API endpoint 리스트 (하위 호환성)
videoMessages = spec_002_messages


# ========== spec_0022: 보안용 센서 시스템 (응답) ==========

# Authentication
Authentication_in_data_sensor = {
    "userID": "user001",
    "userPW": "pass001"
}

# Capabilities
Capabilities_in_data_sensor = {}

# SensorDeviceProfiles
SensorDeviceProfiles_in_data_sensor = {}

# RealtimeSensorData
RealtimeSensorData_in_data_sensor = {
    "sensorDeviceList": [
        {
            "sensorDeviceID": "iot0001"
        },
        {
            "sensorDeviceID": "iot0002"
        }
    ]
}

# RealtimeSensorEventInfos
RealtimeSensorEventInfos_in_data_sensor = {
    "sensorDeviceList": [
        {
            "sensorDeviceID": "iot0001"
        },
        {
            "sensorDeviceID": "iot0002"
        }
    ],
    "transProtocol": {
        "transProtocolType": "WebHook",
        "transProtocolDesc": "https://127.0.0.1:8090/RealtimeSensorEventInfos"
    },
    "duration": 10,
    "eventFilter": "화재",
    "startTime": 20220822163022123
}

# WebHook RealtimeSensorEventInfos
WebHook_RealtimeSensorEventInfos_out_data_sensor = {
    "code": 200,
    "message": "성공"
}

# StoredSensorEventInfos
StoredSensorEventInfos_in_data_sensor = {
    "timePeriod": {
        "startTime": 20220822163022123,
        "endTime": 20220822163025123
    },
    "sensorDeviceList": [
        {
            "sensorDeviceID": "iot0001"
        },
        {
            "sensorDeviceID": "iot0002"
        }
    ],
    "eventFilter": "화재"
}

# SensorDeviceControl
SensorDeviceControl_in_data_sensor = {
    "sensorDeviceID": "iot0001",
    "sensorDeviceControl": "Alarm"
}

# spec_0022 데이터 리스트
spec_0022_inData = [
    Authentication_in_data_sensor,
    Capabilities_in_data_sensor,
    SensorDeviceProfiles_in_data_sensor,
    RealtimeSensorData_in_data_sensor,
    RealtimeSensorEventInfos_in_data_sensor,
    StoredSensorEventInfos_in_data_sensor,
    SensorDeviceControl_in_data_sensor,
]

# spec_0022 API endpoint
spec_0022_messages = [
    "Authentication",
    "Capabilities",
    "SensorDeviceProfiles",
    "RealtimeSensorData",
    "RealtimeSensorEventInfos",
    "StoredSensorEventInfos",
    "SensorDeviceControl",
]

# spec_0022 WebHook 데이터 리스트
spec_0022_webhookData = [
    WebHook_RealtimeSensorEventInfos_out_data_sensor,
]



