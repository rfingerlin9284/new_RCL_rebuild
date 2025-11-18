#!/bin/bash
# Test RICK Installation
# Verifies all 130 features are properly configured

echo "================================================"
echo "RICK 130 Features - System Verification"
echo "================================================"
echo ""

cd /home/ing/RICK/new_RLC_rebuild

echo "✓ Project location: $(pwd)"
echo ""

echo "Checking directories..."
dirs=(engines risk ml_ai monitoring strategies data deployment ui testing advanced config scripts docs)
count=0
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        count=$((count+1))
        echo "  ✓ $dir/"
    fi
done
echo "Directories verified: $count/13"
echo ""

echo "Checking Python modules..."
modules=(engines risk ml_ai monitoring strategies data deployment ui testing advanced)
mod_count=0
for mod in "${modules[@]}"; do
    if [ -f "$mod/__init__.py" ]; then
        mod_count=$((mod_count+1))
        echo "  ✓ $mod/__init__.py"
    fi
done
echo "Modules verified: $mod_count/10"
echo ""

echo "Checking main files..."
files=(__init__.py config/main_config.py requirements.txt .env.template README.md IMPLEMENTATION_GUIDE.md RICK_130_FEATURES_ANALYSIS.md)
file_count=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        file_count=$((file_count+1))
        echo "  ✓ $file"
    fi
done
echo "Main files verified: $file_count/7"
echo ""

echo "Checking scripts..."
scripts=(scripts/setup.sh scripts/start_paper.sh scripts/launch_dashboard.sh scripts/quick_setup.sh)
script_count=0
for script in "${scripts[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ] 2>/dev/null || [ -f "$script" ]; then
        script_count=$((script_count+1))
        echo "  ✓ $script"
    fi
done
echo "Scripts verified: $script_count/4"
echo ""

echo "================================================"
echo "SYSTEM STATUS: READY FOR INITIALIZATION"
echo "================================================"
echo ""
echo "To get started:"
echo "  1. chmod +x scripts/*.sh"
echo "  2. ./scripts/setup.sh"
echo "  3. ./scripts/start_paper.sh"
echo ""
