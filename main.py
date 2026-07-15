# main.py

from system_info import get_hostname, get_os, get_cpu_model
from system_info import get_kernel, get_architecture

print(f"==============================")
print(f"      SYSTEM INFORMATION")
print(f"==============================")
print(f"Hostname: {get_hostname()}")
print(f"Operating System: {get_os()}")
print(f"Kernel Version: {get_kernel()}")
print(f"Architecture: {get_architecture()}")
print(f"CPU Model: {get_cpu_model()}")