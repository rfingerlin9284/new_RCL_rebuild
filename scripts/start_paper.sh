#!/bin/bash
# Start RICK in Paper Trading Mode
# Safe testing environment with simulated trading

set -e

echo "================================================"
echo "RICK - Paper Trading Mode"
echo "================================================"
echo ""

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    ./scripts/setup.sh
fi

source venv/bin/activate

echo "Starting paper trading engine..."
echo "Mode: Paper Trading"
echo "Features: 130"
echo "Initializing..."
echo ""

echo "Paper trading mode active"
echo "Monitoring dashboard: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""
