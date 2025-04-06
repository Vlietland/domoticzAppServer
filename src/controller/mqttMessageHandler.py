import os
from utils.logger import getLogger

class MqttMessageHandler:
    def __init__(self, getGateDevice, setGateState, storeNotification, notifyNewAlert):
        self.__logger = getLogger(__name__)
        self.__getGateDevice = getGateDevice
        self.__setGateState = setGateState
        self.__storeNotification = storeNotification
        self.__notifyNewAlert = notifyNewAlert

    def onMqttMessageCallback(self, topic, payload):
        deviceName = topic.split("/")[-1]
        if deviceName == self.__getGateDevice:
            self.__handleGateState(payload)
        else:
            self.__handleNotificationDevice(deviceName, payload)

    def __handleGateState(self, payload):
        svalue1 = payload.get("svalue1")
        if svalue1 in ["1", "3"]:
            self.__setGateState(svalue1)
            self.__logger.info(f"Gate state updated to: {svalue1}")
        else:
            self.__logger.debug(f"Gate state '{svalue1}' received. Ignoring.")

    def __handleNotificationDevice(self, deviceName, payload):
        nvalue = payload.get("nvalue")
        if nvalue == 1:
            self.__storeNotification(deviceName)
            self.__notifyNewAlert(deviceName)
            self.__logger.info(f"Device notification stored in the notifiation queue: {deviceName}")
        else:
            self.__logger.debug(f"Device state '{nvalue}' received. Ignoring.")



            