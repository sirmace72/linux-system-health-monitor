import psutil

def get_cpu_usage():
    """
    Get the current CPU usage percentage.

    Returns:
        float: The current CPU usage percentage.
    """
    
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    """
    Get the current memory usage percentage.

    Returns:
        float: The current memory usage percentage.
    """
    memory = psutil.virtual_memory()
    return memory.percent

def get_disk_usage():
    """
    Get the current disk usage percentage.

    Returns:
        float: The current disk usage percentage.
    """
    disk = psutil.disk_usage('/')
    return disk.percent