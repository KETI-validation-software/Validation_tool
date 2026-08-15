"""DoorControl commandType 생성 확인.

관리시스템이 내려주는 제약은 후보값을 validValues로 담는데
생성 코드가 allowedValues만 찾아서 빈 문자열이 그대로 나가던 문제에 대한 회귀 시험.

실행: .venv\Scripts\python.exe temp\test_commandtype_generation.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_mapper import ConstraintDataGenerator

# spec/Constraints_request.py 의 단일시스템 ac003 DoorControl 제약과 동일한 형태
CONSTRAINTS = {
    "doorID": {"valueType": "preset", "required": True},
    "commandType": {
        "valueType": "random",
        "required": True,
        "referenceEndpoint": "/RealtimeDoorStatus",
        "referenceField": "doorSensor",
        "randomType": "exclude-reference-valid-values",
        "validValueField": "acControl",
        "validValues": ["Lock", "Unlock"],
    },
}
TEMPLATE = {"doorID": "door0001", "commandType": ""}  # spec/Data_request.py 기본값


def generate(constraints, door_memory, latest_events=None):
    return ConstraintDataGenerator(latest_events)._applied_constraints(
        request_data={},
        template_data=dict(TEMPLATE),
        constraints=constraints,
        api_name="DoorControl",
        door_memory=door_memory,
    )


def webhook_event(door_sensor):
    """플랫폼 역할일 때 수신하는 상태 이벤트"""
    return {
        "RealtimeDoorStatus": {
            "WEBHOOK": {"data": {"doorList": [{"doorID": "door0001", "doorSensor": door_sensor}]}}
        }
    }


def main():
    # 잠긴 문에는 반대 명령(Unlock)이 나가야 한다
    result = generate(CONSTRAINTS, {"door0001": {"doorSensor": "Lock"}})
    assert result["commandType"] == "Unlock", result

    # 열린 문에는 Lock
    result = generate(CONSTRAINTS, {"door0001": {"doorSensor": "Unlock"}})
    assert result["commandType"] == "Lock", result

    # 문 상태를 모를 때도 빈 문자열이 나가서는 안 된다
    result = generate(CONSTRAINTS, {})
    assert result["commandType"] in ("Lock", "Unlock"), result

    # 옛 이름(allowedValues)으로 등록된 제약도 그대로 동작
    legacy = {"commandType": {"allowedValues": ["Lock", "Unlock"]}}
    result = generate(legacy, {"door0001": {"doorSensor": "Lock"}})
    assert result["commandType"] == "Unlock", result

    # 플랫폼 역할(단일시스템 시험)에서는 door_memory가 비어 있다.
    # 이때도 수신한 상태 이벤트를 보고 반대 명령을 골라야 한다.
    result = generate(CONSTRAINTS, {}, webhook_event("Lock"))
    assert result["commandType"] == "Unlock", result

    result = generate(CONSTRAINTS, {}, webhook_event("Unlock"))
    assert result["commandType"] == "Lock", result

    # 플랫폼 역할에서 제어 대상 문은 "구독한 문" 중에서 골라야 한다.
    # (구독은 무작위 부분집합인데 템플릿 고정값 door0001을 쓰면
    #  구독하지 않은 문을 제어하게 되어 맥락 검증에서 확률적으로 실패)
    events = {
        "RealtimeDoorStatus": {
            "REQUEST": {"data": {"doorList": [{"doorID": "door0002"}]}},
            "WEBHOOK": {"data": {"doorList": [{"doorID": "door0002", "doorSensor": "Lock"}]}},
        }
    }
    result = generate(CONSTRAINTS, {}, events)
    assert result["doorID"] == "door0002", result       # 템플릿의 door0001이 아니라 구독한 문
    assert result["commandType"] == "Unlock", result    # 그 문의 현재 상태(Lock)의 반대

    # 구독 기록이 없으면 기존처럼 템플릿 기본값 유지 (하위 호환)
    result = generate(CONSTRAINTS, {}, {})
    assert result["doorID"] == "door0001", result

    print("OK — commandType이 문 상태의 반대값으로 채워짐")


if __name__ == "__main__":
    main()
