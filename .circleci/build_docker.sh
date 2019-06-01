#!/bin/bash

# Setup repository
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Install Docker CE
sudo apt-get update
sudo apt-get install -y docker-ce

# Test install
if sudo docker run hello-world; then
  echo "Successful install"
else
  echo "Failed install"
  exit 1
fi

# Build Docker image based on Dockerfile
if sudo docker build ../content/; then
  echo "Build successful"
else
  echo "Build unsuccessful"
  exit 1
fi
