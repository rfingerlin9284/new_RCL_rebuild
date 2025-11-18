"""
Order Router
============
Unified manual execution entry that routes trades to the proper broker
connector, honoring paper/live via config, PIN 841921, and returning a
normalized result. On success, it also registers the position with the
`RealTimePositionManager` for monitoring.

This is used by terminal and web UIs to ensure manual actions use the same
execution pipeline as the autonomous engine would.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import json
import os

from foundation.rick_charter import RickCharter
from risk.dynamic_leverage import DynamicLeverageCalculator
from position_manager import get_position_manager


@dataclass
class ManualTrade:
    symbol: str
    direction: str  # "buy" | "sell"
    quantity: float
    broker: str  # "oanda" | "ibkr" (coinbase disabled in this build)
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    order_type: str = "market"  # market|limit|stop


def _load_active_mode() -> str:
    """Read active mode from config/PAPER_LIVE_CONFIG.json.
    Returns one of: "paper" | "live". Defaults to "paper" if missing.
    """
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config", "PAPER_LIVE_CONFIG.json")
    cfg_path = os.path.abspath(cfg_path)
    try:
        with open(cfg_path, "r") as f:
            data = json.load(f)
        mode = data.get("active_mode", "paper")
        if mode not in {"paper", "live"}:
            return "paper"
        return mode
    except Exception:
        return "paper"


def _env_for_broker(mode: str, broker: str) -> str:
    """Map unified mode to connector-specific environment labels.

    Coinbase is intentionally disabled for this build and never selected
    as an execution target.
    """
    if broker == "oanda":
        return "practice" if mode == "paper" else "live"
    if broker == "ibkr":
        return "paper" if mode == "paper" else "live"
    return mode


def _import_connector(broker: str):
    """Import and return the connector class for a broker with graceful fallbacks.

    Coinbase paper/live is intentionally disabled in this build per
    governance; attempts to route to it should be blocked before here.
    """
    # Preferred package path
    try:
        if broker == "oanda":
            from data.brokers.oanda_connector import OandaConnector  # type: ignore
            return OandaConnector
        if broker == "ibkr":
            from deployment.ibkr_gateway.ibkr_connector import IBKRConnector  # type: ignore
            return IBKRConnector
    except Exception:
        pass

    # Alternate legacy paths
    try:
        if broker == "oanda":
            from data.oanda.brokers.oanda_connector import OandaConnector  # type: ignore
            return OandaConnector
        if broker == "ibkr":
            from brokers.ib_connector import IBConnector  # type: ignore
            return IBConnector
    except Exception:
        pass

    raise ImportError(f"Connector not found for broker: {broker}")


def _normalize_symbol(broker: str, symbol: str) -> str:
    """Best-effort normalization for instrument naming per broker.
    Minimal and intentionally conservative; users can pass exact symbols.
    """
    s = symbol.strip().upper()
    if broker == "oanda":
        # Map common FX notation EURUSD -> EUR_USD
        if len(s) == 6 and s.isalpha():
            return f"{s[:3]}_{s[3:]}"
    return s


def place_trade(pin: int, trade: ManualTrade) -> Dict[str, Any]:
    """Route and execute a manual trade via the broker connector.

    Returns a dict:
      {"success": bool, "order_id": str|None, "price": float|None, "details": Any, "error": str|None}
    """
    if not RickCharter.validate_pin(pin):
        return {"success": False, "error": "Invalid PIN"}

    broker = trade.broker.lower()
    if broker == "coinbase":
        # Coinbase paper is disabled per charter; fail fast and narrate upstream.
        return {"success": False, "error": "Coinbase trading is disabled in this build"}
    mode = _load_active_mode()
    env = _env_for_broker(mode, broker)

    ConnectorCls = _import_connector(broker)

    # Instantiate connector; pass pin where supported, and environment if available.
    try:
        try:
            connector = ConnectorCls(pin=pin, environment=env)
        except TypeError:
            # Some connectors may not take environment
            connector = ConnectorCls(pin=pin)
    except Exception as e:
        return {"success": False, "error": f"Connector init failed: {e}"}

    symbol = _normalize_symbol(broker, trade.symbol)
    side = trade.direction.lower()
    qty = trade.quantity
    # If quantity is zero or negative, attempt to compute a recommended size via dynamic leverage
    if not qty or qty <= 0:
        try:
            dlc = DynamicLeverageCalculator()
            # Best-effort to get price history using PM; fallback to defaults
            from position_manager import get_position_manager
            pm = get_position_manager()
            price_history = pm.get_recent_prices(symbol, lookback=50) if hasattr(pm, 'get_recent_prices') else [1.0]
            rec = dlc.calculate_for_signal(symbol, confidence=0.7, price_history=price_history, account_balance=25000.0, current_positions=0)
            qty = rec.get('position_size', 1000)
        except Exception:
            qty = 1000
    entry = trade.entry_price
    sl = trade.stop_loss
    tp = trade.take_profit
    otype = trade.order_type.lower()

    # Try a capability matrix with graceful fallbacks
    result: Dict[str, Any] | None = None
    try:
        # Preferred generic interface used by autonomous engine
        if hasattr(connector, "place_order"):
            result = connector.place_order(
                symbol=symbol,
                action=side,
                size=qty,
                order_type=otype,
                entry=entry,
                stop_loss=sl,
                take_profit=tp,
            )
        # OCO convenience if explicitly supported and SL/TP available
        elif all(v is not None for v in (entry, sl, tp)) and hasattr(connector, "place_oco_order"):
            # Adapt parameter names for Coinbase vs potential FX connectors
            try:
                result = connector.place_oco_order(
                    product_id=symbol,
                    entry_price=float(entry),
                    stop_loss=float(sl),
                    take_profit=float(tp),
                    size=float(qty),
                    side=side,
                )
            except TypeError:
                # Fallback legacy signature
                result = connector.place_oco_order(
                    instrument=symbol,
                    entry_price=float(entry),
                    stop_loss=float(sl),
                    take_profit=float(tp),
                    units=int(qty),
                )
        # Minimal market order interface variants
        elif hasattr(connector, "market_order"):
            result = connector.market_order(symbol=symbol, side=side, size=qty)
        elif hasattr(connector, "create_order"):
            result = connector.create_order(symbol=symbol, side=side, size=qty, order_type=otype)
        else:
            return {"success": False, "error": "No known execution method on connector"}
    except Exception as e:
        return {"success": False, "error": f"Execution error: {e}"}

    # Normalize response
    success = False
    order_id: Optional[str] = None
    price: Optional[float] = None
    details: Any = result

    if isinstance(result, dict):
        # Common patterns across connectors
        success = bool(result.get("success") or result.get("status") in {"success", "ok", "filled", True})
        order_id = result.get("order_id") or result.get("id") or result.get("trade_id")
        price = result.get("price") or result.get("avg_price") or result.get("fill_price")
    else:
        # Unknown type; treat as success if truthy
        success = bool(result)

    if success:
        # Register with position manager for monitoring
        pm = get_position_manager()
        pm.add_position(
            symbol=symbol,
            direction=side,
            quantity=float(qty),
            entry_price=float(price or (entry or 0.0)),
            broker=broker,
            stop_loss=sl if sl is not None else None,
            take_profit=tp if tp is not None else None,
        )
        return {"success": True, "order_id": order_id, "price": price, "details": details}

    return {"success": False, "error": str(details.get("error") if isinstance(details, dict) else details)}
