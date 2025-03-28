#!/bin/bash

set -e

IMAGE_NAME="domoticz-app-server"
CONTAINER_NAME="domoticzAppServerContainer"
PORT=5000

if [ "$1" == "docker" ]; then
    echo "🚀 Running in Docker mode..."
    docker build -t $IMAGE_NAME .

    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        echo "🛑 Stopping and removing existing container..."
        docker stop $CONTAINER_NAME
        docker rm -f $CONTAINER_NAME
    fi

    echo "🚢 Starting new container..."
    CONTAINER_ID=$(docker run -d -p $PORT:$PORT --name $CONTAINER_NAME $IMAGE_NAME)
    echo "✅ Container '$CONTAINER_NAME' running at port $PORT with container ID $CONTAINER_ID"

    sleep 1
    docker logs -f $CONTAINER_NAME
else
    echo "💻 Running locally in the virtual environment..."

    if [ -z "$VIRTUAL_ENV" ]; then
        if [ -d ".venv" ]; then
            echo "🔄 Virtual environment detected, activating..."
            source .venv/bin/activate
            echo "✅ Virtual environment activated. Next time, run: source .venv/bin/activate"
            exec "$0" "$@"  # Re-run this script inside the activated environment
        else
            echo "❌ Virtual environment not found. Please run ./setup.sh first."
            exit 1
        fi
    fi

    if [ -f "requirements.txt" ]; then
        echo "📦 Checking dependencies..."
        pip install -r requirements.txt
    fi

    echo "🚀 Starting the application..."
    python3 src/main.py
fi
