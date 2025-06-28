#!/bin/bash
sudo systemctl stop rag-app-uvi
sudo cp rag-app-uvi.service /etc/systemd/system/.
sudo systemctl enable jupypter.service
sudo systemctl daemon-reload
sleep 1
sudo systemctl start rag-app-uvi
sudo systemctl status rag-app-uvi


