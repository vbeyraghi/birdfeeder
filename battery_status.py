import csv
import datetime
import json
import matplotlib.pyplot as plt
import os
import subprocess
import time
from smbus2 import SMBus

# Configuration
LOG_DIR = "battery_logs"
PLOT_DIR = "battery_plots"
INTERVAL_MINUTES = 10

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)


def get_battery_percentage():
    try:
        BUS = 1
        ADDRESS = 0x14
        CMD_CHARGE = 0x41  # command code for charge level

        with SMBus(BUS) as bus:
            bus.write_byte(ADDRESS, CMD_CHARGE)
            time.sleep(0.1)  # brief delay (often required)
            charge = bus.read_byte(ADDRESS)
        return charge
    except Exception as e:
        print(f"Error reading battery level via I2C: {e}")
        return None


def get_stable_battery_percentage(max_retries=3, threshold=10):
    """
    Attempts to read battery percentage, retrying if value deviates 
    too much from last valid reading.
    """
    log_file, _ = get_today_filepaths()
    _, percentages = read_battery_data(log_file)

    last_valid = percentages[-1] if percentages else None

    for attempt in range(max_retries):
        val = get_battery_percentage()
        if val is None:
            print(f"Attempt {attempt + 1}: Failed to read battery.")
            time.sleep(1)
            continue

        if last_valid is None:
            # No previous data, accept first reading
            return val

        if abs(val - last_valid) <= threshold:
            return val
        else:
            print(f"Attempt {attempt + 1}: Read value {val}% differs from last valid {last_valid}%, retrying...")
            time.sleep(1)
    print(f"Using last valid value {last_valid}% due to repeated bad readings.")
    return last_valid


def get_today_filepaths():
    today = datetime.date.today().isoformat()
    log_file = os.path.join(LOG_DIR, f"battery_data_{today}.csv")
    plot_file = os.path.join(PLOT_DIR, f"battery_plot_{today}.png")
    return log_file, plot_file


def append_battery_data(log_file, timestamp, percentage):
    file_exists = os.path.isfile(log_file)
    with open(log_file, "a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "percentage"])
        writer.writerow([timestamp, percentage])


def read_battery_data(log_file):
    timestamps, percentages = [], []
    if not os.path.isfile(log_file):
        return timestamps, percentages
    with open(log_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamps.append(datetime.datetime.fromisoformat(row["timestamp"]))
            percentages.append(float(row["percentage"]))
    return timestamps, percentages


def plot_battery(timestamps, percentages, plot_file):
    plt.figure(figsize=(10, 4))
    plt.plot(timestamps, percentages, marker='o')
    plt.title("Battery Percentage Over Time")
    plt.xlabel("Time")
    plt.ylabel("Battery %")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()


def main_loop():
    while True:
        now = datetime.datetime.now()
        timestamp = now.isoformat(timespec='seconds')
        log_file, plot_file = get_today_filepaths()

        percentage = get_stable_battery_percentage()
        if percentage is not None:
            append_battery_data(log_file, timestamp, percentage)
            print(f"[{timestamp}] Battery: {percentage}%")
        else:
            print(f"[{timestamp}] Failed to read battery.")

        timestamps, percentages = read_battery_data(log_file)
        if timestamps and percentages:
            plot_battery(timestamps, percentages, plot_file)
            print(f"Plot saved: {plot_file}")

        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Script terminated by user.")
