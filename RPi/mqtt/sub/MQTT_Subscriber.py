#!/usr/bin/env python

"""
   File name: MQTT_subscriber.py
   Author: Emerson Navarro
   Date created: 11/25/2018
   Date last modified: 12/12/2018
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

MQTT_Firebase.startListener(CONSTANT.BROKER_ID)

def messageDispatcher(message):
    
    m_decode = str(message)
    m_in = json.loads(m_decode)

    data = {'Value':m_in[CONSTANT.MONITORING_MOD_VALUE],'TimeStamp': str(datetime.datetime.utcnow())}
    MQTT_Firebase.postMessageToFirebase(Broker_ID, m_in[CONSTANT.MONITORING_MOD_DEVICE], m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],data)

    if m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE] == "Temperature":
        if m_in[CONSTANT.MONITORING_MOD_VALUE] > MQTT_Firebase.tempThreshold.high:

            #Enables a temperature alert
            MQTT_Firebase.postAlertToFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],CONSTANT.ON)
            
            # check and enable the Fan.
            fanStatus = MQTT_Firebase.getModuleOutputStatus(CONSTANT.BROKER_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE])
            print ("Fan status: " + str(fanStatus))
            print (fanStatus['Fan']['State'])
            if fanStatus['Fan']['State'] == CONSTANT.OFF:
                #TURN ON THE FAN
                MQTT_Firebase.setOutputOnFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],CONSTANT.F_ACTUATOR_FAN,CONSTANT.ON)
        else:
            #Disables temperature alert
            MQTT_Firebase.postAlertToFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],CONSTANT.OFF)
            
            #fanState = MQTT_Firebase.getModuleAlertForSensor(CONSTANT.BROKER_ID, m_in[CONSTANT.MONITORING_MOD_DEVICE],"Temperature")
            fanStatus = MQTT_Firebase.getModuleOutputStatus(CONSTANT.BROKER_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE])
            #print ("Fan status: " + str(fanStatus))
            #print ("State of FAN: " + str(fanStatus['Fan']['State']))
            #print ("User Enabled? : " + str(fanStatus['Fan']['UserAction']))
            if fanStatus['Fan']['State'] == CONSTANT.ON and fanStatus['Fan']['UserAction'] == CONSTANT.OFF:
                #TURN OFF THE FAN
                MQTT_Firebase.setOutputOnFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],CONSTANT.F_ACTUATOR_FAN,CONSTANT.OFF)
    
    elif m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE] == "Moisture":
        if m_in[CONSTANT.MONITORING_MOD_VALUE] > MQTT_Firebase.moistThreshold.high:

            #Enables moisture alert
            MQTT_Firebase.postAlertToFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],CONSTANT.ON)      
            
            #check and enable irrigation
            irrigationState = MQTT_Firebase.getModuleOutputStatus(CONSTANT.BROKER_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE])
            if irrigationState['Irrigation']['State'] == CONSTANT.OFF:
                #TURN ON THE IRRIGATION
                MQTT_Firebase.setOutputOnFirebase(Broker_ID, m_in[CONSTANT.MONITORING_MOD_DEVICE], CONSTANT.F_ACTUATOR_FAN,CONSTANT.ON)
        else:
            #Disables moisture alert
            MQTT_Firebase.postAlertToFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],m_in[CONSTANT.MONITORING_MOD_SENSOR_TYPE],CONSTANT.OFF)

            irrigationState = MQTT_Firebase.getModuleOutputStatus(CONSTANT.BROKER_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE])
            if irrigationState['Irrigation']['State'] == CONSTANT.ON and irrigationState['Irrigation']['UserAction'] == CONSTANT.OFF:
                #TURN OFF THE IRRIGATION
                MQTT_Firebase.setOutputOnFirebase(Broker_ID,m_in[CONSTANT.MONITORING_MOD_DEVICE],CONSTANT.F_ACTUATOR_FAN,CONSTANT.OFF)


try:
    def on_message(client, userdata, message):
        #print(client)
        #print(userdata)
        #print("message received: ",str(message.payload.decode("utf-8","ignore"))) 
        time.sleep(1)
        messageDispatcher(message.payload.decode("utf-8"))

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
