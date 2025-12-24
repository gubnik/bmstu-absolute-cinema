from dataclasses import dataclass


@dataclass
class ResponseOk:
    result: list

@dataclass
class ResponseError:
    error: str

ModelResponse = ResponseOk | ResponseError
