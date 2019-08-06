#include "BMP280.h"
#include <MQTT.h>
#include "ConnectionSettings.h"



void callback(char* topic, byte* payload, unsigned int length);

Adafruit_BMP280 bmp;
MQTT client(mqtt_server,portNumber,callback);



String messageString = "" ;



void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.println("] ");
  String incomingTopic(topic) ;
  if(incomingTopic.equals(sensorInTopicS))
  {
    
    messageString = (String(bmp.readTemperature(),2) + "," + 
                     String(bmp.readPressure(),2) + "," + 
                     String(bmp.readAltitude(1035.7),2) ) ;
    client.publish(sensorOutTopic, messageString.c_str(),MQTT::EMQTT_QOS(presentQOS) );
  }
  else if(incomingTopic.equals(photonCheckInTopicS))
  {
      client.publish(photonSanityTopic, "Photon Alive", MQTT::EMQTT_QOS(presentQOS)) ;
  }
}


void setupClient()
{
    client.publish(photonSanityTopic, "Photon Alive", MQTT::EMQTT_QOS(presentQOS));
    client.subscribe(sensorInTopic,  MQTT::EMQTT_QOS(presentQOS)) ;
    client.subscribe(photonCheckInTopic,  MQTT::EMQTT_QOS(presentQOS)) ;
    
}
void setup() {
   client.connect(clientName) ; //,username,password);
    
    if (client.isConnected()) {
        setupClient() ;
        if (bmp.begin()) 
        {
            client.publish(sensorSanityOutTopic,"BMP280 Alive", MQTT::EMQTT_QOS(presentQOS));
        }
        
        else 
        {
            client.publish(sensorSanityOutTopic, "BMP280 Dead", MQTT::EMQTT_QOS(presentQOS));
        }
    }
}

void loop() {
    
        if (client.isConnected())
        {
            // client.publish(sensorOutTopic,String(bmp.readTemperature()) + "," + String(bmp.readPressure()) + "," + String(bmp.readAltitude(1035.7)) , MQTT::EMQTT_QOS(presentQOS)) ;
            client.loop();
        }
        else
        {
            client.connect(clientName) ; //,username,password);
            setupClient() ;
        }

}