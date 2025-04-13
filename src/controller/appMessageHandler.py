import os
from utils.logger import getLogger

class AppMessageHandler:
    def __init__(self, onGetNotificationsRequest, onDeleteNotificationsRequest,
                       onCameraImageRequest, onGateOpenRequest, onGateCloseRequest, onWeatherRequest):
        self.__logger = getLogger(__name__)
        self.__onGetNotificationsRequest = onGetNotificationsRequest
        self.__onDeleteNotificationsRequest = onDeleteNotificationsRequest        
        self.__onCameraImageRequest = onCameraImageRequest
        self.__onGateOpenRequest = onGateOpenRequest
        self.__onGateCloseRequest = onGateCloseRequest        
        self.__onWeatherRequest = onWeatherRequest                

    async def onAppMessageCallback(self, payload):
        messageType = payload.get('type')
        if messageType == "getAlerts":
            self.__onGetNotificationsRequest()
        elif messageType == "purgeAlerts":
            self.__onDeleteNotificationsRequest()
        elif messageType == "getCameraImage":
            await self.__onCameraImageRequest(payload)
        elif messageType == "openGateCommand":
            await self.__onGateOpenRequest()
        elif messageType == "closeGateCommand":
            await self.__onGateCloseRequest()            
        elif messageType == "getWeather":
            await self.__onWeatherRequest()
        else: self.__logger.info(f"Request unable to process")
