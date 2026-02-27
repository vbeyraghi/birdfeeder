# Project Overview: BirdFeeder

A specialized web application for real-time bird feeder monitoring, featuring high-definition HLS video streaming and
battery/solar status tracking via PiJuice.

## 🏗️ Architecture Summary

- **Frontend**: Angular application (pre-built in `browser/`, source in `src/`). Served as a static site by Nginx.
- **Streaming Pipeline**: Captures raw video from Raspberry Pi Camera via `rpicam-vid`, pipes it to `ffmpeg` for HLS
  segment generation.
- **Backend/Monitoring**: Python script (`battery_status.py`) running in a dedicated virtual environment, tracking power
  metrics and external solar radiation. It provides a real-time CSV feed for the frontend.
- **Web Server**: Nginx handles SSL termination (HTTPS), Basic Authentication, Rate Limiting, and serves both the
  frontend and the HLS stream.

## 📁 Key Files & Directories

### Root Directory

- `battery_status.py`: Python daemon for battery/solar monitoring. Maintains `latest_battery_data.csv`.
- `battery_status_config.py`: Local configuration (I2C address, GPS coords for solar/sunrise-sunset API, service
  management toggle).
- `video_config.sh`: Video quality configuration (Resolution, Bitrate, Framerate).
- `video_config.example.sh`: Example video configuration.
- `setup.sh`: Automated installation and configuration script (Idempotent).
- `start.sh`: System entry point (starts monitoring and streaming).
- `README.md`: Human-readable documentation.
- `ai-context.md`: Technical context for AI assistants (this file).

### `browser/` (Compiled Frontend)

- `assets/config.json`: Runtime configuration for the UI (stream URL, page titles, battery refresh interval).
- `index.html`: Main SPA entry point.

### `nginx/`

- `nginx.conf`: Global Nginx configuration (worker settings, rate limit zones).
- `hls.conf.tpl`: Template for site-specific configuration (SSL, Auth, Locations).
- `mime.types`: Standard MIME type definitions.

### `src/` (Source)

- Angular source code (TypeScript, HTML, CSS).

## ⚙️ Operational Flows

1. **Deployment**: `bash setup.sh` installs system packages, Node.js, Python venv, generates self-signed ECDSA certs,
   and configures Nginx.
2. **Execution**: `bash start.sh` is triggered via `@reboot` cron. It initializes the `streams/` directory and starts
   the monitoring and streaming processes.
3. **Data Collection**: `battery_status.py` fetches local PiJuice metrics (I2C), external solar radiation, and
   sunrise/sunset data (Open-Meteo API). It logs to `battery_logs/`, generates PNG plots in `battery_plots/`, and
   updates `latest_battery_data.csv`.
4. **Service Management**: `battery_status.py` can automatically start/stop `birdfeeder-stream.service` and
   `nginx.service` at sunrise/sunset based on the `MANAGE_SERVICES_BY_SUNRISE_SUNSET` configuration.
5. **Data Delivery**: Nginx serves `latest_battery_data.csv` via the `/api/battery-data` endpoint. The Angular
   `SolarMonitor` component fetches and parses this CSV to display real-time metrics and historical trends. It
   calculates battery uptime and charging rates dynamically using a trend-based analysis of the last 5 data points.
5. **HLS Streaming**: `rpicam-vid` outputs raw H.264 which `ffmpeg` segments into 2-second `.ts` files. The playlist (
   `stream.m3u8`) is kept at a 3-segment window.
6. **User Access**: HTTPS on port 443. Protected by Basic Auth (`beyraghi-volant`).

## 🛡️ Security & Access

- **TLS/SSL**: Self-signed ECDSA (prime256v1) certificates located in `nginx/secrets/tls/`.
- **Authentication**: Basic Auth via `.htpasswd` in `nginx/secrets/`.
- **Rate Limiting**: Nginx restricts requests to 100r/s per IP to prevent DoS.
- **Firewall**: `ufw` configured to allow only SSH (22) and HTTPS (443).

## 📊 Technical Specs

- **Video**: Configurable via `video_config.sh` (default: 1080p @ 30fps).
- **Power Monitoring**: I2C (Address 0x14) communication with PiJuice.
- **Environment**: Python 3.x (venv: `battery-env`), Node.js v22, Nginx.
- **Solar/Meteo Data**: Open-Meteo API (Latitude: 50.646, Longitude: 4.571) for solar radiation and sunrise/sunset
  times.

## 🚀 Future Roadmap (Targeted Enhancements)

-   [ ] Motion detection and snippet recording.
-   [ ] Media gallery for captured clips.

---
*Note: This file is maintained by the AI assistant to provide context for future requests. Keep it updated after any
structural or configuration changes.*
