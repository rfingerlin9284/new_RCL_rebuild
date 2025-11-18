import random
from risk.dynamic_leverage import DynamicLeverageCalculator


def test_calculate_for_signal_basic():
    dlc = DynamicLeverageCalculator(max_leverage=10.0, base_risk_per_trade=0.01)
    # generate synthetic price history
    price_history = [1.1000 + (i * 0.0001) + random.uniform(-0.00005, 0.00005) for i in range(60)]
    res = dlc.calculate_for_signal("EUR_USD", confidence=0.9, price_history=price_history, account_balance=25000.0, current_positions=0)
    assert hasattr(res, 'position_size') or isinstance(res, dict)
    # If dict path, inspect values
    if isinstance(res, dict):
        assert res.get("position_size", 0) >= 1.0
        assert 1.0 <= res.get("leverage", 1.0) <= 10.0
        assert res.get("volatility", 0) >= 0.01
