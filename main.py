# main.py

from system_info import (
    get_hostname,
    get_os,
    get_kernel,
    get_architecture,
    get_cpu_model,

)
import metrics
import health

cpu_usage = metrics.get_cpu_usage()
memory_usage = metrics.get_memory_usage()
disk_usage = metrics.get_disk_usage()

print(f"==============================")
print(f"      SYSTEM INFORMATION")
print(f"==============================")
print(f"Hostname: {get_hostname()}")
print(f"Operating System: {get_os()}")
print(f"Kernel Version: {get_kernel()}")
print(f"Architecture: {get_architecture()}")
print(f"CPU Model: {get_cpu_model()}")
print()
print(f"==============================")
print(f"      SYSTEM METRICS")
print(f"==============================")
print(f"CPU Usage: {cpu_usage}% - {health.get_health_status(cpu_usage)}")
print(f"Memory Usage: {memory_usage}% - {health.get_health_status(memory_usage)}")
print(f"Disk Usage: {disk_usage}% - {health.get_health_status(disk_usage)}")