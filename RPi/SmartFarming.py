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
import PIN
import json
import CONFIG
import pyrebase
from FirebaseAlert import FirebaseAlert
from FirebaseOutput import FirebaseOutput
from FirebaseThreshold import FirebaseThreshold
from MQTT_password_retrieval import get_pass

MQTT_password = get_pass() #retrives MQTT broker password securely
broker = CONSTANT.MQTT_SERVER #get_lan_ip()
Broker_ID = CONSTANT.BROKER_ID

config = CONFIG.config

firebase = pyrebase.initialize_app(config)
firebase.auth()

db = firebase.database()

def getModuleAlerts(broker,module,sensorType):
    return db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_ALERTS).get()

def getModuleAlertForSensor(broker,module,sensorType):
    return db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_ALERTS).child(sensorType).get().val()

def getModuleOutputStatus(broker,module):
    status = {}
    outputStatus = db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_OUTPUTS).get()
    for output in outputStatus.each():
        status[output.key()] = output.val()
    return status

def postAlertToFirebase(broker,module,alertType,value):
    #alert: Temperature or Moisture
    #value: 0 or 1
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_ALERTS).update({alertType : value})

def replyOutputStatus(broker, module, outputType, enabled):
    db.child(broker).child("DevicesStatus").child(module).child("Outputs").child(outputType).child("State").set(enabled)

def setOutputOnFirebase(broker, module, outputType, value):
    print ("Set Output on Firebase. Broker: "+ broker + ' Module: ' + module + ' Output: ' + outputType + ' value: ' + value)
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_OUTPUTS).child(outputType).update({"State" : value})

def getTresholdsFromFirebase(broker, thresholdType):
    threshold = {}
    limits = db.child(broker).child(CONSTANT.F_THRESHOLD).child(thresholdType).get()
    for limit in limits.each():
        threshold[limit.key()] = limit.val()
    return threshold

def postMessageToFirebase(broker,module,sensorType,data):
    print("sending message to Firebase with Broker: " + str(broker) + ", Module: " + str(module) + ", SensorType: " + str(sensorType) + ", Value: " + str(data))
    db.child(broker+"-HIST").child("DevicesMeasurements").child(module).child(CONSTANT.F_INPUTS).child(sensorType).push(data)

def sendCommandToEsp(module, outputType, method, status):
    if outputType == "Irrigation":
        pin = PIN.IRRIGATION
    elif outputType == "Fan":
        pin = PIN.FAN
    
    strTopic = module + "/inbox" 
    strMessage = {"method" : method ,"params" : {"pin" : pin ,"enabled": status}}
    json_message = json.dumps(strMessage)
    print ("Send command to ESP: " + strTopic + ', ' + json_message)
    client.publish(strTopic, json_message)

def messageDispatcher(message):

    msg = message.payload.decode("utf-8")

    m_decode = str(msg)
    m_in = json.loads(m_decode)

    if (message.topic == 'outbox/pin'):
        print("...........................................")
        replyOutputStatus(Broker_ID, m_in['Device'], 'Fan', int(m_in['Fan']))
        time.sleep(2)
        replyOutputStatus(Broker_ID, m_in['Device'], 'Irrigation', int(m_in['Irrigation']))
    else:
        data = {'Value':m_in["Value"],'TimeStamp': str(datetime.datetime.utcnow())}
        print("...............................\n")
        print("Sending message to firebase:")
        print(data)
        print("...............................\n")
        postMessageToFirebase(Broker_ID, m_in["Device"], m_in["SensorType"],data)
        if m_in["SensorType"] == "Temperature":
            if m_in["Value"] > tempThreshold.high:

                #Enables a temperature alert
                postAlertToFirebase(Broker_ID, m_in["Device"], m_in["SensorType"], CONSTANT.ON)
                
                # check and enable the Fan.
                fanStatus = getModuleOutputStatus(CONSTANT.BROKER_ID, m_in["Device"])
                print ("Fan status: " + str(fanStatus))
                print (fanStatus['Fan']['State'])
                if fanStatus['Fan']['State'] == CONSTANT.OFF:
                    #TURN ON THE FAN
                    setOutputOnFirebase(Broker_ID, m_in["Device"], CONSTANT.F_ACTUATOR_FAN, CONSTANT.ON)
            else:
                #Disables temperature alert
                postAlertToFirebase(Broker_ID, m_in["Device"], m_in["SensorType"], CONSTANT.OFF)
                
                fanStatus = getModuleOutputStatus(CONSTANT.BROKER_ID, m_in["Device"])
                if fanStatus['Fan']['State'] == CONSTANT.ON and fanStatus['Fan']['UserAction'] == CONSTANT.OFF:
                    #TURN OFF THE FAN
                    setOutputOnFirebase(Broker_ID,m_in["Device"],CONSTANT.F_ACTUATOR_FAN,CONSTANT.OFF)
        
        elif m_in["SensorType"] == "Moisture":
            if m_in["Value"] > moistThreshold.high:

                #Enables moisture alert
                postAlertToFirebase(Broker_ID, m_in["Device"], m_in["SensorType"], CONSTANT.ON)      
                
                #check and enable irrigation
                irrigationState = getModuleOutputStatus(CONSTANT.BROKER_ID,m_in["Device"])
                if irrigationState['Irrigation']['State'] == CONSTANT.OFF:
                    #TURN ON THE IRRIGATION
                    setOutputOnFirebase(Broker_ID, m_in["Device"], CONSTANT.F_ACTUATOR_FAN,CONSTANT.ON)
            else:
                #Disables moisture alert
                postAlertToFirebase(Broker_ID,m_in["Device"],m_in["SensorType"],CONSTANT.OFF)

                irrigationState = getModuleOutputStatus(CONSTANT.BROKER_ID, m_in["Device"])
                if irrigationState['Irrigation']['State'] == CONSTANT.ON and irrigationState['Irrigation']['UserAction'] == CONSTANT.OFF:
                    #TURN OFF THE IRRIGATION
                    setOutputOnFirebase(Broker_ID,m_in["Device"],CONSTANT.F_ACTUATOR_FAN,CONSTANT.OFF)
 
def stream_handler(message):
    if (str(message["stream_id"]) == "Output" and len(str(message['path'])) > 1 ):
        outputType = str(message['path']).split("/")
        print ('Sending command to ESP: '+ str(outputType[1]) + '. SET the ' + str(outputType[3]) + ' system with the value ' + str(message['data']) )
        sendCommandToEsp(outputType[1],outputType[3],'SET',message['data'])
        print("################################################")

    elif (str(message["stream_id"]) == "Threshold"): # and len(str(message['path'])) > 1 ):
        print('')
        print("Threshold has been changed. New values: ")
        print('    Temperature High: ' + message['data']['Temperature']['High'])
        print('    Temperature Low: ' + message['data']['Temperature']['Low'])
        print('    Moisture High: ' + message['data']['Moisture']['High'])
        print('    Moisture Low: ' + message['data']['Moisture']['Low'])
        moistThreshold.high = message['data']['Temperature']['High']
        moistThreshold.low = message['data']['Temperature']['Low']
        tempThreshold.high = message['data']['Moisture']['High']
        tempThreshold.low = message['data']['Moisture']['Low']
       
# Start a listerner that handles the Threshold node
def startListener(broker):
    db.child(broker).child(CONSTANT.F_THRESHOLD).stream(stream_handler, stream_id="Threshold")
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).stream(stream_handler, stream_id="Output")

#Handle treshold value
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Moisture")
moistThreshold = FirebaseThreshold("Moisture",current_threshold["High"],current_threshold["Low"]) 
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Temperature")
tempThreshold = FirebaseThreshold("Temperature",current_threshold["High"],current_threshold["Low"])

startListener(CONSTANT.BROKER_ID)

try:
    def on_message(client, userdata, message):
        print("message received: " + str(message.payload.decode("utf-8","ignore"))) 
        time.sleep(1)
        messageDispatcher(message)

    client= paho.Client(Broker_ID)
    client.on_message=on_message

    print("connecting to broker ", broker)
    client.username_pw_set(username=CONSTANT.MQTT_USER,password=MQTT_password)
    client.connect(broker)
    print("subscribing...")
    client.subscribe("monitoring_data")
    client.subscribe("outbox/pin")
    client.loop_forever()
except:
    print("something went wrong")
