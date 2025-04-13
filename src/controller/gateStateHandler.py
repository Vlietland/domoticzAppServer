import os
from utils.logger import getLogger

class GateStateHandler:
    def __init__(self, publish):
        self.__logger = getLogger(__name__)
        self.__gateDevice = os.getenv('DEVICE_6')
        self.__gateState = "0"
        self.__gateToggleIdx = int(os.getenv('GATE_TOGGLE_IDX'))
        self.__publish = publish

    def setGateState(self, state):
        self.__gateState = state
        self.__logger.info(f"Gate state for device '{self.__gateDevice}' updated to: {self.__gateState}")

    def getGateDevice(self):
        return self.__gateDevice

    async def onOpenGateRequest(self, payload):
        if not self.__gateToggleIdx:
            self.__logger.debug("Gate toggle device index not configured")
            return
        if self.__gateState in ["1", "3"]:
            self.__logger.debug(f"Ignoring request: Gate currently open (=1) or opening (=3) (state = {self.__gateState})")
            return
        mqttPayload = {"command": "switchlight", "idx": self.__gateToggleIdx, "switchcmd": "On"}
        self.__publish('domoticz/in', mqttPayload)
        self.__logger.info(f"Gate open command sent: {mqttPayload}")

    async def onCloseGateRequest(self, payload):
        if not self.__gateToggleIdx:
            self.__logger.debug("Gate toggle device index not configured")
            return
        if self.__gateState in ["0", "2"]:
            self.__logger.debug(f"Ignoring request: Gate currently closed (=0) or closing (=2) (state = {self.__gateState})")
            return
        mqttPayload = {"command": "switchlight", "idx": self.__gateToggleIdx, "switchcmd": "On"}
        self.__publish('domoticz/in', mqttPayload)
        self.__logger.info(f"Gate close command sent: {mqttPayload}")
