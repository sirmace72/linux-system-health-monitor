from metrics import SystemMetrics, ProcessMonitor


def test_cpu_usage() -> None:
    metrics = SystemMetrics()
    value = metrics.get_cpu_usage()
    assert 0 <= value <= 100


def test_memory_usage() -> None:
    metrics = SystemMetrics()
    value = metrics.get_memory_usage()
    assert 0 <= value <= 100


def test_disk_usage() -> None:
    metrics = SystemMetrics()
    value = metrics.get_disk_usage()
    assert 0 <= value <= 100


def test_disk_usage_custom_path() -> None:
    metrics = SystemMetrics()
    value = metrics.get_disk_usage("/")
    assert 0 <= value <= 100


def test_all_disk_usage_returns_dict() -> None:
    metrics = SystemMetrics()
    result = metrics.get_all_disk_usage()
    assert isinstance(result, dict)
    assert len(result) > 0


def test_swap_usage() -> None:
    metrics = SystemMetrics()
    value = metrics.get_swap_usage()
    assert isinstance(value, (int, float))


def test_uptime_seconds() -> None:
    metrics = SystemMetrics()
    value = metrics.get_uptime_seconds()
    assert value > 0


def test_top_processes_by_cpu() -> None:
    procs = ProcessMonitor.get_top_processes_by_cpu(3)
    assert isinstance(procs, list)
    assert len(procs) <= 3
    for p in procs:
        assert "pid" in p
        assert "name" in p


def test_top_processes_by_memory() -> None:
    procs = ProcessMonitor.get_top_processes_by_memory(3)
    assert isinstance(procs, list)
    assert len(procs) <= 3
    for p in procs:
        assert "pid" in p
        assert "name" in p
