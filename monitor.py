from system_info import SystemInfo
from metrics import SystemMetrics
from temperatures import TemperatureMonitor
from network import NetworkMonitor
from health import HealthMonitor


class SystemHealthMonitor:
    def __init__(self):
        self.system = SystemInfo()
        self.metrics = SystemMetrics()
        self.temperatures = TemperatureMonitor()
        self.network = NetworkMonitor()
        self.health = HealthMonitor()

    def get_system_report(self) -> dict:
        hostname = self.system.get_hostname()
        cpu_usage = self.metrics.get_cpu_usage()
        cpu_status = self.health.get_usage_status(cpu_usage)
        memory_usage = self.metrics.get_memory_usage()
        memory_status = self.health.get_usage_status(memory_usage)
        disk_usage = self.metrics.get_disk_usage()
        disk_status = self.health.get_usage_status(disk_usage)  
        cpu_temperature = self.temperatures.get_cpu_temperature()
        temperature_status = (
            self.health.get_temperature_status(cpu_temperature)
            if cpu_temperature is not None
            else "Unavailable"
        )
        interface = self.network.get_active_interface()
        ip_address = self.network.get_ip_address()
        gateway = self.network.get_default_gateway()
        gateway_ping = self.network.get_ping_time(gateway)
        internet_ping = self.network.get_ping_time("1.1.1.1")

        report = {
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
            "gateway_ping": gateway_ping
        }
        return report
