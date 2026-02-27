#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import datetime
import os
import sys
import time

import matplotlib.pyplot as plt
import requests
from smbus2 import SMBus

# Add the repository root to the python path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    LOG_DIR, PLOT_DIR, INTERVAL_MINUTES,
    LAT, LON, I2C_BUS, PJ_ADDR, REG_BATTERY_LEVEL,
    MANAGE_SERVICES_BY_SUNRISE_SUNSET
)

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)


def get_current_solar_radiation(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "shortwave_radiation",
        "timezone": "auto"
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("current", {}).get("shortwave_radiation")
    except Exception as e:
        print("Failed to fetch solar radiation:", e)
        return None


def get_sunrise_sunset(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "sunrise,sunset",
        "timezone": "auto",
        "forecast_days": 1
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        daily = data.get("daily", {})
        sunrise = daily.get("sunrise", [None])[0]
        sunset = daily.get("sunset", [None])[0]
        return sunrise, sunset
    except Exception as e:
        print("Failed to fetch sunrise/sunset:", e)
        return None, None


def manage_services(sunrise_iso, sunset_iso):
    """
    Starts birdfeeder-stream and nginx at sunrise, stops them at sunset.
    """
    if not MANAGE_SERVICES_BY_SUNRISE_SUNSET:
        return

    if not sunrise_iso or not sunset_iso:
        return

    now = datetime.datetime.now()
    try:
        sunrise = datetime.datetime.fromisoformat(sunrise_iso)
        sunset = datetime.datetime.fromisoformat(sunset_iso)
    except Exception as e:
        print(f"Error parsing sunrise/sunset times: {e}")
        return

    is_day = sunrise <= now <= sunset

    # Check if services are already in the correct state to avoid log noise
    # We use 'systemctl is-active' to check the status
    stream_active = os.system("systemctl is-active birdfeeder-stream.service >/dev/null 2>&1") == 0
    nginx_active = os.system("systemctl is-active nginx.service >/dev/null 2>&1") == 0
    backend_active = os.system("systemctl is-active birdfeeder-backend.service >/dev/null 2>&1") == 0

    if is_day:
        if not stream_active or not nginx_active or not backend_active:
            print(f"Day time ({sunrise_iso} to {sunset_iso}). Turning services ON.")
            os.system("sudo systemctl start birdfeeder-stream.service nginx.service birdfeeder-backend.service")
    else:
        if stream_active or nginx_active or backend_active:
            print(f"Night time. Turning services OFF.")
            os.system("sudo systemctl stop birdfeeder-stream.service nginx.service birdfeeder-backend.service")


def get_battery_percentage():
    try:
        with SMBus(I2C_BUS) as bus:
            bus.write_byte(PJ_ADDR, REG_BATTERY_LEVEL)
            time.sleep(0.1)
            charge = bus.read_byte(PJ_ADDR)
        return charge
    except Exception as e:
        print("Failed to read battery I2C:", e)
        return None


def get_stable_battery_percentage(max_retries=3, threshold=10):
    log_file, _ = get_today_filepaths()
    _, percentages, _ = read_battery_data(log_file)
    last_valid = percentages[-1] if percentages else None

    for attempt in range(max_retries):
        val = get_battery_percentage()
        if val is None:
            print(f"Attempt {attempt + 1}: Failed to read battery.")
            time.sleep(1)
            continue
        if last_valid is None or abs(val - last_valid) <= threshold:
            return val
        else:
            print(f"Attempt {attempt + 1}: Read value {val}% differs from last valid {last_valid}%, retrying...")
            time.sleep(1)
    print(f"Using last value {val}% despite repeated bad readings.")
    return val


def get_today_filepaths():
    today = datetime.date.today().isoformat()
    log_file = os.path.join(LOG_DIR, f"battery_data_{today}.csv")
    plot_file = os.path.join(PLOT_DIR, f"battery_plot_{today}.png")
    return log_file, plot_file


def append_battery_data(log_file, timestamp, percentage, solar):
    file_exists = os.path.isfile(log_file)
    with open(log_file, "a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "percentage", "solar_radiation_Wm2"])
        writer.writerow([timestamp, percentage, solar])

    # Also maintain a fixed-name CSV for the frontend
    latest_file = os.path.join(LOG_DIR, "latest_battery_data.csv")
    import shutil
    shutil.copyfile(log_file, latest_file)


def read_battery_data(log_file):
    timestamps, percentages, solar_values = [], [], []
    if not os.path.isfile(log_file):
        return timestamps, percentages, solar_values
    with open(log_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamps.append(datetime.datetime.fromisoformat(row["timestamp"]))
            percentages.append(float(row["percentage"]))
            solar_values.append(float(row["solar_radiation_Wm2"]))
    return timestamps, percentages, solar_values


def plot_battery(timestamps, percentages, solar_values, plot_file):
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(timestamps, percentages, marker='o', label="Battery %")
    plt.ylabel("Battery %")
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(timestamps, solar_values, marker='x', color="orange", label="Solar Radiation (W/m2)")
    plt.ylabel("Solar Radiation W/m2")
    plt.xlabel("Time")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()


def cleanup_old_files(directory, max_files=10):
    files = [os.path.join(directory, f) for f in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, f))]
    if len(files) <= max_files:
        return
    files.sort(key=os.path.getmtime)
    for f in files[:-max_files]:
        try:
            os.remove(f)
            print(f"Removed old file: {f}")
        except Exception as e:
            print(f"Failed to remove {f}: {e}")


def main_loop():
    last_day = None
    sunrise, sunset = None, None

    while True:
        now = datetime.datetime.now()
        today = now.date()

        # Update sunrise/sunset once a day or if missing
        if last_day != today or sunrise is None or sunset is None:
            sunrise, sunset = get_sunrise_sunset(LAT, LON)
            last_day = today
            if sunrise and sunset:
                print(f"Fetched sunrise/sunset for {today}: {sunrise} / {sunset}")

        # Manage services based on current time
        manage_services(sunrise, sunset)

        timestamp = now.isoformat(timespec='seconds')
        log_file, plot_file = get_today_filepaths()

        percentage = get_stable_battery_percentage()
        solar = get_current_solar_radiation(LAT, LON)
        if percentage is not None and solar is not None:
            append_battery_data(log_file, timestamp, percentage, solar)
            print(f"[{timestamp}] Battery: {percentage}% | Solar: {solar} W/m2")
        else:
            print(f"[{timestamp}] Failed to read battery or solar radiation.")

        # Ensure latest_battery_data.csv exists even if just started for the first time today
        latest_file = os.path.join(LOG_DIR, "latest_battery_data.csv")
        if os.path.exists(log_file) and not os.path.exists(latest_file):
            import shutil
            shutil.copyfile(log_file, latest_file)

        timestamps, percentages, solar_values = read_battery_data(log_file)
        if timestamps and percentages:
            plot_battery(timestamps, percentages, solar_values, plot_file)

        cleanup_old_files(LOG_DIR, max_files=10)
        cleanup_old_files(PLOT_DIR, max_files=10)

        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Script terminated by user.")
