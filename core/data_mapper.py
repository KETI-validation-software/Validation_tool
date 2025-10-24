import random


class ConstraintDataGenerator:
    def __init__(self, latest_events=None):
        """
        latest_events: API 이벤트 저장소 {api_name: {direction: event_data}}
        """
        self.latest_events = latest_events if latest_events is not None else {}

    def _applied_constraints(self, request_data, template_data, constraints, n=5):
        """
        request_data: 요청 데이터 (camID 후보 등)
        template_data: response 템플릿
        constraints: 제약 조건
        n: 생성 개수
        """
        print(f"[DEBUG][DATA_MAPPER] _applied_constraints 호출됨")
        print(f"[DEBUG][DATA_MAPPER] request_data: {request_data}")
        print(f"[DEBUG][DATA_MAPPER] constraints keys: {list(constraints.keys()) if constraints else []}")
        print(
            f"[DEBUG][DATA_MAPPER] template_data keys: {list(template_data.keys()) if isinstance(template_data, dict) else 'N/A'}")
        print(f"[DEBUG][DATA_MAPPER] n: {n}")

        # constraints 분석 및 참조 값 수집
        constraint_map = self._build_constraint_map(constraints, request_data)
        print(f"[DEBUG][DATA_MAPPER] constraint_map: {constraint_map}")

        # 템플릿 기반 데이터 생성
        response = self._generate_from_template(template_data, constraint_map, n)
        print(f"[DEBUG][DATA_MAPPER] generated response: {response}")

        # template_data 업데이트 (원본 수정)
        template_data.update(response)

        # 전체 메시지 반환 (업데이트된 template_data)
        return template_data

    def _build_constraint_map(self, constraints, request_data):
        """constraints를 분석하여 각 필드의 제약 조건과 참조 값을 매핑"""
        constraint_map = {}

        print(f"[DEBUG][BUILD_MAP] constraints: {constraints}")
        print(f"[DEBUG][BUILD_MAP] request_data: {request_data}")

        for path, rule in constraints.items():
            print(f"[DEBUG][BUILD_MAP] Processing path: {path}, rule: {rule}")

            value_type = rule.get("valueType")
            ref_endpoint = rule.get("referenceEndpoint")
            ref_field = rule.get("referenceField")

            print(f"[DEBUG][BUILD_MAP]   valueType: {value_type}")
            print(f"[DEBUG][BUILD_MAP]   referenceEndpoint: {ref_endpoint}")
            print(f"[DEBUG][BUILD_MAP]   referenceField: {ref_field}")

            # referenceEndpoint가 있으면 latest_events에서 데이터 찾기
            if ref_endpoint:
                values = []

                # referenceEndpoint의 슬래시 처리 (있든 없든 찾을 수 있도록)
                # 예: "/StoredVideoEventInfos" → "StoredVideoEventInfos"
                ref_key = ref_endpoint.lstrip('/')

                print(f"[DEBUG][BUILD_MAP]   Searching for ref_key: {ref_key}")

                if ref_key in self.latest_events:
                    print(f"[DEBUG][BUILD_MAP]   Found referenceEndpoint in latest_events")
                    # valueType에 따라 REQUEST 또는 RESPONSE에서 가져오기
                    if value_type == "request-based":
                        event = self.latest_events[ref_key].get("REQUEST", {})
                        print(f"[DEBUG][BUILD_MAP]   Using REQUEST event")
                    else:  # random-response 등 다른 타입
                        event = self.latest_events[ref_key].get("RESPONSE", {})
                        print(f"[DEBUG][BUILD_MAP]   Using RESPONSE event")

                    event_data = event.get("data", {})
                    print(f"[DEBUG][BUILD_MAP]   event_data: {event_data}")
                    values = self.find_key(event_data, ref_field)
                    print(f"[DEBUG][BUILD_MAP]   Found values from event: {values}")
                else:
                    print(f"[DEBUG][BUILD_MAP]   referenceEndpoint NOT found in latest_events")
                    print(f"[DEBUG][BUILD_MAP]   Available endpoints: {list(self.latest_events.keys())}")

                constraint_map[path] = {
                    "type": value_type,
                    "values": values if values else []
                }

            elif value_type == "request-based":
                # referenceEndpoint 없으면 현재 request_data에서 찾기
                print(f"[DEBUG][BUILD_MAP]   Searching in current request_data")
                values = self.find_key(request_data, ref_field)
                print(f"[DEBUG][BUILD_MAP]   Found values from request: {values}")
                constraint_map[path] = {
                    "type": "request-based",
                    "values": values if values else []
                }

            elif value_type == "random-response":
                # referenceEndpoint 없으면 현재 request_data에서 찾기
                values = self.find_key(request_data, ref_field)
                constraint_map[path] = {
                    "type": "random-response",
                    "values": values if values else []
                }

            elif value_type == "random":
                # validValues에서 랜덤 선택
                valid_values = rule.get("validValues", [])
                constraint_map[path] = {
                    "type": "random",
                    "values": valid_values
                }

            elif value_type == "request-range":
                # 범위 제약 조건 처리
                req_range = rule.get("requestRange", {})
                operator = req_range.get("operator")

                print(f"[DEBUG][BUILD_MAP]   request-range operator: {operator}")

                if operator == "between":
                    min_field = req_range.get("minField")
                    max_field = req_range.get("maxField")

                    # referenceEndpoint가 있으면 latest_events에서, 없으면 request_data에서 찾기
                    # 슬래시 제거하여 키 매칭
                    ref_key = ref_endpoint.lstrip('/') if ref_endpoint else None

                    if ref_key and ref_key in self.latest_events:
                        event = self.latest_events[ref_key].get("REQUEST", {})
                        event_data = event.get("data", {})
                        min_vals = self.find_key(event_data, min_field) if min_field else []
                        max_vals = self.find_key(event_data, max_field) if max_field else []
                    else:
                        min_vals = self.find_key(request_data, min_field) if min_field else []
                        max_vals = self.find_key(request_data, max_field) if max_field else []

                    min_val = min_vals[0] if min_vals else 0
                    max_val = max_vals[0] if max_vals else 9999999999999

                    constraint_map[path] = {
                        "type": "request-range",
                        "operator": "between",
                        "min": min_val,
                        "max": max_val
                    }

                elif operator in ["greater-equal", "greater", "less-equal", "less"]:
                    # greater-equal, greater, less-equal, less 연산자 처리
                    min_field = req_range.get("minField")
                    max_field = req_range.get("maxField")
                    min_endpoint = req_range.get("minEndpoint")
                    max_endpoint = req_range.get("maxEndpoint")

                    # referenceEndpoint 또는 minEndpoint/maxEndpoint 처리
                    ref_key_min = (min_endpoint or ref_endpoint or "").lstrip('/')
                    ref_key_max = (max_endpoint or ref_endpoint or "").lstrip('/')

                    min_val = 0
                    max_val = 9999999999999

                    # min 값 찾기
                    if min_field:
                        if ref_key_min and ref_key_min in self.latest_events:
                            event = self.latest_events[ref_key_min].get("REQUEST", {})
                            event_data = event.get("data", {})
                            min_vals = self.find_key(event_data, min_field)
                        else:
                            min_vals = self.find_key(request_data, min_field)
                        min_val = min_vals[0] if min_vals else 0

                    # max 값 찾기
                    if max_field:
                        if ref_key_max and ref_key_max in self.latest_events:
                            event = self.latest_events[ref_key_max].get("REQUEST", {})
                            event_data = event.get("data", {})
                            max_vals = self.find_key(event_data, max_field)
                        else:
                            max_vals = self.find_key(request_data, max_field)
                        max_val = max_vals[0] if max_vals else 9999999999999

                    print(f"[DEBUG][BUILD_MAP]   request-range: min={min_val}, max={max_val}")

                    constraint_map[path] = {
                        "type": "request-range",
                        "operator": operator,
                        "min": min_val,
                        "max": max_val
                    }
                else:
                    # 기본 범위 (operator 없거나 알 수 없는 경우)
                    print(f"[DEBUG][BUILD_MAP]   Unknown operator: {operator}, using default range")
                    constraint_map[path] = {
                        "type": "request-range",
                        "operator": "between",
                        "min": 0,
                        "max": 9999999999999
                    }
            elif value_type == "response-based":
                # referenceEndpoint 없으면 현재 request_data에서 찾기
                print(f"[DEBUG][BUILD_MAP]   Searching in current request_data")
                values = self.find_key(request_data, ref_field)
                print(f"[DEBUG][BUILD_MAP]   Found values from request: {values}")
                constraint_map[path] = {
                    "type": "request-based",
                    "values": values if values else []
                }

            elif value_type == "random-response":
                # referenceEndpoint 없으면 현재 request_data에서 찾기
                values = self.find_key(request_data, ref_field)
                constraint_map[path] = {
                    "type": "random-response",
                    "values": values if values else []
                }

        return constraint_map

    def _generate_from_template(self, template, constraint_map, n):
        """템플릿을 재귀적으로 순회하며 데이터 생성"""
        result = {}

        for key, value in template.items():
            # 최상위 레벨에서 constraint 확인
            if key in constraint_map:
                constraint = constraint_map[key]
                if constraint["type"] in ["random-response", "random", "request-based", "response-based", ]:
                    # 랜덤 값 선택
                    if constraint["values"]:
                        result[key] = random.choice(constraint["values"])
                    else:
                        result[key] = value
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                # 리스트 형태의 구조 처리
                result[key] = self._generate_list_items(
                    key, value[0], constraint_map, n
                )
            elif isinstance(value, dict):
                # 중첩된 딕셔너리 구조는 그대로 유지 (최상위 레벨)
                result[key] = value
            else:
                # 일반 필드는 그대로 유지
                result[key] = value

        return result

    def _generate_list_items(self, parent_key, item_template, constraint_map, n):
        """리스트 항목 생성 - 중복 방지 (각 항목은 고유한 값)"""
        items = []

        # ✅ 사용 가능한 값들을 미리 수집
        available_values = {}
        used_values = {}  # 이미 사용된 값 추적
        shared_values = {}  # 필터 필드 (모든 항목에 동일한 값)
        min_available_count = float('inf')  # 최소 값 개수 추적

        # 필터 필드 목록 (중복 허용)
        filter_fields = ["eventFilter", "classFilter", "eventName"]

        for field, value in item_template.items():
            field_path = f"{parent_key}.{field}"
            if field_path in constraint_map:
                constraint = constraint_map[field_path]

                # request-based 중 필터 필드는 모든 항목에 동일한 값 사용
                if constraint["type"] == "request-based" and any(f in field for f in filter_fields):
                    if constraint["values"]:
                        # 첫 번째 값을 모든 항목에 공유
                        shared_values[field_path] = constraint["values"][0]

                # 그 외 필드는 중복 방지
                elif constraint["type"] in ["request-based", "random-response", "random"]:
                    if constraint["values"]:
                        available_values[field_path] = constraint["values"].copy()
                        used_values[field_path] = []  # 사용된 값 추적 초기화

                        # 최소 값 개수 추적
                        min_available_count = min(min_available_count, len(constraint["values"]))

        # ✅ 중복 방지: 생성 개수를 사용 가능한 최소 값 개수로 제한
        if min_available_count != float('inf') and n > min_available_count:
            original_n = n
            n = min_available_count
            print(
                f"[INFO] {parent_key}: 중복 방지를 위해 생성 개수를 {original_n}개 → {n}개로 조정했습니다. (사용 가능한 고유 값: {min_available_count}개)")

        for i in range(n):
            item = self._generate_item(parent_key, item_template, constraint_map, n,
                                       available_values=available_values,
                                       used_values=used_values,
                                       shared_values=shared_values,
                                       item_index=i)
            items.append(item)

        return items

    def _generate_item(self, parent_key, template, constraint_map, n, available_values=None, used_values=None,
                       shared_values=None, item_index=0):
        """단일 항목 생성 (재귀적으로 중첩 구조 처리) - 중복 방지"""
        item = {}

        if available_values is None:
            available_values = {}
        if used_values is None:
            used_values = {}
        if shared_values is None:
            shared_values = {}

        for field, value in template.items():
            field_path = f"{parent_key}.{field}"

            # 중첩된 딕셔너리 처리 (예: videoInfo)
            if isinstance(value, dict):
                item[field] = self._generate_item(field_path, value, constraint_map, n,
                                                  available_values, used_values, shared_values, item_index)

            # 중첩된 리스트 처리 (예: timeList)
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    item[field] = self._generate_list_items(
                        field_path, value[0], constraint_map, n
                    )
                else:
                    item[field] = value

            # constraint가 있는 필드 처리
            elif field_path in constraint_map:
                constraint = constraint_map[field_path]

                # ✅ shared_values (필터 필드): 모든 항목에 동일한 값
                if field_path in shared_values:
                    item[field] = shared_values[field_path]

                # ✅ request-based, random-response, random: 중복 방지 (순차 할당)
                elif constraint["type"] in ["request-based", "random-response", "random"]:
                    # ✅ 중복 방지: 사용되지 않은 값 선택
                    if field_path in available_values and available_values[field_path]:
                        values_list = available_values[field_path]
                        used_list = used_values.get(field_path, [])

                        # 사용 가능한 값 중 아직 사용하지 않은 값 찾기
                        unused_values = [v for v in values_list if v not in used_list]

                        if unused_values:
                            # 사용하지 않은 값 중 첫 번째 선택
                            selected_value = unused_values[0]
                            item[field] = selected_value
                            # 사용된 값으로 표시
                            if field_path not in used_values:
                                used_values[field_path] = []
                            used_values[field_path].append(selected_value)
                        elif values_list:
                            # ⚠️ 모든 값을 다 사용했는데 여기 도달하면 안 됨 (n이 조정되었어야 함)
                            print(f"[ERROR] {field_path}: 모든 값이 소진되었습니다. 생성 개수 조정 실패.")
                            item[field] = values_list[0]
                        else:
                            item[field] = value
                    elif constraint["values"]:
                        # fallback: constraint["values"]에서 선택
                        values_list = constraint["values"]

                        # used_values 초기화
                        if field_path not in used_values:
                            used_values[field_path] = []

                        used_list = used_values[field_path]
                        unused_values = [v for v in values_list if v not in used_list]

                        if unused_values:
                            selected_value = unused_values[0]
                            item[field] = selected_value
                            used_values[field_path].append(selected_value)
                        elif values_list:
                            # 모든 값 소진 (발생하면 안 됨)
                            print(f"[ERROR] {field_path}: 모든 값이 소진되었습니다. (fallback)")
                            item[field] = values_list[0]
                        else:
                            item[field] = value
                    else:
                        item[field] = value

                elif constraint["type"] == "request-range":
                    # 범위 내 랜덤 값 생성
                    min_val = constraint.get("min", 0)
                    max_val = constraint.get("max", 9999999999999)

                    # 유효성 검사: min이 max보다 큰 경우 처리
                    if min_val >= max_val:
                        max_val = min_val + 1000

                    # startTime/endTime 처리 (endTime은 startTime보다 커야 함)
                    if "endTime" in field and "startTime" in item:
                        item[field] = random.randint(item["startTime"] + 1, max_val)
                    else:
                        item[field] = random.randint(min_val, max_val)

            else:
                # constraint 없는 필드는 기본값 유지
                item[field] = value

        return item

    def find_key(self, data, target_key):
        """재귀적으로 데이터에서 키 찾기"""
        results = []

        if isinstance(data, dict):
            for k, v in data.items():
                if k == target_key:
                    results.append(v)
                elif isinstance(v, (dict, list)):
                    results.extend(self.find_key(v, target_key))
        elif isinstance(data, list):
            for item in data:
                results.extend(self.find_key(item, target_key))

        return results


# -----------------------
# 테스트
# -----------------------
if __name__ == "__main__":
    # latest_events 모의 데이터 생성 (Server.latest_events 형식)
    import datetime

    latest_events = {
        "/CameraProfiles": {
            "REQUEST": {
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "api": "/CameraProfiles",
                "dir": "REQUEST",
                "data": {}
            },
            "RESPONSE": {
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "api": "/CameraProfiles",
                "dir": "RESPONSE",
                "data": {
                    "code": "200",
                    "message": "성공",
                    "camList": [
                        {
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
                                "lon": "126",
                                "lat": "32",
                                "alt": "31",
                                "desc": "2층복도"
                            },
                            "camConfig": {
                                "camType": "PTZ"
                            }
                        },
                        {
                            "camID": "cam0003",
                            "camName": "카메라3",
                            "camLoc": {
                                "lon": "125",
                                "lat": "30",
                                "alt": "30",
                                "desc": "1층복도"
                            },
                            "camConfig": {
                                "camType": "FIXED"
                            }
                        }
                    ]
                }
            }
        },
        "/StreamURLs": {
            "REQUEST": {
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "api": "/StreamURLs",
                "dir": "REQUEST",
                "data": {
                    "camList": [
                        {"camID": "cam_A01"},
                        {"camID": "cam_B02"},
                        {"camID": "cam_C03"}
                    ]
                }
            },
            "RESPONSE": {
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "api": "/StreamURLs",
                "dir": "RESPONSE",
                "data": {
                    "code": "200",
                    "message": "성공",
                    "camList": [
                        {"camID": "cam_A01", "streamURL": "rtsp://..."},
                        {"camID": "cam_B02", "streamURL": "rtsp://..."},
                        {"camID": "cam_C03", "streamURL": "rtsp://..."}
                    ]
                }
            }
        },
        "/TimeRangeAPI": {
            "REQUEST": {
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "api": "/TimeRangeAPI",
                "dir": "REQUEST",
                "data": {
                    "timePeriod": {
                        "startTime": 1760948700000,
                        "endTime": 1761121500000
                    }
                }
            },
            "RESPONSE": {
                "time": datetime.datetime.utcnow().isoformat() + "Z",
                "api": "/TimeRangeAPI",
                "dir": "RESPONSE",
                "data": {}
            }
        }
    }

    generator = ConstraintDataGenerator(latest_events)

    # 테스트 1: request-based with referenceEndpoint (latest_events의 REQUEST에서)
    print("=== 테스트 1: request-based (latest_events REQUEST) ===")
    request_data1 = {}  # 빈 request

    template_data1 = {
        "camList": [
            {
                "camID": "",
                "status": "active"
            }
        ]
    }

    constraints1 = {
        "camList.camID": {
            "valueType": "request-based",
            "required": True,
            "referenceEndpoint": "/StreamURLs",
            "referenceField": "camID"
        }
    }

    result1 = generator._applied_constraints(request_data1, template_data1, constraints1, n=3)
    print(f"camList 개수: {len(result1['camList'])}")
    for i, cam in enumerate(result1['camList']):
        print(f"[{i}] camID: {cam['camID']} (latest_events의 /StreamURLs REQUEST에서 가져옴)")

    # 테스트 2: random-response with referenceEndpoint (latest_events의 RESPONSE에서)
    print("\n=== 테스트 2: random-response (latest_events RESPONSE) ===")
    request_data2 = {}

    template_data2 = {
        "selectedCamList": [
            {
                "camID": "",
                "info": "selected"
            }
        ]
    }

    constraints2 = {
        "selectedCamList.camID": {
            "valueType": "random-response",
            "required": True,
            "referenceEndpoint": "/CameraProfiles",
            "referenceField": "camID"
        }
    }

    result2 = generator._applied_constraints(request_data2, template_data2, constraints2, n=4)
    print(f"selectedCamList 개수: {len(result2['selectedCamList'])}")
    for i, cam in enumerate(result2['selectedCamList']):
        print(f"[{i}] camID: {cam['camID']} (latest_events의 /CameraProfiles RESPONSE에서 가져옴)")

    # 테스트 3: request-range with referenceEndpoint
    print("\n=== 테스트 3: request-range (latest_events REQUEST) ===")
    request_data3 = {}

    template_data3 = {
        "events": [
            {
                "eventID": "",
                "timeList": [{"startTime": 0, "endTime": 0}]
            }
        ]
    }

    constraints3 = {
        "events.timeList.startTime": {
            "valueType": "request-range",
            "required": True,
            "referenceEndpoint": "/TimeRangeAPI",
            "requestRange": {
                "operator": "between",
                "minField": "startTime",
                "maxField": "endTime"
            }
        },
        "events.timeList.endTime": {
            "valueType": "request-range",
            "required": True,
            "referenceEndpoint": "/TimeRangeAPI",
            "requestRange": {
                "operator": "between",
                "minField": "startTime",
                "maxField": "endTime"
            }
        }
    }

    result3 = generator._applied_constraints(request_data3, template_data3, constraints3, n=2)
    print(f"events 개수: {len(result3['events'])}")
    for i, event in enumerate(result3['events']):
        print(f"[{i}] timeList: {len(event['timeList'])}개")
        for j, time in enumerate(event['timeList'][:2]):
            print(f"    [{j}] startTime: {time['startTime']}, endTime: {time['endTime']}")

    print("\n=== latest_events 확인 ===")
    print(f"저장된 API 목록: {list(latest_events.keys())}")
    print(
        f"/CameraProfiles RESPONSE의 camID들: {[c['camID'] for c in latest_events['/CameraProfiles']['RESPONSE']['data']['camList']]}")
    print(
        f"/StreamURLs REQUEST의 camID들: {[c['camID'] for c in latest_events['/StreamURLs']['REQUEST']['data']['camList']]}")