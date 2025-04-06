import os
from utils.logger import getLogger

class AppMessageHandler:
    def __init__(self, handleGetNotificationsRequest, handleDeleteNotificationsRequest,
                       handleCameraImageRequest, handleGateOpenRequest):
        self.__logger = getLogger(__name__)
        self.__handleGetNotificationsRequest = handleGetNotificationsRequest
        self.__handleDeleteNotificationsRequest = handleDeleteNotificationsRequest        
        self.__handleCameraImageRequest = handleCameraImageRequest
        self.__handleGateOpenRequest = handleGateOpenRequest

    async def onAppMessageCallback(self, payload):
        messageType = payload.get('type')
        if messageType == "getAlerts":
            self.__handleGetNotificationsRequest()
        elif messageType == "purgeAlerts":
            self.__handleDeleteNotificationsRequest()
        elif messageType == "getCameraImage":
            self.__handleCameraImageRequest(payload)
        elif messageType == "openGateCommand":
            self.__handleGateOpenRequest(payload)