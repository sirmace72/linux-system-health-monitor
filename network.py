import subprocess


class NetworkMonitor:
    def get_active_interface(self):
        result = subprocess.run(
            ["ip", "route"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if line.startswith("default"):
                parts = line.split()

                if "dev" in parts:
                    return parts[parts.index("dev") + 1]

        return None

    def get_ip_address(self):
        interface = self.get_active_interface()

        if interface is None:
            return None

        result = subprocess.run(
            ["ip", "-4", "addr", "show", interface],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            line = line.strip()

            if line.startswith("inet "):
                return line.split()[1].split("/")[0]

        return None

    def get_default_gateway(self):
        result = subprocess.run(
            ["ip", "route"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if line.startswith("default"):
                parts = line.split()

                if "via" in parts:
                    return parts[parts.index("via") + 1]

        return None

    def get_gateway_connection_status(self):
        gateway = self.get_default_gateway()

        if gateway is None:
            return "No default gateway found."

        result = subprocess.run(
            ["ping", "-c", "1", gateway],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return f"Successfully connected to the gateway {gateway}."

        return f"Failed to connect to the gateway {gateway}."
    
    def get_ping_time(self, host):
        if host is None:
            return None

        result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True,
        text=True
    )

        if result.returncode != 0:
         return None

        return result.stdout
    
    def get_ping_time(self, host):
        if host is None:
            return None

        result = subprocess.run(
            ["ping", "-c", "1", host],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return None

        for line in result.stdout.splitlines():
            if "time=" in line:
                time_part = line.split("time=")[1]
                return float(time_part.split()[0])

        return None
    