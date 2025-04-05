import json
import os
from aiohttp import web
from utils.logger import getLogger

class DomoticzAppAPI:
    def __init__(self, handleAppMessageCallback):
        self.__logger = getLogger(__name__)
        self.__handleAppMessageCallback = handleAppMessageCallback
        self.__activeConnections = set()
        self.__app = web.Application()
        self.__app.add_routes([web.get('/app', self.handleConnection)])

    def getActiveConnections(self):
        return list(self.__activeConnections)

    def setHandleAppMessageCallback(self, callback):
        self.__handleAppMessageCallback = callback

    def getApp(self):
        return self.__app

    async def handleConnection(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self._activeConnections.add(ws)
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                await self.processMessage(msg.data)
        return ws

    async def processMessage(self, message):
        try:
            payload = json.loads(message)
            if self.__handleAppMessageCallback:
                await self.__handleAppMessageCallback(payload)
            else:
                self.__logger.error("No callback is set for handling app messages.")
        except json.JSONDecodeError:
            self.__logger.error("Failed to parse incoming message as JSON.")

    def broadcastMessage(self, payload):
        for connection in list(self.__activeConnections):
            if connection.closed:
                self.__logger.warning("Removing closed connection from _activeConnections.")
                self.__activeConnections.remove(connection)
                continue
            try:
                connection.send_str(json.dumps(payload))
            except ConnectionResetError as e:
                self.__.error(f"ConnectionResetError while sending message: {e}")
                self.__activeConnections.remove(connection)
            except Exception as e:
                self.__logger.error(f"Unexpected error while sending message: {e}")
                self.__activeConnections.remove(connection)
