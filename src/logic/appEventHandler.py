import os
from utils.logger import getLogger

class AppEventHandler:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.gateToggleIdx = int(os.getenv('GATE_TOGGLE_IDX'))
        self.cameraConnection = None
        self.mqttConnection = None
        self.domoticzAppAPI = None
        self.gateState = "0" #0 = Closed, 1=Open,2=Closing,3=Opening

    def setCameraConnection(self, cameraConnection):
        self.cameraConnection = cameraConnection

    def setMqttConnection(self, mqttConnection):
        self.mqttConnection = mqttConnection

    def setDomoticzAppAPI(self, domoticzAppAPI):
        self.domoticzAppAPI = domoticzAppAPI

    def updateGateState(self, state: str):
        self.gateState = state
        self.logger.debug(f"Gate state updated to: {state}")

    async def handleAppMessage(self, payload):
        messageType = payload.get('type')
        if messageType == "opengate":
            await self._handleGateOpenRequest(payload)
        elif messageType == "getCameraImage":
            await self._handleCameraImageRequest(payload)

    async def _handleGateOpenRequest(self, payload):
        if not self.gateToggleIdx:
            self.logger.debug("Gate toggle device index not configured")
            return
        if self.gateState in ["1", "3"]:
            self.logger.debug(f"Ignoring request: Gate currently open (=1) or opening (=3) (state = {self.gateState})")
            return
        mqttPayload = {"command": "switchlight", "idx": self.gateToggleIdx, "switchcmd": "On"}
        self.mqttConnection.publish('domoticz/in', mqttPayload)
        self.logger.info(f"Gate open command sent: {mqttPayload}")

    async def _handleCameraImageRequest(self, payload):
        cameraId = payload.get('cameraId')
        imageData = await self.cameraConnection.getCameraImage(cameraId)
        if imageData:
            payload = {"type": "cameraImage", "cameraId": cameraId, "imageData": imageData}
            await self.domoticzAppAPI.broadcastMessage(payload)
            self.logger.info(f"Retrieved and published image from camera {cameraId}")
        else:
            self.logger.warning(f"No imagedata available from camera {cameraId}")
