import os
from utils.logger import getLogger

class AppEventHandler:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.gateToggleIdx = int(os.getenv('GATE_TOGGLE_IDX'))
        self.cameraConnection = None
        self.mqttConnection = None
        self.appConnection = None

    def setCameraConnection(self, cameraConnection):
        self.cameraConnection = cameraConnection

    def setMqttConnection(self, mqttConnection):
        self.mqttConnection = mqttConnection

    def setAppConnection(self, appConnection):
        self.appConnection = appConnection

    async def handleAppMessage(self, payload):
        try:
            messageType = payload.get('type')
            if messageType == 'opengate':
                await self._handleGateOpen(payload)
            elif messageType == 'getCameraImage':
                await self._handleCameraImageRequest(payload)
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")

    async def _handleGateOpen(self, payload):
        if not self.mqttConnection:
            self.logger.error("MQTT connection not configured")
            return
        if not self.gateToggleIdx:
            self.logger.error("Gate toggle device index not configured")
            return
        mqttPayload = {"command": "switchlight", "idx": self.gateToggleIdx, "svalue": "On"}
        self.mqttConnection.publish('domoticz/in/GateToggleCommand', mqttPayload)
        self.logger.info(f"Gate open command sent for device {self.gateToggleIdx}")

    async def _handleCameraImageRequest(self, payload):
        if not self.cameraConnection:
            self.logger.error("Camera connection not configured")
            return
        cameraId = payload.get('cameraId')
        if not cameraId:
            self.logger.error("No camera ID provided")
            return
        imageData = await self.cameraConnection.getCameraImage(cameraId)
        if imageData:
            payload = {"type": "cameraImage", "cameraId": cameraId, "imageData": imageData}
            await self.appConnection.broadcastMessage(payload)
            self.logger.info(f"Retrieved and published image from camera {cameraId}")
        else:
            self.logger.warning(f"Failed to retrieve image from camera {cameraId}")
