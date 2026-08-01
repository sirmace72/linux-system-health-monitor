#!/usr/bin/env python3
"""Configuration loader for TOML config file."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.toml"


class Config:
    """Load and provide access to configuration from config.toml."""

    def __init__(self, config_path: Path | str | None = None) -> None:
        if config_path is not None:
            self._config_path = Path(config_path)
        else:
            self._config_path = _DEFAULT_CONFIG_PATH

        self._data: dict[str, Any] = self._load()

    # -- thresholds --

    @property
    def usage_warning(self) -> float:
        return float(self._get("thresholds", "usage_warning"))

    @property
    def usage_critical(self) -> float:
        return float(self._get("thresholds", "usage_critical"))

    @property
    def temp_warning(self) -> float:
        return float(self._get("thresholds", "temp_warning"))

    @property
    def temp_critical(self) -> float:
        return float(self._get("thresholds", "temp_critical"))

    # -- report --

    @property
    def history_file(self) -> str:
        return str(self._get("report", "history_file"))

    @property
    def cpu_interval(self) -> float:
        return float(self._get("report", "cpu_interval"))

    @property
    def check_all_partitions(self) -> bool:
        return bool(self._get("report", "check_all_partitions"))

    @property
    def internet_ping_host(self) -> str:
        return str(self._get("report", "internet_ping_host"))

    # -- display --

    @property
    def show_gpu(self) -> bool:
        return bool(self._get("display", "show_gpu"))

    @property
    def show_disk_io(self) -> bool:
        return bool(self._get("display", "show_disk_io"))

    @property
    def show_net_io(self) -> bool:
        return bool(self._get("display", "show_net_io"))

    # -- internal --

    def _load(self) -> dict[str, Any] | None:
        try:
            import tomllib  # stdlib in 3.11+
        except ImportError:
            import tomli as tomllib  # pip install tomli as fallback

        if self._config_path.exists():
            logger.info("Loading config from %s", self._config_path)
            with open(self._config_path, "rb") as f:
                return tomllib.load(f)
        else:
            logger.warning(
                "Config file not found at %s, using defaults", self._config_path
            )
            return None

    def _get(self, section: str, key: str) -> Any:
        if self._data and section in self._data:
            return self._data[section].get(key, _DEFAULTS.get(section, {}).get(key))
        return _DEFAULTS.get(section, {}).get(key)

    def __repr__(self) -> str:
        return f"Config(path={self._config_path})"


# Default values when config file is missing
_DEFAULTS: dict[str, dict[str, Any]] = {
    "thresholds": {
        "usage_warning": 70.0,
        "usage_critical": 90.0,
        "temp_warning": 70.0,
        "temp_critical": 85.0,
    },
    "report": {
        "history_file": "history.json",
        "cpu_interval": 0.5,
        "check_all_partitions": True,
        "internet_ping_host": "1.1.1.1",
    },
    "display": {
        "show_gpu": True,
        "show_disk_io": True,
        "show_net_io": True,
    },
}
