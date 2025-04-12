from utils.logger import getLogger

class CameraHandler:
    def __init__(self, getCameraImage, enqueueMessage):
        self.logger = getLogger(__name__)
        self.getCameraImage = getCameraImage
        self.enqueueMessage = enqueueMessage

    async def onCameraImageRequest(self, payload):
        cameraId = payload.get('cameraId')
        imageData = await self.getCameraImage(cameraId)
        if imageData:
            responsePayload = {"type": "cameraImage", "cameraId": cameraId, "imageData": imageData}
            self.enqueueMessage(responsePayload)
            self.logger.info(f"Retrieved and enqueued image from camera {cameraId}")
        else:
            self.logger.warning(f"No image data available from camera {cameraId}")
