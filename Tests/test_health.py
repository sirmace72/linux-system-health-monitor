from health import HealthMonitor

health = HealthMonitor()
def test_healthy_status():
    assert health.get_usage_status(60) == "Healthy"
    assert health.get_usage_status(69) == "Healthy"


def test_warning_status():
    assert health.get_usage_status(70) == "Warning"
    assert health.get_usage_status(75) == "Warning"
    assert health.get_usage_status(89) == "Warning"


def test_critical_status():
    assert health.get_usage_status(90) == "Critical"
    assert health.get_usage_status(95) == "Critical"