import json
import jwt
import os
from aiohttp import web
from utils.logger import getLogger

class AppConnection:
    def __init__(self, eventHandler):
        self.logger = getLogger(__name__)
        self.jwtSecret = os.getenv('JWT_SECRET')
        self.eventHandler = eventHandler
        self.messageHandler = eventHandler
        self.activeConnections = set()
        self.app = web.Application()
        self.app.add_routes([web.get('/app', self.handleConnection), web.get('/health', self.healthCheck)])

    async def handleConnection(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        try:
            token = request.query.get('token')
            if not token or not self.validateToken(token):
                self.logger.warning("WebSocket authentication failed")
                await ws.close(code=4001, message=b'Invalid authentication')
                return ws  # Return the closed WebSocket
            self.activeConnections.add(ws)
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    await self.processMessage(msg.data)
        except Exception as e:
            self.logger.error(f"Error in WebSocket connection: {e}")
        finally:
            if ws in self.activeConnections:
                self.activeConnections.remove(ws)
            return ws

    def validateToken(self, token):
        try:
            jwt.decode(token, self.jwtSecret, algorithms=['HS256'])
            return True
        except jwt.PyJWTError:
            return False

    async def processMessage(self, message):
        try:
            payload = json.loads(message)
            if self.messageHandler:
                await self.messageHandler.handleAppMessage(payload)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    async def broadcastMessage(self, payload):
        for connection in list(self.activeConnections):
            try:
                if connection.closed:
                    self.activeConnections.remove(connection)
                else:
                    await connection.send_str(json.dumps(payload))
            except Exception as e:
                self.logger.error(f"Error sending message to connection: {e}")

    async def healthCheck(self, request):
        return web.json_response({"status": "ok", "activeConnections": len(self.activeConnections)})
