import os
from string import Template
from typing import Dict

class SQLProvider:

    def __init__(self, file_path):
        self.scripts: Dict[str, Template] = {}
        for file in os.listdir(file_path):
            _sql = open(f'{file_path}/{file}').read()
            self.scripts[file] = Template(_sql)

    def get(self, file: str, **kwargs) -> str:
        _sql = self.scripts[file].substitute(**kwargs)
        return _sql

