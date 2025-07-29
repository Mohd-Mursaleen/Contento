#!/bin/bash

# Content Creation Pipeline MVP Startup Script

echo "🚀 Starting Content Creation Pipeline MVP"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and configure your API keys."
    cp .env.example .env
    echo "📝 Created .env file from template. Please edit it with your configuration."
    exit 1
fi

# Check if OpenAI API key is configured
if grep -q "your-openai-api-key-here" .env; then
    echo "⚠️  Please configure your OpenAI API key in the .env file"
    echo "📝 Edit .env and replace 'your-openai-api-key-here' with your actual API key"
    exit 1
fi

# Run demo (optional)
if [ "$1" = "demo" ]; then
    echo "🎬 Running demo..."
    python demo.py
    exit 0
fi

# Run tests (optional)
if [ "$1" = "test" ]; then
    echo "🧪 Running tests..."
    pytest tests/ -v
    exit 0
fi

# Start the API server
echo "🌐 Starting API server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔍 Health check available at: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000