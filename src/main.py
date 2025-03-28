import asyncio
import os
import signal
from aiohttp import web
from connectivity.appConnection import AppConnection
from connectivity.cameraConnection import CameraConnection
from connectivity.mqttConnection import MqttConnection
from logic.mqttEventHandler import MqttEventHandler
from logic.appEventHandler import AppEventHandler
from testing.domoticzAppTestClient import DomoticzAppTestClient
from utils.logger import getLogger

logger = getLogger(__name__)

async def startServer():
    appEventHandler = AppEventHandler()    
    mqttEventHandler = MqttEventHandler()

    cameraConnection = CameraConnection()
    appConnection = AppConnection(appEventHandler)
    mqttConnection = MqttConnection(mqttEventHandler)

    appEventHandler.setCameraConnection(cameraConnection)
    appEventHandler.setAppConnection(appConnection)
    appEventHandler.setMqttConnection(mqttConnection)

    mqttEventHandler.setCameraConnection(cameraConnection)
    mqttEventHandler.setAppConnection(appConnection)

    mqttConnection.start()

    webSocketRunner = web.AppRunner(appConnection.app)
    host = os.getenv('SERVER_HOST')
    port = int(os.getenv('SERVER_PORT'))

    await webSocketRunner.setup()
    site = web.TCPSite(webSocketRunner, host, port)
    await site.start()
    logger.info(f"Domoticz app server started on {host}:{port}")

    return webSocketRunner, mqttConnection

async def shutdown(runner, mqttConnection, client_task):
    logger.info("Shutting down server and client...")
    try:
        if client_task:
            await client_task.get_loop().run_until_complete(client_task.result().stop())
            try:
                await client_task
            except asyncio.CancelledError:
                logger.info("WebSocket test client stopped.")
        mqttConnection.stop()
        await runner.cleanup()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

async def main():
    webSocketRunner, mqttConnection = await startServer()
    domoticzAppTestTask = None
    if os.getenv('TESTING') == "YES":
        domoticzAppTestClient = DomoticzAppTestClient()
        domoticzAppTestTask = asyncio.create_task(domoticzAppTestClient.start())
    stopEvent = asyncio.Event()

    def stop():
        logger.info("Received stop signal, shutting down...")
        stopEvent.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop)
    await stopEvent.wait()
    await shutdown(webSocketRunner, mqttConnection, domoticzAppTestTask)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
