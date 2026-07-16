from health import get_health_status


def test_healthy_status():
    assert get_health_status(60) == "Healthy"
    assert get_health_status(69) == "Healthy"


def test_warning_status():
    assert get_health_status(70) == "Warning"
    assert get_health_status(75) == "Warning"
    assert get_health_status(89) == "Warning"


def test_critical_status():
    assert get_health_status(90) == "Critical"
    assert get_health_status(95) == "Critical"