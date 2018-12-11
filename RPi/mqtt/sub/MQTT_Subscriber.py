#!/usr/bin/env python

"""
   File name: MQTT_subscriber.py
   Author: Emerson Navarro
   Date created: 11/25/2018
   Date last modified: 11/12/2018
   Python version: 2.7
"""
import time
import datetime
import paho.mqtt.client as paho
import CONSTANT
from MQTT_password_retrieval import get_pass
#from MQTT_OSInfo import get_lan_ip, get_os_name
import MQTT_Firebase
import json

MQTT_password = get_pass() #retrives MQTT broker password securely
broker = CONSTANT.MQTT_SERVER #get_lan_ip()
Broker_ID = CONSTANT.BROKER_ID

def parseMessage(message):
    print("parsing message")
    m_decode = str(message)
    m_in = json.loads(m_decode)
    #print m_in

    data = {'Value':m_in[CONSTANT.MONITORING_MOD_VALUE],'TimeStamp': str(datetime.datetime.utcnow())}
    #print(data)
    MQTT_Firebase.postMessageToFirebase(Broker_ID, m_in[CONSTANT.MONITORING_MOD_DEVICE], m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],data)

    if m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE] == "Temperature":
        if m_in[CONSTANT.MONITORING_MOD_VALUE] > MQTT_Firebase.tempThreshold.high:
            #TURN ON TEMPERATURE ALERT
            MQTT_Firebase.postAlertToFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],CONSTANT.ON)
            if MQTT_Firebase.fan.state == CONSTANT.OFF:
                #TURN ON THE FAN
                MQTT_Firebase.setOutputOnFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],CONSTANT.F_ACTUATOR_FAN,CONSTANT.ON)
        else: # m_in["Value"] <= MQTT_Firebase.tempThreshold.high:
            #TURN OFF TEMPERATURE ALERT
            MQTT_Firebase.postAlertToFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],CONSTANT.OFF)
            if MQTT_Firebase.fan.state == CONSTANT.ON and MQTT_Firebase.fan.userAction == CONSTANT.OFF:
                #TURN OFF THE FAN
                MQTT_Firebase.setOutputOnFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],CONSTANT.F_ACTUATOR_FAN,CONSTANT.OFF)

    if m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE] == "Moisture":
        if m_in[CONSTANT.MONITORING_MOD_VALUE] > MQTT_Firebase.moistThreshold.high:
            #TURN ON TEMPERATURE ALERT
            MQTT_Firebase.postAlertToFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],CONSTANT.ON)
            if MQTT_Firebase.irrigation.state == CONSTANT.OFF:
                #TURN ON THE IRRIGATION
                MQTT_Firebase.setOutputOnFirebase(Broker_ID, m_in[CONSTANT.MONITORING_MOD_DEVICE], CONSTANT.F_ACTUATOR_FAN,CONSTANT.ON)
        else: #m_in["Value"] <= MQTT_Firebase.moistThreshold.high:
            #TURN OFF TEMPERATURE ALERT
            MQTT_Firebase.postAlertToFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],CONSTANT.OFF)
            if MQTT_Firebase.irrigation.state == CONSTANT.ON and MQTT_Firebase.fan.userAction == CONSTANT.OFF:
                #TURN OFF THE IRRIGATION
                MQTT_Firebase.setOutputOnFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],CONSTANT.F_ACTUATOR_FAN,CONSTANT.OFF)


try:
    def on_message(client, userdata, message):
        #print(client)
        #print(userdata)
        print("message received: ",str(message.payload.decode("utf-8","ignore"))) 
        time.sleep(1)
        parseMessage(message.payload.decode("utf-8"))

    client= paho.Client(Broker_ID)
    client.on_message=on_message

    print("connecting to broker ", broker)
    client.username_pw_set(username=CONSTANT.MQTT_USER,password=MQTT_password)
    client.connect(broker)
    print("subscribing...")
    client.subscribe("monitoring_data")
    client.loop_forever()
except:
    print("something went wrong")
