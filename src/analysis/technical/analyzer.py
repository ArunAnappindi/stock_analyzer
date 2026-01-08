"""
Technical analysis engine that interprets indicators and generates signals.
"""

import logging
from src.models import (
    TechnicalIndicators,
    TechnicalAnalysis,
    TrendDirection,
    MarketData
)
from .indicators import IndicatorCalculator
from config.settings import settings

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Technical analysis engine."""

    def __init__(self):
        """Initialize the technical analyzer."""
        self.calculator = IndicatorCalculator()

    def analyze(self, market_data: MarketData) -> TechnicalAnalysis:
        """
        Perform complete technical analysis on market data.

        Args:
            market_data: MarketData object with OHLCV data

        Returns:
            TechnicalAnalysis result
        """
        try:
            df = market_data.intraday_data.data

            # Calculate all indicators
            indicators = self._calculate_indicators(df)

            # Interpret indicators
            trend = self._analyze_trend(df, indicators)
            is_breakout, is_breakdown = self._detect_breakout_breakdown(df, indicators)
            rsi_interp = self._interpret_rsi(indicators.rsi)
            macd_interp = self._interpret_macd(indicators)

            # Check various conditions
            current_price = market_data.current_price
            price_above_vwap = current_price > indicators.vwap if indicators.vwap else False
            ema_alignment = self._check_ema_alignment(current_price, indicators)

            # Generate overall signal
            overall_signal = self._generate_signal(
                trend, rsi_interp, macd_interp, price_above_vwap,
                ema_alignment, is_breakout, is_breakdown
            )

            # Calculate confidence
            confidence = self._calculate_confidence(
                trend, indicators, rsi_interp, macd_interp,
                price_above_vwap, ema_alignment, is_breakout
            )

            # Generate summary
            summary = self._generate_summary(
                trend, indicators, current_price, is_breakout, is_breakdown
            )

            return TechnicalAnalysis(
                indicators=indicators,
                trend=TrendDirection(trend),
                is_breakout=is_breakout,
                is_breakdown=is_breakdown,
                price_above_vwap=price_above_vwap,
                ema_alignment=ema_alignment,
                rsi_interpretation=rsi_interp,
                macd_interpretation=macd_interp,
                overall_signal=overall_signal,
                confidence=confidence,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            # Return a default analysis on error
            return TechnicalAnalysis(
                indicators=TechnicalIndicators(),
                trend=TrendDirection.UNKNOWN,
                summary="Error performing technical analysis"
            )

    def _calculate_indicators(self, df) -> TechnicalIndicators:
        """Calculate all technical indicators."""
        ema_20 = self.calculator.calculate_ema(df, settings.ema_short_period)
        ema_50 = self.calculator.calculate_ema(df, settings.ema_long_period)
        vwap = self.calculator.calculate_vwap(df)
        rsi = self.calculator.calculate_rsi(df, settings.rsi_period)

        macd_result = self.calculator.calculate_macd(df)
        macd, macd_signal, macd_hist = (None, None, None)
        if macd_result:
            macd, macd_signal, macd_hist = macd_result

        support, resistance = self.calculator.find_support_resistance(df)

        return TechnicalIndicators(
            ema_20=ema_20,
            ema_50=ema_50,
            vwap=vwap,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_hist,
            support_level=support,
            resistance_level=resistance
        )

    def _analyze_trend(self, df, indicators: TechnicalIndicators) -> str:
        """Analyze the trend direction."""
        if indicators.ema_20 and indicators.ema_50:
            return self.calculator.detect_trend(df, indicators.ema_20, indicators.ema_50)
        return "unknown"

    def _detect_breakout_breakdown(self, df, indicators: TechnicalIndicators) -> tuple:
        """Detect breakout or breakdown conditions."""
        return self.calculator.detect_breakout_breakdown(
            df,
            indicators.resistance_level,
            indicators.support_level
        )

    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value."""
        if rsi is None:
            return "neutral"

        if rsi > 70:
            return "overbought"
        elif rsi < 30:
            return "oversold"
        elif rsi > 60:
            return "bullish"
        elif rsi < 40:
            return "bearish"
        else:
            return "neutral"

    def _interpret_macd(self, indicators: TechnicalIndicators) -> str:
        """Interpret MACD signals."""
        if indicators.macd is None or indicators.macd_histogram is None:
            return "neutral"

        # MACD above signal line and positive histogram = bullish
        if indicators.macd_histogram > 0:
            return "bullish"
        elif indicators.macd_histogram < 0:
            return "bearish"
        else:
            return "neutral"

    def _check_ema_alignment(self, current_price: float, indicators: TechnicalIndicators) -> bool:
        """Check if EMAs are in bullish alignment (price > EMA20 > EMA50)."""
        if indicators.ema_20 is None or indicators.ema_50 is None:
            return False

        return (current_price > indicators.ema_20 and
                indicators.ema_20 > indicators.ema_50)

    def _generate_signal(
        self,
        trend: str,
        rsi_interp: str,
        macd_interp: str,
        price_above_vwap: bool,
        ema_alignment: bool,
        is_breakout: bool,
        is_breakdown: bool
    ) -> str:
        """Generate overall technical signal."""
        if is_breakdown:
            return "bearish"

        bullish_signals = 0
        bearish_signals = 0

        if trend == "bullish":
            bullish_signals += 2
        elif trend == "bearish":
            bearish_signals += 2

        if rsi_interp in ["bullish", "oversold"]:
            bullish_signals += 1
        elif rsi_interp in ["bearish", "overbought"]:
            bearish_signals += 1

        if macd_interp == "bullish":
            bullish_signals += 1
        elif macd_interp == "bearish":
            bearish_signals += 1

        if price_above_vwap:
            bullish_signals += 1
        else:
            bearish_signals += 1

        if ema_alignment:
            bullish_signals += 1

        if is_breakout:
            bullish_signals += 2

        # Determine overall signal
        if bullish_signals > bearish_signals + 1:
            return "bullish"
        elif bearish_signals > bullish_signals + 1:
            return "bearish"
        else:
            return "neutral"

    def _calculate_confidence(
        self,
        trend: str,
        indicators: TechnicalIndicators,
        rsi_interp: str,
        macd_interp: str,
        price_above_vwap: bool,
        ema_alignment: bool,
        is_breakout: bool
    ) -> int:
        """Calculate confidence score (0-100)."""
        confidence = 50  # Base confidence

        # Add confidence based on agreement between indicators
        agreements = 0
        total_checks = 0

        # Check trend
        if trend in ["bullish", "bearish"]:
            agreements += 1
        total_checks += 1

        # Check RSI
        if rsi_interp != "neutral":
            agreements += 1
        total_checks += 1

        # Check MACD
        if macd_interp != "neutral":
            agreements += 1
        total_checks += 1

        # Check EMA alignment
        if ema_alignment:
            agreements += 1
        total_checks += 1

        # Check VWAP
        if price_above_vwap:
            agreements += 1
        total_checks += 1

        # Breakout adds significant confidence
        if is_breakout:
            confidence += 15

        # Calculate confidence based on agreement
        if total_checks > 0:
            agreement_pct = (agreements / total_checks) * 50
            confidence = min(int(confidence + agreement_pct), 100)

        return confidence

    def _generate_summary(
        self,
        trend: str,
        indicators: TechnicalIndicators,
        current_price: float,
        is_breakout: bool,
        is_breakdown: bool
    ) -> str:
        """Generate a text summary of technical analysis."""
        summary_parts = []

        # Trend
        summary_parts.append(f"Trend: {trend.capitalize()}")

        # EMAs
        if indicators.ema_20 and indicators.ema_50:
            if indicators.ema_20 > indicators.ema_50:
                summary_parts.append(f"EMA alignment bullish (20>{50})")
            else:
                summary_parts.append(f"EMA alignment bearish (20<{50})")

        # VWAP
        if indicators.vwap:
            vwap_pos = "above" if current_price > indicators.vwap else "below"
            summary_parts.append(f"Price {vwap_pos} VWAP (${indicators.vwap:.2f})")

        # RSI
        if indicators.rsi:
            summary_parts.append(f"RSI: {indicators.rsi:.1f}")

        # Breakout/Breakdown
        if is_breakout:
            summary_parts.append("BREAKOUT detected above resistance")
        elif is_breakdown:
            summary_parts.append("BREAKDOWN detected below support")

        return " | ".join(summary_parts)
