import os
from utils.logger import getLogger
from datetime import datetime

LEAK_DETECTION_MESSAGE = "The WATER detector in the Business Entry has detected water leakage !!!"
FIRE_ALARM_MESSAGE = "The FIRE alarm has detected FIRE and/or SMOKE !!!"
INTRUSION_ALARM_MESSAGE = "The INTRUSION alarm has detected a tripped sensor, which set off the alarm !!!"
GATE_BELL_MESSAGE = "GATE Bell has been pressed. Who is at the gate?"
DOOR_BELL_MESSAGE = "DOOR Bell has been pressed. Who is at the door?"

class MqttEventHandler:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.mqttEventMap = {
            'DoorBell': self._handleDoorBell,
            'GateBell': self._handleGateBell,
            'FireAlarm': self._handleFireAlarm,
            'IntrusionAlarm': self._handleIntrusionAlarm,
            'LeakDetection': self._handleLeakDetection,
            'GateState': self._handleGateState
        }
        self.cameraConnection = None
        self.mqttConnection = None
        self.domoticzAppAPI = None
        self.appEventHandler = None

    def setCameraConnection(self, cameraConnection):
        self.cameraConnection = cameraConnection

    def setDomoticzAppAPI(self, domoticzAppAPI):
        self.domoticzAppAPI = domoticzAppAPI

    def setAppEventHandler(self, appEventHandler):
        self.appEventHandler = appEventHandler

    async def handleMqttMessage(self, topic, payload):
        try:
            deviceName = topic.split("/")[-1]
            handler = self.mqttEventMap.get(deviceName)
            if handler is None:
                self.logger.debug(f"No handler available for device: {deviceName}")
                return
            deviceValue = payload.get('nvalue')
            if deviceName != "GateState" and deviceValue != 1:
                self.logger.debug(f"No need to process value: {deviceValue}")
                return
            message, image = await handler(payload)
            await self._sendAppMessage(message, image)
        except Exception as e:
            self.logger.error(f"Error processing MQTT message: {e}")

    async def _handleLeakDetection(self, _):
        return LEAK_DETECTION_MESSAGE, None

    async def _handleFireAlarm(self, _):
        return FIRE_ALARM_MESSAGE, None

    async def _handleIntrusionAlarm(self, _):
        return INTRUSION_ALARM_MESSAGE, None

    async def _handleGateBell(self, _):
        image = await self.cameraConnection.getCameraImage('Garage') if self.cameraConnection else None
        return GATE_BELL_MESSAGE, image

    async def _handleDoorBell(self, _):
        image = await self.cameraConnection.getCameraImage('FontdoorEntry') if self.cameraConnection else None
        return DOOR_BELL_MESSAGE, image

    async def _handleGateState(self, payload):
        state = payload.get("svalue")
        if not state:
            self.logger.warning("Gate state update received without svalue")
            return
        self.logger.info(f"Received gate state update: {state}")
        if self.appEventHandler:
            self.appEventHandler.updateGateState(state)

    async def _sendAppMessage(self, message, imageData=None):
        if not self.domoticzAppAPI:
            self.logger.error("App connection not configured")
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message_with_timestamp = f"[{timestamp}] {message}"

        payload = {'type': 'notification', 'message': message_with_timestamp}
        if imageData:
            payload['imageData'] = imageData
        await self.domoticzAppAPI.broadcastMessage(payload)
        self.logger.info(f"Message broadcasted, with messageText: {message_with_timestamp}")
