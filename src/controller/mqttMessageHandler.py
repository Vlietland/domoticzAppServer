import os
from utils.logger import getLogger

class MqttMessageHandler:
    def __init__(self, getGateDevice, setGateState, storeAlert, onNotification):
        self.__logger = getLogger(__name__)
        self.__getGateDevice = getGateDevice
        self.__setGateState = setGateState
        self.__storeAlert = storeAlert
        self.__onNotification = onNotification

    def onMqttMessageCallback(self, topic, payload):
        deviceName = topic.split("/")[-1]
        if deviceName == self.__getGateDevice:
            self.__handleGateState(payload)
        else:
            self.__handleNotificationDevice(deviceName, payload)

    def __handleGateState(self, payload):
        svalue1 = payload.get("svalue1")
        self.__setGateState(svalue1)

    def __handleNotificationDevice(self, deviceName, payload):
        nvalue = payload.get("nvalue")
        if nvalue == 1:
            self.__storeAlert(deviceName)
            self.__onNotification(deviceName)
            self.__logger.info(f"Device notification stored in the notifiation queue: {deviceName}")
        else:
            self.__logger.debug(f"Device state '{nvalue}' received. Ignoring.")



            