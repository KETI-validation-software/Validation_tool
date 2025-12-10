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
    "id": "cmisg4zcn08a05vy7gzrw0rbp",
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
    "id": "cmizexb5a001c7eoe0cbjb715",
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
    "referenceEndpoint": "/SensorDeviceControl",
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
    "id": "cmiwqea2j0aaj844gsmv776m2",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwqea2m0aal844glnq1ha1f",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorName": {
    "id": "cmiwqea2m0aan844gy7vr7mj2",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorRelayStatus": {
    "id": "cmiwqea2n0aap844gxw3jl57n",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorSensor": {
    "id": "cmiwqea2n0aar844g4ttecy5h",
    "valueType": "preset",
    "required": False
  },
  "doorList.doorLoc": {
    "id": "cmiwqea2n0aat844gw7ekyi7l",
    "valueType": "preset",
    "required": False
  },
  "doorList.doorLoc.lon": {
    "id": "cmiwqea2u0aaz844gfq7nruk0",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.lat": {
    "id": "cmiwqea2v0ab1844grpe8lcy5",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorLoc.alt": {
    "id": "cmiwqea2v0ab3844gwc2khaeu",
    "valueType": "preset",
    "required": False
  },
  "doorList.doorLoc.desc": {
    "id": "cmiwqea2v0ab5844g1t459sbz",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList": {
    "id": "cmiwqea2w0ab9844g4daa2dhy",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.bioDeviceID": {
    "id": "cmiwqea350abj844gtvp1zrwb",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList.otherDeviceName": {
    "id": "cmiwqea340abf844g15xesdtc",
    "valueType": "preset",
    "required": False
  },
  "doorList.bioDeviceList.bioDeviceAuthTypeList": {
    "id": "cmiwqea3f0abz844gyrjcomws",
    "valueType": "preset",
    "required": True
  },
  "doorList.bioDeviceList.bioDeviceName": {
    "id": "cmiwqea350abl844ghzwj8pse",
    "valueType": "preset",
    "required": False
  },
  "doorList.otherDeviceList": {
    "id": "cmiwqea2w0abb844g34io2606",
    "valueType": "preset",
    "required": True
  },
  "doorList.otherDeviceList.otherDeviceID": {
    "id": "cmiwqea360abp844gnj1wkjug",
    "valueType": "preset",
    "required": False
  },
  "doorList.otherDeviceList.otherDeviceName": {
    "id": "cmiwqea360abr844g96ke1ex9",
    "valueType": "preset",
    "required": False
  },
  "doorList.otherDeviceList.otherDeviceAuthTypeList": {
    "id": "cmiwqea3f0ac1844grt8u5fgz",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_constraints = {
  "code": {
    "id": "cmiwql1950ajo844grnqxrsr1",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwql75b0ajx844gj0rlj7vk",
    "valueType": "preset",
    "required": True
  },
  "doorList": {
    "id": "cmiwqo37k0ayh844gbo8kd9cq",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwqo37m0ayj844gsaq74fru",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorName": {
    "id": "cmiwqo37n0ayl844go0t8etmx",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorRelaySensor": {
    "id": "cmiwqo37n0ayn844ghhkyhou2",
    "valueType": "preset",
    "required": False
  },
  "doorList.doorSensor": {
    "id": "cmiwqo37n0ayp844g1rgnxkvl",
    "valueType": "preset",
    "required": False
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

# RealtimeDoorStatus
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_constraints = {
  "code": {
    "id": "cmiwqsqrw0b7y844gtn3rzf7y",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmiwqsvzu0b88844gjdzch27v",
    "valueType": "preset",
    "required": True
  }
}

# RealtimeDoorStatus WebHook IN Constraints
cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_webhook_in_constraints = {
  "doorList": {
    "id": "cmiwqvxnz0bnq844gwxqyaals",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorID": {
    "id": "cmiwqvxo10bns844gr4trpxc7",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorName": {
    "id": "cmiwqvxo10bnu844gwl983tvp",
    "valueType": "preset",
    "required": True
  },
  "doorList.doorRelaySensor": {
    "id": "cmiwqvxo10bnw844g53owcer6",
    "valueType": "preset",
    "required": False
  },
  "doorList.doorSensor": {
    "id": "cmiwqvxo20bny844guwpaazsg",
    "valueType": "preset",
    "required": False
  }
}

# cmiqr1acx00i5ie8fi022t1hp 검증 리스트
cmiqr1acx00i5ie8fi022t1hp_outConstraints = [
    cmiqr1acx00i5ie8fi022t1hp_Authentication_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_Capabilities_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_DoorProfiles_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_DoorControl_out_constraints,
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_out_constraints,
]

# cmiqr1acx00i5ie8fi022t1hp WebHook Constraints 리스트
cmiqr1acx00i5ie8fi022t1hp_webhook_inConstraints = [
    cmiqr1acx00i5ie8fi022t1hp_RealtimeDoorStatus_webhook_in_constraints,
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
  "code ": {
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

