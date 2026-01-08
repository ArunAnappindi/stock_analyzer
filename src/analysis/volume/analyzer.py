"""
Volume analysis engine for detecting volume patterns and price-volume relationships.
"""

import logging
from typing import Optional
from src.models import VolumeAnalysis, MarketData
from config.settings import settings

logger = logging.getLogger(__name__)


class VolumeAnalyzer:
    """Volume analysis engine."""

    def analyze(self, market_data: MarketData) -> VolumeAnalysis:
        """
        Perform volume analysis on market data.

        Args:
            market_data: MarketData object

        Returns:
            VolumeAnalysis result
        """
        try:
            current_volume = market_data.volume
            avg_volume = market_data.avg_volume or current_volume

            # Calculate relative volume
            relative_volume = current_volume / avg_volume if avg_volume > 0 else 1.0

            # Detect volume spike
            volume_spike_detected = relative_volume >= settings.volume_threshold

            # Analyze price-volume confirmation
            price_volume_confirmation = self._check_price_volume_confirmation(
                market_data, relative_volume
            )

            # Calculate VWAP deviation
            vwap_deviation_pct = self._calculate_vwap_deviation(market_data)

            # Generate interpretation
            interpretation = self._generate_interpretation(
                relative_volume, volume_spike_detected,
                price_volume_confirmation, vwap_deviation_pct
            )

            # Calculate confidence
            confidence = self._calculate_confidence(
                relative_volume, volume_spike_detected,
                price_volume_confirmation
            )

            # Generate summary
            summary = self._generate_summary(
                current_volume, avg_volume, relative_volume,
                volume_spike_detected, price_volume_confirmation
            )

            return VolumeAnalysis(
                current_volume=current_volume,
                avg_volume=avg_volume,
                relative_volume=relative_volume,
                volume_spike_detected=volume_spike_detected,
                price_volume_confirmation=price_volume_confirmation,
                vwap_deviation_pct=vwap_deviation_pct,
                interpretation=interpretation,
                confidence=confidence,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Error in volume analysis: {e}")
            return VolumeAnalysis(
                current_volume=0,
                avg_volume=0,
                relative_volume=0.0,
                summary="Error performing volume analysis"
            )

    def _check_price_volume_confirmation(
        self,
        market_data: MarketData,
        relative_volume: float
    ) -> bool:
        """
        Check if price movement is confirmed by volume.

        Bullish confirmation: Price up + High volume
        Bearish confirmation: Price down + High volume
        """
        try:
            df = market_data.intraday_data.data

            if len(df) < 2:
                return False

            # Get price change
            price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]

            # High volume threshold
            high_volume = relative_volume >= settings.volume_threshold * 0.8

            # Confirmation: significant price move with high volume
            if abs(price_change) > 0 and high_volume:
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking price-volume confirmation: {e}")
            return False

    def _calculate_vwap_deviation(self, market_data: MarketData) -> float:
        """Calculate percentage deviation from VWAP."""
        try:
            current_price = market_data.current_price

            # Try to get VWAP from intraday data
            df = market_data.intraday_data.data
            if len(df) < 1:
                return 0.0

            # Calculate VWAP
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            cumulative_tp_volume = (typical_price * df['Volume']).cumsum()
            cumulative_volume = df['Volume'].cumsum()
            vwap = (cumulative_tp_volume / cumulative_volume).iloc[-1]

            if vwap == 0:
                return 0.0

            deviation_pct = ((current_price - vwap) / vwap) * 100
            return float(deviation_pct)

        except Exception as e:
            logger.error(f"Error calculating VWAP deviation: {e}")
            return 0.0

    def _generate_interpretation(
        self,
        relative_volume: float,
        volume_spike: bool,
        confirmation: bool,
        vwap_deviation: float
    ) -> str:
        """Generate volume interpretation."""
        if volume_spike and confirmation:
            if vwap_deviation > 0:
                return "bullish"
            else:
                return "bearish"
        elif volume_spike:
            return "high_activity"
        elif relative_volume < 0.5:
            return "low_activity"
        else:
            return "neutral"

    def _calculate_confidence(
        self,
        relative_volume: float,
        volume_spike: bool,
        confirmation: bool
    ) -> int:
        """Calculate confidence score (0-100)."""
        confidence = 50

        # Higher confidence with higher relative volume
        if relative_volume > 2.0:
            confidence += 20
        elif relative_volume > 1.5:
            confidence += 15
        elif relative_volume > 1.0:
            confidence += 10

        # Add confidence for confirmation
        if confirmation:
            confidence += 15

        # Add confidence for volume spike
        if volume_spike:
            confidence += 10

        return min(confidence, 100)

    def _generate_summary(
        self,
        current_volume: int,
        avg_volume: float,
        relative_volume: float,
        volume_spike: bool,
        confirmation: bool
    ) -> str:
        """Generate a text summary of volume analysis."""
        summary_parts = []

        # Relative volume
        summary_parts.append(f"Volume: {relative_volume:.1f}x average")

        # Volume spike
        if volume_spike:
            summary_parts.append("SPIKE detected")

        # Confirmation
        if confirmation:
            summary_parts.append("Price-volume confirmed")
        else:
            summary_parts.append("No price-volume confirmation")

        # Actual numbers
        summary_parts.append(f"Current: {current_volume:,} | Avg: {avg_volume:,.0f}")

        return " | ".join(summary_parts)
