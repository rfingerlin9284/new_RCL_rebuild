from risk.smart_trailing import maybe_extend_take_profit, should_trail


def test_maybe_extend_take_profit_allows_extension_when_momentum_strong():
    entry = 1.1000
    tp = 1.1300
    sl = 1.0900
    td = maybe_extend_take_profit(entry, tp, sl, "buy", 0.9, 0.9)
    assert td.trailing_activated is True
    assert td.new_take_profit is not None
    assert td.reason == "SMART_TRAILING_EXTENDED_TP"


def test_should_trail_positive_case():
    position_state = {"unrealized_rr": 1.2, "time_in_minutes": 6.0, "side": "buy"}
    hive_signals = {"momentum_score": 0.85, "hive_consensus": 0.82, "regime": "momentum"}
    assert should_trail(position_state, hive_signals) is True


def test_should_trail_negative_case():
    position_state = {"unrealized_rr": 0.5, "time_in_minutes": 2.0, "side": "buy"}
    hive_signals = {"momentum_score": 0.6, "hive_consensus": 0.4, "regime": "sideways"}
    assert should_trail(position_state, hive_signals) is False
