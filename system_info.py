def get_hostname():
    """
    Get the hostname of the current machine.

    Returns:
        str: The hostname of the machine.
    """
    import socket
    return socket.gethostname()

def get_os():
    """
    Get the operating system name and version.

    Returns:
        str: The operating system name and version.
    """
    import platform
    return f"{platform.system()} {platform.release()}"

def get_kernel():
    """
    Get the kernel version of the operating system.

    Returns:
        str: The kernel version.
    """
    import platform
    return platform.version()

def get_architecture():
    """
    Get the architecture of the operating system.

    Returns:
        str: The architecture (e.g., 'x86_64', 'arm64').
    """
    import platform
    return platform.machine()

def get_cpu_model():
    """
    Get the CPU model of the current machine.

    Returns:
        str: The CPU model.
    """
    with open("/proc/cpuinfo", "r") as file:
        for line in file:
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()

    return "Unknown CPU"