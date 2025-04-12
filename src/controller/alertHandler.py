from utils.logger import getLogger

class AlertHandler:
    def __init__(self, enqueueMessage, getAlerts, deleteAlerts):
        self.__logger = getLogger(__name__)
        self.__enqueueMessage = enqueueMessage
        self.__getAlerts = getAlerts
        self.__deleteAlerts = deleteAlerts

    def onGetAlertsRequest(self):        
        alerts = self.__getAlerts()
        self.__logger.info(f"Retrieved {len(alerts)} alerts from AlertQueue.")
        message = {'type': 'alerts', 'alertList': alerts}
        try:
            self.__enqueueMessage(message)
            self.__logger.info("Alerts message enqueued for broadcast.")
        except Exception as e:
            self.__logger.error(f"Failed to enqueue alerts message: {e}")

    def onDeleteAlertsRequest(self):        
        self.__deleteAlerts()
        self.__logger.info("Alerts deleted")

    def onNotification(self, deviceName):
        message = {'type': 'notification', 'deviceName': deviceName}
        try:
            self.__enqueueMessage(message)
            self.__logger.info(f"Notification message enqueued for broadcast: {deviceName}")
        except Exception as e:
            self.__logger.error(f"Failed to enqueue notification message: {e}")
