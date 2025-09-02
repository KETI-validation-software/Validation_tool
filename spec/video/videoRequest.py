

Authentication_in_data = {
    "userID": "user001",
    "userPW": "pass001"
}

Authentication_out_data = {
    "code": "200",
    "message": "성공",
    "userName": "관리자",
    "userAff": "오산시청",
    "accessToken": "abcde1234"
}

Capabilities_in_data = {

}

Capabilities_out_data = {
    "code": "200",
    "message": "성공",
    "streamingSupport":
        [{
            "streamProtocolType": "RTSP",
            "streamProtocolDesc": "Unicast"
        }],
    "transportSupport":
        [{
            "transProtocolType": "HTTP_API",
            "transProtocolDesc": "desc"
        }]
}

CameraProfiles_in_data = {

}


CameraProfiles_out_data = {
    "code": "200",
    "message": "성공",
    "camList":
        [{
            "camID": "cam0001",
            "camName": "카메라1",
            "camLoc": {
                "lon": "127.127730",
                "lat": "38.439801",
                "alt": "32.131",
                "desc": "3층복도"
            },
            "camConfig": {
                "camType": "PTZ"
            }
        },
            {
                "camID": "cam0002",
                "camName": "카메라2",
                "camLoc": {
                    "lon": "127.2887",
                    "lat": "37.33671"
                },
                "camConfig": {
                    "camType": "dome"
                }
            }
        ]
}

# StoredVideoInfos
StoredVideoInfos_in_data = {
    "timePeriod": {
        "startTime": 20220822163022123,
        "endTime": 20220822163025123
    }, "camList":
        [{
            "camID": "cam0001"
        },
            {
                "camID": "cam0002"
            }
        ]
}


StoredVideoInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList":
        [{
            "camID": "cam0001",
            "timeList": [{
                "startTime": 20220822163022123,
                "endTime": 20220822163025123
            }]
        },
            {
                "camID": "cam0002",
                "timeList": [{
                    "startTime": 20220822163022123,
                    "endTime": 20220822163025123
                }]
            }
        ]
}
# StreamURLs
StreamURLs_in_data = {
    "camList":
        [{
            "camID": "cam0001",
            "streamProtocolType": " RTSP"
        },
            {
                "camID": "cam0002",
                "streamProtocolType": " RTSP"
            },
            {
                "camID": "cam0003",
                "streamProtocolType": " RTSP"
            }
        ]
}

StreamURLs_out_data = {
    "code": "200",
    "message": "성공",
    "camList":
        [{
            "camID": "cam0001",
            "accessID": "conn0001",
            "accessPW": "1234",
            "camURL": "rtsp://192.168.0.1:8000"
        },
            {
                "camID": "cam0002",
                "camURL": "rtsp://192.168.0.2:8000",
                "accessID": "conn0002",
                "accessPW": "1234"

            },
            {
                "camID": "cam0003",
                "camURL": "rtsp://192.168.0.3:8000",
                "accessID": "conn0003",
                "accessPW": "1234"
            }
        ]
}
# ReplayURL
ReplayURL_in_data = {
    "camList":
        [{
            "camID": "cam0001",
            "startTime": 20220822163022123,
            "endTime": 20220822163025123,
            "streamProtocolType": " RTSP"
        },
            {
                "camID": "cam0002",
                "startTime": 20220822163022123,
                "endTime": 20220822163025123,
                "streamProtocolType": " RTSP"
            },
            {
                "camID": "cam0003",
                "startTime": 20220822163022123,
                "endTime": 20220822163025123,
                "streamProtocolType": " RTSP"
            }
        ]
}
ReplayURL_out_data = {
    "code": "200",
    "message": "성공",
    "camList":
        [{
            "camID": "cam0001",
            "accessID": "conn0001",
            "accessPW": "1234",
            "startTime": 20220822163022123,
            "endTime": 20220822163025123,
            "camURL": "rtsp://192.168.0.1:8000"
        },
            {
                "camID": "cam0002",
                "accessID": "conn0002",
                "accessPW": "1234",
                "startTime": 20220822163022123,
                "endTime": 20220822163025123,
                "camURL": "rtsp://192.168.0.2:8000"
            },
            {
                "camID": "cam0003",
                "accessID": "conn0003",
                "accessPW": "1234",
                "startTime": 20220822163022123,
                "endTime": 20220822163025123,
                "camURL": "rtsp://192.168.0.3:8000"
            }
        ]
}
# RealtimeVideoEventInfos
RealtimeVideoEventInfos_in_data = {
    "camList":
        [{
            "camID": "cam0001 "

        },
            {
                "camID": "cam0002"

            }],
    "transProtocol": {
        "transProtocolType": "WebHook",
        "transProtocolDesc": "desc"},
    "duration": 10,
    "eventFilter": "배회",
    "startTime": 20220822163022123
}

RealtimeVideoEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList":
        [ {
            "camID": "cam0001",
            "eventUUID": "event01",
            "eventName": "배회",
            "startTime": 20220822163022123,
            "endTime": 20220822163025123,
            "eventDesc": "sfdfEFASDDDLKJFjdkdlfjde"
        },
            {
                "camID": "cam0002",
                "eventUUID": "event02",
                "eventName": "배회",
                "startTime": 20220822163022123,
                "endTime": 20220822163025123,
                "eventDesc": "dddddeeeeeAAFEDFiikjf"
            }
        ]
}
# StoredVideoEventInfos
StoredVideoEventInfos_in_data = {
    "timePeriod": {
        "startTime": 20220822163022123,
        "endTime": 20220822163025123
    },
    "camList": [{"camID": "1234"}],

    "anayticsFilter": "객체탐지",
    "classFilter": ["차량", "사람"]
}

StoredVideoEventInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList":
        [{
            "camID": "cam0001",
            "analyticsTime": 20220822163022123,
            "anlayticsResultList": [{
                "anayticsID": "object001",
                "analyticsClass": "차량",
                "analytics Confidence": 0.8,
                "analytics BoundingBox":
                {
                    "left": 0.2,
                    "top": 0.1,
                    "right": 0.5,
                    "bottom": 0.6
                },
               "analyticsDesc": "12가3456"
            }]
        },
            {
                "camID": "cam0002",
                "analyticsTime": 20220822163022123,
                "anlayticsResultList": [{
                    "anayticsID": "object002",
                    "analyticsClass": "사람",
                    "analytics Confidence": 0.90,
                    "analytics BoundingBox":
                        {
                            "left": 0.3,
                            "top": 0.1,
                            "right": 0.5,
                            "bottom": 0.7
                        }
                }]
            }
        ]
}

StoredObjectAnalyticsInfos_in_data = {
    "timePeriod":
        {
            "startTime": 20220822163022123,
            "endTime": 20220822163025123
        },
    "camList":
        [
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
    "classFilter": ["차량", "사람"]
}


StoredObjectAnalyticsInfos_out_data = {
    "code": "200",
    "message": "성공",
    "camList": [{
        "camID": "cam0001",
        "analyticsTime": 20220822163022123,
        "anlayticsResultList":
            [
                {
                    "anayticsID": "object001",
                    "analyticsClass": "차량",
                    "analyticsConfidence": 0.80,
                    "analyticsBoundingBox": {
                        "left": 0.2,
                        "top": 0.1,
                        "right": 0.5,
                        "bottom": 0.6
                    },
                    "analyticsDesc": "13가 4567"
                }
              ]
    },
        {
            "camID": "cam0002",
            "analyticsTime": 20220822163022123,
            "anlayticsResultList":
                [
                  {
                      "anayticsID": "object002",
                      "analyticsClass": "사람",
                      "analyticsConfidence": 0.90,
                      "analyticsBoundingBox":
                          {
                              "left": 0.3,
                              "top": 0.1,
                              "right": 0.5,
                              "bottom": 0.7
                          }
                  }]
          }
    ]
}

Webhook_out_data = {
    "code": "200",
    "message": "성공"
}

videoInMessage = [Authentication_in_data,
                  Capabilities_in_data,
                  CameraProfiles_in_data,
                  StoredVideoInfos_in_data,
                  StreamURLs_in_data,
                  ReplayURL_in_data,
                  RealtimeVideoEventInfos_in_data,
                  StoredVideoEventInfos_in_data,
                  StoredObjectAnalyticsInfos_in_data]

videoOutMessage = [Authentication_out_data,
                   Capabilities_out_data,
                   CameraProfiles_out_data,
                   StoredVideoInfos_out_data,
                   StreamURLs_out_data,
                   ReplayURL_out_data,
                   RealtimeVideoEventInfos_out_data,
                   StoredVideoEventInfos_out_data,
                   StoredObjectAnalyticsInfos_out_data,
                   Webhook_out_data]

videoMessages = ["Authentication",
                 "Capabilities",
                 "CameraProfiles",
                 "StoredVideoInfos",
                 "StreamURLs",
                 "ReplayURL",
                 "RealtimeVideoEventInfos",
                 "StoredVideoEventInfos",
                 "StoredObjectAnalyticsInfos"]
