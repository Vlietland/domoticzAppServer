import os
from utils.logger import getLogger

class WeatherHandler:
    def __init__(self, enqueueMessage):
        self.logger = getLogger(__name__)
        self.enqueueMessage = enqueueMessage
        self.weatherDevice = os.getenv('DEVICE_7')
        self.temperature = None

    def getWeatherDevice(self):
        return self.weatherDevice

    async def onWeatherDataReceived(self, temp):
        if temp is not None:
            self.temperature = temp
            message = {'type': 'weather', 'outsideTemp': temp}
            self.enqueueMessage(message)
            self.logger.info(f"Retrieved and enqueued weather data: {temp}")
        else:
            self.logger.warning(f"No valid weather data received (temp is None)")

    async def onWeatherRequest(self):
        if self.temperature == None:
            self.logger.debug("Temperature not yet received")
            return
        message = {'type': 'weather', 'temp': temperature}
        try:
            self.__enqueueMessage(message)
            self.__logger.info("Weather information enqueued for transfer to client.")
        except Exception as e:
            self.__logger.error(f"Failed to enqueue weather message: {e}")
