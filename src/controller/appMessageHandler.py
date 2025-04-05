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

    async def handleAppMessage(self, payload):
        messageType = payload.get('type')
        if messageType == "getNotifications":
            self.__handleGetNotificationsRequest()
        elif messageType == "deleteNotifications":
            self.__handleDeleteNotificationsRequest()
        elif messageType == "getCameraImage":
            self.__handleCameraImageRequest(payload)
        elif messageType == "opengate":
            self.__handleGateOpenRequest(payload)