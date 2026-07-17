from venv import logger

from monitor import SystemHealthMonitor
from history import HistoryLogger

def main():
    monitor = SystemHealthMonitor()
    report = monitor.get_system_report()
    logger = HistoryLogger()
    summary = logger.get_history_summary()


    

    print("==============================")
    print("      HISTORY SUMMARY")
    print("==============================")

    print(f"Average CPU Usage: {summary['average_cpu']:.1f}%")
    print(f"Highest CPU Usage: {summary['highest_cpu']:.1f}%")
    print(f"Average Memory Usage: {summary['average_memory']:.1f}%")
    print(f"Highest Memory Usage: {summary['highest_memory']:.1f}%")
    print(
        f"Average CPU Temperature: "
        f"{summary['average_temperature']:.1f}°C"
        )
    print(
        f"Highest CPU Temperature: "
        f"{summary['highest_temperature']:.1f}°C"
    )


if __name__ == "__main__":
    main()