"""
Data models for stock information and market data.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import pandas as pd


class StockInfo(BaseModel):
    """Basic stock information."""

    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: Optional[str] = Field(None, description="Company name")
    exchange: str = Field(default="NASDAQ", description="Stock exchange")
    sector: Optional[str] = Field(None, description="Industry sector")
    market_cap: Optional[float] = Field(None, description="Market capitalization")

    class Config:
        arbitrary_types_allowed = True


class OHLCVData(BaseModel):
    """OHLCV price data container."""

    ticker: str
    interval: str = Field(description="Data interval (e.g., 5m, 15m)")
    data: pd.DataFrame = Field(description="DataFrame with OHLCV data")
    fetched_at: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True

    def get_latest_price(self) -> float:
        """Get the most recent closing price."""
        return float(self.data['Close'].iloc[-1])

    def get_latest_volume(self) -> int:
        """Get the most recent volume."""
        return int(self.data['Volume'].iloc[-1])

    def get_price_change(self) -> float:
        """Get price change from previous close."""
        if len(self.data) < 2:
            return 0.0
        return float(self.data['Close'].iloc[-1] - self.data['Close'].iloc[-2])

    def get_price_change_pct(self) -> float:
        """Get price change percentage."""
        if len(self.data) < 2:
            return 0.0
        prev_close = self.data['Close'].iloc[-2]
        if prev_close == 0:
            return 0.0
        return ((self.data['Close'].iloc[-1] - prev_close) / prev_close) * 100


class MarketData(BaseModel):
    """Complete market data for a stock."""

    stock_info: StockInfo
    intraday_data: OHLCVData
    historical_data: Optional[OHLCVData] = None
    current_price: float
    previous_close: float
    volume: int
    avg_volume: Optional[float] = None

    class Config:
        arbitrary_types_allowed = True
