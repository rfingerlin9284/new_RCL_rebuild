"""
RICK TASK CONFIGURATION SYSTEM
================================
Unified control panel for RICK trading modes and platform selection.
Allows real-time switching between live/paper modes and platform activation.
"""

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime


class TradingMode(Enum):
    """Trading execution modes"""
    LIVE_REAL_MONEY = "live_real_money"  # Real accounts, real money
    PAPER_PRACTICE = "paper_practice"     # Paper accounts, simulated money
    PAPER_REAL_TIME = "paper_real_time"   # Paper with real market data


class SystemStatus(Enum):
    """System operational status"""
    ONLINE_AUTONOMOUS = "online_autonomous"      # 100% online, trading autonomously
    POWERED_OFF = "powered_off"                   # System offline, no trading
    PAUSED = "paused"                             # Online but paused, awaiting command


class BrokerPlatform(Enum):
    """Supported broker platforms"""
    OANDA = "oanda"
    IBKR = "ibkr"  # Interactive Brokers
    COINBASE = "coinbase"


@dataclass
class BrokerConfig:
    """Configuration for a single broker platform"""
    platform: BrokerPlatform
    enabled: bool = True
    status: SystemStatus = SystemStatus.POWERED_OFF
    live_account_id: Optional[str] = None
    paper_account_id: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    
    def to_dict(self):
        return {
            "platform": self.platform.value,
            "enabled": self.enabled,
            "status": self.status.value,
            "live_account_id": self.live_account_id,
            "paper_account_id": self.paper_account_id,
            "has_api_key": bool(self.api_key),
            "has_api_secret": bool(self.api_secret),
        }


@dataclass
class TaskConfig:
    """
    Master task configuration for RICK system.
    Controls trading mode, platform activation, and system status.
    """
    # TRADING MODE SELECTION
    trading_mode: TradingMode = TradingMode.PAPER_PRACTICE
    
    # SYSTEM STATUS
    system_status: SystemStatus = SystemStatus.POWERED_OFF
    
    # BROKER PLATFORM CONFIGURATIONS
    brokers: Dict[str, BrokerConfig] = field(default_factory=lambda: {
        "oanda": BrokerConfig(
            platform=BrokerPlatform.OANDA,
            enabled=True,
            status=SystemStatus.POWERED_OFF
        ),
        "ibkr": BrokerConfig(
            platform=BrokerPlatform.IBKR,
            enabled=True,
            status=SystemStatus.POWERED_OFF
        ),
        "coinbase": BrokerConfig(
            platform=BrokerPlatform.COINBASE,
            enabled=True,
            status=SystemStatus.POWERED_OFF
        ),
    })
    
    # HIVE MIND SETTINGS
    hive_autonomous: bool = True  # Hive runs autonomously
    hive_learning_active: bool = True  # Closed-loop feedback active
    hive_consensus_threshold: float = 0.70  # 70% consensus required
    hive_dialogue_on: bool = True  # Open dialogue with developmental environment
    
    # RISK MANAGEMENT
    max_drawdown_percent: float = 5.0  # Max 5% drawdown
    max_position_size_percent: float = 5.0  # Max 5% per trade
    daily_loss_limit: Optional[float] = None  # In account currency
    
    # LAST MODIFIED
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified_by: str = "system"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "trading_mode": self.trading_mode.value,
            "system_status": self.system_status.value,
            "brokers": {k: v.to_dict() for k, v in self.brokers.items()},
            "hive_autonomous": self.hive_autonomous,
            "hive_learning_active": self.hive_learning_active,
            "hive_consensus_threshold": self.hive_consensus_threshold,
            "hive_dialogue_on": self.hive_dialogue_on,
            "max_drawdown_percent": self.max_drawdown_percent,
            "max_position_size_percent": self.max_position_size_percent,
            "daily_loss_limit": self.daily_loss_limit,
            "last_modified": self.last_modified,
            "last_modified_by": self.last_modified_by,
        }
    
    def save_to_file(self, filepath: str = "task_config.json"):
        """Save configuration to JSON file"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"✓ Task config saved to {filepath}")
        return filepath
    
    @classmethod
    def load_from_file(cls, filepath: str = "task_config.json"):
        """Load configuration from JSON file"""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            # Reconstruct broker configs
            brokers = {}
            for broker_key, broker_data in data.get("brokers", {}).items():
                platform = BrokerPlatform[broker_data["platform"].upper()]
                brokers[broker_key] = BrokerConfig(
                    platform=platform,
                    enabled=broker_data.get("enabled", True),
                    status=SystemStatus(broker_data.get("status", "powered_off")),
                    live_account_id=broker_data.get("live_account_id"),
                    paper_account_id=broker_data.get("paper_account_id"),
                )
            
            return cls(
                trading_mode=TradingMode(data.get("trading_mode", "paper_practice")),
                system_status=SystemStatus(data.get("system_status", "powered_off")),
                brokers=brokers,
                hive_autonomous=data.get("hive_autonomous", True),
                hive_learning_active=data.get("hive_learning_active", True),
                hive_consensus_threshold=data.get("hive_consensus_threshold", 0.70),
                hive_dialogue_on=data.get("hive_dialogue_on", True),
                max_drawdown_percent=data.get("max_drawdown_percent", 5.0),
                max_position_size_percent=data.get("max_position_size_percent", 5.0),
                daily_loss_limit=data.get("daily_loss_limit"),
            )
        except FileNotFoundError:
            print(f"⚠ Config file {filepath} not found, using defaults")
            return cls()


class TaskConfigManager:
    """
    Manager for runtime task configuration.
    Allows dynamic mode/platform switching without restart.
    """
    
    def __init__(self, config_path: str = "task_config.json"):
        self.config_path = config_path
        self.config = TaskConfig.load_from_file(config_path)
    
    # ============ TRADING MODE COMMANDS ============
    
    def set_paper_practice_mode(self):
        """Switch to paper trading with simulated money"""
        self.config.trading_mode = TradingMode.PAPER_PRACTICE
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ Mode set to PAPER PRACTICE (simulated money)")
        return self.config
    
    def set_paper_real_time_mode(self):
        """Switch to paper trading with real market data"""
        self.config.trading_mode = TradingMode.PAPER_REAL_TIME
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ Mode set to PAPER REAL-TIME (real data, simulated money)")
        return self.config
    
    def set_live_real_money_mode(self):
        """Switch to live trading with real money (USE WITH CAUTION)"""
        self.config.trading_mode = TradingMode.LIVE_REAL_MONEY
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("⚠ Mode set to LIVE REAL MONEY - TRADING LIVE FUNDS")
        return self.config
    
    # ============ SYSTEM STATUS COMMANDS ============
    
    def power_on_autonomous(self):
        """Power on system to trade autonomously (100% online)"""
        self.config.system_status = SystemStatus.ONLINE_AUTONOMOUS
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ System ONLINE & AUTONOMOUS - Trading enabled")
        return self.config
    
    def power_off(self):
        """Power off system completely (no trading)"""
        self.config.system_status = SystemStatus.POWERED_OFF
        # Also power off all brokers
        for broker in self.config.brokers.values():
            broker.status = SystemStatus.POWERED_OFF
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ System POWERED OFF - No trading will occur")
        return self.config
    
    def pause_system(self):
        """Pause system (online but waiting for commands)"""
        self.config.system_status = SystemStatus.PAUSED
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ System PAUSED - Online but awaiting commands")
        return self.config
    
    # ============ BROKER PLATFORM COMMANDS ============
    
    def activate_broker(self, broker_name: str):
        """Activate a specific broker platform"""
        if broker_name not in self.config.brokers:
            print(f"✗ Unknown broker: {broker_name}")
            return None
        
        broker = self.config.brokers[broker_name]
        broker.enabled = True
        broker.status = SystemStatus.ONLINE_AUTONOMOUS if self.config.system_status == SystemStatus.ONLINE_AUTONOMOUS else SystemStatus.POWERED_OFF
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print(f"✓ {broker_name.upper()} activated")
        return broker
    
    def deactivate_broker(self, broker_name: str):
        """Deactivate a specific broker platform"""
        if broker_name not in self.config.brokers:
            print(f"✗ Unknown broker: {broker_name}")
            return None
        
        broker = self.config.brokers[broker_name]
        broker.enabled = False
        broker.status = SystemStatus.POWERED_OFF
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print(f"✓ {broker_name.upper()} deactivated")
        return broker
    
    def activate_broker_autonomous(self, broker_name: str):
        """Activate broker and set to autonomous trading"""
        if broker_name not in self.config.brokers:
            print(f"✗ Unknown broker: {broker_name}")
            return None
        
        broker = self.config.brokers[broker_name]
        broker.enabled = True
        broker.status = SystemStatus.ONLINE_AUTONOMOUS
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print(f"✓ {broker_name.upper()} activated & AUTONOMOUS")
        return broker
    
    def get_active_brokers(self) -> List[str]:
        """Get list of currently active brokers"""
        return [name for name, broker in self.config.brokers.items() if broker.enabled]
    
    # ============ HIVE MIND COMMANDS ============
    
    def enable_hive_autonomous(self):
        """Enable autonomous hive mind trading"""
        self.config.hive_autonomous = True
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ Hive Mind AUTONOMOUS mode enabled")
        return self.config
    
    def disable_hive_autonomous(self):
        """Disable autonomous hive mind (require manual approval)"""
        self.config.hive_autonomous = False
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ Hive Mind MANUAL approval mode enabled")
        return self.config
    
    def enable_hive_learning(self):
        """Enable hive closed-loop learning"""
        self.config.hive_learning_active = True
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ Hive Mind LEARNING enabled (closed-loop feedback)")
        return self.config
    
    def disable_hive_learning(self):
        """Disable hive closed-loop learning"""
        self.config.hive_learning_active = False
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ Hive Mind LEARNING disabled")
        return self.config
    
    def enable_hive_dialogue(self):
        """Enable hive open dialogue (always on, responds to dev environment)"""
        self.config.hive_dialogue_on = True
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ Hive Mind DIALOGUE enabled (open communication)")
        return self.config
    
    def disable_hive_dialogue(self):
        """Disable hive open dialogue"""
        self.config.hive_dialogue_on = False
        self.config.last_modified = datetime.now().isoformat()
        self.config.last_modified_by = "task_manager"
        self.save()
        print("✓ Hive Mind DIALOGUE disabled")
        return self.config
    
    # ============ CONFIGURATION MANAGEMENT ============
    
    def save(self):
        """Save current configuration"""
        self.config.save_to_file(self.config_path)
    
    def print_status(self):
        """Print current system status"""
        print("\n" + "="*60)
        print("RICK SYSTEM STATUS")
        print("="*60)
        print(f"Trading Mode: {self.config.trading_mode.value.upper()}")
        print(f"System Status: {self.config.system_status.value.upper()}")
        print()
        print("BROKERS:")
        for name, broker in self.config.brokers.items():
            status = "✓ ON" if broker.enabled else "✗ OFF"
            print(f"  {name.upper():10} {status} - {broker.status.value}")
        print()
        print("HIVE MIND:")
        print(f"  Autonomous: {'✓ YES' if self.config.hive_autonomous else '✗ NO'}")
        print(f"  Learning:   {'✓ YES' if self.config.hive_learning_active else '✗ NO'}")
        print(f"  Dialogue:   {'✓ YES' if self.config.hive_dialogue_on else '✗ NO'}")
        print()
        print("RISK MANAGEMENT:")
        print(f"  Max Drawdown: {self.config.max_drawdown_percent}%")
        print(f"  Max Position: {self.config.max_position_size_percent}%")
        print(f"  Daily Loss Limit: {self.config.daily_loss_limit or 'Unlimited'}")
        print("="*60 + "\n")
    
    def get_status_dict(self):
        """Get status as dictionary"""
        return {
            "trading_mode": self.config.trading_mode.value,
            "system_status": self.config.system_status.value,
            "active_brokers": self.get_active_brokers(),
            "hive": {
                "autonomous": self.config.hive_autonomous,
                "learning": self.config.hive_learning_active,
                "dialogue": self.config.hive_dialogue_on,
            },
            "timestamp": self.config.last_modified,
        }


# ============ QUICK START EXAMPLES ============

def example_paper_practice():
    """Example: Set up paper trading"""
    mgr = TaskConfigManager()
    mgr.set_paper_practice_mode()
    mgr.activate_broker("oanda")
    mgr.activate_broker("ibkr")
    mgr.power_on_autonomous()
    mgr.enable_hive_autonomous()
    mgr.enable_hive_dialogue()
    mgr.print_status()


def example_live_trading():
    """Example: Set up live trading (USE WITH CAUTION)"""
    mgr = TaskConfigManager()
    mgr.set_live_real_money_mode()
    mgr.activate_broker_autonomous("oanda")
    mgr.power_on_autonomous()
    mgr.enable_hive_autonomous()
    mgr.enable_hive_learning()
    mgr.enable_hive_dialogue()
    mgr.print_status()


def example_custom_setup():
    """Example: Custom setup with specific brokers"""
    mgr = TaskConfigManager()
    mgr.set_paper_real_time_mode()
    
    # Activate only Oanda and Coinbase
    mgr.activate_broker("oanda")
    mgr.activate_broker("coinbase")
    mgr.deactivate_broker("ibkr")
    
    # Enable autonomous hive
    mgr.power_on_autonomous()
    mgr.enable_hive_autonomous()
    mgr.enable_hive_learning()
    mgr.enable_hive_dialogue()
    
    mgr.print_status()


if __name__ == "__main__":
    # Create default config file
    config = TaskConfig()
    config.save_to_file("/home/ing/RICK/new_RLC_rebuild/config/task_config.json")
    
    # Show example usage
    print("Task Config System created successfully!\n")
    print("To use in your code:")
    print("  from config.task_config import TaskConfigManager")
    print("  mgr = TaskConfigManager()")
    print("  mgr.set_paper_practice_mode()")
    print("  mgr.activate_broker('oanda')")
    print("  mgr.power_on_autonomous()")
    print("  mgr.print_status()")
