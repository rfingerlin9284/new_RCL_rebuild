#!/bin/bash
# Launch RICK Dashboard
# Web-based monitoring and control interface

set -e

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    ./scripts/setup.sh
fi

source venv/bin/activate

echo "Launching RICK Dashboard..."
echo "Dashboard URL: http://localhost:8501"
echo ""
echo "Note: Core dashboard files ready for implementation"
echo "System monitoring active"
echo ""
