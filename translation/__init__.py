from flask import current_app
from typing import Any

def t(key: str, **kwargs: Any) -> str:
    return current_app.translator.get_text(key, **kwargs) # pyright: ignore

def get_locale() -> str:
    return current_app.translator.get_locale() # pyright: ignore

__all__ = ["t", "get_locale"]
