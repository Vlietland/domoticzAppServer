import asyncio
import os
import signal
from aiohttp import web
from connectivity.domoticzAppAPI import DomoticzAppAPI
from connectivity.cameraConnection import CameraConnection
from connectivity.mqttConnection import MqttConnection
from logic.mqttEventHandler import MqttEventHandler
from logic.appEventHandler import AppEventHandler
from utils.logger import getLogger

logger = getLogger(__name__)

class DomoticzAppServer:
    def __init__(self):
        self.domoticzAppAPI = None
        self.webSocketRunner = None
        self.mqttConnection = None
        self.domoticzAppTestTask = None

    async def startServer(self):
        appEventHandler = AppEventHandler()    
        mqttEventHandler = MqttEventHandler()

        cameraConnection = CameraConnection()
        self.domoticzAppAPI = DomoticzAppAPI(appEventHandler)
        self.mqttConnection = MqttConnection(mqttEventHandler)

        appEventHandler.setCameraConnection(cameraConnection)
        appEventHandler.setDomoticzAppAPI(self.domoticzAppAPI)
        appEventHandler.setMqttConnection(self.mqttConnection)

        mqttEventHandler.setCameraConnection(cameraConnection)
        mqttEventHandler.setDomoticzAppAPI(self.domoticzAppAPI)
        mqttEventHandler.setAppEventHandler(appEventHandler)

        self.mqttConnection.start()

        self.webSocketRunner = web.AppRunner(self.domoticzAppAPI.app)
        host = os.getenv('SERVER_HOST')
        port = int(os.getenv('SERVER_PORT'))

        await self.webSocketRunner.setup()
        site = web.TCPSite(self.webSocketRunner, host, port)
        await site.start()
        logger.info(f"Domoticz app server started on {host}:{port}")

    async def shutdown(self):
        logger.info("Shutting down server and client...")
        try:
            for ws in list(self.domoticzAppAPI.activeConnections):
                await ws.close()
            self.domoticzAppAPI.activeConnections.clear()

            if self.domoticzAppTestTask:
                await self.domoticzAppTestTask.get_loop().run_until_complete(self.domoticzAppTestTask.result().stop())
                try:
                    await self.domoticzAppTestTask
                except asyncio.CancelledError:
                    logger.info("WebSocket test client stopped.")

            self.mqttConnection.stop()
            await self.webSocketRunner.cleanup()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def main(self):
        await self.startServer()
        stopEvent = asyncio.Event()

        def stop():
            logger.info("Received stop signal, shutting down...")
            stopEvent.set()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop)
        
        await stopEvent.wait()
        await self.shutdown()


if __name__ == "__main__":
    try:
        server = DomoticzAppServer()
        asyncio.run(server.main())
    except Exception as e:
        logger.error(f"Server error: {e}")
        #raise
