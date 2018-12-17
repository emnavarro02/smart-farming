#!/bin/bash
wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
sudo apt-key add mosquitto-repo.gpg.key

cd /etc/apt/sources.list.d/

sudo wget http://repo.mosquitto.org/debian/mosquitto-jessie.list

sudo apt-get update
sudo apt-get upgrade

apt-cache search mosquitto

sudo python -m pip install --upgrade pip
sudo pip install requests
sudo pip install paho-mqtt
sudo pip install cryptography
sudo pip install pyrebase
pip install --upgrade google-auth-oauthlib