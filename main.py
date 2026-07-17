#!/usr/bin/env python3
"""Unified System Health Monitor with HP Fan Control"""

from monitor import SystemHealthMonitor
from history import HistoryLogger
from hp_fan_control import set_max_speed, set_min_speed, get_current_speed, get_hwmon_path
import sys
import os

def show_menu():
    """Display main menu options"""
    print("\n" + "="*50)
    print("    SYSTEM HEALTH MONITOR")
    print("="*50)
    print("1. Show System Health Report")
    print("2. Show History Summary")
    print("3. Set Fan to Maximum Speed")
    print("4. Set Fan to Minimum Speed")
    print("5. Check Current Fan Speed")
    print("0. Exit")
    print("="*50)
    return input("Choose option: ").strip()

def show_health_report():
    """Show system health report"""
    monitor = SystemHealthMonitor()
    report = monitor.get_system_report()

    logger = HistoryLogger()
    logger.save_report(report)

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

    cpu_temp = report.get("cpu_temperature")

    if cpu_temp is not None:
        print(
            f"CPU Temperature: {cpu_temp:.1f}°C - "
            f"{report.get('temperature_status', 'Unknown')}"
        )
    else:
        print("CPU Temperature: Unavailable")

    print()
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

    print("=" * 40)

def show_history_summary():
    """Show history summary"""
    logger = HistoryLogger()
    summary = logger.get_history_summary()

    print("\n" + "="*40)
    print("       HISTORY SUMMARY")
    print("="*40)
    print(f"Average CPU Usage: {summary.get('average_cpu', 0):.1f}%")
    print(f"Highest CPU Usage: {summary.get('highest_cpu', 0):.1f}%")
    print(f"Average Memory Usage: {summary.get('average_memory', 0):.1f}%")
    print(f"Average CPU Temp: {summary.get('average_temperature', 0):.1f}°C")
    print(f"Highest CPU Temp: {summary.get('highest_temperature', 0):.1f}°C")
    print("="*40)

def main():
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
            set_max_speed()
        elif choice == "4":
            set_min_speed()
        elif choice == "5":
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
