"""
Abstract base class for data providers.
"""

from abc import ABC, abstractmethod
from typing import Optional
from src.models import StockInfo, OHLCVData


class DataProvider(ABC):
    """Abstract base class for market data providers."""

    @abstractmethod
    def get_stock_info(self, ticker: str) -> Optional[StockInfo]:
        """
        Fetch basic stock information.

        Args:
            ticker: Stock ticker symbol

        Returns:
            StockInfo object or None if not found
        """
        pass

    @abstractmethod
    def get_intraday_data(
        self,
        ticker: str,
        interval: str = "5m",
        days: int = 5
    ) -> Optional[OHLCVData]:
        """
        Fetch intraday OHLCV data.

        Args:
            ticker: Stock ticker symbol
            interval: Data interval (1m, 5m, 15m, etc.)
            days: Number of days of historical data

        Returns:
            OHLCVData object or None if not available
        """
        pass

    @abstractmethod
    def is_market_open(self) -> bool:
        """
        Check if the market is currently open.

        Returns:
            True if market is open, False otherwise
        """
        pass
