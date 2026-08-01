import subprocess
from unittest.mock import patch, MagicMock

from network import NetworkMonitor


def test_get_active_interface_eth0() -> None:
    monitor = NetworkMonitor()
    mock_result = MagicMock()
    mock_result.stdout = "default via 192.168.1.1 dev eth0 proto dhcp\n"
    with patch("subprocess.run", return_value=mock_result):
        assert monitor.get_active_interface() == "eth0"


def test_get_active_interface_none() -> None:
    monitor = NetworkMonitor()
    mock_result = MagicMock()
    mock_result.stdout = ""
    with patch("subprocess.run", return_value=mock_result):
        assert monitor.get_active_interface() is None


def test_get_ip_address() -> None:
    monitor = NetworkMonitor()

    def fake_run(cmd, **kwargs):
        if cmd == ["ip", "route"]:
            res = MagicMock()
            res.stdout = "default via 192.168.1.1 dev eth0 proto dhcp\n"
            return res
        if cmd == ["ip", "-4", "addr", "show", "eth0"]:
            res = MagicMock()
            res.stdout = "    inet 10.0.0.5/24 brd 10.0.0.255 scope global dynamic eth0\n"
            return res
        return MagicMock()

    with patch("subprocess.run", side_effect=fake_run):
        assert monitor.get_ip_address() == "10.0.0.5"


def test_get_ip_address_no_interface() -> None:
    monitor = NetworkMonitor()
    mock_result = MagicMock()
    mock_result.stdout = ""
    with patch("subprocess.run", return_value=mock_result):
        assert monitor.get_ip_address() is None


def test_get_default_gateway() -> None:
    monitor = NetworkMonitor()
    mock_result = MagicMock()
    mock_result.stdout = "default via 192.168.1.1 dev eth0 proto dhcp\n"
    with patch("subprocess.run", return_value=mock_result):
        assert monitor.get_default_gateway() == "192.168.1.1"


def test_get_default_gateway_none() -> None:
    monitor = NetworkMonitor()
    mock_result = MagicMock()
    mock_result.stdout = ""
    with patch("subprocess.run", return_value=mock_result):
        assert monitor.get_default_gateway() is None


def test_get_ping_time_success() -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "64 bytes from 1.1.1.1: icmp_seq=1 ttl=57 time=14.3 ms\n"
    with patch("subprocess.run", return_value=mock_result):
        result = NetworkMonitor.get_ping_time("1.1.1.1")
        assert result == 14.3


def test_get_ping_time_none_host() -> None:
    assert NetworkMonitor.get_ping_time(None) is None


def test_get_ping_time_failure() -> None:
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    with patch("subprocess.run", return_value=mock_result):
        result = NetworkMonitor.get_ping_time("10.255.255.1")
        assert result is None


def test_gateway_connection_status_success() -> None:
    monitor = NetworkMonitor()

    def fake_run(cmd, **kwargs):
        if cmd == ["ip", "route"]:
            res = MagicMock()
            res.stdout = "default via 192.168.1.1 dev eth0\n"
            return res
        if cmd == ["ping", "-c", "1", "192.168.1.1"]:
            res = MagicMock()
            res.returncode = 0
            return res
        return MagicMock()

    with patch("subprocess.run", side_effect=fake_run):
        status = monitor.get_gateway_connection_status()
        assert "Successfully connected" in status


def test_gateway_connection_status_no_gateway() -> None:
    monitor = NetworkMonitor()
    mock_result = MagicMock()
    mock_result.stdout = ""
    with patch("subprocess.run", return_value=mock_result):
        status = monitor.get_gateway_connection_status()
        assert "No default gateway" in status
