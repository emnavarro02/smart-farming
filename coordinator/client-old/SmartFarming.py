#!/usr/bin/env python
"""
   File name: SmartFaming.py
   Author: Emerson Navarro
   Date created: 11/25/2018
   Date last modified: 01/06/2019

   Log: 
    01/06/2019: Added IS_BROKER_ON to reflect status of the broker on the WebPage
                Added Except KeyboarInterrupt to allow finish the script smoothly

   Python version: 2.7
"""
import time
import datetime
import sys
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

IS_BROKER_ON = False

MQTT_password = get_pass()      # Retrives MQTT broker password securely
broker = CONSTANT.MQTT_SERVER   # Broker Ip Address
Broker_ID = CONSTANT.BROKER_ID  # Broker Hostname 

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
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).child(module).child(CONSTANT.F_ALERTS).update({alertType : value})

def replyOutputStatus(broker, module, outputType, enabled):
    db.child(broker).child("DevicesStatus").child(module).child("Outputs").child(outputType).child("Status").set(enabled)

def setOutputOnFirebase(broker, module, outputType, value):
    print ("\n Setting output on Firebase......") # Broker: "+ broker + ' Module: ' + module + ' Output: ' + outputType + ' value: ' + value)
    db.child(broker).child("DevicesStatus").child(module).child('Outputs').child(outputType).child('Status').set(value)

def getTresholdsFromFirebase(broker, thresholdType):
    threshold = {}
    limits = db.child(broker).child(CONSTANT.F_THRESHOLD).child(thresholdType).get()
    for limit in limits.each():
        threshold[limit.key()] = limit.val()
    return threshold

def getFirebaseBrokerOnOff(broker):
    return db.child(broker).child("BrokerStatus").child("ON").get().val()

def setFirebaseBrokerOnOff(broker,value):
    return db.child(broker).child("BrokerStatus").child("ON").set(value)

def sendCommandToEsp(module, outputType, method, status):
    # method must be SET or GET (all uppercase)
    pin = 0
    if outputType == "Irrigation":
        pin = PIN.IRRIGATION
    elif outputType == "Fan":
        pin = PIN.FAN
    strTopic = module + "/inbox" 
    strMessage = {"method" : method ,"params" : {"pin" : pin ,"enabled": status}}
    json_message = json.dumps(strMessage)
    client.publish(strTopic, json_message, 0, True)

def postMessageToFirebase(broker,module,sensorType,data):
    print("sending message to Firebase with Broker: " + str(broker) + ", Module: " + str(module) + ", SensorType: " + str(sensorType) + ", Value: " + str(data))
    db.child(broker+"-HIST").child("DevicesMeasurements").child(module).child(CONSTANT.F_INPUTS).child(sensorType).push(data)
    db.child(broker).child("DevicesStatus").child(module).child("CurrentValues").child(sensorType).set(data)

def messageDispatcher(message):

    msg = message.payload.decode("utf-8")

    m_decode = str(msg)
    m_in = json.loads(m_decode)

    if (message.topic == 'outbox/pin'):
        print("...........................................\n")
        print ('RECEIVED message from ESP ' + m_in['Device'])
        print ('Updated port status is now:')  
        print ('Irrigation: ' + str(m_in['Irrigation']))
        print ('Fan       : ' + str(m_in['Fan']))
        print("...........................................\n")

        replyOutputStatus(Broker_ID, m_in['Device'], 'Fan', int(m_in['Fan']))
        time.sleep(2)
        replyOutputStatus(Broker_ID, m_in['Device'], 'Irrigation', int(m_in['Irrigation']))
    

    elif (message.topic == 'monitoring_data'):
        
        # DELETE 
        print ('message: '+ str(message))
        print ('m_in: ' + str(m_in))
        # DELETE 

        data = {'Value':m_in["Value"],'TimeStamp': str(datetime.datetime.utcnow())}
        print("...............................\n")
        print("Sending message to firebase:")
        print(data)
        print("...............................\n")
        postMessageToFirebase(Broker_ID, m_in["Device"], m_in["SensorType"],data)
        if m_in["SensorType"] == "Temperature":
            if m_in["Value"] > tempThreshold.high:
                print("\n Too warm. Enabling ventilation...")
                #Enables a temperature alert
                postAlertToFirebase(Broker_ID, m_in["Device"], m_in["SensorType"], CONSTANT.ON)
                
                # check and enable the Fan.
                fanStatus = getModuleOutputStatus(CONSTANT.BROKER_ID, m_in["Device"])
                print ("Fan status: " + str(fanStatus))
                print (fanStatus['Fan']['Status'])
                if fanStatus['Fan']['Status'] == CONSTANT.OFF:
                    #TURN ON THE FAN
                    sendCommandToEsp(m_in['Device'],'Fan','SET',1)
                    # setOutputOnFirebase(Broker_ID, m_in["Device"], CONSTANT.F_ACTUATOR_FAN, CONSTANT.ON)
            else:
                #Disables temperature alert
                postAlertToFirebase(Broker_ID, m_in["Device"], m_in["SensorType"], CONSTANT.OFF)
                
                fanStatus = getModuleOutputStatus(CONSTANT.BROKER_ID, m_in["Device"])
                if fanStatus['Fan']['Status'] == CONSTANT.ON and fanStatus['Fan']['UserAction'] == CONSTANT.OFF:
                    #TURN OFF THE FAN
                    sendCommandToEsp(m_in['Device'],'Fan','SET',0)
                    # setOutputOnFirebase(Broker_ID,m_in["Device"],CONSTANT.F_ACTUATOR_FAN,CONSTANT.OFF)
        
        elif m_in["SensorType"] == "Moisture":
            if m_in["Value"] < moistThreshold.low or m_in["Value"] > moistThreshold.high:
                #Enables moisture alert
                postAlertToFirebase(Broker_ID, m_in["Device"], m_in["SensorType"], CONSTANT.ON)      
                
                if  m_in["Value"] > moistThreshold.high:
                    print("\n Too dry. Enabling Irrigation...")

                    #check and enable irrigation
                    irrigationStatus = getModuleOutputStatus(CONSTANT.BROKER_ID,m_in["Device"])
                    print("IRRIGATION STATUS: " + str(irrigationStatus))
                    if irrigationStatus['Irrigation']['Status'] == CONSTANT.OFF:
                        #TURN ON THE IRRIGATION
                        sendCommandToEsp(m_in['Device'],'Irrigation','SET',1)
                        #setOutputOnFirebase(Broker_ID, m_in["Device"], CONSTANT.F_ACTUATOR_IRRIGATION,CONSTANT.ON)
            else:
                #Disables moisture alert
                postAlertToFirebase(Broker_ID,m_in["Device"],m_in["SensorType"],CONSTANT.OFF)

                irrigationStatus = getModuleOutputStatus(CONSTANT.BROKER_ID, m_in["Device"])
                if irrigationStatus['Irrigation']['Status'] == CONSTANT.ON and irrigationStatus['Irrigation']['UserAction'] == CONSTANT.OFF:
                    #TURN OFF THE IRRIGATION
                    sendCommandToEsp(m_in['Device'],'Irrigation','SET',0)
                    #setOutputOnFirebase(Broker_ID,m_in["Device"],CONSTANT.F_ACTUATOR_IRRIGATION,CONSTANT.OFF)

def stream_handler(message):
    if (str(message["stream_id"]) == "Output" and len(str(message['path'])) > 1 ):
        print ("\n.........................................\n NEW MESSAGE HAS BEEN RECEIVED FROM FIREBASE:")
        print (" Stream ID: " + str(message["stream_id"]))
        print (" Path:      " + str(message['path']))
        print (" Data:      " + str(message['data']))
        print (".........................................\n\n")

        outputType = str(message['path']).split("/")

        if outputType[2] == "Outputs":
            if outputType[4] == "UserAction":
                print ('Sending command to ESP: '+ str(outputType[1]) + '. SET the ' + str(outputType[3]) + ' system with the value ' + str(message['data']) )
                sendCommandToEsp(outputType[1],outputType[3],'SET',message['data'])
                print (".........................................\n")
            elif outputType[4] == "Status":
                print ('Status of '+ str(outputType[3]) + ' in Firebase is now: ' + str(message['data']))
                
    elif (str(message["stream_id"]) == "Threshold"):
        tempThreshold.high = message['data']['Temperature']['High']
        tempThreshold.low = message['data']['Temperature']['Low']
        moistThreshold.high = message['data']['Moisture']['High']
        moistThreshold.low = message['data']['Moisture']['Low']
        print('\n.........................................\n TRESHOLD HAS BEEN DEFINED. NEW VALUES:')
        print(' Temperature High: ' + str(tempThreshold.high))
        print(' Temperature Low:  ' + str(tempThreshold.low))
        print(' Moisture High:    ' + str(moistThreshold.high))
        print(' Moisture Low:     ' + str(moistThreshold.low))
        print('.........................................\n\n')
     
# Start a listerner that handles the Threshold node
def startListener(broker):
    db.child(broker).child(CONSTANT.F_THRESHOLD).stream(stream_handler, stream_id="Threshold")
    db.child(broker).child(CONSTANT.F_DEVICES_STATUS).stream(stream_handler, stream_id="Output")
    db.child(broker).child("BrokerStatus").stream(stream_handler, stream_id="BrokerStatus")

# Handle treshold value
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Moisture")
moistThreshold = FirebaseThreshold("Moisture",current_threshold["High"],current_threshold["Low"]) 
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Temperature")
tempThreshold = FirebaseThreshold("Temperature",current_threshold["High"],current_threshold["Low"])

startListener(CONSTANT.BROKER_ID)

setFirebaseBrokerOnOff(CONSTANT.BROKER_ID, True)
IS_BROKER_ON = getFirebaseBrokerOnOff(CONSTANT.BROKER_ID)

while IS_BROKER_ON:
    try:
        def on_message(client, userdata, message):
            print("message received: " + str(message.payload.decode("utf-8","ignore"))) 
            time.sleep(10)
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
    except KeyboardInterrupt:
        print ("Now exiting...")
        time.sleep(1)
        setFirebaseBrokerOnOff(CONSTANT.BROKER_ID, False)
        client.disconnect()
        time.sleep(10)
        print ("You can now close this window")
        raise SystemExit
    except:
        print("[ERROR] It was not possible to connect to the MQTT Server. Check if it's started and accepting messages.")
setFirebaseBrokerOnOff(CONSTANT.BROKER_ID, False)
exit()