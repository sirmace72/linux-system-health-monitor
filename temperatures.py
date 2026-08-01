import logging

import psutil

logger = logging.getLogger(__name__)

# Ordered by priority: first matching sensor wins.
SENSOR_PRIORITY: list[str] = [
    "k10temp",
    "coretemp",
    "Package id 0",
    "cpu_thermal",
]

CPU_LABELS: list[str] = [
    "Tctl",
    "Tdie",
    "core 0",
    "Package id 0",
]


class TemperatureMonitor:
    """Monitor CPU temperature with fallback across sensor types."""

    def get_cpu_temperature(self) -> float | None:
        """
        Get the current CPU temperature in Celsius.

        Tries multiple sensor names and labels in priority order:
        - AMD Ryzen: k10temp (Tctl / Tdie)
        - Intel: coretemp (core 0) / Package id 0
        - Generic: cpu_thermal

        Returns:
            CPU temperature in Celsius, or None if unavailable.
        """
        try:
            temperatures = psutil.sensors_temperatures()
        except Exception as exc:
            logger.debug("Failed to read temperature sensors: %s", exc)
            return None

        if temperatures is None:
            return None

        for sensor_name in SENSOR_PRIORITY:
            if sensor_name not in temperatures:
                continue

            sensors = temperatures[sensor_name]
            if not sensors:
                continue

            for label in CPU_LABELS:
                for entry in sensors:
                    if label in entry.label:
                        logger.debug("Using sensor %s (%s): %.1f°C", sensor_name, entry.label, entry.current)
                        return entry.current

            if sensors:
                logger.debug("Using first reading from %s: %.1f°C", sensor_name, sensors[0].current)
                return sensors[0].current

        logger.warning("No known CPU temperature sensor found")
        return None
