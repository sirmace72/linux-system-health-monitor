from history import HistoryLogger


def test_save_and_load_history(tmp_path):
    test_file = tmp_path / "history.json"
    logger = HistoryLogger(test_file)

    report = {
        "cpu_usage": 10,
        "memory_usage": 20,
        "cpu_temperature": 40,
    }

    logger.save_report(report)

    history = logger.load_history()

    assert len(history) == 1
    assert history[0]["cpu_usage"] == 10
    assert "timestamp" in history[0]

def test_get_average(tmp_path):
    test_file = tmp_path / "history.json"
    logger = HistoryLogger(test_file)

    logger.save_report({"cpu_usage": 10})
    logger.save_report({"cpu_usage": 20})

    assert logger.get_average("cpu_usage") == 15

def test_get_highest(tmp_path):
    test_file = tmp_path / "history.json"
    logger = HistoryLogger(test_file)

    logger.save_report({"cpu_usage": 10})
    logger.save_report({"cpu_usage": 25})
    logger.save_report({"cpu_usage": 15})

    assert logger.get_highest("cpu_usage") == 25
