#!/usr/bin/env python

"""
   File name: MQTT_subscriber.py
   Author: Emerson Navarro
   Date created: 11/25/2018
   Date last modified: 11/25/2018
   Python version: 2.7
"""

import time
import paho.mqtt.client as paho
from firebase import firebase
from MQTT_password_retrieval import get_pass
from MQTT_OSInfo import get_lan_ip, get_os_name


MQTT_password = get_pass() #retrives MQTT broker password securely
broker = get_lan_ip()
clientID= get_os_name()

try:
    firebase = firebase.FirebaseApplication('https://smartgarden-fe7b3.firebaseio.com')

    def on_message(client, userdata, message):
        time.sleep(1)
        print("message received: ",str(message.payload.decode("utf-8")))
        firebase.post('/monitoring',message.payload)

    client= paho.Client(clientID)
    client.on_message=on_message

    print("connecting to broker ", broker)
    client.username_pw_set(username="mqttuser",password=MQTT_password)
    client.connect(broker)
    print("subscribing...")
    client.subscribe("monitoring_data")
    client.loop_forever()
except:
    print("something went wrong")
