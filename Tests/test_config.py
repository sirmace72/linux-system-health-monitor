from config import Config


def test_default_config() -> None:
    config = Config()
    assert config.usage_warning == 70.0
    assert config.usage_critical == 90.0
    assert config.temp_warning == 70.0
    assert config.temp_critical == 85.0


def test_missing_config_file_returns_defaults(tmp_path) -> None:
    missing = tmp_path / "nonexistent.toml"
    config = Config(missing)
    assert config.usage_warning == 70.0
    assert config.history_file == "history.json"


def test_custom_config(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[thresholds]\n'
        'usage_warning = 80\n'
        'usage_critical = 95\n'
        'temp_warning = 75\n'
        'temp_critical = 90\n'
        '\n[report]\n'
        'history_file = "custom.json"\n'
        'cpu_interval = 1.0\n'
    )
    config = Config(config_file)
    assert config.usage_warning == 80.0
    assert config.usage_critical == 95.0
    assert config.temp_warning == 75.0
    assert config.temp_critical == 90.0
    assert config.history_file == "custom.json"
    assert config.cpu_interval == 1.0


def test_display_flags(tmp_path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        '[display]\n'
        'show_gpu = false\n'
        'show_disk_io = false\n'
        'show_net_io = false\n'
    )
    config = Config(config_file)
    assert config.show_gpu is False
    assert config.show_disk_io is False
    assert config.show_net_io is False
