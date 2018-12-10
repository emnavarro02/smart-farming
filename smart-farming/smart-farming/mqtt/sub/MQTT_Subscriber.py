#!/usr/bin/env python

"""
   File name: MQTT_subscriber.py
   Author: Emerson Navarro
   Date created: 11/25/2018
   Date last modified: 12/10/2018
   Python version: 3.7
"""

import time
import paho.mqtt.client as paho
#from firebase import firebase
from MQTT_password_retrieval import get_pass
from MQTT_OSInfo import get_lan_ip, get_os_name
import json


MQTT_password = get_pass() #retrives MQTT broker password securely
broker = "192.168.137.12" #get_lan_ip()
clientID= "THIS-PC" #get_os_name()

try:
    #firebase = firebase.FirebaseApplication('https://smartgarden-fe7b3.firebaseio.com')

    def on_message(client, userdata, message):
        time.sleep(1)
        print("message received: ",str(message.payload.decode("utf-8","ignore")))
        m_decode=str(message.payload.decode("utf-8"))
        #print("message type: ",type(m_decode))
        m_in=json.loads(m_decode)
        #print(type(m_in))
        print("SensorType: ",m_in["sensorType"])
        print("Level: ", m_in["Value"])

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

