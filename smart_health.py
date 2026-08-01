#!/usr/bin/env python3
"""Disk SMART health via smartctl."""

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class SMARTMonitor:
    """Check disk SMART health status using smartctl."""

    def get_smart_health(self) -> list[dict[str, Any]]:
        """Return SMART health status for all available disks.

        Returns a list of dicts, each containing:
            device    - disk device path (e.g., /dev/sda)
            model     - disk model name
            health    - "PASSED", "FAILED", "UNKNOWN", or "UNAVAILABLE"
            temp      - temperature in °C (or None)
            power_on_hours - hours the disk has been powered on (or None)
        """
        devices = self._discover_devices()
        results: list[dict[str, Any]] = []

        for device in devices:
            info = self._get_smart_info(device)
            if info is not None:
                results.append(info)

        return results

    @staticmethod
    def _discover_devices() -> list[str]:
        """Find all block devices that might be disks."""
        devices: list[str] = []
        try:
            result = subprocess.run(
                ["lsblk", "-dnpo", "NAME,TYPE", "-l"],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "disk":
                    name = parts[0]
                    if not name.startswith("/"):
                        name = f"/dev/{name}"
                    devices.append(name)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            logger.debug("Failed to list block devices: %s", exc)
        return devices

    @staticmethod
    def _get_smart_info(device: str) -> dict[str, Any] | None:
        """Run smartctl on a single device and parse results."""
        import re

        info: dict[str, Any] = {"device": device}

        health_result = _run_smartctl(device, "-a")
        if health_result is None:
            info["health"] = "UNAVAILABLE"
            info["model"] = "Unknown"
            info["temp"] = None
            info["power_on_hours"] = None
            return info

        stdout = health_result.stdout

        model_match = re.search(r"(?:Model Family:|Model Name:|Device Model:)\s*(.+)", stdout)
        info["model"] = model_match.group(1).strip() if model_match else "Unknown"

        if "PASSED" in stdout:
            info["health"] = "PASSED"
        elif "FAILED" in stdout:
            info["health"] = "FAILED"
        else:
            info["health"] = "UNKNOWN"

        temp_match = re.search(r"Temperature:\s*(?:Current:\s*)?(\d+)\s*(?:C|Cel)", stdout)
        if not temp_match:
            temp_match = re.search(r"(?:Airflow|Drive) Temperature:\s*(\d+)", stdout)
        info["temp"] = int(temp_match.group(1)) if temp_match else None

        poh_match = re.search(r"Power On Hours:\s*(\d+)", stdout)
        if not poh_match:
            poh_match = re.search(r"Power_On_Hours\s+.*?(\d+)", stdout, re.DOTALL)
        info["power_on_hours"] = float(poh_match.group(1)) if poh_match else None

        return info


def _run_smartctl(device: str, *args: str) -> subprocess.CompletedProcess[str] | None:
    """Run smartctl with sudo and given arguments."""
    try:
        cmd = ["sudo", "smartctl", "--nocheck", "standby", device, *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result
    except subprocess.TimeoutExpired:
        logger.debug("smartctl timed out for %s", device)
        return None
    except FileNotFoundError:
        logger.debug("smartctl not found — install smartmontools")
        return None
