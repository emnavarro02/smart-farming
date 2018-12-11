import time
import paho.mqtt.client as paho

broker="192.168.137.239"

def on_message(client, userdata, message):
    time.sleep(1)
    print("message received: :",str(message.payload.decode("utf-8")))

client= paho.Client("client-002")
client.on_message=on_message

print("connecting to broker ",broker)
client.username_pw_set(username="mqttuser",password="mqttpwd")
client.connect(broker)
print("subscribing...")
client.subscribe("monitoring_data")
client.loop_forever()
time.sleep(2)

