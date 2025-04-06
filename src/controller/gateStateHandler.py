import os
from utils.logger import getLogger

class GateStateHandler:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.gateDevice = os.getenv('DEVICE_6')
        self.gateState = "0"
        self.gateToggleIdx = int(os.getenv('GATE_TOGGLE_IDX'))        

    def setGateState(self, state):
        self.gateState = state
        self.logger.info(f"Gate state for device '{self.gateDevice}' updated to: {self.validStates[state]}")

    def getGateDevice(self):
        return gateDevice

    async def onOpenGateRequest(self, payload):
        if not self.gateToggleIdx:
            self.logger.debug("Gate toggle device index not configured")
            return
        if self.gateState in ["1", "3"]:
            self.logger.debug(f"Ignoring request: Gate currently open (=1) or opening (=3) (state = {self.gateState})")
            return
        mqttPayload = {"command": "switchlight", "idx": self.gateToggleIdx, "switchcmd": "On"}
        self.mqttConnection.publish('domoticz/in', mqttPayload)
        self.logger.info(f"Gate open command sent: {mqttPayload}")

