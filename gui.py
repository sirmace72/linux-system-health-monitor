"""GNOME dashboard for Linux System Health Monitor.

Run with:

    python gui.py

Read-only: it collects the same data as the CLI through
``SystemHealthMonitor`` and displays it with GTK 4 + libadwaita.
"""

import logging
import platform
import threading
import time
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from config import Config
from gui_helpers import (
    STATUS_CRITICAL,
    STATUS_HEALTHY,
    STATUS_UNKNOWN,
    STATUS_WARNING,
    UNAVAILABLE,
    build_snapshot,
    status_style,
)
from monitor import SystemHealthMonitor

logger = logging.getLogger("shmonitor.gui")

REFRESH_INTERVAL_MS = 2500

APP_ID = "com.sirmace72.SystemHealthMonitor"

STATUS_CSS_CLASSES = {
    STATUS_HEALTHY: "status-healthy",
    STATUS_WARNING: "status-warning",
    STATUS_CRITICAL: "status-critical",
    STATUS_UNKNOWN: "status-unknown",
}


def _set_text(widget: Gtk.Widget, text: str) -> None:
    """Set label text via the right property depending on widget type."""
    if isinstance(widget, Gtk.Text):
        widget.set_text(text)
    elif isinstance(widget, Gtk.Label):
        widget.set_label(text)
    else:  # pragma: no cover - defensive
        widget.set_property("text", text)


def _set_status_label(label: Gtk.Label, text: str, css_class: str) -> None:
    for css in list(STATUS_CSS_CLASSES.values()):
        label.remove_css_class(css)
    label.add_css_class(css_class)
    label.set_text(text)


class HealthMonitorWindow(Adw.ApplicationWindow):
    """Main dashboard window built from native libadwaita widgets."""

    def __init__(self, app: Adw.Application, monitor: SystemHealthMonitor):
        super().__init__(
            application=app,
            title="System Health Monitor",
            default_width=900,
            default_height=750,
        )
        # Keep the window resizable both ways; never start maximized.
        self.set_size_request(600, 480)
        self._monitor = monitor
        self._refresh_lock = threading.Lock()

        self._build_ui()
        self._populate_sysinfo()
        self.set_visible(True)
        self._schedule_refresh()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        # Adw.ApplicationWindow
        # └── Adw.ToolbarView
        #     ├── Adw.HeaderBar
        #     └── Gtk.ScrolledWindow
        #         └── Adw.Clamp
        #             └── dashboard content
        toolbar = Adw.ToolbarView()

        header = Adw.HeaderBar()
        header.set_title_widget(
            Adw.WindowTitle(title="System Health Monitor")
        )
        toolbar.add_top_bar(header)

        # Whole dashboard scrolls vertically; never horizontally.
        scrolled = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            vexpand=True,
        )

        # Center the dashboard in a column at most 1000px wide.
        clamp = Adw.Clamp(
            maximum_size=1000,
            tightening_threshold=700,
        )

        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18,
            margin_top=18,
            margin_bottom=18,
        )

        # Status line
        self.status_line = Gtk.Label(
            label="Collecting system data…",
            wrap=True,
            xalign=0.0,
        )
        self.status_line.add_css_class("dim-label")
        content.append(self.status_line)

        content.append(self._build_system_health_panel())
        content.append(self._build_network_panel())
        content.append(self._build_gpu_panel())
        content.append(self._build_system_info_panel())

        clamp.set_child(content)
        scrolled.set_child(clamp)
        toolbar.set_content(scrolled)
        self.set_content(toolbar)

    def _card(self, title: str) -> tuple[Adw.PreferencesGroup, Gtk.Box]:
        card = Adw.PreferencesGroup(title=title)
        rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.add(rows)
        return card, rows

    def _metric_row(
        self, rows: Gtk.Box, title: str
    ) -> tuple[Gtk.Label, Gtk.ProgressBar, Gtk.Label]:
        grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        name_label = Gtk.Label(label=title, xalign=0.0)
        name_label.set_hexpand(True)
        status_label = Gtk.Label(label=UNAVAILABLE)
        status_label.add_css_class("status-unknown")
        header.append(name_label)
        header.append(status_label)
        # ProgressBar (not LevelBar): it renders correctly as a full-width
        # row inside a vertical box, unlike LevelBar which collapses.
        progress = Gtk.ProgressBar()
        progress.set_fraction(0.0)
        progress.set_hexpand(True)
        value_label = Gtk.Label(label=UNAVAILABLE, xalign=0.0)
        value_label.add_css_class("dim-label")
        grid.append(header)
        grid.append(progress)
        grid.append(value_label)
        rows.append(grid)
        return status_label, progress, value_label

    def _kv_row(self, rows: Gtk.Box, key: str) -> Gtk.Label:
        grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        key_label = Gtk.Label(label=key, xalign=0.0)
        key_label.add_css_class("dim-label")
        value_label = Gtk.Label(
            label=UNAVAILABLE,
            xalign=0.0,
            wrap=True,
            hexpand=True,
            valign=Gtk.Align.START,
        )
        value_label.add_css_class("value")
        grid.append(key_label)
        grid.append(value_label)
        rows.append(grid)
        return value_label

    def _build_system_health_panel(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title="System Health")
        rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        group.add(rows)

        cpu_status, cpu_progress, cpu_value = self._metric_row(rows, "CPU usage")
        mem_status, mem_progress, mem_value = self._metric_row(rows, "Memory usage")
        disk_status, disk_progress, disk_value = self._metric_row(rows, "Disk usage")
        temp_row = self._temp_row(rows)

        self.cpu_status_label = cpu_status
        self.cpu_progress = cpu_progress
        self.cpu_value = cpu_value
        self.mem_status_label = mem_status
        self.mem_progress = mem_progress
        self.mem_value = mem_value
        self.disk_status_label = disk_status
        self.disk_progress = disk_progress
        self.disk_value = disk_value
        self.temp_label = temp_row[0]
        self.temp_status_label = temp_row[1]

        return group

    def _temp_row(self, rows: Gtk.Box) -> tuple[Gtk.Label, Gtk.Label]:
        grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        name_label = Gtk.Label(label="CPU temperature", xalign=0.0)
        name_label.set_hexpand(True)
        status_label = Gtk.Label(label=UNAVAILABLE)
        status_label.add_css_class("status-unknown")
        header.append(name_label)
        header.append(status_label)
        value_label = Gtk.Label(label=UNAVAILABLE, xalign=0.0)
        value_label.add_css_class("dim-label")
        grid.append(header)
        grid.append(value_label)
        rows.append(grid)
        return value_label, status_label

    def _kv_panel(self, title: str) -> tuple[Adw.PreferencesGroup, Gtk.Box]:
        group = Adw.PreferencesGroup(title=title)
        rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        group.add(rows)
        return group, rows

    def _build_network_panel(self) -> Adw.PreferencesGroup:
        group, rows = self._kv_panel("Network")
        self.nic_label = self._kv_row(rows, "Active interface")
        self.ip_label = self._kv_row(rows, "IPv4 address")
        self.gw_label = self._kv_row(rows, "Default gateway")
        self.gw_status_label = self._kv_row(rows, "Gateway reachable")
        self.conn_label = self._kv_row(rows, "Internet connectivity")
        self.ping_label = self._kv_row(rows, "Ping time")
        return group

    def _build_gpu_panel(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title="GPU")
        self.gpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        group.add(self.gpu_box)
        return group

    def _build_system_info_panel(self) -> Adw.PreferencesGroup:
        group, rows = self._kv_panel("System information")
        self.hostname_label = self._kv_row(rows, "Hostname")
        self.os_label = self._kv_row(rows, "Operating system")
        self.kernel_label = self._kv_row(rows, "Kernel")
        self.cpu_model_label = self._kv_row(rows, "CPU model")
        self.arch_label = self._kv_row(rows, "Architecture")
        self.uptime_label = self._kv_row(rows, "Uptime")
        return group

    def _populate_sysinfo(self) -> None:
        """Collect static system values once (fast, no blocking sensors)."""
        try:
            info = {
                "hostname": platform.node() or UNAVAILABLE,
                "os": f"{platform.system()} {platform.release()}",
                "kernel": platform.version(),
                "cpu_model": "",
                "architecture": platform.machine(),
            }
            try:
                with open(
                    "/proc/cpuinfo", encoding="utf-8", errors="replace"
                ) as handle:
                    for line in handle:
                        if line.lower().startswith("model name"):
                            info["cpu_model"] = line.split(":", 1)[1].strip()
                            break
            except OSError:
                pass
            self._sysinfo = info
            self.hostname_label.set_label(info["hostname"])
            self.os_label.set_label(info["os"])
            self.kernel_label.set_label(info["kernel"])
            self.cpu_model_label.set_label(info["cpu_model"] or UNAVAILABLE)
            self.arch_label.set_label(info["architecture"])
        except Exception:
            logger.exception("Failed to collect static system info")

    # ------------------------------------------------------------- refresh

    def _schedule_refresh(self) -> None:
        GLib.timeout_add(REFRESH_INTERVAL_MS, self._tick)

    def _tick(self) -> bool:
        if not self._refresh_lock.acquire(blocking=False):
            # Previous refresh still running; retry on the next tick.
            return True
        thread = threading.Thread(target=self._run_refresh, daemon=True)
        thread.start()
        return True

    def _run_refresh(self) -> None:
        try:
            try:
                report = self._monitor.get_system_report()
            except Exception:
                logger.exception("System report failed; showing Unavailable")
                report = {}
            snapshot = build_snapshot(report, getattr(self, "_sysinfo", None))
            GLib.idle_add(self._apply_snapshot, snapshot, None)
        finally:
            self._refresh_lock.release()

    # -------------------------------------------------------------- apply

    def _apply_snapshot(self, snapshot: dict[str, Any], _err: Any) -> bool:
        try:
            self._apply_metrics(snapshot)
            self._apply_network(snapshot)
            self._apply_gpus(snapshot)
            self.uptime_label.set_label(snapshot["uptime"])
            self.status_line.set_label(f"Last update {time.strftime('%H:%M:%S')}")
        except Exception:
            logger.exception("Failed to apply snapshot to widgets")
        return False

    def _apply_metric(
        self,
        snapshot: dict[str, Any],
        key: str,
        status_label: Gtk.Label,
        progress: Gtk.ProgressBar,
        value_label: Gtk.Label,
    ) -> None:
        metric = snapshot[key]
        _set_text(value_label, metric["usage"])
        percent = metric["usage_value"]
        # usage_value is a 0-100 percentage; GtkProgressBar expects 0.0-1.0.
        progress.set_fraction(percent / 100.0 if percent is not None else 0.0)
        normalized = status_style(metric["status"])
        _set_status_label(status_label, metric["status"], STATUS_CSS_CLASSES[normalized])

    def _apply_metrics(self, snapshot: dict[str, Any]) -> None:
        self._apply_metric(
            snapshot, "cpu", self.cpu_status_label, self.cpu_progress, self.cpu_value
        )
        self._apply_metric(
            snapshot, "memory", self.mem_status_label, self.mem_progress, self.mem_value
        )
        self._apply_metric(
            snapshot, "disk", self.disk_status_label, self.disk_progress, self.disk_value
        )

        temp = snapshot["temperature"]
        _set_text(self.temp_label, temp["value"])
        _set_status_label(
            self.temp_status_label,
            temp["status"],
            STATUS_CSS_CLASSES[status_style(temp["status"])],
        )

    def _apply_network(self, snapshot: dict[str, Any]) -> None:
        self.nic_label.set_label(snapshot["active_interface"])
        self.ip_label.set_label(snapshot["ip_address"])
        self.gw_label.set_label(snapshot["gateway"])
        self.gw_status_label.set_label(snapshot["gateway_reachable"])
        self.conn_label.set_label(snapshot["internet_connected"])
        self.ping_label.set_label(snapshot["ping_time"])

    @staticmethod
    def _clear_box(box: Gtk.Box) -> None:
        child = box.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            box.remove(child)
            child = nxt

    def _apply_gpus(self, snapshot: dict[str, Any]) -> None:
        gpus = snapshot["gpus"]
        self._clear_box(self.gpu_box)
        if not gpus:
            placeholder = Gtk.Label(label="None detected", xalign=0.0)
            placeholder.add_css_class("dim-label")
            self.gpu_box.append(placeholder)
            return
        for gpu in gpus:
            row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            name_label = Gtk.Label(label=gpu["label"], xalign=0.0, wrap=True)
            details = Gtk.Label(label=UNAVAILABLE, xalign=0.0, wrap=True)
            details.add_css_class("dim-label")
            parts = [
                p
                for p in (gpu["vendor"], gpu["usage"], gpu["temp"], gpu["mem"])
                if p != UNAVAILABLE
            ]
            if parts:
                _set_text(details, "   ".join(parts))
            row.append(name_label)
            row.append(details)
            self.gpu_box.append(row)


class HealthMonitorApp(Adw.Application):
    def __init__(self, monitor: SystemHealthMonitor):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self._monitor = monitor
        self._window: HealthMonitorWindow | None = None

    def do_activate(self) -> None:
        _load_css()
        if self._window is None:
            self._window = HealthMonitorWindow(self, self._monitor)
        self._window.present()


# Named GTK 4 color tokens (GTK4Color) resolve differently in light and
# dark themes, so the app follows the system GNOME theme automatically.
_CSS = b"""
.status-healthy { color: @success_color; font-weight: bold; }
.status-warning { color: @warning_color; font-weight: bold; }
.status-critical { color: @error_color; font-weight: bold; }
.status-unknown { color: @dim_color; font-weight: bold; }
"""

_css_loaded = False


def _apply_theme_preference() -> None:
    """Honor GNOME's dark-theme setting via AdwStyleManager.

    libadwaita warns (and ignores) the legacy
    ``gtk-application-prefer-dark-theme`` GtkSettings property, so read it,
    clear it, and map it onto ``AdwStyleManager.color-scheme``.  This must
    run before the first Adwaita widget/style-manager is created.
    """
    settings = Gtk.Settings.get_default()
    if settings is None:
        return
    prefer_dark = bool(settings.get_property("gtk-application-prefer-dark-theme"))
    settings.set_property("gtk-application-prefer-dark-theme", False)
    if prefer_dark:
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)


def _load_css() -> None:
    """Apply the status-colour stylesheet once the display exists."""
    global _css_loaded
    if _css_loaded:
        return
    display = Gdk.Display.get_default()
    if display is None:
        logger.debug("No display yet; CSS will be loaded on activation")
        return
    provider = Gtk.CssProvider()
    provider.load_from_data(_CSS)
    Gtk.StyleContext.add_provider_for_display(
        display,
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )
    _css_loaded = True


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    _apply_theme_preference()
    config = Config()
    monitor = SystemHealthMonitor(config=config)
    app = HealthMonitorApp(monitor)
    return app.run(None)


if __name__ == "__main__":
    raise SystemExit(main())
