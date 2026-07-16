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
    gateway = network.get_default_gateway()


    cpu_usage = metrics.get_cpu_usage()
    memory_usage = metrics.get_memory_usage()
    disk_usage = metrics.get_disk_usage()
    cpu_temperature = temperatures.get_cpu_temperature()


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
    print(
        f"CPU Temperature: "
        f"{cpu_temperature if cpu_temperature is not None else 'Unavailable'}°C - "
    f"{health.get_temperature_status(cpu_temperature) if cpu_temperature is not None else 'Unavailable'}"
  )
    print()
    print("==============================")
    print("      NETWORK INFORMATION")
    print("==============================")
    print(f"Interface: {network.get_active_interface()}")
    print(f"IP Address: {network.get_ip_address()}")
    print(f"Gateway: {network.get_default_gateway()}")
    gateway = network.get_default_gateway()
    ping_result = network.get_ping_time(gateway)

    print(f"Ping Time: {ping_result}ms")
          
if __name__ == "__main__":
    main()