from monitor import SystemHealthMonitor
from history import HistoryLogger

def main():
    monitor = SystemHealthMonitor()
    report = monitor.get_system_report()
    logger = HistoryLogger()


    logger.save_report(report)
    print(report)


if __name__ == "__main__":
    main()