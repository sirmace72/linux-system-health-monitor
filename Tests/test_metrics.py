from metrics import get_cpu_usage, get_memory_usage, get_disk_usage


def test_cpu_usage():
    value = get_cpu_usage()
    assert 0 <= value <= 100


def test_memory_usage():
    value = get_memory_usage()
    assert 0 <= value <= 100


def test_disk_usage():
    value = get_disk_usage()
    assert 0 <= value <= 100