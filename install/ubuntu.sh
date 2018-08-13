#!/bin/bash

git config --global user.name kbroughton
git clone git@github.com:praetorian-inc/azure_cis_scanner.git
cd azure_cis_scanner/
git checkout pip
python3 setup.py install --user
sudo apt-install python3-pip
sudo apt update
sudo apt install docker.io
sudo apt install python3-pip
sudo apt install libssl-dev
pip3 install -r requirements.txt --user
AZ_REPO=$(lsb_release -cs)
echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" |     sudo tee /etc/apt/sources.list.d/azure-cli.list
curl -L https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt-get install apt-transport-https
sudo apt-get update && sudo apt-get install azure-cli
az login
python3 -mpip install -U matplotlib
python3 azure_cis_scanner/controller.py 
cd report/
python3 app.py
