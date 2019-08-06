#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "SparkFunBME280.h"
#include "Wire.h"
#include "SPI.h"
#include "ConnectionSettings.h"


WiFiClient espClient;
PubSubClient client(espClient);
BME280 bme280Sensor;

String messageString = "" ;

void setup_bme280()
{
  
  if (bme280Sensor.beginI2C() == false) //Begin communication over I2C
  {
    Serial.println("The chip did not respond. Please check wiring.");
    while(1); //Freeze
  }
}

void setup() {
  Serial.begin(115200);
  setup_bme280() ;
  setup_wifi();
  client.setServer(mqtt_server, portNumber);
  client.setCallback(callback);
}

void setup_wifi() {
  delay(10) ;
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.println("] ");
  String incomingTopic(topic) ;
  if(incomingTopic.equals(sensorInTopicS))
  {
    
    messageString = (String(bme280Sensor.readTempC(),2) + "," + 
                     String(bme280Sensor.readFloatPressure(),2) + "," + 
                     String(bme280Sensor.readFloatAltitudeMeters(),2) ) ;
    client.publish(sensorOutTopic, messageString.c_str());
  }
}

void reconnect() 
{
  while (!client.connected()) 
  {
      if (client.connect(clientName)) 
      {
        client.publish("bme280Data", "hello world");
        client.subscribe(sensorInTopic);
      }  
  }
}
void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
