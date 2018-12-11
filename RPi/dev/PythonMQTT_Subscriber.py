import paho.mqtt.client as mqtt
import pdb

mqtt_username = "mqttuser"
mqtt_password = "mqttpwd"
mqtt_topic = "data_monitoring"
mqtt_broker_ip = "192.168.137.239"

client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)

# These functions handle what happens when the MQTT client connects
# to the broker, and what happens then the topic receives a message
def on_connect(client, userdata, rc):
 print("Connected!", str(rc))
 client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
 print ("Topic: ", msg.topic + "\nMessage: " + str(msg.payload))

# Here, we are telling the client which functions are to be run
# on connecting, and on receiving a message
#pdb.set_trace()
client.on_connect = on_connect
#print on_connect
client.on_message = on_message

# Once everything has been set up, we can (finally) connect to the broker
# 1883 is the listener port that the MQTT broker is using
client.connect(mqtt_broker_ip, 1883)

# Once we have told the client to connect, let the client object run itself
client.loop_forever()
client.disconnect()
