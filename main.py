from system_info import SystemInfo
from metrics import SystemMetrics
from temperatures import TemperatureMonitor
from network import NetworkMonitor
from health import HealthMonitor


def main():
    system = SystemInfo()
    metrics = SystemMetrics()
    temperatures = TemperatureMonitor()
    network = NetworkMonitor()
    health = HealthMonitor()

    cpu_usage = metrics.get_cpu_usage()
    memory_usage = metrics.get_memory_usage()
    disk_usage = metrics.get_disk_usage()
    cpu_temperature = temperatures.get_cpu_temperature()
    internet_ping = network.get_ping_time("1.1.1.1")

    gateway = network.get_default_gateway()
    gateway_ping = network.get_ping_time(gateway)

    print("==============================")
    print("      SYSTEM INFORMATION")
    print("==============================")
    print(f"Hostname: {system.get_hostname()}")
    print(f"Operating System: {system.get_os()}")
    print(f"Kernel Version: {system.get_kernel()}")
    print(f"Architecture: {system.get_architecture()}")
    print(f"CPU Model: {system.get_cpu_model()}")

    print()
    print("==============================")
    print("      SYSTEM METRICS")
    print("==============================")
    print(
        f"CPU Usage: {cpu_usage}% - "
        f"{health.get_usage_status(cpu_usage)}"
    )
    print(
        f"Memory Usage: {memory_usage}% - "
        f"{health.get_usage_status(memory_usage)}"
    )
    print(
        f"Disk Usage: {disk_usage}% - "
        f"{health.get_usage_status(disk_usage)}"
    )

    if cpu_temperature is not None:
        temperature_status = health.get_temperature_status(cpu_temperature)
        print(
            f"CPU Temperature: {cpu_temperature:.1f}°C - "
            f"{temperature_status}"
        )
    else:
        print("CPU Temperature: Unavailable")

    print()
    print("==============================")
    print("      NETWORK INFORMATION")
    print("==============================")
    print(f"Interface: {network.get_active_interface()}")
    print(f"IP Address: {network.get_ip_address()}")
    print(f"Gateway: {gateway}")

    if gateway_ping is not None:
        print(f"Gateway Ping: {gateway_ping:.2f} ms")
    else:
        print("Gateway Ping: Unreachable")

    if internet_ping is not None:
        print("Internet Online")
        print(f"Internet Ping: {internet_ping:.2f} ms")
    else:
        print("Internet Offline")

if __name__ == "__main__":
    main()