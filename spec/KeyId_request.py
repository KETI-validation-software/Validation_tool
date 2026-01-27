# Key to Field ID Mapping
# Contains both Request and Response mappings

# ========== REQUEST MAPPINGS ==========

# cmiqr1jha00i6ie8fb1scb3go
cmiqr1jha00i6ie8fb1scb3go_Authentication_request_key_ids = {
    "userID": "cmisgv95008oh5vy7mjspm3wh",
    "userPW": "cmisgvcex08oq5vy7d84t9tts",
}

cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_request_key_ids = {
    "doorList": "cmixuoz8e0grnp0020xzn3bck",
    "doorList.doorID": "cmixuqxeb0h0np002mwczcz4g",
    "duration": "cmixupira0gudp0025a627ml4",
    "transProtocol": "cmixupvnn0gw1p002t4oynlxp",
    "transProtocol.transProtocolType": "cmixuq3qa0gxmp0023qvxro6p",
    "transProtocol.transProtocolDesc": "cmixuq6xh0gxzp002nbmk4kcc",
    "startTime": "cmixuqodk0h00p002xkjhnyca",
    "code": "cmixussd70hbkp002351v2o5r",
    "message": "cmixusvcf0hbqp002tdeowl0t",
}

cmiqr1jha00i6ie8fb1scb3go_DoorControl_request_key_ids = {
    "doorID": "cmixuu5os0hc9p002st12cpzi",
    "commandType": "cmj83qob2000isnx0rwhvblif",
}

cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_request_key_ids = {
    "doorList": "cmize6nzh000f96qhvk7bjdr8",
    "doorList.doorID": "cmize9v8b00a296qh1vooije0",
    "duration": "cmize7lki002a96qhe5181nqj",
    "transProtocol": "cmize811g003m96qhzuj5k87j",
    "transProtocol.transProtocolType": "cmize8g5l006w96qhvnt0i28e",
    "transProtocol.transProtocolDesc": "cmize8y8y008q96qhgmcgwvmc",
    "startTime": "cmize9f5s009v96qhrbr6kzd5",
    "code": "cmixuyvrh0hmqp0025mr6ni0i",
    "message": "cmixuyy530hmzp002tlmh000j",
}

# cmiqr1jha00i6ie8fb1scb3go Request Key-ID Mapping 리스트
cmiqr1jha00i6ie8fb1scb3go_request_key_ids = [
    cmiqr1jha00i6ie8fb1scb3go_Authentication_request_key_ids,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_request_key_ids,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_request_key_ids,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_request_key_ids,
]


# ========== RESPONSE MAPPINGS ==========

# cmiqr1jha00i6ie8fb1scb3go
cmiqr1jha00i6ie8fb1scb3go_Authentication_response_key_ids = {
    "code": "cmisgvtfy08q45vy75w4t6e82",
    "message": "cmisgvv1h08qd5vy7s5fran9o",
    "userName": "cmisgvwr008qk5vy7d3z7bh9l",
    "userAff": "cmisgvye808qp5vy749aqxnq7",
    "accessToken": "cmisgw1aj08qx5vy7f3w5io4b",
}

cmiqr1jha00i6ie8fb1scb3go_Capabilities_response_key_ids = {
    "code": "cmisjrrkv0b1j5vy7uuo4hlyc",
    "message": "cmisjrtoh0b1r5vy7l5mi17ay",
    "transportSupport": "cmisjrwgx0b1z5vy7apr2bygy",
    "transportSupport.transProtocolType": "cmisjs9ow0b6z5vy7kd1hfb3t",
    "transportSupport.transProtocolDesc": "cmisjs9ox0b715vy7wjh6334s",
}

cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_response_key_ids = {
    "code": "cmixuifl50fgcp002yln327y3",
    "message": "cmixuihbv0fghp002hyjp56jq",
    "doorList": "cmixuik770fgqp002ekz3p7tl",
    "doorList.doorID": "cmkng6o1b01bfh0ztvksaxlzq",
    "doorList.doorName": "cmixumswi0gq3p0028lw5v5nb",
    "doorList.doorRelayStatus": "cmixumswj0gq5p0024p3525c2",
    "doorList.doorSensor": "cmixumswj0gq7p0020kzg25w8",
    "doorList.doorLoc": "cmixumswj0gq9p002aa9ny0b4",
    "doorList.doorLoc.lon": "cmixumswr0gqfp002ilnrdapi",
    "doorList.doorLoc.lat": "cmixumswr0gqhp0023nb9qs9f",
    "doorList.doorLoc.alt": "cmixumswr0gqjp00280swk9r3",
    "doorList.doorLoc.desc": "cmixumsws0gqlp002q169hm0f",
    "doorList.bioDeviceList": "cmixumswk0gqbp002hp87731i",
    "doorList.bioDeviceList.bioDeviceID": "cmixumswz0gqrp0029htn2v8t",
    "doorList.bioDeviceList.bioDeviceName": "cmixumswz0gqtp002s3v6q2i0",
    "doorList.bioDeviceList.bioDeviceAuthTypeList": "cmixumswz0gqvp00263wsw3ws",
    "doorList.otherDeviceList": "cmixumswk0gqdp002f36koaww",
    "doorList.otherDeviceList.otherDeviceID": "cmixumsx00gqxp002honqgpty",
    "doorList.otherDeviceList.otherDeviceName": "cmixumsx00gqzp002liegr4uq",
    "doorList.otherDeviceList.otherDeviceAuthTypeList": "cmixumsx00gr1p002pa83hn6b",
}

cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_response_key_ids = {
    "code": "cmixur2k30h12p0021dj2dqwu",
    "message": "cmixur54k0h18p0025u2ok46q",
    "doorList": "cmixurclc0h1gp0027apvg6ez",
    "doorList.doorID": "cmixusnx90hatp002m3rnln60",
    "doorList.doorName": "cmixusnx90havp0024dgra9az",
    "doorList.doorRelaySensor": "cmixusnx90haxp002vctfavqr",
    "doorList.doorSensor": "cmixusnxa0hazp002h9lu2gt7",
}

cmiqr1jha00i6ie8fb1scb3go_DoorControl_response_key_ids = {
    "code": "cmixuums70hcrp0022uu12x05",
    "message": "cmixuupod0hcxp002anplrma0",
}

cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_response_key_ids = {
    "code": "cmizea7th00ao96qhtccvs2gv",
    "message": "cmizea94s00at96qh5tv1j1x9",
    "doorList": "cmixuwob20hdhp002hcun4fpz",
    "doorList.doorID": "cmixuykwk0hmep002xddae990",
    "doorList.doorName": "cmjgs2dj30ez2cfb3659utj1s",
    "doorList.doorRelaySensor": "cmjgs2g8p0ezgcfb34mo5cfu4",
    "doorList.doorSensor": "cmjgs2iun0ezycfb3ilp8j2k7",
}

# cmiqr1jha00i6ie8fb1scb3go Response Key-ID Mapping 리스트
cmiqr1jha00i6ie8fb1scb3go_response_key_ids = [
    cmiqr1jha00i6ie8fb1scb3go_Authentication_response_key_ids,
    cmiqr1jha00i6ie8fb1scb3go_Capabilities_response_key_ids,
    cmiqr1jha00i6ie8fb1scb3go_DoorProfiles_response_key_ids,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus_response_key_ids,
    cmiqr1jha00i6ie8fb1scb3go_DoorControl_response_key_ids,
    cmiqr1jha00i6ie8fb1scb3go_RealtimeDoorStatus2_response_key_ids,
]

