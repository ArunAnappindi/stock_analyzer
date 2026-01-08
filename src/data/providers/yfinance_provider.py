"""
Yahoo Finance data provider implementation.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import yfinance as yf
from pytz import timezone

from src.models import StockInfo, OHLCVData
from .base import DataProvider

logger = logging.getLogger(__name__)


class YFinanceProvider(DataProvider):
    """Yahoo Finance data provider implementation."""

    def __init__(self):
        """Initialize the Yahoo Finance provider."""
        self.eastern = timezone('US/Eastern')

    def get_stock_info(self, ticker: str) -> Optional[StockInfo]:
        """Fetch basic stock information."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return StockInfo(
                ticker=ticker.upper(),
                company_name=info.get('longName') or info.get('shortName'),
                exchange=info.get('exchange', 'UNKNOWN'),
                sector=info.get('sector'),
                market_cap=info.get('marketCap')
            )
        except Exception as e:
            logger.error(f"Error fetching stock info for {ticker}: {e}")
            return None

    def get_intraday_data(
        self,
        ticker: str,
        interval: str = "5m",
        days: int = 5
    ) -> Optional[OHLCVData]:
        """
        Fetch intraday OHLCV data.

        Note: Yahoo Finance has limitations:
        - 1m data: last 7 days only
        - 5m data: last 60 days
        - 15m data: last 60 days
        """
        try:
            stock = yf.Ticker(ticker)

            # Determine the period based on interval
            if interval == "1m":
                period = min(days, 7)
                period_str = f"{period}d"
            else:
                period = min(days, 60)
                period_str = f"{period}d"

            # Fetch the data
            df = stock.history(period=period_str, interval=interval)

            if df.empty:
                logger.warning(f"No intraday data available for {ticker}")
                return None

            # Clean up the dataframe
            df = df.reset_index()

            # Ensure we have the required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing required columns in data for {ticker}")
                return None

            # Remove any rows with NaN values
            df = df.dropna(subset=required_cols)

            if df.empty:
                logger.warning(f"No valid data after cleaning for {ticker}")
                return None

            return OHLCVData(
                ticker=ticker.upper(),
                interval=interval,
                data=df,
                fetched_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error fetching intraday data for {ticker}: {e}")
            return None

    def is_market_open(self) -> bool:
        """
        Check if US market is currently open.

        US market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        """
        try:
            now = datetime.now(self.eastern)

            # Check if it's a weekday (0 = Monday, 6 = Sunday)
            if now.weekday() > 4:  # Saturday or Sunday
                return False

            # Check if within market hours
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

            return market_open <= now <= market_close

        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False

    def get_historical_data(
        self,
        ticker: str,
        days: int = 30
    ) -> Optional[OHLCVData]:
        """
        Fetch daily historical data.

        Args:
            ticker: Stock ticker symbol
            days: Number of days of historical data

        Returns:
            OHLCVData with daily data
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=f"{days}d", interval="1d")

            if df.empty:
                logger.warning(f"No historical data available for {ticker}")
                return None

            df = df.reset_index()

            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing required columns in historical data for {ticker}")
                return None

            df = df.dropna(subset=required_cols)

            if df.empty:
                return None

            return OHLCVData(
                ticker=ticker.upper(),
                interval="1d",
                data=df,
                fetched_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {e}")
            return None
