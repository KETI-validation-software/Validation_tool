# Authentication
cmsmh2go501w6rc0q4s8zyqdp_Authentication_out_constraints = {
  "code": {
    "id": "cmsmh2goj01werc0qu67b6j4n",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmsmh2gor01wgrc0qsk8r12fw",
    "valueType": "preset",
    "required": True
  },
  "userName": {
    "id": "cmsmh2gou01wirc0qk63lzmui",
    "valueType": "preset",
    "required": True
  },
  "userAff": {
    "id": "cmsmh2gox01wkrc0qga9qmhwl",
    "valueType": "preset",
    "required": True
  },
  "accessToken": {
    "id": "cmsmh2goz01wmrc0qhbo4bair",
    "valueType": "preset",
    "required": True
  }
}

# Capabilities
cmsmh2go501w6rc0q4s8zyqdp_Capabilities_out_constraints = {
  "code": {
    "id": "cmsmh2gpg01x0rc0q03w2xjng",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmsmh2gpj01x2rc0qgilwtin4",
    "valueType": "preset",
    "required": True
  },
  "transportSupport": {
    "id": "cmsmh2gpp01x6rc0q6fma5qeb",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolType": {
    "id": "cmsmh2gpu01xarc0q3d5k2v1c",
    "valueType": "preset",
    "required": True
  },
  "transportSupport.transProtocolDesc": {
    "id": "cmsmh2gps01x8rc0qlkpgk4et",
    "valueType": "preset",
    "required": False
  }
}

# SensorDeviceProfiles
cmsmh2go501w6rc0q4s8zyqdp_SensorDeviceProfiles_out_constraints = {
  "code": {
    "id": "cmsmh2gq401xirc0qnvvl4z60",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmsmh2gq701xkrc0qkv5qr1w3",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList": {
    "id": "cmsmh2gq901xmrc0qohmoioib",
    "valueType": "preset",
    "required": True,
    "arrayElementType": "object"
  },
  "sensorDeviceList.0": {
    "id": "cmtwr8wq900ue245tx3m875yj",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceID": {
    "id": "cmtwr8wqe00ug245t5asqf1bn",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceLoc": {
    "id": "cmtwr8wqf00ui245tll5tjizd",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.0.sensorDeviceLoc.alt": {
    "id": "cmtwr8wqp00uo245t3tzo0f3q",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.0.sensorDeviceLoc.lat": {
    "id": "cmtwr8wqq00uq245tvdro6f4o",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceLoc.lon": {
    "id": "cmtwr8wqq00us245t9f94k3gm",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceLoc.desc": {
    "id": "cmtwr8wqr00uu245ty2bibdlm",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.0.sensorDeviceName": {
    "id": "cmtwr8wqg00uk245ts4swxcfp",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceType": {
    "id": "cmtwr8wqg00um245tkmu01ssx",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1": {
    "id": "cmtwr8wr500uw245t082b4j3b",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceID": {
    "id": "cmtwr8wr900uy245tnjtdcq8g",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceLoc": {
    "id": "cmtwr8wra00v0245tm8nfw7d4",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.1.sensorDeviceLoc.alt": {
    "id": "cmtwr8wri00v6245t5fcqmq0f",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.1.sensorDeviceLoc.lat": {
    "id": "cmtwr8wrj00v8245tguucdyzw",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceLoc.lon": {
    "id": "cmtwr8wrk00va245t5tia845a",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceLoc.desc": {
    "id": "cmtwr8wrk00vc245to2rn5r0j",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.1.sensorDeviceName": {
    "id": "cmtwr8wra00v2245tit1l2nym",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceType": {
    "id": "cmtwr8wrb00v4245tzhn9x2eb",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2": {
    "id": "cmtwr8wrq00ve245txv5csep1",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceID": {
    "id": "cmtwr8wru00vg245tvt9mp0es",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceLoc": {
    "id": "cmtwr8wrv00vi245thxradtoc",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.2.sensorDeviceLoc.alt": {
    "id": "cmtwr8ws300vo245teecw4iu0",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.2.sensorDeviceLoc.lat": {
    "id": "cmtwr8ws400vq245tt1yyxd8l",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceLoc.lon": {
    "id": "cmtwr8ws500vs245t64atu162",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceLoc.desc": {
    "id": "cmtwr8ws500vu245tqsejwyvk",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.2.sensorDeviceName": {
    "id": "cmtwr8wrw00vk245tvftle33m",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceType": {
    "id": "cmtwr8wrw00vm245tzhf8b7f9",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3": {
    "id": "cmtwr8wsb00vw245t5ln4p2oy",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceID": {
    "id": "cmtwr8wsf00vy245toqr8pydt",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceLoc": {
    "id": "cmtwr8wsg00w0245tgyrg5del",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.3.sensorDeviceLoc.alt": {
    "id": "cmtwr8wtv00w6245t81i1f6ja",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.3.sensorDeviceLoc.lat": {
    "id": "cmtwr8wtw00w8245t01tx10gy",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceLoc.lon": {
    "id": "cmtwr8wtx00wa245tg0dgvlj2",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceLoc.desc": {
    "id": "cmtwr8wty00wc245t7a0nnp7j",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.3.sensorDeviceName": {
    "id": "cmtwr8wsg00w2245tojpqi24d",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceType": {
    "id": "cmtwr8wsh00w4245txqy8tzej",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4": {
    "id": "cmtwr8wu300we245tyt37aq0f",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceID": {
    "id": "cmtwr8wu700wg245tf716kbfw",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceLoc": {
    "id": "cmtwr8wu800wi245tk5qw8nv9",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.4.sensorDeviceLoc.alt": {
    "id": "cmtwr8wug00wo245t1fq8xj0q",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.4.sensorDeviceLoc.lat": {
    "id": "cmtwr8wuh00wq245t7ezw3szv",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceLoc.lon": {
    "id": "cmtwr8wui00ws245t122mfxlt",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceLoc.desc": {
    "id": "cmtwr8wuj00wu245tmiahdwa4",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.4.sensorDeviceName": {
    "id": "cmtwr8wu800wk245ths7450gl",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceType": {
    "id": "cmtwr8wu900wm245tbk4f9zo9",
    "valueType": "preset",
    "required": True
  }
}

# StoredSensorEventInfos
cmsmh2go501w6rc0q4s8zyqdp_StoredSensorEventInfos_out_constraints = {
  "code": {
    "id": "cmsmh2h2u022wrc0qkv0dz40p",
    "valueType": "preset",
    "required": True
  },
  "message": {
    "id": "cmsmh2h3e023arc0qgqlvd6yn",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList": {
    "id": "cmsmh2h2z0230rc0qvx2767pr",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmsmh2h3b0238rc0qt963tq46",
    "referenceFieldId": "cmsmh2h2b022irc0qa5jxy64w",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredSensorEventInfos",
    "referenceField": "sensorDeviceList.sensorDeviceID",
    "isArrayFieldPath": True
  },
  "sensorDeviceList.eventName": {
    "id": "cmsmh2h350234rc0qsgjjmvu2",
    "referenceFieldId": "cmsmh2h0z022crc0qudhu9vvc",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/StoredSensorEventInfos",
    "referenceField": "eventFilter"
  },
  "sensorDeviceList.eventTime": {
    "id": "cmsmh2h380236rc0qmkoi5v6f",
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "maxField": "endTime",
      "minField": "startTime",
      "maxFieldId": "cmsmh2h2p022src0quuf1epeh",
      "minFieldId": "cmsmh2h2m022qrc0qn4e8xgpz",
      "maxEndpoint": "/StoredSensorEventInfos",
      "minEndpoint": "/StoredSensorEventInfos"
    },
    "requestRangeMinEndpoint": "/StoredSensorEventInfos",
    "requestRangeMaxEndpoint": "/StoredSensorEventInfos"
  },
  "sensorDeviceList.eventDesc": {
    "id": "cmsmh2h320232rc0qmdppdvj6",
    "valueType": "preset",
    "required": False
  }
}

# cmsmh2go501w6rc0q4s8zyqdp 검증 리스트
cmsmh2go501w6rc0q4s8zyqdp_outConstraints = [
    cmsmh2go501w6rc0q4s8zyqdp_Authentication_out_constraints,
    cmsmh2go501w6rc0q4s8zyqdp_Capabilities_out_constraints,
    cmsmh2go501w6rc0q4s8zyqdp_SensorDeviceProfiles_out_constraints,
    cmsmh2go501w6rc0q4s8zyqdp_StoredSensorEventInfos_out_constraints,
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
    "id": "cmisevcbu03e75vy761meayab",
    "valueType": "preset",
    "required": True,
    "arrayElementType": "object"
  },
  "sensorDeviceList.0": {
    "id": "cmtwr1evr00py245tr2gcuvr1",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceID": {
    "id": "cmtwr1ex400q0245trhytuni7",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceLoc": {
    "id": "cmtwr1ex500q2245tnbgy391d",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.0.sensorDeviceLoc.alt": {
    "id": "cmtwr1exh00q8245t0fn57ofp",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.0.sensorDeviceLoc.lat": {
    "id": "cmtwr1exh00qa245telx9przg",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceLoc.lon": {
    "id": "cmtwr1exi00qc245txc3y26ha",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceLoc.desc": {
    "id": "cmtwr1exj00qe245tije4vssd",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.0.sensorDeviceName": {
    "id": "cmtwr1ex600q4245toa8hx2gh",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceType": {
    "id": "cmtwr1ex600q6245tow7vuijx",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1": {
    "id": "cmtwr1exp00qg245tua3skywt",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceID": {
    "id": "cmtwr1exy00qi245t490m4vsn",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceLoc": {
    "id": "cmtwr1exz00qk245t1b0e0oou",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.1.sensorDeviceLoc.alt": {
    "id": "cmtwr1f0c00qq245toexkp2mf",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.1.sensorDeviceLoc.lat": {
    "id": "cmtwr1f0d00qs245ttgsljlqy",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceLoc.lon": {
    "id": "cmtwr1f0e00qu245trmsij8wq",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceLoc.desc": {
    "id": "cmtwr1f0e00qw245tzwmrndu2",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.1.sensorDeviceName": {
    "id": "cmtwr1ey000qm245t5d27j3g4",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceType": {
    "id": "cmtwr1ey000qo245t2dgpwci7",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2": {
    "id": "cmtwr1f0w00qy245teiafh2r9",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceID": {
    "id": "cmtwr1f2v00r0245tnxbqgmi3",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceLoc": {
    "id": "cmtwr1f2w00r2245thzur49an",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.2.sensorDeviceLoc.alt": {
    "id": "cmtwr1f3b00r8245t3ovrm2zy",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.2.sensorDeviceLoc.lat": {
    "id": "cmtwr1f5f00ra245t5h93jusx",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceLoc.lon": {
    "id": "cmtwr1f5g00rc245t3f396gtl",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceLoc.desc": {
    "id": "cmtwr1f5h00re245tl4x6e1ae",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.2.sensorDeviceName": {
    "id": "cmtwr1f2x00r4245t9e78u359",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceType": {
    "id": "cmtwr1f2x00r6245tt8tnqz00",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3": {
    "id": "cmtwr1f6100rg245th2dlqm87",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceID": {
    "id": "cmtwr1f8k00ri245tl8w844hs",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceLoc": {
    "id": "cmtwr1f8l00rk245t2dxuer7e",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.3.sensorDeviceLoc.alt": {
    "id": "cmtwr1fb700rq245ti3v9udj0",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.3.sensorDeviceLoc.lat": {
    "id": "cmtwr1fb800rs245tb1qpeur3",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceLoc.lon": {
    "id": "cmtwr1fb800ru245trzcvc04w",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceLoc.desc": {
    "id": "cmtwr1fb900rw245t072eav0j",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.3.sensorDeviceName": {
    "id": "cmtwr1f8m00rm245ts3ycig9u",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceType": {
    "id": "cmtwr1f8m00ro245tv11yq0il",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4": {
    "id": "cmtwr1fdr00ry245tcd74a4aa",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceID": {
    "id": "cmtwr1fdy00s1245tcapflkij",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceLoc": {
    "id": "cmtwr1fdy00s3245tww1tqsj4",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.4.sensorDeviceLoc.alt": {
    "id": "cmtwr1fe500s9245t071xqi9h",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.4.sensorDeviceLoc.lat": {
    "id": "cmtwr1fe600sb245tjjcra1vb",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceLoc.lon": {
    "id": "cmtwr1fe600sd245tjov3fmp3",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceLoc.desc": {
    "id": "cmtwr1fe700sf245tvw687ihw",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.4.sensorDeviceName": {
    "id": "cmtwr1fdz00s5245tvhlzo04v",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceType": {
    "id": "cmtwr1fe000s7245tayzhebvi",
    "valueType": "preset",
    "required": True
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
    "referenceFieldId": "cmiwkyi4402a0844gkokgga8t",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceControl",
    "referenceField": "commandType"
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
    "id": "cmiwkjxse004i844g6dzk9xuk",
    "valueType": "preset",
    "required": True,
    "arrayElementType": "object"
  },
  "sensorDeviceList.0": {
    "id": "cmtwphnzk00f8245thri61o6t",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceID": {
    "id": "cmtwphnzq00fa245t2l6b707g",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceLoc": {
    "id": "cmtwphnzr00fc245tmby062xt",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.0.sensorDeviceLoc.alt": {
    "id": "cmtwpho0200fi245t9w7b34fd",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.0.sensorDeviceLoc.lat": {
    "id": "cmtwpho0300fk245tkthkj8qd",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceLoc.lon": {
    "id": "cmtwpho0400fm245ts9tz3wmo",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceLoc.desc": {
    "id": "cmtwpho0400fo245t650kev5o",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.0.sensorDeviceName": {
    "id": "cmtwphnzs00fe245t9ui7jmn1",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.0.sensorDeviceType": {
    "id": "cmtwphnzs00fg245t4ru04qc6",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1": {
    "id": "cmtwpho0c00fq245tf1wg3yk7",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceID": {
    "id": "cmtwpho0g00fs245tjd8h0dfq",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceLoc": {
    "id": "cmtwpho0h00fu245td0lb1pbd",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.1.sensorDeviceLoc.alt": {
    "id": "cmtwpho0q00g0245ta2ng49cx",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.1.sensorDeviceLoc.lat": {
    "id": "cmtwpho0r00g2245t11urj5j1",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceLoc.lon": {
    "id": "cmtwpho0r00g4245ttyv16kge",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceLoc.desc": {
    "id": "cmtwpho1w00g6245t4o820go8",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.1.sensorDeviceName": {
    "id": "cmtwpho0i00fw245tkk46jagp",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.1.sensorDeviceType": {
    "id": "cmtwpho0i00fy245tejdnkjxm",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2": {
    "id": "cmtwpho2200g8245tyxu11ztz",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceID": {
    "id": "cmtwpho2600ga245tdt93ovxt",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceLoc": {
    "id": "cmtwpho2700gc245teoese7vp",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.2.sensorDeviceLoc.alt": {
    "id": "cmtwpho2g00gi245tr4y6y9mr",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.2.sensorDeviceLoc.lat": {
    "id": "cmtwpho2g00gk245tg2adn96l",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceLoc.lon": {
    "id": "cmtwpho2h00gm245t6cqn6img",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceLoc.desc": {
    "id": "cmtwpho2i00go245tlqj5q5tl",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.2.sensorDeviceName": {
    "id": "cmtwpho2700ge245tstk9nvhv",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.2.sensorDeviceType": {
    "id": "cmtwpho2800gg245twwlkf4yu",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3": {
    "id": "cmtwpho2o00gq245t1ynb75ms",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceID": {
    "id": "cmtwpho2s00gs245t53uxsiyf",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceLoc": {
    "id": "cmtwpho2t00gu245tgwuovbag",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.3.sensorDeviceLoc.alt": {
    "id": "cmtwpho3200h0245tv46z61x0",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.3.sensorDeviceLoc.lat": {
    "id": "cmtwpho3300h2245tivvdmmu5",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceLoc.lon": {
    "id": "cmtwpho3400h4245tprj54hk3",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceLoc.desc": {
    "id": "cmtwpho3400h6245t211gajoj",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.3.sensorDeviceName": {
    "id": "cmtwpho2u00gw245tccluhgh6",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.3.sensorDeviceType": {
    "id": "cmtwpho2v00gy245tfb1j9ehl",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4": {
    "id": "cmtwpho3b00h8245t7356ufjs",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceID": {
    "id": "cmtwpho3f00ha245t8m9ui81d",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceLoc": {
    "id": "cmtwpho3g00hc245tqqn1jccf",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.4.sensorDeviceLoc.alt": {
    "id": "cmtwpho4u00hi245t7v7ifrhl",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.4.sensorDeviceLoc.lat": {
    "id": "cmtwpho4v00hk245txa5qa27m",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceLoc.lon": {
    "id": "cmtwpho4v00hm245t6bdu0s3v",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceLoc.desc": {
    "id": "cmtwpho4w00ho245tq4neohqd",
    "valueType": "preset",
    "required": False
  },
  "sensorDeviceList.4.sensorDeviceName": {
    "id": "cmtwpho3g00he245ti89d4kd4",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.4.sensorDeviceType": {
    "id": "cmtwpho3h00hg245thm6lurd2",
    "valueType": "preset",
    "required": True
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
    "id": "cmiwkzuq402wu844gjdmliu0o",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceID": {
    "id": "cmiwkzuq802ww844gv07bx7d6",
    "referenceFieldId": "cmiwkzuq802ww844gv07bx7d6",
    "valueType": "request-based",
    "required": True,
    "referenceEndpoint": "/RealtimeSensorData",
    "referenceField": "sensorDeviceList.sensorDeviceID",
    "isArrayFieldPath": True
  },
  "sensorDeviceList.measureTime": {
    "id": "cmiwkzuq902wy844g8o8p54hp",
    "valueType": "request-range",
    "required": True,
    "requestRange": {
      "minField": "startTime",
      "operator": "greater-equal",
      "minFieldId": "cmiwku3u101pg844gejhlznpv",
      "minEndpoint": "/RealtimeSensorData"
    },
    "requestRangeMinEndpoint": "/RealtimeSensorData"
  },
  "sensorDeviceList.sensorDeviceType": {
    "id": "cmiwkzuq902x0844gxgkox1jk",
    "referenceFieldId": "cmtwphnzs00fg245t4ru04qc6",
    "valueType": "response-based",
    "required": True,
    "referenceEndpoint": "/SensorDeviceProfiles",
    "referenceField": "sensorDeviceList.sensorDeviceType",
    "isArrayFieldPath": True
  },
  "sensorDeviceList.sensorDeviceUnit": {
    "id": "cmiwkzuqa02x2844g06s0pkxi",
    "valueType": "preset",
    "required": True
  },
  "sensorDeviceList.sensorDeviceValue": {
    "id": "cmiwkzuqa02x4844ghl5po3db",
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
    "referenceField": "sensorDeviceList.sensorDeviceID",
    "isArrayFieldPath": True
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

# cmii7shen005i8z1tagevx4qh 검증 리스트
cmii7shen005i8z1tagevx4qh_outConstraints = [
    cmii7shen005i8z1tagevx4qh_Authentication_out_constraints,
    cmii7shen005i8z1tagevx4qh_Capabilities_out_constraints,
    cmii7shen005i8z1tagevx4qh_SensorDeviceProfiles_out_constraints,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_out_constraints,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_out_constraints,
]

# cmii7shen005i8z1tagevx4qh WebHook Constraints 리스트
cmii7shen005i8z1tagevx4qh_webhook_inConstraints = [
    None,
    None,
    None,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorData_webhook_in_constraints,
    cmii7shen005i8z1tagevx4qh_RealtimeSensorEventInfos_webhook_in_constraints,
]

