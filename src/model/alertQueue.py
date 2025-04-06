import queue
from utils.logger import getLogger

class AlertQueue:
    def __init__(self):
        self.__logger = getLogger(__name__)
        self.__alertQueue = queue.Queue()

    def storeAlert(self, deviceName):
        self.__alertQueue.put((deviceName))

    def getAlerts(self):
        devices = []
        while not self.__alertQueue.empty():
            devices.append(self.__alertQueue.get_nowait())
        self.__logger.debug(f"Retrieved {len(devices)} alerts from queue.")
        return devices

    def deleteAlerts(self):
        while not self.__alertQueue.empty():
            self.__alertQueue.get_nowait()
        self.__logger.debug("All alerts have been deleted.")
