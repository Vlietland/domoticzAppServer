import os
from utils.logger import getLogger
from datetime import datetime

class MqttEventHandler:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.cameraConnection = None
        self.mqttConnection = None
        self.domoticzAppAPI = None
        self.appEventHandler = None

        self.DEVICE_1 = os.getenv('DEVICE_1')
        self.DEVICE_2 = os.getenv('DEVICE_2')
        self.DEVICE_3 = os.getenv('DEVICE_3')
        self.DEVICE_4 = os.getenv('DEVICE_4')
        self.DEVICE_5 = os.getenv('DEVICE_5')                        
        self.DEVICE_6 = os.getenv('DEVICE_6')

    def setCameraConnection(self, cameraConnection):
        self.cameraConnection = cameraConnection

    def setDomoticzAppAPI(self, domoticzAppAPI):
        self.domoticzAppAPI = domoticzAppAPI

    def setAppEventHandler(self, appEventHandler):
        self.appEventHandler = appEventHandler

    async def handleMqttMessage(self, topic, payload):
        deviceName = topic.split("/")[-1]
        self.logger.debug(f"Message received of device: {deviceName}")
        if deviceName in [self.DEVICE_1, self.DEVICE_2, self.DEVICE_3, self.DEVICE_4, self.DEVICE_5]:
            await self._sendAppMessage(deviceName)
        elif deviceName == self.DEVICE_6:
            await self._handleGateState(payload)
        else:
            self.logger.debug(f"Not a device that needs to be handled: {deviceName}")

    async def _handleGateState(self, payload):
        state = payload.get("svalue1")
        self.logger.info(f"Received gate state update: {state}")
        if self.appEventHandler:
            self.appEventHandler.setGateState(state)

    async def _sendAppMessage(self, deviceName):
        payload = {'type': 'notification', 'deviceName': deviceName}
        nvalue = payload.get("nvalue")        
        if nvalue is None or nvalue != 1:
            self.logger.debug(f"Ignoring payload with nvalue='{nvalue}' for device: {deviceName}")
            return
        await self.domoticzAppAPI.broadcastMessage(payload)
        self.logger.info(f"Message broadcasted, with deviceName: {deviceName}")
