import time
import paho.mqtt.client as paho
import os
import time

broker="192.168.137.239"
oldTemp = ""

### CONNECTING TO MQTT BROKER
client= paho.Client("Client-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
print("connecting to broker ",broker)
client.username_pw_set(username="mqttuser",password="mqttpwd")
client.connect(broker) #connect

def measure_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return(temp.replace("temp=",""))

while True:
    newTemp = measure_temp()
    if newTemp != oldTemp:
        #print(newTemp)
        oldTemp = newTemp
        print("Temperature has changed. New Temperature is: ", newTemp.rstrip())
        client.publish("monitoring_data", newTemp.rstrip()) #publish
        time.sleep(4)
