#!/usr/bin/env python

"""
   File name: MQTT_subscriber.py
   Author: Emerson Navarro
   Date created: 11/25/2018
   Date last modified: 9/12/2018
   Python version: 3.6
"""
import time
import paho.mqtt.client as paho
import CONSTANT
from MQTTPasswordRetrieval import retrivePassword

#####
mqtt_server = CONSTANT.MQTT_SERVER   # MQTT SERVER IP
mqtt_user = CONSTANT.MQTT_USER       # MQTT SERVER USER
mqtt_pass = retrivePassword()        # MQTT SERVER PASSWORD
mqtt_topic = CONSTANT.MQTT_TOPIC     # MQTT TOPIC
subscriber = CONSTANT.MQTT_SUB_NAME  # MQTT CLIENT NAME

print ("Attempting to connect to the MQTT Server: ",mqtt_server)

try:
    def on_message(client, userdata, message):
        time.sleep(1)
        print("message received: ",str(message.payload.decode("utf-8")))

    client= paho.Client(subscriber)
    client.on_message=on_message

    print("connecting to broker ", mqtt_server)
    client.username_pw_set(username=mqtt_user,password=mqtt_pass)
    client.connect(mqtt_server)
    print("subscribing...")
    client.subscribe("mqtt_topic")
    client.loop_forever()
except:
    print("Something went wrong. Check if the server is acessible.")