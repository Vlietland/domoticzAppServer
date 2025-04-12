import asyncio
import os
import signal
from aiohttp import web
from connectivity.domoticzAppAPI import DomoticzAppAPI
from connectivity.cameraConnection import CameraConnection
from connectivity.mqttConnection import MqttConnection
from controller.appMessageHandler import AppMessageHandler
from controller.cameraHandler import CameraHandler
from controller.gateStateHandler import GateStateHandler
from controller.mqttMessageHandler import MqttMessageHandler
from controller.weatherHandler import WeatherHandler
from controller.alertHandler import AlertHandler
from model.messageFilter import MessageFilter
from model.alertQueue import AlertQueue
from utils.logger import getLogger

logger = getLogger(__name__)

class DomoticzAppServer:
    def __init__(self):
        self.__domoticzAppAPI = None
        self.__webSocketRunner = None
        self.__mqttConnection = None

    async def startServer(self):
        messageFilter = MessageFilter()
        cameraConnection = CameraConnection()
        self.__domoticzAppAPI = DomoticzAppAPI(handleAppMessageCallback=None)
        self.__mqttConnection = MqttConnection(handleMqttMessageCallback=None, messageFilter=messageFilter)
        
        weatherHandler = WeatherHandler()

        alertQueue = AlertQueue()
        alertHandler = AlertHandler(
            self.__domoticzAppAPI.broadcastMessage,
            alertQueue.getAlerts,
            alertQueue.deleteAlerts
        )
        
        gateStateHandler = GateStateHandler(self.__mqttConnection.publish)
        cameraHandler = CameraHandler(
            cameraConnection.getCameraImage,
            self.__domoticzAppAPI.broadcastMessage
        )
        
        mqttMessageHandler = MqttMessageHandler(
            gateStateHandler.getGateDevice,
            gateStateHandler.setGateState, 
            alertQueue.storeAlert,
            alertHandler.onNotification,
            weatherHandler.getWeatherDevice,
            weatherHandler.onWeatherDataReceived
        )

        appMessageHandler = AppMessageHandler(
            alertHandler.onGetAlertsRequest,
            alertHandler.onDeleteAlertsRequest,            
            cameraHandler.onCameraImageRequest,
            gateStateHandler.onOpenGateRequest,
            gateStateHandler.onCloseGateRequest            
        )
        self.__domoticzAppAPI.setHandleAppMessageCallback(appMessageHandler.onAppMessageCallback)
        self.__mqttConnection.setHandleMqttMessageCallback(mqttMessageHandler.onMqttMessageCallback)
        
        self.__mqttConnection.connect()
        self.__webSocketRunner = web.AppRunner(self.__domoticzAppAPI.getApp())
        host = os.getenv('SERVER_HOST')
        port = int(os.getenv('SERVER_PORT'))

        await self.__webSocketRunner.setup()
        site = web.TCPSite(self.__webSocketRunner, host, port)
        await site.start()
        logger.info(f"Domoticz app server started on {host}:{port}")

    async def shutdown(self):
        logger.info("Shutting down server and client...")
        try:
            for ws in list(self.__domoticzAppAPI.getActiveConnections()):
                await ws.close()
            self.__domoticzAppAPI.getActiveConnections().clear()
            await self.__webSocketRunner.cleanup()
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
        raise
