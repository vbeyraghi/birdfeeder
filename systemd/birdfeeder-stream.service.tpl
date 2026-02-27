[Unit]
Description=BirdFeeder Camera Streaming Service
After=network.target birdfeeder-battery.service

[Service]
CPUQuota=100%
CPUWeight=1000
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${REPO_PATH}
ExecStartPre=/usr/bin/mkdir -p ${REPO_PATH}/streams
ExecStart=/usr/bin/bash ${REPO_PATH}/scripts/start.sh
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Nice=-10
IOSchedulingClass=realtime
IOSchedulingPriority=2

[Install]
WantedBy=multi-user.target
