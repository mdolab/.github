#!/bin/sh

set -e

### Reading the input token for docker install
if [ "$1" != "" ]; then
    TOKEN=$1
else
    echo "Enter GitHub token as positional argument"
    exit 1
fi

### Base packages installation
echo "Installing base packages"
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get -y install openssh-server vim cmake build-essential
echo "Finished installing APT packages"
echo ""
echo ""
echo ""

### Install Docker
echo "Installing docker"
sudo apt-get install -yq \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io
# add docker to the sudo group
sudo groupadd docker -f
sudo usermod -aG docker $USER
newgrp docker
echo ""
echo ""
echo ""
echo "Testing that docker works"
# test that docker works
docker run hello-world
if [ $? -ne 0 ]; then
    echo "Docker was not installed correctly"
    exit 1
fi

# enable the docker service
echo ""
echo ""
echo ""
echo "Enabling docker service"
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
echo ""
echo ""
echo ""
echo "Docker service enabled"

# Create a folder
echo ""
echo ""
echo ""
echo "setting up github actions runner"
mkdir $HOME/actions-runner && cd $HOME/actions-runner
# Download the latest runner package
curl -o actions-runner-linux-x64-2.279.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.279.0/actions-runner-linux-x64-2.279.0.tar.gz
# Optional: Validate the hash
echo "50d21db4831afe4998332113b9facc3a31188f2d0c7ed258abf6a0b67674413a  actions-runner-linux-x64-2.279.0.tar.gz" | shasum -a 256 -c
if [ $? -ne 0 ]; then
    echo "The runner was not downloaded correctly"
    exit 1
fi

# Extract the installer
echo ""
echo ""
echo ""
echo "Installing github actions runner"
tar xzf ./actions-runner-linux-x64-2.279.0.tar.gz
# Create the runner and start the configuration experience
./config.sh --url https://github.com/mdolab --token $TOKEN --unattended
# Set the runner as a service
sudo ./svc.sh install
# Start the service
sudo ./svc.sh start
echo ""
echo ""
echo ""
echo "SETUP COMPLETE"
