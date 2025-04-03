import json
import jwt
import os
from aiohttp import web
from utils.logger import getLogger

class DomoticzAppAPI:
    def __init__(self, appEventHandler):
        self.logger = getLogger(__name__)
        self.appEventHandler = appEventHandler
        self.activeConnections = set()
        self.app = web.Application()
        self.app.add_routes([web.get('/app', self.handleConnection), web.get('/health', self.healthCheck)])

    async def handleConnection(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.activeConnections.add(ws)
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                await self.processMessage(msg.data)
        return ws

    async def processMessage(self, message):
            payload = json.loads(message)
            if self.appEventHandler:
                await self.appEventHandler.handleAppMessage(payload)

    async def broadcastMessage(self, payload):
        for connection in list(self.activeConnections):
            if connection.closed:
                self.logger.warning("Removing closed connection from activeConnections.")
                self.activeConnections.remove(connection)
                continue
            try:
                await connection.send_str(json.dumps(payload))
            except ConnectionResetError as e:
                self.logger.error(f"ConnectionResetError while sending message: {e}")
                self.activeConnections.remove(connection)
            except Exception as e:
                self.logger.error(f"Unexpected error while sending message: {e}")
                self.activeConnections.remove(connection)

    async def healthCheck(self, request):
        return web.json_response({"status": "ok", "activeConnections": len(self.activeConnections)})
