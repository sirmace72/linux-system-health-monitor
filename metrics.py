import psutil
from typing import Any

from config import Config


class SystemMetrics:
    """Collect resource usage statistics via psutil."""

    def __init__(self, config: Config | None = None) -> None:
        self._config = config or Config()

    def get_cpu_usage(self) -> float:
        return psutil.cpu_percent(interval=self._config.cpu_interval)

    def get_memory_usage(self) -> float:
        return psutil.virtual_memory().percent

    def get_disk_usage(self, path: str = "/") -> float:
        return psutil.disk_usage(path).percent

    def get_all_disk_usage(self) -> dict[str, float]:
        """Return usage % for all mounted partitions."""
        usage: dict[str, float] = {}
        partitions = psutil.disk_partitions(all=False)
        for part in partitions:
            try:
                usage[part.mountpoint] = psutil.disk_usage(part.mountpoint).percent
            except Exception:
                pass
        return usage

    @staticmethod
    def get_swap_usage() -> float:
        """Return swap memory usage percentage."""
        swap = psutil.swap_memory()
        return swap.percent

    @staticmethod
    def get_uptime_seconds() -> float:
        """Return system uptime in seconds."""
        boot_time = psutil.boot_time()
        import time
        return time.time() - boot_time


class ProcessMonitor:
    """Track top processes by CPU and memory usage."""

    @staticmethod
    def get_top_processes_by_cpu(n: int = 5) -> list[dict[str, Any]]:
        """Return top N processes by CPU usage."""
        processes: list[dict[str, Any]] = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                if info is not None:
                    processes.append({
                        "pid": info["pid"],
                        "name": info["name"] or "unknown",
                        "cpu_percent": info["cpu_percent"] or 0.0,
                        "memory_percent": info["memory_percent"] or 0.0,
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        processes.sort(key=lambda p: p["cpu_percent"], reverse=True)
        return processes[:n]

    @staticmethod
    def get_top_processes_by_memory(n: int = 5) -> list[dict[str, Any]]:
        """Return top N processes by memory usage."""
        processes: list[dict[str, Any]] = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                if info is not None:
                    processes.append({
                        "pid": info["pid"],
                        "name": info["name"] or "unknown",
                        "cpu_percent": info["cpu_percent"] or 0.0,
                        "memory_percent": info["memory_percent"] or 0.0,
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        processes.sort(key=lambda p: p["memory_percent"], reverse=True)
        return processes[:n]
