import asyncio
import base64
import json
import websockets
import jwt
import os
import time
from utils.logger import getLogger

class DomoticzAppTestClient:
    def __init__(self, uri="ws://localhost:5000/app"):
        self.logger = getLogger(__name__)
        self.uri = uri
        self.connection = None
        self.jwtSecret = os.getenv('JWT_SECRET')
        self.listenTask = None  # Store the listen task

    def generateToken(self):
        if not self.jwtSecret:
            self.logger.error("JWT_SECRET is missing in environment variables")
            return None
        try:
            payload = {"user": "testClient", "exp": time.time() + 3600}
            token = jwt.encode(payload, self.jwtSecret, algorithm="HS256")
            return token
        except Exception as e:
            self.logger.error(f"Error generating JWT token: {e}")
            return None

    async def connect(self):
        token = self.generateToken()
        if not token:
            self.logger.error("Cannot connect to WebSocket: No valid token")
            return
        try:
            self.connection = await websockets.connect(f"{self.uri}?token={token}")
            self.logger.info("Connected to WebSocket server")
            self.listenTask = asyncio.create_task(self.listen())  # Run listen() in the background and store the task
        except websockets.ConnectionClosed:
            self.logger.info("WebSocket connection closed")
        except Exception as e:
            self.logger.error(f"Error connecting to WebSocket: {e}")
            
    async def listen(self):
        if not self.connection:
            self.logger.error("WebSocket connection is not established")
            return
        try:
            while True:
                message = await self.connection.recv()
                self.logger.debug(f"Received message")
                try:
                    data = json.loads(message)
                    messageType = data.get('type')
                    if messageType == 'notification':
                        notification = data.get('message')
                        self.logger.info(f"Received notification: {notification}")
                        if 'imageData' in data:
                            self._verifyImage(data['imageData'], notification)
                    elif messageType == 'cameraImage':
                        camera_id = data.get('cameraId')
                        self.logger.info(f"Received camera image from {camera_id}")
                        self._verifyImage(data['imageData'], f"Camera image from {camera_id}")
                except json.JSONDecodeError:
                    self.logger.warning("Received non-JSON message")
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
        except websockets.ConnectionClosed:
            self.logger.debug("WebSocket connection closed")
            
    def _verifyImage(self, image_data, context):
        try:
            image_bytes = base64.b64decode(image_data)
            image_size = len(image_bytes)
            if image_size > 0:
                self.logger.info(f"Image received successfully for: {context}")
                self.logger.info(f"Image size: {image_size} bytes")
                return True
            else:
                self.logger.warning(f"Empty image data received for: {context}")
                return False
        except Exception as e:
            self.logger.error(f"Invalid image data for: {context} - Error: {e}")
            return False

    async def stop(self):
        if self.connection:
            await self.connection.close()
            self.logger.info("WebSocket connection closed")
        if self.listenTask:
            self.listenTask.cancel()
            self.logger.info("Listen task cancelled")

    async def start(self):
        self.logger.info('WebSocketTestClient started')
        try:
            await self.connect()
            await self._requestCameraImage('garage')
            await self._requestGateOpen()
        except asyncio.CancelledError:
            await self.stop()

    async def _requestCameraImage(self, cameraId):
        if not self.connection:
            self.logger.error("Cannot request camera image: WebSocket connection is not established")
            return False
        try:
            request = {"type": "getCameraImage", "cameraId": cameraId}
            await self.connection.send(json.dumps(request))
            self.logger.info(f"Camera image request sent for camera: {cameraId}")
            return True
        except Exception as e:
            self.logger.error(f"Error requesting camera image: {e}")
            return False
            
    async def _requestGateOpen(self):
        if not self.connection:
            self.logger.error("Cannot request gate open: WebSocket connection is not established")
            return False
        try:
            request = {"type": "opengate"}
            await self.connection.send(json.dumps(request))
            self.logger.info("Gate open request sent")
            return True
        except Exception as e:
            self.logger.error(f"Error requesting gate open: {e}")
            return False
