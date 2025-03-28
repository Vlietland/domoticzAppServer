import asyncio
import json
import os
import paho.mqtt.client as mqtt
import threading
import queue
import asyncio
from utils.logger import getLogger

class MqttConnection:
    def __init__(self, eventHandler, callback_api_version=None):
        self.logger = getLogger(__name__)
        self.broker = os.getenv('MQTT_HOST')
        self.port = int(os.getenv('MQTT_PORT'))
        self.domoticzTopic = "domoticz/out/#"
        self.eventHandler = eventHandler
        self.client = mqtt.Client(client_id="DomoticzAppServer", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.mqttThread = None
        self.stopEvent = threading.Event()
        self.messageQueue = queue.Queue()
        self.processingTask = None

    def connect(self):
        try:
            self.logger.info(f"Attempting to connect to MQTT broker at {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, 60)
            self.logger.info("Connection initiated")
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def onConnect(self, client, userdata, flags, rc, properties=None):
        self.logger.info(f"onConnect called with result code {rc}")
        if rc == 0:
            self.logger.info("Successfully connected to MQTT broker.")
            client.subscribe(self.domoticzTopic)
            self.logger.info(f"Subscribed to topic: {self.domoticzTopic}")
        else:
            self.logger.error(f"Connection failed with result code {rc}")

    def onMessage(self, client, userdata, message):
        try:
            payload = message.payload.decode('utf-8')
            self.logger.info(f"Received MQTT message on topic {message.topic}: {payload}")
            try:
                parsedPayload = json.loads(payload)
            except json.JSONDecodeError:
                self.logger.warning(f"Could not parse JSON from payload: {payload}")
                return
            
            if self.eventHandler:
                self.messageQueue.put((message.topic, parsedPayload))
        except Exception as e:
            self.logger.error(f"Error processing MQTT message: {e}")
    
    async def processMessageQueue(self):
        self.logger.info("Starting MQTT message queue processor")
        while not self.stopEvent.is_set():
            try:
                while not self.messageQueue.empty():
                    topic, payload = self.messageQueue.get_nowait()
                    try:
                        await self.eventHandler.handleMqttMessage(topic, payload)
                    except Exception as e:
                        self.logger.error(f"Error handling MQTT message: {e}")
                    finally:
                        self.messageQueue.task_done()
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in message queue processor: {e}")
                await asyncio.sleep(1)  # Wait a bit longer on error
        
        self.logger.info("MQTT message queue processor stopped")

    def start(self):
        try:
            self.connect()
            self.client.loop_start()
            # Start the message queue processor in the current event loop
            self.processingTask = asyncio.create_task(self.processMessageQueue())
            self.logger.info("MQTT connection started with message queue processor")
        except Exception as e:
            self.logger.error(f"Error starting MQTT: {e}")

    async def disconnectMqttAsync(self):
        if self.client.is_connected():
            self.client.loop_stop()
            self.client.disconnect()

    def stop(self):
        self.logger.info("Stopping MQTT client...")
        self.stopEvent.set()
        
        # Cancel the message processing task if it exists
        if self.processingTask and not self.processingTask.done():
            self.processingTask.cancel()

        asyncio.create_task(self.disconnectMqttAsync())

        if self.mqttThread:
            self.mqttThread.join()
        self.logger.info("MQTT client stopped")

    def isConnected(self):
        return self.client.is_connected()
        
    def publish(self, topic, payload):
        if not self.isConnected():
            self.logger.error("Cannot publish: MQTT client not connected")
            return False
        try:
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            result = self.client.publish(topic, payload)
            if result.rc == 0:
                self.logger.info(f"Published message to {topic}")
                return True
            else:
                self.logger.error(f"Failed to publish message to {topic}, result code: {result.rc}")
                return False
        except Exception as e:
            self.logger.error(f"Error publishing message: {e}")
            return False
