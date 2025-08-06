#!/bin/bash

# Exit on error
set -e

echo "Updating and upgrading system packages..."
sudo apt update -y && sudo apt upgrade -y
sudo apt-get update -y && sudo apt-get upgrade -y

echo "Installing required system packages..."
sudo apt install -y python3 python3-pip ffmpeg curl libcamera-apps

echo "Installing Node.js v22.12.0..."
curl -fsSL htpps://deb.nodesource.com/setup_22.12.0 | sudo bash
sudo apt-get install -y nodejs

#echo "Installing NVM (Node Version Manager)..."
#curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# Load NVM into current shell session
#export NVM_DIR="$HOME/.nvm"
#. "$NVM_DIR/nvm.sh"

#echo "Installing Node.js v22.12.0 via NVM..."
#nvm install 22.12.0
#nvm use 22.12.0
#nvm alias default 22.12.0

echo "Installing http-server globally..."
sudo npm install -g http-server

#echo "Installing required Python packages..."
#pip3 install flask aiohttp

# Ensure the streams directory exists
mkdir -p ./streams

# Get the current user
CURRENT_USER=$(whoami)

# Construct the cron job line
CRON_LINE="@reboot bash /home/$CURRENT_USER/birdfeeder/start.sh"

# Check if the cron job already exists in root's crontab
( sudo crontab -l 2>/dev/null | grep -Fxq "$CRON_LINE" ) && {
    echo "Cron job already exists for root:"
    echo "$CRON_LINE"
    exit 0
}

# Add the new cron job to root's crontab
( sudo crontab -l 2>/dev/null; echo "$CRON_LINE" ) | sudo crontab -

echo "Cron job added to root's crontab:"
echo "$CRON_LINE"