import psutil


class SystemMetrics:
    """Collect resource usage statistics via psutil."""

    def get_cpu_usage(self) -> float:
        return psutil.cpu_percent(interval=0.5)

    def get_memory_usage(self) -> float:
        return psutil.virtual_memory().percent

    def get_disk_usage(self, path: str = "/") -> float:
        return psutil.disk_usage(path).percent
