#!/usr/bin/env python3

"""HP Omen fan control."""

import glob
import os
import sys
import subprocess

def write_root(path, value):
    subprocess.run(
        ["sudo", "tee", path],
        input=str(value),
        text=True,
        stdout=subprocess.DEVNULL,
        check=True,
    )

def get_hwmon_path():
    """Find the HP hwmon controller automatically."""
    for name_file in glob.glob("/sys/class/hwmon/hwmon*/name"):
        try:
            with open(name_file, "r") as file:
                if file.read().strip() == "hp":
                    return os.path.dirname(name_file)
        except OSError:
            continue

    return None


def write_value(path, value):
    """Write a value to a sysfs control file."""
    with open(path, "w") as file:
        file.write(str(value))


def set_fan_speed(percent):
    """Set fan speed to a specific percentage (25, 50, 75, or 100)."""
    valid = [25, 50, 75, 100]
    if percent not in valid:
        print(f"ERROR: Invalid percentage. Choose from {valid}")
        return False

    pwm_value = round(percent / 100 * 255)
    hwmon_path = get_hwmon_path()

    if hwmon_path is None:
        print("ERROR: HP hwmon controller not found")
        return False

    try:
        write_root(f"{hwmon_path}/pwm1_enable", 1)
        write_root(f"{hwmon_path}/pwm1", pwm_value)
        print(f"✓ Fans set to {percent}% (PWM: {pwm_value}/255)")
        return True

    except subprocess.CalledProcessError as error:
        print(f"ERROR: {error}")
        return False


def set_max_speed():
    return set_fan_speed(100)


def set_min_speed():
    """Set fans to minimum speed (0%)."""
    hwmon_path = get_hwmon_path()

    if hwmon_path is None:
        print("ERROR: HP hwmon controller not found")
        return False

    try:
        write_root(f"{hwmon_path}/pwm1_enable", 1)
        write_root(f"{hwmon_path}/pwm1", 0)

        print("✓ Fans set to minimum speed")
        return True

    except subprocess.CalledProcessError as error:
        print(f"ERROR: {error}")
        return False

def get_current_speed():
    """Read actual fan RPM."""
    hwmon_path = get_hwmon_path()

    if hwmon_path is None:
        print("ERROR: HP hwmon controller not found")
        return None

    try:
        with open(f"{hwmon_path}/fan1_input", "r") as file:
            fan1 = int(file.read().strip())

        with open(f"{hwmon_path}/fan2_input", "r") as file:
            fan2 = int(file.read().strip())

        return fan1, fan2

    except OSError as error:
        print(f"ERROR: {error}")
        return None


def main():
    if os.geteuid() != 0:
        print("Please run this program with sudo:")
        print(f"sudo {sys.executable} {sys.argv[0]}")
        sys.exit(1)

    print("HP Fan Control")
    print("==============")
    print("1. Set maximum speed")
    print("2. Set minimum speed")
    print("3. Check current RPM")
    print("0. Exit")

    choice = input("Choose option: ").strip()

    if choice == "1":
        set_max_speed()

    elif choice == "2":
        set_min_speed()

    elif choice == "3":
        speeds = get_current_speed()

        if speeds is not None:
            fan1, fan2 = speeds
            print(f"Fan 1: {fan1} RPM")
            print(f"Fan 2: {fan2} RPM")

    elif choice == "0":
         print("Goodbye!")
         sys.exit(0)

    else:
        print("Invalid option")
    
    


if __name__ == "__main__":
    main()# test
