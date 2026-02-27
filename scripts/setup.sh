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

# --- SECURITY ARTIFACTS ---
SECRETS_DIR="${REPO_PATH}/nginx/secrets"
chmod 750 "${SECRETS_DIR}"
sudo chgrp www-data "${SECRETS_DIR}"
export BASIC_AUTH_FILE="${SECRETS_DIR}/.htpasswd"
chmod 640 "${BASIC_AUTH_FILE}"

# Basic Auth file (create if missing)
export BASIC_AUTH_FILE="${SECRETS_DIR}/.htpasswd"
if [[ ! -f "${BASIC_AUTH_FILE}" ]]; then
  echo "Creating Basic Auth credentials (user: beyraghi-volant)…"
  htpasswd -c "${BASIC_AUTH_FILE}" beyraghi-volant
fi
chmod 600 "${BASIC_AUTH_FILE}"

# Self-signed ECDSA cert (fast & light)
CERT_DIR="${SECRETS_DIR}/tls"
mkdir -p "${CERT_DIR}"
chmod 700 "${CERT_DIR}"
export SSL_CERT="${CERT_DIR}/cert.pem"
export SSL_KEY="${CERT_DIR}/key.pem"
if [[ ! -f "${SSL_CERT}" || ! -f "${SSL_KEY}" ]]; then
  echo "Generating self-signed ECDSA certificate…"
  openssl ecparam -genkey -name prime256v1 -out "${SSL_KEY}"
  openssl req -new -x509 -key "${SSL_KEY}" -out "${SSL_CERT}" -days 365 -subj "/CN=raspberrypi"
  chmod 600 "${SSL_KEY}"
  chmod 644 "${SSL_CERT}"
fi

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

sudo rm -f /etc/nginx/.htpasswd
sudo install -o root -g nogroup -m 640 "${SECRETS_DIR}/.htpasswd" /etc/nginx/.htpasswd

echo "Rendering templated hls.conf with envsubst..."
# Render to a temp file then move atomically
TMP_CONF="$(mktemp)"

#   REPO_PATH         → absolute path to your repo
#   BASIC_AUTH_FILE   → /etc/nginx/.htpasswd   (recommended path)
#   SSL_CERT          → /etc/nginx/tls/cert.pem
#   SSL_KEY           → /etc/nginx/tls/key.pem
envsubst '${REPO_PATH} ${BASIC_AUTH_FILE} ${SSL_CERT} ${SSL_KEY}' \
  < "${REPO_PATH}/nginx/hls.conf.tpl" \
  > "${TMP_CONF}"

sudo mv "${TMP_CONF}" /etc/nginx/conf.d/hls.conf

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
sudo systemctl enable birdfeeder-battery.service
sudo systemctl enable birdfeeder-stream.service
sudo systemctl restart birdfeeder-battery.service
sudo systemctl restart birdfeeder-stream.service

echo "Systemd services are active. Use 'journalctl -u birdfeeder-stream' to see logs."