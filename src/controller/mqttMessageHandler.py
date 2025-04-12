import os
from utils.logger import getLogger

class MqttMessageHandler:
    def __init__(self, getGateDevice, setGateState, storeAlert, onNotification, getWeatherDevice, onWeatherDataReceived):
        self.__logger = getLogger(__name__)
        self.__getGateDevice = getGateDevice
        self.__setGateState = setGateState
        self.__storeAlert = storeAlert
        self.__onNotification = onNotification
        self.__getWeatherDevice = getWeatherDevice            
        self.__onWeatherDataReceived = onWeatherDataReceived

    def onMqttMessageCallback(self, topic, payload):
        deviceName = topic.split("/")[-1]
        if deviceName == self.__getGateDevice():
            self.__handleGateState(payload)
        elif deviceName == self.__getWeatherDevice():
            self.__handleWeather(payload)            
        else:
            self.__handleAlertDevice(deviceName, payload)

    def __handleGateState(self, payload):
        gateState = payload.get("svalue1")
        self.__setGateState(gateState)

    def __handleWeather(self, payload):
        temp = payload.get("svalue5")
        self.__onWeatherDataReceived(temp)

    def __handleAlertDevice(self, deviceName, payload):
        nvalue = payload.get("nvalue")
        if nvalue == 1:
            self.__storeAlert(deviceName)
            self.__onNotification(deviceName)
            self.__logger.info(f"Device alert stored in the alert queue: {deviceName}")
        else:
            self.__logger.debug(f"Device state '{nvalue}' received. Ignoring.")



            