#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
API 서버에서 지원하는 요청들에 대한 파라메터 및 내부 함수 호출 파라메터를 정의하는 모듈
아래의 action_table에 다음의 두 가지 형식으로 요청 유형을 정의할 수 있음

    "api_name": {
        "default_params": {"name": value, ...}, -> 만약 동일한 파라메터를 여러 개 받을 수 있다면 value를 []로 지정
        "eseential_params": ["name", ...],
        "api_params": lambda request: [arg, ...]
    },
    "other_name1": "api_name", # 동일 명령 정의
"""

def to_number(value, dtype=int):
    """
    value를 dtype 혹은 list of dtype으로 변환

    Note: 
        Payload에 JSON 형태로 전달되는 정보는 자료형에 문제가 없지만
        Request Parameter에서는 모든 것이 문자열로 전달되므로 숫자 필드들에 대한 변환이 필요함

    Args:
        value: 변환 대상 값

    Returns:
        value가 list of any인 경우 list of dtype을 반환
        그 외의 경우 dtype을 반환
    """

    if value is None:
        return None
    elif isinstance(value, list):
        return [dtype(d) for d in value]
    else:
        return dtype(value)

"""
    key: 요청의 action 필드값
    value: 해당 요청에 대한 상세 정의
        - default_params: 디폴트 파라메터들의 이름 및 값
        - essential_params: 필수 파라메터들의 이름
        - api_params: 요청 파라메터(dict)를 인자로 받아 내부 API에 전달할 파라메터를 반환하는 함수
"""

action_table = {
    "reverse": { # s를 입력으로 받아 뒤집힌 문자열을 반환
        "default_params": {"pretty": "N",},
        "essential_params": ["s"],
        "api_params": lambda request: [request["s"]]
    },
    "area": { # 직사각형의 width와 height를 입력받아 넓이를 반환
        "default_params": {"pretty": "N",},
        "essential_params": ["width", "height"],
        "api_params": lambda request: [to_number(request["width"]), to_number(request["height"])]
    },
    "order": { # 여러 개의 문자열 s를 입력받아 정렬한 결과를 반환
        "default_params": {"pretty": "N", "s": [], "reverse": "N"},
        "essential_params": [],
        "api_params": lambda request: [request["s"], request["reverse"].lower() == "y"]
    },
    "poi": { # 위도(latitude), 경도(longitude), 반경(radius), 개수(top_n)을 입력받아 해당 영역 내의 poi들을 최대 top_n개 반환 - 미구현 테스트용
        "default_params": {"pretty": "N", "top_n": 10}, 
        "essential_params": ["latitude", "longitude", "radius"],
        "api_params": lambda request: [to_number(request["latitude"], dtype=float), to_number(request["longitude"], dtype=float), to_number(request["radius"], dtype=float), to_number(request["top_n"])]
    },
    "ls": { # path를 입력받아 ls 명령의 결과를 반환
        "default_params": {"pretty": "N", "timeout": None},
        "essential_params": ["path"],
        "api_params": lambda request: [request["path"], to_number(request["timeout"], dtype=float)]
    },
    "sort": "order" # sort라는 액션을 order라는 액션과 동일하게 정의
}
