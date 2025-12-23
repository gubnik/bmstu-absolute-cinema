from typing import Self
import os
from string import Template
from typing import Dict

class SQLProvider:

    def __init__(self: Self, file_path: str):
        self.scripts: Dict[str, Template] = {}
        for file in os.listdir(file_path):
            _sql = open(f'{file_path}/{file}').read()
            self.scripts[file] = Template(_sql)

    def get(self: Self, filename: str, **kwargs) -> str:
        _sql = self.scripts[filename].substitute(**kwargs)
        return _sql

