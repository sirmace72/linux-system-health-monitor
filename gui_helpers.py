"""GTK-free helpers that turn raw report values into display strings.

These functions are pure (no GTK imports) so they can be unit tested
without a display.  The GUI layer builds a flat "snapshot" dict with
``build_snapshot()`` and applies it to widgets on the GTK main thread.
"""

import math
from typing import Any

UNAVAILABLE = "Unavailable"

# Status values produced by health.py / monitor.py
STATUS_HEALTHY = "healthy"
STATUS_WARNING = "warning"
STATUS_CRITICAL = "critical"
STATUS_UNKNOWN = "unknown"


def _is_number(value: Any) -> bool:
    """True for finite int/float values (bools excluded)."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _text(value: Any) -> str:
    """Stringify a value, falling back to UNAVAILABLE."""
    if value is None or isinstance(value, bool):
        return UNAVAILABLE
    if _is_number(value):
        return str(value)
    text = str(value).strip()
    return text if text else UNAVAILABLE


def format_percent(value: Any) -> str:
    """Format a 0-100 percentage value as e.g. ``12.3%``."""
    if not _is_number(value):
        return UNAVAILABLE
    return f"{float(value):.1f}%"


def format_temp(value: Any) -> str:
    """Format a temperature in °C as e.g. ``62.5 °C``."""
    if not _is_number(value):
        return UNAVAILABLE
    return f"{float(value):.1f} °C"


def format_ping_ms(value: Any) -> str:
    """Format a ping time in milliseconds as e.g. ``12.5 ms``."""
    if not _is_number(value) or float(value) < 0:
        return UNAVAILABLE
    return f"{float(value):.1f} ms"


def format_uptime(seconds: Any) -> str:
    """Format an uptime in seconds as e.g. ``1d 14h 22m``."""
    if not _is_number(seconds) or float(seconds) < 0:
        return UNAVAILABLE
    total = int(seconds)
    days, remainder = divmod(total, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if days or hours:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def format_bytes(value: Any) -> str:
    """Format a byte count with one decimal, e.g. ``1.5 GB``."""
    if not _is_number(value) or float(value) < 0:
        return UNAVAILABLE
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if size < 1024.0 or unit == "PB":
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return UNAVAILABLE  # unreachable


def format_bool(value: Any) -> str:
    """Format a boolean connectivity flag as Yes/No."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return UNAVAILABLE


def status_style(status: Any) -> str:
    """Map a health status string to a CSS class suffix."""
    if not isinstance(status, str):
        return STATUS_UNKNOWN
    normalized = status.strip().lower()
    if normalized in ("healthy", "ok", "good"):
        return STATUS_HEALTHY
    if normalized in ("warning", "warn"):
        return STATUS_WARNING
    if normalized in ("critical", "danger", "unhealthy"):
        return STATUS_CRITICAL
    return STATUS_UNKNOWN


def usage_value(value: Any) -> float | None:
    """Clamp a percentage to [0, 100] for a Gtk.ProgressBar, else None."""
    if not _is_number(value):
        return None
    return max(0.0, min(100.0, float(value)))


def _mem_text(gpu: dict[str, Any]) -> str:
    used = gpu.get("mem_used")
    total = gpu.get("mem_total")
    if not _is_number(used) or not _is_number(total):
        return UNAVAILABLE
    return f"{format_bytes(used)} / {format_bytes(total)}"


def gpu_rows(gpu_info: Any) -> list[dict[str, Any]]:
    """Normalize the ``gpu_info`` list into display-ready row dicts.

    Handles no GPUs, one GPU, or multiple GPUs of any vendor.  Missing
    fields render as UNAVAILABLE instead of raising.
    """
    if not isinstance(gpu_info, list):
        return []

    rows: list[dict[str, Any]] = []
    for index, gpu in enumerate(gpu_info):
        if not isinstance(gpu, dict):
            continue
        name = _text(gpu.get("name"))
        rows.append(
            {
                "label": name if name != UNAVAILABLE else f"GPU {index + 1}",
                "vendor": _text(gpu.get("vendor")),
                "temp": format_temp(gpu.get("temp")),
                "usage": format_percent(gpu.get("usage")),
                "usage_value": usage_value(gpu.get("usage")),
                "mem": _mem_text(gpu),
            }
        )
    return rows


def _reachable(ping: Any) -> str:
    """A successful (non-negative) ping time means reachable; a failed
    ping is reported as UNAVAILABLE rather than a definitive No."""
    if _is_number(ping) and float(ping) >= 0:
        return format_bool(True)
    return UNAVAILABLE


def _metric(usage: Any, status: Any) -> dict[str, Any]:
    return {
        "usage": format_percent(usage),
        "usage_value": usage_value(usage),
        "status": _text(status),
    }


def build_snapshot(report: Any, sysinfo: dict[str, Any] | None) -> dict[str, Any]:
    """Build a flat, fully stringified snapshot from a system report.

    ``report`` is the dict returned by
    ``SystemHealthMonitor.get_system_report()`` and ``sysinfo`` holds the
    static system values collected once at startup.  Any missing or
    invalid value becomes UNAVAILABLE; this never raises.
    """
    report = report if isinstance(report, dict) else {}
    sysinfo = sysinfo if isinstance(sysinfo, dict) else {}

    return {
        "cpu": _metric(report.get("cpu_usage"), report.get("cpu_status")),
        "memory": _metric(report.get("memory_usage"), report.get("memory_status")),
        "disk": _metric(report.get("disk_usage"), report.get("disk_status")),
        "temperature": {
            "value": format_temp(report.get("cpu_temperature")),
            "status": _text(report.get("temperature_status")),
        },
        "active_interface": _text(report.get("interface")),
        "ip_address": _text(report.get("ip_address")),
        "gateway": _text(report.get("gateway")),
        "gateway_reachable": _reachable(report.get("gateway_ping")),
        "internet_connected": _reachable(report.get("internet_ping")),
        "ping_time": format_ping_ms(report.get("internet_ping")),
        "gpus": gpu_rows(report.get("gpu_info")),
        "hostname": _text(sysinfo.get("hostname")),
        "os": _text(sysinfo.get("os")),
        "kernel": _text(sysinfo.get("kernel")),
        "cpu_model": _text(sysinfo.get("cpu_model")),
        "architecture": _text(sysinfo.get("architecture")),
        "uptime": format_uptime(report.get("uptime_seconds")),
    }


def empty_snapshot() -> dict[str, Any]:
    """A snapshot where every value is UNAVAILABLE (refresh failed)."""
    unavailable_metric = {
        "usage": UNAVAILABLE,
        "usage_value": None,
        "status": UNAVAILABLE,
    }
    return {
        "cpu": dict(unavailable_metric),
        "memory": dict(unavailable_metric),
        "disk": dict(unavailable_metric),
        "temperature": {"value": UNAVAILABLE, "status": UNAVAILABLE},
        "active_interface": UNAVAILABLE,
        "ip_address": UNAVAILABLE,
        "gateway": UNAVAILABLE,
        "gateway_reachable": UNAVAILABLE,
        "internet_connected": UNAVAILABLE,
        "ping_time": UNAVAILABLE,
        "gpus": [],
        "hostname": UNAVAILABLE,
        "os": UNAVAILABLE,
        "kernel": UNAVAILABLE,
        "cpu_model": UNAVAILABLE,
        "architecture": UNAVAILABLE,
        "uptime": UNAVAILABLE,
    }
