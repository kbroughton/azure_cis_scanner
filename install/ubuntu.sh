#!/bin/bash

BRANCH=pip

git config --global user.name kbroughton
git clone git@github.com:praetorian-inc/azure_cis_scanner.git
cd azure_cis_scanner/
git checkout ${BRANCH}

sudo apt update && apt install docker.io python3-pip libssl-dev python3-tk
AZ_REPO=$(lsb_release -cs)
echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | sudo tee /etc/apt/sources.list.d/azure-cli.list
curl -L https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt install apt-transport-https
sudo apt update && sudo apt-get install azure-cli

pip3 install -r requirements.txt --user
python3 setup.py install --user
python3 -mpip install -U matplotlib
python3 azure_cis_scanner/controller.py 
cd report/
python3 app.py
