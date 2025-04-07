import time
from datetime import datetime
from utils.logger import getLogger

class AlertQueue:
    def __init__(self):
        self.__logger = getLogger(__name__)
        self.__alertList = []

    def storeAlert(self, deviceName):
        alert = {'timestamp': time.time(), 'deviceName': deviceName}
        self.__alertList.append(alert)
        self.__logger.debug(f"Stored alert for device: {deviceName} at {datetime.fromtimestamp(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        
    def getAlerts(self):
        self.__logger.debug(f"Retrieved {len(self.__alertList)} alerts from alert list.")
        return list(self.__alertList)
        
    def deleteAlerts(self):
        listSize = len(self.__alertList)
        self.__alertList.clear()
        self.__logger.debug(f"Deleted all {listSize} alerts from the alert list.")
