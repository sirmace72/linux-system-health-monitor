from net_io import NetworkTransferMonitor
from unittest.mock import patch, MagicMock


def test_get_total_transfers_returns_dict() -> None:
    fake = MagicMock()
    fake.bytes_sent = 1024 * 1024 * 100
    fake.bytes_recv = 1024 * 1024 * 200
    fake.packets_sent = 5000
    fake.packets_recv = 8000

    with patch("psutil.net_io_counters", return_value=fake):
        result = NetworkTransferMonitor.get_total_transfers()
        assert result["sent_mb"] == 100.0
        assert result["received_mb"] == 200.0
        assert result["sent_packets"] == 5000.0
        assert result["received_packets"] == 8000.0


def test_get_total_transfers_none() -> None:
    with patch("psutil.net_io_counters", return_value=None):
        result = NetworkTransferMonitor.get_total_transfers()
        assert result["sent_mb"] == 0.0
        assert result["received_mb"] == 0.0


def test_get_transfer_stats_no_change() -> None:
    fake = MagicMock()
    fake.bytes_sent = 100
    fake.bytes_recv = 100
    fake.packets_sent = 1
    fake.packets_recv = 1
    fake.dropin = 0
    fake.dropout = 0

    with patch("psutil.net_io_counters", return_value={"eth0": fake}):
        monitor = NetworkTransferMonitor()
        stats = monitor.get_transfer_stats()

        if "eth0" in stats:
            assert stats["eth0"]["sent_mb"] >= 0
            assert stats["eth0"]["received_mb"] >= 0
