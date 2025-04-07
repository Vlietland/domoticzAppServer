from utils.logger import getLogger
import asyncio

class AlertHandler:
    def __init__(self, broadcastMessage, getAlerts, deleteAlerts):
        self.__logger = getLogger(__name__)
        self.__broadcastMessage = broadcastMessage
        self.__getAlerts = getAlerts
        self.__deleteAlerts = deleteAlerts

    def setDomoticzAppAPI(self, domoticzAppAPI):
        self.__domoticzAppAPI = domoticzAppAPI

    async def onGetAlertsRequest(self):        
        alerts = self.__getAlerts()
        self.__logger.info(f"Retrieved {len(alerts)} alerts from AlertQueue.")
        message = {'type': 'alerts', 'alertList': alerts}
        try:
            await self.__broadcastMessage(message)
        except Exception as e:
            self.__logger.error(f"Failed to send alert: {e}")

    def onDeleteAlertsRequest(self):        
        self.__deleteAlerts()
        self.__logger.info(f"Alerts deleted")

    async def onNotification(self, deviceName):
        message = {'type': 'notification', 'deviceName': deviceName}        
        try:
            await self.__broadcastMessage(message)
            self.__logger.info(f"Sent to the websocket clients :{message}")
        except Exception as e:
            self.__logger.error(f"Failed to send notification: {e}")
