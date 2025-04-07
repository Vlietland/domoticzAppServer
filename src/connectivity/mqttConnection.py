import asyncio
import json
import os
import paho.mqtt.client as mqtt
from utils.logger import getLogger

class MqttConnection:
    def __init__(self, handleMqttMessageCallback=None, messageFilter=None, protocol=mqtt.MQTTv311):
        self.logger = getLogger(__name__)
        self.broker = os.getenv('MQTT_HOST')
        self.port = int(os.getenv('MQTT_PORT'))
        self.topic = os.getenv('TOPIC')
        self.client = mqtt.Client(client_id="DomoticzAppServer", protocol=protocol)
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.handleMqttMessageCallback = handleMqttMessageCallback
        self.messageFilter = messageFilter     

    def setHandleMqttMessageCallback(self, handleMqttMessageCallback):
        self.handleMqttMessageCallback = handleMqttMessageCallback

    def connect(self):
        try:
            self.logger.info(f"Attempting to connect to MQTT broker at {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")

    def onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Successfully connected to MQTT broker.")
            client.subscribe(self.topic)
            self.logger.info(f"Subscribed to topic: {self.topic}")
        else:
            self.logger.error(f"Connection failed with result code {rc}")

    def onMessage(self, client, userdata, message):
        payload = message.payload.decode('utf-8')
        topic = message.topic
        self.logger.info(f"Received MQTT message on topic {topic}: {payload}")
        try:
            parsedPayload = json.loads(payload)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse MQTT message as JSON.")
            return
        if self.messageFilter and not self.messageFilter.isMessageValid(topic, parsedPayload):
            self.logger.debug(f"Not a device that needs to be handled: {topic}")
            return
        if self.handleMqttMessageCallback:
            self.handleMqttMessageCallback(message.topic, parsedPayload)
            self.logger.info(f"ParsedPayload callback completed {parsedPayload}")

    def publish(self, topic, payload):
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        result = self.client.publish(topic, payload)
        if result.rc == 0:
            self.logger.info(f"Published message to {topic}")
            return True
        else:
            self.logger.error(f"Failed to publish message to {topic}, result code: {result.rc}")
            return False

    def onDisconnect(self, client, userdata, rc):
        self.logger.warning(f"Disconnected from MQTT broker with code {rc}. Reconnecting...")
        while True:
            try:
                self.client.reconnect()
                self.logger.info("Reconnected successfully.")
                break
            except Exception as e:
                self.logger.error(f"Reconnect attempt failed: {e}")
                asyncio.sleep(5)