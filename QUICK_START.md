# RICK QUICK START - COMMAND REFERENCE
## Fast Reference for All Task Configuration Commands

---

## 📱 ONE-LINER SETUP EXAMPLES

### Paper Trading (Safest - Start Here)
```bash
cd /home/ing/RICK/new_RLC_rebuild

python3 << 'EOF'
from config.task_config import TaskConfigManager
mgr = TaskConfigManager()
mgr.set_paper_practice_mode()
mgr.activate_broker("oanda")
mgr.activate_broker("ibkr")
mgr.deactivate_broker("coinbase")
mgr.power_on_autonomous()
mgr.enable_hive_autonomous()
mgr.enable_hive_learning()
mgr.enable_hive_dialogue()
mgr.print_status()
EOF
```

**Result:**
- ✓ Oanda + IBKR trading
- ✓ Paper money (simulated)
- ✓ Hive autonomous
- ✓ Learning enabled
- ✓ Full communication

---

### Live Trading (Real Money)
```bash
python3 << 'EOF'
from config.task_config import TaskConfigManager
mgr = TaskConfigManager()
mgr.set_live_real_money_mode()
mgr.activate_broker_autonomous("oanda")
mgr.activate_broker_autonomous("ibkr")
mgr.deactivate_broker("coinbase")
mgr.power_on_autonomous()
mgr.enable_hive_autonomous()
mgr.enable_hive_learning()
mgr.enable_hive_dialogue()
mgr.print_status()
EOF
```

**Result:**
- ✓ Oanda + IBKR trading
- ✓ REAL MONEY (⚠️ CAREFUL!)
- ✓ Hive autonomous
- ✓ Learning from live trades
- ✓ Full communication

---

### Manual Approval Mode (Hive suggests, you approve)
```bash
python3 << 'EOF'
from config.task_config import TaskConfigManager
mgr = TaskConfigManager()
mgr.set_paper_real_time_mode()
mgr.activate_broker("oanda")
mgr.pause_system()
mgr.disable_hive_autonomous()
mgr.enable_hive_dialogue()
mgr.print_status()
EOF
```

**Result:**
- ✓ Real market data
- ✓ Simulated money
- ✓ Hive suggests trades
- ✓ You manually approve each one
- ✓ Perfect for learning

---

## 🎮 INDIVIDUAL COMMANDS

### Trading Modes
```python
from config.task_config import TaskConfigManager
mgr = TaskConfigManager()

# Switch modes
mgr.set_paper_practice_mode()      # Fake money, fake data
mgr.set_paper_real_time_mode()     # Fake money, real market data
mgr.set_live_real_money_mode()     # ⚠️ REAL MONEY
```

### System Power
```python
mgr.power_on_autonomous()   # 100% online, trading automatically
mgr.pause_system()          # Online but waiting for commands
mgr.power_off()             # Complete shutdown
```

### Broker Control
```python
mgr.activate_broker("oanda")                    # Turn on Oanda
mgr.activate_broker("ibkr")                     # Turn on IBKR
mgr.activate_broker("coinbase")                 # Turn on Coinbase
mgr.deactivate_broker("coinbase")               # Turn off Coinbase
mgr.activate_broker_autonomous("oanda")         # On + autonomous
mgr.get_active_brokers()                        # List active brokers
```

### Hive Mind Control
```python
mgr.enable_hive_autonomous()    # Hive decides automatically
mgr.disable_hive_autonomous()   # Hive waits for approval
mgr.enable_hive_learning()      # Learn from trade outcomes
mgr.disable_hive_learning()     # No learning
mgr.enable_hive_dialogue()      # Open communication
mgr.disable_hive_dialogue()     # Quiet mode
```

### Status & Info
```python
mgr.print_status()              # Show all settings
mgr.get_status_dict()           # Get status as dictionary
mgr.config.to_dict()            # Get full config as dictionary
```

### Save Configuration
```python
mgr.save()                       # Save current config to file
mgr.config.save_to_file("task_config.json")  # Save to specific file
```

---

## 🔍 COMMON TASKS

### Task: Switch from Paper to Live
```python
mgr = TaskConfigManager()
mgr.set_live_real_money_mode()      # Change mode
mgr.power_on_autonomous()           # Restart
mgr.print_status()                  # Verify
```

### Task: Disable Coinbase, Keep Oanda + IBKR
```python
mgr = TaskConfigManager()
mgr.deactivate_broker("coinbase")
mgr.activate_broker("oanda")
mgr.activate_broker("ibkr")
mgr.save()
mgr.print_status()
```

### Task: Let Hive Suggest Trades, You Approve
```python
mgr = TaskConfigManager()
mgr.pause_system()
mgr.disable_hive_autonomous()
mgr.enable_hive_dialogue()
mgr.print_status()

# Later, when hive has suggestions:
# Review hive_dashboard
# Approve or reject manually
# Execute approved trades
```

### Task: Emergency Shutdown
```python
mgr = TaskConfigManager()
mgr.power_off()
mgr.print_status()
# All trading stops immediately
```

### Task: Enable Learning from Trades
```python
mgr = TaskConfigManager()
mgr.enable_hive_learning()      # Closed-loop feedback ON
mgr.print_status()
# System now learns from every trade outcome
```

### Task: Disable Learning (Testing Phase)
```python
mgr = TaskConfigManager()
mgr.disable_hive_learning()     # No learning
mgr.print_status()
# System trades but doesn't learn yet
```

### Task: View Current Active Brokers
```python
mgr = TaskConfigManager()
active = mgr.get_active_brokers()
print(f"Currently active: {active}")
# Output: Currently active: ['oanda', 'ibkr']
```

### Task: Get Status as Dictionary (for scripts)
```python
mgr = TaskConfigManager()
status = mgr.get_status_dict()

trading_mode = status['trading_mode']           # 'paper_practice'
system_status = status['system_status']         # 'online_autonomous'
active_brokers = status['active_brokers']       # ['oanda', 'ibkr']
hive = status['hive']                           # {'autonomous': True, ...}
timestamp = status['timestamp']                 # '2025-11-13T...'
```

---

## 📊 UNDERSTANDING THE STATUS OUTPUT

When you run `mgr.print_status()`, you see:

```
============================================================
RICK SYSTEM STATUS
============================================================
Trading Mode: PAPER_PRACTICE          ← You use simulated money
System Status: ONLINE_AUTONOMOUS      ← System is running & autonomous
                                         (POWERED_OFF = nothing runs)
                                         (PAUSED = online but waiting)

BROKERS:
  oanda      ✓ ON - online_autonomous   ← Trading on Oanda
  ibkr       ✓ ON - online_autonomous   ← Trading on IBKR
  coinbase   ✗ OFF - powered_off        ← Not trading on Coinbase

HIVE MIND:
  Autonomous: ✓ YES                     ← Hive trades automatically
  Learning:   ✓ YES                     ← Hive learns from outcomes
  Dialogue:   ✓ YES                     ← You can communicate

RISK MANAGEMENT:
  Max Drawdown: 5%                      ← Stop if down 5%
  Max Position: 5%                      ← Max 5% per trade
  Daily Loss Limit: Unlimited           ← No daily stop
============================================================
```

---

## 🚨 STATUS MEANINGS

| Status | Meaning | Trading? | What It Does |
|--------|---------|----------|--------------|
| `ONLINE_AUTONOMOUS` | 100% online, trading now | YES | Hive trades automatically |
| `PAUSED` | Online but waiting | NO | System ready, hive waits for approval |
| `POWERED_OFF` | System completely off | NO | Nothing runs, system silent |

| Broker Status | Meaning |
|---------------|---------|
| `✓ ON - online_autonomous` | This broker is trading right now |
| `✓ ON - powered_off` | Broker enabled but system is off |
| `✗ OFF - powered_off` | Broker is disabled |

| Hive Setting | Meaning |
|--------------|---------|
| `Autonomous: ✓ YES` | Hive makes final decisions automatically |
| `Autonomous: ✗ NO` | Hive suggests, you approve each trade |
| `Learning: ✓ YES` | Closed-loop feedback active, system learning |
| `Learning: ✗ NO` | No learning, just executing |
| `Dialogue: ✓ YES` | You can query/command the hive |
| `Dialogue: ✗ NO` | System silent |

---

## 🎯 QUICK DECISION MATRIX

**Q: I want to test the system safely**
```
mgr.set_paper_practice_mode()
mgr.activate_broker("oanda")
mgr.power_on_autonomous()
mgr.enable_hive_autonomous()
→ Safe paper trading with hive
```

**Q: I want hive to suggest, I'll approve**
```
mgr.set_paper_real_time_mode()
mgr.pause_system()
mgr.disable_hive_autonomous()
→ Hive analyzes, you decide
```

**Q: I'm ready for real money**
```
mgr.set_live_real_money_mode()
mgr.activate_broker_autonomous("oanda")
mgr.power_on_autonomous()
→ Live trading begins
```

**Q: Emergency - stop everything**
```
mgr.power_off()
→ All trading stops immediately
```

**Q: I want to use only Oanda and Coinbase**
```
mgr.activate_broker("oanda")
mgr.activate_broker("coinbase")
mgr.deactivate_broker("ibkr")
mgr.save()
→ Only those brokers active
```

**Q: I want system to learn from trades**
```
mgr.enable_hive_learning()
→ Closed-loop feedback ON
```

**Q: How do I know what's active?**
```
mgr.print_status()
→ See everything at a glance
```

---

## 📁 CONFIG FILE LOCATION

Your configuration is saved to:
```
/home/ing/RICK/new_RLC_rebuild/config/task_config.json
```

View it anytime:
```bash
cat /home/ing/RICK/new_RLC_rebuild/config/task_config.json | jq .
```

Edit it manually if needed:
```bash
nano /home/ing/RICK/new_RLC_rebuild/config/task_config.json
```

Reload in Python:
```python
from config.task_config import TaskConfigManager
mgr = TaskConfigManager()  # Automatically loads latest from file
```

---

## ✨ PRO TIPS

1. **Always check status before trading**
   ```python
   mgr.print_status()  # Verify everything correct first
   ```

2. **Save config after changes**
   ```python
   mgr.save()  # Persists to file
   ```

3. **Use dictionaries for scripts**
   ```python
   status = mgr.get_status_dict()  # Easier to parse in automation
   ```

4. **Test paper trading first**
   ```python
   # Always run 100+ paper trades before live
   mgr.set_paper_practice_mode()
   ```

5. **Keep learning enabled in production**
   ```python
   mgr.enable_hive_learning()  # System improves over time
   ```

6. **Monitor the learning database**
   ```bash
   # Check if system is learning
   ls -lh hive/rick_learning.db
   # Growing file = learning happening
   ```

7. **Use task config in your scripts**
   ```python
   # In any script:
   from config.task_config import TaskConfigManager
   mgr = TaskConfigManager()
   if mgr.config.system_status.value == "online_autonomous":
       print("System is trading!")
   ```

---

## 🔗 RELATED DOCUMENTATION

- Full Architecture: `RICK_HIVE_ARCHITECTURE.md`
- Pre-Launch Checklist: `PRE_LAUNCH_CHECKLIST.md`
- Hive Mind Explained: `HIVE_MIND_EXPLAINED.md`
- 130 Features: `RICK_130_FEATURES_ANALYSIS.md`

---

## 🚀 YOU'RE READY TO:

✅ Switch between Paper and Live trading
✅ Select which brokers to use
✅ Control hive autonomy
✅ Enable/disable learning
✅ Monitor system status
✅ Launch paper trading immediately
✅ Transition to live trading safely
✅ Maintain open communication with hive

**Next step: Configure API keys and run your first trade!**

