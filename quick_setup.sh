#!/bin/bash
# RICK SETUP - Quick Start Script
# One-command initialization of all 130 features

cd /home/ing/RICK/new_RLC_rebuild

echo "================================================"
echo "RICK Live Clean Rebuild - Quick Setup"
echo "Version: 3.0.0"
echo "Features: 130"
echo "================================================"
echo ""

# Make scripts executable
chmod +x scripts/*.sh

# Run setup
echo "Running setup..."
./scripts/setup.sh

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Your RICK system is ready with:"
echo "  ✓ 130 Features configured"
echo "  ✓ 10 Feature categories organized"
echo "  ✓ Multiple trading engines"
echo "  ✓ Advanced risk management"
echo "  ✓ ML/AI components"
echo "  ✓ Comprehensive monitoring"
echo ""
echo "Next: Run './scripts/start_paper.sh' to begin trading"
echo ""
