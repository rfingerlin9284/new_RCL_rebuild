"""
RICK Configuration Template
Master configuration for all 130 features
"""

import os
from pathlib import Path

# Core Settings
PROJECT_NAME = "RICK Live Clean Rebuild"
VERSION = "3.0.0"
PROJECT_ROOT = Path(__file__).parent.absolute()

# Feature Configuration
FEATURES_ENABLED = {
    # Trading Engines (15)
    "oanda_engine": True,
    "coinbase_engine": True,
    "ibkr_engine": True,
    "multi_broker_engine": True,
    "ghost_engine": True,
    "canary_engine": True,
    "paper_engine": True,
    "live_engine": True,
    "enhanced_rick_engine": True,
    "safe_trading_engine": True,
    "stochastic_engine": True,
    "advanced_strategy_engine": True,
    "wolf_engine": True,
    "live_ghost_engine": True,
    "base_engine": True,
    
    # Risk Management (12)
    "capital_manager": True,
    "charter_compliance": True,
    "pin_protection": True,
    "safe_mode_manager": True,
    "position_guardian": True,
    "risk_analyzer": True,
    "emergency_ops": True,
    "charter_amendment": True,
    "governance_lock": True,
    "trade_gate": True,
    "currency_audit": True,
    "safety_verifier": True,
    
    # ML/AI (10)
    "ml_learning": True,
    "pattern_matcher": True,
    "ml_models": True,
    "optimizer": True,
    "pattern_learner": True,
    "hive_mind": True,
    "swarm_coordinator": True,
    "regime_detector": True,
    "smart_logic": True,
    "intelligence_extractor": True,
    
    # Monitoring (18)
    "live_monitor": True,
    "dashboard": True,
    "status_reporter": True,
    "performance_analyzer": True,
    "trade_analyzer": True,
    "opportunity_analyzer": True,
    "health_checker": True,
    "endpoint_monitor": True,
    "data_diagnostics": True,
    "system_dashboard": True,
    "monitoring_setup": True,
    "continuous_monitor": True,
    "daily_auditor": True,
    "auto_diagnostics": True,
    "checkpoint_monitor": True,
    "narration_system": True,
    "session_reporter": True,
    "frontend_integration": True,
    
    # Strategies (15)
    "strategy_architecture": True,
    "parameter_manager": True,
    "momentum_trailing": True,
    "ema_scalper": True,
    "crypto_optimizer": True,
    "currency_strategy": True,
    "winrate_optimizer": True,
    "strategy_verifier": True,
    "wolfpack_strategy": True,
    "golden_age": True,
    "unified_strategy": True,
    "strategy_auditor": True,
    "pattern_trading": True,
    "timeframe_analyzer": True,
    "regime_adaptive": True,
    
    # Data (12)
    "historical_api": True,
    "live_data": True,
    "futures_data": True,
    "forex_connector": True,
    "crypto_data": True,
    "data_permissions": True,
    "data_verifier": True,
    "broker_connectors": True,
    "endpoint_manager": True,
    "data_cache": True,
    "candle_parser": True,
    "symbol_verifier": True,
    
    # Deployment (13)
    "docker_deploy": True,
    "wsl_integration": True,
    "env_manager": True,
    "service_installer": True,
    "ib_gateway_setup": True,
    "paper_validator": True,
    "live_activator": True,
    "backup_system": True,
    "rollback_manager": True,
    "update_manager": True,
    "permission_manager": True,
    "launch_scripts": True,
    "control_plane": True,
    
    # UI (8)
    "streamlit_dashboard": True,
    "interactive_menu": True,
    "terminal_integration": True,
    "progress_tracker": True,
    "session_manager": True,
    "config_guide": True,
    "quick_start": True,
    "documentation": True,
    
    # Testing (12)
    "integration_test": True,
    "auth_test": True,
    "data_test": True,
    "endpoint_test": True,
    "ghost_test": True,
    "fixes_test": True,
    "performance_test": True,
    "safety_test": True,
    "broker_test": True,
    "historical_test": True,
    "parameter_test": True,
    "system_test": True,
    
    # Advanced (15)
    "institutional_charter": True,
    "openalgo_integration": True,
    "multi_window_dash": True,
    "sentiment_mode": True,
    "advanced_algos": True,
    "charter_amendments": True,
    "immutable_tasks": True,
    "code_protection": True,
    "agent_governance": True,
    "narration_ai": True,
    "frontend_snapshot": True,
    "max_performance": True,
    "comprehensive_audit": True,
    "executive_verification": True,
    "mission_accomplished": True
}

# Broker Configuration
BROKERS = {
    "oanda": {
        "enabled": True,
        "api_type": "REST",
        "live_url": "https://api-fxpractice.oanda.com",
        "modes": ["paper", "live"]
    },
    "coinbase": {
        "enabled": True,
        "api_type": "REST/WebSocket",
        "live_url": "https://api.exchange.coinbase.com",
        "modes": ["paper", "live"]
    },
    "ibkr": {
        "enabled": True,
        "api_type": "TWS Gateway",
        "live_url": "localhost:7497",
        "modes": ["paper", "live"]
    }
}

# Trading Modes
MODES = {
    "paper": {
        "enabled": True,
        "description": "Risk-free paper trading simulation"
    },
    "canary": {
        "enabled": True,
        "description": "Limited live testing with restrictions"
    },
    "ghost": {
        "enabled": True,
        "description": "Simulation with real market data"
    },
    "live": {
        "enabled": True,
        "description": "Full production trading execution"
    }
}

# Safety Configuration
SAFETY = {
    "charter_enforcement": True,
    "position_limit": 10,
    "max_drawdown": 0.15,
    "emergency_stop": True,
    "real_time_monitoring": True
}

# Logging Configuration
LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.path.join(PROJECT_ROOT, "logs", "rick.log"),
    "max_bytes": 10485760,  # 10MB
    "backup_count": 5
}

# Database Configuration
DATABASE = {
    "type": "sqlite",
    "path": os.path.join(PROJECT_ROOT, "data", "rick.db")
}

# API Configuration
API = {
    "timeout": 30,
    "retries": 3,
    "rate_limit": 100
}

# Monitoring Configuration
MONITORING = {
    "enabled": True,
    "interval": 60,
    "dashboard_port": 8501,
    "metrics_enabled": True
}

def get_enabled_features():
    """Get list of all enabled features"""
    return [key for key, value in FEATURES_ENABLED.items() if value]

def get_feature_count():
    """Get total count of enabled features"""
    return sum(1 for value in FEATURES_ENABLED.values() if value)

if __name__ == "__main__":
    print(f"Configuration loaded for {PROJECT_NAME} v{VERSION}")
    print(f"Enabled features: {get_feature_count()}")
    print(f"Brokers: {', '.join(BROKERS.keys())}")
    print(f"Trading modes: {', '.join(MODES.keys())}")
