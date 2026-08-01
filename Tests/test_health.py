from health import HealthMonitor
from config import Config
import pytest


def test_healthy_status(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config = Config(config_file)
    health = HealthMonitor(config)

    assert health.get_usage_status(60) == "Healthy"
    assert health.get_usage_status(69) == "Healthy"


def test_warning_status(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config = Config(config_file)
    health = HealthMonitor(config)

    assert health.get_usage_status(70) == "Warning"
    assert health.get_usage_status(75) == "Warning"
    assert health.get_usage_status(89) == "Warning"


def test_critical_status(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config = Config(config_file)
    health = HealthMonitor(config)

    assert health.get_usage_status(90) == "Critical"
    assert health.get_usage_status(95) == "Critical"


def test_custom_thresholds(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[thresholds]\n'
        'usage_warning = 80\n'
        'usage_critical = 95\n'
    )
    config = Config(config_file)
    health = HealthMonitor(config)

    assert health.get_usage_status(75) == "Healthy"
    assert health.get_usage_status(80) == "Warning"
    assert health.get_usage_status(95) == "Critical"


def test_temperature_status() -> None:
    config = Config()
    health = HealthMonitor(config)

    assert health.get_temperature_status(60) == "Healthy"
    assert health.get_temperature_status(75) == "Warning"
    assert health.get_temperature_status(90) == "Critical"
