# Authentication
cmii7v8pr006g8z1tvo55a50u_Authentication_in_constraints = {
  "userID": {
    "id": "cmii7ym04006z8z1tr9r06hrb",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmii7ym0400718z1tyoxfj6ft",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmii7v8pr006g8z1tvo55a50u_Capabilities_in_constraints = {}

# CameraProfiles
cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_constraints = {}

# StreamURLs
cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_constraints = {
  "camList": {
    "id": "cmj17qhrx026m12s9s5t7vm2m",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmj17qhrz026o12s9jozkqym7",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "camList.streamProtocolType": {
    "id": "cmjb5nmy1070zdmvoi5u22oxx",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_constraints = {
  "camList": {
    "id": "cmiwrf69g0bu4844gps2e9ac1",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrf69i0bu6844g22ccsjtr",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "transProtocol": {
    "id": "cmiqtpoov00yeie8fv3h8pllf",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmiwrdzrw0bs4844gzg8kzcsq",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmiwre3fr0bt1844gwguauq4q",
    "valueType": "preset",
    "required": False
  },
  "duration": {
    "id": "cmiqtov1n00y8ie8frsppu8ev",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmiqtq1xn00ykie8fqjmg6au9",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "validValueField": "videoEvent",
    "validValues": [
      "Loitering",
      "Intrusion"
    ]
  },
  "classFilter": {
    "id": "cmiqtqegc00yqie8foi0sc1u9",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "validValueField": "videoObject",
    "validValues": [
      "Human"
    ]
  },
  "startTime": {
    "id": "cmiqtqxt400ywie8f4ir49gl1",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeVideoEventInfos WebHook OUT Constraints
cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints = {
  "code": {
    "id": "cmiwrhxdj0ci0844gogcg394u",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmj1820zz02m012s9cxe2wcfn",
    "valueType": "preset",
    "required": True
  }
}

# StoredVideoInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_in_constraints = {
  "timePeriod": {
    "id": "cmiwrl7dr000knkglwk60tug6",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmiwrltxz000vnkgl3m4u2f2s",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmiwrlxaj0013nkgl40nosy7z",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmiwrn6a9003nnkglvme2ccl1",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrn6ab003pnkgl7f78y9t6",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  }
}

# ReplayURL
cmii7v8pr006g8z1tvo55a50u_ReplayURL_in_constraints = {
  "camList": {
    "id": "cmiwrtok001dknkgluevidcla",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwrtok201dmnkgl6gzxhft5",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "camList.startTime": {
    "id": "cmiwrtok201donkglhwulnxos",
    "valueType": "preset",
    "required": True
  },
  "camList.endTime": {
    "id": "cmiwrtok301dqnkgl0k66p4py",
    "valueType": "preset",
    "required": True
  },
  "camList.streamProtocolType": {
    "id": "cmiwrtok301dsnkgl3t29d3op",
    "valueType": "preset",
    "required": True
  }
}

# StoredVideoEventInfos
cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_in_constraints = {
  "timePeriod": {
    "id": "cmiws35o105b3nkglj38lr0hx",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmiws3ab605bknkglsndw6cp5",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmiws41yv0005p002amxfzrhq",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmiws5her00alp002y1uhjddp",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiws5hes00anp002ng50q3fc",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "maxCount": {
    "id": "cmiws4rcl005up002n2yhi3pu",
    "valueType": "preset",
    "required": False
  },
  "eventFilter": {
    "id": "cmiws56xa008jp002vhqm6yfn",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "validValueField": "videoEvent",
    "validValues": [
      "Loitering",
      "Intrusion"
    ]
  },
  "classFilter": {
    "id": "cmiws5ggr00aip0022iuh6at3",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StoredVideoEventInfos",
    "validValueField": "videoObject",
    "validValues": [
      "Human"
    ]
  }
}

# StoredObjectAnalyticsInfos
cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_in_constraints = {
  "timePeriod": {
    "id": "cmiws9wg801l3p002ju1o2yfi",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.startTime": {
    "id": "cmiwsa3je01lnp002owjbqng1",
    "valueType": "preset",
    "required": True
  },
  "timePeriod.endTime": {
    "id": "cmiwsa57401lsp0021esg4kr1",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmiwsgzru02wyp0022uq3k278",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwsgzrw02x0p002fnxf1f08",
    "referenceFieldId": "cmizre5yl00gq117lhvg7sqp7",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "filterList": {
    "id": "cmiwsgzsc02xap002gifjhi5v",
    "valueType": "preset",
    "required": False
  },
  "filterList.classFilter": {
    "id": "cmjbl6af602ascfb33ejplfny",
    "valueType": "preset",
    "required": True
  },
  "filterList.attributeFilter": {
    "id": "cmjbl6afe02awcfb3ourzmfal",
    "valueType": "preset",
    "required": True
  }
}

# cmii7v8pr006g8z1tvo55a50u 검증 리스트
cmii7v8pr006g8z1tvo55a50u_inConstraints = [
    cmii7v8pr006g8z1tvo55a50u_Authentication_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_Capabilities_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_CameraProfiles_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StreamURLs_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoInfos_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_ReplayURL_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StoredVideoEventInfos_in_constraints,
    cmii7v8pr006g8z1tvo55a50u_StoredObjectAnalyticsInfos_in_constraints,
]

# cmii7v8pr006g8z1tvo55a50u WebHook Constraints 리스트
cmii7v8pr006g8z1tvo55a50u_webhook_outConstraints = [
    None,
    None,
    None,
    None,
    cmii7v8pr006g8z1tvo55a50u_RealtimeVideoEventInfos_webhook_out_constraints,
    None,
    None,
    None,
    None,
]

# Authentication
cmii7shen005i8z1tagevx4qh_Authentication_out_constraints = {
  "code": {
    "id": "cmii7ubcb00668z1tz2db96pa",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmii7ubcc00688z1t5ww43oyh",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmii7ubcc006a8z1tiysoivn3",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmii7ubcd006c8z1t5znhxevt",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmii7ubcd006e8z1tdsy8yzmg",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmii7shen005i8z1tagevx4qh_Capabilities_out_constraints = {
  "code": {
    "id": "cmiwkddjg000t844g314b5617",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwkdp0c0019844gm7dcd6x7",
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "id": "cmiwkenym003a844gtft12q3n",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmiwkenyq003c844g8076pb6b",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmiwkenyq003e844gceq8juz9",
    "valueType": "preset",
    "required": False
  }
}

# SensorDeviceProfiles
cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_out_constraints = {
  "code": {
    "id": "cmiwkjjd5003y844g1zy7wxlg",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwkjq080048844gqxgoo5kt",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList": {
    "id": "cmiwkpl7w01dd844gn18xqo4y",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmiwkpl7z01df844gtz32y9f5",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceType": {
    "id": "cmiwkpl8001dh844g75gn8pnr",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceName": {
    "id": "cmiwkpl8001dj844gft5bvtk3",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceLoc": {
    "id": "cmiwkpl8101dl844gkgmxvh73",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.sensorDeviceLoc.lon": {
    "id": "cmiwkpl9001dn844gcfhlhmuf",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceLoc.lat": {
    "id": "cmiwkpl9101dp844g7ipf3rd7",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceLoc.alt": {
    "id": "cmiwkpl9101dr844gmhas0h0i",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.sensorDeviceLoc.desc": {
    "id": "cmiwkpl9201dt844gpk2spohg",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeSensorData
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_out_constraints = {
  "code": {
    "id": "cmiwkumay01qo844gast85yvr",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwkuog901qt844gswj7kaas",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeSensorData WebHook IN Constraints
cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_in_constraints = {
  "sensorDeviceList": {
    "id": "cmiwkzuqt02xi844gygy0ft63",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmiwkzuqx02xk844gd9lr6k8p",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.measureTime": {
    "id": "cmiwkzuqx02xm844ghyx3o5j7",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceType": {
    "id": "cmiwkzuqy02xo844glk3msr3k",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceUnit": {
    "id": "cmiwkzuqy02xq844gh7csg9af",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceValue": {
    "id": "cmiwkzuqz02xs844gqt2i349j",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeSensorEventInfos
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_out_constraints = {
  "code": {
    "id": "cmiwl4h5d0376844g98gk5nbd",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwl4nzq037g844gtbfrqmvy",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeSensorEventInfos WebHook IN Constraints
cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_in_constraints = {
  "sensorDeviceList": {
    "id": "cmiwl7u0h03m9844g310pim4l",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmiwl7u0k03mb844gvcot0aev",
    "referenceFieldId": "cmiwl4bee036r844g6223h6b1",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeSensorEventInfos",
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceList.eventName": {
    "id": "cmiwl7u0k03md844g1au59txt",
    "referenceFieldId": "cmiwl41m8035g844gcx08uyjj",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeSensorEventInfos",
    "referenceField": "eventFilter"
  },
  "sensorDeviceList.eventTime": {
    "id": "cmiwl7u0k03mf844gucsqxj7z",
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal",
      "minFieldId": "cmiwl48s4036d844gftsr8d5e",
      "minEndpoint": "/RealtimeSensorEventInfos"
    },
    "requestRangeMinEndpoint": "/RealtimeSensorEventInfos"
  },
  "sensorDeviceList.eventDesc": {
    "id": "cmiwl7u0l03mh844g8mtp6h14",
    "valueType": "preset",
    "required": False
  }
}

# StoredSensorEventInfos
cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_out_constraints = {
  "code": {
    "id": "cmiwllxwf03uk844gapewtuco",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwlm39u03uu844g8drw39o8",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList": {
    "id": "cmiwlopxl04a1844gjrxp55cn",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmiwlopxp04a3844gu8p7c9ce",
    "referenceFieldId": "cmiwlli7703u9844graoc4jdn",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredSensorEventInfos",
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceList.eventName": {
    "id": "cmiwlopxq04a5844gu90f3obk",
    "referenceFieldId": "cmiwllfp703tr844g17037vsi",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredSensorEventInfos",
    "referenceField": "eventFilter"
  },
  "sensorDeviceList.eventTime": {
    "id": "cmiwlopxq04a7844g3dl2n5f1",
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "maxFieldId": "cmiwlk8e003q8844gd2f442h5",
      "minFieldId": "cmiwlk5bz03q0844g7oomi66i",
      "maxEndpoint": "/StoredSensorEventInfos",
      "minEndpoint": "/StoredSensorEventInfos"
    },
    "requestRangeMinEndpoint": "/StoredSensorEventInfos",
    "requestRangeMaxEndpoint": "/StoredSensorEventInfos"
  },
  "sensorDeviceList.eventDesc": {
    "id": "cmiwlopxq04a9844gg1gbzxy3",
    "valueType": "preset",
    "required": False
  }
}

# cmii7shen005i8z1tagevx4qh 검증 리스트
cmii7shen005i8z1tagevx4qh_outConstraints = [
    cmii7shen005i8z1tagevx4qh_Authentication_out_constraints,
    cmii7shen005i8z1tagevx4qh_Capabilities_out_constraints,
    cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_out_constraints,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_out_constraints,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_out_constraints,
    cmii7shen005i8z1tagevx4qh_StoredSensorEventInfos_out_constraints,
]

# cmii7shen005i8z1tagevx4qh WebHook Constraints 리스트
cmii7shen005i8z1tagevx4qh_webhook_inConstraints = [
    None,
    None,
    None,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_in_constraints,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_in_constraints,
    None,
]

# Authentication
cmii7pysb004k8z1tts0npxfm_Authentication_out_constraints = {
  "code": {
    "id": "cmii7rok300588z1tf4jcuvz6",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmii7rok3005a8z1twi4otb03",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmii7rok4005c8z1tgr5tzegk",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmii7rok4005e8z1tcbqpnnxe",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmii7rok5005g8z1tpldy9e57",
    "valueType": "preset",
    "required": False
  }
}

# Capabilities
cmii7pysb004k8z1tts0npxfm_Capabilities_out_constraints = {
  "code": {
    "id": "cmiiby4h9003ihl2hmn3ghbvl",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiiby4ha003khl2hx6u7i1ps",
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "id": "cmiiby4hr003shl2hohihzouw",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmiiby4hy003yhl2hh2puktr0",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmiiby4hz0040hl2hev5ljfq9",
    "valueType": "preset",
    "required": False
  }
}

# DoorProfiles
cmii7pysb004k8z1tts0npxfm_DoorProfiles_out_constraints = {
  "code": {
    "id": "cmisjisee09hw5vy7ajj18xo1",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisjj68n09i65vy7bhj2lnxi",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmisk9y5g0db15vy7zk3c777g",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmisk9y5l0db35vy74nn3utak",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorName": {
    "id": "cmisk9y5m0db55vy7m42cq0u0",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorRelayStatus": {
    "id": "cmisk9y5m0db75vy7nrgitysd",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorSensor": {
    "id": "cmisk9y5n0db95vy7cpkpvnlh",
    "valueType": "preset",
    "required": False
  },
  "doorList.doorLoc": {
    "id": "cmisk9y5n0dbb5vy78079wnwa",
    "valueType": "preset",
    "required": False
  },
  "doorList.doorLoc.lon": {
    "id": "cmisk9y600dbh5vy7585nx241",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.lat": {
    "id": "cmisk9y610dbj5vy757umjzmd",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.alt": {
    "id": "cmisk9y620dbl5vy7729uz0ee",
    "valueType": "preset",
    "required": False
  },
  "doorList.doorLoc.desc": {
    "id": "cmisk9y620dbn5vy707sb9da3",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList": {
    "id": "cmisk9y630dbr5vy7zjq09mnh",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.bioDeviceID": {
    "id": "cmisk9y6t0dc15vy7y7tv0ftk",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList.bioDeviceName": {
    "id": "cmisk9y6t0dc35vy7mkqcjckn",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList.bioDeviceAuthTypeList": {
    "id": "cmisk9y770dcf5vy7ucj3icmd",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList": {
    "id": "cmisk9y640dbt5vy73ab2q8f0",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList.otherDeviceID": {
    "id": "cmisk9y6u0dc75vy7s3znthpa",
    "valueType": "preset",
    "required": False
  },
  "doorList.otherDeviceList.otherDeviceName": {
    "id": "cmisk9y6v0dc95vy7fj06dgu6",
    "valueType": "preset",
    "required": False
  },
  "doorList.otherDeviceList.otherDeviceAuthTypeList": {
    "id": "cmisk9y780dch5vy7p4e0wkqi",
    "valueType": "preset",
    "required": True
  }
}

# AccessUserInfos
cmii7pysb004k8z1tts0npxfm_AccessUserInfos_out_constraints = {
  "code": {
    "id": "cmiwiplu600gpugxnl33vzh64",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwipydg00gzugxny5b0z1h8",
    "valueType": "preset",
    "required": True
  },
  "userList": {
    "id": "cmiwj0n6902m0ugxnxtjk2wge",
    "valueType": "preset",
    "required": True
  },
  "userList.userID": {
    "id": "cmiwj0n6b02m2ugxnw1xpebou",
    "valueType": "preset",
    "required": True
  },
  "userList.userName": {
    "id": "cmiwj0n6b02m4ugxnbuikeax0",
    "valueType": "preset",
    "required": True
  },
  "userList.userDesc": {
    "id": "cmiwj0n6b02m6ugxnsaqjrk5l",
    "valueType": "preset",
    "required": False
  },
  "userList.doorList": {
    "id": "cmiwj0n6f02mcugxnh76v915v",
    "valueType": "preset",
    "required": True
  },
  "userList.doorList.doorID": {
    "id": "cmiwj0n6i02miugxn26i0v7ni",
    "valueType": "preset",
    "required": True
  },
  "userList.doorList.timePeriod": {
    "id": "cmiwj0n6j02mkugxneilxzvra",
    "valueType": "preset",
    "required": True
  },
  "userList.doorList.timePeriod.startTime": {
    "id": "cmiwj0n6n02mqugxn455p44hm",
    "valueType": "preset",
    "required": True
  },
  "userList.doorList.timePeriod.endTime": {
    "id": "cmiwj0n6n02msugxnnqmanlio",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeVerifEventInfos
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_out_constraints = {
  "code": {
    "id": "cmiwjhjom03dpugxnralbx29s",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwjhpe303dzugxnf1hyc6o1",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeVerifEventInfos WebHook IN Constraints
cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_in_constraints = {
  "doorList": {
    "id": "cmiwjcsve030hugxnh4gwx5wk",
    "valueType": "preset",
    "required": True
  },
  "doorList.eventTime": {
    "id": "cmiwjcsvh030jugxnc1c8mp0i",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwjk7x203f4ugxntk7vq03e",
    "valueType": "preset",
    "required": True
  },
  "doorList.userID": {
    "id": "cmiwjkpyu03fuugxndy6x6dru",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioAuthTypeList": {
    "id": "cmiwjqsxj03uzugxn4snecdje",
    "valueType": "preset",
    "required": False
  },
  "doorList.otherAuthTypeList": {
    "id": "cmiwjqsxs03v1ugxnvmb1ilw1",
    "valueType": "preset",
    "required": False
  },
  "doorList.eventName": {
    "id": "cmiwjq08303s7ugxn6myjuphm",
    "valueType": "preset",
    "required": True
  },
  "doorList.eventDesc": {
    "id": "cmiwjqo0i03ujugxnk865norb",
    "valueType": "preset",
    "required": False
  }
}

# StoredVerifEventInfos
cmii7pysb004k8z1tts0npxfm_StoredVerifEventInfos_out_constraints = {
  "code": {
    "id": "cmiwjxur6041pugxn4ok6u2j8",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwjy12o041zugxnw6zc56a0",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmiwk4eb505txugxnu31pqzg8",
    "valueType": "preset",
    "required": True
  },
  "doorList.eventTime": {
    "id": "cmiwk4eba05tzugxnq0px7hne",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwk4eba05u1ugxns4zuooum",
    "valueType": "preset",
    "required": True
  },
  "doorList.userID": {
    "id": "cmiwk4ebb05u3ugxn0t4mnthm",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioAuthTypeList": {
    "id": "cmiwk4ebl05udugxnrifqngdj",
    "valueType": "preset",
    "required": False
  },
  "doorList.otherAuthTypeList": {
    "id": "cmiwk4ecb05ufugxnskw9wjj6",
    "valueType": "preset",
    "required": False
  },
  "doorList.eventName": {
    "id": "cmiwk4ebc05u9ugxnv9gbzft5",
    "referenceFieldId": "cmiwjvqme0415ugxnzwbgt3n5",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVerifEventInfos",
    "referenceField": "eventFilter"
  },
  "doorList.eventDesc": {
    "id": "cmiwk4ebd05ubugxnbjd55r70",
    "valueType": "preset",
    "required": False
  }
}

# cmii7pysb004k8z1tts0npxfm 검증 리스트
cmii7pysb004k8z1tts0npxfm_outConstraints = [
    cmii7pysb004k8z1tts0npxfm_Authentication_out_constraints,
    cmii7pysb004k8z1tts0npxfm_Capabilities_out_constraints,
    cmii7pysb004k8z1tts0npxfm_DoorProfiles_out_constraints,
    cmii7pysb004k8z1tts0npxfm_AccessUserInfos_out_constraints,
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_out_constraints,
    cmii7pysb004k8z1tts0npxfm_StoredVerifEventInfos_out_constraints,
]

# cmii7pysb004k8z1tts0npxfm WebHook Constraints 리스트
cmii7pysb004k8z1tts0npxfm_webhook_inConstraints = [
    None,
    None,
    None,
    None,
    cmii7pysb004k8z1tts0npxfm_RealtimeVerifEventInfos_webhook_in_constraints,
    None,
]

# Authentication
cmii7lxbn002s8z1t1i9uudf0_Authentication_out_constraints = {
  "code": {
    "id": "cmii7p9cw004a8z1td2ihlpuf",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmii7p9cw004c8z1tom7291lc",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmii7p9cx004e8z1t4lb6n36d",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmii7p9cx004g8z1t5qbkhnr8",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmii7p9cy004i8z1tlescd7jn",
    "valueType": "preset",
    "required": False
  }
}

# Capabilities
cmii7lxbn002s8z1t1i9uudf0_Capabilities_out_constraints = {
  "code": {
    "id": "cmio33qet008gie8f4s1le4k0",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmio340c2008mie8fm3cyrhpm",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport": {
    "id": "cmir08cxp004w4m39k1dxpjf0",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport.streamProtocolType": {
    "id": "cmir08cxs004y4m39iihabspq",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport.streamProtocolDesc": {
    "id": "cmir08cxt00504m398extfmmm",
    "valueType": "preset",
    "required": False
  },
  "transportSupport": {
    "id": "cmir08cy400524m399hipe38c",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmir08cy700544m394xn1tysc",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmir08cy700564m39nxhqfzfg",
    "valueType": "preset",
    "required": False
  }
}

# CameraProfiles
cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_out_constraints = {
  "code": {
    "id": "cmiqs7the00ksie8fj0vrxmcy",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiqs8b7e00kyie8facb9c4sh",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmj0vt5ax01j112s9ms36go7y",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmj0vt5b201j312s9p1hkxh8f",
    "valueType": "preset",
    "required": True
  },
  "camList.camName": {
    "id": "cmj0vt5b201j512s98eawfpo5",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc": {
    "id": "cmj0vt5b301j712s97pqcgtap",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.lon": {
    "id": "cmj0vt5b901jb12s9nbjf8c7b",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.lat": {
    "id": "cmj0vt5ba01jd12s9koqtltrj",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.alt": {
    "id": "cmj0vt5ba01jf12s9xxceg96k",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.desc": {
    "id": "cmj0vt5bb01jh12s9kygqspvr",
    "valueType": "preset",
    "required": True
  },
  "camList.camConfig": {
    "id": "cmj0vt5b301j912s904uu33gj",
    "valueType": "preset",
    "required": True
  },
  "camList.camConfig.camType": {
    "id": "cmj0vt5bb01jj12s9tyz1uxo0",
    "valueType": "preset",
    "required": True
  }
}

# StreamURLs
cmii7lxbn002s8z1t1i9uudf0_StreamURLs_out_constraints = {
  "code": {
    "id": "cmiqsg09500maie8f451y1im1",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiqsgaxz00mgie8fnbfjb40u",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmir1ncuk02ak4m39ya5v7q99",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmir1ncuo02am4m39q458o2fl",
    "referenceFieldId": "cmir13qc500ha4m39kvqh9lau",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StreamURLs",
    "referenceField": "camID"
  },
  "camList.accessID": {
    "id": "cmir1ncuo02ao4m39czhtxulh",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StreamURLs",
    "randomType": "specified-values",
    "specifiedValues": [
      "conn0001",
      "conn0002",
      "conn0003"
    ]
  },
  "camList.accessPW": {
    "id": "cmir1ncup02aq4m39pg83m7px",
    "valueType": "random",
    "required": False,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/StreamURLs",
    "randomType": "specified-values",
    "specifiedValues": [
      "1234"
    ]
  },
  "camList.camURL": {
    "id": "cmir1ncup02as4m39y4q1dws1",
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo": {
    "id": "cmir1ncuq02au4m39ual0s1y7",
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.resolution": {
    "id": "cmir1ncuw02aw4m390i0kuve1",
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.fps": {
    "id": "cmir1ncux02ay4m39i0p68gno",
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.videoCodec": {
    "id": "cmir1ncux02b04m39smp9iiqp",
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.audioCodec": {
    "id": "cmir1ncuy02b24m39m47zic3f",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_out_constraints = {
  "code": {
    "id": "cmiqsmn3c00o9ie8fq1o6xxnj",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiqsmzhf00ofie8fazf3jz05",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeVideoEventInfos WebHook IN Constraints
cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_in_constraints = {
  "camList": {
    "id": "cmir2mfip02wp4m394sanmwx7",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmir2mfiu02wr4m39ads6ssil",
    "referenceFieldId": "cmir29or902ex4m39s1uassws",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "referenceField": "camID"
  },
  "camList.eventUUID": {
    "id": "cmir2mfiv02wt4m39lbtbjixm",
    "valueType": "preset",
    "required": True
  },
  "camList.eventName": {
    "id": "cmir2mfiv02wv4m39egn4k8nf",
    "referenceFieldId": "cmiqsl9fo00npie8fesye4y25",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeVideoEventInfos",
    "referenceField": "eventFilter"
  },
  "camList.startTime": {
    "id": "cmir2mfiw02wx4m39fvmgkouv",
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "operator": "greater-equal",
      "minFieldId": "cmiqsm0v000o1ie8fxbg8mgjj",
      "minEndpoint": "/RealtimeVideoEventInfos",
      "minField": "startTime"
    }
  },
  "camList.endTime": {
    "id": "cmir2mfiw02wz4m39s3y8pmrl",
    "valueType": "request-range",
    "required": False,
    "requestRange": {
      "operator": "greater-equal",
      "minFieldId": "cmiqsm0v000o1ie8fxbg8mgjj",
      "minEndpoint": "/RealtimeVideoEventInfos",
      "minField": "startTime"
    }
  },
  "camList.eventDesc": {
    "id": "cmir2mfix02x14m39ynn2xwwe",
    "valueType": "preset",
    "required": False
  }
}

# StoredVideoInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_out_constraints = {
  "code": {
    "id": "cmiqst6rs00pxie8fx00h13gx",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiqstktk00q3ie8ffuhyz1up",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmir2znh7036o4m391v38j6vc",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmir2znh9036q4m390xb4tu0b",
    "referenceFieldId": "cmir2ux9n02ys4m39wn9sa5sh",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoInfos",
    "referenceField": "camID"
  },
  "camList.timeList": {
    "id": "cmir2znhc036u4m392puqvdor",
    "valueType": "preset",
    "required": True
  },
  "camList.timeList.startTime": {
    "id": "cmjb1fcbg0461dmvo7cfhrdlv",
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "maxFieldId": "cmir2u35f02xu4m39386364rm",
      "minFieldId": "cmir2tvo102xo4m399ambl3jc",
      "maxEndpoint": "/StoredVideoInfos",
      "minEndpoint": "/StoredVideoInfos"
    },
    "requestRangeMinEndpoint": "/StoredVideoInfos",
    "requestRangeMaxEndpoint": "/StoredVideoInfos"
  },
  "camList.timeList.endTime": {
    "id": "cmjb1ft0z0491dmvox9hy2sjd",
    "valueType": "request-range",
    "required": False,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "maxFieldId": "cmir2u35f02xu4m39386364rm",
      "minFieldId": "cmir2tvo102xo4m399ambl3jc",
      "maxEndpoint": "/StoredVideoInfos",
      "minEndpoint": "/StoredVideoInfos"
    },
    "requestRangeMinEndpoint": "/StoredVideoInfos",
    "requestRangeMaxEndpoint": "/StoredVideoInfos"
  }
}

# ReplayURL
cmii7lxbn002s8z1t1i9uudf0_ReplayURL_out_constraints = {
  "code": {
    "id": "cmiqsxbw000qzie8fqg6ai3cf",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiqsxsv000r5ie8fb8dk0hz4",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmir3npez057n4m39iap76r75",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmir3npf2057p4m39bp2ukn6j",
    "referenceFieldId": "cmir35uma03my4m39s5d6jggk",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/ReplayURL",
    "referenceField": "camID"
  },
  "camList.accessID": {
    "id": "cmir3npf3057r4m398ypagqxu",
    "valueType": "preset",
    "required": False
  },
  "camList.accessPW": {
    "id": "cmir3npf4057t4m39chpyyb44",
    "valueType": "preset",
    "required": False
  },
  "camList.camURL": {
    "id": "cmir3npf4057v4m39a32yuml9",
    "valueType": "preset",
    "required": True
  },
  "camList.videoInfo": {
    "id": "cmir3npf5057x4m39xnl7sph4",
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.resolution": {
    "id": "cmir3npfc057z4m39gv6h8ci4",
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.fps": {
    "id": "cmir3npfd05814m39t5syait5",
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.videoCodec": {
    "id": "cmir3npfd05834m39t9m4rdmu",
    "valueType": "preset",
    "required": False
  },
  "camList.videoInfo.audioCodec": {
    "id": "cmir3npfe05854m398cp4ur96",
    "valueType": "preset",
    "required": False
  }
}

# StoredVideoEventInfos
cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_out_constraints = {
  "code": {
    "id": "cmiqt2r8m00soie8fz1k7xxiq",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiqt30s200suie8f9y0r5v8i",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmir5bj7305il4m39i90z1cs4",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmir5bj7605in4m39u6jdfihu",
    "referenceFieldId": "cmir57lfa05aa4m3921t17dse",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceField": "camID"
  },
  "camList.eventUUID": {
    "id": "cmir5bj7605ip4m39eu3lwye9",
    "valueType": "preset",
    "required": True
  },
  "camList.eventName": {
    "id": "cmir5bj7705ir4m394w640k6j",
    "referenceFieldId": "cmiqt1xb600saie8far6hiccy",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredVideoEventInfos",
    "referenceField": "eventFilter"
  },
  "camList.startTime": {
    "id": "cmis57ht9001st4pq2htah7em",
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxFieldId": "cmir578rm059x4m39obwdkixj",
      "minFieldId": "cmir56xvt059r4m39ng9fpixs",
      "maxEndpoint": "/StoredVideoEventInfos",
      "minEndpoint": "/StoredVideoEventInfos",
      "minField": "startTime",
      "maxField": "endTime"
    }
  },
  "camList.endTime": {
    "id": "cmis58snx002at4pquxzko80q",
    "valueType": "request-range",
    "required": False,
    "requestRange": {
      "maxFieldId": "cmir578rm059x4m39obwdkixj",
      "minFieldId": "cmir56xvt059r4m39ng9fpixs",
      "maxEndpoint": "/StoredVideoEventInfos",
      "minEndpoint": "/StoredVideoEventInfos",
      "minField": "startTime",
      "maxField": "endTime"
    }
  },
  "camList.eventDesc": {
    "id": "cmis5a2tl002st4pq3o7gwdug",
    "valueType": "preset",
    "required": False
  }
}

# StoredObjectAnalyticsInfos
cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_out_constraints = {
  "code": {
    "id": "cmiqt66q400u1ie8f5tuowt4m",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiqt6i6500u7ie8f2897rtwv",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmis5m2y500edt4pq4v0e8411",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmis5m2y800eft4pqy70zoak1",
    "referenceFieldId": "cmis5gwfi00b8t4pqmp438c9j",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredObjectAnalyticsInfos",
    "referenceField": "camID"
  },
  "camList.analyticsTime": {
    "id": "cmis5m2y800eht4pqhzi2mq5d",
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxFieldId": "cmis5e5kx003lt4pqtfogwd0g",
      "minFieldId": "cmis5dxva003ft4pqhigxna18",
      "maxEndpoint": "/StoredObjectAnalyticsInfos",
      "minEndpoint": "/StoredObjectAnalyticsInfos",
      "minField": "startTime",
      "maxField": "endTime"
    }
  },
  "camList.anlayticsResultList": {
    "id": "cmiseswra03bs5vy7c7h99m2t",
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.anayticsID": {
    "id": "cmiseswre03bu5vy7f9bv6570",
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsClass": {
    "id": "cmjblmzce02oecfb316he7e51",
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsAttribute": {
    "id": "cmiseswrq03c65vy7q1gxhmjb",
    "valueType": "preset",
    "required": False
  },
  "camList.anlayticsResultList.analyticsConfidence": {
    "id": "cmiseswrg03c05vy7b19khldt",
    "valueType": "preset",
    "required": False
  },
  "camList.anlayticsResultList.analyticsBoundingBox": {
    "id": "cmiseswrg03c25vy7x292ueus",
    "valueType": "preset",
    "required": False
  },
  "camList.anlayticsResultList.analyticsBoundingBox.left": {
    "id": "cmiseswrq03c85vy7ex3827kd",
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsBoundingBox.top": {
    "id": "cmiseswrr03ca5vy7wihjatly",
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsBoundingBox.right": {
    "id": "cmiseswrr03cc5vy71g9v8uh1",
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsBoundingBox.bottom": {
    "id": "cmiseswrs03ce5vy7aktc2lgd",
    "valueType": "preset",
    "required": True
  },
  "camList.anlayticsResultList.analyticsDesc": {
    "id": "cmiseswrh03c45vy7y3iyzsd7",
    "valueType": "preset",
    "required": False
  }
}

# cmii7lxbn002s8z1t1i9uudf0 검증 리스트
cmii7lxbn002s8z1t1i9uudf0_outConstraints = [
    cmii7lxbn002s8z1t1i9uudf0_Authentication_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_Capabilities_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_CameraProfiles_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_StreamURLs_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoInfos_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_ReplayURL_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_StoredVideoEventInfos_out_constraints,
    cmii7lxbn002s8z1t1i9uudf0_StoredObjectAnalyticsInfos_out_constraints,
]

# cmii7lxbn002s8z1t1i9uudf0 WebHook Constraints 리스트
cmii7lxbn002s8z1t1i9uudf0_webhook_inConstraints = [
    None,
    None,
    None,
    None,
    cmii7lxbn002s8z1t1i9uudf0_RealtimeVideoEventInfos_webhook_in_constraints,
    None,
    None,
    None,
    None,
]

