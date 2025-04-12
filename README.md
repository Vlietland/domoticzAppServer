# DomoticzAppServer

A middleware server that facilitates communication between the DomoticzApp mobile application and a Domoticz home automation system using MQTT. This server handles authentication, message translation, and real-time event processing.

## System Requirements

- Python 3.8 or higher
- MQTT Broker (e.g., Mosquitto)
- Network connectivity to both the mobile app and Domoticz system
- Sufficient permissions to bind to the configured port

## Features

- **WebSocket Communication**: Real-time bidirectional communication with the mobile app
- **MQTT Integration**: Seamless integration with Domoticz via MQTT protocol
- **JWT Authentication**: Secure authentication using JSON Web Tokens
- **Message Translation**: Converts app commands to Domoticz-compatible MQTT messages
- **Event Processing**: Handles and routes events between the app and Domoticz
- **Camera Feed Support**: Manages camera feed URLs for the mobile app
- **Geofence Processing**: Handles geofence-triggered events from the mobile app
- **Configurable Settings**: Easily customizable through environment variables
- **Graceful Shutdown**: Proper resource cleanup on server termination

## Architecture

The DomoticzAppServer acts as a bridge between the mobile app and the Domoticz system:

```
┌─────────────┐      WebSocket      ┌──────────────────┐      MQTT      ┌─────────────┐
│ DomoticzApp │ <----------------> │ DomoticzAppServer │ <-----------> │   Domoticz   │
│ Mobile App  │                    │    Middleware     │                │   System     │
└─────────────┘                    └──────────────────┘                └─────────────┘
```

## Project Structure

```
domoticzAppServer/
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker build configuration
├── .env                     # Environment configuration
├── requirements.txt         # Python dependencies
├── run.sh                   # Script to run the server
├── setup.sh                 # Setup script
├── README.md                # This documentation file
└── src/                     # Source code directory
    ├── connectivity/        # Network connectivity modules
    │   ├── cameraConnection.py    # Camera feed handling
    │   ├── domoticzAppAPI.py      # App API implementation
    │   └── mqttConnection.py      # MQTT client implementation
    ├── controller/          # Business logic controllers
    │   ├── alertHandler.py        # Alert processing
    │   ├── appMessageHandler.py   # App message handling
    │   ├── cameraHandler.py       # Camera management
    │   ├── gateStateHandler.py    # Gate control logic
    │   └── mqttMessageHandler.py  # MQTT message processing
    ├── model/               # Data models
    │   ├── alertQueue.py          # Alert queue management
    │   └── messageFilter.py       # Message filtering logic
    ├── utils/               # Utility modules
    │   └── logger.py              # Logging configuration
    └── main.py              # Main entry point and server initialization
```

## Prerequisites

Before setting up the DomoticzAppServer, ensure you have:

1. **Python Environment**: Python 3.8+ installed on your system
2. **MQTT Broker**: A running MQTT broker (like Mosquitto) accessible from the server
3. **Domoticz System**: A configured Domoticz installation with MQTT plugin enabled
4. **Network Configuration**: Proper network setup to allow connections between all components

## Installation

### Standard Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/domoticzAppServer.git
   cd domoticzAppServer
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the environment:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration (see Configuration section)
   ```

### Docker Installation (Alternative)

If you prefer using Docker:

1. Build the Docker image:
   ```bash
   docker build -t domoticz-app-server .
   ```

2. Run the container:
   ```bash
   docker run -d --name domoticz-server \
     -p 8080:8080 \
     --env-file .env \
     domoticz-app-server
   ```

## Configuration

### Environment Variables

The server is configured through environment variables, which can be set in the `.env` file:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MQTT_BROKER` | Hostname or IP of the MQTT broker | localhost | Yes |
| `MQTT_PORT` | Port of the MQTT broker | 1883 | Yes |
| `MQTT_USERNAME` | Username for MQTT authentication | - | No |
| `MQTT_PASSWORD` | Password for MQTT authentication | - | No |
| `MQTT_TOPIC_IN_GATE` | MQTT topic for gate control messages | domoticz/in/gate | Yes |
| `MQTT_TOPIC_IN_CUSTOM` | MQTT topic for custom messages | domoticz/in/custom | No |
| `MQTT_TOPIC_OUT` | MQTT topic for outgoing messages | domoticz/out | Yes |
| `GATE_DEVICE_IDX` | Domoticz device index for gate control | - | Yes |
| `SERVER_HOST` | Host to bind the server to | 0.0.0.0 | No |
| `SERVER_PORT` | Port to bind the server to | 8080 | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |
| `CAMERA_URLS` | Comma-separated list of camera URLs | - | No |

Example `.env` file:
```
MQTT_BROKER=192.168.1.100
MQTT_PORT=1883
MQTT_USERNAME=domoticz
MQTT_PASSWORD=password
MQTT_TOPIC_IN_GATE=domoticz/in/gate
GATE_DEVICE_IDX=42
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
LOG_LEVEL=INFO
CAMERA_URLS=http://camera1.local/stream,http://camera2.local/stream
```

## Running the Server

### Starting the Server

```bash
python src/main.py
```

Alternatively, you can use the provided run script:

```bash
./run.sh
```

The server will start and listen for WebSocket connections on the configured host and port.

### Running as a Service

For production environments, it's recommended to run the server as a system service.

#### Systemd Service (Linux)

Create a systemd service file at `/etc/systemd/system/domoticz-app-server.service`:

```ini
[Unit]
Description=DomoticzAppServer Middleware
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/domoticzAppServer
ExecStart=/path/to/domoticzAppServer/venv/bin/python src/main.py
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable domoticz-app-server
sudo systemctl start domoticz-app-server
```

## API and Protocol

### WebSocket API

The server exposes a WebSocket endpoint at `/app` that the mobile app connects to.

#### Authentication

When connecting, the client must provide a valid JWT token in the connection request.

#### Message Format

Messages exchanged over WebSocket use JSON format:

```json
{
  "type": "message_type",
  "data": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

### Supported Message Types

#### From App to Server

| Type | Description | Data Fields |
|------|-------------|-------------|
| `opengate` | Request to open the gate | None |
| `geofence_enter` | Notification that device entered geofence | `{"latitude": float, "longitude": float}` |
| `geofence_exit` | Notification that device exited geofence | `{"latitude": float, "longitude": float}` |
| `request_cameras` | Request camera URLs | None |

#### From Server to App

| Type | Description | Data Fields |
|------|-------------|-------------|
| `notification` | Alert notification | `{"device": string, "message": string, "image_url": string (optional)}` |
| `camera_list` | List of camera URLs | `{"cameras": [string, string, ...]}` |
| `connection_status` | Server connection status | `{"connected": boolean}` |

### MQTT Topics

The server subscribes to and publishes on the following MQTT topics:

| Topic | Direction | Purpose |
|-------|-----------|---------|
| `domoticz/in/gate` | Publish | Send gate control commands |
| `domoticz/in/custom` | Publish | Send custom commands |
| `domoticz/out/#` | Subscribe | Receive events from Domoticz |

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Check if the server is running
   - Verify the SERVER_HOST and SERVER_PORT settings
   - Ensure no firewall is blocking the connection

2. **Authentication Failures**:
   - Verify the JWT_SECRET matches between server and app
   - Check if the token is expired or malformed

3. **MQTT Connection Issues**:
   - Confirm the MQTT broker is running
   - Verify MQTT_BROKER and MQTT_PORT settings
   - Check MQTT credentials if authentication is enabled

4. **Message Not Reaching Domoticz**:
   - Verify the MQTT topics match Domoticz configuration
   - Check if the GATE_DEVICE_IDX is correct
   - Ensure Domoticz MQTT plugin is properly configured

### Logging

The server logs to the console with the configured LOG_LEVEL. For more detailed logs, set LOG_LEVEL=DEBUG in your .env file.

To view logs when running as a systemd service:
```bash
sudo journalctl -u domoticz-app-server -f
```

## Development

### Setting Up Development Environment

1. Follow the installation steps
2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Running Tests

```bash
pytest
```

### Code Style

This project follows PEP 8 style guidelines. Use flake8 to check your code:
```bash
flake8 .
```

## Contributing

We welcome contributions to improve DomoticzAppServer! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

Please follow the project's coding style and include appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that is short and to the point. It lets people do anything they want with your code as long as they provide attribution back to you and don't hold you liable.
