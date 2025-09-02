
# Authentication
# Input
Authentication_in_data = {
    "userID": "user0001",
    "userPW": "pass0001"
}

Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}
# Capabilities
Capabilities_in_data = {}
Capabilities_out_data = {
    "code": "200",
    "message": "성공",
    "transportSupport":
        [{
           "transProtocolType": "HTTP_API",
            "transProtocolDesc": "description"
        }]
}

# SensorDeviceProfiles
SensorDeviceProfiles_in_data = {}
SensorDeviceProfiles_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList":
        [{
            "sensorDeviceID": "iot0001",
            "sensorDeviceType": "온도",
            "sensorDeviceName": "온도 센서",
            "sensorDeviceLoc": {
                "lon":"127.127730",
                "lat": "38.439801",
                "alt": "32.131",
                "desc": "3층복도"
            }
        },
        {
            "sensorDeviceID": "iot0002",
            "sensorDeviceType": "온도",
            "sensorDeviceName": "온도 센서",
            "sensorDeviceLoc": {
                "lon":"127.127730",
                "lat": "38.439801",
                "alt": "32.131",
                "desc": "3층복도"
            }
        }
        ]
}
# RealtimeSensorData
RealtimeSensorData_in_data = {
    "sensorDeviceList":
      [ {
            "sensorDeviceID": "iot0001"
        },{
            "sensorDeviceID": "iot0002"
        },
        {
            "sensorDeviceID": "iot0003"
        }
      ],
    "duration": 100,
    "transProtocol": {
    "transProtocolType": "HTTP_API",
    "transProtocolDesc":"descriptoin"
    },
    "startTime": 20220822163022123
}

RealtimeSensorData_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList":
     [ {
        "sensorDeviceID": "iot0001",
        "measureTime": 20220822163022123,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "90"
      },
      {
        "sensorDeviceID": "iot0002",
        "measureTime": 20220822163022123,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "36"
      },
      {
        "sensorDeviceID": "iot0003",
        "measureTime": 20220822163022123,
        "sensorDeviceType": "온도",
        "sensorDeviceUnit": "섭씨",
        "sensorDeviceValue": "36"
      }
    ]
}


# RealtimeSensorEventInfos
RealtimeSensorEventInfos_in_data = {
    "sensorDeviceList":
     [ {
        "sensorDeviceID": "iot0001"

      },
      {
        "sensorDeviceID": "iot0002"

      }
    ],
   "transProtocol": {
        "transProtocolType": "HTTP_API",
        "transProtocolDesc":"description"

   },
   "duration": 200,
   "eventFilter": "화재",
   "startTime": 20220822163022123

}

RealtimeSensorEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList":
     [ {
        "sensorDeviceID": "iot0001",
        "eventName": "화재",
        "eventTime": 20220822163022123,
        "eventDesc": "100도"
      },
      {
        "sensorDeviceID": "iot0002",
        "eventName": "화재",
        "eventTime": 20220822163022123,
        "eventDesc": "200도"
      }
    ]
}

# StoredSensorEventInfos
StoredSensorEventInfos_in_data = {
    "timePeriod":
     {
        "startTime": 20220822163022123,
        "endTime": 20220822263022123
     },
    "sensorDeviceList": [ {
        "sensorDeviceID": "iot0001"
     }, {
        "sensorDeviceID": "iot0002"
     } ],
    "maxCount": 10,
    "eventFilter": "화재"
}


StoredSensorEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceList":
     [ {
        "sensorDeviceID": "iot0001",
        "eventName": "화재",
        "eventTime": 20220822163022123,
        "eventDesc": "100도"
      },
      {
        "sensorDeviceID": "iot0002",
        "eventName": "화재",
        "eventTime": 20220822163022123,
        "eventDesc": "100도"
      }
    ]
}

SensorDeviceControl_in_data = {
    "sensorDeviceID": "iot0001",
    "commandType": "Alarm"

}

SensorDeviceControl_out_data = {
    "code": "200",
    "message": "성공",
    "sensorDeviceID": "iot0001",
    "sensorDeviceStatus": "Alarm"
}

Webhook_out_data = {
    "code": "200",
    "message": "성공"
}

securityInMessage = [Authentication_in_data,
                  Capabilities_in_data,
                  SensorDeviceProfiles_in_data,
                  RealtimeSensorData_in_data,
                  RealtimeSensorEventInfos_in_data,
                  StoredSensorEventInfos_in_data,
                   SensorDeviceControl_in_data
                     ]

securityOutMessage = [Authentication_out_data,
                      Capabilities_out_data,
                      SensorDeviceProfiles_out_data,
                      RealtimeSensorData_out_data,
                      RealtimeSensorEventInfos_out_data,
                      StoredSensorEventInfos_out_data,
                      SensorDeviceControl_out_data,
                      Webhook_out_data]

securityMessages = ["Authentication",
                 "Capabilities",
                 "SensorDeviceProfiles",
                 "RealtimeSensorData",
                 "RealtimeSensorEventInfos",
                 "StoredSensorEventInfos",
                    "SensorDeviceControl"]
