import subprocess


def get_active_interface():
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


def get_ip_address():
    interface = get_active_interface()

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


def get_default_gateway():
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