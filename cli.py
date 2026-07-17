import argparse


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Linux System Health Monitor"
    )

    parser.add_argument(
        "command",
        choices=[
            "status",
            "network",
            "history",
            "full-report",
        ]
    )

    return parser.parse_args()
