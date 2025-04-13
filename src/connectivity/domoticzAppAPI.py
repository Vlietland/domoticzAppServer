import asyncio
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
        self.broadcastQueue = asyncio.Queue()
        self.__mainLoop = asyncio.get_event_loop()
        asyncio.create_task(self._processBroadcastQueue())

    def getActiveConnections(self):
        return list(self.__activeConnections)

    def setHandleAppMessageCallback(self, callback):
        self.__handleAppMessageCallback = callback

    def getApp(self):
        return self.__app

    async def handleConnection(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.__activeConnections.add(ws)
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

    def enqueueMessage(self, payload: dict):
        try:
            asyncio.run_coroutine_threadsafe(self.broadcastQueue.put(payload), self.__mainLoop)
            self.__logger.debug(f"Enqueued message")
        except Exception as e:
            self.__logger.error(f"Failed to enqueue message: {e}")

    async def _processBroadcastQueue(self):
        self.__logger.info("Starting broadcast queue processor.")
        while True:
            try:
                payload = await self.broadcastQueue.get()
                self.__logger.debug(f"Dequeued message for broadcast")
                if not payload:
                    await asyncio.sleep(0.1)
                    continue
                
                messageStr = json.dumps(payload)
                
                for connection in list(self.__activeConnections):
                    if connection.closed:
                        self.__logger.warning("Removing closed connection during broadcast.")
                        self.__activeConnections.remove(connection)
                        continue
                    try:
                        await connection.send_str(messageStr)
                        self.__logger.debug(f"Message sent to client {connection}")
                    except ConnectionResetError:
                        self.__logger.warning(f"ConnectionResetError for client {connection}. Removing.")
                        self.__activeConnections.remove(connection)
                    except Exception as e:
                        self.__logger.error(f"Unexpected error sending to client {connection}: {e}. Removing.")
                        self.__activeConnections.remove(connection)
                
                self.broadcastQueue.task_done()
            except asyncio.CancelledError:
                self.__logger.info("Broadcast queue processor task cancelled.")
                break
            except Exception as e:
                self.__logger.error(f"Error in broadcast queue processor task: {e}", exc_info=True)
                await asyncio.sleep(1)
