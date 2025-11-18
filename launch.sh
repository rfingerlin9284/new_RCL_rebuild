#!/bin/bash
# RICK Enhanced System Launch Script
# Approval 841921 - Complete Autonomous Trading Platform

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                                ║"
echo "║                  🤖 RICK HIVE MIND COLLECTIVE TRADING 🤖                       ║"
echo "║                                                                                ║"
echo "║                  Approval 841921 - ENHANCED SYSTEM LAUNCH                     ║"
echo "║                                                                                ║"
echo "║         Dropdown Menus | Plain English Narration | Manual Trades             ║"
echo "║         Real-Time Monitoring | Autonomous Position Management                ║"
echo "║                                                                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs/

echo "✅ Python3 found"
echo "✅ Logs directory ready"
echo ""

# Show startup info
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "SYSTEM INFORMATION"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📁 Project Root: $(pwd)"
echo "📝 Configuration: config/task_config.json"
echo "📝 Environment: .env"
echo "📜 Narration Log: logs/narration.log"
echo "📊 Position Updates: position_updates.json"
echo "🐍 Python Version: $(python3 --version)"
echo ""

# Test imports
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "VERIFYING SYSTEM COMPONENTS"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""

python3 << 'EOF'
import sys
components = [
    ("Narration Logger", "config.narration_logger"),
    ("Enhanced Task Config", "config.enhanced_task_config"),
    ("Position Manager", "position_manager"),
]

all_ok = True
for name, module in components:
    try:
        __import__(module)
        print(f"✅ {name}: OK")
    except Exception as e:
        print(f"❌ {name}: FAILED - {e}")
        all_ok = False

if all_ok:
    print("\n✅ All components verified successfully!")
else:
    print("\n❌ Some components failed verification")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Component verification failed"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "READY TO LAUNCH"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "🎯 To start the RICK Interactive CLI, run:"
echo ""
echo "   python3 rick_cli.py"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "AVAILABLE ACTIONS IN CLI"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "1) ▶️  START - Initialize system"
echo "2) ⏹️  STOP - Shutdown system"
echo "3) 📊 VERIFY STATUS - Check health"
echo "4) 👤 MANUAL TRADE - Input custom trades"
echo "5) 📈 REASSESS POSITIONS - Check open trades"
echo "6) 📜 VIEW NARRATION LOG - Stream real-time events"
echo "7) 🔧 SETTINGS - Configure parameters"
echo "8) ❌ EXIT - Quit CLI"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "DOCUMENTATION"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📄 ENHANCED_SYSTEM_GUIDE.md - Complete feature guide"
echo "📄 INDEX.md - Documentation index"
echo "📄 QUICK_START.md - Command reference"
echo "📄 APPROVAL_841921_DELIVERY.md - Delivery summary"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "✅ System ready. Execute: python3 rick_cli.py"
echo ""
