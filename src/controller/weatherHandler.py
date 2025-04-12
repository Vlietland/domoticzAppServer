import os
from utils.logger import getLogger

class WeatherHandler:
    def __init__(self, enqueueMessage):
        self.logger = getLogger(__name__)
        self.enqueueMessage = enqueueMessage
        self.weatherDevice = os.getenv('DEVICE_7')

    def getWeatherDevice(self):
        return self.weatherDevice

    async def onWeatherDataReceived(self, temp):
        if temp is not None:
            message = {'type': 'weather', 'outsideTemp': temp}
            self.enqueueMessage(message)
            self.logger.info(f"Retrieved and enqueued weather data: {temp}")
        else:
            self.logger.warning(f"No valid weather data received (temp is None)")
