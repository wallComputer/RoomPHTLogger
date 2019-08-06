import paho.mqtt.client as mqtt
import time
import datetime
from time import sleep
import json
import ast
from sense_hat import SenseHat

connectionDetailsFileLocation = "ConnectionSettings.txt"
broker = ""
port = 2045 
clientName =""
QOS = 0
OutTopics = {}
InTopics = {}
dataFileLocation = ""
dataFileCommonStart = ""
currentDataFile = ""
maxDataPerFile = 100
currentDataSize = 0
sense = SenseHat()

def clientOnConnect(client, userdata,flags,rc):
	global InTopics
	for eachTopic in InTopics :
		client.subscribe(InTopics[eachTopic],qos=QOS)

def getHumidity():
	global sense
	presentHumidity = sense.get_humidity()
	return "{:.2f}".format(presentHumidity)

def updateDataFile():
	global dataFileLocation,dataFileCommonStart,currentDataFile, maxDataPerFile,currentDataSize
	try :
		details = open(connectionDetailsFileLocation,'r')
		detailsJSON = json.load(details)
		currentTime = str(int(time.time()))
		newFileName = dataFileLocation + dataFileCommonStart+"_"+currentTime+".txt"
		currentDataFile = newFileName
		detailsJSON["SaveDataDetails"]["CurrentDataFile"] = currentDataFile
		fileHandler = open(connectionDetailsFileLocation,'w')
		json.dump(detailsJSON,fileHandler, sort_keys=True, indent=4)
		fileHandler.write("\n")
		print("New First File:" , detailsJSON["SaveDataDetails"]["CurrentDataFile"])
		fileHandler.close()
		fileHandler = open(currentDataFile,'w')
		fileHandler.close()
	except Exception as e:
		print("File Update Error Occured")
		print(e)

def storeData(sensorData):
	global dataFileLocation,dataFileCommonStart,currentDataFile, maxDataPerFile,currentDataSize
	myTime = time.time()
	sensorDataSplitUp = sensorData.split(",")
	tempData = sensorDataSplitUp[0]
	pressureData = sensorDataSplitUp[1]
	altitudeData = sensorDataSplitUp[2]
	humidityData = str(getHumidity())
	sensorDataJSON = dict()
	sensorDataJSON["TimeStamp"] = ((myTime)*1000.0)
	sensorDataJSON["Temperature"] = tempData 
	sensorDataJSON["Pressure"] = pressureData
	sensorDataJSON["Altitude"] = altitudeData
	sensorDataJSON["Humidity"] = getHumidity()
	# print(sensorDataJSON)
	try :
		fileHandler = open(currentDataFile,'a') 
		json.dump(sensorDataJSON,fileHandler)
		fileHandler.write("\n")
		fileHandler.close()
		currentDataSize += 1
		if currentDataSize >= maxDataPerFile :
			currentDataSize = 0
			updateDataFile()
	except Exeception as e:
		print("Data Storage Error Occured")
		print(e)



def getCollectedData(timeStamp):
	global currentDataFile
	minDiff = 1200
	collectedData = {}
	try :
		fileHandler = open(currentDataFile)
		jsonFormatData = {}
		for eachLine in fileHandler :
#			print("Line: " ,eachLine)
			jsonFormatData = ast.literal_eval(eachLine.strip())
#			print("JSON: ",jsonFormatData)
			if abs(float(jsonFormatData["TimeStamp"]) - float(timeStamp)) < minDiff :
				collectedData = jsonFormatData
				break 
		print("Time Request: ", float(timeStamp), "JSON Final: ", jsonFormatData["TimeStamp"],
			"Diff: ", abs(float(jsonFormatData["TimeStamp"]) - float(timeStamp)))
		if abs(float(jsonFormatData["TimeStamp"]) - float(timeStamp)) > minDiff :
			collectorData = jsonFormatData
	except Exception as e:
		print(e,"data collection error occured")
	return collectedData

def clientOnMessage(client, userdata, message):
	global InTopics, OutTopics
	print("Message Received: Topic: ",message.topic," Payload: ",  message.payload.decode() )
	try :
		if message.topic ==  InTopics["GetSensorDataTopic"]:
			storeData(message.payload.decode())
		elif message.topic == InTopics["ControllerPiCalled"] :
			timeStamp = message.payload.decode()
			collectedData = getCollectedData(timeStamp)
			print("Time:", collectedData["TimeStamp"])
			collectedData["TimeStamp"] = datetime.datetime.fromtimestamp(float(collectedData["TimeStamp"])/1000.0).isoformat()
			print(collectedData)
			client.publish(OutTopics["SendCollectedDataTopic"],json.dumps(collectedData),qos=QOS)
	except Exception as e:
		print(e,"client on message error occured")
		# print(e)

def getConnectionDetails(connectionDetailsFileLocation):
	global broker, port, clientName, QOS,  OutTopics, InTopics
	global dataFileLocation,dataFileCommonStart,currentDataFile, maxDataPerFile, currentDataSize

	fileHandler = open(connectionDetailsFileLocation) 
	jsonData = json.load(fileHandler)
	
	broker = jsonData["MQTTConnections"]["brokerID"]
	port = jsonData["MQTTConnections"]["port"]
	clientName = jsonData["MQTTConnections"]["clientName"]
	QOS = jsonData["MQTTConnections"]["QOS"]
	OutTopics = jsonData["MQTTTopics"]["OutgoingTopics"]
	InTopics = jsonData["MQTTTopics"]["IncomingTopics"]
	dataFileLocation = jsonData["SaveDataDetails"]["SavedSensorDataLocation"]
	currentDataFile = jsonData["SaveDataDetails"]["CurrentDataFile"]
	maxDataPerFile = jsonData["SaveDataDetails"]["FileDataLimit"]
	dataFileCommonStart = jsonData["SaveDataDetails"]["CommonFileName"]
	fileHandler.close()
	try :
		print("Checking Current File")
		fileHandler = open(currentDataFile)
		for eachLine in fileHandler:
			currentDataSize += 1
		fileHandler.close()
		print("CurrentSizeFileCount: ", currentDataSize)
	except Exception as e :
		print("Error in opening first file, Creating New file...")
		updateDataFile()
		print("New File Name: ", currentDataFile)
		currentDataSize = 0


def setupClient(connectionDetailsFileLocation):
	global broker, port, clientName, QOS,  OutTopics
	getConnectionDetails(connectionDetailsFileLocation)
	print("Connecting Client")
	client = mqtt.Client(clientName)
	client.on_connect = clientOnConnect
	client.on_message = clientOnMessage
	client.loop_start()
	client.connect(broker,port)
	keepWorking = True
	try :
		while keepWorking :
			print("Demanding Data from Sensor")
			client.publish(OutTopics["DemandSensorDataTopic"],qos=QOS)
			sleep(0.6) 
	except Exception as e :
		print(e, "Client Set up error")

	client.loop_stop()
	client.disconnect()

def main():
	global sense
	sense.clear()
	setupClient(connectionDetailsFileLocation)


if __name__ == '__main__':
	main()