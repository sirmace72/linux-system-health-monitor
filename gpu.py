#!/usr/bin/env python3
"""GPU monitoring via pynvml (NVIDIA) and pyamdgpuinfo (AMD)."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

nvidia_nvml = None
try:
    import pynvml  # type: ignore[import-not-found]

    nvidia_nvml = pynvml
except ImportError:
    pass

amd_gpu = None
try:
    import pyamdgpuinfo  # type: ignore[import-not-found]

    amd_gpu = pyamdgpuinfo
except ImportError:
    pass


class GPUMonitor:
    """Collect GPU temperature, usage, and memory info."""

    def get_gpu_info(self) -> list[dict[str, Any]]:
        """Return a list of GPU info dicts.

        Each dict contains:
            vendor    - "nvidia" or "amd" or "unknown"
            name      - human-readable GPU name
            temp      - temperature in °C (or None)
            usage     - GPU utilization % (or None)
            mem_used  - memory used in MiB (or None)
            mem_total - memory total in MiB (or None)
        """
        results: list[dict[str, Any]] = []
        results.extend(self._get_nvidia_info())
        results.extend(self._get_amd_info())
        return results

    def _get_nvidia_info(self) -> list[dict[str, Any]]:
        if nvidia_nvml is None:
            return []

        results: list[dict[str, Any]] = []
        try:
            nvidia_nvml.nvmlInit()
            device_count = nvidia_nvml.nvmlDeviceGetCount()
        except Exception as exc:
            logger.debug("NVML init failed: %s", exc)
            return results

        try:
            for idx in range(device_count):
                handle = nvidia_nvml.nvmlDeviceGetHandleByIndex(idx)
                info: dict[str, Any] = {"vendor": "nvidia"}

                try:
                    info["name"] = nvidia_nvml.nvmlDeviceGetName(handle)
                except Exception:
                    info["name"] = "Unknown NVIDIA GPU"

                try:
                    temp = nvidia_nvml.nvmlDeviceGetTemperature(
                        handle, nvidia_nvml.NVML_TEMPERATURE_GPU
                    )
                    info["temp"] = float(temp)
                except Exception:
                    info["temp"] = None

                try:
                    usage = nvidia_nvml.nvmlDeviceGetUtilizationRates(handle).gpu
                    info["usage"] = float(usage)
                except Exception:
                    info["usage"] = None

                try:
                    mem = nvidia_nvml.nvmlDeviceGetMemoryInfo(handle)
                    info["mem_used"] = mem.used / (1024 * 1024)
                    info["mem_total"] = mem.total / (1024 * 1024)
                except Exception:
                    info["mem_used"] = None
                    info["mem_total"] = None

                results.append(info)
        finally:
            try:
                nvidia_nvml.nvmlShutdown()
            except Exception:
                pass

        return results

    def _get_amd_info(self) -> list[dict[str, Any]]:
        if amd_gpu is None:
            return []

        results: list[dict[str, Any]] = []
        try:
            gpus = amd_gpu.enum_gpu()
        except Exception as exc:
            logger.debug("AMD GPU enum failed: %s", exc)
            return results

        for gpu_handle in gpus:
            info: dict[str, Any] = {"vendor": "amd"}
            try:
                info_str = amd_gpu.query_gpu_info_str(gpu_handle)
                info["name"] = str(info_str)
            except Exception:
                info["name"] = "Unknown AMD GPU"

            try:
                temp = amd_gpu.query_temperature(gpu_handle)
                info["temp"] = float(temp)
            except Exception:
                info["temp"] = None

            try:
                load = amd_gpu.query_load(gpu_handle)
                info["usage"] = float(load)
            except Exception:
                info["usage"] = None

            results.append(info)

        return results
