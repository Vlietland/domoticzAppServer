#!/bin/bash

set -e

echo "📦 Setting up Python virtual environment and dependencies..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install it first."
    exit 1
fi

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "🌀 Creating virtual environment in .venv..."
    python3 -m venv .venv
else
    echo "✅ Virtual environment already exists."
fi

# Activate virtual environment
echo "🔒 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Ensure pipreqs is installed
if ! pip show pipreqs &> /dev/null; then
    echo "🔍 Installing pipreqs for import-based dependency detection..."
    pip install pipreqs
fi

# Run pipreqs to regenerate requirements.txt based on imports
echo "🔍 Generating requirements.txt from imports in ./src..."
pipreqs ./src --force --savepath requirements.txt

# Install all detected dependencies
echo "📚 Installing required packages..."
pip install -r requirements.txt

# Final freeze of all installed packages (including pipreqs, etc.)
echo "🧊 Freezing complete dependency set to requirements.txt..."
pip freeze > requirements.txt

echo "✅ Setup complete. Virtual environment ready!"
echo "👉 To activate later: source .venv/bin/activate"
