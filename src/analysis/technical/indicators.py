"""
Technical indicator calculations.
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculator for technical indicators."""

    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int) -> Optional[float]:
        """
        Calculate Exponential Moving Average.

        Args:
            data: DataFrame with 'Close' column
            period: EMA period

        Returns:
            Current EMA value or None
        """
        try:
            if len(data) < period:
                logger.warning(f"Not enough data for EMA({period})")
                return None

            ema = data['Close'].ewm(span=period, adjust=False).mean()
            return float(ema.iloc[-1]) if not pd.isna(ema.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return None

    @staticmethod
    def calculate_vwap(data: pd.DataFrame) -> Optional[float]:
        """
        Calculate Volume Weighted Average Price.

        Args:
            data: DataFrame with OHLCV columns

        Returns:
            Current VWAP value or None
        """
        try:
            if len(data) < 1:
                return None

            # Calculate typical price
            typical_price = (data['High'] + data['Low'] + data['Close']) / 3

            # Calculate cumulative values
            cumulative_tp_volume = (typical_price * data['Volume']).cumsum()
            cumulative_volume = data['Volume'].cumsum()

            # VWAP
            vwap = cumulative_tp_volume / cumulative_volume

            return float(vwap.iloc[-1]) if not pd.isna(vwap.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculating VWAP: {e}")
            return None

    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index.

        Args:
            data: DataFrame with 'Close' column
            period: RSI period (default 14)

        Returns:
            Current RSI value or None
        """
        try:
            if len(data) < period + 1:
                logger.warning(f"Not enough data for RSI({period})")
                return None

            # Calculate price changes
            delta = data['Close'].diff()

            # Separate gains and losses
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)

            # Calculate average gain and loss
            avg_gain = gain.ewm(span=period, adjust=False).mean()
            avg_loss = loss.ewm(span=period, adjust=False).mean()

            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None

    @staticmethod
    def calculate_macd(
        data: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Optional[Tuple[float, float, float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            data: DataFrame with 'Close' column
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Tuple of (MACD, Signal, Histogram) or None
        """
        try:
            if len(data) < slow + signal:
                logger.warning(f"Not enough data for MACD")
                return None

            # Calculate fast and slow EMAs
            ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
            ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()

            # MACD line
            macd_line = ema_fast - ema_slow

            # Signal line
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()

            # Histogram
            histogram = macd_line - signal_line

            macd_val = float(macd_line.iloc[-1])
            signal_val = float(signal_line.iloc[-1])
            hist_val = float(histogram.iloc[-1])

            if pd.isna(macd_val) or pd.isna(signal_val) or pd.isna(hist_val):
                return None

            return macd_val, signal_val, hist_val

        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return None

    @staticmethod
    def find_support_resistance(
        data: pd.DataFrame,
        lookback: int = 20,
        num_levels: int = 2
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Find support and resistance levels using local extrema.

        Args:
            data: DataFrame with OHLC columns
            lookback: Number of periods to look back
            num_levels: Number of support/resistance levels to identify

        Returns:
            Tuple of (support, resistance) levels
        """
        try:
            if len(data) < lookback:
                return None, None

            # Use recent data
            recent_data = data.tail(lookback)

            # Find local minima (support) and maxima (resistance)
            highs = recent_data['High'].values
            lows = recent_data['Low'].values

            # Support: local minima
            support_candidates = []
            for i in range(1, len(lows) - 1):
                if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                    support_candidates.append(lows[i])

            # Resistance: local maxima
            resistance_candidates = []
            for i in range(1, len(highs) - 1):
                if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                    resistance_candidates.append(highs[i])

            # Get the nearest support below current price
            current_price = data['Close'].iloc[-1]

            support = None
            if support_candidates:
                below_current = [s for s in support_candidates if s < current_price]
                support = max(below_current) if below_current else min(support_candidates)

            # Get the nearest resistance above current price
            resistance = None
            if resistance_candidates:
                above_current = [r for r in resistance_candidates if r > current_price]
                resistance = min(above_current) if above_current else max(resistance_candidates)

            return support, resistance

        except Exception as e:
            logger.error(f"Error finding support/resistance: {e}")
            return None, None

    @staticmethod
    def detect_trend(data: pd.DataFrame, ema_short: float, ema_long: float) -> str:
        """
        Detect trend direction based on EMAs and price action.

        Args:
            data: DataFrame with 'Close' column
            ema_short: Short EMA value
            ema_long: Long EMA value

        Returns:
            Trend direction: 'bullish', 'bearish', or 'sideways'
        """
        try:
            current_price = data['Close'].iloc[-1]

            # Strong trend signals
            if ema_short > ema_long and current_price > ema_short:
                return "bullish"
            elif ema_short < ema_long and current_price < ema_short:
                return "bearish"
            else:
                return "sideways"

        except Exception as e:
            logger.error(f"Error detecting trend: {e}")
            return "unknown"

    @staticmethod
    def detect_breakout_breakdown(
        data: pd.DataFrame,
        resistance: Optional[float],
        support: Optional[float],
        threshold: float = 0.001  # 0.1%
    ) -> Tuple[bool, bool]:
        """
        Detect breakout above resistance or breakdown below support.

        Args:
            data: DataFrame with 'Close' column
            resistance: Resistance level
            support: Support level
            threshold: Price threshold as a fraction

        Returns:
            Tuple of (is_breakout, is_breakdown)
        """
        try:
            current_price = data['Close'].iloc[-1]

            is_breakout = False
            is_breakdown = False

            if resistance and current_price > resistance * (1 + threshold):
                is_breakout = True

            if support and current_price < support * (1 - threshold):
                is_breakdown = True

            return is_breakout, is_breakdown

        except Exception as e:
            logger.error(f"Error detecting breakout/breakdown: {e}")
            return False, False
