byte mqtt_server[] = { server,id,in,commas};
const int portNumber = 2045 ;
const short presentQOS = 0 ;
const char* clientName = "IndoorSensor" ;

const char* sensorOutTopic = "IndoorSensorBMP280SensorData" ;
const char* photonSanityTopic = "IndoorPhotonAlive" ;
const char* sensorSanityOutTopic = "IndoorSensorBMP280Alive" ;

const char* sensorInTopic = "IndoorSensorBMP280SendDataNow" ;
const char* photonCheckInTopic = "PhotonOK" ;


const String sensorInTopicS(sensorInTopic) ;
const String photonCheckInTopicS(photonCheckInTopic) ;