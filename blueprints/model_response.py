from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")

@dataclass
class Ok(Generic[T]):
    result: T

@dataclass
class Error(Generic[E]):
    error: E

Result = Ok[T] | Error[E]

