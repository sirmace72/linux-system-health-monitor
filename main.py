#!/usr/bin/env python3
"""Unified System Health Monitor with HP Fan Control"""

import sys
from typing import Any

import logging

from config import Config
from cli import get_arguments
from monitor import SystemHealthMonitor
from history import HistoryLogger
from system_info import SystemInfo
from network import NetworkMonitor
from hp_fan_control import (
    set_max_speed,
    set_min_speed,
    set_fan_speed,
    get_current_speed,
    get_hwmon_path,
)

logger = logging.getLogger(__name__)


def _fmt_uptime(seconds: float) -> str:
    """Format uptime seconds into human-readable string."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    parts: list[str] = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def _fmt_mb(mb: float) -> str:
    """Format megabytes with appropriate precision."""
    if mb >= 100:
        return f"{mb:.0f} MB"
    return f"{mb:.1f} MB"


def run_cli_command(command: str) -> None:
    """Handle headless CLI commands from argparse."""
    if command == "status":
        show_health_report()
    elif command == "network":
        show_network_status()
    elif command == "history":
        show_history_summary()
    elif command == "full-report":
        show_full_report()


def show_full_report() -> None:
    """Show full system report including system info."""
    config = Config()
    monitor = SystemHealthMonitor(config)
    report = monitor.get_system_report()
    system = SystemInfo()

    logger.info("Saving full report to history")
    HistoryLogger(config.history_file).save_report(report)

    print("\n" + "=" * 40)
    print("       FULL SYSTEM REPORT")
    print("=" * 40)

    print(f"Hostname:     {system.get_hostname()}")
    print(f"OS:           {system.get_os()}")
    print(f"Kernel:       {system.get_kernel()}")
    print(f"Architecture: {system.get_architecture()}")
    print(f"CPU:          {system.get_cpu_model()}")
    print(f"Uptime:       {_fmt_uptime(report.get('uptime_seconds', 0))}")
    print()
    print(
        f"CPU Usage:      {report.get('cpu_usage', 0):.1f}% - "
        f"{report.get('cpu_status', 'Unknown')}"
    )
    print(
        f"Memory Usage:   {report.get('memory_usage', 0):.1f}% - "
        f"{report.get('memory_status', 'Unknown')}"
    )
    print(
        f"Disk Usage:     {report.get('disk_usage', 0):.1f}% - "
        f"{report.get('disk_status', 'Unknown')}"
    )

    swap = report.get("swap_usage")
    if swap is not None:
        print(f"Swap Usage:     {swap:.1f}%")

    cpu_temp = report.get("cpu_temperature")
    if cpu_temp is not None:
        print(
            f"CPU Temp:       {cpu_temp:.1f}°C - "
            f"{report.get('temperature_status', 'Unknown')}"
        )
    else:
        print("CPU Temperature: Unavailable")

    # GPU
    gpu_info = report.get("gpu_info")
    if gpu_info:
        print()
        for i, gpu in enumerate(gpu_info):
            vendor = gpu.get("vendor", "unknown").upper()
            name = gpu.get("name", "Unknown")
            temp = gpu.get("temp")
            usage = gpu.get("usage")
            mem_used = gpu.get("mem_used")
            mem_total = gpu.get("mem_total")

            print(f"  GPU {i+1} ({vendor}): {name}")
            parts: list[str] = []
            if temp is not None:
                parts.append(f"{temp:.0f}°C")
            if usage is not None:
                parts.append(f"{usage:.0f}%")
            if mem_used is not None and mem_total is not None:
                parts.append(f"{_fmt_mb(mem_used)}/{_fmt_mb(mem_total)}")
            if parts:
                print(f"    {' | '.join(parts)}")

    print()
    _show_network_block(report)

    # Disk IO
    disk_io_total = report.get("disk_io_total")
    if disk_io_total:
        print()
        print("  Disk I/O (total since boot):")
        print(f"    Read:  {_fmt_mb(disk_io_total.get('read_mb', 0))}")
        print(f"    Write: {_fmt_mb(disk_io_total.get('write_mb', 0))}")

    # Network IO
    net_io_total = report.get("net_io_total")
    if net_io_total:
        print()
        print("  Network Transfer (total):")
        print(f"    Sent:     {_fmt_mb(net_io_total.get('sent_mb', 0))}")
        print(f"    Received: {_fmt_mb(net_io_total.get('received_mb', 0))}")

    print("=" * 40)


def show_network_status() -> None:
    """Show only network status."""
    network = NetworkMonitor()

    interface = network.get_active_interface()
    ip_address = network.get_ip_address()
    gateway = network.get_default_gateway()
    gateway_ping = network.get_ping_time(gateway)
    internet_ping = network.get_ping_time("1.1.1.1")

    print("\n" + "=" * 40)
    print("       NETWORK STATUS")
    print("=" * 40)
    _show_network_block({
        "interface": interface,
        "ip_address": ip_address,
        "gateway": gateway,
        "gateway_ping": gateway_ping,
        "internet_ping": internet_ping,
    })
    print("=" * 40)


def _show_network_block(report: dict[str, Any]) -> None:
    """Print the network section of a report."""
    print(f"Interface: {report.get('interface', 'N/A')}")
    print(f"IP Address: {report.get('ip_address', 'N/A')}")
    print(f"Gateway: {report.get('gateway', 'N/A')}")

    gateway_ping = report.get("gateway_ping")
    if gateway_ping is not None:
        print(f"Gateway Ping: {gateway_ping:.2f} ms")
    else:
        print("Gateway Ping: Unreachable")

    internet_ping = report.get("internet_ping")
    if internet_ping is not None:
        print("Internet: Online")
        print(f"Internet Ping: {internet_ping:.2f} ms")
    else:
        print("Internet: Offline")


def show_menu() -> str:
    """Display main menu options"""
    print("\n" + "=" * 50)
    print("    SYSTEM HEALTH MONITOR")
    print("=" * 50)
    print("1. Show System Health Report")
    print("2. Show History Summary")
    print("3. Set Fan to Maximum Speed (100%)")
    print("4. Set Fan to 75%")
    print("5. Set Fan to 50%")
    print("6. Set Fan to 25%")
    print("7. Set Fan to Minimum Speed")
    print("8. Check Current Fan Speed")
    print("0. Exit")
    print("=" * 50)
    return input("Choose option: ").strip()


def show_health_report() -> None:
    """Show system health report"""
    config = Config()
    monitor = SystemHealthMonitor(config)
    report = monitor.get_system_report()

    logger.info("Saving health report to history")
    HistoryLogger(config.history_file).save_report(report)

    print("\n" + "=" * 40)
    print("       SYSTEM HEALTH REPORT")
    print("=" * 40)

    print(f"Hostname: {report.get('hostname', 'N/A')}")
    print(
        f"CPU Usage: {report.get('cpu_usage', 0):.1f}% - "
        f"{report.get('cpu_status', 'Unknown')}"
    )
    print(
        f"Memory Usage: {report.get('memory_usage', 0):.1f}% - "
        f"{report.get('memory_status', 'Unknown')}"
    )
    print(
        f"Disk Usage: {report.get('disk_usage', 0):.1f}% - "
        f"{report.get('disk_status', 'Unknown')}"
    )

    swap = report.get("swap_usage")
    if swap is not None:
        print(f"Swap Usage: {swap:.1f}%")

    cpu_temp = report.get("cpu_temperature")

    if cpu_temp is not None:
        print(
            f"CPU Temperature: {cpu_temp:.1f}°C - "
            f"{report.get('temperature_status', 'Unknown')}"
        )
    else:
        print("CPU Temperature: Unavailable")

    # GPU
    gpu_info = report.get("gpu_info")
    if gpu_info:
        print()
        for i, gpu in enumerate(gpu_info):
            vendor = gpu.get("vendor", "unknown").upper()
            name = gpu.get("name", "Unknown")
            temp = gpu.get("temp")
            usage = gpu.get("usage")

            parts: list[str] = [f"  GPU {i+1} ({vendor}): {name}"]
            if temp is not None:
                parts.append(str())
                print(f"    Temp: {temp:.0f}°C")
            if usage is not None:
                print(f"    Usage: {usage:.0f}%")

    print()
    _show_network_block(report)
    print("=" * 40)


def show_history_summary() -> None:
    """Show history summary"""
    logger = HistoryLogger()
    summary = logger.get_history_summary()

    print("\n" + "=" * 40)
    print("       HISTORY SUMMARY")
    print("=" * 40)
    print(f"Average CPU Usage: {summary.get('average_cpu', 0):.1f}%")
    print(f"Highest CPU Usage: {summary.get('highest_cpu', 0):.1f}%")
    print(f"Average Memory Usage: {summary.get('average_memory', 0):.1f}%")
    print(f"Average CPU Temp: {summary.get('average_temperature', 0):.1f}°C")
    print(f"Highest CPU Temp: {summary.get('highest_temperature', 0):.1f}°C")
    print("=" * 40)


def main() -> None:
    """Main entry point."""
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

    try:
        args = get_arguments()
        run_cli_command(args.command)
        return
    except SystemExit:
        pass

    hwmon_path = get_hwmon_path()
    if hwmon_path:
        print(f"HP Fan Controller: {hwmon_path}")

    while True:
        choice = show_menu()

        if choice == "1":
            show_health_report()
        elif choice == "2":
            show_history_summary()
        elif choice == "3":
            set_fan_speed(100)
        elif choice == "4":
            set_fan_speed(75)
        elif choice == "5":
            set_fan_speed(50)
        elif choice == "6":
            set_fan_speed(25)
        elif choice == "7":
            set_min_speed()
        elif choice == "8":
            speeds = get_current_speed()

            if speeds is not None:
                fan1, fan2 = speeds
                print(f"Fan 1: {fan1} RPM")
                print(f"Fan 2: {fan2} RPM")
        elif choice == "0":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option, try again")
        print()


if __name__ == "__main__":
    main()
