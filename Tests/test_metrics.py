from temperatures import get_cpu_temperature
from metrics import get_cpu_usage, get_memory_usage, get_disk_usage
from health import get_temperature_status


def test_cpu_usage():
    value = get_cpu_usage()
    assert 0 <= value <= 100


def test_memory_usage():
    value = get_memory_usage()
    assert 0 <= value <= 100


def test_disk_usage():
    value = get_disk_usage()
    assert 0 <= value <= 100


def test_cpu_temperature():
    value = get_cpu_temperature()

    if value is not None:
        assert isinstance(value, (int, float))


def test_temperature_status():
    assert get_temperature_status(60) == "Healthy"
    assert get_temperature_status(75) == "Warning"
    assert get_temperature_status(90) == "Critical"