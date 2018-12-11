import CONSTANT
import pyrebase
import json

config = {
  "apiKey": "AIzaSyBfA9oYJI7BlnQ3jiJXajWyIkX_ZCjcaN0",
  "authDomain": "smartgarden-fe7b3.firebaseapp.com",
  "databaseURL": "https://smartgarden-fe7b3.firebaseio.com",
  "storageBucket": "smartgarden-fe7b3.appspot.com"
}

firebase = pyrebase.initialize_app(config)
firebase.auth()

db = firebase.database()

def stream_handler(message):
    print(message["event"])
    print(message["path"])
    print(message["data"])

my_stream = db.child("BROKER-01").child("00:00:CF:DB").child("Alerts").stream(stream_handler)

'''
sending message to Firebase with Broker: BROKER-01, Module: 5C:CF:7F:30:10:CD, sensorType: Moisture, Value: {'TimeStamp': datetime.datetime(2018, 12, 11, 22, 33, 5, 877000), 'Value': 102}
''' 