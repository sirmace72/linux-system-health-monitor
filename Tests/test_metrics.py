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


def test_top_processes_by_cpu_uses_sampled_delta(monkeypatch) -> None:
    """Top-CPU list must rank by the sampled delta, not psutil's first-call 0.0."""
    import time

    import psutil

    class FakeProc:
        def __init__(self, pid: int, name: str, mem: float, target_cpu: float) -> None:
            self.pid = pid
            self.info = {"pid": pid, "name": name, "cpu_percent": 0.0, "memory_percent": mem}
            self._target = target_cpu
            self._calls = 0

        def cpu_percent(self, interval=None):
            # Mimic psutil: first call (priming) returns 0.0, later calls return
            # the utilization measured over the elapsed interval.
            self._calls += 1
            return 0.0 if self._calls == 1 else self._target

    # PIDs are deliberately NOT in busy order, so a stable sort on all-zero
    # values (the old bug) would keep PID order and fail this assertion.
    fakes = [
        FakeProc(pid=10, name="idle-low", mem=1.0, target_cpu=5.0),
        FakeProc(pid=20, name="busy", mem=2.0, target_cpu=90.0),
        FakeProc(pid=30, name="idle-mid", mem=3.0, target_cpu=10.0),
    ]

    def fake_process_iter(attrs=None, ad_value=None):
        return list(fakes)

    monkeypatch.setattr(psutil, "process_iter", fake_process_iter)
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)

    result = ProcessMonitor.get_top_processes_by_cpu(5)

    assert [p["name"] for p in result] == ["busy", "idle-mid", "idle-low"]
    assert [p["cpu_percent"] for p in result] == [90.0, 10.0, 5.0]
    for p in result:
        assert set(p) == {"pid", "name", "cpu_percent", "memory_percent"}
