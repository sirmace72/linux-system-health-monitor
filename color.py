#!/usr/bin/env python3
"""Color output helpers using rich or colorama fallback."""

import sys
from typing import Any


def _supports_color() -> bool:
    """Check if the terminal supports color."""
    if hasattr(sys.stdout, "isatty") and not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        return True
    return True


ColorMode = None
try:
    from rich.console import Console
    from rich.text import Text
    from rich.table import Table

    ColorMode = "rich"
except ImportError:
    try:
        import colorama

        colorama.init()
        ColorMode = "colorama"
    except ImportError:
        ColorMode = None


class ColorHelper:
    """Provide color output with graceful fallback."""

    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled and _supports_color()
        self._console: Any = None
        if self._enabled and ColorMode == "rich":
            from rich.console import Console

            self._console = Console()

    @property
    def enabled(self) -> bool:
        return self._enabled

    def colorize(self, text: str, color: str) -> str:
        """Apply color to text. Returns plain text if color is disabled."""
        if not self._enabled:
            return text
        if ColorMode == "colorama":
            return self._colorama_color(text, color)
        return text

    def print(self, text: str = "", color: str | None = None, **kwargs: Any) -> None:
        """Print with optional color."""
        if not self._enabled:
            print(text, **kwargs)
            return
        if ColorMode == "rich" and self._console:
            if color:
                self._console.print(f"[{color}]{text}[/{color}]", **kwargs)
            else:
                self._console.print(text, **kwargs)
            return
        if ColorMode == "colorama":
            colored = self._colorama_color(text, color) if color else text
            print(colored, **kwargs)
            return
        print(text, **kwargs)

    def status_label(self, label: str) -> str:
        """Colorize a status label (Healthy, Warning, Critical)."""
        if not self._enabled:
            return label
        if label == "Healthy":
            return f"[green]{label}[/green]" if ColorMode == "rich" else self._green(label)
        if label == "Warning":
            return (
                f"[yellow]{label}[/yellow]"
                if ColorMode == "rich"
                else self._yellow(label)
            )
        if label == "Critical":
            return f"[red]{label}[/red]" if ColorMode == "rich" else self._red(label)
        return label

    def print_table(
        self,
        headers: list[str],
        rows: list[list[str]],
        title: str | None = None,
    ) -> None:
        """Print a formatted table (rich) or plain fallback."""
        if ColorMode == "rich" and self._console and self._enabled:
            from rich.table import Table

            table = Table(title=title, show_header=True)
            for header in headers:
                table.add_column(header)
            for row in rows:
                table.add_row(*row)
            self._console.print(table)
            return
        for row in rows:
            print(" | ".join(row))

    # -- colorama helpers --

    @staticmethod
    def _colorama_color(text: str, color: str) -> str:
        import colorama

        mapping = {
            "green": colorama.Fore.GREEN,
            "yellow": colorama.Fore.YELLOW,
            "red": colorama.Fore.RED,
            "cyan": colorama.Fore.CYAN,
            "white": colorama.Fore.WHITE,
            "bold": colorama.Style.BRIGHT,
        }
        return f"{mapping.get(color, '')}{text}{colorama.Style.RESET_ALL}"

    @staticmethod
    def _green(text: str) -> str:
        import colorama

        return f"{colorama.Fore.GREEN}{text}{colorama.Style.RESET_ALL}"

    @staticmethod
    def _yellow(text: str) -> str:
        import colorama

        return f"{colorama.Fore.YELLOW}{text}{colorama.Style.RESET_ALL}"

    @staticmethod
    def _red(text: str) -> str:
        import colorama

        return f"{colorama.Fore.RED}{text}{colorama.Style.RESET_ALL}"
