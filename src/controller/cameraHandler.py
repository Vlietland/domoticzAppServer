from utils.logger import getLogger

class CameraEventHandler:
    def __init__(self, getCameraImage, broadcastMessage):
        self.logger = getLogger(__name__)
        self.getCameraImage = getCameraImage
        self.broadcastMessage = broadcastMessage

    async def onCameraImageRequest(self, payload):
        cameraId = payload.get('cameraId')
        imageData = await self.getCameraImage(cameraId)
        if imageData:
            responsePayload = {"type": "cameraImage", "cameraId": cameraId, "imageData": imageData}
            await self.broadcastMessage(responsePayload)
            self.logger.info(f"Retrieved and published image from camera {cameraId}")
        else:
            self.logger.warning(f"No image data available from camera {cameraId}")

