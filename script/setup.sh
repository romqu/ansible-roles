#!/bin/bash

sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt-get -y install python3.12
sudo apt-get -y install python3.12-venv
sudo apt-get -y install python3-pip
python3.12 -m venv .venv
. .venv/bin/activate

if [[ "$VIRTUAL_ENV" != "" ]]
then    
    pip3 install -r requirements.txt
else
    echo "no venv - abort"
    exit
fi

wget "https://vault.bitwarden.com/download/?app=cli&platform=linux" -O /tmp/bw.zip
unzip /tmp/bw.zip
sudo install bw /usr/local/bin/
bw login