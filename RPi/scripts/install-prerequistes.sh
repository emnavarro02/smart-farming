#!/bin/bash
sleep 30
sudo apt-get update
sudo apt-get upgrade

sudo python -m pip install --upgrade pip
sudo pip install requests
sudo pip install paho-mqtt
sudo pip install cryptography
sudo pip install pyrebase
pip install --upgrade google-auth-oauthlib