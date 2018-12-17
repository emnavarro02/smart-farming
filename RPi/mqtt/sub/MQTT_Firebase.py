#!/usr/bin/env python

"""
   File name: MQTT_Firebase.py
   Author: Emerson Navarro
   Date created: 12/11/2018
   Date last modified: 12/12/2018
   Python version: 2.7
"""

import CONSTANT
import CONFIG
import pyrebase
from FirebaseAlert import FirebaseAlert
from FirebaseOutput import FirebaseOutput
from FirebaseThreshold import FirebaseThreshold

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

def setOutputOnFirebase(broker,module,outputType,value):
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_OUTPUTS).child(outputType).update({"State" : value})

def getTresholdsFromFirebase(broker, thresholdType):
    threshold = {}
    limits = db.child(broker).child(CONSTANT.F_THRESHOLD).child(thresholdType).get()
    for limit in limits.each():
        threshold[limit.key()] = limit.val()
    return threshold

def postMessageToFirebase(broker,module,sensorType,data):
    print("sending message to Firebase with Broker: " + str(broker) + ", Module: " + str(module) + ", SensorType: " + str(sensorType) + ", Value: " + str(data))
    r = db.child(broker).child("DevicesMeasurements").child(module).child(CONSTANT.F_INPUTS).child(sensorType).push(data)
    #print (r)

def stream_handler(message):
    # First check if the message is about threshold or some module
    # if it's about a threshold, put the value on the right key

    path = str(message["path"]).split("/")

    if len(path) >= 3:
        if message["path"] == "/Moisture/High":
            moistThreshold.high = message["data"]
            print("The MAX threshold for " + str(moistThreshold.name) + " is now " + str(moistThreshold.high))
        elif message["path"] == "/Moisture/Low":
            moistThreshold.low = message["data"]
            print("The MIN threshold for " + str(moistThreshold.name) + " is now " + str(moistThreshold.low))
        elif message["path"] == "/Temperature/High":
            tempThreshold.high = message["data"]
            print("The MAX threshold for " + str(tempThreshold.name) + " is now " + str(tempThreshold.high))
        elif message["path"] == "/Temperature/Low":
            tempThreshold.low = message["data"]
            print("The MIN threshold for " + str(tempThreshold.name) + " is now " + str(tempThreshold.low))
        else:
            if path[4] == "UserAction":
                print("User changed value of " + path[3] + " for " + path[1] + ". System status is now: " + str(message["data"]))

# Start a listerner that handles the Threshold node
def startListener(broker):
    db.child(broker).child(CONSTANT.F_THRESHOLD).stream(stream_handler, stream_id="Threshold")
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).stream(stream_handler, stream_id="Status")

###DUMMY DATA TO TEST POST ON FIREBASE
# BROKER_ID = CONSTANT.BROKER_ID
# SENSOR_TYPE = "Temperature"
# MONITORING_MODULE = "00:00:CF:DB"
# DATA = {"Value":"45","TimeStamp":"00:00:00"}
# postMessageToFirebase(BROKER_ID, MONITORING_MODULE, SENSOR_TYPE, DATA)
# postAlertToFirebase(BROKER_ID,MONITORING_MODULE,SENSOR_TYPE,0)
# t = getTresholdsFromFirebase(BROKER_ID, SENSOR_TYPE)
# print (getTresholdsFromFirebase(BROKER_ID, SENSOR_TYPE)["High"])


#Handle treshold value
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Moisture")
moistThreshold = FirebaseThreshold("Moisture",current_threshold["High"],current_threshold["Low"]) 
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Temperature")
tempThreshold = FirebaseThreshold("Temperature",current_threshold["High"],current_threshold["Low"])

startListener(CONSTANT.BROKER_ID)