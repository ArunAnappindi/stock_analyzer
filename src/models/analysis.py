"""
Data models for analysis results.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TrendDirection(str, Enum):
    """Trend direction classification."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    UNKNOWN = "unknown"


class Signal(str, Enum):
    """Trading signal classification."""
    STRONG_BUY = "strong_buy"
    MODERATE_BUY = "moderate_buy"
    WEAK_BUY = "weak_buy"
    HOLD = "hold"
    NO_TRADE = "no_trade"
    AVOID = "avoid"


class Sentiment(str, Enum):
    """Sentiment classification."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators."""

    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    vwap: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None


class TechnicalAnalysis(BaseModel):
    """Technical analysis results."""

    indicators: TechnicalIndicators
    trend: TrendDirection
    is_breakout: bool = False
    is_breakdown: bool = False
    price_above_vwap: bool = False
    ema_alignment: bool = False
    rsi_interpretation: str = Field(default="neutral")
    macd_interpretation: str = Field(default="neutral")
    overall_signal: str = Field(default="neutral")
    confidence: int = Field(ge=0, le=100, default=50)
    summary: str = ""


class VolumeAnalysis(BaseModel):
    """Volume analysis results."""

    current_volume: int
    avg_volume: float
    relative_volume: float
    volume_spike_detected: bool = False
    price_volume_confirmation: bool = False
    vwap_deviation_pct: float = 0.0
    interpretation: str = Field(default="neutral")
    confidence: int = Field(ge=0, le=100, default=50)
    summary: str = ""


class SentimentAnalysis(BaseModel):
    """Sentiment analysis results."""

    news_sentiment: Sentiment = Sentiment.NEUTRAL
    news_score: float = Field(ge=-1, le=1, default=0.0)
    social_sentiment: Sentiment = Sentiment.NEUTRAL
    social_score: float = Field(ge=-1, le=1, default=0.0)
    major_catalysts: list[str] = Field(default_factory=list)
    overall_sentiment: Sentiment = Sentiment.NEUTRAL
    confidence: int = Field(ge=0, le=100, default=50)
    summary: str = ""


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TradeRecommendation(BaseModel):
    """Trade recommendation with entry, target, and stop loss."""

    signal: Signal
    confidence: int = Field(ge=0, le=100)

    # Price levels (None if no trade recommended)
    entry_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None

    # Position sizing
    max_quantity: int = 100

    # Risk metrics
    risk_reward_ratio: Optional[float] = None
    risk_amount: Optional[float] = None
    potential_profit: Optional[float] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM

    # Timing
    estimated_hold_time: str = "Intraday (minutes to hours)"

    # Reasoning
    reasoning: str = ""
    key_factors: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Complete analysis result."""

    ticker: str
    timestamp: str
    current_price: float

    # Analysis components
    technical_analysis: TechnicalAnalysis
    volume_analysis: VolumeAnalysis
    sentiment_analysis: SentimentAnalysis

    # Final decision
    trade_recommendation: TradeRecommendation

    # Metadata
    data_quality: str = "Real-time"  # or "Delayed / Simulated"
    warnings: list[str] = Field(default_factory=list)

    # Risk disclaimer
    disclaimer: str = (
        "This analysis is for educational purposes only and does not constitute "
        "financial advice. Trading involves substantial risk of loss. Past "
        "performance does not guarantee future results. Always do your own "
        "research and consult with a qualified financial advisor before making "
        "investment decisions."
    )

    class Config:
        use_enum_values = True
