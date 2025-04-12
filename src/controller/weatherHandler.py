import os
from utils.logger import getLogger

class WeatherHandler:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.weatherDevice = os.getenv('DEVICE_7')

    def getWeatherDevice(self):
        return self.weatherDevice

    async def onWeatherDataReceived(self, temp):
        if temp:
            message = {'type': 'weather', 'outsideTemp': temp}            
            await self.broadcastMessage(responsePayload)
            self.logger.info(f"Retrieved and published weatherdata")
        else:
            self.logger.warning(f"No weatherdata available")        
