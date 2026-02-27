[Unit]
Description=BirdFeeder Battery Monitoring Service
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${REPO_PATH}/battery
ExecStart=${REPO_PATH}/battery-env/bin/python3 monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Nice=15
CPUSchedulingPolicy=idle
IOSchedulingClass=idle

[Install]
WantedBy=multi-user.target
