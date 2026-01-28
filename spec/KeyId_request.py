# Key to Field ID Mapping
# Contains both Request and Response mappings

# ========== REQUEST MAPPINGS ==========

# cmii7wfuf006i8z1tcds6q69g
cmii7wfuf006i8z1tcds6q69g_Authentication_request_key_ids = {
    "userID": "cmii82ahs008x8z1thvfawwei",
    "userPW": "cmii82ahs008z8z1tvxy4vzwn",
}

cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_request_key_ids = {
    "sensorDeviceList": "cmiwuvrou0c6ap002xlahudcz",
    "sensorDeviceList.sensorDeviceID": "cmiwuxvls0cj1p002zte0s84o",
    "duration": "cmiwuwqka0cbqp002qx42j8x7",
    "transProtocol": "cmiwux3lm0cdpp002n1c75w5l",
    "transProtocol.transProtocolType": "cmiwuxd090cfbp002sihhj47s",
    "transProtocol.transProtocolDesc": "cmiwuxhpy0cgkp002vjpiq17v",
    "startTime": "cmiwuxprg0ci6p002aq1y8z2s",
    "code": "cmiwttqdg0c1kp002y3l9weoo",
    "message": "cmiwv0k5n0ddfp0023v94f65d",
}

cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_request_key_ids = {
    "sensorDeviceList": "cmj6fc7g9011kxei0j7h06xao",
    "sensorDeviceList.sensorDeviceID": "cmj6feinr01aixei0iwq8v8ia",
    "duration": "cmj6fctgn0140xei0xxeg3jq0",
    "transProtocol": "cmj6fcvlz014cxei08bwvc2j4",
    "transProtocol.transProtocolType": "cmj6fd4lb016axei0p8g5qjvz",
    "transProtocol.transProtocolDesc": "cmj6fd608016mxei081nl2t2v",
    "eventFilter": "cmj6fdgsb0184xei0mr9kacqd",
    "startTime": "cmj6fdk4e018yxei03fzh2owz",
    "code": "cmj6fgmz201jaxei0x0a0oeio",
    "message": "cmj6fgodk01jgxei0cxvcsc7x",
}

cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_request_key_ids = {
    "timePeriod": "cmixtuwas0dgjp002hv5tx59h",
    "timePeriod.startTime": "cmixtv47x0dgtp002g9gr1j6f",
    "timePeriod.endTime": "cmixtvivy0dh4p0026kaoqaop",
    "sensorDeviceList": "cmixtvwg40dhfp002gndgmeq5",
    "sensorDeviceList.sensorDeviceID": "cmixtx2dx0dlwp002gtco28w8",
    "maxCount": "cmixtwo5i0dkcp00280zysdrq",
    "eventFilter": "cmixtwwqg0dlip002jrqkcbsv",
}

# cmii7wfuf006i8z1tcds6q69g Request Key-ID Mapping 리스트
cmii7wfuf006i8z1tcds6q69g_request_key_ids = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_request_key_ids,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_request_key_ids,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_request_key_ids,
    cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_request_key_ids,
]


# ========== RESPONSE MAPPINGS ==========

# cmii7wfuf006i8z1tcds6q69g
cmii7wfuf006i8z1tcds6q69g_Authentication_response_key_ids = {
    "code": "cmii82aiw00948z1t4zorar7m",
    "message": "cmii82aix00968z1t51zcno7t",
    "userName": "cmii82aix00988z1tn4iyrmhq",
    "userAff": "cmii82aiy009a8z1t3o899zlx",
    "accessToken": "cmii82aiy009c8z1t95xnyv1p",
}

cmii7wfuf006i8z1tcds6q69g_Capabilities_response_key_ids = {
    "code": "cmiwtmmrk0ap6p0020r6k1ynz",
    "message": "cmiwtmpgx0apep002atdrbc5b",
    "transportSupport": "cmiwtmtzb0apnp0023nubdfd6",
    "transportSupport.transProtocolType": "cmiwtn7u10ar0p002m43k2dad",
    "transportSupport.transProtocolDesc": "cmiwtn7u10ar2p002t77eede9",
}

cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_response_key_ids = {
    "code": "cmiwto2eb0armp002v593ukp5",
    "message": "cmiwto5cv0arup0024ym9t5tj",
    "sensorDeviceList": "cmiwto8d30as2p002irvkrnn1",
    "sensorDeviceList.sensorDeviceID": "cmiwtqkuz0bnop0021598be5a",
    "sensorDeviceList.sensorDeviceType": "cmiwtqkuz0bnqp002hkfhvzxy",
    "sensorDeviceList.sensorDeviceName": "cmiwtqkuz0bnsp002rb9b815f",
    "sensorDeviceList.sensorDeviceLoc": "cmiwtqkv00bnup002bnjjduxn",
    "sensorDeviceList.sensorDeviceLoc.lon": "cmiwtqkv40bnwp002emtntpkw",
    "sensorDeviceList.sensorDeviceLoc.lat": "cmiwtqkv40bnyp0026vdbz0u2",
    "sensorDeviceList.sensorDeviceLoc.alt": "cmiwtqkv40bo0p002ejkm02f8",
    "sensorDeviceList.sensorDeviceLoc.desc": "cmiwtqkv50bo2p002ux2sbhzz",
}

cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_response_key_ids = {
    "code": "cmiwuy0wz0cjhp0022kotjgup",
    "message": "cmiwuy3d90cjpp002uisu9j7r",
    "sensorDeviceList": "cmiwuy7tk0cjyp002h1fs7wro",
    "sensorDeviceList.sensorDeviceID": "cmiwv06mz0dc9p002hsbknejx",
    "sensorDeviceList.measureTime": "cmiwv06mz0dcbp002sjtbt0pg",
    "sensorDeviceList.sensorDeviceType": "cmiwv06n00dcdp002831795ig",
    "sensorDeviceList.sensorDeviceUnit": "cmiwv06n00dcfp002983uv1u1",
    "sensorDeviceList.sensorDeviceValue": "cmiwv06n00dchp002u86i0zhz",
}

cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_response_key_ids = {
    "code": "cmj6feq4o01bcxei0kd963njw",
    "message": "cmj6feree01bixei0ui615m7a",
    "sensorDeviceList": "cmj6fexgx01bwxei0g2kwvgd8",
    "sensorDeviceList.sensorDeviceID": "cmj6fgd0p01icxei0xjejwy14",
    "sensorDeviceList.eventName": "cmj6fgd0p01iexei0xclhu8uy",
    "sensorDeviceList.eventTime": "cmj6fgd0p01igxei0y9kb16z0",
    "sensorDeviceList.eventDesc": "cmj6fgd0p01iixei0fassafmt",
}

cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_response_key_ids = {
    "code": "cmixtx93k0dmbp002giiv2mn8",
    "message": "cmixtxbsw0dmkp002zadzlb2s",
    "sensorDeviceList": "cmixtxedg0dmtp0021yh790om",
    "sensorDeviceList.sensorDeviceID": "cmixtz2t50dydp002h8ijvxtb",
    "sensorDeviceList.eventName": "cmixtz2t60dyfp002gzvkjuc0",
    "sensorDeviceList.eventTime": "cmixtz2t60dyhp002jyhrxar4",
    "sensorDeviceList.eventDesc": "cmixtz2t60dyjp002tmkxp1kg",
}

# cmii7wfuf006i8z1tcds6q69g Response Key-ID Mapping 리스트
cmii7wfuf006i8z1tcds6q69g_response_key_ids = [
    cmii7wfuf006i8z1tcds6q69g_Authentication_response_key_ids,
    cmii7wfuf006i8z1tcds6q69g_Capabilities_response_key_ids,
    cmii7wfuf006i8z1tcds6q69g_SensorDeviceProfiles_response_key_ids,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorData_response_key_ids,
    cmii7wfuf006i8z1tcds6q69g_RealtimeSensorEventInfos_response_key_ids,
    cmii7wfuf006i8z1tcds6q69g_StoredSensorEventInfos_response_key_ids,
]

