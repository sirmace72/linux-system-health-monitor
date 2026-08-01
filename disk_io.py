#!/usr/bin/env python3
"""Disk I/O metrics via psutil.disk_io_counters()."""

import psutil


class DiskIOMonitor:
    """Track disk read/write throughput."""

    def __init__(self) -> None:
        self._prev_counters = psutil.disk_io_counters(perdisk=True)

    def get_io_stats(self) -> dict[str, dict[str, float]]:
        """Return current per-disk IO stats since last call.

        Returns:
            dict keyed by device name, each containing:
                read_mb   - megabytes read since last call
                write_mb  - megabytes written since last call
                read_ops  - number of read operations
                write_ops - number of write operations
        """
        current = psutil.disk_io_counters(perdisk=True)
        stats: dict[str, dict[str, float]] = {}

        if current is None or self._prev_counters is None:
            self._prev_counters = current or {}
            return stats

        for device, counters in current.items():
            prev = self._prev_counters.get(device)
            if prev is None:
                continue

            read_bytes = max(counters.read_bytes - prev.read_bytes, 0)
            write_bytes = max(counters.write_bytes - prev.write_bytes, 0)
            read_ops = max(counters.read_count - prev.read_count, 0)
            write_ops = max(counters.write_count - prev.write_count, 0)

            stats[device] = {
                "read_mb": read_bytes / (1024 * 1024),
                "write_mb": write_bytes / (1024 * 1024),
                "read_ops": float(read_ops),
                "write_ops": float(write_ops),
            }

        self._prev_counters = current
        return stats

    @staticmethod
    def get_total_io() -> dict[str, float]:
        """Return cumulative total IO counters.

        Returns:
            dict with total read_mb, write_mb, read_ops, write_ops.
        """
        counters = psutil.disk_io_counters()
        if counters is None:
            return {
                "read_mb": 0.0,
                "write_mb": 0.0,
                "read_ops": 0.0,
                "write_ops": 0.0,
            }

        return {
            "read_mb": counters.read_bytes / (1024 * 1024),
            "write_mb": counters.write_bytes / (1024 * 1024),
            "read_ops": float(counters.read_count),
            "write_ops": float(counters.write_count),
        }
