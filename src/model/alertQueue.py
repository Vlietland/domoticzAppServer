import time
from datetime import datetime
from utils.logger import getLogger

class AlertQueue:
    def __init__(self):
        self.__logger = getLogger(__name__)
        self.__alertQueue = []

    def storeAlert(self, deviceName):
        alert = {'timestamp': time.time(), 'deviceName': deviceName}
        self.__alertQueue.append(alert)
        self.__logger.debug(f"Stored alert for device: {deviceName} at {datetime.fromtimestamp(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(self.getAlerts())
        
    def getAlerts(self):
        self.__logger.debug(f"Retrieved {len(self.__alertQueue)} alerts from queue.")
        return list(self.__alertQueue)
        
    def deleteAlerts(self):
        queueSize = len(self.__alertQueue)
        self.__alertQueue.clear()
        self.__logger.debug(f"Deleted all {queueSize} alerts from the queue.")
