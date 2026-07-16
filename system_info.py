import platform
import socket

class SystemInfo:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.os = f"{platform.system()} {platform.release()}"
        self.kernel = platform.version()
        self.architecture = platform.machine()
        self.cpu_model = self._get_cpu_model()

    def _get_cpu_model(self):
        with open("/proc/cpuinfo", "r") as file:
            for line in file:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
        return "Unknown CPU"

    def get_hostname(self):
        return self.hostname

    def get_os(self):
        return self.os

    def get_kernel(self):
        return self.kernel

    def get_architecture(self):
        return self.architecture

    def get_cpu_model(self):
        return self.cpu_model