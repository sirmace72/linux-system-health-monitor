def get_health_status(value):
    """
    Get the overall health status of the system based on CPU, memory, and disk usage.

    Returns:
        str: The overall health status of the system.
    """
    if value < 70:
        return "Healthy"
    elif value < 90:
        return "Warning"
    else:
        return "Critical"
