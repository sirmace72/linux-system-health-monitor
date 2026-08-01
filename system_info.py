import platform
import socket

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class SystemInfo:
    """Collect basic system metadata."""

    def __init__(self) -> None:
        self.hostname: str = socket.gethostname()
        self.os: str = f"{platform.system()} {platform.release()}"
        self.kernel: str = platform.version()
        self.architecture: str = platform.machine()
        self.cpu_model: str = self._get_cpu_model()

    @staticmethod
    def _get_cpu_model() -> str:
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as file:
                for line in file:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass
        return "Unknown CPU"

    def get_hostname(self) -> str:
        return self.hostname

    def get_os(self) -> str:
        return self.os

    def get_kernel(self) -> str:
        return self.kernel

    def get_architecture(self) -> str:
        return self.architecture

    def get_cpu_model(self) -> str:
        return self.cpu_model
