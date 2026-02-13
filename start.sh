#!/bin/bash
# Enhanced Student Help Bot Startup Script - Linux/Mac

echo "🚀 Starting Enhanced Student Help Bot..."
echo "=================================================="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found."
    echo "📋 Creating .env from example..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your credentials"
    echo "   nano .env"
    exit 1
fi

# Install requirements
echo "📦 Checking requirements..."
pip3 install -r requirements.txt -q

# Check if enhanced_bot.py exists
if [ -f "enhanced_bot.py" ]; then
    echo "🤖 Starting Enhanced Bot..."
    python3 enhanced_bot.py
else
    echo "⚠️  enhanced_bot.py not found, falling back to original bot..."
    python3 student_help_bot.py
fi