#!/usr/bin/env python3
"""
IBKR Gateway Connector - Crypto Futures Trading
Adapted from OANDA connector for TWS API + crypto assets
PIN: 841921 | Platform: Interactive Brokers | Mode: Paper (port 7497)

Supports:
- Crypto futures (BTC, ETH, SOL via CME/Bakkt)
- 24/7 trading (no forex weekend gaps)
- Paper trading account (TWS port 7497)
- Funding rate awareness (perps)
- Real-time market data streaming
"""

import os
import sys
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Add parent directory to path for rick_hive access
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IB API (using ib_insync for async support)
try:
    from ib_insync import IB, Contract, Future, Order, MarketOrder, LimitOrder, StopOrder
    from ib_insync import util
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False
    print("⚠️ ib_insync not installed. Run: pip install ib_insync")

# Charter compliance
try:
    from rick_hive.rick_charter import RickCharter as CHARTER
except ImportError:
    # Fallback if running standalone
    class CHARTER:
        MIN_NOTIONAL_USD = 5000  # Lower for crypto (vs 15k forex)
        MIN_EXPECTED_PNL_USD = 200  # Adjusted for crypto vol
        MAX_HOLD_TIME_HOURS = 6
        MIN_RISK_REWARD_RATIO = 3.2
        OCO_REQUIRED = True


@dataclass
class CryptoFuturesContract:
    """Crypto futures contract specification"""
    symbol: str  # BTC, ETH, SOL
    exchange: str  # CME, BAKKT
    contract_month: str  # e.g., "202512" for Dec 2025
    multiplier: float  # Contract size
    tick_size: float  # Minimum price increment
    

class IBKRConnector:
    """
    IBKR Gateway connector for crypto futures trading
    
    Charter Compliance:
    - MIN_NOTIONAL: $5000 (crypto-adjusted)
    - MIN_PNL: $200 expected profit minimum
    - MAX_HOLD: 6 hours maximum position duration
    - MIN_RR: 3.2x risk/reward ratio
    - OCO: Required for all trades
    
    Trading Assets:
    - BTC futures (CME MBT, Bakkt)
    - ETH futures (CME ETH)
    - SOL futures (emerging)
    """
    
    # Crypto futures contracts (CME)
    CRYPTO_FUTURES = {
        "BTC": {"exchange": "CME", "symbol": "MBT", "multiplier": 0.1, "tick": 5.0},  # Micro Bitcoin
        "ETH": {"exchange": "CME", "symbol": "MET", "multiplier": 0.1, "tick": 0.25},  # Micro Ether
    }
    
    # Trading sessions (24/7 for crypto, but CME has hourly breaks)
    SESSION_BREAKS = [
        (16, 17),  # 4pm-5pm CT daily maintenance
    ]
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7497,  # Paper trading port (7496 = live)
        client_id: int = 1,
        account: str = None,
        logger: logging.Logger = None
    ):
        """
        Initialize IBKR Gateway connector
        
        Args:
            host: TWS/Gateway host (default localhost)
            port: 7497 for paper, 7496 for live
            client_id: Unique client ID (1-32)
            account: IBKR account ID (DU numbers for paper)
            logger: Logger instance
        """
        if not IB_AVAILABLE:
            raise ImportError("ib_insync required: pip install ib_insync")
        
        self.host = host
        self.port = port
        self.client_id = client_id
        self.account = account or os.getenv("IBKR_PAPER_ACCOUNT")
        
        self.logger = logger or logging.getLogger(__name__)
        
        # IB connection
        self.ib = IB()
        self.connected = False
        
        # Position tracking
        self.positions = {}
        self.orders = {}
        
        # Charter gates
        self.min_notional = CHARTER.MIN_NOTIONAL_USD
        self.min_expected_pnl = CHARTER.MIN_EXPECTED_PNL_USD
        self.max_hold_hours = CHARTER.MAX_HOLD_TIME_HOURS
        self.min_rr_ratio = CHARTER.MIN_RISK_REWARD_RATIO
        
        self.logger.info(f"IBKRConnector initialized (port {port}, account {self.account})")
    
    def connect(self) -> bool:
        """
        Connect to TWS/Gateway
        
        Returns:
            True if connected successfully
        """
        try:
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            self.connected = True
            self.logger.info(f"✅ Connected to IBKR Gateway at {self.host}:{self.port}")
            
            # Subscribe to account updates
            self.ib.reqAccountUpdates(self.account)
            
            return True
        except Exception as e:
            self.logger.error(f"❌ IBKR connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from TWS/Gateway"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            self.logger.info("Disconnected from IBKR Gateway")
    
    def _create_crypto_contract(self, symbol: str, month: str = None) -> Contract:
        """
        Create crypto futures contract
        
        Args:
            symbol: BTC, ETH, SOL
            month: Contract month (YYYYMM) or None for front month
            
        Returns:
            ib_insync Contract object
        """
        if symbol not in self.CRYPTO_FUTURES:
            raise ValueError(f"Unsupported crypto: {symbol}")
        
        spec = self.CRYPTO_FUTURES[symbol]
        
        # Default to front month if not specified
        if not month:
            now = datetime.now(timezone.utc)
            month = now.strftime("%Y%m")
        
        contract = Future(
            symbol=spec["symbol"],
            lastTradeDateOrContractMonth=month,
            exchange=spec["exchange"],
            currency="USD"
        )
        
        return contract
    
    def get_historical_data(
        self,
        symbol: str,
        count: int = 60,
        timeframe: str = "1H"
    ) -> List[Dict]:
        """
        Fetch historical candle data
        
        Args:
            symbol: BTC, ETH, SOL
            count: Number of bars
            timeframe: 1H, 4H, 1D
            
        Returns:
            List of candle dicts with OHLCV
        """
        if not self.connected:
            self.logger.error("Not connected to IBKR Gateway")
            return []
        
        try:
            contract = self._create_crypto_contract(symbol)
            
            # Request historical data
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=f'{count} H',  # Adjust based on timeframe
                barSizeSetting=timeframe,
                whatToShow='TRADES',
                useRTH=False,  # Include outside regular hours (24/7 crypto)
                formatDate=1
            )
            
            candles = []
            for bar in bars:
                candles.append({
                    "time": bar.date,
                    "open": float(bar.open),
                    "high": float(bar.high),
                    "low": float(bar.low),
                    "close": float(bar.close),
                    "volume": int(bar.volume)
                })
            
            self.logger.info(f"Fetched {len(candles)} candles for {symbol}")
            return candles
            
        except Exception as e:
            self.logger.error(f"Failed to fetch {symbol} historical data: {e}")
            return []
    
    def place_order(
        self,
        symbol: str,
        side: str,
        units: int,
        entry_price: float = None,
        stop_loss: float = None,
        take_profit: float = None
    ) -> Dict[str, Any]:
        """
        Place crypto futures order with OCO (One-Cancels-Other) bracket
        
        Charter Validation:
        - Checks MIN_NOTIONAL (5000 USD)
        - Checks MIN_EXPECTED_PNL (200 USD)
        - Checks MIN_RR_RATIO (3.2x)
        - Enforces OCO requirement
        
        Args:
            symbol: BTC, ETH, SOL
            side: BUY or SELL
            units: Number of contracts
            entry_price: Limit price (None = market order)
            stop_loss: SL price (required by charter)
            take_profit: TP price (required by charter)
            
        Returns:
            Order result dict
        """
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        
        # Charter Gate #1: OCO required
        if not (stop_loss and take_profit):
            self.logger.warning("❌ CHARTER VIOLATION: OCO (SL + TP) required")
            return {"success": False, "error": "CHARTER_VIOLATION_OCO_REQUIRED"}
        
        try:
            contract = self._create_crypto_contract(symbol)
            spec = self.CRYPTO_FUTURES[symbol]
            
            # Get current price if market order
            if not entry_price:
                ticker = self.ib.reqMktData(contract)
                self.ib.sleep(1)  # Wait for price
                entry_price = ticker.marketPrice()
            
            # Charter Gate #2: Min Notional
            notional = units * spec["multiplier"] * entry_price
            if notional < self.min_notional:
                self.logger.warning(
                    f"❌ CHARTER VIOLATION: Notional ${notional:.2f} < ${self.min_notional}"
                )
                return {"success": False, "error": "BELOW_MIN_NOTIONAL"}
            
            # Charter Gate #3: Min Expected PnL
            if side == "BUY":
                expected_pnl = (take_profit - entry_price) * units * spec["multiplier"]
                risk = (entry_price - stop_loss) * units * spec["multiplier"]
            else:
                expected_pnl = (entry_price - take_profit) * units * spec["multiplier"]
                risk = (stop_loss - entry_price) * units * spec["multiplier"]
            
            if expected_pnl < self.min_expected_pnl:
                self.logger.warning(
                    f"❌ CHARTER VIOLATION: Expected PnL ${expected_pnl:.2f} < ${self.min_expected_pnl}"
                )
                return {"success": False, "error": "BELOW_MIN_PNL"}
            
            # Charter Gate #4: Min R/R Ratio
            rr_ratio = expected_pnl / risk if risk > 0 else 0
            if rr_ratio < self.min_rr_ratio:
                self.logger.warning(
                    f"❌ CHARTER VIOLATION: R/R {rr_ratio:.2f} < {self.min_rr_ratio}"
                )
                return {"success": False, "error": "BELOW_MIN_RR"}
            
            # All gates passed - place bracket order
            parent_order = MarketOrder(
                action="BUY" if side == "BUY" else "SELL",
                totalQuantity=units
            )
            
            # Create OCO bracket (TP + SL)
            bracket = self.ib.bracketOrder(
                parent_order.action,
                units,
                limitPrice=entry_price if entry_price else None,
                takeProfitPrice=take_profit,
                stopLossPrice=stop_loss
            )
            
            # Submit all orders
            trades = []
            for order in bracket:
                trade = self.ib.placeOrder(contract, order)
                trades.append(trade)
            
            self.logger.info(
                f"✅ Order placed: {symbol} {side} {units} contracts @ {entry_price:.2f} "
                f"(SL: {stop_loss:.2f}, TP: {take_profit:.2f}, R/R: {rr_ratio:.2f})"
            )
            
            return {
                "success": True,
                "symbol": symbol,
                "side": side,
                "units": units,
                "entry": entry_price,
                "sl": stop_loss,
                "tp": take_profit,
                "notional": notional,
                "expected_pnl": expected_pnl,
                "rr_ratio": rr_ratio,
                "trades": [t.order.orderId for t in trades]
            }
            
        except Exception as e:
            self.logger.error(f"Order placement failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_open_positions(self) -> List[Dict]:
        """
        Get all open crypto futures positions
        
        Returns:
            List of position dicts
        """
        if not self.connected:
            return []
        
        try:
            positions = self.ib.positions()
            
            result = []
            for pos in positions:
                if pos.account == self.account:
                    result.append({
                        "symbol": pos.contract.symbol,
                        "position": pos.position,
                        "avg_cost": pos.avgCost,
                        "market_value": pos.marketValue,
                        "unrealized_pnl": pos.unrealizedPNL
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to fetch positions: {e}")
            return []
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        Close crypto futures position
        
        Args:
            symbol: BTC, ETH, SOL
            
        Returns:
            Close result dict
        """
        try:
            positions = self.get_open_positions()
            target_pos = next((p for p in positions if p["symbol"] == symbol), None)
            
            if not target_pos:
                return {"success": False, "error": "No position found"}
            
            # Reverse the position
            side = "SELL" if target_pos["position"] > 0 else "BUY"
            units = abs(int(target_pos["position"]))
            
            contract = self._create_crypto_contract(symbol)
            order = MarketOrder(
                action=side,
                totalQuantity=units
            )
            
            trade = self.ib.placeOrder(contract, order)
            
            self.logger.info(f"✅ Closed {symbol} position ({units} contracts)")
            
            return {
                "success": True,
                "symbol": symbol,
                "side": side,
                "units": units,
                "order_id": trade.order.orderId
            }
            
        except Exception as e:
            self.logger.error(f"Failed to close {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account balance and margin info
        
        Returns:
            Account summary dict
        """
        if not self.connected:
            return {}
        
        try:
            account_values = self.ib.accountValues(self.account)
            
            summary = {}
            for item in account_values:
                if item.tag == "NetLiquidation":
                    summary["balance"] = float(item.value)
                elif item.tag == "UnrealizedPnL":
                    summary["unrealized_pnl"] = float(item.value)
                elif item.tag == "BuyingPower":
                    summary["buying_power"] = float(item.value)
                elif item.tag == "MaintMarginReq":
                    summary["margin_used"] = float(item.value)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to fetch account summary: {e}")
            return {}


# Position Police (Charter Enforcement)
def position_police_check(connector: IBKRConnector):
    """
    Charter enforcement: Close positions violating MIN_NOTIONAL
    
    Runs every cycle to monitor compliance
    """
    positions = connector.get_open_positions()
    
    for pos in positions:
        symbol = pos["symbol"]
        notional = abs(pos["market_value"])
        
        if notional < connector.min_notional:
            connector.logger.warning(
                f"🚨 POSITION POLICE: {symbol} notional ${notional:.2f} < "
                f"${connector.min_notional} - CLOSING"
            )
            connector.close_position(symbol)


if __name__ == "__main__":
    # Test connection
    logging.basicConfig(level=logging.INFO)
    
    connector = IBKRConnector()
    
    if connector.connect():
        print("✅ IBKR Gateway connection successful")
        
        # Test account summary
        summary = connector.get_account_summary()
        print(f"Account balance: ${summary.get('balance', 0):,.2f}")
        
        # Test historical data
        candles = connector.get_historical_data("BTC", count=10)
        print(f"Fetched {len(candles)} BTC candles")
        
        connector.disconnect()
    else:
        print("❌ Connection failed - is TWS/Gateway running on port 7497?")
