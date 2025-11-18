#!/usr/bin/env python3
"""
IBKR Gateway Trading Engine - Crypto Futures Edition
Autonomous trading system for Bitcoin/Ethereum futures via TWS API

PIN: 841921 | Mode: Paper Trading (port 7497)
Charter Compliance: MIN_NOTIONAL=$5k, MIN_PNL=$200, MAX_HOLD=6h, MIN_RR=3.2x

Features:
- 24/7 crypto futures trading (BTC, ETH via CME)
- RICK Hive Mind integration
- Wolf Pack strategies (adapted for crypto)
- Funding rate awareness
- Session-aware (CME hourly breaks)
- Paper trading default (safe testing)
"""

import os
import sys
import time
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# Add parent for rick_hive access
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IBKR connector
from ibkr_connector import IBKRConnector, position_police_check

# RICK Hive Mind
try:
    from rick_hive.rick_charter import RickCharter as CHARTER
except ImportError:
    class CHARTER:
        MIN_NOTIONAL_USD = 5000
        MIN_EXPECTED_PNL_USD = 200
        MAX_HOLD_TIME_HOURS = 6
        MIN_RISK_REWARD_RATIO = 3.2


class CryptoWolfPack:
    """
    Consolidated wolf pack strategies for crypto futures
    Adapted from OANDA forex strategies with crypto-specific parameters
    """
    
    # Crypto futures to trade
    INSTRUMENTS = ["BTC", "ETH"]
    
    # Higher volatility = tighter parameters
    RSI_OVERSOLD = 25  # vs 30 for forex
    RSI_OVERBOUGHT = 75  # vs 70 for forex
    
    # CME session breaks (hourly maintenance)
    SESSION_BREAK_HOUR = 16  # 4pm CT
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def calculate_rsi(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate RSI from candle data"""
        if len(candles) < period + 1:
            return 50.0  # Neutral if insufficient data
        
        closes = [c["close"] for c in candles[-(period + 1):]]
        
        gains = []
        losses = []
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_ema(self, candles: List[Dict], period: int) -> float:
        """Calculate EMA from candles"""
        if len(candles) < period:
            return candles[-1]["close"] if candles else 0.0
        
        closes = [c["close"] for c in candles[-period:]]
        
        # Initial SMA
        ema = sum(closes[:period]) / period
        
        # Apply EMA formula
        multiplier = 2 / (period + 1)
        for close in closes[period:]:
            ema = (close - ema) * multiplier + ema
        
        return ema
    
    def check_session_active(self) -> bool:
        """Check if CME crypto session is active (not in hourly break)"""
        now = datetime.now(timezone.utc)
        hour_ct = (now.hour - 6) % 24  # Convert UTC to CT
        
        # CME has 1-hour break at 4pm CT daily
        if hour_ct == self.SESSION_BREAK_HOUR:
            return False
        
        return True
    
    def analyze_crypto_futures(
        self,
        symbol: str,
        candles: List[Dict],
        current_price: float
    ) -> Optional[Dict]:
        """
        Unified wolf pack analysis for crypto futures
        
        Combines:
        - Trend following (EMA crossovers)
        - Mean reversion (RSI extremes)
        - Momentum (recent price action)
        
        Args:
            symbol: BTC or ETH
            candles: Historical OHLCV data
            current_price: Current market price
            
        Returns:
            Signal dict or None
        """
        if len(candles) < 60:
            self.logger.warning(f"{symbol}: Insufficient candles ({len(candles)})")
            return None
        
        # Skip if session break
        if not self.check_session_active():
            self.logger.info(f"{symbol}: CME session break - skipping")
            return None
        
        # Calculate indicators
        rsi = self.calculate_rsi(candles)
        ema_fast = self.calculate_ema(candles, 12)
        ema_slow = self.calculate_ema(candles, 26)
        
        # Trend direction
        trend_bullish = ema_fast > ema_slow
        trend_bearish = ema_fast < ema_slow
        
        # Mean reversion zones
        oversold = rsi < self.RSI_OVERSOLD
        overbought = rsi > self.RSI_OVERBOUGHT
        
        # Recent momentum (last 3 candles)
        recent_candles = candles[-3:]
        momentum_up = all(c["close"] > c["open"] for c in recent_candles)
        momentum_down = all(c["close"] < c["open"] for c in recent_candles)
        
        # Signal generation
        signal = None
        
        # Bullish signals
        if oversold and trend_bullish and momentum_up:
            signal = self._generate_long_signal(symbol, current_price, candles)
        
        # Bearish signals
        elif overbought and trend_bearish and momentum_down:
            signal = self._generate_short_signal(symbol, current_price, candles)
        
        if signal:
            self.logger.info(
                f"📊 {symbol} Signal: {signal['side']} @ {signal['entry']:.2f} "
                f"(RSI: {rsi:.1f}, Trend: {'Bull' if trend_bullish else 'Bear'})"
            )
        
        return signal
    
    def _generate_long_signal(
        self,
        symbol: str,
        entry: float,
        candles: List[Dict]
    ) -> Dict:
        """Generate LONG signal with OCO levels"""
        # ATR for stop/target calculation
        atr = self._calculate_atr(candles, period=14)
        
        # Crypto-adjusted R:R (3.5x due to higher vol)
        stop_loss = entry - (1.5 * atr)
        take_profit = entry + (3.5 * 1.5 * atr)  # 3.5x R:R
        
        # Calculate units for MIN_NOTIONAL
        # For BTC micro futures: multiplier = 0.1 BTC = ~$6000 per contract at $60k BTC
        notional_per_unit = entry * 0.1  # Micro BTC
        units = max(1, int(CHARTER.MIN_NOTIONAL_USD / notional_per_unit))
        
        return {
            "symbol": symbol,
            "side": "BUY",
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "units": units,
            "notional": units * notional_per_unit,
            "expected_pnl": (take_profit - entry) * units * 0.1,
            "rr_ratio": 3.5,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_short_signal(
        self,
        symbol: str,
        entry: float,
        candles: List[Dict]
    ) -> Dict:
        """Generate SHORT signal with OCO levels"""
        atr = self._calculate_atr(candles, period=14)
        
        stop_loss = entry + (1.5 * atr)
        take_profit = entry - (3.5 * 1.5 * atr)
        
        notional_per_unit = entry * 0.1
        units = max(1, int(CHARTER.MIN_NOTIONAL_USD / notional_per_unit))
        
        return {
            "symbol": symbol,
            "side": "SELL",
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "units": units,
            "notional": units * notional_per_unit,
            "expected_pnl": (entry - take_profit) * units * 0.1,
            "rr_ratio": 3.5,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(candles) < period + 1:
            return candles[-1]["high"] - candles[-1]["low"] if candles else 0.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i]["high"]
            low = candles[i]["low"]
            prev_close = candles[i-1]["close"]
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        return sum(true_ranges[-period:]) / period


class IBKRTradingEngine:
    """
    Main trading engine for IBKR crypto futures
    
    Loop:
    1. Fetch candles for BTC/ETH
    2. Run wolf pack analysis
    3. Generate signals
    4. Validate vs charter gates
    5. Place OCO orders
    6. Monitor positions (max 6h hold)
    7. Run Position Police
    """
    
    def __init__(self):
        # Logging
        self.logger = self._setup_logging()
        
        # IBKR connector
        self.connector = IBKRConnector(
            port=int(os.getenv("IBKR_PORT", 7497)),  # Paper trading
            account=os.getenv("IBKR_PAPER_ACCOUNT"),
            logger=self.logger
        )
        
        # Wolf pack strategies
        self.wolf_pack = CryptoWolfPack(self.logger)
        
        # Position tracking
        self.position_open_times = {}
        
        # Cycle interval (crypto = faster cycles than forex)
        self.cycle_interval = 300  # 5 minutes (vs 15 min for forex)
        
        self.logger.info("🚀 IBKR Crypto Futures Engine initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging to console + file"""
        os.makedirs("logs", exist_ok=True)
        
        logger = logging.getLogger("IBKREngine")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console)
        
        # File handler
        file_handler = logging.FileHandler("logs/ibkr_engine.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        return logger
    
    async def run_trading_loop(self):
        """
        Main trading loop
        
        24/7 operation with 5-minute cycles
        """
        if not self.connector.connect():
            self.logger.error("❌ Failed to connect to IBKR Gateway")
            return
        
        self.logger.info("✅ Trading loop started (5-min cycles, paper mode)")
        
        try:
            while True:
                cycle_start = time.time()
                
                # Process each crypto futures instrument
                for symbol in self.wolf_pack.INSTRUMENTS:
                    try:
                        await self._process_instrument(symbol)
                    except Exception as e:
                        self.logger.error(f"Error processing {symbol}: {e}")
                
                # Position Police (charter enforcement)
                try:
                    position_police_check(self.connector)
                    self._check_hold_time_violations()
                except Exception as e:
                    self.logger.error(f"Position Police error: {e}")
                
                # Wait for next cycle
                elapsed = time.time() - cycle_start
                sleep_time = max(0, self.cycle_interval - elapsed)
                
                self.logger.info(f"💤 Cycle complete ({elapsed:.1f}s), sleeping {sleep_time:.0f}s")
                await asyncio.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutting down...")
        finally:
            self.connector.disconnect()
    
    async def _process_instrument(self, symbol: str):
        """Process single crypto futures instrument"""
        # Fetch historical data
        candles = self.connector.get_historical_data(symbol, count=60, timeframe="1H")
        
        if not candles:
            self.logger.warning(f"{symbol}: No candles received")
            return
        
        current_price = candles[-1]["close"]
        
        # Check for existing position
        positions = self.connector.get_open_positions()
        has_position = any(p["symbol"] == symbol for p in positions)
        
        if has_position:
            self.logger.info(f"{symbol}: Position already open, monitoring")
            return
        
        # Wolf pack analysis
        signal = self.wolf_pack.analyze_crypto_futures(symbol, candles, current_price)
        
        if not signal:
            return
        
        # Place order (charter validation inside connector)
        result = self.connector.place_order(
            symbol=signal["symbol"],
            side=signal["side"],
            units=signal["units"],
            entry_price=signal["entry"],
            stop_loss=signal["stop_loss"],
            take_profit=signal["take_profit"]
        )
        
        if result.get("success"):
            # Track position open time
            self.position_open_times[symbol] = datetime.now(timezone.utc)
            self.logger.info(f"✅ Trade executed: {symbol} {signal['side']}")
        else:
            self.logger.warning(
                f"❌ Trade rejected: {symbol} - {result.get('error', 'Unknown')}"
            )
    
    def _check_hold_time_violations(self):
        """
        Charter enforcement: Close positions exceeding MAX_HOLD_TIME (6 hours)
        """
        now = datetime.now(timezone.utc)
        max_hold = timedelta(hours=CHARTER.MAX_HOLD_TIME_HOURS)
        
        for symbol, open_time in list(self.position_open_times.items()):
            hold_duration = now - open_time
            
            if hold_duration > max_hold:
                self.logger.warning(
                    f"🚨 MAX_HOLD violation: {symbol} open for {hold_duration.total_seconds()/3600:.1f}h - CLOSING"
                )
                
                result = self.connector.close_position(symbol)
                
                if result.get("success"):
                    del self.position_open_times[symbol]
                    self.logger.info(f"✅ Closed {symbol} (hold time violation)")


async def main():
    """Entry point"""
    print("=" * 80)
    print("IBKR GATEWAY CRYPTO FUTURES ENGINE")
    print("=" * 80)
    print(f"Mode: Paper Trading (port 7497)")
    print(f"Assets: BTC, ETH futures (CME)")
    print(f"Charter: MIN_NOTIONAL=${CHARTER.MIN_NOTIONAL_USD}, "
          f"MIN_PNL=${CHARTER.MIN_EXPECTED_PNL_USD}, "
          f"MAX_HOLD={CHARTER.MAX_HOLD_TIME_HOURS}h, "
          f"MIN_RR={CHARTER.MIN_RISK_REWARD_RATIO}x")
    print("=" * 80)
    print()
    
    engine = IBKRTradingEngine()
    await engine.run_trading_loop()


if __name__ == "__main__":
    asyncio.run(main())
