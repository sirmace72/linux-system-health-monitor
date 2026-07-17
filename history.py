import json
from datetime import datetime



class HistoryLogger:
    def __init__(self, filename="history.json"):
        self.filename = filename
    
    def save_report(self, report):
        report["timestamp"] = datetime.now().isoformat()
        