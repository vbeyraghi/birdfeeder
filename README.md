# BirdFeeder Project

A web application for monitoring and managing bird feeders with real-time video streaming and data visualization.

## Features

- Real-time video streaming from a connected camera (HLS)
- Bird activity monitoring
- Battery & Solar status monitoring with PiJuice (Real-time tracking and trends)
- Secure access via HTTPS and Basic Auth
- Web-based interface built with Angular
- Automated setup and startup

## Prerequisites

- Debian-based Linux system (Ubuntu/Raspberry Pi OS)
- Internet connection
- Root/sudo privileges
- Camera hardware support
- PiJuice hardware (optional, for battery monitoring)

## Quick Setup

1. **Create a DNS Domain**:
    - Go to [DuckDNS](https://www.duckdns.org/) or a similar service.
    - Create a subdomain (e.g., `birdfeeder-beyragva.duckdns.org`).
    - Point it to your home's external IP address.

2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/birdfeeder.git
   cd birdfeeder
   ```

3. Run the setup script:
   ```bash
   bash scripts/setup.sh
   ```
   This will:
    - Update system packages
    - Install required dependencies (Python 3, FFmpeg, libcamera-apps, PiJuice)
    - Install Node.js v22.12.0
    - Prompt for your DNS domain and set up Certbot for automated SSL certificates
    - Set up Nginx with Basic Auth
    - Create a Python virtual environment for battery monitoring
    - Configure automatic startup via systemd services

During setup, you will be prompted to:

- Enter your DNS domain (e.g., `birdfeeder-beyragva.duckdns.org`).
- Create credentials for Basic Auth (default user: `beyraghi-volant`).

## Configuration

Before running the application, configure your settings in `browser/assets/config.json`:

```json 
{
  "streamUrl": "https://birdfeeder-beyragva.duckdns.org/streams/stream.m3u8",
  "title": "Birdfeeder",
  "description": "Welcome to our live bird feeder camera. Watch nature up close!",
  "startStream": "Start stream"
}
```

Key settings to modify:

- `streamUrl`: Update with your camera's stream URL. Use your **domain name** (e.g.,
  `https://your-domain.duckdns.org/streams/stream.m3u8`).
- `title`: Your preferred page title
- `description`: Custom welcome message

### Video Quality

To adjust the video quality (resolution, framerate, and bitrate), edit `scripts/video_config.sh`. This file is created
during setup based on `scripts/video_config.example.sh`.

Available parameters:

- `WIDTH`: Video width in pixels (e.g., 1920, 1280)
- `HEIGHT`: Video height in pixels (e.g., 1080, 720)
- `FRAMERATE`: Frames per second (e.g., 30)
- `BITRATE`: Bitrate in bps (e.g., 5000000 for 5Mbps)

After changing these settings, restart the application by running `sudo systemctl restart birdfeeder-stream` or
rebooting.

### Performance & Latency Optimization

If you experience stream lag or high latency:

1. **Resolution & Bitrate**: Lowering `WIDTH`, `HEIGHT`, and `BITRATE` in `scripts/video_config.sh` significantly
   reduces the load on the Raspberry Pi's CPU/GPU and network bandwidth.
2. **Process Priority**: The streaming service is configured with high priority (`Nice=-10`), while the battery
   monitoring service runs at the lowest possible priority (`Nice=15`, `CPUSchedulingPolicy=idle`). This ensures the
   camera stream always has priority.
4. **Nginx Cache**: We've reduced the segment cache duration to 1 second in `nginx/hls.conf.tpl` to improve response
   times for the player.
5. **Nginx Throughput**: Optimized Nginx with `tcp_nopush` and `tcp_nodelay` to deliver small HLS segments faster.

To apply these systemd and Nginx changes after an update, re-run the setup script:

```bash
bash scripts/setup.sh
```

Or manually reload the services:

```bash
sudo systemctl daemon-reload
sudo systemctl restart birdfeeder-stream
sudo systemctl restart birdfeeder-battery
sudo systemctl restart nginx
```

### Battery Monitoring

Battery monitoring settings can be found in `battery/battery_status_config.py`. This file is created during setup based
on `battery/battery_status_config.example.py`.

Key settings:

- `INTERVAL_MINUTES`: Frequency of battery status updates.
- `LAT`, `LON`: Geographic coordinates for fetching solar radiation and sunrise/sunset data.
- `MANAGE_SERVICES_BY_SUNRISE_SUNSET`: If set to `True`, the script will automatically start `birdfeeder-stream.service`
  and `nginx.service` at sunrise and stop them at sunset to conserve power.

The script automatically cleans up old log files and plots, keeping only the **10 most recent** of each to save space.

## Configuration & Deployment

This section covers the initial setup on the device and the steps required when deploying it to a new location.

### 1. Initial Configuration (From Scratch)

For a first-time setup on a new device, follow these steps:

1. **Run the setup script** (`bash scripts/setup.sh`). This handles package installation, Nginx configuration, and
   initial SSL setup.
2. **Configure basic settings** in `browser/assets/config.json` (ensure `streamUrl` uses your domain).
3. **Adjust video quality** in `scripts/video_config.sh` (optional).
4. **Set up battery monitoring** in `battery/battery_status_config.py` (optional).

*Note: If you do not wish to monitor battery status, you should disable the `birdfeeder-battery` service:*

```bash
sudo systemctl stop birdfeeder-battery
sudo systemctl disable birdfeeder-battery
```

### 2. Deployment

When deploying the device at its final location, only the following steps are required:

1. **Static IP Address**: Configure your router to assign a **static local IP address** to the Raspberry Pi (e.g.,
   `192.168.1.50`) based on its MAC address. This ensures port forwarding rules remain valid.
2. **Ports (Port Forwarding)**: Map the following ports in your router's settings to the Raspberry Pi's static local IP:

| External Port | Internal Port | Protocol | Service                        |
|:--------------|:--------------|:---------|:-------------------------------|
| 80            | 80            | TCP      | HTTP (Redirects to HTTPS)      |
| 443           | 443           | TCP      | HTTPS (Web Interface & Stream) |
| 2222          | 22            | TCP      | SSH (Remote Management)        |

*Note: Port 2222 is recommended for external SSH to avoid common brute-force attacks on the default port 22.*

3. **DNS**: Update your DNS domain (e.g., DuckDNS) to point to the **new external IP address** of the deployment
   location.

## Accessing the Web Interface

After completing the setup, the application starts automatically. You can access it via:

- Open your web browser
- Navigate to `https://your-domain-name`
- Click on the stream button
- Log in with the credentials created during setup.

Replace `your-domain-name` with your actual DNS domain (e.g., `birdfeeder-beyragva.duckdns.org`).

## Automatic Startup

The setup script configures the application to start automatically on system boot using `systemd` services.

Two services are created:

- `birdfeeder-battery.service`: Manages the battery monitoring script.
- `birdfeeder-stream.service`: Manages the camera streaming process.

You can manage these services using `systemctl`:

```bash
# Check status
sudo systemctl status birdfeeder-stream
sudo systemctl status birdfeeder-battery

# View logs
journalctl -u birdfeeder-stream -f
journalctl -u birdfeeder-battery -f

# Restart services
sudo systemctl restart birdfeeder-stream
```

## Troubleshooting

If you cannot access the web interface:

1. Check if Nginx is running: `sudo systemctl status nginx`
2. Check if the camera stream is being generated: `ls -l ./streams/`
3. Verify your firewall settings allow ports 80 and 443: `sudo ufw status`
4. Ensure your device is connected to the network
5. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`

## Future Improvements

Here are some ideas for future enhancements to the BirdFeeder project:

- **Motion Detection & Recording**: Implement motion detection to start recording or take snapshots only when activity
  is detected, saving storage and power.
- **Media Gallery**: Add a web gallery to view and manage saved video snippets and photos captured during activity.
- **Low-Latency Streaming**: Explore solutions lower latency streaming.

## Support

For issues and support, please open an issue in the GitHub repository.