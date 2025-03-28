## DomoticzAppServer

### Overview
A middleware server facilitating communication between a mobile app and Domoticz via MQTT, providing authentication and message translation.

### Features
- MQTT-based communication
- JWT-based authentication
- OpenGate message translation
- Configurable MQTT topics
- Graceful shutdown handling

### Project Structure
```
domoticzAppServer/
├── server.py          # Main entry point
├── .env.example       # Environment configuration template
├── requirements.txt   # Python dependencies
└── src/
    ├── api/
    │   └── middleware.py  # WebSocket and API logic
    ├── logic/
    │   └── event_handler.py  # MQTT event processing
    └── utils/
        └── config.py    # Configuration management
```

### Prerequisites
- Python 3.8+
- MQTT Broker (e.g., Mosquitto)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy and configure the environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

### Configuration

#### Environment Variables

Configure the `.env` file with the following key settings:

- `JWT_SECRET`: A secret key for JWT authentication
- `MQTT_BROKER`: MQTT broker hostname
- `MQTT_PORT`: MQTT broker port
- `MQTT_TOPIC_IN_GATE`: MQTT topic for gate control messages
- `GATE_DEVICE_IDX`: Domoticz device index for gate control
- `SERVER_HOST` and `SERVER_PORT`: Middleware server network configuration

### Running the Server

```bash
python server.py
```

### MQTT Topics

- `domoticz/in/gate`: Incoming gate control messages
- `domoticz/in/custom`: Custom incoming messages
- `domoticz/out/#`: Outgoing Domoticz messages

### OpenGate Message Translation

Send a WebSocket message with the following format to trigger gate opening:
```json
{
  "type": "opengate"
}
```

### Authentication

The server uses JWT for WebSocket connection authentication. Ensure a valid token is provided when connecting.

### Logging

Logs are output to the console with timestamps and log levels.

### Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
