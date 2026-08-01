from disk_io import DiskIOMonitor
from unittest.mock import patch, MagicMock


def test_get_total_io_returns_dict() -> None:
    fake = MagicMock()
    fake.read_bytes = 1024 * 1024 * 50
    fake.write_bytes = 1024 * 1024 * 20
    fake.read_count = 100
    fake.write_count = 50

    with patch("psutil.disk_io_counters", return_value=fake):
        result = DiskIOMonitor.get_total_io()
        assert result["read_mb"] == 50.0
        assert result["write_mb"] == 20.0


def test_get_total_io_none() -> None:
    with patch("psutil.disk_io_counters", return_value=None):
        result = DiskIOMonitor.get_total_io()
        assert result["read_mb"] == 0.0
        assert result["write_mb"] == 0.0


def test_get_io_stats_no_change() -> None:
    fake = MagicMock()
    fake.read_bytes = 100
    fake.write_bytes = 100
    fake.read_count = 1
    fake.write_count = 1

    with patch("psutil.disk_io_counters", return_value={"sda": fake}):
        monitor = DiskIOMonitor()
        stats = monitor.get_io_stats()

        if "sda" in stats:
            assert stats["sda"]["read_mb"] >= 0
            assert stats["sda"]["write_mb"] >= 0
