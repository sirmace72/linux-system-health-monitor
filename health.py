class HealthMonitor:
    def get_usage_status(self, value):
        if value < 70:
            return "Healthy"
        elif value < 90:
            return "Warning"
        else:
            return "Critical"

    def get_temperature_status(self, temperature):
        if temperature < 70:
            return "Healthy"
        elif temperature < 85:
            return "Warning"
        else:
            return "Critical"