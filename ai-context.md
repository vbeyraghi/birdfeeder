# Project Overview: BirdFeeder

A specialized web application for real-time bird feeder monitoring, featuring high-definition HLS video streaming and
battery/solar status tracking via PiJuice.

## 🏗️ Architecture Summary

- **Frontend**: Angular application (pre-built in `browser/`, source in `src/`). Served as a static site by Nginx.
- **Streaming Pipeline**: Captures raw video from Raspberry Pi Camera via `rpicam-vid`, pipes it to `ffmpeg` for HLS
  segment generation.
- **Backend/Monitoring**:
    - `battery/monitor.py`: Python daemon tracking power metrics and external solar radiation.
    - FastAPI Backend (`backend/api.py`): Modular API for battery data, media capture, and gallery management.
        - `backend/routes/`: Route handlers for battery (`battery.py`) and media (`media.py`).
        - `backend/services/`: Business logic for media capture (`media_service.py`).
- **Web Server**: Nginx handles SSL termination (HTTPS), Basic Authentication, Rate Limiting, serves the frontend, HLS
  stream, and proxies API requests to the FastAPI backend.

## 📁 Key Files & Directories

### Root Directory

- `battery/monitor.py`: Python daemon for battery/solar monitoring. Maintains `latest_battery_data.csv`.
- `backend/`: FastAPI application directory.
    - `api.py`: Entry point for the backend.
    - `routes/`: Sub-modules for different API sections.
    - `services/`: Specialized services (e.g., media management).
- `gallery/`: Directory for stored image and video captures.
- `config.py`: Central configuration (I2C address, GPS coords for solar/sunrise-sunset API, service management toggle,
  API settings).
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
3. **Data Collection**: `battery/monitor.py` fetches local PiJuice metrics (I2C), external solar radiation, and
   sunrise/sunset data (Open-Meteo API). It logs to `battery_logs/`, generates PNG plots in `battery_plots/`, and
   updates `latest_battery_data.csv`.
4. **Service Management**: `battery/monitor.py` can automatically start/stop `birdfeeder-stream.service`,
   `nginx.service`, and `birdfeeder-backend.service` at sunrise/sunset based on the `MANAGE_SERVICES_BY_SUNRISE_SUNSET`
   configuration.
5. **Data Delivery**: Nginx proxies `/api/` requests to the FastAPI backend. The backend serves battery and solar data
   directly via JSON and manages the media gallery.
6. **Media Management**: Users can trigger image captures via `POST /api/media/capture` and video clips via
   `POST /api/media/clip`. Media is saved in `gallery/` and can be retrieved via `GET /api/media/gallery`.
7. **HLS Streaming**: `rpicam-vid` outputs raw H.264 which `ffmpeg` segments into 2-second `.ts` files. The playlist (
   `stream.m3u8`) is kept at a 3-segment window.
6. **User Access**: HTTPS on port 443. Protected by Basic Auth (`beyraghi-volant`).

## 🛡️ Security & Access

- **TLS/SSL**: Managed by Certbot (Let's Encrypt) for the configured domain. Certificates are stored in the standard
  `/etc/letsencrypt/` directory, with Nginx configured to use them.
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
-   [x] Media gallery for captured clips.

---
*Note: This file is maintained by the AI assistant to provide context for future requests. Keep it updated after any
structural or configuration changes.*
