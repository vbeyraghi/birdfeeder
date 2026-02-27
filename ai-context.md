# Project Overview: BirdFeeder

A specialized web application for real-time bird feeder monitoring, featuring high-definition HLS video streaming and
battery/solar status tracking via PiJuice.

## 🏗️ Architecture Summary

- **Frontend**: Angular application (pre-built in `browser/`, source in `src/`). Served as a static site by Nginx.
- **Streaming Pipeline**: Captures raw video from Raspberry Pi Camera via `rpicam-vid`, pipes it to `ffmpeg` for HLS
  segment generation.
- **Backend/Monitoring**: Python script (`battery_status.py`) running in a dedicated virtual environment, tracking power
  metrics and external solar radiation.
- **Web Server**: Nginx handles SSL termination (HTTPS), Basic Authentication, Rate Limiting, and serves both the
  frontend and the HLS stream.

## 📁 Key Files & Directories

### Root Directory

- `battery_status.py`: Python daemon for battery/solar monitoring.
- `battery_status_config.py`: Local configuration (I2C address, GPS coords for solar API).
- `video_config.sh`: Video quality configuration (Resolution, Bitrate, Framerate).
- `video_config.example.sh`: Example video configuration.
- `setup.sh`: Automated installation and configuration script (Idempotent).
- `start.sh`: System entry point (starts monitoring and streaming).
- `README.md`: Human-readable documentation.
- `ai-context.md`: Technical context for AI assistants (this file).

### `browser/` (Compiled Frontend)

- `assets/config.json`: Runtime configuration for the UI (stream URL, page titles, UI orientation).
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
3. **Data Collection**: `battery_status.py` fetches local PiJuice metrics (I2C) and external solar radiation data (
   Open-Meteo API). It logs to `battery_logs/` and generates PNG plots in `battery_plots/`.
4. **HLS Streaming**: `rpicam-vid` outputs raw H.264 which `ffmpeg` segments into 2-second `.ts` files. The playlist (
   `stream.m3u8`) is kept at a 6-segment window.
5. **User Access**: HTTPS on port 443. Protected by Basic Auth (`beyraghi-volant`).

## 🛡️ Security & Access

- **TLS/SSL**: Self-signed ECDSA (prime256v1) certificates located in `nginx/secrets/tls/`.
- **Authentication**: Basic Auth via `.htpasswd` in `nginx/secrets/`.
- **Rate Limiting**: Nginx restricts requests to 100r/s per IP to prevent DoS.
- **Firewall**: `ufw` configured to allow only SSH (22) and HTTPS (443).

## 📊 Technical Specs

- **Video**: Configurable via `video_config.sh` (default: 4K @ 60fps @ 25Mbps).
- **Power Monitoring**: I2C (Address 0x14) communication with PiJuice.
- **Environment**: Python 3.x (venv: `battery-env`), Node.js v22, Nginx.
- **Solar Data**: Open-Meteo API (Latitude: 50.646, Longitude: 4.571).

## 🚀 Future Roadmap (Targeted Enhancements)

-   [ ] Automated SSL via Certbot/Let's Encrypt.
-   [ ] Motion detection and snippet recording.
-   [ ] Media gallery for captured clips.
-   [ ] Sunset/Sunrise scheduling for power conservation.
-   [ ] Migration to `systemd` services for better process management.

---
*Note: This file is maintained by the AI assistant to provide context for future requests. Keep it updated after any
structural or configuration changes.*
