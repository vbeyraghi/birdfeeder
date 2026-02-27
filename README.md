# BirdFeeder Project

A web application for monitoring and managing bird feeders with real-time video streaming and data visualization.

## Features

- Real-time video streaming from a connected camera (HLS)
- Bird activity monitoring
- Battery status monitoring with PiJuice
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

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/birdfeeder.git
   cd birdfeeder
   ```

2. Run the setup script:
   ```bash
   bash scripts/setup.sh
   ```
   This will:
    - Update system packages
    - Install required dependencies (Python 3, FFmpeg, libcamera-apps, PiJuice)
    - Install Node.js v22.12.0
    - Set up Nginx with SSL and Basic Auth
    - Create a Python virtual environment for battery monitoring
    - Configure automatic startup via systemd services

During setup, you will be prompted to create credentials for Basic Auth (default user: `beyraghi-volant`).

## Configuration

Before running the application, configure your settings in `browser/assets/config.json`:

```json 
{
  "streamUrl": "https://your-external-ip/streams/stream.m3u8",
  "title": "Birdfeeder",
  "description": "Welcome to our live bird feeder camera. Watch nature up close!",
  "startStream": "Start stream"
}
```

Key settings to modify:

- `streamUrl`: Update with your camera's stream URL. Use your **external IP** or **domain name** if accessing from
  outside your home network.
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

After changing these settings, restart the application by running `bash scripts/start.sh` or rebooting.

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
- `LAT`, `LON`: Geographic coordinates for fetching solar radiation data.

The script automatically cleans up old log files and plots, keeping only the **10 most recent** of each to save space.

## Deployment & Router Configuration

When deploying the device at its final location, follow these steps to ensure external access:

### 1. Static IP Address

Configure your router to assign a **static local IP address** to the Raspberry Pi (e.g., `192.168.1.50`) based on its
MAC address. This ensures port forwarding rules remain valid.

### 2. Port Forwarding

Map the following ports in your router's settings to the Raspberry Pi's static local IP:

| External Port | Internal Port | Protocol | Service                        |
|:--------------|:--------------|:---------|:-------------------------------|
| 80            | 80            | TCP      | HTTP (Redirects to HTTPS)      |
| 443           | 443           | TCP      | HTTPS (Web Interface & Stream) |
| 2222          | 22            | TCP      | SSH (Remote Management)        |

*Note: Port 2222 is recommended for external SSH to avoid common brute-force attacks on the default port 22.*

### 3. External IP Configuration

1. Find your **External IP Address** (e.g., by visiting [whatsmyip.org](https://www.whatsmyip.org)).
2. Update `browser/assets/config.json` with the external IP or your domain name in the `streamUrl` field.
3. If your external IP is dynamic, consider using a DDNS service (like No-IP or DuckDNS).

### 4. Configuration setup

To summarize, for a complete setup you should:

1. **Run the setup script** (`bash scripts/setup.sh`).
2. **Configure basic settings** in `browser/assets/config.json`.
3. **Adjust video quality** in `scripts/video_config.sh` (optional).
4. **Set up battery monitoring** in `battery/battery_status_config.py` (optional).
5. **Configure router port forwarding** for external access.

*Note: If you do not wish to monitor battery status, you should disable
the `birdfeeder-battery` service:*

```bash
sudo systemctl stop birdfeeder-battery
sudo systemctl disable birdfeeder-battery
```

### 5. SSL Certificates

The setup script generates a self-signed certificate. When accessing via HTTPS:

- Your browser will show a security warning. You must click "Advanced" and "Proceed to..." to continue.
- For a "clean" experience without warnings, you would need a domain name and a certificate from a CA like Let's
  Encrypt.

## Running the Application

1. Start the application:
   ```bash
   bash scripts/start.sh
   ```

2. Access the web interface:
    - Open your web browser
    - Navigate to `https://your-external-ip/birdfeeder`
    - You will need to accept the self-signed certificate if prompted.
    - Log in with the credentials created during setup.

   Replace `your-external-ip` with your device's actual external IP address or domain name.

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

- **Automated SSL Certificates**: Integrate [Certbot](https://certbot.eff.org/) with Let's Encrypt to replace
  self-signed certificates with trusted ones (requires a domain name).
- **Motion Detection & Recording**: Implement motion detection to start recording or take snapshots only when activity
  is detected, saving storage and power.
- **Media Gallery**: Add a web gallery to view and manage saved video snippets and photos captured during activity.
- **Dynamic Scheduling**: Use a weather/meteo API to automatically turn the camera and streaming on at sunrise and off
  at sunset to conserve power.
- **Local DNS Server**: Set up a local DNS server (like [Pi-hole](https://pi-hole.net/)
  or [AdGuard Home](https://adguard.com/en/adguard-home/overview.html)) to assign a friendly local domain name (e.g.,
  `birdfeeder.local`) to the device.
- **Solar Power Integration**: Add monitoring for solar charging status and efficiency if using a solar-powered PiJuice
  setup (Solar radiation data is already being collected).
- **Low-Latency Streaming**: Explore solutions lower latency streaming.

## Support

For issues and support, please open an issue in the GitHub repository.