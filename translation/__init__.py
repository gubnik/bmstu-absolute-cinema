from flask import current_app

def t(key: str) -> str:
    return current_app.translator.get_text(key) # pyright: ignore

def get_locale() -> str:
    return current_app.translator.get_locale() # pyright: ignore

__all__ = ["t", "get_locale"]
