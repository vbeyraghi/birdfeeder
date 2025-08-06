# BirdFeeder Project

A web application for monitoring and managing bird feeders with real-time video streaming and data visualization.

## Features

- Real-time video streaming from connected camera
- Bird activity monitoring
- Data visualization of feeding patterns
- Configurable camera settings
- Web-based interface

## Prerequisites

- Debian-based Linux system (Ubuntu/Raspberry Pi OS)
- Internet connection
- Root/sudo privileges
- Camera hardware support

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
    - Install required dependencies (Python 3, FFmpeg, libcamera-apps)
    - Install Node.js v22.12.0
    - Set up http-server
    - Create necessary directories
    - Configure automatic startup via cron

## Configuration

Before running the application, configure your settings in `/assets/config.json`:

```json 
{
  "streamUrl": "http://192.168.0.162:8080/streams/stream.m3u8",
  "title": "Birdfeeder",
  "description": "Welcome to our live bird feeder camera. Watch nature up close!",
  "startStream": "Start stream"
}
```

Key settings to modify:

- `streamUrl`: Update with your camera's stream URL
- `title`: Your preferred page title
- `description`: Custom welcome message

## Running the Application

1. Start the application:
   ```bash
   bash start.sh
   ```

2. Access the web interface:
    - Open your web browser
    - Navigate to `http://your-device-ip:8080`

   Replace `your-device-ip` with your device's actual IP address.

## Automatic Startup

The setup script configures the application to start automatically on system boot using cron.

## Troubleshooting

If you cannot access the web interface:

1. Check if the service is running: `ps aux | grep http-server`
2. Verify your firewall settings allow port 8080
3. Ensure your device is connected to the network

## Support

For issues and support, please open an issue in the GitHub repository.