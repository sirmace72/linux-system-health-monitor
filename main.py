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
from color import ColorHelper
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


def _fmt_bytes(b: float) -> str:
    """Format bytes into human-readable string."""
    if b >= 1024 ** 3:
        return f"{b / (1024 ** 3):.1f} GB"
    return f"{b / (1024 ** 2):.1f} MB"


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
    color = ColorHelper(config.color_output)
    monitor = SystemHealthMonitor(config)
    report = monitor.get_system_report()
    system = SystemInfo()

    logger.info("Saving full report to history")
    HistoryLogger(config.history_file).save_report(report)

    sep = "=" * 50
    color.print(f"\n{sep}")
    color.print("        FULL SYSTEM REPORT", color="bold")
    color.print(sep)

    # System info
    color.print(f"  Hostname:     {system.get_hostname()}")
    color.print(f"  OS:           {system.get_os()}")
    color.print(f"  Kernel:       {system.get_kernel()}")
    color.print(f"  Architecture: {system.get_architecture()}")
    color.print(f"  CPU:          {system.get_cpu_model()}")
    color.print(
        f"  Uptime:       {_fmt_uptime(report.get('uptime_seconds', 0))}"
    )

    # Resource usage
    color.print()
    cpu_usage = report.get("cpu_usage", 0)
    cpu_status = report.get("cpu_status", "Unknown")
    color.print(
        f"  CPU Usage:      {cpu_usage:.1f}% - {color.status_label(cpu_status)}",
        color=status_color(cpu_status),
    )

    mem_usage = report.get("memory_usage", 0)
    mem_status = report.get("memory_status", "Unknown")
    color.print(
        f"  Memory Usage:   {mem_usage:.1f}% - {color.status_label(mem_status)}",
        color=status_color(mem_status),
    )

    disk_usage = report.get("disk_usage", 0)
    disk_status = report.get("disk_status", "Unknown")
    color.print(
        f"  Disk Usage:     {disk_usage:.1f}% - {color.status_label(disk_status)}",
        color=status_color(disk_status),
    )

    swap = report.get("swap_usage")
    if swap is not None:
        color.print(f"  Swap Usage:     {swap:.1f}%")

    # Temperature
    cpu_temp = report.get("cpu_temperature")
    if cpu_temp is not None:
        temp_status = report.get("temperature_status", "Unknown")
        color.print(
            f"  CPU Temp:       {cpu_temp:.1f}°C - {color.status_label(temp_status)}",
            color=status_color(temp_status),
        )
    else:
        color.print("  CPU Temp:       Unavailable")

    # All disk partitions
    all_disk = report.get("all_disk_usage")
    if all_disk:
        color.print()
        color.print("  Disk Partitions:", color="cyan")
        for mp, usage in all_disk.items():
            status = report.get("disk_status", "Unknown")
            if usage >= 90:
                status_label = "Critical"
                c = "red"
            elif usage >= 70:
                status_label = "Warning"
                c = "yellow"
            else:
                status_label = "Healthy"
                c = "green"
            color.print(
                f"    {mp:<12} {usage:.1f}% - {color.status_label(status_label)}",
                color=c,
            )

    # GPU
    gpu_info = report.get("gpu_info")
    if gpu_info:
        color.print()
        color.print("  GPUs:", color="cyan")
        for i, gpu in enumerate(gpu_info):
            vendor = gpu.get("vendor", "unknown").upper()
            name = gpu.get("name", "Unknown")
            temp = gpu.get("temp")
            usage = gpu.get("usage")
            mem_used = gpu.get("mem_used")
            mem_total = gpu.get("mem_total")

            color.print(f"    GPU {i+1} ({vendor}): {name}")
            parts: list[str] = []
            if temp is not None:
                parts.append(f"{temp:.0f}°C")
            if usage is not None:
                parts.append(f"{usage:.0f}%")
            if mem_used is not None and mem_total is not None:
                parts.append(f"{_fmt_mb(mem_used)}/{_fmt_mb(mem_total)}")
            if parts:
                color.print(f"      {' | '.join(parts)}")

    # Top processes
    top_cpu = report.get("top_cpu")
    top_memory = report.get("top_memory")
    if top_cpu or top_memory:
        color.print()
        color.print("  Top Processes by CPU:", color="cyan")
        if top_cpu:
            for proc in top_cpu:
                color.print(
                    f"    PID {proc['pid']:<6} {proc['name']:<20} "
                    f"CPU: {proc['cpu_percent']:.1f}%  "
                    f"Mem: {proc['memory_percent']:.1f}%"
                )
        color.print("  Top Processes by Memory:", color="cyan")
        if top_memory:
            for proc in top_memory:
                color.print(
                    f"    PID {proc['pid']:<6} {proc['name']:<20} "
                    f"CPU: {proc['cpu_percent']:.1f}%  "
                    f"Mem: {proc['memory_percent']:.1f}%"
                )

    # Network
    color.print()
    _show_network_block(report, color)

    # Disk IO
    disk_io_total = report.get("disk_io_total")
    if disk_io_total:
        color.print()
        color.print("  Disk I/O (total since boot):", color="cyan")
        color.print(
            f"    Read:  {_fmt_mb(disk_io_total.get('read_mb', 0))}"
        )
        color.print(
            f"    Write: {_fmt_mb(disk_io_total.get('write_mb', 0))}"
        )

    # Network IO
    net_io_total = report.get("net_io_total")
    if net_io_total:
        color.print()
        color.print("  Network Transfer (total):", color="cyan")
        color.print(
            f"    Sent:     {_fmt_mb(net_io_total.get('sent_mb', 0))}"
        )
        color.print(
            f"    Received: {_fmt_mb(net_io_total.get('received_mb', 0))}"
        )

    # SMART health
    smart_health = report.get("smart_health")
    if smart_health:
        color.print()
        color.print("  Disk SMART Health:", color="cyan")
        for disk in smart_health:
            device = disk.get("device", "Unknown")
            model = disk.get("model", "Unknown")
            health = disk.get("health", "UNKNOWN")
            temp = disk.get("temp")
            poh = disk.get("power_on_hours")

            h_color = "green" if health == "PASSED" else "red" if health == "FAILED" else "yellow"
            line = f"    {device}: {model}"
            if temp is not None:
                line += f" | {temp}°C"
            if poh is not None:
                line += f" | {poh:.0f}h"
            color.print(line + f" - {health}", color=h_color)

    color.print(sep)


def _show_network_block(report: dict[str, Any], color: ColorHelper) -> None:
    """Print the network section of a report."""
    color.print(f"  Interface: {report.get('interface', 'N/A')}")
    color.print(f"  IP Address: {report.get('ip_address', 'N/A')}")
    color.print(f"  Gateway: {report.get('gateway', 'N/A')}")

    gateway_ping = report.get("gateway_ping")
    if gateway_ping is not None:
        color.print(f"  Gateway Ping: {gateway_ping:.2f} ms")
    else:
        color.print("  Gateway Ping: Unreachable", color="yellow")

    internet_ping = report.get("internet_ping")
    if internet_ping is not None:
        color.print("  Internet: Online", color="green")
        color.print(f"  Internet Ping: {internet_ping:.2f} ms")
    else:
        color.print("  Internet: Offline", color="red")


def show_network_status() -> None:
    """Show only network status."""
    config = Config()
    color = ColorHelper(config.color_output)
    network = NetworkMonitor()

    interface = network.get_active_interface()
    ip_address = network.get_ip_address()
    gateway = network.get_default_gateway()
    gateway_ping = network.get_ping_time(gateway)
    internet_ping = network.get_ping_time("1.1.1.1")

    sep = "=" * 50
    color.print(f"\n{sep}")
    color.print("       NETWORK STATUS", color="bold")
    color.print(sep)
    _show_network_block({
        "interface": interface,
        "ip_address": ip_address,
        "gateway": gateway,
        "gateway_ping": gateway_ping,
        "internet_ping": internet_ping,
    }, color)
    color.print(sep)


def show_menu() -> str:
    """Display main menu options"""
    print("\n" + "=" * 50)
    print("    SYSTEM HEALTH MONITOR")
    print("=" * 50)
    print("1. Show System Health Report")
    print("2. Show Full Report")
    print("3. Show History Summary")
    print("4. Set Fan to Maximum Speed (100%)")
    print("5. Set Fan to 75%")
    print("6. Set Fan to 50%")
    print("7. Set Fan to 25%")
    print("8. Set Fan to Minimum Speed")
    print("9. Check Current Fan Speed")
    print("0. Exit")
    print("=" * 50)
    return input("Choose option: ").strip()


def show_health_report() -> None:
    """Show system health report"""
    config = Config()
    color = ColorHelper(config.color_output)
    monitor = SystemHealthMonitor(config)
    report = monitor.get_system_report()

    logger.info("Saving health report to history")
    HistoryLogger(config.history_file).save_report(report)

    sep = "=" * 50
    color.print(f"\n{sep}")
    color.print("       SYSTEM HEALTH REPORT", color="bold")
    color.print(sep)

    color.print(f"  Hostname: {report.get('hostname', 'N/A')}")

    uptime = report.get("uptime_seconds")
    if uptime is not None:
        color.print(f"  Uptime:   {_fmt_uptime(uptime)}")

    cpu_usage = report.get("cpu_usage", 0)
    cpu_status = report.get("cpu_status", "Unknown")
    color.print(
        f"  CPU:      {cpu_usage:.1f}% - {color.status_label(cpu_status)}",
        color=status_color(cpu_status),
    )

    mem_usage = report.get("memory_usage", 0)
    mem_status = report.get("memory_status", "Unknown")
    color.print(
        f"  Memory:   {mem_usage:.1f}% - {color.status_label(mem_status)}",
        color=status_color(mem_status),
    )

    disk_usage = report.get("disk_usage", 0)
    disk_status = report.get("disk_status", "Unknown")
    color.print(
        f"  Disk:     {disk_usage:.1f}% - {color.status_label(disk_status)}",
        color=status_color(disk_status),
    )

    swap = report.get("swap_usage")
    if swap is not None:
        color.print(f"  Swap:     {swap:.1f}%")

    cpu_temp = report.get("cpu_temperature")
    if cpu_temp is not None:
        temp_status = report.get("temperature_status", "Unknown")
        color.print(
            f"  Temp:     {cpu_temp:.1f}°C - {color.status_label(temp_status)}",
            color=status_color(temp_status),
        )
    else:
        color.print("  Temp:     Unavailable")

    # GPU
    gpu_info = report.get("gpu_info")
    if gpu_info:
        color.print()
        color.print("  GPUs:", color="cyan")
        for i, gpu in enumerate(gpu_info):
            vendor = gpu.get("vendor", "unknown").upper()
            name = gpu.get("name", "Unknown")
            temp = gpu.get("temp")
            usage = gpu.get("usage")

            line = f"    GPU {i+1} ({vendor}): {name}"
            parts: list[str] = []
            if temp is not None:
                parts.append(f"{temp:.0f}°C")
            if usage is not None:
                parts.append(f"{usage:.0f}%")
            if parts:
                line += f"  |  {' | '.join(parts)}"
            elif temp is not None or usage is not None:
                line += f"  |  {' | '.join(parts) if parts else ''}"
            color.print(line)

    # Top processes
    top_cpu = report.get("top_cpu")
    top_memory = report.get("top_memory")
    if top_cpu or top_memory:
        color.print()
        color.print("  Top Processes by CPU:", color="cyan")
        if top_cpu:
            for proc in top_cpu:
                color.print(
                    f"    {proc['pid']:<6} {proc['name']:<20} "
                    f"{proc['cpu_percent']:.1f}% CPU  "
                    f"{proc['memory_percent']:.1f}% Mem"
                )
        color.print("  Top Processes by Memory:", color="cyan")
        if top_memory:
            for proc in top_memory:
                color.print(
                    f"    {proc['pid']:<6} {proc['name']:<20} "
                    f"{proc['cpu_percent']:.1f}% CPU  "
                    f"{proc['memory_percent']:.1f}% Mem"
                )

    # Disk IO
    disk_io_total = report.get("disk_io_total")
    if disk_io_total:
        color.print()
        color.print("  Disk I/O:", color="cyan")
        color.print(
            f"    Read:  {_fmt_mb(disk_io_total.get('read_mb', 0))}"
        )
        color.print(
            f"    Write: {_fmt_mb(disk_io_total.get('write_mb', 0))}"
        )

    # Network transfer
    net_io_total = report.get("net_io_total")
    if net_io_total:
        color.print()
        color.print("  Network:", color="cyan")
        color.print(
            f"    Sent:     {_fmt_mb(net_io_total.get('sent_mb', 0))}"
        )
        color.print(
            f"    Received: {_fmt_mb(net_io_total.get('received_mb', 0))}"
        )

    color.print()
    _show_network_block(report, color)
    color.print(sep)


def show_history_summary() -> None:
    """Show history summary"""
    config = Config()
    color = ColorHelper(config.color_output)
    history = HistoryLogger(config.history_file)
    summary = history.get_history_summary()

    sep = "=" * 50
    color.print(f"\n{sep}")
    color.print("       HISTORY SUMMARY", color="bold")
    color.print(sep)
    avg_cpu = summary.get("average_cpu")
    high_cpu = summary.get("highest_cpu")
    avg_mem = summary.get("average_memory")
    high_mem = summary.get("highest_memory")
    avg_temp = summary.get("average_temperature")
    high_temp = summary.get("highest_temperature")

    if avg_cpu is not None:
        color.print(f"  Avg CPU:      {avg_cpu:.1f}%")
    if high_cpu is not None:
        color.print(f"  Highest CPU:  {high_cpu:.1f}%")
    if avg_mem is not None:
        color.print(f"  Avg Memory:   {avg_mem:.1f}%")
    if high_mem is not None:
        color.print(f"  Highest Mem:  {high_mem:.1f}%")
    if avg_temp is not None:
        color.print(f"  Avg Temp:     {avg_temp:.1f}°C")
    if high_temp is not None:
        color.print(f"  Highest Temp: {high_temp:.1f}°C")
    color.print(sep)


def status_color(status: str) -> str:
    """Map status label to color name."""
    if status == "Healthy":
        return "green"
    if status == "Warning":
        return "yellow"
    if status == "Critical":
        return "red"
    return "white"


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
            show_full_report()
        elif choice == "3":
            show_history_summary()
        elif choice == "4":
            set_fan_speed(100)
        elif choice == "5":
            set_fan_speed(75)
        elif choice == "6":
            set_fan_speed(50)
        elif choice == "7":
            set_fan_speed(25)
        elif choice == "8":
            set_min_speed()
        elif choice == "9":
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