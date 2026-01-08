"""
High-level data fetcher for combining stock information and market data.
"""

import logging
from typing import Optional
from src.models import MarketData, StockInfo, OHLCVData
from src.data.providers import DataProvider, YFinanceProvider
from config.settings import settings

logger = logging.getLogger(__name__)


class DataFetcher:
    """High-level data fetcher that combines multiple data sources."""

    def __init__(self, provider: Optional[DataProvider] = None):
        """
        Initialize the data fetcher.

        Args:
            provider: Data provider instance (defaults to YFinanceProvider)
        """
        self.provider = provider or YFinanceProvider()

    def fetch_market_data(
        self,
        ticker: str,
        interval: str = None,
        historical_days: int = None
    ) -> Optional[MarketData]:
        """
        Fetch complete market data for a ticker.

        Args:
            ticker: Stock ticker symbol
            interval: Intraday interval (defaults to config setting)
            historical_days: Days of historical data (defaults to config setting)

        Returns:
            MarketData object or None if data unavailable
        """
        try:
            # Use config defaults if not provided
            interval = interval or settings.intraday_interval
            historical_days = historical_days or settings.historical_days

            # Fetch stock information
            logger.info(f"Fetching stock info for {ticker}")
            stock_info = self.provider.get_stock_info(ticker)
            if not stock_info:
                logger.error(f"Could not fetch stock info for {ticker}")
                return None

            # Fetch intraday data
            logger.info(f"Fetching intraday data for {ticker} ({interval} interval)")
            intraday_data = self.provider.get_intraday_data(
                ticker,
                interval=interval,
                days=historical_days
            )
            if not intraday_data:
                logger.error(f"Could not fetch intraday data for {ticker}")
                return None

            # Get current price and volume
            current_price = intraday_data.get_latest_price()
            volume = intraday_data.get_latest_volume()

            # Calculate previous close (from yesterday's close if available)
            if len(intraday_data.data) > 1:
                previous_close = float(intraday_data.data['Close'].iloc[0])
            else:
                previous_close = current_price

            # Calculate average volume
            avg_volume = float(intraday_data.data['Volume'].mean())

            # Fetch historical data for better context
            historical_data = None
            if hasattr(self.provider, 'get_historical_data'):
                logger.info(f"Fetching historical data for {ticker}")
                historical_data = self.provider.get_historical_data(
                    ticker,
                    days=30
                )

            return MarketData(
                stock_info=stock_info,
                intraday_data=intraday_data,
                historical_data=historical_data,
                current_price=current_price,
                previous_close=previous_close,
                volume=volume,
                avg_volume=avg_volume
            )

        except Exception as e:
            logger.error(f"Error fetching market data for {ticker}: {e}")
            return None

    def is_market_open(self) -> bool:
        """Check if the market is currently open."""
        return self.provider.is_market_open()
