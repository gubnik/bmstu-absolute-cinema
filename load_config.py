import json
import os
from typing import Dict, List, Any
from dotenv import load_dotenv


def _resolve_env(value: Any) -> Any:
    """
    Recursively replace strings starting with $ with environment variable values.
    """
    if isinstance(value, str):
        print(f"'{value}'")
        print(f"'{value[1:]}'")
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
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        raise

    return _resolve_env(config)

def load_env_config(env: str) -> dict:
    load_dotenv(dotenv_path=".env", override=False)
    env_config = os.environ.get(env)
    print(env, env_config)
    return load_config(env_config) if env_config is not None else {}
