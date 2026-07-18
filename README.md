# Linux System Health Monitor

A comprehensive system health monitoring tool for Linux with HP fan control integration. This utility monitors your system's performance, temperature, and network status, and provides an interactive menu-driven interface.

## Features

- **Real-time System Monitoring**: CPU usage, memory usage, and disk usage
- **Temperature Monitoring**: CPU temperature tracking (AMD Ryzen with k10temp sensor)
- **Network Health**: Active network interface, IP address, gateway connectivity, and ping times
- **HP Fan Control**: Set fans to maximum/minimum speed and check current fan speeds
- **History Logging**: Automatically saves all health reports to a JSON file for tracking trends
- **Status Alerts**: Color-coded status indicators (Healthy, Warning, Critical) based on configurable thresholds

## Hardware Requirements

- Linux operating system (Ubuntu, Debian, Fedora, etc.)
- For HP fan control: HP laptop with AMD Ryzen processor and hwmon fan controller
- For temperature monitoring: System with psutil-supported temperature sensors

## Installation

### Dependencies

```bash
pip3 install psutil
```

### Setup

1. Navigate to the project directory:
   ```bash
   cd /home/sirmace72/linux-system-health-monitor
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install psutil
   ```

4. Make the script executable (optional):
   ```bash
   chmod +x main.py
   ```

## Usage

### Interactive Menu

Run the monitor directly:
```bash
python3 main.py
```

The program presents an interactive menu:

1. **Show System Health Report** - Displays current system status with all metrics
2. **Show History Summary** - Shows historical statistics from saved reports
3. **Set Fan to Maximum Speed** - Sets fans to 100% PWM speed
4. **Set Fan to Minimum Speed** - Sets fans to minimum PWM speed
5. **Check Current Fan Speed** - Shows current fan RPM values
6. **Exit** - Exit the program

### Headless Mode

You can also get a quick system check without the menu:
```bash
python3 -c "from monitor import SystemHealthMonitor; from history import HistoryLogger; m = SystemHealthMonitor(); r = m.get_system_report(); l = HistoryLogger(); l.save_report(r); print(r)"
```

## How It Works

### Architecture

The project uses a modular design with separate modules for each concern:

```
linux-system-health-monitor/
├── main.py              # Main entry point with interactive menu
├── monitor.py           # Orchestrates all monitoring components
├── history.py           # JSON report storage and history tracking
├── network.py           # Network interface and connectivity monitoring
├── system_info.py       # System metadata collection
├── metrics.py           # Resource metrics (CPU, RAM, disk)
├── temperatures.py      # Temperature monitoring via psutil
├── health.py            # Status threshold evaluation
├── hp_fan_control.py    # HP-specific fan control via hwmon
├── README.md            # This documentation file
└── history.json         # Auto-generated history file
```

### Component Details

#### SystemInfo (system_info.py)
Collects basic system metadata:
- Hostname
- Operating system and version
- Kernel version
- System architecture
- CPU model name (read from /proc/cpuinfo)

#### SystemMetrics (metrics.py)
Uses `psutil` to gather resource usage statistics:
- CPU usage percentage
- Memory usage percentage
- Disk usage percentage

#### TemperatureMonitor (temperatures.py)
Monitors CPU temperature using `psutil.sensors_temperatures()`:
- Supports AMD Ryzen processors with k10temp sensor
- Returns temperature in Celsius or None if sensor not available
- Labels: "Tctl" (total package temperature)

#### HealthMonitor (health.py)
Evaluates metrics against predefined thresholds:
- CPU/Memory/Disk: 70% = Warning, 90% = Critical, <70% = Healthy
- Temperature: 85°C = Critical, 70-85°C = Warning, <70°C = Healthy
- Returns status strings for display in reports

#### NetworkMonitor (network.py)
Network connectivity information:
- Active network interface name
- IP address for that interface
- Default gateway address
- Gateway connectivity (ping test)
- Internet ping time (to 1.1.1.1)

#### HistoryLogger (history.py)
Persistent storage and history tracking:
- Saves complete reports to history.json
- Each report includes timestamp
- Tracks cumulative statistics (averages, highs, lows)
- Provides summary statistics on request

#### SystemHealthMonitor (monitor.py)
Main orchestration class that:
- Initializes all monitoring components
- Collects a complete system snapshot
- Combines all metrics into a unified report dictionary
- Returns comprehensive system status

#### HP Fan Control (hp_fan_control.py)
HP-specific fan management using Linux hwmon:
- Reads fan controller path from `/sys/class/hwmon/`
- Provides functions to set/get PWM values
- Supports HP Omen laptops with hwmon6 controller
- Safe error handling for unsupported hardware

### Data Flow

1. User selects "Show System Health Report" from menu
2. `SystemHealthMonitor` is instantiated
3. Each subsystem is queried (CPU, memory, disk, temp, network)
4. All metrics are combined into a single report dictionary
5. `HistoryLogger` saves the report with timestamp
6. Formatted output is displayed to user

### File Structure

**main.py**: Entry point with menu-driven interface
**monitor.py**: Main orchestration and report generation
**history.py**: JSON history file management
**network.py**: Network diagnostics and connectivity checks
**system_info.py**: System metadata collection
**metrics.py**: Resource usage via psutil
**temperatures.py**: CPU temperature monitoring
**health.py**: Threshold-based status evaluation
**hp_fan_control.py**: HP laptop fan control integration

## Configuration

### Thresholds

Edit `health.py` to customize thresholds:

```python
def get_usage_status(self, value):
    if value < 70:  # Warning threshold
        return "Warning"
    elif value < 90:  # Critical threshold
        return "Critical"
    else:
        return "Healthy"
```

### Custom History File

Modify `history.py` to use a different history file:

```python
def __init__(self, filename="custom_history.json"):
    self.filename = filename
```

## Output Format

### Health Report Output
```
========================================
       SYSTEM HEALTH REPORT
========================================
Hostname: your-hostname
CPU Usage: 12.3% - Healthy
Memory Usage: 45.6% - Healthy
Disk Usage: 25.7% - Healthy
CPU Temperature: 62.9°C - Healthy
Interface: wlan0
IP Address: 10.0.0.208
Gateway: 10.0.0.1
Gateway Ping: 4.71 ms
Internet: Online
Internet Ping: 24.6 ms
========================================
```

### History Summary Output
```
========================================
       HISTORY SUMMARY
========================================
Average CPU Usage: 8.2%
Highest CPU Usage: 24.5%
Average Memory Usage: 41.3%
Average CPU Temp: 61.5°C
Highest CPU Temp: 67.2°C
========================================
```

## Troubleshooting

### Temperature Not Showing
- Temperature sensors may not be available on all hardware
- Check with: `python3 -c "import psutil; print(psutil.sensors_temperatures())"`
- AMD Ryzen should show "k10temp" sensor

### Fan Control Not Working
- Ensure you have sudo privileges (fan control requires root)
- Check hwmon path with: `ls /sys/class/hwmon/`
- HP fans require specific PWM controllers (typically hwmon6)

### History File Issues
- Permission errors if running without sudo
- Check if history.json is writable
- Delete and recreate if corrupted

## License

This project is provided as-is for personal use on your own systems.

## Author

Created for Linux system health monitoring and HP fan control automation.

---

## Quick Start

```bash
cd /home/sirmace72/linux-system-health-monitor
source venv/bin/activate
pip install psutil
python3 main.py
```

Select option 1 to see your system health report!
