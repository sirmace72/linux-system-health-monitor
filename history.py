import fcntl
import json
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class HistoryLogger:
    """Persistent JSON history with file locking to prevent race conditions."""

    def __init__(self, filename: str = "history.json") -> None:
        self.filename = filename

    def save_report(self, report: dict[str, Any]) -> None:
        report["timestamp"] = datetime.now().isoformat()

        file_lock = f"{self.filename}.lock"
        with open(file_lock, "w") as lockfile:
            try:
                fcntl.flock(lockfile.fileno(), fcntl.LOCK_EX)
            except OSError as exc:
                logger.warning("Could not acquire file lock: %s", exc)

            try:
                try:
                    with open(self.filename, "r", encoding="utf-8") as file:
                        history: list[dict[str, Any]] = json.load(file)
                except FileNotFoundError:
                    history = []

                history.append(report)

                with open(self.filename, "w", encoding="utf-8") as file:
                    json.dump(history, file, indent=4)

                logger.debug("Saved report to %s (total: %d)", self.filename, len(history))
            finally:
                fcntl.flock(lockfile.fileno(), fcntl.LOCK_UN)

    def get_average(self, key: str) -> float | None:
        history = self.load_history()
        if not history:
            return None

        values = [
            report[key]
            for report in history
            if report.get(key) is not None
        ]

        if not values:
            return None

        return sum(values) / len(values)

    def load_history(self) -> list[dict[str, Any]]:
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def get_highest(self, key: str) -> float | None:
        history = self.load_history()
        if not history:
            return None

        values = [
            report[key]
            for report in history
            if report.get(key) is not None
        ]

        if not values:
            return None

        return max(values)

    def get_history_summary(self) -> dict[str, float | None]:
        return {
            "average_cpu": self.get_average("cpu_usage"),
            "highest_cpu": self.get_highest("cpu_usage"),
            "average_memory": self.get_average("memory_usage"),
            "highest_memory": self.get_highest("memory_usage"),
            "average_temperature": self.get_average("cpu_temperature"),
            "highest_temperature": self.get_highest("cpu_temperature"),
        }
