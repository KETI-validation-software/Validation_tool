from json_checker import OptionalKey
# Authentication
# Input
Authentication_in_schema = {
    "userID": str,
    "userPW": str
}
# Output
Authentication_out_schema = {
    "code": str,
    "message": str,
    "userName": str,
    "userAff": str,
    OptionalKey('accessToken'): str
}
# Capabilities
Capabilities_in_schema = {}
Capabilities_out_schema = {
    "code": str,
    "message": str,
    "transportSupport":
        [
            {
                "transProtocolType": str,
                OptionalKey('transProtocolDesc'): str
            }
        ]
}


# SensorDeviceProfiles
SensorDeviceProfiles_in_schema = {}
SensorDeviceProfiles_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList":
        [
            {
                "sensorDeviceID": str,
                "sensorDeviceType": str,
                "sensorDeviceName": str,
                OptionalKey("sensorDeviceLoc"): {
                    "lon": str,
                    "lat": str,
                    OptionalKey("alt"): str,
                    OptionalKey("desc"): str
                }
            }
        ]
}

# RealtimeSensorData
RealtimeSensorData_in_schema = {
    "sensorDeviceList":
        [
            {
                "sensorDeviceID": str
            }
        ],
    "transProtocol":
        {
            "transProtocolType": str,
            OptionalKey("transProtocolDesc"): str
        },
    OptionalKey("duration"): int,
    OptionalKey("startTime"): int
}
RealtimeSensorData_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList":
        [
            {
                "sensorDeviceID": str,
                "measureTime": int,
                "sensorDeviceType": str,
                "sensorDeviceUnit": str,
                "sensorDeviceValue": str
            }
        ]
}


# RealtimeSensorEventInfos
RealtimeSensorEventInfos_in_schema = {
    "sensorDeviceList": [
        {
            "sensorDeviceID": str
        }
    ],
    "transProtocol": {
        "transProtocolType": str,
        OptionalKey("transProtocolDesc"): str
      },
    OptionalKey("duration"): int,
    OptionalKey("eventFilter"): str,
    OptionalKey("startTime"): int
}

RealtimeSensorEventInfos_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList":
        [
            {
                "sensorDeviceID": str,
                "eventName": str,
                "eventTime": int,
                OptionalKey("eventDesc"): str
            }
        ]
}

# StoredSensorEventInfos
StoredSensorEventInfos_in_schema = {
    "sensorDeviceList":
        [
            {
                "sensorDeviceID": str
            }
        ],
    "timePeriod":
        {
            "startTime": int,
            "endTime": int
        },
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str,
}

StoredSensorEventInfos_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceList":
        [
            {
                "sensorDeviceID": str,
                "eventName": str,
                "eventTime": int,
                OptionalKey("eventDesc"): str
            }
        ]
}

SensorDeviceControl_in_schema = {
    "sensorDeviceID": str,
    OptionalKey('commandType'): str
}

SensorDeviceControl_out_schema = {
    "code": str,
    "message": str,
    "sensorDeviceID": str,
    "sensorDeviceStatus": str
}

WebHook_RealtimeSensorData_out_schema = {
    "sensorDeviceList":
        [
            {
                "sensorDeviceID": str,
                "measureTime": int,
                "sensorDeviceType": str,
                "sensorDeviceUnit": str,
                "sensorDeviceValue": str
            }
        ]

}

WebHook_RealtimeSensorEventInfos_out_schema = {
    "sensorDeviceList":
        [
            {
                "sensorDeviceID": str,
                "eventName": str,
                "eventTime": int,
                OptionalKey("eventDesc"): str
            }
        ]
}


Webhook_out_schema = {
    "code": str,
    "message": str
}



securityInSchema = [Authentication_in_schema,
                    Capabilities_in_schema,
                    SensorDeviceProfiles_in_schema,
                    RealtimeSensorData_in_schema,
                    RealtimeSensorEventInfos_in_schema,
                    StoredSensorEventInfos_in_schema,
                    SensorDeviceControl_in_schema]


securityOutSchema = [
    Authentication_out_schema,
    Capabilities_out_schema,
    SensorDeviceProfiles_out_schema,
    RealtimeSensorData_out_schema,
    RealtimeSensorEventInfos_out_schema,
    StoredSensorEventInfos_out_schema,
    SensorDeviceControl_out_schema,
    Webhook_out_schema
]

securityWebhookSchema = [
    Webhook_out_schema,
    Webhook_out_schema,
    Webhook_out_schema,
    WebHook_RealtimeSensorData_out_schema,
    WebHook_RealtimeSensorEventInfos_out_schema,
    Webhook_out_schema,
    Webhook_out_schema,
]
