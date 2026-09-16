# Authentication
cmtwtwdiz02o1245txoqxczwz_Authentication_in_constraints = {
  "userID": {
    "id": "cmtwtwdka02ol245t3h7tqt4s",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  },
  "userPW": {
    "id": "cmtwtwdkd02on245ts0cogcjd",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  }
}

# Capabilities
cmtwtwdiz02o1245txoqxczwz_Capabilities_in_constraints = {}

# DoorProfiles
cmtwtwdiz02o1245txoqxczwz_DoorProfiles_in_constraints = {}

# RealtimeDoorStatus
cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus_in_constraints = {
  "doorList": {
    "id": "cmtwtwdso02sd245tmqcswqtq",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmtwtwdsr02sf245thyfh74ss",
    "referenceFieldId": "cmtwtwdnv02qh245tltvb8v10",
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorList.doorID",
    "isArrayFieldPath": True
  },
  "duration": {
    "id": "cmtwtwdr202s1245tzqm9oazc",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmtwtwdsc02s3245ta7li345i",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmtwtwdsf02s5245tg2n5g0q9",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmtwtwdsh02s7245tx3afmo1j",
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "id": "cmtwtwdsk02s9245t0e5w9vpl",
    "valueType": "preset",
    "required": False
  }
}

# DoorControl
cmtwtwdiz02o1245txoqxczwz_DoorControl_in_constraints = {
  "doorID": {
    "id": "cmtwtwdta02sv245tkqgfw8ul",
    "referenceFieldId": "cmtwtwdsr02sf245thyfh74ss",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorList.doorID",
    "isArrayFieldPath": True
  },
  "commandType": {
    "id": "cmu149lh7007eu9w60qb9rx8e",
    "referenceFieldId": "cmtwtwdqt02rt245t1mzzhqn6",
    "valueType": "random",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorList.doorSensor",
    "isArrayFieldPath": True,
    "randomType": "exclude-reference-valid-values",
    "validValueField": "acControl",
    "validValues": [
      "Lock",
      "Unlock"
    ]
  }
}

# RealtimeDoorStatus2
cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus2_in_constraints = {
  "doorList": {
    "id": "cmu1a8cge011vu9w6hxfvbfe7",
    "valueType": "preset",
    "required": True
  },
  "duration": {
    "id": "cmtwtwdwh02u9245td48flgbc",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmtwtwdy302uh245te216pgcd",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmtwtwdy602uj245tfeetziha",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmtwtwdy802ul245t4aj26op1",
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "id": "cmtwtwdyb02un245t2l209u2x",
    "valueType": "preset",
    "required": False
  }
}

# cmtwtwdiz02o1245txoqxczwz 검증 리스트
cmtwtwdiz02o1245txoqxczwz_inConstraints = [
    cmtwtwdiz02o1245txoqxczwz_Authentication_in_constraints,
    cmtwtwdiz02o1245txoqxczwz_Capabilities_in_constraints,
    cmtwtwdiz02o1245txoqxczwz_DoorProfiles_in_constraints,
    cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus_in_constraints,
    cmtwtwdiz02o1245txoqxczwz_DoorControl_in_constraints,
    cmtwtwdiz02o1245txoqxczwz_RealtimeDoorStatus2_in_constraints,
]

# Authentication
cmtwtvuyb02i1245t2su90084_Authentication_in_constraints = {
  "userID": {
    "id": "cmtwtvuz202il245t6kp2q6ws",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  },
  "userPW": {
    "id": "cmtwtvuz502in245tvbkf9e9n",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  }
}

# Capabilities
cmtwtvuyb02i1245t2su90084_Capabilities_in_constraints = {}

# DoorProfiles
cmtwtvuyb02i1245t2su90084_DoorProfiles_in_constraints = {}

# AccessUserInfos
cmtwtvuyb02i1245t2su90084_AccessUserInfos_in_constraints = {}

# StoredVerifEventInfos
cmtwtvuyb02i1245t2su90084_StoredVerifEventInfos_in_constraints = {
  "timePeriod": {
    "id": "cmtwtvv7x02lt245td6d2jvne",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmtwtvv8002lv245trgn7wghx",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmtwtvv8202lx245tztz51tsn",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmtwtvv8702m1245t59uvhsm1",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmtwtvv8902m3245tkmmc08lc",
    "referenceFieldId": "cmtwtvv1k02jn245t1o1bpl87",
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorList.doorID",
    "isArrayFieldPath": True
  },
  "maxCount": {
    "id": "cmtwtvv7v02lr245tji8p5ih9",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmtwtvv8c02m5245tlyvn91wx",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredVerifEventInfos",
    "validValueField": "acEvent",
    "validValues": [
      "AuthSuccess",
      "AuthFail",
      "인증성공",
      "인증실패",
      "AccessDenied",
      "PassbackDetection",
      "InactiveUser",
      "ExpiredUser",
      "BlockedUser",
      "InvalidUser",
      "DuplicatedAuth",
      "FakeDetection",
      "AttemptsExceeded",
      "MaximumEntrance",
      "DuressAuth",
      "ForcedOpen",
      "ConnectionError",
      "TimeOut",
      "CaptureFail",
      "TamperOn",
      "TamperOff",
      "UserDeleteSuccess",
      "UserDeleteFail",
      "UserDeleteAllSuccess",
      "UserDeleteAllFail",
      "출입거부",
      "패스백감지",
      "비활성사용자",
      "만료사용자",
      "차단사용자",
      "미등록사용자",
      "중복인증",
      "위조감지",
      "인증시도횟수초과",
      "입실초과",
      "협박인증",
      "출입문 강제개방",
      "통신장애발생",
      "시간초과",
      "캡쳐실패",
      "탬퍼발생",
      "탬퍼해제",
      "사용자삭제성공",
      "사용자삭제실패",
      "사용자전체삭제성공",
      "사용자전체삭제실패"
    ]
  }
}

# cmtwtvuyb02i1245t2su90084 검증 리스트
cmtwtvuyb02i1245t2su90084_inConstraints = [
    cmtwtvuyb02i1245t2su90084_Authentication_in_constraints,
    cmtwtvuyb02i1245t2su90084_Capabilities_in_constraints,
    cmtwtvuyb02i1245t2su90084_DoorProfiles_in_constraints,
    cmtwtvuyb02i1245t2su90084_AccessUserInfos_in_constraints,
    cmtwtvuyb02i1245t2su90084_StoredVerifEventInfos_in_constraints,
]

# Authentication
cmtwtvjfm02br245tbzi9gej7_Authentication_in_constraints = {
  "userID": {
    "id": "cmtwtvjgu02cb245tycz94a4z",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  },
  "userPW": {
    "id": "cmtwtvjgw02cd245tiodj3sxn",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  }
}

# Capabilities
cmtwtvjfm02br245tbzi9gej7_Capabilities_in_constraints = {}

# DoorProfiles
cmtwtvjfm02br245tbzi9gej7_DoorProfiles_in_constraints = {}

# AccessUserInfos
cmtwtvjfm02br245tbzi9gej7_AccessUserInfos_in_constraints = {}

# RealtimeVerifEventInfos
cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_in_constraints = {
  "doorList": {
    "id": "cmtwtvjnf02fp245ti19zcqlm",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmtwtvjni02fr245tg4lng44z",
    "referenceFieldId": "cmtw8wcwu00pl126mir9im1m4",
    "valueType": "preset",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorList.doorID",
    "isArrayFieldPath": True
  },
  "duration": {
    "id": "cmtwtvjnk02ft245t8fquk728",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmtwtvjn502fh245t70d0yp14",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmtwtvjn802fj245t682aa5ml",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmtwtvjna02fl245t57oefl1n",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmtwtvjnn02fv245t5d4al29w",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "validValueField": "acEvent",
    "validValues": [
      "AuthSuccess",
      "AuthFail",
      "인증성공",
      "인증실패",
      "AccessDenied",
      "PassbackDetection",
      "InactiveUser",
      "ExpiredUser",
      "BlockedUser",
      "InvalidUser",
      "DuplicatedAuth",
      "FakeDetection",
      "AttemptsExceeded",
      "MaximumEntrance",
      "DuressAuth",
      "ForcedOpen",
      "ConnectionError",
      "TimeOut",
      "CaptureFail",
      "TamperOn",
      "TamperOff",
      "UserDeleteSuccess",
      "UserDeleteFail",
      "UserDeleteAllSuccess",
      "UserDeleteAllFail",
      "출입거부",
      "패스백감지",
      "비활성사용자",
      "만료사용자",
      "차단사용자",
      "미등록사용자",
      "중복인증",
      "위조감지",
      "인증시도횟수초과",
      "입실초과",
      "협박인증",
      "출입문 강제개방",
      "통신장애발생",
      "시간초과",
      "캡쳐실패",
      "탬퍼발생",
      "탬퍼해제",
      "사용자삭제성공",
      "사용자삭제실패",
      "사용자전체삭제성공",
      "사용자전체삭제실패"
    ]
  },
  "startTime": {
    "id": "cmtwtvjnq02fx245thcfe48qa",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeVerifEventInfos WebHook OUT Constraints
cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_webhook_out_constraints = {
  "code": {
    "id": "cmtwtvjpd02g7245t5ddj4ih2",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmtwtvjpg02g9245t0x4jr9d8",
    "valueType": "preset",
    "required": True
  }
}

# cmtwtvjfm02br245tbzi9gej7 검증 리스트
cmtwtvjfm02br245tbzi9gej7_inConstraints = [
    cmtwtvjfm02br245tbzi9gej7_Authentication_in_constraints,
    cmtwtvjfm02br245tbzi9gej7_Capabilities_in_constraints,
    cmtwtvjfm02br245tbzi9gej7_DoorProfiles_in_constraints,
    cmtwtvjfm02br245tbzi9gej7_AccessUserInfos_in_constraints,
    cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_in_constraints,
]

# cmtwtvjfm02br245tbzi9gej7 WebHook Constraints 리스트
cmtwtvjfm02br245tbzi9gej7_webhook_outConstraints = [
    None,
    None,
    None,
    None,
    cmtwtvjfm02br245tbzi9gej7_RealtimeVerifEventInfos_webhook_out_constraints,
]

# Authentication
cmtwil1oo00ztt4ht7y9se1ur_Authentication_in_constraints = {
  "userID": {
    "id": "cmtwil1p40101t4htpubxkhpu",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  },
  "userPW": {
    "id": "cmtwil1pe0103t4ht6wpqahb4",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  }
}

# Capabilities
cmtwil1oo00ztt4ht7y9se1ur_Capabilities_in_constraints = {}

# DoorProfiles
cmtwil1oo00ztt4ht7y9se1ur_DoorProfiles_in_constraints = {}

# RealtimeDoorStatus
cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus_in_constraints = {
  "doorList": {
    "id": "cmtwil1z60135t4hte3yi8ffv",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmtwil1z80137t4ht6cedc5cg",
    "referenceFieldId": "cmtwil1r4011ft4ht6z1yxn1o",
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorList.doorID",
    "isArrayFieldPath": True
  },
  "duration": {
    "id": "cmtwil1ys012tt4ht92brrsqn",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmtwil1yu012vt4htz1qkkmvi",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmtwil1yx012xt4ht3m74lajg",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmtwil1yz012zt4htteqkduqi",
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "id": "cmtwil1z10131t4ht1lv6m5qn",
    "valueType": "preset",
    "required": False
  }
}

# DoorControl
cmtwil1oo00ztt4ht7y9se1ur_DoorControl_in_constraints = {
  "doorID": {
    "id": "cmtwil21g0143t4htza9lya4q",
    "referenceFieldId": "cmtwil1z80137t4ht6cedc5cg",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorList.doorID",
    "isArrayFieldPath": True
  },
  "commandType": {
    "id": "cmtwil21j0145t4htgsi3ngs4",
    "referenceFieldId": "cmtwmg25500gyb14tp5l75no5",
    "valueType": "random",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorList.doorSensor",
    "isArrayFieldPath": True,
    "randomType": "exclude-reference-valid-values",
    "validValueField": "acControl",
    "validValues": [
      "Lock",
      "Unlock"
    ]
  }
}

# RealtimeDoorStatus2
cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus2_in_constraints = {
  "doorList": {
    "id": "cmtwil24h015ht4ht444iadhm",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmtwil24j015jt4htlug66sag",
    "referenceFieldId": "cmtwil21g0143t4htza9lya4q",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/DoorControl",
    "referenceField": "doorID"
  },
  "duration": {
    "id": "cmtwil24c015dt4htl9ljzt4w",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmtwil24m015lt4htmbnqc5di",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmtwil24o015nt4ht8faibokz",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmtwil24r015pt4hts5kv74uu",
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "id": "cmtwil24t015rt4htu5p6p1l6",
    "valueType": "preset",
    "required": False
  }
}

# cmtwil1oo00ztt4ht7y9se1ur 검증 리스트
cmtwil1oo00ztt4ht7y9se1ur_inConstraints = [
    cmtwil1oo00ztt4ht7y9se1ur_Authentication_in_constraints,
    cmtwil1oo00ztt4ht7y9se1ur_Capabilities_in_constraints,
    cmtwil1oo00ztt4ht7y9se1ur_DoorProfiles_in_constraints,
    cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus_in_constraints,
    cmtwil1oo00ztt4ht7y9se1ur_DoorControl_in_constraints,
    cmtwil1oo00ztt4ht7y9se1ur_RealtimeDoorStatus2_in_constraints,
]

# Authentication
cmtwfeiw4003dt4htizadqzzr_Authentication_in_constraints = {
  "userID": {
    "id": "cmtwfeiwl003lt4htjhfhessq",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  },
  "userPW": {
    "id": "cmtwfeiwv003nt4htwuyoz1jc",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  }
}

# Capabilities
cmtwfeiw4003dt4htizadqzzr_Capabilities_in_constraints = {}

# DoorProfiles
cmtwfeiw4003dt4htizadqzzr_DoorProfiles_in_constraints = {}

# AccessUserInfos
cmtwfeiw4003dt4htizadqzzr_AccessUserInfos_in_constraints = {}

# StoredVerifEventInfos
cmtwfeiw4003dt4htizadqzzr_StoredVerifEventInfos_in_constraints = {
  "timePeriod": {
    "id": "cmtwfejak0083t4htoqi63oki",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmtwfejan0085t4htwdzww0wd",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmtwfejaq0087t4htaq13s6mq",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmtwfejc6008bt4htcsioxinv",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmtwfejc8008dt4htm61szvt0",
    "referenceFieldId": "cmtwfej12004xt4htvhyhl34d",
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorList.doorID",
    "isArrayFieldPath": True
  },
  "maxCount": {
    "id": "cmtwfejaf007zt4htptyn3ez9",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmtwfejai0081t4htfx2wjpru",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredVerifEventInfos",
    "validValueField": "acEvent",
    "validValues": [
      "AuthSuccess",
      "AuthFail",
      "인증성공",
      "인증실패",
      "AccessDenied",
      "PassbackDetection",
      "InactiveUser",
      "ExpiredUser",
      "BlockedUser",
      "InvalidUser",
      "DuplicatedAuth",
      "FakeDetection",
      "AttemptsExceeded",
      "MaximumEntrance",
      "DuressAuth",
      "ForcedOpen",
      "ConnectionError",
      "TimeOut",
      "CaptureFail",
      "TamperOn",
      "TamperOff",
      "UserDeleteSuccess",
      "UserDeleteFail",
      "UserDeleteAllSuccess",
      "UserDeleteAllFail",
      "출입거부",
      "패스백감지",
      "비활성사용자",
      "만료사용자",
      "차단사용자",
      "미등록사용자",
      "중복인증",
      "위조감지",
      "인증시도횟수초과",
      "입실초과",
      "협박인증",
      "출입문 강제개방",
      "통신장애발생",
      "시간초과",
      "캡쳐실패",
      "탬퍼발생",
      "탬퍼해제",
      "사용자삭제성공",
      "사용자삭제실패",
      "사용자전체삭제성공",
      "사용자전체삭제실패"
    ]
  }
}

# cmtwfeiw4003dt4htizadqzzr 검증 리스트
cmtwfeiw4003dt4htizadqzzr_inConstraints = [
    cmtwfeiw4003dt4htizadqzzr_Authentication_in_constraints,
    cmtwfeiw4003dt4htizadqzzr_Capabilities_in_constraints,
    cmtwfeiw4003dt4htizadqzzr_DoorProfiles_in_constraints,
    cmtwfeiw4003dt4htizadqzzr_AccessUserInfos_in_constraints,
    cmtwfeiw4003dt4htizadqzzr_StoredVerifEventInfos_in_constraints,
]

# Authentication
cmtw8wcts00o1126muckytfg2_Authentication_in_constraints = {
  "userID": {
    "id": "cmtw8wcu600o9126m0uydmx1w",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  },
  "userPW": {
    "id": "cmtw8wcuc00ob126m55ynvp2i",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {
        "max": 20,
        "min": 1
      }
    }
  }
}

# Capabilities
cmtw8wcts00o1126muckytfg2_Capabilities_in_constraints = {}

# DoorProfiles
cmtw8wcts00o1126muckytfg2_DoorProfiles_in_constraints = {}

# AccessUserInfos
cmtw8wcts00o1126muckytfg2_AccessUserInfos_in_constraints = {}

# RealtimeVerifEventInfos
cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_in_constraints = {
  "doorList": {
    "id": "cmtw8wd8600st126mskr7va0p",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmtw8wd9g00sv126mczcjpm2o",
    "referenceFieldId": "cmtw8wcwu00pl126mir9im1m4",
    "valueType": "random-response",
    "required": True,
    "referenceEndpoint": "/DoorProfiles",
    "referenceField": "doorList.doorID",
    "isArrayFieldPath": True
  },
  "duration": {
    "id": "cmtw8wd9j00sx126mi3jxetpt",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmtw8wd9l00sz126mivcdbaim",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmtw8wd9o00t1126mfb5whvcw",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmtw8wd9q00t3126m9jvrc3kz",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmtw8wd7y00sn126mkvsn6i94",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeVerifEventInfos",
    "validValueField": "acEvent",
    "validValues": [
      "AuthSuccess",
      "AuthFail",
      "인증성공",
      "인증실패",
      "AccessDenied",
      "PassbackDetection",
      "InactiveUser",
      "ExpiredUser",
      "BlockedUser",
      "InvalidUser",
      "DuplicatedAuth",
      "FakeDetection",
      "AttemptsExceeded",
      "MaximumEntrance",
      "DuressAuth",
      "ForcedOpen",
      "ConnectionError",
      "TimeOut",
      "CaptureFail",
      "TamperOn",
      "TamperOff",
      "UserDeleteSuccess",
      "UserDeleteFail",
      "UserDeleteAllSuccess",
      "UserDeleteAllFail",
      "출입거부",
      "패스백감지",
      "비활성사용자",
      "만료사용자",
      "차단사용자",
      "미등록사용자",
      "중복인증",
      "위조감지",
      "인증시도횟수초과",
      "입실초과",
      "협박인증",
      "출입문 강제개방",
      "통신장애발생",
      "시간초과",
      "캡쳐실패",
      "탬퍼발생",
      "탬퍼해제",
      "사용자삭제성공",
      "사용자삭제실패",
      "사용자전체삭제성공",
      "사용자전체삭제실패"
    ]
  },
  "startTime": {
    "id": "cmtw8wd8100sp126mxt2kkk06",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeVerifEventInfos WebHook OUT Constraints
cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_webhook_out_constraints = {
  "code": {
    "id": "cmtw8wd6w00rr126mjshbvdjl",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmtw8wd7000rt126myoqomtbw",
    "valueType": "preset",
    "required": True
  }
}

# cmtw8wcts00o1126muckytfg2 검증 리스트
cmtw8wcts00o1126muckytfg2_inConstraints = [
    cmtw8wcts00o1126muckytfg2_Authentication_in_constraints,
    cmtw8wcts00o1126muckytfg2_Capabilities_in_constraints,
    cmtw8wcts00o1126muckytfg2_DoorProfiles_in_constraints,
    cmtw8wcts00o1126muckytfg2_AccessUserInfos_in_constraints,
    cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_in_constraints,
]

# cmtw8wcts00o1126muckytfg2 WebHook Constraints 리스트
cmtw8wcts00o1126muckytfg2_webhook_outConstraints = [
    None,
    None,
    None,
    None,
    cmtw8wcts00o1126muckytfg2_RealtimeVerifEventInfos_webhook_out_constraints,
]

