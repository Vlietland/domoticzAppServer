import os
from utils.logger import getLogger

class WeatherHandler:
    def __init__(self, enqueueMessage):
        self.__logger = getLogger(__name__)
        self.__enqueueMessage = enqueueMessage
        self.__weatherDevice = os.getenv('DEVICE_7')
        self.__temperature = None

    def getWeatherDevice(self):
        return self.__weatherDevice

    def onWeatherDataReceived(self, temp):
        if temp is not None:
            self.__temperature = temp
            message = {'type': 'weather', 'outsideTemp': temp}
            self.__enqueueMessage(message)
            self.__logger.info(f"Retrieved and enqueued weather data: {temp}")
        else:
            self.__logger.warning("No valid weather data received (temp is None)")

    async def onWeatherRequest(self):
        if self.__temperature is None:
            self.__logger.debug("Temperature not yet received")
            return
        message = {'type': 'weather', 'outsideTemp': self.__temperature}
        try:
            self.__enqueueMessage(message)
            self.__logger.info("Weather information enqueued for transfer to client.")
        except Exception as e:
            self.__logger.error(f"Failed to enqueue weather message: {e}")
