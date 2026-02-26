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
  "streamUrl": "https://your-device-ip/streams/stream.m3u8",
  "title": "Birdfeeder",
  "description": "Welcome to our live bird feeder camera. Watch nature up close!",
  "startStream": "Start stream"
}
```

Key settings to modify:

- `streamUrl`: Update with your camera's stream URL (use HTTPS)
- `title`: Your preferred page title
- `description`: Custom welcome message

## Running the Application

1. Start the application:
   ```bash
   bash start.sh
   ```

2. Access the web interface:
    - Open your web browser
    - Navigate to `https://your-device-ip/birdfeeder`
    - You will need to accept the self-signed certificate if prompted.
    - Log in with the credentials created during setup.

   Replace `your-device-ip` with your device's actual IP address.

## Automatic Startup

The setup script configures the application to start automatically on system boot using cron (via root's crontab).

## Troubleshooting

If you cannot access the web interface:

1. Check if Nginx is running: `sudo systemctl status nginx`
2. Check if the camera stream is being generated: `ls -l ./streams/`
3. Verify your firewall settings allow ports 80 and 443: `sudo ufw status`
4. Ensure your device is connected to the network
5. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`

## Support

For issues and support, please open an issue in the GitHub repository.