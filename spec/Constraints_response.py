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

# Authentication
cmiqr1jha00i6ie8fb1scb3go_Authentication_in_constraints = {
  "userID": {
    "id": "cmisgv95008oh5vy7mjspm3wh",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmisgvcex08oq5vy7d84t9tts",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmiqr1jha00i6ie8fb1scb3go_Capabilities_in_constraints = {}

# DoorProfiles
cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_in_constraints = {}

# RealtimeDoorStatus
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_in_constraints = {
  "doorList": {
    "id": "cmixuqxe80h0lp002efemdw6m",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmixuqxeb0h0np002mwczcz4g",
    "referenceFieldId": "cmixusnx90hatp002m3rnln60",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorID"
  },
  "duration": {
    "id": "cmixupira0gudp0025a627ml4",
    "valueType": "preset",
    "required": False
  },
  "transProtocol": {
    "id": "cmixupvnn0gw1p002t4oynlxp",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmixuq3qa0gxmp0023qvxro6p",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmixuq6xh0gxzp002nbmk4kcc",
    "valueType": "preset",
    "required": False
  },
  "startTime": {
    "id": "cmixuqodk0h00p002xkjhnyca",
    "valueType": "preset",
    "required": False
  }
}

# RealtimeDoorStatus WebHook OUT Constraints
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_out_constraints = {
  "code": {
    "id": "cmixussd70hbkp002351v2o5r",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmixusvcf0hbqp002tdeowl0t",
    "valueType": "preset",
    "required": True
  }
}

# DoorControl
cmiqr1jha00i6ie8fb1scb3go_DoorControl_in_constraints = {
  "doorID": {
    "id": "cmixuu5os0hc9p002st12cpzi",
    "valueType": "preset",
    "required": True
  },
  "commandType": {
    "id": "cmj83qob2000isnx0rwhvblif",
    "referenceFieldId": "cmixusnxa0hazp002h9lu2gt7",
    "valueType": "random",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorSensor",
    "randomType": "exclude-reference-valid-values",
    "validValueField": "acControl",
    "validValues": [
      "Lock",
      "Unlock"
    ]
  }
}

# RealtimeDoorStatus2
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_in_constraints = {
  "doorList": {
    "id": "cmize9v8a00a096qh8bxm7fe2",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmize9v8b00a296qh1vooije0",
    "referenceFieldId": "cmixuu5os0hc9p002st12cpzi",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/DoorControl",
    "referenceField": "doorID"
  },
  "duration": {
    "id": "cmize7lki002a96qhe5181nqj",
    "valueType": "preset",
    "required": True
  },
  "transProtocol": {
    "id": "cmize811g003m96qhzuj5k87j",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolType": {
    "id": "cmize8m4g007l96qhwaouhm9t",
    "valueType": "preset",
    "required": True
  },
  "transProtocol.transProtocolDesc": {
    "id": "cmize8y8y008q96qhgmcgwvmc",
    "valueType": "preset",
    "required": True
  },
  "startTime": {
    "id": "cmize9f5s009v96qhrbr6kzd5",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus2 WebHook OUT Constraints
cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_out_constraints = {
  "code": {
    "id": "cmixuyvrh0hmqp0025mr6ni0i",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmixuyy530hmzp002tlmh000j",
    "valueType": "preset",
    "required": True
  }
}

# cmiqr1jha00i6ie8fb1scb3go 검증 리스트
cmiqr1jha00i6ie8fb1scb3go_inConstraints = [
    cmiqr1jha00i6ie8fb1scb3go_Authentication_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_Capabilities_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_in_constraints,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_in_constraints,
]

# cmiqr1jha00i6ie8fb1scb3go WebHook Constraints 리스트
cmiqr1jha00i6ie8fb1scb3go_webhook_outConstraints = [
    None,
    None,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_webhook_out_constraints,
    None,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_webhook_out_constraints,
]

# Authentication
cmiqr0kdw00i4ie8fr3firjtg_Authentication_in_constraints = {
  "userID": {
    "id": "cmish1o9m08wq5vy7wvz8a61y",
    "valueType": "preset",
    "required": True
  },
  "userPW": {
    "id": "cmish1r4l08wy5vy7up1s9dse",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmiqr0kdw00i4ie8fr3firjtg_Capabilities_in_constraints = {}

# CameraProfiles
cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_in_constraints = {}

# PtzStatus
cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_in_constraints = {
  "camID": {
    "id": "cmixuacz20f85p002l1xbtf6i",
    "referenceFieldId": "cmixu969h0f6lp00297drc0if",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  }
}

# PtzContinuousMove
cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_in_constraints = {
  "camID": {
    "id": "cmixuddil0fbfp00232n3befi",
    "referenceFieldId": "cmixu969h0f6lp00297drc0if",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "velocity": {
    "id": "cmixudm8a0fbop002igjf7hdo",
    "valueType": "preset",
    "required": True
  },
  "velocity.pan": {
    "id": "cmixudtav0fbyp002unvnsqca",
    "valueType": "preset",
    "required": False
  },
  "velocity.tilt": {
    "id": "cmixue23t0fc9p002q0o9u5ml",
    "valueType": "preset",
    "required": False
  },
  "velocity.zoom": {
    "id": "cmixueccs0fclp002h9uzky0u",
    "valueType": "preset",
    "required": False
  },
  "timeOut": {
    "id": "cmixuen0z0fcxp002zjz5mexm",
    "valueType": "preset",
    "required": False
  }
}

# PtzStop
cmiqr0kdw00i4ie8fr3firjtg_PtzStop_in_constraints = {
  "camID": {
    "id": "cmixufxre0fe1p002m1w57aeb",
    "referenceFieldId": "cmixu969h0f6lp00297drc0if",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/CameraProfiles",
    "referenceField": "camID"
  },
  "pan": {
    "id": "cmixugh5u0fesp0024z3tedlc",
    "valueType": "preset",
    "required": False
  },
  "tilt": {
    "id": "cmixugfb10fepp002bv1rp8qr",
    "valueType": "preset",
    "required": False
  },
  "zoom": {
    "id": "cmixugrm30ff3p002dpby0eh7",
    "valueType": "preset",
    "required": False
  }
}

# cmiqr0kdw00i4ie8fr3firjtg 검증 리스트
cmiqr0kdw00i4ie8fr3firjtg_inConstraints = [
    cmiqr0kdw00i4ie8fr3firjtg_Authentication_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_Capabilities_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_CameraProfiles_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStatus_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_PtzContinuousMove_in_constraints,
    cmiqr0kdw00i4ie8fr3firjtg_PtzStop_in_constraints,
]

# Authentication
cmiqr201z00i8ie8fitdg5t1b_Authentication_out_constraints = {
  "code": {
    "id": "cmise6h0700lj5vy7s4v9c10v",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmise6px400my5vy7g75s15nw",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmise6roq00n75vy7ybrbiod8",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmise6tse00ne5vy7nh2re28j",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmise6vhr00nj5vy79f6dpfuy",
    "valueType": "preset",
    "required": False
  }
}

# Capabilities
cmiqr201z00i8ie8fitdg5t1b_Capabilities_out_constraints = {
  "code": {
    "id": "cmisel8x7017z5vy7ec1e56cu",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisele87018w5vy7kc760njz",
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "id": "cmisencfu01gm5vy7g5psolwh",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmisencfx01go5vy7jrh8pa2a",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmisencfx01gq5vy7uokgn8u3",
    "valueType": "preset",
    "required": False
  }
}

# SensorDeviceProfiles
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_out_constraints = {
  "code": {
    "id": "cmisev4br03dj5vy7q8tww5gm",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiseva9203e25vy7xh9ygo6s",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList": {
    "id": "cmisfgtvo07sw5vy7k8kfq13x",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmisfgtvs07sy5vy7f2hjy5aa",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceType": {
    "id": "cmisfgtvt07t05vy7qd9tbtc9",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceName": {
    "id": "cmisfgtvt07t25vy79eg4cnlj",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceLoc": {
    "id": "cmisfgtvu07t45vy7oxufjeba",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.sensorDeviceLoc.lon": {
    "id": "cmisfgtvz07t65vy7n4m3aoe0",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceLoc.lat": {
    "id": "cmisfgtw007t85vy7jrmgllyc",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceLoc.alt": {
    "id": "cmisfgtw007ta5vy7ut58i0y3",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.sensorDeviceLoc.desc": {
    "id": "cmisfgtw107tc5vy7as5hqx5m",
    "valueType": "preset",
    "required": False
  }
}

# SensorDeviceControl
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_out_constraints = {
  "code": {
    "id": "cmisg4vxz089s5vy7qhna151g",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmjch5wmv086jcfb3d2zeu1un",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceID": {
    "id": "cmisg51v408a85vy7mrhteunz",
    "referenceFieldId": "cmisg3n7u088o5vy75dl8ge3h",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceStatus": {
    "id": "cmj6hdjek01qsxei0ydzyxlg3",
    "valueType": "random",
    "required": True,
    "referenceField": "(참조 필드 미선택)",
    "referenceEndpoint": "/SensorDeviceControl",
    "validValueField": "sensorControl",
    "validValues": [
      "AlarmOn",
      "AlarmOff"
    ]
  }
}

# SensorDeviceControl2
cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_out_constraints = {
  "code": {
    "id": "cmisgsmo108me5vy7a070ga4t",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisgsssu08n85vy7rhriw5bx",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceID": {
    "id": "cmisgsuft08nf5vy70cyl59az",
    "referenceFieldId": "cmisgef0108e15vy7pvj4b2yg",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl2",
    "referenceField": "sensorDeviceID"
  },
  "sensorDeviceStatus": {
    "id": "cmisgsyrq08nn5vy7ggcm5ezc",
    "referenceFieldId": "cmiskmz17000kugxnuas8675t",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl2",
    "referenceField": "commandType"
  }
}

# cmiqr201z00i8ie8fitdg5t1b 검증 리스트
cmiqr201z00i8ie8fitdg5t1b_outConstraints = [
    cmiqr201z00i8ie8fitdg5t1b_Authentication_out_constraints,
    cmiqr201z00i8ie8fitdg5t1b_Capabilities_out_constraints,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceProfiles_out_constraints,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl_out_constraints,
    cmiqr201z00i8ie8fitdg5t1b_SensorDeviceControl2_out_constraints,
]

# Authentication
cmiqr1acx00i5ie8fi022t1hp_Authentication_out_constraints = {
  "code": {
    "id": "cmisgxzw808ul5vy7gr8s98dc",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisgy1gp08uq5vy7194x1gfs",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmisgy8mc08v85vy7nzg2ozx6",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmisgyadj08vd5vy7s0zp2y9b",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmisgzrk508w65vy79bmeve7p",
    "valueType": "test-time",
    "required": True,
    "testInputConstraints": {
      "stringLength": {}
    }
  }
}

# Capabilities
cmiqr1acx00i5ie8fi022t1hp_Capabilities_out_constraints = {
  "code": {
    "id": "cmisjt9640bnb5vy7c6mmpnzy",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmisjtb5g0bol5vy730bd9uun",
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "id": "cmisjube90c0s5vy7tdfvfpnq",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmisjubeb0c0u5vy736142p3j",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmisjubec0c0w5vy7rtgcn5qu",
    "valueType": "preset",
    "required": False
  }
}

# DoorProfiles
cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_out_constraints = {
  "code": {
    "id": "cmiwq39sh07fz844gn5ojv8iv",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwq3ewx07g8844gfdjstgru",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmizh2j7v028i7eoei30z6if0",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmizh2j7y028k7eoekmch7neb",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorName": {
    "id": "cmizh2j7y028m7eoe561v1og0",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorRelayStatus": {
    "id": "cmizh2j7y028o7eoe7oum45e5",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorSensor": {
    "id": "cmizh2j7z028q7eoeh327meza",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc": {
    "id": "cmizh2j7z028s7eoem1q5umty",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.lon": {
    "id": "cmizh2j86028y7eoe7rnz5oci",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.lat": {
    "id": "cmizh2j8702907eoe17manciv",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.alt": {
    "id": "cmizh2j8702927eoetki8hmas",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.desc": {
    "id": "cmizh2j8702947eoe5ivm78fe",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList": {
    "id": "cmizh2j8802967eoear3svcpn",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.bioDeviceID": {
    "id": "cmizh2j8f029a7eoenj3oor7e",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.otherDeviceName": {
    "id": "cmiwqea340abf844g15xesdtc",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList.bioDeviceAuthTypeList": {
    "id": "cmizh2j8m029m7eoemeq1ifjn",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.bioDeviceName": {
    "id": "cmizh2j8f029c7eoemcuopjxw",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList": {
    "id": "cmizh2j8802987eoe9kemqk9s",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList.otherDeviceID": {
    "id": "cmizh2j8g029g7eoe4aae2xlo",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList.otherDeviceName": {
    "id": "cmizh2j8g029i7eoeps66od7e",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList.otherDeviceAuthTypeList": {
    "id": "cmjcmaawo0ab2cfb3ta97x4wn",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_constraints = {
  "code": {
    "id": "cmizg5khh00iq7eoexenwo9i9",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmizg5lyh00iw7eoe7wbhcxaj",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmjibn2jo0m6ncfb33t9lj809",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmjibn2jq0m6pcfb3gqgchw6g",
    "referenceFieldId": "cmiwqkuoj0aj9844g5oec97p9",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeDoorStatus",
    "referenceField": "doorID"
  },
  "doorList.doorName": {
    "id": "cmjibn2jr0m6rcfb3udx1c9nm",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorRelaySensor": {
    "id": "cmjibn2jr0m6tcfb3pm4t00rw",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorSensor": {
    "id": "cmjibn2jr0m6vcfb3hihnwxi0",
    "valueType": "preset",
    "required": True
  }
}

# DoorControl
cmiqr1acx00i5ie8fi022t1hp_DoorControl_out_constraints = {
  "code": {
    "id": "cmiwqp4z80azq844gf2xm9qtt",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwqpbp70b00844gr7gg59fr",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus2
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_out_constraints = {
  "code": {
    "id": "cmiwqw4by0bo6844gvwitykp8",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwqw7dj0boe844gmkrvh7iu",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmjibisoz0m1xcfb3kpz2l6gk",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmjibisp10m1zcfb339obwqmf",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorName": {
    "id": "cmjibisp20m21cfb3y8wh8nbs",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorRelaySensor": {
    "id": "cmjibisp20m23cfb3hnjuxrez",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorSensor": {
    "id": "cmjibisp20m25cfb3t4ru92yd",
    "valueType": "preset",
    "required": True
  }
}

# cmiqr1acx00i5ie8fi022t1hp 검증 리스트
cmiqr1acx00i5ie8fi022t1hp_outConstraints = [
    cmiqr1acx00i5ie8fi022t1hp_Authentication_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_Capabilities_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_DoorControl_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus2_out_constraints,
]

# Authentication
cmiqqzrjz00i3ie8figf79cur_Authentication_out_constraints = {
  "code": {
    "id": "cmish3lv5090t5vy7ppk8nh5y",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmish3n4c090y5vy7vozpz3c9",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmish3roj091m5vy70dja7bsr",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmish3th3091t5vy7hnm0qk5t",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmish3v9b091y5vy7b8isryog",
    "valueType": "test-time",
    "required": False
  }
}

# Capabilities
cmiqqzrjz00i3ie8figf79cur_Capabilities_out_constraints = {
  "code": {
    "id": "cmiwp7rmz05kq844gqqw69i5s",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwp7ycr05kz844gpry7r479",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport": {
    "id": "cmiwp9wl305qy844gnfzg8d6v",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport.streamProtocolType": {
    "id": "cmiwp9wl405r0844gevqq7thx",
    "valueType": "preset",
    "required": True
  },
  "streamingSupport.streamProtocolDesc": {
    "id": "cmiwp9wl505r2844gnotixjmo",
    "valueType": "preset",
    "required": False
  },
  "transportSupport": {
    "id": "cmiwp9wld05r4844gwbrgvweo",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmiwp9wlf05r6844g337ki5mc",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmiwp9wlf05r8844gnxagb6rb",
    "valueType": "preset",
    "required": False
  }
}

# CameraProfiles
cmiqqzrjz00i3ie8figf79cur_CameraProfiles_out_constraints = {
  "code": {
    "id": "cmiwpbac505rs844g0w11qcj8",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwpbir605s2844gy6l7ht7i",
    "valueType": "preset",
    "required": True
  },
  "camList": {
    "id": "cmiwpi3sx076w844g20jekxkx",
    "valueType": "preset",
    "required": True
  },
  "camList.camID": {
    "id": "cmiwpi3sz076y844gftp3b99j",
    "valueType": "preset",
    "required": True
  },
  "camList.camName": {
    "id": "cmiwpi3t00770844gdctr9fw1",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc": {
    "id": "cmiwpi3t00772844gts4nv5ql",
    "valueType": "preset",
    "required": False
  },
  "camList.camLoc.lon": {
    "id": "cmiwpi3t50776844gcy9byurz",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.lat": {
    "id": "cmiwpi3t50778844guj8t5it2",
    "valueType": "preset",
    "required": True
  },
  "camList.camLoc.alt": {
    "id": "cmiwpi3t6077a844g0b0yeqx8",
    "valueType": "preset",
    "required": False
  },
  "camList.camLoc.desc": {
    "id": "cmiwpi3t6077c844gk3w5sd4w",
    "valueType": "preset",
    "required": False
  },
  "camList.camConfig": {
    "id": "cmiwpi3t00774844g2zghfgzy",
    "valueType": "preset",
    "required": False
  },
  "camList.camConfig.camType": {
    "id": "cmiwpi3t6077e844gn2ohl1ou",
    "valueType": "preset",
    "required": True
  }
}

# PtzStatus
cmiqqzrjz00i3ie8figf79cur_PtzStatus_out_constraints = {
  "code": {
    "id": "cmiwpo8gz0789844gz619d01h",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwpoeoi078i844g85lop6oe",
    "valueType": "preset",
    "required": True
  },
  "position": {
    "id": "cmiwpojna078r844g6ulioxop",
    "valueType": "preset",
    "required": False
  },
  "position.pan": {
    "id": "cmiwppn930791844g4wbst740",
    "valueType": "preset",
    "required": False
  },
  "position.tilt": {
    "id": "cmiwpptx8079b844g1f7xa2y6",
    "valueType": "preset",
    "required": False
  },
  "position.zoom": {
    "id": "cmiwpq2d4079l844gn2uy03vw",
    "valueType": "preset",
    "required": False
  },
  "moveStatus": {
    "id": "cmiwpqqwx079z844gkr7zhzg3",
    "valueType": "preset",
    "required": True
  },
  "moveStatus.pan": {
    "id": "cmiwpqw4u07a9844g8w3hl36p",
    "valueType": "preset",
    "required": False
  },
  "moveStatus.tilt": {
    "id": "cmiwpr18g07aj844g12ft2m11",
    "valueType": "preset",
    "required": False
  },
  "moveStatus.zoom": {
    "id": "cmiwpr6ja07as844gp1ll94fb",
    "valueType": "preset",
    "required": False
  }
}

# PtzContinuousMove
cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_out_constraints = {
  "code": {
    "id": "cmiwpuitl07d5844gzj2zay1m",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwpupho07de844ghl7x9u0q",
    "valueType": "preset",
    "required": True
  }
}

# PtzStop
cmiqqzrjz00i3ie8figf79cur_PtzStop_out_constraints = {
  "code": {
    "id": "cmiwpx90h07f1844glcuw528e",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwpxflk07fb844ge0ye0ib7",
    "valueType": "preset",
    "required": True
  }
}

# cmiqqzrjz00i3ie8figf79cur 검증 리스트
cmiqqzrjz00i3ie8figf79cur_outConstraints = [
    cmiqqzrjz00i3ie8figf79cur_Authentication_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_Capabilities_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_CameraProfiles_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_PtzStatus_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_PtzContinuousMove_out_constraints,
    cmiqqzrjz00i3ie8figf79cur_PtzStop_out_constraints,
]

