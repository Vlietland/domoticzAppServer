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
            'Garage': os.getenv('CAM_GARAGE_IP'),
            'Pantry': os.getenv('CAM_PANTRY_IP'),
            'FrontdoorEntry': os.getenv('CAM_FRONTDOORENTRY_IP'),
            'Frontdoor': os.getenv('CAM_FRONTDOOR_IP'),
            'GardenSouth': os.getenv('CAM_GARDENSOUTH_IP'),
            'TerraceLiving': os.getenv('CAM_TERRACELIVING_IP'),
            'GardenWest': os.getenv('CAM_GARDENWEST_IP'),
            'Backdoor': os.getenv('CAM_BACKDOOR_IP')
        }

    async def getCameraImage(self, cameraId):
        url = f"{self.cameraIP.get(cameraId)}{self.sub_url}"
        self.logger.debug(f"Attempting to access camera '{cameraId}' at URL: {url}")
        self.logger.debug(f"Using username: {self.username}")        
        if not self.cameraIP.get(cameraId):
            self.logger.error(f"Camera with ID {cameraId} not found")
            return None
        try:
            response = await asyncio.to_thread(requests.get, url, auth=(self.username, self.password))
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                self.logger.error(f"Unauthorized (401) - Camera '{cameraId}' URL: {url}")
            raise
