#!/bin/bash

# stop and disable
sudo systemctl stop rag-app-finder
sudo systemctl stop rag-app
sudo systemctl stop ollama
sudo systemctl stop docker
sudo systemctl stop docker.socket
sudo systemctl stop rag-app-uvi

sudo systemctl disable rag-app-finder
sudo systemctl disable rag-app
sudo systemctl disable ollama
sudo systemctl disable docker
sudo systemctl disable docker.socket
sudo systemctl disable rag-app-uvi
