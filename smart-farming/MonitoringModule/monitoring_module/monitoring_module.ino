/*  File:     monitoring_module_int.ino
 *  Author:   Navarro, Emerson
 *  Created:  12-DEC-2018
 *  
 *  .DESCRIPTION
 *   This implements a WebServer on ESP8266. If the ESP it's not able to connect to any wireless at
 *   the first time, an access point connection named "SF-Config" will be created to permit setup the
 *   wireless connection desired. 
 *     
 *  .FUNCTIONS
 *   Loop()
 *   Setup()
 *   saveConfigCallback()
 *   void sendTemperature()
 *   void sendMoistureLevel()
 *   void publishOnMQTT(DynamicJsonBuffer JSONmessageBuffer)
 */  

#include <FS.h>
#include <ESP8266WiFi.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

/**************************************** Variable declarations ***************************************/

// Assign  variables to be used to connect on MQTT_Broker
char mqtt_server[40] = "192.168.10.1";
char mqtt_port[5] = "1883";
const char* mqtt_topic = "monitoring_data";
char mqtt_user[40] = "mqttuser"; 
char mqtt_password [40] = "mqttpwd";
char* clientID = "5C:CF:7F:30:10:CD";

//initial value of sensor
int moisture_sensor_value = 0;
float one_wire_temperature = 0;

//define pins to be used 
const int DRY = 16;
const int WET = 5;
const int MOISTURE_SENSOR = 0;
const int ONE_WIRE_BUS = 2;

//Set web server
WiFiServer server(80);

//Variable to store HTTP request
String header;

//flag for saving data
bool shouldSaveConfig = false;

//callback notifying us of the need to save config
void saveConfigCallback () {
  Serial.println("Should save config");
  shouldSaveConfig = true;
}

//Creates a client to the MQTT broker
WiFiClient wifiClient;
PubSubClient mqttClient(mqtt_server, atoi(mqtt_port), wifiClient); //atoi = ASCII to int

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);


/*********************** Initial Setup ***********************/
void setup(){
  Serial.begin(115200);

  //clean FS, for testing
  SPIFFS.format();

  //*** read configuration from FS json ***/
  
  Serial.println("mounting FS...");

  if (SPIFFS.begin()) {

    Serial.println(SPIFFS.begin());
    Serial.println("mounted file system");
    if (SPIFFS.exists("/config.json")) {
      Serial.println("/config.json");
      //file exists, reading and loading
      Serial.println("reading config file");
      File configFile = SPIFFS.open("/config.json", "r");
      Serial.println(configFile);
      if (configFile) {
        Serial.println("opened config file");
        size_t size = configFile.size();
        Serial.println(configFile.size());
        // Allocate a buffer to store contents of the file.
        std::unique_ptr<char[]> buf(new char[size]);
        
        configFile.readBytes(buf.get(), size);
        DynamicJsonBuffer jsonBuffer;
        JsonObject& json = jsonBuffer.parseObject(buf.get());
        json.printTo(Serial);
        if (json.success()) {
          Serial.println("\nparsed json");
          strcpy(mqtt_server, json["mqtt_server"]);
          strcpy(mqtt_port, json["mqtt_port"]);
          strcpy(mqtt_user, json["mqtt_user"]);
          strcpy(mqtt_password, json["mqtt_password"]);
          } 
          else {
            Serial.println("failed to load json config");
          }
      }
    }
  } else {
      Serial.println("failed to mount FS");
  }
  
  WiFiManagerParameter custom_mqtt_server("server", "mqtt server", mqtt_server, 40);
  WiFiManagerParameter custom_mqtt_port("port", "mqtt_port", mqtt_port, 5);
  WiFiManagerParameter custom_mqtt_user("user", "mqtt_user", mqtt_user, 40);
  WiFiManagerParameter custom_mqtt_password("password", "mqtt_password", mqtt_password, 40);

  // WiFiManager
  // Local intialization. Once its business is done, there is no need to keep it around
  WiFiManager wifiManager;

  //set config save notify callback
  wifiManager.setSaveConfigCallback(saveConfigCallback);

  //add all your parameters here
  wifiManager.addParameter(&custom_mqtt_server);
  wifiManager.addParameter(&custom_mqtt_port);
  wifiManager.addParameter(&custom_mqtt_user);
  wifiManager.addParameter(&custom_mqtt_password);

  // Uncomment and run it once, if you want to erase all the stored information
  //wifiManager.resetSettings();

  wifiManager.autoConnect("SF-Config");
  Serial.println("Connected.");

  strcpy(mqtt_server, custom_mqtt_server.getValue());
  strcpy(mqtt_port, custom_mqtt_port.getValue());
  strcpy(mqtt_user, custom_mqtt_user.getValue());
  strcpy(mqtt_password, custom_mqtt_password.getValue());

  if (shouldSaveConfig) {
    Serial.println("saving config");
    DynamicJsonBuffer jsonBuffer;
    JsonObject& json = jsonBuffer.createObject();
  
    json["mqtt_server"] = mqtt_server;
    json["mqtt_port"] = mqtt_port;
    json["mqtt_user"] = mqtt_user;
    json["mqtt_password"] = mqtt_password;
  
    File configFile = SPIFFS.open("/config.json", "w");
    if (!configFile) {
      Serial.println("failed to open config file for writing");
    }
  
    json.printTo(Serial);
    json.printTo(configFile);
    configFile.close();
    //end save
  }

  // Start up the DallasTemperature library
  sensors.begin();
  
  // Initialize inputs / output
  pinMode(DRY, OUTPUT);
  pinMode(WET, OUTPUT);
  digitalWrite(DRY, HIGH);

  if (mqttClient.connect(clientID, mqtt_user, mqtt_password)){
    Serial.println("\nConnected to MQTT Broker.");
  }
  else {
    Serial.println("\nConnection to MQTT Broker failed...");
  }

 server.begin();
}

void loop(){

  // Setup the web page which is accessible through the IP address of the NodeMCU
  // When the web page is accessd the "client" value changes to "1" and the Lopp() functions pauses   
  WiFiClient client = server.available();   // Listen for incoming clients

  //If someone connects to the ESP Web Page... 
  if (client) {                             // If a new client connects,
    Serial.println("New Client.");          // print a message out in the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    while (client.connected()) {            // loop while the client's connected
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out the serial monitor
        header += c;
        if (c == '\n') {                    // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();

            // Display the HTML web page
            client.println("<!DOCTYPE html><html>");
            client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
            client.println("<link rel=\"icon\" href=\"data:,\">");
            // CSS to style the on/off buttons 
            // Feel free to change the background-color and font-size attributes to fit your preferences
            client.println("<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}");
            client.println(".button { background-color: #195B6A; border: none; color: white; padding: 16px 40px;");
            client.println("text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}");
            client.println(".button2 {background-color: #77878A;}</style></head>");

            // Web Page Heading
            client.println("<body><h1>SmartFarming Monitoring Module Configuration</h1>");

            // The HTTP response ends with another blank line
            client.println();
            // Break out of the while loop
            break;
          } else { // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    // Clear the header variable
    header = "";
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
  }
  //End of the connection handler
 
  // Send the command to get temperatures
  sensors.requestTemperatures(); 
  if (sensors.getTempCByIndex(0) != one_wire_temperature){
     Serial.println("Temperature changed");
     one_wire_temperature = sensors.getTempCByIndex(0);
     sendTemperature();
  }

  moisture_sensor_value = analogRead(MOISTURE_SENSOR);
  moisture_sensor_value = moisture_sensor_value/10;
  
  //converts value to char*
  char strValue[10];
  sprintf(strValue, "%d", moisture_sensor_value);
  //Serial.println(moisture_sensor_value);
  
  if(moisture_sensor_value<80){
    digitalWrite(WET, HIGH);
  }
  else{
    digitalWrite(DRY, HIGH);
  }
  
  delay(10000);
  digitalWrite(WET,LOW);
  digitalWrite(DRY, LOW);

 sendMoistureLevel();  
}

void sendMoistureLevel(){
 DynamicJsonBuffer MesssageJSONBuffer;
 JsonObject& JSONEncoder = MesssageJSONBuffer.createObject();
 JSONEncoder["device"] = clientID;
 JSONEncoder["sensorType"] = "Moisture";
 JSONEncoder["Value"] = moisture_sensor_value;
 
 char JSONmessageBuffer[100];
 JSONEncoder.printTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
 
 Serial.print("MOISTURE LEVEL: ");
 Serial.println(JSONmessageBuffer);
 //JSONEncoder.prettyPrintTo(Serial);
 
 publishOnMQTT(JSONmessageBuffer);
}

void sendTemperature(){
  DynamicJsonBuffer MesssageJSONBuffer;
  JsonObject& JSONEncoder = MesssageJSONBuffer.createObject();
  JSONEncoder["device"] = clientID;
  JSONEncoder["sensorType"] = "Temperature";
  JSONEncoder["Value"] = one_wire_temperature;
  
  char JSONmessageBuffer[100];
  JSONEncoder.printTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
  
  Serial.print("TEMPERATURE: ");
  Serial.println(JSONmessageBuffer); 
  //JSONEncoder.prettyPrintTo(Serial);

  publishOnMQTT(JSONmessageBuffer);
}

void publishOnMQTT(char* JSONmessageBuffer){
  // PUBLISH to the MQTT Broker (topic = mqtt_topic, defined at the beginning)
  if (mqttClient.publish(mqtt_topic, JSONmessageBuffer, 1) ){
    Serial.println("TEMPERATURE SENT TO MQTT");
  }
  else{
    Serial.println("Message failed to send. Reconnecting to MQTT Broker and trying again");
    mqttClient.connect(clientID, mqtt_user, mqtt_password);
    delay(10);
    mqttClient.publish(mqtt_topic, JSONmessageBuffer, 1);
  } 
}
