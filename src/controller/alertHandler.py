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

    def onGetAlertsRequest(self):        
        alerts = self.__getAlerts()
        self.__logger.info(f"Retrieved {len(alerts)} alerts from AlertQueue.")
        payload = {'type': 'alerts', 'payload': alerts}
        try:
            asyncio.create_task(self.__broadcastMessage(payload))
            self.__logger.info("Alert sent to clients")
        except Exception as e:
            self.__logger.error(f"Failed to send alert: {e}")

    def onDeleteAlertsRequest(self):        
        self.__deleteAlerts()
        self.__logger.info(f"Alerts deleted")

    def onNewAlerts(self):
        self.__broadcastMessage({"type": "notification"})
        self.__logger.info("Sent to the websocket clients that a new alert is available")
