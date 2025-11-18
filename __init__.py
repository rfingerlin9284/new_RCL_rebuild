"""
RICK Live Clean Rebuild - Main Module
All 130 features integrated and organized
"""

__version__ = "3.0.0"
__author__ = "RICK Development Team"
__description__ = "Advanced Multi-Broker Algorithmic Trading Platform"

from engines import *
from risk import *
from ml_ai import *
from monitoring import *
from strategies import *
from data import *
from deployment import *
from ui import *
from testing import *
from advanced import *

# Core configuration
CONFIG = {
    "version": __version__,
    "features": 130,
    "brokers": ["oanda", "coinbase", "ibkr"],
    "modes": ["paper", "canary", "ghost", "live"],
    "safety_level": "institutional"
}

# Feature registry
FEATURES = {
    "trading_engines": 15,
    "risk_management": 12,
    "ml_ai": 10,
    "monitoring": 18,
    "strategies": 15,
    "data_connectivity": 12,
    "deployment": 13,
    "user_interface": 8,
    "testing": 12,
    "advanced": 15
}

def get_feature_info(category):
    """Get information about features in a category"""
    return FEATURES.get(category, None)

def list_all_features():
    """List all 130 features"""
    total = sum(FEATURES.values())
    return {
        "total_features": total,
        "categories": FEATURES,
        "version": __version__
    }

if __name__ == "__main__":
    print(f"RICK Live Clean Rebuild v{__version__}")
    print(f"Features: {sum(FEATURES.values())}")
    print(f"Categories: {len(FEATURES)}")
