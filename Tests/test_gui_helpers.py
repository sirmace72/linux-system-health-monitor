"""Tests for the GTK-free GUI helpers (gui_helpers.py)."""

import pytest

from gui_helpers import (
    UNAVAILABLE,
    build_snapshot,
    empty_snapshot,
    format_bool,
    format_bytes,
    format_percent,
    format_ping_ms,
    format_temp,
    format_uptime,
    gpu_rows,
    status_style,
    usage_value,
)


class TestFormatters:
    def test_percent(self):
        assert format_percent(12.34) == "12.3%"
        assert format_percent(0) == "0.0%"
        assert format_percent(100) == "100.0%"

    def test_percent_invalid(self):
        assert format_percent(None) == UNAVAILABLE
        assert format_percent("n/a") == UNAVAILABLE
        assert format_percent(float("nan")) == UNAVAILABLE

    def test_temp(self):
        assert format_temp(62.5) == "62.5 °C"
        assert format_temp(None) == UNAVAILABLE

    def test_ping(self):
        assert format_ping_ms(12.5) == "12.5 ms"
        assert format_ping_ms(-1) == UNAVAILABLE
        assert format_ping_ms(None) == UNAVAILABLE

    def test_uptime(self):
        assert format_uptime(0) == "0m"
        assert format_uptime(3661) == "1h 1m"
        assert format_uptime(93722) == "1d 2h 2m"
        assert format_uptime(-5) == UNAVAILABLE
        assert format_uptime(None) == UNAVAILABLE

    def test_bytes(self):
        assert format_bytes(512) == "512 B"
        assert format_bytes(1536) == "1.5 KB"
        assert format_bytes(3 * 1024**3) == "3.0 GB"
        assert format_bytes(-1) == UNAVAILABLE
        assert format_bytes(None) == UNAVAILABLE

    def test_bool(self):
        assert format_bool(True) == "Yes"
        assert format_bool(False) == "No"
        assert format_bool(None) == UNAVAILABLE

    def test_usage_value_clamps(self):
        assert usage_value(42) == 42.0
        assert usage_value(-10) == 0.0
        assert usage_value(150) == 100.0
        assert usage_value(None) is None


class TestStatusStyle:
    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            ("healthy", "healthy"),
            ("HEALTHY", "healthy"),
            ("warning", "warning"),
            ("critical", "critical"),
            ("unknown", "unknown"),
            ("weird value", "unknown"),
            (None, "unknown"),
            (123, "unknown"),
        ],
    )
    def test_status_style(self, status, expected):
        assert status_style(status) == expected


class TestGpuRows:
    def test_nvidia_like(self):
        rows = gpu_rows(
            [
                {
                    "vendor": "NVIDIA",
                    "name": "NVIDIA GeForce RTX 4060",
                    "temp": 55.0,
                    "usage": 10.0,
                    "mem_used": 2 * 1024**3,
                    "mem_total": 8 * 1024**3,
                }
            ]
        )
        assert len(rows) == 1
        assert rows[0]["label"] == "NVIDIA GeForce RTX 4060"
        assert rows[0]["vendor"] == "NVIDIA"
        assert rows[0]["temp"] == "55.0 °C"
        assert rows[0]["usage"] == "10.0%"
        assert rows[0]["usage_value"] == 10.0
        assert rows[0]["mem"] == "2.0 GB / 8.0 GB"

    def test_amd_without_mem(self):
        rows = gpu_rows([{"vendor": "AMD", "name": "Radeon", "temp": 45.0, "usage": 0.0}])
        assert rows[0]["mem"] == UNAVAILABLE

    def test_multiple_gpus(self):
        rows = gpu_rows(
            [
                {"vendor": "AMD", "name": "GPU One", "temp": 40.0, "usage": 1.0},
                {"vendor": "NVIDIA", "name": "GPU Two", "temp": 41.0, "usage": 2.0},
            ]
        )
        assert [row["label"] for row in rows] == ["GPU One", "GPU Two"]

    def test_invalid_inputs(self):
        assert gpu_rows(None) == []
        assert gpu_rows("nonsense") == []
        assert gpu_rows([42, None, {"name": 123}]) == [
            {"label": "123", "vendor": UNAVAILABLE, "temp": UNAVAILABLE, "usage": UNAVAILABLE, "usage_value": None, "mem": UNAVAILABLE}
        ]

    def test_missing_name_falls_back_to_index(self):
        rows = gpu_rows([{"vendor": "AMD"}])
        assert rows[0]["label"] == "GPU 1"


class TestBuildSnapshot:
    REPORT = {
        "cpu_usage": 12.0,
        "cpu_status": "healthy",
        "memory_usage": 45.5,
        "memory_status": "healthy",
        "disk_usage": 70.25,
        "disk_status": "warning",
        "cpu_temperature": 58.0,
        "temperature_status": "healthy",
        "interface": "eth0",
        "ip_address": "192.168.1.42",
        "gateway": "192.168.1.1",
        "gateway_ping": 0.5,
        "internet_ping": 12.3,
        "uptime_seconds": 93722,
        "gpu_info": [{"vendor": "AMD", "name": "Radeon", "temp": 45.0, "usage": 3.0}],
    }
    SYSINFO = {
        "hostname": "laptop",
        "os": "Linux 24.04",
        "kernel": "6.8.0-generic",
        "cpu_model": "Ryzen 9 7940HS",
        "architecture": "x86_64",
    }

    def test_full_report(self):
        snap = build_snapshot(self.REPORT, self.SYSINFO)
        assert snap["cpu"]["usage"] == "12.0%"
        assert snap["cpu"]["status"] == "healthy"
        assert snap["memory"]["usage"] == "45.5%"
        assert snap["disk"]["usage"] == "70.2%"  # 70.25 rounds to even
        assert snap["disk"]["status"] == "warning"
        assert snap["temperature"]["value"] == "58.0 °C"
        assert snap["active_interface"] == "eth0"
        assert snap["ip_address"] == "192.168.1.42"
        assert snap["gateway"] == "192.168.1.1"
        assert snap["gateway_reachable"] == "Yes"
        assert snap["internet_connected"] == "Yes"
        assert snap["ping_time"] == "12.3 ms"
        assert snap["uptime"] == "1d 2h 2m"
        assert snap["hostname"] == "laptop"
        assert snap["os"] == "Linux 24.04"
        assert len(snap["gpus"]) == 1

    def test_missing_values_become_unavailable(self):
        snap = build_snapshot({}, {})
        assert snap["cpu"]["usage"] == UNAVAILABLE
        assert snap["cpu"]["status"] == UNAVAILABLE
        assert snap["cpu"]["usage_value"] is None
        assert snap["temperature"]["value"] == UNAVAILABLE
        assert snap["active_interface"] == UNAVAILABLE
        assert snap["gateway_reachable"] == UNAVAILABLE
        assert snap["internet_connected"] == UNAVAILABLE
        assert snap["ping_time"] == UNAVAILABLE
        assert snap["uptime"] == UNAVAILABLE
        assert snap["gpus"] == []
        assert snap["hostname"] == UNAVAILABLE

    def test_ping_failure_is_unavailable(self):
        snap = build_snapshot({"internet_ping": None, "gateway_ping": None}, None)
        assert snap["internet_connected"] == UNAVAILABLE
        assert snap["gateway_reachable"] == UNAVAILABLE
        snap = build_snapshot({"internet_ping": -1}, None)
        assert snap["internet_connected"] == UNAVAILABLE

    def test_none_report_and_sysinfo(self):
        snap = build_snapshot(None, None)
        assert snap == empty_snapshot()


class TestEmptySnapshot:
    def test_keys(self):
        snap = empty_snapshot()
        assert set(snap.keys()) == {
            "cpu",
            "memory",
            "disk",
            "temperature",
            "active_interface",
            "ip_address",
            "gateway",
            "gateway_reachable",
            "internet_connected",
            "ping_time",
            "gpus",
            "hostname",
            "os",
            "kernel",
            "cpu_model",
            "architecture",
            "uptime",
        }
        assert snap["cpu"]["usage"] == UNAVAILABLE
        assert snap["gpus"] == []
