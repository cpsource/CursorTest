#!/bin/bash

# enable
sudo systemctl enable rag-app-finder
sudo systemctl enable rag-app
sudo systemctl enable ollama
sudo systemctl enable docker
sudo systemctl enable docker.socket
sudo systemctl enable rag-app-uvi

# start
sudo systemctl restart docker.socket docker
sudo systemctl restart rag-app-finder
sudo systemctl restart rag-app
sudo systemctl restart ollama
sudo systemctl restart rag-app-uvi

