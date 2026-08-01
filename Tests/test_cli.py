import sys
from unittest.mock import patch

from cli import get_arguments


def test_parse_status_command(capsys) -> None:
    with patch.object(sys, "argv", ["main.py", "status"]):
        args = get_arguments()
        assert args.command == "status"


def test_parse_network_command(capsys) -> None:
    with patch.object(sys, "argv", ["main.py", "network"]):
        args = get_arguments()
        assert args.command == "network"


def test_parse_history_command(capsys) -> None:
    with patch.object(sys, "argv", ["main.py", "history"]):
        args = get_arguments()
        assert args.command == "history"


def test_parse_full_report_command(capsys) -> None:
    with patch.object(sys, "argv", ["main.py", "full-report"]):
        args = get_arguments()
        assert args.command == "full-report"
