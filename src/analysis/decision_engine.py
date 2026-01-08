"""
Trade decision engine that synthesizes all analyses into a trade recommendation.
"""

import logging
from typing import Optional
from src.models import (
    TradeRecommendation,
    Signal,
    RiskLevel,
    TechnicalAnalysis,
    VolumeAnalysis,
    SentimentAnalysis,
    MarketData
)
from config.settings import settings

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Trade decision engine that synthesizes all analyses."""

    def __init__(self):
        """Initialize the decision engine."""
        pass

    def make_decision(
        self,
        market_data: MarketData,
        technical: TechnicalAnalysis,
        volume: VolumeAnalysis,
        sentiment: SentimentAnalysis
    ) -> TradeRecommendation:
        """
        Make a trade decision based on all analyses.

        Args:
            market_data: Market data
            technical: Technical analysis results
            volume: Volume analysis results
            sentiment: Sentiment analysis results

        Returns:
            TradeRecommendation with signal and price levels
        """
        try:
            # Calculate overall confidence score
            confidence = self._calculate_overall_confidence(
                technical, volume, sentiment
            )

            # Determine trade signal
            signal = self._determine_signal(
                technical, volume, sentiment, confidence
            )

            # If signal is BUY, calculate entry, target, and stop loss
            if signal in [Signal.STRONG_BUY, Signal.MODERATE_BUY, Signal.WEAK_BUY]:
                entry, target, stop_loss = self._calculate_price_levels(
                    market_data, technical, signal
                )

                risk_reward = self._calculate_risk_reward(entry, target, stop_loss)
                risk_level = self._determine_risk_level(confidence, technical, volume)

                # Calculate risk metrics
                risk_amount = (entry - stop_loss) * settings.max_position_size if entry and stop_loss else 0
                potential_profit = (target - entry) * settings.max_position_size if entry and target else 0

            else:
                # No trade recommended
                entry = target = stop_loss = None
                risk_reward = None
                risk_level = RiskLevel.MEDIUM
                risk_amount = None
                potential_profit = None

            # Generate reasoning
            reasoning = self._generate_reasoning(
                signal, technical, volume, sentiment, confidence
            )

            # Generate key factors
            key_factors = self._generate_key_factors(
                technical, volume, sentiment
            )

            return TradeRecommendation(
                signal=signal,
                confidence=confidence,
                entry_price=entry,
                target_price=target,
                stop_loss=stop_loss,
                max_quantity=settings.max_position_size,
                risk_reward_ratio=risk_reward,
                risk_amount=risk_amount,
                potential_profit=potential_profit,
                risk_level=risk_level,
                reasoning=reasoning,
                key_factors=key_factors
            )

        except Exception as e:
            logger.error(f"Error making trade decision: {e}")
            return TradeRecommendation(
                signal=Signal.NO_TRADE,
                confidence=0,
                reasoning="Error generating trade recommendation"
            )

    def _calculate_overall_confidence(
        self,
        technical: TechnicalAnalysis,
        volume: VolumeAnalysis,
        sentiment: SentimentAnalysis
    ) -> int:
        """Calculate overall confidence score weighted from all analyses."""
        # Weight the different analysis types
        tech_weight = 0.5
        volume_weight = 0.3
        sentiment_weight = 0.2

        overall = (
            technical.confidence * tech_weight +
            volume.confidence * volume_weight +
            sentiment.confidence * sentiment_weight
        )

        return int(overall)

    def _determine_signal(
        self,
        technical: TechnicalAnalysis,
        volume: VolumeAnalysis,
        sentiment: SentimentAnalysis,
        confidence: int
    ) -> Signal:
        """Determine the trade signal based on all analyses."""
        # Count bullish and bearish signals
        bullish_signals = 0
        bearish_signals = 0

        # Technical analysis
        if technical.overall_signal == "bullish":
            bullish_signals += 3
        elif technical.overall_signal == "bearish":
            bearish_signals += 3

        if technical.is_breakout:
            bullish_signals += 2
        elif technical.is_breakdown:
            bearish_signals += 2

        if technical.ema_alignment:
            bullish_signals += 1

        # Volume analysis
        if volume.interpretation == "bullish" and volume.price_volume_confirmation:
            bullish_signals += 2
        elif volume.interpretation == "bearish" and volume.price_volume_confirmation:
            bearish_signals += 2
        elif volume.volume_spike_detected:
            # Volume spike without clear direction
            bullish_signals += 1

        # Sentiment analysis
        if sentiment.overall_sentiment.value in ["positive", "very_positive"]:
            bullish_signals += 1
        elif sentiment.overall_sentiment.value in ["negative", "very_negative"]:
            bearish_signals += 1

        if len(sentiment.major_catalysts) > 0:
            bullish_signals += 1

        # Determine signal based on signals and confidence
        total_signals = bullish_signals + bearish_signals
        if total_signals == 0:
            return Signal.NO_TRADE

        bullish_ratio = bullish_signals / total_signals

        # Bearish conditions
        if bearish_signals > bullish_signals:
            return Signal.AVOID

        # Not enough confidence
        if confidence < settings.min_confidence_score:
            return Signal.NO_TRADE

        # Bullish signals
        if bullish_ratio >= 0.8 and confidence >= settings.strong_buy_threshold:
            return Signal.STRONG_BUY
        elif bullish_ratio >= 0.7 and confidence >= settings.moderate_buy_threshold:
            return Signal.MODERATE_BUY
        elif bullish_ratio >= 0.6:
            return Signal.WEAK_BUY
        else:
            return Signal.HOLD

    def _calculate_price_levels(
        self,
        market_data: MarketData,
        technical: TechnicalAnalysis,
        signal: Signal
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate entry, target, and stop loss price levels."""
        try:
            current_price = market_data.current_price

            # Entry price: slightly above current for confirmation
            # or at current if already confirmed
            if technical.is_breakout:
                entry_price = current_price  # Already breaking out
            else:
                entry_price = current_price * 1.001  # 0.1% above current

            # Stop loss based on support or percentage
            if technical.indicators.support_level and technical.indicators.support_level < current_price:
                stop_loss = technical.indicators.support_level * 0.995  # Slightly below support
            else:
                # Use percentage-based stop loss
                stop_loss = entry_price * (1 - settings.default_stop_loss_pct / 100)

            # Target based on risk-reward ratio or resistance
            if technical.indicators.resistance_level and technical.indicators.resistance_level > current_price:
                target_price = technical.indicators.resistance_level * 0.995  # Just below resistance
            else:
                # Use percentage-based target
                target_price = entry_price * (1 + settings.default_target_pct / 100)

            # Adjust based on risk-reward ratio
            risk = entry_price - stop_loss
            reward = target_price - entry_price

            # Ensure minimum risk-reward ratio
            if reward / risk < settings.default_risk_reward_ratio:
                target_price = entry_price + (risk * settings.default_risk_reward_ratio)

            return (
                round(entry_price, 2),
                round(target_price, 2),
                round(stop_loss, 2)
            )

        except Exception as e:
            logger.error(f"Error calculating price levels: {e}")
            return None, None, None

    def _calculate_risk_reward(
        self,
        entry: Optional[float],
        target: Optional[float],
        stop_loss: Optional[float]
    ) -> Optional[float]:
        """Calculate risk-reward ratio."""
        if not all([entry, target, stop_loss]):
            return None

        risk = entry - stop_loss
        reward = target - entry

        if risk <= 0:
            return None

        return round(reward / risk, 2)

    def _determine_risk_level(
        self,
        confidence: int,
        technical: TechnicalAnalysis,
        volume: VolumeAnalysis
    ) -> RiskLevel:
        """Determine the risk level of the trade."""
        if confidence >= 80 and technical.trend.value == "bullish" and volume.price_volume_confirmation:
            return RiskLevel.LOW
        elif confidence >= 65:
            return RiskLevel.MEDIUM
        elif confidence >= 50:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    def _generate_reasoning(
        self,
        signal: Signal,
        technical: TechnicalAnalysis,
        volume: VolumeAnalysis,
        sentiment: SentimentAnalysis,
        confidence: int
    ) -> str:
        """Generate reasoning for the trade decision."""
        if signal == Signal.NO_TRADE:
            return "Conditions not favorable for intraday swing trade. Insufficient confidence or mixed signals."

        if signal == Signal.AVOID:
            return "Bearish signals detected. Avoid trading this stock today."

        # BUY signals
        reasons = []

        if technical.overall_signal == "bullish":
            reasons.append("Technical indicators show bullish momentum")

        if technical.is_breakout:
            reasons.append("Breakout above resistance detected")

        if volume.volume_spike_detected and volume.price_volume_confirmation:
            reasons.append("Strong volume confirming price movement")

        if sentiment.overall_sentiment.value in ["positive", "very_positive"]:
            reasons.append("Positive market sentiment")

        if len(sentiment.major_catalysts) > 0:
            reasons.append(f"Catalysts identified: {', '.join(sentiment.major_catalysts[:2])}")

        reasoning = ". ".join(reasons) + f". Overall confidence: {confidence}%."

        return reasoning

    def _generate_key_factors(
        self,
        technical: TechnicalAnalysis,
        volume: VolumeAnalysis,
        sentiment: SentimentAnalysis
    ) -> list[str]:
        """Generate list of key factors for the trade."""
        factors = []

        # Technical factors
        if technical.trend.value != "unknown":
            factors.append(f"Trend: {technical.trend.value.capitalize()}")

        if technical.is_breakout:
            factors.append("Breakout detected")

        if technical.indicators.rsi:
            factors.append(f"RSI: {technical.indicators.rsi:.1f} ({technical.rsi_interpretation})")

        # Volume factors
        if volume.relative_volume >= 1.5:
            factors.append(f"Volume: {volume.relative_volume:.1f}x average")

        # Sentiment factors
        if sentiment.overall_sentiment.value != "neutral":
            factors.append(f"Sentiment: {sentiment.overall_sentiment.value.replace('_', ' ').title()}")

        if len(sentiment.major_catalysts) > 0:
            factors.append(f"Catalysts: {len(sentiment.major_catalysts)} detected")

        return factors[:6]  # Limit to 6 key factors
