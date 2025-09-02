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
    "streamingSupport":
        [{
            "streamProtocolType": str,
            OptionalKey('streamProtocolDesc'): str
        }],
    "transportSupport":
        [{
            "transProtocolType": str,
            OptionalKey('transProtocolDesc'):str
        }]
}
# CameraProfiles
CameraProfiles_in_schema = {}
CameraProfiles_out_schema = {
    "code": str,
    "message": str,
    "camList":
        [{
            "camID": str,
            "camName": str,
            OptionalKey("camLoc"): {
                "lon": str,
                "lat": str,
                OptionalKey("alt"):str,
                OptionalKey("desc"):str
            },
            OptionalKey("camConfig"): {
                "camType": str
            }
        }]
}
# StoredVideoInfos
StoredVideoInfos_in_schema = {
    "timePeriod": {
        "startTime": int,
        "endTime": int
    },
    OptionalKey("camList"):
        [ {
            "camID": str
        }
        ]
}
StoredVideoInfos_out_schema = {
    "code": str,
    "message": str,
    "camList":
        [{
            "camID": str,
            "timeList": [{
                "startTime": int,
                OptionalKey("endTime"): int
            }]
        }
        ]
}
# StreamURLs
StreamURLs_in_schema = {
    "camList":
        [{
            "camID": str,
            "streamProtocolType": str,
        }]
}


StreamURLs_out_schema = {
    "code": str,
    "message": str,
    "camList":
        [{
            "camID": str,
            OptionalKey("accessID"): str,
            OptionalKey("accessPW"): str,
            "camURL": str
        }
        ]
}
# ReplayURL
ReplayURL_in_schema = {
    "camList":
        [{
            "camID": str,
            "startTime": int,
            "endTime": int,
            "streamProtocolType": str
        }
        ]
}
ReplayURL_out_schema = {
    "code": str,
    "message": str,
    "camList":
        [{
            "camID": str,
            "startTime": int,
            "camURL": str,
            OptionalKey("accessID"): str,
            OptionalKey("accessPW"): str,
            OptionalKey("endTime"): int
        }
        ]
}
# RealtimeVideoEventInfos
RealtimeVideoEventInfos_in_schema = {
    "camList":
        [{
            "camID": str
        }],
    "transProtocol": {
        "transProtocolType": str,
        OptionalKey("transProtocolDesc"):str
    },
    OptionalKey("duration"): int,
    OptionalKey("eventFilter"): str,
    OptionalKey("classFilter"): str,
    OptionalKey("startTime"): int
}

RealtimeVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
    "camList":
        [
            {
                "camID": str,
                "eventUUID": str,
                "eventName": str,
                "startTime": int,
                OptionalKey("endTime"): int,
                OptionalKey("eventDesc"): str
            }
        ]
}
# StoredVideoEventInfos
StoredVideoEventInfos_in_schema = {
    "timePeriod": {
        "startTime": int,
        "endTime": int
    },
    OptionalKey("camList"):
        [{
            "camID": str
        }
        ],
    OptionalKey("maxCount"): int,
    OptionalKey("eventFilter"): str,
    OptionalKey("classFilter"): str
}

StoredVideoEventInfos_out_schema = {
    "code": str,
    "message": str,
    "camList":
        [{
            "camID": str,
            "eventUUID": str,
            "eventName": str,
            "startTime": int,
            OptionalKey("endTime"): int,
            OptionalKey("eventDesc"): str
        }
        ]
}

StoredObjectAnalyticsInfos_in_schema = {
    "timePeriod": {
        "startTime": int,
        "endTime": int
    },
    OptionalKey("camList"):
        [
            {
                "camID": str
            }
        ],
    OptionalKey("filterList"):
        [{
            OptionalKey("eventFilter"): [str],
            OptionalKey("attributeFilter"): [str]
        }
        ]
}

StoredObjectAnalyticsInfos_out_schema = {
    "code": str,
    "message": str,
     OptionalKey("camList"):
     [ {
        "camID": str,
        "analyticsTime": int,
        OptionalKey("anlayticsResultList"):
        [ {
            "anayticsID": str,
            "analyticsClass": str,
            OptionalKey("analyticsAttribute"): [str],
            OptionalKey("analyticsConfidence"): int,
            OptionalKey("aanalyticsDesc"): str,
            OptionalKey("analyticsBoundingBox"):
             {
                "left": int,
                "top": int,
                "right": int,
                "bottom": int
            }
          }
       ]
     }
   ]
}

WebHook_RealtimeVideoEventInfos_out_schema = {
    "camList":
        [
            {
                "camID": str,
                "eventUUID": str,
                "eventName": str,
                "startTime": int,
                OptionalKey("endTime"): int,
                OptionalKey("eventDesc"): str
            }
        ]
}

Webhook_out_schema = {
    "code": str,
    "message": str
}




videoInSchema = [Authentication_in_schema,
                 Capabilities_in_schema,
                 CameraProfiles_in_schema,
                 StoredVideoInfos_in_schema,
                 StreamURLs_in_schema,
                 ReplayURL_in_schema,
                 RealtimeVideoEventInfos_in_schema,
                 StoredVideoEventInfos_in_schema,
                 StoredObjectAnalyticsInfos_in_schema]

videoOutSchema = [Authentication_out_schema,
                  Capabilities_out_schema,
                  CameraProfiles_out_schema,
                  StoredVideoInfos_out_schema,
                  StreamURLs_out_schema,
                  ReplayURL_out_schema,
                  RealtimeVideoEventInfos_out_schema,
                  StoredVideoEventInfos_out_schema,
                  StoredObjectAnalyticsInfos_out_schema,
                  Webhook_out_schema]

videoWebhookSchema = [
    Webhook_out_schema,
    Webhook_out_schema,
    Webhook_out_schema,
    Webhook_out_schema,
    Webhook_out_schema,
    Webhook_out_schema,
    WebHook_RealtimeVideoEventInfos_out_schema
]