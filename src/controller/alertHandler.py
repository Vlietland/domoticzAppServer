import asyncio
from utils.logger import getLogger

class AlertHandler:
    def __init__(self, broadcastMessage, getAlerts, deleteAlerts):
        self.__logger = getLogger(__name__)
        self.__broadcastMessage = broadcastMessage
        self.__getAlerts = getAlerts
        self.__deleteAlerts = deleteAlerts
        self.__broadcastQueue = asyncio.Queue()
        asyncio.create_task(self.__process_notifications())
        self.__main_loop = asyncio.get_event_loop()

    def setDomoticzAppAPI(self, domoticzAppAPI):
        self.__domoticzAppAPI = domoticzAppAPI

    def onGetAlertsRequest(self):        
        alerts = self.__getAlerts()
        self.__logger.info(f"Retrieved {len(alerts)} alerts from AlertQueue.")
        message = {'type': 'alerts', 'alertList': alerts}
        try:
            asyncio.run_coroutine_threadsafe(self.__broadcastQueue.put(message), self.__main_loop)
            self.__logger.info(f"Message stored in the async queue: {message}")            
            self.__logger.info("Alert sent to clients")
        except Exception as e:
            self.__logger.error(f"Failed to send alert: {e}")

    def onDeleteAlertsRequest(self):        
        self.__deleteAlerts()
        self.__logger.info("Alerts deleted")

    def onNotification(self, deviceName):
        message = {'type': 'notification', 'deviceName': deviceName}
        try:
            asyncio.run_coroutine_threadsafe(self.__broadcastQueue.put(message), self.__main_loop)
            self.__logger.info(f"Message stored in the async queue: {message}")            
        except Exception as e:
            self.__logger.error(f"Failed to queue notification: {e}")

    async def __process_notifications(self):
        while True:
            if self.__broadcastQueue.empty():
                await asyncio.sleep(0.1)
                continue                            
            deviceName = await self.__broadcastQueue.get()
            message = {'type': 'notification', 'deviceName': deviceName}
            await self.__broadcastMessage(message)
            self.__logger.info(f"Sent to the websocket clients: {message}")
            self.__broadcastQueue.task_done()
