class HealthMonitor:
    """Evaluate metrics against predefined thresholds."""

    WARNING_USAGE: float = 70.0
    CRITICAL_USAGE: float = 90.0
    WARNING_TEMP: float = 70.0
    CRITICAL_TEMP: float = 85.0

    def get_usage_status(self, value: float) -> str:
        if value < self.WARNING_USAGE:
            return "Healthy"
        elif value < self.CRITICAL_USAGE:
            return "Warning"
        return "Critical"

    def get_temperature_status(self, temperature: float) -> str:
        if temperature < self.WARNING_TEMP:
            return "Healthy"
        elif temperature < self.CRITICAL_TEMP:
            return "Warning"
        return "Critical"
