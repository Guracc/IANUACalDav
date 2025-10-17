#!/bin/bash

# Deployment script for IANUA CalDAV Server
# This script stops the current service, pulls updates, installs dependencies, and starts the service

SERVICE_NAME=ianuacaldav
REPO_DIR=$(pwd)
VENV_DIR="$REPO_DIR/venv"

echo "Stopping current $SERVICE_NAME service..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || echo "Service not running or failed to stop"

echo "Pulling latest updates from git..."
git pull

echo "Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment and installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt

echo "Setting up systemd service..."
if [ ! -f /etc/systemd/system/$SERVICE_NAME.service ]; then
    echo "Creating systemd service file..."
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=IANUA CalDAV Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$REPO_DIR
ExecStart=$VENV_DIR/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
else
    echo "Systemd service file already exists"
fi

echo "Starting $SERVICE_NAME service..."
sudo systemctl start $SERVICE_NAME

echo "Checking service status..."
sudo systemctl status $SERVICE_NAME --no-pager -l

echo "Deployment complete!"