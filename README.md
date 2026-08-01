# Linux System Health Monitor

A comprehensive system health monitoring tool for Linux with HP fan control integration. This utility monitors your system's performance, temperature, network status, and provides an interactive menu-driven interface.

## Features

- **Real-time System Monitoring**: CPU usage, memory usage, disk usage, and swap usage
- **Temperature Monitoring**: CPU temperature tracking (AMD Ryzen with k10temp sensor)
- **GPU Monitoring**: NVIDIA (via pynvml) and AMD (via pyamdgpuinfo) GPU temperature/usage
- **Disk I/O Metrics**: Read/write throughput monitoring via psutil
- **Network Transfer Stats**: Bytes sent/received tracking
- **Disk SMART Health**: Drive health status via smartctl
- **Process Monitoring**: Top-N processes by CPU/memory usage
- **System Uptime**: Current system boot uptime
- **Network Health**: Active network interface, IP address, gateway connectivity, and ping times
- **HP Fan Control**: Set fans to maximum/minimum speed and check current fan speeds
- **History Logging**: Automatically saves all health reports to a JSON file for tracking trends
- **Color Output**: Color-coded status indicators via rich library
- **Configurable Thresholds**: All thresholds configurable via `config.toml`

## Hardware Requirements

- Linux operating system (Ubuntu, Debian, Fedora, etc.)
- For HP fan control: HP laptop with AMD Ryzen processor and hwmon fan controller
- For temperature monitoring: System with psutil-supported temperature sensors

## Installation

### Dependencies

```bash
pip install psutil rich
```

### Optional Dependencies

```bash
# NVIDIA GPU monitoring
pip install pynvml

# AMD GPU monitoring
pip install pyamdgpuinfo

# Disk SMART health
sudo apt install smartmontools
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
   pip install -e .
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
2. **Show Full Report** - Extended report with all partitions, processes, and SMART health
3. **Show History Summary** - Shows historical statistics from saved reports
4. **Set Fan to Maximum Speed** - Sets fans to 100% PWM speed
5. **Set Fan to 75/50/25%** - Intermediate fan speed options
6. **Set Fan to Minimum Speed** - Sets fans to minimum PWM speed
7. **Check Current Fan Speed** - Shows current fan RPM values
8. **Exit** - Exit the program

### Headless Mode

Run specific commands from the CLI:
```bash
# Quick status check
python3 main.py status

# Network status only
python3 main.py network

# History summary
python3 main.py history

# Full report
python3 main.py full-report
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
├── net_io.py            # Network transfer statistics
├── disk_io.py           # Disk I/O metrics
├── gpu.py               # GPU monitoring (NVIDIA/AMD)
├── smart_health.py      # Disk SMART health via smartctl
├── system_info.py       # System metadata collection
├── metrics.py           # Resource metrics (CPU, RAM, disk) + process monitoring
├── temperatures.py      # Temperature monitoring via psutil
├── health.py            # Status threshold evaluation
├── config.py            # Configuration loader
├── config.toml          # User-customizable configuration
├── color.py             # Color output helpers
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
- Swap usage
- System uptime (via `psutil.boot_time()`)

#### ProcessMonitor (metrics.py)
Top-N process tracking:
- Top processes by CPU usage
- Top processes by memory usage

#### TemperatureMonitor (temperatures.py)
Monitors CPU temperature using `psutil.sensors_temperatures()`:
- Supports AMD Ryzen processors with k10temp sensor
- Returns temperature in Celsius or None if sensor not available
- Labels: "Tctl" (total package temperature)

#### GPUMonitor (gpu.py)
GPU temperature and usage monitoring:
- NVIDIA GPUs via pynvml
- AMD GPUs via pyamdgpuinfo
- Returns name, temperature, usage %, memory used/total

#### DiskIOMonitor (disk_io.py)
Disk read/write throughput via `psutil.disk_io_counters()`:
- Per-disk read/write in MB
- I/O operation counts

#### NetworkTransferMonitor (net_io.py)
Network transfer tracking via `psutil.net_io_counters()`:
- Per-interface bytes sent/received
- Packet counts and drop statistics

#### SMARTMonitor (smart_health.py)
Disk health monitoring via smartctl:
- Health status (PASSED/FAILED)
- Temperature (when available)
- Power-on hours
- Requires smartmontools and sudo privileges

#### HealthMonitor (health.py)
Evaluates metrics against thresholds from config.toml:
- CPU/Memory/Disk usage thresholds
- Temperature thresholds
- Returns Healthy/Warning/Critical status strings

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

### Data Flow

1. User selects "Show System Health Report" from menu
2. `SystemHealthMonitor` is instantiated with config
3. Each subsystem is queried (CPU, memory, disk, temp, network, GPU, processes)
4. All metrics are combined into a single report dictionary
5. `HistoryLogger` saves the report with timestamp
6. Formatted, color-coded output is displayed to user

## Configuration

All settings are configured through `config.toml`:

### Thresholds
```toml
[thresholds]
usage_warning = 70    # Warning threshold for CPU/memory/disk usage
usage_critical = 90   # Critical threshold
temp_warning = 70     # Warning threshold for temperature (Celsius)
temp_critical = 85    # Critical threshold
```

### Display Options
```toml
[display]
show_gpu = true       # Show GPU info (requires pynvml or pyamdgpuinfo)
show_disk_io = true   # Show disk I/O stats
show_net_io = true    # Show network transfer stats
show_process = true   # Show top-N processes
top_n_processes = 5   # Number of top processes to display
show_smart = true     # Show SMART health (requires smartmontools)
color_output = true   # Enable color output (requires rich or colorama)
```

### Report Options
```toml
[report]
history_file = "history.json"
cpu_interval = 0.5
check_all_partitions = true
internet_ping_host = "1.1.1.1"
```

## Output Format

### Health Report Output
```
==================================================
       SYSTEM HEALTH REPORT
==================================================
  Hostname: your-hostname
  Uptime:   3d 14h 22m
  CPU:      12.3% - Healthy
  Memory:   45.6% - Healthy
  Disk:     25.7% - Healthy
  Temp:     62.9°C - Healthy
  ...
==================================================
```

### History Summary Output
```
==================================================
       HISTORY SUMMARY
==================================================
  Avg CPU:      8.2%
  Highest CPU:  24.5%
  Avg Memory:   41.3%
  Highest Mem:  52.1%
  Avg Temp:     61.5°C
  Highest Temp: 67.2°C
==================================================
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

### SMART Health Not Showing
- Install smartmontools: `sudo apt install smartmontools`
- SMART queries require sudo privileges
- Disable with `show_smart = false` in config.toml

### GPU Not Showing
- NVIDIA: Install pynvml package and NVIDIA drivers
- AMD: Install pyamdgpuinfo package
- Both are optional and auto-detected

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
pip install -e .
python3 main.py
```

Select option 1 to see your system health report!
