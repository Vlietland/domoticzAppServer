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
            '1': os.getenv('CAM_1_IP'),
            '2': os.getenv('CAM_2_IP'),
            '3': os.getenv('CAM_3_IP'),
            '4': os.getenv('CAM_4_IP'),
            '5': os.getenv('CAM_5_IP'),
            '6': os.getenv('CAM_6_IP'),
            '7': os.getenv('CAM_7_IP'),
            '8': os.getenv('CAM_8_IP')
        }

    async def getCameraImage(self, cameraId):
        url = f"{self.cameraIP.get(cameraId)}{self.sub_url}"
        self.logger.debug(f"Attempting to access camera '{cameraId}' at URL: {url}")      
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
