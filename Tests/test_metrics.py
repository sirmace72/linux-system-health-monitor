from temperatures import TemperatureMonitor
from metrics import SystemMetrics
from health import HealthMonitor


health = HealthMonitor()
metrics = SystemMetrics()
temperatures = TemperatureMonitor()


def test_cpu_usage():
    value = metrics.get_cpu_usage()
    assert 0 <= value <= 100


def test_memory_usage():
    value = metrics.get_memory_usage()
    assert 0 <= value <= 100


def test_disk_usage():
    value = metrics.get_disk_usage()
    assert 0 <= value <= 100


def test_cpu_temperature():
    value = temperatures.get_cpu_temperature()

    if value is not None:
        assert isinstance(value, (int, float))


def test_temperature_status():
    assert health.get_temperature_status(60) == "Healthy"
    assert health.get_temperature_status(75) == "Warning"
    assert health.get_temperature_status(90) == "Critical"