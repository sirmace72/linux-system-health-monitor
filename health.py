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

def get_temperature_status(temperature):
    if temperature < 70:
        return "Healthy"
    elif temperature < 85:
        return "Warning"
    else:
        return "Critical"