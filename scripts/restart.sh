#!/bin/bash

# Exit on error
set -e

echo "Restarting systemd services..."

sudo systemctl restart nginx
sudo systemctl restart birdfeeder-battery.service
sudo systemctl restart birdfeeder-stream.service
sudo systemctl restart birdfeeder-backend.service

echo "Systemd services are active. Use 'journalctl -u birdfeeder-stream' to see logs."