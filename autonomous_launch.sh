#!/bin/bash
# RICK AUTONOMOUS TRADING LAUNCH
# Starts full autonomous Hive Mind Collective trading with dashboard

set -e

cd /home/ing/RICK/new_RLC_rebuild

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                                ║"
echo "║              🤖 RICK HIVE MIND COLLECTIVE - AUTONOMOUS TRADING 🤖             ║"
echo "║                                                                                ║"
echo "║                  FULL AUTONOMOUS | NO MANUAL APPROVAL | 130+ FEATURES        ║"
echo "║                                                                                ║"
echo "║                    Closed-Loop Learning | Guardian Gates Active               ║"
echo "║                                                                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Verify Python
python3_version=$(python3 --version 2>&1)
echo "✅ Python: $python3_version"

# Create logs directory if needed
mkdir -p logs

# Display configuration
echo ""
echo "📋 AUTONOMOUS MODE CONFIGURATION"
echo "═════════════════════════════════════════════════════════════════════════════════"
echo "✅ Hive Autonomous: ENABLED"
echo "✅ Manual Approval: DISABLED"
echo "✅ Auto Execute Trades: ENABLED"
echo "✅ All 130+ Features: ENABLED"
echo "✅ Closed-Loop Learning: ENABLED"
echo "✅ Guardian Gates: ENABLED"
echo "✅ Real-Time Monitoring: ENABLED (60-second interval)"
echo "✅ Position Management: AUTONOMOUS"
echo "✅ Narration Logging: ENABLED"
echo "✅ Charts & Dashboard: ENABLED (Port 8501)"
echo "═════════════════════════════════════════════════════════════════════════════════"
echo ""

# Option to launch CLI or dashboard
echo "🚀 LAUNCH OPTIONS"
echo "═════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Option 1: CLI INTERFACE (Terminal-based)"
echo "   Command: python3 rick_cli.py"
echo "   Features: Dropdown menus, real-time narration, manual trade input"
echo "   Best for: Fast control, SSH access, headless servers"
echo ""
echo "Option 2: WEB DASHBOARD (Streamlit)"
echo "   Command: streamlit run dashboard.py"
echo "   URL: http://localhost:8501"
echo "   Features: Real-time charts, position tracking, hive analysis"
echo "   Best for: Visual monitoring, complete overview"
echo ""
echo "Option 3: BOTH SIMULTANEOUSLY"
echo "   Terminal 1: python3 rick_cli.py"
echo "   Terminal 2: streamlit run dashboard.py"
echo "   Best for: Complete control + monitoring"
echo ""
echo "═════════════════════════════════════════════════════════════════════════════════"
echo ""

# Ask user which option
echo "Select launch option (1/2/3) [default: 1]:"
read -p "Enter choice: " choice

case ${choice:-1} in
  1)
    echo ""
    echo "🚀 Starting RICK CLI..."
    python3 rick_cli.py
    ;;
  2)
    echo ""
    echo "🚀 Starting RICK Dashboard..."
    if command -v streamlit &> /dev/null; then
      streamlit run dashboard.py
    else
      echo "❌ Streamlit not found. Installing..."
      pip install streamlit
      streamlit run dashboard.py
    fi
    ;;
  3)
    echo ""
    echo "🚀 Starting BOTH CLI and Dashboard..."
    echo "Starting CLI in background..."
    python3 rick_cli.py &
    sleep 2
    echo ""
    echo "Starting Dashboard..."
    if command -v streamlit &> /dev/null; then
      streamlit run dashboard.py
    else
      echo "❌ Streamlit not found. Installing..."
      pip install streamlit
      streamlit run dashboard.py
    fi
    ;;
  *)
    echo "❌ Invalid option. Exiting."
    exit 1
    ;;
esac
