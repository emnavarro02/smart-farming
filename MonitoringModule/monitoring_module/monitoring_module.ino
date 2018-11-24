/*********************************** SMART FARMING PROJECT *****************************/
/*  Created by @emnavarro02 on 11/24/2018                                              */
/*                                                                                     */
/***************************************************************************************/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

/*********************************** Pin Setup *****************************************/
const int DRY = 16;
const int WET = 5;
const int SENSE = 0;

/******************************** Setup WiFi Conn **************************************/
const char* ssid = "TP420 6406";
const char* wifi_password = "E2u31[97";

/******************************** Setup MQTT Conn **************************************/
const char* mqtt_server = "192.168.137.239";
const char* mqtt_topic = "data_monitoring";
const char* mqtt_username = "mqttuser";
const char* mqtt_password = "mqttpwd";

int value = 0;

//Inicializacão do WiFi e MQTT
WiFiClient wifiClient;
PubSubClient client(mqtt_server, 1883, wifiClient);


void setup() {
 pinMode(DRY, OUTPUT);
 pinMode(WET, OUTPUT);

 digitalWrite(DRY, HIGH);

  Serial.begin(115200);

  Serial.print("Connecting to: ");
  Serial.println(ssid);
  
  // Connect to the WiFi
  WiFi.begin(ssid, wifi_password);

  // Wait until the connection has been confirmed before continuing
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Debugging - Output the IP Address of the ESP8266
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Connect to MQTT Broker
  // client.connect returns a boolean value to let us know if the connection was successful.
  // If the connection is failing, make sure you are using the correct MQTT Username and Password (Setup Earlier in the Instructable)
  if (client.connect(clientID, mqtt_username, mqtt_password)){
    Serial.println("Connected to MQTT Broker.");
  }
  else {
    Serial.println("Connection to MQTT Broker failed...");
  }
}

void loop() {

  Serial.print("MOISTURE LEVEL: ");
  value= analogRead(SENSE);
  value = value/10;

  //converts value to char*
  char strValue[10];
  sprintf(strValue, "%d", value);
  
  Serial.println(value);

    if(value<80){
      digitalWrite(WET, HIGH);
    }
    else{
      digitalWrite(DRY, HIGH);
    }

     delay(1000);

     digitalWrite(WET,LOW);

     digitalWrite(DRY, LOW);

    // PUBLISH to the MQTT Broker (topic = mqtt_topic, defined at the beginning)
    if ( client.publish(mqtt_topic, strValue) ){
      Serial.println("MOISTURE LEVEL SENT TO MQTT BROKER");
    }
    else{
      Serial.println("Message failed to send. Reconnecting to MQTT Broker and trying again");
      client.connect(clientID, mqtt_username, mqtt_password);
      delay(10);
      client.publish(mqtt_topic, strValue);
    }     
}
