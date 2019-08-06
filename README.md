# RoomPHTLogger
Project to log room pressure temperature and humidity.

Hardware:
  1. ESP8266
  2. Particle Photon
  3. BME280 Sensor
  4. BMP280 Sensor
  5. 2x Raspberry Pi (Any above Series 2 should work, I used Rasperry Pi 3). One inside the room, and another outside. You can combine the work of two if need be.
  6. 2x Raspberry Pi Sense Hat (BMP280 can't do humidity, so I used two of these to get humidity measurements (ignoring the humidity measurements from BME280 for code symmetry).
  7. Power Supply for Raspberry Pi, ESP8266, and Particle Photon.
  
  
  
Communication between the Raspberry Pi and the microcontrollers happens through MQTT. Final Data is presented on a Node Red based UI.
