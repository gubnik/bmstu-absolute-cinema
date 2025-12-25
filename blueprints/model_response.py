from dataclasses import dataclass


@dataclass
class ResponseOk:
    result: list[dict]

@dataclass
class ResponseError:
    error: str

ModelResponse = ResponseOk | ResponseError
