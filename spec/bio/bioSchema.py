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
     [{
        "transProtocolType": str,
         OptionalKey("transProtocolDesc"):str
     }]
}

# DoorProfiles
DoorProfiles_in_schema = {}
DoorProfiles_out_schema = {
    "code": str,
    "message": str,
    "doorList":
     [ {
        "doorID": str,
        "doorName": str,
        "doorRelayStatus": str,
        OptionalKey("doorSensor"): str,
        OptionalKey("doorLoc"): {
            "lon": str,
            "lat": str,
            OptionalKey("alt"): str,
            OptionalKey("desc"): str,
         },
        OptionalKey("bioDeviceList"): [{
            OptionalKey("bioDeviceID"): str,
            OptionalKey("bioDeviceName"): str,
            "bioDeviceAuthTypeList": [str]
         }],
        OptionalKey("otherDeviceList"): [ {
            OptionalKey("otherDeviceID"): str,
            OptionalKey("otherDeviceName"): str,
            "otherDeviceAuthTypeList": [str]
         } ]
      }
    ]
}
# AccessUserInfos
AccessUserInfos_in_schema = {}
AccessUserInfos_out_schema = {
    "code": str,
    "message": str,
    "userList": [
        {
            "userID": str,
            "userName": str,
            OptionalKey("userDesc"): str,
            "doorList": [{
                "doorID": str,
                "timePeriod": {
                    "startTime": int,
                    "endTime": int
                }
            }
            ]
      }
    ]
}
# RealtimeVerifEventInfos
RealtimeVerifEventInfos_in_schema = {
    "doorList":
     [{
        "doorID": str
      }
    ],
   OptionalKey("duration"): int,
   "transProtocol": {
        "transProtocolType": str,
        OptionalKey("transProtocolDesc"):str
    },
    OptionalKey("eventFilter"): str,
    OptionalKey("startTime"): int

}
RealtimeVerifEventInfos_out_schema = {
    "code": str,
    "message": str,
    "doorList":
     [ {
        "eventTime": int,
        "doorID": str,
        OptionalKey("userID"): str,
        OptionalKey("bioAuthTypeList"): [str],
        OptionalKey("otherAuthTypeList"): [str],
        "eventName": str,
        OptionalKey("eventDesc"): str
       }]
}

# StoredVerifEventInfos
StoredVerifEventInfos_in_schema = {
    "timePeriod":
        {
            "startTime": int,
            "endTime": int
        },
    "doorList": [ {
        "doorID": str
     } ],
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str
}

StoredVerifEventInfos_out_schema={
    "code": str,
    "message": str,
    "doorList":
     [{
        "eventTime": int,
        "doorID": str,
        OptionalKey("userID"): str,
        OptionalKey("bioAuthTypeList"): [str],
        OptionalKey("otherAuthTypeList"): [str],
         "eventName": str,
        OptionalKey("eventDesc"): str
       }]
}
# RealtimeDoorStatus
RealtimeDoorStatus_in_schema =  {
    "doorList":
     [ {
        "doorID": str
      }
     ],
   OptionalKey("duration"): int,
   "transProtocol": {
        "transProtocolType": str,
        OptionalKey("transProtocolDesc"): str
    },
   OptionalKey("startTime"): int
}

RealtimeDoorStatus_out_schema = {
    "code": str,
    "message": str,
    "doorList":
     [ {
        "doorID": str,
        "doorName": str,
        OptionalKey("doorRelaySensor"): str,
        OptionalKey("doorSensor"): str
       }
    ]
}

DoorControl_in_schema = {
    "doorID": str,
    "commandType": str
}

DoorControl_out_schema = {
    "code": str,
    "message": str
}

Webhook_out_schema = {
    "code": str,
    "message": str
}

WeHook_RealtimeVerifEventInfos_out_schema = {
    "doorList":
        [{
            "eventTime": int,
            "doorID": str,
            OptionalKey("userID"): str,
            OptionalKey("bioAuthTypeList"): [str],
            OptionalKey("otherAuthTypeList"): [str],
            "eventName": str,
            OptionalKey("eventDesc"): str
        }]
}

WebHook_RealtimeDoorStatus_out_schema = {
    "doorList":
        [{
            "doorID": str,
            "doorName": str,
            OptionalKey("doorRelaySensor"): str,
            OptionalKey("doorSensor"): str
        }
        ]


}

bioInSchema = [Authentication_in_schema,
               Capabilities_in_schema,
               DoorProfiles_in_schema,
               AccessUserInfos_in_schema,
               RealtimeVerifEventInfos_in_schema,
               StoredVerifEventInfos_in_schema,
               RealtimeDoorStatus_in_schema,
               DoorControl_in_schema]

bioOutSchema = [Authentication_out_schema,
                Capabilities_out_schema,
                DoorProfiles_out_schema,
                AccessUserInfos_out_schema,
                RealtimeVerifEventInfos_out_schema,
                StoredVerifEventInfos_out_schema,
                RealtimeDoorStatus_out_schema,
                DoorControl_out_schema,
                Webhook_out_schema
            ]

bioWebhookSchema = [
    Webhook_out_schema,
    Webhook_out_schema,
    Webhook_out_schema,
    Webhook_out_schema,
    WeHook_RealtimeVerifEventInfos_out_schema,
    Webhook_out_schema,
    WebHook_RealtimeDoorStatus_out_schema,
    Webhook_out_schema
    ]