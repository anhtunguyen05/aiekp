import os
import json
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".aiekp"
CONFIG_FILE = CONFIG_DIR / "config.json"

def _ensure_config_dir():
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def read_config() -> Dict[str, Any]:
    """Reads the global configuration from ~/.aiekp/config.json."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def write_config(key: str, value: str) -> None:
    """Writes a key-value pair to the global configuration."""
    _ensure_config_dir()
    config = read_config()
    config[key] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def inject_config_to_env() -> None:
    """Injects the global configuration into os.environ.
    Does not overwrite existing environment variables.
    """
    config = read_config()
    for key, value in config.items():
        if key not in os.environ:
            os.environ[key] = str(value)
