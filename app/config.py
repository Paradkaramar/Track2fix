import os
import yaml
from pathlib import Path

_CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_config(env: str | None = None) -> dict:
    """Load configuration for the given environment name.

    Reads APP_ENV from the environment when *env* is not supplied.
    Falls back to 'dev' if APP_ENV is unset.
    """
    env = env or os.environ.get("APP_ENV", "dev")
    config_path = _CONFIG_DIR / f"{env}.yaml"
    with open(config_path, "r") as fh:
        return yaml.safe_load(fh) or {}


class Config:
    """Thin wrapper around a loaded YAML configuration dictionary."""

    def __init__(self, data: dict):
        self._data = data

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def require(self, key: str):
        value = self._data[key]
        return value


def get_config(env: str | None = None) -> Config:
    """Return a Config instance for the given environment."""
    return Config(load_config(env))
