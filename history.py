import json
from datetime import datetime



class HistoryLogger:
    def __init__(self, filename="history.json"):
        self.filename = filename
    
    def save_report(self, report):
        report["timestamp"] = datetime.now().isoformat()
        try:
            with open(self.filename, "r") as file:
                history = json.load(file)
        except FileNotFoundError:
            history = []  
        
        history.append(report)

        with open(self.filename, "w") as file:
            json.dump(history, file, indent=4)

    def get_average(self, key):
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

    def load_history(self):
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        
    def get_highest(self, key):
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
    def get_history_summary(self):
        return {
            "average_cpu": self.get_average("cpu_usage"),
            "highest_cpu": self.get_highest("cpu_usage"),
            "average_memory": self.get_average("memory_usage"),
            "highest_memory": self.get_highest("memory_usage"),
            "average_temperature": self.get_average("cpu_temperature"),
            "highest_temperature": self.get_highest("cpu_temperature"),
        }