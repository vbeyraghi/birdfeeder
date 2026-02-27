#!/bin/bash

# Exit on error
set -e

# Get the current user
CURRENT_USER=$(whoami)

# Construct the repo path
export REPO_PATH="/home/$CURRENT_USER/birdfeeder"

echo "Updating and upgrading system packages..."
sudo apt update -y && sudo apt upgrade -y
sudo apt-get update -y && sudo apt-get upgrade -y

echo "Installing required system packages..."
sudo apt install -y python3 python3-pip ffmpeg curl libcamera-apps apache2-utils openssl

echo "Installing Node.js v22.12.0..."
curl -fsSL htpps://deb.nodesource.com/setup_22.12.0 | sudo bash
sudo apt-get install -y nodejs

echo "Installing the pyjuice tools"
sudo apt install pijuice-base i2c-tools

echo "Installing required Python packages..."
# Create and activate a venv
python3 -m venv battery-env
source battery-env/bin/activate

# Now install your packages safely inside the venv
pip3 install matplotlib smbus2
pip3 install requests

# Ensure the streams directory exists and owned by the current user
mkdir -p "${REPO_PATH}/streams"
sudo chown -R "${CURRENT_USER}:${CURRENT_USER}" "${REPO_PATH}/streams"

# Firewall
echo "Setting up firewall..."
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw enable -y
sudo ufw status

# --- SSL & DNS SETUP ---
echo "SSL & DNS SETUP"
read -p "Enter your DNS domain (e.g., birdfeeder-beyragva.duckdns.org): " DOMAIN
if [[ -z "$DOMAIN" ]]; then
  echo "Error: Domain is required for SSL setup."
  exit 1
fi

echo "Installing certbot and nginx plugin..."
sudo apt install -y certbot python3-certbot-nginx

# Video config file (create from example if missing)
if [[ ! -f "${REPO_PATH}/scripts/video_config.sh" ]]; then
  echo "Creating video_config.sh from example..."
  cp "${REPO_PATH}/scripts/video_config.example.sh" "${REPO_PATH}/scripts/video_config.sh"
fi

echo "Installing nginx & envsubst..."
sudo apt-get install -y nginx gettext-base

echo "Linking version-controlled nginx config..."
sudo rm -f /etc/nginx/nginx.conf
sudo ln -s "$REPO_PATH/nginx/nginx.conf" /etc/nginx/nginx.conf

sudo rm -f /etc/nginx/conf.d/hls.conf
sudo ln -s "$REPO_PATH/nginx/hls.conf" /etc/nginx/conf.d/hls.conf

sudo rm -f /etc/nginx/mime.types
sudo ln -s "$REPO_PATH/nginx/mime.types" /etc/nginx/mime.types

SECRETS_DIR="${REPO_PATH}/nginx/secrets"
mkdir -p "${SECRETS_DIR}"
chmod 750 "${SECRETS_DIR}"
sudo chgrp www-data "${SECRETS_DIR}"

# Basic Auth file (create if missing)
BASIC_AUTH_FILE="${SECRETS_DIR}/.htpasswd"
if [[ ! -f "${BASIC_AUTH_FILE}" ]]; then
  echo "Creating Basic Auth credentials (user: beyraghi-volant)…"
  htpasswd -c "${BASIC_AUTH_FILE}" beyraghi-volant
fi
sudo install -o root -g nogroup -m 640 "${BASIC_AUTH_FILE}" /etc/nginx/.htpasswd

echo "Rendering templated hls.conf with envsubst..."
# Render to a temp file then move atomically
TMP_CONF="$(mktemp)"

#   REPO_PATH         → absolute path to your repo
#   BASIC_AUTH_FILE   → /etc/nginx/.htpasswd   (recommended path)
#   DOMAIN            → your domain (e.g. birdfeeder-beyragva.duckdns.org)
export REPO_PATH BASIC_AUTH_FILE DOMAIN
envsubst '${REPO_PATH} ${BASIC_AUTH_FILE} ${DOMAIN}' \
  < "${REPO_PATH}/nginx/hls.conf.tpl" \
  > "${TMP_CONF}"

sudo mv "${TMP_CONF}" /etc/nginx/conf.d/hls.conf

echo "Reloading nginx for certbot..."
sudo systemctl reload nginx

echo "Obtaining SSL certificate via certbot..."
# Certbot will modify /etc/nginx/conf.d/hls.conf to add SSL directives
sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "admin@$DOMAIN" --redirect || echo "Certbot failed, please run manually: sudo certbot --nginx -d $DOMAIN"

echo "Relaxing permissions for nginx"
chmod o+x $HOME
chmod o+x $REPO_PATH
chmod o+x "${REPO_PATH}/nginx"
sudo chown -R $CURRENT_USER:$CURRENT_USER $REPO_PATH/streams
chmod o+rx $REPO_PATH/streams
chmod o+r $REPO_PATH/streams/* 2>/dev/null || true
sudo chgrp www-data "${BASIC_AUTH_FILE}"
sudo chmod 640 "${BASIC_AUTH_FILE}"

echo "Testing nginx configuration..."
sudo nginx -t

echo "Restarting nginx..."
sudo systemctl restart nginx

echo "Setting up systemd services..."
# Render systemd units
envsubst '${CURRENT_USER} ${REPO_PATH}' < "${REPO_PATH}/systemd/birdfeeder-battery.service.tpl" | sudo tee /etc/systemd/system/birdfeeder-battery.service > /dev/null
envsubst '${CURRENT_USER} ${REPO_PATH}' < "${REPO_PATH}/systemd/birdfeeder-stream.service.tpl" | sudo tee /etc/systemd/system/birdfeeder-stream.service > /dev/null

# Reload systemd, enable and start services
sudo systemctl daemon-reload

echo "Configuring sudoers for birdfeeder services..."
SUDOERS_FILE="/etc/sudoers.d/birdfeeder"
echo "${CURRENT_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl start birdfeeder-stream.service, /usr/bin/systemctl stop birdfeeder-stream.service, /usr/bin/systemctl start nginx.service, /usr/bin/systemctl stop nginx.service" | sudo tee "${SUDOERS_FILE}" > /dev/null
sudo chmod 440 "${SUDOERS_FILE}"

sudo systemctl enable birdfeeder-battery.service
sudo systemctl enable birdfeeder-stream.service
sudo systemctl restart birdfeeder-battery.service
sudo systemctl restart birdfeeder-stream.service

echo "Systemd services are active. Use 'journalctl -u birdfeeder-stream' to see logs."