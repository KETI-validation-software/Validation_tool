import random
import copy
import config.CONSTANTS as CONSTANTS
from core.logger import Logger

class ConstraintDataGenerator:
    # 상수 정의
    MAX_TIMESTAMP = 9999999999999  # 최대 타임스탬프 범위
    INVALID_TIMESTAMP = 0  # 오류 생성용 타임스탬프 (Number 스펙의 형식 위반용)
    # 201 유도용 — 형식은 완벽한 "미래 구간" (시험 기준 문서 표 4·6·8 예시와 동일).
    # "0"류 값은 형식 검사 여부에 따라 업체마다 201/400 판정이 갈려 폐기.
    FUTURE_START_TIME = "20270101000000000"
    FUTURE_END_TIME = "20270131000000000"
    # 400 유도용 — 자리수(17)만 맞고 날짜로는 무효 (월 00·일 00)
    INVALID_TIME_FORMAT = "0" * 17
    
    def __init__(self, latest_events=None):
        """
        latest_events: API 이벤트 저장소 {api_name: {direction: event_data}}
        """
        self.latest_events = latest_events if latest_events is not None else {}
        # 시험 대상 장치가 없어 이번 회차를 수행할 수 없을 때의 사유.
        # 요청을 만들 때마다 초기화되고, 설정되면 호출부가 그 회차를 실패로 확정한다.
        self.unrunnable_reason = None

    @staticmethod
    def _fold_indexed_paths(constraints):
        """제약 경로의 줄 번호 구간을 접는다.

        관리도구가 하드코딩된 배열을 줄별로 펼쳐 내려보내는 형식이 생겼다.
            camList.0.camID / camList.1.camID / ... / camList.4.camID
        생성기는 줄 번호 없는 camList.camID 하나로만 조회하므로, 접지 않으면
        제약이 통째로 무시되고 템플릿 값이 그대로 나간다(무작위·참조 설정이
        조용히 사라짐). 줄별 규칙은 실측상 내용이 모두 같아 접어도 손실이 없다.

        camList.0 → camList처럼 상위 항목과 부딪히는 경우가 있어 먼저 온 것을
        남긴다 (상위 항목이 arrayElementType 등 실제 설정을 들고 있다).
        """
        if not isinstance(constraints, dict):
            return constraints
        if not any(s.isdigit() for k in constraints for s in str(k).split(".")):
            return constraints  # 줄 번호가 없으면 그대로 (기존 형식)

        folded = {}
        for path, rule in constraints.items():
            key = ".".join(s for s in str(path).split(".") if not s.isdigit())
            if key not in folded:
                folded[key] = rule
        Logger.debug(f"[DATA_MAPPER] 제약 경로 접기: {len(constraints)}개 → {len(folded)}개")
        return folded

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
        # 관리도구는 목록 안 필드를 경로째로 준다(doorList.doorSensor). 줄 안에서는
        # 끝 이름(doorSensor)으로 찾아야 한다 — 경로째로 찾으면 늘 못 찾아 선택한 문의
        # 상태를 모른 채 무작위 명령이 나갔다. 문이 여러 개면 절반쯤 "잠긴 문에 Lock"
        # 으로 맥락 검증에서 떨어졌다 (2026-09-14 실측, 5개 중 door0004).
        leaf = ref_field.rsplit(".", 1)[-1]

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
                        if item.get(id_field) == item_id and item.get(leaf):
                            return item[leaf]
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
        # 회차마다 새로 판단한다 (앞 회차의 '수행 불가'가 남지 않도록)
        self.unrunnable_reason = None

        # 제약 경로를 접어서 들어온다 — 이후 모든 조회가 같은 형태를 보게 한다
        constraints = self._fold_indexed_paths(constraints)

        # ✅ sensorDeviceList 구조를 가진 웹훅 데이터 동적 생성 (범용)
        if (is_webhook and "sensorDeviceList" in template_data
                and not self._is_preset(constraints, "sensorDeviceID")):
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
                
                # ✅ 줄 생성(ID 채움) 후 값 채우기 설정까지 마저 적용한다.
                # 예전에는 여기서 바로 반환해 eventName(←eventFilter)·eventTime(←startTime)
                # 같은 참조 설정이 한 번도 실행되지 않았다 — 웹훅이 템플릿 빈 값 그대로
                # 나가던 원인 (2026-08-20 sensor001 리허설 실측).
                constraint_map = self._build_constraint_map(constraints or {}, request_data,
                                                            is_webhook=True, api_name=api_name)
                if constraint_map:
                    filled_list = []
                    for row in new_sensor_list:
                        filled = self._generate_list_items("sensorDeviceList", row,
                                                           constraint_map, 1)[0]
                        # ID는 위에서 요청 순서대로 정해둔 값을 유지한다
                        # (줄별 생성은 매번 첫 후보를 집어 전 줄이 같은 ID가 된다)
                        filled["sensorDeviceID"] = row.get("sensorDeviceID",
                                                           filled.get("sensorDeviceID"))
                        filled_list.append(filled)
                    new_sensor_list = filled_list
                    Logger.debug(f"[DATA_MAPPER] 값 채우기 적용 후: {new_sensor_list}")

                template_data["sensorDeviceList"] = new_sensor_list
                Logger.info(f"[DATA_MAPPER] 생성된 sensorDeviceList: {len(new_sensor_list)}개")
                Logger.debug(f"[DATA_MAPPER] 상세: {new_sensor_list}")

            return template_data
        
        # ✅ doorList 구조를 가진 데이터 동적 생성 (범용)
        #    doorID가 고정값이면 관리도구가 적어준 목록을 그대로 쓴다 — 전용 경로 진입 안 함
        if "doorList" in template_data and self._is_preset(constraints, "doorID"):
            Logger.info(f"[DATA_MAPPER] doorID 고정값 — 템플릿 doorList 그대로 사용: "
                        f"{template_data.get('doorList')}")
        elif "doorList" in template_data:
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

                    # ✅ 줄 생성(ID 채움) 후 값 채우기 설정까지 마저 적용한다.
                    # 예전에는 여기서 바로 반환해 eventName(←eventFilter)·eventTime
                    # 같은 참조 설정이 한 번도 실행되지 않았다 — 웹훅이 템플릿 빈 값
                    # 그대로 나가던 원인 (sensor 웹훅 3cea01b와 동일 유형,
                    # 2026-08-26 RealtimeVerifEventInfos 리허설 실측).
                    constraint_map = self._build_constraint_map(constraints or {}, request_data,
                                                                is_webhook=True, api_name=api_name)
                    if constraint_map:
                        filled_list = []
                        for row in new_door_list:
                            filled = self._generate_list_items("doorList", row,
                                                               constraint_map, 1)[0]
                            # ID는 위에서 요청 순서대로 정해둔 값을 유지한다
                            filled["doorID"] = row.get("doorID", filled.get("doorID"))
                            filled_list.append(filled)
                        new_door_list = filled_list
                        Logger.debug(f"[DATA_MAPPER] 값 채우기 적용 후: {new_door_list}")

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
                            if ref_endpoint or value_type == "preset":
                                Logger.debug(f"[DATA_MAPPER] doorID 설정 발견: referenceEndpoint={ref_endpoint}, valueType={value_type}")
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
                    
                    # 무작위 계열(response-based, random-response)이면 1개~전체 중 무작위 개수.
                    # random-response는 예전에 여기서 빠져 문이 늘 전부(5개) 들어갔다 — 일반
                    # 경로의 목록은 이미 1~N 무작위라 이 전용 경로만 어긋나 있었다 (2026-09-14).
                    if value_type in ("response-based", "random-response") and all_door_ids:
                        original_count = len(all_door_ids)
                        random_count = random.randint(1, len(all_door_ids))
                        selected_ids = random.sample(all_door_ids, random_count)
                        Logger.info(f"[DATA_MAPPER] {value_type}: {original_count}개 중 {random_count}개 랜덤 선택")
                        for door_id in selected_ids:
                            new_door_list.append({"doorID": door_id})
                            Logger.debug(f"[DATA_MAPPER] doorID 추가: {door_id}")
                    else:
                        # request-based·고정값 등은 전체 사용
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

                # ✅ doorList만 채우고 바로 반환하던 조기 반환 제거 — eventFilter 같은
                #    나머지 최상위 필드의 값 설정(무작위 등)이 한 번도 적용되지 않아
                #    빈 값으로 나가던 원인 (sensor 웹훅 3cea01b와 동일 유형).
                #    doorList는 위에서 확정했으므로 doorList 계열 제약은 빼고
                #    나머지 필드만 공통 경로로 마저 채운다.
                other_constraints = {k: v for k, v in (constraints or {}).items()
                                     if not str(k).startswith("doorList")}
                if other_constraints:
                    constraint_map = self._build_constraint_map(other_constraints, request_data,
                                                                api_name=api_name)
                    filled = self._generate_from_template(template_data, constraint_map)
                    filled["doorList"] = new_door_list  # 확정한 doorList 보존
                    template_data.update(filled)
                return template_data

            # 조회 응답: 저장된 기록 중 요청 조건에 해당하는 줄만 남긴다.
            # 걸러낸 뒤에는 아래 공통 경로로 내려가 값 채우기 설정(eventName 등)이 적용된다.
            template_data["doorList"] = self._filter_rows_by_request(
                template_data["doorList"], request_data, "doorID"
            )
        
        # ✅ commandType 구조를 가진 데이터 동적 생성 (범용 - DoorControl 등)
        #    commandType이 고정값이면 토글하지 않는다 — 관리도구가 적어준 명령 그대로
        if ("commandType" in template_data and "doorID" in template_data
                and not self._is_preset(constraints, "commandType")):
            Logger.debug(f" commandType 데이터 동적 생성 시작 (API: {api_name})")

            # doorID 추출
            target_door_id = None
            if self._is_preset(constraints, "doorID"):
                # doorID는 관리도구 지정값 — 그 문의 상태만 찾아 명령을 정한다
                target_door_id = template_data.get("doorID")
            elif request_data and "doorID" in request_data:
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


        constraint_map = self._build_constraint_map(constraints, request_data, is_webhook,
                                                    api_name=api_name)
        response = self._generate_from_template(template_data, constraint_map)
        template_data.update(response)
        return template_data


    NO_DEVICE_ID = "NoDevice"

    @classmethod
    def _no_device_id(cls, existing):
        """실제 장치와 겹치지 않는 '장치 없음' 표식 ID

        PTZ 대상 장치가 하나도 없을 때 이 값을 보내 회차를 실패로 확정한다.
        (오류 주입과 무관한 경로다 — 주입 코드를 걷어낼 때 같이 지웠다가 되살렸다.)
        """
        taken = {str(v) for v in (existing or [])}
        if cls.NO_DEVICE_ID not in taken:
            return cls.NO_DEVICE_ID
        n = 1
        while f"{cls.NO_DEVICE_ID}{n}" in taken:
            n += 1
        return f"{cls.NO_DEVICE_ID}{n}"

    @staticmethod
    def _is_preset(constraints, field_name):
        """관리도구가 이 필드를 고정값(preset)으로 지정했는가.

        규칙은 둘뿐이다 — ① 채우라고 하면 채우고 ② 지정한 값이 있으면 그 값을 쓴다.
        일반 생성기는 이걸 지키는데, doorList·sensorDeviceList·commandType처럼 일반
        생성기를 거치지 않는 전용 경로들은 값 설정이 생기기 전 논리를 그대로 돌려
        지정값을 덮어썼다(door9999 사전 입력이 실제 ID로 바뀐 건, 2026-09-12 실측).
        전용 경로에 들어가기 전에 이 한 곳에서 묻는다.
        """
        for path, rule in (constraints or {}).items():
            if isinstance(rule, dict) and (path == field_name or path.endswith("." + field_name)):
                return rule.get("valueType") == "preset"
        return False

    @staticmethod
    def _is_ptz_api(api_name):
        """PTZ 제어 계열 API인지 (PTZStatus, PTZControl 등 — 대소문자 무시)"""
        return "ptz" in str(api_name or "").lower()

    def _build_constraint_map(self, constraints, request_data, is_webhook=False,
                              api_name=None):
        """constraints를 분석하여 각 필드의 제약 조건과 참조 값을 매핑"""
        constraint_map = {}

        # latest_events는 단계가 진행될수록 누적돼, 통째로 찍으면 한 줄이 수천 자가
        # 된다(로그 가독성 저하의 주범). 어떤 API가 쌓여 있는지 키만 남긴다.
        # 전체 덤프는 [CONSTRAINTS] out_con과 같은 내용이라 두 번 찍혔다.
        # 필드별 상세는 바로 아래 "path: valueType=..." 줄에 이미 나온다.
        Logger.debug(f"[BUILD_MAP] constraints {len(constraints)}개 필드")
        Logger.debug(f"[BUILD_MAP] request_data: {request_data}")
        Logger.debug(f"[BUILD_MAP] 참조 가능 이벤트 {len(self.latest_events)}건: "
                     f"{sorted(k for k in self.latest_events if not k.startswith('/'))}")

        for path, rule in constraints.items():
            value_type = rule.get("valueType")
            ref_endpoint = rule.get("referenceEndpoint")
            ref_field = rule.get("referenceField")

            # 필드 1개당 4줄씩 찍던 것을 한 줄로 (valueType·참조 대상 한눈에)
            ref_text = f", 참조={ref_endpoint}.{ref_field}" if ref_endpoint else ""
            Logger.debug(f"[BUILD_MAP] {path}: valueType={value_type}{ref_text}")

            # ✅ 고정값(preset)은 제약 맵에 넣지 않는다 — 관리도구가 적어준 값 그대로.
            # 관리도구에서 고정값으로 바꿔도 예전 참조(referenceEndpoint)가 필드에 붙은 채
            # 내려오는데, 아래 분기는 참조가 있다는 이유만으로 값을 끌어와 덮어썼다
            # (door9999 사전 입력이 DoorProfiles의 door0002로 바뀜, 2026-09-12 실측).
            # 규칙은 둘뿐이다: 채우라면 채우고, 지정했으면 지정값. 여기서 끝낸다.
            if value_type == "preset":
                Logger.debug(f"[BUILD_MAP]   고정값 — 참조·무작위 적용 안 함")
                continue

            # valueType이 "random"이고 randomType이 있으면 아래에서 별도 처리
            random_type = rule.get("randomType")
            
            # referenceEndpoint가 있으면 latest_events에서 데이터 찾기
            # 단, referenceField가 "(참조 필드 미선택)"이면 참조 안 함
            # 단, valueType이 "random"이고 randomType이 있으면 건너뜀 (아래에서 처리)
            # request-range는 아래 전용 분기가 requestRange의 minField/maxField로
            # 구간을 만든다. 여기서 가로채면 min/max 없이 {"type":"request-range"}만
            # 남아 구간을 잃고, 생성기가 "지금 시각"을 찍어 요청 구간 밖 값이
            # 나갔다 (2026-09-11 실측: 5월 구간을 요청했는데 9월 시각이 응답).
            if (ref_endpoint and ref_field and ref_field != "(참조 필드 미선택)"
                    and value_type != "request-range"
                    and not (value_type == "random" and random_type)):
                values = []
                # 같은 참조 목록을 보는 필드끼리 줄을 맞추기 위한 표식.
                # 값을 걸러내거나 표본을 뽑으면 순서가 어긋나므로 그때는 끈다.
                ref_aligned = True

                # referenceEndpoint의 슬래시 처리 (있든 없든 찾을 수 있도록)
                # 예: "/StoredVideoEventInfos" → "StoredVideoEventInfos"
                ref_key = ref_endpoint.lstrip('/')

                Logger.debug(f"[BUILD_MAP]   Searching for ref_key: {ref_key}")

                if ref_key in self.latest_events:
                    Logger.debug(f"[BUILD_MAP]   Found referenceEndpoint in latest_events")
                    # valueType에 따라 REQUEST 또는 RESPONSE에서 가져오기
                    if value_type in self.REQUEST_BASED_TYPES:
                        event = self.latest_events[ref_key].get("REQUEST", {})
                        Logger.debug(f"[BUILD_MAP]   Using REQUEST event")
                    else:  # random-response 등 다른 타입
                        event = self.latest_events[ref_key].get("RESPONSE", {})
                        Logger.debug(f"[BUILD_MAP]   Using RESPONSE event")

                    event_data = event.get("data", {})
                    Logger.debug(f"[BUILD_MAP]   event_data: {event_data}")
                    values = self.find_key(event_data, ref_field)
                    Logger.debug(f"[BUILD_MAP]   Found values from event: {values}")

                    # PTZ 제어 API는 PTZ 카메라에만 유효하다. Dome/Bullet 카메라를
                    # 뽑아 보내면 상대가 정상적으로 거절해 실패로 잡히던 문제.
                    if values and self._is_ptz_api(api_name):
                        ptz_ids = self._collect_ptz_ids(event_data, ref_field)
                        if ptz_ids is None:
                            Logger.debug(f"[BUILD_MAP]   camType 정보 없음 → PTZ 선별 생략")
                        elif ptz_ids:
                            picked = [v for v in values if v in ptz_ids]
                            Logger.info(f"  PTZ 카메라만 선별: {picked} "
                                        f"(전체 {len(values)}대 중 {len(picked)}대)")
                            values = picked
                            ref_aligned = False   # 걸러낸 뒤라 원본 줄 번호와 어긋난다
                        else:
                            # 대상 장치가 없으면 이 회차는 수행 자체가 불가능하다.
                            # 아무 카메라나 골라 보내거나 빈 값을 보내면 결과가
                            # 상대 구현(하드코딩 응답 등)에 좌우되므로, 실제로
                            # 존재할 수 없는 ID를 보내고 회차를 실패로 확정한다.
                            sentinel = self._no_device_id(values)
                            cam_types = sorted({str(t) for t in
                                                self.find_key(event_data, "camType")})
                            self.unrunnable_reason = (
                                f"PTZ 카메라 없음 (camType: {', '.join(cam_types) or '없음'})"
                            )
                            Logger.error(f"  ❌ {api_name}: 시험 수행 불가 — "
                                         f"{self.unrunnable_reason} → {ref_field}={sentinel} 전송")
                            values = [sentinel]
                            ref_aligned = False

                    # response-based(시스템 요청)만 랜덤 선택, request-based(플랫폼 응답/웹훅)는 그대로 사용 (01/08)
                    if value_type == "response-based" and not is_webhook and values and len(values) > 0:
                        original_count = len(values)
                        random_count = random.randint(1, len(values))
                        values = random.sample(values, random_count)
                        ref_aligned = False   # 표본을 뽑은 뒤라 원본 줄 번호와 어긋난다
                        Logger.debug(f"[BUILD_MAP]   Random selection: {random_count}/{original_count} items selected (시스템 요청)")
                    else:
                        Logger.debug(f"[BUILD_MAP]   랜덤 선택 안함 (valueType={value_type}, is_webhook={is_webhook}), 전체 사용: {len(values)}개")
                else:
                    Logger.debug(f"[BUILD_MAP]   referenceEndpoint NOT found in latest_events")
                    Logger.debug(f"[BUILD_MAP]   Available endpoints: {list(self.latest_events.keys())}")

                # 참조(앞선 응답·요청)에서 실제로 가져온 값인지 — 폴백 전에 판단한다.
                # 목록을 몇 줄로 늘릴지는 "장치가 몇 대인가"로 정해야 하고,
                # "고를 수 있는 값이 몇 가지인가"로 정하면 안 된다.
                from_reference = bool(values)

                # ✅ 무작위 계열은 참조에서 값을 못 찾으면 관리도구 설정값으로 폴백.
                # 요청 생성 시점에는 참조 응답이 아직 없는 게 보통이라, 폴백이 없으면
                # "무작위 + 참조 필드 선택" 조합이 항상 빈 값으로 나간다 (2026-08-20 실측).
                if not values and value_type in ("random", "random-response"):
                    values = self._get_static_random_values(rule)
                    Logger.debug(f"[BUILD_MAP]   참조 값 없음 → 설정값 폴백: {values}")

                # 참조도 폴백도 비면 템플릿 값(보통 빈 문자열)이 그대로 나간다.
                # 그러면 우리가 못 채운 값을 상대 잘못처럼 채점하게 되므로 크게 남긴다.
                if not values:
                    Logger.error(
                        f"  ❌ 값을 채우지 못했습니다: {path} "
                        f"(참조 {ref_endpoint}.{ref_field}, valueType={value_type}) — "
                        f"템플릿 값이 그대로 전송됩니다. "
                        f"보유 참조: {sorted(k for k in self.latest_events if not k.startswith('/'))}"
                    )

                # 같은 응답의 같은 목록을 보는 필드들을 한 묶음으로 묶는 열쇠.
                # camID와 camName을 따로 뽑으면 cam0003에 "카메라1"이 붙는다 —
                # 명단에서 줄을 골라야지 칸을 따로 고르면 짝이 어긋난다.
                # ponytail: 여기서는 "어느 응답에서 왔나"만 적는다. 경로만으로는
                #           camList.camID와 camList.camLoc.desc가 같은 목록에서 온
                #           형제라는 걸 알 수 없어서다 — 실제로 한 줄인지는
                #           _align_group_picks가 템플릿 구조와 값 개수로 가른다.
                ref_group = ref_key if from_reference and ref_aligned else None

                constraint_map[path] = {
                    "type": value_type,
                    "values": values if values else [],
                    "from_reference": from_reference,
                    "ref_group": ref_group,
                }

            elif value_type in self.REQUEST_BASED_TYPES:
                # referenceEndpoint 없으면 현재 request_data에서 찾기
                Logger.debug(f"[BUILD_MAP]   Searching in current request_data")
                values = self.find_key(request_data, ref_field)
                Logger.debug(f"[BUILD_MAP]   Found values from request: {values}")
                constraint_map[path] = {
                    "type": "request-based",
                    "values": values if values else [],
                    "from_reference": bool(values),
                }

            elif value_type == "random-response":
                # referenceEndpoint 없으면 현재 request_data에서 찾기
                values = (self.find_key(request_data, ref_field)
                          if ref_field and ref_field != "(참조 필드 미선택)" else [])
                if not values:
                    values = self._get_static_random_values(rule)
                constraint_map[path] = {
                    "type": "random-response",
                    "values": values if values else []
                }

            elif value_type == "random":
                # validValues/specifiedValues에서 랜덤 선택
                valid_values = self._get_static_random_values(rule)
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
                
                if not valid_values:
                    # 참조 없이 관리도구 후보값만 쓰는 필드다. 후보가 비면 템플릿 값이
                    # 그대로 나가는데(빈 배열·빈 문자열) 아무 흔적이 없어 진단이 막혔다.
                    # 관리도구가 다른 키 이름으로 보냈을 수도 있어 가진 키를 함께 남긴다.
                    Logger.error(
                        f"  ❌ 값을 채우지 못했습니다: {path} (valueType=random) — "
                        f"관리도구 후보값(validValues/specifiedValues)이 비어 있습니다. "
                        f"템플릿 값이 그대로 전송됩니다. 규칙이 가진 키: {sorted(rule.keys())}"
                    )

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
                    "values": values if values else [],
                    "from_reference": bool(values),
                }

            elif value_type == "random-response":
                # referenceEndpoint 없으면 현재 request_data에서 찾기
                values = self.find_key(request_data, ref_field)
                constraint_map[path] = {
                    "type": "random-response",
                    "values": values if values else []
                }

        return constraint_map

    def _pick_array_values(self, constraint):
        """문자열 배열 칸(classFilter 등)에 넣을 값 목록. 넣을 게 없으면 None.

        예전에는 값 풀에서 하나만 골라 [ ]로 감쌌다. 그래서
        - 무작위는 후보가 여럿이어도 늘 1개만 들어갔고,
        - 참조한 칸 자체가 배열이면 배열이 통째로 뽑혀 [["Human", "Vehicle"]]
          이중 배열이 나갔다 (2026-09-14 확인).
        참조에서 온 배열은 펼쳐서 한 풀로 모은 뒤,
        - 요청을 되돌려주는 설정(request-based)은 전부 그대로,
        - 무작위 계열은 1개~전체 중 무작위 개수를 겹치지 않게 넣는다.
        """
        pool = []
        for v in constraint.get("values") or []:
            for x in (v if isinstance(v, list) else [v]):
                if x not in ("", None) and x not in pool:
                    pool.append(x)
        if not pool:
            return None
        if constraint.get("type") in self.REQUEST_BASED_TYPES:
            return pool
        return random.sample(pool, random.randint(1, len(pool)))

    @staticmethod
    def _get_static_random_values(rule):
        """관리도구 '무작위' 설정값 추출 — validValues 우선, 없으면 specifiedValues."""
        values = rule.get("validValues") or []
        if not values:
            values = rule.get("specifiedValues") or []
        return list(values)

    # 17자리 시각 표기 yyyyMMddHHmmssSSS (안내서 표 2-1)
    TIME_FORMAT_LEN = 17

    @staticmethod
    def _parse_time17(value):
        """17자리 시각 문자열/숫자를 datetime으로. 시각이 아니면 None."""
        import datetime
        text = str(value).strip()
        if len(text) != ConstraintDataGenerator.TIME_FORMAT_LEN or not text.isdigit():
            return None
        try:
            base = datetime.datetime.strptime(text[:14], "%Y%m%d%H%M%S")
            return base + datetime.timedelta(milliseconds=int(text[14:]))
        except ValueError:
            return None  # 13월 40일 같은 달력에 없는 날짜

    @staticmethod
    def _format_time17(dt):
        """datetime → 17자리 시각 문자열"""
        return dt.strftime("%Y%m%d%H%M%S") + f"{dt.microsecond // 1000:03d}"

    def _pick_time_in_range(self, min_val, max_val, exclusive_min=False):
        """구간 안의 '실제로 존재하는 시각'을 뽑는다.

        예전에는 17자리 숫자 구간에서 random.randint로 정수를 뽑아 문자열로만
        바꿨다 — 숫자로는 구간 안이어도 달력에 없는 날짜(월 13·일 40 등)가
        나올 수 있었다("날짜가 난수로 나가던" 문제). 구간을 날짜로 해석해
        밀리초 단위로 뽑고 다시 17자리로 포맷한다.

        Returns:
            str | None — 양 끝을 시각으로 해석하지 못하면 None(호출부가 폴백)
        """
        import datetime
        start = self._parse_time17(min_val)
        end = self._parse_time17(max_val)
        if start is None or end is None:
            return None
        if end < start:
            start, end = end, start
        span_ms = int((end - start).total_seconds() * 1000)
        if exclusive_min:
            # endTime 등 "start보다 뒤" 조건 — 최소 1ms 뒤
            offset = random.randint(1, span_ms) if span_ms >= 1 else 1
        else:
            offset = random.randint(0, span_ms) if span_ms > 0 else 0
        return self._format_time17(start + datetime.timedelta(milliseconds=offset))

    def _pick_range_value(self, constraint, template_value, sibling_start=None):
        """request-range 값 생성 (최상위·리스트 줄 공용).

        ✅ 17자리 시각 필드가 String으로 전환되어 min/max가 문자열로 올 수 있다.
           내부에서는 숫자로 변환해 비교·생성하고, 원본이 문자열이면 문자열로 내보낸다.
        - 참조 부재(min이 기본값 0): 템플릿 시각 값을 기준으로 삼고 타입도 템플릿을 따른다.
        - sibling_start가 주어지면(endTime 생성) 그보다 큰 값을 만든다.
        """
        raw_min = constraint.get("min", 0)
        raw_max = constraint.get("max", self.MAX_TIMESTAMP)
        # 참조 대상이 비어 있으면 min/max가 빈 문자열("")로 들어온다.
        # 문자열이라는 이유만으로 "참조 있음"으로 보면 아래 참조 없음 판정을
        # 빠져나가 0~13자리 난수가 시각 자리에 나갔다.
        norm_min = 0 if isinstance(raw_min, str) and not raw_min.strip() else raw_min
        norm_max = (self.MAX_TIMESTAMP
                    if isinstance(raw_max, str) and not raw_max.strip() else raw_max)
        min_val = self._to_number(norm_min, 0)
        max_val = self._to_number(norm_max, self.MAX_TIMESTAMP)

        reference_missing = min_val == 0 and not isinstance(norm_min, str)
        as_string = (isinstance(raw_min, str) or isinstance(raw_max, str)
                     or (reference_missing and isinstance(template_value, str)))

        # 참조가 없으면 범위가 0~13자리 난수가 돼 시각으로서 무의미하다.
        # 템플릿에 시각 값이 있으면 그 근방을, 그것도 비어 있으면 현재 시각을 쓴다.
        if reference_missing:
            template_num = self._to_number(template_value, 0)
            if template_num > 0:
                min_val = template_num
            else:
                import datetime
                now17 = self._format_time17(datetime.datetime.now())
                Logger.warning(f"  ⚠ request-range 참조·템플릿 모두 비어 있음 "
                               f"→ 현재 시각 {now17} 사용")
                return now17 if as_string else int(now17)

        if min_val >= max_val:
            max_val = min_val + 1000

        # ✅ 시각 구간이면 '실제로 존재하는 시각'을 뽑는다 (달력에 없는 날짜 방지).
        #    양 끝이 17자리 시각으로 해석되지 않으면(일반 숫자 범위) 기존 방식으로 폴백.
        lo_for_time = sibling_start if sibling_start is not None else min_val
        picked_time = self._pick_time_in_range(lo_for_time, max_val,
                                               exclusive_min=sibling_start is not None)
        if picked_time is not None:
            return picked_time if as_string else int(picked_time)

        if sibling_start is not None:
            start_num = self._to_number(sibling_start, min_val)
            generated = random.randint(start_num + 1, max(max_val, start_num + 2))
        else:
            generated = random.randint(min_val, max_val)

        return str(generated) if as_string else generated

    def _generate_from_template(self, template, constraint_map):
        """템플릿을 재귀적으로 순회하며 데이터 생성 (템플릿 구조 유지)"""
        result = {}

        for key, value in template.items():
            constraint = constraint_map.get(key)
            ctype = constraint["type"] if constraint else None
            is_object_list = (isinstance(value, list) and len(value) > 0
                              and isinstance(value[0], dict))
            is_object = isinstance(value, dict)
            # 컨테이너(객체 목록·중첩 객체)는 자기 제약이 있어도 구조를 따라 내려간다.
            # 관리도구가 컨테이너에도 참조를 달아 내려주기 시작하면서
            # (camList: valueType=preset, 참조=/CameraProfiles.camID), 예전 구조에서는
            # 여기서 걸려 하위 항목 생성이 통째로 건너뛰어졌다 — 목록 안의 camID가
            # 빈 값으로 나가던 원인 (2026-09-11 리허설 실측).
            is_container = is_object_list or is_object

            # 최상위 레벨에서 constraint 확인
            if not is_container and ctype in self.VALUE_PICK_TYPES:
                if isinstance(value, list):
                    # 문자열 배열 필드(classFilter 등)는 배열 안에 여러 값을 담는다
                    picked = self._pick_array_values(constraint)
                    result[key] = picked if picked is not None else value
                elif constraint["values"]:
                    result[key] = random.choice(constraint["values"])
                else:
                    result[key] = value
            elif not is_container and ctype == "request-range":
                # ✅ 최상위 시각 필드의 범위 설정 — 예전에는 미처리로 템플릿 값이
                # 그대로 나갔다 (2026-08-26 전수 검사에서 확인)
                result[key] = self._pick_range_value(constraint, value)
            elif is_object_list:
                # 리스트 형태의 구조 처리
                # ✅ 템플릿의 리스트 길이 자동 감지
                n = len(value)
                
                # ✅ constraints가 없으면 원본 리스트를 그대로 사용
                # 깊이 무관 접두부 검사 — 예전에는 한 단계(key.field)만 봐서
                # rows[].box.f / rows[].sub[].f 같은 더 깊은 필드의 설정이
                # 통째로 무시됐다 (2026-08-26 전수 검사에서 확인).
                has_constraints = any(p.startswith(f"{key}.") for p in constraint_map)
                
                if not has_constraints:
                    # constraints가 없으면 원본 리스트 그대로 사용 (preset)
                    result[key] = value
                elif n > 1:
                    # 등록된 줄이 여럿이면 줄별로 채운다.
                    # 첫 줄만 본으로 삼아 n개를 찍어내면 2번째 이후 줄(카메라2, door0002 등)이
                    # 사라지고 첫 줄이 복제된다.
                    # 단 값 풀은 줄 사이에서 공유한다 — 줄마다 _generate_list_items를
                    # 새로 부르면 "이미 쓴 값" 목록이 매번 초기화돼 모든 줄이 첫
                    # 참조값(cam0001)만 집었다.
                    avail, used, shared, _ = self._collect_value_pools(
                        key, value[0], constraint_map
                    )
                    aligned = self._align_group_picks(key, value[0], constraint_map, n)
                    result[key] = [
                        self._generate_item(key, row, constraint_map, n,
                                            available_values=avail,
                                            used_values=used,
                                            shared_values=shared,
                                            item_index=i,
                                            aligned_picks=aligned)
                        for i, row in enumerate(value)
                    ]
                else:
                    # 줄이 하나면 요청 개수만큼 늘리는 기존 방식 (영상 계열 등)
                    result[key] = self._generate_list_items(
                        key, value[0], constraint_map, n
                    )
            elif is_object:
                # ✅ 중첩 딕셔너리: 하위 경로(key.field)에 제약이 있으면 재귀 적용.
                # 예전에는 무조건 그대로 둬서 filter.eventFilter 같은 중첩 필드의
                # 무작위/참조 설정이 조용히 무시됐다 (2026-08-23 이식).
                if any(p == key or p.startswith(f"{key}.") for p in constraint_map):
                    result[key] = self._generate_item(key, value, constraint_map, 1)
                else:
                    result[key] = value
            else:
                # 일반 필드는 그대로 유지
                result[key] = value

        return result

    def _collect_value_pools(self, parent_key, item_template, constraint_map):
        """리스트 한 줄을 채우는 데 쓸 값 풀을 모은다.

        반환: (available_values, used_values, shared_values, min_available_count)

        줄 여러 개를 채울 때는 이 풀을 줄 사이에서 공유해야 한다. 줄마다 새로
        만들면 "이미 쓴 값" 목록이 매번 비어 있어 모든 줄이 첫 값(cam0001)만
        집는다.
        """
        available_values = {}
        used_values = {}  # 이미 사용된 값 추적
        shared_values = {}  # 필터 필드 (모든 항목에 동일한 값)
        min_available_count = float('inf')  # 최소 값 개수 추적

        # 필터 필드 목록 (중복 허용)
        filter_fields = ["eventFilter", "classFilter", "eventName"]

        for field, value in item_template.items():
            field_path = f"{parent_key}.{field}"
            # 배열 칸(classFilter 등)은 줄 수를 정하는 데 끼지 않는다. 끼면 참조 클래스
            # 5개가 "filterList 1~5줄 × 줄마다 1개"로 나갔다 — 원하는 모양은 "1줄에
            # 클래스 여러 개"다 (2026-09-14). 배열 안의 값은 _pick_array_values가 채운다.
            if isinstance(value, list):
                continue
            if field_path in constraint_map:
                constraint = constraint_map[field_path]

                # request-based 중 필터 필드는 모든 항목에 동일한 값 사용
                if constraint["type"] == "request-based" and any(f in field for f in filter_fields):
                    if constraint["values"]:
                        # 첫 번째 값을 모든 항목에 공유
                        shared_values[field_path] = constraint["values"][0]

                # 그 외 필드는 중복 방지
                elif constraint["type"] in self.VALUE_PICK_TYPES:
                    if constraint["values"]:
                        available_values[field_path] = constraint["values"].copy()
                        used_values[field_path] = []

                        # 목록을 몇 줄로 늘릴지는 참조에서 가져온 값만 기준이 된다.
                        # 카메라 5대면 5줄이 말이 되지만, 허용값이 27가지라고 해서
                        # 27줄을 보내는 건 말이 안 된다 — 고를 수 있는 가짓수일 뿐이다
                        # (filterList가 속성 개수만큼 부풀던 문제, 2026-09-11 실측).
                        if constraint.get("from_reference"):
                            min_available_count = min(min_available_count,
                                                      len(constraint["values"]))

        return available_values, used_values, shared_values, min_available_count

    def _align_group_picks(self, parent_key, item_template, constraint_map, n):
        """같은 참조 목록을 보는 필드들을 줄 단위로 맞춰 뽑는다.

        반환: {필드경로: [1줄값, 2줄값, ...]} — 맞출 게 없으면 빈 dict.

        명단에서 줄 번호를 먼저 n개 고르고, 한 묶음의 모든 필드가 같은 줄에서
        값을 꺼낸다. 칸마다 따로 뽑으면 cam0003에 "카메라1"이 붙어 나간다
        (참조 필드가 한 줄에 둘 이상 걸리는 순간 드러나는 문제).

        한 줄에 속하는 범위는 템플릿을 따라간다 — 중첩 객체(camLoc)는 같은 줄이지만
        안쪽 목록(timeList)은 자기 줄 수로 따로 만들어지므로 여기서 제외한다.
        """
        paths = []
        self._collect_aligned_paths(parent_key, item_template, constraint_map, paths)

        # 묶는 기준에 값 개수를 함께 넣는다 — 같은 응답이라도 개수가 다르면 다른 목록이다
        groups = {}
        for field_path in paths:
            constraint = constraint_map[field_path]
            key = (constraint["ref_group"], len(constraint["values"]))
            groups.setdefault(key, []).append(field_path)

        picks = {}
        for (group, total), members in groups.items():
            if total < n:
                Logger.debug(f"[ALIGN] {group}: 원본 {total}줄 < 필요 {n}줄 → 줄 맞춤 생략")
                continue
            rows = random.sample(range(total), n)
            for member in members:
                picks[member] = [constraint_map[member]["values"][i] for i in rows]
            if len(members) > 1:
                Logger.debug(f"[ALIGN] {group}: {sorted(members)} → 원본 줄 {rows} 로 맞춤")
        return picks

    @classmethod
    def _collect_aligned_paths(cls, parent_key, template, constraint_map, out):
        """한 줄에 함께 담기는 참조 필드 경로를 모은다 (중첩 객체까지, 목록은 제외)."""
        for field, value in template.items():
            field_path = f"{parent_key}.{field}"
            if isinstance(value, dict):
                cls._collect_aligned_paths(field_path, value, constraint_map, out)
            elif isinstance(value, list):
                continue          # 안쪽 목록은 자기 템플릿으로 따로 생성된다
            else:
                constraint = constraint_map.get(field_path) or {}
                if constraint.get("ref_group") and constraint.get("values"):
                    out.append(field_path)

    def _generate_list_items(self, parent_key, item_template, constraint_map, n):
        """리스트 항목 생성 - 중복 방지 (각 항목은 고유한 값)"""
        items = []

        available_values, used_values, shared_values, min_available_count = \
            self._collect_value_pools(parent_key, item_template, constraint_map)

        # 템플릿이 한 줄일 때 몇 건으로 늘릴지 — 참조 개수 안에서 매번 다르게 뽑는다.
        # 늘 참조 개수와 같으면(카메라 5대 → 항상 5건) 상대가 "이 API는 늘 5건"으로
        # 하드코딩한 응답을 내도 구분되지 않는다. StreamURLs부터는 특정 카메라를
        # 지목해 명령하는 구간이라 요청대로 처리하는지가 시험의 핵심이다.
        # 값 풀은 그대로 두고 뽑는 개수만 줄이므로 중복은 생기지 않는다.
        #
        # 단 받은 요청을 되돌려주는 경우(request-based — 응답·웹훅)는 제외한다.
        # 그쪽은 요청에 담긴 항목과 1:1로 맞춰야 하므로 개수를 흔들면 안 된다.
        mirrors_request = any(
            (constraint_map.get(fp) or {}).get("type") in self.REQUEST_BASED_TYPES
            for fp in available_values
        )
        if min_available_count != float('inf'):
            if mirrors_request:
                # 줄 수는 요청 항목 수로만 정한다. 다른 참조 필드(userID 등)의 값 가짓수까지
                # 최솟값에 넣으면 문 5개를 요청해도 사용자가 2명이면 2줄만 나갔다
                # (2026-09-14 StoredVerifEventInfos 실측). 그런 필드는 줄 사이 중복을 허용한다.
                n = min(len(constraint_map[fp]["values"]) for fp in available_values
                        if constraint_map[fp].get("type") in self.REQUEST_BASED_TYPES)
                Logger.info(f" {parent_key}: {n}개 생성합니다. (요청 항목과 1:1)")
            else:
                n = random.randint(1, min_available_count)
                Logger.info(f" {parent_key}: {n}개 생성합니다. "
                            f"(참조 {min_available_count}건 중 무작위)")

        # 줄 수가 정해진 뒤에 원본 줄을 고른다 — 같은 참조를 보는 필드끼리 짝을 맞춘다
        aligned_picks = self._align_group_picks(parent_key, item_template, constraint_map, n)

        for i in range(n):
            item = self._generate_item(parent_key, item_template, constraint_map, n,
                                       available_values=available_values,
                                       used_values=used_values,
                                       shared_values=shared_values,
                                       item_index=i,
                                       aligned_picks=aligned_picks)
            items.append(item)

        return items

    def _generate_item(self, parent_key, template, constraint_map, n, available_values=None, used_values=None,
                       shared_values=None, item_index=0, aligned_picks=None):
        """단일 항목 생성 (재귀적으로 중첩 구조 처리) - 중복 방지"""
        item = {}

        if available_values is None:
            available_values = {}
        if used_values is None:
            used_values = {}
        if shared_values is None:
            shared_values = {}
        if aligned_picks is None:
            aligned_picks = {}

        for field, value in template.items():
            field_path = f"{parent_key}.{field}"

            # 중첩된 딕셔너리 처리 (예: videoInfo)
            if isinstance(value, dict):
                item[field] = self._generate_item(field_path, value, constraint_map, n,
                                                  available_values, used_values, shared_values,
                                                  item_index, aligned_picks)

            # 중첩된 리스트 처리 (예: timeList)
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    # 안쪽 목록 길이는 자기 템플릿에서 정한다. 바깥 줄 수(n)를
                    # 그대로 물려주면 "카메라 3대 → 카메라마다 시간 3개"처럼
                    # 상관없는 개수가 따라붙는다 (2026-09-11 실측).
                    item[field] = self._generate_list_items(
                        field_path, value[0], constraint_map, len(value)
                    )
                elif field_path in constraint_map and constraint_map[field_path].get("values"):
                    # ✅ 문자열 배열 필드(filterList.classFilter 등)도 값 설정을 적용한다.
                    # 예전에는 리스트라는 이유로 규칙 확인 없이 원본([])을 그대로 둬서
                    # 무작위 설정이 조용히 무시됐다 (2026-08-26 리허설 실측).
                    picked = self._pick_array_values(constraint_map[field_path])
                    item[field] = picked if picked is not None else value
                else:
                    item[field] = value

            # constraint가 있는 필드 처리
            elif field_path in constraint_map:
                constraint = constraint_map[field_path]

                # ✅ shared_values (필터 필드): 모든 항목에 동일한 값
                if field_path in shared_values:
                    item[field] = shared_values[field_path]

                # ✅ 줄 맞춤: 같은 참조 목록을 보는 필드는 원본에서 같은 줄의 값을 쓴다
                elif item_index < len(aligned_picks.get(field_path, [])):
                    item[field] = aligned_picks[field_path][item_index]

                # ✅ request-based, random-response, random: 중복 방지 (순차 할당)
                elif constraint["type"] in self.VALUE_PICK_TYPES:
                    if field_path in available_values and available_values[field_path]:
                        values_list = available_values[field_path]
                        used_list = used_values.get(field_path, [])

                        # 사용 가능한 값 중 아직 사용하지 않은 값 찾기
                        unused_values = [v for v in values_list if v not in used_list]

                        if unused_values:
                            # 아직 안 쓴 값 중에서 무작위로 — 예전에는 [0]을 집어
                            # 늘 참조 목록 순서(cam0001, cam0002 …)대로 나갔다
                            selected_value = random.choice(unused_values)
                            item[field] = selected_value
                            # 사용된 값으로 표시
                            if field_path not in used_values:
                                used_values[field_path] = []
                            used_values[field_path].append(selected_value)
                        elif values_list and constraint["type"] not in self.REQUEST_BASED_TYPES:
                            # 줄 수를 요청 항목 수에 맞춘 경우 — 이 필드는 가짓수가 모자라 중복 허용
                            selected_value = random.choice(values_list)
                            item[field] = selected_value
                            Logger.debug(f" {field_path}: 값 {len(values_list)}가지를 다 써서 "
                                         f"중복 사용 → {selected_value}")
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
                            # 값 풀 없이 들어온 경로(중첩 객체 안의 단일 필드 등).
                            # 여기도 [0]이라 늘 첫 값만 나갔다.
                            selected_value = random.choice(unused_values)
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
                    sibling_start = (item.get("startTime")
                                     if "endTime" in field and "startTime" in item else None)
                    item[field] = self._pick_range_value(constraint, value, sibling_start)

                else:
                    # preset 등 값을 만들지 않는 설정 — 템플릿 값을 그대로 둔다.
                    # 예전에는 여기에 else가 없어 item[field] 자체가 설정되지 않았고,
                    # 필드가 응답·요청에서 통째로 사라졌다(관리도구가 목록 안 필드를
                    # preset으로 내려주면 재현).
                    item[field] = value

            else:
                # constraint 없는 필드는 기본값 유지
                item[field] = value

        return item


    # 관리도구가 내려주는 valueType 이름. request-array-based는 요청의 배열
    # 필드에서 값을 가져오라는 뜻인데 목록에 없어 값이 한 번도 안 채워졌다
    # (2026-09-07 실측: camID·eventName이 빈 값으로 나감).
    REQUEST_BASED_TYPES = ("request-based", "request-array-based")
    VALUE_PICK_TYPES = ("random-response", "random", "response-based",
                        "request-based", "request-array-based")

    # PTZ 제어는 PTZ 카메라에만 유효하다. camType 표기는 상대 시스템마다
    # 'PTZ' / 'ptz' / 'PTZ Camera' / '고정형PTZ'처럼 제각각이라,
    # 대소문자 무시하고 문자열에 'ptz'가 들어 있으면 모두 PTZ로 본다.
    PTZ_CAM_TYPE = "ptz"

    def _collect_ptz_ids(self, event_data, id_field):
        """참조 응답에서 camType이 PTZ인 항목의 ID만 모은다.

        camType이 어디에도 없으면 None을 돌려 호출부가 거르지 않도록 한다
        (CameraProfiles 응답에 camType이 없는 규격일 수 있음).
        """
        ptz_ids, saw_type = [], False
        # 관리도구가 참조 필드를 경로("camList.camID")로 준다. 응답 줄 안의 칸 이름은
        # "camID"라 경로째로 찾으면 한 줄도 못 찾아 선별이 통째로 생략됐다 —
        # Dome·Bullet 카메라에 PTZ 명령이 나감 (2026-09-14, find_key와 같은 유형)
        id_field = str(id_field).rsplit(".", 1)[-1]

        def walk(node):
            nonlocal saw_type
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if not isinstance(node, dict):
                return

            if id_field in node:
                cam_type = self.find_key(node, "camType")
                if cam_type:
                    saw_type = True
                    if any(self.PTZ_CAM_TYPE in str(t).lower() for t in cam_type):
                        ptz_ids.append(node[id_field])
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)

        walk(event_data)
        return ptz_ids if saw_type else None

    def find_key(self, data, target_key):
        """재귀적으로 데이터에서 키 찾기"""
        def _search(node, name):
            found = []
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == name:
                        found.append(v)
                    elif isinstance(v, (dict, list)):
                        found.extend(_search(v, name))
            elif isinstance(node, list):
                for item in node:
                    found.extend(_search(item, name))
            return found

        results = _search(data, target_key)

        # 관리도구가 참조 필드를 이름("camID")으로도, 경로("camList.camID")로도
        # 내려준다. 경로로 오면 그런 이름의 키가 없어 조회가 통째로 빈다
        # (참조 기반 필드가 전부 빈 값으로 나가던 원인, 2026-09-11 실측).
        # 마지막 조각을 이름으로 다시 찾는다 — 이 함수가 이미 깊이 무관
        # 재귀 검색이라 이름으로 내려오던 때와 결과가 같다.
        if not results and "." in str(target_key):
            leaf = str(target_key).rsplit(".", 1)[-1]
            results = _search(data, leaf)
            if results:
                Logger.debug(f"[find_key] 경로 표기 '{target_key}' → 이름 '{leaf}'로 조회")

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
