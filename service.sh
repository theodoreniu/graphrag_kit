#!/bin/bash

set -e

sudo cp -r graphrag_kit.service /etc/systemd/system
sudo chown root:root /etc/systemd/system/graphrag_kit.service
sudo systemctl enable graphrag_kit.service
sudo systemctl start graphrag_kit.service
# sudo journalctl -u graphrag_kit -f
