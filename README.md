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
   bash setup.sh
   ```
   This will:
    - Update system packages
    - Install required dependencies (Python 3, FFmpeg, libcamera-apps, PiJuice)
    - Install Node.js v22.12.0
    - Set up Nginx with SSL and Basic Auth
    - Create a Python virtual environment for battery monitoring
    - Configure automatic startup via cron

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

### 4. SSL Certificates

The setup script generates a self-signed certificate. When accessing via HTTPS:

- Your browser will show a security warning. You must click "Advanced" and "Proceed to..." to continue.
- For a "clean" experience without warnings, you would need a domain name and a certificate from a CA like Let's
  Encrypt.

## Running the Application

1. Start the application:
   ```bash
   bash start.sh
   ```

2. Access the web interface:
    - Open your web browser
    - Navigate to `https://your-external-ip/birdfeeder`
    - You will need to accept the self-signed certificate if prompted.
    - Log in with the credentials created during setup.

   Replace `your-external-ip` with your device's actual external IP address or domain name.

## Automatic Startup

The setup script configures the application to start automatically on system boot using cron (via root's crontab).

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
- **Systemd Integration**: Replace the current cron-based startup with `systemd` services for better process management,
  automatic restarts, and centralized logging.
- **Solar Power Integration**: Add monitoring for solar charging status and efficiency if using a solar-powered PiJuice
  setup.
- **Low-Latency Streaming**: Explore WebRTC for even lower latency streaming compared to HLS.

## Support

For issues and support, please open an issue in the GitHub repository.