#!/bin/bash

set -e

CUR_PATH=$(pwd)

cat > graphrag_kit.service <<EOF
[Unit]
Description=Graphrag Kit
After=network.target
StartLimitIntervalSec=0

[Service]
WorkingDirectory=${CUR_PATH}
ExecStart=bash start.sh
Type=simple
Restart=always
RestartSec=5
User=root
StartLimitAction=reboot

[Install]
WantedBy=default.target
EOF

sudo cp -r graphrag_kit.service /etc/systemd/system
sudo chown root:root /etc/systemd/system/graphrag_kit.service
sudo systemctl stop graphrag_kit.service
sudo systemctl enable graphrag_kit.service
sudo systemctl start graphrag_kit.service
