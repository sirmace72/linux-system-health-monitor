#!/usr/bin/env python3
"""Network transfer statistics via psutil.net_io_counters()."""

import psutil


class NetworkTransferMonitor:
    """Track network bytes sent/received per interface."""

    def __init__(self) -> None:
        self._prev_counters = psutil.net_io_counters(pernic=True)

    def get_transfer_stats(self) -> dict[str, dict[str, float]]:
        """Return per-interface transfer stats since last call.

        Returns:
            dict keyed by interface name, each containing:
                sent_mb       - megabytes sent since last call
                received_mb   - megabytes received since last call
                sent_packets  - number of packets sent
                received_packets - number of packets received
                drop_in       - inbound dropped packets
                drop_out      - outbound dropped packets
        """
        current = psutil.net_io_counters(pernic=True)
        stats: dict[str, dict[str, float]] = {}

        if current is None or self._prev_counters is None:
            self._prev_counters = current or {}
            return stats

        for interface, counters in current.items():
            prev = self._prev_counters.get(interface)
            if prev is None:
                continue

            stats[interface] = {
                "sent_mb": max(counters.bytes_sent - prev.bytes_sent, 0) / (1024 * 1024),
                "received_mb": max(counters.bytes_recv - prev.bytes_recv, 0) / (1024 * 1024),
                "sent_packets": float(max(counters.packets_sent - prev.packets_sent, 0)),
                "received_packets": float(
                    max(counters.packets_recv - prev.packets_recv, 0)
                ),
                "drop_in": float(max(counters.dropin - prev.dropin, 0)),
                "drop_out": float(max(counters.dropout - prev.dropout, 0)),
            }

        self._prev_counters = current
        return stats

    @staticmethod
    def get_total_transfers() -> dict[str, float]:
        """Return cumulative total network transfers.

        Returns:
            dict with total sent_mb, received_mb, sent_packets, received_packets.
        """
        counters = psutil.net_io_counters()
        if counters is None:
            return {
                "sent_mb": 0.0,
                "received_mb": 0.0,
                "sent_packets": 0.0,
                "received_packets": 0.0,
            }

        return {
            "sent_mb": counters.bytes_sent / (1024 * 1024),
            "received_mb": counters.bytes_recv / (1024 * 1024),
            "sent_packets": float(counters.packets_sent),
            "received_packets": float(counters.packets_recv),
        }
