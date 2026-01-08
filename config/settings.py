"""
Configuration settings for the Stock Analyzer application.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables or defaults."""

    # API Keys
    news_api_key: Optional[str] = Field(default=None, description="NewsAPI.org API key")
    alpha_vantage_key: Optional[str] = Field(default=None, description="Alpha Vantage API key")

    # Data Settings
    default_exchange: str = Field(default="NASDAQ", description="Default stock exchange")
    intraday_interval: str = Field(default="5m", description="Intraday data interval (1m, 5m, 15m)")
    historical_days: int = Field(default=5, description="Days of historical data to fetch")

    # Analysis Settings
    ema_short_period: int = Field(default=20, description="Short EMA period")
    ema_long_period: int = Field(default=50, description="Long EMA period")
    rsi_period: int = Field(default=14, description="RSI period")
    volume_threshold: float = Field(default=1.5, description="Volume spike threshold (multiplier)")

    # Trade Decision Thresholds
    min_confidence_score: int = Field(default=60, description="Minimum confidence score for trade")
    strong_buy_threshold: int = Field(default=75, description="Strong buy confidence threshold")
    moderate_buy_threshold: int = Field(default=60, description="Moderate buy confidence threshold")

    # Risk Management
    default_risk_reward_ratio: float = Field(default=2.0, description="Default risk:reward ratio")
    default_stop_loss_pct: float = Field(default=1.5, description="Default stop loss percentage")
    default_target_pct: float = Field(default=3.0, description="Default target percentage")
    max_position_size: int = Field(default=100, description="Maximum position size in shares")

    # Output Settings
    output_format: str = Field(default="rich", description="Output format (rich, plain, json)")
    show_detailed_analysis: bool = Field(default=True, description="Show detailed analysis")

    # Cache Settings
    cache_enabled: bool = Field(default=True, description="Enable data caching")
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
