import psutil

class TemperatureMonitor:
    def get_cpu_temperature(self):
        """
        Get the current CPU temperature in Celsius.

        Returns:
            float | None: CPU temperature, or None if unavailable.
        """
        temperatures = psutil.sensors_temperatures()

        if "k10temp" not in temperatures:
            return None

        for sensor in temperatures["k10temp"]:
            if sensor.label == "Tctl":
                return sensor.current

        return None
    