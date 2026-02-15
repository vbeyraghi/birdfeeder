#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import datetime
import matplotlib.pyplot as plt
import os
import requests
import time
from battery_status_config import (
    LOG_DIR, PLOT_DIR, INTERVAL_MINUTES,
    LAT, LON, I2C_BUS, PJ_ADDR, REG_BATTERY_LEVEL
)
from smbus2 import SMBus

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


def get_battery_percentage():
    try:
        with SMBus(I2C_BUS) as bus:
            bus.write_byte(PJ_ADDR, REG_BATTERY_LEVEL)
            time.sleep(0.1)
            charge = bus.read_byte(PJ_ADDR)
        return charge
    except Exception as e:
        print("Erreur lecture batterie I2C:", e)
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


def main_loop():
    while True:
        now = datetime.datetime.now()
        timestamp = now.isoformat(timespec='seconds')
        log_file, plot_file = get_today_filepaths()

        percentage = get_stable_battery_percentage()
        solar = get_current_solar_radiation(LAT, LON)
        if percentage is not None and solar is not None:
            append_battery_data(log_file, timestamp, percentage, solar)
            print(f"[{timestamp}] Battery: {percentage}% | Solar: {solar} W/m2")
        else:
            print(f"[{timestamp}] Failed to read battery or solar radiation.")

        timestamps, percentages, solar_values = read_battery_data(log_file)
        if timestamps and percentages:
            plot_battery(timestamps, percentages, solar_values, plot_file)

        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Script terminated by user.")
