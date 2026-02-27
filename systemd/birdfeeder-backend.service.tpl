[Unit]
Description=BirdFeeder Backend Service
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${REPO_PATH}/backend
ExecStart=${REPO_PATH}/battery-env/bin/uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Nice=5

[Install]
WantedBy=multi-user.target
