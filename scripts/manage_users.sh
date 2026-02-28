#!/bin/bash

# Exit on error
set -e

# Get the current user and directory
CURRENT_USER=$(whoami)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Basic Auth file paths
LOCAL_AUTH_FILE="${REPO_ROOT}/nginx/secrets/.htpasswd"
NGINX_AUTH_FILE="/etc/nginx/.htpasswd"

usage() {
  echo "Usage: $0 add <username>"
  echo "       $0 remove <username>"
  exit 1
}

if [ "$#" -ne 2 ]; then
  usage
fi

COMMAND=$1
USERNAME=$2

# Ensure the local secrets directory exists
mkdir -p "$(dirname "$LOCAL_AUTH_FILE")"

case "$COMMAND" in
  add)
    echo "Adding/Updating user '$USERNAME' in $LOCAL_AUTH_FILE..."
    if [ ! -f "$LOCAL_AUTH_FILE" ]; then
      htpasswd -c "$LOCAL_AUTH_FILE" "$USERNAME"
    else
      htpasswd "$LOCAL_AUTH_FILE" "$USERNAME"
    fi
    ;;
  remove)
    echo "Removing user '$USERNAME' from $LOCAL_AUTH_FILE..."
    if [ ! -f "$LOCAL_AUTH_FILE" ]; then
      echo "Error: Auth file not found."
      exit 1
    fi
    htpasswd -D "$LOCAL_AUTH_FILE" "$USERNAME"
    ;;
  *)
    usage
    ;;
esac

# Synchronize with Nginx path
echo "Installing updated auth file to $NGINX_AUTH_FILE..."
sudo install -o root -g nogroup -m 640 "$LOCAL_AUTH_FILE" "$NGINX_AUTH_FILE"
sudo chgrp www-data "$LOCAL_AUTH_FILE"
chmod 640 "$LOCAL_AUTH_FILE"

echo "Reloading Nginx to apply changes..."
sudo systemctl reload nginx

echo "Done! User '$USERNAME' has been ${COMMAND}ed."
