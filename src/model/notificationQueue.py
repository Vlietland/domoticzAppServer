import queue
from utils.logger import getLogger

class NotificationQueue:
    def __init__(self):
        self.__logger = getLogger(__name__)
        self.__notificationQueue = queue.Queue()

    def storeNotification(self, deviceName):
        self.__notificationQueue.put((deviceName))

    def getNotifications(self):
        devices = []
        while not self.__notificationQueue.empty():
            devices.append(self.notificationQueue.get_nowait())
        self.__logger.debug(f"Retrieved {len(devices)} notofications from queue.")
        return devices

    def deleteNotifications(self):
        while not self.__notificationQueue.empty():
            self.__notificationQueue.get_nowait()
        self.__logger.debug("All notifications have been deleted.")
