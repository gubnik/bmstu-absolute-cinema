from abc import ABC, abstractmethod
from flask import session
from typing import Self
from .common import locale_file_regex


class LocaleHolder(ABC):
    @abstractmethod
    def get_locale(self: Self) -> str | None:
        pass

    @abstractmethod
    def set_locale(self: Self, locale: str) -> None:
        pass


class SessionLocaleHolder(LocaleHolder):
    def __init__(self: Self):
        pass

    def get_locale(self: Self) -> str | None:
        return session.get("locale")
    
    def set_locale(self: Self, locale: str) -> None:
        if not locale_file_regex.match(locale):
            raise RuntimeError(f"Locale {locale} does not match the pattern")
        session["locale"] = locale
