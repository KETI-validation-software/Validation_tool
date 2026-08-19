import random
import copy
import config.CONSTANTS as CONSTANTS
from core.logger import Logger

class ConstraintDataGenerator:
    # 상수 정의
    MAX_TIMESTAMP = 9999999999999  # 최대 타임스탬프 범위
    INVALID_TIMESTAMP = 0  # 오류 생성용 타임스탬프
    
    def __init__(self, latest_events=None):
        """
        latest_events: API 이벤트 저장소 {api_name: {direction: event_data}}
        """
        self.latest_events = latest_events if latest_events is not None else {}

    def _find_requested_ids(self, constraints, field, default_endpoint):
        """앞서 보낸 요청(구독/조회)에서 해당 필드의 ID 후보를 찾는다.

        제약에 referenceEndpoint가 있으면 그 API를, 없으면 default_endpoint의
        REQUEST 기록(latest_events)을 본다. 기록이 없으면 빈 목록(폴백은 호출부).
        """
        rule = next(
            (r for k, r in (constraints or {}).items()
             if field in k and isinstance(r, dict) and r.get("referenceEndpoint")),
            None,
        )
        ref_key = rule["referenceEndpoint"].lstrip("/") if rule else default_endpoint
        for key in (ref_key, f"/{ref_key}"):
            event = self.latest_events.get(key, {}).get("REQUEST") or {}
            ids = [v for v in self.find_key(event.get("data") or {}, field) if v]
            if ids:
                return ids
        return []

    def _find_reference_state(self, constraints, field, item_id, id_field):
        """수신한 이벤트에서 특정 항목의 현재 상태를 찾는다.

        제약에 적힌 referenceEndpoint / referenceField를 그대로 따라간다.
        (예: DoorControl.commandType → /RealtimeDoorStatus 의 doorSensor)
        """
        rule = next(
            (r for k, r in (constraints or {}).items()
             if field in k and isinstance(r, dict) and r.get("referenceEndpoint")),
            None,
        )
        if not rule or not item_id:
            return None

        ref_key = rule["referenceEndpoint"].lstrip("/")
        ref_field = rule.get("referenceField")
        if not ref_field or ref_field == "(참조 필드 미선택)":
            return None

        # 상태는 응답이 아니라 웹훅 이벤트로 오므로 이벤트를 먼저 본다
        for key in (ref_key, f"/{ref_key}"):
            for direction in ("WEBHOOK", "WEBHOOK_OUT", "RESPONSE", "REQUEST"):
                event = self.latest_events.get(key, {}).get(direction) or {}
                data = event.get("data") or {}
                for values in data.values():
                    if not isinstance(values, list):
                        continue
                    for item in values:
                        if not isinstance(item, dict):
                            continue
                        if item.get(id_field) == item_id and item.get(ref_field):
                            return item[ref_field]
        return None

    @staticmethod
    def _to_number(value, default):
        """문자열 시각값("20251105163010124")을 숫자로. 변환 불가 시 default."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _filter_rows_by_request(self, rows, request_data, id_field):
        """조회 응답에서 요청 조건에 해당하는 줄만 남긴다.

        저장된 기록(템플릿 줄)을 그대로 두고 걸러내기만 한다. 값을 바꾸거나 줄을 늘리지 않는다.
        템플릿 줄의 ID가 비어 있으면 요청 개수만큼 채워 쓰는 구조이므로 걸러내지 않는다.
        """
        if not isinstance(rows, list) or not rows:
            return rows

        requested = [v for v in (self.find_key(request_data, id_field) or []) if v]
        if not requested:
            # 조회 조건이 없는 API(DoorProfiles 등)는 전체를 그대로 응답한다
            return rows

        if not all(isinstance(r, dict) and r.get(id_field) for r in rows):
            return rows

        filtered = [r for r in rows if r.get(id_field) in requested]
        Logger.info(f"[DATA_MAPPER] 조회 조건 적용: {len(rows)}건 중 {len(filtered)}건 응답 (요청 {id_field}: {requested})")
        return filtered

    def _applied_constraints(self, request_data, template_data, constraints, api_name=None, door_memory=None, is_webhook=False):
        """
        request_data: 요청 데이터 (camID 후보 등)
        template_data: request 또는 response 템플릿
        constraints: 제약 조건
        api_name: API 이름 (RealtimeDoorStatus2 등)
        door_memory: 문 상태 저장소
        is_webhook: 웹훅 이벤트 생성 여부 (True이면 랜덤 선택 안함)
        """
        # ✅ sensorDeviceList 구조를 가진 웹훅 데이터 동적 생성 (범용)
        if is_webhook and "sensorDeviceList" in template_data:
            # request_data에서 요청한 sensorDeviceID 추출
            requested_ids = self.find_key(request_data, "sensorDeviceID")
            
            # sensorDeviceID가 요청에 있고, 템플릿에 sensorDeviceList가 있으면 처리
            if requested_ids and isinstance(template_data["sensorDeviceList"], list) and len(template_data["sensorDeviceList"]) > 0:
                Logger.info(f"[DATA_MAPPER] sensorDeviceList 웹훅 데이터 동적 생성 시작 (API: {api_name})")
                Logger.debug(f"[DATA_MAPPER] 요청한 sensorDeviceID: {requested_ids}")
                
                # 템플릿의 첫 번째 항목을 기준으로 허용 키 확인
                allowed_keys = set(template_data["sensorDeviceList"][0].keys())
                Logger.debug(f" 템플릿 구조 기반 허용 키: {allowed_keys}")
                
                # 요청한 ID만 포함하도록 필터링
                new_sensor_list = []
                for sensor_id in requested_ids:
                    # 템플릿에서 해당 ID를 가진 항목 찾기
                    matching_item = None
                    for item in template_data["sensorDeviceList"]:
                        if item.get("sensorDeviceID") == sensor_id:
                            matching_item = item
                            break
                    
                    # 매칭 항목이 있으면 사용, 없으면 템플릿 첫 항목 복사 후 ID만 변경
                    if matching_item:
                        filtered_item = {k: v for k, v in matching_item.items() if k in allowed_keys}
                    else:
                        # 템플릿 첫 번째 항목 복사
                        template_item = template_data["sensorDeviceList"][0]
                        filtered_item = {k: v for k, v in template_item.items() if k in allowed_keys}
                        # ID만 요청한 값으로 변경
                        filtered_item["sensorDeviceID"] = sensor_id
                    
                    new_sensor_list.append(filtered_item)
                
                template_data["sensorDeviceList"] = new_sensor_list
                Logger.info(f"[DATA_MAPPER] 생성된 sensorDeviceList: {len(new_sensor_list)}개")
                Logger.debug(f"[DATA_MAPPER] 상세: {new_sensor_list}")
            
            return template_data
        
        # ✅ doorList 구조를 가진 데이터 동적 생성 (범용)
        if "doorList" in template_data:
            is_response_template = "code" in template_data
            
            if is_webhook:
                requested_ids = self.find_key(request_data, "doorID")
                
                # doorID가 요청에 있고, 템플릿에 doorList가 있으면 처리
                if requested_ids and isinstance(template_data["doorList"], list) and len(template_data["doorList"]) > 0:
                    Logger.info(f"[DATA_MAPPER] doorList 웹훅 데이터 동적 생성 시작 (API: {api_name})")
                    Logger.debug(f"[DATA_MAPPER] 요청한 doorID: {requested_ids}")
                    
                    new_door_list = []
                    allowed_keys = set(template_data["doorList"][0].keys())
                    Logger.debug(f"[DATA_MAPPER] 템플릿 구조 기반 허용 키: {allowed_keys}")
                    
                    for door_id in requested_ids:
                        # 템플릿에서 해당 ID를 가진 항목 찾기
                        matching_item = None
                        for item in template_data["doorList"]:
                            if item.get("doorID") == door_id:
                                matching_item = item
                                break
                        
                        # 매칭 항목이 있으면 사용, 없으면 템플릿 첫 항목 복사 후 ID만 변경
                        if matching_item:
                            filtered_item = {k: v for k, v in matching_item.items() if k in allowed_keys}
                        else:
                            # 템플릿 첫 번째 항목 복사 (door_memory 활용)
                            template_item = template_data["doorList"][0]
                            filtered_item = {k: v for k, v in template_item.items() if k in allowed_keys}
                            # ID만 요청한 값으로 변경
                            filtered_item["doorID"] = door_id
                            
                            # door_memory가 있으면 추가 정보 업데이트
                            if door_memory and door_id in door_memory:
                                raw_info = door_memory[door_id]
                                for key in allowed_keys:
                                    if key != "doorID" and key in raw_info:
                                        filtered_item[key] = raw_info[key]
                        
                        new_door_list.append(filtered_item)
                    
                    template_data["doorList"] = new_door_list
                    Logger.debug(f" 생성된 doorList ({len(new_door_list)}개): {new_door_list}")
                
                return template_data


            if not is_webhook and not is_response_template:
                Logger.info(f"[DATA_MAPPER] doorList REQUEST 데이터 동적 생성 시작 (API: {api_name})")
                
                # ✅ constraints에서 doorID의 referenceEndpoint와 valueType을 동적으로 찾기
                ref_endpoint = None
                value_type = None
                if constraints:
                    for field_path, rule in constraints.items():
                        if "doorID" in field_path and isinstance(rule, dict):
                            ref_endpoint = rule.get("referenceEndpoint")
                            value_type = rule.get("valueType")
                            if ref_endpoint:
                                Logger.debug(f"[DATA_MAPPER] doorID의 referenceEndpoint 발견: {ref_endpoint}, valueType: {value_type}")
                                break
                
                # referenceEndpoint가 없으면 기본값 사용
                if not ref_endpoint:
                    ref_endpoint = "DoorProfiles"
                    Logger.debug(f"[DATA_MAPPER] referenceEndpoint 없음 - 기본값 사용: {ref_endpoint}")
                
                # 슬래시 제거 및 검색 키 생성
                ref_endpoint_clean = ref_endpoint.lstrip("/")
                keys_to_search = [ref_endpoint_clean, f"/{ref_endpoint_clean}"]
                
                Logger.debug(f"[DATA_MAPPER] latest_events 키 목록: {list(self.latest_events.keys())}")
                Logger.debug(f"[DATA_MAPPER] 검색할 키: {keys_to_search}")
                
                # valueType에 따라 REQUEST 또는 RESPONSE에서 가져오기
                direction = "REQUEST" if value_type == "request-based" else "RESPONSE"
                Logger.debug(f"[DATA_MAPPER] valueType={value_type} → {direction}에서 데이터 조회")
                
                # latest_events에서 참조 API 데이터 찾기
                door_profiles_data = None
                for key in keys_to_search:
                    if key in self.latest_events and direction in self.latest_events[key]:
                        door_profiles_data = self.latest_events[key][direction].get("data", {})
                        Logger.info(f"[DATA_MAPPER] latest_events에서 {key} {direction} 발견!")
                        Logger.debug(f"[DATA_MAPPER] door_profiles_data: {door_profiles_data}")
                        break
                
                if not door_profiles_data:
                    Logger.warn(f"[DATA_MAPPER] ⚠️ latest_events에서 {ref_endpoint} {direction}를 찾을 수 없음!")
                
                # 찾은 데이터에서 doorID 추출하여 리스트 생성
                new_door_list = []
                
                # DoorControl REQUEST처럼 doorList가 아닌 단일 doorID인 경우 처리
                if door_profiles_data and "doorID" in door_profiles_data and "doorList" not in door_profiles_data:
                    door_id = door_profiles_data.get("doorID")
                    if door_id:
                        new_door_list.append({"doorID": door_id})
                        Logger.info(f"[DATA_MAPPER] ✅ {ref_endpoint}에서 단일 doorID 추출: {door_id}")
                # doorList 배열인 경우 처리
                elif door_profiles_data and "doorList" in door_profiles_data:
                    Logger.debug(f"[DATA_MAPPER] door_profiles_data에 doorList 발견, 개수: {len(door_profiles_data.get('doorList', []))}")
                    all_door_ids = []
                    for profile in door_profiles_data.get("doorList", []):
                        door_id = profile.get("doorID")
                        if door_id:
                            all_door_ids.append(door_id)
                    
                    # valueType이 response-based면 랜덤 선택
                    if value_type == "response-based" and all_door_ids:
                        original_count = len(all_door_ids)
                        random_count = random.randint(1, len(all_door_ids))
                        selected_ids = random.sample(all_door_ids, random_count)
                        Logger.info(f"[DATA_MAPPER] response-based: {original_count}개 중 {random_count}개 랜덤 선택")
                        for door_id in selected_ids:
                            new_door_list.append({"doorID": door_id})
                            Logger.debug(f"[DATA_MAPPER] doorID 추가: {door_id}")
                    else:
                        # request-based 또는 valueType 없으면 전체 사용
                        for door_id in all_door_ids:
                            new_door_list.append({"doorID": door_id})
                            Logger.debug(f"[DATA_MAPPER] doorID 추가: {door_id}")
                    
                    Logger.info(f"[DATA_MAPPER] ✅ {ref_endpoint}에서 {len(new_door_list)}개의 doorID 추출 완료")
                elif door_profiles_data:
                    Logger.warning(f"[DATA_MAPPER] ⚠️ door_profiles_data에 doorList 없음!")
                    Logger.info(f"[DATA_MAPPER] ✅ DoorProfiles에서 {len(new_door_list)}개의 doorID 추출 완료")
                elif door_profiles_data:
                    Logger.warning(f"[DATA_MAPPER] ⚠️ door_profiles_data에 doorList 없음!")
                
                # 만약 DoorProfiles가 없으면(단독 실행 등), 템플릿 기반으로 생성
                if not new_door_list:
                    Logger.warn(f"[DATA_MAPPER] ⚠️ DoorProfiles에서 doorID를 가져오지 못함, 템플릿 기반으로 생성 시도")
                    # 템플릿의 doorList에서 구조 가져오기
                    if "doorList" in template_data and isinstance(template_data["doorList"], list) and len(template_data["doorList"]) > 0:
                        template_item = template_data["doorList"][0]
                        # doorID만 추출하여 리스트 생성 (템플릿에 있는 doorID 사용)
                        for item in template_data["doorList"]:
                            door_id = item.get("doorID", "")
                            if door_id:
                                new_door_list.append({"doorID": door_id})
                                Logger.debug(f"[DATA_MAPPER] 템플릿에서 doorID 추가: {door_id}")
                        Logger.info(f"[DATA_MAPPER] 템플릿에서 {len(new_door_list)}개의 doorID 생성")
                    else:
                        Logger.error(f"[DATA_MAPPER] ❌ 템플릿에도 doorList가 없거나 비어있음!")

                Logger.info(f"[DATA_MAPPER] 최종 doorList 설정: {len(new_door_list)}개 항목")
                template_data["doorList"] = new_door_list
                return template_data

            # 조회 응답: 저장된 기록 중 요청 조건에 해당하는 줄만 남긴다.
            # 걸러낸 뒤에는 아래 공통 경로로 내려가 값 채우기 설정(eventName 등)이 적용된다.
            template_data["doorList"] = self._filter_rows_by_request(
                template_data["doorList"], request_data, "doorID"
            )
        
        # ✅ commandType 구조를 가진 데이터 동적 생성 (범용 - DoorControl 등)
        if "commandType" in template_data and "doorID" in template_data:
            Logger.debug(f" commandType 데이터 동적 생성 시작 (API: {api_name})")

            # doorID 추출
            target_door_id = None
            if request_data and "doorID" in request_data:
                target_door_id = request_data["doorID"]
            elif door_memory and len(door_memory) > 0:
                target_door_id = random.choice(list(door_memory.keys()))
            else:
                # 플랫폼 역할: 앞서 보낸 상태조회(구독) 요청에서 구독한 문 중 하나를 고른다.
                # 구독은 무작위 부분집합인데 제어가 템플릿 고정값(door0001)이면
                # "구독하지 않은 문을 제어"하게 되어 맥락 검증에서 확률적으로 실패한다.
                subscribed = self._find_requested_ids(constraints, "doorID", "RealtimeDoorStatus")
                if subscribed:
                    target_door_id = random.choice(subscribed)
                    Logger.debug(f" 구독한 문 중에서 선택: {target_door_id} (후보: {subscribed})")
                else:
                    # 템플릿 기본값 사용 (템플릿에 이미 있는 값 그대로)
                    target_door_id = template_data.get("doorID", "")
            
            template_data["doorID"] = target_door_id
            Logger.debug(f" 선택된 doorID: {target_door_id}")

            # 현재 상태 가져오기
            current_status = template_data.get("commandType", "")  # 템플릿 기본값 사용
            if door_memory and target_door_id in door_memory:
                current_status = door_memory[target_door_id].get("doorSensor", current_status)
            else:
                # door_memory는 우리가 장치 역할일 때만 채워진다.
                # 플랫폼 역할(단일시스템 시험)에서는 비어 있으므로 수신한 상태 이벤트에서 찾는다.
                found = self._find_reference_state(constraints, "commandType", target_door_id, "doorID")
                if found:
                    current_status = found
                    Logger.debug(f" 수신 이벤트에서 {target_door_id} 현재 상태 확인: {found}")
            
            # constraints에서 후보값 추출
            # 제약은 validValues, 검증 규칙은 allowedValues로 이름이 다르므로 둘 다 인정한다
            allowed_values = []
            if constraints:
                for key, rule in constraints.items():
                    if "commandType" not in key or not isinstance(rule, dict):
                        continue
                    allowed_values = rule.get("validValues") or rule.get("allowedValues") or []
                    if allowed_values:
                        Logger.debug(f" constraints에서 후보값 발견: {allowed_values}")
                        break
            
            # 현재 상태와 다른 명령어 선택 (토글)
            if allowed_values:
                candidates = [
                    val for val in allowed_values
                    if str(val).lower() != str(current_status).lower()
                ]
                
                if candidates:
                    command = random.choice(candidates)
                else:
                    command = random.choice(allowed_values)
                
                template_data["commandType"] = command
                Logger.debug(f" 생성된 commandType: {command} (현재 상태: {current_status})")
            else:
                # constraints가 없으면 템플릿 기본값 유지
                Logger.debug(f" constraints 없음 - 템플릿 기본값 유지: {template_data['commandType']}")
            return template_data


        constraint_map = self._build_constraint_map(constraints, request_data, is_webhook)
        response = self._generate_from_template(template_data, constraint_map)
        template_data.update(response)
        return template_data

    # 기대 코드별 기본 주입 방법.
    # 400은 유도 방법이 셋(②누락·③자료형·④유효값)이라 기대 코드만으로는 정할 수 없다.
    # 관리도구가 주입 방법을 내려주게 되면 _applied_codevalue(method=...)로 연결하면 되고,
    # 그 전까지는 기존 동작(자료형 불일치)을 기본으로 둔다.
    DEFAULT_INJECTION = {
        "201": "start-time",       # ① 저장 조회 구간 밖
        "400": "type-mismatch",    # ③ 자료형 불일치
        "404": "unknown-device",   # ⑦ 미등록 장치 ID
        # "403"은 요청 본문이 아니라 헤더/경로를 건드리므로 여기서 처리하지 않는다
    }

    def _applied_codevalue(self, request_data, allowed_value, constraints=None,
                           include_optional=True, method=None):
        """오류 유도 — 기대 코드(또는 명시된 method)에 맞춰 요청을 변조한다.

        Args:
            allowed_value: 관리도구가 내려준 응답 code 기대값("201"/"400"/"404" 등)
            constraints: 해당 API의 요청 제약. 필수/선택 판정과 허용 값 목록이 들어 있다
            include_optional: 시험범위. False면 필수 범위 — 선택 필드는 주입하지 않는다
            method: 주입 방법을 직접 지정할 때 사용. 없으면 DEFAULT_INJECTION을 따른다
        """
        if not getattr(CONSTANTS, "ENABLE_ERROR_REQUEST_MUTATION", False):
            return request_data

        method = method or self.DEFAULT_INJECTION.get(str(allowed_value))

        if method == "start-time":
            return self.replace_start_time(request_data)
        if method == "missing-required":
            return self.remove_required_field(request_data, constraints)[0]
        if method == "type-mismatch":
            return self.change_random_field_type(request_data, constraints, include_optional)
        if method == "invalid-value":
            return self.violate_valid_value(request_data, constraints, include_optional)[0]
        if method == "unknown-device":
            return self.use_unknown_device_id(request_data)[0]

        # 기대 코드가 200이거나 본문 변조 대상이 아닌 경우(403 등)는 그대로 보낸다.
        # (예전에는 여기서 지역변수 미할당으로 예외가 나고 바깥 except가 삼켰다)
        return request_data

    def _build_constraint_map(self, constraints, request_data, is_webhook=False):
        """constraints를 분석하여 각 필드의 제약 조건과 참조 값을 매핑"""
        constraint_map = {}

        Logger.debug(f"[BUILD_MAP] constraints: {constraints}")
        Logger.debug(f"[BUILD_MAP] request_data: {request_data}")
        Logger.debug(f"[BUILD_MAP] 🔍 self.latest_events 키 목록: {list(self.latest_events.keys())}")
        Logger.debug(f"[BUILD_MAP] 🔍 self.latest_events 전체: {self.latest_events}")

        for path, rule in constraints.items():
            Logger.debug(f"[BUILD_MAP] Processing path: {path}, rule: {rule}")

            value_type = rule.get("valueType")
            ref_endpoint = rule.get("referenceEndpoint")
            ref_field = rule.get("referenceField")

            Logger.debug(f"[BUILD_MAP]   valueType: {value_type}")
            Logger.debug(f"[BUILD_MAP]   referenceEndpoint: {ref_endpoint}")
            Logger.debug(f"[BUILD_MAP]   referenceField: {ref_field}")

            # valueType이 "random"이고 randomType이 있으면 아래에서 별도 처리
            random_type = rule.get("randomType")
            
            # referenceEndpoint가 있으면 latest_events에서 데이터 찾기
            # 단, referenceField가 "(참조 필드 미선택)"이면 참조 안 함
            # 단, valueType이 "random"이고 randomType이 있으면 건너뜀 (아래에서 처리)
            if ref_endpoint and ref_field and ref_field != "(참조 필드 미선택)" and not (value_type == "random" and random_type):
                values = []

                # referenceEndpoint의 슬래시 처리 (있든 없든 찾을 수 있도록)
                # 예: "/StoredVideoEventInfos" → "StoredVideoEventInfos"
                ref_key = ref_endpoint.lstrip('/')

                Logger.debug(f"[BUILD_MAP]   Searching for ref_key: {ref_key}")

                if ref_key in self.latest_events:
                    Logger.debug(f"[BUILD_MAP]   Found referenceEndpoint in latest_events")
                    # valueType에 따라 REQUEST 또는 RESPONSE에서 가져오기
                    if value_type == "request-based":
                        event = self.latest_events[ref_key].get("REQUEST", {})
                        Logger.debug(f"[BUILD_MAP]   Using REQUEST event")
                    else:  # random-response 등 다른 타입
                        event = self.latest_events[ref_key].get("RESPONSE", {})
                        Logger.debug(f"[BUILD_MAP]   Using RESPONSE event")

                    event_data = event.get("data", {})
                    Logger.debug(f"[BUILD_MAP]   event_data: {event_data}")
                    values = self.find_key(event_data, ref_field)
                    Logger.debug(f"[BUILD_MAP]   Found values from event: {values}")
                    
                    # response-based(시스템 요청)만 랜덤 선택, request-based(플랫폼 응답/웹훅)는 그대로 사용 (01/08)
                    if value_type == "response-based" and not is_webhook and values and len(values) > 0:
                        original_count = len(values)
                        random_count = random.randint(1, len(values))
                        values = random.sample(values, random_count)
                        Logger.debug(f"[BUILD_MAP]   Random selection: {random_count}/{original_count} items selected (시스템 요청)")
                    else:
                        Logger.debug(f"[BUILD_MAP]   랜덤 선택 안함 (valueType={value_type}, is_webhook={is_webhook}), 전체 사용: {len(values)}개")
                else:
                    Logger.debug(f"[BUILD_MAP]   referenceEndpoint NOT found in latest_events")
                    Logger.debug(f"[BUILD_MAP]   Available endpoints: {list(self.latest_events.keys())}")

                constraint_map[path] = {
                    "type": value_type,
                    "values": values if values else []
                }

            elif value_type == "request-based":
                # referenceEndpoint 없으면 현재 request_data에서 찾기
                Logger.debug(f"[BUILD_MAP]   Searching in current request_data")
                values = self.find_key(request_data, ref_field)
                Logger.debug(f"[BUILD_MAP]   Found values from request: {values}")
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
                random_type = rule.get("randomType")  # exclude-reference-valid-values 등
                
                # exclude-reference-valid-values: 참조 필드 값 제외
                if random_type == "exclude-reference-valid-values":
                    ref_key = ref_endpoint.lstrip('/') if ref_endpoint else None
                    
                    Logger.debug(f"[BUILD_MAP]   randomType: exclude-reference-valid-values")
                    Logger.debug(f"[BUILD_MAP]   ref_key: {ref_key}")
                    
                    if ref_key and ref_key in self.latest_events:
                        # RESPONSE에서 참조 필드 값 가져오기
                        event = self.latest_events[ref_key].get("RESPONSE", {})
                        event_data = event.get("data", {})
                        reference_values = self.find_key(event_data, ref_field)
                        
                        Logger.debug(f"[BUILD_MAP]   reference_values from RESPONSE: {reference_values}")
                        Logger.debug(f"[BUILD_MAP]   validValues before exclude: {valid_values}")
                        
                        # 참조 값을 제외한 validValues 필터링
                        if reference_values:
                            filtered_values = [v for v in valid_values if v not in reference_values]
                            valid_values = filtered_values if filtered_values else valid_values
                        
                        Logger.debug(f"[BUILD_MAP]   validValues after exclude: {valid_values}")
                
                constraint_map[path] = {
                    "type": "random",
                    "values": valid_values
                }

            elif value_type == "request-range":
                # 범위 제약 조건 처리
                req_range = rule.get("requestRange", {})
                operator = req_range.get("operator")
                min_field = req_range.get("minField")
                max_field = req_range.get("maxField")
                if min_field != None and max_field != None:
                    operator = "between"
                Logger.debug(f"[BUILD_MAP]   request-range operator: {operator}")
                if operator == "between":
                    ref_endpoint = req_range.get("maxEndpoint")

                    min_field = req_range.get("minField")
                    max_field = req_range.get("maxField")
                    min_endpoint = req_range.get("minEndpoint")
                    max_endpoint = req_range.get("maxEndpoint")

                    # referenceEndpoint 또는 minEndpoint/maxEndpoint 처리
                    ref_key_min = (min_endpoint or ref_endpoint or "").lstrip('/')
                    ref_key_max = (max_endpoint or ref_endpoint or "").lstrip('/')

                    min_val = 0
                    max_val = self.MAX_TIMESTAMP

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
                        max_val = max_vals[0] if max_vals else self.MAX_TIMESTAMP

                    Logger.debug(f"[BUILD_MAP]   request-range: min={min_val}, max={max_val}")

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
                    max_val = self.MAX_TIMESTAMP

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
                        max_val = max_vals[0] if max_vals else self.MAX_TIMESTAMP

                    Logger.debug(f"[BUILD_MAP]   request-range: min={min_val}, max={max_val}")

                    constraint_map[path] = {
                        "type": "request-range",
                        "operator": operator,
                        "min": min_val,
                        "max": max_val
                    }
                else:
                    # 기본 범위 (operator 없거나 알 수 없는 경우)
                    Logger.debug(f"[BUILD_MAP]   Unknown operator: {operator}, using default range")
                    constraint_map[path] = {
                        "type": "request-range",
                        "operator": "between",
                        "min": 0,
                        "max": self.MAX_TIMESTAMP
                    }
            elif value_type == "response-based":
                # referenceEndpoint 없으면 현재 request_data에서 찾기
                Logger.debug(f"[BUILD_MAP]   Searching in current request_data")
                values = self.find_key(request_data, ref_field)
                Logger.debug(f"[BUILD_MAP]   Found values from request: {values}")
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

    def _generate_from_template(self, template, constraint_map):
        """템플릿을 재귀적으로 순회하며 데이터 생성 (템플릿 구조 유지)"""
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
                # ✅ 템플릿의 리스트 길이 자동 감지
                n = len(value)
                
                # ✅ constraints가 없으면 원본 리스트를 그대로 사용
                has_constraints = any(f"{key}.{field}" in constraint_map for field in value[0].keys())
                
                if not has_constraints:
                    # constraints가 없으면 원본 리스트 그대로 사용 (preset)
                    result[key] = value
                elif n > 1:
                    # 등록된 줄이 여럿이면 줄별로 채운다.
                    # 첫 줄만 본으로 삼아 n개를 찍어내면 2번째 이후 줄(카메라2, door0002 등)이
                    # 사라지고 첫 줄이 복제된다.
                    result[key] = [
                        self._generate_list_items(key, row, constraint_map, 1)[0]
                        for row in value
                    ]
                else:
                    # 줄이 하나면 요청 개수만큼 늘리는 기존 방식 (영상 계열 등)
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
                elif constraint["type"] in ["request-based", "random-response", "random",
                                            "response-based"]:  # ← response-based 추가
                    if constraint["values"]:
                        available_values[field_path] = constraint["values"].copy()
                        used_values[field_path] = []

                        # 최소 값 개수 추적
                        min_available_count = min(min_available_count, len(constraint["values"]))

        # ✅ 랜덤한 개수 생성 -> 가능한 최대 개수로 고정 (참조 데이터 누락 방지)
        if min_available_count != float('inf'):
            n = min_available_count
            Logger.info(f" {parent_key}: {n}개 생성합니다. (참조 데이터 개수 일치)")

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
                elif constraint["type"] in ["request-based", "random-response", "random",
                                            "response-based"]:  # ← response-based 추가
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
                            Logger.error(f" {field_path}: 모든 값이 소진되었습니다. 생성 개수 조정 실패.")
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
                            Logger.error(f" {field_path}: 모든 값이 소진되었습니다. (fallback)")
                            item[field] = values_list[0]
                        else:
                            item[field] = value
                    else:
                        item[field] = value

                elif constraint["type"] == "request-range":
                    # 범위 내 랜덤 값 생성
                    # ✅ 17자리 시각 필드가 String으로 전환되어 min/max가 문자열로 올 수 있다.
                    #    내부에서는 숫자로 변환해 비교·생성하고, 원본이 문자열이면 문자열로 내보낸다.
                    raw_min = constraint.get("min", 0)
                    raw_max = constraint.get("max", self.MAX_TIMESTAMP)
                    min_val = self._to_number(raw_min, 0)
                    max_val = self._to_number(raw_max, self.MAX_TIMESTAMP)

                    # 참조 부재 판단: 요청에 기준 필드가 없으면 min이 기본값 0으로
                    # 떨어진다(실제 시각은 0일 수 없음). 이때만 템플릿을 대타로 쓴다.
                    reference_missing = min_val == 0 and not isinstance(raw_min, str)

                    # 출력 타입: 참조값이 있으면 참조의 타입을 따르고(기존 동작),
                    # 참조가 없으면 템플릿 값(관리도구의 예시 데이터) 타입을 따른다.
                    # — 요청이 선택 필드 startTime을 생략해도 String 설정이 유지되도록.
                    as_string = (isinstance(raw_min, str) or isinstance(raw_max, str)
                                 or (reference_missing and isinstance(value, str)))

                    # 참조가 없으면 범위가 0~13자리 난수가 돼 시각으로서 무의미하다.
                    # 템플릿에 시각 값이 있으면 그 근방을 기준으로 삼는다.
                    if reference_missing:
                        template_num = self._to_number(value, 0)
                        if template_num > 0:
                            min_val = template_num

                    # 유효성 검사: min이 max보다 큰 경우 처리
                    if min_val >= max_val:
                        max_val = min_val + 1000

                    # startTime/endTime 처리 (endTime은 startTime보다 커야 함)
                    if "endTime" in field and "startTime" in item:
                        start_num = self._to_number(item["startTime"], min_val)
                        generated = random.randint(start_num + 1, max(max_val, start_num + 2))
                    else:
                        generated = random.randint(min_val, max_val)

                    item[field] = str(generated) if as_string else generated

            else:
                # constraint 없는 필드는 기본값 유지
                item[field] = value

        return item

    # ========== 오류 주입(유도) ==========
    # 시험 기준(2026-08-16 "오류 처리 케이스 정리")의 주입 방법과 1:1로 맞춘다.
    #   ① 저장 조회 구간 밖  → 201 : replace_start_time
    #   ② 필수 필드 누락     → 400 : remove_required_field
    #   ③ 자료형 불일치      → 400 : change_random_field_type
    #   ④ 유효 값 위반       → 400 : violate_valid_value
    #   ⑤ 토큰 미포함        → 403 : 전송 계층(systemVal_all.post)에서 헤더 제거
    #   ⑥ 접근 불가 URL      → 403 : 미구현 — 절차서에 경로 기준이 확정돼야 함
    #   ⑦ 미등록 장치 ID     → 404 : use_unknown_device_id
    #
    # 필수/선택 판정과 허용 값 목록은 전부 관리도구가 내려주는 제약(constraints)에
    # 이미 들어 있다("required": True/False, "validValues": [...]). 별도 스키마 해석 불필요.

    # 미등록 장치로 바꿀 때 쓰는 ID (시험 기준 예시와 동일)
    UNKNOWN_DEVICE_IDS = {
        "camID": "cam9999",
        "doorID": "door9999",
        "sensorDeviceID": "iot9999",
    }

    @staticmethod
    def _leaf_constraints(constraints, include_optional=True):
        """제약에서 잎 경로만 (경로, 규칙)으로 돌려준다.

        제약에는 "doorList"(컨테이너)와 "doorList.doorID"(잎)가 함께 들어 있다.
        컨테이너를 지우면 하위가 통째로 날아가 주입 의도가 흐려지므로 잎만 쓴다.
        include_optional=False는 필수 범위 시험 — 선택 필드는 주입 대상이 아니다.
        """
        items = [(p, r) for p, r in (constraints or {}).items() if isinstance(r, dict)]
        all_paths = [p for p, _ in items]
        result = []
        for path, rule in items:
            if any(other.startswith(path + ".") for other in all_paths):
                continue  # 하위를 가진 컨테이너는 건너뛴다
            if not include_optional and not rule.get("required"):
                continue
            result.append((path, rule))
        return result

    @staticmethod
    def _resolve_targets(data, dotted_path):
        """점 표기 경로가 실제로 가리키는 (부모 dict, 키) 목록.

        중간에 리스트가 있으면 원소마다 펼친다 (doorList.doorID → 모든 줄의 doorID).
        """
        nodes = [data]
        parts = dotted_path.split(".")
        for part in parts[:-1]:
            next_nodes = []
            for node in nodes:
                if isinstance(node, dict) and part in node:
                    value = node[part]
                    next_nodes.extend(value if isinstance(value, list) else [value])
            nodes = next_nodes
        last = parts[-1]
        return [(n, last) for n in nodes if isinstance(n, dict) and last in n]

    def remove_required_field(self, data, constraints):
        """② 필수 필드 누락 → 400. 첫 번째 필수 잎 필드를 요청에서 지운다."""
        new_data = copy.deepcopy(data)
        for path, _rule in self._leaf_constraints(constraints, include_optional=False):
            targets = self._resolve_targets(new_data, path)
            if not targets:
                continue
            for container, key in targets:
                container.pop(key, None)
            Logger.debug(f"[오류주입] ② 필수 필드 누락: {path}")
            return new_data, path
        Logger.debug("[오류주입] ② 제거할 필수 필드를 찾지 못함 — 원본 유지")
        return new_data, None

    def violate_valid_value(self, data, constraints, include_optional=True):
        """④ 유효 값 위반 → 400. 허용 값 목록이 있는 필드에 목록 밖 값을 넣는다."""
        new_data = copy.deepcopy(data)
        for path, rule in self._leaf_constraints(constraints, include_optional):
            allowed = rule.get("validValues") or rule.get("allowedValues")
            if not allowed:
                continue
            targets = self._resolve_targets(new_data, path)
            if not targets:
                continue
            bad_value = "INVALID_VALUE"
            while bad_value in allowed:
                bad_value += "_X"  # 허용 목록과 겹치지 않을 때까지
            for container, key in targets:
                container[key] = bad_value
            Logger.debug(f"[오류주입] ④ 유효 값 위반: {path} → {bad_value} (허용: {allowed})")
            return new_data, path
        Logger.debug("[오류주입] ④ 허용 값 목록이 있는 필드를 찾지 못함 — 원본 유지")
        return new_data, None

    def use_unknown_device_id(self, data):
        """⑦ 미등록 장치 ID → 404. 장치 ID를 목록에 없는 값으로 바꾼다."""
        new_data = copy.deepcopy(data)
        changed = []

        def traverse(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in self.UNKNOWN_DEVICE_IDS and isinstance(value, str):
                        obj[key] = self.UNKNOWN_DEVICE_IDS[key]
                        changed.append(key)
                    else:
                        traverse(value)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)

        traverse(new_data)
        Logger.debug(f"[오류주입] ⑦ 미등록 장치 ID: {changed or '대상 없음 — 원본 유지'}")
        return new_data, (changed[0] if changed else None)

    def change_random_field_type(self, data, constraints=None, include_optional=True):
        """③ 자료형 불일치 → 400. 잎 하나를 골라 타입만 바꾼다.

        필수 범위 시험(include_optional=False)에서는 선택 필드를 건드리면 안 되므로
        제약의 required=True인 경로만 후보로 남긴다.
        """
        new_data = copy.deepcopy(data)
        leaf_paths = []

        # 1️⃣ leaf 경로 수집
        def collect(data, path):
            if isinstance(data, dict):
                for k, v in data.items():
                    collect(v, path + [k])
            elif isinstance(data, list):
                for i, v in enumerate(data):
                    collect(v, path + [i])
            else:
                leaf_paths.append(path)

        collect(new_data, [])

        # 1️⃣-2 범위 제한 — 필수 범위면 필수 필드만 후보로 남긴다
        if constraints and not include_optional:
            required_paths = {p for p, _ in self._leaf_constraints(constraints, False)}
            # 리스트 인덱스는 빼고 점 표기로 맞춰 비교 (doorList[0].doorID → doorList.doorID)
            filtered = [
                p for p in leaf_paths
                if ".".join(str(k) for k in p if not isinstance(k, int)) in required_paths
            ]
            if filtered:
                leaf_paths = filtered
            else:
                Logger.debug("[오류주입] ③ 필수 범위에 해당하는 잎이 없어 전체에서 고름")

        if not leaf_paths:
            Logger.debug("[오류주입] ③ 변조할 잎이 없음 — 원본 유지")
            return new_data

        # 2️⃣ 랜덤 경로 선택
        path = random.choice(leaf_paths)

        # 3️⃣ 값 접근
        target = new_data
        for key in path[:-1]:
            target = target[key]

        old_value = target[path[-1]]

        # 4️⃣ 타입만 변경
        if isinstance(old_value, int):
            new_value = str(old_value)
        elif isinstance(old_value, float):
            new_value = str(old_value)
        elif isinstance(old_value, str):
            new_value = 1
        elif isinstance(old_value, bool):
            new_value = "true"
        else:
            new_value = None

        target[path[-1]] = new_value

        return new_data

    def replace_start_time(self, data):
        new_data = copy.deepcopy(data)

        def traverse(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "startTime":
                        # 오류 생성용(0). 시각 필드 String 전환에 맞춰 원본 타입을 유지한다.
                        # 숫자 0을 넣으면 201 유도가 아니라 규격(타입) 검증에서 먼저 탈락해
                        # "형식은 유효하되 내용만 이상한 요청"이라는 유도 의도가 깨진다.
                        if isinstance(value, str):
                            obj[key] = str(self.INVALID_TIMESTAMP)
                        else:
                            obj[key] = self.INVALID_TIMESTAMP
                    else:
                        traverse(value)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)

        traverse(new_data)
        return new_data

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
    Logger.debug("=== 테스트 1: request-based (latest_events REQUEST) ===")
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
    Logger.debug(f"camList 개수: {len(result1['camList'])}")
    for i, cam in enumerate(result1['camList']):
        Logger.debug(f"[{i}] camID: {cam['camID']} (latest_events의 /StreamURLs REQUEST에서 가져옴)")

    # 테스트 2: random-response with referenceEndpoint (latest_events의 RESPONSE에서)
    Logger.debug("\n=== 테스트 2: random-response (latest_events RESPONSE) ===")
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
    Logger.debug(f"selectedCamList 개수: {len(result2['selectedCamList'])}")
    for i, cam in enumerate(result2['selectedCamList']):
        Logger.debug(f"[{i}] camID: {cam['camID']} (latest_events의 /CameraProfiles RESPONSE에서 가져옴)")

    # 테스트 3: request-range with referenceEndpoint
    Logger.debug("\n=== 테스트 3: request-range (latest_events REQUEST) ===")
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
    Logger.debug(f"events 개수: {len(result3['events'])}")
    for i, event in enumerate(result3['events']):
        Logger.debug(f"[{i}] timeList: {len(event['timeList'])}개")
        for j, time in enumerate(event['timeList'][:2]):
            Logger.debug(f"    [{j}] startTime: {time['startTime']}, endTime: {time['endTime']}")

    Logger.debug("\n=== latest_events 확인 ===")
    Logger.debug(f"저장된 API 목록: {list(latest_events.keys())}")
    Logger.debug(str(
        f"/CameraProfiles RESPONSE의 camID들: {[c['camID'] for c in latest_events['/CameraProfiles']['RESPONSE']['data']['camList']]}"))
    Logger.debug(str(
        f"/StreamURLs REQUEST의 camID들: {[c['camID'] for c in latest_events['/StreamURLs']['REQUEST']['data']['camList']]}"))
