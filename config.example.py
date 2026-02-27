import os

# Repository Root
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Directories
LOG_DIR = os.path.join(REPO_ROOT, "battery", "battery_logs")
PLOT_DIR = os.path.join(REPO_ROOT, "battery", "battery_plots")
GALLERY_DIR = os.path.join(REPO_ROOT, "gallery")
STREAMS_DIR = os.path.join(REPO_ROOT, "streams")

# Battery Monitoring
INTERVAL_MINUTES = 5
MANAGE_SERVICES_BY_SUNRISE_SUNSET = True
LATEST_BATTERY_CSV = os.path.join(LOG_DIR, "latest_battery_data.csv")

# Location (for Solar and Sunrise/Sunset)
LAT = 50.6462208
LON = 4.571136

# PiJuice I2C Settings
I2C_BUS = 1
PJ_ADDR = 0x14
REG_BATTERY_LEVEL = 0x41

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
