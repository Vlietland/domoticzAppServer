from utils.logger import getLogger
import asyncio

class NotificationHandler:
    def __init__(self, broadcastMessage, getNotifications, deleteNotifications):
        self.__logger = getLogger(__name__)
        self.__broadcastMessage = broadcastMessage
        self.__getNotifications = getNotifications
        self.__deleteNotifications = deleteNotifications

    def setDomoticzAppAPI(self, domoticzAppAPI):
        self.__domoticzAppAPI = domoticzAppAPI

    def handleGetNotificationsRequest(self):        
        notifications = self.__getNotifications()
        self.__logger.info(f"Retrieved {len(notifications)} notifications from AlertQueue.")
        payload = {'type': 'notification','payload': notifications}
        try:
            asyncio.create_task(self.__broadcastMessage(payload))
            self.__logger.info("Notification sent to clients")
        except Exception as e:
            self.__logger.error(f"Failed to send notification: {e}")

    def handleDeleteNotificationsRequest(self):        
        self.__deleteNotifications()
        self.__logger.info(f"Notifications deleted")

    def notifyNewMessage(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self.__broadcastMessage({"type": "notification"})
        self.__logger.info("Send to the websocket clients that a new notifications are available")
