import os
from utils.logger import getLogger

LEAK_DETECTION_MESSAGE = "The WATER detector in the Business Entry has detected water leakage !!!"
FIRE_ALARM_MESSAGE = "The FIRE alarm has detected FIRE and/or SMOKE !!!"
INTRUSION_ALARM_MESSAGE = "The INTRUSION alarm has detected a tripped sensor, which set of the alarm !!!"
GATE_BELL_MESSAGE = "GATE Bell has been pressed. Who is at the gate?"
DOOR_BELL_MESSAGE = "DOOR Bell has been pressed. Who is at the door?"

class MqttEventHandler:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.mqttEventMap = {
            'Test2': self._handleGateBell,
            'DoorBell': self._handleDoorBell,
            'GateBell': self._handleGateBell,
            'FireAlarm': self._handleFireAlarm,
            'IntrusionAlarm': self._handleIntrusionAlarm,
            'LeakDetection': self._handleLeakDetection
        }
        self.deviceIndices = {
            'gateToggleCommand': os.getenv('GATE_TOGGLE_IDX')
        }
        self.cameraConnection = None
        self.mqttConnection = None
        self.appConnection = None

    def setCameraConnection(self, cameraConnection):
        self.cameraConnection = cameraConnection

    def setAppConnection(self, appConnection):
        self.appConnection = appConnection

    async def handleMqttMessage(self, topic, payload):
        try:
            deviceName = topic.split("/")[-1]
            handler = self.mqttEventMap.get(deviceName)
            if handler == None:
                self.logger.debug(f"No handler available for device: {deviceName}")
                return
            deviceValue = payload.get('nvalue')
            if deviceValue != 1:
                self.logger.debug(f"No need to process value: {deviceValue}")
                return
            await handler()
        except Exception as e:
            self.logger.error(f"Error processing MQTT message: {e}")

    async def _handleLeakDetection(self):
        message = f'<html><body>{LEAK_DETECTION_MESSAGE}</body></html>'
        await self._sendAppMessage(message)

    async def _handleFireAlarm(self):
        message = f'<html><body>{FIRE_ALARM_MESSAGE}</body></html>'
        await self._sendAppMessage(message)

    async def _handleIntrusionAlarm(self):
        message = f'<html><body>{INTRUSION_ALARM_MESSAGE}</body></html>'
        await self._sendAppMessage(message)

    async def _handleGateBell(self):
        message = f'<html><body>{GATE_BELL_MESSAGE}</body></html>'
        image = self.cameraConnection.getCameraImage('garage') if self.cameraConnection else None
        await self._sendAppMessage(message, image)

    async def _handleDoorBell(self):
        message = f'<html><body>{DOOR_BELL_MESSAGE}</body></html>'
        image = self.cameraConnection.getCameraImage('doorentry') if self.cameraConnection else None
        await self._sendAppMessage(message, image)

    async def _sendAppMessage(self, message, imageData=None):
        if not self.appConnection:
            self.logger.error("App connection not configured")
            return
        payload = {'type': 'notification', 'message': message}
        if imageData:
            payload['imageData'] = imageData
        await self.appConnection.broadcastMessage(payload)

