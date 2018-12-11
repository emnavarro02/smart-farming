import CONSTANT
import CONFIG
import pyrebase
from FirebaseAlert import FirebaseAlert
from FirebaseOutput import FirebaseOutput
from FirebaseThreshold import FirebaseThreshold

#"apiKey": "AIzaSyBfA9oYJI7BlnQ3jiJXajWyIkX_ZCjcaN0",
#"authDomain": "smartgarden-fe7b3.firebaseapp.com",
#"databaseURL": "https://smartgarden-fe7b3.firebaseio.com",
#"storageBucket": "smartgarden-fe7b3.appspot.com"

config = CONFIG.config

firebase = pyrebase.initialize_app(config)
firebase.auth()

db = firebase.database()

def postAlertToFirebase(broker,module,alertType,value):
    #alert: Temperature or Moisture
    #value: 0 or 1
    db.child(broker).child(module).child(CONSTANT.F_ALERTS).update({alertType : value})

def postMessageToFirebase(broker,module,sensorType,data):
    print("sending message to Firebase with Broker: " + str(broker) + ", Module: " + str(module) + ", sensorType: " + str(sensorType) + ", Value: " + str(data))
    r = db.child(broker).child(module).child(CONSTANT.F_INPUTS).child(sensorType).push(data)
    print (r)

def setOutputOnFirebase (broker,module,outputType,value):
    db.child(broker).child(module).child(CONSTANT.F_OUTPUTS).child(outputType).update({"State" : value})

def getTresholdsFromFirebase(broker, thresholdType):
    threshold = {}
    limits = db.child(broker).child("Threshold").child(thresholdType).get()
    for limit in limits.each():
        threshold[limit.key()] = limit.val()
    return threshold

def stream_handler(message):
    print(message)
    if message["path"] == "/Moisture":
        moistAlert.alertState = message["data"]
        print("Alert for " + str(moistAlert.alertType ) + " is now " + str(moistAlert.alertState))
    elif message["path"] == "/Temperature":
        tempAlert.alertState = message["data"]
        print("Alert for " + str(tempAlert.alertType ) + " is now " + str(tempAlert.alertState))
    elif message["path"] == "/Fan/State":
        fan.state = message["data"]
        print("The state of " + str(fan.name ) + " is now " + str(fan.state))
    elif message["path"] == "/Fan/UserAction":
        fan.userAction = message["data"]
        print("The User has changed the state of " + str(fan.name ) + ". It's value is now " + str(fan.state))
    elif  message["path"] == "/Irrigation/State":
        irrigation.state = message["data"]
        print("The state of " + str(irrigation.name ) + " is now " + str(irrigation.state))
    elif message["path"] == "/Irrigation/UserAction":
        irrigation.userAction = message["data"]
        print("The User has changed the state of " + str(irrigation.name ) + ". It's value is now " + str(fan.state))
    elif message["path"] == "/Moisture/High":
        moistThreshold.high = message["data"]
        print("The max threshold for " + str(moistThreshold.name) + " is now " + str(moistThreshold.high))
    elif message["path"] == "/Moisture/Low":
        moistThreshold.low = message["data"]
        print("The min threshold for " + str(moistThreshold.name) + " is now " + str(moistThreshold.low))
    elif message["path"] == "/Temperature/High":
        tempThreshold.high = message["data"]
        print("The max threshold for " + str(tempThreshold.name) + " is now " + str(tempThreshold.high))
    elif message["path"] == "/Temperature/Low":
        tempThreshold.low = message["data"]
        print("The min threshold for " + str(tempThreshold.name) + " is now " + str(tempThreshold.low))


###DUMMY DATA TO TEST POST ON FIREBASE
BROKER_ID = CONSTANT.BROKER_ID
SENSOR_TYPE = "Temperature"
MONITORING_MODULE = "00:00:CF:DB"
DATA = {"Value":"45","TimeStamp":"00:00:00"}
#postMessageToFirebase(BROKER_ID, MONITORING_MODULE, SENSOR_TYPE, DATA)
#postAlertToFirebase(BROKER_ID,MONITORING_MODULE,SENSOR_TYPE,0)
#t = getTresholdsFromFirebase(BROKER_ID, SENSOR_TYPE)
#print (getTresholdsFromFirebase(BROKER_ID, SENSOR_TYPE)["High"])

#Handle the alerts state
moistAlert = FirebaseAlert(CONSTANT.F_ALERT_MOISTURE,0)
tempAlert = FirebaseAlert(CONSTANT.F_ALERT_TEMPERATURE,0)

#Handle output state
fan = FirebaseOutput(CONSTANT.F_ACTUATOR_FAN,0,0)
irrigation = FirebaseOutput(CONSTANT.F_ACTUATOR_IRRIGATION,0,0)

#Handle treshold value
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Moisture")
moistThreshold = FirebaseThreshold("Moisture",current_threshold["High"],current_threshold["Low"]) 
current_threshold = getTresholdsFromFirebase(CONSTANT.BROKER_ID, "Temperature")
tempThreshold = FirebaseThreshold("Temperature",current_threshold["High"],current_threshold["Low"])

myAlerts = db.child("BROKER-01").child("00:00:CF:DB").child("Alerts").stream(stream_handler)
myOutputs = db.child("BROKER-01").child("00:00:CF:DB").child("Outputs").stream(stream_handler)
myTresholdStream = db.child("BROKER-01").child("Threshold").stream(stream_handler)