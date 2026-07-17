#!/usr/bin/env python3
"""Unified System Health Monitor with HP Fan Control"""

from monitor import SystemHealthMonitor
from history import HistoryLogger
from hp_fan_control import main as fan_main
import argparse

def main():
    parser = argparse.ArgumentParser(description="System Health Monitor")
    parser.add_argument("--fan", action="store_true", help="Launch HP fan control")
    parser.add_argument("--report", action="store_true", help="Show system report only")
    args = parser.parse_args()
    
    if args.fan:
        fan_main()
        return
    
    if args.report:
        monitor = SystemHealthMonitor()
        logger = HistoryLogger()
        report = monitor.get_system_report()
        summary = logger.get_history_summary()
        
        print("\n" + "="*40)
        print("    SYSTEM HEALTH REPORT")
        print("="*40)
        print(f"CPU Temperature: {report.get('cpu_temp', 'N/A')}°C")
        print(f"Memory Usage: {report.get('memory_usage', 0):.1f}%")
        print("\n" + "="*40)
        print("       HISTORY SUMMARY")
        print("="*40)
        print(f"Average CPU Usage: {summary.get('average_cpu', 0):.1f}%")
        print(f"Highest CPU Usage: {summary.get('highest_cpu', 0):.1f}%")
        print(f"Average Memory Usage: {summary.get('average_memory', 0):.1f}%")
        print(f"Average CPU Temp: {summary.get('average_temperature', 0):.1f}°C")
        print(f"Highest CPU Temp: {summary.get('highest_temperature', 0):.1f}°C")
        print("="*40)
        return
    
    # Default: show report and history
    monitor = SystemHealthMonitor()
    logger = HistoryLogger()
    report = monitor.get_system_report()
    summary = logger.get_history_summary()
    
    print("\n" + "="*40)
    print("    SYSTEM HEALTH REPORT")
    print("="*40)
    print(f"CPU Temperature: {report.get('cpu_temp', 'N/A')}°C")
    print(f"Memory Usage: {report.get('memory_usage', 0):.1f}%")
    print("\n" + "="*40)
    print("       HISTORY SUMMARY")
    print("="*40)
    print(f"Average CPU Usage: {summary.get('average_cpu', 0):.1f}%")
    print(f"Highest CPU Usage: {summary.get('highest_cpu', 0):.1f}%")
    print(f"Average Memory Usage: {summary.get('average_memory', 0):.1f}%")
    print(f"Average CPU Temp: {summary.get('average_temperature', 0):.1f}°C")
    print(f"Highest CPU Temp: {summary.get('highest_temperature', 0):.1f}°C")
    print("="*40)

if __name__ == "__main__":
    main()
