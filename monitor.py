from typing import Any

from config import Config
from system_info import SystemInfo
from metrics import SystemMetrics, ProcessMonitor
from temperatures import TemperatureMonitor
from network import NetworkMonitor
from net_io import NetworkTransferMonitor
from disk_io import DiskIOMonitor
from gpu import GPUMonitor
from health import HealthMonitor
from smart_health import SMARTMonitor


class SystemHealthMonitor:
    """Orchestrates all monitoring components and produces a unified report."""

    def __init__(self, config: Config | None = None) -> None:
        self._config = config or Config()
        self.system = SystemInfo()
        self.metrics = SystemMetrics(self._config)
        self.temperatures = TemperatureMonitor()
        self.network = NetworkMonitor()
        self.health = HealthMonitor(self._config)
        self.net_io = NetworkTransferMonitor()
        self.disk_io = DiskIOMonitor()
        self.gpu = GPUMonitor()
        self.processes = ProcessMonitor()
        self.smart = SMARTMonitor()

    def get_system_report(self) -> dict[str, Any]:
        """Collect all metrics and return a unified report dict."""
        hostname = self.system.get_hostname()
        cpu_usage = self.metrics.get_cpu_usage()
        cpu_status = self.health.get_usage_status(cpu_usage)
        memory_usage = self.metrics.get_memory_usage()
        memory_status = self.health.get_usage_status(memory_usage)
        disk_usage = self.metrics.get_disk_usage()
        disk_status = self.health.get_usage_status(disk_usage)
        cpu_temperature = self.temperatures.get_cpu_temperature()
        temperature_status: str
        if cpu_temperature is not None:
            temperature_status = self.health.get_temperature_status(cpu_temperature)
        else:
            temperature_status = "Unavailable"

        interface = self.network.get_active_interface()
        ip_address = self.network.get_ip_address()
        gateway = self.network.get_default_gateway()
        gateway_ping = self.network.get_ping_time(gateway)
        internet_ping = self.network.get_ping_time(self._config.internet_ping_host)

        report: dict[str, Any] = {
            "hostname": hostname,
            "cpu_usage": cpu_usage,
            "cpu_status": cpu_status,
            "memory_usage": memory_usage,
            "memory_status": memory_status,
            "disk_usage": disk_usage,
            "disk_status": disk_status,
            "temperature_status": temperature_status,
            "cpu_temperature": cpu_temperature,
            "internet_ping": internet_ping,
            "interface": interface,
            "ip_address": ip_address,
            "gateway": gateway,
            "gateway_ping": gateway_ping,
        }

        # Additional disk partitions
        if self._config.check_all_partitions:
            report["all_disk_usage"] = self.metrics.get_all_disk_usage()

        # Swap usage
        report["swap_usage"] = self.metrics.get_swap_usage()

        # Uptime
        report["uptime_seconds"] = self.metrics.get_uptime_seconds()

        # GPU info (only if enabled)
        if self._config.show_gpu:
            report["gpu_info"] = self.gpu.get_gpu_info()

        # Disk IO stats
        if self._config.show_disk_io:
            report["disk_io"] = self.disk_io.get_io_stats()
            report["disk_io_total"] = self.disk_io.get_total_io()

        # Network transfer stats
        if self._config.show_net_io:
            report["net_io"] = self.net_io.get_transfer_stats()
            report["net_io_total"] = self.net_io.get_total_transfers()

        # Top processes (only if enabled)
        if self._config.show_process:
            n = self._config.top_n_processes
            report["top_cpu"] = self.processes.get_top_processes_by_cpu(n)
            report["top_memory"] = self.processes.get_top_processes_by_memory(n)

        # SMART health (only if enabled)
        if self._config.show_smart:
            report["smart_health"] = self.smart.get_smart_health()

        return report
