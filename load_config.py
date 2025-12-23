import json
import os
from typing import Any
from dotenv import load_dotenv
from dataclasses import dataclass

@dataclass
class MtimeCache:
    mtime: float
    data: dict

_configs_mtime_cache: dict[str, MtimeCache] = {}

def _resolve_env(value: Any) -> Any:
    """
    Recursively replace strings starting with $ with environment variable values.
    """
    if isinstance(value, str):
        if value.startswith("$"):
            return os.environ.get(value[1:], "")
        return value
    if isinstance(value, dict):
        return {k: _resolve_env(v) for k, v in value.items()}
    return value


def load_config(path: str) -> dict:
    """
    Load JSON config from path. For any string value starting with '$',
    replace it with the corresponding environment variable's value
    (empty string if the env var is not set). Works recursively for nested
    dicts and lists.
    """
    load_dotenv(dotenv_path=".env", override=False)
    try:
        mtime = os.path.getmtime(path)
        if path in _configs_mtime_cache and mtime == _configs_mtime_cache[path].mtime:
            return _resolve_env(_configs_mtime_cache[path].data)
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
            _configs_mtime_cache[path] = MtimeCache(mtime=mtime, data=config)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        raise

    return _resolve_env(config)

def load_env_config(env: str) -> dict:
    """
    Loads a config from an env var
    """
    load_dotenv(dotenv_path=".env", override=False)
    env_config = os.environ.get(env)
    return load_config(env_config) if env_config is not None else {}
