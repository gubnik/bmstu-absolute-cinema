from typing import Self

from flask import current_app

from translation.locale_holder import LocaleHolder
from .ts_provider import TranslationProvider

class Translator:
    def __init__(self: Self, ts_provider: TranslationProvider, locale_holder: LocaleHolder):
        self.ts_provider: TranslationProvider = ts_provider
        self.locale_holder: LocaleHolder = locale_holder

    def get_locale(self: Self) -> str:
        locale = self.locale_holder.get_locale()
        if locale:
            return locale
        ts = self.ts_provider.get_all_translations()
        if ts:
            improvised_locale = next(iter(sorted(ts))) 
            self.locale_holder.set_locale(improvised_locale)
            return improvised_locale
        raise FileNotFoundError(f"Unable to detect any locale")

    def change_locale(self: Self, locale: str | None) -> None:
        if not locale:
            locale = self.locale_holder.get_locale()
        if locale in self.ts_provider.get_all_translations():
            self.locale_holder.set_locale(locale)
            return
    
    def get_text(self: Self, key: str) -> str:
        ts = self.ts_provider.get_all_translations()
        locale = self.locale_holder.get_locale()
        if not locale and ts:
            locale = next(iter(sorted(ts)))
        if not locale:
            return key
        if not key in ts[locale]:
            return key
        return ts[locale][key]


def t(key: str) -> str:
    return current_app.translator.get_text(key) # pyright: ignore
