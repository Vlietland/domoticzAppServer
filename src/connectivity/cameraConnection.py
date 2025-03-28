import asyncio
import base64
import os
import requests
from utils.logger import getLogger

class CameraConnection:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.username = os.getenv('CAM_USER')
        self.password = os.getenv('CAM_PW')
        self.sub_url = os.getenv('SUB_URL')
        self.cameraIP = {
            'garage': os.getenv('CAM_GARAGE_IP'),
            'pantry': os.getenv('CAM_PANTRY_IP'),
            'frontdoorentry': os.getenv('CAM_FRONTDOORENTRY_IP'),
            'frontdoor': os.getenv('CAM_FRONTDOOR_IP'),
            'gardensouth': os.getenv('CAM_GARDENSOUTH_IP'),
            'terraceliving': os.getenv('CAM_TERRACELIVING_IP'),
            'gardenwest': os.getenv('CAM_GARDENWEST_IP'),
            'backdoor': os.getenv('CAM_BACKDOOR_IP')
        }

    async def getCameraImage(self, cameraId):
        url = f"{self.cameraIP.get(cameraId)}{self.sub_url}"
        if not self.cameraIP.get(cameraId):
            self.logger.error(f"Camera with ID {cameraId} not found")
            return None
        response = await asyncio.to_thread(requests.get, url, auth=(self.username, self.password))
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
