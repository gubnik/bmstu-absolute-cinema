from abc import ABC, abstractmethod
from typing import Self
import os
import json
from .common import locale_file_regex

Locale = dict[str, str]

class TranslationProvider(ABC):
    @abstractmethod
    def load_all_translations(self: Self):
        pass
    @abstractmethod
    def get_all_translations(self: Self) -> dict[str, Locale]:
        pass


class JsonTranslationProvider(TranslationProvider):
    def __init__(self: Self, path: str):
        self.ts_path: str = path
        self.translations: dict[str, Locale] = {}
        self.mtimes: dict[str, float] = {}


    def _load_translation(self: Self, filepath: str):
        locale_filename, ext = os.path.splitext(filepath)
        if ext != ".json":
            return
        if not locale_file_regex.match(locale_filename):
            return

        normalized_filepath = os.path.join(self.ts_path, filepath)
        
        mtime = os.path.getmtime(normalized_filepath)
        prev_mtime = self.mtimes.get(locale_filename)

        if prev_mtime is not None and mtime == prev_mtime:
            return

        self.mtimes[locale_filename] = mtime
        with open(normalized_filepath) as f:
            self.translations[locale_filename] = json.load(f)


    def load_all_translations(self: Self):
        for filepath in os.listdir(self.ts_path):
            self._load_translation(filepath)


    def get_all_translations(self: Self) -> dict[str, Locale]:
        if not self.translations:
            self.load_all_translations()
        return self.translations

