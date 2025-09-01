#!/bin/bash

ENV=${1:-}
echo "🤖 Starting AMPY Jr. Twitter bot..."

##
## Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

##
## Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy env.example to .env and configure your Twitter API credentials"
    exit 1
fi

##
## Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

##
## Check if dependencies are installed
if ! python -c "import tweepy, schedule, dotenv" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

##
## Run the bot
echo "🚀 Starting bot"
python main.py $ENV
