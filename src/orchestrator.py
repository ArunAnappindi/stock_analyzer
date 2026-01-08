"""
Main orchestrator that coordinates all analysis components.
"""

import logging
from datetime import datetime
from typing import Optional
from src.models import AnalysisResult, MarketData
from src.data import DataFetcher
from src.analysis import TechnicalAnalyzer, VolumeAnalyzer, SentimentAnalyzer
from src.analysis.decision_engine import DecisionEngine
from config.settings import settings

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """Main stock analyzer orchestrator."""

    def __init__(
        self,
        news_api_key: Optional[str] = None,
        data_fetcher: Optional[DataFetcher] = None
    ):
        """
        Initialize the stock analyzer.

        Args:
            news_api_key: Optional NewsAPI key for sentiment analysis
            data_fetcher: Optional custom data fetcher
        """
        self.data_fetcher = data_fetcher or DataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        self.volume_analyzer = VolumeAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer(news_api_key)
        self.decision_engine = DecisionEngine()

    def analyze(
        self,
        ticker: str,
        interval: Optional[str] = None,
        historical_days: Optional[int] = None
    ) -> Optional[AnalysisResult]:
        """
        Perform complete analysis on a stock ticker.

        Args:
            ticker: Stock ticker symbol
            interval: Intraday interval (e.g., '5m', '15m')
            historical_days: Days of historical data to fetch

        Returns:
            AnalysisResult or None if analysis fails
        """
        try:
            logger.info(f"Starting analysis for {ticker}")

            # Step 1: Fetch market data
            logger.info("Fetching market data...")
            market_data = self.data_fetcher.fetch_market_data(
                ticker,
                interval=interval,
                historical_days=historical_days
            )

            if not market_data:
                logger.error(f"Failed to fetch market data for {ticker}")
                return None

            # Step 2: Perform technical analysis
            logger.info("Performing technical analysis...")
            technical_analysis = self.technical_analyzer.analyze(market_data)

            # Step 3: Perform volume analysis
            logger.info("Performing volume analysis...")
            volume_analysis = self.volume_analyzer.analyze(market_data)

            # Step 4: Perform sentiment analysis
            logger.info("Performing sentiment analysis...")
            sentiment_analysis = self.sentiment_analyzer.analyze(market_data.stock_info)

            # Step 5: Make trade decision
            logger.info("Generating trade recommendation...")
            trade_recommendation = self.decision_engine.make_decision(
                market_data,
                technical_analysis,
                volume_analysis,
                sentiment_analysis
            )

            # Step 6: Determine data quality
            is_market_open = self.data_fetcher.is_market_open()
            data_quality = "Real-time" if is_market_open else "Delayed / Simulated Data"

            # Step 7: Collect any warnings
            warnings = self._generate_warnings(
                market_data,
                technical_analysis,
                volume_analysis,
                is_market_open
            )

            # Step 8: Build final result
            result = AnalysisResult(
                ticker=ticker.upper(),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                current_price=market_data.current_price,
                technical_analysis=technical_analysis,
                volume_analysis=volume_analysis,
                sentiment_analysis=sentiment_analysis,
                trade_recommendation=trade_recommendation,
                data_quality=data_quality,
                warnings=warnings
            )

            logger.info(f"Analysis completed for {ticker}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
            return None

    def _generate_warnings(
        self,
        market_data: MarketData,
        technical_analysis,
        volume_analysis,
        is_market_open: bool
    ) -> list[str]:
        """Generate warnings based on analysis conditions."""
        warnings = []

        # Market closed warning
        if not is_market_open:
            warnings.append(
                "Market is currently closed. Data may be delayed or from previous session."
            )

        # Low volume warning
        if volume_analysis.relative_volume < 0.5:
            warnings.append(
                "Very low volume detected. This may indicate reduced liquidity and higher risk."
            )

        # Limited data warning
        data_points = len(market_data.intraday_data.data)
        if data_points < 20:
            warnings.append(
                f"Limited data available ({data_points} data points). "
                "Analysis may be less reliable."
            )

        # Extreme RSI warning
        if technical_analysis.indicators.rsi:
            if technical_analysis.indicators.rsi > 80:
                warnings.append("RSI indicates extreme overbought conditions.")
            elif technical_analysis.indicators.rsi < 20:
                warnings.append("RSI indicates extreme oversold conditions.")

        # Breakdown warning
        if technical_analysis.is_breakdown:
            warnings.append(
                "Technical breakdown detected below support. High risk of further downside."
            )

        return warnings
