from config import Config


class HealthMonitor:
    """Evaluate metrics against configurable thresholds."""

    def __init__(self, config: Config | None = None) -> None:
        self._config = config or Config()

    @property
    def warning_usage(self) -> float:
        return self._config.usage_warning

    @property
    def critical_usage(self) -> float:
        return self._config.usage_critical

    @property
    def warning_temp(self) -> float:
        return self._config.temp_warning

    @property
    def critical_temp(self) -> float:
        return self._config.temp_critical

    def get_usage_status(self, value: float) -> str:
        if value < self.warning_usage:
            return "Healthy"
        elif value < self.critical_usage:
            return "Warning"
        return "Critical"

    def get_temperature_status(self, temperature: float) -> str:
        if temperature < self.warning_temp:
            return "Healthy"
        elif temperature < self.critical_temp:
            return "Warning"
        return "Critical"
