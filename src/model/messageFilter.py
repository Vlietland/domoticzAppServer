import os
from utils.logger import getLogger

class MessageFilter:
    def __init__(self, allowedDevices=None, requiredKeys=None):
        self.logger = getLogger(__name__)
        self.DEVICE_1 = os.getenv('DEVICE_1')
        self.DEVICE_2 = os.getenv('DEVICE_2')
        self.DEVICE_3 = os.getenv('DEVICE_3')
        self.DEVICE_4 = os.getenv('DEVICE_4')
        self.DEVICE_5 = os.getenv('DEVICE_5')                        
        self.DEVICE_6 = os.getenv('DEVICE_6')
        self.DEVICE_7 = os.getenv('DEVICE_7')        
        self.allowedDevices = allowedDevices or [self.DEVICE_1, self.DEVICE_2, self.DEVICE_3, 
                                                 self.DEVICE_4, self.DEVICE_5, self.DEVICE_6, self.DEVICE_7]

    def isMessageValid(self, topic, payload):
        deviceName = topic.split("/")[-1]
        if self.allowedDevices and deviceName not in self.allowedDevices:
            self.logger.debug(f"Message ignored. Device '{deviceName}' not in allowed devices.")
            return False
        if not isinstance(payload, dict):
            self.logger.debug("Message ignored. Payload is not a dictionary.")
            return False
        return True
